#!/usr/bin/env python3
"""Generate a rule-level index for Xtext grammar files.

Purpose: deep syntax checks should locate a rule by name and jump straight to
its line range instead of reading (or re-downloading) the whole grammar.

Output is a Markdown table per grammar file:

    | rule | kind | lines | definition head |

The script is structure-aware: comments and string literals are masked out
(positions preserved) before rule scanning, so a `:` or `;` inside a comment
or a literal never confuses the parser. Rule bodies end at the first `;`
found at bracket depth 0.

Usage:
    python3 gen_index.py <grammar.xtext> [<grammar.xtext> ...] > index.md
    python3 gen_index.py --title "CML" --source "repo @ commit" file.xtext ...

Exit status is non-zero when a file cannot be parsed or yields no rules.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

MASK = "\x00"

RULE_HEAD_RE = re.compile(
    r"(?m)^(?P<prefix>(?:abstract|enum|terminal(?:\s+fragment)?|fragment)\s+)?"
    r"(?P<name>[A-Za-z_][\w]*)"
    r"(?P<mid>(?:\s+returns\s+[^:;\n]+|\s+hidden\s*\([^)\n]*\)|\s+generates\s+[^:;\n]+|\s+imports\s+[^:;\n]+)*)"
    r"\s*:",
)


def mask_source(text: str) -> str:
    """Blank out comments and string-literal interiors, preserving length."""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            end = n if end == -1 else end + 2
            for j in range(i, end):
                if out[j] not in "\n\r":
                    out[j] = MASK
            i = end
        elif ch == "/" and i + 1 < n and text[i + 1] == "/":
            end = text.find("\n", i)
            end = n if end == -1 else end
            for j in range(i, end):
                out[j] = MASK
            i = end
        elif ch in "'\"":
            quote = ch
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == quote:
                    j += 1
                    break
                j += 1
            for k in range(i + 1, min(j, n)):
                if out[k] not in "\n\r":
                    out[k] = MASK
            i = j
        else:
            i += 1
    return "".join(out)


@dataclass
class Rule:
    name: str
    kind: str
    start_line: int
    end_line: int
    head: str


def scan_rules(text: str) -> list[Rule]:
    masked = mask_source(text)
    line_starts = [0]
    for idx, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(idx + 1)

    def line_of(pos: int) -> int:
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    rules: list[Rule] = []
    pos = 0
    while True:
        m = RULE_HEAD_RE.search(masked, pos)
        if not m:
            break
        # walk to the terminating ';' at depth 0
        depth = 0
        end = None
        i = m.end()
        while i < len(masked):
            c = masked[i]
            if c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
            elif c == ";" and depth <= 0:
                end = i
                break
            i += 1
        if end is None:
            end = len(masked) - 1

        prefix = (m.group("prefix") or "").strip()
        kind = {
            "enum": "enum",
            "terminal": "terminal",
            "terminal fragment": "terminal-fragment",
            "abstract": "abstract",
            "fragment": "fragment",
        }.get(prefix, "parser")

        # definition head: original body text right after ':', first ~72 chars
        # (bodies usually start on the next line, so scan forward across lines)
        body = " ".join(text[m.end() : end].split())
        body = re.sub(r"\s*//.*", "", body)
        head = body[:69] + "..." if len(body) > 72 else body

        rules.append(
            Rule(
                name=m.group("name"),
                kind=kind,
                start_line=line_of(m.start()),
                end_line=line_of(end),
                head=head,
            )
        )
        pos = end + 1
    return rules


def render(path: Path, title: str, source: str) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    rules = scan_rules(text)
    if not rules:
        raise SystemExit(f"[gen_index] no rules found in {path}")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    total = len(text.splitlines())
    kinds = {}
    for r in rules:
        kinds[r.kind] = kinds.get(r.kind, 0) + 1
    kind_summary = " · ".join(f"{k} {v}" for k, v in sorted(kinds.items()))

    lines = [
        f"# {title} 语法规则索引 — {path.name}",
        "",
        "> **自动生成，勿手改**（生成器：`dsl/gen_index.py`，重跑：`python3 dsl/sync.py`）。",
        "> 深度语法检查流程：在本表按规则名定位行区间 → 用 `read` 工具带 `offset`/`limit` 精读该区间；",
        "> 不要下载/解压上游仓库，也不要读临时目录里的副本。",
        "",
        f"- 语法文件：[`{path.name}`](./{path.name})（{total} 行，sha256 `{digest[:16]}...`）",
        f"- 上游：{source}",
        f"- 规则数：{len(rules)}（{kind_summary}）",
        f"- 生成日期：{date.today().isoformat()}",
        "",
        "| 规则 | 类型 | 行区间 | 定义首行摘要 |",
        "|------|------|--------|--------------|",
    ]
    for r in rules:
        span = f"{r.start_line}" if r.start_line == r.end_line else f"{r.start_line}–{r.end_line}"
        head = r.head.replace("|", "\\|") or "—"
        lines.append(f"| `{r.name}` | {r.kind} | {span} | `{head}` |" if r.head else f"| `{r.name}` | {r.kind} | {span} | — |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", help="Xtext grammar files to index")
    ap.add_argument("--title", default="DSL", help="index title prefix (e.g. CML / MDSL)")
    ap.add_argument("--source", default="（未记录）", help="provenance line, e.g. 'repo @ commit (date)'")
    ap.add_argument("-o", "--output", help="write here instead of stdout")
    args = ap.parse_args()

    parts = [render(Path(f), args.title, args.source) for f in args.files]
    out = "\n---\n\n".join(parts)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
