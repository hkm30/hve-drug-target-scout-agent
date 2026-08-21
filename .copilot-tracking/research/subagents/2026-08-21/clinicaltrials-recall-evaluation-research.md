<!-- markdownlint-disable-file -->
# Drug Target Scout 临床试验靶点检索召回率评测与范围判定研究

研究基线日期：2026-08-21。

## 研究问题

1. 在没有完整全球 ground truth 时，怎样构建 30 至 50 条金样本并避免只用同一映射源自证？
2. 如何区分 retrieval yield、proxy recall、true recall、precision@K、coverage 和 mechanism relevance？
3. 对 Go/No-Go 决策支持，漏掉 active、late-phase、terminated trials 的风险权重如何建模？
4. 什么阈值可作为 1 至 2 周 DEMO 的可接受门槛，并明确阈值是项目建议而非行业标准？
5. 如何做 source ablation，量化 direct target、manual seed、Open Targets、ChEMBL 和多源 union 的边际召回与精度代价？
6. 建议采用什么失败与降级语义？

## 研究范围与证据原则

本研究评估的对象不是 ClinicalTrials.gov API 的可用性，而是 Drug Target Scout 对“目标靶点 + 适应症”相关试验的候选召回、机制判定和排序质量。评测单位是 `(target, indication, NCT ID)` 三元组。相同 NCT 在不同靶点或适应症下可以有不同相关性标签。

ClinicalTrials.gov API v2 的 OpenAPI 契约只提供 intervention、condition、keywords、description、phase、overall status、`whyStopped` 等字段，没有独立的分子靶点本体字段。因此：

* ClinicalTrials.gov 负责返回和验证试验登记事实，包括 NCT、适应症、干预、阶段和状态
* direct target、manual seed、Open Targets 和 ChEMBL 负责生成不同的查询词或干预候选
* 人工机制判定负责确认“该干预是否在该适应症中直接作用于目标靶点”
* 来源命中数、靶点字符串命中和 target-to-drug 映射都不能单独充当 relevance ground truth

证据分为三层：

| 证据等级 | 用途 | 可以证明 | 不能证明 |
|---|---|---|---|
| 官方契约或权威登记 | ClinicalTrials.gov OpenAPI、单条 NCT 记录 | 记录存在、阶段、状态、适应症、登记干预、`whyStopped` 原文 | 干预必然直接作用于目标，终止必然代表机制失败 |
| 一手或领域权威资料 | 原始药理研究、监管标签、同行评议综述、官方数据库文档 | 干预身份、作用机制、靶点方向和来源边界 | 全球所有相关试验已经枚举完整 |
| 项目判定 | 双人标注、代理金集、风险权重、门槛 | 在冻结范围内比较策略，决定 DEMO 是否可演示 | 行业标准、生产级安全性或全球 true recall |

以下所有数值门槛均为 **Drug Target Scout 1 至 2 周 DEMO 的项目建议，不是信息检索、临床开发或监管行业标准**。门槛用于阻止低覆盖结果被包装成 Go/No-Go 结论，不用于证明系统具有临床决策资格。

### 可接受的产品声明

通过本文门禁后，DEMO 可以声明：

> 在冻结的 ClinicalTrials.gov 数据时间、映射来源版本、目标和适应症测试范围内，系统能够以可审计方式召回并排序大部分已知的直接机制相关试验，关键展示记录均经过 NCT 回查。

DEMO 不得声明：

* 已穷尽全球所有相关临床试验
* 零结果证明不存在相关试验
* terminated 自动证明靶点或药物机制失败
* Open Targets 与 ChEMBL 的一致命中构成两个完全独立证据
* 代理召回率等同于 true recall

## 指标定义

先固定符号：

* `q` 是一个 target-indication 查询场景
* `C(q, s, L)` 是来源策略 `s` 经 NCT 去重、统一过滤和统一排序后的前 `L` 个候选
* `G+(q)` 是代理金集中经人工判为直接机制相关的已知正例
* `J(q, K)` 是已经完成相关性判定的前 `K` 个结果
* `rel(i)` 是试验 `i` 的机制相关性等级

### Retrieval yield

`retrieval yield` 是候选产出量，不是召回率：

`yield(q, s) = |C(q, s, L)|`

