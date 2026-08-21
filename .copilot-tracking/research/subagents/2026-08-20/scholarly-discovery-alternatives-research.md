<!-- markdownlint-disable-file -->

# Scholarly Discovery Alternatives Research (2026-08-20)

## Scope And Questions

1. Verify via official Google sources whether Google Scholar has a public, supported official API.
2. Research OpenAlex official API, data snapshot, sources, coverage: works, citations, external IDs (DOI/PMID), life-science coverage, full-text availability boundaries.
3. Research Europe PMC official REST API/data scope: PubMed/PMC, Europe PMC-only records, preprints, grants/patents/full text/citation network; biomedical retrieval and PMID back-lookup support.
4. Quantitative coverage numbers must include official source date; explain inconsistencies as dynamic corpus if needed.
5. Evaluate OpenAlex and Europe PMC as Google Scholar alternatives by dimensions: discovery breadth, life-science precision, citation network, abstract/full text, identifiers, licensing/bulk access, API stability. State clearly: not fully equivalent substitutes.
6. Run minimal official API requests (OpenAlex works lookup, Europe PMC search) and preserve request + response excerpts.

## Research Log

- Initialized document and pending evidence collection.
- Collected Google Scholar official pages (About/Help/Inclusion/Libraries) and Google developer API catalog pages.
- Collected OpenAlex official help pages for API, data model, works corpus, snapshot/sync/fulltext, and source pipeline.
- Collected Europe PMC official REST docs and About page; ran minimal REST calls for `search` lookups and source counts.
- Captured endpoint responses for OpenAlex DOI/PMID lookup and Europe PMC DOI/PMID-style back-lookup (`EXT_ID + SRC`).

## Findings

### 1) Google Scholar 是否有公开、受支持的官方 API

结论 1.1：未发现 Google 官方提供“Google Scholar 专用公开 API”。  
标记：条件性/仍是假设

- 证据 A（Scholar 官方信息架构）：Scholar 官方导航页仅提供 About/Search/Profiles/Inclusion/Metrics/Publishers/Libraries 等功能文档，未出现开发者 API 入口。  
	来源：
	- https://scholar.google.com/intl/en/scholar/about.html
	- https://scholar.google.com/intl/en/scholar/help.html
	- https://scholar.google.com/intl/en/scholar/inclusion.html
	- https://scholar.google.com/intl/en/scholar/libraries.html
- 证据 B（Google API 目录侧面排除）：Google APIs Explorer/Developer API 目录包含大量 Google API，但未见 Scholar 独立 API 条目；可见的是 Books API、Custom Search API 等不同产品。  
	来源：
	- https://developers.google.com/apis-explorer

结论 1.2：Google Custom Search JSON API 不是 Google Scholar API，不应混同。  
标记：官方规范已验证

- 官方描述明确其面向 Programmable Search Engine（可编排站点/站群搜索），不是 Scholar 数据接口。  
	来源：
	- https://developers.google.com/custom-search/docs/overview （Last updated 2024-08-21 UTC）
	- https://developers.google.com/custom-search/v1/introduction （Last updated 2026-01-20 UTC）
	- https://developers.google.com/custom-search/v1/overview （Last updated 2026-02-18 UTC）

结论 1.3：Scholar 机器人策略显示对核心搜索路径存在抓取限制，不支持把网页抓取当作官方 API 替代。  
标记：官方规范已验证

- `robots.txt` 对 `/search`、`/scholar`、`/citations?` 等路径存在 `Disallow`。  
	来源：
	- https://scholar.google.com/robots.txt

说明：Google 并未在上述页面给出一句“Scholar API 不存在”的显式声明；当前结论基于官方文档集合中的“缺失 API 声明 + 产品边界声明 + robots 限制”进行审慎判断。

### 2) OpenAlex 官方 API、快照、来源与覆盖范围

结论 2.1：OpenAlex 提供官方 REST API，支持免费起步与结构化查询。  
标记：官方规范已验证

