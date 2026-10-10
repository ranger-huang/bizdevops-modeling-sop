#!/usr/bin/env python3
"""Sync and verify the vendored CML / MDSL grammar files under dsl/.

Single owner for "which upstream revision is vendored here": it pins each DSL
to an upstream commit, verifies every file byte-for-byte against the upstream
git blob sha, regenerates `grammar-index.md` per DSL directory, and rewrites
`VERSIONS.md` (the ledger).

Usage:
    python3 dsl/sync.py            # fetch upstream default branch, install, verify, regenerate
    python3 dsl/sync.py --check    # no writes: report pin drift + local tampering
    python3 dsl/sync.py --pin <sha> --dsl cml   # vendor a specific upstream commit

Env:
    GITHUB_TOKEN   optional, raises the api.github.com rate limit

Exit status: 0 ok, 1 drift/tamper found in --check, 2 fetch or verification failure.
Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

DSL_ROOT = Path(__file__).resolve().parent
API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
UA = "bizdevops-modeling-sop/dsl-sync (+local skill maintenance)"


@dataclass
class GrammarFile:
    upstream: str          # path inside the upstream repo
    local: str             # file name under dsl/<key>/
    is_grammar: bool = True  # False for LICENSE and other companions


@dataclass
class DSL:
    key: str               # directory name under dsl/
    title: str             # CML / MDSL
    long_name: str
    repo: str              # owner/name
    branch: str
    license_id: str
    files: list[GrammarFile]
    index: str = "grammar-index.md"
    note: str = ""

    @property
    def dir(self) -> Path:
        return DSL_ROOT / self.key


DSLS = [
    DSL(
        key="cml",
        title="CML",
        long_name="Context Mapping DSL (Context Mapper)",
        repo="ContextMapper/context-mapper-dsl",
        branch="master",
        license_id="Apache-2.0",
        note=(
            "ContextMappingDSL.xtext 以 `grammar ... with org.contextmapper.tactic.dsl.TacticDDDLanguage` "
            "继承战术 DDD 语法，两个文件必须成对使用；上游另有 "
            "`org.contextmapper.servicecutter/dsl/ServiceCutterConfigurationDSL.xtext`（服务切分配置），"
            "本手册 SOP 未引用，故不入库。"
        ),
        files=[
            GrammarFile("org.contextmapper.dsl/src/org/contextmapper/dsl/ContextMappingDSL.xtext", "ContextMappingDSL.xtext"),
            GrammarFile("org.contextmapper.dsl/src/org/contextmapper/tactic/dsl/TacticDDDLanguage.xtext", "TacticDDDLanguage.xtext"),
            GrammarFile("LICENSE", "LICENSE", is_grammar=False),
        ],
    ),
    DSL(
        key="mdsl",
        title="MDSL",
        long_name="Microservice Domain Specific Language (MDSL / AsyncMDSL)",
        repo="Microservice-API-Patterns/MDSL-Specification",
        branch="master",
        license_id="Apache-2.0",
        note=(
            "APIDescription.xtext 是 MDSL 的唯一语法文件，AsyncMDSL 扩展（channel / message broker / "
            "message endpoint / flow）已内联在同一文件中；上游 `GenerateAPIDescription.mwe2` 只是 "
            "Xtext 代码生成配置，与语法检查无关，故不入库。"
        ),
        files=[
            GrammarFile("dsl-core/io.mdsl/src/io/mdsl/APIDescription.xtext", "APIDescription.xtext"),
            GrammarFile("LICENSE", "LICENSE", is_grammar=False),
        ],
    ),
]


# --------------------------------------------------------------------------- #
# HTTP helpers
# --------------------------------------------------------------------------- #

def _get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"[sync] HTTP {exc.code} for {url}: {exc.reason}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SystemExit(f"[sync] network failure for {url}: {exc}") from exc


def get_json(url: str) -> object:
    return json.loads(_get(url).decode("utf-8"))


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------- #
# upstream facts
# --------------------------------------------------------------------------- #

def head_commit(dsl: DSL, pin: str | None) -> tuple[str, str]:
    if pin:
        data = get_json(f"{API}/repos/{dsl.repo}/commits/{pin}")
        return data["sha"], data["commit"]["committer"]["date"]
    data = get_json(f"{API}/repos/{dsl.repo}/commits?sha={dsl.branch}&per_page=1")
    item = data[0]
    return item["sha"], item["commit"]["committer"]["date"]


def tree_blobs(dsl: DSL, commit: str) -> dict[str, str]:
    data = get_json(f"{API}/repos/{dsl.repo}/git/trees/{commit}?recursive=1")
    if data.get("truncated"):
        print(f"[sync] warning: {dsl.repo} tree truncated; blob verification may be partial")
    return {t["path"]: t["sha"] for t in data.get("tree", []) if t["type"] == "blob"}


def latest_release(dsl: DSL, commit: str, head_bytes: dict[str, bytes]) -> dict[str, object]:
    """Latest release tag + whether its grammar files differ from the pinned commit."""
    info: dict[str, object] = {"tag": None, "commit": None, "drift": None, "error": None}
    try:
        rel = get_json(f"{API}/repos/{dsl.repo}/releases/latest")
        tag = rel.get("tag_name")
        info["tag"] = tag
        info["published"] = rel.get("published_at")
        ref = get_json(f"{API}/repos/{dsl.repo}/git/refs/tags/{tag}")
        obj = ref["object"]
        if obj["type"] == "tag":  # annotated tag -> dereference
            obj = get_json(f"{API}/repos/{dsl.repo}/git/tags/{obj['sha']}")["object"]
        tag_commit = obj["sha"]
        info["commit"] = tag_commit
        drift = []
        for gf in dsl.files:
            if not gf.is_grammar:
                continue
            tag_bytes = _get(f"{RAW}/{dsl.repo}/{tag_commit}/{gf.upstream}")
            if tag_bytes != head_bytes.get(gf.local, b""):
                drift.append(gf.local)
        info["drift"] = drift
    except SystemExit as exc:
        info["error"] = str(exc)
    return info


# --------------------------------------------------------------------------- #
# ledger
# --------------------------------------------------------------------------- #

PIN_RE = re.compile(r"<!-- pin:(\w+) commit=([0-9a-f]{40}) date=(\S+) -->")


def read_pins() -> dict[str, tuple[str, str]]:
    ledger = DSL_ROOT / "VERSIONS.md"
    if not ledger.exists():
        return {}
    return {m.group(1): (m.group(2), m.group(3)) for m in PIN_RE.finditer(ledger.read_text(encoding="utf-8"))}


@dataclass
class SyncResult:
    dsl: DSL
    commit: str
    commit_date: str
    changed: list[str] = field(default_factory=list)
    verified: list[tuple[str, str, int, int, str]] = field(default_factory=list)  # local, blob, bytes, lines, sha256
    release: dict[str, object] = field(default_factory=dict)
    release_note: str | None = None  # verbatim ledger line, reused by partial runs
    blob_mismatch: list[str] = field(default_factory=list)


def render_ledger(results: list[SyncResult]) -> str:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    out = [
        "# 语法文件版本账本（VERSIONS）",
        "",
        "> **本文件由 `python3 dsl/sync.py` 自动生成，勿手改。** 使用说明见 [README.md](./README.md)。",
        f"> 最近同步：{now}",
        "",
        "深度语法检查一律以本目录下的语法文件为准；下表记录它们的上游出处与校验值，",
        "用于证明「本地副本 == 上游某个确定 commit 的逐字节内容」。",
        "",
    ]
    for r in results:
        dsl = r.dsl
        rel = r.release or {}
        out += [
            f"<!-- pin:{dsl.key} commit={r.commit} date={r.commit_date} -->",
            f"## {dsl.title} — {dsl.long_name}",
            "",
            f"- 上游仓库：[`{dsl.repo}`](https://github.com/{dsl.repo})",
            f"- 跟踪分支：`{dsl.branch}`",
            f"- 锁定 commit：[`{r.commit[:12]}`](https://github.com/{dsl.repo}/commit/{r.commit})（提交时间 {r.commit_date}）",
            f"- 许可证：{dsl.license_id}（副本：[`{dsl.key}/LICENSE`](./{dsl.key}/LICENSE)）",
        ]
        if r.release_note:
            out.append(f"- {r.release_note}")
        elif rel.get("tag"):
            drift = rel.get("drift")
            if drift == []:
                rel_note = f"最新 release `{rel['tag']}`：**语法文件与该 tag 逐字节一致**（无漂移）"
            elif drift:
                rel_note = f"最新 release `{rel['tag']}`：语法文件与该 tag 存在差异（{', '.join(drift)}）——以锁定 commit 为准"
            else:
                rel_note = f"最新 release `{rel['tag']}`"
            out.append(f"- {rel_note}")
        if rel.get("error") and not r.release_note:
            out.append(f"- release 对照：未完成（{rel['error']}）")
        if dsl.note:
            out.append(f"- 入库范围说明：{dsl.note}")
        if r.blob_mismatch:
            out.append(f"- ⚠️ blob 校验不一致：{', '.join(r.blob_mismatch)}")
        out += [
            "",
            "| 本地文件 | 上游路径 | 字节 | 行数 | git blob sha1 | sha256 |",
            "|----------|----------|------|------|---------------|--------|",
        ]
        gf_by_local = {gf.local: gf for gf in dsl.files}
        for local, blob, nbytes, lines, digest in r.verified:
            up = gf_by_local[local].upstream
            out.append(
                f"| [`{dsl.key}/{local}`](./{dsl.key}/{local}) | `{up}` | {nbytes} | {lines} | `{blob}` | `{digest[:32]}…` |"
            )
        if r.changed:
            out += ["", f"本次同步改动的文件：{', '.join('`' + c + '`' for c in r.changed)}"]
        out += [
            "",
            f"- 规则索引：[`{dsl.key}/{dsl.index}`](./{dsl.key}/{dsl.index})（规则名 → 行区间，自动生成）",
            "",
        ]
    out += [
        "---",
        "",
        "## 校验方式",
        "",
        "1. **完整性**：每个文件的 `git blob sha1` 与上游 `GET /git/trees/<commit>?recursive=1` 返回的 blob sha 逐一相等（逐字节一致）。",
        "2. **本地未被改动**：`python3 dsl/sync.py --check` 用 sha256 对比本地文件与本账本记录。",
        "3. **上游是否前进**：同一命令比较上游 `master` HEAD 与锁定 commit，报告漂移。",
        "",
        "## 手动核对命令",
        "",
        "```bash",
        "python3 dsl/sync.py --check          # 只读：报告漂移与篡改",
        "python3 dsl/sync.py                  # 同步到上游分支 HEAD 并重生成账本/索引",
        "shasum -a 256 dsl/*/*.xtext          # 与上表 sha256 对照",
        "```",
        "",
    ]
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# index generation (delegates to gen_index.py, same directory)
# --------------------------------------------------------------------------- #

def regenerate_index(dsl: DSL, commit: str, commit_date: str) -> None:
    sys.path.insert(0, str(DSL_ROOT))
    sys.dont_write_bytecode = True  # keep __pycache__ out of the vendored tree
    import gen_index  # noqa: PLC0415  (local module, imported after path setup)

    source = f"[`{dsl.repo}`](https://github.com/{dsl.repo}) @ `{dsl.branch}` commit `{commit[:12]}`（{commit_date[:10]}）"
    grammar_files = [dsl.dir / gf.local for gf in dsl.files if gf.is_grammar]
    parts = [gen_index.render(p, dsl.title, source) for p in grammar_files]
    (dsl.dir / dsl.index).write_text("\n---\n\n".join(parts), encoding="utf-8")


# --------------------------------------------------------------------------- #
# modes
# --------------------------------------------------------------------------- #

def do_sync(dsl: DSL, pin: str | None, with_release: bool) -> SyncResult:
    commit, commit_date = head_commit(dsl, pin)
    blobs = tree_blobs(dsl, commit)
    dsl.dir.mkdir(parents=True, exist_ok=True)
    result = SyncResult(dsl=dsl, commit=commit, commit_date=commit_date)
    fetched: dict[str, bytes] = {}

    for gf in dsl.files:
        data = _get(f"{RAW}/{dsl.repo}/{commit}/{gf.upstream}")
        fetched[gf.local] = data
        blob = git_blob_sha1(data)
        expected = blobs.get(gf.upstream)
        if expected and expected != blob:
            result.blob_mismatch.append(f"{gf.local}(local={blob[:10]} upstream={expected[:10]})")
        target = dsl.dir / gf.local
        before = target.read_bytes() if target.exists() else None
        if before != data:
            result.changed.append(gf.local)
        target.write_bytes(data)
        result.verified.append(
            (gf.local, blob, len(data), len(data.decode("utf-8", "replace").splitlines()), sha256(data))
        )

    if with_release:
        result.release = latest_release(dsl, commit, fetched)
    regenerate_index(dsl, commit, commit_date)
    return result


def do_check() -> int:
    pins = read_pins()
    if not pins:
        print("[check] VERSIONS.md 中没有 pin 记录，先运行 python3 dsl/sync.py")
        return 2
    failures = 0
    for dsl in DSLS:
        pin = pins.get(dsl.key)
        if not pin:
            print(f"[check] {dsl.title}: 账本中没有记录 -> 需要重新同步")
            failures += 1
            continue
        commit, commit_date = pin
        print(f"\n=== {dsl.title} pinned at {commit[:12]} ({commit_date[:10]}) ===")
        # 1. local integrity against the ledger table
        ledger = (DSL_ROOT / "VERSIONS.md").read_text(encoding="utf-8")
        for gf in dsl.files:
            path = dsl.dir / gf.local
            if not path.exists():
                print(f"  MISSING  {gf.local}")
                failures += 1
                continue
            digest = sha256(path.read_bytes())
            row = re.search(
                re.escape(f"| [`{dsl.key}/{gf.local}`]") + r".*?\| `([0-9a-f]{40})` \| `([0-9a-f]{32})",
                ledger,
                re.S,
            )
            if not row:
                print(f"  UNTRACKED {gf.local}（账本里没有对应行）")
                failures += 1
                continue
            blob_ok = row.group(1) == git_blob_sha1(path.read_bytes())
            sha_ok = digest.startswith(row.group(2))
            print(f"  {'OK  ' if (blob_ok and sha_ok) else 'FAIL'}     {gf.local}  blob={'✓' if blob_ok else '✗'} sha256={'✓' if sha_ok else '✗'}")
            if not (blob_ok and sha_ok):
                failures += 1
        # 2. upstream drift
        try:
            head, head_date = head_commit(dsl, None)
        except SystemExit as exc:
            print(f"  DRIFT?   上游查询失败（{exc}）")
            continue
        if head == commit:
            print(f"  DRIFT    无：上游 {dsl.branch} HEAD 仍是 {head[:12]}")
        else:
            print(f"  DRIFT    上游 {dsl.branch} 已前进到 {head[:12]}（{head_date[:10]}）；运行 python3 dsl/sync.py 更新")
            failures += 1
    print()
    if failures:
        print(f"[check] {failures} 项需要处理")
        return 1
    print("[check] 全部一致：本地文件 == 账本记录，且上游无前进")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="只读校验：报告 pin 漂移与本地篡改，不写任何文件")
    ap.add_argument("--dsl", choices=[d.key for d in DSLS], help="只处理某一个 DSL")
    ap.add_argument("--pin", help="锁定到指定上游 commit（配合 --dsl）")
    ap.add_argument("--no-release", action="store_true", help="跳过与最新 release tag 的语法漂移对照")
    args = ap.parse_args()

    if args.check:
        return do_check()

    selected = [d for d in DSLS if not args.dsl or d.key == args.dsl]
    if args.pin and len(selected) != 1:
        raise SystemExit("[sync] --pin 必须配合 --dsl 指定单个 DSL")

    results: list[SyncResult] = []
    for dsl in selected:
        pin = args.pin if (args.pin and args.dsl == dsl.key) else None
        print(f"[sync] {dsl.title}: 拉取 {dsl.repo} @ {pin or dsl.branch + ' HEAD'} ...")
        results.append(do_sync(dsl, pin, with_release=not args.no_release))

    # a full run rewrites the whole ledger; a partial run must keep other DSL entries
    ledger_path = DSL_ROOT / "VERSIONS.md"
    if args.dsl and ledger_path.exists():
        kept = [r for r in [_stub_for(d, read_pins().get(d.key)) for d in DSLS if d.key != args.dsl] if r]
        results = [r for r in results] + kept
        results.sort(key=lambda r: [d.key for d in DSLS].index(r.dsl.key))
    ledger_path.write_text(render_ledger(results), encoding="utf-8")

    for r in results:
        status = "无变化" if not r.changed else "改动：" + ", ".join(r.changed)
        flag = " ⚠️ blob 不一致" if r.blob_mismatch else ""
        print(f"[sync] {r.dsl.title} @ {r.commit[:12]} — {status}{flag}")
    print(f"[sync] 账本已更新：{ledger_path.relative_to(DSL_ROOT.parent)}")
    try:
        out = subprocess.run(
            ["git", "status", "--short", "--", str(DSL_ROOT)],
            cwd=DSL_ROOT.parent, capture_output=True, text=True, check=False,
        ).stdout.strip()
        if out:
            print("[sync] git 变更：\n" + out)
    except OSError:
        pass
    return 2 if any(r.blob_mismatch for r in results) else 0


def _stub_for(dsl: DSL, pin: tuple[str, str] | None) -> SyncResult | None:
    """Rebuild a ledger entry for an untouched DSL from files already on disk."""
    if not pin:
        return None
    commit, commit_date = pin
    res = SyncResult(dsl=dsl, commit=commit, commit_date=commit_date)
    for gf in dsl.files:
        path = dsl.dir / gf.local
        if not path.exists():
            return None
        data = path.read_bytes()
        res.verified.append(
            (gf.local, git_blob_sha1(data), len(data), len(data.decode("utf-8", "replace").splitlines()), sha256(data))
        )
    ledger = (DSL_ROOT / "VERSIONS.md").read_text(encoding="utf-8")
    block = re.search(rf"^## {re.escape(dsl.title)} —.*?(?=^## |^---$|\Z)", ledger, re.S | re.M)
    if block:
        note = re.search(r"^- (最新 release .*|release 对照：.*)$", block.group(0), re.M)
        if note:
            res.release_note = note.group(1).strip()
    return res


if __name__ == "__main__":
    raise SystemExit(main())
