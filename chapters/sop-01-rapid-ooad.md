# SOP-01: 快速 OOAD 建模（Rapid OOAD）

> **定位**: 从书面需求（用户故事/用例）快速推导子域（Subdomain）与限界上下文（Bounded Context）的初始分解，覆盖五阶段管线"需求 → 分析模型 → 设计模型"的前三段 | **组**: A（需求到模型） | **主要来源**: CML-Specification §25/§21/§6/§7；ICWE 2020 keynote

## 何时启用

- 当项目早期需要从一份书面需求清单快速得到初始领域分解与上下文结构时，使用本 SOP
- 当需求基线发生重大变更、既有分解需要整体重跑时，使用本 SOP 重建初稿
- 当需要向干系人展示可视化初始架构、且团队接受"初稿 + 后续重构演进"的工作方式时，使用本 SOP
- 当需求尚未成文、只能通过协作探索获得时，改走 [SOP-03](sop-03-event-storming-modeling.md)（事件风暴路线）

## 触发条件

- 已存在（或可立即补齐）用户故事 / 用例清单
- 项目尚无子域 / 限界上下文结构，或既有结构与需求已明显脱节
- 需求文本可精化到"角色–动词–对象–收益"四元组质量（角色与收益缺失时先补需求，再启动建模）
- 团队认同：本轮产出是**可演进的初稿**，结构级调整后续交给 [SOP-05](sop-05-architectural-refactorings.md)/[SOP-06](sop-06-systematic-decomposition.md)

## 完整步骤

四步建模过程：第 1 步人工执行且不可省略；第 2–4 步是"可推导"步骤——有自动化推导能力时一键生成初稿，没有时按同样的人工规则执行（推导的本质是映射规则，不是工具）。

### 第 1 步（人工）：捕获并精化用户需求

把每条需求写成用户故事（User Story）或用例（Use Case），精化为四元组：

| 槽位 | 含义 | 示例 |
|------|------|------|
| 角色（As an） | 谁发起 | 保险员工（Insurance Employee） |
| 动词（I want to） | 做什么动作 | create / update / offer |
| 对象（a/an） | 动作作用于什么业务对象 | 客户（Customer）、合同（Contract） |
| 收益（so that） | 为什么值得做 | 能管理客户数据并提供保险合同 |

- 用例形态登记：参与者（actor）、交互列表（interactions，逗号分隔的动词–对象对）、收益（benefit）；交互可附实体属性（with its "firstname", "lastname"）与容器引用（for a / for an / in a / in an）
- 可选增强：按 Cockburn 风格补充范围（scope）与层级（level，如 Summary），用主成功场景交互列表充实简述式用例；登记次要参与者（secondary actors）
- 同一角色、同一收益的多个动词–对象对可合并为一条故事（多行 "I want to"）
- 动词是复合词（如 "manage"）时，先走 [SOP-02](sop-02-story-splitting.md) 拆分再进入第 2 步

### 第 2 步（可推导）：从功能需求导出子域

- 按业务对象对功能需求（故事/用例的动词–对象对）聚类，每个聚类候选一个子域
- 每个子域生成三件套：
  1. **领域愿景陈述**（Domain Vision Statement）——由其支持需求的收益（benefit）转化而来，格式"Aims at promoting the following benefit for a ⟨角色⟩: ⟨收益⟩"
  2. **实体清单**——由需求对象名词导出
  3. **服务与操作**——由需求动词导出（操作以动词命名，如 createCustomer、offerContract）
- 声明子域与需求的 supports 追溯关系，保证每条故事可回查
- 可选：为子域标注类型——核心域（CORE_DOMAIN，关键差异化能力）、支撑域（SUPPORTING_DOMAIN）、通用域（GENERIC_SUBDOMAIN）
- 注意：子域层只放实体做业务建模，聚合等战术概念属于下一步的限界上下文层

### 第 3 步（可推导）：从子域导出 FEATURE 型限界上下文

- 每个子域导出一个 **FEATURE 型**限界上下文，以 implements 声明其实现的子域
- 限界上下文携带自己的领域愿景陈述（声明"本上下文实现了哪些子域"）
- 子域的实体与服务收拢为初始聚合（Aggregate）
- 推导结果**保留 TODO 精化标记**，这是交付物的一部分而非缺陷：
  - 按实体拆分聚合（后续用 [SOP-05](sop-05-architectural-refactorings.md) 的 AR-1"Split Aggregate by Entities"）
  - 为实体补属性
  - 为服务补操作

### 第 4 步（可选，可推导）：从 FEATURE 导出 SYSTEM

