# SOP-07: 领域驱动服务设计（Domain-Driven Service Design）

> **定位**: 从用户故事经 DDD 建模、抽象服务契约、模式装饰、协议绑定到实现骨架的端到端七步管线——一份领域模型派生多种技术契约（polyglot） | **组**: C（契约设计） | **主要来源**: MDSL 规范 §10.3；SummerSoC 2020 §3.3（Table 2）；ICWE 2020 主题演讲

## 何时启用

绿地项目或棕地再设计，需要一条"业务需求 → 可运行架构原型"的完整、可演示通路时使用。本 SOP 是三维设计模型的落地管线：

- **上下文至上（Context matters）**——先用战略+战术 DDD 界定上下文边界，没有放之四海皆准的设计；
- **契约长存（Contracts rule）**——框架和基础设施会过时，API 契约长存；契约先行于实现；
- **组件约束成本（Components contain）**——端点、操作、消息表示用模式化组件约束成本与风险，每个服务做买/租/建的自觉决策。

管线全貌（五阶段视图，七步是其展开）：

```
用户故事/用例 → 分析模型（子域、实体） → 设计模型（FEATURE 型 BC + 聚合；SYSTEM 型 BC）
             → 服务契约（抽象契约语言 → 技术专属 IDL） → 客户端/服务端实现
```

每一阶段转移都可自动推导初稿、人工精化（自动化程度递减：分析→设计模型可较完整推导，契约→实现只给骨架/桩）。**人不可替代的两个环节：领域分析（步骤 2）与模式装饰决策（步骤 4）**——其余环节的推导都建立在这两个人工决策之上。

## 触发条件

- 需要"需求→架构原型"的可演示通路（向干系人验证架构、争取共识）。
- 一份领域模型必须支撑多种技术栈（polyglot 集成）：同一契约要出 HTTP、消息、RPC 多种形态。
- API-first 开发启动：契约先于实现，服务端与客户端团队按契约并行开工。
- 已有成熟 DDD 模型（经 SOP-01/03/05/06），但尚未落到服务契约层。

## 完整步骤

### 步骤 1：捕获用户故事/用例（人工）

角色-动作-对象-收益四元组；用例亦可。过大故事先走 [SOP-02](./sop-02-story-splitting.md) 拆分。故事是整条管线的"理由链"源头——后续每个端点/操作都要能回溯到它。

### 步骤 2：战略 + 战术 DDD 建模（人工，不可替代环节 ①）

- 战略：子域划分 → 限界上下文（FEATURE 型起步）→ 上下文映射（U/D、OHS/PL、Partnership/SK 关系）。
- 战术：聚合、根实体、值对象、服务方法、领域事件。
- 分解不成熟时先走 [SOP-05](./sop-05-architectural-refactorings.md)/[SOP-06](./sop-06-systematic-decomposition.md)；事件风暴产出走 [SOP-03](./sop-03-event-storming-modeling.md)。
- **在关系上标注暴露聚合（exposed aggregates）**——这是步骤 3 端点推导的直接输入。

### 步骤 3：按映射表推导抽象服务契约（可自动推导初稿）

DDD 概念到服务契约概念的系统映射（SummerSoC Table 2 完整表）：

| DDD 概念 | 契约概念 | 说明 |
|---|---|---|
| 上游限界上下文（关系中处于 upstream 者） | API 契约 | 一 BC 一（微）服务一契约 |
| 上游暴露的聚合 | API 端点 | 每个暴露聚合一个独立端点 |
| 根实体或服务中的方法 | 操作（operation） | 从聚合内根实体/服务的方法派生 |
| 上述方法的参数与返回类型 | 数据类型定义 | 被操作的请求/响应消息引用 |
| 上游限界上下文 | API 提供方（provider） | 向下游暴露领域模型的一部分 |
| 下游限界上下文 | API 消费方（client） | 使用上游暴露的模型 |

推导产物是**技术中立的抽象契约**，含四段：数据类型、端点与操作（含期待/交付消息）、提供方（含协议与地址绑定位）、消费方。抽象契约语言的设计原则（以 MDSL 为代表）：

