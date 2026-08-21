<!-- markdownlint-disable-file -->
# Task Research: Drug Target Scout 技术假设验证

验证 prd-v0.1.md 中与生物医学文献、临床试验数据源和引用真实性校验相关的技术假设，为后续实现规划提供可追溯证据。结论基线日期为 2026-08-20。

## Executive Finding

PRD 的总体方向可行，但三项实现假设必须在规划前修正：

1. Google Scholar 没有可确认的公开、受支持官方 API，不应作为 DEMO 的可编程必选依赖。Europe PMC 应承担生物医学补充检索，OpenAlex 应承担跨学科发现和引用网络补充。
2. ClinicalTrials.gov API v2 没有独立分子靶点结构化字段。`query.intr`、`query.term` 和高级 `AREA[...]` 查询只能召回干预名、MeSH 和文本中出现靶点词的记录，不能声称完成了 target ontology 查询。
3. PMID/NCT 的“真实存在”必须由权威源独立回查并精确比对回显 ID。PMID 推荐 NCBI ESummary；NCT 推荐 ClinicalTrials.gov `GET /studies/{nctId}`。普通搜索命中、可点击链接和 LLM 输出都不能替代该步骤。

PubMed E-utilities 与 ClinicalTrials.gov API v2 的结构化字段足以支撑摘要级 DEMO。仍需项目验证的是检索召回率、同义词扩展质量、来源冲突处理、吞吐/缓存参数，以及“记录存在”之外的相关性、撤稿状态和证据质量。

## Question-to-Answer Map

| User question | Direct answer | Evidence status | Detailed section |
|---|---|---|---|
| PubMed ESearch/EFetch、速率、`retmax`、日期 | ESearch 默认 XML/20 条，JSON 核心字段已实测；PubMed EFetch 使用 XML；无 key 3 rps；支持 `datetype` + 日期范围/相对日期；文档称 10,000，2026-08-20 实测裁剪为 9,999 | 官方规范 + 端点实测；9,999 是时间点条件性结论 | PubMed E-utilities contract；PubMed E-utilities scenario |
| ClinicalTrials.gov 版本、靶点参数、phase/status | 当前主 API 为 v2；使用 `query.intr`、`query.cond`、`query.term`/`AREA[...]`；无独立分子靶点字段；phase/status 路径分别为 `designModule.phases[]` 和 `statusModule.overallStatus` | 官方规范 + 端点实测；靶点相关性仍需项目评测 | ClinicalTrials.gov v2 contract；ClinicalTrials.gov scenario |
| Google Scholar、OpenAlex、Europe PMC | 未发现公开受支持 Scholar API；OpenAlex 适合跨学科和引用图谱，Europe PMC 适合生命科学、PMID/PMCID、全文/OA/预印本补充；两者不能完全等价 Scholar | Scholar 结论为高置信条件性；替代源能力有官方规范和端点实测 | Discovery source comparison；Scholarly Discovery Alternatives |
| PMID/NCT 真实存在回查 | PMID 用 ESummary 精确对象且无 error；NCT 用 `/studies/{nctId}` 的状态码和精确 ID 回显；HTTP 200、EFetch 或普通搜索命中都不够 | 权威端点实测已验证；NCT alias 301 尚待实测 | Strict existence verification；Citation Existence Verification |

## Task Implementation Requests

* 查证 PubMed E-utilities 的 `esearch`/`efetch` 返回字段、无 API key 速率限制、`retmax` 上限和时间过滤能力
* 查证 ClinicalTrials.gov 当前 API 版本、靶点/干预措施查询参数，以及试验阶段和状态字段
* 查证 Google Scholar 是否提供官方 API，并比较 OpenAlex 与 Europe PMC 的替代适用性和覆盖范围
* 定义通过 PMID 或 NCT 号程序化确认记录真实存在的引用回查机制
* 区分已验证证据、文档未保证的行为和仍需项目验证的假设
* 选定一套可实施的推荐方案并记录依据来源

## Scope and Success Criteria

* Scope: 数据源公开接口、官方文档、可重复最小请求、标识符存在性验证和面向 Agent 的集成建议；不评估药理学推理质量、商业数据库或完整系统架构
* Assumptions:
  * 当前日期为 2026-08-20，API 版本和限制以该日期可获取的官方资料为准
  * “真实存在”指权威源能返回与输入标识符一致的结构化记录，不等同于研究结论正确、记录未撤回或临床试验结果可信
  * 优先采用官方 API 和官方文档；第三方资料只能补充，不能单独支撑关键结论
* Success Criteria:
  * 四个研究问题均有官方或一手来源依据
  * 每项结论标记为“已验证”“条件性结论”或“仍是假设”
  * PMID 与 NCT 回查分别给出请求、判定条件、失败语义和建议测试用例
  * 至少评估两套可行集成方案，并明确推荐一种
  * 所有关键外部来源记录访问上下文和 URL

