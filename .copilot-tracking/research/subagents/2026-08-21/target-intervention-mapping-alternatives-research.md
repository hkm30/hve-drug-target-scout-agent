<!-- markdownlint-disable-file -->
# Drug Target Scout target-to-intervention mapping 可行实现路径研究

结论基线日期：2026-08-21。

## 研究状态

完成。七条路径、推荐架构、召回边界、基准测试和一手/官方来源均已记录。Pharos 数据许可作为未决问题保留，不影响推荐架构。

## 研究问题

* 比较不做映射、人工种子词典、Open Targets Platform、ChEMBL、多源联合、LLM/Web 动态候选和 condition-first 全量召回后重排七条实现路径。
* 对每条路径核验数据模型、目标标识符解析、药物与生物制剂覆盖、别名归一化、许可与使用条款、更新与可重放性、延迟、工程复杂度、召回漏项、精度代价和 1 至 2 周 DEMO 适用性。
* 不虚构绝对召回率，用可验证的 recall ceiling、failure modes 和建议基准测试表达取舍。
* 选择推荐架构，并解释 mapping 为什么必要但不充分，或在什么条件下可以省略。

## 本地上下文

* prd-v0.1.md
* .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md

## 待核验的一手与官方来源

* Open Targets Platform 数据模型、GraphQL API、下载、许可和发布说明（已核验）
* ChEMBL Web Services、数据模型、下载、许可和发布说明（已核验）
* DrugCentral、NCATS Pharos、RxNorm 和 PubChem 的官方能力边界与许可（已核验；Pharos 数据许可仍未明确）
* 目标标识符和别名权威来源，包括 HGNC、Ensembl、UniProt 和相关 cross-reference（已核验）

## 发现与证据

### 结论摘要

推荐在 1 至 2 周 DEMO 中实现一个“可追溯的混合候选生成器”，而不是依赖单一映射源，也不是完全取消映射：

1. 先用 Open Targets `mapIds` 解析用户靶点，并用 HGNC 快照确认 human gene 的 approved/previous/alias symbol、Ensembl、UniProt 和 Entrez ID。
2. 以 Open Targets `drugAndClinicalCandidates` 作为低延迟主候选源，以固定版本 ChEMBL mechanism snapshot/API 作为独立补充。
3. 保留一个很小的人工种子层，只覆盖 DEMO 靶点的已知结构化源缺口、研发代码和必须展示的失败案例，不把它伪装成通用知识库。
4. 用候选药物的规范名、商品名和研发代码查询 ClinicalTrials.gov `query.intr`，同时保留 target/同义词/机制词的 `query.term` 查询。两路候选取并集并去重。
5. 对结构化 mapping 稀疏或冲突的 target-condition pair，再执行 condition-first 候选池并重排。不得默认对所有条件全量拉取，因为本轮官方 API 快照显示候选池可扩大一个至三个数量级。
6. DrugCentral 可作为直接 target-drug 补源；RxNorm 只做临床药名/RxCUI/品牌归一化；PubChem 只做结构、同义词和 BioAssay 补漏；Pharos 先作为实验性补充；LLM/Web 只能提出待验证候选。

Mapping 在本场景中是**必要但不充分**的。必要性来自 ClinicalTrials.gov 没有独立 molecular target 字段，很多试验只写药名或研发代码；不充分性来自单源知识库的覆盖、模态、时效、复合靶点和新候选缺口，而且 target-drug 关系本身不证明该药在用户指定疾病中的相关性。

### 证据分级

| 级别 | 含义 |
|---|---|
| 已验证 | 官方文档明确说明，或官方 API/发布包的可重复响应直接证实 |
| 条件性结论 | 在记录日期、查询式、release 或样例范围内成立，不能外推为总体召回率 |
| 仍需项目验证 | 依赖目标样本、延迟预算、许可审查或人工相关性判定 |

### Open Targets Platform

* 数据模型已验证：Target 的主标识符是 Ensembl gene ID。官方 Target 文档明确指出 human targets 来源于 Ensembl，范围包括 protein-coding genes、RNA 和 pseudogene，但当前 target entity 不涵盖 gene fusion 或 protein complex。
* ID 解析已验证：2026-08-21 对官方 GraphQL `mapIds` 的实测中，`GLP-1R`、`TL1A`、`PCSK9` 分别映射到 `ENSG00000112164`、`ENSG00000181634`、`ENSG00000169174`，命中名称分别为 GLP1R、TNFSF15、PCSK9。API 元数据返回 `26.6.3`，data release 为 `26.06`。
* 别名模型已验证：当前 `Target` schema 含 `synonyms`、`symbolSynonyms`、`nameSynonyms`、`obsoleteSymbols`、`obsoleteNames`、`proteinIds` 和 `dbXrefs`。自由文本映射命中含 score，但 score 为 1 不能替代人工歧义检查。
* 药物关系已验证：26.06 将旧 `knownDrugs` 字段替换为 `Target.drugAndClinicalCandidates`。官方文档说明该数据集由 drug-target mechanism 与 drug-disease clinical report join 而来。GLP1R 实测返回 17 个候选，包括 small molecule danuglipron 和多种 `Protein` 药物；semaglutide 记录返回 ChEMBL/AACT 别名、商品名、`AGONIST` 机制及 Ensembl target。
* 覆盖边界已验证：Platform 的 Drug 是经过条件筛选的 ChEMBL 子集，只纳入已知 indication、已知 target、DrugBank 分子或 chemical probe。官方说明可覆盖 small molecules、antibodies、oligonucleotides 等，但不表示 vaccines、blood products、cell therapies；multi-ingredient drug 只可能以各 active moiety 表示。
* Target 边界已验证：当前 target entity 不处理 protein complex 和 gene fusion。这是源级 recall ceiling，不是查询优化可以补救的漏项。
* 单源漏项已验证：HGNC 能将 TL1A 解析为 TNFSF15（Ensembl `ENSG00000181634`、UniProt `O95150`），但 2026-08-21 的 Open Targets `drugAndClinicalCandidates` 返回 0。同期 ClinicalTrials.gov 的人工药名/代码检索返回 26 条。这说明 Open Targets 的 0 命中不能解释为“没有临床干预”。
* 更新与可重放性已验证：官方按 release 发布分区 Parquet 下载和历史归档。26.06 发布于 2026-06-24，含 ChEMBL 37；GraphQL 文档明确建议单实体查询用 API，系统性多实体查询用下载或 BigQuery。API schema 会变化，`knownDrugs` 到 `drugAndClinicalCandidates` 的变化已经实测触发 400。
* 许可已验证：Platform 数据标记为 CC0 1.0，代码为 Apache 2.0。Terms of Use 同时要求尊重原始数据所有者权利并进行良好科学实践归属；下载/再分发时仍应保存来源与 release 信息。

