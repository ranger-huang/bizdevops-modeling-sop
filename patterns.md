# Patterns — 决策规则库

> 紧凑速查表；展开步骤 → 对应 SOP 章节。素材来源：CML §28/§30、SummerSoC 2020（DC/Table 2/Fig.6）、MDSL §3/§4、APIace EuroPLoP 2021、ICWE 2020 主题演讲。

## ① 架构重构（AR）目录（→ [SOP-05](chapters/sop-05-architectural-refactorings.md)）

| AR | 名称 | 触发信号 | 前置条件 | 逆操作 | 驱动准则 |
|----|------|---------|---------|--------|---------|
| AR-1 | Split Aggregate by Entities | 聚合含多实体需独立演化 | 聚合含 ≥2 实体 | AR-6 | Identity & Lifecycle Commonality（DC-1） |
| AR-2 | Split BC by Features | 聚合服务于不同特性 | BC 含 ≥2 聚合且被不同特性使用 | AR-7 | Semantic Proximity（DC-2） |
| AR-3 | Split BC by Owner | 一个 BC 多团队维护 | BC 含 ≥2 聚合且属不同团队 | AR-7 | Shared Owner（DC-3；Conway 定律） |
| AR-4 | Extract Aggregates by Volatility | 实现期变更频率分化 | BC 含 ≥2 个变更可能性不同的聚合（RARELY/NORMAL/OFTEN） | AR-7 | Structural Volatility（DC-4；Parnas） |
| AR-5 | Extract Aggregates by Cohesion | 按内聚/NFR 手动微调 | BC 含 ≥2 聚合 | AR-7 | 任选耦合准则或 NFR |
| AR-6 | Merge Aggregates | 聚合层拆过头 | 两聚合含同名领域对象时不可用 | AR-1 | —（回退） |
| AR-7 | Merge BCs | 拆过头、跨上下文事务频繁 | — | AR-4、AR-5 | —（回退） |
| AR-8 | Extract Shared Kernel | SK 被两 BC 共享失控 | ≥2 个 BC 处于 SK 关系 | — | 产出：新 BC + 2 条 U/D 关系 |
| AR-9 | Suspend Partnership | 伙伴关系难以为继 | 存在 Partnership | — | 三策略：a) 合并（AR-7）b) 提取共性为新 BC c) 转 U/D |
| AR-10 | SK → Partnership | 协作趋紧、需对等共担 | 存在 SK 关系 | AR-11 | —（关系类） |
| AR-11 | Partnership → SK | 两团队已同节奏共模 | 存在 Partnership | AR-10 | —（关系类） |

规则：AR 结果必须仍是语义一致的模型（引用/依赖随之调整）。分步流程：AR-2 → AR-3 → AR-4 → AR-5 ⇄ AR-7（聚合层 AR-1 ⇄ AR-6）；非严格时序、可多轮迭代。

## ② 耦合准则目录（→ [SOP-06](chapters/sop-06-systematic-decomposition.md)）

**DC-1~5 分解准则**：DC-1 业务实体（语言/领域专家边界）· DC-2 用例 · DC-3 代码属主/团队（Conway）· DC-4 变更可能性（Parnas：隔离易变者）· DC-5 泛化 NFR（可变性/存储相似性/可用性/安全）。

**14 项扩展准则**（参考默认优先级；XS 最低 → XL 最高，须按项目上下文重排）：

| 准则 | 默认 | 准则 | 默认 |
|------|------|------|------|
| Identity & Lifecycle Commonality | M | Latency | M |
| Semantic Proximity | M | Consistency Constraint | M |
| Shared Owner | M | Consistency Criticality | XS |
| Structural Volatility | XS | Availability Criticality | XS |
| Content Volatility | XS | Security Constraint | M |
| Predefined Service Constraint | M | Security Criticality | XS |
| Storage Similarity | XS | Security Contextuality | M |

前提：实体必须有**属性**（否则无法派生 nanoentity）、用例/故事读写关系明确。每个切分决策须指认 ≥1 条准则；准则冲突时显式排优先级。

## ③ MAP 速查（→ [SOP-10](chapters/sop-10-map-decoration.md)）

**元素刻板印象（IRT 角色）**：`D` Data · `ID` Identifier · `L` Link · `MD` Metadata；`P` 占位符（未细定，支持部分规格/敏捷建模）。

**端点角色**：Information Holder Resource，特化五种 — Master Data Holder（主数据：多枚举、少而大的创建/更新）· Operational Data Holder（运营数据：可枚举+可追加，常可变）· Reference Data Holder（参考数据：只读）· Data Transfer Resource（解耦多客户端的可变集合）· Link Lookup Resource（链接查找）；以及 Processing Resource（执行计算/流程）。

