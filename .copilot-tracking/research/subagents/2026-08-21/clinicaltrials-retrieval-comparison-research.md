<!-- markdownlint-disable-file -->
# ClinicalTrials.gov 靶点检索对照研究

## 研究状态

完成。执行日期为 2026-08-21，所有执行时间均为 UTC。

ClinicalTrials.gov 版本端点在 `2026-08-21T06:19:27Z` 返回：

```json
{"apiVersion":"2.0.5","dataTimestamp":"2026-08-20T09:00:05"}
```

版本请求：

```text
GET https://clinicaltrials.gov/api/v2/version
```

原始响应 SHA-256：
`fd313096965bf0c48a8ce92112cf23a516f93ca69c10fcb9e097fb02b4b574ed`。

> [!IMPORTANT]
> ClinicalTrials.gov 是动态数据库。本文所有 count、NCT 集合和差集都是以上数据时间戳附近的时间点快照，不是永久常数。相同请求在未来可能返回不同结果。

## 执行结论

| 靶点 | 适应症口径 | A 去重 NCT | B 去重 NCT | overlap | direct-only | mapping-only | A∪B |
|---|---|---:|---:|---:|---:|---:|---:|
| GLP-1R | Obesity OR Type 2 Diabetes Mellitus | 626 | 1,602 | 463 | 163 | 1,139 | 1,765 |
| TL1A | Inflammatory Bowel Disease OR Crohn Disease OR Ulcerative Colitis | 12 | 26 | 5 | 7 | 21 | 33 |
| PCSK9 | Hypercholesterolemia OR Familial Hypercholesterolemia | 194 | 199 | 122 | 72 | 77 | 271 |

集合定义：

```text
overlap      = A ∩ B
direct-only  = A - B
mapping-only = B - A
```

这些数字说明不同检索策略会产生显著不同的候选集合，但不能说明任何策略的真实 recall。没有经人工判定的完整金标准，就不能把 `totalCount`、去重 NCT 数、B/A 倍数或 C 候选数称为 recall。

主要发现：

* B 对三个靶点都补充了 A 未召回的 NCT，尤其是 GLP-1R 的 mapping-only 为 1,139 条
* A 也有 B 未覆盖的记录，说明当前独立映射词表不是完备药物本体，直接词命中也可能包含次要机制、伴随用药或非干预语境
* mapping-only 不等于“完整登记 JSON 一定没有靶点词”。9 条确定性样本中，GLP-1R 为 3/3 不含目标词，TL1A 为 0/3 不含，PCSK9 为 1/3 不含
* TL1A 和 PCSK9 的 mapping-only 样本中，部分靶点词只出现在参考文献、结果或结局字段。A 使用的 `query.term` 没有召回它们，证明搜索索引范围不能等同于 API 返回 JSON 的全部字符串字段
* condition-first 候选宇宙很大：GLP-1R 口径 25,195 条、TL1A 口径 4,304 条、PCSK9 口径 1,483 条
* 完整执行的 C 中，TL1A 离线字段筛选得到 26 条，与 B 完全一致；PCSK9 得到 184 条，全部属于 B，但 B 另有 15 条未被离线字段规则命中
* 因此，condition-first 的原始候选宇宙可以视为高成本候选上界，但基于有限字段和有限词表的离线筛选结果不是可证明的 recall 上界

## 研究问题

针对以下 PRD 示例，比较 ClinicalTrials.gov API v2 的三种召回策略：

* GLP-1R，肥胖和 2 型糖尿病
* TL1A，炎症性肠病
* PCSK9，高胆固醇血症或其他经证据支持的心血管适应症

策略定义：

* A：规范化靶点名和同义词直接查询
* B：用独立、可引用来源确认的已知干预名称做并集查询
* C：如接口和数据规模允许，先按 condition 召回，再离线按机制筛选，作为高成本候选上界

## 判定口径

* 每个策略的 `count` 指当次可重放 API 查询经 NCT ID 去重后的集合大小，不代表真实 recall
* `overlap = |A ∩ B|`
* `direct-only = |A - B|`
* `mapping-only = |B - A|`
* 机制相关性以独立来源和登记文本为依据，不由靶点命中数推断
* ClinicalTrials.gov 是动态数据库，本文所有数量均为带 UTC 时间的时间点快照

## 可证伪假设与最低成本检查

假设：直接靶点词查询会漏掉仅登记药名、未在可检索登记文本中写出靶点机制的试验。检查方法是完整抓取 A 与 B 的 NCT 集合，计算集合差，并对 `mapping-only` 样本离线检查完整登记 JSON 是否出现靶点词，同时用独立来源确认药物机制。

该假设只得到部分支持。GLP-1R 的 3 条 mapping-only 样本确实只写 AC2993/exendin-4，没有目标词。TL1A 与 PCSK9 的部分 mapping-only 记录含目标词，但目标词位于 `query.term` 未召回的参考文献、结果或结局字段。这将原假设细化为两个可区分原因：

1. 只登记干预名而不写目标词
2. 登记 JSON 中存在目标词，但该字段不在当前查询的有效索引范围或相关词法路径中

## 靶点名称规范化

A 的规范词从 HGNC 官方 REST API 取得，不依赖模型记忆。请求时间为 `2026-08-21T06:19:27Z` 附近。

| 输入 | HGNC ID | 规范符号 | 规范名称 | HGNC 别名/旧符号 | Ensembl | UniProt |
|---|---|---|---|---|---|---|
| GLP-1R | HGNC:4324 | GLP1R | glucagon like peptide 1 receptor | GLP-1R | ENSG00000112164 | P43220 |
| TL1A | HGNC:11931 | TNFSF15 | TNF superfamily member 15 | TL1, VEGI, TL1A, VEGI192A 等 | ENSG00000181634 | O95150 |
| PCSK9 | HGNC:20001 | PCSK9 | proprotein convertase subtilisin/kexin type 9 | NARC-1, FH3；旧符号 HCHOLA3 | ENSG00000169174 | Q8NBP7 |

准确请求：

```text
GET https://rest.genenames.org/fetch/symbol/GLP1R
GET https://rest.genenames.org/fetch/symbol/TNFSF15
GET https://rest.genenames.org/fetch/symbol/PCSK9
Accept: application/json
```