## Outline

1. PRD 中的相关技术声明和隐含约束
2. PubMed E-utilities 契约与运行限制
3. ClinicalTrials.gov API 契约与检索语义
4. Google Scholar、OpenAlex 与 Europe PMC 的覆盖和替代边界
5. PMID/NCT 引用回查算法与验收测试
6. 实现方案比较、风险和最终推荐

## Potential Next Research

* 用项目真实靶点和适应症构建 30 至 50 条金样本，量化 PubMed、Europe PMC 和 OpenAlex 的 Precision@K、Recall@K 与重复率
  * Reasoning: 官方契约只能证明接口可用，不能证明检索式在 Drug Target Scout 场景中的召回质量
  * Reference: prd-v0.1.md:154-157, 217-225
* 验证 NCT alias 的 HTTP 301 行为并确定审计策略
  * Reasoning: OpenAPI 声明 alias 重定向，但本轮未取得可重复 alias 样本
  * Reference: .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md
* 确定批量回查规模、缓存 TTL 和延迟目标
  * Reasoning: 单条确定性与批量吞吐之间的选择依赖实际引用数量和 10 分钟总时限
  * Reference: prd-v0.1.md:515-523, 551
* 增加撤稿、关注声明和临床记录一致性校验研究
  * Reasoning: 本轮只证明标识符可解析，不证明证据仍有效或支持具体论断
  * Reference: .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md

## Research Executed

### File Analysis

* prd-v0.1.md
  * PubMed、ClinicalTrials.gov 和 Google Scholar 被列为必选来源，OpenAlex 与 Europe PMC 被列为本次不建议实现的可选源：prd-v0.1.md:165-194
  * 文献 Agent 要求返回标题、摘要、PMID 和链接，Clinical Agent 要求返回 NCT、阶段、状态、适应症和干预：prd-v0.1.md:211-248
  * PRD 要求官方结构化源优先、部分失败可降级、关键结论有来源：prd-v0.1.md:373-375, 510-523
  * “前 10 至 20 条”与“只抓前 5 条”存在数量口径冲突：prd-v0.1.md:217, 515-517
  * 头号隐含缺口是引用回查算法、失败语义和验收阈值未定义：prd-v0.1.md:482-487, 510-512, 549-555

### Code Search Results

* 工作区未发现应用原型、依赖清单、API 客户端、配置或测试
* 除 PRD、Git 元数据和本轮研究文件外，没有可用于验证实现行为的代码
* 研究依据：.copilot-tracking/research/subagents/2026-08-20/prd-local-assumptions-research.md

### External Research