必须同时报告去重前命中数、去重后 NCT 数、各来源独有 NCT 数和实际审核数。更大的 yield 可能只表示更多噪声、同义词扩张或分页差异。

### Proxy recall

在完整 ground truth 不可得时，使用已知正例集合计算代理召回，也可称 relative recall：

`proxy_recall@L = |C(q, s, L) ∩ G+(q)| / |G+(q)|`

分母只能包含已人工确认的正例。该值说明系统找回了多少“已知相关试验”，不能证明未知相关试验不存在。报告时必须写成 `proxy recall` 或 `relative recall`，不能简写成未经限定的 `recall`。

### True recall

`true_recall = |C ∩ R_all| / |R_all|`

只有在冻结范围内已经穷举并判定全部相关试验 `R_all` 时才能计算。Drug Target Scout DEMO 没有完整全球 ground truth，因此不报告 true recall。即使采用 condition-only broad search 或多源 union，它们也只是更宽的候选池，不自动成为 `R_all`。

### Precision@K

`precision@K = relevant_count(J(q, K)) / K`

必须对每个 Top K 结果完成判定，不能默认未判定项不相关。建议同时报告：

* `strict P@K`：仅 `R2` 直接机制相关算正例
* `broad P@K`：`R2` 和 `R1` 均算正例
* `unjudged@K`：Top K 中尚未判定的比例，验收时必须为 0

### Coverage

`coverage` 必须带限定词，避免与 recall 混用：

| 名称 | 定义 | 用途 |
|---|---|---|
| scenario coverage | 有至少一个 `R2` 被召回的 gold-positive 场景数 / gold-positive 场景总数 | 防止总体平均掩盖某个靶点完全失效 |
| critical-stratum coverage | 被召回的 critical gold positives / critical gold positives 总数 | 观察 active、late-phase、terminated 等高风险漏项 |
| source execution coverage | 成功完成且无分页截断的计划来源数 / 计划来源总数 | 区分质量问题和来源故障 |
| field coverage | 展示记录中完成 NCT、condition、intervention、status、phase-nullability、provenance 解析的比例 | 验证结构化输出完整性 |

### Mechanism relevance

机制相关性是人工判定维度，不是 API 字段。建议使用四级标签：

| 标签 | 判定 | 进入指标 |
|---|---|---|
| `R2_DIRECT` | 干预直接调节目标靶点，方向可确认，适应症符合范围 | strict precision、proxy recall、风险加权 recall |
| `R1_CONTEXTUAL` | 组合疗法中含目标相关成分、通路下游/上游关联、biomarker-selected 或近邻机制，但不能证明该试验直接检验目标 | broad precision、graded ranking |
| `R0_IRRELEVANT` | 仅文本提及、同名歧义、适应症不符、干预并不作用于目标 | 负例 |
| `U_UNJUDGED` | 证据不足或冲突未解决 | 不得当成负例；不得进入最终关键证据 |

排序质量使用 `nDCG@10`，建议 gain 设为 `R2=3, R1=1, R0=0`。同时保留 strict P@5/P@10，使一个高 nDCG 不能掩盖大量间接机制候选。

### 不完整判断集的处理

TREC 的 pooling/qrels 实践和 Buckley、Voorhees 对 incomplete judgments 的研究表明，未判定文档不能简单等价为不相关。DEMO 采用以下规则：

* Top 10 必须全判，确保 P@5/P@10 可直接解释
* 代理金集正例必须逐条检查是否被各策略召回
* Top 10 之外保留 `U_UNJUDGED`，不纳入精度分母
* 如候选池仍有大量未判定项，可附加 `bpref` 作为诊断指标，但不把它作为主要产品门禁
* 报告分子和分母原始计数，并给出 Wilson 95% 区间；DEMO 门槛按点估计判定，区间仅显示小样本不确定性

## 金样本设计

### 样本结构

建议建立 **40 条主判定记录**，允许范围 30 至 50 条：

* 8 个 target-indication 场景，每个场景 4 个经确认的 `R2_DIRECT` 正例，共 32 条
* 8 个 hard negatives 或 borderline records，用于覆盖 `R1_CONTEXTUAL`、`R0_IRRELEVANT` 和名称歧义
* 如果某个场景找不到 4 个 `R2`，保留真实低基数并补充其他场景，不用低相关记录填满正例配额

