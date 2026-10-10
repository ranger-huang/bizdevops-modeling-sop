# SOP-09: 事件驱动服务设计（Event-Driven Service Design）

> **定位**: 从事件风暴产出到服务端点、技术契约与消息路由/集成流的五步连续精化管线 | **组**: C（契约设计） | **主要来源**: MDSL 规范 §10.2（事件驱动服务设计）、§4.8（编排流）、§4.9（异步消息扩展）、§7（流到端点变换）；CML 规范 §39–40

## 何时启用

当异步/事件密集集成场景需要把事件风暴（Event Storming）产出直接推进到 API 设计与集成流时，使用本 SOP。事件/命令流在其中充当**动态分析工件（白板产出）与技术专属 API 描述之间的中间语言**：白板 → 领域模型 → 流程视图 → 服务端点 → 技术契约 → 消息路由，每步产物都是下一步的输入，可反复精化。

适用情形：
- 事件风暴工作坊已完成（或即将完成），产出需要固化为精确、可校验的模型
- 系统间以事件/命令流交互，同时需要与请求-响应 API 形成统一视图
- 选定事件溯源（Event Sourcing）或 CQRS 架构风格，需要把状态事件、命令侧/查询侧分离落到契约层

## 触发条件

- 已完成事件风暴/类似协作探索，可衔接 [SOP-03](sop-03-event-storming-modeling.md) 的结构化领域模型
- 白板便利贴面临丢失风险，团队需要统一的模型表示
- 消费方与提供方之间的交互本质上是"发生了什么"（事件）而非"请做什么"（同步调用）
- 需要设计消息路由、通道与补偿路径（异步失败处理）

## 完整步骤

### 步骤 1：协作白板勾画命令/事件 → 转入领域模型

- 在协作白板上勾画**命令**（祈使语气：引发事件的动作）与**领域事件**（过去时：领域中已发生之事）
- 按 [SOP-03](sop-03-event-storming-modeling.md) 的映射固化为结构化领域模型：领域事件、命令、聚合（一致性边界）、问题/策略（可选）、用户角色（可选）、视图/读模型（可选）、事件流
- 事件溯源场景：在聚合内声明状态事件与状态迁移；CQRS 场景：命令侧与查询侧（读模型）分离建模，由应用层流程串联
- **显式声明已知局限**：并非所有事件风暴元素都有对应建模概念（如问题、策略类便利贴可能无处安放）；把无法映射的元素单独登记，不要硬凑

### 步骤 2：派生流程视图

- 用流程记法（如业务流程建模标注 BPMN）表示事件/命令流，供业务侧与开发侧共同评审
- 为每条流标注类型：应用流、集成流、服务编排、API 调用序列、事件溯源流
- 流步骤的基本结构：**事件触发命令，命令发出事件**；支持组合步骤、拆分步骤、并行分支（AND/OR/XOR）与汇合（join）
- 流程视图是端点推导（步骤 3）与消息路由（步骤 5）的共同蓝本，两者必须与它一致

### 步骤 3：推导服务层 API 端点

从流程与聚合推导端点及操作，映射规则。「流程元素」列使用 MDSL 语法规则名（`FlowStep` 的三种步骤类型及其子规则），不用自然语言描述：

| 流程元素（MDSL grammar element） | 端点产物 | 操作职责（MAP 模式名） |
|----------|----------|------------------------|
| `Orchestration` (`flow`) start event — `events+` of the leading `CommandInvokationStep` | 新增 `EndpointContract`（`endpoint type`），启动事件写入 `receives`；`exposes` 的操作可后补 | —（事件入口，不派生 `Operation`） |
| `CommandInvokation` — `command` side: `SingleCommandInvokation` / `ConcurrentCommandInvokation` / `ExclusiveAlternativeCommandInvokation` / `InclusiveAlternativeCommandInvokation` | 派生 `Operation`：`with responsibility …` + `transitions from … to …`（`StateTransition`） | State Creation Operation / State Transition Operation |
| `EventProduction` — `emits` side of `DomainEventProductionStep` / `CombinedInvocationStep`: `SingleEventProduction` / `MultipleEventProduction` / `ExclusiveAlternativeEventProduction` / `InclusiveAlternativeEventProduction` | 派生 `Operation`：`in NOTIFICATION conversation` + `emitting event …`；该事件同时写入端点 `receives` | Event Processor |

