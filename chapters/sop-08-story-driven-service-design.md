# SOP-08: 故事驱动服务设计（Story-Driven Service Design）

> **定位**: 以集成故事（integration story）为起点的契约优先（contract-first）七步工作流，保证每个 API 操作"有理由存在" | **组**: C（契约设计） | **主要来源**: MDSL 规范 §10.1（故事驱动服务设计）、§4.7（集成场景与故事）、§7（变换与重构）

## 何时启用

当以集成需求为起点设计 API 产品、需要快速给出最小可行 API 产品（MVP API）时，使用本 SOP。它把"需求捕获 → 数据契约 → 操作设计 → 协议绑定 → 评审发布 → 技术契约 → 实现验收"串成一条可追溯的推导链，核心纪律是**无故事不操作**：每个操作都由故事引入，API-first 的"理由链"由此成立。

适用情形：
- API-first 开发启动，消费方与提供方需在实现前对齐契约
- 业务代表要参与契约起草（工作坊形式，部分规格即可开工）
- 已有故事清单但尚无契约结构，或契约评审发现"说不出理由"的操作

与 [SOP-07](sop-07-domain-driven-service-design.md) 的分工：SOP-07 从领域模型（DDD）出发走端到端链路；本 SOP 从集成故事出发，更轻、更快，适合领域边界尚不清晰、以对接需求为主导的场景。

## 触发条件

- 存在明确的消费方-提供方集成故事（谁、经由什么 API、做什么、为何）
- API 产品需要 MVP 版本快速上线并让消费方尽早签核
- 评审中出现无法解释存在理由的操作（"这个接口是谁要的？"）
- 团队采用契约优先，但缺少从需求到契约的系统推导步骤

## 完整步骤

### 步骤 1：捕获集成故事

用结构化故事六要素起草（工作坊即可产出，非技术人员可参与）：

| 要素 | 含义 | 示例 |
|------|------|------|
| 前置/触发（when） | 引发故事的业务事件或状态 | "订单已支付" |
| 角色（a/an/the） | 消费方画像，可以是人也可以是系统 | "订单履约系统" |
| 动作（wants to） | 动词 + 业务对象 | "为订单创建发货单" |
| 地点/上下文（in） | 业务发生场所或上下文 | "在仓储上下文中" |
| 产出（yielding） | 后置条件/结果 | "获得发货单号" |
| 目标（so that） | 业务影响 | "物流状态可被跟踪" |

补充约定：
- **故事类型**标注：用户故事、工作任务故事（job story）、测试用例、API mock——后两类在步骤 5/7 直接复用
- **场景类型**标注：业务 API、前端集成场景、后端集成场景（一个场景聚合一组故事）
- 成组操作可用紧凑记法（如"客户端要对某业务对象做 CRUD"）；**CRUD 故事在推导时受到特别关注**——逐动词检查哪些操作真的需要存在，而不是照单全收

### 步骤 2：推导数据契约（部分规格即可）

- 从故事的**宾语**（业务对象名词）推导数据类型定义
- **部分规格即可用**（敏捷建模原则："规格不必完整就有用"）：结构未定的元素留占位符——不含刻板印象、角色、类型信息，只给标识符
- 渐进精化路径：占位符 → 无类型数据元素 → 基本类型（string/int/bool/double/raw 等）→ 嵌套结构（参数树）或命名类型引用
- 被多个操作复用的结构提取为命名数据类型

### 步骤 3：为每个故事动词引入操作并做模式变换

- 故事的**动词** → 一个操作；请求对应动作与对象，响应对应产出——操作与故事一一挂钩，形成追溯链
- 端点推导：同一场景的故事聚到同一端点类型；可新增端点，也可向已有端点追加操作
- 对重复性设计任务应用模式变换（人工执行或工具辅助，均可）：

| 变换 | 何时使用 |
|------|----------|
| 分页（页式/偏移/游标） | 请求与响应均为参数树、结果集可能很大 |
| 条件过滤（Request Condition） | 消费方只需满足条件的数据 |
| 字段选择（Wish List / Wish Template） | 响应过大、消费方并非全需 |
| 请求打包（Request Bundle） | 一次提交多个标识做批量查询/操作 |
| 表示元素定型 | 占位符精化为具体角色与类型（承接步骤 2） |

模式取舍的力场分析见 [SOP-10](sop-10-map-decoration.md)。

### 步骤 4：添加协议绑定与治理信息

