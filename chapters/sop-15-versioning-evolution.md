# SOP-15: 版本演进（Versioning & Evolution）

> **定位**: 为已发布/多方消费的 API 契约建立多层级版本标识、选定演进策略并治理兼容性与弃用退役，使"契约长存"下的每次变更都可定位、可沟通、可回退 | **组**: F（质量与演进治理） | **主要来源**: 《MDSL - SLA 与版本演进（Versioning & Evolution）语法调研》

## 何时启用

当 API 契约**已发布或被多方消费**、且会随时间变更时启用——需要为契约建立版本标识、选定演进策略、治理兼容性与弃用退役。

核心前提（与 [SOP-10](sop-10-map-decoration.md) 共用）：**契约长存**——框架与基础设施来来去去，API 契约长存；演进决策在契约层做，不在实现层做。SOP-10 治理契约的**结构与语义**（表示元素/端点角色/操作职责），本 SOP 治理契约的**时间维度**（版本/演进策略/兼容性/弃用）。

关键认知：版本号**不是**一个只挂在顶层的单一数字。它可以挂载在多个层级（API 整体 / 运行时提供方 / 端点契约 / 操作 / 数据元素 …），各层级**可独立演进**（一个操作可以比它所属的契约更频繁地打补丁）。本 SOP 的方法论从 MDSL（契约建模 DSL）的版本与演进语法实证中提炼，但表述工具中立——具体语法见文末折叠段。

## 触发条件

满足任一即应启动：

1. **契约即将对外发布或已被多方消费** — 需要稳定的版本标识与演进承诺；
2. **准备做破坏性变更** — 删除/重命名操作、改字段语义、把可选元素改为必填；
3. **需要决定版本并存与下线策略** — 同时维护几个版本？旧版本何时退役？
4. **消费方抱怨不可预期** — "不知道接口什么时候变、变了会不会破坏我"；
5. **存量 API 盘点（[SOP-11](sop-11-api-structure-analysis.md)）发现版本语义缺失或不一致**；
6. **消费方需要在报文里读取版本** — 做兼容路由/灰度判断（报文层版本标识符）；
7. **结构演进（[SOP-05](sop-05-architectural-refactorings.md) 的 AR）触发契约变更** — 分解结构变化需对应版本动作。

## 完整步骤

### 步骤 1：确定版本标识方案（语义化版本）

- 采用**语义化三段号** `major.minor.patch`（x.y.z）：major = 破坏性变更、minor = 兼容性新增、patch = 兼容性修复。
- **关键实证**：建模语言通常**不解析、不校验**版本号格式——版本号本质是一个**字符串**令牌（MDSL 的语义化版本标识符就是一个字符串，语法注释称"格式可由 API linter 检查"，但实测 linter 并未实现该检查）。
- 推论：版本方案（何时升 major/minor/patch、是否带 `v` 前缀）必须是**团队书面约定 + 评审/linter 把关**，不能指望语言强制；版本号必须**显式书写**（带引号/明确字段），裸写会歧义甚至报错。

### 步骤 2：选择版本挂载层级（多层级独立演进）

版本可挂载的建模层级（完整清单见折叠段）：**API 描述整体 / 数据契约 / 关系类型 / 事件类型 / 命令类型 / 端点契约 / 操作 / 运行时提供方 / 客户端 / 网关 / 集成场景**等。要点：

- 版本标注是**逐元素可选**的：有的操作声明版本、有的不声明（官方示例中同一契约下两个操作，一个有版本一个没有）。
- 不同层级**独立演进**：操作级补丁版本可以高于其所属端点契约的版本。
- **类层 vs 实例层分工**：版本号挂在"类层"（端点契约/数据契约/操作）；运行时"实例层"（端点实例）通常**不挂版本号，而挂治理策略**（见步骤 3）。
- 决策：至少为 **API 整体 + 端点契约** 声明版本；高频变更的**操作/数据元素**按需独立版本化。

### 步骤 3：选择演进策略（演进策略枚举）

从演进策略枚举中为契约/提供方选定一个**承诺级别**（用 MAP 演进模式名表述）：