建议至少覆盖以下维度，具体靶点由领域专家在开工日确认：

| 维度 | 最低覆盖 | 可选例子，仅用于选型 |
|---|---|---|
| PRD 主场景 | 3 个场景 | GLP1R + 肥胖/T2D、TNFSF15/TL1A + IBD、PCSK9 + 高胆固醇血症 |
| 小分子与突变特异靶点 | 至少 1 个 | EGFR 或 KRAS G12C |
| 抗体或配体/受体命名歧义 | 至少 1 个 | TNFSF15/TL1A、IL23A/IL23R |
| RNA 或其他非传统 modality | 至少 1 个 | PCSK9 siRNA 或经专家确认的等价场景 |
| 失败密集靶点 | 至少 1 个 | BACE1、CETP 或经专家确认的等价场景 |
| 多靶点/组合 hard case | 至少 1 个 | 组合疗法、双特异性或共享通路干预 |

状态和阶段可重叠计数，但主判定集中建议至少包含：

* 8 条 active records，状态来自 `RECRUITING`、`NOT_YET_RECRUITING`、`ENROLLING_BY_INVITATION` 或 `ACTIVE_NOT_RECRUITING`
* 8 条 late-phase records，最高阶段为 Phase 3 或 Phase 4
* 8 条 terminated/suspended/withdrawn records，其中至少 4 条为 Phase 2 或更高
* 6 条 early-phase records
* 8 条 mechanism hard cases，包括组合疗法、target mention only、biomarker-only 或同名歧义

这些配额用于风险覆盖，不代表临床试验总体分布。

### 五路候选发现

候选发现采用 pooling，但每一路都只能“提名”，不能单独给自己贴正例标签：

1. Direct target：HGNC 规范符号、常见别名、蛋白/配体名称在 ClinicalTrials.gov intervention/basic search 中的候选
2. Manual seed：由领域专家从监管标签、原始药理研究、试验论文和高质量综述整理的干预别名
3. Open Targets：固定 release 的 target-known-drug 或等价导出
4. ChEMBL：固定 release 的 mechanism-of-action 与 target-molecule 记录
5. Broad residual：按适应症、sponsor、已知药物类别和 condition-only 检索后离线筛选的候选，用于发现四路策略共同漏掉的记录

合并后按 NCT ID 去重，隐藏“由哪个来源提名”的信息，再交给标注者。这样可以降低来源声誉对 relevance 标签的影响。

### 防止单源自证

每条 `R2_DIRECT` 必须满足三个独立判定面：

| 判定面 | 最低证据 | 规则 |
|---|---|---|
| Trial identity | ClinicalTrials.gov 单条 `/studies/{nctId}` 精确回显 | 确认 NCT、intervention、condition、phase、status |
| Mechanism identity | 至少一项不依赖候选提名源的证据 | 原始药理研究、监管标签、同行评议药物机制资料；不能只引用提名它的 Open Targets/ChEMBL 条目 |
| Scope fit | 两名标注者依据冻结 inclusion/exclusion rubric 判定 | 确认目标方向、适应症和干预在试验中的实际角色 |

Open Targets 的 known-drug 数据可能整合 ChEMBL 等来源。因此，Open Targets 与 ChEMBL 同时命中只算“映射来源一致”，不能自动算两个独立机制证据。每个 release 必须保存 provenance；如果无法确认来源独立性，按相关来源处理。

### 标注流程

1. 在标注前冻结 inclusion/exclusion rubric 和 target/indication scope
2. 对候选来源、策略排名和系统输出盲化
3. 两名标注者独立判定 `R2/R1/R0/U`、作用方向、适应症匹配和终止原因类别
4. 分歧由共识会议或第三名领域专家裁决
5. 记录原始标签、裁决标签、证据 URL、证据日期和说明，不覆盖历史标签
6. 报告 raw agreement 和 Cohen's kappa；建议 `kappa >= 0.70` 才进入验收，否则先修订 rubric。该值是项目建议，不是通用行业门槛

### 开发集和盲测集

按 target-indication 场景分组切分，不按 NCT 随机切分：

* 5 个场景作为 development set，用于同义词、排序和阈值调试
* 3 个场景作为 holdout set，直到检索策略冻结后才揭示标签
* 同一靶点的相邻适应症尽量放在同一侧，避免干预词泄漏
* 所有正式门槛以 holdout 为主，同时报告 full-set 结果

