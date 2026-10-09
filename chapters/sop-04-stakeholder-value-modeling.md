# SOP-04: 干系人与价值建模（Stakeholder & Value Modeling / VDAD）

> **定位**: 用价值驱动分析与设计（Value-Driven Analysis & Design，VDAD）把干系人（Stakeholder）及其价值（Value）显式化，支撑需求优先级排序、伦理影响评估与价值追溯 | **组**: A（需求到模型） | **主要来源**: CML-Specification §27/§29/§22/§23/§46.10

## 何时启用

- 当故事积压需要业务价值之外的**价值排序依据**时，使用本 SOP
- 当需要做伦理影响评估（某特性促进什么价值、损害什么价值）时，使用本 SOP
- 当要向业务侧/合规侧证明设计与干系人价值对齐时，使用本 SOP
- 当多干系人利益冲突（如用户隐私 vs 运营透明）需要显式化并进入决策记录时，使用本 SOP

## 触发条件

- 多干系人利益冲突浮现，口头协调已不可持续
- 合规/伦理审查要求提供价值影响的书面记录
- 需求评审缺少共同价值语言，优先级争论无法收敛
- 故事集已具备角色槽位（可从 [SOP-01](sop-01-rapid-ooad.md)/[SOP-02](sop-02-story-splitting.md) 的产出直接导出干系人）
- 语料佐证：干系人与价值建模能力自源工具链 v6.12.0（2024-08）起达到稳定状态，四步工作流完整可用

## 完整步骤

四步价值建模工作流（v6.12.0 引入的能力组合：干系人建模、价值登记册、故事估值语法扩展、地图派生与转换动作）：

### 第 1 步：干系人建模（Stakeholder Mapping）

- **从用户故事的角色批量导出干系人**——不手工另起清单，保证与需求侧同源可追溯
- 为每个干系人登记三属性：
  - 描述（description）：该干系人为何/如何使用系统或受其影响
  - 影响力（influence）：LOW / MEDIUM / HIGH
  - 关注利益（interest）：LOW / MEDIUM / HIGH
- 相关干系人可组织为**干系人组**（Stakeholder Group，如公司/团队/部门）
- 作用域二选一：绑定特定限界上下文（of ⟨BC⟩），或全局登记
- 影响力 × 利益四象限是第 4 步评审会的优先级输入

### 第 2 步：价值登记册（Value Register）

- 创建价值登记册：全局，或面向特定限界上下文；术语对齐 IEEE 7000 标准
- 登记价值条目（如 Privacy、Respect、Integrity），并补充价值属性：
  - **核心价值**（isCore）标记
  - **示例化**（demonstrator）：把价值落为可判断的具体陈述，如 "right to be left alone"
  - **关联价值**（relatedValue）与**对立价值**（opposingValue）：显式登记价值张力（如 Privacy 对立于 Transparency）
- 用**价值簇**（Value Cluster）组织相关价值并标注簇的核心价值类别（如 core PRIVACY）
- 在价值簇下建立**干系人–价值关系**，登记价值对该干系人的影响
- 已有干系人缺价值条目时，执行"为干系人生成价值"动作补齐

### 第 3 步：故事估值（Story Valuation，含伦理价值评估）

- 为既有用户故事追加**估值段**：在收益（so that）之外——
  - 用 "and that ⟨价值⟩ is promoted" 声明故事**促进**的价值
  - 用 "accepting that ⟨价值⟩ are harmed" 声明故事**接受损害**的价值
- 价值判断必须指向价值登记册中已登记的条目（估值–登记册闭环，杜绝口号式价值）
- 伦理评估 = 促进价值与受损价值的权衡记录，作为需求取舍与优先级的显式依据

### 第 4 步：视图派生与决策支撑

- 派生**干系人地图**（Stakeholder Map）：干系人/组及其影响力–利益分布的可视化
- 派生**价值影响地图**（Value Impact Map）：故事 → 价值 → 干系人的影响链可视化
- 表格化导出干系人数据与价值登记册数据（CSV 类），供离线评审与归档
- 两张地图 + 估值故事集带入优先级决策会议；决策结论应能回指到地图上的价值依据

