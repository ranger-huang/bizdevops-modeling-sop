# SOP-10: API 消息模式装饰（API Message Pattern Decoration with MAP）

> **定位**: 用微服务 API 模式语言（Microservice API Patterns, MAP）装饰契约骨架：表示元素刻板印象 → 端点角色 → 操作职责 → 结构模式力场权衡 → 演进检查 | **组**: C（契约设计） | **主要来源**: MDSL 规范 §3/§10.4、ICWE 2020 主题演讲 Part 3、APIace EuroPLoP 2021 §5.2

## 何时启用

当契约骨架（端点 + 操作 + 数据类型）已存在，需要精化消息表示、明确端点角色与操作职责、把质量属性权衡显式化时，使用本 SOP。MAP 的起点是**企业集成模式（EIP）止步之处**：EIP 定义了文档消息、命令消息、事件消息三种消息类型，MAP 研究这些消息的**载荷结构**——表示元素如何组织、端点承担什么角色、操作负什么职责、结构如何权衡。

MAP 语言组织（装饰时按类取用）：表示元素（Representation Elements）、基础模式（Foundation Patterns：API 可见性与使用方向等）、职责模式（Responsibility Patterns：端点角色 + 操作职责）、结构模式与质量模式（Structural / Quality Patterns）。

## 触发条件

- 契约评审发现表示元素语义不明（这个字段是标识符、业务数据、链接还是元数据？）
- 性能/一致性/可演进性的权衡需要显式决策（嵌入还是链接？分页选哪种？）
- 新端点/新操作设计，需要角色与职责身份
- [SOP-11](sop-11-api-structure-analysis.md) 输出存量 API 修正建议，需按力场选择目标模式
- 消费方抱怨"接口语义要靠猜"

## 完整步骤

### 步骤 1：表示元素刻板印象（Element Stereotypes）

为每个表示元素标注**名称-角色-类型三元组**（IRT：Identifier-Role-Type）：

| 刻板印象 | 含义 | 典型例子 |
|----------|------|----------|
| ID（标识符元素，Identifier Element） | 标识某实体/资源 | customerId、orderNo |
| Link（链接元素，Link Element） | 指向另一个 API 端点的引用 | 关联资源地址 |
| Data（数据元素，Data Element） | 业务数据本体 | name、amount |
| Metadata（元数据元素，Metadata Element） | 描述数据的数据 | 时间戳、分页信息 |

- 元数据特化：Control Metadata（控制元数据）、Aggregated Metadata（聚合元数据）、Provenance Metadata（溯源元数据）
- 结构刻板印象：Parameter Tree（参数树，嵌套结构）、Atomic Parameter（原子参数）
- 基本类型：bool / int / long / double / string / raw / void
- **基数标记**：可选（0 或 1）、零或多、一或多、恰好一（默认）；**可变性**：一个元素可为多类型之选（如整数或字符串）
- 允许占位符（不定型元素）——先标角色后补类型，符合敏捷建模

### 步骤 2：端点角色（Endpoint Roles）

| 端点角色 | 当 Y 时使用 |
|----------|-------------|
| Information Holder Resource（信息持有者资源） | 端点以提供数据访问为主 |
| — Master Data Holder（主数据持有者） | 主数据：大量读取、少量笨重的创建/更新 |
| — Operational Data Holder（运营数据持有者） | 运营数据：可枚举 + 可追加，常支持整集合变更 |
| — Reference Data Holder（参考数据持有者） | 参考数据：只读，仅枚举 |
| — Data Transfer Resource（数据传输资源） | 解耦多个应用客户端的临时数据中转 |
| — Link Lookup Resource（链接查找资源） | 返回一组相关链接 |
| Processing Resource（处理资源） | 端点以执行计算/处理为主（特化：Validation / Transformation / Stateless Processing Resource） |
| Collection Resource（集合资源） | 暴露集合访问（常与 Information Holder 并用） |

与 [SOP-11](sop-11-api-structure-analysis.md) 结构原语的经验对应（存量 API 交叉验证用）：Master Data Holder ≈ 可枚举 + 可追加集合；Operational Data Holder ≈ 可枚举 + 可追加（常为可变集合）；Reference Data Holder ≈ 只读可枚举集合（Enumerable Collection）；Data Transfer Resource ≈ 可变集合（Mutable Collection）；一组 Link Lookup Resource ≈ Collection。

### 步骤 3：操作职责（Operation Responsibilities）

