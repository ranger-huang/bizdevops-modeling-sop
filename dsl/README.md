# dsl/ — CML / MDSL 语法文件（随仓库版本化）

**为什么存在**：本手册 15 个 SOP 的示例都是原生 CML / MDSL，深度语法检查过去每次都要去上游仓库下载、解压或读临时副本。语法文件现在与项目一起版本化留档，就地取证、可校验、可追溯。

- **CML**（Context Mapping DSL）：[`cml/ContextMappingDSL.xtext`](./cml/ContextMappingDSL.xtext) + [`cml/TacticDDDLanguage.xtext`](./cml/TacticDDDLanguage.xtext)（主语法 `with` 继承战术语法，必须成对使用）
- **MDSL**（含 AsyncMDSL 扩展）：[`mdsl/APIDescription.xtext`](./mdsl/APIDescription.xtext)（唯一语法文件）
- 出处、pin commit、校验值见 [`VERSIONS.md`](./VERSIONS.md)（自动生成）

## 深度语法检查的取证顺序

1. **定位** — 查 [`cml/grammar-index.md`](./cml/grammar-index.md) / [`mdsl/grammar-index.md`](./mdsl/grammar-index.md)，按规则名拿到行区间
2. **精读** — 用 `read` 工具带 `offset`/`limit` 读对应 `.xtext` 区间（语法形态的**唯一权威**）；也可 `grep` 关键字面量反查规则
3. **确认版本** — 需要声明依据时引用 [`VERSIONS.md`](./VERSIONS.md) 的 pin commit 与 blob sha1
4. **章节折叠段** — 各 SOP 文末「原始语法参考」是**语料原文摘录**，用于追溯手册措辞来源；与语法文件冲突时**以语法文件为准**，并按 SOP-13 记录校正

**不要**：下载/解压上游仓库、读取 `/tmp` 或缓存里的副本、凭记忆断言语法形态或枚举取值域。
语法文件只回答「能不能这么写」；「能写但表达不了什么」（测量值仅整数、无 deprecated/sunset 子句等）见 [patterns.md](../patterns.md) ⑧⑨ 与 sop-14/15，不可表达部分一律带外治理。

## 目录

| 路径 | 内容 | 可否手改 |
|------|------|----------|
| `cml/*.xtext`、`mdsl/*.xtext` | 上游语法文件，逐字节原样留档 | ❌ 不手改、不加头注释 |
| `cml/grammar-index.md`、`mdsl/grammar-index.md` | 规则名 → 类型 → 行区间 → 定义首行摘要 | ❌ 自动生成 |
| `*/LICENSE` | 上游 Apache-2.0 许可证副本（随文件分发所需） | ❌ |
| `VERSIONS.md` | 版本账本：pin commit、字节/行数、git blob sha1、sha256、release 对照 | ❌ 自动生成 |
| `sync.py` | 同步 + 校验工具（版本信息的**唯一 owner**） | ✅ |
| `gen_index.py` | 索引生成器（被 `sync.py` 调用，也可单独运行） | ✅ |
| `README.md` | 本文件 | ✅ |

## 维护：保持最新

```bash
python3 dsl/sync.py --check                  # 只读：报告上游是否前进 + 本地是否被改动
python3 dsl/sync.py                          # 同步到上游分支 HEAD，逐字节校验，重生成账本与索引
python3 dsl/sync.py --dsl cml --pin <sha>    # 锁定/回退到指定上游 commit
GITHUB_TOKEN=... python3 dsl/sync.py         # 未认证时 api.github.com 限 60 次/小时
```

约定：

- **默认跟随上游分支 HEAD**（即「维护最新」）；`VERSIONS.md` 里的 pin 记录是上一次同步的结果，`--check` 用它报告漂移。
- 同步后 `git diff dsl/` 复核语法变化，并把影响落回相关章节（对照下表），同一次提交里更新章节的「语法形态核对」日期与 pin commit。
- 语法文件保持与上游逐字节一致，这样 `git blob sha1` 校验有效、后续 `git diff` 只反映真实的上游演进。出处信息只写在 `VERSIONS.md`，不写进语法文件。
- 索引/账本由工具生成，出现分歧时重跑 `sync.py` 而不是手工修补。

## SOP 主题 → 语法规则对照

起点定位用；行区间一律查对应的 `grammar-index.md`（不在本表复制，避免二次维护）。

| SOP / 主题 | DSL | 关键规则 |
|------------|-----|----------|
| 01 快速 OOAD · 05 架构重构 · 06 系统化分解 | CML | `ContextMap` `BoundedContext` `Domain` `Subdomain` `Aggregate` `UpstreamDownstreamRelationship` `Partnership` `SharedKernel` `CustomerSupplierRelationship` |
| 02 用户故事拆分 | CML | `UserStory` `StoryFeature` |
| 03 事件风暴建模（CQRS/事件溯源） | CML | `Application` `Flow` `FlowStep` `DomainEventProductionStep` `CommandInvokationStep` `Coordination`；战术侧 `Enum` `TargetState` `ServiceOperation` |
| 04 干系人与价值建模（VDAD） | CML | `Stakeholders` `Stakeholder` `StakeholderGroup` `ValueRegister` `ValueCluster` `ValueElicitation` `StoryValuation` `CoreValue` |
| 07/08 领域与故事驱动服务设计 | MDSL | `ServiceSpecification` `DataContract` `EndpointContract` `Operation` `IntegrationScenario` `IntegrationStory` |
| 07/10 契约精化与 MAP 装饰 | MDSL | `PatternStereotype` `MapPattern` `EipPattern` `ParameterRole` `ResourceRole` `OperationResponsibility` `TypeReference` `AtomicParameter` `ParameterTree` `BasicDataType` |
| 09 事件驱动服务设计（AsyncMDSL） | MDSL | `ChannelContract` `ChannelType` `DeliveryGuarantee` `OneWayChannel` `RequestReplyChannel` `Payload` `MessageType` `MessageBroker` `MessageEndpoint` `Orchestration` |
| 11 存量 API 结构分析 | MDSL | `OperationResponsibility` `ResourceRole` |
| 12 模型-代码一致性验证 | CML | `Entity` `ValueObject` `Attribute` `Reference` `Visibility` `Type` `Parameter` `DomainObjectOperation` `Service` `ServiceOperation` |
| 14 质量管理与治理 | MDSL | `SLATemplate` `Provider` `EndpointInstance` `Client` `Gateway` |
| 15 版本演进 | MDSL | `SemanticVersioningIdentifier` `EvolutionStrategy` `EndpointContract` `Operation` `Provider` `EndpointInstance` `Gateway` |

## 许可证与归属

两套语法均为 **Apache-2.0**：CML © The Context Mapper Project Team（战术语法源自 Sculptor Project Team）；MDSL © Olaf Zimmermann。许可证全文副本随各自目录留档（`cml/LICENSE`、`mdsl/LICENSE`）。本目录仅作为方法学参考再分发，未修改上游内容。

## 入库范围（有疑就删）

- 已入库：上表语法文件 + 许可证 + 生成的索引与账本。
- 未入库：CML `ServiceCutterConfigurationDSL.xtext`（服务切分工具配置，本手册 SOP 未引用）、MDSL `GenerateAPIDescription.mwe2`（Xtext 代码生成配置，与语法检查无关）、上游示例 `*.mdsl`/`*.cml`（章节示例已自足）。需要时再按同样方式加进 `sync.py` 的 `DSLS` 配置。
