<!-- markdownlint-disable-file -->
# Task Research: ClinicalTrials.gov 靶点到干预映射的范围影响

基于既有研究中“ClinicalTrials.gov API v2 没有独立分子靶点结构化字段”的结论，评估该限制对 Drug Target Scout DEMO 功能范围、临床试验召回能力和 PRD 完整性的影响。研究基线日期为 2026-08-21。

## Executive Decision

对当前 prd-v0.1.md 的产品承诺，实务答案是：**推荐的一至两周低延迟 DEMO 必须加入最小、可追溯的靶点到干预措施关系层，不能只依赖已测试的靶点文本查询；所有进入临床、竞争和 Go / No-Go 结论的试验都必须完成关系判定。**

这个结论有两个重要限定：

1. 映射不是所有靶点相关研究的普遍逻辑必要条件。登记文本已经明确写出 target 时，直接词检索即可命中；biomarker、遗传学、自然史或观察性研究也可能没有可映射的治疗干预。
2. 映射不是充分条件。某药物已知作用于某靶点，不代表它在特定登记中是目标干预，也不代表该试验在用户指定适应症中验证了该靶点。对照药、背景治疗、伴随用药、多靶点药物和排除标准都可能制造误归因。

本轮证据否证了“只依赖已测试的 direct target-text query 即可可靠履行当前 PRD”的假设，但没有证明“所有可达到某一召回门槛的架构都必须在检索前调用外部映射库”。Condition-first 候选池加 trial-level mechanism classification 是一个成本更高的反例架构。因此，最准确的工程结论是：

> 关系判定是靶点级结论的必要条件。对本研究选定的低延迟在线 DEMO，预查询 target-to-intervention mapping 是补回已验证 direct-query 漏项、控制候选审核成本的推荐组件，不是所有检索架构的普遍逻辑必要条件，也尚未由 gold set/source ablation 证明为达到某一召回门槛的唯一实现。映射本身不充分，最终相关性仍必须由 trial-level condition、intervention role、机制证据和原文共同判定。

如果不做映射，仍可交付“ClinicalTrials.gov 靶点文本候选发现”，但必须把运行状态降为 `DISCOVERY_ONLY`，不得声称形成完整临床管线、竞争拥挤度或基于临床证据的 Go / No-Go。零命中也不得解释为没有临床开发活动。

## Task Implementation Requests

* 判断达到可接受的临床试验召回率是否必须引入靶点到干预措施的映射能力
* 若需要，评估可行实现路径、数据源、工程复杂度及各路径的召回率代价
* 对照 prd-v0.1.md，明确该能力在原始需求中是显式覆盖、隐含要求还是未覆盖
* 给出一个适合 1 至 2 周 DEMO 的推荐范围，并定义可验证的验收方法

## Scope and Success Criteria

* Scope: ClinicalTrials.gov API v2 的检索字段与登记数据语义、靶点到药物或生物制剂的查询扩展、免费或开放映射来源、结果合并与相关性判定、PRD 需求覆盖；不设计完整药理知识图谱，不采购商业数据库，不声称在没有金标准时得到绝对召回率
* Assumptions:
  * “靶点检索”意指发现与目标分子机制相关的临床试验，而不只是检索正文中恰好出现靶点字符串的记录
  * “可接受召回率”在原 PRD 中没有数值定义，本研究提出的是可执行的 DEMO 工程门槛，不是行业或监管标准
  * 既有研究中 ClinicalTrials.gov 无独立分子靶点字段的结论作为已验证基线；本轮官方 schema、PRS 定义和端点反例再次支持该结论
  * 映射产生的候选试验仍需适应症过滤、干预身份归一化和机制方向校验，不能把共靶点或组合疗法自动视为完全相关
* Success Criteria:
  * 用官方 schema 或一手文档确认 ClinicalTrials.gov 能与不能表达的检索语义
  * 对 PRD 相关条款逐项分类为显式覆盖、隐含依赖或缺失，并提供行号
  * 至少评估三条实现路径，并为每条说明覆盖增益、漏召回来源、误召回风险、成本和许可条件
  * 通过 PRD 示例靶点比较直接靶点词检索与映射扩展检索；明确区分结果数量、代理召回率和真实召回率
  * 选定一条 1 至 2 周内可实施的 DEMO 路径，并定义离线金样本与线上审计验收标准

## Working Hypothesis and Disconfirming Check

* Initial hypothesis: 如果系统承诺发现“与靶点或机制相关”的临床试验，而 ClinicalTrials.gov 记录常仅使用干预措施名称，则靶点到干预措施映射是达到可接受召回率的必要检索扩展；它可以不是独立 Agent，也不必是完整知识图谱
* Cheap disconfirming check: 对 GLP-1R、TL1A、PCSK9 分别执行靶点名和同义词直接检索，再用独立来源列出的已知干预名称执行并集检索。如果直接检索覆盖绝大多数映射候选且漏项均与 PRD 决策无关，则 MVP 可以不引入映射
* Result: 假设的弱形式获得支持。本轮证明 direct-text-only 存在决策相关漏项，并支持在所选 DEMO 架构中加入映射扩展；本轮尚未证明外部预查询映射对所有高召回架构构成必要条件。三个场景均出现 `mapping-only` 候选，并有完整登记不含 target 词但机制由独立来源确认的实例；同时 `direct-only` 候选和上下文误报证明映射不能替代直接检索或相关性判定

## Research Questions and Answers

