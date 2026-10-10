# SOP-12: 模型-代码一致性验证（Model–Code Consistency Validation）

> **定位**: 把领域模型中的结构约束转写为构建期自动执行的架构规则（架构适应度函数），让"模型-代码鸿沟"（model-code gap）无处悄悄扩大 | **组**: D | **主要来源**: CML §43 架构验证、§46.7/46.8/46.9 发布记录（工具已泛化为"架构规则验证"方法）

## 何时启用

当模型与实现**并存**之后启用——即领域模型已经用于生成代码骨架、指导手工实现，或作为架构评审的权威依据时。

典型处境：
- 模型驱动开发已跑通一轮（模型 → 契约 → 实现骨架），进入持续迭代期；
- 团队发现有人在实现里绕过模型直接改结构（新增跨边界依赖、私自暴露聚合内部）；
- 架构评审时代码结构与模型图对不上，且没人说得清哪边是"对的"；
- 棕地系统刚补建领域模型，需要代码现状与模型的差异清单。

一句话原则：**建模不消除漂移，守护才消除漂移**。模型画得再精确，只要没有自动化验证闭环，模型-代码鸿沟就会随每次"顺手改一下"而扩大，最终模型沦为无人相信的装饰品。

## 触发条件

满足任一即应启动本 SOP：

1. **模型已投入实现用途** — 模型被用于生成实现骨架/契约，或被团队公认为结构的权威来源；
2. **出现绕行修改** — 代码评审发现实现直接变更了结构（跨限界上下文引用、绕过聚合根访问内部实体），而模型未同步更新；
3. **评审发现结构偏离** — 架构评审中代码的包/模块边界与模型中的限界上下文（Bounded Context）、聚合（Aggregate）边界不一致；
4. **重构历史分叉** — 模型侧做过架构重构（SOP-05 的 AR），但代码侧的对应重构无迹可查（或反之）；
5. **新成员提问暴露鸿沟** — "文档说的和代码里的不一样，我该信哪个？"这类问题反复出现。

## 完整步骤

### 步骤 0：先验证模型自身（前提）

代码级验证只有在模型自身一致时才有意义。先对模型做语义一致性校验：

- 无悬空引用（引用了不存在的上下文/聚合/类型）；
- 无不可达的限界上下文（不在任何上下文映射中、也无任何关系连接）；
- 关系角色组合合法（如：防腐层（ACL）与遵奉者（CF）互斥、不能同时应用于同一下游；开放主机服务（OHS）/发布语言（PL）只能由上游承担；对称关系（伙伴关系/共享内核）中不适用 OHS/PL/ACL/CF）。

模型自身红灯时先修模型（或按 SOP-05 走架构重构），**不要**带着病模型转写代码规则——否则会把模型错误固化成规则。

### 步骤 1：盘点模型中可验证的结构约束

从模型中提取三类核心约束（这是规则集的骨架，宁少勿滥）：

| 约束类 | 模型侧表述 | 代码侧含义 |
|--------|-----------|-----------|
| **BOUNDED_CONTEXT_BOUNDARY**（BC 边界） | 每个限界上下文拥有自己的聚合与类型 | 上下文内的类型不得被其他上下文的代码单元（包/模块/服务）引用；跨上下文交互只经由契约（暴露的端点/发布语言） |
| **AGGREGATE_BOUNDARY**（聚合边界） | 聚合有唯一聚合根（aggregate root）；跨聚合引用通过标识（值对象 ID），在 CML 中即 `REF`（`-`）引用 | 聚合内部类型（非根实体、值对象）不得被聚合外直接引用；对其他聚合的引用必须是标识符而非对象引用 |
| **STEREOTYPE**（刻板印象） | 实体/值对象/领域事件/服务等构造型（stereotype）标注 | 每类构造型对应代码中的构造约定：如值对象不可变、聚合根携带根标记、领域事件命名与载荷同模型一致 |

实践提示：当模型规模大时，先只覆盖**一个**限界上下文的三类约束跑通闭环，再逐个上下文推广。

### 步骤 2：把约束转写为架构规则