| 操作职责 | 含义 | HTTP 动词经验映射 |
|----------|------|-------------------|
| Retrieval Operation | 读取，无副作用 | GET |
| State Creation Operation | 创建状态 | POST |
| State Transition Operation | 变更状态 | PUT（全量替换变体）/ PATCH（部分更新变体）/ POST（部分更新变体） |
| State Deletion Operation | 删除状态（State Transition 的变体） | DELETE |
| Computation Function | 计算并返回结果，不改状态 | GET（参数简单时）或 POST（参数复杂时） |
| Event Processor | 事件处理（通知型，异步场景） | —（消息协议） |

动词映射来自对大规模真实 API 的实证归纳：**设计新 API** 时用它校验绑定一致性（声明 Retrieval 却绑定 POST 需要解释）；**盘点存量 API** 时用它反推真实职责（见 SOP-11）。

### 步骤 4：力场权衡选结构模式

决策规则：**当客户端需要关联数据且往返代价高时用 Embedded Entity；当消息过大且数据并非全需时用 Linked Information Holder；当结果集大时用 Pagination。**

**模式对 1：Embedded Entity vs. Linked Information Holder**（同一力场，相反解法）

| | Embedded Entity（嵌入实体） | Linked Information Holder（链接信息持有者） |
|---|---|---|
| 问题 | 接收方需要洞察多个相关信息元素时，如何避免交换多条消息？ | 暴露结构化、可能深度嵌套的信息时，如何避免发送充满"接收方未必全需"数据的大消息？ |
| 解法 | 对客户端必须跟随的每个关系，在消息中嵌入目标实体的数据元素（而非链接） | 在消息中添加引用另一 API 端点的链接元素；让该端点代表被链接实体（如一个 Information Holder Resource） |
| 力场 | 性能、可扩展性 ↔ 灵活性、可修改性 ↔ 数据质量、新鲜度、一致性 | 同左（同一力场的另一侧取舍） |

**模式 2：Pagination（分页）**——七段模板完整示例：

- **Context**: 端点及其调用已识别并规格化
- **Problem**: 提供方如何优化"向客户端返回大量同构数据"的响应？
- **Forces**: 数据集大小与访问画像（消费方需要多少记录）；数据可变性（结果元素是否同构、定义变更频率）；双方可用内存；网络能力（服务器拓扑、中间件）；安全与健壮性/可靠性
- **Solution**: 把大响应数据集切成可管理、易传输的块；首条响应只发部分结果并告知如何增量获取；消费方按需迭代处理；双方约定请求关联与部分结果的终止策略
- **Variants**: 游标式（cursor-based）vs. 偏移式（offset-based）——按数据变化频率选择
- **Consequences**: 例如需要状态管理（游标/进度保存）
- **Known Uses**: 社交网络公开 API

**按需引入的其他质量/结构模式**：Request Bundle（批量请求）、Wish List / Wish Template（字段选择）、Request Condition（条件请求/过滤）、Context Representation（上下文表示）、Error Report（错误报告）。

**结构调整重构**（对既有设计动刀）：Extract Information Holder（嵌入实体 → 链接 + 独立端点）、Inline Information Holder（链接 → 嵌入）、Split Operation（按顶层请求元素拆操作）、Segregate Commands from Queries（CQRS 式命令查询分离，检索操作迁出）。

### 步骤 5：检查演进模式

- **版本化**：API 描述、端点、操作三级各自声明语义化版本号（x.y.z），变更影响范围可定位
- **契约长存**：框架与基础设施来来去去，API 契约长存——演进决策在契约层做，不在实现层做
- **兼容性扩展**：利用基数标记区分必选/可选元素；新增元素尽量标记为可选，控制对既有消费方的破坏面
- 每个模式决策按七段模板记录（见使用示例），保证可复盘

### MAP 模式模板（决策记录格式）

七段：**Context（上下文）/ Problem（问题）/ Forces（力场）/ Solution（解法）/ Variants（变体）/ Consequences（后果）/ Known Uses（已知用途）**。权衡记录至少填 Problem、Forces、Solution、Consequences 四段。

## 使用示例

客户查询端点的装饰记录（工具中立 YAML 风格伪码）：