| 演进策略（MAP 模式名） | 对消费方的承诺 | 典型适用 |
|---|---|---|
| Eternal Lifetime Guarantee（永久生命周期保证） | 永不破坏或停用已发布版本 | 平台级公共 API |
| Limited Lifetime Guarantee（有限生命周期保证） | 固定时间窗内不破坏；每个版本标**过期日期** | 有明确支持周期的 API |
| Two in Production（双版本并存） | 同时部署支持**两个**版本，滚动重叠地更新与退役 | 需要平滑迁移的 API |
| Aggressive Obsolescence（激进淘汰） | 公布**下线日期**；旧部分仍可用但**不再推荐**；到期移除 | 快速迭代/内部 API |
| Experimental Preview（实验性预览） | 尽力而为，**不承诺**功能/稳定/长存 | 沙箱/试验性接口 |
| Other Strategy（自定义策略） | 逃生舱：自定义，语言不约束 | 上述都不 fit |
| Undisclosed（未披露，**默认值**） | 未声明策略时的缺省 | —（应尽量避免停留在此） |

- **三级挂载**：策略可挂在**提供方级 / 端点级 / 网关级**，三者**可共存且语义独立**——单个端点可以比整个提供方更激进地淘汰。
- **实证教训**：三个挂载点的关键字在语言中**并不统一**（提供方级、端点级、网关级各用不同前缀）——方法论要求：**策略声明必须写清挂载层级**，避免"谁比谁更激进"的歧义（具体关键字见折叠段）。

### 步骤 4：兼容性判定与破坏性变更管理

- **判定规则**：破坏性变更 → 升 **major**；兼容性新增（尤其新增**可选**元素）→ 升 **minor**；兼容性修复 → 升 **patch**。
- **控制破坏面**：利用表示元素的**基数标记**（必选/可选，见 [SOP-10](sop-10-map-decoration.md) 步骤 1）——新增元素尽量标记为**可选**，避免把既有消费方"打挂"。
- **每个破坏性变更必须产出**：① 影响清单（哪些消费方/操作/字段受影响）；② 版本动作（major 提升记录）；③ 消费方**迁移计划**。
- **与 MAP 演进模式映射**：报文层版本标识符 + 模型层语义化版本 + 上述五个承诺级策略，构成完整的演进模式工具箱（映射详表见折叠段与来源）。

### 步骤 5：弃用与退役治理（带外机制）

- **关键实证**：MDSL **没有**元素级弃用/下线语法——无法标记"某操作/某字段于某日弃用"，也**无法携带具体下线日期**。表达"淘汰"的唯一手段是**策略级**的 Aggressive Obsolescence（激进淘汰），它是策略声明而非元素标记。
- **方法论补偿（必须显式做）**：用**带外（out-of-band）机制**补齐语言缺口：
  1. **弃用清单**：哪个元素、何时宣布弃用、计划下线日期；
  2. **通知期**：提前多久通知消费方（如 ≥ 90 天）；
  3. **调用方监控**：用遥测/日志确认"谁还在用被弃用元素"，迁移完成方可退役；
  4. **日期/条款承载**：具体下线日期写进**自由文本**（条款条件/通知字段）或注释——语言层表达不了。
- **退役前置**：监控证据显示无活跃消费方，方可移除。

### 步骤 6：数据层版本标记（报文层版本标识符）

- 除模型层的版本号元数据外，可在**表示元素**上打"版本标识符"构造型（MAP *Version Identifier* 模式），标注消息体/参数中**承载版本号的那个字段**。
- 对应模式解法："在端点地址、协议头或消息载荷中添加一个元数据元素"作为显式版本指示符。
- **与模型层互补**：模型层版本号是**建模元数据**（供人读/模型查询）；报文层版本标识符是**消费方可见字段**（供兼容路由/灰度判断）。
- 决策：当消费方需要**在报文里读到版本**时，用报文层标识符；否则模型层版本号即可。

### 步骤 7：演进评审与回归验证（联动 SOP-12）

- 每次版本提升/策略变更过**演进评审**，核对：每个破坏性变更有 major + 迁移计划？每个弃用项有通知期 + 调用方监控证据？演进策略在提供方/端点层级一致或差异有书面理由？
- **联动 [SOP-12](sop-12-model-code-validation.md)**：版本/演进决策同样要防"声明与真实行为漂移"——把"破坏性变更必须升 major""弃用必须有通知期"转写为可校验规则，纳入构建期守护。
- **元数据质量需实测验证（实证教训）**：不要假设建模语言会校验或正确传播版本元数据。实测发现：① 版本号传播到下游接口描述文档时可能有**格式缺陷**（带引号的字符串令牌被原样写入，产生**双重引号**）；② 端点/操作级版本**可能不传播**到下游，精细版本化只停留在模型里。→ 版本元数据流入下游前必须**实测**并必要时后处理。