### ChEMBL

* 数据模型已验证：`target`、`mechanism`、`molecule` 是可链式查询的独立资源。GLP1R target search 返回 `CHEMBL1784`，其 component 含 UniProt `P43220`、gene symbol `GLP1R` 和 `GLP-1-R`、`GLP-1R`、`GLP-1 receptor` 等同义词。
* ID 解析边界已验证：ChEMBL target 的外部稳定入口是 ChEMBL target ID，protein target 主要以 UniProt accession 连接。protein complex/family 可含多个 accession，protein variant 与 parent 可共用 target ChEMBL ID，isoform 被映射到 primary UniProt accession。这要求实现保留 target type、component relationship 和 accession 数组，不能强制一对一映射为 gene。
* 机制关系已验证：按 `target_chembl_id=CHEMBL1784` 查询 ChEMBL 37 mechanism 返回 17 条，字段包含 molecule/parent molecule ChEMBL ID、mechanism of action、action type、direct interaction、disease efficacy、max phase 和 reference。官方 Web Services 也给出 approved drug -> mechanism -> target -> assay/activity 的链式用例。
* 药物与生物制剂覆盖已验证：`molecule` 支持 `biotherapeutic` 和 molecule type。semaglutide 返回 `Protein`、蛋白序列、商品名、研发代码、parent hierarchy、max phase 4。API 官方示例提供 `biotherapeutic__isnull=false` 检索。它不是小分子专用源，但 cell/gene therapy、混合产品和未被 ChEMBL 建模的模态仍有上限。
* 召回上限已验证：ChEMBL FAQ 明确部分 assay 因无靶点、歧义、尚未创建或尚未审核而保持 `Unchecked`；protein family/complex 与 variant/isoform 语义也会损失一对一 gene 关系。2026-08-21 的 TNFSF15 target search 返回 0，说明原生 ChEMBL 也会漏掉正在开发的 anti-TL1A 干预。
* 更新与可重放性已验证：当前 ChEMBL 37，官方 status 返回 release date `2026-05-01`。官方提供 SQLite、MySQL、PostgreSQL、SDF、FASTA、RDF、schema、release notes 和 release DOI（ChEMBL 37 为 `10.6019/CHEMBL.database.37`），适合作为冻结的 DEMO snapshot。
* 许可已验证：ChEMBL 37 官方下载目录的 LICENSE 是 CC BY-SA 3.0 Unported。EMBL-EBI Terms 要求归属并提醒原始贡献数据可能有第三方权利。若把修改后的 ChEMBL 数据集再分发，应审查 ShareAlike 义务；仅运行时查询并展示有出处的事实也应保留 ChEMBL 归属。

### 直接和辅助补充源

#### DrugCentral

* 它是直接映射源。官网支持 HUGO gene symbol、UniProt accession、target name 和 SwissProt ID；Target Card 明确展示 drug relations，并区分 mechanism-of-action target 与仅在 bioactivity profile 中出现的 target。
* 当前公开 OpenAPI 含 `act_table_full`、`target_component`、`target_dictionary`、`td2tc`、`structures`、`synonyms` 和 identifier 等资源，可表达 drug-target activity 和 target component。
* 它覆盖 FDA、EMA、PMDA approved drug，也含 veterinary drug 与 bioactivity；不能假设其等价于完整临床候选管线，更不能把 potency hit 全部视为 therapeutic intervention。
* 官网下载页提供 PostgreSQL dump、drug-target interaction TSV、approved drug CSV、SDF 和 SQL 示例，但公开 dump 标签为 2023-11-01。较旧 snapshot 有利于重放，不利于新候选召回。
* 官网许可页为 CC BY-SA 4.0。多源合并并再分发时需评估 ShareAlike；DEMO 可只保存必要派生字段和来源链接，仍应归属。

#### NCATS Pharos/TCRD

* 它可直接表达 target-ligand。NCATS 官方 `pharos-graphql-server` schema 中 Target 以 UniProt 为必填标识，另含 gene symbol、synonyms、xrefs；`Target.ligands(isdrug: Boolean)`、`LigandActivity.moa` 和 `LigandAssocDetails.modeOfAction` 可返回 ligand/activity 关系，Ligand 可标记 `isdrug`。
* Ligand ID 支持 PubChem CID、DrugCentral、Guide to Pharmacology、UNII、name 和 LyCHI 前缀，有利于多源 crosswalk。
* 该关系更接近 target-ligand/activity，不自动等价于已验证 therapeutic mechanism 或目标疾病中的 intervention。需要用 `isdrug`、activity 证据和 condition relevance 二次过滤。
* 官方仓库 README 只给出 DEV GraphQL 实例；前端代码为 MIT，但 GraphQL server 仓库没有 LICENSE 文件。软件许可证不能推导 TCRD 数据许可。本轮产品首页又对自动请求返回 403，因此数据使用、下载版本和服务稳定性需单独确认。
* 结论：可作为实验性补充或人工调查工具，不应成为 1 至 2 周 DEMO 的唯一在线依赖，也不应在许可未确认时打包再分发其数据。

#### RxNorm

* 它不是 target mapping 源。NLM 将 RxNorm 定义为 clinical drug normalized names 与常见药学 vocabularies 的链接；API 资源围绕 RxCUI、名称、ingredient/product/brand、NDC、历史状态和相关 clinical drug concept，没有 molecular target 或 mechanism API。
* semaglutide 官方 API 实测解析为 RxCUI `1991302`。它适合把结构化源生成的候选扩展到品牌、剂型和 RxCUI，也适合规范 ClinicalTrials intervention 文本；它不会生成 target-to-drug 边。
* API 中大多数内容为 NLM 非专有 RxNorm，官方 Terms 表示除 RxClass/SNOMED CT 例外外不需许可，API 免费，要求不超过每 IP 20 rps、建议缓存 12 至 24 小时，并建议展示 NLM 数据免责声明。
* 完整 RxNorm release 有月更和周更、历史下载和 release notes；完整包需要 UMLS license，Prescribable 下载不需要 license。固定 dated release 可重放，直接在线 API 需记录 `/version` 与响应。

#### PubChem

