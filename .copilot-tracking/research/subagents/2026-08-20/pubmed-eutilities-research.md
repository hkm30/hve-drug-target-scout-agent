<!-- markdownlint-disable-file -->

# PubMed / NCBI E-utilities 契约研究（截至 2026-08-20）

## 研究范围

目标：核对并验证 PubMed 相关 E-utilities 契约，重点覆盖：

1. ESearch (`esearch.fcgi`) XML/JSON 顶层与核心字段、默认行为
2. EFetch (`efetch.fcgi?db=pubmed`) PubMed XML 核心结构，`retmode`/`rettype` 限制
3. 速率限制（无 API key 与有 API key 对照）、`tool`/`email` 要求
4. `retmax` 默认、通用上限与 PubMed 特有可检索上限（区分“单页参数可接受值”与“可遍历总结果数”）
5. 时间范围过滤：`datetype`/`mindate`/`maxdate`/`reldate` 与 PubMed 日期字段语义和格式
6. 少量只读实测，记录 URL、响应摘录与观察时间，验证边界，不做负载测试

## 访问上下文与方法

- 研究日期：2026-08-20
- 端点实测观察时间（UTC）：2026-08-20T09:11:40Z
- 实测策略：仅执行少量 GET 请求，避免并发与压测；主要依赖 NCBI 官方文档 + 官方端点返回
- 主要来源：
  - E-utilities 总体与参数规范（Bookshelf Chapter 2/4）
  - EFetch 有效 `retmode`/`rettype` 表（Chapter 4 Table 1）
  - PubMed User Guide（日期字段语义、格式）

## 关键结论总览（按结论标签）

### 1) ESearch XML 与 JSON 的顶层/核心字段、默认行为

- [官方规范已验证] `esearch.fcgi` 默认 `retmode=xml`。
- [官方规范已验证] `db` 默认值是 `pubmed`。
- [官方规范已验证] `retmax` 默认值是 `20`。
- [官方规范已验证] `rettype` 允许 `uilist`（默认）或 `count`。
- [官方规范已验证] JSON 输出受支持（`retmode=json`）。
- [端点实测已验证] XML 响应核心字段可见：`<eSearchResult>`, `<Count>`, `<RetMax>`, `<RetStart>`, `<IdList>`, `<TranslationSet>`, `<QueryTranslation>`。
- [端点实测已验证] JSON 顶层结构为：`header` + `esearchresult`；`esearchresult`中常见：`count`, `retmax`, `retstart`, `idlist`, `translationset`, `querytranslation`。
- [端点实测已验证] `usehistory=y` 时 JSON 中增加 `querykey` 与 `webenv`。
- [条件性/仍是假设] JSON 是否总会出现 `translationstack`：在本次实测样本中未出现；官方章节主要以 XML 讲解该块，JSON 字段集合在不同查询下可能稀疏化。

### 2) EFetch(pubmed) XML 核心结构与 `retmode`/`rettype` 限制

- [官方规范已验证] `efetch.fcgi` 支持多数据库；PubMed 支持 XML 与 text 视图，具体组合以 Table 1 为准。
- [官方规范已验证] 对 `db=pubmed`：
  - `retmode=xml` + `rettype` 为空（null）可返回 PubMed XML
  - `retmode=text` 可配 `rettype=medline|uilist|abstract`
- [官方规范已验证] Table 1 明示 `db=pubmed` 默认是 XML（`rettype` 空、`retmode=xml` 默认）。
- [端点实测已验证] `efetch.fcgi?db=pubmed&id=30049270&retmode=xml` 返回 `<PubmedArticleSet>` 顶层，包含 `<PubmedArticle>`。
- [端点实测已验证] PubMed XML 核心层次（样本）：
  - `PubmedArticleSet`
  - `PubmedArticle`
  - `MedlineCitation`（含 `PMID`, `Article`, `Journal`, `Abstract`, `AuthorList`, `PublicationTypeList`, `MeshHeadingList` 等）
  - `PubmedData`（含 `History`, `ArticleIdList`, `ReferenceList` 等）
- [端点实测已验证] 不传 `retmode`/`rettype` 时，`db=pubmed` 返回 XML（与 Table 1 默认一致）。
- [端点实测已验证] `retmode=json` 对 `db=pubmed` 未返回结构化 JSON，本次样本返回纯文本 `30049270`（参数不在官方允许组合内时的非预期降级行为）。
- [条件性/仍是假设] 对非法组合的错误处理是否稳定：文档未承诺统一错误格式；实测表现可能因网关/后端策略变化。

### 3) 速率限制、API key 对照、`tool`/`email` 要求

