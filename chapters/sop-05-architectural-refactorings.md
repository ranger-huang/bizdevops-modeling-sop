# SOP-05: 架构重构（Architectural Refactorings, AR）

> **定位**: 用 11 个模型级重构操作目录（AR-1~11）与分步应用流程，让分解结构随组织与变更热点增量、可逆、有准则依据地演进 | **组**: B（模型演进） | **主要来源**: CML 规范 §28；SummerSoC 2020 §3.2

## 何时启用

当初始分解不再适配现状、或架构评审发现结构异味时，使用本 SOP。架构重构（Architectural Refactoring, AR）直接作用于精确、机器可读的领域模型（上下文映射、限界上下文（Bounded Context）、聚合（Aggregate）），而非代码：每次重构都保证结果模型仍语义正确（可通过校验），模型中其他部分的引用与依赖被自动调整。

核心心智：**分解是持续过程，不是一次性事件**。初始分解来自用例/用户故事/事件风暴（见 SOP-01/03），随后随团队变化、变更热点、非功能需求（NFR）分化，通过一系列 AR 增量演进；拆过头可以合并回来（每个拆分 AR 都有逆操作）。

AR 分两类：

- **结构类重构（Structural Refactorings）**：改变分解结构本身（限界上下文与聚合的拆分/合并/提取）——AR-1~AR-7
- **关系类重构（Relationship Refactorings）**：只改变上下文映射（Context Map）上关系的类型（Partnership、Shared Kernel、Upstream-Downstream 之间的转换）——AR-8~AR-11

## 触发条件

观察到下列信号时选对应 AR（"当 Y 时使用 X"）：

| 触发信号 | 使用的 AR |
|---|---|
| 一个聚合过大，内含多个身份与生命周期应独立的实体 | AR-1（Split Aggregate by Entities） |
| 限界上下文内不同聚合服务于不同特性/用例 | AR-2（Split BC by Features） |
| 一个限界上下文由多团队共同维护，合并冲突、发布互相牵制 | AR-3（Split BC by Owner） |
| 实现期发现部分聚合变更频繁、其余稳定 | AR-4（Extract Aggregates by Volatility） |
| 需按内聚性或特定 NFR（可用性/安全/一致性）提取部分聚合 | AR-5（Extract Aggregates by Cohesion） |
| 拆过头：两个聚合总是一起变更、跨聚合事务频繁 | AR-6（Merge Aggregates，AR-1 的逆） |
| 拆过头：两个限界上下文的协作成本超过独立收益 | AR-7（Merge BCs，AR-2~5 的逆） |
| 两上下文间 Shared Kernel 共享的模型部分不断膨胀失控 | AR-8（Extract Shared Kernel） |
| Partnership（两团队同成败）无法维持 | AR-9（Suspend Partnership，三策略） |
| Shared Kernel 过密，想退回协作规划关系 | AR-10（SK → Partnership） |
| Partnership 协作密切到需要共享领域模型（如共享库） | AR-11（Partnership → SK） |

## 完整步骤

### 步骤 0：确认前提

- 模型是精确、机器可读、可校验的——手绘上下文映射无法支撑 AR（不可校验、引用不可自动调整）。
- 聚合已标注决策证据：属主团队（owner）、关联特性/用例（features/useCases）、易变性等特征（取值 RARELY / NORMAL / OFTEN）。缺这些标注，AR-2/3/4/5 就没有输入。

### 步骤 1：识别触发信号

信号来源：架构评审、团队反馈（合并冲突、发布耦合）、变更热点统计、NFR 冲突（一个特性要高可用、另一个要强一致）。

### 步骤 2：选择 AR 并指认驱动准则

每个结构类 AR 都对应耦合准则；选择时必须能指认准则与证据（分解必须可辩护）：

| AR | 驱动准则 |
|---|---|
| AR-1 | 身份与生命周期共性（Identity & Lifecycle Commonality） |
| AR-2 | 语义邻近（Semantic Proximity） |
| AR-3 | 共享属主（Shared Owner）；Conway 定律 |
| AR-4 | 结构易变性（Structural Volatility）；Parnas（1972）：把常变者与不常变者隔离 |
| AR-5 | 任意耦合准则或 NFR（人工选定） |

### 步骤 3：检查前置条件

对照下方目录表逐项检查；任一前置不满足，先补全模型标注或放弃本次重构，不要硬做。

### 步骤 4：执行重构

AR 以模型变换（model transformation）方式实现：模型文本 → 解析为抽象语法树/模型对象 → 应用变换 → 反解析回模型文本。该机制保证结果模型必能通过校验，且模型其他部分的引用与依赖（如上下文映射中的关系规则）被自动调整。

