<!-- markdownlint-disable-file -->

# ClinicalTrials.gov 靶点字段与检索语义核验

访问日期：2026-08-21

研究状态：Complete

## 研究问题

* ClinicalTrials.gov API v2 是否存在独立或可等价使用的分子靶点结构化字段
* `target`、`mechanism`、`intervention`、`keywords`、MeSH、`briefSummary` 与 `detailedDescription` 分别位于何处，是否为必填，以及可通过哪些查询参数检索
* 仅有靶点字符串和同义词时会系统性漏掉哪些登记
* `query.intr`、`query.term` 与 `AREA[...]` 查询能否弥补这些漏召回
* AACT 或 ClinicalTrials.gov browse terms 是否增加 target-to-intervention 语义
* 靶点到干预映射是召回相关登记的必要条件、充分条件，还是两者都不是

## 证据分类

* 已验证事实：由官方 OpenAPI、Data API 文档、PRS Data Element Definitions、官方复杂查询指南或可重复官方端点响应直接支持
* 条件性事实：在特定端点版本、查询表达式、样本或访问日期下实测成立，但官方资料未承诺一般性
* 推断：由结构、检索结果或领域语义推导，尚无官方契约直接声明

## 执行摘要

截至 2026-08-21，ClinicalTrials.gov API v2 的公开 OpenAPI、Study Data Structure 和 PRS Data Element Definitions 中均没有独立的 molecular target、gene target、protein target 或 mechanism-of-action 结构化字段，也没有可与其等价使用的字段。`DesignPrimaryPurpose=BASIC_SCIENCE` 只说明研究主要目的可能是考察基本作用机制，不提供机制内容、靶点实体或 intervention-to-target 关系，不能作为等价字段。

可用数据分为三层：

* PRS 提交的 protocol 文本和干预结构，包括 intervention name/type/description/other names、keywords、brief summary 和 detailed description
* ClinicalTrials.gov 派生的 condition/intervention browse 数据，包括 MeSH、ancestor、browse leaf 和 branch
* 搜索索引定义的复合 Search Areas，例如 `InterventionSearch` 和 `BasicSearch`，它们把多个字段按权重合并检索

这些层都不编码“某 intervention 作用于某 molecular target”的关系。`query.intr`、`query.term` 和 `AREA[...]` 可以扩大或定向文本召回，但不能替代外部药物-靶点映射，也不能证明机制相关性。

若输入只有 target 字符串及 target 同义词，系统会系统性漏掉所有只登记 intervention 名称、研究代码、商品名或通用名而未在可搜索字段中写出 target 的记录。反向地，宽泛文本搜索会召回仅在背景、伴随用药、比较药、排除标准或 biomarker/outcome 中提到 target 的无关记录。

因此，target-to-intervention 映射作为普遍逻辑条件是“既非必要也非充分”：显式写出 target 的相关登记无需映射即可命中，target-centric observational/biomarker/genetic studies 也可能没有可映射治疗 intervention；而仅知道某药作用于该 target，仍不能证明该药在某登记中承担目标机制、而非对照、背景治疗、排除项或非目标用途。工程上，外部映射是实现高召回 target-centric 检索的必要组成部分，但必须与 trial-level 文本、arm/intervention 角色、condition 和人工或模型相关性判定结合，不能单独作为充分判据。

## 字段与检索矩阵

以下“PRS 必填性”来自官方 Protocol Registration Data Element Definitions。以下“API 必填性”是独立维度：v2 OpenAPI 对 `Study`、`ProtocolSection`、`DescriptionModule`、`ConditionsModule`、`ArmsInterventionsModule`、`Intervention` 和 `BrowseModule` 未声明相关属性为 `required`，所以 API 客户端必须允许字段缺失，即使当前 PRS 规则要求新登记提交该字段。