- 一个命令/事件对应一个操作；操作与流程步骤一一可追溯
- 追溯性由绑定语法承载，不是口头约定：`OrchestrationBinding`（`binding to` → `EndpointTypeBinding` | `ChannelBinding`）下的 `StepToEndpointBinding` = `EventToOperationBinding`（`event E to operation op`）| `CommandToOperationBinding`（`command C to operation op`），两者均可带 `with mediation <DataTransformation>`（`from <DataContract> to <DataContract>`，语法注释标记 experimental）；消息侧对应 `StepToChannelBinding` = `EventToMessageBinding` | `CommandToMessageBinding`（`… to message …`），见步骤 5
- 需要业务级撤销时，在**同一端点内**为操作声明补偿操作（`compensated by <Operation>`，saga 支持）
- 命令侧与查询侧操作分离到不同端点（CQRS 场景的结构重构"命令查询分离"见 [SOP-10](sop-10-map-decoration.md)）

### 步骤 4：派生技术专属契约

- 从端点派生一种或多种技术契约：OpenAPI、gRPC IDL、GraphQL Schema 等（一模型多契约）
- 纯异步消息 API 使用面向通道的描述规范（如 AsyncAPI 或项目等价物）
- 技术契约是派生物；事实源保持在抽象契约层

### 步骤 5：设计消息路由/集成流

- **通道类型**：点对点、发布-订阅、数据类型通道；质量类通道：无效消息通道、死信通道、保证投递通道
- **消息意图**标注：事件消息、命令消息、文档消息（企业集成模式 EIP 术语）
- **请求-应答通道**：声明关联标识（correlation）与应答通道，处理"异步中的同步语义"
- **消息代理与端点**：代理暴露通道（含地址与协议绑定），消息端点声明使用哪些通道，并可带端点角色与职责标注（衔接 [SOP-10](sop-10-map-decoration.md)）
- 集成流可绑定到具体流程实现技术（流程引擎、编程实现等——按上下文选择，不做先验假设）
- 为每条失败路径显式建模：死信去处、补偿操作、重试语义

### 已知局限（必须向团队显式声明）

1. **并非所有事件风暴元素都有对应的建模概念**——未映射元素登记在案，人工决策去留
2. **步骤间的推导不覆盖全部语言特性**——每步产物需人工评审与精化，不能盲目信任自动结果
3. **错误/补偿路径不会自动出现**——异步交互的失败语义（死信、补偿、幂等）必须由设计者补充建模

## 使用示例

订单履约事件流（以 MDSL + AsyncMDSL 扩展为载体；方法本身工具中立）。`ServiceSpecification` 的元素顺序强制：`data type` → `event type` / `command type` → `channel` → `message broker` → `message endpoint` → `flow`。

**步骤 1–2：领域模型 + 流程视图**

```
  [OrderPaid] ──triggers──> 〈CreateShipment〉 ──emits──> [ShipmentCreated]
       │                                                        │
       └──triggers──> 〈NotifyWarehouse〉 ──emits──> [WarehouseNotified]
                                                                 └──triggers──> 〈TrackShipment〉

  流类型: INTEGRATION_FLOW（EIP）；并行分支: +（AND）—— CreateShipment 与 NotifyWarehouse 并行
```

**步骤 3：事件 ↔ 操作映射表**

