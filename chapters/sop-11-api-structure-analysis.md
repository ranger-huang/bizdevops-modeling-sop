# SOP-11: 存量 API 结构分析与坏味道识别（API Structure Analysis & Design Smell Detection）

> **定位**: 对存量 HTTP API 的结构化分析管线：资源树 → 碎片化 → 双重聚类 → 原语识别 → 坏味道标记与修正 | **组**: D（存量分析） | **主要来源**: APIace EuroPLoP 2021 论文（Serbout, Pautasso, Zdun, Zimmermann："From OpenAPI Fragments to API Pattern Primitives and Design Smells"）

## 何时启用

当接手、评审或治理存量 HTTP API，或棕地迁移前需要做现状盘点时，使用本 SOP。方法在 6,619 份真实 OpenAPI 描述上验证（提取 277,094 个带标签碎片、归并出 79,728 种树结构），既适用于单个 API 的评审，也适用于大规模 API 组合的量化治理。它回答两类问题：**这个集合资源在结构上"是什么"（四原语归类）**，以及**它"哪里可疑"（五坏味道标记）**。

## 触发条件

- 存在 OpenAPI 类描述文档，或可盘点出"路径 × HTTP 方法"路由清单
- API 行为语义不明："这个 POST 到底是创建、更新，还是触发动作？"
- 消费方抱怨接口风格不一致、语义歧义、无法预期行为
- 棕地治理路线启动（11 → 06 → 05 → 12）
- API 治理专项需要可量化、可复查的结构健康度指标

## 完整步骤

### 步骤 1：构建资源树（API Tree）

- 把 API 描述转为树模型：**路径段为节点，HTTP 方法挂在对应节点上**
- 制作无标签版本（API Tree Structure，抹去节点标签）以提升抽象层级——结构分析在无标签层进行
- **参数化路径段（如 {id}）与静态段是不同节点类型**：拓扑相同但段类型不同的碎片视为不同结构
- 集合类 API 的基本骨架：

```
R                            Container Resource（容器资源，静态命名）
   ... 挂载的 HTTP 方法
{collection item address}    Collection Item Resource（集合项资源，参数化寻址）
   ... 挂载的 HTTP 方法
```

### 步骤 2：碎片化（Fragmentation）

- **API 碎片（API Fragment）= 资源树的任意子树**（包含原树部分叶子的连通子图）
- 以容器资源为根切出子树：容器资源 + 集合项资源 + 各自的方法组合
- 每个带标签碎片投影为两部分：**树结构**（拓扑 + 方法挂载 + 路径段类型）与**标签序列**（节点标签的有序序列，如 `projects, {projectId}, tasks, {taskId}`）

### 步骤 3：结构 + 语义双重聚类

- **第一重（结构匹配）**：按树结构聚类——相同结构的碎片归为一类，出现频次即"这种结构有多常见"
- **第二重（语义聚类）**：在同结构簇内对标签序列做语义比较——提取单词与 n-gram → 计算标签序列间距离 → 聚合层次聚类（Agglomerative Hierarchical Clustering）+ 相似度阈值分簇
- 高频结构簇即**已知用途（Known Uses）**——结构模式原语的候选；语义簇回答"该结构惯用于什么业务上下文"（例如 user 类标签惯用什么方法组合）
- 单 API 评审时可退化执行：人工按方法组合归类 + 对照下文判定表，不必真跑聚类

### 步骤 4：原语识别（P1–P4 判定表）

四原语共享同一上下文：设计者需通过 HTTP API 提供对服务器端存储的**条目集合**的访问；集合由静态命名的**容器资源**标识，条目在容器资源内**动态寻址**。**原语由容器资源上的方法组合区分；变体（variant）由集合项上的方法组合区分。**

| 原语 | 容器资源方法 | 语义 | 集合项方法变体 |
|------|--------------|------|----------------|
| **P1 Enumerable Collection**（可枚举集合） | GET | 只读枚举：条目可发现、可寻址、可读取 | v1 GET ／ v2 GET+PUT ／ v3 PUT+DEL ／ v4 GET+PUT+DEL |
| **P2 Appendable Collection**（可追加集合） | POST | 只追加：**必须向客户端返回新建条目的地址**（因为无法枚举） | v1 GET+PUT+DEL ／ v2 GET+DEL ／ v3 GET |
| **P3 Collection**（集合，最常见，故名最短） | GET + POST | 枚举 + 追加（又名 Enumerable-Appendable Collection） | v1 GET+PUT+DEL+PATCH ／ v2 GET+PUT+DEL ／ v3 GET+DEL+PATCH ／ v4 GET ／ v5 PUT+DEL ／ v6 GET+DEL ／ v7 DEL |
| **P4 Mutable Collection**（可变集合） | 在 P3 基础上 + PUT 或 DELETE | 整集合批量操作：替换全部内容（PUT）或清空（DELETE） | v1 GET+PUT+DEL+PATCH |