| 概念 | API v2 JSON 路径 | PRS 提交要求 | API schema 要求 | 默认查询入口 | 精确字段查询 | 语义边界 |
|---|---|---|---|---|---|---|
| molecular target | 无独立路径；字符串可能散落于 title、summary、description、keywords、outcomes、eligibility 等自由文本 | 无该数据元素或填写要求 | 不存在该属性 | 视字符串所在字段，可由 `query.term` 或 `query.intr` 覆盖一部分 | `AREA[具体字段]` | 只能从文本命中或外部映射推断 |
| mechanism of action | 无独立路径；机制描述可能散落于自由文本 | 无独立数据元素或填写要求 | 不存在该属性 | 视字符串所在字段，可由 `query.term` 或 `query.intr` 覆盖一部分 | `AREA[具体字段]` | 没有受控 mechanism entity 或 relation |
| basic-science purpose | `protocolSection.designModule.designInfo.primaryPurpose` | 干预性研究且 Study Start Date 在 2017-01-18 或以后时必填；可选值之一是 Basic Science | 可缺失 | `query.term` | `AREA[DesignPrimaryPurpose]` | 只表示主要研究目的可能考察 basic mechanism，不含具体 target 或 mechanism，不能等价使用 |
| intervention 集合 | `protocolSection.armsInterventionsModule.interventions[]` | 干预性研究至少一项必填；观察性研究仅在存在 intervention/exposure of interest 时填写 | 可缺失 | `query.intr`、`query.term` | `AREA[InterventionName]`、`AREA[InterventionDescription]` 等 | 结构化的是 intervention 实体及 arm label，不是 target 关系 |
| intervention type | `...interventions[].type` | 每项 intervention 必填 | 可缺失 | `query.intr`、`query.term` | `AREA[InterventionType]` | 粗粒度类型枚举，不编码药理靶点 |
| intervention name | `...interventions[].name` | 每项 intervention 必填；应使用非专有名，如无则用描述名或 identifier | 可缺失 | `query.intr`、`query.term` | `AREA[InterventionName]` | 可为药名、研究代码、程序、行为、器械等 |
| other intervention names | `...interventions[].otherNames[]` | 如有公开使用过的其他名或 alias 则条件必填 | 可缺失 | `query.intr`、`query.term` | `AREA[InterventionOtherName]` | 提高 intervention 名称召回，不提供 target |
| intervention description | `...interventions[].description` | `*§`，Study Start Date 在 2017-01-18 或以后时必填 | 可缺失 | `query.intr`、`query.term` | `AREA[InterventionDescription]` | 可能含给药详情或机制文本，但定义只要求足以区分相似 intervention |
| keywords | `protocolSection.conditionsModule.keywords[]` | 无符号，ClinicalTrials.gov 可选 | 可缺失 | `query.intr`、`query.cond`、`query.term` | `AREA[Keyword]` | 提交者自由文本，官方建议适当使用 MeSH；不保证 target 或机制 |
| brief summary | `protocolSection.descriptionModule.briefSummary` | `*`，必填 | 可缺失 | `query.term` 的 `BasicSearch` | `AREA[BriefSummary]` | `query.intr` 不搜索该字段 |
| detailed description | `protocolSection.descriptionModule.detailedDescription` | 无符号，ClinicalTrials.gov 可选 | 可缺失 | 不在 `BasicSearch` 或 `InterventionSearch` | `AREA[DetailedDescription]` | plain `query.term=<target>` 与 `query.intr=<target>` 都可能漏掉只在这里出现的 target |
| intervention MeSH | `derivedSection.interventionBrowseModule.meshes[].{id,term}` | 非 PRS 提交元素，是派生 browse 数据 | 可缺失 | `query.intr`、`query.term` | `AREA[InterventionMeshTerm]` | study-level derived term，不绑定到具体 `interventions[]` 项，也不是 target relation |
| intervention ancestor | `derivedSection.interventionBrowseModule.ancestors[].{id,term}` | 非 PRS 提交元素 | 可缺失 | `query.intr`、`query.term` | `AREA[InterventionAncestorTerm]` | 上位 browse 词，不等于 molecular target ontology |
| condition MeSH/ancestor | `derivedSection.conditionBrowseModule.meshes[]`、`ancestors[]` | 非 PRS 提交元素 | 可缺失 | `query.cond`、`query.term` | `AREA[ConditionMeshTerm]`、`AREA[ConditionAncestorTerm]` | 描述疾病或研究焦点层级，不建立 target-to-intervention 关系 |
| browse leaf/branch | `derivedSection.interventionBrowseModule.browseLeaves[]`、`browseBranches[]` | 非 PRS 提交元素 | 可缺失 | 无单独高级参数；可按 study structure 字段用 `AREA` | 对应 study structure field | 用于浏览层级；OpenAPI 对象只有名称、ID、as-found、relevance 或 branch 名称/缩写，无 intervention ID 或 target ID |

