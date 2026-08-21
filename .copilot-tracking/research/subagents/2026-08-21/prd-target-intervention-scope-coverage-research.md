<!-- markdownlint-disable-file -->

# 靶点到干预措施映射范围覆盖研究

## 研究状态

完整。结论基线日期为 2026-08-21。

研究范围限定为对照以下两份工作区文件，不修改原始 PRD，也不把后续技术研究中的工程建议反向解释为原始需求：

* prd-v0.1.md
* .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md

## 研究问题

1. 对照 prd-v0.1.md 与 .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md，判断“靶点到干预措施映射能力”在原始需求中属于显式覆盖、隐含依赖还是完全缺失。
2. 区分用户可见功能承诺、数据源或 Agent 功能、工程实现建议、决策逻辑、MVP 或成功标准。
3. 找出支持“不需要映射，只检索靶点文本即可”的范围解释，并检验其与 PRD 语句的冲突。
4. 给出 PRD 修订清单，但不修改 PRD。
5. 说明没有映射能力时必须降级的输出声明。

## 执行摘要

总体分类是 **隐含依赖**，不是“显式覆盖”，也不是“完全缺失”。

更精确地说，PRD 显式承诺了映射后的用户结果，包括“与靶点、机制、适应症相关的临床试验”、干预信息、当前临床进度、竞争格局、积极或失败信号，以及靶点级 Go / No-Go / Need More Data 建议。但是，PRD 没有把“输入靶点解析为干预措施或药物，并以可追溯关系把试验归因到该靶点”定义为独立功能、数据契约、工程步骤或验收标准。因此：

* 用户可见的映射结果承诺是显式的。
* 靶点到干预措施关系本身是这些结果的隐含依赖。
* 映射数据源、关系模型、相关性分级、冲突规则和质量阈值在原始 PRD 中缺失。
* 单纯检索靶点文本并提取命中记录的 intervention 字段，是一种可辩护的窄化 MVP 解释，但只能交付“候选文本命中”，不能继续交付 PRD 当前承诺的靶点级临床归因、竞争判断和完整 Go / No-Go 决策。

控制性证据如下：

* PRD 直接要求临床试验 Agent “找到与靶点、机制、适应症相关的临床试验”，并提取干预方式、识别积极和失败信号：prd-v0.1.md:87-94。
* PRD 的决策规则把 ClinicalTrials.gov 的积极信号、相关临床失败和竞争饱和度作为靶点级 Go / No-Go 依据：prd-v0.1.md:305-334。
* PRD 的 MVP 只写了 ClinicalTrials.gov 检索、LLM 汇总和最终建议，并排除了复杂图谱分析，没有写靶点到干预措施映射：prd-v0.1.md:524-545。
* 技术研究已经证实 ClinicalTrials.gov API v2 没有独立分子靶点字段，靶点词命中不等于目标机制匹配：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:7-14, 274-287。
* 技术研究提出的 target/drug synonym 查询和机制相关性重排属于后续工程补偿方案，不是 PRD 原有显式要求：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:363-387, 650-658。

## 判定口径

本研究使用以下分类口径：

| 分类 | 判定标准 |
|---|---|
| 显式覆盖 | PRD 明确命名该能力，并至少定义可识别的输入、处理、输出或可验收行为 |
| 隐含依赖 | PRD 显式承诺的结果无法可靠产生，但 PRD 没有单独定义该能力或质量门槛 |
| 完全缺失 | PRD 既没有承诺依赖该能力的结果，也没有定义相关处理、字段或验收行为 |

本研究把“靶点到干预措施映射”定义为：从输入靶点及其规范化身份出发，发现一个或多个药物、分子、抗体、程序或其他干预措施，并保存可审计的靶点、作用机制、干预措施、临床试验之间的关系及来源。仅在 ClinicalTrials.gov 全文中命中靶点字符串，然后读取同一记录的 intervention 字段，不足以证明该 intervention 作用于该靶点。

## 分层覆盖判定

### 用户可见功能承诺

结论是“结果层显式覆盖，能力层隐含依赖”。

PRD 的背景问题不是泛化的试验搜索，而是询问“这个靶点”是否有相关临床信号、竞争是否拥挤，以及是否值得继续投入：prd-v0.1.md:8-16。总体目标进一步要求用户只输入靶点名称，系统自动检索临床试验并给出带引用的 Go / No-Go / Need More Data：prd-v0.1.md:26-39。