## 使用示例

三个语料真实案例的中立化呈现：

**示例 1 — 故事估值（保险场景，第 3 步形态）**：

| 估值段槽位 | 内容 |
|-----------|------|
| 角色 | prospective customer of Lakeside Mutual（潜在客户） |
| 想要 | manage the PersonalDataProfile（管理个人数据档案） |
| 收益（so that） | I am offered a valid and fair insurance rate |
| 促进价值（and that … is promoted） | data privacy（数据隐私） |
| 受损价值（accepting that … are harmed） | accountability and auditability（可问责与可审计性） |

**示例 2 — 价值登记册（同日达购物场景，第 2 步形态）**：

```yaml
ValueRegister: SDD_Stakeholder_Values（面向 Online_Shop_Same_Day_Delivery）
  Value Privacy:
    核心价值: 是（isCore）
    示例化:
      - "right to be left alone"
      - "the right to refuse sharing private data"
    关联价值: Intimacy
    对立价值: [Transparency, Inclusiveness]
  ValueCluster Privacy:
    核心类别: PRIVACY
    Value Confidentiality: { 示例化: "right to be left alone" }
    Stakeholder Customers_and_Shoppers:   # 登记价值对该干系人的影响
```

**示例 3 — 干系人组（在线购物场景，第 1 步形态）**：

| 干系人 | 所属组 | 影响力 | 关注利益 | 描述 |
|--------|--------|--------|----------|------|
| Shopper | —（全局） | MEDIUM | HIGH | 使用购物系统购买日常商品 |
| Development_Team | Online_Shopping_Company | MEDIUM | HIGH | |
| Product_Management | Online_Shopping_Company | HIGH | HIGH | |
| Customer_Relationship_Manager | Online_Shopping_Company | HIGH | MEDIUM | |

## 技术交付物

- 干系人登记册：描述 + 影响力 + 关注利益，含组结构与限界上下文作用域
- 价值登记册：价值条目 + 属性（核心/示例化/关联/对立）+ 价值簇 + 干系人–价值关系（IEEE 7000 术语）
- 带估值的故事集：每条含促进价值与受损价值标注
- 干系人地图、价值影响地图（可视化派生物）
- 表格化导出文件（干系人数据、价值登记册数据，供评审归档）

## 成功标准

- 每个故事角色都有对应干系人（导出链完整，非手工补造）
- 每个干系人至少登记一条价值
- 高影响故事（涉及高影响力 × 高关注利益干系人）有价值/伦理标注，**受损价值不被省略**
- 价值判断全部指向登记册条目（无未登记的口号价值）
- 两张地图能支撑一次真实的优先级决策会议，决策可回溯到价值依据

## 反模式

- **只记促进、不记受损**："accepting that … are harmed" 是估值段的一等公民；省略受损价值的伦理评估是半套橡皮图章
- **价值无示例化/无对立面**：缺 demonstrator 与 opposingValue 的价值退化为不可判断的口号，无法进入权衡
- **干系人清单手工另起**：脱离故事角色的干系人列表失去需求侧追溯性——应从故事角色批量导出
- **两张地图只挂墙不进会**：产出可视化却不支撑决策，属合规表演，违反"目的/有用性高于合规"（DPR 方法工程规则三）
- **价值评估取代需求讨论**：估值是优先级与伦理的**输入**，不能替代故事收益（so that）本身的澄清
- **一次性登记**：干系人影响力/利益随项目阶段漂移，价值张力随特性变化——登记册需随迭代复审

## 关联

