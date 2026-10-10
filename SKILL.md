---
name: bizdevops-modeling-sop
description: "BizDevOps 领域建模与服务设计 SOP 手册：15 个 SOP（何时启用/触发条件/步骤/交付物/成功标准）+ 综合速查表。覆盖快速 OOAD、故事拆分、事件风暴建模（ES/CQRS）、VDAD 价值建模、架构重构 AR-1~11、系统化服务分解、领域/故事/事件驱动服务设计、MAP 模式装饰、存量 API 分析、质量治理（SLA/Rate Limit/Pricing Plan）、版本演进（Versioning & Evolution）、模型-代码一致性验证、方法工程（DPR）。随仓库版本化留档 CML / MDSL 官方语法文件（dsl/cml、dsl/mdsl + 规则索引 + 版本账本），深度语法检查就地取证、无需下载上游仓库。当用户进行 DDD 建模、微服务拆分、上下文映射、API 契约设计、事件风暴、API 治理、质量/计费/限流声明、版本与弃用管理、架构演进决策，或需要核对 CML/MDSL 语法形态与枚举取值域时使用。工具中立方法论，不绑定 IDE/生成器。"
---

<!-- argument-hint: [SOP 编号、主题词或场景描述] -->

# BizDevOps 建模 SOP 手册

**来源**: 8 份方法论文档 | **SOP**: 15 个（组 A–F）| **生成**: 2026-10-10

## 如何使用

- **带场景**（"单体拆分"、"契约评审"）→ 按 [cheatsheet.md](cheatsheet.md) 决策树路由到 SOP，读对应章节文件，按五要素执行
- **带编号/主题**（`SOP-05`、"分页怎么选"）→ 直接读 `chapters/sop-*.md` 或 [patterns.md](patterns.md)
- **多 SOP 场景** → 按下方总流程与编排路线串联；一次只加载需要的章节文件
- **深度语法检查**（这段 CML/MDSL 能不能这么写、枚举取值域、子句顺序、行号依据）→ 走 [dsl/README.md](dsl/README.md)：先查 `dsl/<cml|mdsl>/grammar-index.md` 定位规则行区间，再用 `read` 带 `offset`/`limit` 精读本地 `.xtext`。**不要下载/解压上游仓库，也不要读临时目录里的副本**

SOP 文件固定结构：何时启用 → 触发条件 → 完整步骤 → 使用示例 → 技术交付物 → 成功标准 → 反模式 → 关联 → 来源；文末附原始 CML/MDSL 语法折叠段（语料原文摘录，供对接 BCM 的 CUE 元模型）——语法形态争议一律以 [dsl/](dsl/README.md) 的官方语法文件为准。

## SOP 总流程（BizDevOps 愿景）

各 SOP 在 BizDevOps 管线上的位置（愿景图：Zimmermann ICWE keynote，2019；工具中立，原图右栏工具仅为示例）：

| 阶段 | 活动 | SOP |
|------|------|-----|
| Biz | Strategic DDD（系统分解） | 01 / 05 / 06 |
| Dev | Story Telling/Mapping/Splitting · Event Storming · Tactic DDD | 02 / 03 |
| Dev | API Design：抽象→平台特定（contract first / code first） | 07 / 08 / 09 / 10 + **14（质量治理）/ 15（版本演进）** |
| Dev | Service Implementation & Integration | 12（模型-代码一致性守护） |
| Ops | CI/CD · Monitoring | 方法论范围外（BaU）；SLA/Rate Limit 指标接入 Monitoring 反馈 |
| 反馈环 | Ops / API Design → Strategic DDD（愿景图虚线） | 05 增量重构 + 13 方法裁剪 |

---

## 核心框架（F1–F10 精要）

