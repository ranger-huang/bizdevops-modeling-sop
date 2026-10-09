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

从流程与聚合推导端点及操作，映射规则：

| 流程元素 | 端点产物 | 操作职责（MAP 模式名） |
|----------|----------|------------------------|
| 流的启动事件 | 端点声明接收该事件 | —（事件入口） |
| 命令 | 状态创建操作或状态迁移操作，附 from→to 状态声明 | State Creation Operation / State Transition Operation |
| 事件 | 事件处理操作（通知型），声明其发出的事件 | Event Processor |

- 一个命令/事件对应一个操作；操作与流程步骤一一可追溯
- 需要业务级撤销时，在**同一端点内**为操作声明补偿操作（saga 支持）
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

订单履约事件流（工具中立结构化模板）：

```
步骤 1–2：领域模型 + 流程视图（文本图）

  [订单已支付] ──触发──> 〈创建发货单〉 ──发出──> [发货单已创建]
       │                                              │
       └──触发──> 〈通知仓库〉 ──发出──> [仓库已通知]   └──触发──> 〈跟踪物流〉

  流类型: 集成流；并行分支: AND（创建发货单 与 通知仓库 并行）

步骤 3：事件↔操作映射表

| 流程元素          | 端点             | 操作              | 职责                  | 状态声明              |
|-------------------|------------------|-------------------|-----------------------|-----------------------|
| 订单已支付(事件)   | ShipmentEndpoint | （接收声明）       | —                     | —                     |
| 创建发货单(命令)   | ShipmentEndpoint | createShipment    | State Creation        | 未发货 → 已发货        |
| 发货单已创建(事件) | ShipmentEndpoint | onShipmentCreated | Event Processor(通知) | 发出 发货单已创建      |
| 通知仓库(命令)     | WarehouseEndpoint| notifyWarehouse   | State Transition      | 仓库待通知 → 已通知    |

步骤 5：消息路由/集成流（YAML 风格伪码）

channels:
  ShipmentCommands:  { 类型: 点对点,   接受: 命令消息 创建发货单, 死信: ShipmentCommands.DLQ }
  ShipmentEvents:    { 类型: 发布-订阅, 投递保证: 至少一次, 产生: 事件消息 发货单已创建 }
broker:  消息代理（地址与协议绑定按部署上下文确定）
endpoints:
  ShipmentEndpoint:  使用 [ShipmentCommands, ShipmentEvents]
补偿:  cancelShipment（createShipment 的业务级撤销，同端点内）
未映射元素登记:  [策略: 超时自动取消]（本轮无建模对应物 → 人工跟进）
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

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下片段忠实摘自语料原文，供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考。

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

流步骤类型（§4.8）：组合步骤 `event Event1 triggers command Command1 emits event Event2`；并行分支 `+`（AND）、`o`（OR）、`x`（XOR）；汇合 `event Command1Done + Command2Done trigger command JoinedContinuationCommand`。

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
