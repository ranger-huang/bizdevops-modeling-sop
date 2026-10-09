# SOP-14: 质量管理与治理（SLA / Rate Limit / Pricing Plan）

> **定位**: 在 API 契约中显式声明服务质量（SLA/SLO）、用量配额（限流）与计费模式（计价方案），并绑定声明层级、测量载体、执行点与评审兜底，使质量承诺可验证、配额可执行、计费可追溯 | **组**: F（质量与演进治理） | **主要来源**: 《MDSL - Pricing Plan 与 Rate Limit（质量管理与治理）语法调研》、《MDSL - SLA 与版本演进（Versioning & Evolution）语法调研》§二

---

## 何时启用

当契约骨架与模式装饰已完成、API 要作为产品向外部或跨团队消费方提供时，使用本 SOP。MAP 质量模式组分两个子组：数据传输节约（分页、字段选择等，属 [SOP-10](sop-10-map-decoration.md) 范畴）与**质量管理与治理**——后者的三个模式互为咬合，须在契约设计中一体考虑：Service Level Agreement（承诺什么质量、违约怎么办）、Rate Limit（如何防止消费方过度使用）、Pricing Plan（如何计量消耗并据此收费）。官方模式页明确了三者关系：限流与计价的细节可包含在 SLA 中；限流可按订阅档位差异化（计价方案借限流强制档位）；计价方案应引用 SLA。本 SOP 回答五个问题：声明什么、挂在哪一级、用什么测量、谁来执行、如何评审——因为实证显示契约工具链对质量子句的支持远弱于结构子句（见步骤 6），方法论必须自带兜底。

## 触发条件

- API 开放给外部/跨团队消费方，需要明确的可用性、响应时间等质量承诺与违约后果、通报渠道
- 出现过度使用或滥用迹象，需要调用次数/数据量配额与超限处置策略
- 商业化或内部结算：需区分免费档/订阅档/按量档，且档位差异必须可强制执行
- 契约评审发现质量承诺只存在于文档、邮件或口头，契约中无机读子句
- 运维监控阈值与契约承诺脱节：告警响了但对不上 SLA，违约举证拿不出
- 网关层限流配置散落在各环境各团队，需要契约层单一事实源收口

## 完整步骤

### 步骤 1：识别质量关注点类型

按质量模式组把诉求归入三类关注点，登记时标注对应模式：

| 关注点 | 对应模式 | 核心问题 |
|--------|----------|----------|
| 服务质量承诺 | Service Level Agreement | 提供方承诺什么质量？违约罚则与通报渠道是什么？ |
| 用量配额 | Rate Limit（又名 Quota、Usage Limitation） | 如何防止消费方过度使用？时间窗口内请求数/数据量上限是多少？ |
| 计费模式 | Pricing Plan（又名 Metering and Billing、Accounting） | 如何计量服务消耗并据此收费？免费增值/订阅/按量计价三选 |

- 判定 SLA 形式化等级，共五级（从无承诺到全量化）：无、隐式、非正式、定性、定量。等级是给消费方的承诺强度标注——实证提醒：等级标注当前不被工具链校验或消费，等级差异要靠评审与沟通传达。
- 每个 SLA 必须至少含一条可量化的质量目标（SLO）。质量目标没有预置维度枚举（不存在现成的"可用性/性能/可扩展性"分类），目标名由建模者自由命名（响应时间上限、月度可用性、每秒并发请求数……）并配测量值载体。
- 三类关注点不分开写：限流细节是 SLA 的组成部分；计价方案与 SLO 声明在同一质量子句集内，天然满足"计价方案应引用 SLA"。

### 步骤 2：选择声明层级（挂载点）

质量关注点概念上有四级——提供方整体、端点实例、操作、数据元素——但声明位置受契约语言挂载点约束。MDSL 实证：质量子句只有三类合法位置——顶层具名模板声明位、提供方级、端点实例级；端点类层、操作级与文件顶层裸写全部被拒绝。