判定要点：
- P2 的硬性约束：POST 必须返回新条目地址，否则客户端将永远"丢失"自己创建的条目
- P4 的容器 PUT **实践中很少真的用于整集合替换**——多数是借查询参数定位单条更新（这正是 Ambiguous PUT 坏味道的来源）
- 容器 DELETE 用于"delete all"（清空集合）；该形态足够常见，论文提出可升格为独立原语 "Erasable Collection"
- P3 项级只有 GET/PUT 等"无 DELETE"变体不算读缺失：客户端仍可 GET 容器枚举全量后提取单条——但触发 Create without Delete 检查（见步骤 5）

### 步骤 5：五坏味道标记（每条含位置 + 证据）

| 坏味道 | 定义 | 论文中的典型结构 |
|--------|------|------------------|
| **Create without Delete** | 允许客户端创建集合条目，却不提供删除能力 | P3.s1（项级仅 PUT）、P3.s2（项级 GET+PUT） |
| **Delete without Create** | 允许删除条目，却不提供追加能力 | P1.s2（容器 GET，项级 GET+DEL） |
| **Ambiguous POST** | 集合**项**上出现 POST：是追加条目？更新属性？还是触发任意操作？ | P1.s1（项级 GET+POST） |
| **Ambiguous PUT** | 集合（容器资源）上提供 PUT：真的用于整集合替换吗？ | P4.s1、P4.s2（PUT 实际经查询参数更新单条） |
| **Write-Only** | 集合与条目均无任何读操作 | P2.s1（项级 PUT+DEL）、P2.s2（项级仅 DEL） |

**语境判断（Context matters——坏味道是待查信号，不是自动判罪）**：
- Delete without Create 出现在 tasks、jobs、instances 类标签时往往正当：服务器端资源，客户端只能监控与移除，不控制其生命周期
- Write-Only 集合存在有限正当用途：异步作业、订阅、只能提交与取消的消息；前提是 POST 返回新条目地址。因限制过强仍标记为坏味道，但修正建议应是"记录决策"而非"强加 GET"
- Ambiguous POST 的两种真实意图需取证区分：追加条目（POST 放错了位置，应在容器上）或更新属性（误用 POST 顶替 PUT）——提取操作的 summary/description 文本作证据
- Ambiguous PUT 同理：提取 PUT 描述文本，确认是整集合批量替换还是借参数更新单条

### 步骤 6：修正建议 + 组合视角评审

- **已知用途指南**：按容器资源标签聚类查表——常见标签是否有到某原语变体的**无歧义映射**（如 user 类集合多映射为可变集合形态），作为修正目标参考；标签只是统计线索，最终归类必须经方法组合判定表确认
- **修正建议接入 [SOP-10](sop-10-map-decoration.md)**：每个坏味道翻译为一个模式决策——

| 坏味道 | 修正方向（SOP-10 模式语言） |
|--------|------------------------------|
| Create without Delete | 补删除能力（State Transition 的删除变体）；或确认生命周期为服务器端控制并记录决策 |
| Delete without Create | 核对是否正当监控用途；否则在容器上补 State Creation Operation |
| Ambiguous POST | 明确操作职责三选一：State Creation（移到容器 POST）、State Transition（改 PUT/PATCH）、Computation Function（保留项级 POST 并记录理由） |
| Ambiguous PUT | 单条更新移到条目资源（PUT/PATCH）；确为整集合替换则保留并显式声明 |
| Write-Only | 补 Retrieval Operation；或声明有限用途（作业/订阅类）并确认 POST 返回地址 |

- **组合视角**：原语可组合成更大结构——**并列**（side-by-side：无关集合的容器资源放同层）与**嵌套**（nesting：集合条目内挂子容器资源，如 projects/{id}/tasks）；两种可共存于同一 API。评审组合关系是否符合领域结构（嵌套应对应领域中的包含关系）
- **端点角色交叉核对**：Master / Operational / Reference Data Holder、Data Transfer Resource、Link Lookup Resource 各有典型原语形态（对应表见 [SOP-10](sop-10-map-decoration.md) 步骤 2）；实际形态与 API 自称角色不符时记录为发现

## 使用示例

任务管理 API 盘点（结构化分析记录；坏味道与原语用 MAP 发表名，职责用 MDSL `OperationResponsibility` 枚举值）：