### 残余漏项审计

代理金集完成后，再从 broad residual 中分层随机抽取 20 条未进入主判定集的候选，覆盖 active、late phase 和 terminated strata：

* 如果发现任何 critical `R2`，立即扩展金集并重新评测
* 如果 20 条中发现 2 条或更多普通 `R2`，判定代理金集仍过窄，不能发布 recall 门槛结论
* 如果未发现上述问题，只能表述“残余抽样未发现明显系统性漏项”，不能表述 true recall 已知

该残余审计是低成本偏差检查，不是统计意义上的穷举证明。capture-recapture 可以作为探索性估计，但来源相关性、异质检出概率和小样本会使估计不稳定，不作为 DEMO 验收门禁。

## 风险加权模型

普通 proxy recall 将每个已知正例视为同等重要，不能反映 Go/No-Go 中的非对称风险。DEMO 使用透明的 **ordinal miss-loss weight**，不把权重解释为失败概率、临床价值或监管结论。

### 单条试验权重

仅对 `R2_DIRECT` 且适应症符合范围的 gold positives 赋权。每条试验按以下互斥行取得基础权重：

| 试验类别 | 建议权重 | 漏召回的主要决策风险 |
|---|---:|---|
| Active Phase 3/4 | 5 | 低估成熟竞争、差异化门槛和上市接近度，可能形成错误 Go |
| Terminated/Suspended Phase 2+，`whyStopped` 指向 efficacy、safety 或 futility | 5 | 漏掉强负面信号，最容易形成错误 Go |
| Completed Phase 3/4 且有 results | 5 | 漏掉成熟正面或负面结果，扭曲临床可行性判断 |
| Active Phase 2 | 4 | 低估正在形成的竞争与验证信号 |
| Terminated/Suspended Phase 2+，原因未知或无法分类 | 4 | 重要失败线索缺失，但不能假设为机制失败 |
| Terminated/Suspended Phase 1 | 3 | 可能包含安全性或开发性风险，证据成熟度较低 |
| Active Early Phase/Phase 1 | 2 | 竞争与早期验证线索，短期决策影响较低 |
| Withdrawn before enrollment 或明确行政/商业原因 | 2 | 影响竞争格局，但不能视为生物学失败 |
| 其他相关记录 | 1 | 一般信息损失 |

`whyStopped` 为空时必须使用“未知原因”行。`TERMINATED`、`SUSPENDED` 或 `WITHDRAWN` 本身不能自动标记为 efficacy/safety failure。

### 风险加权代理召回

`weighted_proxy_recall = sum(weight_i for retrieved gold positives) / sum(weight_i for all gold positives)`

同时报告：

* overall proxy recall
* weighted proxy recall
* 每个风险 strata 的 numerator/denominator
* critical miss count 与具体 NCT

critical gold positive 定义为以下任一情况：

* Phase 3/4
* Active 且 Phase 2+
* Terminated/Suspended 且 Phase 2+
* 领域专家在盲测前标记为会实质改变 Go/No-Go 的记录

平均分不能抵消 critical miss。即使 weighted proxy recall 达标，只要 holdout 中漏掉一个 critical record，决策支持门禁仍失败。

## Source Ablation 设计

### 固定条件

消融实验必须冻结以下变量，避免把查询或排序变化错误归因于来源：

* ClinicalTrials.gov `dataTimestamp` 和查询 UTC 时间
* Open Targets、ChEMBL 的 release/version、下载日期和许可证说明
* HGNC target normalization、适应症词表、状态/阶段过滤、时间范围
* 干预名称归一化规则、盐型和开发代号 alias 规则
* 每个来源的最大 mapping 数、ClinicalTrials.gov 分页上限和最终候选上限 `L=50`
* 同一个排序器与去重器；排序器只在 development set 调整

### 策略矩阵

