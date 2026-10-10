# SOP-02: 用户故事拆分（Story Splitting）

> **定位**: 把过大、复合动词的用户故事按动词拆为可独立交付的薄片子故事，并用反向引用（split-by back-reference）保持需求追溯链 | **组**: A（需求到模型） | **主要来源**: CML-Specification §26；DPR.md

## 何时启用

- 当一个故事过大、无法放进单个迭代交付时，使用本 SOP 拆薄
- 当一条故事含多个动词/操作（复合动词）、需要拆为可独立验收的薄片时，使用本 SOP
- 当故事将作为建模输入（[SOP-01](sop-01-rapid-ooad.md) 第 1 步）而动词槽位不原子时，先走本 SOP 再进入建模
- 当 API 设计需要"每个操作有独立故事背书"（[SOP-08](sop-08-story-driven-service-design.md) 的无故事不操作原则）而现有故事粒度过粗时，使用本 SOP

## 触发条件

- 故事四元组的动词槽位是**复合动词**：如 "manage" = create + edit + cancel；handle、process、maintain 同类
- 故事估算超过团队迭代阈值
- 验收标准超过约 5 条（经验阈值，按团队上下文调整——上下文至上，Context matters）
- 同一故事的多个动作会被不同团队/不同迭代分别交付

## 完整步骤

### 第 1 步：识别复合动词

检查故事的标准形态，锁定动词槽位：

```cml
// 标准形态模板（尖括号占位符替换后即为可解析的 UserStory；As a / As an 均合法）
// verb 属 UserActivityDefaultVerb（create | read | update | delete）时可不加引号
UserStory <StoryName> {
	As a "<role>"
	I want to "<verb>" an "<entity>" with its "<attribute>", "<attribute>" for a "<containerEntity>"
	so that "<benefit>"
}
```

复合动词是拆分信号：一个动词槽位对应多个可独立发生、独立验收的业务动作时，即触发拆分。

拆片的质量判据（业务分析师视角）：故事应以"自然但精确"的统一语言描述领域概念、属性与关系，让发起人、团队与其他干系人形成共享理解——拆分后的每个薄片仍须满足该判据。

### 第 2 步：展开原子动词

- 把复合动词分解为原子动词清单：manage → create / edit / cancel
- 每个"原子动词 + 原对象"构成一个候选子故事
- 需求为用例形态时，拆分对象是其交互列表（interactions）：列表中每个原子动词–对象对可独立成子故事，实体属性与容器引用（for a / in a）随对象迁移
- 展开时逐一确认：每个原子动作单独发生时，原收益陈述是否仍然成立？不成立的候选项剔除或改写收益

### 第 3 步：生成子故事

- 每个子故事继承原故事的**角色、对象、收益**，仅动词槽位替换为原子动词
- 子故事可以合并登记为一个子故事集（同角色同收益、多行 "I want to"），也可保持为相互独立的故事——按团队的积压管理习惯选择
- 原故事**保留**，作为追溯锚点，不删除

### 第 4 步：建立反向引用

- 原故事挂载 split-by 反向引用，指向其子故事（集）；子故事侧可回指原故事
- 反向引用是追溯链的机器可读形式：需求变更时可从原故事定位全部受影响子故事，反之亦然

### 第 5 步：校验与验收集

- 每个子故事：单一动词、可独立验收、收益陈述完整
- 子故事需要更精确的验收语义时，可登记为极简用例（Pre / 编号的"用户…系统…"交互步骤 / Post）——DPR 轻量工件库推荐的模板形态
- 追溯矩阵完整：原故事 ↔ 全部子故事双向可查
- 拆出的每个动词–对象对能映射为一个独立的服务操作 / API 端点候选

### 第 6 步：喂入下游

- 子故事清单进入 [SOP-01](sop-01-rapid-ooad.md) 第 2 步（原子动词直接派生服务操作）
- 或进入 [SOP-08](sop-08-story-driven-service-design.md)（每个原子动词成为一个操作的存在理由）
- 需要价值排序时进入 [SOP-04](sop-04-stakeholder-value-modeling.md)（子故事单独估值）

### 能力边界（显式声明）

语料确证的成熟实践为 PoC 状态：**仅"按动词拆分"（Split Story by Verb/Operation）一种策略**。按业务规则、数据变体、工作流步骤等其他维度的拆分不在本 SOP 保证范围内，需人工执行并自行验证拆片的独立交付性——按 [SOP-13](sop-13-method-engineering.md) 三规则裁剪采纳。

## 使用示例

账户管理故事（语料真实案例的中立化呈现）：

**原故事（拆分前）**：

| 槽位 | 值 |
|------|-----|
| 角色 | Admin（管理员） |
| 动词 | **manage** ← 复合动词，触发拆分 |
| 对象 | Account（账户） |
| 收益 | can enable users to work with the system |

**拆分结果（按动词 create / edit / cancel）**：

```cml
// 原故事保留作追溯锚点；split by 提供指向子故事（集）的反向引用
UserStory Account_Admin_Story split by Account_Admin_Story_Split {
	As an "Admin" I want to "manage" an "Account" so that "can enable users to work with the system."
}

// 子故事集：继承角色/对象/收益，仅动词槽位替换为原子动词
UserStory Account_Admin_Story_Split {
	As an "Admin"
	I want to "cancel" an "Account"
	I want to "edit" an "Account"
	I want to create an "Account"   // create 属 UserActivityDefaultVerb，可不加引号
	so that "can enable users to work with the system."
}
```