- [官方规范已验证] 无 API key：建议并要求不超过 3 requests/sec（单 IP）；超过会收到错误。
- [官方规范已验证] 有 API key：默认可到 10 requests/sec；更高需申请。
- [官方规范已验证] `tool` 与 `email`：
  - 建议在请求中提供
  - 若触发策略导致封禁，恢复服务要求向 NCBI 注册 `tool`/`email`（仅在 URL 中带值并不等同已注册）
  - `email` 应是开发者有效地址，而非第三方终端用户地址
- [官方规范已验证] 大任务建议在周末或美东工作日 21:00-次日 05:00 执行，避免高峰负载。

### 4) `retmax` 默认、通用上限与 PubMed 特有限制（分页参数 vs 总可遍历量）

#### 4.1 单页参数可接受值（每次请求）

- [官方规范已验证] ESearch：`retmax` 默认 20；文档写“最多 10,000”。
- [官方规范已验证] EFetch/ESummary：`retmax` 上限 10,000。
- [端点实测已验证] 对 `db=pubmed` 请求 `retmax=20000` 被服务端调整为 `RetMax=9999`，并给出 `WarningList`：`Restrictions achieved. start and count adjusted to 0, 9999`。

#### 4.2 可遍历总结果数（通过 retstart 迭代）

- [官方规范已验证] Chapter 4 文本描述：PubMed/PMC 仅能通过 ESearch 取“前 10,000”匹配。
- [端点实测已验证] 当前实际边界更严格：
  - `retstart` 不能大于 `9998`
  - `retstart=9999` 返回 ERROR：仅可检索前 `9,999` 记录
  - `retstart=9998&retmax=2` 被调整为 `RetMax=1`
- [端点实测已验证] 非 PubMed 库（示例 `db=protein`）可用 `retstart=15000&retmax=5` 正常返回，说明“通过 retstart 翻页超过 10k”在其他数据库仍可行。

#### 4.3 结论（必须区分）

- [官方规范已验证] “参数名义上限”常写为 10,000。
- [端点实测已验证] PubMed 当前实现中，单次与总可遍历上限都表现为 9,999（起点最大 9,998，最多再取 1 条）。
- [条件性/仍是假设] 该 9,999 边界可能是实现修订（相对文档“10,000”存在偏差），需持续监控。

### 5) 时间范围过滤能力与语义

- [官方规范已验证] ESearch 支持日期过滤参数：`datetype`, `mindate`, `maxdate`, `reldate`。
- [官方规范已验证] ESearch 日期参数规则：
  - `mindate` 与 `maxdate` 必须成对使用
  - 格式支持 `YYYY`, `YYYY/MM`, `YYYY/MM/DD`
  - `reldate=n` 表示按 `datetype` 回溯最近 n 天
- [官方规范已验证] `datetype` 是“按哪类日期字段筛选”，常见值 `pdat`, `edat`, `mdat`，但具体可用值依数据库而异。
- [官方规范已验证] PubMed 查询侧日期字段语义（User Guide）：
  - `[dp]` / `[pdat]`：Publication Date（两者可互换）
  - `[edat]`：Entry Date（入库处理日期）
  - `[crdt]`：Create Date（记录首次创建日期）
  - `[mhda]`：MeSH Date（MeSH 索引日期）
  - `[epdat]`：电子出版日期
  - `[ppdat]`：纸刊出版日期
- [官方规范已验证] PubMed 也支持查询语法内日期范围（例如 `2000:2010[dp]`）和相对日期（如 `"last 5 years"[dp]`）。
- [条件性/仍是假设] ESearch 的 `datetype` 与 PubMed 查询字段标签是两套入口：前者是 API 参数过滤，后者是检索式字段限制；通常可达成相似目的，但不保证在所有复杂检索中完全等价。

## 端点实测证据（最小只读请求）

说明：以下均为礼貌性只读 GET 示例，未进行并发/压测。

### A. ESearch 字段与默认

1) XML 默认输出

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=asthma%5BTitle%5D&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `<Count>104860</Count>`
  - `<RetMax>20</RetMax>`
  - `<RetStart>0</RetStart>`
  - `<IdList>...20个...</IdList>`
- 观察：默认 `retmode=xml`，默认 `retmax=20`。

2) JSON 输出

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=asthma%5BTitle%5D&retmode=json&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `{"header":{"type":"esearch","version":"0.3"},"esearchresult":{"count":"104860","retmax":"20","retstart":"0","idlist":[...],"translationset":[],"querytranslation":"\"asthma\"[Title]"}}`

3) `rettype=count`

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=asthma%5BTitle%5D&rettype=count&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `<eSearchResult><Count>104860</Count></eSearchResult>`
- 观察：仅返回 `Count`。

4) `usehistory=y` 时 JSON 字段

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=asthma%5BTitle%5D&usehistory=y&retmode=json&retmax=1&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `"querykey":"1"`
  - `"webenv":"MCID_..."`