```yaml
endpoint: CustomerEndpoint
  角色: Information Holder Resource — Master Data Holder      # 步骤 2
  版本: 1.1.0                                                  # 步骤 5
  operations:
    - name: lookupCustomer
      职责: Retrieval Operation                                # 步骤 3
      绑定校验: GET /customers/{customerId} ✓（动词↔职责一致）
      request:                                                 # 步骤 1 IRT
        - { 名称: customerId, 角色: ID, 类型: string }
      response:
        - { 名称: customerId,   角色: ID,   类型: int }
        - { 名称: fullName,     角色: Data, 类型: string }
        - { 名称: lastModified, 角色: Metadata, 类型: string }
        - { 名称: address,      模式: Embedded Entity }        # 决策 DR-1
        - { 名称: creditHistoryLink, 角色: Link,
            模式: Linked Information Holder }                  # 决策 DR-2
    - name: listCustomers
      职责: Retrieval Operation
      模式: Pagination（游标式）                                # 决策 DR-3

decisionRecords:                                               # 七段模板
  - id: DR-1
    pattern: Embedded Entity
    problem: 订单页面需一次获得客户地址，避免二次往返
    forces: 性能(+) / 消息体积(-) / 新鲜度(-，随客户主数据变化)
    solution: 在客户表示中嵌入地址数据元素
    consequences: 消息变大；地址一致性由提供方在响应组装时保证
  - id: DR-2
    pattern: Linked Information Holder
    problem: 信用历史庞大且多数调用不需要
    forces: 消息体积(+) / 往返次数(-，需要时多一跳)
    solution: 添加链接元素指向独立的信用历史端点
    knownUses: 社交网络公开 API（用户概要 + 详情链接）
  - id: DR-3
    pattern: Pagination (cursor-based)
    forces: 数据集大且变化频繁 → 游标式优于偏移式（避免漂移）
    consequences: 提供方需管理游标状态
```

## 技术交付物

1. 带模式装饰的契约（每个表示元素有角色、每个端点有角色、每个操作有职责）
2. 模式决策记录（七段模板，至少含 Problem/Forces/Solution/Consequences）
3. HTTP 动词 ↔ 操作职责一致性检查表
4. 版本化与兼容性策略声明

## 成功标准

- 无"裸"表示元素：每个元素皆有刻板印象（ID/Link/Data/Metadata 或显式占位符 + 精化计划）
- 每个端点有角色身份、每个操作有职责身份
- 每处结构模式决策可按七段模板复盘（说得清"为何嵌入而非链接"）
- 动词↔职责映射一致性检查通过，例外有记录的解释
- 版本策略在 API/端点/操作三级已声明

## 反模式

| 反模式 | 为何失败 |
|--------|----------|
| 裸表示元素 | 语义只存在于作者脑中；消费方靠猜字段是标识符还是数据，歧义转嫁给每个集成方 |
| 默认嵌入一切 | 消息膨胀、新鲜度与一致性失控；Embedded Entity 是权衡的一侧，不是默认值 |
| 分页不经力场 | 照抄游标/偏移而不评估数据集大小、可变性、内存与网络能力；变体选择失去依据 |
| 统一接口足以表达领域语义 | REST 动词过于贫瘠（确认偏误神话之一）；职责必须显式化（操作职责模式/操作标识），否则 POST 语义靠猜 |
| 模式名 cargo cult | 只贴模式名不写 Forces/Consequences；违反"目的高于合规"（见 [SOP-13](sop-13-method-engineering.md)） |
| NIH 综合征 | "我们的扩展性需求独一无二"→ 自造协议/框架；应先回到上下文做买/租/建决策，选建时套用模式 |
| 装饰一次不再维护 | 契约演进后装饰失效；版本升级时须重跑步骤 4/5 检查 |

## 关联

- **编排位置**: [SOP-07](sop-07-domain-driven-service-design.md) / [SOP-08](sop-08-story-driven-service-design.md) / [SOP-09](sop-09-event-driven-service-design.md)（契约骨架）→ **10** → [SOP-12](sop-12-model-code-validation.md)（守护）
- [SOP-11](sop-11-api-structure-analysis.md) 的坏味道修正建议 → 本 SOP 步骤 4 力场权衡落地
- 步骤 4 的 Segregate Commands from Queries 重构 → [SOP-09](sop-09-event-driven-service-design.md)（CQRS 场景）与 [SOP-05](sop-05-architectural-refactorings.md)（模型级重构）
- 步骤 2 端点角色 ↔ 原语对应表与 [SOP-11](sop-11-api-structure-analysis.md) 步骤 4 互为验证
- 决策记录的方法治理（裁剪、态度校验）→ [SOP-13](sop-13-method-engineering.md)

## 来源