## 使用示例

订单管理 API 的版本演进（原生 MDSL + 带外记录；改写自语料 §4.1 那份经 CLI v6.0.0 实测编译通过的综合示例，为聚焦版本与演进已略去 SLA 模板——SLA 形态见 [SOP-14](sop-14-quality-governance.md)）。`version` 在语法中共有 **14 个可挂载位置**，逐元素可选、各层级独立演进：

```mdsl
API description OrderManagementAPI version "2.1.0"      // 步骤 1：API 整体语义化版本（STRING，显式书写）
usage context PUBLIC_API for FRONTEND_INTEGRATION

// 数据契约可独立版本化
data type OrderId version "1.0.0" D<string>
data type OrderRecord version "1.2.0" {OrderId, "total":D<int>, "currency":D<string>}

// 端点契约（类层）与操作（各自带版本位）
endpoint type OrderContract version "2.1.0"
  serves as INFORMATION_HOLDER_RESOURCE
  exposes
    operation createOrder version "2.1.0"
      with responsibility STATE_CREATION_OPERATION in REQUEST_REPLY conversation
      expecting payload OrderRecord
      delivering payload OrderId
    operation lookupOrder version "2.1.1"                // 操作级补丁版本，可比契约更高
      with responsibility RETRIEVAL_OPERATION in REQUEST_REPLY conversation
      expecting payload OrderId
      delivering payload OrderRecord
    operation listOrders                                 // version 逐元素可选，此处不提供
      with responsibility RETRIEVAL_OPERATION
      expecting payload D<string>
      delivering payload OrderRecord*

// 步骤 3：演进策略三级挂载（endpoint / provider / gateway），可共存且语义独立
API provider OrderProviderProd version "2.1.0"
  offers OrderContract
    at endpoint location "https://api.order.example.com:443/v2"
    via protocol HTTP binding resource OrderResource at "/orders"
    endpoint governance TWO_IN_PRODUCTION                // 端点级治理
  provider governance LIMITED_GUARANTEED_LIFETIME        // provider 级治理

// under conditions 与 with provider SLA 互斥（本例聚焦版本，未挂 SLA）
API provider OrderProviderLegacy
  offers OrderContract
    at endpoint location "https://api.order.example.com:443/v1"
    via protocol HTTP binding resource OrderResourceLegacy at "/orders"
    endpoint governance AGGRESSIVE_OBSOLESCENCE          // 旧版本激进淘汰
  under conditions "See https://order.example.com/terms.html"
  provider governance AGGRESSIVE_OBSOLESCENCE

API provider OrderProviderSandbox
  offers OrderContract
    at endpoint location "https://sandbox.order.example.com:443/v2"
    via protocol HTTP binding resource OrderResourceSandbox at "/orders"
    endpoint governance EXPERIMENTAL_PREVIEW
  provider governance EXPERIMENTAL_PREVIEW

API client OrderMobileApp version "2.1.0"
  consumes OrderContract
  from OrderProviderProd
  via protocol HTTP

API gateway OrderGateway version "2.1.0"
  offers OrderContract
    at endpoint location "https://gateway.order.example.com:443/v2"
    via protocol HTTP binding resource GatewayOrderResource
    endpoint governance TWO_IN_PRODUCTION
  consumes OrderContract
  from OrderProviderProd
  via protocol HTTP
  evolution governance TWO_IN_PRODUCTION     // gateway 用 evolution governance，且必须写在 consumes 之后
```