响应 SHA-256：

| 请求 | SHA-256 |
|---|---|
| HGNC GLP1R | `a4a6481e038a952f8c5849bafabffaa2a1feeb282af303b05ee79150bfc80de0` |
| HGNC TNFSF15 | `198626c4294994d33134a69adc3a524fa5de617a9b1e04783cd293e9a617613b` |
| HGNC PCSK9 | `ba9c108ac8805f4ae582d008ce4d91da0a5e8d0db2991cdad5b67538beb55a51` |

TL1A 的扩展措辞 `TNF-like ligand 1A` 和 `TNF-like cytokine 1A` 来自本轮 PubMed 主记录标题/摘要用语。GLP-1R 的连字符版本同时保留，以覆盖常见自然语言写法。

## 独立 target-to-intervention 映射

### GLP-1R 映射

ChEMBL 官方 REST API 把 HGNC/UniProt 对应的人 GLP1R 解析为：

```text
CHEMBL1784
Glucagon-like peptide 1 receptor
SINGLE PROTEIN
UniProt P43220
```

准确请求：

```text
GET https://www.ebi.ac.uk/chembl/api/data/target/search.json?q=GLP1R&limit=20
GET https://www.ebi.ac.uk/chembl/api/data/mechanism.json?target_chembl_id=CHEMBL1784&limit=1000
```

GLP1R 与 PCSK9 机制记录的分子名在一次批量请求中解析。实际参数为：

```text
GET https://www.ebi.ac.uk/chembl/api/data/molecule.json
	?molecule_chembl_id__in=CHEMBL2107841,CHEMBL2107860,CHEMBL2108027,CHEMBL2108336,CHEMBL2108724,CHEMBL2109539,CHEMBL2109540,CHEMBL2364655,CHEMBL3137349,CHEMBL3137352,CHEMBL3990012,CHEMBL4084119,CHEMBL414357,CHEMBL4297576,CHEMBL4297630,CHEMBL4297839,CHEMBL4297949,CHEMBL4298016,CHEMBL4518483,CHEMBL4594554,CHEMBL4594566,CHEMBL4650405,CHEMBL4650470,CHEMBL4650495,CHEMBL5095485,CHEMBL5314776
	&limit=100
```

机制端点返回 17 条直接相互作用记录，其中 16 条为 agonist，1 条为 antagonist；所有记录的 `direct_interaction=1` 且 `disease_efficacy=1`。分子名由 ChEMBL molecule 端点独立解析：

| ChEMBL ID | 首选名 | B 中使用的主要名称/代号 |
|---|---|---|
| CHEMBL414357 | EXENATIDE | exenatide, AC-2993, exendin-4 |
| CHEMBL2107841 | ALBIGLUTIDE | albiglutide, GSK-716155 |
| CHEMBL2107860 | TASPOGLUTIDE | taspoglutide, RO-5073031 |
| CHEMBL2108027 | DULAGLUTIDE | dulaglutide, LY-2189265 |
| CHEMBL2108336 | LIXISENATIDE | lixisenatide, AVE-0010, ZP-10 |
| CHEMBL2108724 | SEMAGLUTIDE | semaglutide, NN-9535 |
| CHEMBL3990012 | PEGAPAMODUTIDE | pegapamodutide, LY-2944876 |
| CHEMBL4084119 | LIRAGLUTIDE | liraglutide, NN-2211 |
| CHEMBL4297576 | EFINOPEGDUTIDE | efinopegdutide, HM-12525A, JNJ-64565111 |
| CHEMBL4297630 | COTADUTIDE | cotadutide, MEDI-0382 |
| CHEMBL4297839 | TIRZEPATIDE | tirzepatide, LY-3298176 |
| CHEMBL4297949 | AVEXITIDE | avexitide, exendin 9-39 |
| CHEMBL4518483 | DANUGLIPRON | danuglipron, PF-06882961 |
| CHEMBL4650470 | EFPEGLENATIDE | efpeglenatide, HM-11260C, SAR-439977 |
| CHEMBL4650495 | PEGSEBRENATIDE | pegsebrenatide, NLY-01 |
| CHEMBL5095485 | RETATRUTIDE | retatrutide, LY-3437943 |
| CHEMBL5314776 | SURVODUTIDE | survodutide, BI-456906 |

关键响应哈希：

| 响应 | SHA-256 |
|---|---|
| ChEMBL GLP1R target search | `77e5e10e17558fb7ff344ca030d017a54835e5de2343f626fd7708df9b0badad` |
| ChEMBL GLP1R mechanisms | `4aa022a6a8f05339ffef9becc77b27ad5346a80c0fc30f5639cab1e5ef2b73e7` |
| ChEMBL GLP1R/PCSK9 molecule names | `c7d6b776994457faf5fb6210d53eed16e0b0998511c0bb3b378218d9a303d1b8` |

### TL1A 映射

Open Targets 26.06 的当前 GraphQL schema 已将旧 `knownDrugs` 字段替换为 `drugAndClinicalCandidates`。官方 schema 请求：

```text
GET https://api.platform.opentargets.org/api/v4/graphql/schema
```

Schema SHA-256：
`d9bfcb4cc45ac0f5274ae691371afa10d5e08fc2aeb0f60170f811500e71cc52`。

按该 schema 查询 `ENSG00000181634`：

```graphql
query {
	target(ensemblId: "ENSG00000181634") {
		id
		approvedSymbol
		approvedName
		drugAndClinicalCandidates {
			count
			rows {
				maxClinicalStage
				drug {
					id
					name
					drugType
					synonyms { label source }
					tradeNames { label source }
				}
			}
		}
	}
}
```

`2026-08-21T06:30:42Z` 返回 HTTP 200、`approvedSymbol=TNFSF15`、`count=0`。响应 SHA-256 为 `02a611b35593d7d64db25d18462013f2791b6a01a45e5f45f6ade7e429433607`。该零结果只表示当时 Open Targets “Drugs and Clinical Candidates”联结数据没有返回行，不能推断现实中没有 TL1A 药物。

因此 TL1A 映射改由 NCBI PubMed 官方 API 独立建立。发现查询：

