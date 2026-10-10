# bizdevops-modeling-sop

> BizDevOps 领域建模与服务设计 **SOP 手册**——一个工具中立的 Agent Skill：15 个可直接执行的 SOP（何时启用 / 触发条件 / 步骤 / 交付物 / 成功标准）+ 综合速查表 + 决策规则库 + **随仓库版本化留档的 CML / MDSL 官方语法文件**。

![SOP](https://img.shields.io/badge/SOP-15%20%28A%E2%80%93F%29-blue)
![CML](https://img.shields.io/badge/CML-v6.12.0%20pinned-informational)
![MDSL](https://img.shields.io/badge/MDSL-v6.0.0%20pinned-informational)
![deps](https://img.shields.io/badge/dependencies-none-success)
![style](https://img.shields.io/badge/tool--neutral-methodology-lightgrey)
![license](https://img.shields.io/badge/license-Apache--2.0-blue)

覆盖 DDD 战略/战术建模、事件风暴结果固化、干系人与价值建模（VDAD）、架构重构（AR-1~11）、系统化服务分解、领域/故事/事件驱动服务设计、MAP 模式装饰、存量 API 结构分析、模型-代码一致性验证、质量治理（SLA / Rate Limit / Pricing Plan）、版本演进（Versioning & Evolution）与方法工程（DPR）。

## 目录

- [这是什么](#这是什么)
- [何时使用 / 何时不使用](#何时使用--何时不使用)
- [安装](#安装)
- [快速开始](#快速开始)
- [SOP 一览](#sop-一览)
- [编排路线](#编排路线)
- [仓库结构](#仓库结构)
- [内容约定](#内容约定)
- [CML / MDSL 语法取证](#cml--mdsl-语法取证)
- [维护](#维护)
- [来源与致谢](#来源与致谢)
- [许可证](#许可证)

## 这是什么

一份**给 agent 和人共用**的方法论手册，不是代码库：

- **无构建、无运行时依赖**：全部内容是 Markdown；`dsl/sync.py`、`dsl/gen_index.py` 是仅用 Python 3 标准库的维护脚本。
- **按需加载**：入口 `SKILL.md` 只放路由与索引（110 行），15 个 SOP 正文各成一章（184–412 行），一次只读需要的那一章。
- **可辩护**：每个 SOP 都有「成功标准」「反模式」「来源」；每处分解/合并决策要求指认至少一条分解准则（DC-1~5 或 14 项耦合准则）。
- **语法可取证**：CML / MDSL 的官方 `.xtext` 语法文件逐字节留档在 `dsl/`，配规则名→行区间索引与版本账本（pin commit / blob sha1 / sha256），深度语法检查就地取证，**不需要下载上游仓库、不凭记忆断言语法形态**。

内容来自 8 份方法论文档（CML 规范、MDSL 规范、SummerSoC 2020、ICWE 2020 keynote、APIace EuroPLoP 2021、DPR、两份 MDSL 语法调研），生成于 2026-10-10，详见[来源与致谢](#来源与致谢)。

## 何时使用 / 何时不使用

**适用**：DDD 建模与上下文映射、微服务拆分与增量重构、事件风暴产出固化、API 契约设计（contract first / code first）与 MAP 精化、存量 OpenAPI 盘点治理、SLA / 限流 / 计费声明、版本与弃用管理、模型-代码漂移守护、方法引入与裁剪，以及核对 CML/MDSL 语法形态与枚举取值域。

**不适用**：CI/CD 与监控落地（属 BaU，方法论范围外）、Context Mapper Generators、JHipster 教程、IDE 插件/生成器/CLI 的安装配置——本手册**工具中立**，不绑定任何 IDE 或代码生成器。

已知边界（按 SOP-13 三规则自行裁剪）：故事拆分在源文档中为 PoC（仅按动词拆分）；耦合准则目录源自已停用工具，方法学仍有效；质量/版本子句的表达力有实证边界（测量值仅整数、无 `deprecated`/`sunset` 语法、金额与客户端差异化配额不可表达等，见 `patterns.md` ⑧⑨ 与 sop-14/15），不可表达部分一律**带外治理**。

## 安装

作为 Agent Skill（任何遵循 `SKILL.md` frontmatter 约定的 agent 运行时，如 Claude Code、DeepSeek Harness）：

```bash
# 用户级（Claude Code 约定）
git clone https://github.com/ranger-huang/bizdevops-modeling-sop.git \
  ~/.claude/skills/bizdevops-modeling-sop

# 用户级（agents 目录约定）
git clone https://github.com/ranger-huang/bizdevops-modeling-sop.git \
  ~/.agents/skills/bizdevops-modeling-sop

# 项目级（随仓库分发给团队）
git clone https://github.com/ranger-huang/bizdevops-modeling-sop.git \
  .claude/skills/bizdevops-modeling-sop
```

重载会话后，`bizdevops-modeling-sop` 应出现在 skill 目录中；触发依据是 `SKILL.md` frontmatter 的 `name` 与 `description`。

**不用 agent 也能读**：直接当文档仓库用——从 [cheatsheet.md](cheatsheet.md) 的「场景 → SOP 决策树」进入，再读对应 `chapters/sop-*.md`。

更新：`git pull`。若关心上游语法是否前进，跑 `python3 dsl/sync.py --check`（见[维护](#维护)）。

## 快速开始

带场景描述，让 agent 按决策树路由到 SOP：

| 你说 | 走哪条路 |
|------|---------|
| "这个单体要拆服务，切分老是有争议" | SOP-06（可辩护分解）→ SOP-05（增量 AR）；先 SOP-11 盘点存量 API |
| "事件风暴工作坊刚结束，白板明天就擦" | SOP-03（固化为 CML 事件/命令/聚合模型 + BC 边界） |
| "评审这份 OpenAPI，语义歧义太多" | SOP-11（P1–P4 原语归类 + 五坏味道 + 修正建议） |
| "契约骨架有了，表示/分页/角色说不清" | SOP-10（MAP 装饰 + 力场权衡记录） |
| "要对外承诺 SLA、限流和计费" | SOP-14（质量登记 + 执行点映射；无校验器则评审+监控兜底） |
| "要做破坏性变更和弃用" | SOP-15（版本登记 + 演进策略 + 带外弃用时间表） |
| "模型和代码好像已经不一致了" | SOP-12（架构规则集 + CI 验证 + 处置记录） |
| "这段 MDSL 的 `rate limit` 能这么写吗" | `dsl/mdsl/grammar-index.md` 定位规则行区间 → `read` 精读 `APIDescription.xtext` |

也可以直接点名：`SOP-05`、`按 patterns.md ① 选 AR`、`用编排路线「棕地治理」走一遍`。

每个 SOP 的执行产物是**技术交付物 + 成功标准自查**，例如 SOP-06 产出「耦合准则标注 + 候选方案对比」，成功标准是「切分可追溯准则、与组织兼容」。

## SOP 一览

| # | SOP | 组 | 何时启用 | 关键触发信号 | 核心交付物 |
|---|-----|----|---------|--------------|------------|
| [01](chapters/sop-01-rapid-ooad.md) | 快速 OOAD 建模 | A | 从书面需求快速推导初始分解 | 有故事/用例清单、无 BC 结构 | 子域模型 + 初始上下文映射 |
| [02](chapters/sop-02-story-splitting.md) | 用户故事拆分 | A | 大故事拆为可独立交付薄片 | 复合动词（manage=create+edit+cancel）、估算超阈值 | 子故事集 + 追溯矩阵 |
| [03](chapters/sop-03-event-storming-modeling.md) | 事件风暴结果建模 | A | 工作坊产出固化为精确模型 | 事件风暴完成、白板将丢 | 事件/命令/聚合模型 + BC 边界 |
| [04](chapters/sop-04-stakeholder-value-modeling.md) | 干系人与价值建模（VDAD） | A | 价值排序 / 伦理评估 / 价值对齐 | 利益冲突、合规审查、积压需排序 | 干系人 + 价值登记册、两张地图 |
| [05](chapters/sop-05-architectural-refactorings.md) | 架构重构（AR-1~11） | B | 分解结构失配时增量演进 | 多团队共维一 BC、变更热点、拆过头 | 重构前后对照 + 决策记录 |
| [06](chapters/sop-06-systematic-decomposition.md) | 系统化服务分解 | B | 需要可辩护的候选切分方案 | 切分争议、棕地迁移启动 | 耦合准则标注 + 候选方案对比 |
| [07](chapters/sop-07-domain-driven-service-design.md) | 领域驱动服务设计 | C | 需求→原型端到端链路 | API-first 启动、polyglot 集成 | 领域模型 + 抽象契约 + 原型 |
| [08](chapters/sop-08-story-driven-service-design.md) | 故事驱动服务设计 | C | 集成故事起点的最小可行 API | 有消费方-提供方集成故事 | 集成故事 + 渐进契约 + 验收基线 |
| [09](chapters/sop-09-event-driven-service-design.md) | 事件驱动服务设计（AsyncMDSL） | C | 异步/事件密集集成设计 | 事件风暴完成、事件流交互 | 事件模型 + 端点映射 + 集成流 |
| [10](chapters/sop-10-map-decoration.md) | API 消息模式装饰（MAP） | C | 契约精化：表示/角色/职责/质量 | 表示语义不明、权衡需显式化 | 装饰后契约 + 力场权衡记录 |
| [11](chapters/sop-11-api-structure-analysis.md) | 存量 API 结构分析 | D | 既有 API 盘点/评审/治理 | 有 OpenAPI 类描述、语义歧义抱怨 | 原语分类 + 坏味道清单 + 修正建议 |
| [12](chapters/sop-12-model-code-validation.md) | 模型-代码一致性验证 | D | 防止模型与实现静默漂移 | 模型指导实现后、绕行修改出现 | 架构规则集 + CI 验证 + 处置记录 |
| [13](chapters/sop-13-method-engineering.md) | 方法工程与采纳（DPR） | E | 引入/裁剪任何方法与模板时 | 新方法提案、文书负担抱怨 | 方法元素卡 + 采纳决策记录 |
| [14](chapters/sop-14-quality-governance.md) | 质量管理与治理 | F | 契约声明 SLA/限流/计费 | 质量承诺不明、商业化/防滥用/配额 | 质量登记 + 限流计费声明 + 执行点映射 |
| [15](chapters/sop-15-versioning-evolution.md) | 版本演进 | F | 多层级版本与演进策略治理 | 破坏性变更、弃用/退役、承诺级别谈判 | 版本登记 + 演进策略 + 带外弃用时间表 |

完整版（含成功标准要点与来源列）见 [cheatsheet.md](cheatsheet.md)；决策规则细则见 [patterns.md](patterns.md)；术语见 [glossary.md](glossary.md)。

## 编排路线

各 SOP 在 BizDevOps 管线上的位置：Biz（战略 DDD / 系统分解：01、05、06）→ Dev（故事与事件风暴：02、03；API 设计：07–10 + 14、15；实现与集成守护：12）→ Ops（范围外，SLA/Rate Limit 指标回流 Monitoring）→ 反馈环（05 增量重构 + 13 方法裁剪）。

| 路线 | 顺序 |
|------|------|
| 绿地项目 | 13（定方法）→ 01/03（建模）→ 04（价值对齐）→ 05/06（演进分解）→ 07（端到端契约）→ 10（精化）→ 14/15（质量与演进）→ 12（守护） |
| API 产品 | 08（故事→契约）→ 10（模式精化）→ 14（质量治理）→ 12（守护） |
| 事件密集系统 | 03（风暴建模）→ 09（事件驱动设计）→ 10 → 14 → 12 |
| 棕地治理 | 11（盘点）→ 06（再分解）→ 05（增量重构）→ 15（演进治理）→ 12（守护） |

## 仓库结构

```text
.
├── SKILL.md                  # 入口：frontmatter 触发描述 + 如何使用 + SOP 索引 + 编排路线 + 范围边界
├── README.md                 # 本文件
├── cheatsheet.md             # 速查表完整版 + 场景→SOP 决策树 + 编排路线 + 14 条原则 + 反模式速查
├── patterns.md               # 决策规则库 ①–⑨：AR 目录 / 耦合准则 / MAP 速查 / P1–P4 与坏味道 /
│                             #   DDD→契约映射 / HTTP 动词→操作职责 / 神话破除 / 质量治理 / 版本演进
├── glossary.md               # 术语双语对照表（按英文原词排序，→ 指向 SOP 或框架编号）
├── chapters/                 # 15 个 SOP 正文，一章一文件，按需加载
│   ├── sop-01-rapid-ooad.md
│   ├── …
│   └── sop-15-versioning-evolution.md
└── dsl/                      # 版本化留档的官方语法文件（深度语法检查的第一手依据）
    ├── README.md             # 取证顺序 + 目录可否手改约定 + 维护命令 + SOP→语法规则对照
    ├── VERSIONS.md           # 版本账本（自动生成）：pin commit、字节/行数、blob sha1、sha256、release 对照
    ├── sync.py               # 同步 + 校验工具（版本信息的唯一 owner，仅标准库）
    ├── gen_index.py          # 规则索引生成器（被 sync.py 调用，也可单独运行）
    ├── cml/                  # ContextMappingDSL.xtext + TacticDDDLanguage.xtext + grammar-index.md + LICENSE
    └── mdsl/                 # APIDescription.xtext（含 AsyncMDSL 扩展）+ grammar-index.md + LICENSE
```

## 内容约定

**SOP 章节固定结构**（九段 + 折叠段）：何时启用 → 触发条件 → 完整步骤 → 使用示例 → 技术交付物 → 成功标准 → 反模式 → 关联 → 来源；文末附「📎 原始语法参考（CML/MDSL）」折叠段。

**两处语料的分工，冲突以 `dsl/` 为准**：

- `dsl/` 下的 `.xtext` 是**权威副本**（上游逐字节留档 + 规则索引 + pin commit 账本）——回答「能不能这么写」。
- 章节折叠段是**语料原文摘录**，用于追溯手册措辞来源、对接 BCM（`appfun-dev/bcm`）的 CUE 元模型——保留原样，含原有 typo。
- 「能写但表达不了什么」不在语法文件里，见 `patterns.md` ⑧⑨ 与 sop-14/15。

**校正记录**：语料与官方语法冲突时，摘录保留、正文改正，并在该章「来源」段写一条「校正记录」（例：`implements` 只接受 Domain/Subdomain、`ValueCluster.core` 为条件必填、`CargoPlaner`→`CargoPlanner`）。

**示例语法**：使用示例是原生 CML / MDSL（非 YAML 伪码），决策记录类字段用英文技术词汇；语言无法表达的治理信息（弃用时间表、评审记录）以带外记录段承载。

## CML / MDSL 语法取证

深度语法检查（这段能不能这么写、枚举取值域、子句顺序、行号依据）的固定顺序：

1. **定位**：查 [`dsl/cml/grammar-index.md`](dsl/cml/grammar-index.md) / [`dsl/mdsl/grammar-index.md`](dsl/mdsl/grammar-index.md)，按规则名拿到行区间。
2. **精读**：用 `read` 带 `offset`/`limit` 读对应 `.xtext` 区间（语法形态的唯一权威），或 `grep` 关键字面量反查规则。
3. **确认版本**：需要声明依据时引用 [`dsl/VERSIONS.md`](dsl/VERSIONS.md) 的 pin commit 与 blob sha1。
4. **对照章节折叠段**：只作语料追溯，不作语法依据。

**不要**：下载/解压上游仓库、读取 `/tmp` 或缓存副本、凭记忆断言语法形态或枚举取值域。

当前锁定版本（最近同步 2026-10-10T14:53:23+08:00）：

| DSL | 上游仓库 | 跟踪分支 | pin commit | 对照 release |
|-----|----------|---------|-----------|-------------|
| CML | [`ContextMapper/context-mapper-dsl`](https://github.com/ContextMapper/context-mapper-dsl) | `master` | `995f486a9cde`（2025-07-08） | `v6.12.0`，逐字节一致 |
| MDSL | [`Microservice-API-Patterns/MDSL-Specification`](https://github.com/Microservice-API-Patterns/MDSL-Specification) | `master` | `9da0bac0e613`（2025-01-23） | `v6.0.0`，逐字节一致 |

CML 主语法以 `with` 继承战术 DDD 语法，`ContextMappingDSL.xtext` 与 `TacticDDDLanguage.xtext` **必须成对使用**；MDSL 的 AsyncMDSL 扩展（channel / message broker / message endpoint / flow）已内联在唯一的 `APIDescription.xtext` 中。SOP 主题 → 语法规则对照表见 [`dsl/README.md`](dsl/README.md)。

## 维护

**保持语法文件最新**（需要网络访问 GitHub API；未认证时 `api.github.com` 限 60 次/小时，可用 `GITHUB_TOKEN` 提额）：

```bash
python3 dsl/sync.py --check                  # 只读：报告上游漂移 + 本地篡改（退出码 1 = 发现漂移/篡改）
python3 dsl/sync.py                          # 同步到上游分支 HEAD，逐字节校验，重生成账本与索引
python3 dsl/sync.py --dsl cml --pin <sha>    # 锁定/回退到指定上游 commit
shasum -a 256 dsl/*/*.xtext                  # 与 VERSIONS.md 的 sha256 对照
```

同步后的落地流程：`git diff dsl/` 复核语法变化 → 把影响落回相关章节（对照 `dsl/README.md` 的 SOP→规则表）→ 同一次提交里更新章节「语法形态核对」的日期与 pin commit。

**可否手改**：

| 文件 | 手改 |
|------|------|
| `dsl/*/*.xtext`、`dsl/*/grammar-index.md`、`dsl/VERSIONS.md`、`dsl/*/LICENSE` | ❌ 逐字节留档 / 自动生成；分歧时重跑 `sync.py`，不手工修补 |
| `dsl/sync.py`、`dsl/gen_index.py`、`dsl/README.md` | ✅ |
| `SKILL.md`、`cheatsheet.md`、`patterns.md`、`glossary.md`、`chapters/*.md`、`README.md` | ✅ 遵守[内容约定](#内容约定) |

**提交信息**：Conventional Commits，scope 用 `sop-NN` / `dsl` / `patterns`（例：`docs(sop-04): 校正 ValueCluster.core 必填性为"条件必填"`、`feat(dsl): 版本化留档 CML/MDSL 官方语法文件`）。

**改动手册时的自查**：SOP 九段结构完整？每处分解/模式决策指认了准则？语法断言以 `dsl/` 取证并标了核对日期与 pin commit？新增术语进了 `glossary.md`？新决策规则进了 `patterns.md` 而不是散落在章节里？

## 来源与致谢

- **CML Specification**（[contextmapper.org](https://contextmapper.org/)、[仓库](https://github.com/ContextMapper/context-mapper-dsl)）——§5–7 上下文映射与 BC 分型、§18–23 战术 DDD/故事/干系人/价值语法、§25–30 变换（Rapid OOAD、Story Splitting、VDAD、AR、耦合准则目录）、§39–40 事件风暴与 CQRS/事件溯源、§42 系统化分解、§43/§46 架构验证
- **MDSL Specification**（[仓库](https://github.com/Microservice-API-Patterns/MDSL-Specification)）——§2 设计目标、§3 与 MAP 的集成、§4 语言参考（含 AsyncMDSL）、§5 快速参考、§7 变换与重构、§10.1–10.5 服务设计博客摘要
- **Microservice API Patterns（MAP）**——[质量模式组](https://microservice-api-patterns.org/patterns/quality/)、[演进模式组](https://microservice-api-patterns.org/patterns/evolution/)、[站点](https://microservice-api-patterns.org/)
- **Kapferer & Zimmermann, *Domain-driven Service Design***（SummerSoC 2020）——DC-1~5 分解准则、DDD→契约映射 Table 2、分步 AR 应用流程 Fig.6、MDSL 设计原则
- **Zimmermann, *Dimensions of Successful Web API Design and Evolution***（ICWE 2020 keynote）——三维设计模型、五阶段管线、神话破除、Embedded Entity / Linked Information Holder 与 Pagination 模式卡
- **Serbout, Pautasso, Zdun, Zimmermann, *From OpenAPI Fragments to API Pattern Primitives and Design Smells***（APIace, EuroPLoP 2021）——P1–P4 结构原语、五坏味道、HTTP 动词↔操作职责映射
- **Zimmermann, *Design Practice Repository and Reference*（DPR）**（[ozimmer.ch](https://ozimmer.ch/)）——方法工程元模型、三规则、Enabling vs. Directing
- **两份 MDSL 语法调研**（Pricing Plan / Rate Limit；SLA / Versioning & Evolution）——含 CLI v6.0.0 实测探针、穷举证伪反例与已知限制
- **BCM**（`appfun-dev/bcm`）——章节折叠段的语料摘录用于对接其 CUE 元模型

第三方语法文件归属：CML © The Context Mapper Project Team（战术语法源自 Sculptor Project Team）；MDSL © Olaf Zimmermann。均为 Apache-2.0，许可证全文副本随 `dsl/cml/LICENSE`、`dsl/mdsl/LICENSE` 留档，上游内容未修改。

## 许可证

本仓库原创内容——手册正文（`SKILL.md`、`README.md`、`cheatsheet.md`、`patterns.md`、`glossary.md`、`chapters/`）与配套脚本（`dsl/sync.py`、`dsl/gen_index.py`）——采用 **Apache License 2.0**，全文见根目录 [LICENSE](LICENSE)。版权所有 © 2026 Ranger Huang。

`dsl/cml/`、`dsl/mdsl/` 下的第三方语法文件为**原样留档、未修改**的上游内容，各自适用其上游的 Apache-2.0，许可证全文副本随 `dsl/cml/LICENSE`、`dsl/mdsl/LICENSE` 保留；版权归属见[来源与致谢](#来源与致谢)。

## 相关

- 手册入口：[SKILL.md](SKILL.md)
- 一页速查：[cheatsheet.md](cheatsheet.md)
- 决策规则库：[patterns.md](patterns.md)
- 术语表：[glossary.md](glossary.md)
- 语法取证：[dsl/README.md](dsl/README.md) · [dsl/VERSIONS.md](dsl/VERSIONS.md)