```yaml
version_register:                    # 步骤 2：层级 × 当前版本（14 个 version 挂载位中的 7 类）
  versioning_scheme: "Semantic Versioning major.minor.patch（STRING；语言不强制校验，团队书面约定）"
  entries:
    - { level: API_DESCRIPTION, element: OrderManagementAPI, version: "2.1.0" }
    - { level: DATA_TYPE,       element: OrderId,            version: "1.0.0" }
    - { level: DATA_TYPE,       element: OrderRecord,        version: "1.2.0" }
    - { level: ENDPOINT_TYPE,   element: OrderContract,      version: "2.1.0" }
    - { level: OPERATION,       element: createOrder,        version: "2.1.0" }
    - { level: OPERATION,       element: lookupOrder,        version: "2.1.1" }       # 操作级补丁，可比契约更高
    - { level: OPERATION,       element: listOrders,         version: NOT_DECLARED }  # 未提供 version 子句
    - { level: PROVIDER,        element: OrderProviderProd,  version: "2.1.0" }
    - { level: CLIENT,          element: OrderMobileApp,     version: "2.1.0" }
    - { level: GATEWAY,         element: OrderGateway,       version: "2.1.0" }

evolution_strategy_consistency:      # 步骤 3：三级策略共存时的一致性说明（差异须有书面理由）
  - "OrderProviderProd：endpoint 级（TWO_IN_PRODUCTION）比 provider 级（LIMITED_GUARANTEED_LIFETIME）更具体——单端点可比整体更激进"
  - "OrderProviderLegacy：endpoint 级与 provider 级一致（AGGRESSIVE_OBSOLESCENCE）"
  - "OrderProviderSandbox：两级一致（EXPERIMENTAL_PREVIEW）"

breaking_change_impact:              # 步骤 4（示例行，展示交付物结构）
  - change: "lookupOrder 响应拟新增字段"
    compatibility: COMPATIBLE_ADDITIVE      # 标记为可选；若转必填则为 BREAKING
    version_action: MINOR_BUMP              # 2.1.1 → 2.2.0；转必填则 MAJOR_BUMP
    affected_clients: [OrderMobileApp]
    migration_plan: "新增字段先标记为可选，灰度一个版本、监控读取方后再评估转必填"

deprecation_schedule:                # 步骤 5：语言无元素级 deprecated / sunset 语法 → 一律带外
  - element: "OrderProviderLegacy（/v1 端点，AGGRESSIVE_OBSOLESCENCE）"
    deprecation_announced: "T0"
    notice_period: ">= 90 days"
    planned_sunset: "T0 + 180 days"
    date_carrier: "under conditions 自由文本 + 带外弃用清单（语言层无法表达具体日期）"
    caller_monitoring: "遥测确认 /v1 调用量降至阈值下、无活跃消费方，方可退役"

payload_version_marker:              # 步骤 6：报文层版本标识符（消费方可见）
  pattern: Version_Identifier        # MAP 构造型：版本标记同时进 API 描述与交换消息
  placement: [message payload, protocol header, endpoint location]
  relation_to_model_layer: "互补——模型层 version 是建模元数据，报文层标识符供消费方做兼容路由"

evolution_review:                    # 步骤 7（联动 SOP-12 回归验证）
  - { item: "每个破坏性变更有 major 提升 + 迁移计划",                verdict: PASS }
  - { item: "弃用项有通知期 + 调用方监控证据",                        verdict: PASS }
  - { item: "演进策略在 provider / endpoint 层级一致或差异有书面理由", verdict: PASS }
  - { item: "版本元数据下游传播已实测（防双重引号 / 丢失）",           verdict: NEEDS_POSTPROCESS_CHECK }
```

## 技术交付物

1. **版本标识登记**：层级 × 当前版本（API/数据契约/端点契约/操作/提供方…）；
2. **演进策略声明**：策略 × 挂载层级（提供方/端点/网关），含层级间一致性说明；
3. **破坏性变更影响清单**：变更 → 受影响消费方/操作/字段 → 版本动作（major）→ 迁移计划；
4. **弃用/退役时间表（带外）**：弃用清单 + 通知期 + 调用方监控证据 + 计划下线日；
5. **兼容性评审记录**：演进评审结论（联动 SOP-12 的回归验证）。

## 成功标准

- [ ] 每个对外契约元素有明确的**版本标识方案**（语义化三段号），且方案为团队书面约定（不依赖语言校验）；
- [ ] 版本挂载层级至少覆盖 **API 整体 + 端点契约**；高频变更的操作/数据元素按需独立版本化；
- [ ] **每个破坏性变更**有 major 版本提升记录 + 消费方迁移计划；
- [ ] **演进策略在提供方与端点层级一致**，或差异有书面理由；
- [ ] **所有弃用项**均有通知期 + 调用方监控证据（退役前确认无活跃消费方）；
- [ ] 弃用/退役的**具体日期通过带外机制承载**（语言层无元素级弃用语法时的补偿）；
- [ ] 版本元数据**下游传播已实测验证**（无双重引号/丢失等格式缺陷流入下游文档）。

