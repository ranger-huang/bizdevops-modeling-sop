# SOP-06: 系统化服务分解（Systematic Service Decomposition）

> **定位**: 用分解准则（DC-1~5）+ 14 项耦合准则目录 + 优先级配置 + 图聚类，产出**可辩护**的候选服务切分方案，替代直觉画圈 | **组**: B（模型演进） | **主要来源**: CML 规范 §42、§30（准则目录方法）；SummerSoC 2020 §3.2a

## 何时启用

当单体拆分或新建系统需要一个**可辩护**的候选切分方案时使用。本 SOP 的立场：切分决策必须能指认至少一条准则与证据；准则冲突时显式排优先级，而非拍脑袋。它回答的是"边界应该画在哪里、为什么画在那里"，产出的候选方案交由架构评审裁决，再由 [SOP-05](./sop-05-architectural-refactorings.md) 的 AR 操作增量落地。

> 方法学说明：本 SOP 取自一套已停用工具集成背后的**耦合准则目录与优先级方法**——工具会过时，准则目录与图聚类方法学仍然有效，且与任何建模语言/工具无关。

## 触发条件

- 干系人对切分方案有争议，需要证据化裁决（而非嗓门大的赢）。
- 需要系统评估多种候选分解并对比（第一个想到的方案 ≠ 唯一方案）。
- 棕地迁移启动：存量盘点（[SOP-11](./sop-11-api-structure-analysis.md)）之后需要重新分解。
- 团队在用简单启发式分解（两个披萨团队规模、代码行数阈值、if-then 经验法则）——这些不含领域语义与耦合证据，应切换到准则化方法。

## 完整步骤

### 步骤 1：前提补全（输入质量决定输出质量）

聚类分析对模型完备性有硬性前提，缺一项结果就不可信：

| 前提 | 为什么必需 |
|---|---|
| 实体必须有**属性** | 没有属性就无法派生纳米实体（nanoentity，实体+属性构成的耦合分析最小单元），耦合图没有节点 |
| 用例/用户故事与实体的**读写关系**明确（读哪些实体的哪些属性、写哪些） | 语义邻近、身份与生命周期共性等准则的证据来源 |
| 聚合**属主团队**标注 | 共享属主准则与 Conway 兼容检查的输入 |
| 特征标注：易变性、可用性/一致性/安全关键度、存储相似性等 | DC-5（泛化 NFR）与对应耦合准则的证据 |
| 预定义服务约束登记（合规、既有系统边界、已定的买/租/建决策） | 作为硬约束参与聚类 |

### 步骤 2：确认顶层分解准则（DC-1~5）

五条分解准则（Decomposition Criteria）是全部耦合准则的顶层框架，其遴选本身遵循三条元准则：**实践相关性**（对所有软件项目普遍相关）、**代表性**（多个独立来源都提到）、**一般性**（可类推扩展其他准则）：

| 准则 | 内容 | 渊源 |
|---|---|---|
| DC-1 业务实体 | 属于同一领域部分的属性与实体归组；领域分区形成**语言或领域专家边界** | 统一语言 / 领域专家边界 |
| DC-2 用例 | 被同一批用例使用的领域对象归组 | 用例驱动分解 |
| DC-3 代码属主/开发团队 | 限界上下文围绕代码属主（开发团队）构建 | Conway 定律 |
| DC-4 变更可能性 | 把常变者与不常变者隔离 | Parnas（1972） |
| DC-5 泛化 NFR | 在某 NFR 上相似的元素归组（可变性、存储相似性、可用性、安全等） | NFR 驱动分解 |

### 步骤 3：耦合准则标注（14 项目录）

为每对领域元素（纳米实体/聚合）标注耦合证据。当元素对满足某准则时记一条带权边；证据必须落到具体标注（属性、读写交互、属主、特征值）：