**操作职责**：Retrieval（只读）· State Creation（新建）· State Transition（变更：全量/部分/删除）· Computation Function（计算不改状态）。

**结构模式选择**（力场：性能/可扩展性 ↔ 灵活性/可修改性 ↔ 数据质量/新鲜度/一致性）：

| 当… | 选 | 可逆变换 |
|-----|----|---------|
| 客户端需关联数据、多次往返代价高 | Embedded Entity（嵌入实体数据） | Extract Information Holder（转链接） |
| 消息过大、数据非总全需 | Linked Information Holder（链接另端点） | Inline Information Holder（转内嵌） |
| 结果集大需分批 | Pagination（变体 page/offset/cursor-based；数据变化频繁时游标稳于偏移） | — |

## ④ API 结构原语判定 + 五坏味道（→ [SOP-11](chapters/sop-11-api-structure-analysis.md)）

**原语判定（看容器资源上的方法组合）**：

| 容器方法 | 客户端能力 | 原语 |
|---------|-----------|------|
| GET | 仅枚举发现内容 | P1 Enumerable Collection |
| POST | 仅追加（须返回新条目地址） | P2 Appendable Collection |
| GET + POST | 枚举 + 追加 | P3 Collection（最常见） |
| GET + POST +（PUT 或 DELETE） | 再 + 整集合批量替换/清空 | P4 Mutable Collection |

**五坏味道 → 修正方向**（括号为实测条目方法组合示例，`.s` 后缀）：

| 坏味道 | 判定信号 | 修正方向 |
|--------|---------|---------|
| Create without Delete | 能创建、无删除途径（P3.s1 PUT-Only、P3.s2 GET/PUT） | 补 DELETE；因留存法规故意不删则显式记录理由 |
| Delete without Create | 条目可读可删、不可追加（P1.s2 GET/DEL） | 补追加操作，或明确为服务端生命周期资源（如任务） |
| Ambiguous POST | POST 挂在集合**条目**上，追加还是动作不明（P1.s1 GET/POST） | POST 移回容器（=追加）或显式声明动作语义 |
| Ambiguous PUT | 容器 PUT 实为更新单条目（P4.s1、P4.s2） | PUT 移到条目资源；确为整集合批量替换才保留在容器 |
| Write-Only | 集合与条目均无任何读操作（P2.s1 PUT/DEL、P2.s2 DEL） | 补读操作；有意只写（异步作业/订阅）必须向创建者返回条目地址 |

**组合算子**：side-by-side（无关集合同层并列）· nesting（子集合嵌套于条目内）；同一 API 可混用。

**原语 ↔ Information Holder 特化**：Reference Data Holder → P1；Master Data Holder → 可枚举+可追加（P1/P2 能力，常成 P3）；Operational Data Holder → P3（常 P4）；Data Transfer Resource → P4；一组 Link Lookup Resource → 集合且条目可变。

## ⑤ DDD → 服务契约映射（SummerSoC Table 2；→ [SOP-07](chapters/sop-07-domain-driven-service-design.md)）

| DDD 概念（CML） | 契约概念（MDSL） | 说明 |
|---------|---------|------|
| Upstream Bounded Context | `API description` + `endpoint type` | 一 BC 一服务一契约 |
| Exposed Aggregate | `endpoint`（resource） | 每个聚合一个独立端点 |
| Aggregate Root Entity / Service method | `operation` | 由根实体或服务的方法派生 |
| Method Parameter & Return Type | `data type` / `data element` | 被 `expecting` / `returning` 消息引用 |
| Upstream BC / Downstream BC | `API provider` / `API client` | 契约的暴露者与使用者 |

## ⑥ HTTP 动词 → MAP 操作职责映射（→ SOP-10/11）

| HTTP | MAP 操作职责 |
|------|-------------|
| GET | Retrieval Operation |
| POST | State Creation Operation；亦可为 State Transition（部分更新变体） |
| PUT | State Transition（全量替换变体） |
| PATCH | State Transition（部分更新变体） |
| DELETE | State Transition 的变体 |
| Computation Function | 请求参数简单 → GET；复杂 → POST |

## ⑦ 神话破除表（ICWE 2020；配合 [cheatsheet 反模式速查](cheatsheet.md)）