## 反模式

| 反模式 | 为何失败 |
|--------|----------|
| 版本号只挂顶层 | 子层级（操作/数据元素）的破坏性变更不可见；消费方无法定位"到底哪个操作变了" |
| 无元素级弃用机制却直接删操作 | 语言缺弃用/下线语法**不是**静默删除的借口；消费方在毫无通知下被破坏 |
| 演进策略声明与真实变更行为不符 | 声明"永久生命周期"却频繁破坏性变更 → 策略沦为装饰，消费方失去信任依据 |
| 依赖语言校验版本格式 | 建模语言通常不解析/不校验版本号（只是一个字符串）；格式约束必须靠外部 linter/评审 |
| 元数据质量不实测就信 | 版本号传播到下游文档可能有格式缺陷（双重引号）/子层级版本不传播；不实测就假设正确 |
| 策略挂载层级含糊 | 同一策略在提供方/端点/网关语义独立；不写清挂载层级 → "谁比谁更激进"歧义 |
| 新增元素默认必填 | 扩大对既有消费方的破坏面；兼容性扩展应优先标记为**可选**（用基数标记） |

## 关联

- **编排位置（棕地治理）**: [SOP-11](sop-11-api-structure-analysis.md)（盘点）→ [SOP-06](sop-06-systematic-decomposition.md)（再分解）→ [SOP-05](sop-05-architectural-refactorings.md)（增量重构）→ **15**（版本演进）→ [SOP-12](sop-12-model-code-validation.md)（守护）；见 [../SKILL.md](../SKILL.md)
- [SOP-12](sop-12-model-code-validation.md) — 步骤 7 演进评审/回归验证联动；版本与演进决策同样需防"声明-行为漂移"
- [SOP-10](sop-10-map-decoration.md) — 互补：SOP-10 管契约**结构/语义**装饰（其步骤 5 演进检查），本 SOP 管契约**时间维度**；表示元素基数标记（必选/可选）是兼容性扩展的共用机制
- [SOP-14](sop-14-quality-governance.md) — 同属组 F（质量与演进治理）：SLA/质量目标治理见该章，演进策略/版本治理见本章
- [SOP-05](sop-05-architectural-refactorings.md) — 结构演进（AR）触发契约版本提升；分解结构变化 → 端点/操作版本动作

## 来源