| # | 耦合准则 | 含义 | 典型证据 |
|---|---|---|---|
| 1 | 身份与生命周期共性（Identity & Lifecycle Commonality） | 一起创建、一起销毁 | 同一聚合根、同一状态机 |
| 2 | 语义邻近（Semantic Proximity） | 领域语义相近、服务同一目的 | 被同一用例读写（DC-1/DC-2） |
| 3 | 共享属主（Shared Owner） | 同一团队拥有 | owner 标注相同（DC-3） |
| 4 | 结构易变性（Structural Volatility） | 结构变更频率相近者同组、相异者分开放 | likelihoodForChange 标注（DC-4） |
| 5 | 内容易变性（Content Volatility） | 数据内容变更频率 | contentVolatility 标注 |
| 6 | 预定义服务约束（Predefined Service Constraint） | 已事先确定的分组/隔离约束 | 合规要求、既有系统边界 |
| 7 | 延迟（Latency） | 低延迟要求的交互应在同一服务内 | 同步调用链、性能预算 |
| 8 | 一致性约束（Consistency Constraint） | 需要强一致的元素同组 | 事务边界、不变量 |
| 9 | 一致性关键度（Consistency Criticality） | 一致性要求级别相近者同组 | LOW/NORMAL/HIGH 标注 |
| 10 | 可用性关键度（Availability Criticality） | 可用性要求级别相近者同组 | LOW/NORMAL/HIGH 标注 |
| 11 | 安全约束（Security Constraint） | 同一安全域的元素同组 | 安全区（security zone）标注 |
| 12 | 安全关键度（Security Criticality） | 安全敏感级别相近者同组 | LOW/NORMAL/HIGH 标注 |
| 13 | 安全上下文性（Security Contextuality） | 依赖相同安全上下文（认证/授权环境） | 访问组标注 |
| 14 | 存储相似性（Storage Similarity） | 数据量级/存储技术相近者同组 | TINY/NORMAL/HUGE 标注 |

### 步骤 4：优先级配置（XS~XL）

准则之间必然冲突（语义邻近说合、共享属主说分），冲突靠**优先级**裁决：

- 五级优先级：`XS`（最低）、`S`、`M`、`L`、`XL`（最高），作用于每条准则的边权。
- **优先级是项目上下文的函数**：合规驱动的项目把安全约束调高；性能敏感的项目把延迟调高。
- 默认参考起点（来自方法原始配置，须按项目重排）：`M` 级——身份与生命周期共性、语义邻近、共享属主、安全约束、安全上下文性、延迟、一致性约束、预定义服务约束；`XS` 级——结构易变性、内容易变性、存储相似性、一致性关键度、可用性关键度、安全关键度。
- 每次优先级配置都要记录**项目上下文依据**（为什么这条准则在本项目重要）。

### 步骤 5：图聚类得候选切分

- 以纳米实体为节点、带优先级加权的耦合准则边构图。
- 用图聚类分析得出候选切分：可选马尔可夫聚类（MCL）、标签传播（Leung）、Chinese Whispers 等算法——后两者结果随机，需多次运行对比稳定性；也可人工分组（小模型）。
- **至少产出 2 个候选方案**（不同算法/不同优先级配置/不同粒度），单方案不构成决策。

### 步骤 6：多方案对比评审（含 Conway 兼容检查）

对每个候选切分（cut）做架构评审：

- 每个候选能否追溯到准则证据（哪些边主导了这个分组）？
- **Conway 定律兼容检查**：候选服务边界与团队边界是否对齐？错位处是改组织还是改方案？
- 跨服务交互代价：候选切分把高频读写交互切到了服务外吗（延迟/一致性代价）？
- 演进性：该方案给 AR 增量演进（SOP-05）留了空间吗？

### 步骤 7：决策与落地

- 选定方案，用 Y 型决策记录（考虑过什么、为什么选它、放弃了什么）固化。
- 与现状模型的差距分解为 AR 序列，交 [SOP-05](./sop-05-architectural-refactorings.md) 增量落地；边界约束交 [SOP-12](./sop-12-model-code-validation.md) 守护。

## 使用示例

货运跟踪域（Cargo Tracking）走查——两个聚合属主不同（CargoPlanner / Administrators），核心用例 `ViewTracking` 只读跟踪链数据：