- **提供方级**：适用于该提供方全部端点。注意与"条款与条件"链接声明互斥——提供方级要么挂条款、要么挂质量子句，不能并存；常见规避是条款放提供方级、质量子句挂端点实例。
- **端点实例级**：挂在具体访问地址实例上。网关端点复用端点实例规则，同样能挂质量子句——网关是限流执行点，条款跟着网关端点走是最自然的声明位。
- **顶层具名模板**：一次声明、多处按名引用（见步骤 4）。
- **操作级与数据元素级不可声明**：按操作计量用量（per-operation usage statistics）在契约内不可表达，只能登记到带外计量配置，契约中留指向。
- 原则：声明层级越贴近执行点越好；质量是实例层概念——同一端点类型的不同承诺用不同实例区分。

### 步骤 3：选择测量值与单位载体

质量子句的测量载体 = 整数值 + 单位（时间、容量或自定义计数单位）。实证边界必须绕开设计：

- **测量值只能是整数**：小数一律非法。百分比承诺（99.9% 可用性）、百分位延迟（p99.9）、小数配额（0.5 GB）都无法直接表达——要么整数近似 + 自由文本说明（官方范例把可用性写成 100、将"尽力而为不作保证"的免责说明塞进单位位），要么降级为注释，要么转移到监控系统载体。
- **单位无语义校验**：预置单位（hours/minutes/seconds/MB/GB）之外任意自定义单位都合法，拼错也静默通过（单复数写错、大小写写错、拼写打错均编译通过）。团队应维护受控单位词表并在评审中比对——"能编译 ≠ 单位写对"。
- **分档目标**：单值太刚时用"最低可接受 / 目标 / 最优"三档测量表达梯度；前两档必填、最优档可选。
- **窗口语义完整**：一条限流 = 配额值 + 时间窗口，两者各自独立测量；"不限流"也必须显式声明并给出窗口——显式不限流与没写是两种治理状态，前者是决策、后者是缺失。

### 步骤 4：复用模板与统一档位

- **具名 SLA 模板**：把完整质量子句集（等级 + SLO + 罚则 + 通报 + 计价方案 + 限流）在顶层声明一次，多个端点按名引用挂载——同档位承诺文本一致，修订一处全局生效。
- 内联声明只用于一次性特例；内联泛滥是承诺漂移的前奏。
- **档位矩阵 = 模板矩阵**：免费档、标准档、计量档、伙伴档各建一个模板、配额递增；不同档位挂到不同端点实例（免费域名与付费域名分离）——这是"按订阅档位差异化限流"在不能绑定客户端身份的语言中的唯一表达方式。
- 一个模板内可并存多条限流：短窗口防突发 + 长窗口控总量（每小时千次与每天十 GB 的双窗口叠加，即业界常见的"每小时 + 每天"双限的契约形态）。
- 计价方案每个模板至多一条，且只是类型声明（免费增值/订阅/按量计价三选）——不携带金额、货币、计费周期；价格明细属契约外的商业配置（见反模式）。

### 步骤 5：治理绑定（谁执行、谁监控）

声明 ≠ 执行。每条质量子句在治理交付物中指认执行者与反馈回路：

- **执行点**：限流与计量统一落在 API 网关层执行（拦截、计数、扣减）；计量可用线束截取（wire tap）模式旁路实施——把请求副本导入消息存储计数，不侵入服务本体。
- **身份 → 档位映射**：契约子句不绑定消费方身份（API key 之类的识别机制在协议绑定层，与限流子句零结构关联）；"谁在哪档、适用哪套配额"的映射由网关订阅配置维护，并在治理交付物中登记。
- **超限行为**：超过窗口配额后拒绝全部后续请求、返回 429 类状态码、通报剩余配额与重置时刻——这些行为契约语言表达不了，须在执行层定义；剩余配额状态可用上下文表示（Context Representation）模式回传客户端，运行时动态调节配额可用控制总线（Control Bus）模式。
- **监控闭环**：SLO → 监控告警阈值 → 违约证据 → 罚则与通报渠道兑现，四者一一对应；实测数据（真实百分位、真实可用性）回流契约修订，与演进治理（[SOP-15](sop-15-versioning-evolution.md)）衔接。

### 步骤 6：验证与评审（检查表兜底）