1. **平台与协议无关**——模块化语言结构，抽象契约与提供方绑定（provider binding）分离；
2. **部分规格支持敏捷建模**——允许占位符（placeholder `P`）与不完整数据类型，工作坊起草、增量精化；
3. **可读性优先于解析效率**——契约是给人评审的。

表示元素采用**名称-角色-类型三元组**（如 `"customerName": ID<string>`），角色即 MAP 元素刻板印象（ID / Link / Data / Metadata），支持基数（`?` `*` `+`）与嵌套（Parameter Tree 模式）。

### 步骤 4：用 MAP 模式装饰契约（人工决策，不可替代环节 ②）

抽象语法由 MAP（Microservice API Patterns）领域模型驱动；装饰是设计决策而非机械变换，详见 [SOP-10](./sop-10-map-decoration.md)：

- 端点角色：Information Holder（主数据/运营数据/参考数据持有者、数据传输资源、链接查找资源）或 Processing Resource；
- 操作职责：Retrieval / State Creation / State Transition / Computation Function；
- 表示元素刻板印象与结构模式（Embedded Entity vs Linked Information Holder、Pagination 等），按力场（性能/可扩展 ↔ 灵活性/可修改性 ↔ 数据质量/新鲜度/一致性）权衡。

### 步骤 5：绑定协议与技术（按上下文决策）

协议选择取决于上下文与需求：请求-响应语义、前后端集成 → RESTful HTTP；异步/事件密集 → 消息队列、事件流。**"任何服务必须暴露 HTTP 资源 API"是确认偏误**——IDEAL 云原则、事件溯源、流处理都是合法选项。同时补治理信息：端点地址、版本、SLA。

### 步骤 6：派生技术专属契约（可自动派生）

从同一份抽象契约派生多种技术专属描述：OpenAPI、gRPC（Protocol Buffers）、GraphQL 等任一 IDL。**polyglot 验证点：一份抽象模型必须能支撑 ≥2 种技术契约**——若某种技术契约无法从抽象模型表达，说明抽象层泄漏或模式装饰不足，回到步骤 3/4 修模型而不是在 IDL 里打补丁。

### 步骤 7：生成实现骨架并部署验证（桩级自动化）

- 按契约生成服务端骨架与客户端桩（stub），实现按契约展开、契约先行于实现。
- 部署到验证环境跑通一条端到端故事路径，证明"需求→原型"通路成立。
- 骨架之后的填充是常规开发；模型与代码的一致性从此交 [SOP-12](./sop-12-model-code-validation.md) 守护（"模型-代码鸿沟"不会因生成而消失）。

## 使用示例

保险客户核心域走查（对应步骤 3 折叠段的示例契约）：

```yaml
step1_story: "作为客户自助应用，我需要为客户创建与修改地址（经客户核心 API）"
step2_model:
  bounded_context: CustomerCore          # FEATURE 型，PUBLIC_API
  upstream_of: [CustomerSelfService, CustomerManagement, PolicyManagement]
  exposed_aggregate: CustomersAggregate
    root_entity: Customer
      attributes: { firstname: string, lastname: string,
                    sin: SocialInsuranceNumber, addresses: Address* }
      methods:
        - createAddress(customer, address) -> AddressId   # 写
        - changeAddress(address) -> bool                  # 写
step3_contract_derivation:               # 按 Table 2 逐行映射
  api_contract:  CustomerCoreAPI          # ← 上游 BC
  endpoint:      CustomersAggregate       # ← 暴露聚合
  operations:                             # ← 根实体方法
    createAddress: { expecting: createAddressParameter, delivering: AddressId }
    changeAddress: { expecting: Address,  delivering: D<bool> }
  data_types: [Customer, Address, SocialInsuranceNumber,
               AddressId(P 占位符——尚未细化，合法的部分规格),
               createAddressParameter]
  provider: CustomerCoreProvider          # ← 上游
  clients:  [CustomerSelfService, CustomerManagement, PolicyManagement]  # ← 下游
step4_decoration:                         # 人工模式决策
  endpoint_role: INFORMATION_HOLDER       # 主数据持有者
  operation_responsibility:
    createAddress: STATE_CREATION
    changeAddress: STATE_TRANSITION
  element_stereotypes: { firstname/lastname/sin/addresses: D, AddressId: ID }
step5_binding: { protocol: "RESTful HTTP", location: "…:8000",
                 rationale: "前后端集成 + 后端集成，请求-响应语义" }
step6_polyglot_check:
  openapi: ✓ 派生成功
  grpc_proto: ✓ 派生成功      # 一模型两契约，polyglot 验证通过
step7_prototype: 服务端骨架 + 客户端桩 → 部署验证环境 → 跑通"创建地址"故事路径
human_touchpoints: [step2 领域分析, step4 模式装饰决策]   # 其余为推导初稿+精化
```