```yaml
decomposition_analysis:
  step1_preconditions:
    nanoentities:            # 实体+属性派生（前提：Entity 已带 Attribute）
      - Cargo.trackingId
      - Cargo.origin
      - Cargo.routeSpecification
      - Cargo.itinerary
      - Cargo.delivery
      - Location.unLocode
      - Location.name
    use_case_interactions:   # 读写关系已明确（CML 中即 UseCase 的 interactions）
      ViewTracking:
        - read Cargo with [trackingId]
        - read HandlingEvent with [handlingEventType, location, completionTime]
        - read Delivery with [transportStatus, estimatedArrivalTime, misdirected]
        - read Voyage with [voyageNumber]
        - read RouteSpecification with [destination]
    ownership: { Cargo: CargoPlanner, Location: Administrators }   # 二者在 CML 中须声明为 type = TEAM 的 Bounded Context
  step4_priorities:          # 本项目上下文：跨团队协作摩擦是主要痛点
    Identity & Lifecycle Commonality: L
    Shared Owner: L           # 调高：两属主团队发布节奏完全不同
    Semantic Proximity: M
    Latency: S
    Storage Similarity: XS
  step5_clustering:
    algorithm: "Markov Clustering"          # 图聚类
    candidate_A:
      CargoTrackingService: [Cargo.*]       # 货运跟踪服务：Cargo.* 及跟踪链
      BaseDataService: [Location.*]         # 基础数据服务
    candidate_B:
      MonolithicService: [all nanoentities] # 单一服务
  step6_review:
    candidate_A:
      criterion_trace: "Shared Owner + Semantic Proximity"   # 属主相异；ViewTracking 只读跟踪链，Location 仅被引用
      conway_check: COMPATIBLE              # ✓ 一服务一团队
      cross_service_cost: "Location 查询低频、可缓存，延迟代价可接受"
    candidate_B:
      criterion_trace: "Storage Similarity"                  # 仅 XS 级准则支持
      conway_check: CONFLICT                # ✗ 两团队共维一服务，回到当前摩擦
  step7_decision: candidate_A               # 用 Y-Statement 记录；后续经 AR-3/AR-4 增量演进
```

## 技术交付物

- 带属性与特征标注的领域模型（实体、属性、owner、用例读写交互、易变性/关键度/存储标注）
- 纳米实体（nanoentity）清单
- 耦合准则证据标注表（元素对 × 准则 × 证据）
- 优先级配置（XS~XL，附项目上下文依据）
- ≥2 个候选分解方案 + 对比评审记录（含 Conway 兼容检查）
- 最终切分决策记录（Y-statement）+ AR 落地序列

## 成功标准

- 每个候选切分可追溯到准则证据（图中每条主导边有准则来源与标注出处）。
- 优先级排序有项目上下文依据，不是默认值照抄。
- 至少两个候选方案经过对比评审，落选方案有明确落选理由。
- 最终方案通过团队评审，且与组织结构（Conway）兼容——或错位处有显式的组织侧决策。
- 选定方案可被分解为 SOP-05 的 AR 增量序列（可落地、可回退）。

## 反模式

| 反模式 | 为何失败 | 纠正 |
|---|---|---|
| 简单启发式分解（两个披萨、代码行数、if-then 经验法则） | 不含领域语义与耦合证据，边界画在哪全凭直觉 | 代之以分解准则 + 系统化方法（本 SOP） |
| 直觉画圈、无准则辩论 | 争议无法裁决，方案无法复盘 | 每对边界指认准则证据 |
| 准则冲突靠拍脑袋 | 冲突是常态（语义邻近 vs 共享属主），随手裁决不可辩护 | 显式优先级配置 + 记录依据 |
| 默认优先级照抄 | 优先级是项目上下文的函数；抄默认等于没排 | 按合规/性能/组织痛点重排并记录理由 |
| 无属性、无读写标注就分解 | 纳米实体派生不出来，聚类结果是噪声 | 先做步骤 1 前提补全 |
| 单方案直接定稿 | 第一个想到的切分没有对比就没有说服力 | 至少 2 个候选 + 对比评审 |
| 一次性分解 | 分解是持续过程；方案定死后环境变化无人负责 | 选定方案后接 SOP-05 增量演进 |
| 忽视 Conway | 与团队边界冲突的切分会被组织引力撕回原状 | 步骤 6 强制 Conway 兼容检查 |

## 关联