将每条约束转写为一条可机器执行的规则（用你技术栈中任何"架构规则验证/适应度函数"手段：架构测试库、依赖分析脚本、自定义静态检查皆可）。规则表述模式：

```
rule <id> (<constraint class>):
  statement:  <who> MUST NOT | MUST <structural relation> <whom>
  scope:      <code unit / package / namespace pattern>
  because:    model element <path>        # 如 eCommerceContext/Order（Aggregate）
  severity:   ERROR（红灯阻断）| WARNING（记录不阻断）

constraint class ∈ { BOUNDED_CONTEXT_BOUNDARY, AGGREGATE_BOUNDARY, STEREOTYPE }
```

三条底线：
- 每条规则**必须回指模型元素**——规则是模型约束的投影，不是独立的代码规范；
- 起点全部设 ERROR 太重时，允许存量违规先降级为 WARNING（冻结清单），但**新增违规必须 ERROR**；
- 规则集进版本库，与模型同版本节奏演进。

### 步骤 3：固化为构建期自动化验证

把规则集挂到每次构建/持续集成流水线上，作为**架构适应度函数**（architectural fitness function）执行：

- 违规 → 构建失败（红灯），清单指明：违反哪条规则、代码位置、对应模型元素；
- 验证必须发生在**合并之前**（构建期/提交期），而非季度性架构评审——鸿沟是在日常提交中形成的，守护也必须在日常提交中发生。

### 步骤 4：红灯处置——二选一，禁止第三条路

每次红灯只有两个合法出口：

| 出口 | 动作 | 记录 |
|------|------|------|
| **A. 改代码** | 认定模型是对的，把代码改回合规（如：把对象引用改回标识引用） | 提交信息注明"恢复与模型一致" |
| **B. 正式改模型** | 认定代码揭示了模型的问题，走正式模型变更：更新模型 → 记录决策（Y-statement，见 SOP-13）→ 若涉及分解结构变化则按 SOP-05 补架构重构记录 → 同步更新规则集 | 决策记录：为什么代码是对的、模型错在哪 |

被禁止的第三条路：**静默豁免**（注释掉规则、加白名单不写理由、"先跳过以后再说"）。每一次豁免都是一次无声的模型漂移。

### 步骤 5：定期比对演进历史

每个迭代/每月做一次轻量比对：

- 模型侧的变更（尤其 SOP-05 的 AR 应用）是否都有代码侧对应重构？
- 代码侧的结构性变更是否都反映回模型？
- WARNING 冻结清单是在缩小还是在扩大？

比对结果一页纸即可，目的是发现“规则集落后于模型演进”这类二阶漂移。

## 使用示例

电商域模型（两个聚合）：

```cml
// R1（BOUNDED_CONTEXT_BOUNDARY）：本 BC 内类型不得被其他 BC 的代码单元引用
BoundedContext eCommerceContext {
	Aggregate Product {
		// R5（STEREOTYPE）：aggregateRoot 标记 —— 每个模型聚合根在代码中有且仅有一个根标记类型
		Entity Product {
			aggregateRoot
			- ProductId id;         // '-' 是 REF 终结符（'-' | 'reference'）：引用值对象标识，非普通属性
			String name;
			String description;
			double price;
		}

		// R4（STEREOTYPE）：模型中标注为 ValueObject 的类型在代码中不可变（无公开设值方法）
		ValueObject ProductId {
			String value;
		}
	}

	Aggregate Order {
		Entity Order {
			aggregateRoot
			- OrderId id;
			- UserId purchaserId;             // R3（AGGREGATE_BOUNDARY）：跨聚合引用用标识类型，不用实体类型
			- List<OrderItem> items;          // R2（AGGREGATE_BOUNDARY）：OrderItem 不得被 Order 聚合外直接引用
			DateTime ordered;
		}

		ValueObject OrderItem {
			- ProductId productId;            // 引用 Product 聚合：只持标识，不持对象
			int amount;
		}

		// 语料 §43 摘录未声明 OrderId / UserId，此处补齐使模型自洽（否则为悬空引用）
		ValueObject OrderId {
			String value;
		}

		ValueObject UserId {
			String value;
		}
	}
}
```