### Search Areas 的相关字段

官方 Search Areas 页面说明 Search Area 可以是一个字段，也可以是多个有权重字段的组合，并标记哪些文本字段产生 synonyms。

`InterventionSearch` 是 `query.intr` 的默认范围，共 12 个字段：

1. `InterventionName`
2. `InterventionType`
3. `ArmGroupType`
4. `InterventionOtherName`
5. `BriefTitle`
6. `OfficialTitle`
7. `ArmGroupLabel`
8. `InterventionMeshTerm`
9. `Keyword`
10. `InterventionAncestorTerm`
11. `InterventionDescription`
12. `ArmGroupDescription`

`BasicSearch` 是 `query.term` 的默认范围，共 57 个字段。与本研究直接相关的字段包括 `InterventionName`、`InterventionOtherName`、`Condition`、`Keyword`、`BriefSummary`、`InterventionDescription`、`ArmGroupDescription`、`InterventionMeshTerm`、`ConditionMeshTerm`、`InterventionAncestorTerm`、`ConditionAncestorTerm`、titles 和 outcome fields。其官方字段表不含 `DetailedDescription` 或 `EligibilityCriteria`。

`ConditionSearch` 是 `query.cond` 的默认范围，共 7 个字段：`Condition`、`BriefTitle`、`OfficialTitle`、`ConditionMeshTerm`、`ConditionAncestorTerm`、`Keyword` 和 `NCTId`。它可能因 keywords 或 title 命中 target 字符串，但不是 target 查询入口。

## 官方规范证据

### API 版本与 OpenAPI

访问 `https://clinicaltrials.gov/api/v2/version` 于 2026-08-21 返回：

```json
{"apiVersion":"2.0.5","dataTimestamp":"2026-08-20T09:00:05"}
```

同日下载的官方 OpenAPI `https://clinicaltrials.gov/api/oas/v2` 为 2,836 行、80,983 bytes，SHA-256 为 `ba31adaea67e6bb09ff77af5c0c11daf36d5aff7f5d6cbed89f0aab04b297aea`。对全部 schema property 名进行大小写不敏感扫描，未发现 `target`、`targets`、`mechanism` 或 `mechanisms` 属性；存在的 `targetDuration` 是 patient registry 的目标随访时长，与 molecular target 无关。

OpenAPI 明确把以下参数都声明为可选字符串，并使用 Essie expression syntax：

* `query.intr`：Intervention / treatment，默认 `InterventionSearch`
* `query.term`：Other terms，默认 `BasicSearch`
* `query.cond`：Conditions or disease，默认 `ConditionSearch`

### PRS Data Element Definitions

官方页面先定义符号：`*` 为 required，`*§` 为 Study Start Date 在 2017-01-18 或以后时 required，`[*]` 为 conditionally required，无符号为 ClinicalTrials.gov optional。

已验证定义：

* `Brief Summary *`：面向公众的简短研究描述，含研究假设简述，最多 5,000 字符
* `Detailed Description`：可选的扩展技术描述，最多 32,000 字符
* `Keywords`：可选；描述 protocol 的词或短语，帮助用户检索，建议适当使用 MeSH
* `Interventions *`：干预性研究至少一项；观察性研究填写 intervention/exposure of interest（如有）
* `Intervention Type *`：每项干预的通用类型
* `Intervention Name(s) *`：非专有名优先，否则使用描述名或 identifier
* `Other Intervention Name(s) [*]`：如有公开使用的 current/former names、brand names 或 serial numbers 则填写
* `Intervention Description *§`：公开可用且足以区分相似干预的详情；药物示例是剂型、剂量、频率和疗程