| 代号 | Query expansion | 目的 |
|---|---|---|
| `D` | canonical target + target synonyms | direct baseline |
| `M` | manual seeds only | 人工领域先验上界和维护成本基线 |
| `O` | Open Targets mappings only | 自动映射来源之一 |
| `C` | ChEMBL mechanisms only | 自动机制来源之一 |
| `D+M` | direct + manual | 最小可用 DEMO 候选 |
| `D+O` | direct + Open Targets | 自动扩展增益 |
| `D+C` | direct + ChEMBL | 自动机制增益 |
| `D+M+O+C` | 多源 union | 候选召回上界与精度代价 |
| `ALL-source` | union 去掉单一来源 | leave-one-out，衡量来源不可替代性 |

还应报告 `O ∩ C`、`O - C` 和 `C - O` 的 intervention 与 NCT 重叠。由于 Open Targets 和 ChEMBL 可能有数据血缘重叠，不能把来源数量直接当作 evidence strength。

### 每个来源的边际指标

对来源 `s` 和当前基线 `B` 计算：

* `delta_proxy_recall = proxy_recall(B ∪ s) - proxy_recall(B)`
* `delta_weighted_recall = weighted_recall(B ∪ s) - weighted_recall(B)`
* `delta_P@5` 和 `delta_P@10`，使用相同排序器
* `unique_positive_gain = |G+ ∩ (C_s - C_B)|`
* `critical_recovered = critical positives in (C_s - C_B)`
* `unique_candidate_cost = |C_s - C_B|`
* `NNR_incremental = unique_candidate_cost / unique_positive_gain`，若分母为 0 则记为 infinity
* `latency_delta`、mapping 条目数和失败率，作为工程代价

同时做累计添加和 leave-one-out。仅做固定顺序的累计添加会产生顺序偏差；leave-one-out 可以回答“完整 union 缺少该来源后损失多少”。

### DEMO 来源保留规则

建议保留一个自动映射源的条件是满足任一召回收益，并且排序后精度仍达门禁：

* 找回至少 1 个其他策略漏掉的 critical positive
* 找回至少 2 个 unique `R2` positives
* weighted proxy recall 增加至少 0.05

如果一个来源没有 unique positives、`NNR_incremental > 20` 且增加明显运行复杂度，可从 1 至 2 周 DEMO 移除。`20`、`2` 和 `0.05` 都是项目建议。即使来源保留，最终 P@5/P@10 和 critical miss 硬门禁仍必须满足。

### 可复现输出表

本文完成实验设计，未运行待实现系统。实施阶段每个策略至少输出：

| Strategy | Yield | Unique NCT | Gold R2 hit/total | Proxy recall@50 | Weighted recall@50 | Strict P@5 | Strict P@10 | nDCG@10 | Critical misses | Incremental NNR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `D` | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | n/a |
| `D+M` | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 |
| `D+O` | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 |
| `D+C` | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 |
| `D+M+O+C` | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 | 未实测 |

## DEMO 验收矩阵

### 候选池与展示层分离

PRD 的 Top 5 展示不能同时充当召回候选上限。建议：

* 每个场景、每个策略完整分页后形成去重候选，统一排序并截取 `L=50` 用于 proxy recall
* UI 默认展示 Top 5，离线评测完整判定 Top 10 用于 precision 和 mechanism ranking
* 如果查询结果被上游分页、时间预算或客户端上限截断，标记 `QUERY_TRUNCATED`，该次运行不得声称 coverage 或 recall

### 建议门槛

| 类别 | 指标 | 1 至 2 周 DEMO 建议门槛 | 不通过时的产品判定 |
|---|---|---:|---|
| Gold set | 主判定记录数 | 30 至 50，建议 40 | 阻止正式召回声明 |
| Gold set | 已确认 `R2` positives | 至少 24，建议 32 | 阻止正式召回声明 |
| Independence | `R2` 是否有 trial identity + 独立 mechanism evidence + 双人 scope 判定 | 100% | 标签降为 `U` 或移出 gold positive |
| Adjudication | Top 10 与 gold positives 已判定 | 100% | 指标无效 |
| Agreement | Cohen's kappa | >= 0.70 | 修订 rubric 后重标；项目建议 |
| Candidate recall | holdout overall proxy recall@50 | >= 0.85 | 限定为 discovery prototype，不提供 Go/No-Go |
| Risk recall | holdout weighted proxy recall@50 | >= 0.90 | 强制 `NEED_MORE_DATA` |
| Critical safety | holdout critical miss count | 0 | 硬失败，阻止 Go/No-Go |
| Scenario coverage | gold-positive holdout 场景至少返回一个 `R2` | 100% | 硬失败，说明目标族覆盖不稳定 |
| Top display | holdout strict P@5 | >= 0.80 | 不适合直接向用户展示 Top 5 |
| Review list | holdout strict P@10 | >= 0.70 | 排序/机制过滤需返工 |
| Broad relevance | holdout broad P@10 | >= 0.80 | 噪声过高 |
| Ranking | holdout mechanism nDCG@10 | >= 0.80 | 不能声称高相关优先 |
| Identity | 展示 NCT 的权威端点 exact-ID 回查 | 100% | 未验证记录不得展示为关键证据 |
| Field coverage | NCT、condition、intervention、status、phase-nullability、provenance | 100% | 降级并显示字段缺口 |
| Residual audit | 20 条中 critical `R2` 数；普通 `R2` 数 | 0；最多 1 | 扩展 gold set，重新评测 |
| Failure contract | 主源、映射源、分页、零结果、冲突 fixture | 100% 通过 | 不允许演示决策流程 |