* 它不是直接 therapeutic target-to-intervention 目录。PUG REST 数据域分为 Compound、Substance、Assay、Gene、Protein 等。它确实支持 `assay/target/{geneid|genesymbol|accession}`，也能由 assay 返回 CID/SID，但这条链表达的是 BioAssay target 与 activity，不是药物机制、临床阶段或适应症。
* GLP1R NCBI GeneID 2740 的 target assay 查询实测返回 239 个 AID。该数字是 assay 候选池，不是 239 个药物，也不能用作临床干预召回率。
* 模态边界条件性实测：semaglutide 可按名称解析为 CID `56843331`，pembrolizumab 按 Compound name 返回 404 `No CID found`。PubChem 可覆盖部分结构化肽，但不能假设抗体、细胞、基因和无确定化学结构的生物制剂都进入 Compound。
* PubChem 适合提供 CID、SID、synonym、InChIKey、SMILES、depositor cross-reference 和小分子 assay 补漏。将 active assay compound 纳入 intervention 前必须过滤 assay type、activity、artifact、drug status、mechanism 和疾病上下文。
* 官方 FTP 提供 Compound/Substance full and incremental dump、BioAssay、Target、RDF 和 schema，可保存下载时间与文件哈希重放。NCBI 自身不限制分子数据库数据使用和分发，但明确提醒 PubChem 等资源可能包含第三方贡献或许可内容，用户需遵守权利人条款并归属 NLM。

### Target 标识符解析基线

HGNC 适合作为 human gene target 的确定性解析基线：

* 官方 REST `search` 用于模糊发现，只返回 HGNC ID、symbol 和 score；`fetch` 用 HGNC ID 或确定字段取得完整记录。
* 可检索 approved symbol/name、alias symbol/name、previous symbol/name、HGNC、Ensembl、Entrez、UniProt、RefSeq、RNAcentral 等字段。
* REST 官方限制为 10 rps，`/info` 返回 lastModified、文档数量和可检索字段。
* 完整 TSV/JSON、withdrawn entries 和月度/季度归档公开可下载。HGNC 数据为 CC0，推荐但不强制归属。
* HGNC 只解决 human gene nomenclature。protein complex、fusion、pathogen target、non-gene target 和产品层 intervention 仍需保留原源 ID 与人工确认。

### ClinicalTrials.gov 检索基线和对照样例

* API v2 快照返回 `apiVersion=2.0.5`、`dataTimestamp=2026-08-20T09:00:05`。公开 schema 和上一轮官方研究均未发现独立 molecular target 字段。
* target/同义词/机制词只能走 `query.term` 等文本检索；映射后的药名和研发代码可走 `query.intr`；疾病可走 `query.cond`。这三种候选池语义不同，必须保留 `retrieval_route`。
* 2026-08-21 的 `countTotal=true` 条件性快照如下。A 为 target/同义词文本，B 为人工候选药名/代码，C 为 condition-only。数字只表示给定查询式的候选池规模，不表示真阳性或绝对召回率。

| Target-condition | A: target text | B: mapped interventions | C: condition-only |
|---|---:|---:|---:|
| GLP1R + obesity/T2D | 626 | 1,602 | 25,195 |
| TL1A + IBD/Crohn/UC | 12 | 26 | 4,304 |
| PCSK9 + hypercholesterolemia | 194 | 199 | 1,483 |

* 文本精度失败案例：`query.term=GLP1R` 的首条返回 NCT07446439，实际 intervention 是 Tradipitant，用来治疗 GLP-1R agonist 引起的 nausea/vomiting，而不是靶向 GLP1R 的候选。这是 context mention false positive。
* 映射召回失败案例：TL1A/TNFSF15 在 Open Targets 和 ChEMBL 都是 0 个药物/target 命中，但 ClinicalTrials.gov NCT07158242 的 intervention 是 Afimkibart，other names 为 `PF-06480605`、`RVT-3101`、`RG6631`、`RO7790121`，记录全文不含 TL1A/TNFSF15。PubMed PMID 40706613 的题名明确称其为 anti-TL1A antibody。这类记录只有候选药名或 condition-first 路线能找到。
* 这些样例说明：A、B、C 是互补候选生成器，不能把数量较大的路线视为更准确，也不能把结构化源 0 命中视为无临床活动。

## 路径比较

### 路径 1：不做映射，仅 target/同义词/机制词检索

* 数据模型：只生成文本词袋 `{target input, approved symbol, aliases, full name, mechanism phrases}`，直接查询 PubMed、ClinicalTrials.gov 和 Web，不生成 target-drug 边。
* 目标标识符解析：最低限度仍应解析 HGNC/Ensembl/UniProt，否则 TL1A/TNFSF15、旧 symbol、同名缩写和拼写变体会不可控。若连该步骤也省略，输入歧义无法审计。
* 药物/生物制剂覆盖：理论上不受结构化数据库模态限制，只要记录正文写出 target 或机制词即可；实际对只写药名、品牌、研发代码的 small molecule、antibody、protein、oligonucleotide、cell/gene therapy 都会漏。
* 别名归一化：依赖用户输入、HGNC 或人工规则。机制短语（如 “GLP-1 receptor agonist”）可能召回药物类别和不良反应研究，但无法规范到具体 intervention。
* 许可/条款：不新增映射数据许可，但仍需遵守 PubMed、ClinicalTrials.gov 和 Web 来源条款。没有结构化来源并不等于没有法律责任。
* 更新与可重放性：词袋可版本化；上游搜索结果仍随索引变化。必须保存 query、时间、API version、分页响应和 hash。
* 延迟：最低，通常只增加 target text 查询本身。
* 工程复杂度：最低，适合首日 baseline。
* 召回漏项：recall ceiling 是“注册记录/文献明确出现 target 或所列同义词”的集合，无法触及纯药名/研发代码记录。TL1A/Afimkibart 是已验证漏项。
* 精度代价：target 可能只是背景、伴随用药、不良反应、测量标志或排除条件。GLP1R/Tradipitant 是已验证 false positive。
* 1 至 2 周 DEMO：可作为 baseline 和兜底，不能单独支撑竞争格局结论。

### 路径 2：项目内人工种子词典