两个用户场景也将输出绑定到输入靶点：GLP-1R 场景要求“相关试验概况”，TL1A 场景要求“当前临床进度”“竞争拥挤程度”和是否值得跟进：prd-v0.1.md:114-140。前端固定展示总体建议、试验表格、阶段或状态统计、竞争与风险：prd-v0.1.md:443-487。

这些都是用户可见的显式承诺。但 PRD 没有告诉用户结果是基于直接映射、文本命中还是模型推断，也没有让 UI 暴露关系类型或映射覆盖率。因此，承诺的语义强于其定义的能力。

### 数据源与 Agent 功能

结论是“字段抽取显式，关系建立缺失”。

PRD 明确把 ClinicalTrials.gov 定义为必选数据源，并要求提取阶段、状态、适应症和干预：prd-v0.1.md:163-174。临床试验 Agent 的输出和最低实现要求包括相关试验列表、积极或失败信号、NCT、阶段、状态、适应症和干预：prd-v0.1.md:228-248。

最强的映射意图证据是 Agent 需要“找到与靶点、机制、适应症相关的临床试验”，再提取干预方式：prd-v0.1.md:87-94。这清楚表达了结果语义，却没有定义关系是如何建立和验证的。

技术研究给出了关键反证：ClinicalTrials.gov v2 只支持 intervention、condition 和文本查询，没有独立 molecular-target 字段；因此 target text hit 不能标记为 structured target match：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:274-287。该研究要求把靶点词命中标为候选相关性，并另做同义词和机制相关性重排：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:363-387。

因此，ClinicalTrials.gov 能显式提供 intervention 字段，但不能独自提供 PRD 所需的 target-intervention relation。字段共现不能自动升级为药理关系。

### 工程实现建议

结论是“原始 PRD 未覆盖映射实现，后续研究补充了建议”。

PRD 的工程路径是官方 API 优先、搜索适配层和 LLM 汇总：prd-v0.1.md:175-190, 558-574。系统流程只描述输入靶点、查询 PubMed/Scholar/ClinicalTrials.gov、返回结构化 JSON 和汇总报告，没有 target normalization、intervention expansion、relation evidence 或映射验证步骤：prd-v0.1.md:388-429。

对 PRD 进行定向搜索，查询式为 `映射|ontology|知识图谱|图谱|target match|target ontology|机制相关性|药物别名|干预.*靶点|靶点.*干预`。唯一命中是 MVP 不做“复杂图谱分析”：prd-v0.1.md:544。该非目标只排除了复杂图谱，不能证明最小映射表、规则关联或证据化关系也被排除。

技术研究中的 Query Planner、target/drug synonyms、mechanism relevance ranking 和 Target-mechanism relevance 规则，是为弥补上述缺口提出的项目设计：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:363-387, 474-524, 580-588。其最终建议也明确要求修改 PRD，将靶点检索改写为候选召回并另设机制相关性排序：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:650-658。

后续研究建议不能反向证明原始 PRD 已显式覆盖映射能力。它只能证明工程团队已经识别到这项隐含依赖。

### 决策逻辑

结论是“强隐含依赖”。

PRD 的 Go 条件包含正向生物学机制、ClinicalTrials.gov 积极临床信号和未完全饱和的竞争；No-Go 条件包含机制不足、相关临床失败或终止，以及差异化不足：prd-v0.1.md:305-325。最终结论还必须说明原因、证据来源和不确定性：prd-v0.1.md:327-334。

这些规则只有在每条临床记录能够被合理归因到输入靶点时才成立。否则：

* 一个试验的积极结果可能属于相同疾病但不同机制的干预措施。
* 一个 terminated 状态可能与安全性、招募、商业原因或非目标机制相关，不能自动变成该靶点的失败信号。
* 试验数量和阶段分布不能自动变成该靶点的竞争拥挤度。
* 干预措施之间的差异化无法从靶点文本共现推导。

技术研究同样说明 phase/status 到积极、失败或不确定信号的业务映射未在 PRD 中定义，仍是假设：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:274-287。即使引用真实存在，也不能从 existence verification 推导药物靶点相关性、试验可信度或 Go/No-Go 质量：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:623-637。

### MVP 与成功标准