**追溯矩阵（第 5 步校验用）**：

| 原故事 | 子故事动词 | 单一动词 | 独立验收 | 映射目标（操作/端点候选） |
|--------|-----------|---------|---------|--------------------------|
| Account_Admin_Story | create | ✅ | ✅ | 创建账户操作 |
| Account_Admin_Story | edit | ✅ | ✅ | 修改账户操作 |
| Account_Admin_Story | cancel | ✅ | ✅ | 注销账户操作 |

## 技术交付物

- 子故事集（每条含指向原故事的反向引用）
- 原故事 ↔ 子故事追溯矩阵
- （可选）子故事 → 操作/端点映射表，供 SOP-01/08 直接消费

## 成功标准

- 每个子故事单一动词、可独立验收
- 反向引用完整：从任一子故事可达原故事，从原故事可达全部子故事
- 拆分后每个动词–对象对可映射为独立操作/端点（粒度满足下游建模与契约设计）
- 子故事继承原收益陈述，"so that" 不因拆分丢失或失真

## 反模式

- **复合动词直接进建模**："manage" 操作混杂 create/edit/cancel 语义，契约层出现语义不明的操作（对应 [SOP-11](sop-11-api-structure-analysis.md) 的 Ambiguous 坏味道家族）
- **拆分后丢失反向引用**：追溯链断裂，需求变更无法定位受影响子故事，拆分产物变成孤儿积压
- **货物崇拜式拆分**：机械地对所有故事执行拆分而不论其是否触发条件——违反"目的/有用性高于合规"（DPR 方法工程规则三）；只在触发条件满足时拆
- **拆片丢失收益**：子故事说不清 "so that"，说明拆分粒度错误（拆到了无独立业务价值的技术任务层）
- **只拆不验**：拆完不做第 5 步校验，子故事间仍存在隐含依赖、无法独立交付

## 关联

- 上游：[SOP-01](sop-01-rapid-ooad.md) 第 1 步（捕获精化需求时发现复合动词即转入本 SOP）
- 下游：[SOP-01](sop-01-rapid-ooad.md)（子故事喂入子域/BC 推导）；[SOP-08](sop-08-story-driven-service-design.md)（无故事不操作：每个原子动词背书一个操作）；[SOP-04](sop-04-stakeholder-value-modeling.md)（子故事进入价值评估）
- 方法治理：[SOP-13](sop-13-method-engineering.md)（以 DPR 三规则自检拆分策略的采纳与裁剪）
- 编排路线（绿地项目）：13 → 01/03 → 04 → 05/06 → 07 → 10 → 12（本 SOP 作为 01 的前置微步骤按需插入）

## 来源

- CML-Specification §26（Story Splitting PoC：Split Story by Verb/Operation、账户管理示例、split by 反向引用语义）
- CML-Specification §21（用户故事语法：多 "I want to" 行的故事集形态）
- DPR.md（story splitting 方法元素，2020-12 收录；方法工程三规则：上下文至上、有疑就删、目的高于合规）
- ICWE 2020 keynote（用户故事作为敏捷实践入口；业务分析师的故事模板——自然但精确的统一语言描述）
- 语法形态核对（2026-10-10，`ContextMapper/context-mapper-dsl` @ master）：`ContextMappingDSL.xtext` 的 `UserStory`（`'UserStory' name=ID ('split by' splittingStory=[UserStory])?`——反向引用挂在原故事侧）、`StoryFeature`（`'I want to' verb (a|an|the)? entity ('with its' 属性列表)? ('in'|'for'|'to' (a|an)? 容器实体)?`，多行 `I want to` 即多 Feature）、`UserActivityDefaultVerb`（`create|read|update|delete`，可不加引号；其余动词须写成 STRING）

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下代码块忠实摘自语料原文，供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考；每段标注来源与用途。上方「使用示例」已是**原生 CML**，与下方 §26「拆分后的结果」摘录同形——摘录按约定保留，作为语料原文证据；`split by` 反向引用挂在**原故事**侧，以语法为准。

**CML 拆分前的用户故事（CML-Specification §26，输入形态）**：

```cml
UserStory Account_Admin_Story {
    As an "Admin" I want to "manage" an "Account" so that "can enable users to work with the system."
}
```

**CML 按动词拆分后的结果（CML-Specification §26；`split by` 关键字提供指回原故事的反向引用）**：

```cml
UserStory Account_Admin_Story split by Account_Admin_Story_Split {
	As an "Admin" I want to "manage" an "Account" so that "can enable users to work with the system."
}

UserStory Account_Admin_Story_Split {
	As an "Admin"
	I want to "cancel" an "Account"
	I want to "edit" an "Account"
	I want to create an "Account"
	so that "can enable users to work with the system."
}
```

**CML 多动词故事集形态（CML-Specification §21，拆分目标形态的语法基础）**：

```cml
UserStory US1_Example {
  As an "Insurance Employee"
    I want to "create" a "Customer" with its "firstname", "lastname"
    I want to "update" an "Address" for a "Customer"
    I want to "offer" a "Contract" for a "Customer"
  so that "I am able to manage the customers data and offer them insurance contracts."
}
```

</details>