- 《MDSL - SLA 与版本演进（Versioning & Evolution）语法调研》：§三（版本号/挂载清单/示例六~九/演进策略枚举/无元素级弃用语法/与 MAP 演进模式映射表）、§四（综合示例与两条实测约束）、§五 5.2/5.4/5.7（语法摘录）、§六（已知限制：版本号下游传播缺陷与元数据格式 Bug）
- MAP 演进模式官方页（模式映射依据，实测 evolution 组仅 7 个已发布模式）：[Evolution 索引](https://microservice-api-patterns.org/patterns/evolution/)、[Semantic Versioning](https://microservice-api-patterns.org/patterns/evolution/SemanticVersioning.html)、[Version Identifier](https://microservice-api-patterns.org/patterns/evolution/VersionIdentifier.html)、[Two in Production](https://microservice-api-patterns.org/patterns/evolution/TwoInProduction.html)、[Aggressive Obsolescence](https://microservice-api-patterns.org/patterns/evolution/AggressiveObsolescence.html)、[Experimental Preview](https://microservice-api-patterns.org/patterns/evolution/ExperimentalPreview.html)、[Limited Lifetime Guarantee](https://microservice-api-patterns.org/patterns/evolution/LimitedLifetimeGuarantee.html)、[Eternal Lifetime Guarantee](https://microservice-api-patterns.org/patterns/evolution/EternalLifetimeGuarantee.html)（注：Version Arrow、Aggressively Communicate Version 两页实测未发布）
- 一手源码：仓库 `Microservice-API-Patterns/MDSL-Specification`（master 分支，实测 HEAD `9da0bac0e6133b8a69131925e38bc98e63e20af2`，2025-01-23）；官方语法文件——版本号定义 #L66、演进策略枚举 #L653-L658、端点契约/操作版本位 #L233-L272、版本标识符构造型 #L187-L201、Provider/EndpointInstance #L436-L457；OpenAPI 转换器（版本传播与引号 Bug）`MDSL2OpenAPIConverter.java` #L62/#L131-L133（深度语法核对改读仓库内权威副本：MDSL `../dsl/mdsl/APIDescription.xtext`，规则名→行区间查对应 `grammar-index.md`，pin commit 与 sha256 见 `../dsl/VERSIONS.md`），不再下载/解压上游仓库或读临时副本；本章引用的 `.xtext` 行号锚点以该 pin commit 为准
- 官方示例 `.mdsl`：`CRMServiceContract.mdsl`（三层版本号）、`ProviderSLAClientExample.mdsl`（治理三级挂载）、`Skeleton.mdsl` / `CRMFromGitPages.mdsl`（版本占位符模板）；`changelog.md`（版本演进史）
- 使用示例的语法基准：主源 §4.1「综合示例」——其等价结构（全部 5 种 `SLAType`、全部 7 种 `EvolutionStrategy`、三级 `version`、`rate plan` 三值、`rate limit` 三分支、LandingZone、provider / client / gateway）已在 CLI v6.0.0 下编译通过（`probe/t1_all_sla_types.mdsl`）。本次改写略去 SLA 模板、只保留版本与演进相关子句，并添加中文步骤注释；原 YAML 的中文键改为英文字段并拆成 6 段记录（`version_register` / `evolution_strategy_consistency` / `breaking_change_impact` / `deprecation_schedule` / `payload_version_marker` / `evolution_review`），其中弃用时间表与评审记录属**语言无法表达的带外机制**

---
<details>
<summary>📎 原始 MDSL 语法参考（Versioning & Evolution）— 点击展开</summary>

以下片段忠实摘自语料原文（《MDSL - SLA 与版本演进（Versioning & Evolution）语法调研》），供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考。每一非空行与源文件逐字一致（空白归一化）；语料原有 typo 保留。上方「使用示例」的 MDSL 段以主源 §4.1 那份经 CLI v6.0.0 实测编译通过的综合示例为基准（略去 SLA 模板以聚焦版本与演进）；摘录按约定保留——§3.3 示例六（多层级版本号）与 §3.6 示例八（治理三级挂载）是示例各段的直接依据。两条实测约束已写入示例注释：`under conditions` 与 `with provider SLA` 互斥；`API gateway` 的 `evolution governance` 必须写在 `consumes` 之后。

**① 版本号定义（L66）——语义化版本标识符就是一个 STRING（格式不由语言校验）**：

```xtext
// APIDescription.xtext:66
SemanticVersioningIdentifier: STRING; // format could be checked by API linters
```

**② version 挂载位置清单（§3.2，14 处，逐元素可选；实例层不挂版本号而挂治理）**：

`version` 子句在语法中出现 **14 处**，均为 `('version' svi=SemanticVersioningIdentifier)?`：

| # | 建模层级 | 语法规则 | 行号 | 官方示例佐证 |
|---|---|---|---|---|
| 1 | `API description` | `ServiceSpecification` | 32 | `API description SampleCustomerManagementAPI version "1.0.0"` |
| 2 | `data type` | `DataContract` | 72 | `data type BooleanExpression version "1" D<bool>` |
| 3 | `relation type` | `LinkContract` | 80 | — |
| 4 | `event type` | `EventType` | 92 | 注释：`// version can only be given if structure is there` |
| 5 | `command type` | `CommandType` | 102 | — |
| 6 | `endpoint type` | `EndpointContract` | 235 | `endpoint type CustomerManagementContract version "1.0.0"` |
| 7 | `event`（引用实例） | `Event` | 253 | — |
| 8 | `operation` | `Operation` | 259 | `operation lookupSingleCustomer version "1.0.1"` |
| 9 | `API provider` | `Provider` | 441 | — |
| 10 | `API client` | `Client` | 665 | — |
| 11 | `API gateway` | `Gateway` | 743 | — |
| 12 | `integration scenario` | `IntegrationScenario` | 782 | 实验性 |
| 13 | `integration story` | `IntegrationStory` | 792 | 实验性 |
| 14 | `orchestration` | `Orchestration` | 829 | 实验性 |

**注意**：`EndpointInstance`（`at endpoint location ...`）**没有** `version` 子句——它只有 SLA 和 governance。这与"实例层用治理策略、类层用版本号"的分工一致。

**③ 演进策略枚举（L653-658）与三级挂载关键字（provider/endpoint/gateway，关键字不统一）**：

```xtext
// APIDescription.xtext:653-658
// **** evolution

enum EvolutionStrategy: 
	ETERNAL_LIFETIME | LIMITED_GUARANTEED_LIFETIME | TWO_IN_PRODUCTION | AGGRESSIVE_OBSOLESCENCE | EXPERIMENTAL_PREVIEW // MAPs
	| OTHER_STRATEGY | UNDISCLOSED // default: UNDISCLOSED
;

// APIDescription.xtext:444
('provider' 'governance'  evolStrat=EvolutionStrategy)? 

// APIDescription.xtext:456
('endpoint' 'governance'  evolStrat=EvolutionStrategy)?

// APIDescription.xtext:745
('evolution' 'governance' evolStrat=EvolutionStrategy)?
```

**④ 示例八节选（官方 ProviderSLAClientExample.mdsl）——endpoint 级 + provider 级治理共存；Ts&Cs 与 governance 共存**：

```mdsl
    endpoint governance AGGRESSIVE_OBSOLESCENCE
  with provider SLA // provider1SLA
  type QUALITATIVE
  objective performanceSLO2 "availability" 
     100 "every commercially reasonable effort, but not guaranteed"
  provider governance TWO_IN_PRODUCTION
  
API provider SampleProvider
offers SomeDemoContract
at endpoint location "http://www.tbc.io:80/path/subpath"
via protocol HTTP // or other supported protocol
binding resource SampleProvider
under conditions "See http://www.tbc.io/terms-and-conditions.html"
provider governance AGGRESSIVE_OBSOLESCENCE
```

**⑤ Version_Identifier 构造型（数据层版本标记，§3.7）——MapPattern 含 'Version_Identifier'，PatternStereotype 形如 <<...>>**：

```xtext
// APIDescription.xtext:195-201
MapPattern:
	'API_Key' | 'Context_Representation' | 'Error_Report' | 'Request_Bundle' | 'Request_Condition' | 'Wish_List' | 'Wish_Template' 
	| 'Embedded_Entity' | 'Linked_Information_Holder' | 'Annotated_Parameter_Collection' | 'Pagination' 
	| 'Data_Element' | 'Identifier_Element' | 'Id_Element' | 'Link_Element' | 'Metadata_Element'  | 'Control_Metadata' | 'Aggregated_Metadata' | 'Provenance_Metadata' 
	| 'Command' | 'Response_Bundle' | 'Version_Identifier'
	| STRING  
;

// APIDescription.xtext:187-189
PatternStereotype:
    '<<' (pattern=MapPattern | eip=EipPattern | name=ID) '>>'
;
```

**⑥ EndpointContract / Operation 的版本位（§5.7）**：

```xtext
EndpointContract:
	'endpoint' 'type' name=ID 
	('version' svi=SemanticVersioningIdentifier)? 

Operation:
	'operation' 
	name=ID 
	('version' svi=SemanticVersioningIdentifier)?
```

**⑦ §4.1 综合示例的版本与治理部分（节选 version / governance 行）**：

```mdsl
API description OrderManagementAPI version "2.1.0"
data type OrderId version "1.0.0" D<string>
data type OrderRecord version "1.2.0" {OrderId, "total":D<int>, "currency":D<string>}
endpoint type OrderContract version "2.1.0"
    operation createOrder version "2.1.0"
    operation lookupOrder version "2.1.1"   // 操作级补丁版本，可比契约更高
    operation listOrders                    // version 逐元素可选，此处不提供
API provider OrderProviderProd version "2.1.0"
    endpoint governance TWO_IN_PRODUCTION  // 端点级治理
  provider governance LIMITED_GUARANTEED_LIFETIME   // provider 级治理
API provider OrderProviderLegacy
    endpoint governance AGGRESSIVE_OBSOLESCENCE   // 旧版本激进淘汰
  under conditions "See https://order.example.com/terms.html"
  provider governance AGGRESSIVE_OBSOLESCENCE
API provider OrderProviderSandbox
    endpoint governance EXPERIMENTAL_PREVIEW
  provider governance EXPERIMENTAL_PREVIEW
API client OrderMobileApp version "2.1.0"
API gateway OrderGateway version "2.1.0"
    endpoint governance TWO_IN_PRODUCTION
  evolution governance TWO_IN_PRODUCTION    // 注意 gateway 用 evolution governance
```

</details>