| 流程元素（MDSL flow step） | Endpoint | Operation | 职责（OperationResponsibility） | 状态声明 |
|---|---|---|---|---|
| `event OrderPaid` — start event, `CommandInvokationStep`.`events+` | ShipmentEndpoint | （`receives` 声明，无对应 `Operation`） | — | — |
| `command CreateShipment` — `SingleCommandInvokation` | ShipmentEndpoint | createShipment | STATE_CREATION_OPERATION | NOT_SHIPPED → SHIPPED |
| `command NotifyWarehouse` — `ConcurrentCommandInvokation` (`+`/`and`) | WarehouseEndpoint | notifyWarehouse | STATE_TRANSITION_OPERATION | NOTIFICATION_PENDING → NOTIFIED |
| `event ShipmentCreated` — `DomainEventProductionStep`.`EventProduction` | ShipmentEndpoint | onShipmentCreated | EVENT_PROCESSOR（`in NOTIFICATION conversation`） | `emitting event ShipmentCreated` |
| `event WarehouseNotified` — `DomainEventProductionStep`.`EventProduction` | WarehouseEndpoint | onWarehouseNotified | EVENT_PROCESSOR（`in NOTIFICATION conversation`） | `emitting event WarehouseNotified`（流终点，无下游 `triggers`） |
| `command TrackShipment` — `SingleCommandInvokation` | ShipmentEndpoint | trackShipment | STATE_TRANSITION_OPERATION | SHIPPED → IN_TRANSIT（示例状态名，实际取自 [SOP-03](sop-03-event-storming-modeling.md) 的聚合生命周期） |

六个流程元素恰好覆盖契约中声明的 3 个 `event type` 与 3 个 `command type`——映射表覆盖率是步骤 3 的自检项（见成功标准第 1、2 条），漏行即漏操作。

**步骤 3 + 步骤 5：端点契约与消息路由（MDSL）**