实证前提决定评审策略：MDSL 工具链对质量子句零校验器（矛盾组合全部静默通过）、生成物零结构化痕迹（OpenAPI 与中间模型输出丢失全部质量/限流/计价内容）、格式化器不排版这些规则、语法自 2020 年起冻结且官方注释自认 PoC 定位。**质量子句若无校验器/生成器支持，必须靠评审检查表与运行时监控兜底**——这是本 SOP 最重要的方法论教训。四类检查（由 20 个实测反例提炼）：

1. **枚举值形状**：计价方案与限流类型只取合法枚举，大小写敏感、禁引号、禁造词（"按次付费"之类看起来合理的臆想档位并不存在）。
2. **金额与测量值**：计价子句未携带金额/货币；测量值为整数；百分比与小数有替代载体且标注了去向；单位在受控词表内。
3. **基数与顺序**：至少一条质量目标；计价方案至多一条；限流可多条；子句顺序（目标 → 罚则 → 通报 → 计价 → 限流）未颠倒；"不限流"也带窗口。
4. **挂载点**：子句只出现在合法挂载位（模板/提供方级/端点实例级）；类层、操作级、顶层裸写为违规；层级间计价方案冲突、"不限流 + 配额并存"矛盾已人工裁决并记录（语言不校验这些）。

追加两类治理检查：每条限流/计价声明指认了执行点与身份映射维护处；生成物会丢质量子句 → 契约不是质量信息的唯一载体，监控配置与网关配置存在同步通道并登记在册。

## 使用示例

SaaS 计费 API 的质量治理决策记录（语料综合示例的中立化改写，伪码风格）：

```yaml
api: SaaSMonetizationAPI             # 公开 API，供前端集成，v1.0.0
SLA模板:                             # 步骤 4：一个档位一个具名模板
  - 名称: 免费档
    等级: 定量                       # 步骤 1：五级形式化标注
    SLO:
      - { 目标: 响应时间, 测量: 上限 2 秒 }
      - { 目标: 可用性, 测量: 99, 单位位备注: "百分比，尽力而为" }  # 步骤 3：整数近似 + 文本免责
    罚则: 无（免费档）
    通报: 仅状态页
    计价方案: 免费增值
    限流:
      - { 种类: 调用次数配额, 配额: 60 次, 窗口: 1 小时 }   # 对齐知名开放 API 的未认证档
      - { 种类: 数据量配额, 配额: 10 MB, 窗口: 24 小时 }
  - 名称: 标准档
    等级: 定量
    SLO: [ { 目标: 响应时间, 测量: 上限 1 秒 }, { 目标: 可用性, 测量: 99 } ]
    罚则: 服务补偿（credits）
    通报: 支持工单
    计价方案: 订阅
    限流: [ { 种类: 调用次数配额, 配额: 5000 次, 窗口: 1 小时 },
            { 种类: 数据量配额, 配额: 1 GB, 窗口: 24 小时 } ]
  - 名称: 计量档
    SLO: [ { 目标: 吞吐, 测量: 每秒并发请求数 10 } ]  # 并发只能作 SLO 目标表达，无强制语义
    计价方案: 按量计价
    限流: [ { 种类: 调用次数配额, 配额: 1000000 次, 窗口: 30 天 } ]  # 月度计量上限档
  - 名称: 伙伴档
    SLO:
      - 目标: 延迟
        分档测量: { 最低: 5 秒, 目标: 2 秒, 最优: 1 秒 }    # 步骤 3：三档目标
    计价方案: 订阅
    限流: [ { 种类: 不限流, 窗口: 1 小时 } ]         # 显式不限流 ≠ 未声明
挂载:                                # 步骤 2：挂载点决策
  - 端点: 生产付费域名 /v1 → 标准档模板；演进策略: 双实例生产运行
  - 端点: 免费档域名 /v1 → 免费档模板；演进策略: 激进废弃
  - 提供方整体（生产）: 内联子句（月度可用性目标 + 订阅 + 每 24 小时 100000 次总闸）
  - 端点: 沙箱域名 /v1 → 计量档模板；提供方级改挂条款链接  # 条款与提供方级 SLA 互斥
  - 端点: 网关域名 /v1 → 伙伴档模板               # 网关端点同样可挂质量子句
治理:                                # 步骤 5/6：执行点映射
  执行: 网关层统一计数与拦截；超限返回 429 类状态码 + 剩余配额通报头（执行层定义，契约不表达）
  身份档位映射: 网关订阅配置维护（契约子句不绑定客户端身份）
  监控闭环: 每条 SLO 对应一个告警阈值；违约证据触发罚则/通报兑现
  已知损耗: 下游生成物丢失全部质量子句 → 监控/网关配置带外同步并登记（检查表兜底）
```