结论是“交付结果显式，映射验收缺失”。

MVP 必做项明确包含输入靶点、ClinicalTrials.gov 检索、LLM 汇总和 Go / No-Go / Need More Data；不做项包含复杂图谱分析：prd-v0.1.md:524-545。成功标准要求用户输入靶点后能看出临床信号，并给出初步建议：prd-v0.1.md:547-555。

但是，MVP 和成功标准都没有要求：

* 识别不含靶点文本但其干预措施已知作用于该靶点的试验。
* 区分 direct、inferred、text-only 和 unknown 关系。
* 给出映射来源、证据和置信度。
* 测量 target-intervention 或 target-trial 相关性的 precision、recall 或误归因率。
* 在映射失败时强制决策降级。

所以，MVP 可以按字面实现成文本检索原型，但不能同时按当前成功标准声称已验证靶点级临床信号和完整立项建议。

## 支持“只检索靶点文本”的范围解释

以下语句可支持一个窄化解释，即 MVP 不做独立映射，只使用靶点及别名查询文本并抽取命中记录：

| 支持依据 | 可支持的解释 | 边界 |
|---|---|---|
| PRD 定位为快速搭建的 DEMO 和立项早筛原型：prd-v0.1.md:1-4, 43-55 | 产品可优先证明链路和展示能力 | 早筛不等于可以把候选文本命中表述成已确认靶点关系 |
| 输入允许用户给出靶点同义词或别名：prd-v0.1.md:145-157 | 查询可以直接用 target 和 alias 做关键词扩展 | 别名扩展只能改善靶点词召回，不能发现只写药物名的试验 |
| 临床 Agent 的最低实现要求只写“支持 ClinicalTrials.gov 检索”并提取字段：prd-v0.1.md:243-248 | 最低工程闭环可以是搜索加字段解析 | “相关临床试验”“积极/失败信号”是更强的上层输出承诺 |
| 系统流程只写去 ClinicalTrials.gov 找临床信号，再交给 LLM 汇总：prd-v0.1.md:388-429 | 原型可以不引入独立知识服务 | LLM 汇总不能凭空证明 target-intervention relation |
| MVP 不做复杂图谱分析：prd-v0.1.md:524-545 | MVP 无需构建复杂知识图谱 | 最小映射不必是复杂图谱；可以是有来源的关系表或受控推断 |
| 第一阶段只要求接 API 并让 LLM 总结：prd-v0.1.md:558-566 | 第一演示版本可以先跑 target-text query | 若保留当前输出名，就会把检索能力包装成映射能力 |
| 技术研究称现有 API 足以支持摘要级 DEMO：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:7-14 | 可以交付“摘要级候选记录检索” | 同一段同时声明相关性、同义词扩展和证据质量仍需项目验证 |

因此，“只检索靶点文本”不是完全不合理。它是一种 **范围降级方案**，而不是对当前 PRD 全部承诺的等价实现。只有把产品输出改名为候选文本命中、明确覆盖限制，并把完整决策强制降级后，这个解释才内部一致。

## 文本检索解释与 PRD 的冲突

| PRD 语句 | 与纯文本检索的冲突 | 证据 |
|---|---|---|
| 找到与靶点、机制、适应症相关的临床试验 | 文本命中只能证明词项出现，不能证明 intervention 作用于 target 或 trial 测试该机制 | prd-v0.1.md:87-94；技术限制见 .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:7-14, 274-287 |
| 输出 GLP-1R 的相关试验概况，输出 TL1A 的当前临床进度 | 纯文本检索会漏掉只使用资产名或药物名、不出现靶点词的试验，也可能混入仅背景提及靶点的试验 | prd-v0.1.md:114-140；召回与相关性仍需验证见 .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:14-14, 138-139 |
| 识别潜在积极信号和失败或风险信号 | 试验状态或结果只有在 relation 成立时才能归因到目标靶点 | prd-v0.1.md:228-248, 305-325 |
| 判断竞争活跃度、拥挤赛道和公司或管线动态 | 竞争资产常以 intervention 或公司项目名出现；无映射时无法形成完整的靶点管线集合 | prd-v0.1.md:96-103, 250-268 |
| 用临床信号和竞争饱和度决定 Go / No-Go | 未确认相关性的候选记录不能作为靶点级决策事实 | prd-v0.1.md:288-334 |
| 成功标准要求看出临床信号并给出初步建议 | 文本召回可以证明系统找到候选记录，不能证明临床信号属于该靶点 | prd-v0.1.md:547-555 |
| 一句话总结声称帮助团队对某个靶点做初步 Go / No-Go | 无映射时最多支持文献与文本命中摘要，不能支持完整靶点立项判断 | prd-v0.1.md:579-583 |