```mdsl
API description OrderFulfillmentEventsAPI version "0.1.0"
usage context SOLUTION_INTERNAL_API for BACKEND_INTEGRATION

data type Shipment { "shipmentNo": ID, "orderId": ID<int>, "status": D<string> }

event type OrderPaid, ShipmentCreated, WarehouseNotified
command type CreateShipment, NotifyWarehouse, TrackShipment

// ── 步骤 3 产物：端点契约 ─────────────────────────────────────────────────
// 槽位约束：endpoint type 与 channel 同属 ServiceSpecification 的 contracts 槽位，
// 必须排在 message broker（providers 槽位）与 flow（orchestrations 槽位）之前。
// 子句顺序固定：version → supports → serves as → policy → exposes → receives。
// serves as 多角色用 and 连接、末尾 role 关键字可省；资源角色（ResourceRole）与
// 操作职责（OperationResponsibility）是两个正交轴，不可互相替代。
// supports 只接受单个 flow 或 scenario（语法注明多流支持属 future work）——一个端点
// 参与多条流时，该关系须带外登记。
endpoint type ShipmentEndpoint
  supports flow ShipmentFulfillmentFlow
  serves as OPERATIONAL_DATA_HOLDER and MUTABLE_COLLECTION_RESOURCE
  exposes
    operation createShipment with responsibility STATE_CREATION_OPERATION
      expecting payload Shipment
      delivering payload "shipmentNo": ID
      transitions from "NOT_SHIPPED" to "SHIPPED"
      compensated by cancelShipment        // 前向引用同端点内操作，官方示例同款写法
    operation trackShipment with responsibility STATE_TRANSITION_OPERATION
      expecting payload "shipmentNo": ID
      delivering payload Shipment
      transitions from "SHIPPED" to "IN_TRANSIT"
    operation onShipmentCreated with responsibility EVENT_PROCESSOR
      in NOTIFICATION conversation
      emitting event ShipmentCreated       // 操作可无 expecting/delivering（语法允许不完整规格）
    // 补偿操作不是流程元素，故不出现在映射表中，由下方 YAML 过程记录登记
    operation cancelShipment with responsibility STATE_TRANSITION_OPERATION
      expecting payload "shipmentNo": ID
      transitions from "SHIPPED" to "CANCELLED"
  receives
    event OrderPaid                        // 启动事件：只声明接收，不派生 Operation

// 仓储侧只处理命令与事件、本文未建模其数据类型，故取 PROCESSING_RESOURCE；
// 若后续引入库存/通知记录数据类型，应改判为 OPERATIONAL_DATA_HOLDER——角色随模型演进而非一次定死。
// 并行分支（+）下仓储侧经 command NotifyWarehouse 抵达，不直接 receives OrderPaid。
endpoint type WarehouseEndpoint
  supports flow ShipmentFulfillmentFlow
  serves as PROCESSING_RESOURCE
  exposes
    operation notifyWarehouse with responsibility STATE_TRANSITION_OPERATION
      expecting payload Shipment
      transitions from "NOTIFICATION_PENDING" to "NOTIFIED"
    operation onWarehouseNotified with responsibility EVENT_PROCESSOR
      in NOTIFICATION conversation
      emitting event WarehouseNotified     // 流终点，无下游 triggers

// 命令通道：点对点 + 死信；消息意图 = COMMAND_MESSAGE
channel ShipmentCommands of type POINT_TO_POINT
  delivery guarantee AT_LEAST_ONCE
  on path "queue://shipment/commands"
  accepts message CreateShipmentCommand
    expecting payload Shipment as COMMAND_MESSAGE

channel ShipmentCommandsDLQ of type DEAD_LETTER
  on path "queue://shipment/commands/dlq"
  accepts message CreateShipmentCommand
    expecting payload Shipment as COMMAND_MESSAGE

// 事件通道：发布-订阅 + 保证投递；消息意图 = EVENT_MESSAGE
channel ShipmentEvents of type PUBLISH_SUBSCRIBE, GUARANTEED_DELIVERY
  delivery guarantee AT_LEAST_ONCE
  on path "topic://shipment/events"
  produces message ShipmentCreatedEvent
    delivering payload Shipment as EVENT_MESSAGE

// 消息代理：暴露通道，地址与协议绑定按部署上下文确定
message broker ShipmentBroker
  exposes ShipmentCommands, ShipmentEvents
    at location "amqp://broker.internal:5672"
    via protocol AMQP

// 集成流：+ / and = 并行，x / xor / alternatively = 互斥其一，o / or = 包含（一个或多个）
flow ShipmentFulfillmentFlow type INTEGRATION_FLOW
  event OrderPaid triggers command CreateShipment + NotifyWarehouse
  command CreateShipment emits event ShipmentCreated
  command NotifyWarehouse emits event WarehouseNotified
  event ShipmentCreated triggers command TrackShipment
```

**过程记录（端点通道使用、补偿、未映射元素）**：

```yaml
event_flow_record:
  endpoint_channels:                 # 通道使用属 message endpoint 规则（clients 槽位，排在 message broker 之后），
                                     # 与契约中的 endpoint type ShipmentEndpoint（contracts 槽位）同名会冲突，故此处带外登记。
                                     # 若要落成 DSL：另取名字（如 ShipmentConsumer），句式 message endpoint <name> uses from <broker>: <channel>, <channel>
    ShipmentEndpoint: [ShipmentCommands, ShipmentEvents]
  compensation:
    operation: cancelShipment        # createShipment 的业务级撤销，同端点内
  correlation: PENDING               # 请求-应答通道须声明关联标识（where 子句的 CorrelationIdWhereClause）与应答通道
  unmapped_elements:                 # 已知局限 1：并非所有事件风暴元素都有建模对应物
    - element: "策略：超时自动取消"
      status: NO_MODEL_COUNTERPART   # 本轮无建模对应物 → 人工跟进
```

## 技术交付物