- API 基址、响应结构、过滤/搜索/分组/分页、端点索引均有官方文档。  
	来源：
	- https://help.openalex.org/api

结论 2.2：OpenAlex 在 works 层面支持 DOI/PMID 等外部 ID 映射，并可单实体直接查询。  
标记：官方规范已验证 + 端点实测已验证

- 官方数据模型说明每个实体有 `ids` 对象，Works 的 canonical external ID 是 DOI；外部 ID 可用于直接查找。  
	来源：
	- https://help.openalex.org/data
	- https://help.openalex.org/api
- 实测：
	- `GET https://api.openalex.org/works/https://doi.org/10.1038/nature12373`
	- `GET https://api.openalex.org/works?filter=ids.pmid:https://pubmed.ncbi.nlm.nih.gov/31452104&per-page=1`
	均返回 `ids.doi`、`ids.pmid` 等字段。

结论 2.3：OpenAlex works/citations 能力覆盖“引用网络基本面”，但不是“全文数据库”。  
标记：官方规范已验证 + 端点实测已验证

- Works 官方属性与构建说明指出：有 `referenced_works`、`cited_by_count`、引用构建流程。  
	来源：
	- https://help.openalex.org/data/works/
	- https://help.openalex.org/data/how-its-built/
- 实测返回含 `cited_by_count`、`referenced_works`、`counts_by_year`。
- 全文边界：
	- `abstract_inverted_index` 对部分 works 为 `null`（并非每条有摘要）；
	- 全文是“可用子集”（`has_content` / `content_urls` / OA 来源），非全量出版物全文。  
	来源：
	- https://help.openalex.org/access/fulltext/
	- https://help.openalex.org/access/snapshot/

结论 2.4：OpenAlex 规模数字随语料与口径动态变化；core 与 all 语料要区分。  
标记：官方规范已验证

- Works 语料分层：`core`（约 320M+）、`expansion`（约 190M）、`all`（约 510M+），默认 API 是 core。  
	来源：
	- https://help.openalex.org/data/works/corpus/ （Last updated August 12, 2026）
- Works 概览页显示约 322,044,938（动态页面计数）与 homepage 的 517M 量级口径可能并存。  
	来源：
	- https://help.openalex.org/data/works/ （Last updated August 8, 2026）
	- https://openalex.org/（首页动态指标）
- 不一致解释：
	- 统计口径差异（core vs all）；
	- API 连续更新 vs 快照季度/日更；
	- 页面指标刷新时点不同。

结论 2.5：OpenAlex 支持官方快照和批量下载，许可为 CC0（元数据层面）。  
标记：官方规范已验证

- 公共快照（免费）季度发布；付费可日更快照 + 高级同步过滤。  
	来源：
	- https://help.openalex.org/access/snapshot/ （Last updated August 17, 2026）
	- https://help.openalex.org/access/sync/ （Last updated August 17, 2026）
- 数据开放许可说明：CC0。  
	来源：
	- https://help.openalex.org/api
	- https://help.openalex.org/data/how-its-built/

### 3) Europe PMC 官方 REST API 与覆盖范围（生物医学）

结论 3.1：Europe PMC 提供官方 Articles REST API，支持 JSON/XML/DC，具备可版本化发布机制。  
标记：官方规范已验证

- API 文档列出 `search`、`/{source}/{id}/citations`、`/{source}/{id}/references`、`/fields` 等模块，并说明生产/测试双版本发布。  
	来源：
	- https://europepmc.org/RestfulWebService

结论 3.2：Europe PMC 是生命科学文献聚合平台，覆盖 PubMed/PMC/预印本/专利等多源。  
标记：官方规范已验证 + 端点实测已验证

- 官方 About 与 REST 概览均指向多来源聚合与生命科学定位。  
	来源：
	- https://europepmc.org/About
	- https://europepmc.org/RestfulWebService