“不做复杂图谱分析”与上述冲突不构成豁免。PRD 排除的是复杂图谱分析，不是所有靶点到干预措施关系。一个最小关系表、受控词典、可追溯外部关系源或明确标记的推断层，都可以在不实现复杂图谱的情况下满足最低映射需求。

## 建议的 PRD 修订清单

以下修订用于消除范围歧义，但本研究不修改 PRD：

* [ ] 在术语表中定义 target、intervention、mechanism、target-intervention relation、target-trial relevance 和 clinical signal，明确“文本命中”不等于“关系确认”。
* [ ] 在 MVP 范围中二选一并明确写出：实现最小靶点到干预措施映射，或仅实现 target-text candidate retrieval。基于当前用户承诺，建议选择前者。
* [ ] 若选择映射模式，新增显式功能需求：规范化靶点身份和别名，发现干预措施，保存 relation type、relation source、evidence citation、confidence 和 checked-at。
* [ ] 指定权威或批准的映射数据源及回退策略。ClinicalTrials.gov 只能作为试验和 intervention 字段权威，不能作为独立 molecular-target relation 权威。具体关系源需要另行研究后在 PRD 中确定。
* [ ] 定义最小关系状态，例如 `DIRECT_VERIFIED`、`INFERRED_WITH_EVIDENCE`、`TEXT_ONLY_CANDIDATE`、`UNKNOWN`，禁止把后两类静默升级为已确认映射。
* [ ] 在临床 Agent 流程中拆开候选召回、关系判定、NCT 存在性回查、相关性排序和信号归因，不让 LLM 一步完成全部职责。
* [ ] 修改临床 Agent 输出 schema，给每个 trial 增加 queried target、intervention、relation status、relation evidence、relevance rationale 和 uncertainty。
* [ ] 明确同一试验存在多个 intervention、组合疗法、多个靶点或仅 biomarker 关联时的归因规则。
* [ ] 明确 phase/status 到积极、失败或不确定信号的业务规则，避免把 terminated 自动等同于靶点失败。
* [ ] 在决策逻辑中加入证据门槛：只有达到允许 relation status 的试验才能计入 target-level clinical signal、competition 和 Go / No-Go。
* [ ] 新增降级规则：没有足够映射证据时，完整立项结论必须为 Need More Data；允许返回文献结论和候选文本命中，但不得输出靶点级临床验证或竞争结论。
* [ ] 在 UI 中展示检索模式、映射覆盖率、每条关系状态和未覆盖警告，使用户能区分 mapped evidence 与 text-only candidates。
* [ ] 更新 MVP 成功标准，分别验收候选召回质量和映射质量。至少定义金样本、Precision@K、Recall@K、错误归因率和未知关系占比；具体阈值由产品与领域专家确认。
* [ ] 更新非目标：可以继续排除复杂知识图谱，但不能用该非目标排除满足当前承诺所需的最小证据化关系层。
* [ ] 更新一句话总结，明确建议是“基于已验证关系的靶点早筛”，或在 text-only MVP 下改为“候选证据发现原型”。

## 无映射时必须降级的输出声明

无映射时，系统仍可返回 PubMed 文献、ClinicalTrials.gov 文本命中记录、NCT、phase、status、condition 和 intervention 原始字段。以下声明必须降级：