* 数据模型：建议每条为 `{canonical_target, HGNC, Ensembl, UniProt[], aliases[], mechanism_terms[], interventions[{canonical_name, aliases[], modality, action, source, verified_at}]}`，每条关系必须有来源和验证日期。
* 目标标识符解析：用 HGNC snapshot 生成 canonical target；人工只裁决歧义、复合靶点和项目展示案例，不能手抄所有基因别名。
* 药物/生物制剂覆盖：可精确加入任何模态，包括结构化源缺失的 antibody、cell/gene therapy、vaccine 和最新研发代码。覆盖上限完全等于人工已录入集合。
* 别名归一化：最适合保存 trial 中真实出现的研发代码、品牌和拼写变体；也最容易产生过时 alias、重复 active moiety 和错误 parent/child 合并。
* 许可/条款：词典中若复制 ChEMBL/DrugCentral 数据，仍受 CC BY-SA 与归属要求；若只保存经人工验证的少量事实、ID 和来源链接，也必须记录 provenance 并做项目法律确认。
* 更新与可重放性：Git/versioned JSON/YAML 最强，可用 review date 和 source snapshot 重放；更新依赖人工，freshness ceiling 最低。
* 延迟：本地 O(1) 查找，最低。
* 工程复杂度：代码低，生物医学维护成本随 target 数线性增加。
* 召回漏项：未播种的新药、新代码、失败/终止项目和非预期模态全部漏；不能外推到任意用户 target。
* 精度代价：小范围可达到高精度，但错误关系会系统性污染所有 trial 查询；必须双人或至少二次来源复核关键关系。
* 1 至 2 周 DEMO：非常适合作为 3 至 10 个演示 target 的 exception layer，不适合作为产品主架构。

### 路径 3：单一开放知识源在线映射，Open Targets Platform

* 数据模型：`free text -> mapIds/search -> Ensembl Target -> drugAndClinicalCandidates -> ChEMBL Drug -> mechanisms/clinical reports/diseases`。
* 目标标识符解析：当前 `mapIds` 可直接把常见 symbol/alias 映射到 Ensembl；Target 还提供 obsolete symbol/name、protein IDs 和 dbXrefs。仍需对多 hit、non-human、complex/fusion 和 0 hit 做人工门控。
* 药物/生物制剂覆盖：覆盖经过筛选的 ChEMBL drug/candidate，小分子、抗体、蛋白、寡核苷酸可见；官方明确不覆盖部分 vaccine、blood product、cell therapy，也不表示 multi-ingredient product。
* 别名归一化：Drug 提供 ChEMBL 与 AACT aliases、trade names、parent/child。AACT alias 有利于 trial recall，但也可能混入类别词或剂量描述，必须分级使用。
* 许可/条款：Platform 数据 CC0、代码 Apache 2.0；仍应归属并保存上游来源/release，遵守 Terms 对原始数据权利的提醒。
* 更新与可重放性：在线 API 低运维但 schema/data 会升级；Parquet release 可完整重放。必须在结果中记录 API `meta`、dataVersion 和 query hash，并有 schema contract test。
* 延迟：单 target 通常是一至数次 GraphQL 网络往返，适合交互；官方不建议逐实体批扫。
* 工程复杂度：低至中等，GraphQL schema、分页、null 和字段漂移处理是主要工作。
* 召回漏项：ceiling 是 Platform 的筛选药物集和 clinical target join。TL1A 0 命中证明新候选/新机制会漏；complex/fusion 和官方排除模态是结构性漏项。
* 精度代价：target-drug mechanism 通常比文本词精确，但 target-drug 不等于 target-drug-condition；多靶点药物、indirect evidence、parent/child 和最高阶段跨适应症传播会造成疾病上下文误判。
* 1 至 2 周 DEMO：最适合主在线源，但必须配 ChEMBL/种子/文本或 condition-first 兜底。

### 路径 4：ChEMBL mechanism/target API 或固定下载

* 数据模型：`target search/component -> target_chembl_id -> mechanism -> molecule/parent -> synonyms/biotherapeutic/max_phase`；如需 potency，可继续 join assay/activity。
* 目标标识符解析：以 UniProt component 和 gene-symbol synonym 对接 HGNC/Ensembl。必须处理 single protein、family、complex、多 component、variant、isoform 和 non-molecular target，不能只取第一个 accession。
* 药物/生物制剂覆盖：小分子和已建模 biotherapeutic 均支持，semaglutide protein 已验证；覆盖比 Open Targets 筛选子集宽，但仍受 ChEMBL curation 和 molecule/target model 限制。
* 别名归一化：molecule synonym type、trade/research code、parent hierarchy 和 target component synonyms 适合生成 trial intervention query；需要把 salt/child、active moiety 和 combination 分开建模。
* 许可/条款：CC BY-SA 3.0，需归属；修改并再分发数据库派生物需评估 ShareAlike。EMBL-EBI 条款也提醒第三方权利。
* 更新与可重放性：在线 API 用 status 锁定版本；下载 release 37 的关系表、schema、release DOI 和文件 hash 可重放性很强。
* 延迟：在线需 target search + mechanism + molecules 多次调用；本地 SQLite/抽取表查询低延迟，但首次下载和 ETL 较重。
* 工程复杂度：API 版中等，download 版中至高。复杂点在 schema join、component 语义、分页和 parent/child 去重。
* 召回漏项：未 curated mechanism、Unchecked assay、新 code name、无 ChEMBL target 和官方未建模模态会漏；TL1A 是已验证 0 hit。
* 精度代价：mechanism relation 高于 assay activity；若把 assay hit 当 mechanism，会引入 off-target、phenotypic、非人源、低 potency 和 artifact。应默认只用 mechanism，BioAssay 另作低置信补源。
* 1 至 2 周 DEMO：推荐在线 API 或只下载小型已抽取 mechanism/target/molecule snapshot；不建议首周导入全量 activity。

### 路径 5：多源联合