- 实测 `SRC` 计数（2026-08-20）：
	- `SRC:*` => `hitCount: 48639368`
	- `SRC:MED` => `40960109`
	- `SRC:PMC` => `885696`
	- `SRC:PPR`（preprints）=> `1220111`
	- `SRC:PAT`（patents）=> `4229296`
	- `SRC:AGR`（Agricola）=> `1017585`

结论 3.3：Europe PMC 对生物医学检索与 PMID 回查可用，但推荐用其字段语法（如 `EXT_ID + SRC`）而非假设通用 `PMID` 字段。  
标记：端点实测已验证

- 实测成功：
	- `GET .../search?query=EXT_ID:31452104 AND SRC:MED&format=json&pageSize=1`  
		命中 1 条，返回 `pmid`、`doi`、`citedByCount` 等。
	- `GET .../search?query=DOI:10.1038/nature12373&format=json&pageSize=1`  
		命中 1 条，返回 `pmid:23903748`、`pmcid:PMC4221854`。
- 实测失败示例（说明字段语法差异）：
	- `PMID:23903748`、`SRC:MED AND PMID:31452104` 返回 `hitCount:0`。

结论 3.4：Europe PMC 引用网络、全文可用性、开放获取、注释网络均有官方能力，但全文并非“全记录可得”。  
标记：官方规范已验证 + 端点实测已验证

- 官方声明支持 citations/references、text-mined annotations、open access/full text 子集访问。  
	来源：
	- https://europepmc.org/RestfulWebService
	- https://europepmc.org/About
- 实测全文相关计数（2026-08-20）：
	- `HAS_FT:Y` => `11980020`
	- `OPEN_ACCESS:Y` => `8031892`

### 4) 量化覆盖数字与“数字不一致”解释（含日期）

Google Scholar：

- 官方 Scholar 页面未提供统一“可机读总记录数 API”口径。  
	标记：官方规范已验证

OpenAlex（官方页面+文档）：

- `core ~320M+ / expansion ~190M / all ~510M+`（works corpus 文档，Last updated 2026-08-12）。
- Works Overview 示例计数约 `322,044,938`（页面动态呈现，文档 Last updated 2026-08-08）。
- 官网首页呈现约 `517M work records`（动态指标，抓取日期 2026-08-20）。

Europe PMC（官方页面+API）：

- About/主页文案显示约 `48.6M`（抓取日期 2026-08-20，页面为动态计数）。
- API 实测 `SRC:*` 返回 `48,639,368`（2026-08-20，version 6.9）。

不一致的合理解释：

- 动态语料持续更新；
- 统计口径不同（核心语料 vs 扩展语料；abstract-level vs full-text subset）；
- 页面更新时间与 API 查询时间不一致。

## API Minimal Validation

### OpenAlex endpoint checks

1) DOI 单条查询

Request:

```http
GET https://api.openalex.org/works/https://doi.org/10.1038/nature12373
```

Response excerpt:

```json
{
	"id": "https://openalex.org/W2159974629",
	"doi": "https://doi.org/10.1038/nature12373",
	"ids": {
		"openalex": "https://openalex.org/W2159974629",
		"doi": "https://doi.org/10.1038/nature12373",
		"pmid": "https://pubmed.ncbi.nlm.nih.gov/23903748"
	},
	"cited_by_count": 1981,
	"referenced_works_count": 36,
	"has_fulltext": true,
	"open_access": { "is_oa": true, "oa_status": "bronze" },
	"abstract_inverted_index": null,
	"updated_date": "2026-08-18T07:49:30.821534"
}
```

验证结论：DOI 查询、外部 ID 映射、引用字段、OA/全文相关字段可用。  
标记：端点实测已验证

2) PMID 过滤查询

Request:

```http
GET https://api.openalex.org/works?filter=ids.pmid:https://pubmed.ncbi.nlm.nih.gov/31452104&per-page=1
```

Response excerpt:

```json
{
	"meta": { "count": 1, "page": 1, "per_page": 1 },
	"results": [
		{
			"id": "https://openalex.org/W2970603197",
			"ids": {
				"doi": "https://doi.org/10.1007/978-1-4939-9752-7_10",
				"pmid": "https://pubmed.ncbi.nlm.nih.gov/31452104"
			}
		}
	]
}
```

验证结论：PMID 作为外部 ID 过滤可行。  
标记：端点实测已验证

3) 速率限制观察

Request:

```http
GET https://api.openalex.org/works?search=crispr&per-page=1
```

Observed:

```text
HTTP 429
```

验证结论：公共 API 存在速率限制，生产使用需遵循认证/配额策略。  
标记：端点实测已验证

### Europe PMC endpoint checks

1) PMID 回查（推荐语法）

Request:

```http
GET https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:31452104%20AND%20SRC:MED&format=json&pageSize=1
```

Response excerpt:

```json
{
	"version": "6.9",
	"hitCount": 1,
	"resultList": {
		"result": [
			{
				"source": "MED",
				"pmid": "31452104",
				"doi": "10.1007/978-1-4939-9752-7_10",
				"citedByCount": 120
			}
		]
	}
}
```

验证结论：可用于 PMID 回查并拿到结构化元数据。  
标记：端点实测已验证

2) DOI 回查

Request:

```http
GET https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/nature12373&format=json&pageSize=1
```

Response excerpt:

```json
{
	"hitCount": 1,
	"resultList": {
		"result": [
			{
				"source": "MED",
				"pmid": "23903748",
				"pmcid": "PMC4221854",
				"doi": "10.1038/nature12373",
				"citedByCount": 679
			}
		]
	}
}
```

验证结论：DOI -> PMID/PMCID 映射可直接用于生物医学检索流程。  
标记：端点实测已验证

3) 覆盖计数与预印本

Requests:

```http
GET .../search?query=SRC:*&format=json&pageSize=1
GET .../search?query=SRC:PPR&format=json&pageSize=1
GET .../search?query=HAS_FT:Y&format=json&pageSize=1
GET .../search?query=OPEN_ACCESS:Y&format=json&pageSize=1
```

Response key metrics (2026-08-20):

```json
{
	"SRC:*": 48639368,
	"SRC:PPR": 1220111,
	"HAS_FT:Y": 11980020,
	"OPEN_ACCESS:Y": 8031892
}
```

验证结论：生命科学语境下，预印本、全文子集、OA 子集均可程序化检索。  
标记：端点实测已验证

## Comparison Matrix

结论总述：OpenAlex + Europe PMC 能覆盖大量“可程序化学术发现”场景，但二者合计仍不等价于 Google Scholar 的整体检索语义与覆盖策略；它们是“可替代部分任务”的组合，不是“完全替代”。  
标记：条件性/仍是假设

| 维度 | Google Scholar | OpenAlex | Europe PMC | 评估结论 |
|---|---|---|---|---|
| 发现广度（跨学科） | 官方强调 broad scholarly search；但无公开官方 API | 多学科知识图谱，works 3.2e8+（core）到 5.1e8+（all） | 生命科学为主（约 4.86e7） | OpenAlex 在 API 广度上更接近 Scholar 的“跨学科可编程替代”；Europe PMC 偏生命科学深耕 |
| 生命科学精度 | 强，但黑盒排序 | 覆盖生命科学且有 PMID/MeSH 等字段（记录层级依来源而异） | 生物医学原生平台（PubMed/PMC/预印本/基金等集成） | Europe PMC 在生命科学检索与回查流程中更“领域原生” |
| 引用网络 | Scholar 有 Cited by，但无官方公开 API | `referenced_works`、`cited_by_count` 官方可编程 | citations/references 端点官方可用 | OpenAlex/Europe PMC 在“可编程引用网络”上优于 Scholar 的官方开放性 |
| 摘要/全文 | Scholar 以链接聚合为主，全文可得性依外部来源 | 摘要并非全覆盖；全文是可用子集（content archive） | 提供全文子集、OA 子集、fullTextXML（OA） | 两者均不是“全量全文库”；需接受子集边界 |
| 标识符（DOI/PMID/PMCID） | 页面级可见，不提供官方统一 API 合同 | DOI canonical；`ids` 可含 PMID/ORCID/ROR 等 | DOI/PMID/PMCID 在 REST 查询和结果中稳定可用 | 生物医学回查链路 Europe PMC 更直接；OpenAlex 适合图谱联通 |
| 许可/批量访问 | 官方未给 Scholar 公共数据下载接口 | CC0 元数据；官方 snapshot/sync/fulltext 产品线 | 官方 API + bulk downloads，开放科研基础设施定位 | OpenAlex/Europe PMC 均可合法批量/自动化；Scholar 不提供同等级官方通道 |
| API 稳定性与工程化 | 未见官方 Scholar API | API 文档完善，快照/发布机制透明，状态页可观测 | 双版本发布、release notes、字段文档、社区支持 | 二者均具生产级 API 治理特征 |