| 当前或隐含声明 | 无映射时允许的降级表述 | 无映射时不得声称 |
|---|---|---|
| “与目标靶点相关的临床试验” | “ClinicalTrials.gov 中命中目标靶点或别名文本的候选记录” | 这些试验的 intervention 已确认作用于目标靶点 |
| “当前临床进度” | “候选文本命中记录的 phase/status 快照，可能不完整” | 这是该靶点完整或代表性的临床开发进度 |
| “积极临床信号” | “候选记录中观察到的结果或状态线索，尚未完成靶点归因” | 临床结果验证或支持了目标靶点 |
| “失败/风险信号” | “候选记录中存在 terminated、withdrawn 或负面线索，需要人工核验原因和关系” | 这些记录证明目标靶点失败或存在机制性风险 |
| “竞争活跃程度/拥挤赛道” | “目标词在公开文献、网页和试验文本中的可见活动度” | 已识别完整竞争资产、公司管线或市场拥挤度 |
| “公司/管线公开动态” | “可能相关的公司或资产发现线索” | 公司资产已确认针对目标靶点 |
| “主要机会/主要风险” | “待验证假设和后续调查问题” | 基于完整干预版图得出的机会或风险结论 |
| “Go / No-Go” | 对完整立项决策强制输出 Need More Data；可另给“文献和文本发现层建议” | 基于临床和竞争证据给出目标靶点 Go 或 No-Go |
| “能看出临床信号”成功标准 | “能看出候选试验文本命中及其原始状态字段” | 已验收 target-level clinical signal |
| “带引用的关键结论” | 引用可证明记录存在和原文内容；同时标注 relation 未验证 | 引用存在本身证明该记录与目标靶点存在药理关系 |

文献中的靶点生物学支持可以保留，但必须与干预措施临床验证分开陈述。引用存在性回查也可以保留，但技术研究已明确：引用真实存在不能推出药物靶点相关性、试验可信度或决策质量：.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:623-637。

## 结论证据表

| 维度 | 原始需求覆盖 | 最终分类 | 关键证据 |
|---|---|---|---|
| 用户可见靶点级临床和竞争结果 | 显式承诺 | 显式结果，隐含能力 | prd-v0.1.md:8-16, 26-39, 114-140, 443-487 |
| ClinicalTrials.gov intervention 字段抽取 | 显式要求 | 显式覆盖 | prd-v0.1.md:163-174, 228-248 |
| 靶点到干预措施关系建立 | 未命名、无 schema、无来源 | 缺失的工程契约 | prd-v0.1.md:175-190, 388-429, 524-574 |
| 将试验信号归因到目标靶点 | 决策规则依赖但未定义 | 隐含依赖 | prd-v0.1.md:305-334 |
| 映射质量验收 | 无指标 | 完全缺失 | prd-v0.1.md:547-555 |
| 数据源原生 target 字段 | PRD 默认假设可检索 | 已被技术研究否证 | .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:7-14, 274-287 |
| 候选召回和机制相关性重排 | 技术研究后加建议 | 工程建议，不是原始范围证据 | .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:363-387, 650-658 |

因此，若必须在“显式覆盖、隐含依赖、完全缺失”中只选一个，答案是 **隐含依赖**。若允许分层表达，则答案是：**用户结果显式覆盖，映射能力隐含依赖，映射工程契约和验收标准缺失**。

## 未完成研究

本轮请求的范围分类已完成。以下事项未在本轮开展，因为超出“两份现有文件对照”的原始问题：

* [ ] 评估可作为 target-intervention relation 权威源的公开数据库、API 契约、许可、覆盖和更新频率。
* [ ] 用 GLP-1R、TL1A、PCSK9 等真实靶点构建金样本，测量 target-text retrieval 与 intervention-expanded retrieval 的 Precision@K 和 Recall@K。
* [ ] 定义 direct target、pathway target、biomarker、combination therapy 和 multi-target intervention 的领域归因规则。
* [ ] 与药理、临床和研发立项专家验证最低可接受映射质量及 Go / No-Go 门槛。
* [ ] 验证没有映射时 UI、导出报告和审计日志是否持续显示 `TEXT_ONLY_CANDIDATE` 和覆盖警告。

## 澄清问题

以下问题不影响本轮“隐含依赖”的分类，但需要产品负责人或领域专家决定后才能修订 PRD：

1. MVP 是否必须发现“试验文本没有靶点名称，但 intervention 已知作用于该靶点”的记录？
2. 哪些关系可以计入映射：直接结合、通路调节、biomarker 关联、组合疗法，还是仅直接靶向？
3. 允许使用 LLM 推断 target-intervention relation，还是必须由结构化权威源或人工审核确认？
4. text-only 模式下是否允许出现 Go / No-Go，还是完整决策必须强制 Need More Data？
5. 谁负责提供金样本和批准 Precision@K、Recall@K、误归因率等验收阈值？