- 上游：[SOP-01](sop-01-rapid-ooad.md) / [SOP-02](sop-02-story-splitting.md)（故事角色是干系人的导出源；拆分后的子故事单独估值）；[SOP-03](sop-03-event-storming-modeling.md)（事件风暴的用户角色同为干系人线索）
- 下游：[SOP-08](sop-08-story-driven-service-design.md)（故事驱动契约设计以估值故事为优先级输入）；[SOP-10](sop-10-map-decoration.md)（价值张力可映射为契约层力场权衡，如隐私 ↔ 数据新鲜度）
- 方法治理：[SOP-13](sop-13-method-engineering.md)（估值模板的裁剪与采纳自检）
- 编排路线（绿地项目）：13 → 01/03 → **SOP-04** → 05/06 → 07 → 10 → 12

## 来源

- CML-Specification §27（干系人与价值建模变换三动作：为故事添加伦理价值评估、从故事角色创建干系人、为干系人创建价值）
- CML-Specification §29（VDAD 支持：干系人地图与价值影响地图派生、故事估值语法扩展、表格化导出）
- CML-Specification §22（干系人语法：容器、三属性、干系人组、限界上下文作用域）、§23（价值登记册语法：IEEE 7000 术语、价值属性、价值簇、干系人–价值关系）、§21（故事估值/ESE 语法）
- CML-Specification §46.10（v6.12.0，2024-08-30：干系人与价值建模支持发布并稳定，四步工作流的能力组合）
- 分析报告 F9（VDAD 链：干系人建模 → 价值登记册 → 故事估值 → 两张地图）

---
<details>
<summary>📎 原始语法参考（CML/MDSL）— 点击展开</summary>

以下代码块忠实摘自语料原文，供对接 BCM（`github.com/appfun-dev/bcm`）的 CUE 元模型时参考；每段标注来源与用途。

**CML 故事估值/ESE（CML-Specification §21，第 3 步估值段语法：and that … is promoted / accepting that … are harmed）**：

```cml
UserStory SampleStory {
  As a "prospective customer of Lakeside Mutual"
  I want to "manage" the "PersonalDataProfile" 
  so that "I am offered a valid and fair insurance rate"
  and that "data privacy" is promoted
  accepting that "accountability and auditability" are harmed
}
```

**CML 干系人容器与个体（CML-Specification §22，第 1 步：作用域、三属性）**：

```cml
BoundedContext ExampleContext

Stakeholders of ExampleContext {
  Stakeholder Shopper {
    description "Is using the shopping system to by everday goods."
    
    influence MEDIUM
    interest HIGH
  }
}
```

**CML 干系人组（CML-Specification §22，第 1 步：组结构组织）**：

```cml
Stakeholders of ExampleContext {
  StakeholderGroup Online_Shopping_Company {
    Stakeholder Development_Team {
      influence MEDIUM
      interest HIGH
    }
    Stakeholder Product_Management {
      influence HIGH
      interest HIGH
    }
    Stakeholder Customer_Relationship_Manager {
      influence HIGH
      interest MEDIUM
    }
  }

  Stakeholder Shopper {
    description "Is using the shopping system to by everday goods."
    influence MEDIUM
    interest HIGH
  }
}
```

**CML 价值登记册与价值属性（CML-Specification §23，第 2 步：登记册作用域、isCore/demonstrator/relatedValue/opposingValue）**：

```cml
// For a specific Bounded Context
BoundedContext Online_Shop_Same_Day_Delivery

ValueRegister SDD_Stakeholder_Values for Online_Shop_Same_Day_Delivery {
  // model values inside value register
}

ValueRegister SDD_Stakeholder_Values {
  Value Privacy {
    isCore

    demonstrator = "right to be left alone"
    demonstrator = "the right to refuse sharing private data"
    relatedValue = "Intimacy"
    opposingValue = "Transparency"
    opposingValue = "Inclusiveness"
  }
}
```

**CML 价值簇与干系人–价值关系（CML-Specification §23，第 2 步：簇组织与影响登记）**：

```cml
ValueRegister SDD_Stakeholder_Values {
  ValueCluster Privacy {
    core PRIVACY

    Value Confidentiality {
      demonstrator = "right to be left alone"  
    }
    
    Stakeholder Customers_and_Shoppers {
      // impact on this stakeholder
    }
  }
}
```

</details>