### 步骤 5：重构后校验

- **语义一致性**：无悬空引用、无不可达限界上下文、关系组合满足语义规则。
- **准则复核**：拆分后的上下文是否满足"单一团队属主 / 单一特性簇 / 均匀易变性"（按所选 AR 的驱动准则复核）。
- **关系补全**：新上下文是否需要补关系定义（U/D 角色、OHS/PL、暴露聚合标注）。

### 步骤 6：记录决策

每次 AR 一条记录：触发信号、驱动准则与证据、前置检查结果、逆操作、为何不选其他 AR。建议用 Y 型决策记录（见 SOP-13）。

### 步骤 7：迭代

按下方分步应用流程随项目阶段多轮迭代；逻辑顺序不强制一次性时序执行。

### AR 完整目录

| 编号 | 名称 | 对象 | 动作（输入→输出） | 前置条件 | 逆操作 | 驱动准则 |
|---|---|---|---|---|---|---|
| AR-1 | Split Aggregate by Entities | 聚合 | 按实体拆分，每实体一个聚合（1→n） | 聚合含 ≥2 个实体 | AR-6 | 身份与生命周期共性 |
| AR-2 | Split Bounded Context by Features | BC | 按用例/用户故事把聚合分组进不同 BC（1→n） | BC 含 ≥2 个聚合；聚合被不同特性使用 | AR-7 | 语义邻近 |
| AR-3 | Split Bounded Context by Owner | BC | 按属主团队把聚合分组进不同 BC（1→n） | BC 含 ≥2 个聚合；聚合分属不同团队 | AR-7 | 共享属主；Conway 定律 |
| AR-4 | Extract Aggregates by Volatility | BC | 把给定易变性（RARELY/NORMAL/OFTEN）的聚合全部提取进新 BC（1→2） | BC 含 ≥2 个变更可能性不同的聚合 | AR-7 | 结构易变性；Parnas（1972） |
| AR-5 | Extract Aggregates by Cohesion | BC | 人工选定聚合按内聚准则提取（1→2） | BC 含 ≥2 个聚合 | AR-7 | 任意耦合准则或 NFR |
| AR-6 | Merge Aggregates | 聚合 | 两聚合合一（2→1） | 两聚合不含同名领域对象；属性尽量合并，不可合并的元属性（名称、知识级别）取第一个聚合的 | AR-1 | —（回退操作） |
| AR-7 | Merge Bounded Contexts | BC | 两 BC 合一，结果含双方全部聚合（2→1） | 模型中存在两个 BC | AR-4、AR-5 | —（回退操作） |
| AR-8 | Extract Shared Kernel | SK 关系 | 共享模型部分提取为新 BC，原 SK 关系替换为两条 U/D 关系（1 SK → 1 新 BC + 2 U/D） | ≥2 个 BC 处于 Shared Kernel 关系 | — | — |
| AR-9 | Suspend Partnership | Partnership | 中止伙伴关系（三策略见下） | 存在 Partnership 关系 | — | — |
| AR-10 | Change Shared Kernel to Partnership | SK 关系 | SK → Partnership | 存在 SK 关系 | AR-11 | — |
| AR-11 | Change Partnership to Shared Kernel | Partnership | Partnership → SK | 存在 Partnership 关系 | AR-10 | — |

**AR-9 三策略**（Partnership 无法维持时三选一）：

- **a) 合并两个 BC**——调用 AR-7；适合双方边界已名存实亡。
- **b) 提取共性建新 BC**——为共享部分创建新 BC，与原两 BC 各建 U/D 关系。
- **c) 转为上下游（Upstream-Downstream）**——对称伙伴关系改为单向依赖，明确影响流方向。

### AR 分步应用流程（增量分解方法）

逻辑建议顺序（非严格时序；过程可多轮重复；也允许其他分解策略）：

```
领域分析 → 初始子域 → 初始 BC（来自用例 / 用户故事 / 事件风暴）
                        │
        ┌───────────────┴─────────────────────┐
        │ BC 层                                │ 聚合层
        ▼                                      ▼
  AR-2 按特性/用例成型                    AR-1 按实体拆分
        │（早期：BC 通常围绕特性形成）          ⇅
        ▼                                 AR-6 过度拆分时合并回去
  AR-3 团队变大时按属主拆分
        │
        ▼
  AR-4 实现/维护期发现变更热点后按易变性提取
        │
        ▼
  AR-5 按内聚 / QA / NFR 微调  ⇄  AR-7 过度拆分时合并回退
        │
        ▼
  关系层演进：AR-8 / AR-9 / AR-10 / AR-11
        │
        ▼
  关系定义 + 暴露聚合标注 → 推导服务契约（见 SOP-07）
```

