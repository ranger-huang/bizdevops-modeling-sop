# SOP-03: 事件风暴结果建模（Event Storming Modeling，含事件溯源/CQRS）

> **定位**: 把事件风暴（Event Storming）工作坊的便利贴产出固化为精确、可校验、可演进的领域模型，并覆盖事件溯源（Event Sourcing）与 CQRS 架构的建模差异 | **组**: A（需求到模型） | **主要来源**: CML-Specification §39/§40/§18–20；MDSL-Specification §10.2

## 何时启用

- 当事件风暴工作坊刚结束、白板产出需要固化为结构化领域模型时，立即使用本 SOP（拖延即丢失）
- 当团队需要统一、可校验的模型表示来替代散落的便利贴照片时，使用本 SOP
- 当事件溯源 / CQRS 风格系统需要建模状态事件、聚合生命周期与命令–查询分离时，使用本 SOP 的第 3–4 步
- 当后续要做事件驱动的 API 与集成流设计（[SOP-09](sop-09-event-driven-service-design.md)）而缺少模型输入时，先走本 SOP

## 触发条件

- 已完成事件风暴或类似的协作式领域探索，白板/便利贴产出面临丢失或走样风险
- 同一业务对象在不同团队的统一语言（ubiquitous language）不一致，需要借事件流重新划界
- 系统以事件/命令流为主要交互方式（异步、事件密集集成场景）
- 需要把探索性产出升级为可机器校验的模型（进入 SOP-05/06 演进与 SOP-12 守护的前提）

## 完整步骤

### 第 1 步：逐项映射（便利贴 → 模型元素）

事件风暴的每类产出都有明确的模型对应物（可选项按需建模）：

| 工作坊产出 | 模型元素 | 说明 |
|-----------|---------|------|
| 领域事件（过去时便利贴） | 领域事件（Domain Event） | 领域中已发生之事 |
| 命令 | 命令（Command） | 引发领域事件的动作 |
| 一致性边界/业务对象 | 聚合（Aggregate，或聚合根实体） | 存储与一致性单元 |
| 问题/热点 | 问题（Issue，可选） | 记录争议点与未决事项 |
| 用户角色 | 用户角色（User Role，可选） | 命令的发起者 |
| 视图/读侧 | 视图 / 读模型（View / Read Model，可选） | CQRS 的查询侧 |
| 时间线上的串联 | 事件流（Event Flow，可选） | 命令–事件链；新版流程特性可更好地表达事件风暴结果 |

映射纪律：每张关键便利贴要么有模型对应物，要么登记为问题/TODO——**不允许静默丢弃**。

### 第 2 步：圈定战略边界

- 按事件流的中断点与统一语言的差异圈定限界上下文（Bounded Context）与子域（Subdomain）
- 每个边界必须能用一句话解释依据："这里语言变了（同名异义/异名同义）"或"事件流在此中断、跨团队交接"
- 边界存疑处登记为问题，留给 [SOP-05](sop-05-architectural-refactorings.md)/[SOP-06](sop-06-systematic-decomposition.md) 用准则证据裁决

### 第 3 步：聚合与状态建模（事件溯源场景必做）

事件溯源系统的状态由事件序列重建，建模重点：

- 聚合内声明领域事件（含属性、完成时间/登记时间等时间戳）
- 声明聚合生命周期（aggregate lifecycle）：以枚举列出全部状态
- 每个**写操作**显式标注状态迁移；只读操作标注 read-only。迁移记法的完整变体：
  - 初始状态：`-> CREATED`
  - 简单迁移：`CREATED -> CHECK_REQUESTED`
  - 多源状态（任一源均可迁移）：`CREATED, CHECK_REQUESTED -> CHECK_IN_PROGRESS`
  - 互斥目标（XOR，只达其一）：`CHECK_IN_PROGRESS -> ACCEPTED X REJECTED`
  - 终态标记（`*`）：`ACCEPTED* X REJECTED*`

### 第 4 步：CQRS 建模（命令侧与查询侧分离）