## 技术交付物

- 领域模型（BC / 聚合 / 根实体方法 / U-D 关系 / 暴露聚合标注）
- 抽象服务契约（技术中立：数据类型段、端点-操作段、提供方/消费方段；允许占位符）
- MAP 模式装饰决策记录（端点角色、操作职责、元素刻板印象及力场权衡理由）
- 技术专属契约 ≥1 份（OpenAPI / gRPC / GraphQL 等 IDL）+ polyglot 验证记录
- 可运行原型（服务端骨架 + 客户端桩 + 部署验证记录）

## 成功标准

- **一模型多契约**：同一份抽象模型派生出多种技术契约（polyglot 验证通过）；技术细节零泄漏进抽象层。
- **映射链完整**：每个端点可追溯到暴露聚合、每个操作可追溯到根实体/服务方法、每个数据类型可追溯到方法签名（Table 2 六行逐行可对账）。
- **契约先行**：实现按契约桩展开，不存在"先写实现再补契约"。
- **部分规格合法但受控**：占位符与不完整数据类型允许存在，且有精化计划（敏捷建模，不是一次性交付全部细节）。
- **人工环节有主**：领域分析与模式决策两个环节有明确负责人与决策记录（其余环节的自动化不掩盖这两处判断）。

## 反模式

| 反模式 | 为何失败 | 纠正 |
|---|---|---|
| 技术优先 / 一刀切（Technology First, One Size Fits All） | 先定框架再找需求，忽略用户上下文 | 先观察/倾听用户提取业务价值，建立统一语言，再进管线 |
| HTTP/微服务确认偏误 | "任何服务必须暴露 HTTP 资源 API""微服务必须极小"都是神话 | 协议与粒度取决于上下文；消息队列、事件流、流处理皆是选项 |
| 相信统一接口足以表达领域语义 | REST 动词过于贫瘠，领域语义丢失 | DDD + 抽象契约语言 + 操作职责显式化（MAP 装饰 / operationId） |
| NIH 综合征 | "我们的扩展性需求独一无二"→ 自造框架/协议 | 回到上下文与需求，做买/租/建决策；建时用模式 |
| 跳过抽象层直接写 IDL | 技术绑定过早，polyglot 不可能，契约被单一框架绑架 | 先抽象契约（步骤 3/4）再派生 IDL（步骤 6） |
| 把生成当万灵药 | "模型-代码鸿沟"不因生成消失；领域分析与模式决策无法外包给工具 | 两个人工环节显式排期；生成后接 SOP-12 一致性守护 |
| 直接暴露领域模型内部 | 上游内部变更全线传导给每个下游 | 只暴露关系上标注的聚合子集，经 Published Language 商定 |

## 关联

- **前置**：[SOP-01 快速 OOAD](./sop-01-rapid-ooad.md) / [SOP-03 事件风暴建模](./sop-03-event-storming-modeling.md)（模型输入）、[SOP-05](./sop-05-architectural-refactorings.md) / [SOP-06](./sop-06-systematic-decomposition.md)（分解成熟）、[SOP-04 干系人与价值建模](./sop-04-stakeholder-value-modeling.md)（价值对齐）。
- **步骤内展开**：步骤 4 细化为 [SOP-10 API 消息模式装饰](./sop-10-map-decoration.md)。
- **替代入口**：以集成故事为起点走 [SOP-08 故事驱动服务设计](./sop-08-story-driven-service-design.md)；事件密集/异步场景走 [SOP-09 事件驱动服务设计](./sop-09-event-driven-service-design.md)——三者共享"抽象契约→技术契约→实现"的后半程。
- **后置守护**：[SOP-12 模型-代码一致性验证](./sop-12-model-code-validation.md)。
- **编排路线**：绿地项目 13→01/03→04→05/06→**07**→10→12。