- **协议按上下文选择**——HTTP 不是唯一答案（事件流、消息队列、RPC 皆是选项；见反模式）
- HTTP 绑定要点：资源路径（可含 URI 模板参数）、操作→动词映射（同一资源内唯一）、消息元素→参数位置（PATH/QUERY/BODY/HEADER/COOKIE）、错误报告→状态码、安全策略→认证方案、请求/响应媒体类型
- 治理信息：版本号（API/端点/操作三级语义化版本）、SLA、错误报告结构、安全策略

### 步骤 5：发布契约供消费方评审

- 契约以工作坊起草、增量迭代——紧凑的抽象记法让非技术干系人也能读写
- **消费方签核是契约冻结前的门槛**；评审意见回到步骤 2/3 精化
- 测试用例型故事随契约一同评审，作为验收标准草案

### 步骤 6：派生技术专属描述

- 从同一份抽象契约派生一种或多种技术专属契约：OpenAPI、gRPC/Protocol Buffers、GraphQL Schema 等（一模型多契约，polyglot integration）
- 技术专属描述是**派生物**而非事实源；事实源保持在抽象契约层

### 步骤 7：契约驱动实现与验收测试

- 实现按契约展开：服务端骨架、客户端 mock 均以契约为准
- 测试用例型故事 → 验收测试基线；API mock 型故事 → 模拟服务
- 实现期对契约的任何偏离必须回写契约并记录决策，防止静默漂移（见 [SOP-12](sop-12-model-code-validation.md)）

## 使用示例

订单履约 API 的最小推导。以 MDSL 作为抽象契约语言的代表载体（方法本身工具中立）：步骤 1–4 合成**一份完整契约**，步骤 4 的资源路径/动词映射与步骤 5–7 另以走查记录承载。

注意 `ServiceSpecification` 的元素顺序是**强制的**：`API description` → `data type` → `relation type` → `event type` / `command type` → `endpoint type` → `SLA template` → `API provider` → `API client` → `API gateway` → `flow` → `scenario`。因此集成故事（步骤 1）在文件里位于**末尾**，与七步的执行顺序相反：

```mdsl
API description OrderFulfillmentAPI version "0.1.0"
usage context SOLUTION_INTERNAL_API for BACKEND_INTEGRATION

// 步骤 2：数据契约（渐进精化；P = 占位符，ID/D = MAP 元素刻板印象）
data type Shipment { "shipmentNo": ID, "orderId": ID<int>, "status": D<string>, "items": P }
data type ShipmentId P
data type OrderId ID<int>
data type CreateShipmentRequest { "orderId": ID<int>, "items": P }

// 步骤 3：端点与操作（每操作可追溯到来源故事 = API-first 理由链）
endpoint type ShipmentEndpoint version "0.1.0"
  exposes
    operation createShipment version "0.1.0" with responsibility STATE_CREATION_OPERATION
      expecting payload CreateShipmentRequest        // ← S1（动词：创建）
      delivering payload ShipmentId
    operation lookupShipmentByOrder with responsibility RETRIEVAL_OPERATION
      expecting payload OrderId                      // ← S2（动词：查询）
      delivering payload Shipment                    // 字段选择 <<Wish_List>> 待评估（装饰在表示元素上，见 SOP-10）

// 步骤 4：提供方与协议绑定
API provider OrderFulfillmentProvider version "0.1.0"
  offers ShipmentEndpoint
  at endpoint location "https://fulfillment.example.com/shipments" via protocol HTTP

API client OrderFulfillmentConsumer
  consumes ShipmentEndpoint
API client CustomerServiceFrontend
  consumes ShipmentEndpoint

// 步骤 1：集成故事（语法上位于 ServiceSpecification 末尾；官方标注 experimental preview）
scenario OrderFulfillmentIntegration type BACKEND_INTEGRATION_SCENARIO
  story S1 type USER_STORY
    when "an order has been paid"
    a "Order Fulfillment System"
    wants to "create a shipment for an order"
    yielding "shipment number"
    so that "shipping status can be tracked"
  story S2 type TEST_CASE
    a "Customer Service Frontend"
    wants to "look up shipment status by order id"
    yielding "shipment with status and item links"
    so that "customer inquiries can be answered"
```

`wants to` 之后只能接 STRING 或 `ActionKeyword`（`CRUD` / `CRUDSF` / `CQRS`）——语法注释明确指出 `create` 这类词会破坏操作命名，故此处用自由文本；紧凑记法形态见折叠段 §4.7 的 `a API client wants to CRUD "SomeBusinessObject"`。