* 数据模型：以 canonical target graph 和 candidate intervention graph 联合 Open Targets、ChEMBL、DrugCentral、可选 Pharos；RxNorm、PubChem 作为 ID/alias/activity enrichment。所有 edge 带 `source`, `source_release`, `relation_type`, `action`, `modality`, `evidence_ref`, `confidence_tier`。
* 目标标识符解析：HGNC/Ensembl 作为 human gene 主键，UniProt 数组连接 ChEMBL/DrugCentral/Pharos，保留 ChEMBL target ID、HGNC ID、Entrez Gene。complex/fusion/non-human target 用 typed ID，不强行压成 gene。
* 药物/生物制剂覆盖：结构化源的并集扩大 ceiling。Open Targets/ChEMBL 覆盖 small molecule、protein/antibody/oligo；DrugCentral偏 approved/bioactivity；Pharos偏 target-ligand；RxNorm偏 clinical drug concepts；PubChem偏有结构 compound/assay。仍不能宣称覆盖 vaccine、cell/gene therapy、最新隐秘管线或所有 combination。
* 别名归一化：先按源内 stable ID/parent hierarchy 去重，再用 RxCUI、InChIKey/CID、UNII、ChEMBL ID 和名称交叉验证。名称相同不应自动 merge，不同 salt/formulation 不应自动拆掉临床意义。
* 许可/条款：最复杂。Open Targets/HGNC 为 CC0；ChEMBL CC BY-SA 3.0；DrugCentral CC BY-SA 4.0；NCBI 数据含第三方权利提醒；RxNorm full release 有 UMLS 条款；Pharos 数据许可本轮未确认。运行时查询、内部缓存与公开再分发是不同法律场景。
* 更新与可重放性：必须建立 per-source manifest、release/version、download URL、timestamp、hash、schema version 和 normalization code version。在线多源即时 union 不保存原始响应则不可重放。
* 延迟：并行在线请求的 p95 取决于最慢源和重试；本地 snapshots 快但占构建时间。应设 source timeout 和 partial-result policy。
* 工程复杂度：最高，ID resolution、冲突、许可、source weighting、去重和 freshness 都需显式规则。
* 召回漏项：ceiling 是各源关系并集，能缓解单源 0 hit，但共同盲区仍存在；低更新频率源不能补最新候选。
* 精度代价：activity、prediction、mechanism、label indication 和 trial mention 不是同一关系。若不分 relation type，联合越多误报越多。
* 1 至 2 周 DEMO：只适合“窄多源”：Open Targets + ChEMBL + 小种子，DrugCentral 可选。不要同时产品化 Pharos、RxNorm、PubChem 全链路。

### 路径 6：LLM/Web 动态生成候选，仅作补充

* 数据模型：`{candidate_name, aliases, claimed_target, claimed_action, modality, evidence_urls, generated_by, model, prompt_hash, generated_at, verification_state}`。未经验证的候选不能进入最终 evidence set。
* 目标标识符解析：先由 HGNC/Open Targets 解析 canonical target，再把 ID、approved name 和 aliases 放入 prompt/search；禁止让 LLM 自行决定 canonical ID。
* 药物/生物制剂覆盖：理论上可发现最新抗体、cell/gene therapy、公司 code 和新闻稿，突破结构化 release lag；ceiling 受 Web 可见性、索引、付费墙、模型知识截止和 query 影响。
* 别名归一化：LLM 可提出变体但容易合并不同产品或发明不存在的 code。所有 alias 必须回查 sponsor trial record、监管标签、公司管线页、PubMed 或结构化源。
* 许可/条款：需遵守搜索提供商、网页、模型和内容许可。摘要事实与复制受保护文本不同；只保存必要元数据、短摘录和链接，并记录来源。
* 更新与可重放性：Web 索引和页面可变；Microsoft 官方明确默认输出非确定，即使 seed 与 `system_fingerprint` 相同也不保证确定性。必须保存 prompt、模型/deployment、参数、fingerprint、原始响应、搜索结果和网页快照/hash。
* 延迟：最高且方差大，常需搜索、页面读取和二次验证。
* 工程复杂度：生成候选很低，做可信验证和审计为中至高。
* 召回漏项：可补最新公开候选，但没有可定义的稳定 ceiling；隐藏管线、无索引代码、术语歧义仍会漏。
* 精度代价：hallucinated drug、错误 target、同名公司/产品、旧 code、preclinical assay 被误称临床药物。必须设置 `UNVERIFIED` 隔离区。
* 1 至 2 周 DEMO：适合作为“structured sources sparse 时点击补充”的可选流程，不应默认执行或直接驱动结论。

### 路径 7：condition-first 全量召回后重排

* 数据模型：先按 `query.cond` 遍历全部 trial，抽取 NCT、intervention name/otherNames/description、标题、摘要、phase/status/sponsor/date，再对 target relevance 重排。
* 目标标识符解析：target canonical ID 仍需 HGNC/Open Targets；重排特征使用 target aliases、mapped drugs、mechanism terms 和 evidence-backed LLM classification。
* 药物/生物制剂覆盖：只要记录属于条件且 intervention 有文本，就不受外部 mapping 模态限制，理论 ceiling 高于 target/drug query；但 registry condition indexing、历史记录完整度和错误 condition 标签仍是上限。
* 别名归一化：可直接从每条 trial 的 intervention/otherNames 学习新代码，再回查结构化源或原始资料；同名 placebo、procedure、behavioral intervention 和 formulation 会增加归一化负担。
* 许可/条款：主要受 ClinicalTrials.gov API 与再利用政策约束；若重排使用外部知识和 LLM，再叠加其条款。
* 更新与可重放性：保存所有分页响应、`dataTimestamp`、nextPageToken 链、query 和 hash 可以重放；只保存排序结果不足以审计漏项。
* 延迟：最高。条件池实测为 GLP1R 25,195、TL1A 4,304、PCSK9 1,483，分页、解析和模型重排成本显著。
* 工程复杂度：数据抓取中等，可靠重排与人工验收高。需要处理 observation、device、procedure、behavioral、placebo、background therapy 等类型。
* 召回漏项：ceiling 是 condition query 返回全集；如果 condition 过窄、ontology 不匹配或 trial 尚未公开，仍会漏。它也不能证明每个 condition trial 的 target。
* 精度代价：极高，绝大多数 condition trial 与指定 target 无关。重排器若过度依赖 target mention，又会重新制造路径 1 的漏项。
* 1 至 2 周 DEMO：不适合作为默认主路径。适合作为 sparse/zero-result 安全网，或离线 benchmark 的高-ceiling candidate pool；应设置记录上限、日期/phase/status 过滤和人工 review budget。

## 推荐架构

### 推荐：可追溯的分层混合映射与召回