这些点估计在 30 至 50 条样本上会有宽置信区间。它们适合 DEMO 的 go/no-go engineering gate，不足以支持跨靶点总体性能声明。正式生产评估应扩大 target-level holdout、重复时间快照并预注册阈值。

### 产品范围判定

| 评测结果 | 允许范围 | 禁止范围 |
|---|---|---|
| 全部门槛通过 | 在已测试目标族上提供带证据的 `Go / No-Go / Need More Data` 辅助建议，并显示 coverage 限定 | 不得声称全球穷尽或替代研发委员会 |
| recall/precision 达标但 critical miss > 0 | 只提供候选发现、人工复核清单 | 不得输出 Go/No-Go |
| direct-only 达标，映射来源不可用 | 可以演示直接词发现 | 不得称为完整 target clinical landscape |
| 来源运行部分失败或查询截断 | 返回已验证部分结果和失败状态 | 不得把零命中或部分结果用于 No-Go |
| 金集或独立判定不足 | 演示 API 链路和 UI | 不得展示性能百分比或决策质量结论 |

## 失败与降级语义

运行状态和业务决策必须分离。`FAILED`、`DEGRADED` 或 `NEED_MORE_DATA` 不是 target 的 `No-Go`。

### Run-level 状态

| 状态 | 含义 | 是否允许 Go/No-Go |
|---|---|---|
| `COMPLETE` | 所有必需来源成功，分页完整，NCT 验证和评测门禁通过 | 允许辅助建议 |
| `DEGRADED_OPTIONAL_SOURCE` | 可选映射源失败，但预先验证的剩余策略仍满足门槛 | 可允许，但必须显示缺失来源和较窄 coverage |
| `DISCOVERY_ONLY` | direct-only、机制映射不足或 precision/recall 门禁失败 | 不允许 |
| `NEED_MORE_DATA` | 主源不可用、关键字段/机制冲突、查询截断或 critical miss | 不允许，只能返回待补证据 |
| `FAILED` | 输入无效、schema drift、数据损坏或无法形成可验证候选 | 不允许 |

### 失败矩阵