这些定义没有要求提交 molecular target 或 mechanism of action。

### 复杂查询与同义词扩展

官方复杂查询指南（页面标注最后更新 2026-02-09）说明：

* search term 必须作为 study record 的值出现；operator 只改变词如何被解释、限定或排序
* `AREA[SearchAreaOrField]` 指定 Search Area，或直接指定 Study Data Structure 的任意字段
* `EXPANSION[Concept]` 使用 UMLS synonyms
* `EXPANSION[Relaxation]` 在 Concept 基础上放宽多词邻接，默认未显式指定 `EXPANSION` 时使用该模式
* `EXPANSION[Lossy]` 还允许缺失部分词，召回更宽但精度更低
* `COVERAGE` 控制 full/start/end/contains 匹配范围

因此，ClinicalTrials.gov 的 synonyms 是搜索词扩展，而不是 intervention-to-target 知识图谱。若 target 未以 target 名、同义词或 UMLS 可扩展概念出现在所选字段中，扩展不会凭 intervention 名推导 target。

### AACT 与 browse terms

AACT 官方首页说明其内容每日从 ClinicalTrials.gov 下载并加载到关系数据库。AACT schema 页面说明它展示 ClinicalTrials.gov 数据如何存储，并将每列映射回 ClinicalTrials.gov data point。

AACT 官方数据字典在 2026-08-21 的检索结果：

* `intervention` 命中 `interventions`、`intervention_other_names`、`design_group_interventions` 和 `browse_interventions`
* `browse_interventions` 只有 `id`、`nct_id`、`mesh_term`、`downcase_mesh_term` 和 `mesh_type`；它把 ClinicalTrials.gov 的 intervention MeSH heading/ancestor browse terms 关系化，`mesh_type` 用于区分类型
* `target` 仅命中 `studies.target_duration`，其含义是观察性 patient registry 的目标随访时长
* `mechanism` 和 `protein` 在数据字典中零命中
* `gene` 的命中来自普通英文描述（例如 “internally generated”），不是 gene-target 列

AACT 增加的是关系化表结构和 `design_group_interventions` 的 arm/group-to-intervention 连接，不是 molecular target-to-intervention 连接。ClinicalTrials.gov 的 `interventionBrowseModule` 同样位于 study-level `derivedSection`，没有可连接到某个 `interventions[].id` 的键；其 MeSH/ancestor/leaf/branch 对象也没有 target relation type。

## 已验证事实与推断账本