| 流行说法（神话） | 事实（纠正） |
|----------------|-------------|
| 技术优先、一刀切：IT 是创新核心，用户以后教育；一套设计通吃 | 观察/倾听用户提取业务价值，建立统一语言；上下文至上，拒绝货物崇拜 |
| SOA 与微服务是竞争风格，"微"=极小 | 微服务是 SOA 的一种实现途径；服务大小随上下文而变 |
| 任何（微）服务必须暴露 HTTP 资源 API | 协议取决于上下文：事件溯源/流、消息队列（IDEAL 架构）皆是选项 |
| REST 统一接口足以表达丰富领域语义 | 动词过于贫瘠：需 DDD + 契约语言 + 显式操作职责（operationId/MAP 装饰） |
| 我们的扩展性需求独一无二，必须自造框架/协议（NIH） | 回到上下文与需求；每服务做自觉的 buy-rent-build 决策，建则用模式 |
| 两个披萨/代码行数/编辑器屏占比/if-then 经验法则可定分解 | 简单启发式不含领域语义与耦合证据；代之以分解准则 + 系统化方法（SOP-06） |

## ⑧ 质量治理决策规则（→ [SOP-14](chapters/sop-14-quality-governance.md)）

**子句选择（MAP Quality Management & Governance 组：Pricing Plan / Rate Limit / SLA）**：

| 关注点 | 子句 | 基数/必填 |
|--------|------|-----------|
| Quality Objective（SLO，性能/可用性…） | `objective` + Landing Zone `minimal`/`target`/`optimal` | ≥1 条（语法 `slos+=SLO+`）；minimal+target 必填 |
| SLA Type（类型显式化） | `type`：NONE/IMPLICIT/INFORMAL/QUALITATIVE/QUANTITATIVE | 可选（实证：未被校验） |
| Violation Handling（违约处置） | `penalty` / `notification`（STRING 自由文本） | 可选 |
| Pricing Plan（计费模式） | `rate plan`：FREEMIUM / SUBSCRIPTION / USAGE_BASED | ≤1 条（语法 `rp=RatePlan?`） |
| Rate Limit（用量配额） | `rate limit`：MAX_CALLS / DATA_QUOTA / NONE + `within` 窗口 | 0..n 条（语法 `rl+=RateLimit*`）；within 必填（含 NONE） |
| SLA Reuse（跨端点复用） | `SLA template` 具名 + `with endpoint SLA <name>` / `with provider SLA <name>` 引用 | 顶层 0..n |

**模式间关系**：Pricing Plan 可用 Rate Limit 强制计费档位（一档一 endpoint 实例挂不同 SLA template）；Rate Limit 与 Pricing Plan 细节应写入 SLA。计量执行点：网关旁路计数（请求副本→计数存储）。

**表达力边界（契约内不可表达 → 一律带外）**：金额/货币/计费周期 · per-operation 计量 · 超限行为（429/错误体）· 按客户端身份差异化配额 · 并发数 · 配额重置锚点 · 剩余配额回传头。声明这些需求时同步登记带外载体（计费系统/网关配置/监控头），否则视为未声明。

## ⑨ 版本演进决策规则（→ [SOP-15](chapters/sop-15-versioning-evolution.md)）

**EvolutionStrategy 选择（对外承诺级别，高→低）**：

| 策略 | 承诺 | 选用时机 |
|------|------|---------|
| ETERNAL_LIFETIME | 永不破坏或停用已发布版本 | 公共基础设施/法定接口 |
| LIMITED_GUARANTEED_LIFETIME | 固定期内不破坏；版本标注到期日 | 有明确支持窗口的商业 API |
| TWO_IN_PRODUCTION | 同时支持两版本、滚动重叠退役 | 消费方迁移周期长的平台 API |
| AGGRESSIVE_OBSOLESCENCE | 公告退役日期；过期即删 | 内部/快速迭代 API |
| EXPERIMENTAL_PREVIEW | best-effort、零承诺 | 试用/预览通道 |
| OTHER / UNDISCLOSED | 自定义 / 未声明（语法默认值） | UNDISCLOSED 是陷阱：必须显式改写 |

**版本挂载层级**：provider / endpoint 实例 / 操作 / 数据元素（Version_Identifier 构造型：版本标记同时进 API 描述与交换消息）；版本号 = 语义化版本 x.y.z 字符串，**破坏性变更 = major 提升**，且须附消费方迁移计划。

**弃用治理带外**：契约语言无 deprecated/sunset 语法 → 弃用清单 + 通知期 + 调用方监控 + 移除检查表四件套缺一不可；演进策略在 provider 与 endpoint 层级不一致时须书面说明理由。
