<!-- markdownlint-disable-file -->

# Task Research Phase 2: Drug Target Scout 实现替代方案评估

## 研究状态

- Status: Complete
- Date: 2026-08-20
- Scope: 仅基于工作区 PRD 与已产出研究文档，形成可落地 DEMO 方案选择，不修改 PRD 与主研究文档。

## 研究问题（本次必须回答）

1. 在“引用必须可验证、10 分钟内返回、允许部分失败降级”的约束下，A/B/C 三种引用回查架构哪种最可实施。
2. 在 1/2/3 三种来源组合中，哪种最符合 PRD 目标与当前已验证技术事实。
3. 如何给出可执行的模块边界、最小数据模型、故障语义、测试与验收标准。
4. 第一阶段研究是否存在阻塞缺口。

---

## 一、官方证据决定的事实（非设计偏好）

### F1. PRD 明确把 PubMed、ClinicalTrials.gov、Google Scholar/Web 补充纳入 MVP 范围

- PRD 明确列出 Google Scholar 为必选来源，并强调通过搜索代理/第三方 API/web search 方式接入，不建议直接爬虫。
- PRD 明确 PubMed 与 ClinicalTrials.gov 是主结构化证据层。

Evidence:
- prd-v0.1.md:171-178
- prd-v0.1.md:183
- prd-v0.1.md:373-374
- prd-v0.1.md:533
- prd-v0.1.md:565

### F2. PRD 的交付约束：10 分钟、可解释引用、部分失败可降级

Evidence:
- prd-v0.1.md:510
- prd-v0.1.md:521-522
- prd-v0.1.md:551-552

### F3. PRD 内部存在结果条数口径冲突（Top 10-20 vs 只抓前 5）

Evidence:
- prd-v0.1.md:217
- prd-v0.1.md:515

### F4. ClinicalTrials.gov v2 是当前主 API；不存在独立分子靶点结构化字段

- 当前应使用 v2（`https://clinicaltrials.gov/api/v2`）。
- 公开结构与查询能力下，靶点检索本质上是干预/术语/文本命中，不等同 target ontology 精确匹配。

Evidence:
- .copilot-tracking/research/subagents/2026-08-20/clinicaltrials-api-research.md:8
- .copilot-tracking/research/subagents/2026-08-20/clinicaltrials-api-research.md:28
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:11

### F5. 引用存在性验证必须走权威单条/摘要回查；不能用普通搜索命中替代

- PMID 推荐 ESummary 精确回显检查。
- NCT 推荐 `/studies/{nctId}`。
- `query.id` 存在误命中风险，不能用于严格 existence check。

Evidence:
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:12
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:425
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:449
- .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md:116-121
- .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md:147-149

### F6. Scholar 无可确认的公开受支持官方 API；Europe PMC + OpenAlex 是可编程补充路径

Evidence:
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:10
- .copilot-tracking/research/subagents/2026-08-20/scholarly-discovery-alternatives-research.md:34-49
- .copilot-tracking/research/subagents/2026-08-20/scholarly-discovery-alternatives-research.md:97-116