```text
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
	?db=pubmed
	&term=(TL1A[Title/Abstract] OR TNFSF15[Title/Abstract])
				AND (inflammatory bowel disease[Title/Abstract]
						 OR ulcerative colitis[Title/Abstract]
						 OR Crohn disease[Title/Abstract])
				AND (trial[Title/Abstract] OR phase[Title/Abstract])
	&retmode=json
	&retmax=100
```

URL 编码后的有效请求：

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=%28TL1A%5bTitle%2fAbstract%5d+OR+TNFSF15%5bTitle%2fAbstract%5d%29+AND+%28inflammatory+bowel+disease%5bTitle%2fAbstract%5d+OR+ulcerative+colitis%5bTitle%2fAbstract%5d+OR+Crohn+disease%5bTitle%2fAbstract%5d%29+AND+%28trial%5bTitle%2fAbstract%5d+OR+phase%5bTitle%2fAbstract%5d%29&retmode=json&retmax=100
```

ESearch 返回 26 个 PMID。随后以 EFetch XML 读取标题和摘要，并只从每篇主记录的 `MedlineCitation/Article` 提取药名，不使用参考文献中的无关管线药物。

EFetch 的实际参数为：

```text
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
	?db=pubmed
	&id=42560355,42500947,42462750,42235928,42166713,42106953,41941212,41904333,41822012,41389712,41389455,40706613,40507829,40065559,40006003,39907869,39772947,39711916,39321363,39068930,38574740,34427649,34126262,31758576,24814505,22795953
	&retmode=xml
```

| 干预名称 | 独立 PMID 证据 | 文本中的机制关系 |
|---|---|---|
| tulisokibart | PMID 39321363 | 标题和摘要明确为 anti-TL1A monoclonal antibody；对应 NCT04996797 |
| PRA023 / PRA-023 | PMID 39321363 + ChEMBL CHEMBL5095370 | ChEMBL 将 PRA023/PRA-023 解析为 tulisokibart 同义词 |
| afimkibart | PMID 40706613 | 标题和摘要明确为 TL1A-directed antibody；对应 NCT04090411 |
| PF-06480605 | PMID 34126262、31758576、40065559 | 摘要明确为 fully human antibody targeting TL1A |
| duvakitug | PMID 42462750 | 摘要明确为 anti-TL1A monoclonal antibody；对应 NCT05499130 |
| TEV-48574 | PMID 38574740 + ChEMBL CHEMBL5314733 | PubMed 记录明确其为 anti-TL1A；ChEMBL 将其解析为 duvakitug 同义词 |
| SPY002 | PMID 42106953 | 标题和摘要明确为 monoclonal antibody targeting TL1A |
| SPY072 | PMID 42106953 | 标题和摘要明确为 monoclonal antibody targeting TL1A |

PubMed 响应哈希：

| 响应 | SHA-256 |
|---|---|
| ESearch JSON | `b3f3c906ffc2380655b751cf92d0263b4dc1fec36e6df5fa33dd80d33597bad7` |
| EFetch XML，26 个 PubmedArticle | `07c20ee52d63f3fd25fa63f150e00aabff3ec240435ea9db3614a68debafc168` |

### PCSK9 映射

ChEMBL target search 同时返回与 HGNC 标识一致的蛋白和 mRNA 靶点：

| ChEMBL target | 类型 | 标识 |
|---|---|---|
| CHEMBL2929 | SINGLE PROTEIN | UniProt Q8NBP7 |
| CHEMBL4630662 | NUCLEIC-ACID | Ensembl ENSG00000169174 |

准确请求：

```text
GET https://www.ebi.ac.uk/chembl/api/data/target/search.json?q=PCSK9&limit=20
GET https://www.ebi.ac.uk/chembl/api/data/mechanism.json?target_chembl_id=CHEMBL2929
GET https://www.ebi.ac.uk/chembl/api/data/mechanism.json?target_chembl_id=CHEMBL4630662
GET https://www.ebi.ac.uk/chembl/api/data/molecule.json?molecule_chembl_id__in=CHEMBL3990033,CHEMBL5095052&limit=20
```

蛋白端点返回 9 条直接 PCSK9 inhibitor 机制记录；mRNA 端点返回 2 条直接 RNAi inhibitor 记录。分子解析如下：

| ChEMBL ID | 首选名 | B 中使用的主要名称/代号 |
|---|---|---|
| CHEMBL2109539 | RG-7652 | RG-7652 |
| CHEMBL2109540 | ALIROCUMAB | alirocumab, REGN-727, SAR-236553 |
| CHEMBL2364655 | EVOLOCUMAB | evolocumab, AMG-145 |
| CHEMBL3137349 | BOCOCIZUMAB | bococizumab, PF-04950615, RN-316 |
| CHEMBL3137352 | RALPANCIZUMAB | ralpancizumab, PF-05335810, RN-317 |
| CHEMBL4298016 | FROVOCIMAB | frovocimab, LY-3015014 |
| CHEMBL4594554 | TAFOLECIMAB | tafolecimab, IBI-306 |
| CHEMBL4594566 | ONGERICIMAB | ongericimab, JS-002 |
| CHEMBL4650405 | LERODALCIBEP | lerodalcibep |
| CHEMBL3990033 | INCLISIRAN | inclisiran, ALN-60212, ALN-PCSSC |
| CHEMBL5095052 | INCLISIRAN SODIUM | inclisiran sodium, ALN-60212 SODIUM, ALN-PCSSC SODIUM |

关键响应哈希：

| 响应 | SHA-256 |
|---|---|
| ChEMBL PCSK9 target search | `cff2377c06066023980ed0e603d35392b93ed65eae13b4a3174c78572f25f96b` |
| ChEMBL PCSK9 protein mechanisms | `7d1b78ca8857aa08d1bc7425cdfab7a8b8ce96e2adf0253bee320a4f65a5ecbf` |
| ChEMBL PCSK9 mRNA mechanisms | `809f84c7aa57c780c99cc3da58be14307106fe9791d25b8c4c605a9185b87223` |
| ChEMBL inclisiran molecule names | `6aed8411f5f94f6a81cec7542eded4887a0d1948682c8de2b85955a473b95221` |

## ClinicalTrials.gov A/B 查询设计

共同端点和共同参数：

```text
GET https://clinicaltrials.gov/api/v2/studies
pageSize=250
countTotal=true
fields=NCTId
```

* A 使用 `query.term`，目标是让规范靶点名和同义词在 ClinicalTrials.gov 的通用搜索语义中召回候选
* B 使用 `query.intr`，对独立来源确认的干预名称和研发代号做 OR 并集查询
* 两者都使用独立 `query.cond`，不对 phase、status、study type 或日期做额外过滤
* 每页的 `nextPageToken` 原样传入下一请求；最终将所有 NCT ID 按字典序排序并去重

### A 的准确参数

| 靶点 | 参数 | 准确值 |
|---|---|---|
| GLP-1R | `query.term` | `(GLP1R OR "GLP-1R" OR "glucagon like peptide 1 receptor" OR "glucagon-like peptide 1 receptor")` |
| GLP-1R | `query.cond` | `Obesity OR Type 2 Diabetes Mellitus` |
| TL1A | `query.term` | `(TNFSF15 OR TL1A OR "TNF superfamily member 15" OR "TNF-like ligand 1A" OR "TNF-like cytokine 1A")` |
| TL1A | `query.cond` | `Inflammatory Bowel Disease OR Crohn Disease OR Ulcerative Colitis` |
| PCSK9 | `query.term` | `(PCSK9 OR "proprotein convertase subtilisin/kexin type 9" OR "NARC-1" OR HCHOLA3)` |
| PCSK9 | `query.cond` | `Hypercholesterolemia OR Familial Hypercholesterolemia` |

### B 的准确参数

GLP-1R `query.intr`：

```text
(exenatide OR "AC-2993" OR "exendin-4" OR albiglutide OR "GSK-716155" OR taspoglutide OR "RO-5073031" OR dulaglutide OR "LY-2189265" OR lixisenatide OR "AVE-0010" OR "ZP-10" OR semaglutide OR "NN-9535" OR pegapamodutide OR "LY-2944876" OR liraglutide OR "NN-2211" OR efinopegdutide OR "HM-12525A" OR "JNJ-64565111" OR cotadutide OR "MEDI-0382" OR tirzepatide OR "LY-3298176" OR avexitide OR "exendin 9-39" OR danuglipron OR "PF-06882961" OR efpeglenatide OR "HM-11260C" OR "SAR-439977" OR pegsebrenatide OR "NLY-01" OR retatrutide OR "LY-3437943" OR survodutide OR "BI-456906")
```

GLP-1R `query.cond`：

```text
Obesity OR Type 2 Diabetes Mellitus
```

TL1A `query.intr`：

```text
(tulisokibart OR PRA023 OR "PRA-023" OR afimkibart OR "PF-06480605" OR duvakitug OR "TEV-48574" OR SPY002 OR SPY072)
```

TL1A `query.cond`：

```text
Inflammatory Bowel Disease OR Crohn Disease OR Ulcerative Colitis
```

PCSK9 `query.intr`：

```text
("RG-7652" OR alirocumab OR "REGN-727" OR "SAR-236553" OR evolocumab OR "AMG-145" OR bococizumab OR "PF-04950615" OR "RN-316" OR ralpancizumab OR "PF-05335810" OR "RN-317" OR frovocimab OR "LY-3015014" OR tafolecimab OR "IBI-306" OR ongericimab OR "JS-002" OR lerodalcibep OR inclisiran OR "inclisiran sodium" OR "ALN-60212" OR "ALN-PCSSC")
```

PCSK9 `query.cond`：

```text
Hypercholesterolemia OR Familial Hypercholesterolemia
```

### 首请求的有效 URL

每个 URL 省略后续页的 `pageToken`。后续页只增加上一响应返回的 `pageToken`，其他参数保持不变。

```text
GLP A
https://clinicaltrials.gov/api/v2/studies?query.term=%28GLP1R+OR+%22GLP-1R%22+OR+%22glucagon+like+peptide+1+receptor%22+OR+%22glucagon-like+peptide+1+receptor%22%29&query.cond=Obesity+OR+Type+2+Diabetes+Mellitus&pageSize=250&countTotal=true&fields=NCTId