```text
User target + condition
Stage 1: Target Resolver
Open Targets mapIds
HGNC snapshot/search+fetch validation
Canonical bundle: HGNC, Ensembl, UniProt[], Entrez, symbols/aliases, target type
Stage 2: Candidate Generators in parallel
Open Targets 26.06 drugAndClinicalCandidates (primary fast path)
ChEMBL 37 mechanism by target component (independent supplement)
Versioned manual exception seed (DEMO targets only)
Target/synonym/mechanism text terms (baseline/fallback)
Optional DrugCentral direct target-drug supplement
Optional verified LLM/Web discovery only when sparse
Stage 3: Candidate Normalizer
ChEMBL parent/child and aliases
Optional RxNorm brand/RxCUI normalization
Optional PubChem CID/InChIKey enrichment for structured molecules
Stage 4: ClinicalTrials.gov Retrieval
query.intr(mapped canonical names + verified aliases/codes)
query.term(target + synonyms + mechanism terms)
Condition-first pool only when sparse or for benchmark
Stage 5: Union + deterministic dedupe + provenance
Stage 6: Re-ranker
Explicit intervention alias match
Verified target-mechanism edge
Condition match and trial metadata
Negative/context-only rules
LLM relevance classification with cited input, never sole gate
Stage 7: Human review for ambiguous target and top evidence
Stage 8: Report with route/source/release/query/citation
```

### 为什么选择该架构

* Open Targets 提供最快的 target resolution 与临床候选图，开发量最低。
* ChEMBL 是 Open Targets 药物层的重要上游，但直接读取可见更完整的 mechanism、target component、molecule hierarchy 和固定 release，可作独立 cross-check。
* 人工种子只承担结构化源已知缺口。TL1A 案例证明这个 exception layer 对 DEMO 有实际价值。
* target text 与 mapped intervention 两路并行，分别覆盖“记录写 target”与“记录只写药名/代码”的情况。
* condition-first 不默认全跑，避免把 1,483 至 25,195 条候选交给模型；它作为 sparse fallback 和 benchmark ceiling 更合理。
* 每条候选必须保留 provenance 和 relation type，避免把 PubChem activity、Pharos ligand、ChEMBL mechanism、DrugCentral MoA、trial mention 混成同一种事实。

### Mapping 必要但不充分

Mapping 必要：ClinicalTrials.gov 没有 molecular target 字段，Afimkibart 试验只写药名与研发代码；不建立 target-to-intervention 关系就无法稳定召回。

Mapping 不充分：

* Open Targets 和 ChEMBL 对 TL1A 均为 0，而临床试验和论文已经存在。
* 映射源有 release lag、模态排除、复合靶点/变体语义和 curation 缺口。
* target-drug relation 不含用户指定 condition 的充分证明；最高临床阶段可能来自其他适应症。
* mapping 召回还会漏 registry 新 code、class-only wording 和未规范化组合产品。
* 因此最终相关性必须结合 trial condition、intervention 字段、机制证据、状态/阶段和原文引用重排。

### 可以省略 mapping 的边界

只有当 DEMO 明确降级为“靶点文本证据检索”，不声称完整展示临床管线/竞争格局，并在 UI 明示“只返回显式提到 target/同义词的记录”时，mapping 才可以省略。此时输出不得把 0 条 trial 解读为无临床开发活动。

## 建议基准测试

### 目标

不设未经验证的“绝对召回率”目标。评估每条路径在固定数据快照和人工裁决 gold set 上的可观察 recall ceiling、precision、review burden、freshness 和 reproducibility。

### Gold set

选择 6 至 10 个 target-condition pair，至少覆盖：

* 成熟、机制明确且多药物的 protein target：GLP1R
* 新兴 antibody target 且结构化源出现 0 hit：TL1A/TNFSF15
* 多模态 target：PCSK9（antibody、siRNA/oligonucleotide、小分子或其他候选）
* 一个 protein complex/family 或 fusion target，测试 gene-only resolver ceiling
* 一个 cell/gene therapy 或 vaccine 相关 target，测试 Open Targets Drug 模态排除
* 一个高歧义 symbol/alias，测试 identifier resolution

每个 pair 由人工从 ClinicalTrials.gov condition pool、监管标签、公司管线页和 PMID 回查建立：

* canonical target bundle
* verified intervention 列表与 aliases/research codes
* verified relevant NCT 列表
* relation evidence 与 modality
* 排除项及原因（背景提及、不良反应处理、biomarker、off-target、非治疗 assay 等）

### 指标

| 指标 | 定义 |
|---|---|
| Target resolution accuracy | 输入 alias 是否解析到正确 canonical target；多 hit/0 hit 单独统计 |
| Intervention candidate recall | 给定 source release 能找回 gold interventions 的比例，按 modality 分层；只对 gold set 报告 |
| Trial recall | 候选查询并集找回 gold NCT 的比例；报告 target-only、mapping-only、union、condition-first ceiling |
| Precision@K | Top 10/20/50 中人工确认 target-condition relevant 的比例 |
| Review burden | 每找回一个 relevant NCT 需人工检查的候选数；condition-first 尤其重要 |
| Freshness lag | intervention 首次可验证公开日期到 source release/在线映射可见日期的间隔 |
| Provenance completeness | 候选是否有 source、release、relation type、ID、query 和 evidence reference |
| Modality coverage | small molecule、antibody/protein、oligo/RNA、cell/gene/vaccine、combination 分层命中 |
| Reproducibility | 同一 snapshot/query/code 重跑的 ID 集一致性；在线/LLM 路线记录 Jaccard 与变化原因 |
| Latency/reliability | 每路线 p50/p95、超时、429/5xx、部分失败率和缓存命中率 |

### 必测 failure modes

* Alias drift：TL1A -> TNFSF15、旧 symbol、连字符和大小写变化
* Context mention：治疗靶向药不良反应但不作用于目标的 trial
* Drug-only registry：NCT 只写药名/研发代码，不写 target
* Multi-target：双/三激动剂或多靶点小分子
* Parent/child：盐、剂型、active moiety、品牌、组合制剂
* Modality gap：antibody、protein、oligonucleotide、cell/gene therapy、vaccine
* Target model gap：complex、family、fusion、variant、isoform、non-human target
* Evidence-type confusion：mechanism vs bioactivity vs prediction vs text mention
* Freshness lag：最新 trial/company code 尚未进入结构化 release
* Source conflict：不同 source 对 action、target、phase 或 parent molecule 不一致

### DEMO 验收建议

* 不设全行业绝对 recall 门槛。先要求推荐 union 在预先裁决的 6 至 10 个 pair 上不低于任何单一路线，并公开每个漏项原因。
* Top 20 作为用户可审查界面，另展示“候选总数”和 retrieval route；不要只展示模型排序分数。
* 若 Open Targets + ChEMBL + seed 都为 0，自动触发 target-text 和 condition-first bounded fallback，并把结论降级为 Need More Data。
* 每次演示固定 Open Targets data version、ChEMBL release、HGNC snapshot、ClinicalTrials data timestamp、query 和 seed dictionary commit。
* LLM/Web 生成项只有在至少一个权威/一手来源确认候选名称和 target relation 后，才能进入 trial query 的高置信词表；否则只能显示“待验证线索”。