- 命令侧：在应用层（Application Layer）登记命令与发布的事件——应用层声明哪些服务/命令可从限界上下文外部调用、哪些事件对外发布
- 查询侧：视图/读模型独立建模（第 1 步的可选元素在此成为必需）
- 用应用层**流程（Flow）**串联两侧：`command X emits event Y`（事件产生）、`event X triggers command Y`（命令触发）；也可用 operation 替代 command 表述
- 流程操作符：`+` 全部（并行网关语义）、`X` 互斥其一（排他网关）、`O` 一个或多个（包含网关）
- 流程可加委派（delegates to 聚合）并附状态迁移与发起者标注
- 跨限界上下文的流程用协调（Coordination）声明，逐条引用各上下文的应用服务操作

### 第 5 步：校验与评审

- 建模语言校验：无悬空引用（流程引用的命令/事件/操作均已声明）、流程闭合
- 团队评审两问：白板上每个关键便利贴有对应物吗？每条 BC 边界的依据能复述吗？
- **显式声明已知局限**：并非所有事件风暴元素都有对应建模概念，转换也不支持全部语言特性（语料明确承认）——未映射项登记为问题清单，随模型一起交付

### 第 6 步（可选）：下游推导管线

固化的模型可沿五步管线走向实现（工具中立表述；详见 [SOP-09](sop-09-event-driven-service-design.md)）：

1. 协作白板勾画命令/事件 → 转入领域模型（即本 SOP 第 1–2 步）
2. 从模型派生**流程视图**（活动/事件流的流程记法表示）
3. 从流程与聚合推导**服务层 API 端点**：事件 → 通知型操作；命令 → 状态创建/状态迁移操作
4. 派生技术专属 API 契约（抽象契约先行，一份模型多种技术绑定）
5. 设计消息路由/集成流（端点间的事件编排）

## 使用示例

理赔管理流程（语料真实案例的中立化呈现）：

**便利贴 → 模型映射表**：

| 便利贴 | 类型 | 模型对应物 |
|--------|------|-----------|
| "理赔已提交" | 领域事件 | Event ClaimSubmitted |
| "提交理赔" | 命令 | Command SubmitClaim |
| "理赔单" | 聚合 | Aggregate Claims（根实体 Claim） |
| "理赔员" | 用户角色 | 命令发起者标注 |
| "评估通过还是拒绝？" | 问题/分支 | 流程中的互斥操作符 X |

**应用层流程（含互斥分支）**：

```cml
BoundedContext ClaimsManagement {
	Application {
		// 命令侧：声明可从限界上下文外部调用的命令
		Command SubmitClaim
		Command CheckClaimDocumentation
		Command CheckInsurance
		Command AcceptClaim
		Command RejectClaim

		// 对外发布的领域事件
		Event ClaimSubmitted
		Event ClaimRegistered
		Event AssessmentPerformed
		Event ClaimAccepted
		Event ClaimRejected

		// 流程串联命令与事件；操作符 X = XOR 互斥其一，+ = 全部（并行），O = 一个或多个（包含）
		Flow ClaimsFlow {
			command SubmitClaim emits event ClaimSubmitted
			event ClaimSubmitted triggers command CheckClaimDocumentation
			command CheckClaimDocumentation emits event ClaimRegistered
			event ClaimRegistered triggers command CheckInsurance
			command CheckInsurance emits event AssessmentPerformed
			event AssessmentPerformed triggers command AcceptClaim X RejectClaim
			command AcceptClaim emits event ClaimAccepted
			command RejectClaim emits event ClaimRejected
		}
	}
}
```

**事件溯源视角的状态迁移（同一案例）**：

| 操作 | 读写 | 状态迁移 |
|------|------|---------|
| submitClaim | write | `-> OPEN`（初始状态） |
| checkInsurance | read-only（无迁移） | |
| acceptClaim | write | `OPEN -> ACCEPTED*` |
| rejectClaim | write | `OPEN -> REJECTED*` |

同一内容的原生 CML：`enum` + `aggregateLifecycle` 声明聚合生命周期，写操作以 `: write [ FROM -> TO ]` 标注迁移，`*` 为终态标记（`TargetState: value=[EnumValue] (endState?='*')?`）：