## 技术交付物

1. 质量需求登记册：按提供方/端点——SLA 等级、每条 SLO（目标名 + 测量值 + 单位或分档目标）、罚则、通报渠道、声明层级
2. 限流与计价声明清单：按档位/模板——计价方案类型、每条限流（种类［不限流/调用次数/数据量］+ 配额值 + 窗口 + 单位）、短长窗口叠加关系
3. 治理执行点映射表：子句 → 执行位置（网关/监控）→ 身份-档位映射维护处 → 超限行为定义处 → 告警阈值对应
4. 评审检查表执行记录：步骤 6 四类检查 + 两类治理检查的结论与豁免记录
5. 档位-端点矩阵：订阅档位 ↔ 端点实例 ↔ 模板引用关系（"一档一端点"的结构说明）

## 成功标准

- 每个对外 endpoint 均有质量子句挂载或显式豁免记录；"不限流"以显式声明而非缺失的形式出现
- 每条限流子句测量载体完整：整数配额 + 明确时间窗口 + 单位在受控词表内
- 计价方案与用量测量一一对应：按量计价必有可计量的配额子句；金额/货币/计费周期有明确的带外载体且在契约登记指向
- 每条 SLO 能指认对应的监控告警阈值与违约证据来源（闭环成立）
- 四类评审检查通过或例外有裁决记录；每条限流/计价声明有指名的执行点
- 档位差异化结构可落地：不同档位 = 不同端点实例 + 不同模板，网关据此可分发配额
- 质量信息不依赖单一载体：生成物丢子句的前提下，监控与网关配置的同步通道已建立并登记

## 反模式

| 反模式 | 为何失败 |
|--------|----------|
| 只写声明不管工具链支持 | 实证：质量子句零校验、零生成——不进交付物、不进 CI 门禁，静默失效；评审检查表 + 运行时监控不兜底就等于没写 |
| 用浮点表达百分比/小数 | 测量载体只收整数：99.9%、p99.9、0.5 GB 均非法；硬写导致解析失败或语义失真，应改整数近似 + 文本备注、分档目标或监控载体 |
| 把金额塞进计价子句 | 计价方案只是类型声明；金额/货币/计费周期无结构位，硬塞即报错；价格表在专门商业配置中建模，契约留引用指向 |
| rate 子句挂错层级 | 提供方/端点块内裸写、挂端点类层、挂文件顶层——全部被实测拒绝；质量子句是实例层概念，模板与两个挂载点是唯一合法容器 |
| 只声明不限流执行点 | 契约既不绑定客户端身份也不表达超限行为；网关不计数不拦截，配额就是纸面数字 |
| 单位拼错与臆造枚举值 | 单位无语义校验，单复数/大小写/拼写错误静默通过；枚举值大小写敏感且禁引号，臆造词一律失败——"能编译 ≠ 写对" |
| 矛盾组合不裁决 | "不限流"与配额并存、端点级与提供方级计价方案冲突——语言全收；评审必须人工裁决并记录理由 |
| 纯限流无质量目标 | 结构上限流/计价子句必须依附至少一条 SLO；语义上限流本就是 SLA 的组成部分——"只限制不承诺"不成立 |
| 照抄旧语法化石 | 历史示例注释块里的提供方级 SLA 引用旧写法已废弃，照抄必错；以现行语法为准 |
| 等语言演进补齐商业语义 | 限流/计价语法自 2020 年发布以来一字未改，官方自认 PoC、"可建模得更好"；重要商业语义应当下带外建模，不要等 |

## 关联