```yaml
api: "TaskTracker API v2"          # OpenAPI 类描述，14 条路径

# 步骤 1–2：资源树 + 碎片（Fragment）
fragments:
  - id: F1
    path: "/projects/{projectId}/tasks/{taskId}"
    container: { path: "/projects/{projectId}/tasks", methods: [GET, POST] }
    item:      { path: "/projects/{projectId}/tasks/{taskId}", methods: [GET, PUT] }   # 原为省略号，已补全
  - id: F2
    path: "/webhooks/{webhookId}"
    container: { path: "/webhooks", methods: [POST] }
    item:      { path: "/webhooks/{webhookId}", methods: [DELETE] }

# 步骤 3–4：原语归类（按容器方法组合判定）
classification:
  - { fragment: F1, primitive: "P3 Collection",            variant: P3.s2 }   # 容器 GET+POST；项级 GET+PUT
  - { fragment: F2, primitive: "P2 Appendable Collection", variant: P2.s2 }   # 容器仅 POST；项级仅 DELETE

# 步骤 5：坏味道清单（位置 + 证据 + 语境判断）
smells:
  - id: SM-1
    smell: "Create without Delete"
    location: { fragment: F1, path: "/projects/{projectId}/tasks" }
    evidence: "容器 POST 可创建任务；全子树无任何 DELETE"
    context: "任务生命周期由客户端控制 → 非正当豁免，需修正"
  - id: SM-2
    smell: "Write-Only"
    location: { fragment: F2, path: "/webhooks" }
    evidence: "容器与条目均无 GET；POST 返回新条目地址 ✓"
    context: "订阅类有限用途候选 → 与消费方确认后二选一（补 GET / 记录决策）"

# 步骤 6：修正建议（转 SOP-10 模式决策）+ 组合评审
fixes:
  - smell: SM-1
    action: "新增 DELETE /projects/{projectId}/tasks/{taskId}"
    operation_responsibility: STATE_DELETION_OPERATION    # MDSL 有专门的删除职责枚举值
  - smell: SM-2
    action: "建议补 GET /webhooks/{webhookId}"
    operation_responsibility: RETRIEVAL_OPERATION
    alternative: "若保留 Write-Only，须记录决策与'POST 返回新条目地址'约束"
composition:
  - { operator: nesting, verdict: PASS }     # ✓ tasks 嵌于 projects 项下，符合领域包含关系
roleCheck:
  - fragment: F2
    claimed_role: "Reference Data Holder"    # 自称"配置数据端点"
    observed_primitive: "P2 Appendable Collection"
    verdict: MISMATCH                        # Reference Data Holder 预期只读可枚举（→ P1），记录待处理
```

## 技术交付物

1. 资源树清单（全部路径 × 方法，含参数化/静态段类型标注）
2. 碎片清单（容器 + 项 + 方法组合 + 标签序列）
3. 原语分类表（每碎片 → P1–P4 + 变体，或显式"非集合原语"标注）
4. 坏味道清单（位置 + 证据 + 语境判断）
5. 修正建议表（每条映射为 SOP-10 可执行的模式决策）
6. 组合结构评估（并列/嵌套 vs. 领域结构）与端点角色交叉核对记录

## 成功标准

- 每个集合资源有原语归类（或显式"非集合原语"标注），归类依据是可复查的方法组合
- 每个坏味道有位置、证据、语境判断、修正路径四要素
- 修正建议可直接转为 [SOP-10](sop-10-map-decoration.md) 的模式决策（而非"建议优化"类空话）
- 评审后消费方语义歧义消除：能明确回答"这个 POST/PUT 到底做什么"
- 盘点覆盖描述文档中的全部路径与方法，无遗漏

## 反模式

| 反模式 | 为何失败 |
|--------|----------|
| 只看单端点不看树 | 坏味道是结构性的（方法组合的缺失/错位）；单端点评审看不见 Create without Delete |
| 把所有 POST 当创建 | POST 可能是 State Creation、State Transition（部分更新变体）或 Computation Function；不区分则 Ambiguous POST 漏检 |
| 照抄已知用途映射 | 标签聚类只是统计线索；不经方法组合判定表确认会误判（同标签不同结构大量存在） |
| 标坏味道不做语境判断 | tasks/jobs 类 Delete without Create、订阅类 Write-Only 可能是正当设计；坏味道是信号不是判决 |
| 只列问题不给修正路径 | 盘点报告沦为抱怨清单；价值在"每个味道 → 一个可执行模式决策" |
| 一次性盘点 | API 持续演进；结构健康度应纳入治理循环定期复查（衔接 SOP-12） |

## 关联

- **棕地治理路线**: **11（盘点）→ [SOP-06](sop-06-systematic-decomposition.md)（再分解）→ [SOP-05](sop-05-architectural-refactorings.md)（增量重构）→ [SOP-12](sop-12-model-code-validation.md)（守护）**
- 修正建议落地 → [SOP-10](sop-10-map-decoration.md) 步骤 4（力场权衡）与步骤 3（职责显式化）
- HTTP 动词 ↔ MAP 职责映射与 [SOP-10](sop-10-map-decoration.md) 步骤 3 同源（APIace §5.2）
- 结构问题指向服务边界问题时 → [SOP-06](sop-06-systematic-decomposition.md)（耦合准则 + 聚类再分解）
- 盘点后的契约重设计 → [SOP-08](sop-08-story-driven-service-design.md)（按故事重建理由链）