| Question | Answer | Evidence status |
|---|---|---|
| ClinicalTrials.gov 是否存在 molecular target 或 mechanism 字段 | 不存在独立或等价结构化字段；`targetDuration` 是随访时长，不是分子靶点 | 官方 OpenAPI、Study Data Structure、PRS 定义与全 schema 扫描已验证 |
| `query.intr`、`query.term`、`AREA` 能否代替映射 | 只能扩大或定向文本召回；不能从药物名推导未写出的靶点，也不能判断语义角色 | 官方 Search Areas、复杂查询指南和 NCT06275724 反例已验证 |
| AACT 或 browse terms 是否提供 target-to-intervention relation | 不提供。AACT 关系化登记数据并增加 arm/group-to-intervention 连接；browse terms 是 study-level MeSH 层级 | 官方 AACT schema/data dictionary 和 CT.gov schema 已验证 |
| 当前 PRD 是否覆盖映射能力 | 总体是隐含依赖：结果层显式承诺，关系建立能力未命名，工程契约和质量验收完全缺失 | PRD 逐条文件分析 |
| 映射是否必须 | 对所选低延迟 DEMO，最小映射扩展是推荐且应纳入的实现；跨所有架构并非普遍必要，condition-first + relation classification 可替代。无论采用哪种候选生成方式，关系判定对靶点级结论都是必须的 | 产品范围、检索反例和替代架构共同支持；具体 recall 门槛仍待 gold set 验证 |
| 映射是否充分 | 不充分。还需 trial-level role、适应症、机制方向、组合疗法和原文判定 | ClinicalTrials.gov 字段语义和误报样本支持 |
| 能否报告各路径绝对 recall | 不能。没有完整全球 ground truth；只能报告候选集合差、代理金集上的 proxy recall 和风险加权 proxy recall | 信息检索评测原则与本轮实验设计 |

## Research Executed

### File Analysis

* prd-v0.1.md
  * 背景和总体目标要求用户输入靶点后获得相关临床信号、竞争判断和 Go / No-Go / Need More Data：prd-v0.1.md:8-16, 26-39
  * Clinical Agent 显式要求找到“与靶点、机制、适应症相关”的试验、提取干预并识别积极和失败信号：prd-v0.1.md:87-94
  * Competition Agent 显式要求竞争活跃度、拥挤程度和公司/管线动态：prd-v0.1.md:96-103, 250-268
  * GLP-1R 和 TL1A 场景把相关试验、当前临床进度和竞争拥挤度绑定到输入靶点：prd-v0.1.md:114-140
  * 数据源和 Clinical Agent 最低要求只定义 ClinicalTrials.gov 查询与 NCT、phase、status、condition、intervention 字段提取：prd-v0.1.md:163-190, 228-248
  * Go / No-Go 规则把积极临床信号、失败/终止和竞争饱和度作为靶点级决策依据：prd-v0.1.md:288-334
  * 系统流程没有 target normalization、intervention expansion、relation evidence 或映射验证步骤：prd-v0.1.md:388-429
  * MVP 排除复杂图谱分析，但仍要求 ClinicalTrials.gov 检索和 Go / No-Go；这不能推出“排除最小关系表”：prd-v0.1.md:524-545
  * 成功标准要求看出临床信号并给出建议，却没有 recall、precision、误归因或降级门槛：prd-v0.1.md:547-555
* .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md
  * 已验证 ClinicalTrials.gov API v2 无独立分子靶点字段：该文件第 7 至 14 行、第 274 至 287 行
  * 既有建议只提出 target/drug synonyms 和机制相关性排序，尚未回答是否必须引入 target-to-intervention candidate expansion：该文件第 363 至 387 行

### Code Search Results

* 工作区仍只有 PRD 与研究文档，没有应用代码、依赖清单、API adapter、映射 schema 或测试
* 因此推荐方案以接口契约、数据模型和验收门禁为中心，不假设任何现有实现惯例

### Subagent Evidence

* .copilot-tracking/research/subagents/2026-08-21/prd-target-intervention-scope-coverage-research.md
  * 对 PRD 做逐条范围分类，结论为“用户结果显式覆盖、映射能力隐含依赖、工程契约与验收缺失”
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-field-semantics-research.md
  * 核验 OpenAPI、PRS、Search Areas、复杂查询、AACT 和端点反例
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-retrieval-comparison-research.md
  * 对 GLP-1R、TL1A、PCSK9 完成 A/B 查询、分页、集合差、哈希和样本回查
* .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md
  * 比较七条映射/召回路径，核验 Open Targets、ChEMBL、DrugCentral、Pharos、RxNorm、PubChem 的能力和许可边界
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-recall-evaluation-research.md
  * 设计代理金集、风险加权指标、source ablation、产品门禁与降级语义

### External Research