注意：Order 引用 Product 用的是**值对象 ProductId（标识）**，而非对象本身。

**转写出的规则集**：

| 规则 | 约束类 | 陈述 | 严重度 |
|------|--------|------|--------|
| R1 | BOUNDED_CONTEXT_BOUNDARY | `ecommerce` 包内类型不得被其他 BC 的包引用（契约层除外） | ERROR |
| R2 | AGGREGATE_BOUNDARY | `OrderItem` 不得被 Order 聚合之外的代码直接引用 | ERROR |
| R3 | AGGREGATE_BOUNDARY | 跨聚合引用必须使用标识类型（`ProductId`/`OrderId`），不得使用实体类型 | ERROR |
| R4 | STEREOTYPE | 模型中标注为值对象的类型在代码中不可变（无公开设值方法） | ERROR |
| R5 | STEREOTYPE | 每个模型聚合根在代码中有且仅有一个根标记类型 | WARNING |

上表只列出陈述与严重度两列；模板要求的另两字段在本示例中的落点是——`because`（模型依据）= 上方 CML 里 R1~R5 注释所锚定的元素路径，`scope`（代码单元/包模式）= 各规则实际落地时按项目包结构填写。

**红灯场景**：某开发者为"省一次查询"，让 `OrderItem` 直接持有 `Product` 实体引用 → R3 红灯。

**二选一处置**：
- 出口 A（多数情况）：改回 `ProductId` 标识引用，查询在应用层按需组装 → 提交注明"恢复与模型一致"；
- 出口 B（少数情况）：团队评审发现 Order 与 Product 实际上总是一起变更、由同一团队维护 → 这不是代码问题而是分解问题 → 按 SOP-05 评估 AR-6（合并聚合）→ 更新模型 + Y-statement 决策记录 + 调整规则集。

## 技术交付物

1. **架构规则集**（版本化文件）：每条规则含陈述、范围、模型依据、严重度；
2. **CI 验证任务**：构建期执行的适应度函数配置，红灯即阻断合并；
3. **违规清单与处置记录**：存量 WARNING 冻结清单（只许缩小）+ 每次红灯的出口 A/B 处置记录；
4. **模型-代码比对报告**（定期一页纸）：双向变更对照与鸿沟趋势。

## 成功标准

- [ ] 规则覆盖**三类核心约束**：BOUNDED_CONTEXT_BOUNDARY（BC 边界）、AGGREGATE_BOUNDARY（聚合边界）、STEREOTYPE（刻板印象）——每类至少一条 ERROR 级规则；
- [ ] 验证在构建期自动执行，**红灯即停**——违规代码无法静默合入主干；
- [ ] 每一次模型与代码的偏离都有**显式决策记录**（出口 A 的提交说明或出口 B 的 Y-statement），无静默漂移；
- [ ] 每条规则可回指模型元素；模型变更后规则集同步更新（步骤 5 比对无长期悬空项）；
- [ ] 存量冻结清单随时间**单调缩小**。

## 反模式

| 反模式 | 后果与纠正 |
|--------|-----------|
| **静默模型漂移** | 实现绕过模型直接改、无人拦截 → 文档与现实脱节，模型失去权威性；纠正：把验证放进构建期而非评审期 |
| **规则集体豁免** | 红灯太多时团队一键注释规则/加大白名单 → 规则名存实亡；纠正：存量降级 WARNING 冻结、新增必须 ERROR，冻结清单只许缩小 |
| **一次性验证** | 项目启动时验证一轮就不再执行 → 鸿沟在日常提交中重新形成；纠正：适应度函数随每次构建运行 |
| **代码反向绑架模型** | 红灯一律走"改模型让它过" → 模型退化为代码的影子文档；纠正：出口 B 必须有决策记录并过评审 |
| **规则无模型依据** | 把一般代码规范混进架构规则集 → 规则集膨胀、噪音淹没真信号；纠正：每条规则回指模型元素，纯代码规范另置 |
| **模型自身不一致就开始转写** | 把模型错误固化成规则 → 规则集先天带病；纠正：先过步骤 0 的模型级语义校验 |

## 关联