| ID | 结论 | 状态 | 证据 |
|---|---|---|---|
| F1 | API v2 OpenAPI 没有 molecular target 或 mechanism 属性 | 已验证事实 | 全量 OpenAPI property 扫描；Study Data Structure；PRS definitions |
| F2 | `targetDuration` 不是 molecular target，而是 patient registry follow-up duration | 已验证事实 | OpenAPI `DesignModule.targetDuration`；PRS Target Follow-Up Duration |
| F3 | PRS 的 Brief Summary 必填，Detailed Description 和 Keywords 可选，intervention 字段按研究类型和日期条件必填 | 已验证事实 | PRS 符号表与各数据元素定义 |
| F4 | OpenAPI 不把相关返回属性声明为 required，客户端必须接受缺失 | 已验证事实 | OpenAPI schema 的 `Study`、module 和 `Intervention` 定义 |
| F5 | `query.intr` 搜 12 个 InterventionSearch 字段；plain `query.term` 搜 57 个 BasicSearch 字段；BasicSearch 不含 Detailed Description 或 Eligibility Criteria | 已验证事实 | 官方 Search Areas 字段表 |
| F6 | `AREA` 可指定 Search Area 或 Study Data Structure 中任意字段；Concept expansion 使用 UMLS，但不会从 intervention 名推导未写出的 target | 前半为已验证事实，后半由官方语义和端点反例共同验证 | 官方复杂查询指南；NCT06275724 单条零命中验证 |
| F7 | AACT 不含 target/mechanism/intervention-target schema；其 browse/intervention 表映射 ClinicalTrials.gov 数据 | 已验证事实（限 2026-08-21 公布的数据字典） | AACT provenance、schema 与 data dictionary 查询 |
| F8 | NCT06275724 的完整 JSON 不含 PCSK9 官方名或别名，但 intervention 为 inclisiran，且 target synonym queries 返回零条 | 已验证事实（单条反例） | ClinicalTrials.gov 单条响应、`filter.ids` 查询、HGNC synonym set |
| F9 | ChEMBL 把 inclisiran 标为 PCSK9 mRNA RNAi inhibitor | 已验证外部药理事实 | ChEMBL mechanism 与 target endpoints |
| I1 | 只有 target 字符串会系统性漏掉药名或代码名登记、历史稀疏记录和非干预性 target studies | 高置信推断；inclisiran 类别有直接反例，其余需金样本量化 | PRS 可选性、Search Areas 覆盖、NCT06275724 |
| I2 | target-to-intervention mapping 作为普遍逻辑条件既非必要也非充分，但对高召回工程流程是必要组成部分 | 设计推断 | 显式 target 命中、无 intervention 的 target studies、映射角色歧义和 false-positive 反例 |

## 最小可重复端点验证

所有以下请求均为只读 `GET`，访问日期为 2026-08-21，服务数据时间戳为 2026-08-20T09:00:05。计数会随数据库更新变化，语义和相对差异比绝对值更重要。

### PCSK9 查询范围对比

```http
GET https://clinicaltrials.gov/api/v2/studies?query.intr=EXPANSION%5BNone%5DPCSK9&pageSize=1&countTotal=true&fields=NCTId&format=json
GET https://clinicaltrials.gov/api/v2/studies?query.term=EXPANSION%5BNone%5DPCSK9&pageSize=1&countTotal=true&fields=NCTId&format=json
GET https://clinicaltrials.gov/api/v2/studies?query.term=AREA%5BDetailedDescription%5DEXPANSION%5BNone%5DPCSK9&pageSize=1&countTotal=true&fields=NCTId&format=json
GET https://clinicaltrials.gov/api/v2/studies?query.term=AREA%5BInterventionName%5DEXPANSION%5BNone%5DPCSK9&pageSize=1&countTotal=true&fields=NCTId&format=json
```

使用 `EXPANSION[None]` 的观察 `totalCount` 分别为 264、436、145 和 41。使用默认 `EXPANSION[Relaxation]` 时，同四类查询的计数为 269、439、145 和 43。两个模式下的相对关系一致：`query.term`、`query.intr` 与单字段 `AREA` 不是等价检索，同义词/松弛扩展只解释少量增量，不能解释主要覆盖差异。

### Detailed Description 能补到 `query.intr` 漏召回

```http
GET https://clinicaltrials.gov/api/v2/studies?query.term=AREA%5BDetailedDescription%5DPCSK9%20AND%20NOT%20AREA%5BInterventionSearch%5DPCSK9&pageSize=1&countTotal=true&fields=NCTId%2CBriefTitle%2CBriefSummary%2CDetailedDescription%2CKeyword%2CInterventionName%2CInterventionDescription&format=json
```

该请求返回 `totalCount=70`。首条 NCT05234775 的 intervention name 为 `lerodalcibep`，intervention description 只写 `300 mg` 单次皮下注射；PCSK9 只出现在 `detailedDescription` 的 pharmacodynamics 描述。该样本证明 `AREA[DetailedDescription]` 能补到 `query.intr=PCSK9` 未覆盖的记录。