### 条件性计数实验的可重放输入

下列输入用于 2026-08-21 的 ClinicalTrials.gov API v2 `countTotal=true` 候选池规模实验。它们不是 gold set，也不证明某条 mapping 来源有对应的 recall；B 词表是当时人工组合的已知名称/研发代码，用途仅是比较检索路线的候选量级。所有请求同时传入表中 condition，并只读取 `NCTId` 计数。

| Pair | A: `query.term` | B: `query.intr` | C |
|---|---|---|---|
| GLP1R + obesity/T2D | `GLP1R OR "GLP-1R" OR "glucagon like peptide 1 receptor" OR "glucagon-like peptide 1 receptor"` | `exenatide OR "AC-2993" OR "exendin-4" OR albiglutide OR "GSK-716155" OR taspoglutide OR "RO-5073031" OR dulaglutide OR "LY-2189265" OR lixisenatide OR "AVE-0010" OR "ZP-10" OR semaglutide OR "NN-9535" OR pegapamodutide OR "LY-2944876" OR liraglutide OR "NN-2211" OR efinopegdutide OR "HM-12525A" OR "JNJ-64565111" OR cotadutide OR "MEDI-0382" OR tirzepatide OR "LY-3298176" OR avexitide OR "exendin 9-39" OR danuglipron OR "PF-06882961" OR efpeglenatide OR "HM-11260C" OR "SAR-439977" OR pegsebrenatide OR "NLY-01" OR retatrutide OR "LY-3437943" OR survodutide OR "BI-456906"` | `query.cond=Obesity OR Type 2 Diabetes Mellitus` |
| TL1A + IBD | `TNFSF15 OR TL1A OR "TNF superfamily member 15" OR "TNF-like ligand 1A" OR "TNF-like cytokine 1A"` | `tulisokibart OR PRA023 OR "PRA-023" OR afimkibart OR "PF-06480605" OR duvakitug OR "TEV-48574" OR SPY002 OR SPY072` | `query.cond=Inflammatory Bowel Disease OR Crohn Disease OR Ulcerative Colitis` |
| PCSK9 + hypercholesterolemia | `PCSK9 OR "proprotein convertase subtilisin/kexin type 9" OR "NARC-1" OR HCHOLA3` | `"RG-7652" OR alirocumab OR "REGN-727" OR "SAR-236553" OR evolocumab OR "AMG-145" OR bococizumab OR "PF-04950615" OR "RN-316" OR ralpancizumab OR "PF-05335810" OR "RN-317" OR frovocimab OR "LY-3015014" OR tafolecimab OR "IBI-306" OR ongericimab OR "JS-002" OR lerodalcibep OR inclisiran OR "inclisiran sodium" OR "ALN-60212" OR "ALN-PCSSC"` | `query.cond=Hypercholesterolemia OR Familial Hypercholesterolemia` |

最小请求模板：

```http
GET https://clinicaltrials.gov/api/v2/studies
?query.cond=<condition>
&query.term=<A terms>       # A 路线，B 路线改用 query.intr
&pageSize=1
&countTotal=true
&fields=NCTId
```

Open Targets 实测请求使用 GraphQL `meta`、`mapIds(queryTerms, entityNames:["target"])`、`target(ensemblId).drugAndClinicalCandidates` 和 `drug(chemblId).mechanismsOfAction`。ChEMBL 实测请求使用：

```text
GET https://www.ebi.ac.uk/chembl/api/data/status.json
GET https://www.ebi.ac.uk/chembl/api/data/target/search.json?q=GLP-1%20receptor&limit=5
GET https://www.ebi.ac.uk/chembl/api/data/mechanism.json?target_chembl_id=CHEMBL1784&limit=1000
GET https://www.ebi.ac.uk/chembl/api/data/molecule/CHEMBL2108724.json
```

## 未决问题

* DEMO 的公开展示是否构成 ChEMBL/DrugCentral 派生数据库再分发，需要项目法务确认 CC BY-SA 义务和归属方式。
* Pharos/TCRD 数据本身的当前许可、生产 API SLA、版本和下载路径未从可访问的一手页面确认；只有 frontend MIT 许可不能替代数据许可。
* ClinicalTrials.gov condition-first 的最大允许 review budget、日期范围和状态/phase 过滤尚未由产品定义。
* 复合靶点、fusion、cell/gene therapy 和 combination product 在首版是明确标为 unsupported，还是通过人工 seed 支持，需要产品裁决。
* 候选关系的最低证据门槛待定：regulatory label、curated mechanism、primary paper、company pipeline page、trial description 应如何分级。
* 是否允许把 LLM/Web 候选自动加入查询，还是必须 human approval 后运行，需结合“Human in the loop”交互确定。
* 需要实际延迟测试才能决定在线 ChEMBL/DrugCentral 并行调用还是预构建小型 snapshot。本轮未对 API SLA 或吞吐作保证。

## 来源清单

所有外部来源均于 2026-08-21 访问。除特别标注的实测端点外，下列链接为官方文档、官方发布目录、政府站点或项目维护方官方仓库。

### Open Targets Platform