```cml
// 事件溯源视角：聚合生命周期 + 每个写操作的显式状态迁移（与上表一一对应）
enum ClaimStates {
	aggregateLifecycle
	OPEN, ACCEPTED, REJECTED
}

Aggregate Claims {
	Entity Claim {
		String claimId key
		String reason4Rejection
	}

	// 聚合侧操作是应用层 Command 的对应物（流程中亦可用 operation 替代 command 表述）
	Service ClaimsService {
		String submitClaim (@Claim claim) : write [ -> OPEN ];              // 初始状态
		boolean checkInsurance (String claimId) : read-only;                // 只读，无迁移
		boolean acceptClaim (String claimId) : write [ OPEN -> ACCEPTED* ]; // * = 终态
		boolean rejectClaim (String claimId) : write [ OPEN -> REJECTED* ];
	}
}
```

## 技术交付物

- 结构化领域模型：领域事件 / 命令 / 聚合（+ 可选：问题、用户角色、读模型、事件流）
- 限界上下文边界划分及**依据说明**（语言边界/事件流中断点）
- 状态迁移图（事件溯源场景：生命周期状态 + 迁移 + 终态标记）
- 应用层流程定义（含操作符语义）与跨上下文协调声明
- 未映射便利贴的问题清单（已知局限的显式记录）
- （走第 6 步时）流程视图、端点清单、事件 ↔ 操作映射表

## 成功标准

- 白板上每个关键便利贴有模型对应物或已登记的问题（无静默丢失）
- 限界上下文边界能用语言边界/事件流中断解释，团队评审通过
- 模型通过建模语言校验：引用完整、流程闭合、状态迁移无悬空状态
- 事件溯源场景：每个写操作的状态迁移显式可审（支撑事件重放语义）
- CQRS 场景：命令侧与查询侧分别建模，应用层流程把两侧串联闭合

## 反模式

- **白板拍照即建模**：照片不可机器校验、无法演进、无法推导契约——精确模型是后续 SOP-05/09/12 的前提（对应报告反模式"手绘上下文映射"）
- **假装全覆盖**：不声明"并非所有事件风暴元素都有模型对应物"的已知局限，未映射信息静默丢失
- **只建快乐路径**：流程漏掉互斥分支（X）、失败与补偿路径；下游集成设计（SOP-09）才发现异步错误路径未建模
- **CQRS 单侧化**：漏建读模型/视图，或命令与查询混在同一服务里且不标注 read-only / write
- **状态迁移含糊**：事件溯源系统不声明生命周期与迁移，事件重放后的状态不可审计
- **一次性划界**：把工作坊当轮的边界当终局；边界应随准则证据经 SOP-05/06 增量演进

## 关联