## 使用示例

场景（保险域）：客户核心上下文 `CustomerCore` 含两个聚合——`Customers`（属主：客户团队）与 `Policies`（属主：合同团队）。近三个迭代两团队修改同一模型、发布互相牵制——典型"一个 BC 多团队共维"信号。完整走查：

```yaml
refactoring_record:
  id: AR-2025-003
  trigger_signal: "Customers 与 Policies 分属两团队维护；合并冲突频繁、发布需双边协调"
  ar_selected: "AR-3（Split Bounded Context by Owner）"
  driving_criterion: "共享属主（Shared Owner）；Conway 定律——组织边界已固化，技术边界应对齐"
  alternatives_considered:
    - "AR-2（按特性拆）：两聚合特性有重叠（客户视图需要保单数据），驱动力不如属主强"
  preconditions_check:
    - "BC 含 ≥2 个聚合：满足（Customers、Policies）"
    - "聚合分属不同团队：满足（owner 标注分别为 CustomerTeam / ContractTeam）"
  execution:
    input: "CustomerCore（含 Customers、Policies）"
    output: "CustomerCore（含 Customers） + PolicyContext（含 Policies）"
    reference_adjustment: "上下文映射关系规则中的引用由变换自动替换"
  relationship_added: "CustomerCore [U,OHS,PL] -> [D] PolicyContext（下游经 Published Language 访问保单数据，而非上游内部模型）"
  validation:
    semantic_consistency: "通过（无悬空引用、无不可达 BC）"
    criterion_review: "通过（每 BC 单一团队属主）"
    model_check: "通过"
  inverse_operation: "AR-7（未来团队合并时可回退）"
```

前后对照（文本图）：

```
重构前：                             重构后：
CustomerCore                         CustomerCore
 ├─ Customers （客户团队）             └─ Customers （客户团队）
 └─ Policies  （合同团队）            PolicyContext
                                       └─ Policies  （合同团队）
                                     关系：CustomerCore [U,OHS,PL] -> [D] PolicyContext
```

关系类走查（简例）：`CustomerSelfService` 与 `PolicyManagement` 原为 Partnership，同步规划与联合发布已无法维持 → 应用 **AR-9 策略 c**，转为 U/D 关系并明确 `PolicyManagement` 为上游；若两者后来共享部分客户模型且协作再度密切，可用 **AR-11** 转 Shared Kernel；共享部分再膨胀失控时，用 **AR-8** 提取为独立 BC。

## 技术交付物

- 重构前后模型对照（含关系与暴露聚合标注的调整）
- 每次 AR 的决策记录（触发信号 / 驱动准则与证据 / 前置检查 / 逆操作 / 取舍理由）
- 更新后的上下文映射（通过语义校验）
- 聚合特征标注表（owner、features/useCases、易变性——AR 决策的输入证据）

## 成功标准

- 每次重构可指认驱动准则（DC-1~5 或耦合准则目录）及证据——分解可辩护。
- 重构后模型通过语义一致性校验：无悬空引用、无不可达 BC、关系语义规则满足。
- 逆操作已知且记录在决策记录中（可回退）。
- 拆分后的 BC 满足所选 AR 的目标属性（单一团队 / 单一特性簇 / 均匀易变性）。
- AR 应用记录呈迭代时间线——分解随组织与变更热点演化，而非一次定死。

## 反模式

| 反模式 | 为何失败 | 纠正 |
|---|---|---|
| 手绘上下文映射上做演进 | 不可机器校验、引用无法自动调整，重构后一致性靠人脑 | 模型先进入精确、可校验的建模语言，再执行 AR |
| 一次性分解 | 分解是持续过程；拒绝增量演进会让早期错误固化 | 按分步应用流程多轮迭代 |
| 无准则重构 | 说不清为什么拆，评审通不过，出问题无法回溯 | 每次 AR 指认驱动准则并记录证据 |
| 跳过前置条件检查 | AR-1 需聚合含 ≥2 实体；AR-6 遇同名领域对象即失败 | 对照目录表逐项检查后再执行 |
| 把合并当失败 | AR-6/AR-7 是目录中的正规逆操作；过度拆分比不拆更贵 | 跨上下文事务频繁、协作成本高企时果断合并回退 |
| 只拆模型不看组织 | 与团队边界冲突的拆分会被 Conway 定律拉回原状 | 重构时同步检查组织-技术边界兼容（见 SOP-06） |
| 拆分后直接暴露上游内部模型 | 下游耦合上游内部实体，变更全线传导 | 用 OHS + Published Language 暴露商定的模型子集 |