GLP B
https://clinicaltrials.gov/api/v2/studies?query.intr=%28exenatide+OR+%22AC-2993%22+OR+%22exendin-4%22+OR+albiglutide+OR+%22GSK-716155%22+OR+taspoglutide+OR+%22RO-5073031%22+OR+dulaglutide+OR+%22LY-2189265%22+OR+lixisenatide+OR+%22AVE-0010%22+OR+%22ZP-10%22+OR+semaglutide+OR+%22NN-9535%22+OR+pegapamodutide+OR+%22LY-2944876%22+OR+liraglutide+OR+%22NN-2211%22+OR+efinopegdutide+OR+%22HM-12525A%22+OR+%22JNJ-64565111%22+OR+cotadutide+OR+%22MEDI-0382%22+OR+tirzepatide+OR+%22LY-3298176%22+OR+avexitide+OR+%22exendin+9-39%22+OR+danuglipron+OR+%22PF-06882961%22+OR+efpeglenatide+OR+%22HM-11260C%22+OR+%22SAR-439977%22+OR+pegsebrenatide+OR+%22NLY-01%22+OR+retatrutide+OR+%22LY-3437943%22+OR+survodutide+OR+%22BI-456906%22%29&query.cond=Obesity+OR+Type+2+Diabetes+Mellitus&pageSize=250&countTotal=true&fields=NCTId

TL1A A
https://clinicaltrials.gov/api/v2/studies?query.term=%28TNFSF15+OR+TL1A+OR+%22TNF+superfamily+member+15%22+OR+%22TNF-like+ligand+1A%22+OR+%22TNF-like+cytokine+1A%22%29&query.cond=Inflammatory+Bowel+Disease+OR+Crohn+Disease+OR+Ulcerative+Colitis&pageSize=250&countTotal=true&fields=NCTId

TL1A B
https://clinicaltrials.gov/api/v2/studies?query.intr=%28tulisokibart+OR+PRA023+OR+%22PRA-023%22+OR+afimkibart+OR+%22PF-06480605%22+OR+duvakitug+OR+%22TEV-48574%22+OR+SPY002+OR+SPY072%29&query.cond=Inflammatory+Bowel+Disease+OR+Crohn+Disease+OR+Ulcerative+Colitis&pageSize=250&countTotal=true&fields=NCTId