- **编排位置**: [SKILL.md](../SKILL.md) API 产品路线 [SOP-08](sop-08-story-driven-service-design.md) → [SOP-10](sop-10-map-decoration.md) → **14** → [SOP-12](sop-12-model-code-validation.md)；绿地与事件密集路线同样在契约精化后经本 SOP 进入守护
- 步骤 2 挂载点与档位-端点矩阵承接 [SOP-10](sop-10-map-decoration.md) 的端点角色与实例层装饰——质量子句是模式装饰之上的"承诺维度"装饰
- 步骤 6 检查表与 [SOP-12](sop-12-model-code-validation.md) 衔接：契约质量子句 ↔ 网关/监控运行时配置的一致性核验，是模型-代码守护在治理面的延伸
- 服务粒度与提供方边界来自 [SOP-07](sop-07-domain-driven-service-design.md)：质量承诺与计价档位按服务/产品边界声明，跨边界共享 SLA 先做拆分
- 同组姊妹篇 [SOP-15](sop-15-versioning-evolution.md)（版本演进）：演进策略与质量子句在同一挂载点共同声明，违约与弃用谈判并行
- 速查表 [patterns.md](../patterns.md) ⑧ 质量治理决策规则：子句选择表与表达力边界带外清单

## 来源

- 主源：《MDSL - Pricing Plan 与 Rate Limit（质量管理与治理）语法调研》——§一 MAP 模式内容总结（质量模式组索引、Pricing Plan / Rate Limit 模式要素、模式↔语法覆盖缺口表）、§二 语法规范、§三 官方示例与作者实测范例、§四 综合示例、§五 穷举证伪（20 反例与精确报错）、§六–§八 工具链支持状态 / 文档核查 / 已知限制与坑
- 辅源：《MDSL - SLA 与版本演进（Versioning & Evolution）语法调研》§二——SLA 语法规则（逐字摘录）、SLA 关键字清单、挂载点、五个示例与 SLA 模板机制
- MAP 官方模式页（2026-10-10 实测抓取）：
  - 质量模式组索引 — <https://microservice-api-patterns.org/patterns/quality/>
  - Pricing Plan — <https://microservice-api-patterns.org/patterns/quality/qualityManagementAndGovernance/PricingPlan.html>（Forces 四项与 Table 1 分级价目取自原始 HTML）
  - Rate Limit — <https://microservice-api-patterns.org/patterns/quality/qualityManagementAndGovernance/RateLimit.html>（Forces 五项、GitHub 429/X-RateLimit-* 示例、Figure 1 题注取自原始 HTML）
  - Service Level Agreement（Related Patterns 交叉链接）— <https://microservice-api-patterns.org/patterns/quality/qualityManagementAndGovernance/ServiceLevelAgreement.html>
- 一手源码：仓库 `Microservice-API-Patterns/MDSL-Specification`，分支 master，实测 HEAD `9da0bac0e6133b8a69131925e38bc98e63e20af2`（2025-01-23，与前序调研行号零漂移）；历史版本对照 tag `v3.1`（2020-05，rate 语法自此冻结）；语法文件行锚点 L40 / L438–457 / L556 / L596–651 / L741–753；OpenAPI 转换器 L185（网关生成崩溃根因）；格式化器 TODO L55；changelog L230（External SLAs now supported）、L3–9（V6.0.0 "No new features"）——逐条 URL 详见主源 §九
- 官方示例与文档（限流/计价子句全仓出现处全量）：`examples/MDSLGitPages/ProviderSLAClientExample.mdsl`（L10–26）、`examples/examples-advanced/CustomerRelationshipManagementExample.mdsl`（L102–145，含废弃语法化石注释）、`examples/examples-advanced/MAPDecoratorUsageReference.mdsl`（L171–188）、`docs/optionalparts.md`（L52–76，全部官方文档中唯一记载处）

---
<details>
<summary>📎 原始 MDSL 语法参考（质量与限流子句）— 点击展开</summary>

以下片段忠实摘自语料原文，供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考。

2.1 RatePlan 规则（L615–618）

```xtext
// APIDescription.xtext:615-618
// TODO rename to 'Pricing Plan' (MAP)
RatePlan:
	'rate' 'plan' ('FREEMIUM' | "SUBSCRIPTION" | "USAGE_BASED") // note: actual pricing not modeled yet
;
```