- MDSL-Specification（站点研究报告）：§3 与 MAP 的集成（模式类别 ↔ 装饰位置、刻板印象全列表、元素角色表）；§10.4 MAP 元博客摘要（EIP 止步处、模式语言演进）；§5 快速参考（IRT 语法、基数、可变性）；§4.2 端点类型（角色/职责装饰概念）；§7 变换与重构（模式引入变换、结构重构）
- ICWE 2020 主题演讲（Zimmermann）：Part 3（Embedded Entity / Linked Information Holder 完整模式卡、Pagination 七段示例、神话破除 2/3：HTTP 确认偏误、NIH 综合征）
- APIace EuroPLoP 2021（Serbout, Pautasso, Zdun, Zimmermann）：§5.2（HTTP 动词 ↔ MAP 职责映射、Computation Function 绑定规则、端点角色 ↔ 结构原语对应）
- 分析报告 §2 F7、§3 SOP-10 草案

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下片段忠实摘自语料原文，供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考。

**MAP 模式类别与装饰位置（MDSL §3）**：

| MAP Pattern Category | MDSL Integration |
|---|---|
| **Representation Elements** | Serve as grammar rules in the data contract part (e.g., ParameterTree, AtomicParameter) |
| **Foundation Patterns** | Appear as decorators/annotations for the entire API description (e.g., `PUBLIC_API`, `FRONTEND_INTEGRATION`) |
| **Responsibility Patterns (Endpoint Roles)** | Serve as decorators for endpoint roles (e.g., `PROCESSING_RESOURCE`, `MASTER_DATA_HOLDER`) |
| **Responsibility Patterns (Operation Roles)** | Represented as decorators for operation responsibilities (e.g., `COMPUTATION_FUNCTION`, `EVENT_PROCESSOR`) |
| **Structural/Quality Patterns** | Appear as stereotypes annotating representation elements (e.g., `<<Embedded_Entity>>`, `<<Wish_List>>`) |

**MAP 刻板印象全列表（MDSL §3）**：

```
API_Key | Context_Representation | Request_Bundle | Request_Condition
Wish_List | Wish_Template | Pagination | Error_Report
Embedded_Entity | Linked_Information_Holder | Annotated_Parameter_Collection
Data_Element | Metadata_Element | Identifier_Element | Link_ELement
Control_Metadata | Aggregated_Metadata | Provenance_Metadata
```

**原子参数 IRT 语法与基数（MDSL §5 快速参考）**：

```
<<pattern>>"name": Role<Type>
```

Full example: `<<API_Key>>"accessToken1":D<string>`
Compact examples: `ID`, `D<bool>`, `L<string>`, `"resultCounter":MD<int>`
Placeholder: `P` (must not contain stereotype, role, or type information, but can have an identifier).

| Marker | Meaning |
|---|---|
| `?` | Optional (none or one) |
| `*` | Zero or more |
| `+` | One or more |
| `!` | Exactly one (default) |

**角色与职责装饰实例（MDSL §4.2，节选）**：

```mdsl
endpoint type CustomerManagementContract 
  version "1.0.0" 
  serves as INFORMATION_HOLDER_RESOURCE
  exposes 
  	operation lookupSingleCustomer version "1.0.1"
	  with responsibility RETRIEVAL_OPERATION in REQUEST_REPLY conversation
	  expecting 
		payload ID<string> 
	  delivering  
		payload {"customerId":ID<int>,
		          "name":D,
		          "address"} 
```

**模式引入变换（MDSL §7）**——步骤 4 各模式的可自动化引入点：

| MDSL 元素 | 变换 | 结果 |
|---|---|---|
| Operation with parameter tree request | Introduce Wish List | Set parameter added, `<<Wish_List>>` |
| Operation with parameter trees | Introduce page-based / offset-based / cursor-based pagination | Metadata parameters, `<<Pagination>>` |
| Operation with parameter trees | Bundle Requests | Parameter tree turned into set, `<<Request_Bundle>>` |
| Operation | Introduce Context Representation | Sample DTO, `<<Context_Representation>>` |
| Operation | Make Request Conditional | Metadata parameter, `<<Request_Condition>>` |
| Operation with `<<Embedded_Entity>>` | Extract Information Holder | Endpoint and DTO added; link parameter replaces entity |
| Operation with `<<Linked_Information_Holder>>` | Inline Information Holder | Type reference replaces link parameter |
| Endpoint and operations | Segregate commands from queries | CQRS pattern; retrieval operations moved |

</details>