PCSK9 A
https://clinicaltrials.gov/api/v2/studies?query.term=%28PCSK9+OR+%22proprotein+convertase+subtilisin%2fkexin+type+9%22+OR+%22NARC-1%22+OR+HCHOLA3%29&query.cond=Hypercholesterolemia+OR+Familial+Hypercholesterolemia&pageSize=250&countTotal=true&fields=NCTId

PCSK9 B
https://clinicaltrials.gov/api/v2/studies?query.intr=%28%22RG-7652%22+OR+alirocumab+OR+%22REGN-727%22+OR+%22SAR-236553%22+OR+evolocumab+OR+%22AMG-145%22+OR+bococizumab+OR+%22PF-04950615%22+OR+%22RN-316%22+OR+ralpancizumab+OR+%22PF-05335810%22+OR+%22RN-317%22+OR+frovocimab+OR+%22LY-3015014%22+OR+tafolecimab+OR+%22IBI-306%22+OR+ongericimab+OR+%22JS-002%22+OR+lerodalcibep+OR+inclisiran+OR+%22inclisiran+sodium%22+OR+%22ALN-60212%22+OR+%22ALN-PCSSC%22%29&query.cond=Hypercholesterolemia+OR+Familial+Hypercholesterolemia&pageSize=250&countTotal=true&fields=NCTId
```

## A/B 执行审计

每个响应页均满足 HTTP 200 且通过 `jq` 完整 JSON 解析后才加入集合。`response_sum`、API `totalCount` 和最终唯一 NCT 数在六组查询中一致，未观察到跨页重复 NCT。

| 查询 | UTC 时间窗口 | 页数 | response_sum | 唯一 NCT | 集合 SHA-256 | 逐页清单 SHA-256 |
|---|---|---:|---:|---:|---|---|
| GLP A | 06:51:58 - 06:52:00 | 3 | 626 | 626 | `de3f9c9a5cac2a4cf5b692fb72f2f81a283d44d95a655da11ebf7d5b72763a3c` | `87856c3ed1689bb53a5529e90824118e62b5e32430923668412a897da3dab313` |
| GLP B | 06:51:20 - 06:51:26 | 7 | 1,602 | 1,602 | `f73fdf8e48e9b7f0acfe72b16334468db4362c560ed61ac806b44ea382a13897` | `c2895567152d8a4b9645a370731e1e49dfe6a4ba881429ae442c84f68098ee0c` |
| TL1A A | 06:52:01 | 1 | 12 | 12 | `ff97073a7577b83f40123ada81b369cc3933e97f171adb684d32638679d72bda` | `60e0c3a0257ca473fb4194186b096e0ee978b7d3e323efc212ca2e90f6f45df8` |
| TL1A B | 06:52:02 | 1 | 26 | 26 | `6bfb225f80c1912a933ca486f361a68a70185fc0e12870d94b35810f81abdd0a` | `392d5f2afb72f1d1524d894880c1076f832573319cebb8acd944686e69329a86` |
| PCSK9 A | 06:52:03 | 1 | 194 | 194 | `9d4b223ebcdfdc3e385f1d4a51ca61d7386999e238dac9ef60479f4728d2be3d` | `1c38b61c908a72668dcb31c622303cd3933c545c4548e6ac3bf35a65bb60d1f0` |
| PCSK9 B | 06:52:04 | 1 | 199 | 199 | `43f1d6053a35a11f4abfa025f03ec4e263f8eddc2482a6af2d5065930014286b` | `633c48c340444297115cc74ae006f50de1bf43a9f5b881bffa970a47dd215f72` |

逐页清单每行保存：

```text
captured_at_utc<TAB>page_number<TAB>http_code<TAB>study_count<TAB>response_sha256<TAB>effective_url
```

大集合没有直接嵌入本文，以避免数千个 NCT 行淹没证据。排序 NCT 集合、差集和交集以计数、SHA-256、准确查询参数和可重跑脚本组成可审计摘要。

### 交差集合哈希

| 靶点 | overlap SHA-256 | direct-only SHA-256 | mapping-only SHA-256 |
|---|---|---|---|
| GLP-1R | `2a88137428656f83e5b8e9509a9f2ffcae26fc450497f0802d03026f9636744d` | `b0c8223f63fd95bc1decad8f420d36c7f96d1d5f651c3c6b748c98eb293f6228` | `e5ab9d6ef0c511f1a452df1152a84b1119fad2f89119570ac79c80a5b2495fef` |
| TL1A | `cbb075791f516a56a91263bf0bb92125bd4e9490b56582ebae1f4ab3ca41cb0d` | `314c14da102fa96bc5e622a2c7bdc956db99a94269fc3bc5654d9c489e71bdf4` | `4bafcafd17a18eaecf5c156fc57b34268873ea5be131d04fb6635098ac85ce1e` |
| PCSK9 | `360ec2339c8537b56e01cd7d7f21838fc663c80adafa41f20c3b26d3113bf487` | `64e699d1f09ab290026cb8620e26c3fd04999bf187be7c53c33d6f2a62dc0acb` | `b164f11e5efea076132c54f7f31a5a4b849029bef2b45e3e17ece330dab32233` |

### TL1A 完整小集合

TL1A A，12 条：

```text
NCT01140802
NCT02796339
NCT02840721
NCT04090411
NCT06052059
NCT06430801
NCT06651281
NCT06715540
NCT07029971
NCT07078994
NCT07080034
NCT07686406
```

TL1A B，26 条：

```text
NCT02840721
NCT04090411
NCT04996797
NCT05013905
NCT05107492
NCT05471492
NCT05499130
NCT05668013
NCT05910528
NCT06052059
NCT06430801
NCT06588855
NCT06589986
NCT06651281
NCT06819878
NCT06819891
NCT06829225
NCT07012395
NCT07158242
NCT07184931
NCT07184944
NCT07184996
NCT07185009
NCT07298421
NCT07652294
NCT07665723
```

TL1A overlap，5 条：

```text
NCT02840721
NCT04090411
NCT06052059
NCT06430801
NCT06651281
```

TL1A direct-only，7 条：

```text
NCT01140802
NCT02796339
NCT06715540
NCT07029971
NCT07078994
NCT07080034
NCT07686406
```

TL1A mapping-only，21 条：

```text
NCT04996797
NCT05013905
NCT05107492
NCT05471492
NCT05499130
NCT05668013
NCT05910528
NCT06588855
NCT06589986
NCT06819878
NCT06819891
NCT06829225
NCT07012395
NCT07158242
NCT07184931
NCT07184944
NCT07184996
NCT07185009
NCT07298421
NCT07652294
NCT07665723
```

## C condition-first 执行

### 候选规模探针

准确请求模板：

```text
GET https://clinicaltrials.gov/api/v2/studies
	?query.cond=<condition expression>
	&pageSize=1
	&countTotal=true
	&fields=NCTId