| 条件 | 机器状态 | 用户可见语义 | 决策动作 |
|---|---|---|---|
| Target 名称无法规范化 | `TARGET_INVALID` | 无法识别靶点，请确认 HGNC symbol/别名 | 停止检索 |
| Target 指向多个实体 | `TARGET_AMBIGUOUS` | 列出候选实体并请求人工确认 | 停止检索 |
| ClinicalTrials.gov timeout/429/5xx | `PRIMARY_SOURCE_UNAVAILABLE` | 主临床登记源暂不可用，结果不完整 | `NEED_MORE_DATA`，不得 No-Go |
| ClinicalTrials.gov schema/path 变化 | `SCHEMA_DRIFT` | 结构化字段无法可靠解析 | `FAILED`，报警并阻止输出 |
| page token 丢失、页数上限或时间预算截断 | `QUERY_TRUNCATED` | 仅返回部分候选，不能计算 coverage | `NEED_MORE_DATA` |
| 单个 Open Targets/ChEMBL 来源失败 | `PARTIAL_MAPPING_COVERAGE` | 指明缺失来源、版本和预期影响 | 仅在剩余策略离线门禁通过时允许 degraded 建议 |
| 所有映射来源失败，但 direct query 成功 | `DIRECT_ONLY_DISCOVERY` | 只覆盖登记文本直接出现靶点词的试验 | `DISCOVERY_ONLY` |
| 映射返回空集合 | `MAPPING_EMPTY` | 区分“确认无映射”与“源调用失败/解析失败” | 默认 `NEED_MORE_DATA`，不得推断无试验 |
| Open Targets 与 ChEMBL 机制冲突 | `MECHANISM_CONFLICT` | 显示冲突来源，要求人工裁决 | 冲突项为 `U_UNJUDGED`，不进关键证据 |
| NCT 单条回查不匹配或不存在 | `NCT_VERIFICATION_FAILED` | 记录被排除并留下审计原因 | 不引用该记录 |
| NCT 存在但机制证据不足 | `MECHANISM_UNCONFIRMED` | 保留为候选，不作为直接机制证据 | 降为 `U` 或 `R1` |
| `TERMINATED` 但 `whyStopped` 为空/模糊 | `TERMINATION_REASON_UNKNOWN` | 可报告已终止，不得写成疗效或安全失败 | 人工复核，降低结论确定性 |
| 全部必需来源成功且确实无 `R2` | `VALID_EMPTY_WITHIN_SCOPE` | 在指定来源、时间和查询范围内未找到已确认直接相关试验 | 默认 `NEED_MORE_DATA`，不能表述“全球不存在” |
| 离线门禁不通过 | `EVAL_GATE_FAILED` | 当前版本只支持候选发现，不能支持决策 | `DISCOVERY_ONLY` |

### 最低审计字段

每次运行保存：

* target canonical ID、输入别名、适应症范围、查询时间窗
* ClinicalTrials.gov API version、`dataTimestamp`、完整查询、分页是否完成
* 每个 mapping source 的 release/version、请求或本地快照哈希
* source execution state、候选数、去重数、截断原因
* 每条 NCT 的发现来源、排序分、机制标签、标注证据和 exact-ID verification
* run-level state、是否允许决策、降级原因和用户可见措辞

## 证据与参考资料

### 信息检索与不完整 ground truth