* [Target](https://platform-docs.opentargets.org/target.md)：Ensembl 主标识、target 纳入范围、complex/fusion 缺口
* [Drug](https://platform-docs.opentargets.org/drug.md)：ChEMBL 筛选条件、药物模态、vaccine/blood/cell therapy 与 multi-ingredient 缺口
* [Drugs and Clinical Candidates](https://platform-docs.opentargets.org/target/drugs.md)：clinical target 的 drug-target mechanism 与 drug-disease report join
* [Target-disease evidence](https://platform-docs.opentargets.org/evidence.md)：Ensembl/EFO 标准化与 clinical precedence 推断
* [GraphQL API](https://platform-docs.opentargets.org/data-access/graphql-api.md)：单实体 API、批量下载建议与 endpoint
* [GraphQL schema](https://api.platform.opentargets.org/api/v4/graphql/schema)：`mapIds`、Target、Drug、ClinicalTarget、mechanism 和 version schema
* [GraphQL endpoint](https://api.platform.opentargets.org/api/v4/graphql)：26.06 实测 target resolution、GLP1R candidates 和 semaglutide mechanism
* [Download datasets](https://platform-docs.opentargets.org/data-access/datasets.md)：分区 Parquet、历史 release、FTP/GCS 与格式变更
* [Release notes](https://platform-docs.opentargets.org/release-notes.md)：26.06 日期、ChEMBL 37、metrics 和 pipeline/schema 更新
* [Licence](https://platform-docs.opentargets.org/licence.md)：Platform CC0、代码 Apache 2.0 与上游许可表
* [Terms of use](https://platform-docs.opentargets.org/licence/terms-of-use.md)：归属、服务连续性、原始数据权利与责任边界

### ChEMBL 和 EMBL-EBI

* [ChEMBL Data Web Services](https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services.md)：resources、filters、search、分页、mechanism/target/biotherapeutic 用例
* [Target Questions](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/target-questions.md)：UniProt、complex/family、variant、isoform、Unchecked 和 gene-symbol join
* [Downloads](https://chembl.gitbook.io/chembl-interface-documentation/downloads.md)：ChEMBL 37、数据库格式、RDF、release DOI 和历史版本
* [ChEMBL 37 release directory](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/)：schema、database dumps、FASTA/SDF、release notes
* [ChEMBL LICENSE](https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/LICENSE)：CC BY-SA 3.0 Unported
* [ChEMBL status](https://www.ebi.ac.uk/chembl/api/data/status.json)：release 37、release date 和当前记录规模
* [ChEMBL GLP1R target search](https://www.ebi.ac.uk/chembl/api/data/target/search.json?q=GLP-1%20receptor&limit=5)：CHEMBL1784、P43220、target component aliases
* [ChEMBL GLP1R mechanisms](https://www.ebi.ac.uk/chembl/api/data/mechanism.json?target_chembl_id=CHEMBL1784&limit=1000)：17 条 mechanism、action、phase 和 references
* [ChEMBL semaglutide molecule](https://www.ebi.ac.uk/chembl/api/data/molecule/CHEMBL2108724.json)：Protein、biotherapeutic sequence、synonyms、brand 和 parent hierarchy
* [EMBL-EBI Terms of Use](https://www.ebi.ac.uk/about/terms-of-use)：归属、上游数据所有者与第三方权利

### DrugCentral 与 Pharos

* [DrugCentral](https://drugcentral.org/)：target search 输入、Target Card、MoA target 与 bioactivity target 区分
* [DrugCentral downloads](https://drugcentral.org/download)：PostgreSQL dump、drug-target TSV、approved CSV、SDF 和公开日期
* [DrugCentral license](https://drugcentral.org/privacy)：CC BY-SA 4.0
* [DrugCentral OpenAPI](https://uxn2ycvimg.us-east-2.awsapprunner.com/openapi.json)：activity、target component/dictionary、structure 和 synonym resources
* [NCATS Pharos GraphQL server](https://github.com/ncats/pharos-graphql-server)：官方 API server 仓库和 DEV endpoint 说明
* [NCATS Pharos schema](https://raw.githubusercontent.com/ncats/pharos-graphql-server/master/src/schema.graphql)：Target、Ligand、LigandActivity、ID prefixes 和 target-ligand fields
* [NCATS Pharos frontend LICENSE](https://raw.githubusercontent.com/ncats/pharos_frontend/master/LICENSE)：frontend 软件 MIT 许可；不用于推导数据许可

### HGNC、RxNorm 与 PubChem

* [HGNC REST help](https://www.genenames.org/help/rest/)：search/fetch、alias/previous symbol、cross-IDs、10 rps 和 lastModified
* [HGNC downloads](https://www.genenames.org/download/statistics-and-files/)：完整 TSV/JSON、withdrawn entries 与月度/季度归档
* [HGNC license](https://www.genenames.org/about/license/)：CC0 与推荐归属
* [RxNorm overview](https://www.nlm.nih.gov/research/umls/rxnorm/index.html)：normalized clinical drug names 与 vocabulary links
* [RxNorm API](https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html)：RxCUI、名称、ingredient/product/brand、NDC 和历史 API
* [RxNav Terms of Service](https://lhncbc.nlm.nih.gov/RxNav/TermsofService.html)：许可例外、免责声明、20 rps 和缓存建议
* [RxNorm files](https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html)：月更/周更、历史 release、full 与 Prescribable 下载许可差异
* [RxNorm semaglutide lookup](https://rxnav.nlm.nih.gov/REST/rxcui.json?name=semaglutide&search=2)：RxCUI 1991302 实测
* [PubChem PUG REST](https://pubchem.ncbi.nlm.nih.gov/pcfe/docs/markdown/pug-rest.md)：Compound/Substance/Assay/Gene/Protein domains、target assay 和 operations
* [PubChem FTP README](https://ftp.ncbi.nlm.nih.gov/pubchem/README)：full/incremental Compound/Substance、BioAssay、Target、RDF 和 schema
* [NCBI policies](https://www.ncbi.nlm.nih.gov/home/about/policies/)：public-domain government content、NCBI reuse policy 和 PubChem 第三方权利提醒
* [PubChem semaglutide lookup](https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/semaglutide/cids/JSON)：CID 56843331 实测
* [PubChem pembrolizumab lookup](https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/pembrolizumab/cids/JSON)：404 `No CID found` 实测
* [PubChem GLP1R target assays](https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/target/geneid/2740/aids/JSON)：239 个 AID 的条件性实测

### ClinicalTrials.gov、PubMed 与 LLM 可重放性

* [ClinicalTrials.gov Data API](https://clinicaltrials.gov/data-api/api)：API v2 入口和文档
* [ClinicalTrials.gov OpenAPI](https://clinicaltrials.gov/api/oas/v2)：`/studies`、单条 record、query/filter/fields/pagination schema
* [Complex search queries](https://clinicaltrials.gov/find-studies/constructing-complex-search-queries)：AREA 与组合查询语义
* [NCT07158242](https://clinicaltrials.gov/api/v2/studies/NCT07158242)：Afimkibart intervention 与研发代码、无 TL1A target 文本
* [NCT07446439](https://clinicaltrials.gov/api/v2/studies/NCT07446439)：Tradipitant 治疗 GLP-1R agonist nausea/vomiting 的 context-only false positive
* [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25497/)：ESearch/ESummary 官方接口
* [PMID 40706613](https://pubmed.ncbi.nlm.nih.gov/40706613/)：Afimkibart 为 anti-TL1A antibody 的 Phase 2b 临床试验论文题名证据
* [Azure OpenAI reproducible output](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/reproducible-output)：默认非确定性、seed/system fingerprint 仍不保证确定性