```

`2026-08-21T06:44:23Z` 的结果：

| 口径 | totalCount | 探针响应 SHA-256 |
|---|---:|---|
| Obesity OR Type 2 Diabetes Mellitus | 25,195 | `5e34fdd781c8eb99d37e67b44fa5d5b008ae2dc9db045d6e4ea4280bc361e49b` |
| Inflammatory Bowel Disease OR Crohn Disease OR Ulcerative Colitis | 4,304 | `c525270989fcd5318f1971330aed8aa1b85a8014e483b6e2a6001def7eb64fcc` |
| Hypercholesterolemia OR Familial Hypercholesterolemia | 1,483 | `78d0ae83bbf322427da1228a46f8fb75dcf42d1b7ea7d16523c6298b93637d4f` |

### 完整抓取和离线筛选规则

完整 C 使用：

```text
pageSize=100
countTotal=true
fields=NCTId,InterventionName,InterventionOtherName,InterventionDescription
```

每条研究被压成：

```text
NCTId<TAB>all intervention names | other names | descriptions
```

然后使用与 B 相同的独立映射词表做大小写不敏感离线匹配。C 没有调用 LLM 做机制判定。

| C 口径 | UTC 时间窗口 | 页数 | 原始候选 | 离线匹配 | 与 A overlap | 与 B overlap | B-C | C-B |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TL1A | 07:00:51 - 07:03:34 | 44 | 4,304 | 26 | 5 | 26 | 0 | 0 |
| PCSK9 | 06:55:53 - 06:59:04 | 15 | 1,483 | 184 | 116 | 184 | 15 | 0 |

C 审计哈希：

| C 口径 | 逐页清单 SHA-256 | 展平候选 TSV SHA-256 | 离线结果 SHA-256 |
|---|---|---|---|
| TL1A | `029c0f7a477bc6efa8781f9fd1e40fa2151b04aa770500a78022b3d37216c16d` | `6ed6fa59cb5ef47c7c939c2d0f9ed5ef91ce63a085ccaa457607e2f85ea1e548` | `6bfb225f80c1912a933ca486f361a68a70185fc0e12870d94b35810f81abdd0a` |
| PCSK9 | `3f32df4a1e1bd8d4defb4ebe6542208dd4a121b37bac83ab9f4d2b6290cc6744` | `a602d577f5d5c275575401767c66a2df1882e245f2937987e76ae0b4747dc101` | `b82dd5e05910aac78efbfa532f76977993288936d79928468ca6bb95598d2d1a` |

PCSK9 的 15 条 `B-C`：

```text
NCT01163838
NCT02770131
NCT02808403
NCT02906124
NCT03110432
NCT04319081
NCT05129241
NCT05438069
NCT05834673
NCT06507852
NCT06595069
NCT07023445
NCT07409636
NCT07468500
NCT07543731
```

GLP-1R C 没有执行完整分页。25,195 条候选在 `pageSize=100` 下需要约 252 个请求，并传输所有干预名、别名和描述。本轮已有两个完整 C 足以验证工作流，并观察到 C 离线结果不一定覆盖 B，因此没有把 25,195 条高成本候选继续拉取。可重跑脚本保留了通用 C 方法。

## Mapping-only 抽样核查

抽样规则为每个排序后 mapping-only 集合的前 3 条，共 9 条。每条都通过单记录端点回查：

```text
GET https://clinicaltrials.gov/api/v2/studies/{NCT_ID}
```

要求 HTTP 200 且 `protocolSection.identificationModule.nctId` 与请求 ID 完全相同。执行窗口为 `2026-08-21T07:04:28Z` 到 `07:04:35Z`。9 条抽样清单 SHA-256 为 `3895cd836bb4c88b9e6f074e80e24a1b9603e109a101904f80bc6caa43ef4a8b`。

靶点词检查对完整单条 JSON 的所有字符串做大小写不敏感扫描。结果：

| 靶点 | NCT | 登记干预/标题线索 | 目标词 | 命中路径或缺失结论 | 独立机制依据 |
|---|---|---|---|---|---|
| GLP-1R | NCT00035984 | AC2993；other name `synthetic exendin-4` | 不存在 | 完整 JSON 未命中 A 的任何 GLP1R 词 | ChEMBL CHEMBL414357 将 AC-2993/exendin-4 解析为 exenatide，GLP1R direct agonist |
| GLP-1R | NCT00039013 | AC2993；other name `synthetic exendin-4` | 不存在 | 完整 JSON 未命中 A 的任何 GLP1R 词 | 同上 |
| GLP-1R | NCT00039026 | AC2993；other name `synthetic exendin-4` | 不存在 | 完整 JSON 未命中 A 的任何 GLP1R 词 | 同上 |
| TL1A | NCT04996797 | tulisokibart；MK-7240/PRA023 | 存在 | `protocolSection.referencesModule.references[].citation` 和 `resultsSection.baselineCharacteristicsModule...description` | PMID 39321363 明确 tulisokibart 为 anti-TL1A monoclonal antibody；ChEMBL CHEMBL5095370 确认 PRA023 同义词 |
| TL1A | NCT05013905 | tulisokibart；PRA023/MK-7240 | 存在 | `protocolSection.referencesModule.references[].citation` | PMID 39321363 及该记录引用的独立临床论文明确 anti-TL1A 机制 |
| TL1A | NCT05107492 | intervention 名只写 450mg/150mg/placebo；标题写 PF-06480605 | 存在 | `protocolSection.outcomesModule.secondaryOutcomes[]` 和 `resultsSection.outcomeMeasuresModule...` 的 sTL1A 测量 | PMID 40065559、34126262、31758576 明确 PF-06480605 targeting TL1A |
| PCSK9 | NCT00991159 | RN316/PF-04950615 | 存在 | `protocolSection.referencesModule.references[].citation` | ChEMBL CHEMBL3137349 将 RN316/PF-04950615 解析为 bococizumab，PCSK9 direct inhibitor |
| PCSK9 | NCT01161082 | REGN727/SAR236553 | 存在 | `protocolSection.referencesModule.references[].citation` | ChEMBL CHEMBL2109540 将 REGN727/SAR236553 解析为 alirocumab，PCSK9 direct inhibitor |
| PCSK9 | NCT01163838 | intervention 名为剂量；标题写 RN316 | 不存在 | 完整 JSON 未命中 A 的任何 PCSK9 词 | ChEMBL CHEMBL3137349 将 RN316 解析为 bococizumab，PCSK9 direct inhibitor |

单条响应哈希：

| NCT | SHA-256 |
|---|---|
| NCT00035984 | `08b92962ad70af00681fbdccf2854220a2534cd75533a0c26ea850fab174eb22` |
| NCT00039013 | `8082fdd1b0c9855b9fbc771a36a42d5dc928cd99ae1f03da6e8be175e20af694` |
| NCT00039026 | `8c5e6e0b8bc7b5a25bcef27e94c06720d336c38a030d543a7001b5b64c6d1fe7` |
| NCT04996797 | `143dce568dc75827d6165288cd4326aa07976aa1a1596a5a5f0824fc7a941d84` |
| NCT05013905 | `ae8e0a6ea86383bff3930551e20374424f7b3d5a59a3cbf8e3b8ca130ec9bd62` |
| NCT05107492 | `579e3391ee83b52aa43031df54469891a20f853998ebcb5604bd743ed7fb04f1` |
| NCT00991159 | `67776a011b45dcdfb62aa062ad2aaa0d776164f23c1658a2792cca3ec03d3021` |
| NCT01161082 | `099909b79e96636151dd17aec2e60217689c3ff9fc503d2310a730858bdf1b66` |
| NCT01163838 | `ea03472e5a41cbc7595acc1770e51abdc8616a8445e90f5bcc83d1047611eff0` |

抽样反驳了一个过强解释：不能把所有 mapping-only 都归因于“登记完全没写 target”。正确解释必须允许登记字段索引覆盖差异。

## 失败、降级与未采用数据

* Open Targets 第三次 GraphQL introspection 请求返回 HTTP 403。随后改用公开 schema URL，并按当前 `drugAndClinicalCandidates` 字段成功查询 TNFSF15。没有用 403 前后的任何缺失正文编造映射
* Open Targets TNFSF15 当前查询返回 `count=0`。该结果没有被解释为“无药”，而是触发 PubMed 独立映射路径
* ChEMBL `/mechanism/search.json?q=TL1A+TNFSF15` 返回 404。后续只使用 target ID 精确机制过滤和 molecule search
* ChEMBL PCSK9 mechanism 请求带 `limit=1000` 时返回 400；去掉非必要 limit 后返回 HTTP 200、9 条蛋白机制记录
* PubMed 首个含通配符的复合查询返回 400；移除通配符并使用稳定的 Title/Abstract 语法后返回 HTTP 200、26 条
* ClinicalTrials.gov 的富字段 `pageSize=1000` 响应在当前执行环境中被截断，JSON 无法完整解析。正式 A/B 改为只取 `NCTId`、`pageSize=250`，每页强制通过 `jq` 完整性检查
* TL1A C 的首个沙箱请求被代理返回 `CONNECT tunnel failed, response 403`。同一准确请求在非沙箱环境返回 HTTP 200，之后完整抓取 44 页。该 403 是执行环境网络代理失败，不是 ClinicalTrials.gov 业务响应
* 多个持久终端曾返回其他并行研究命令的延迟 stdout。本研究只采信带唯一哨兵的输出，或预期文件存在且可解析、可哈希的结果；串台输出不进入任何计数

## 局限

* 缺少完整人工金标准，无法计算真实 recall、precision、sensitivity 或 specificity
* A 的 `query.term` 是通用文本搜索，不是分子靶点结构化字段；B 的 `query.intr` 也可能使用 ClinicalTrials.gov 的词法扩展和索引逻辑
* B 的药物词表由公开来源构建，但不是完整药物本体。新药、地区代号、组合制剂、品牌名、拼写变体和未进入 ChEMBL/PubMed 的候选可能缺失
* GLP-1R B 包含多靶点激动剂。它们确有 GLP1R 机制，但不能据此推断 GLP1R 是唯一或主要临床作用机制
* PCSK9 C 只扫描选定的干预名称、别名和描述，因此未覆盖 B 的 15 条记录。这个观察直接说明有限字段离线筛选不是可靠的真实上界
* condition 查询也不是精确疾病本体裁剪。例如 NCT00991159 的结构化 condition 为 Healthy，但仍出现在 PCSK9 B 口径中，可能受搜索扩展、参考文本或其他索引字段影响
* TL1A B 的 SPY002/SPY072 映射由 PMID 42106953 支持，但本轮 ChEMBL molecule search 返回 0；它们仍属于有独立 PubMed 证据的候选，不是 ChEMBL 映射
* 所有数量都是 `dataTimestamp=2026-08-20T09:00:05` 附近快照。未来重跑必须保存新的版本、时间、查询和集合哈希，不能与本轮数字静默混用

## 可重跑脚本

以下 Bash 脚本重放单个 A/B 集合并生成逐页清单。`SEARCH_PARAM`、`QUERY` 和 `CONDITION` 使用上文准确值。

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE_URL='https://clinicaltrials.gov/api/v2/studies'
OUT_DIR="${1:-./ctgov-replay-$(date -u +%Y%m%dT%H%M%SZ)}"
KEY="${KEY:?set KEY, for example glp-A}"
SEARCH_PARAM="${SEARCH_PARAM:?set query.term or query.intr}"
QUERY="${QUERY:?set exact query expression}"
CONDITION="${CONDITION:?set exact condition expression}"
mkdir -p "$OUT_DIR"

token=''
page=1
: > "$OUT_DIR/$KEY.raw.ids"
: > "$OUT_DIR/$KEY.manifest.tsv"

while true; do
	page_file=$(printf '%s/%s-page-%04d.json' "$OUT_DIR" "$KEY" "$page")
	captured=$(date -u +%Y-%m-%dT%H:%M:%SZ)
	args=(
		--max-time 60
		--silent
		--show-error
		--get "$BASE_URL"
		--data-urlencode "$SEARCH_PARAM=$QUERY"
		--data-urlencode "query.cond=$CONDITION"
		--data 'pageSize=250'
		--data 'countTotal=true'
		--data 'fields=NCTId'
	)
	if [[ -n "$token" ]]; then
		args+=(--data-urlencode "pageToken=$token")
	fi

	metadata=$(curl "${args[@]}" \
		--write-out $'%{http_code}\t%{url_effective}' \
		--output "$page_file")
	http_code=${metadata%%$'\t'*}
	effective_url=${metadata#*$'\t'}
	[[ "$http_code" == '200' ]]
	jq -e '.studies and (.studies | type == "array")' "$page_file" >/dev/null

	count=$(jq '.studies | length' "$page_file")
	response_sha=$(shasum -a 256 "$page_file" | awk '{print $1}')
	printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
		"$captured" "$page" "$http_code" "$count" "$response_sha" "$effective_url" \
		>> "$OUT_DIR/$KEY.manifest.tsv"
	jq -r '.studies[].protocolSection.identificationModule.nctId' "$page_file" \
		>> "$OUT_DIR/$KEY.raw.ids"

	token=$(jq -r '.nextPageToken // empty' "$page_file")
	[[ -z "$token" ]] && break
	page=$((page + 1))
done

sort -u "$OUT_DIR/$KEY.raw.ids" > "$OUT_DIR/$KEY.sorted.ids"
wc -l "$OUT_DIR/$KEY.sorted.ids"
shasum -a 256 "$OUT_DIR/$KEY.sorted.ids" "$OUT_DIR/$KEY.manifest.tsv"
```