- 当需要前后端职责分离或多部署单元视图时使用
- 为每个部署单元导出 **SYSTEM 型**限界上下文（物理/流程/部署视角），登记进上下文映射（Context Map）
- 为 SYSTEM 间关系标注：关系模式（如 Published Language → Conformist）、实现技术（如 RESTful HTTP）、暴露的聚合（exposed aggregates）

### 第 5 步（人工）：精化与校验

- 逐项消化 TODO：补实体属性、补服务操作、必要时拆聚合
- 语义一致性校验：无悬空引用、无不可达限界上下文、每条故事可追溯
- 限界上下文分型速查（设计模型层的视角分型）：

| 类型 | 视角 | 典型例子 |
|------|------|----------|
| FEATURE | 分析/早期设计抽象，功能场景视角 | 客户管理相关的一切（建客户、改地址…） |
| APPLICATION | 逻辑设计与实现视角 | 一个自助前端应用、一个后端系统 |
| SYSTEM | 物理/流程/部署视角 | 一个单页应用、一个后端应用、一个数据库 |
| TEAM | 开发团队 | 客户前端团队、合同团队 |

## 使用示例

保险员工管理场景（语料真实案例的中立化呈现）：

**输入（第 1 步人工精化后的需求四元组）**：

| 槽位 | 值 |
|------|-----|
| 角色 | Insurance Employee（保险员工） |
| 动词 | create（同用例可扩展 update、offer） |
| 对象 | Customer（关联 Contract） |
| 收益 | I am able to manage customer data and offer insurance contracts |

**第 2–3 步推导结果**：

```yaml
Domain: InsuranceDomain
  Subdomain: CustomerDomain
    愿景陈述: >
      Aims at promoting the following benefit for a Insurance Employee:
      I am able to manage the customers data and offer them insurance contracts.
    实体: [Customer, Contract]
    Service: US1_ExampleService
      操作: [createCustomer, updateCustomer, offerContract]

BoundedContext: NewContextFromSubdomains
  type: FEATURE
  implements: CustomerDomain
  愿景陈述: "This Bounded Context realizes the following subdomains: CustomerDomain"
  聚合: CustomerDomain 聚合（收纳子域的实体与服务）
  TODO:
    - 按实体拆分聚合（转 SOP-05 / AR-1）
    - 为实体补属性与操作
    - 为服务补操作
```

**第 4 步（可选，前后端分离）**：

```yaml
ContextMap:
  contains: [CustomerManagementFrontend, CustomerManagementBackend]
  关系: CustomerManagementBackend [PL] -> [CF] CustomerManagementFrontend
    implementationTechnology: "RESTful HTTP"
    exposedAggregates: CustomerManagementAggregateBackend
  CustomerManagementBackend:
    type: SYSTEM
    implements: CustomerManagement
```

## 技术交付物

- 需求四元组清单（故事/用例，含追溯标识）
- 子域模型：愿景陈述 + 实体 + 服务/操作 + supports 追溯关系
- 初始上下文映射：限界上下文（含 FEATURE/SYSTEM 分型）+ 关系模式 + 暴露聚合
- 待精化 TODO 列表（推导标记的汇总，含负责人与去向 SOP）

## 成功标准

- 每条故事可追溯到子域与限界上下文（supports / implements 链完整）
- 每个限界上下文与子域都有领域愿景陈述
- 聚合/实体/操作与故事的动词–对象对一一对应（操作以动词命名）
- 模型通过语义一致性校验：无悬空引用、无不可达限界上下文
- TODO 列表存在且有明确去向（精化被计划，而非被遗忘）

## 反模式

- **模糊需求直接喂入**：四元组槽位缺失会产出无愿景陈述的子域与无操作的服务——第 1 步是人工不可省环节（五阶段管线中领域分析是人不可替代的部分）
- **手绘上下文映射**：不可机器校验、无法支撑重构与自动推导；精确、可校验的模型才是后续 AR 演进（SOP-05）的前提
- **一次性分解**：把初稿当终稿。分解是持续过程，结构级调整走 SOP-05/06，拒绝增量演进会导致早期错误固化
- **忽略 TODO 标记**：推导完不精化，模型停留在骨架级别，无法支撑契约设计（SOP-07）
- **技术优先（Technology First）**：先定技术栈再划子域边界；应先观察/倾听用户提取业务价值、建立统一语言（ubiquitous language），实现技术只是 SYSTEM 分型的一个标注属性

## 关联