- **F1 三维设计模型** — 评审三问：Context matters（上下文界定了吗？没有普适设计）、Contracts rule（契约先行吗？框架会过时，契约长存；HTTP 不是唯一答案）、Components contain（每服务做买/租/建决策）
- **F2 五阶段管线** — 故事/用例 → 分析模型（子域、实体）→ 设计模型（BC、聚合；FEATURE/SYSTEM 分型）→ 服务契约 → 实现。人不可替代 = 领域分析 + 模式装饰决策
- **F3 分解准则体系** — DC-1 业务实体、DC-2 用例、DC-3 属主/团队（Conway）、DC-4 变更可能性（Parnas：隔离易变者）、DC-5 泛化 NFR；扩展 14 项耦合准则目录（优先级 XS~XL）。**分解决策必须指认至少一条准则**
- **F4 架构重构目录（AR-1~11）** — 结构类 AR-1~8（按实体/特性/属主/易变性/内聚拆分、合并聚合/BC、提取共享内核）；关系类 AR-9~11（中止伙伴关系 3 策略、SK↔P 互转）。每个 AR 有前置条件与逆操作
- **F5 AR 分步流程** — 初始 BC → AR-2 特性成型 → AR-3 属主拆分 → AR-4 易变性提取 → AR-5 内聚微调 ⇄ AR-7 合并回退；聚合层 AR-1 ⇄ AR-6。**分解是持续过程而非一次性事件**
- **F6 DDD→契约映射** — BC→契约（一 BC 一服务一契约）、聚合→端点、方法→操作、参数/返回类型→数据类型、上下游 BC→提供方/消费方
- **F7 MAP 模式语言** — EIP 止步处（消息载荷结构）。刻板印象（ID/Link/Data/Metadata）、端点角色（Information Holder 特化 / Processing Resource）、操作职责（Retrieval / State Creation / State Transition / Computation）；核心权衡 Embedded Entity vs Linked Information Holder、Pagination 游标 vs 偏移
- **F8 API 结构原语与坏味道** — 管线：API 描述→资源树→碎片化→双重聚类→原语识别。P1 Enumerable / P2 Appendable / P3 Collection / P4 Mutable Collection；五坏味道：Create without Delete、Delete without Create、Ambiguous POST/PUT、Write-Only
- **F9 VDAD** — 干系人（从故事角色导出）→ 价值登记册 → 故事估值（含伦理）→ 干系人地图 + 价值影响图
- **F10 DPR 方法工程** — 角色执行活动，技术与模板支持，产出工件。三规则：上下文至上、有疑就删、目的高于合规。**Enabling（导游）而非 Directing（律师）**

---

## SOP 综合速查表

| # | SOP | 组 | 何时启用 | 关键触发信号 | 章节 |
|---|-----|----|----------|--------------|------|
| 01 | 快速 OOAD 建模 | A | 从书面需求快速推导初始分解 | 有故事/用例清单、无 BC 结构 | [sop-01](chapters/sop-01-rapid-ooad.md) |
| 02 | 用户故事拆分 | A | 大故事拆为可独立交付薄片 | 复合动词（manage=create+edit+cancel）、估算超阈值 | [sop-02](chapters/sop-02-story-splitting.md) |
| 03 | 事件风暴结果建模 | A | 工作坊产出固化为精确模型 | 事件风暴完成、白板将丢 | [sop-03](chapters/sop-03-event-storming-modeling.md) |
| 04 | 干系人与价值建模 | A | 价值排序/伦理评估/价值对齐 | 利益冲突、合规审查、积压需排序 | [sop-04](chapters/sop-04-stakeholder-value-modeling.md) |
| 05 | 架构重构（AR） | B | 分解结构失配时增量演进 | 多团队共维一 BC、变更热点、拆过头 | [sop-05](chapters/sop-05-architectural-refactorings.md) |
| 06 | 系统化服务分解 | B | 需要可辩护的候选切分方案 | 切分争议、棕地迁移启动 | [sop-06](chapters/sop-06-systematic-decomposition.md) |
| 07 | 领域驱动服务设计 | C | 需求→原型端到端链路 | API-first 启动、polyglot 集成 | [sop-07](chapters/sop-07-domain-driven-service-design.md) |
| 08 | 故事驱动服务设计 | C | 集成故事起点的最小可行 API | 有消费方-提供方集成故事 | [sop-08](chapters/sop-08-story-driven-service-design.md) |
| 09 | 事件驱动服务设计 | C | 异步/事件密集集成设计 | 事件风暴完成、事件流交互 | [sop-09](chapters/sop-09-event-driven-service-design.md) |
| 10 | API 消息模式装饰 | C | 契约精化：表示/角色/职责/质量 | 表示语义不明、权衡需显式化 | [sop-10](chapters/sop-10-map-decoration.md) |
| 11 | 存量 API 结构分析 | D | 既有 API 盘点/评审/治理 | 有 OpenAPI 类描述、语义歧义抱怨 | [sop-11](chapters/sop-11-api-structure-analysis.md) |
| 12 | 模型-代码一致性验证 | D | 防止模型与实现静默漂移 | 模型指导实现后、绕行修改出现 | [sop-12](chapters/sop-12-model-code-validation.md) |
| 13 | 方法工程与采纳 | E | 引入/裁剪任何方法与模板时 | 新方法提案、文书负担抱怨 | [sop-13](chapters/sop-13-method-engineering.md) |
| 14 | 质量管理与治理 | F | 契约声明 SLA/限流/计费 | 质量承诺不明、商业化/防滥用/配额需求 | [sop-14](chapters/sop-14-quality-governance.md) |
| 15 | 版本演进 | F | 多层级版本与演进策略治理 | 破坏性变更、弃用/退役、承诺级别谈判 | [sop-15](chapters/sop-15-versioning-evolution.md) |

