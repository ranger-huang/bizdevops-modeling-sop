# MDSL 语法规则索引 — APIDescription.xtext

> **自动生成，勿手改**（生成器：`dsl/gen_index.py`，重跑：`python3 dsl/sync.py`）。
> 深度语法检查流程：在本表按规则名定位行区间 → 用 `read` 工具带 `offset`/`limit` 精读该区间；
> 不要下载/解压上游仓库，也不要读临时目录里的副本。

- 语法文件：[`APIDescription.xtext`](./APIDescription.xtext)（967 行，sha256 `8376badbd8e47356...`）
- 上游：[`Microservice-API-Patterns/MDSL-Specification`](https://github.com/Microservice-API-Patterns/MDSL-Specification) @ `master` commit `9da0bac0e613`（2025-01-23）
- 规则数：159（enum 17 · parser 142）
- 生成日期：2026-10-10

| 规则 | 类型 | 行区间 | 定义首行摘要 |
|------|------|--------|--------------|
| `ServiceSpecification` | parser | 30–48 | `'API' 'description' name=ID ('version' svi=SemanticVersioningIdentifi...` |
| `Visibility` | parser | 58 | `'PUBLIC_API' \| 'COMMUNITY_API' \| 'SOLUTION_INTERNAL_API' \| STRING` |
| `DirectionList` | parser | 60–62 | `primaryDirection=Direction ('and' otherDirection=Direction)?` |
| `Direction` | parser | 64 | `'FRONTEND_INTEGRATION' \| 'BACKEND_INTEGRATION' \| STRING` |
| `SemanticVersioningIdentifier` | parser | 66 | `STRING` |
| `DataContract` | parser | 70–75 | `'data' 'type' name=ID ('version' svi=SemanticVersioningIdentifier)? s...` |
| `LinkContract` | parser | 78–84 | `'relation' 'type' name=ID` |
| `EventTypes` | parser | 86–88 | `'event' 'type' events+=EventType (',' events+=EventType)*` |
| `EventType` | parser | 90–94 | `name=ID ( ('version' svi=SemanticVersioningIdentifier)?` |
| `CommandTypes` | parser | 96–98 | `'command' 'type' commands+=CommandType (',' commands+=CommandType)*` |
| `CommandType` | parser | 100–105 | `name=ID ('version' svi=SemanticVersioningIdentifier)? (subject=Elemen...` |
| `ElementStructure` | parser | 110–112 | `pf=ParameterForest \| pt=ParameterTree \| apl=AtomicParameterList \| np=...` |
| `ParameterForest` | parser | 114–117 | `classifier=PatternStereotype? '[' ptl=ParameterTreeList ']'` |
| `ParameterTreeList` | parser | 123–125 | `first=ParameterTree (';' next+=ParameterTree)*` |
| `ParameterTree` | parser | 127–134 | `classifier=PatternStereotype? (name=STRING':')? '{' first=TreeNode ((...` |
| `TreeNode` | parser | 136–138 | `pn=SingleParameterNode \| apl=AtomicParameterList \| children=Parameter...` |
| `SingleParameterNode` | parser | 140–143 | — |
| `GenericParameter` | parser | 145–149 | `name=STRING` |
| `TypeReference` | parser | 158–162 | `classifier=PatternStereotype? (name=STRING':')? (dcref=[DataContract]...` |
| `AtomicParameterList` | parser | 164–169 | `classifier=PatternStereotype? (name=STRING':')? '(' first=AtomicParam...` |
| `AtomicParameter` | parser | 171–175 | `classifier=PatternStereotype? rat=RoleAndType card=Cardinality?` |
| `RoleAndType` | parser | 177–180 | — |
| `DefaultValue` | parser | 183–185 | `'default' 'is' default=STRING` |
| `PatternStereotype` | parser | 187–189 | `'<<' (pattern=MapPattern \| eip=EipPattern \| name=ID) '>>'` |
| `EipPattern` | parser | 191–193 | `'Command_Message' \| 'Document_Message' \| 'Event_Message'` |
| `MapPattern` | parser | 195–201 | `'API_Key' \| 'Context_Representation' \| 'Error_Report' \| 'Request_Bund...` |
| `ParameterRole` | parser | 203–213 | `'D'` |
| `BasicDataType` | parser | 221–224 | — |
| `Cardinality` | parser | 226–228 | `zeroOrOne='?' \| zeroOrMore='*' \| atLeastOne='+' \| exactlyOne='!'` |
| `EndpointContract` | parser | 233–242 | `'endpoint' 'type' name=ID ('version' svi=SemanticVersioningIdentifier)?` |
| `ResourceRole` | parser | 246–248 | `'PROCESSING_RESOURCE' \| 'INFORMATION_HOLDER_RESOURCE' \| 'OPERATIONAL_...` |
| `Event` | parser | 250–254 | `'event' type=[EventType] ('version' svi=SemanticVersioningIdentifier)?` |
| `Operation` | parser | 256–272 | `'operation' name=ID ('version' svi=SemanticVersioningIdentifier)? ('w...` |
| `StateTransition` | parser | 276–278 | `'from' from=STRING 'to' to=STRING` |
| `RelationshipLink` | parser | 280–282 | `name=STRING ':' lcref=[LinkContract]` |
| `StatusReports` | parser | 284–286 | `reportList+=StatusReport+` |
| `StatusReport` | parser | 288–290 | `('status' \| 'error' \| 'analytics') name=ID reportData=ElementStructure?` |
| `SecurityPolicies` | parser | 292–294 | `policyList+=SecurityPolicy+` |
| `SecurityPolicy` | parser | 296–298 | `'policy' name=ID securityObject=ElementStructure?` |
| `OperationResponsibility` | parser | 303 | `cf='COMPUTATION_FUNCTION' \| sco='STATE_CREATION_OPERATION' \| ro='RETR...` |
| `MessageExchangePattern` | parser | 305 | `'ONE_WAY' \| 'REQUEST_REPLY' \| 'NOTIFICATION' \| STRING` |
| `DataTransferRepresentation` | parser | 308–312 | `('headers' headers=ElementStructure)? 'payload' payload=ElementStructure` |
| `TypeSystem` | parser | 314–316 | `'MAP_TYPE' \| 'JOLIE_TYPE' \| 'JSON_SCHEMA' \| 'XML_SCHEMA' \|'PROTOCOL_B...` |
| `ChannelContract` | parser | 321–327 | `'channel' name=ID` |
| `ChannelType` | enum | 329–331 | `POINT_TO_POINT \| PUBLISH_SUBSCRIBE \| DATA_TYPE \| INVALID_MESSAGE \| DE...` |
| `DeliveryGuarantee` | enum | 334–336 | `UNKNOWN \| AT_LEAST_ONCE \| AT_MOST_ONCE \| EXACTLY_ONCE` |
| `BindingValue` | parser | 338–340 | `{BindingValue} str=STRING \| {BindingValue} number=INT \| bool=('true' ...` |
| `BindingParameter` | parser | 342–344 | `name=STRING ':' value=(BindingValue \| BindingParams)` |
| `BindingParams` | parser | 346–351 | `'{' params+=BindingParameter (',' params+=BindingParameter)* '}'` |
| `BasicParameterWithDescription` | parser | 353–355 | `paramName=ID ':' type=BasicDataType (',' description=STRING)?` |
| `ChannelPathWithParams` | parser | 357–363 | `'path' path=STRING ('with' params+=BasicParameterWithDescription (','...` |
| `RequestReplyChannel` | parser | 365–369 | `request=RequestChannel reply=ReplyChannel` |
| `RequestChannel` | parser | 371–378 | `'request' 'message' name=ID (('description' description=STRING)? & 'o...` |
| `ReplyChannel` | parser | 380–387 | `'reply' 'message' name=ID (('description' description=STRING)? & 'on'...` |
| `Payload` | parser | 389–392 | `schema=DataTransferRepresentation ('as' messageType=MessageType)?` |
| `OneWayChannel` | parser | 395–401 | `(('description' description=STRING)? & 'on' path=ChannelPathWithParam...` |
| `Message` | parser | 403–407 | `'message' name=ID ('description' description=STRING)? (deliveringPayl...` |
| `WhereClauses` | parser | 409–413 | `MessageExpireWhereClause \| SequenceIdWhereClause \| CorrelationIdWhere...` |
| `MessageExpireWhereClause` | parser | 415–417 | `'MESSAGE_EXPIRES' 'in' messageExpire=INT messageExpireUnit=MessageExp...` |
| `SequenceIdWhereClause` | parser | 419–421 | `'SEQUENCE_ID' 'is' expression=STRING` |
| `CorrelationIdWhereClause` | parser | 423–425 | `'CORRELATION_ID' 'is' source=STRING` |
| `MessageExpireUnit` | enum | 427–429 | `s \| m` |
| `MessageType` | enum | 431–433 | `COMMAND_MESSAGE \| EVENT_MESSAGE \| DOCUMENT_MESSAGE` |
| `Provider` | parser | 438–445 | `'API' 'provider'` |
| `EndpointList` | parser | 447–450 | `'offers' contract=[EndpointContract]` |
| `EndpointInstance` | parser | 452–457 | `'at' 'endpoint' 'location' location=STRING pb+=TechnologyBinding+` |
| `MessageBroker` | parser | 461–466 | `'message' 'broker' name=ID ('description' description=STRING)? ('expo...` |
| `AsyncEndpoint` | parser | 468–474 | `contracts+=[ChannelContract] (',' contracts+=[ChannelContract])* 'at'...` |
| `TechnologyBinding` | parser | 479–481 | `'via' 'protocol' protBinding=ProtocolBinding` |
| `ProtocolBinding` | parser | 483–485 | `http=HTTPBinding \| java=JavaBinding \| grpc=GRPCBinding \| other=OtherB...` |
| `HTTPBinding` | parser | 487–489 | `http='HTTP' ('static'\|'dynamic')? 'binding' eb+=HTTPResourceBinding+` |
| `HTTPResourceBinding` | parser | 491–494 | — |
| `CustomMediaType` | parser | 496–499 | — |
| `HTTPTypeBinding` | parser | 501–506 | `CustomMediaType \| 'data' 'type' dt=[DataContract] 'to' (mt+=[CustomMe...` |
| `StandardMediaType` | parser | 508–510 | `ianaName=STRING` |
| `HypermediaLink` | parser | 512–515 | — |
| `HTTPOperationBinding` | parser | 517–525 | — |
| `MediaTypeList` | parser | 527–529 | `(cmt+=[CustomMediaType] \| smt+=StandardMediaType)+` |
| `HTTPGlobalParameterBinding` | parser | 531–533 | `'all' 'elements' 'realized' 'as' parameterMapping=HTTPParameter 'para...` |
| `HTTPParameterBinding` | parser | 536–539 | `'element' (boundParameter=STRING) 'realized' 'as' parameterMapping=HT...` |
| `HTTPVerb` | enum | 541–542 | `GET \| PUT \| POST \| PATCH \| DELETE \| HEAD \| OPTIONS \| TRACE` |
| `HTTPParameter` | enum | 544–545 | `QUERY \| HEADER \| PATH \| COOKIE \| BODY` |
| `ReportBinding` | parser | 547–549 | `'report' name=ID 'realized' 'as' httpStatusCode=INT ('with' details=S...` |
| `SecurityBinding` | parser | 551–554 | — |
| `OASSecurity` | enum | 556 | `BASIC_AUTHENTICATION \| JWT \| API_KEY \| OAUTH_IMPLICIT \| OAUTH_FLOW \| ...` |
| `JavaBinding` | parser | 559–562 | — |
| `JavaOperationBinding` | parser | 564–567 | `'operation' boundOperation=ID 'to' method=STRING` |
| `JavaParameterBinding` | parser | 569–571 | `'element' (boundParameter=ID\|any='*') 'realized' 'as' pm=JavaParamete...` |
| `JavaParameter` | enum | 573 | `byte \| short \| int \| long \| float \| double \| boolean \| char \| String` |
| `GRPCBinding` | parser | 576–578 | `gRPC='gRPC' (binding='binding' opsBinding+=GRPCOperationBinding+)?` |
| `GRPCOperationBinding` | parser | 580–582 | `'operation' boundOperation=ID ('to' method=STRING)? ('as' so=Streamin...` |
| `StreamingOption` | enum | 584–586 | `client \| server \| bidirectional` |
| `OtherBinding` | parser | 589–591 | `soap='SOAP_HTTP' \| jsonrpc='JSON-RPC' \| avro='Avro_RPC' \| thrift='Thr...` |
| `SLA` | parser | 596–598 | `'SLA' (builtin=InternalSLA \| external=[SLATemplate])` |
| `SLATemplate` | parser | 600–604 | `'SLA' 'template' name=ID slas+=InternalSLA` |
| `InternalSLA` | parser | 606–613 | `('type' type=SLAType)?` |
| `RatePlan` | parser | 616–618 | `'rate' 'plan' ('FREEMIUM' \| "SUBSCRIPTION" \| "USAGE_BASED")` |
| `RateLimit` | parser | 620–622 | `'rate' 'limit' (none='NONE' \| "MAX_CALLS" callRate=SimpleMeasurement ...` |
| `SLAType` | enum | 624–626 | `NONE \| IMPLICIT \| INFORMAL \| QUALITATIVE \| QUANTITATIVE` |
| `SLO` | parser | 628–634 | `'objective' name=ID qualityGoal=STRING` |
| `Measurement` | parser | 636–638 | `sm=SimpleMeasurement \| lz=LandingZone` |
| `SimpleMeasurement` | parser | 642–645 | `value=INT unitOfMeasure=('hours' \| 'minutes' \| 'seconds' \| 'MB' \| 'GB...` |
| `LandingZone` | parser | 647–651 | `'minimal' s=SimpleMeasurement 'target' t=SimpleMeasurement ('optimal'...` |
| `EvolutionStrategy` | enum | 655–658 | `ETERNAL_LIFETIME \| LIMITED_GUARANTEED_LIFETIME \| TWO_IN_PRODUCTION \| ...` |
| `Client` | parser | 663–667 | `'API' 'client' name=ID ('version' svi=SemanticVersioningIdentifier)? ...` |
| `Consumption` | parser | 669–675 | `'consumes' contract=[EndpointContract]` |
| `ClientBinding` | parser | 677–679 | `http='HTTP' \| grpc='gRPC' \| java='Java' \| OtherBinding` |
| `MessageEndpoint` | parser | 683–693 | `'message' 'endpoint' name=ID ('of' 'type' types+=MessageEndpointType ...` |
| `MessageEndpointType` | enum | 695–697 | `TRANSACTIONAL_CLIENT \| POLLING_CONSUMER \| EVENT_DRIVEN_CONSUMER \| IDE...` |
| `AsyncConsumptionFromBroker` | parser | 699–703 | `'from' broker=[MessageBroker] ':' channels+=AsyncConsumptionNoProtoco...` |
| `Channel` | parser | 706–709 | `ChannelContract \| RequestChannel \| ReplyChannel` |
| `AsyncConsumptionNoProtocolBinding` | parser | 711–714 | `(channel=[Channel]) (where=WhereConstruct)?` |
| `AsyncConsumptionWithProtocolBinding` | parser | 716–720 | `(channel=[Channel]) (where=WhereConstruct)? (binding+=ProtocolBinding)?` |
| `WhereConstruct` | parser | 722–726 | `{WhereConstruct} 'where' (whereClauses+=ConsumptionWhereClauses (',' ...` |
| `ConsumptionWhereClauses` | parser | 728–730 | `'consumed' 'if' leftExp=STRING op=BinaryOperator rightExpr=IfExpr` |
| `IfExpr` | parser | 732–734 | `STRING \| INT` |
| `BinaryOperator` | parser | 735–737 | `'==' \| '!=' \| '>' \| '<' \| '<=' \| '>='` |
| `Gateway` | parser | 741–746 | `('API' 'gateway' ) name=ID` |
| `Gate` | parser | 748–753 | `( 'offers' ) upstreamContract+=[EndpointContract]+` |
| `DataTransformation` | parser | 755–757 | `'from' indc=[DataContract] 'to' outdc=[DataContract]` |
| `ProviderImplementation` | parser | 762–769 | `'API' 'provider' 'implementation' name=ID 'realizes' upstreamBinding=...` |
| `ImplementationTechnology` | enum | 774–775 | `PlainJava /* \| SpringMVC \| vlingo */ \| STRING` |
| `IntegrationScenario` | parser | 780–784 | `'scenario' name=ID ('type' type=ScenarioType)? ('version' svi=Semanti...` |
| `ScenarioType` | enum | 786–788 | `BUSINESS_API \| FRONTEND_INTEGRATION_SCENARIO \| BACKEND_INTEGRATION_SC...` |
| `IntegrationStory` | parser | 790–801 | `('story' name=ID ('version' svi=SemanticVersioningIdentifier)? ('type...` |
| `Action` | parser | 803–805 | `plainAction=STRING \| keyword=ActionKeyword ('a'\|'an'\|'the')? target=S...` |
| `ActionKeyword` | enum | 807–810 | `CRUD \| CRUDSF \| CQRS` |
| `StoryObject` | parser | 813–815 | `('with'\|'against'\|'for'\|'at'\|'in'\|'to'\|'on'\|'from'\|'and'\|'into'\|'with...` |
| `StoryType` | enum | 817–819 | `USER_STORY \| JOB_STORY \| TEST_CASE \| API_MOCK` |
| `RelatedStories` | parser | 821–823 | `'follows' related+=[IntegrationStory] \| 'alternative' 'to' related+=[...` |
| `Orchestration` | parser | 827–833 | `'flow' name=ID ('version' svi=SemanticVersioningIdentifier)? ('realiz...` |
| `FlowType` | enum | 835–837 | `APPLICATION_FLOW \| INTEGRATION_FLOW /* EIP */ \| SERVICE_ORCHESTRATION...` |
| `OrchestrationBinding` | parser | 841–845 | `'binding' /* 'flow' */ 'to' (eptb+=EndpointTypeBinding\|cb+=ChannelBin...` |
| `EndpointTypeBinding` | parser | 847–849 | `'endpoint' 'type' epcs+=[EndpointContract] stepBindings+=StepToEndpoi...` |
| `ChannelBinding` | parser | 851–853 | `'channel' 'type' channels+=[ChannelContract] stepBindings+=StepToChan...` |
| `FlowTechnology` | parser | 855–857 | `'APACHE_CAMEL_ROUTE' \| 'SPRING_INTEGRATION_FLOW' \| 'BPMN_PROCESS' \| '...` |
| `StepToEndpointBinding` | parser | 859–861 | `eob=EventToOperationBinding \| cob=CommandToOperationBinding` |
| `StepToChannelBinding` | parser | 863–865 | `emb=EventToMessageBinding \| cmb=CommandToMessageBinding` |
| `EventToOperationBinding` | parser | 867–870 | `'event' event=[EventType] 'to' 'operation' operation=ID` |
| `CommandToOperationBinding` | parser | 872–875 | `'command' command=[CommandType] 'to' 'operation' operation=ID` |
| `EventToMessageBinding` | parser | 877–880 | `'event' event=[EventType] 'to' 'message' requesReplyChannelMessage=ID` |
| `CommandToMessageBinding` | parser | 882–885 | `'command' command=[CommandType] 'to' 'message' oneWayChannelMsg=ID` |
| `FlowStep` | parser | 889–891 | `depStep=DomainEventProductionStep \| cisStep=CommandInvokationStep \| e...` |
| `CombinedInvocationStep` | parser | 895–897 | `cisStep=CommandInvokationStep ('emits'\|'emit') ('event'\|'events') eve...` |
| `DomainEventProductionStep` | parser | 899–903 | — |
| `CommandInvokationStep` | parser | 905–908 | — |
| `EitherCommandOrOperation` | parser | 911–913 | `('command' command=[CommandType] /* \| 'operation' operation=ServiceOp...` |
| `EitherCommandOrOperationInvokation` | parser | 915–917 | `(('command'\|'commands') ci=CommandInvokation) \| ('flow' spi=SubProces...` |
| `SubProcessInvocation` | parser | 919–922 | — |
| `CommandInvokation` | parser | 924–927 | — |
| `SingleCommandInvokation` | parser | 929–931 | `commands+=[CommandType]` |
| `ConcurrentCommandInvokation` | parser | 933–935 | `commands+=[CommandType] (('+' \| 'and') commands+=[CommandType])+` |
| `ExclusiveAlternativeCommandInvokation` | parser | 937–939 | `commands+=[CommandType] (('x' \| 'X' \| 'xor' \| 'alternatively') comman...` |
| `InclusiveAlternativeCommandInvokation` | parser | 941–943 | `commands+=[CommandType] (('o' \| 'O' \| 'or') commands+=[CommandType])+` |
| `EventProduction` | parser | 947–949 | `sep=SingleEventProduction \| mep=MultipleEventProduction \| eaep=Exclus...` |
| `SingleEventProduction` | parser | 951–953 | `events+=[EventType]` |
| `MultipleEventProduction` | parser | 955–957 | `events+=[EventType] (('+' \| 'and' ) events+=[EventType])+` |
| `ExclusiveAlternativeEventProduction` | parser | 959–961 | `events+=[EventType] (('x' \| 'X' \| 'xor' \| 'alternatively') events+=[E...` |
| `InclusiveAlternativeEventProduction` | parser | 963–965 | `events+=[EventType] (('o' \| 'O' \| 'or') events+=[EventType])+` |