```yaml
pipeline_record:
  step4_resource_binding:            # MDSL 只表达 location + protocol；路径/动词映射属绑定细节
    protocol: HTTP
    resources:
      "/shipments":           { createShipment: POST }
      "/shipments/{orderId}": { lookupShipmentByOrder: GET }
  governance:
    version: "0.1.0"                              # 端点与操作各自带版本
    error_report: { code: int, message: string }  # → 4xx/5xx 状态码
    sla: DRAFT                                    # 评审时与消费方确认（→ SOP-14）
  step5_review: { consumer_signoff: PENDING }      # S2 作为验收标准草案
  step6_derive: { openapi: PENDING, grpc_proto: OPTIONAL }
  step7_accept: { acceptance_tests_from: [S1, S2], status: PENDING }
```

## 技术交付物

1. 集成故事集（结构化六要素，含故事/场景类型标注）
2. 数据契约（渐进精化，占位符附精化计划）
3. 操作清单（每操作 ↔ 来源故事追溯）
4. 完整服务契约（含版本号、SLA、错误报告、安全策略）
5. 协议绑定说明（资源路径、动词映射、参数位置）
6. 技术专属契约（OpenAPI/gRPC/GraphQL 等派生物）
7. 验收测试基线（来自测试用例型故事）与消费方签核记录

## 成功标准

- **无故事不操作**：每个操作能指认至少一个背书故事
- 每个故事的宾语/动词/产出分别体现在数据类型/操作签名/响应结构中
- 每个占位符有精化计划（谁、何时、精化到什么程度）
- 契约可被非技术干系人在工作坊中起草并迭代（无需读代码）
- 消费方签核记录在契约冻结前完成
- 技术专属契约可从抽象契约重复派生（一模型多契约成立）

## 反模式

| 反模式 | 为何失败 |
|--------|----------|
| 操作先行 | 先设计一套 CRUD 再找故事挂靠；无理由的操作是接口膨胀与攻击面的温床，摧毁 API-first 理由链 |
| 大而全前置设计 | 等规格"完整"才肯发布；部分规格 + 占位符的价值正是敏捷建模——规格不必完整就有用 |
| HTTP/微服务确认偏误 | "任何服务必须暴露 HTTP 资源 API"是神话；协议与风格取决于上下文（事件流、消息队列、RPC 皆是选项） |
| 技术优先、一刀切 | 先定技术方案再"教育"用户；应先观察/倾听用户提取业务价值，建立统一语言 |
| 契约当文档 | 契约写完即弃、实现绕开契约直接改；契约应驱动实现与验收，偏离必须回写（否则触发 SOP-12 的漂移问题） |
| CRUD 紧凑记法吞掉判断 | "要对 X 做 CRUD"只是记法缩写；须逐动词检查 Delete/Update 是否真有故事背书 |
| 把工具当方法 | 认为七步必须靠特定工具链完成；步骤本身人工可执行，工具只是加速器（且多为技术演示品） |

## 关联

- **编排路线（API 产品）**: 08 → [SOP-10](sop-10-map-decoration.md)（模式精化）→ [SOP-12](sop-12-model-code-validation.md)（一致性守护）
- 上游输入：[SOP-02](sop-02-story-splitting.md)（过大故事先拆薄片再进入步骤 1）；[SOP-04](sop-04-stakeholder-value-modeling.md)（故事积压按价值排序后择优进入）
- 平行起点：[SOP-07](sop-07-domain-driven-service-design.md)（领域驱动端到端）；[SOP-09](sop-09-event-driven-service-design.md)（事件驱动五步，异步场景）
- 步骤 3 的模式变换与步骤 4 的角色/职责标注 → [SOP-10](sop-10-map-decoration.md) 步骤 1–4
- 存量 API 中发现"无理由操作"或语义歧义 → [SOP-11](sop-11-api-structure-analysis.md) 盘点后回到本 SOP 重设计
- 方法本身的引入与裁剪 → [SOP-13](sop-13-method-engineering.md)

## 来源