## 来源

- APIace：Serbout, Pautasso, Zdun, Zimmermann, "From OpenAPI Fragments to API Pattern Primitives and Design Smells", EuroPLoP 2021——§2（领域概念：API Tree / API Tree Structure / API Fragment / 投影为树结构+标签序列；碎片化方法；数据集规模）、§3（结构匹配 + 语义聚类管线、Known Uses 选取）、§4（P1–P4 原语定义、变体与坏味道逐一分析、Known Uses 指南表）、§5（并列/嵌套组合算子；与 MAP 的关系：HTTP↔职责映射、端点角色↔原语对应、MDSL 重建示例）
- 分析报告 §2 F8、§3 SOP-11 草案、§6 反模式（API 结构五坏味道）
- 术语与枚举核对（2026-10-10，`Microservice-API-Patterns/MDSL-Specification` @ master，`APIDescription.xtext`）：`OperationResponsibility` 含 `STATE_DELETION_OPERATION`——项级 DELETE 与容器"delete all"应对应此值，而非笼统写作 State Transition 的删除变体；另有 `RETRIEVAL_OPERATION` / `STATE_CREATION_OPERATION` / `STATE_TRANSITION_OPERATION` / `EVENT_PROCESSOR` / `COMPUTATION_FUNCTION`。`ResourceRole` 含 `REFERENCE_DATA_HOLDER` / `MASTER_DATA_HOLDER` / `OPERATIONAL_DATA_HOLDER` / `DATA_TRANSFER_RESOURCE` / `LINK_LOOKUP_RESOURCE`，即步骤 6「端点角色交叉核对」的取值域

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下片段忠实摘自语料原文（APIace 论文 §5.2 用 MDSL 重建被分析 API 的示例），供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考——展示"盘点结论如何落成抽象契约"。上方「使用示例」是**分析记录**（结构化 YAML，非 DSL）：坏味道与原语沿用 MAP 发表名，便于与 [patterns.md ④](../patterns.md) 逐条对账；操作职责则改用 MDSL `OperationResponsibility` 枚举值，便于直接落进契约。

**数据契约（原语归类后的表示元素定型）**：

```mdsl
API description ApactaAPI version "v1"
overview "See previous paper sections and APIs.guru"
data type CityCollection {
"data":City*,
"pagination":PaginationDetails,
"success":Metadata<bool>}
data type City {
"created":Metadata<string>,
"deleted":Metadata<string>,
"id":ID<string>,
"modified":Metadata<string>,
"name":Data<string>,
"zipCode":Data<int>}
data type PaginationDetails {
"count":Metadata<int>,
"current_page":ID<string>,
"has_next_page":Metadata<bool>,
"has_prev_page":Metadata<bool>,
"limit": Metadata<int>,
"page_count":Metadata<int>}
data type ErrorNotFound {
"data": {
"code":Data<int>,
"message":Data<string>,
"url":Link},
"success":Metadata<bool>}
```

**端点契约（端点角色 + 操作职责 + 错误报告装饰）**：

```mdsl
endpoint type CityEndpoint
serves as REFERENCE_DATA_HOLDER and COLLECTION_RESOURCE
exposes
operation getListOfCities
with responsibility RETRIEVAL_OPERATION
expecting payload "zipCode":Data<string>?
delivering payload CityCollection
reporting error searchFailed "404": ErrorNotFound
operation getCityDetails
with responsibility RETRIEVAL_OPERATION
expecting payload "cityId":ID<string>
delivering payload City
reporting error noSuchCity "404": ErrorNotFound
```

**HTTP 绑定（抽象契约 → 资源树的显式绑定）**：

```mdsl
API provider CityEndpointProvider
offers CityEndpoint
at endpoint location "http://tbc.tbc.tbc:8080"
via protocol HTTP binding
resource CityCollection at "/cities"
operation getListOfCities to GET
element "zipCode" realized as QUERY parameter
report searchFailed realized as 404 with "Not found"
resource CityDetails at "/cities/{cityId}"
operation getCityDetails to GET
element "cityId" realized as PATH parameter
report noSuchCity realized as 404 with "Not found"
```

论文注：此类抽象契约可译为 HTTP、gRPC、GraphQL Schema 等多种 IDL；到 HTTP 资源 API 的翻译并非直截了当，因此受益于显式绑定（建立含参数化路径段的资源树；映射超出 HTTP 统一动词接口承载力的操作）。

</details>