```http
GET https://clinicaltrials.gov/api/v2/studies?query.term=AREA%5BDetailedDescription%5DPCSK9%20AND%20NOT%20PCSK9&pageSize=1&countTotal=true&fields=NCTId%2CBriefTitle%2CBriefSummary%2CDetailedDescription%2CKeyword%2CInterventionName%2CInterventionDescription&format=json
```

该请求返回 `totalCount=36`。首条 NCT05418166 在 detailed description 中写明 evolocumab 是 targeting PCSK9 的 monoclonal antibody，但 BasicSearch 字段中没有 PCSK9。该样本证明 plain `query.term=PCSK9` 也会漏掉只在 Detailed Description 出现的 target。

### 只给 target 字符串会漏掉 target-directed intervention

```http
GET https://clinicaltrials.gov/api/v2/studies?query.term=AREA%5BInterventionName%5Dinclisiran&filter.ids=NCT06275724&pageSize=1&countTotal=true&fields=NCTId%2CInterventionName%2CInterventionMeshTerm%2CInterventionAncestorTerm&format=json
```

该请求返回 `totalCount=1`。NCT06275724 的完整 JSON 中，intervention 为 `inclisiran`，描述为前瞻性观察研究且没有 treatment allocation；派生 `interventionBrowseModule.meshes` 只有 `C585830 / ALN-PCS`。

对完整响应递归扫描以下 HGNC 官方名称集合，命中路径为零：

* approved symbol：`PCSK9`
* approved name：`proprotein convertase subtilisin/kexin type 9`
* alias symbols：`NARC-1`、`FH3`
* previous symbol：`HCHOLA3`

再以相同 NCT ID 作为过滤条件执行：

```http
GET https://clinicaltrials.gov/api/v2/studies?query.term=EXPANSION%5BConcept%5D%28PCSK9%20OR%20%22proprotein%20convertase%20subtilisin%2Fkexin%20type%209%22%20OR%20%22NARC-1%22%20OR%20HCHOLA3%20OR%20FH3%29&filter.ids=NCT06275724&pageSize=1&countTotal=true&fields=NCTId&format=json
GET https://clinicaltrials.gov/api/v2/studies?query.intr=EXPANSION%5BConcept%5D%28PCSK9%20OR%20%22proprotein%20convertase%20subtilisin%2Fkexin%20type%209%22%20OR%20%22NARC-1%22%20OR%20HCHOLA3%20OR%20FH3%29&filter.ids=NCT06275724&pageSize=1&countTotal=true&fields=NCTId&format=json
```

两者均返回 `totalCount=0`。这排除了“UMLS Concept expansion 会自动从 inclisiran 推导 PCSK9”的可能性。

为独立确认 intervention-target 关系，ChEMBL 官方端点返回：

* `CHEMBL5095052`（inclisiran sodium）的 `mechanism_of_action` 为 `PCSK9 mRNA rnai inhibitor`
* `target_chembl_id` 为 `CHEMBL4630662`
* `CHEMBL4630662` 的 preferred name 为 `PCSK9 mRNA`，organism 为 `Homo sapiens`

这构成可重复反例：一个已由外部权威药理源明确映射到 PCSK9 的 intervention，其 ClinicalTrials.gov 完整登记可能完全不写 PCSK9 或 HGNC 同义词，Concept expansion 和 browse term 也不补出 PCSK9。

NCT06958315 是较弱但有说明价值的边界样本：其核心标题、summary、detailed description、keywords、intervention 和 browse terms 不含 PCSK9，但完整 JSON 的 secondary outcome description 含 `PCSK9i`。因此它会被更宽的 `query.term` 召回，却可能被只覆盖 intervention-related fields 的策略漏掉。该样本不再用作“完整记录无 target”证据。

### 宽泛文本检索会制造机制假阳性

```http
GET https://clinicaltrials.gov/api/v2/studies?query.term=AREA%5BEligibilityCriteria%5DPCSK9%20AND%20NOT%20PCSK9%20AND%20NOT%20AREA%5BDetailedDescription%5DPCSK9&pageSize=1&countTotal=true&fields=NCTId%2CBriefTitle%2CBriefSummary%2CDetailedDescription%2CEligibilityCriteria%2CKeyword%2CInterventionName%2CInterventionDescription&format=json
```