完整版（含交付物/成功标准/来源列）见 [cheatsheet.md](cheatsheet.md)。

## 编排路线

- **绿地项目**: 13（定方法）→ 01/03（建模）→ 04（价值对齐）→ 05/06（演进分解）→ 07（端到端契约）→ 10（精化）→ 14/15（质量与演进）→ 12（守护）
- **API 产品**: 08（故事→契约）→ 10 → 14（质量治理）→ 12
- **事件密集系统**: 03（风暴固化）→ 09 → 10 → 14 → 12
- **棕地治理**: 11（盘点）→ 06（再分解）→ 05（增量重构）→ 15（演进治理）→ 12

## 关键原则（14 条一句话版）

上下文至上 · 契约长存 · 组件约束成本（买/租/建）· 赋能而非指令 · 有疑就删 · 部分规格支持敏捷建模 · 一模型多契约 · 分解必须可辩护 · 组织与技术边界共演（Conway）· 隔离易变者（Parnas）· 模型-代码鸿沟需主动守护 · 无故事不操作 · 质量承诺必须可执行（子句无校验器支撑时以评审+运行时监控兜底）· 演进策略必须显式声明（默认 undisclosed 即治理真空）

---

## 主题索引

- **架构重构/AR/拆分合并** → sop-05；**架构验证/模型-代码鸿沟** → sop-12
- **事件风暴/CQRS/事件溯源** → sop-03；**事件驱动集成/消息路由** → sop-09
- **服务分解/耦合准则/Conway** → sop-06；**单体拆分** → sop-11 → 06 → 05
- **契约设计/API-first/polyglot** → sop-07、08；**契约精化/分页/嵌入 vs 链接** → sop-10
- **故事拆分** → sop-02；**快速建模/子域推导** → sop-01；**价值/干系人/伦理** → sop-04
- **存量 API/坏味道/资源树** → sop-11；**MAP/刻板印象/端点角色** → sop-10
- **SLA/限流/计费计划/质量治理/SLO** → sop-14；**版本演进/弃用/语义化版本/EvolutionStrategy** → sop-15
- **模板/方法引入/裁剪/Y-statement** → sop-13

## 支持文件

- [cheatsheet.md](cheatsheet.md) — 速查表完整版 + 场景→SOP 决策树 + 原则/反模式速查
- [patterns.md](patterns.md) — 决策规则库：AR 目录、耦合准则、MAP 速查、P1–P4 判定、坏味道修正、DDD→契约映射、质量治理与版本演进规则、神话破除表
- [glossary.md](glossary.md) — 术语双语对照表
- [dsl/README.md](dsl/README.md) — 随仓库版本化的 **CML / MDSL 官方语法文件**（`dsl/cml/`、`dsl/mdsl/`）+ 规则索引（规则名→行区间）+ 版本账本 [dsl/VERSIONS.md](dsl/VERSIONS.md)（pin commit / blob sha1 / sha256）；深度语法检查的第一手依据，`python3 dsl/sync.py --check` 校验是否落后上游

## 范围与边界

- **工具中立方法论手册**：不含 IDE 插件/生成器/CLI 命令；落地时结合项目自身的建模语言与校验工具
- 原始 CML/MDSL 语法有两处：**权威副本**在 [dsl/](dsl/README.md)（上游 `.xtext` 逐字节留档 + 规则索引 + pin commit 账本，`python3 dsl/sync.py` 维护最新）；各 SOP 文末折叠段是**语料原文摘录**，用于对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型与追溯措辞来源。两者冲突以 `dsl/` 为准
- 排除：Context Mapper Generators（官方文档 §32–38）、JHipster 教程、工具安装配置
- 稳定性提示：故事拆分在源文档中为 PoC（仅按动词拆分）；耦合准则目录源自已停用工具，方法学仍有效——按 SOP-13 三规则自行裁剪
- 质量/版本子句的表达力实证边界（测量值仅整数、无 deprecated/sunset 语法、金额与客户端差异化配额不可表达等）见 sop-14/15 与 patterns.md⑧⑨；不可表达部分一律带外治理