* Buckley C, Voorhees EM. [Retrieval evaluation with incomplete information](https://doi.org/10.1145/1008992.1009000). SIGIR 2004. 该工作提出并验证 bpref，核心用途是降低不完整 relevance judgments 对评测的影响。本文据此保留未判定状态，但不把 bpref 作为主要产品门禁。
* Sampson M, et al. [An alternative to the hand searching gold standard: validating methodological search filters using relative recall](https://doi.org/10.1186/1471-2288-6-33). BMC Medical Research Methodology. 2006;6:33. PMID 16836754. 该工作支持在不可得绝对金标准时，用多个既有发现渠道形成 reference set 并报告 relative recall。
* NIST. [TREC 2021 Clinical Trials Track data](https://trec.nist.gov/data/clinical2021.html). TREC clinical-trial retrieval 使用 topics、pooling 和 qrels，说明临床试验检索应分开评价检索、人工 relevance judgment 和排名，而不是用返回数量代替质量。
* Cochrane. [Cochrane Handbook, Chapter 4: Searching for and selecting studies](https://training.cochrane.org/handbook/current/chapter-04). 该权威指南支持多渠道检索和试验注册库检索，说明单一数据库或单一检索式不应被假定为完整 ground truth。

### ClinicalTrials.gov 字段与失败语义

* ClinicalTrials.gov. [REST API v2 OpenAPI specification](https://clinicaltrials.gov/api/oas/v2). 2026-08-21 本地快照显示 API version `2.0.5`，`query.intr` 是 intervention/treatment query，phase 与 status 来自结构化枚举，`whyStopped` 是可选字符串；公开 schema 未提供独立分子靶点字段。
* ClinicalTrials.gov. [Constructing complex search queries](https://clinicaltrials.gov/find-studies/constructing-complex-search-queries). `query.*` 与 `AREA[...]` 仍是登记字段/文本检索语义，不是 target ontology lookup。
* 既有本地研究证据：`.copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md`、`.copilot-tracking/research/subagents/2026-08-20/clinicaltrials-api-research.md`。二者已核验 NCT exact-ID 回查、phase/status 字段路径和无独立靶点字段边界。

### 映射来源

* Open Targets Platform. [Platform documentation](https://platform-docs.opentargets.org/). Open Targets 可用于 target-drug 候选发现，但需要固定 release、保存 provenance，并按当前 release 核对 underlying source。
* Ochoa D, et al. [The next-generation Open Targets Platform: reimagined, redesigned, rebuilt](https://doi.org/10.1093/nar/gkac1046). Nucleic Acids Research. 2023;51(D1):D1353-D1359. 该资料说明 Open Targets 是多来源整合平台，因此不能默认其与底层数据库完全独立。
* ChEMBL. [ChEMBL Data Web Services](https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services). mechanism 等资源可用于 molecule-target-mechanism 候选映射，但记录仍需版本固定、target identity 和 action type 过滤。
* Zdrazil B, et al. [The ChEMBL Database in 2023: a drug discovery platform spanning multiple bioactivity data types and time periods](https://doi.org/10.1093/nar/gkad1004). Nucleic Acids Research. 2024;52(D1):D1180-D1192. 该资料界定 ChEMBL 是药物发现与 bioactivity 数据平台，不是 ClinicalTrials.gov 完整试验 relevance ground truth。

### 证据适用边界

外部资料支持的是方法和来源边界，不支持本文的具体数字门槛。`0.85`、`0.90`、`P@5=0.80`、`critical miss=0`、40 条样本、风险权重 1 至 5 和来源保留规则均为本项目基于错误 Go 风险、两周工期和人工审核预算提出的建议。

## 局限与待确认问题

* 30 至 50 条记录只能发现明显回归和来源增益，不能稳定估计跨疾病、跨 modality 的总体性能；置信区间会较宽
* 代理金集由多源 pooling 构建，仍可能漏掉所有来源都未发现的试验；残余抽样只能降低风险，不能证明完整
* Open Targets 与 ChEMBL 的数据血缘随 release 变化，正式消融前必须检查当期 provenance，不能永久假设独立或完全重叠
* ClinicalTrials.gov 是动态登记库。评测必须冻结 `dataTimestamp`，否则新增/更新记录会让集合差异无法归因
* `whyStopped` 是登记方文本且可能缺失。终止原因分类需要人工复核，不能由状态枚举自动推断
* precision@K 依赖 Top K 全判；未判定项较多时，不能把它们默认为不相关
* 本研究没有实际执行 40 条标注和 source ablation，因此阈值是预注册建议，不是当前系统实测结果
* 需要领域专家确认 8 个 target-indication 场景、direct mechanism inclusion rubric 和“会改变 Go/No-Go”的 critical 清单

## 执行顺序

1. 在半天内冻结 8 个场景、标签 rubric、风险权重和查询/来源版本
2. 用五路候选发现建立 pooled candidate sheet，按来源盲化
3. 两名标注者完成约 40 条主记录和 20 条 residual audit，先裁决 gold set
4. 冻结 query builder、intervention normalization、ranker 和 `L=50/K=10`
5. 运行 `D/M/O/C/union/leave-one-out`，输出原始集合、重叠矩阵和验收表
6. 只在 holdout 全部门槛通过后启用 Go/No-Go；否则把 DEMO 范围明确收窄为 candidate discovery

## 结论

在没有完整全球 ground truth 时，严格且适合 DEMO 的方案不是声称 true recall，而是构建跨来源、双人判定、target-level holdout 的 30 至 50 条代理金集，报告 proxy recall、风险加权 recall、Top-K precision、graded mechanism relevance 和带限定词的 coverage。多源 union 的价值必须通过 unique positives、critical recovery 和 incremental review cost 证明，不能用命中数量或“两个映射库都说有”自证。

对 Drug Target Scout，建议将 `proxy recall@50 >= 0.85`、`weighted proxy recall@50 >= 0.90`、`critical miss=0`、`strict P@5 >= 0.80`、`strict P@10 >= 0.70`、`mechanism nDCG@10 >= 0.80`、展示 NCT 100% 回查作为两周 DEMO 门禁。任何主源失败、查询截断、critical miss 或 gold-set 独立性不足都必须阻止 Go/No-Go，并降级为 `NEED_MORE_DATA` 或 `DISCOVERY_ONLY`。