- **编排路线**：棕地治理 11→**06**→05→12（存量盘点后重新分解）；绿地项目 13→01/03→04→05/**06**→07→10→12。
- **输入**：[SOP-01 快速 OOAD](./sop-01-rapid-ooad.md)、[SOP-03 事件风暴建模](./sop-03-event-storming-modeling.md) 提供领域模型与用例；[SOP-04 干系人与价值建模](./sop-04-stakeholder-value-modeling.md) 提供价值/优先级证据；[SOP-11 存量 API 分析](./sop-11-api-structure-analysis.md) 提供棕地现状。
- **输出消费**：[SOP-05 架构重构](./sop-05-architectural-refactorings.md) 把选定切分落为 AR 序列；[SOP-07 领域驱动服务设计](./sop-07-domain-driven-service-design.md) 从成熟分解推导服务契约；[SOP-12 模型-代码一致性验证](./sop-12-model-code-validation.md) 守护边界。
- **方法治理**：优先级配置与准则裁剪本身是一次方法采纳决策，走 [SOP-13](./sop-13-method-engineering.md) 的三规则过滤。

## 来源

- CML 规范 §42 Systematic Service Decomposition（教程）：前提条件（实体属性 → 纳米实体派生）、示例领域模型、用例读写交互建模
- CML 规范 §30 耦合准则目录与优先级方法：14 项准则、XS~XL 五级优先级、默认优先级参考、图聚类算法选项（该工具集成已停用，本 SOP 仅取准则目录与优先级方法学）
- SummerSoC 2020（Kapferer & Zimmermann）§3.2a：DC-1~5 分解准则、准则遴选三元准则（实践相关性/代表性/一般性）、Parnas 1972、Conway 定律、准则来源（Gysel 等耦合准则目录及 DDD 实践者文献）
- ICWE 2020 主题演讲（Zimmermann）：分解启发式批判（两个披萨、LOC、if-then 规则）、"哪些耦合准则对（微）服务分解重要"之问
- 语法形态核对（2026-10-10，`ContextMapper/context-mapper-dsl` @ master）：`Aggregate` 的 `owner=[BoundedContext]`（须指向 `type = TEAM` 的 Bounded Context）与特征位 `contentVolatility` / `likelihoodForChange`（别名 `structuralVolatility`）/ `availabilityCriticality` / `consistencyCriticality` / `storageSimilarity` / `securityCriticality`；枚举取值 `Volatility` = UNDEFINED|NORMAL|RARELY|OFTEN、`Criticality` = UNDEFINED|NORMAL|HIGH|LOW、`Similarity` = UNDEFINED|NORMAL|HUGE|TINY；`UseCase` 的 `interactions` 由 `NormalFeature` 组成（`verb` + `a|an|the` + `entity` + 可选 `with its` 属性列表 + 可选 `in|for|to` 容器实体）——步骤 1 的"读写交互"即此语法（深度语法核对改读仓库内权威副本：CML `../dsl/cml/ContextMappingDSL.xtext` + `../dsl/cml/TacticDDDLanguage.xtext`，规则名→行区间查对应 `grammar-index.md`，pin commit 与 sha256 见 `../dsl/VERSIONS.md`），不再下载/解压上游仓库或读临时副本
- 校正记录：语料原稿把属主拼作 `CargoPlaner`（折叠段摘录保留原拼写），正文与使用示例统一改为 `CargoPlanner`

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下片段忠实摘自语料原文（CML：Context Mapping DSL），供对接 BCM 的 CUE 元模型时参考。上方「使用示例」的 `decomposition_analysis` 是**决策记录**（非 DSL 语法），其每一项取值都应能落到下方摘录的 CML 特征位上。两处需注意：① 摘录中的属主名 `CargoPlaner` 为语料原稿拼写，正文与示例已统一为 `CargoPlanner`，摘录按约定保留原样；② §18 特征标注摘录把 `Aggregate` 写在顶层，那是片段省略了外层 `BoundedContext`——按 `ContextMappingModel` 规则，`Aggregate` 与 `enum` 都不能出现在 `.cml` 顶层。

**前提补全的输入形态：带属性与属主的聚合**（没有属性就派生不出纳米实体）——CML §42 示例模型：

```cml
BoundedContext CargoTracking {
  Aggregate Cargo {
    owner CargoPlaner

    Entity Cargo {
      aggregateRoot
      - TrackingId trackingId
      - Location origin
      - RouteSpecification routeSpecification
      - Itinerary itinerary
      - Delivery delivery
    }
  }
  Aggregate Location {
    owner Administrators

    Entity Location {
      aggregateRoot
      - UnLocode unLocode
      String name
    }
  }
  // ...
}
```

**用例读写交互建模**（语义邻近等准则的证据来源；原文如此，含原稿拼写）——CML §42：

```cml
UseCase ViewTracking {
  interactions
    read "Cargo" with its "trackindId",
    read "HandlingEvent" with its "handlingEventType", "location", "completionTime",
    read "Delivery" with its "transportStatus", "estimatedArrivalTime", "misdirected", 
    read "Voyage" with its "voyageNumber",
    read "RouteSpecification" with its "destination"
}
```

**特征标注语法**（DC-5 与耦合准则 4/5/9/10/12/14 的证据输入）——CML §18：

```cml
Aggregate CustomerManagement {
  contentVolatility = OFTEN
  // ...
}
```

```cml
Aggregate CustomerManagement {
  likelihoodForChange = OFTEN
  // or:
  structuralVolatility = NORMAL
}
```

```cml
Aggregate CustomerManagement {
  availabilityCriticality = HIGH
}
```

```cml
Aggregate CustomerManagement {
  storageSimilarity = HUGE
}
```

</details>