- [SOP-05 架构重构](sop-05-architectural-refactorings.md) — 红灯出口 B 涉及分解结构变化时，走 AR 流程并补决策记录
- [SOP-07 领域驱动服务设计](sop-07-domain-driven-service-design.md) — 本 SOP 守护的正是"模型 → 契约 → 实现"链路的最后一环
- [SOP-11 存量 API 分析](sop-11-api-structure-analysis.md) — 棕地场景常先做 API 盘点（SOP-11）再补模型，随后进入本 SOP 守护
- [SOP-13 方法工程与采纳](sop-13-method-engineering.md) — 验证规则集本身也是方法元素，引入时过三规则；Y-statement 模板见该章
- [../patterns.md](../patterns.md) — AR 目录（出口 B 用）；[../glossary.md](../glossary.md) — model-code gap、聚合根、刻板印象等术语

## 来源

- CML §43《架构验证》：验证代码符合模型、"keeping model and implementation in sync"（本文泛化为架构规则验证方法，不绑定具体工具）
- CML §46.8：验证扩展首次发布——"验证代码中的战术 DDD 概念符合模型"；§46.9：示例应用演示该验证；§46.7：模型级语义验证器（歧义引用、不可达限界上下文）
- CML §4 语义规则 Rule #1–#10（步骤 0 模型级校验的依据）
- 分析报告 §3 SOP-12、§5 原则 11（模型-代码鸿沟需主动守护）、§6 反模式（静默模型漂移）
- 语法形态核对（2026-10-10，`ContextMapper/context-mapper-dsl` @ master，`TacticDDDLanguage.xtext`）：`terminal REF : ('-' | 'reference')` 与 `Reference` 规则（`REF (visibility)? (CollectionType<@DomainObject> | @DomainObject) name`——故 `- ProductId id` 与 `- List<OrderItem> items` 都是**引用**而非普通属性）；`enum Visibility : public | protected | private | package`（**不含** `-` / `+` / `#` 符号，因此 `-` 只能解释为 REF）；`Attribute` 规则末尾为 `(";")?`（分号可选）；`Entity` 的 `aggregateRoot` 标记；`ValueObject` 单词连写；`Type` 含 `double` / `DateTime` / `BigDecimal` 等且末位为 `JavaIdentifier`（深度语法核对改读仓库内权威副本：CML `../dsl/cml/ContextMappingDSL.xtext` + `../dsl/cml/TacticDDDLanguage.xtext`，规则名→行区间查对应 `grammar-index.md`，pin commit 与 sha256 见 `../dsl/VERSIONS.md`），不再下载/解压上游仓库或读临时副本
- 校正记录：语料 §43 摘录里 `- OrderId id`、`- UserId purchaserId` 所引用的 `OrderId` / `UserId` 未在摘录内声明（`ProductId`、`OrderItem` 有声明），单独拷贝会悬空；使用示例已补 `ValueObject OrderId` 与 `ValueObject UserId` 使模型自洽

---
<details>
<summary>📎 原始语法参考（CML）— 点击展开</summary>

CML §43 架构验证示例模型（本文步骤 2 三条规则的转写对象）。上方「使用示例」已是同一模型的**原生 CML 完整版**——补声明了摘录中未定义的 `OrderId` / `UserId`，并把 R1~R5 锚点标到对应元素上；摘录按约定保留原样。关键语法点：`- ProductId productId` 里的 `-` 是 `REF` 终结符（`terminal REF : ('-'|'reference')`），表示**引用另一个领域对象**，不是可见性修饰——这正是 AGGREGATE_BOUNDARY 类规则"跨聚合引用必须用标识"的语言级载体：

```cml
BoundedContext eCommerceContext {
  Aggregate Product {
    Entity Product {
      aggregateRoot
      - ProductId id;
      String name;
      String description;
      double price;
    }

    ValueObject ProductId {
      String value;
    }
  }

  Aggregate Order {
    Entity Order {
      aggregateRoot
      - OrderId id;
      - UserId purchaserId;
      - List<OrderItem> items;
      DateTime ordered;
    }

    ValueObject OrderItem {
      - ProductId productId;
      int amount;
    }
  }
}
```

</details>