* NCBI E-utilities 官方参考与端点实测
  * [A General Introduction to the E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25497/)
  * [The E-utilities In-Depth](https://www.ncbi.nlm.nih.gov/books/NBK25499/)
  * [EFetch valid retmode and rettype table](https://www.ncbi.nlm.nih.gov/books/NBK25499/table/chapter4.T._valid_values_of__retmode_and/?report=objectonly)
  * [PubMed User Guide](https://pubmed.ncbi.nlm.nih.gov/help/#search-field-descriptions)
* ClinicalTrials.gov 官方 API、OpenAPI 与端点实测
  * [ClinicalTrials.gov Data API](https://clinicaltrials.gov/data-api/api)
  * [ClinicalTrials.gov API migration guide](https://clinicaltrials.gov/data-api/about-api/api-migration)
  * [ClinicalTrials.gov OpenAPI v2](https://clinicaltrials.gov/api/oas/v2)
  * [Complex search query guide](https://clinicaltrials.gov/find-studies/constructing-complex-search-queries)
* Google Scholar、OpenAlex 和 Europe PMC 官方资料与端点实测
  * [Google Scholar About](https://scholar.google.com/intl/en/scholar/about.html)
  * [Google APIs Explorer](https://developers.google.com/apis-explorer)
  * [Google Scholar robots.txt](https://scholar.google.com/robots.txt)
  * [OpenAlex API](https://help.openalex.org/api)
  * [OpenAlex works corpus](https://help.openalex.org/data/works/corpus/)
  * [OpenAlex snapshot](https://help.openalex.org/access/snapshot/)
  * [Europe PMC REST API](https://europepmc.org/RestfulWebService)
  * [Europe PMC About](https://europepmc.org/About)

### Project Conventions

* Standards referenced: Task Researcher 模式、HVE Core Markdown 与写作风格说明
* Instructions followed: 所有调查活动委派给 Researcher Subagent；主代理仅综合并更新 `.copilot-tracking/research/`
* Detailed evidence:
  * .copilot-tracking/research/subagents/2026-08-20/prd-local-assumptions-research.md
  * .copilot-tracking/research/subagents/2026-08-20/pubmed-eutilities-research.md
  * .copilot-tracking/research/subagents/2026-08-20/clinicaltrials-api-research.md
  * .copilot-tracking/research/subagents/2026-08-20/scholarly-discovery-alternatives-research.md
  * .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md
  * .copilot-tracking/research/subagents/2026-08-20/integration-alternatives-analysis.md
  * .copilot-tracking/research/subagents/2026-08-20/final-research-completeness-review.md

## Key Discoveries

### Evidence Classification

| Classification | Meaning |
|---|---|
| 已验证 | 官方规范明确说明，或官方端点的可重复响应直接证实 |
| 条件性结论 | 在特定参数、数据类型、时间点或服务条件下成立 |
| 仍是假设 | 官方资料未保证，或需要项目环境、负载、语义评测进一步验证 |

### Verified Evidence Versus Remaining Assumptions

| Topic | 已验证的证据 | 条件性结论或仍是假设 |
|---|---|---|
| PubMed | ESearch 默认 XML、默认 `retmax=20`；JSON 有 `header` 和 `esearchresult`；无 key 3 rps；支持日期参数；PubMed EFetch 应使用 XML | 当前 9,999 边界可能变化；摘要完整率、靶点查询召回率和结果质量需项目样本验证 |
| ClinicalTrials.gov | 当前主 API 为 v2；`/studies` 与 `/studies/{nctId}` 可用；phase/status 路径已验证 | 无公开独立靶点字段，因此靶点词召回不等于目标机制匹配；具体召回率需项目验证 |
| Google Scholar | 未发现公开、受支持 Scholar API；Custom Search API 不是 Scholar API；robots 规则限制核心搜索路径 | Google 未公开一句绝对的“API 不存在”声明，因此形式上属于高置信条件性结论；不可假设有隐藏企业接口 |
| OpenAlex | 官方 REST API、CC0 元数据、快照、外部 PMID/DOI、引用网络可用 | 生命科学字段完整率、摘要和全文覆盖并非全量，不能假设等价于 PubMed 或 Scholar |
| Europe PMC | 官方 REST API、生命科学语料、PMID/DOI/PMCID、引用和全文子集可用 | 全文不是全记录可得；不同 `SRC` 的字段语义和检索质量需专项验证 |
| 引用存在性 | PMID ESummary 和 NCT 单条 v2 端点能区分存在、格式错误与不存在；HTTP 200 本身不构成存在证明 | NCT alias 301 尚未实测；PMID 最大位数是项目策略而非本轮找到的 NCBI 硬契约 |

### Project Structure

当前仓库处于“只有 PRD、没有实现”的阶段。后续规划需要把本研究中的 API 路径、字段映射、错误状态和验收矩阵直接转化为接口契约与合同测试，而不能依赖现有代码惯例。

### Implementation Patterns

* 发现与验证分离
  * 搜索端点负责召回候选记录
  * 权威单条/摘要端点负责确认标识符存在
  * LLM 只能总结已经过回查的记录，不能自行生成或修正 PMID/NCT
* 主证据与补充证据分层
  * PubMed 与 ClinicalTrials.gov 是主证据源
  * Europe PMC 用于生命科学扩展、全文/OA/预印本与引用补充
  * OpenAlex 用于跨学科发现和引用图谱补充
* 每条引用保留审计包
  * 规范化输入、权威源、请求方法、HTTP 状态、精确回显 ID、验证时间、响应哈希、最终状态
* 上游不确定性不折叠为“不存在”
  * 超时、429 和 5xx 是 `TRANSIENT_*`
  * 格式错误是 `INVALID_FORMAT`
  * 权威源明确无记录才是 `NOT_FOUND`

### Complete Examples

#### PubMed discovery and fetch

```http
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=asthma%5BTitle%5D&retmode=json&retmax=20&usehistory=y&tool=drug_target_scout&email=developer%40example.org
```

ESearch JSON 的实测核心结构：

```json
{
  "header": {
    "type": "esearch",
    "version": "0.3"
  },
  "esearchresult": {
    "count": "104860",
    "retmax": "20",
    "retstart": "0",
    "idlist": ["..."],
    "translationset": [],
    "querytranslation": "\"asthma\"[Title]",
    "querykey": "1",
    "webenv": "MCID_..."
  }
}
```

```http
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30049270&retmode=xml&tool=drug_target_scout&email=developer%40example.org
```

PubMed EFetch 应解析 `PubmedArticleSet > PubmedArticle > MedlineCitation` 和 `PubmedData`。不要请求或依赖 `retmode=json`，该组合不在 PubMed EFetch 的官方结构化契约中，本轮实测只返回纯文本 ID。

#### ClinicalTrials.gov discovery

```http
GET https://clinicaltrials.gov/api/v2/studies?query.intr=imatinib&query.cond=leukemia&pageSize=20&fields=NCTId,BriefTitle,Condition,InterventionName,OverallStatus,Phase&format=json
```

字段路径：

```text
NCT ID: protocolSection.identificationModule.nctId
Overall status: protocolSection.statusModule.overallStatus
Phase: protocolSection.designModule.phases[]
Interventions: protocolSection.armsInterventionsModule.interventions[]
```

`phases` 对观察性研究等记录可以缺失。实现必须把缺失值表示为 `null` 或 `not_applicable`，不能推断为 `NA`。

#### Strict existence verification

```text
function verify_pmid(raw_id):
  id = trim(raw_id)
  if id does not match project-configured positive-integer PMID policy:
    return INVALID_FORMAT

  response = GET NCBI ESummary(db=pubmed, id=id, retmode=json)
  if timeout, 429, or 5xx:
    return TRANSIENT_RETRYABLE
  if response.error contains "Invalid uid":
    return INVALID_FORMAT
  if id is absent from result.uids:
    return NOT_FOUND
  if result[id] is absent or contains error:
    return NOT_FOUND or UPSTREAM_SEMANTIC_ERROR by error type
  return EXISTS only when the exact id-keyed object exists without error

function verify_nct(raw_id):
  id = uppercase(trim(raw_id))
  if id does not match ^NCT0*[1-9][0-9]{0,7}$:
    return INVALID_FORMAT

  response = GET https://clinicaltrials.gov/api/v2/studies/{id}
  if response is 400:
    return INVALID_FORMAT
  if response is 404:
    return NOT_FOUND
  if timeout, 429, or 5xx:
    return TRANSIENT_RETRYABLE
  if response is not 200:
    return UPSTREAM_PROTOCOL_ERROR
  observed = protocolSection.identificationModule.nctId
  return EXISTS only when observed exactly matches id
```

### API and Schema Documentation

#### PubMed E-utilities contract

| Concern | Verified behavior | Implementation consequence |
|---|---|---|
| ESearch default output | XML | Set `retmode=json` explicitly for discovery |
| ESearch default database | `pubmed` | Still pass `db=pubmed` explicitly for auditability |
| ESearch default `retmax` | 20 | Set bounded `retmax` explicitly |
| ESearch JSON | `header`, `esearchresult`; core fields include `count`, `retmax`, `retstart`, `idlist`, `translationset`, `querytranslation` | Treat optional blocks as sparse; `usehistory=y` adds `querykey` and `webenv` |
| EFetch PubMed | XML by default; text supports `medline`, `uilist`, `abstract` | Use XML for structured article metadata and abstract extraction |
| No API key rate | 3 requests per second per IP | Central host-level limiter at no more than 3 rps; avoid parallel subagents bypassing it |
| API key rate | 10 requests per second by default | Optional for DEMO; higher rates require NCBI approval |
| `tool` and `email` | Officially requested; registration matters for restoring blocked clients | Configure developer contact and stable tool name; never use end-user email |
| `retmax` | Docs often say 10,000; PubMed live endpoint clipped to 9,999 on 2026-08-20 | Keep client cap configurable and parse Warning/Error; DEMO only needs 5 to 20 |
| Date filtering | `datetype`, paired `mindate/maxdate`, or `reldate`; formats `YYYY`, `YYYY/MM`, `YYYY/MM/DD` | Expose explicit date type; do not conflate publication date with entry date |

PubMed 日期字段包括 `[dp]`/`[pdat]`、`[edat]`、`[crdt]`、`[mhda]`、`[epdat]` 和 `[ppdat]`。API 参数过滤与检索式字段限制是两套入口，不能假设复杂查询时完全等价。

#### ClinicalTrials.gov v2 contract

| Concern | Verified behavior | Implementation consequence |
|---|---|---|
| Current API | v2, base `https://clinicaltrials.gov/api/v2` | 不使用 classic `/api/query/*`；2026-08-20 的版本端点返回 `2.0.5` |
| Search | `GET /studies` | 使用 `query.intr`、`query.cond`、`query.term` 和必要的 `filter.*` |
| Single record | `GET /studies/{nctId}` | 用作严格存在性回查 |
| Target search | No independent molecular-target field found in public schema | 将其标为 intervention/text retrieval，不能标成结构化靶点匹配 |
| Phase | `protocolSection.designModule.phases[]` | 可缺失，不要伪造 |
| Status | `protocolSection.statusModule.overallStatus` | 按官方枚举保存原始值，再做业务映射 |
| Pagination | `pageSize` default 10, values over 1000 clipped; use `nextPageToken` | DEMO 使用固定小页；续页参数保持一致 |
| Fields | Omit for all fields or send non-empty field list | 明确字段白名单，减少响应和 schema 漂移面 |

Phase 枚举为 `NA`, `EARLY_PHASE1`, `PHASE1`, `PHASE2`, `PHASE3`, `PHASE4`。Overall status 包括 recruiting、completed、terminated、withdrawn、suspended 等官方枚举。业务层可以映射为积极/失败/不确定信号，但该映射尚未在 PRD 定义，仍是假设。

#### Discovery source comparison

| Dimension | Google Scholar | OpenAlex | Europe PMC |
|---|---|---|---|
| Official supported API | 未发现 | 有 | 有 |
| Primary scope | 广泛学术网页检索，排序黑盒 | 跨学科知识图谱 | 生命科学文献平台 |
| 2026-08 coverage evidence | 无统一官方机器计数 | Core 约 320M+，all 约 510M+ works，口径动态 | API 实测约 48.64M records |
| Biomedical identifiers | 页面可能显示，缺少官方 API 契约 | Works `ids` 可含 DOI/PMID | PMID/PMCID/DOI 原生可查 |
| Citation graph | 页面 `Cited by`，无公开官方 API | `referenced_works`, `cited_by_count` | citations/references endpoints |
| Abstract/full text | 依外部来源 | 摘要和全文均为子集 | 摘要、OA/full-text 也是子集 |
| Bulk/legal automation | 无同等级官方通道 | CC0 metadata and snapshots | Official API and bulk downloads |
| DEMO role | 不作为直接依赖 | 跨学科和引用网络补充 | 生物医学补充与全文/OA/预印本扩展 |

### Configuration Examples

```yaml
sources:
  pubmed:
    base_url: https://eutils.ncbi.nlm.nih.gov/entrez/eutils
    requests_per_second_without_key: 3
    search_retmax: 20
    tool: drug_target_scout
    email_env: NCBI_CONTACT_EMAIL
  clinical_trials:
    base_url: https://clinicaltrials.gov/api/v2
    page_size: 20
  europe_pmc:
    base_url: https://www.ebi.ac.uk/europepmc/webservices/rest
    role: biomedical_supplement
  openalex:
    base_url: https://api.openalex.org
    role: cross_domain_and_citation_graph

citation_verification:
  required_before_report: true
  transient_retry_attempts: 3
  accepted_terminal_state: EXISTS
  cache_ttl_exists_seconds: TBD
  cache_ttl_not_found_seconds: TBD
```

缓存 TTL、并发和重试退避数值需要负载目标与上游政策验证，示例中的 `3` 次重试是设计建议，不是官方保证。

## Technical Scenarios

### PubMed E-utilities

**Requirements:**

* 通过 ESearch 找候选 PMID
* 通过 EFetch XML 取得标题、摘要和元数据
* 支持 publication/entry 等明确日期范围
* 全部调用遵守同一进程级 3 rps 限制（无 API key）
* 对 WarningList、空摘要、格式错误和上游失败显式建模

**Preferred Approach:**

采用 ESearch JSON 发现、EFetch XML 批量取内容、ESummary JSON 独立验证 PMID 的三段式。三者职责不同，不应为了减少一个端点而混用：EFetch 已实测会把 `ABC123` 强制解释成 PMID `123`，不适合存在性判据。

```text
query builder -> ESearch JSON -> candidate PMIDs
candidate PMIDs -> EFetch XML -> evidence records
all emitted PMIDs -> ESummary JSON -> verified citations
```

#### Considered Alternatives

* 只使用 ESearch
  * 无法提供完整摘要字段，且精确 ID 查询会把格式错误与不存在都压成零命中
* 只使用 EFetch
  * 非法 ID 存在强制转换误判风险，不能作为回查主方法
* 用 Europe PMC 替代 PubMed 作为真实性权威源
  * Europe PMC 可补充检索，但 PMID 的权威存在性仍应由 NCBI 判定

### ClinicalTrials.gov

**Requirements:**

* 使用 v2 `/studies` 搜索干预、疾病和相关文本
* 保留原始 NCT、phase、overall status、condition 和 intervention
* 将“靶点词命中”明确标成候选相关性，不标成结构化 target match
* 用单条 `/studies/{nctId}` 对最终引用回查

**Preferred Approach:**

先用 `query.intr=<target-or-drug>` 与 `query.cond=<indication>` 召回，并在需要时用 `query.term=AREA[...]` 收窄；再由规则/模型执行靶点同义词和机制相关性重排。阶段与状态只从结构化路径读取。

```text
target/drug synonyms + indication
  -> query.intr/query.cond or AREA query
  -> candidate studies
  -> exact NCT verification
  -> mechanism relevance ranking
```

#### Considered Alternatives

* 把 `query.term=<target>` 当作精确靶点检索
  * 它是全文搜索语义，会产生与分子靶点无关的文本命中
* 使用 `query.id` 回查 NCT
  * 实测 `ABC123` 可因次级 ID 命中无关 NCT，不适合严格身份验证
* 继续使用 classic API
  * 已有 v2 官方契约，classic 样例在 2026-08-20 返回 404

### Scholarly Discovery Alternatives

**Requirements:**

* 不依赖未公开 API 或网页抓取
* 保持主证据权威性，同时扩展预印本、全文、引用和跨学科线索
* 对每个来源保留来源类型，不把聚合记录冒充 PubMed 原始记录

**Preferred Approach:**

用 Europe PMC 替代 PRD 中 Scholar 的生物医学补充角色，用 OpenAlex 作为可选跨学科/引用网络补充。两者均不取代 PubMed 和 ClinicalTrials.gov 的权威回查。

```text
PubMed ------------------------ primary literature evidence
Europe PMC ------------------- biomedical expansion and OA/full-text clues
OpenAlex --------------------- cross-domain discovery and citation graph
ClinicalTrials.gov ----------- primary trial evidence
NCBI/ClinicalTrials exact APIs authority verification
```

#### Considered Alternatives

* 直接抓取 Google Scholar
  * 没有公开受支持 API 契约，核心路径受 robots 规则限制，稳定性和合规性不适合作为 DEMO 必选依赖
* 采购第三方 Scholar API
  * 能降低接入时间，但仍受供应商抓取方式、覆盖和成本影响；对本 DEMO 没有必要
* 仅使用 OpenAlex
  * 跨学科广度较强，但生物医学语义、摘要和全文字段完整率不如 Europe PMC 领域原生
* 仅使用 Europe PMC
  * 适合生命科学，但无法覆盖 OpenAlex 的跨学科广度和知识图谱角色

### Citation Existence Verification

**Requirements:**

* 引用写入报告前必须处于 `EXISTS` 状态
* 精确比对权威源返回 ID，不依赖 HTTP 200 或搜索命中
* `INVALID_FORMAT`、`NOT_FOUND`、`TRANSIENT_*` 和 `UPSTREAM_*` 分开处理
* 保存请求方法、时间、响应哈希和判定理由
* 上游不可用时不得把引用标成不存在，也不得无验证进入最终关键结论

**Preferred Approach:**

PMID 使用 ESummary JSON，NCT 使用 v2 单条端点。批量 PMID 可使用多 ID ESummary 后逐项验证；批量 NCT 可使用 `filter.ids` 后对请求集合与返回集合做精确 join。最终报告只接收通过权威源回查的引用。

```text
candidate citation
  -> normalize
  -> strict syntax gate
  -> authority request
  -> exact echo match
  -> EXISTS / NOT_FOUND / INVALID_FORMAT / TRANSIENT / UPSTREAM_ERROR
  -> audit record
  -> report eligibility gate
```

#### Minimum Acceptance Matrix

| Case | Input | Authority method | Expected result |
|---|---|---|---|
| Valid PMID | `31452104` | ESummary | Exact result object, no nested error, `EXISTS` |
| Invalid PMID | `ABC123` | Local gate/ESummary safety test | `INVALID_FORMAT` |
| Missing PMID | `999999999` | ESummary | Nested `cannot get document summary`, `NOT_FOUND` |
| EFetch coercion guard | `ABC123` | EFetch safety test | Method rejected even if response contains PMID `123` |
| Valid NCT | `NCT04280705` | `/studies/{id}` | HTTP 200 and exact NCT echo, `EXISTS` |
| Invalid NCT | `ABC123` | Local gate/single endpoint | `INVALID_FORMAT` or HTTP 400 |
| Missing NCT | `NCT99999999` | `/studies/{id}` | HTTP 404, `NOT_FOUND` |
| NCT search guard | `ABC123` | `query.id` | Method blocked for existence checks |
| Upstream failure | valid ID with mocked 429/5xx/timeout | Either authority | Retry bounded; final state remains transient, never not-found |

#### Considered Alternatives

* 检查引用 URL 是否返回 200
  * 页面可重定向、缓存或返回错误页面，且不能证明回显记录与输入 ID 一致
* 复用普通搜索端点的“有命中”结果
  * 搜索语义可匹配别名、次级 ID 或文本，已发现 NCT `query.id` 误命中风险
* 让 LLM 检查引用格式
  * 只能检查表面格式，无法证明权威记录存在

### Recommended Integration

选择 **同进程集中式 Citation Verification Gateway + PubMed/ClinicalTrials.gov 主证据 + Europe PMC 补充 + OpenAlex 可选**。

该选择由两类依据组成：

* 官方证据决定的事实
  * PMID 和 NCT 有明确权威回查端点
  * Scholar 缺少可确认的公开受支持 API
  * Europe PMC 和 OpenAlex 提供官方可编程接口
  * ClinicalTrials.gov 没有公开的独立分子靶点字段
* 项目设计选择
  * 验证逻辑集中在同一进程的确定性模块，不拆成微服务
  * 默认只验证 Top5，Top20 使用有界批处理开关
  * 补充源失败不阻塞主结论，主源失败则降级为 `NEED_MORE_DATA`
  * 未通过存在性回查的记录不得进入关键结论证据集

#### Selected Architecture

```text
Orchestrator
  -> Query Planner
       -> PubMed discovery adapter
       -> ClinicalTrials.gov v2 discovery adapter
       -> Europe PMC supplement adapter
       -> optional OpenAlex citation/discovery adapter
  -> Citation Verification Gateway
       -> NCBI ESummary for PMID
       -> ClinicalTrials.gov /studies/{nctId} for NCT
  -> Evidence Assembler and audit store
  -> LLM synthesis over verified primary evidence
  -> GO / NO_GO / NEED_MORE_DATA
```

Citation Verification Gateway 是确定性业务组件，不是 Agent。它只接受标识符及来源类型，返回类型化状态和审计证据，不进行自然语言推理。该边界把“发现是否相关”和“标识符是否真实存在”拆成两个可独立测试的问题。

#### Module Boundaries

1. Query Planner
   * 输入 target、indication、time window、focus 和 topK mode
   * 生成各来源的有界查询计划和同义词集合
2. Source Adapters
   * `PubMedAdapter` 负责 ESearch 与 EFetch
   * `ClinicalTrialsAdapter` 负责 v2 `/studies` 候选召回
   * `EuropePMCAdapter` 负责生物医学补充
   * `OpenAlexAdapter` 负责可选跨学科和引用网络扩展
3. Citation Verification Gateway
   * PMID 使用 ESummary
   * NCT 使用 `/studies/{nctId}`
   * 统一 normalization、exact-match、重试、错误分类和审计
4. Evidence Assembler
   * 只把 `EXISTS` 的主证据放入关键结论集
   * 去重、排序并保留来源层级和冲突
5. Synthesis Engine
   * 只总结组装后的证据
   * 不生成新 PMID/NCT，不覆盖权威结构化字段

#### Minimum Data Model

```json
{
  "query": {
    "target": "EGFR",
    "indication": "non-small cell lung cancer",
    "timeWindow": "2021/01/01..2026/08/20",
    "topKMode": "TOP5_SYNC"
  },
  "evidence": [
    {
      "source": "PUBMED",
      "sourceTier": "PRIMARY",
      "canonicalId": "31452104",
      "title": "...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/31452104/",
      "structured": {},
      "verification": {
        "status": "EXISTS",
        "method": "esummary",
        "checkedAt": "2026-08-20T09:00:00Z",
        "httpStatus": 200,
        "responseHash": "sha256:...",
        "reasonCode": "EXACT_ID_MATCH"
      }
    }
  ],
  "decision": {
    "label": "NEED_MORE_DATA",
    "rationale": [],
    "uncertainty": []
  }
}
```

允许的验证状态至少包括：

```text
EXISTS
INVALID_FORMAT
NOT_FOUND
TRANSIENT_TIMEOUT
TRANSIENT_RATE_LIMIT
TRANSIENT_SERVER_ERROR
UPSTREAM_PROTOCOL_ERROR
UPSTREAM_SEMANTIC_ERROR
UNVERIFIED_SUPPLEMENT
```

#### Source-of-Truth Rules

| Fact | Authority | Rule |
|---|---|---|
| PMID exists | NCBI ESummary | Exact UID-keyed object must exist without nested error |
| PubMed title/abstract/metadata | NCBI PubMed XML | Supplement sources may enrich but not overwrite authority fields silently |
| NCT exists | ClinicalTrials.gov `/studies/{nctId}` | HTTP 200 plus exact `identificationModule.nctId` match |
| Trial phase/status | ClinicalTrials.gov v2 record | Preserve raw enum and missing values before business mapping |
| Europe PMC/OpenAlex record | Respective official API | Evidence remains `SUPPLEMENT`; it cannot establish PMID/NCT authority by itself |
| Target-mechanism relevance | Project ranking/evaluation layer | Must be labeled as inferred relevance, not API-provided target identity |

#### Failure and Degradation Rules

| Situation | Report behavior | Decision impact |
|---|---|---|
| Europe PMC or OpenAlex unavailable | Return primary evidence and show supplement coverage warning | Does not force downgrade |
| PubMed or ClinicalTrials.gov completely unavailable | Return available partial evidence with source failure | Force `NEED_MORE_DATA` for the full investment decision |
| Citation is `INVALID_FORMAT` or `NOT_FOUND` | Exclude from key evidence and record validation failure | Never cite it as support |
| Citation check is transiently unavailable | Retry with bounded backoff; if exhausted, keep unverified and exclude from key evidence | Do not reinterpret as not found |
| No primary citation reaches `EXISTS` | Return diagnostic evidence only | Force `NEED_MORE_DATA` |
| Supplement conflicts with authority record | Preserve conflict for review | Authority field wins; confidence decreases |

#### TopK Strategy

PRD 的 Top 10 至 20 与 Top5 冲突采用显式模式解决，而不是在实现中保留模糊常量：

* `TOP5_SYNC` 是 DEMO 默认值
  * 在同步时限内完成发现、内容拉取和权威回查
  * 适合头号验收指标和 10 分钟目标
* `TOP20_BOUNDED_BATCH` 是可选增强
  * 仍在同一进程内有界执行，不引入队列
  * 时间预算不足时退回已验证 Top5，并标注 coverage

#### Implementation Order

1. 定义 evidence、verification 和 failure schema
2. 实现 PMID/NCT Citation Verification Gateway 及合同测试
3. 实现 PubMed 与 ClinicalTrials.gov discovery adapters
4. 打通 `TOP5_SYNC`、审计记录和部分失败降级
5. 增加 Europe PMC supplement adapter
6. 增加可选 OpenAlex citation/discovery adapter
7. 增加 `TOP20_BOUNDED_BATCH` 与时间预算回退
8. 使用真实靶点金样本评测召回、相关性和来源重复率

#### Acceptance Criteria

| Criterion | Required result |
|---|---|
| Time | 默认 Top5 查询在 10 分钟内完成 |
| Citation existence | 关键结论引用 100% 为 `verification.status=EXISTS` |
| Exact identity | 每个 PMID/NCT 均与权威源回显精确匹配 |
| Error taxonomy | `INVALID_FORMAT`, `NOT_FOUND`, `TRANSIENT_*`, `UPSTREAM_*` 可区分和审计 |
| Supplement failure | Europe PMC/OpenAlex 失败时主流程仍可返回，并显示覆盖警告 |
| Primary failure | PubMed 或 ClinicalTrials.gov 整源失败时强制 `NEED_MORE_DATA` |
| Conflict handling | 补充源不得静默覆盖主源结构化事实 |
| Repeatability | 固定 fixture 下字段、验证状态和降级决策可稳定重放 |
| Safety guards | EFetch 不用于 PMID existence；`query.id` 不用于 NCT existence |

这些标准验证“引用真实存在”的头号指标。药物靶点相关性、撤稿状态、试验可信度和 Go/No-Go 决策质量必须使用另外的评测集，不能从 existence pass 推导。

#### Considered Alternatives

| Alternative | Benefit | Rejection reason |
|---|---|---|
| A. 每个 adapter 内联验证 | 初期代码最少 | 错误分类、审计字段和重试策略会分散，合同测试重复，长期最易漂移 |
| B. 同进程集中式 gateway | 一致、可测试、无额外部署 | **Selected**；初期多一个模块边界，但总复杂度最低 |
| C. 异步队列/离线服务 | 适合海量引用 | DEMO 引入队列、幂等、回填和双阶段 UI，增加 10 分钟验收风险 |
| 1. Scholar/web 必选直译 | 最符合 PRD 字面 | Scholar 无可确认官方 API，结果不可稳定重放，第三方依赖不必要 |
| 2. Primary + Europe PMC + optional OpenAlex | 官方 API、分层清晰、覆盖平衡 | **Selected**；需要把 PRD 的 Scholar 必选改写为补充发现能力 |
| 3. 仅 PubMed + ClinicalTrials.gov | 实现最小 | 缺少 PRD 需要的综述、预印本、引用和跨学科补充广度 |

## Final Recommendation

按 B+2 进入实现规划，不等待更多外部研究。规划前应在 PRD 中明确以下变更：

1. 将 Google Scholar 从“必选数据源”改为“补充学术发现能力”，默认实现为 Europe PMC，OpenAlex 可选；不直接抓取 Scholar
2. 将 ClinicalTrials.gov 的“靶点检索”表述改为“基于干预、MeSH 和文本的候选试验召回”，另设机制相关性排序
3. 新增 Citation Verification Gateway，要求关键结论 PMID/NCT 的存在性验证通过率为 100%
4. 把 Top5 定义为 DEMO 默认，把 Top20 定义为有界增强模式
5. 明确主源失败强制 `NEED_MORE_DATA`，补充源失败只降低覆盖度

第一阶段研究没有阻塞开发的缺口。NCT alias 301、PMID 位数上限和具体缓存 TTL 是非阻塞项，应通过可配置策略与合同测试处理。