1. 结构化领域事件/命令模型（含聚合、角色、读模型、事件流）
2. 流程视图（流程记法表示，标注流类型与并行/汇合结构）
3. 事件↔操作映射表（每个流程元素可追溯到端点操作）
4. 端点清单（含操作职责、状态迁移声明、补偿声明）
5. 技术专属契约（OpenAPI/gRPC/GraphQL/AsyncAPI 类派生物）
6. 集成流/消息路由定义（通道、代理、关联标识、死信、投递保证）
7. 未映射事件风暴元素清单（已知局限的显式记录）

## 成功标准

- 每个事件/命令在契约层有对应操作或消息（或出现在未映射清单中）
- 流程视图与端点清单一致：每条流步骤可追溯到操作，反之亦然
- 异步交互的错误/补偿路径已建模（死信通道、补偿操作有明确去处）
- 命令侧/查询侧职责分离清晰（CQRS 场景）
- 已知局限已向团队显式声明，无"便利贴静默消失"

## 反模式

| 反模式 | 为何失败 |
|--------|----------|
| 事件写成命令 | 事件是已发生之事（过去时），命令是请求之动作（祈使语气）；语气混淆导致职责与幂等语义无法判定 |
| 只画流程图不落契约 | 白板与流程图不可校验、不可追溯；不固化为结构化模型等于没有设计 |
| 强行同步化 | 把事件密集交互硬塞进请求-响应 API；协议取决于上下文，忽略它就是 HTTP 确认偏误 |
| 忽略补偿与死信 | 异步失败是常态；缺补偿/死信路径等于把生产事故预留给消费方 |
| 隐藏建模局限 | 假装每个风暴元素都有建模对应物；未映射元素必须显式登记而非悄悄丢弃 |
| 一次性推导不再精化 | 五步是"连续精化"过程；每步产物都需人工评审回灌，推导不是免检通道 |

## 关联

- **编排路线（事件密集系统）**: [SOP-03](sop-03-event-storming-modeling.md)（风暴固化）→ 09 → [SOP-10](sop-10-map-decoration.md)（模式精化）→ [SOP-12](sop-12-model-code-validation.md)（守护）
- 步骤 1 直接消费 [SOP-03](sop-03-event-storming-modeling.md) 的产出（含事件溯源/CQRS 建模）
- 步骤 3 的端点角色/操作职责/表示元素精化 → [SOP-10](sop-10-map-decoration.md)
- 命令查询分离引发端点/上下文拆分时 → [SOP-05](sop-05-architectural-refactorings.md)（AR 目录）；拆分依据 → [SOP-06](sop-06-systematic-decomposition.md)
- 同步为主的集成场景改用 [SOP-08](sop-08-story-driven-service-design.md)（故事驱动）或 [SOP-07](sop-07-domain-driven-service-design.md)（领域驱动）

## 来源