该请求返回 `totalCount=207`。首条 NCT04966897 是囊性纤维化营养补充剂研究，PCSK9 只出现在排除标准的 “Use of lipid lowering therapy including ... PCSK9 inhibitors”。它不是 PCSK9-directed intervention trial。该样本证明 `AREA` 能提高字段覆盖，却不能独立判断语义角色。

## 四个重点问题的结论

### 1. 仅有 target 字符串和同义词会系统性漏掉什么

已验证事实与直接推断合并后，可预期系统性漏掉：

* 只登记 intervention 的 INN、商品名、研究代码、serial number 或内部 identifier，而未写 target 的药物试验
* intervention mechanism 已由外部药理知识确定，但 ClinicalTrials.gov 文本仅描述适应症、剂量、疗程或临床终点的记录
* target 只出现在可选 `DetailedDescription`、eligibility、outcome、references 或其他非默认 Search Area 的记录
* 较早登记或字段不完整的记录，因为当前 PRS 必填规则不能追溯保证所有历史 API 记录字段齐全
* target 字符串使用未被输入 synonym set 或 UMLS expansion 覆盖的旧名、蛋白复合物名、家族名、splice variant、mutation、pathway、phenotype 或功能描述的记录
* target-relevant biomarker、genetic、natural-history、observational 或 diagnostic studies，它们可能没有 target-directed intervention
* 多成分或组合 intervention 中只有某一成分作用于 target，而登记只使用组合产品名或 regimen 名的记录

其中 inclisiran/PCSK9 是已验证的具体漏召回反例。其余类别是由 PRS 可选性、Search Areas 覆盖和常见登记表达方式推导的高置信推断，仍需金样本量化。

### 2. `query.intr`、`query.term` 和 `AREA` 能否弥补

只能部分弥补：

* `query.intr` 比只搜 `InterventionName` 更宽，能搜索 other name、MeSH、ancestor、keywords、intervention/arm descriptions 和 titles
* `query.term` 的 BasicSearch 进一步覆盖 Brief Summary、condition 和多类结果字段，但不覆盖 Detailed Description 或 Eligibility Criteria
* `AREA[DetailedDescription]`、`AREA[EligibilityCriteria]`、`AREA[Keyword]`、`AREA[InterventionName]` 等可以显式补齐指定字段
* UMLS concept/relaxation expansion 可以补一部分术语变体与同义词

它们无法弥补“记录根本未写 target，只有 intervention 名”的缺口，也不能区分 target 在 intervention、背景、比较、伴随用药、排除标准或 outcome 中的角色。更宽检索同时增加 false positives。

### 3. AACT 或 browse terms 是否增加 target-to-intervention 语义

没有。AACT 增加关系数据库形式、查询便利性和 arm/group-to-intervention 连接；browse terms 增加 study-level MeSH/ancestor/leaf/branch 受控词。公开 schema 中不存在 target 表、mechanism 表或 intervention-target join。BrowseModule 也没有连接到具体 intervention 项的外键或关系类型。

它们可能偶然产生与 target 同名的 MeSH/browse 词，从而提高某些记录的字符串召回，但这不构成稳定、可审计的 target-to-intervention 语义。NCT06958315 的 browse term 为 `ALN-PCS` 而非 PCSK9，是已验证反例。

### 4. 映射是必要条件、充分条件还是都不是

作为普遍逻辑条件，两者都不是：

* 非必要：target 显式出现在 trial 文本时无需映射即可检索；有些 target-centric studies 没有治疗 intervention
* 非充分：intervention-target 映射不能证明该 trial 在所研究 condition、arm、dose 和 role 下测试该 target 机制

作为工程策略，外部 target-to-intervention 映射是达到高召回的必要组成部分，但必须与字符串/同义词查询并集使用，并经过 trial-level role 和 relevance 判定。不能用“mapped intervention 出现在登记中”单独生成机制结论。