### 维度化结论标签

- “OpenAlex 可替代 Scholar 的跨学科程序化检索主干”  
	标记：条件性/仍是假设（取决于业务是否依赖 Scholar 私有排序/索引策略）
- “Europe PMC 可替代 Scholar 的生物医学检索与 PMID 回查流程”  
	标记：官方规范已验证 + 端点实测已验证
- “两者合并可完全等价替代 Scholar”  
	标记：条件性/仍是假设（当前证据不支持完全等价）

## Remaining Questions

1. Google 官方是否存在隐藏/未公开但受支持的 Scholar 企业接口？

- 当前公开文档未发现；若需“强否定结论”，建议通过 Google 官方支持渠道获得书面确认。  
	标记：条件性/仍是假设

2. OpenAlex 生命科学专题覆盖是否可与特定 gold standard（如 MEDLINE MeSH 深度）逐字段对齐？

- 已确认可含 PMID/MeSH 相关字段，但字段完整性随来源而异；需样本化评测。  
	标记：条件性/仍是假设

3. Europe PMC 各 `SRC` 代码全集与字段语义的系统映射（用于严格 ETL）

- 本次已实测 `MED/PMC/PPR/PAT/AGR`；其余来源可继续通过 `/fields` 与文档补齐。  
	标记：条件性/仍是假设

## References (Official / Primary)

Google Scholar / Google Developer:

- https://scholar.google.com/intl/en/scholar/about.html
- https://scholar.google.com/intl/en/scholar/help.html
- https://scholar.google.com/intl/en/scholar/inclusion.html
- https://scholar.google.com/intl/en/scholar/libraries.html
- https://scholar.google.com/robots.txt
- https://developers.google.com/apis-explorer
- https://developers.google.com/custom-search/docs/overview
- https://developers.google.com/custom-search/v1/introduction
- https://developers.google.com/custom-search/v1/overview

OpenAlex:

- https://help.openalex.org/api
- https://help.openalex.org/data
- https://help.openalex.org/data/works/
- https://help.openalex.org/data/works/corpus/
- https://help.openalex.org/data/common-attributes/
- https://help.openalex.org/data/how-its-built/
- https://help.openalex.org/access/snapshot/
- https://help.openalex.org/access/sync/
- https://help.openalex.org/access/fulltext/
- https://openalex.org/
- https://status.openalex.org/

Europe PMC:

- https://europepmc.org/RestfulWebService
- https://europepmc.org/About
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:31452104%20AND%20SRC:MED&format=json&pageSize=1
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/nature12373&format=json&pageSize=1
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:*&format=json&pageSize=1
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:MED&format=json&pageSize=1
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:PMC&format=json&pageSize=1
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:PPR&format=json&pageSize=1
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:PAT&format=json&pageSize=1
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:AGR&format=json&pageSize=1
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=HAS_FT:Y&format=json&pageSize=1
- https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=OPEN_ACCESS:Y&format=json&pageSize=1