- 同组互补：[SOP-01](sop-01-rapid-ooad.md)（书面需求存在时的另一建模入口，二者互为替代）；[SOP-02](sop-02-story-splitting.md)（命令语义复合时先拆故事）
- 直接下游：[SOP-09](sop-09-event-driven-service-design.md)（从模型派生端点、契约与集成流——第 6 步管线的承接者）
- 演进与治理：[SOP-05](sop-05-architectural-refactorings.md)（边界与聚合的 AR 重构）；[SOP-06](sop-06-systematic-decomposition.md)（事件风暴产出可作耦合准则证据输入）；[SOP-12](sop-12-model-code-validation.md)（模型–代码一致性守护）
- 编排路线（事件密集系统）：**SOP-03** → 09 → 10 → 12；（绿地项目）13 → 01/**03** → 04 → 05/06 → 07 → 10 → 12

## 来源

- CML-Specification §39（Event Storming Modeling：九类模型元素映射清单；事件/命令流特性备注）
- CML-Specification §40（Event Sourcing & CQRS Modeling：聚合内领域事件、命令、应用层流程、状态迁移）
- CML-Specification §18（聚合生命周期与状态迁移记法全部变体）、§19（战术 DDD：实体/领域事件/命令/服务/仓库）、§20（应用层：命令/事件、流程与操作符、委派、协调）
- MDSL-Specification §10.2（Event-Driven Service Design：五步工作流、中间语言定位、已知局限声明）
- ICWE 2020 keynote（事件风暴用于发现领域模型元素；五阶段管线）
- 语法形态核对（2026-10-10，`ContextMapper/context-mapper-dsl` @ master）：`ContextMappingDSL.xtext` 的 `Application`（commands / events / services / flows / coordinations 五类成员）、`Flow` 与 `FlowStep`（`DomainEventProductionStep` = `command X [delegates to Agg [迁移]] emits event Y`；`CommandInvokationStep` = `event X triggers command A X B`；操作符 `+`/`X`/`O`）、`Coordination`（`BC :: Service :: operation;`）；`TacticDDDLanguage.xtext` 的 `("Command" | "CommandEvent")` 与 `("DomainEvent" | "Event")`（体均可省）、`Enum`（`aggregateLifecycle` 关键字）、`TargetState`（`*` 终态标记）、`ServiceOperation`（`: write [ FROM -> TO ]` / `: read-only`）

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下代码块忠实摘自语料原文，供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考；每段标注来源与用途。上方「使用示例」的两段已是**原生 CML**（应用层命令/事件/流程 + 聚合生命周期与状态迁移），与下方 §20 的 Application/Flow 摘录、§18 的生命周期摘录同形——摘录按约定保留，作为语料原文证据。

**CML 领域事件与命令（CML-Specification §19，第 1 步映射的目标语法）**：

```cml
DomainEvent HandlingEvent {
  Type handlingType;
  - Voyage voyage;
  - LocationShared location;
  Date completionTime;
  Date registrationTime;
  - Cargo cargo;
}

Command RejectClaim {
  - Claim claim2Reject
  - Employee decisionMaker
  String reason4Rejection
}
```

**CML 聚合生命周期与写操作状态迁移（CML-Specification §18，第 3 步事件溯源建模）**：

```cml
enum States {
  aggregateLifecycle
  CREATED, POLICE_CREATED, RECALLED
}

Service ContractService {
  @ContractId createContract(@Contract contrace) : write [ -> CREATED];
  @Contract getContract(@ContractId contractId) : read-only;
  boolean createPolicy(@ContractId contractId) : write [ CREATED -> POLICE_CREATED ];
  boolean recall(@ContractId contractId) : write [ CREATED, POLICE_CREATED -> RECALLED ];
}
```

**CML 状态迁移记法全部变体（CML-Specification §18，X=XOR 互斥目标，\*=终态标记）**：

```cml
// an initial state:
-> CREATED

// simple state transition from one state into the other
CREATED -> CHECK_REQUESTED

// the left side can contain multiple states:
// (this means that the state on the right can be reached by any of those on the left side)
CREATED, CHECK_REQUESTED -> CHECK_IN_PROGRESS

// multiple target states possible
// X stands for XOR and means one OR the other will be reached but not both at the same time (exclusive OR)
CHECK_IN_PROGRESS -> ACCEPTED X REJECTED

// target state markers (*) indicate end states
CHECK_IN_PROGRESS -> ACCEPTED* X REJECTED*
```

**CML 应用层命令与事件（CML-Specification §20，第 4 步 CQRS 命令侧）**：

```cml
Application {
  Command SubmitClaim {
    // attributes/body optional
  }
  Command AcceptClaim
  Command RejectClaim
  
  Event ClaimSubmitted {
    // attributes/body optional
  }
  Event ClaimAccepted
  Event ClaimRejected
}
```

**CML 应用层流程与操作符（CML-Specification §20，第 4 步流程串联；+ 全部 / X 互斥 / O 包含）**：

```cml
Application {
  Flow ClaimsFlow {
    command SubmitClaim emits event ClaimSubmitted
    event ClaimSubmitted triggers command CheckClaimDocumentation
    command CheckClaimDocumentation emits event ClaimRegistered
    event ClaimRegistered triggers command CheckInsurance
    command CheckInsurance emits event AssessmentPerformed

    event AssessmentPerformed triggers command AcceptClaim X RejectClaim 
    command AcceptClaim emits event ClaimAccepted
    command RejectClaim emits event ClaimRejected
  }
}
```

**CML 委派与发起者标注（CML-Specification §20，流程精化）**：

```cml
// Delegate to aggregate
command SubmitClaim delegates to Claims emits event Event1 X Event2 X Event3

// With state transition
command SubmitClaim delegates to Claims [ -> SUBMITTED ] emits event Event1 X Event2 X Event3

// With initiator
command SubmitClaim [ initiated by "Customer" ] delegates to Claims [ -> SUBMITTED ] emits event Event1
```

**MDSL 事件/命令类型与流程（MDSL-Specification §5 Quick Reference，第 6 步契约侧流程语法）**：

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

</details>
