# CML 语法规则索引 — ContextMappingDSL.xtext

> **自动生成，勿手改**（生成器：`dsl/gen_index.py`，重跑：`python3 dsl/sync.py`）。
> 深度语法检查流程：在本表按规则名定位行区间 → 用 `read` 工具带 `offset`/`limit` 精读该区间；
> 不要下载/解压上游仓库，也不要读临时目录里的副本。

- 语法文件：[`ContextMappingDSL.xtext`](./ContextMappingDSL.xtext)（556 行，sha256 `440d9a081c28c89b...`）
- 上游：[`ContextMapper/context-mapper-dsl`](https://github.com/ContextMapper/context-mapper-dsl) @ `master` commit `995f486a9cde`（2025-07-08）
- 规则数：79（enum 17 · parser 60 · terminal 2）
- 生成日期：2026-10-10

| 规则 | 类型 | 行区间 | 定义首行摘要 |
|------|------|--------|--------------|
| `ContextMappingModel` | parser | 23–34 | `( (topComment=SL_COMMENT \| topComment=ML_COMMENT)? & (imports+=Import...` |
| `Import` | parser | 36–37 | `'import' importURI=STRING` |
| `ContextMap` | parser | 39–48 | `{ContextMap}` |
| `BoundedContext` | parser | 50–71 | `(comment=ML_COMMENT \| comment=SL_COMMENT)? 'BoundedContext' name=ID (...` |
| `DomainPart` | parser | 73–75 | `Domain \| Subdomain` |
| `Domain` | parser | 77–85 | `'Domain' name=ID ( OPEN (('domainVisionStatement' ('=')? domainVision...` |
| `Subdomain` | parser | 87–97 | `'Subdomain' name=ID ('supports' (supportedFeatures+=[UserRequirement]...` |
| `Relationship` | parser | 99–101 | `SymmetricRelationship \| UpstreamDownstreamRelationship` |
| `SymmetricRelationship` | parser | 103–105 | `Partnership \| SharedKernel` |
| `Partnership` | parser | 107–119 | `( (participant1 = [BoundedContext] '[''P'']' '<->' '[''P'']' particip...` |
| `SharedKernel` | parser | 121–134 | `( (participant1 = [BoundedContext] '[''SK'']' '<->' '[''SK'']' partic...` |
| `UpstreamDownstreamRelationship` | parser | 136–153 | `CustomerSupplierRelationship \| ( ( (upstream = [BoundedContext] (('['...` |
| `CustomerSupplierRelationship` | parser | 155–171 | `( ( (upstream = [BoundedContext] '['('U'',')?'S'(','(upstreamRoles+=U...` |
| `Aggregate` | parser | 173–200 | `(comment=ML_COMMENT)? (doc=STRING)? "Aggregate" name=ID (OPEN ( (('re...` |
| `Application` | parser | 202–210 | `"Application" (name=ID)? (OPEN ((commands+=CommandEvent)* & (events+=...` |
| `Coordination` | parser | 212–216 | `"Coordination" name=ID (OPEN (coordinationSteps+=CoordinationStep)* C...` |
| `CoordinationStep` | parser | 218–220 | `boundedContext=[BoundedContext] '::' service=[tacticdsl::Service] '::...` |
| `Flow` | parser | 222–226 | `"Flow" name=ID (OPEN (steps+=FlowStep)* CLOSE)?` |
| `FlowStep` | parser | 228–230 | `DomainEventProductionStep \| CommandInvokationStep` |
| `DomainEventProductionStep` | parser | 232–234 | `action=EitherCommandOrOperation ('delegates to' aggregate=[Aggregate]...` |
| `CommandInvokationStep` | parser | 236–238 | `'event' events+=[tacticdsl::DomainEvent] ('+' events+=[tacticdsl::Dom...` |
| `EitherCommandOrOperation` | parser | 240–242 | `('command' command=[tacticdsl::CommandEvent] \| 'operation' operation=...` |
| `EitherCommandOrOperationInvokation` | parser | 244–246 | `CommandInvokation \| OperationInvokation` |
| `CommandInvokation` | parser | 248–250 | `'command' (SingleCommandInvokation \| ConcurrentCommandInvokation \| Ex...` |
| `SingleCommandInvokation` | parser | 252–254 | `commands+=[tacticdsl::CommandEvent]` |
| `ConcurrentCommandInvokation` | parser | 256–258 | `commands+=[tacticdsl::CommandEvent] ('+' commands+=[tacticdsl::Comman...` |
| `ExclusiveAlternativeCommandInvokation` | parser | 260–262 | `commands+=[tacticdsl::CommandEvent] (('X' \| 'x') commands+=[tacticdsl...` |
| `InclusiveAlternativeCommandInvokation` | parser | 264–266 | `commands+=[tacticdsl::CommandEvent] (('O' \| 'o') commands+=[tacticdsl...` |
| `OperationInvokation` | parser | 268–270 | `'operation' (SingleOperationInvokation \| ConcurrentOperationInvokatio...` |
| `SingleOperationInvokation` | parser | 272–274 | `operations+=[tacticdsl::ServiceOperation]` |
| `ConcurrentOperationInvokation` | parser | 276–278 | `operations+=[tacticdsl::ServiceOperation] ('+' operations+=[tacticdsl...` |
| `ExclusiveAlternativeOperationInvokation` | parser | 280–282 | `operations+=[tacticdsl::ServiceOperation] (('X' \| 'x') operations+=[t...` |
| `InclusiveAlternativeOperationInvokation` | parser | 284–286 | `operations+=[tacticdsl::ServiceOperation] (('O' \| 'o') operations+=[t...` |
| `EventProduction` | parser | 288–290 | `SingleEventProduction \| MultipleEventProduction \| ExclusiveAlternativ...` |
| `SingleEventProduction` | parser | 292–294 | `events+=[tacticdsl::DomainEvent]` |
| `MultipleEventProduction` | parser | 296–298 | `events+=[tacticdsl::DomainEvent] ('+' events+=[tacticdsl::DomainEvent])+` |
| `ExclusiveAlternativeEventProduction` | parser | 300–302 | `events+=[tacticdsl::DomainEvent] (('X' \| 'x') events+=[tacticdsl::Dom...` |
| `InclusiveAlternativeEventProduction` | parser | 304–306 | `events+=[tacticdsl::DomainEvent] (('O' \| 'o') events+=[tacticdsl::Dom...` |
| `UserRequirement` | parser | 308–310 | `UseCase \| UserStory` |
| `UseCase` | parser | 312–321 | `'UseCase' name=ID (OPEN (('actor' ('=')? role=STRING)? & ('secondaryA...` |
| `UserStory` | parser | 323–327 | `'UserStory' name=ID ('split by' splittingStory=[UserStory])? (OPEN ((...` |
| `Feature` | parser | 329–331 | `NormalFeature \| StoryFeature` |
| `NormalFeature` | parser | 333–335 | `verb=(UserActivityDefaultVerb \| STRING) (entityArticle='a' \| entityAr...` |
| `StoryFeature` | parser | 337–339 | `'I want to' verb=(UserActivityDefaultVerb \| STRING) (entityArticle='a...` |
| `StoryValuation` | parser | 341–344 | `'and that' promotedValues+=STRING (',' promotedValues+=STRING)* ('is'...` |
| `UserActivityDefaultVerb` | parser | 346–348 | `'create' \| 'read' \| 'update' \| 'delete'` |
| `SculptorModule` | parser | 350–362 | `(doc=STRING)? 'Module' name=ID (OPEN (external?='external')? ('basePa...` |
| `Stakeholders` | parser | 365–371 | `{Stakeholders} 'Stakeholders' ('of' (contexts+=[BoundedContext]) (','...` |
| `AbstractStakeholder` | parser | 373–375 | `StakeholderGroup \| Stakeholder` |
| `StakeholderGroup` | parser | 377–383 | `'StakeholderGroup' name=ID (OPEN ( (stakeholders += Stakeholder)* ) C...` |
| `Stakeholder` | parser | 385–393 | `'Stakeholder' name=ID (OPEN ( ('influence' ('=')? influence=INFLUENCE...` |
| `ValueRegister` | parser | 395–405 | `'ValueRegister' name=ID ('for' context=[BoundedContext])? (OPEN ( (va...` |
| `ValueCluster` | parser | 407–418 | `'ValueCluster' name=ID (OPEN ( (('core' ('=')? coreValue7000 = CoreVa...` |
| `Value` | parser | 420–430 | `'Value' name=ID (OPEN ( (coreValue ?= 'isCore')? & ('demonstrator' ('...` |
| `ValueElicitation` | parser | 434–442 | `('Stakeholder'\|'Stakeholders') stakeholder=[AbstractStakeholder] (OPE...` |
| `ValueEpic` | parser | 445–453 | `'ValueEpic' name=ID (OPEN ( 'As a' stakeholder=[AbstractStakeholder] ...` |
| `ValueNarrative` | parser | 455–464 | `'ValueNarrative' name=ID (OPEN ( 'When the SOI executes' feature=STRI...` |
| `ValueWeigthing` | parser | 466–475 | `'ValueWeigthing' name=ID (OPEN ( 'In the context of the SOI,' 'stakeh...` |
| `Consequence` | parser | 477–479 | `(type='good'\|type='bad'\|type='neutral') consequence=STRING action=Act...` |
| `Action` | parser | 481–483 | `'action' action=STRING type=('ACT'\|'MONITOR'\|STRING)` |
| `UpstreamRole` | enum | 486–488 | `PUBLISHED_LANGUAGE = 'PL' \| OPEN_HOST_SERVICE = 'OHS'` |
| `DownstreamRole` | enum | 490–492 | `ANTICORRUPTION_LAYER = 'ACL' \| CONFORMIST = 'CF'` |
| `ContextMapState` | enum | 494–496 | `UNDEFINED \| AS_IS \| TO_BE` |
| `ContextMapType` | enum | 498–500 | `UNDEFINED \| SYSTEM_LANDSCAPE \| ORGANIZATIONAL` |
| `BoundedContextType` | enum | 502–504 | `UNDEFINED \| FEATURE \| APPLICATION \| SYSTEM \| TEAM` |
| `SubDomainType` | enum | 506–508 | `UNDEFINED \| CORE_DOMAIN \| SUPPORTING_DOMAIN \| GENERIC_SUBDOMAIN` |
| `DownstreamGovernanceRights` | enum | 510–512 | `INFLUENCER \| OPINION_LEADER \| VETO_RIGHT \| DECISION_MAKER \| MONOPOLIST` |
| `KnowledgeLevel` | enum | 514–516 | `META="META" \| CONCRETE="CONCRETE"` |
| `Volatility` | enum | 518–520 | `UNDEFINED \| NORMAL \| RARELY \| OFTEN` |
| `Criticality` | enum | 522–524 | `UNDEFINED \| NORMAL \| HIGH \| LOW` |
| `Similarity` | enum | 526–528 | `UNDEFINED \| NORMAL \| HUGE \| TINY` |
| `Evolution` | enum | 530–532 | `UNDEFINED \| GENESIS \| CUSTOM_BUILT \| PRODUCT \| COMMODITY` |
| `INFLUENCE` | enum | 534–536 | `UNDEFINED \| HIGH \| MEDIUM \| LOW` |
| `INTEREST` | enum | 538–540 | `UNDEFINED \| HIGH \| MEDIUM \| LOW` |
| `PRIORITY` | enum | 542–544 | `UNDEFINED \| HIGH \| MEDIUM \| LOW` |
| `IMPACT` | enum | 546–548 | `UNDEFINED \| HIGH \| MEDIUM \| LOW` |
| `CoreValue` | enum | 550–552 | `UNDEFINED \| AUTONOMY \| CARE \| CONTROL \| FAIRNESS \| INCLUSIVENESS \| IN...` |
| `OPEN` | terminal | 555 | `'{'` |
| `CLOSE` | terminal | 556 | `'}'` |

---

# CML 语法规则索引 — TacticDDDLanguage.xtext

> **自动生成，勿手改**（生成器：`dsl/gen_index.py`，重跑：`python3 dsl/sync.py`）。
> 深度语法检查流程：在本表按规则名定位行区间 → 用 `read` 工具带 `offset`/`limit` 精读该区间；
> 不要下载/解压上游仓库，也不要读临时目录里的副本。

- 语法文件：[`TacticDDDLanguage.xtext`](./TacticDDDLanguage.xtext)（578 行，sha256 `41492434234e62d0...`）
- 上游：[`ContextMapper/context-mapper-dsl`](https://github.com/ContextMapper/context-mapper-dsl) @ `master` commit `995f486a9cde`（2025-07-08）
- 规则数：64（enum 5 · parser 53 · terminal 6）
- 生成日期：2026-10-10

| 规则 | 类型 | 行区间 | 定义首行摘要 |
|------|------|--------|--------------|
| `TacticDDDModel` | parser | 34–35 | `app=TacticDDDApplication` |
| `TacticDDDApplication` | parser | 37–46 | `(doc=STRING)? (("TacticDDDApplication" name=ID "{" "basePackage" "=" ...` |
| `Service` | parser | 48–61 | `(comment=ML_COMMENT)? (doc=STRING)? "Service" name=ID ("{" ( ((gapCla...` |
| `Resource` | parser | 63–74 | `(doc=STRING)? "Resource" name=ID ("{" ( ((gapClass?="gap") \| (noGapCl...` |
| `Consumer` | parser | 76–86 | `(doc=STRING)? "Consumer" name=ID "{" ("hint" "=" hint=STRING)? (depen...` |
| `Subscribe` | parser | 88–90 | `"subscribe" "to" topic=ChannelIdentifier ("eventBus" "=" eventBus=ID)?` |
| `Publish` | parser | 92–94 | `"publish" (("@")?eventType=[Event])? "to" topic=ChannelIdentifier ("e...` |
| `Event` | parser | 96–97 | `DomainEvent \| CommandEvent` |
| `DomainObjectTypedElement` | parser | 99–100 | `ServiceOperation \| RepositoryOperation \| DomainObjectOperation \| Para...` |
| `ServiceOperation` | parser | 102–113 | `(doc=STRING)? (visibility=Visibility)? (returnType=ComplexType\|"void"...` |
| `StateTransition` | parser | 115–117 | `(from+=[EnumValue] (',' from+=[EnumValue])*)? '->' target=StateTransi...` |
| `StateTransitionTarget` | parser | 119–121 | `SingleStateTransitionTarget \| ExclusiveAlternativeStateTransitionTarget` |
| `SingleStateTransitionTarget` | parser | 123–125 | `to+=TargetState` |
| `ExclusiveAlternativeStateTransitionTarget` | parser | 127–129 | `to+=TargetState (('X' \| 'x') to+=TargetState)+` |
| `TargetState` | parser | 131–133 | `value=[EnumValue]((endState?='*'))?` |
| `ServiceOperationDelegate` | parser | 135–136 | `DELEGATE ("@")? delegate=[ServiceRepositoryOption]"."delegateOperatio...` |
| `ServiceRepositoryOption` | parser | 138–139 | `Repository \| Service` |
| `ServiceRepositoryOperationOption` | parser | 141–142 | `RepositoryOperation \| ServiceOperation` |
| `ResourceOperation` | parser | 144–157 | `(doc=STRING)? (visibility=Visibility)? (returnType=ComplexType)? name...` |
| `ResourceOperationDelegate` | parser | 159–160 | `DELEGATE ("@")? delegate=[Service]"."delegateOperation=[ServiceOperat...` |
| `HttpMethod` | enum | 162–163 | `None \| GET="GET" \| POST="POST" \| PUT="PUT" \| DELETE="DELETE"` |
| `RepositoryOperation` | parser | 165–186 | `(doc=STRING)? (visibility=Visibility)? (returnType=ComplexType\|"void"...` |
| `Parameter` | parser | 188–190 | `(doc=STRING)? parameterType=ComplexType name=ID` |
| `ComplexType` | parser | 192–197 | `(type=Type) \| (type=Type"<""@"domainObjectType=[SimpleDomainObject]">...` |
| `SimpleDomainObject` | parser | 199–200 | `BasicType \| Enum \| DomainObject \| DataTransferObject \| Trait` |
| `DomainObject` | parser | 202–203 | `Entity \| ValueObject \| Event` |
| `Entity` | parser | 205–231 | `(comment=ML_COMMENT)? (doc=STRING)? (abstract?="abstract")? "Entity" ...` |
| `ValueObject` | parser | 233–260 | `(comment=ML_COMMENT)? (doc=STRING)? (abstract?="abstract")? "ValueObj...` |
| `DomainEvent` | parser | 262–289 | `(comment=ML_COMMENT)? (doc=STRING)? (abstract?="abstract")? ("DomainE...` |
| `CommandEvent` | parser | 291–318 | `(comment=ML_COMMENT)? (doc=STRING)? (abstract?="abstract")? ("Command...` |
| `Trait` | parser | 320–330 | `(doc=STRING)? "Trait" name=ID ("{" ("package" "=" package=JavaIdentif...` |
| `DomainObjectOperation` | parser | 332–341 | `(doc=STRING)? ("def"\|'*') (abstract?="abstract")? (visibility=Visibil...` |
| `DataTransferObject` | parser | 343–355 | `(comment=ML_COMMENT)? (doc=STRING)? (abstract?="abstract")? "DataTran...` |
| `BasicType` | parser | 357–370 | `(doc=STRING)? "BasicType" name=ID ("with" ("@")?traits+=[Trait])* ("{...` |
| `Attribute` | parser | 372–404 | `(doc=STRING)? (visibility=Visibility)? ((collectionType=CollectionTyp...` |
| `Reference` | parser | 406–430 | `(doc=STRING)? REF (visibility=Visibility)? ((collectionType=Collectio...` |
| `Association` | parser | 432–436 | `(doc=STRING)? ASC (description=STRING)? (("@")?domainObjectType=[Simp...` |
| `DtoAttribute` | parser | 438–467 | `(doc=STRING)? (visibility=Visibility)? (collectionType=CollectionType...` |
| `DtoReference` | parser | 469–482 | `(doc=STRING)? REF (visibility=Visibility)? (collectionType=Collection...` |
| `OppositeHolder` | parser | 484–485 | `OPPOSITE opposite=[Reference]` |
| `Repository` | parser | 487–497 | `(doc=STRING)? "Repository" name=ID ("{" ( ((gapClass?="gap") \| (noGap...` |
| `ServiceDependency` | parser | 499–500 | `('>'\|'inject') ("@"dependency=[Service])` |
| `Dependency` | parser | 502–503 | `('>'\|'inject') (("@"dependency=[ServiceRepositoryOption])\|name=ID)` |
| `Enum` | parser | 505–514 | `(doc=STRING)? "enum" name=ID "{" (("package" "=" package=JavaIdentifi...` |
| `EnumAttribute` | parser | 516–518 | `(doc=STRING)? type=Type name=ID (key?="key")? (";")?` |
| `EnumValue` | parser | 520–522 | `(doc=STRING)? name=ID ("(" parameters+=EnumParameter ("," parameters+...` |
| `EnumParameter` | parser | 524–525 | `((value=STRING) \| (integerValue = INT))` |
| `AnyProperty` | parser | 527–528 | `Property \| DtoProperty` |
| `Property` | parser | 530–531 | `Attribute \| Reference` |
| `DtoProperty` | parser | 533–534 | `DtoAttribute \| DtoReference` |
| `InheritanceType` | enum | 536–537 | `JOINED="JOINED" \| SINGLE_TABLE="SINGLE_TABLE"` |
| `DiscriminatorType` | enum | 539–540 | `STRING="STRING" \| CHAR="CHAR" \| INTEGER="INTEGER"` |
| `Type` | parser | 542–545 | `("String"\|"int"\|"Integer"\|"long"\|"Long"\|"boolean"\|"Boolean"\|"Date"\|"D...` |
| `CollectionType` | enum | 547–548 | `None \| Set="Set" \| List="List" \| Bag="Bag" \| Collection="Collection"` |
| `MAP_COLLECTION_TYPE` | terminal | 550–551 | `"Map"` |
| `Visibility` | enum | 553–554 | `public="public" \| protected="protected" \| private="private" \| package...` |
| `JavaIdentifier` | parser | 556–557 | `(ID ("." ID)*)` |
| `ChannelIdentifier` | parser | 559–560 | `(ID (((".") \| ("/") \| (":")) ID)*)` |
| `ThrowsIdentifier` | parser | 562–563 | `(JavaIdentifier ("," JavaIdentifier)*)` |
| `NOT` | terminal | 565–566 | `('!'\|'not')` |
| `DELEGATE` | terminal | 568–569 | `('=>'\|('delegates to'))` |
| `OPPOSITE` | terminal | 571–572 | `('<->'\|'opposite')` |
| `REF` | terminal | 574–575 | `('-'\|'reference')` |
| `ASC` | terminal | 577–578 | `('--'\|'association')` |