2.2 RateLimit 规则（L620–622）

```xtext
// APIDescription.xtext:620-622
RateLimit:
	'rate' 'limit' (none='NONE' | "MAX_CALLS" callRate=SimpleMeasurement | "DATA_QUOTA" dataRate=SimpleMeasurement) "within" interval=SimpleMeasurement// note: just a PoC/demo, can be modeled much better (see pattern/books)	
;
```

2.3 InternalSLA：rate 子句的唯一宿主与严格顺序（L606–613）

```xtext
// APIDescription.xtext:606-613
InternalSLA:
	('type' type=SLAType)? // note: not checked/used at present (semantic check?) 
	slos+=SLO+
	('penalty' penalties=STRING)?
	('notification' reporting=STRING)?
	rp=RatePlan? 
	rl+=RateLimit*
;
```

由此得出 rate 子句的**全部硬约束**：

| 约束 | 语法依据 | 实测反例 |
|---|---|---|
| `rate plan` / `rate limit` **只能出现在 SLA 内部**（内联 SLA 或 SLA template），别无他处 | `RatePlan`/`RateLimit` 全语法仅被 L611/L612 引用 | n08–n11、n17 |
| 必须先有 **≥1 条 `objective`**（SLO），才能写 rate 子句 | `slos+=SLO+` 在 `rp`/`rl` 之前且为 `+` | n19（`required (...)+ loop did not match anything at input 'rate'`） |
| `rate plan` **最多 1 条** | `rp=RatePlan?` | n07 |
| `rate limit` **0..n 条**（可多条并存，如 MAX_CALLS + DATA_QUOTA 双配额） | `rl+=RateLimit*` | 正例 p2（单 SLA 5 条 limit） |
| **顺序固定**：`type?` → `objective+` → `penalty?` → `notification?` → `rate plan?` → `rate limit*`；rate limit 写在 rate plan 之前会报错 | 规则体有序 | n18（`mismatched input 'plan' expecting 'limit'`） |
| `penalty`/`notification` 若存在，必须在 rate 子句**之前** | 同上 | （由 n18 同机制推得；正例 p2 按序通过） |

2.4 SimpleMeasurement：rate limit 的测量值载体（L642–645）

```xtext
// APIDescription.xtext:642-645
SimpleMeasurement:
	value=INT
	unitOfMeasure=('hours' | 'minutes' | 'seconds' | 'MB' | 'GB'| ID | STRING)? // not a full specification of units/measures, just a PoC/demo
;
```

2.2 SLA 语法规则（逐字摘录）

`SLA` 与 `SLATemplate` 本体（前序 §2.2 已摘录，行号未漂移）：

```xtext
// APIDescription.xtext:596-598
SLA:
	'SLA' (builtin=InternalSLA | external=[SLATemplate])
;
// APIDescription.xtext:600-604
SLATemplate:
	'SLA' 'template'
	name=ID
	slas+=InternalSLA
;
```

2.3 SLA 关键字清单

| 关键字 | 语法角色 | 取值 | 是否必填 |
|---|---|---|---|
| `SLA` | 引入 SLA（内联或引用模板） | — | 可选 |
| `SLA template` | 声明**可复用**的具名 SLA 模板 | 后接 `ID` 名 | 顶层，0..n |
| `type` | SLA 类型 | `NONE` \| `IMPLICIT` \| `INFORMAL` \| `QUALITATIVE` \| `QUANTITATIVE` | 可选（**注释标注"目前未校验/未使用"**） |
| `objective` | 一条 SLO | `<ID 名> <STRING 质量目标> <measurement>` | **至少 1 条**（`slos+=SLO+`） |
| `penalty` | 违约罚则 | `STRING` | 可选 |
| `notification` | 违约通报方式 | `STRING` | 可选 |
| `rate plan` | 定价方案（MAP Pricing Plan） | `FREEMIUM` \| `SUBSCRIPTION` \| `USAGE_BASED` | 可选，最多 1 |
| `rate limit` | 限流（MAP Rate Limit） | `NONE` \| `MAX_CALLS <m>` \| `DATA_QUOTA <m>`，后接 `within <m>` | 可选，0..n |
| `minimal` / `target` / `optimal` | LandingZone 三档测量 | `<INT> <unit>` | `minimal`+`target` 必填，`optimal` 可选 |
| 计量单位 | `unitOfMeasure` | 预置 `hours` `minutes` `seconds` `MB` `GB`，或任意 `ID` / `STRING` | 可选 |