调用示例：

```bash
KEY='tl1a-A' \
SEARCH_PARAM='query.term' \
QUERY='(TNFSF15 OR TL1A OR "TNF superfamily member 15" OR "TNF-like ligand 1A" OR "TNF-like cytokine 1A")' \
CONDITION='Inflammatory Bowel Disease OR Crohn Disease OR Ulcerative Colitis' \
bash replay-ctgov.sh
```

C 使用同一分页循环，但移除 `SEARCH_PARAM/QUERY`，将参数替换为：

```bash
--data 'pageSize=100'
--data 'countTotal=true'
--data-urlencode 'fields=NCTId,InterventionName,InterventionOtherName,InterventionDescription'
```

然后展平并离线匹配：

```bash
jq -r '
	.studies[] |
	[
		.protocolSection.identificationModule.nctId,
		([
			.protocolSection.armsInterventionsModule.interventions[]? |
			(.name // ""),
			(.otherNames[]? // ""),
			(.description // "")
		] | join(" | "))
	] | @tsv
' page-*.json > condition-interventions.tsv

rg -i 'tulisokibart|PRA[- ]?023|afimkibart|PF[- ]?06480605|duvakitug|TEV[- ]?48574|SPY[- ]?002|SPY[- ]?072' \
	condition-interventions.tsv |
	cut -f1 |
	sort -u > tl1a-C.sorted.ids
```