- MDSL-Specification（站点研究报告）：§10.2 事件驱动服务设计博客摘要（五步流程、中间语言定位、已知局限）；§4.8 编排流（流步骤、并行/汇合、流类型与绑定）；§4.9 异步消息扩展 AsyncMDSL（通道类型、消息代理、消息端点、请求-应答通道）；§5 快速参考（含事件/命令类型的流示例）；§7 变换与重构（流到端点变换）
- CML-Specification（站点研究报告）：§39 事件风暴建模（可建模元素清单）、§40 事件溯源与 CQRS 建模
- 分析报告 §3 SOP-09 草案、§2 F2（五阶段管线）
- 语法形态核对（2026-10-10，`Microservice-API-Patterns/MDSL-Specification` @ master，`dsl-core/io.mdsl/src/io/mdsl/APIDescription.xtext`）：`ServiceSpecification` 元素顺序（`data type` → `relation type` → `event type` / `command type` → `endpoint type` / `channel` → `SLA template` → `API provider` / `message broker` → `API client` / `message endpoint` → `API gateway` → `flow` → `scenario`）；`ChannelContract`（`'channel' name ('of' 'type' ChannelType,…)? ('delivery' 'guarantee' DeliveryGuarantee)?` + `OneWayChannel` 或 `RequestReplyChannel`）、`ChannelType`（POINT_TO_POINT | PUBLISH_SUBSCRIBE | DATA_TYPE | INVALID_MESSAGE | DEAD_LETTER | GUARANTEED_DELIVERY）、`DeliveryGuarantee`（UNKNOWN | AT_LEAST_ONCE | AT_MOST_ONCE | EXACTLY_ONCE）、`OneWayChannel`（`on path "…"` + `accepts` / `produces` / `accepts and produces` + `message`）、`Message`（`'message' name ('description')? ('delivering'|'expecting') Payload`）、`Payload`（`DataTransferRepresentation ('as' MessageType)?`）、`MessageType`（COMMAND_MESSAGE | EVENT_MESSAGE | DOCUMENT_MESSAGE，即正文的三种消息意图）、`WhereClauses`（MESSAGE_EXPIRES / SEQUENCE_ID / CORRELATION_ID——请求-应答通道的关联标识）、`MessageBroker`（`'message' 'broker' name ('description')? ('exposes' AsyncEndpoint …)+`；`AsyncEndpoint` = `channels at location "…" via protocol <ProtocolBinding>`，`OtherBinding` 含 AMQP / JMS_ActiveMQ / Kafka / MQTT / STOMP / Web_Sockets / SOAP_HTTP / JSON-RPC / Avro_RPC / Thrift）、`MessageEndpoint`（`'message' 'endpoint' name ('of' 'type' …)? ('serves' 'as' …)? 'uses' ('channels:' …)? ('from' <broker> ':' …)?`）、`Orchestration`（`'flow' name ('version')? ('realizes' scenario)? ('type' FlowType)? steps* ('binding' 'to' …)? ('implemented' 'as' FlowTechnology)?`）、`FlowType`（APPLICATION_FLOW | INTEGRATION_FLOW | SERVICE_ORCHESTRATION | API_CALL_SEQUENCING | EVENT_SOURCING）、`OperationResponsibility`（含 EVENT_PROCESSOR / STATE_CREATION_OPERATION / STATE_TRANSITION_OPERATION）
- 端点声明（`endpoint type`）的写法核对（2026-10-10，同上语法来源 + 官方示例 `examples/CustomerManagementExample.mdsl`、`examples/asyncMDSL/loan-broker-example.mdsl`、`examples/asyncMDSL/hello-world.mdsl`）：`EndpointContract` 子句顺序 `name → version? → supports ('flow'|'scenario')? → serves as ResourceRole ('and' ResourceRole)* 'role'? → SecurityPolicy? → exposes Operation+? → receives Event+?`；`exposes` **只写一次**后接多个 `operation`（`ops+=Operation+`，重复 `exposes` 不合法）；`Operation` 内部顺序 `version? → with responsibility → in <MEP> conversation → expecting → delivering (→ links → reporting) → transitions → emitting → compensated by → protected by`；`StateTransition` = `'from' STRING 'to' STRING`（状态名**必须加引号**，是 STRING 不是 ID）；`compensated by` 的 `undo=[Operation]` 是**交叉引用**，目标操作必须在契约中真实声明（可前向引用同端点内后声明的操作）；`DataTransferRepresentation` = `('headers' …)? 'payload' ElementStructure ('structured as' TypeSystem)?`，`payload` 关键字必需；`ResourceRole` 取值 PROCESSING_RESOURCE | INFORMATION_HOLDER_RESOURCE | OPERATIONAL_DATA_HOLDER | MASTER_DATA_HOLDER | REFERENCE_DATA_HOLDER | DATA_TRANSFER_RESOURCE | LINK_LOOKUP_RESOURCE | STATEFUL_PROCESSING_RESOURCE | STATELESS_PROCESSING_RESOURCE | VALIDATION_RESOURCE | TRANSFORMATION_RESOURCE | COLLECTION_RESOURCE | MUTABLE_COLLECTION_RESOURCE | STRING，其中 `MUTABLE_COLLECTION_RESOURCE` 按语法注释是任何 INFORMATION_HOLDER_RESOURCE 的**次级角色**（故 `OPERATIONAL_DATA_HOLDER and MUTABLE_COLLECTION_RESOURCE` 是文档化组合）；`MessageEndpoint`（`message endpoint`，clients 槽位）与 `EndpointContract`（`endpoint type`，contracts 槽位）是**两条不同规则**，且前者的 `serves as` 用逗号分隔、后者用 `and`；官方 async 示例的顺序实证为 `data type` → `channel` → `message broker` → `message endpoint`，与 contracts → providers → clients 槽位顺序一致
- 步骤 3 映射表的规则名核对（同上来源与日期）：`FlowStep`（`DomainEventProductionStep` | `CommandInvokationStep` | `CombinedInvocationStep`；**无** `EventEmissionStep` 这一规则）、`CommandInvokation` 与 `EventProduction` 各四种分支规则、`OrchestrationBinding`（`'binding' 'to' (EndpointTypeBinding|ChannelBinding)+ ('implemented' 'as' FlowTechnology)?`）、`StepToEndpointBinding`（`EventToOperationBinding` | `CommandToOperationBinding`）、`StepToChannelBinding`（`EventToMessageBinding` | `CommandToMessageBinding`）、`EndpointContract`（`'endpoint' 'type' name … ('supports' 'flow'|'scenario')? ('serves' 'as' ResourceRole …)? ('exposes' Operation+)? ('receives' Event+)?`）、`Operation`（`with responsibility` / `in <MessageExchangePattern> conversation` / `expecting` / `delivering` / `transitions` / `emitting` / `compensated by` / `protected by`）、`StateTransition`（`'from' STRING 'to' STRING`）、`MessageExchangePattern`（ONE_WAY | REQUEST_REPLY | NOTIFICATION | STRING）、`OperationResponsibility` 完整枚举（COMPUTATION_FUNCTION | STATE_CREATION_OPERATION | RETRIEVAL_OPERATION | STATE_TRANSITION_OPERATION | EVENT_PROCESSOR | BUSINESS_ACTIVITY_PROCESSOR | STATE_REPLACEMENT_OPERATION | STATE_DELETION_OPERATION | STRING）、`ScenarioType`（BUSINESS_API | FRONTEND_INTEGRATION_SCENARIO | BACKEND_INTEGRATION_SCENARIO）

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下片段忠实摘自语料原文，供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考。上方「使用示例」已按 AsyncMDSL 语法写成**一份完整契约**（含步骤 3 的 `endpoint type` 声明、步骤 5 的通道/代理/集成流）；摘录按约定保留。对照 master 语法有三点需精确理解：① §5 摘录 `triggers command Command1 or Command2` 里的 `or` 属**包含**分支（`InclusiveAlternativeCommandInvokation`：`o | O | or`，一个或多个），互斥分支是 `x | X | xor | alternatively`——不要把 `or` 读成 XOR；② `CommandInvokationStep` 的**事件侧**不支持 `or`/`xor`（语法注释明示），多个事件触发同一命令只能用 `+`/`and`，或拆成多步；③ 消息意图的两种写法不可混用——`as COMMAND_MESSAGE`（全大写枚举 `MessageType`）只在 `channel` 的 `Payload` 规则里合法，端点操作的 `expecting`/`delivering` 接的是 `DataTransferRepresentation`（无 `as MessageType`），要标 EIP 意图得用 `<<Command_Message>>` 前缀（`TypeReference` 的 classifier 位，混合大小写 `EipPattern`）。