> **重要**：`InternalSLA` 的 `slos+=SLO+` 表示**一个 SLA 必须至少含一条 `objective`**；`rp=RatePlan?` 表示 `rate plan` **最多一条**；`rl+=RateLimit*` 表示 `rate limit` 可以多条。

2.5 挂载点：rate 子句最终能挂在哪里

```xtext
// APIDescription.xtext:40（顶层，ServiceSpecification 内）
	slas+=SLATemplate*          // 位于 contracts+=(...)* 之后、providers+=(...)* 之前 → 顺序约束

// APIDescription.xtext:438-445（provider 级）
Provider:
	'API' 'provider'
	name=ID
	('version' svi=SemanticVersioningIdentifier)? 
	epl+=EndpointList+
	('under' 'conditions' tsandcs=STRING | 'with' 'provider' sla=SLA)? // neither Ts&Cs nor SLA must be present
	('provider' 'governance'  evolStrat=EvolutionStrategy)? 
;

// APIDescription.xtext:452-457（endpoint 实例级）
EndpointInstance: 
	'at' 'endpoint' 'location' location=STRING  
	pb+=TechnologyBinding+
	('with' 'endpoint' sla=SLA)? // SLA is optional
	('endpoint' 'governance'  evolStrat=EvolutionStrategy)?
;
```

- provider 级 `under conditions "..."`（Ts&Cs）与 `with provider SLA` **互斥**（`|` 二选一，前序 §2.4 已证）——想在同一 provider 上既写条款又写含 rate 的 SLA 做不到；官方 CRM 示例的选择是把内联 SLA 挂在 endpoint 上、Ts&Cs 挂在 provider 上（`CustomerRelationshipManagementExample.mdsl` L130–145）。
- `Gateway` 的 `Gate` 规则复用 `EndpointInstance`（`endpoints+=EndpointInstance+`，L748–753），因此**网关端点同样能挂 `with endpoint SLA`**（含 rate 子句）——正例 p5 实测编译通过（但注意 §6.3 的 gateway OAS 崩溃 bug）。
- **不能**挂载的位置（全部实测证伪，§5）：`endpoint type` 类层（n11）、provider/endpoint 上脱离 SLA 直接写（n08–n10）、文件顶层（n17）。

官方示例一：`examples/MDSLGitPages/ProviderSLAClientExample.mdsl`（L10–26，rate 在 L19–20）

```mdsl
API provider SampleAPIProvider1 
  offers SomeDemoContract 
    at endpoint location "http://www.testdomain.io:80"
    via protocol HTTP binding resource SomeResource at "/path/subpath"
  	with endpoint SLA // provider1Endpoint1SLA
      type QUANTITATIVE // optional now
    	objective performanceSLO1 "responseTimeUnder" 5 seconds
    	penalty "If the SLA is not met, the penalty is ..."
    	notification "To report SLA violations, you have to ..."
    	rate plan USAGE_BASED
    	rate limit MAX_CALLS 5 within 24 hours
    endpoint governance AGGRESSIVE_OBSOLESCENCE
  with provider SLA // provider1SLA
  type QUALITATIVE
  objective performanceSLO2 "availability" 
     100 "every commercially reasonable effort, but not guaranteed"
  provider governance TWO_IN_PRODUCTION
```

官方示例二：`examples/examples-advanced/CustomerRelationshipManagementExample.mdsl`（模板 L102–108 + 内联 L130–136）

```mdsl
SLA template externalPerformanceSLAExample
 type QUANTITATIVE
 objective performanceSLO1 "responseTimeUnder" 5 seconds
 penalty "If the SLA is not met, the penalty is ..."
 notification "To report SLA violations, you have to ..."
 rate plan FREEMIUM
 rate limit DATA_QUOTA 1 call within 24 hours
```

</details>