* ClinicalTrials.gov 官方资料
  * [Data API](https://clinicaltrials.gov/data-api/api)
  * [OpenAPI v2](https://clinicaltrials.gov/api/oas/v2)
  * [Search Areas](https://clinicaltrials.gov/data-api/about-api/search-areas)
  * [Constructing Complex Search Queries](https://clinicaltrials.gov/find-studies/constructing-complex-search-queries)
  * [Study Data Structure](https://clinicaltrials.gov/data-api/about-api/study-data-structure)
  * [Protocol Registration Data Element Definitions](https://clinicaltrials.gov/policy/protocol-definitions)
* AACT 官方资料
  * [AACT provenance](https://aact.ctti-clinicaltrials.org/)
  * [AACT schema](https://aact.ctti-clinicaltrials.org/schema)
  * [AACT data dictionary](https://aact.ctti-clinicaltrials.org/documentation)
* 映射与规范化来源
  * [Open Targets GraphQL API](https://platform-docs.opentargets.org/data-access/graphql-api)
  * [Open Targets Drugs and Clinical Candidates](https://platform-docs.opentargets.org/target/drugs)
  * [Open Targets licence](https://platform-docs.opentargets.org/licence)
  * [ChEMBL Data Web Services](https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services)
  * [ChEMBL target questions](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/target-questions)
  * [ChEMBL downloads](https://chembl.gitbook.io/chembl-interface-documentation/downloads)
  * [ChEMBL 37 license](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/LICENSE)
  * [HGNC REST](https://www.genenames.org/help/rest/)
  * [DrugCentral](https://drugcentral.org/)
  * [RxNorm API](https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html)
  * [PubChem PUG REST](https://pubchem.ncbi.nlm.nih.gov/pcfe/docs/markdown/pug-rest)
* 评测方法
  * [Retrieval evaluation with incomplete information](https://doi.org/10.1145/1008992.1009000)
  * [Relative recall in methodological search filters](https://doi.org/10.1186/1471-2288-6-33)
  * [TREC 2021 Clinical Trials Track](https://trec.nist.gov/data/clinical2021.html)
  * [Cochrane Handbook Chapter 4](https://training.cochrane.org/handbook/current/chapter-04)

### Project Conventions

* Standards referenced: Task Researcher 模式、HVE Core Markdown 与写作风格说明
* Instructions followed: 所有代码库、API、文档和外部调查活动均委派给 Researcher Subagent；主代理只综合和更新 `.copilot-tracking/research/`
* Environment note: Microsoft Foundry 技能依赖检查因本机 `azd 1.20.1` 无法解析 `azure.ai.agents` 依赖而失败；本研究不调用 Foundry 资源、SDK 或部署工作流，因此不影响 ClinicalTrials.gov 与映射能力结论

## Key Discoveries

### ClinicalTrials.gov 能表达什么

ClinicalTrials.gov 结构化的是试验登记事实，不是药理靶点关系：

| Concept | API path or search | Requiredness and boundary |
|---|---|---|
| Molecular target | 无独立路径 | PRS 没有该独立数据元素，OpenAPI 没有该属性 |
| Mechanism of action | 无独立路径 | 可能散落于文本，不是受控实体或 relation |
| Intervention | `protocolSection.armsInterventionsModule.interventions[]` | 干预性研究至少一项；包含 type、name、otherNames、description，不包含 target edge |
| Keywords | `protocolSection.conditionsModule.keywords[]` | 提交者可选自由文本，不保证出现 target |
| Brief summary | `protocolSection.descriptionModule.briefSummary` | PRS 必填；属于 `query.term` 的 BasicSearch |
| Detailed description | `protocolSection.descriptionModule.detailedDescription` | PRS 可选；不在默认 BasicSearch/InterventionSearch 中，需 `AREA[DetailedDescription]` |
| Intervention browse terms | `derivedSection.interventionBrowseModule` | 派生 MeSH/ancestor/leaf/branch，study-level，不绑定具体 intervention，也不是 target ontology |

`query.intr` 默认搜索 12 个 InterventionSearch 字段。`query.term` 默认 BasicSearch 搜索 57 个字段，但不包含 Detailed Description 或 Eligibility Criteria。`AREA[...]` 可以定向任意 Study Data Structure 字段，UMLS expansion 可以扩展术语，却不能从 `inclisiran` 推导出登记中没有写出的 `PCSK9`。

AACT 也没有填补该缺口。它把 ClinicalTrials.gov 数据关系化并增加 arm/group-to-intervention 连接；公开 schema 中没有 target、mechanism 或 intervention-target join。

### 可重复的漏召回与误召回证据

ClinicalTrials.gov API v2 在本轮的版本为 `2.0.5`，数据时间戳为 `2026-08-20T09:00:05`。以下都是动态快照，不是永久常数。

#### 单条反例

NCT06275724 的 intervention 是 inclisiran。完整 ClinicalTrials.gov JSON 不含 PCSK9 官方符号、全名或 HGNC 别名；`query.term`、`query.intr` 和 UMLS Concept expansion 在以该 NCT 过滤时都返回零。ChEMBL 则把 inclisiran sodium 的 mechanism 标为 `PCSK9 mRNA rnai inhibitor`。这证明：

```text
target terms only -> cannot retrieve every target-directed intervention record
```

反向误报也存在。NCT04966897 只在排除标准中提到 PCSK9 inhibitors，并不是 PCSK9-directed intervention trial；NCT07446439 的 Tradipitant 用于治疗 GLP-1R agonist 引起的恶心/呕吐，本身不靶向 GLP1R。更宽的 `AREA` 或 BasicSearch 会提高文本覆盖，也会增加上下文误报。

#### 三个 PRD 场景的 A/B 对照

A 使用规范 target 名和同义词的 `query.term`，B 使用独立来源确认干预名和研发代码的 `query.intr`。两者都带 condition query，完整分页后按 NCT 去重。

| Target + indication | A direct terms | B mapped interventions | Overlap | Direct-only | Mapping-only | Union |
|---|---:|---:|---:|---:|---:|---:|
| GLP-1R + obesity/T2D | 626 | 1,602 | 463 | 163 | 1,139 | 1,765 |
| TL1A + IBD/Crohn/UC | 12 | 26 | 5 | 7 | 21 | 33 |
| PCSK9 + hypercholesterolemia | 194 | 199 | 122 | 72 | 77 | 271 |

这些结果证明检索路线互补，但**不构成真实 recall 数字**：

* `mapping-only` 是候选增量，不等于全部为真阳性
* `direct-only` 可能是映射词表漏药，也可能是背景提及、非干预研究或机制误报
* B 词表本身不是完整药物本体，尤其会漏最新资产、组合制剂、地区代号和未进入结构化源的候选
* GLP-1R B 含多靶点激动剂，target relation 成立不代表 GLP1R 是唯一或主要临床机制

9 条 mapping-only 固定抽样中，完整登记 JSON 不含 target 词的比例分别是 GLP-1R 3/3、TL1A 0/3、PCSK9 1/3。TL1A/PCSK9 的其他样本虽然完整 JSON 有 target 词，但它们出现在 reference、result 或 outcome 等 `query.term` 未召回的路径。漏召回至少有两个机制：

1. 登记只写干预名或研发代码，没有 target 词
2. 登记含 target 词，但目标字段不在当前默认搜索范围或未被该检索语义召回

### Condition-first 不是低成本替代品

| Condition scope | Candidate count |
|---|---:|
| Obesity OR Type 2 Diabetes Mellitus | 25,195 |
| Inflammatory Bowel Disease OR Crohn Disease OR Ulcerative Colitis | 4,304 |
| Hypercholesterolemia OR Familial Hypercholesterolemia | 1,483 |

TL1A condition pool 按 B 词表离线筛选得到 26 条，与 B 一致；PCSK9 得到 184 条，均属于 B，但仍漏 B 中 15 条。Condition-first 原始池可以作为高成本候选上界和离线残余审计入口，不能被称为 true-recall 上界，也不适合作为所有在线查询的默认路径。

### PRD 覆盖判定

如果必须在“显式覆盖、隐含依赖、完全缺失”中只选一个，答案是 **隐含依赖**。分层判定如下：

| Layer | Original PRD coverage | Verdict |
|---|---|---|
| 靶点级临床、竞争和决策结果 | 明确要求相关试验、临床进度、竞争、信号和 Go / No-Go | 结果语义显式覆盖 |
| ClinicalTrials.gov intervention 字段抽取 | 明确要求 NCT、phase、status、condition、intervention | 显式覆盖 |
| Target normalization | 用户可输入同义词，但没有 canonical ID、歧义或物种规则 | 工程契约缺失 |
| Target-to-intervention relation | 没有命名能力、数据源、relation type 或 provenance | 显式功能缺失，但属于结果的隐含依赖 |
| Trial-level target relevance | 没有目标干预、对照、背景治疗、多靶点或 biomarker 归因规则 | 决策逻辑的隐含依赖 |
| Mapping quality acceptance | 没有 gold set、proxy recall、P@K、误归因或降级门槛 | 完全缺失 |

“MVP 不做复杂图谱分析”不能用来排除最小映射层。映射可实现为带来源的小型关系表和确定性 resolver，不需要知识图谱、独立 Agent 或新部署单元。

## Technical Scenarios

### Scenario 1: Direct Target Text Only

**Principle:**

用 HGNC approved/previous/alias symbol、全名和受控机制词构建 `query.term`，不生成 target-to-intervention edge。

**Advantages:**

* 实现和延迟最低
* 能找回登记明确写出 target 的试验及没有治疗干预的 target-centric 研究
* 不新增映射数据许可

**Recall cost:**

* 召回上限是“可搜索字段中明确出现 target 或所列同义词”的记录
* 系统性漏掉只写 INN、商品名、研究代码、组合产品名或旧资产代号的试验
* 默认搜索还会漏 Detailed Description、Eligibility Criteria 和部分结果/参考字段
* 无法给出绝对损失率；三场景 A/B 快照中，B 各自增加 1,139、21、77 条 A 未命中的候选

**Precision cost:**

* target 可能只在背景、排除标准、不良反应、测量或伴随用药中出现

**Use boundary:**

仅适合作为 baseline、并行补源或降级模式。若单独使用，产品必须改为 `DISCOVERY_ONLY`。

### Scenario 2: Versioned Manual Seed Dictionary Only

**Principle:**

为少量 DEMO 靶点人工维护 canonical intervention、研究代码、别名、modality、action 和来源。

**Advantages:**

* 对 3 至 10 个固定展示靶点可快速达到高可解释性
* 能覆盖 TL1A 这类 Open Targets/ChEMBL 当前返回零的缺口
* 本地查找延迟低、Git 版本可重放

**Recall cost:**

* 覆盖上限严格等于人工已录入集合
* 新药、新代码、失败项目、地区别名和任意用户输入靶点都会漏
* 维护成本随靶点和资产数量增长，不能外推为通用产品能力

**Precision cost:**

* 小范围可高精度，但任何错误 relation 会污染所有下游试验归因

**Use boundary:**

作为结构化源的 exception layer，不能作为唯一主架构。

### Scenario 3: Open Targets Only

**Principle:**

用 `mapIds` 将输入解析到 Ensembl target，再取 `drugAndClinicalCandidates`。

**Advantages:**

* target resolution 和临床候选图接入快
* 数据为 CC0，提供 release、历史下载、synonyms、trade names 和多种 drug modality
* 单靶点交互查询延迟适合 DEMO

**Recall cost:**

* ceiling 是 Open Targets 筛选后的 ChEMBL/临床关系集合
* 当前 target entity 不覆盖 protein complex 和 gene fusion
* 部分 vaccine、blood product、cell therapy 和 multi-ingredient 产品不在 Drug 模型中
* 2026-08-21 对 TNFSF15/TL1A 的 `drugAndClinicalCandidates` 返回 0，而 ClinicalTrials.gov 映射词表检索有 26 条候选，构成直接单源漏项证据

**Precision cost:**

* Target-drug relation 不等于该适应症下的 trial relevance；多靶点、parent/child 和跨适应症最高阶段可能误导

**Use boundary:**

适合作为快速主源，不可单独使用。

### Scenario 4: ChEMBL Mechanism Only

**Principle:**

由 HGNC/UniProt 解析 ChEMBL target component，读取 mechanism 和 molecule/parent/synonyms。

**Advantages:**

* relation 字段比 assay activity 更接近药理机制
* 同时覆盖 small molecule 和已建模 biotherapeutic
* ChEMBL 37 可固定下载、记录 DOI 和哈希，重放性强

**Recall cost:**

* 未审核机制、`Unchecked` assay、新研发代码和未建模 modality 会漏
* family、complex、variant 和 isoform 不能简单压成一对一 gene edge
* TNFSF15 target search 同样返回 0，是已验证的单源盲点

**Precision cost:**

* 若误把 assay activity 当 mechanism，会引入 off-target、phenotypic、artifact 和低 potency 噪声

**License cost:**

ChEMBL 37 为 CC BY-SA 3.0。DEMO 展示和派生数据再分发需保留归属，并由项目确认 ShareAlike 义务。

**Use boundary:**

适合作为 Open Targets 的机制补源和 cross-check，不可单独使用。

### Scenario 5: Narrow Multi-source Union

**Principle:**

合并 direct target terms、Open Targets、ChEMBL 和小型人工 exception seed。每条 relation 保存 source、release、relation type、action、modality、evidence 和 confidence tier。

**Advantages:**

* 同时覆盖“登记写 target”和“登记只写药物/代码”两类主要路径
* Open Targets 提供低成本解析，ChEMBL 提供机制/组件补充，seed 处理 TL1A 等明确缺口
* 可以通过 source ablation 量化每个来源的独有贡献

**Recall cost:**

* ceiling 是四路 union，仍会漏所有来源共同未知的最新资产、隐藏管线、复杂靶点、组合产品和部分新 modality
* 多源并不自动独立。Open Targets 药物层整合 ChEMBL 等上游，不能把双命中当作两个独立机制证据

**Precision cost:**

* union 越大，relation type 混淆、别名碰撞、多靶点和疾病上下文误报越多
* 必须增加 deterministic dedupe、trial role filter 和 Top-K 相关性排序

**License cost:**

Open Targets/HGNC 为 CC0；ChEMBL 为 CC BY-SA 3.0；若加入 DrugCentral 则为 CC BY-SA 4.0。首版不建议混入许可未确认的 Pharos 数据快照。

**Use boundary:**

这是本研究选定的 1 至 2 周 DEMO 方案。

### Scenario 6: LLM or Web Generated Mapping

**Principle:**

让模型或 Web search 提出最新 candidate name、alias 和 claimed target，再由一手/权威来源验证。

**Advantages:**

* 可能补结构化 release lag、最新抗体和公司研发代码

**Recall cost:**

* 没有稳定可定义的 recall ceiling；隐藏管线、索引缺口和付费墙仍会漏
* 结果受搜索索引、模型、prompt 和时间影响，不可作为可重放主源

**Precision cost:**

* 可能生成不存在的药物、错误 target、旧代码或把 preclinical assay 误称临床项目

**Use boundary:**

只允许进入 `UNVERIFIED_CANDIDATE` 隔离区。至少一个独立来源确认名称与 target relation 后，才能加入高置信试验查询词表。

### Scenario 7: Condition-first Full Candidate Pool

**Principle:**

先按 condition 分页抓取所有试验，再用映射词表、文本和相关性模型离线筛选。

**Advantages:**

* 对只写新药名、未知代码或非标准 modality 的记录有较高候选覆盖潜力
* 可作为 gold-set pooling 和残余漏项审计来源

**Recall cost:**

* ceiling 仍受 condition query、登记公开范围和字段完整度限制，不是全球 true recall
* 有限字段离线筛选仍会漏项，本轮 PCSK9 C 漏掉 B 中 15 条

**Precision and runtime cost:**

* 三个场景的候选池为 1,483 至 25,195 条，绝大多数与指定 target 无关
* 分页、解析、机制验证和人工审核负担比 target/mapping query 高一个至三个数量级

**Use boundary:**

不作为默认在线路径。用于离线 benchmark、残余审计，或所有结构化映射稀疏时的有界 fallback。

## Selected Approach

### Target Architecture

选择 **确定性 Target-Intervention Resolver + direct/mapped 双路查询 + trial-level relation gate**。Resolver 是同一 Python 服务内的业务模块，不是新的 Agent、微服务或知识图谱。

```text
User target + indication
  -> Target Resolver
       -> Open Targets mapIds
       -> HGNC approved/previous/alias validation
       -> canonical HGNC/Ensembl/UniProt bundle
  -> Candidate Mapping Resolver
       -> Open Targets 26.06 drugAndClinicalCandidates
       -> ChEMBL 37 mechanism records
       -> versioned manual exception seed for DEMO targets
       -> optional DrugCentral supplement after license review
  -> Query Planner
       -> ClinicalTrials query.term(target names and aliases)
       -> ClinicalTrials query.intr(verified intervention names/codes)
       -> query.cond(indication)
  -> Candidate Union and NCT dedupe
  -> Trial-level Relation Gate
       -> intervention/arm role
       -> target mechanism evidence
       -> indication relevance
       -> context-only negative rules
  -> Exact NCT verification
  -> Evidence ranking and report eligibility
  -> Go / No-Go / Need More Data
```

### Why This Is the Selected Target Design

* 不需要构建复杂图谱，只需一个 versioned relation snapshot 和确定性查询模块
* 对固定演示靶点，可以在构建时把 HGNC、Open Targets、ChEMBL 和人工复核例外冻结，降低运行时延迟和 schema drift
* Runtime 执行 direct target 与 mapped intervention 双路查询，覆盖本轮观察到的两类互补候选
* 对 TL1A 等结构化源零命中的案例，manual seed 必须引用 PMID、公司或其他一手证据，不能来自 LLM 记忆
* Condition-first 保留为离线评测和有界 fallback，不拖垮默认 10 分钟流程

### One-to-Two-Week Demonstrable Slice

一至两周边界必须分为“可演示功能切片”和“正式质量门禁”。当前工作区没有应用代码、adapter、schema、依赖清单、UI、测试或标注资产，因此不能把完整目标架构、40+20 双人标注和 source ablation 全部承诺在同一时间窗内。

首个可演示切片限定为 PRD 的三个固定场景：

```text
GLP1R + obesity/type 2 diabetes
TNFSF15/TL1A + inflammatory bowel disease
PCSK9 + hypercholesterolemia
```

切片内实现：

* 使用构建时冻结并由领域人员复核的 versioned JSON relation snapshot
* Open Targets 26.06、ChEMBL 37、HGNC 和 PMID 作为 snapshot 生成证据，不要求首版完成通用运行时集成
* 运行 direct `query.term` 与 mapped `query.intr`，按 NCT union/dedupe
* 对 Top 候选执行 exact-ID verification、基础 intervention role 和 relation status
* 实现主源失败、mapping 缺失、查询截断和机制冲突的降级状态
* 页面展示 Top 5、检索路线、关系来源和 coverage 警告

首版明确延后：

* 任意靶点的通用解析和全量 target universe 支持
* DrugCentral、Pharos、RxNorm、PubChem 的产品化接入
* 通用学习排序器和 condition-first 在线回退
* 40 条主金集、20 条残余审计、双人盲标、holdout 和完整 source ablation

在正式质量门禁完成前，不报告 proxy recall 百分比，也不让临床或竞争证据单独触发 Go 或 No-Go。完整结论保持 `NEED_MORE_DATA`；如为演示流程显示规则性标签，必须明确标注为未经过召回门禁的展示输出。

时间估算假设一名全栈工程师负责 API、服务和 UI，另有一名药理或临床专家并行提供复核后的 seed 和关键记录裁决。没有领域专家投入时，正式 gold-set 门禁不属于一至两周承诺。

### Minimum Data Model

```json
{
  "target": {
    "input": "TL1A",
    "canonicalSymbol": "TNFSF15",
    "hgncId": "HGNC:11931",
    "ensemblId": "ENSG00000181634",
    "uniprotIds": ["O95150"],
    "aliases": ["TL1A", "TL1", "VEGI"]
  },
  "interventionCandidate": {
    "canonicalName": "afimkibart",
    "aliases": ["PF-06480605", "RVT-3101"],
    "modality": "MONOCLONAL_ANTIBODY",
    "relationType": "DIRECT_TARGET",
    "action": "INHIBITOR",
    "source": "PUBMED_MANUAL_EXCEPTION",
    "sourceVersion": "2026-08-21",
    "evidenceIds": ["PMID:40706613"],
    "verificationState": "VERIFIED"
  },
  "trialRelation": {
    "nctId": "NCT04090411",
    "retrievalRoutes": ["DIRECT_TERM", "MAPPED_INTERVENTION"],
    "relationStatus": "DIRECT_VERIFIED",
    "interventionRole": "EXPERIMENTAL",
    "conditionMatch": "IN_SCOPE",
    "uncertainty": []
  }
}
```

最低 relation 状态：

```text
DIRECT_VERIFIED
CONTEXTUAL_WITH_EVIDENCE
TEXT_ONLY_CANDIDATE
MECHANISM_UNCONFIRMED
MECHANISM_CONFLICT
IRRELEVANT_CONTEXT
```

只有 `DIRECT_VERIFIED` 可以进入 strict clinical signal 和竞争计数。`CONTEXTUAL_WITH_EVIDENCE` 可以作为补充线索，但不能与 direct evidence 等权。其余状态不得驱动 Go / No-Go。

### Retrieval Flow

```text
target_terms = canonical target names + approved aliases
mapped_terms = verified intervention canonical names + codes + selected aliases

direct_set = CTGov(query.term=target_terms, query.cond=indication)
mapped_set = CTGov(query.intr=mapped_terms, query.cond=indication)
candidates = dedupe_by_nct(direct_set union mapped_set)

for each candidate:
  verify exact NCT identity
  determine intervention role
  verify target-intervention relation provenance
  verify indication scope
  classify DIRECT / CONTEXTUAL / TEXT_ONLY / IRRELEVANT / UNJUDGED

rank verified candidates
apply evaluation and run-state gates before decision synthesis
```

### Source Roles

| Source | Selected role | Not allowed to prove alone |
|---|---|---|
| HGNC | Human gene identity and aliases | Drug mapping or trial relevance |
| Open Targets | Fast target resolution and primary drug candidate generation | Complete clinical pipeline or independent second evidence beside ChEMBL |
| ChEMBL mechanism | Mechanism/component supplement and molecule aliases | Complete current pipeline; assay activity is not automatically therapeutic mechanism |
| Manual exception seed | Reviewed gaps for DEMO targets and new codes | General arbitrary-target coverage |
| ClinicalTrials.gov | Trial identity, intervention text, condition, phase, status and arm data | Molecular target relation |
| LLM/Web | Candidate proposal and cited classification assistance | Canonical ID, final relation or citation existence |

### Extended Source and License Boundaries

| Source | Allowed role | Capability boundary | License or terms boundary |
|---|---|---|---|
| Open Targets | Ensembl target resolution and primary drug/clinical candidate generation | 不是完整管线；不覆盖 complex/fusion target，部分 modality 和 multi-ingredient 产品受限 | Platform output 标记为 CC0 1.0；仍需保存 release、归属和上游 provenance，遵守原始数据所有者权利 |
| ChEMBL | Curated mechanism/component and molecule alias supplement | 优先使用 mechanism；assay activity 不能自动视为治疗机制，也不是完整实时管线 | CC BY-SA 3.0；保留归属，公开再分发 adaptations 前审查 ShareAlike |
| DrugCentral | 可选 direct target-drug/MoA 补源 | 偏 approved drug 和 bioactivity；potency/activity 不能自动视为治疗机制 | CC BY-SA 4.0；保留归属，公开再分发前审查 ShareAlike |
| Pharos/TCRD | 实验性 target-ligand/activity 调查 | 不自动等于 therapeutic relation；生产 endpoint、版本机制和数据许可尚未确认 | 许可和服务条款确认前不打包或再分发数据 |
| RxNorm | Clinical drug name、RxCUI、ingredient/product/brand 和 NDC 归一化 | 不生成 target-to-drug edge | API 多数内容可免费使用但有例外；完整 release 需 UMLS license，Prescribable 下载不需要 |
| PubChem | CID/SID、同义词、结构、cross-reference 和低置信 BioAssay enrichment | Assay target/activity 不是治疗机制、临床阶段或适应症 | NCBI 自有数据不设限制，但第三方贡献内容可能有独立权利 |

### Failure and Degradation Rules

| Situation | Run state | Decision effect |
|---|---|---|
| Target cannot be uniquely normalized | `TARGET_INVALID` or `TARGET_AMBIGUOUS` | Stop and request human confirmation |
| ClinicalTrials.gov unavailable or pagination truncated | `NEED_MORE_DATA` | No Go / No-Go |
| One optional mapping source fails | `DEGRADED_OPTIONAL_SOURCE` | Allow only if remaining strategy previously passed holdout gates; disclose narrower coverage |
| All mapping sources fail, direct query succeeds | `DISCOVERY_ONLY` | Show text candidates only; no target-level clinical or competition conclusion |
| Mapping returns empty | `MAPPING_EMPTY` | Treat as insufficient coverage, not absence of trials |
| Mechanism sources conflict | `MECHANISM_CONFLICT` | Keep candidate unjudged and require review |
| NCT exact verification fails | `NCT_VERIFICATION_FAILED` | Exclude from key evidence |
| `TERMINATED` with unclear `whyStopped` | `TERMINATION_REASON_UNKNOWN` | Report status only; do not call mechanism failure |
| All required sources succeed and no direct relation found | `VALID_EMPTY_WITHIN_SCOPE` | Default `NEED_MORE_DATA`; state only the bounded search scope |

## Recall Evaluation and Acceptance

### Why Absolute Recall Cannot Be Reported Yet

ClinicalTrials.gov 没有 target ground truth，Open Targets/ChEMBL 不是完整临床管线，condition-first 也受疾病索引和登记边界限制。因此：

* 命中数是 `retrieval yield`
* A/B overlap 是检索路线差异
* 多源人工确认集合上的比例是 `proxy recall` 或 `relative recall`
* 只有穷举冻结范围内所有相关试验时才能称为 `true recall`

本轮 A/B 数据足以证明“映射有不可忽略的候选增量”，不足以证明任何路径达到某个绝对 recall 百分比。

### Gold Set

建议建立 40 条主判定记录，允许 30 至 50 条：

* 8 个 target-indication 场景，建议 32 条 `R2_DIRECT` 正例
* 8 条 hard negative 或 contextual records
* 至少覆盖 GLP1R、TNFSF15/TL1A、PCSK9、小分子/突变靶点、失败密集靶点、多靶点或组合场景
* 5 个场景用于 development，3 个按 target 分组作为 holdout
* 两名标注者盲化来源独立判定，分歧由共识或第三名专家裁决
* 每个正例需要三面证据：ClinicalTrials exact NCT、独立 mechanism evidence、双人 scope fit

Open Targets 和 ChEMBL 可能存在数据血缘，双命中不能自动算两份独立机制证据。

### Metrics

```text
proxy_recall@L = retrieved known positives / known positives
weighted_proxy_recall = retrieved gold risk weight / total gold risk weight
strict_P@K = DIRECT_VERIFIED in fully judged top K / K
```

另报告 scenario coverage、critical miss、mechanism nDCG@10、source execution coverage、field coverage、source unique positives 和 incremental review cost。

### Project Gate Suggestions

以下均为 Drug Target Scout DEMO 的建议，不是行业标准：

| Metric | Suggested gate | Failure effect |
|---|---:|---|
| Main judged records | 30 to 50, recommend 40 | No formal recall claim |
| Holdout proxy recall@50 | >= 0.85 | `DISCOVERY_ONLY` |
| Holdout weighted proxy recall@50 | >= 0.90 | `NEED_MORE_DATA` |
| Holdout critical misses | 0 | Hard block on Go / No-Go |
| Holdout strict P@5 | >= 0.80 | Top 5 not suitable for direct display |
| Holdout strict P@10 | >= 0.70 | Rework relation filter/ranking |
| Holdout mechanism nDCG@10 | >= 0.80 | Do not claim highly relevant evidence ranks first |
| Positive scenario coverage | 100% | Target-family coverage is unstable |
| Displayed NCT exact verification | 100% | Unverified records cannot be key evidence |
| Required field/provenance coverage | 100% | Degrade and expose field gaps |

风险加权中，Active Phase 3/4、Completed Phase 3/4 with results，以及因 efficacy/safety/futility 终止的 Phase 2+ 建议权重最高。`TERMINATED` 本身不能自动获得“机制失败”标签。

### Source Ablation

固定 ClinicalTrials `dataTimestamp`、HGNC snapshot、Open Targets release、ChEMBL release、seed commit、query builder、candidate cap 和 ranker，比较：

```text
D = direct target terms
M = manual seed
O = Open Targets
C = ChEMBL mechanism
D+M
D+O
D+C
D+M+O+C
ALL minus each source
```

每个来源报告：`delta_proxy_recall`、`delta_weighted_recall`、unique positive gain、critical recovered、unique candidate cost、incremental number-needed-to-review 和 latency delta。这样才能把“召回率代价”从主观数据库比较变成可执行的项目数据。

## PRD Amendments Required Before Planning

不直接修改 prd-v0.1.md，但规划前应把以下内容纳入需求基线：

1. 定义 target、intervention、mechanism、target-intervention relation、target-trial relevance 和 clinical signal；明确文本命中不等于关系确认。
2. 把“每条驱动靶点级结论的试验必须完成 target-intervention-trial 关系判定”写入 MVP 必做项；对所选低延迟切片，明确使用构建时冻结的最小 mapping snapshot，同时保留“不做复杂知识图谱”。
3. 新增 Target Resolver：规范化 HGNC/Ensembl/UniProt、approved/previous/alias name、歧义与物种。
4. 指定映射来源角色和版本策略：Open Targets 主候选、ChEMBL mechanism 补源、人工 exception seed；ClinicalTrials.gov 不是 mapping authority。
5. 为每条 relation 保存 source、release、relation type、action、modality、evidence citation、verified-at 和 state。
6. 临床 Agent 流程拆成 direct retrieval、mapped retrieval、union、NCT verification、relation gate、ranking 和 signal attribution。
7. Trial 输出增加 retrieval route、relation status、intervention role、mechanism evidence、condition match 和 uncertainty。
8. 明确多干预、组合疗法、多靶点、biomarker、comparator、background therapy 和 excluded medication 的归因规则。
9. 明确 phase/status/`whyStopped` 到积极、失败或不确定信号的业务规则。
10. 新增运行降级：无 mapping 时为 `DISCOVERY_ONLY`；主源失败、截断或 critical miss 时为 `NEED_MORE_DATA`。
11. UI 展示映射来源、relation status、检索路线、coverage 限定和未覆盖警告。
12. 把 30 至 50 条代理金集、proxy recall、risk-weighted recall、P@K、critical miss 和 100% NCT 回查加入 DEMO 成功标准。
13. 明确许可归属和 snapshot manifest，尤其是 ChEMBL/DrugCentral 的 ShareAlike 条款。

## Product Claims With and Without Mapping

| Current claim | With selected mapping and gates | Without mapping |
|---|---|---|
| 相关临床试验 | 可称“在已声明来源和版本范围内确认 target relation 的试验” | 只能称“命中 target/alias 文本的候选记录” |
| 当前临床进度 | 可对 `DIRECT_VERIFIED` 集合汇总 phase/status | 只能显示候选文本命中的字段快照，不能称完整进度 |
| 积极/失败信号 | 需 relation、结果和终止原因证据 | 只能显示待核验线索，不得归因到靶点 |
| 竞争拥挤度 | 可对已验证资产和试验计算，并声明 coverage | 只能描述 target 词公开可见度 |
| Go / No-Go | 只有评测门禁和运行状态允许时才能作为辅助建议 | 完整决策强制 `NEED_MORE_DATA` 或 `DISCOVERY_ONLY` |
| 零结果 | 只能表述为声明范围内未找到已确认试验 | 不得表述为没有临床开发活动 |

## Implementation Order

一至两周可演示切片：

1. 在 PRD 中补齐 relation 定义、固定三场景范围和降级语义
2. 定义 Target、InterventionCandidate、TrialRelation 和 RunState schema
3. 为 GLP1R、TNFSF15/TL1A、PCSK9 冻结 HGNC、Open Targets 26.06、ChEMBL 37 和人工 exception JSON snapshot
4. 实现 direct `query.term` 与 mapped `query.intr` 双路 ClinicalTrials adapter
5. 实现 NCT union/dedupe、exact verification 和基础 relation gate
6. 实现 `DISCOVERY_ONLY`、`NEED_MORE_DATA`、mapping conflict 和 query truncation 状态
7. 展示 Top 5、来源、relation status 和未完成正式质量门禁的警告

正式质量门禁和后续增强：

1. 建立 40 条代理金集和 20 条残余审计，完成双人裁决
2. 运行 source ablation、target-level holdout 和失败 fixture
3. 只有门禁通过后才让临床和竞争证据驱动 Go / No-Go
4. 把 snapshot 生成逐步替换为可复现的通用 Target Resolver 和 source manifest pipeline
5. 将 condition-first 作为离线 residual audit 或稀疏场景的有界增强

## Potential Next Research

* 对 8 个 target-indication 场景实际建立 40 条代理金集并运行 source ablation
  * Reasoning: 本轮证明 mapping 有候选增量，但没有 true recall；只有 gold/holdout 能量化各源的召回率代价
  * Reference: .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-recall-evaluation-research.md
* 由药理和临床专家冻结 target-directed、contextual、biomarker、combination 和 termination reason 标注规则
  * Reasoning: 映射 relation 和 trial relevance 不是 ClinicalTrials.gov 原生事实
  * Reference: prd-v0.1.md:228-248, 305-334
* 完成 ChEMBL/DrugCentral 派生数据展示与再分发许可审查
  * Reasoning: 两者使用 ShareAlike 许可，多源快照的公开交付方式需要确认
  * Reference: [ChEMBL 37 license](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/LICENSE)
* 定义 complex/fusion、cell/gene therapy、vaccine 和 combination product 的首版支持矩阵
  * Reasoning: Open Targets 和 ChEMBL 都存在明确 target/modality ceiling
  * Reference: .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md
* 在固定快照上测量在线 API 与构建时 snapshot 的延迟、失败率和 schema drift
  * Reasoning: 推荐构建时冻结小型 relation snapshot，但尚未实测运行预算
  * Reference: prd-v0.1.md:547-555

## Final Recommendation

在当前 PRD 产品语义不变的前提下，将**可追溯的关系判定**作为 MVP 的显式必做能力。对本研究选定的一至两周固定场景切片，采用构建时冻结的 target-to-intervention JSON snapshot，是补回已验证 direct-query 漏项且控制工程范围的推荐实现；它不是所有检索架构的唯一必要实现。运行时并行执行 target-text 与 mapped-intervention 查询，之后做 trial-level role/relevance gate 和 NCT 精确回查。

不要把“映射”实现成独立 LLM Agent，也不要在首版构建完整知识图谱。不要用单一 Open Targets 或 ChEMBL 作为真相源，TL1A 的零命中已否证该方案。不要把 condition-first 作为默认在线路径，候选池规模和审核负担过高。不要用 A/B 命中数声称真实召回率。

PRD 的准确覆盖结论是：**用户结果显式覆盖，关系/映射能力属于隐含依赖，映射工程契约和质量验收在原始需求中缺失。** 若产品负责人决定不增加关系层，也不采用 condition-first 等替代关系判定路径，就必须同步收窄 PRD：只做靶点文本候选发现，将临床/竞争层的完整建议固定为 `Need More Data`，并明确零结果不代表无相关试验。