- MDSL-Specification（站点研究报告）：§10.1 故事驱动服务设计博客摘要（七步流程、"操作因故事而引入"的 API-first 理由链、优势与代价）；§4.7 集成场景与故事（故事语法、故事/场景类型、CRUD 紧凑记法）；§2 设计目标（敏捷建模、契约优先、多语集成）；§4.6 协议绑定（HTTP 绑定规则）；§7 变换与重构（分析变换、模式引入变换、数据类型变换、变换链）
- ICWE 2020 主题演讲（Zimmermann）：Part 1/2 神话破除（技术优先、HTTP 确认偏误）、Contracts rule、治理信息（SLA/版本）
- 分析报告 §3 SOP-08 草案、§5 原则 6（部分规格支持敏捷建模）/原则 12（无故事不操作）
- 语法形态核对（2026-10-10，`Microservice-API-Patterns/MDSL-Specification` @ master，`APIDescription.xtext`）：`ServiceSpecification` 的**强制元素顺序**（`types` → `links` → `events`/`commands` → `contracts` → `slas` → `providers` → `clients` → `gateways` → `orchestrations` → `realizations` → `scenarios`，其中 `scenario`/`flow`/`gateway` 标注 experimental preview）；`IntegrationScenario`（`'scenario' name ('type' ScenarioType)? ('version')? stories*`）、`IntegrationStory`（`when` / `a|an|the <client>|API client` / `wants to <Action> <StoryObject>*` / `yielding` / `so that`）、`Action`（STRING 或 `ActionKeyword` = CRUD|CRUDSF|CQRS，语法注释指出 `create` 等词会破坏操作命名）、`StoryObject`（可选介词 with/against/for/at/in/to/on/from/and/into/within/via + 可选冠词 a/an/the/its + STRING）、`StoryType`（USER_STORY|JOB_STORY|TEST_CASE|API_MOCK）、`ScenarioType`（BUSINESS_API|FRONTEND_INTEGRATION_SCENARIO|BACKEND_INTEGRATION_SCENARIO）；`EndpointContract` 的 `serves as … role`、`Operation` 的 `with responsibility …`；官方 `examples/examples-advanced/MAPDecoratorUsageReference.mdsl` 的 IRT 写法（`"someID":ID*`、`"someData":D`、`{{P}}`、`data type X P`）（深度语法核对改读仓库内权威副本：MDSL `../dsl/mdsl/APIDescription.xtext`，规则名→行区间查对应 `grammar-index.md`，pin commit 与 sha256 见 `../dsl/VERSIONS.md`），不再下载/解压上游仓库或读临时副本

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下片段忠实摘自语料原文，供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考。上方「使用示例」已按这些语法写成**一份完整契约**；摘录按约定保留——§4.7 的 `scenario`/`story` 示例与 `IntegrationStory` 语法定义是该段的直接依据。一处版本差异：摘录的 `IntegrationStory` 比 master 分支少了 `('version' svi=SemanticVersioningIdentifier)?` 位（语料版本较早），版本号在 `story` 与 `scenario` 上均为可选。

**集成场景与故事（MDSL §4.7 示例）**——步骤 1 的故事结构在抽象契约语言中的表示：

```mdsl
scenario Scenario1
  story Story1
   when "something has happened" // trigger
   a "customer and/or integrator" // actor role (can be system)
   wants to "startProcess" in "location"// action, business activity 
   yielding "a result" // outcome
   so that "both actors are satisfied and profit is made" // goal 
    
  story Story2
    a API client wants to CRUD "SomeBusinessObject"
```

**故事语法（MDSL §4.7，节选）**——六要素与类型枚举的权威定义：

```antlr
IntegrationStory:
	('story' name=ID ('type' type=StoryType)? related+=RelatedStories*)?
	('when' condition=STRING)? // precondition 
	('a'|'an'|'the') (client=STRING | 'API' 'client') // actor, persona
	'wants' 'to' action=Action on+=StoryObject*  // the responsibility/feature
	('yielding' outcome=STRING)? // postcondition 
	('so' 'that' goal=STRING)? // business impact
;

Action:
	plainAction=STRING | keyword=ActionKeyword ('a'|'an'|'the')? target=STRING
;

enum ActionKeyword:
	CRUD | CRUDSF | CQRS 
;

enum StoryType:
	USER_STORY | JOB_STORY | TEST_CASE | API_MOCK
;

enum ScenarioType:
	BUSINESS_API | FRONTEND_INTEGRATION_SCENARIO | BACKEND_INTEGRATION_SCENARIO 
;
```

**场景/故事级分析变换（MDSL §7）**——步骤 2/3"故事→端点→操作"推导的原始定义：

| MDSL 元素 | 变换 | 产物 | 备注 |
|---|---|---|---|
| Scenario | Derive application flow from scenario | Basic flow, single step | 输入可为 API 需求、集成场景/故事集、测试用例 |
| Scenario | Add endpoint type supporting this scenario | Endpoint type (with operations for stories) | CRUD stories receive special attention |
| Scenario story | Add operation to endpoint type supporting scenario | Operation for action, role stereotyped | 端点可已存在也可新建 |

**数据类型精化变换（MDSL §7，节选）**——步骤 2 占位符渐进精化的原始定义：

| MDSL 元素 | 变换 | 结果 |
|---|---|---|
| `P` or id-only `"anonymous"` | Replace with atomic string parameter | `"anonymous":D<string>` |
| Incomplete type `"someType":D` | Add string as type | `"someType":D<string>` |
| Any type in message payload | Extract data type definition | `data type` 定义 + 类型引用（支持复用） |

</details>