### B. EFetch(pubmed) 结构与限制

1) 明确 XML 模式

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30049270&retmode=xml&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `<PubmedArticleSet>`
  - `<PubmedArticle>`
  - `<MedlineCitation ...>`
  - `<PMID Version="1">30049270</PMID>`
  - `<Article>...<Abstract>...<AuthorList>...`
  - `<PubmedData>...<ArticleIdList>...`

2) 默认模式（不传 retmode/rettype）

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30049270&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 观察：返回同类 PubMed XML，符合 Table 1 默认。

3) `retmode=json` 试探

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30049270&retmode=json&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `30049270`
- 观察：非结构化 JSON，不应作为可靠契约。

### C. 上限与边界

1) PubMed `retmax` 超限

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer&retmax=20000&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `<RetMax>9999</RetMax>`
  - `<WarningList><OutputMessage>Restrictions achieved. start and count adjusted to 0, 9999</OutputMessage></WarningList>`

2) PubMed `retstart` 边界

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer&retstart=9998&retmax=2&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `<RetStart>9998</RetStart>`
  - `<RetMax>1</RetMax>`
  - `Restrictions achieved. start and count adjusted to 9998, 1`

3) PubMed `retstart=9999` 报错

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer&retstart=9999&retmax=1&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `ERROR ... 'retstart' cannot be larger than 9998 ... only retrieve the first 9,999 records ...`

4) 非 PubMed 对照（可跨 10k 分页）

- URL:
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=protein&term=kinase&retstart=15000&retmax=5&tool=drug-target-scout-agent-research&email=noreply%40example.org`
- 摘录：
  - `<RetStart>15000</RetStart>`
  - `<RetMax>5</RetMax>`
  - `<IdList>...5个...</IdList>`

## 规范与实测差异（实现必须注意）

1. 文档常写 PubMed 可取“前 10,000”，但当前端点对 `retstart` 的硬性校验显示最大只到 9998（即最多 9,999 条可遍历）。
2. 文档声明 ESearch `retmax` 上限 10,000，但 PubMed 实测被裁剪到 9,999 并返回 WarningList。
3. 对不在 Table 1 的 EFetch 组合（如 PubMed `retmode=json`），返回并非稳定错误 JSON，不可依赖。

## 适用于实现的请求示例

### ESearch（JSON + history）

```text
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
  ?db=pubmed
  &term=asthma%5BTitle%5D
  &retmode=json
  &retmax=100
  &usehistory=y
  &tool=your_tool_name
  &email=dev%40example.org
```

### EFetch（PubMed XML）

```text
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
  ?db=pubmed
  &id=30049270
  &retmode=xml
  &tool=your_tool_name
  &email=dev%40example.org
```

### ESearch（日期过滤参数）

```text
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
  ?db=pubmed
  &term=cancer
  &datetype=edat
  &reldate=60
  &retmax=200
  &tool=your_tool_name
  &email=dev%40example.org
```

## 实现陷阱清单

1. 不要把 PubMed 的“10,000”当作刚性上限；当前应按 9,999 处理并解析 Warning/Error。
2. `retmax` 请求值应做客户端裁剪（建议 PubMed <= 9999，其他库 <= 10000）。
3. 解析 ESearch JSON 时，`translationset` 可能为空；某些字段可能按查询条件省略。
4. `usehistory=y` 时要优先走 `querykey` + `webenv`，避免大 ID 列表传输。
5. 日期过滤要区分两条路径：API 参数（`datetype/mindate/maxdate/reldate`）与检索式字段（如 `[dp]`, `[edat]`, `[crdt]`）。
6. 对 EFetch 非法 `retmode/rettype` 组合，不要假设统一错误格式；要做健壮降级和告警。
7. 大批量任务遵守频率限制；必要时申请 API key，并设置 `tool`/`email`（且建议预先注册）。

## 主要来源

- NCBI Bookshelf: A General Introduction to the E-utilities (NBK25497)
  - https://www.ncbi.nlm.nih.gov/books/NBK25497/
- NCBI Bookshelf: The E-utilities In-Depth: Parameters, Syntax and More (NBK25499)
  - https://www.ncbi.nlm.nih.gov/books/NBK25499/
- NCBI Bookshelf: EFetch valid retmode/rettype table
  - https://www.ncbi.nlm.nih.gov/books/NBK25499/table/chapter4.T._valid_values_of__retmode_and/?report=objectonly
- PubMed User Guide（日期与字段语义）
  - https://pubmed.ncbi.nlm.nih.gov/help/#search-field-descriptions

## 未解决问题与澄清

- 目前无必须阻塞的澄清项。
- 仍需持续观察的问题：PubMed 9,999 边界是否会在后续版本回到文档表述的 10,000。