**含事件/命令类型的流（MDSL §5 快速参考）**——步骤 1/2 的事件-命令流表示：

```mdsl
event type FlowInitiated
event type Event0, Event1, Event2
event type FlowTerminated

command type StartFlowCommand
command type Command1, Command2, Command3, Command4
command type TerminateCommand

flow SampleFlow
event FlowInitiated triggers command Command1 or Command2
command Command1 emits event Event1 
command Command2 emits event Event2
event Event1 and Event2 trigger commands Command3 and Command4
command Command3 emits event FlowTerminated
command Command4 emits event FlowTerminated
```

**流实现场景 + 流步骤形态（MDSL §4.8）**——组合步骤、拆分步骤、并行与汇合：

```mdsl
flow Scenario1Flow realizes Scenario1

event something_has_happened triggers command startProcess
command startProcess emits event startProcessCompleted
event CRUDSomeBusinessObjectTrigger triggers command CRUDSomeBusinessObject
event startProcessCompleted triggers command startProcessCompletedProcessor
command CRUDSomeBusinessObject emits event CRUDSomeBusinessObjectCompleted
```

流步骤类型（§4.8，括号为 master 语法规则名）：`FlowStep` = `DomainEventProductionStep`（`command C emits event E`）| `CommandInvokationStep`（`event E triggers command C`）| `CombinedInvocationStep`（组合步骤 `event Event1 triggers command Command1 emits event Event2`）。命令侧分支由 `CommandInvokation` 承载：`SingleCommandInvokation`、`ConcurrentCommandInvokation`（`+`/`and`，AND 并行）、`ExclusiveAlternativeCommandInvokation`（`x`/`X`/`xor`/`alternatively`，互斥其一）、`InclusiveAlternativeCommandInvokation`（`o`/`O`/`or`，**包含**——一个或多个，不要读成 XOR）；事件生产侧同构：`SingleEventProduction` / `MultipleEventProduction` / `ExclusiveAlternativeEventProduction` / `InclusiveAlternativeEventProduction`。汇合（join）= `CommandInvokationStep` 事件侧的多事件列表 `event Command1Done + Command2Done trigger command JoinedContinuationCommand`，无独立规则。子流程调用走 `EitherCommandOrOperationInvokation` 的 `'flow' SubProcessInvocation` 分支（`subprocess=[Orchestration]`）；流实现技术用 `implemented as <FlowTechnology>`（APACHE_CAMEL_ROUTE | SPRING_INTEGRATION_FLOW | BPMN_PROCESS | BPEL_PROCESS | YET_ANOTHER_FLOW_LANGUAGE | PLAIN_PROGRAMMING）。