## 限制、推断与未决问题

* 端点计数随 ClinicalTrials.gov 每日数据更新和搜索实现变化而变化；本文件记录数据时间戳和访问日期，不把绝对计数视为稳定契约
* `EXPANSION[Relaxation]` 是默认行为，部分计数可能包含 UMLS synonym、词形和松弛邻接命中；后续可用 `EXPANSION[None]` 或 `EXPANSION[Term]` 建立精确字符串基线
* 本轮只用 PCSK9/inclisiran 构造可重复反例，没有建立多 target、多 modality 的 gold standard，不能量化总体 recall/precision
* NCT06275724 已对完整 JSON 做大小写不敏感、HGNC 名称集扫描；推广到其他 target 时仍须版本化 synonym set，并记录所用 ontology 版本
* ChEMBL 用于独立验证 inclisiran-PCSK9 关系，不是 ClinicalTrials.gov 官方来源；它支持反例的药理前提，但不改变 ClinicalTrials.gov schema 结论
* PRS requiredness 是当前提交规则，API OpenAPI 的可选性是客户端契约；二者不能互相替代

## 推荐的下一步研究

* 建立 30 至 50 条多 target、多 modality 金样本，至少覆盖 receptor、kinase、cytokine、RNA target、protein complex、antibody、small molecule、oligonucleotide 和 gene therapy
* 对 `target terms ∪ mapped interventions ∪ AREA[DetailedDescription/EligibilityCriteria/Outcome*]` 的组合检索分别测量 Recall、Precision、边际增益和重复率
* 给每个命中标注语义角色：目标干预、对照、背景治疗、伴随用药、排除项、biomarker、outcome、condition context 或 incidental mention
* 比较 ChEMBL、Open Targets、DrugCentral 等映射源的版本、证据等级、多靶点关系和 intervention name normalization；本轮未选定生产映射源
* 按 study start 或 registration era 分层量化历史记录字段缺失，验证当前 PRS requiredness 对旧记录的适用边界

## 需要输入确认的问题

* “target-relevant trial” 是否只包含 target-directed therapeutic intervention，还是也包含 biomarker、eligibility、genetic、natural-history、diagnostic 和 safety studies
* comparator、background therapy、concomitant medication 和明确禁止使用的 mapped intervention 是否应进入候选集，还是在召回阶段即排除
* 产品是否允许接入并版本固定外部药物-靶点知识库；若不允许，只能接受不可消除的系统性漏召回

## 官方与权威支持来源清单

访问日期均为 2026-08-21：

* [ClinicalTrials.gov Data API](https://clinicaltrials.gov/data-api/api)
* [ClinicalTrials.gov OpenAPI v2](https://clinicaltrials.gov/api/oas/v2)
* [ClinicalTrials.gov API version endpoint](https://clinicaltrials.gov/api/v2/version)
* [ClinicalTrials.gov Search Areas](https://clinicaltrials.gov/data-api/about-api/search-areas)
* [Constructing Complex Search Queries](https://clinicaltrials.gov/find-studies/constructing-complex-search-queries)
* [ClinicalTrials.gov Study Data Structure](https://clinicaltrials.gov/data-api/about-api/study-data-structure)
* [Protocol Registration Data Element Definitions](https://clinicaltrials.gov/policy/protocol-definitions)
* [AACT home and provenance](https://aact.ctti-clinicaltrials.org/)
* [AACT database schema](https://aact.ctti-clinicaltrials.org/schema)
* [AACT data dictionary](https://aact.ctti-clinicaltrials.org/documentation)
* [HGNC PCSK9 record](https://rest.genenames.org/fetch/symbol/PCSK9)
* [ChEMBL inclisiran sodium mechanism](https://www.ebi.ac.uk/chembl/api/data/mechanism.json?molecule_chembl_id=CHEMBL5095052&limit=20)
* [ChEMBL PCSK9 mRNA target](https://www.ebi.ac.uk/chembl/api/data/target/CHEMBL4630662.json)