## 参考来源

* [ClinicalTrials.gov API v2](https://clinicaltrials.gov/data-api/api)
* [ClinicalTrials.gov Search Areas](https://clinicaltrials.gov/data-api/about-api/search-areas)
* [ClinicalTrials.gov Complex Search Queries](https://clinicaltrials.gov/find-studies/constructing-complex-search-queries)
* [HGNC REST web service](https://www.genenames.org/help/rest-web-service-help/)
* [ChEMBL Data Web Services](https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services)
* [Open Targets GraphQL API](https://platform-docs.opentargets.org/data-access/graphql-api)
* [Open Targets Drugs and Clinical Candidates](https://platform-docs.opentargets.org/target/drugs)
* [Open Targets 26.06 release notes](https://platform-docs.opentargets.org/release-notes)
* [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
* [PMID 39321363](https://pubmed.ncbi.nlm.nih.gov/39321363/)
* [PMID 40706613](https://pubmed.ncbi.nlm.nih.gov/40706613/)
* [PMID 42462750](https://pubmed.ncbi.nlm.nih.gov/42462750/)
* [PMID 40065559](https://pubmed.ncbi.nlm.nih.gov/40065559/)
* [PMID 34126262](https://pubmed.ncbi.nlm.nih.gov/34126262/)
* [PMID 31758576](https://pubmed.ncbi.nlm.nih.gov/31758576/)
* [PMID 38574740](https://pubmed.ncbi.nlm.nih.gov/38574740/)
* [PMID 42106953](https://pubmed.ncbi.nlm.nih.gov/42106953/)

## 推荐下一步

* 由临床专家对 A∪B 分层抽样，建立人工相关性金标准，再计算 Precision@K、候选覆盖和错误类型；不要直接把本轮集合比值改名为 recall
* 将 ChEMBL/Open Targets/PubMed 映射保存为带版本、来源 ID、证据 URL、响应哈希和有效期的映射快照，而不是运行时由 LLM 临时生成
* 扩展 B 的组合制剂、品牌名、地区代号和新研发候选，并在扩展前后保存集合差
* 对 A 的 direct-only 分层审查，区分未纳入 B 词表的真实机制、次要机制提及、伴随用药和非相关文本命中
* 若需要 GLP-1R C，按 100 条分页完整抓取 25,195 条 condition 候选，保留约 252 页的审计清单，并与本轮 A/B 快照分开标记执行时间

## 待澄清问题

无。本轮原始问题均有执行结果、失败记录或可重跑路径。