**流到端点变换（MDSL §7）**——步骤 3 推导规则的原始定义：

| MDSL 元素 | 变换 | 产物 | 备注 |
|---|---|---|---|
| Flow | Derive endpoint type from application flow | 端点新增，接收流启动事件 | 操作可后补 |
| Command in flow step | Derive operation(s) realizing command(s) | `STATE_TRANSITION_OPERATION` 装饰 | 追加 `transitions from ... to ...` |
| Event in flow step | Derive event handler operation | `EVENT_PROCESSOR` 装饰 | 追加 `emitting event`，事件加入 `receives` |

**异步通道建模（MDSL §4.9 AsyncMDSL 高级示例）**——步骤 5 的通道/意图/约束/协议绑定：

```mdsl
channel PatientMeasurements
of type PUBLISH_SUBSCRIBE, DATA_TYPE
delivery guarantee AT_LEAST_ONCE
description "Notifies whenever a new measurement comes"
on path "/patients/${patientId}/measurement"
	with 
        patientId: int, "The patient identifier" 
accepts message Measurement
	description "Contains the value and the type of the measurement"
	expecting 
		headers HeadersDTO
		payload MeasurementDTO as EVENT_MESSAGE
	where 
		MESSAGE_EXPIRES in 60m
bindings for MQTT {
    "qos": 1
}
```

通道类型枚举（§4.9）：`POINT_TO_POINT | PUBLISH_SUBSCRIBE | DATA_TYPE | INVALID_MESSAGE | DEAD_LETTER | GUARANTEED_DELIVERY`。

</details>
