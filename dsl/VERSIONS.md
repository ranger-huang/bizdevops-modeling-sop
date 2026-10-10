# 语法文件版本账本（VERSIONS）

> **本文件由 `python3 dsl/sync.py` 自动生成，勿手改。** 使用说明见 [README.md](./README.md)。
> 最近同步：2026-10-10T14:53:23+08:00

深度语法检查一律以本目录下的语法文件为准；下表记录它们的上游出处与校验值，
用于证明「本地副本 == 上游某个确定 commit 的逐字节内容」。

<!-- pin:cml commit=995f486a9cdecb6946257d5c7b6d98ada2978124 date=2025-07-08T10:01:58Z -->
## CML — Context Mapping DSL (Context Mapper)

- 上游仓库：[`ContextMapper/context-mapper-dsl`](https://github.com/ContextMapper/context-mapper-dsl)
- 跟踪分支：`master`
- 锁定 commit：[`995f486a9cde`](https://github.com/ContextMapper/context-mapper-dsl/commit/995f486a9cdecb6946257d5c7b6d98ada2978124)（提交时间 2025-07-08T10:01:58Z）
- 许可证：Apache-2.0（副本：[`cml/LICENSE`](./cml/LICENSE)）
- 最新 release `v6.12.0`：**语法文件与该 tag 逐字节一致**（无漂移）
- 入库范围说明：ContextMappingDSL.xtext 以 `grammar ... with org.contextmapper.tactic.dsl.TacticDDDLanguage` 继承战术 DDD 语法，两个文件必须成对使用；上游另有 `org.contextmapper.servicecutter/dsl/ServiceCutterConfigurationDSL.xtext`（服务切分配置），本手册 SOP 未引用，故不入库。

| 本地文件 | 上游路径 | 字节 | 行数 | git blob sha1 | sha256 |
|----------|----------|------|------|---------------|--------|
| [`cml/ContextMappingDSL.xtext`](./cml/ContextMappingDSL.xtext) | `org.contextmapper.dsl/src/org/contextmapper/dsl/ContextMappingDSL.xtext` | 18089 | 556 | `28786cb6c6cfb04e98af697348c9cce8479c3a80` | `440d9a081c28c89b5fbaac3764ad9ed9…` |
| [`cml/TacticDDDLanguage.xtext`](./cml/TacticDDDLanguage.xtext) | `org.contextmapper.dsl/src/org/contextmapper/tactic/dsl/TacticDDDLanguage.xtext` | 19626 | 578 | `430db4caf0cb44f1b05c481b8f9e6cd85e34fd0f` | `41492434234e62d09185ecc68ad522ff…` |
| [`cml/LICENSE`](./cml/LICENSE) | `LICENSE` | 11357 | 201 | `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64` | `c71d239df91726fc519c6eb72d318ec6…` |

- 规则索引：[`cml/grammar-index.md`](./cml/grammar-index.md)（规则名 → 行区间，自动生成）

<!-- pin:mdsl commit=9da0bac0e6133b8a69131925e38bc98e63e20af2 date=2025-01-23T12:41:41Z -->
## MDSL — Microservice Domain Specific Language (MDSL / AsyncMDSL)

- 上游仓库：[`Microservice-API-Patterns/MDSL-Specification`](https://github.com/Microservice-API-Patterns/MDSL-Specification)
- 跟踪分支：`master`
- 锁定 commit：[`9da0bac0e613`](https://github.com/Microservice-API-Patterns/MDSL-Specification/commit/9da0bac0e6133b8a69131925e38bc98e63e20af2)（提交时间 2025-01-23T12:41:41Z）
- 许可证：Apache-2.0（副本：[`mdsl/LICENSE`](./mdsl/LICENSE)）
- 最新 release `v6.0.0`：**语法文件与该 tag 逐字节一致**（无漂移）
- 入库范围说明：APIDescription.xtext 是 MDSL 的唯一语法文件，AsyncMDSL 扩展（channel / message broker / message endpoint / flow）已内联在同一文件中；上游 `GenerateAPIDescription.mwe2` 只是 Xtext 代码生成配置，与语法检查无关，故不入库。

| 本地文件 | 上游路径 | 字节 | 行数 | git blob sha1 | sha256 |
|----------|----------|------|------|---------------|--------|
| [`mdsl/APIDescription.xtext`](./mdsl/APIDescription.xtext) | `dsl-core/io.mdsl/src/io/mdsl/APIDescription.xtext` | 32605 | 967 | `4c3ca3b34a0105092fe708f4ac34a6c6ab4d6fa9` | `8376badbd8e4735625d20129797f4d8d…` |
| [`mdsl/LICENSE`](./mdsl/LICENSE) | `LICENSE` | 11357 | 201 | `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64` | `c71d239df91726fc519c6eb72d318ec6…` |

- 规则索引：[`mdsl/grammar-index.md`](./mdsl/grammar-index.md)（规则名 → 行区间，自动生成）

---

## 校验方式

1. **完整性**：每个文件的 `git blob sha1` 与上游 `GET /git/trees/<commit>?recursive=1` 返回的 blob sha 逐一相等（逐字节一致）。
2. **本地未被改动**：`python3 dsl/sync.py --check` 用 sha256 对比本地文件与本账本记录。
3. **上游是否前进**：同一命令比较上游 `master` HEAD 与锁定 commit，报告漂移。

## 手动核对命令

```bash
python3 dsl/sync.py --check          # 只读：报告漂移与篡改
python3 dsl/sync.py                  # 同步到上游分支 HEAD 并重生成账本/索引
shasum -a 256 dsl/*/*.xtext          # 与上表 sha256 对照
```