## 关联

- **上游输入**：[SOP-01 快速 OOAD 建模](./sop-01-rapid-ooad.md)、[SOP-03 事件风暴结果建模](./sop-03-event-storming-modeling.md) 产生初始 BC 与聚合；[SOP-06 系统化服务分解](./sop-06-systematic-decomposition.md) 产出候选切分方案，由本 SOP 增量落地与持续演进。
- **下游消费**：[SOP-07 领域驱动服务设计](./sop-07-domain-driven-service-design.md) 从重构后的上游 BC 与暴露聚合推导服务契约；[SOP-12 模型-代码一致性验证](./sop-12-model-code-validation.md) 守护重构后的边界不被实现绕过。
- **准则同源**：驱动准则与 [SOP-06](./sop-06-systematic-decomposition.md) 的分解准则（DC-1~5）及耦合准则目录同源。
- **编排路线**：绿地项目 13→01/03→04→**05**/06→07→10→12；棕地治理 11→06→**05**→12。

## 来源

- CML 规范 §28 Architectural Refactorings：AR-1~11 全目录（目标/前置条件/逆操作/耦合准则）、AR-9 三策略、AR-6 合并规则、"重构结果必为语义正确模型"保证
- SummerSoC 2020（Kapferer & Zimmermann, *Domain-driven Service Design*）§3.2：DC-1~5 分解准则、模型变换三步机制、Fig.6 分步 AR 应用流程
- CML 规范 §5（Context Map）、§6（Bounded Context）、§18（Aggregate：owner / useCases / features / 易变性特征标注）——语言参考部分
- ICWE 2020 主题演讲（Zimmermann）：神话破除 3（NIH 综合征与分解启发式批判）、买/租/建决策上下文

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下片段忠实摘自语料原文（CML：Context Mapping DSL），供对接 BCM 的 CUE 元模型时参考。

**上下文映射与关系属性**（`exposedAggregates` 是契约推导的输入；关系类 AR-8~11 直接操作这些关系线）——CML §5：

```cml
ContextMap DDDSampleContextMap {
  type SYSTEM_LANDSCAPE
  state AS_IS

  contains CargoBookingContext, VoyagePlanningContext, LocationContext

  CargoBookingContext [SK]<->[SK] VoyagePlanningContext
}
```

```cml
VoyagePlanningContext [D,ACL]<-[U,OHS,PL] LocationContext {
    implementationTechnology = "RESTful HTTP"
    downstreamRights = VETO_RIGHT
    exposedAggregates = Customers, Addresses
}
```

**限界上下文声明**（type / 愿景陈述——AR-2/3 拆分产物应各自保有愿景陈述）——CML §6：

```cml
BoundedContext CustomerManagementContext implements CustomerManagementDomain {
  type = FEATURE
  domainVisionStatement = "The customer management context is responsible for ..."
  implementationTechnology = "Java, JEE Application"
  responsibilities = "Customers", "Addresses"
  knowledgeLevel = CONCRETE
}
```

**聚合属主标注**（AR-3 的决策输入；owner 必须指向 TEAM 型限界上下文）——CML §18：

```cml
BoundedContext CustomerSelfServiceContext implements CustomerManagementDomain {
  type = APPLICATION
  domainVisionStatement = "This context represents a web application..."

  Aggregate CustomerFrontend {
    owner = CustomerFrontendTeam

    DomainEvent CustomerAddressChange {
      aggregateRoot
      // ...
    }
  }
}
```

**聚合特性关联**（AR-2 的决策输入；useCases / userStories / features 三种标注）——CML §18：

```cml
BoundedContext PolicyManagementContext implements PolicyManagementDomain {
  Aggregate Offers {
    useCases = CreateOfferForCustomer

    Entity Offer {
      aggregateRoot
      int offerId
      - Customer client
      - List<Product> products
      BigDecimal price
    }
  }
  Aggregate Products {
    userStories = AddProductToOffer
    // ...
  }
  Aggregate Combined {
    features = CreateOfferForCustomer, AddProductToOffer
    // ...
  }
}
```

**易变性特征标注**（AR-4/AR-5 的决策输入）——CML §18（内容易变性取值 RARELY/NORMAL/OFTEN；同理还有 availabilityCriticality=HIGH、consistencyCriticality=NORMAL（LOW/NORMAL/HIGH）、storageSimilarity=HUGE（TINY/NORMAL/HUGE）、securityCriticality=HIGH（LOW/NORMAL/HIGH））：

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

</details>