## 来源

- MDSL 规范 §10.3（*Domain-Driven Service Design* 演示博文摘要，ozimmer.ch，2020-06-10，伴随 ICWE 2020 主题演讲）：七步旅程（故事→DDD→契约生成→MAP 装饰→多技术输出）、polyglot integration、"剩下的人工硬活 = 手工设计步骤与 MAP 装饰"
- SummerSoC 2020（Kapferer & Zimmermann）§3.3 + Table 2：DDD 上下文映射→服务契约六行映射、示例契约（Listing 3.1）、附录 A：MDSL 设计原则（平台/协议无关、部分规格、可读性优先）、名称-角色-类型三元组与 MAP 装饰器
- ICWE 2020 主题演讲（Zimmermann, *Dimensions of Successful Web API Design and Evolution*）：Context/Contracts/Components 三维模型、五阶段管线（User Story→Analysis→Design→Contract→Clients/Servers，生成程度 fully/initially/stubs）、神话破除 1/2/3（技术优先、HTTP 确认偏误、NIH）
- MDSL 规范 §10.4（MAP 元博客摘要）：MAP 起点（EIP 止步处的载荷结构）、元素刻板印象作为契约装饰器

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下片段忠实摘自语料原文（MDSL：Microservice Domain-Specific Language；缩进按原排版恢复），供对接 BCM 的 CUE 元模型时参考。

**由 DDD 上下文映射派生的示例契约**（步骤 3 的产物形态：数据类型段→端点-操作段→提供方/消费方段；`P` 为占位符，体现部分规格）——SummerSoC 2020 Listing 3.1：

```mdsl
API description CustomerCoreAPI // a.k.a. service contract
usage context PUBLIC_API for BACKEND_INTEGRATION and FRONTEND_INTEGRATION
data type Customer { "firstname": D<string>, "lastname": D<string>,
                     "sin":SocialInsuranceNumber, "addresses":Address * }
data type SocialInsuranceNumber { "sin": D<string> }
data type Address { "street": D<string>, "postalCode": D<int>, "city": D<string> }
data type AddressId P // placeholder, AddressId not specified in detail
data type createAddressParameter { "customer":Customer, "address":Address }
endpoint type CustomersAggregate
  exposes
    operation createAddress
      expecting
        payload createAddressParameter
      delivering
        payload AddressId
    operation changeAddress
      expecting
        payload Address
      delivering
        payload D <bool>
API provider CustomerCoreProvider
  offers CustomersAggregate
  at endpoint location "http://localhost:8000"
  via protocol "RESTful HTTP"
API client CustomerSelfServiceClient
  consumes CustomersAggregate
API client CustomerManagementClient
  consumes CustomersAggregate
API client PolicyManagementClient
  consumes CustomersAggregate
```

**MAP 装饰器与名称-角色-类型三元组**（步骤 4 的语言形态：`serves as`/`with responsibility`/`<<pattern>>` 装饰，`ID`/`D` 角色，`+` 基数）——SummerSoC 2020 Listing A.1：

```mdsl
API description HelloWorldAPI // a.k.a. service contract
data type SampleDTO {ID, D<int>} // partially specified tree (two leaves)
endpoint type HelloWorldEndpoint serves as PROCESSING_RESOURCE // MAP decorator
  exposes
    operation sayHello with responsibility COMPUTATION_FUNCTION // MAP decorator
      expecting payload "greeting": D<string>+ // one or more greetings
      delivering payload <<error_report>> SampleDTO // MAP decorator (<<pattern>>)
API provider HelloWorldAPIProvider1
  offers HelloWorldEndpoint
  at endpoint location "https://..." via protocol HTTP
API client HelloWorldAPIClient1
  consumes HelloWorldEndpoint
  from HelloWorldAPIProvider1 via protocol HTTP
```

</details>