External official sources:
- [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api)
- [ClinicalTrials.gov OpenAPI v2](https://clinicaltrials.gov/api/oas/v2)
- [NCBI E-utilities In-Depth](https://www.ncbi.nlm.nih.gov/books/NBK25499/)
- [Google Scholar About](https://scholar.google.com/intl/en/scholar/about.html)
- [OpenAlex API](https://help.openalex.org/api)
- [Europe PMC REST API](https://europepmc.org/RestfulWebService)

---

## 二、项目设计选择（非官方事实，需要团队拍板）

以下内容是“设计选择”，不是官方资料直接给出的事实：

1. 选择 A/B/C 中哪种回查架构。
2. 选择 1/2/3 哪种来源组合作为 DEMO 主路径。
3. 何时采用 Top 5，何时采用 Top 10-20（同步/批量切换规则）。
4. 回查失败时是降级为 `Need More Data` 还是部分输出并显式不确定。
5. 证据冲突时 source-of-truth 优先级。

---

## 三、架构替代方案（A/B/C）Technical Scenario Analysis

## A. Adapter 内联验证并直接返回已验证记录

### 原则
- 每个 source adapter 自己做 normalize + verify + return。

### 数据流
- `Adapter(PubMed)` 拉取并验证 PMID。
- `Adapter(CTGov)` 拉取并验证 NCT。
- `Adapter(Web/Scholar)` 自定义验证逻辑。
- Orchestrator 只做聚合。

### 优势
- 上手快，局部改动少。
- 早期 demo 可最快出结果。

### 理想场景
- 数据源很少、验证规则简单且长期稳定。

### 限制
- 验证逻辑重复，跨 adapter 容易漂移。
- 审计语义不一致（尤其 `INVALID_FORMAT/NOT_FOUND/TRANSIENT`）。
- 难保证“最终报告所有引用一致可信”。

### 项目惯例对齐
- 与“关键结论要有来源”目标部分对齐，但难以长期维持一致性。
- 对“部分失败降级”会出现 adapter 各自定义，系统行为不一致。

Evidence:
- prd-v0.1.md:510
- prd-v0.1.md:521-522
- .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md:292

### 复杂度
- 初期低，中后期高（重复维护成本高）。

### 故障语义
- 高风险：同一错误在不同 adapter 被映射成不同状态。

### 测试和验收影响
- 需要在每个 adapter 重复同一套 existence contract tests。
- 验收成本高，回归风险大。

---

## B. 同进程集中式 Citation Verification Gateway（确定性模块）

### 原则
- 所有候选引用先过统一 deterministic gateway，再进入报告层。
- gateway 不是独立微服务，而是同进程模块。

### 数据流
- `Discovery adapters` 只负责召回候选证据。
- `Citation Verification Gateway` 统一执行：
  - PMID -> ESummary
  - NCT -> `/studies/{nctId}`
- `Evidence Assembler` 只接收 `EXISTS` 或带可解释状态的记录。

### 优势
- 统一错误语义与审计字段。
- 回查规则单点演进，便于测试与验收。
- 与“关键结论必须有来源、可解释”最一致。

Evidence:
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:478
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:425
- .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md:133
- .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md:147

### 理想场景
- 多来源证据汇总且必须统一“存在性/失败语义”的系统。

### 限制
- 需要额外模块边界设计。
- 如果网关实现不当，可能成为延迟瓶颈。

### 项目惯例对齐
- 对齐 PRD 的可解释性、部分失败、MVP 一体化实现诉求。

Evidence:
- prd-v0.1.md:510
- prd-v0.1.md:521-522
- prd-v0.1.md:551

### 复杂度
- 初期中等；长期最低（总拥有成本最优）。

### 故障语义
- 可统一为：`EXISTS / INVALID_FORMAT / NOT_FOUND / TRANSIENT_* / UPSTREAM_*`。

### 测试和验收影响
- 一套 gateway 合同测试覆盖全部 adapter。
- 更容易定义端到端验收门槛。

---

## C. 异步队列或离线批量验证服务

### 原则
- 先返回初步结果，引用回查异步完成并回填。

### 数据流
- 在线流程产出“暂未验证/部分验证”报告。
- 队列消费后写入最终验证状态。

### 优势
- 高吞吐场景下可扩展。
- 适合海量引用离线校验。

### 理想场景
- 非实时报告、可容忍延迟一致性。

### 限制
- 与“10 分钟内给可用结果”并不天然冲突，但会增加解释复杂度（先给未验证结论是否允许）。
- DEMO 阶段工程负担过重（队列、幂等、回填、状态 UI）。

Evidence:
- prd-v0.1.md:551
- prd-v0.1.md:510

### 项目惯例对齐
- 对齐规模化需求，但不对齐当前“1~2 周可演示 MVP”优先级。

Evidence:
- prd-v0.1.md:555

### 复杂度
- 初期高，运维复杂度高。

### 故障语义
- 需要处理“已返回报告但回查失败/超时”的二阶段一致性。

### 测试和验收影响
- 验收需要区分“初稿”和“终稿”，增加产品与测试成本。

---

## 四、来源组合替代方案（1/2/3）Technical Scenario Analysis

## 1) PubMed + ClinicalTrials.gov + Google Scholar/web search（PRD 必选直译）

### 原则
- 保持 PRD 文义一致，覆盖主证据 + 广度补充。

### 优势
- 与当前 PRD 字面最一致。
- 对用户叙事“PubMed + CT + Scholar”最直观。

### 理想场景
- 运行环境有稳定可控的 web search/第三方搜索 API。

### 限制
- Scholar 官方可编程能力不确定，工程稳定性受外部搜索能力强依赖。
- 补充层一致性与可复现性弱于官方结构化 API。

Evidence:
- prd-v0.1.md:171-178
- prd-v0.1.md:183
- .copilot-tracking/research/subagents/2026-08-20/scholarly-discovery-alternatives-research.md:34-49

### 复杂度
- 中等（取决于宿主 web search 可用性）。

### 故障语义
- 需要明确 `SUPPLEMENT_UNAVAILABLE`，且不能污染主证据结论。

### 测试和验收影响
- 需要稳定重放测试数据；web search 结果漂移会导致快照测试脆弱。

---

## 2) PubMed + ClinicalTrials.gov 主证据，Europe PMC 补充，OpenAlex 可选

### 原则
- 主证据全部官方结构化 API；补充层也尽量官方可编程。

### 优势
- 与“主证据优先官方 API”高度一致。
- 生物医学补充（Europe PMC）与跨学科补充（OpenAlex）职责清晰。
- 比组合 1 更可测试、可审计、可复现。

Evidence:
- prd-v0.1.md:373-374
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:10
- .copilot-tracking/research/subagents/2026-08-20/scholarly-discovery-alternatives-research.md:97-116

### 理想场景
- 要求可控 API 契约与可重复验收的 DEMO。

### 限制
- 与 PRD “Scholar 必选”字面不完全一致，需要产品口径澄清：
  - 可以解释为“Scholar/Web 补充能力等价由可编程官方补充源实现”。

Evidence:
- prd-v0.1.md:171-173
- prd-v0.1.md:190-194

### 复杂度
- 中等偏低（可显著降低不确定性）。

### 故障语义
- 主证据与补充证据分层后，降级策略更清晰：主证据失败才影响核心结论。

### 测试和验收影响
- 便于构建稳定 fixtures 与合同测试。

---

## 3) 仅 PubMed + ClinicalTrials.gov 极简 DEMO

### 原则
- 只做两大主证据源，最小闭环。

### 优势
- 开发最快，稳定性高。
- 引用回查链路最简洁。

### 理想场景
- 非常紧迫的内部演示，只验证主证据流程。

### 限制
- 不满足 PRD 对 Scholar/Web 补充层期待。
- 对竞争情报与综述广度支撑偏弱。

Evidence:
- prd-v0.1.md:171-173
- prd-v0.1.md:533

### 复杂度
- 最低。

### 故障语义
- 简单，但当两源之一失败时，结果信息不足风险上升。

### 测试和验收影响
- 最容易通过技术验收，但可能不满足产品叙事验收。

---

## 五、推荐组合（最终选择）

## 推荐：B + 2

- 架构：同进程集中式 Citation Verification Gateway（B）
- 来源：PubMed + ClinicalTrials.gov 主证据，Europe PMC 补充，OpenAlex 可选（2）

### 选择理由

1. 最符合“可实现且可验证”原则：
- 主证据都可走官方结构化 API 与权威回查路径。
- 引用验证统一收口，满足可解释与审计要求。

2. 最符合 10 分钟目标下的工程现实：
- 避免引入队列/离线复杂度（相比 C）。
- 避免 Scholar 官方 API 不确定性造成的波动（相比 1）。

3. 最易处理部分失败降级：
- 主证据失败 -> 明确降级 `Need More Data`。
- 补充层失败 -> 不阻塞主结论，但显式标注覆盖不足。

Evidence:
- prd-v0.1.md:521-522
- prd-v0.1.md:551
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:10-12
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:478

---

## 六、拒绝其余方案的关键证据

## 拒绝 A（内联验证）

- 核心问题：验证语义分散，审计与错误分类易漂移，不利于“关键结论必有来源”的一致兑现。
- 证据：研究已建议独立 deterministic gateway 收敛验证语义。

Evidence:
- prd-v0.1.md:510
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:478

## 拒绝 C（异步/离线）

- 核心问题：MVP 阶段对系统复杂度和验收流程负担过高，不利于 1~2 周演示闭环。

Evidence:
- prd-v0.1.md:551
- prd-v0.1.md:555

## 拒绝来源组合 1（PRD 字面 Scholar 直连思路）

- 核心问题：Scholar 无可确认官方公开 API，强依赖 web search/第三方，稳定性与可复现性弱。

Evidence:
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:10
- .copilot-tracking/research/subagents/2026-08-20/scholarly-discovery-alternatives-research.md:34-49

## 拒绝来源组合 3（仅双源）

- 核心问题：与 PRD 补充搜索层目标不一致，竞争与综述广度不足。

Evidence:
- prd-v0.1.md:171-173
- prd-v0.1.md:533

---

## 七、B+2 的具体落地设计

## 7.1 模块边界

1. Query Planner
- 输入：target、indication、time window、focus
- 输出：各 source 的检索计划（含 topK）

2. Source Adapters
- `PubMedAdapter`：ESearch + EFetch/ESummary
- `CTGovAdapter`：`/studies` 查询候选
- `EuropePMCAdapter`：生物医学补充
- `OpenAlexAdapter`（optional）：跨学科/引用网络补充

3. Citation Verification Gateway（deterministic）
- 输入：候选引用 ID + source type
- 输出：标准化验证状态 + 审计证据
- 禁止 LLM 参与该模块判定

4. Evidence Assembler
- 只接收验证后证据并进行冲突处理、去重、排序

5. Synthesis Engine (LLM)
- 仅对“验证后证据集”做总结与建议生成

## 7.2 最小数据模型（MVP）

```json
{
  "query": {
    "target": "string",
    "indication": "string|null",
    "timeWindow": "string|null",
    "topKMode": "TOP5|TOP20"
  },
  "evidence": [
    {
      "source": "PUBMED|CTGOV|EUROPE_PMC|OPENALEX|WEB_SUPPLEMENT",
      "sourceTier": "PRIMARY|SUPPLEMENT",
      "canonicalId": "string",
      "title": "string|null",
      "url": "string|null",
      "structured": {},
      "verification": {
        "status": "EXISTS|INVALID_FORMAT|NOT_FOUND|TRANSIENT_TIMEOUT|TRANSIENT_RATE_LIMIT|UPSTREAM_ERROR|UNVERIFIED_SUPPLEMENT",
        "method": "esummary|ctgov_study_by_id|none",
        "checkedAt": "ISO-8601"
      }
    }
  ],
  "decision": {
    "label": "GO|NO_GO|NEED_MORE_DATA",
    "rationale": ["string"],
    "uncertainty": ["string"]
  }
}
```

## 7.3 同步/批量切换策略（解决 Top5 vs Top10-20 冲突）

- `TOP5_SYNC`（默认）：
  - 用于满足 10 分钟目标。
  - 单次同步回查并出报告。
- `TOP20_BOUNDED_BATCH`（可选开关）：
  - 仍在同进程中做有界并发批处理，不引入独立队列服务。
  - 超时预算耗尽则回退到 Top5 已验证结果并标注 coverage。

Evidence:
- prd-v0.1.md:217
- prd-v0.1.md:515
- prd-v0.1.md:551

## 7.4 Source-of-Truth 规则

1. PMID existence truth：NCBI ESummary
2. NCT existence truth：CTGov `/studies/{nctId}`
3. 补充源（Europe PMC/OpenAlex/Web）只可“增加线索”，不可覆盖主证据结构化事实。
4. `query.id` 仅用于发现，不可用于 NCT existence 判定。

Evidence:
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:425
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:449
- .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md:116-121

## 7.5 失败降级规则

1. 主证据源之一完全失败：
- 输出 `Need More Data`，并列出失败源与原因。

2. 补充源失败（Europe PMC/OpenAlex/Web）：
- 不阻塞主结论，标注“补充覆盖不足”。

3. 引用未通过验证：
- 不进入“关键结论证据集”；可放入“未验证线索”区。

4. 所有可用证据均未验证通过：
- 强制 `Need More Data`。

Evidence:
- prd-v0.1.md:510
- prd-v0.1.md:521-522
- prd-v0.1.md:554

## 7.6 实施顺序（可执行）

1. 定义统一 evidence 与 verification schema。
2. 实现 PubMed + CTGov adapters（仅 discovery）。
3. 实现 Citation Verification Gateway（PMID/NCT 严格回查）。
4. 打通 Top5 同步闭环与部分失败降级。
5. 增加 Europe PMC adapter。
6. 增加 OpenAlex optional adapter。
7. 加入 Top20 bounded batch 开关与时限回退。
8. 增加端到端验收集。

---

## 八、可执行验收标准（MVP）

1. 时延：单次查询在 10 分钟内完成（Top5 默认）。
2. 引用：关键结论引用 100% 具备 `verification.status=EXISTS`。
3. 语义：`INVALID_FORMAT`、`NOT_FOUND`、`TRANSIENT_*` 可区分并可追溯。
4. 降级：任一补充源不可用时，系统仍返回主结论并显式 coverage 警告。
5. 主源故障：任一主证据源不可用时，结论降级为 `Need More Data`。
6. 冲突规则：补充源不得覆盖主证据结构化事实。
7. 可重复性：同一测试 fixture 下，Top5 报告字段与验证状态稳定重放。

Evidence:
- prd-v0.1.md:510
- prd-v0.1.md:521-522
- prd-v0.1.md:551-554
- .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md:332-334

---

## 九、第一阶段研究缺口与阻塞判断

## 非阻塞缺口（可带风险推进）

1. NCT alias 301 行为尚未实测。
- 影响：低到中（影响边界处理，不影响主流程）。

2. PMID 最大位数是当前项目策略，不是 NCBI 硬契约。
- 影响：中（需保持可配置）。

3. Top5 与 Top10-20 的产品口径未最终统一。
- 影响：中（影响默认策略，但不阻塞按 Top5 先落地）。

Evidence:
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:53
- .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:132
- prd-v0.1.md:217
- prd-v0.1.md:515

## 阻塞缺口（本轮结论）

- 无“必须阻塞开发”的缺口。
- 可以按 B+2 进入实现阶段，并将上述缺口纳入迭代验收清单。

---

## 十、澄清问题（建议但不阻塞）

1. PRD 文案层是否接受将“Scholar 必选”解释为“Scholar/Web 补充能力必选，但实现可由 Europe PMC + OpenAlex + web search adapter 组合满足”？
2. 默认演示口径是否确认为 `Top5`，并把 `Top20` 作为可选增强模式？
3. NCT alias 301 命中时，产品是否展示“别名归一化”提示？
4. 未验证补充证据是否允许在 UI 单独显示“线索区”（不进入关键结论）？

---

## 最终建议摘要

- 推荐组合：B + 2
- 核心理由：在当前证据下，这是唯一同时满足“可实现性、可审计性、10 分钟目标、部分失败降级、引用可验证”的低风险方案。
- 对 A/C 与来源 1/3 的拒绝已给出对应证据与工程风险。