- 上游输入：[SOP-02](sop-02-story-splitting.md)（复合动词故事先拆分再喂入第 1 步）；[SOP-03](sop-03-event-storming-modeling.md)（需求未成文时的协作探索入口，与本 SOP 互为替代）
- 下游演进：[SOP-04](sop-04-stakeholder-value-modeling.md)（价值对齐）；[SOP-05](sop-05-architectural-refactorings.md)（AR 增量重构，消化"按实体拆聚合"等 TODO）；[SOP-06](sop-06-systematic-decomposition.md)（需要可辩护切分方案时）
- 端到端：[SOP-07](sop-07-domain-driven-service-design.md)（按 DDD→契约映射从 BC/聚合推导服务契约）；[SOP-12](sop-12-model-code-validation.md)（模型落地后的一致性守护）
- 编排路线（绿地项目）：[SOP-13](sop-13-method-engineering.md) → **SOP-01**/03 → 04 → 05/06 → 07 → 10 → 12

## 来源

- CML-Specification §25（Rapid OOAD Transformations：四步建模过程、保险员工示例、TODO 标记约定）
- CML-Specification §21（用户故事/用例语法：四元组、Cockburn 风格、次要参与者）
- CML-Specification §6（限界上下文类型：FEATURE/APPLICATION/SYSTEM/TEAM）、§7（域与子域：愿景陈述、类型、supports、子域内实体约束）
- ICWE 2020 keynote（五阶段管线：User Story → Analysis Model → Design Model → Service Contract → Clients/Servers；Rapid OOAD 定位）
- 分析报告 F2（五阶段管线）、F5（分解是持续过程）

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下代码块忠实摘自语料原文，供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考；每段标注来源与用途。

**CML 用户故事与用例（CML-Specification §21/§25，第 1 步需求捕获的语法载体）**：

```cml
UserStory US1_Example {
  As an "Insurance Employee" I want to "create" a "Customer" so that "I am able to manage customer data ..."
}

UseCase UC1_Example {
  actor = "Insurance Employee"
  interactions = "create" a "Customer"
  benefit = "I am able to manage customer data ..."
}
```

**CML 用例：实体属性与容器引用（CML-Specification §21，第 1 步精化语法）**：

```cml
UseCase UC1_Example {
  actor "Insurance Employee"
  interactions
    create a "Customer" with its "firstname", "lastname",
    update an "Address" for a "Customer",
    "offer" a "Contract" for a "Customer"
  benefit "I am able to manage the customers data and offer them insurance contracts."
}
```

**CML 限界上下文与类型（CML-Specification §6，第 3/4 步分型的语法基础）**：

```cml
BoundedContext CustomerManagementContext implements CustomerManagementDomain {
  type = FEATURE
  domainVisionStatement = "The customer management context is responsible for ..."
  implementationTechnology = "Java, JEE Application"
  responsibilities = "Customers", "Addresses"
  knowledgeLevel = CONCRETE
}
```

**CML 第 2 步推导出的子域（CML-Specification §25）**：

```cml
Domain InsuranceDomain {
  Subdomain CustomerDomain {
    domainVisionStatement "Aims at promoting the following benefit for a Insurance Employee: I am able to manage the customers data and offer them insurance contracts."
    Entity Customer
    Entity Contract
    Service US1_ExampleService {
      createCustomer;
      updateCustomer;
      offerContract;
    }
  }
}
```

**CML 第 3 步推导出的限界上下文（CML-Specification §25，注意 TODO 精化标记）**：

```cml
BoundedContext NewContextFromSubdomains implements CustomerDomain {
  domainVisionStatement "This Bounded Context realizes the following subdomains: CustomerDomain"
  /* This Aggregate contains the entities and services of the 'CustomerDomain' subdomain.
   * TODO: You can now refactor the Aggregate, for example by using the 'Split Aggregate by Entities' architectural refactoring.
   * TODO: Add attributes and operations to the entities.
   * TODO: Add operations to the services.
   */
}
```

**CML 第 4 步推导出的 SYSTEM 与上下文映射（CML-Specification §25；PL=Published Language，CF=Conformist）**：

```cml
ContextMap {
  contains CustomerManagementFrontend
  contains CustomerManagementBackend

  CustomerManagementBackend [PL] -> [CF] CustomerManagementFrontend {
    implementationTechnology "RESTful HTTP"
    exposedAggregates CustomerManagementAggregateBackend
  }
}

BoundedContext CustomerManagementBackend implements CustomerManagement {
  domainVisionStatement "This Bounded Context realizes the following subdomains: CustomerManagement"
  type SYSTEM
  implementationTechnology "Sprint Boot"
  // ...
}
```

**CML 域/子域与 supports 追溯（CML-Specification §7，第 2 步追溯关系语法）**：

```cml
Domain Insurance {
  domainVisionStatement = "Insurance domain vision statement ..."

  Subdomain CustomerManagementDomain supports CreateCustomers, CreateCustomerAddresses {
    type = CORE_DOMAIN
    domainVisionStatement = "Subdomain managing everything customer-related."

    Entity Customer {
      String firstname
      String familyname
    }
  }
}
```

</details>
