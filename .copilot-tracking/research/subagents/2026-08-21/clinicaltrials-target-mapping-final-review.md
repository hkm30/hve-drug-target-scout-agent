<!-- markdownlint-disable-file -->

# ClinicalTrials.gov Target Mapping Final Independent Review

## Review Status

Status: Complete

Verdict: **NEEDS REVISION**

* Must-fix findings: 2 Major
* Suggested findings: 1 Minor
* Passed checks: A, C, D, G
* Files modified by this review: only this review file

The central research direction is sound. Direct target-text retrieval is demonstrably incomplete, target-to-intervention relations are not sufficient for trial relevance, A/B counts are correctly treated as retrieval yield, and the PRD coverage classification is accurate. Two statements still exceed the evidence: the document presents pre-query external mapping as an engineering necessity across architectures, and it labels an implementation plus a full dual-review evaluation program as a one-to-two-week minimum DEMO despite starting from a documentation-only workspace.

## Severity Scale

| Severity | Meaning | Required action |
|---|---|---|
| Major | A central conclusion or committed delivery scope is not supported at the stated strength | Must be corrected before planning |
| Minor | The core decision remains valid, but the consolidated document is incomplete or could mislead a reader | Recommended correction |
| PASS | The checked claim is supported and correctly bounded | No correction required |

## Finding Register

| ID | Check | Severity | Disposition |
|---|---|---|---|
| R1 | B. Necessary-but-insufficient logic | Major | Must fix |
| R2 | F. One-to-two-week DEMO feasibility | Major | Must fix |
| R3 | E. Six-source capability and licensing consolidation | Minor | Suggested |
| P1 | A. Coverage of the three user questions | PASS | No change |
| P2 | C. A/B counts and recall terminology | PASS | No change |
| P3 | D. PRD line references and coverage classification | PASS | No change |
| P4 | G. Task Researcher success criteria | PASS | No change |

## A. Coverage of the Three User Questions

Severity: **PASS**

Main-document sections and statements:

* `Task Implementation Requests`, lines 21-26, restates all three requested questions and adds a DEMO acceptance question.
* `Executive Decision`, line 8, answers whether mapping is required for the current product claim.
* `Technical Scenarios`, lines 215-403, evaluates seven paths and their candidate coverage, false-positive risk, cost, and use boundary.
* `PRD 覆盖判定`, lines 200-213, gives the forced single classification and the more accurate layered classification.
* `Final Recommendation`, lines 671-677, gives one selected direction and the no-mapping product downgrade.

Evidence locations:

* .copilot-tracking/research/subagents/2026-08-21/prd-target-intervention-scope-coverage-research.md:24-31, 189-201
* .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md:12-15, 131-231
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-retrieval-comparison-research.md:28-52
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-recall-evaluation-research.md:7-17

Assessment:

The document completely answers the three questions at the level possible without a gold standard. The correctness of the word "necessary" and the implementation timebox are separate findings under B and F; they do not create a missing-answer defect under A.

Suggested revision text: None. Preserve the three-question structure.

## B. Accuracy of the Necessary-but-Insufficient Qualification

Severity: **Major**

Main-document section and exact statements:

* `Executive Decision`, line 17: "对 target-directed intervention trials 的高召回候选生成，外部 target-to-intervention mapping 是必要组成部分。"
* `Working Hypothesis and Disconfirming Check`, line 47: "假设获得支持，但需收紧为对 target-directed intervention trial 的高召回工程流程是必要组成部分。"
* `Final Recommendation`, line 673: mapping is made an "显式必做能力" for the MVP.

Issue:

The document correctly says mapping is neither a universal logical necessity nor a sufficient condition. It then promotes a narrower design inference into a categorical engineering necessity. The experiment falsifies the claim that the tested direct `query.term` strategy is complete: at least some independently verified target-directed records are missed. It does not prove that every architecture capable of acceptable candidate recall must perform an external target-to-intervention expansion before retrieval. A condition-first pool followed by trial-level mechanism classification is an explicit counterexample architecture. It is expensive and unsuitable as the default online path, but its existence prevents the stronger necessity claim. The PRD also does not define "acceptable recall", and no gold-set or source-ablation result has been executed.

This is the exact distinction the review was asked to protect:

* Logical necessity: false in general, as the main document already acknowledges.
* Necessary relationship reasoning for target-level attribution: true. Some evidence-backed relation decision must occur before a trial can drive a target-level clinical or competition conclusion.
* Pre-query external mapping as a necessary engineering component: not proven. It is the selected low-cost architecture, not the only possible architecture.

Evidence locations:

* .copilot-tracking/research/2026-08-21/clinicaltrials-target-intervention-mapping-research.md:12-19, 33, 45-47, 190-198, 540-549
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-field-semantics-research.md:38, 158-161, 274
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-retrieval-comparison-research.md:42-52, 79-86, 631, 646-653
* .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md:219-231, 278-292
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-recall-evaluation-research.md:307-315, 435-449

Suggested revision text:

> 本轮证据否证了“仅依赖已测试的 direct target-text query 即可可靠履行当前 PRD”的假设。对选定的低延迟在线 DEMO 架构，最小、可追溯的 target-to-intervention relation layer 是推荐的工程组件，因为它以较低候选审核成本补回已验证的 direct-query 漏项。它不是所有检索架构的普遍逻辑必要条件，也尚未由 gold-set/source-ablation 证明为达到某一 recall 门槛的唯一必要实现；condition-first + trial-level mechanism classification 是成本更高的替代路线。无论候选如何生成，任何进入靶点级临床、竞争或 Go / No-Go 结论的试验都必须经过 relation evidence、intervention role、condition scope 和原文核验，因此关系判定是必要的，而预查询外部映射不是充分条件。

Replace "假设获得支持" with:

> 假设的弱形式获得支持：本轮证明 direct-text-only 存在决策相关漏项，并支持在所选 DEMO 架构中加入映射扩展；本轮尚未证明外部映射对所有高召回架构构成必要条件。

## C. A/B Counts and Recall Terminology

Severity: **PASS**

Main-document sections and exact statements:

* `三个 PRD 场景的 A/B 对照`, lines 170-188, defines A, B, overlap, direct-only, mapping-only, and union as NCT candidate sets.
* Line 178: "这些结果证明检索路线互补，但不构成真实 recall 数字。"
* Lines 180-183 explicitly state that mapping-only is not all true positive, direct-only is ambiguous, B is incomplete, and GLP-1R includes multi-target agonists.
* `Why Absolute Recall Cannot Be Reported Yet`, lines 540-549, explicitly distinguishes retrieval yield, route overlap, proxy/relative recall, and true recall.

Evidence locations:

* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-retrieval-comparison-research.md:28-52, 66-81, 595-631, 646-653
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-recall-evaluation-research.md:54-106, 307-315, 429-440
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-field-semantics-research.md:158-161

Assessment:

The A/B numbers are not mislabeled as recall. The main document uses them to demonstrate complementary candidate generation and supplements them with independently verified examples. It does not infer a recall percentage, precision, sensitivity, or global coverage from candidate counts. The necessity overstatement identified in B is a conclusion-strength issue, not a recall-labeling error.

Suggested revision text: None. Preserve the current retrieval-yield and proxy-recall terminology.

## D. PRD Line References and Coverage Classification

Severity: **PASS**

Main-document sections and statements:

* `File Analysis`, lines 63-75, cites the controlling PRD ranges.
* `PRD 覆盖判定`, lines 200-213, states: "如果必须在显式覆盖、隐含依赖、完全缺失中只选一个，答案是隐含依赖。"
* Lines 206-211 separate explicit outcome semantics, explicit intervention extraction, absent engineering contracts, implicit trial relevance, and absent quality acceptance.
* `Final Recommendation`, line 677, summarizes: "用户结果显式覆盖，映射能力属于隐含依赖，映射工程契约和质量验收在原始需求中缺失。"

PRD line audit:

| Main-document reference | PRD content | Result |
|---|---|---|
| prd-v0.1.md:8-16 | Target-level clinical signal, competition, risk, and investment questions | Accurate |
| prd-v0.1.md:26-39 | Target-screening purpose and target-input workflow ending in cited Go/No-Go/Need More Data | Accurate, slightly broad but not misleading |
| prd-v0.1.md:87-94 | Clinical Agent finds target/mechanism/indication trials and extracts interventions/signals | Accurate |
| prd-v0.1.md:96-103, 250-268 | Competition activity, crowding, and public pipeline dynamics | Accurate |
| prd-v0.1.md:114-140 | GLP-1R and TL1A target-bound scenarios | Accurate |
| prd-v0.1.md:163-190, 228-248 | Required sources and Clinical Agent output/minimum extraction | Accurate |
| prd-v0.1.md:288-334 | Output contract plus clinical/competition-driven decision rules | Accurate |
| prd-v0.1.md:388-429 | System flow lacks target normalization, intervention expansion, and relation evidence | Accurate |
| prd-v0.1.md:524-545 | MVP required and excluded scope, including no complex graph analysis | Accurate |
| prd-v0.1.md:547-555 | Success criteria omit recall, precision, attribution, and degradation gates | Accurate |

Evidence locations:

* prd-v0.1.md:8-16, 26-39, 87-103, 114-140, 163-190, 228-334, 388-429, 524-555
* .copilot-tracking/research/subagents/2026-08-21/prd-target-intervention-scope-coverage-research.md:24-31, 53-118, 120-157, 189-201

Assessment:

The line references point to the stated PRD content, and the layered classification avoids the common mistake of calling the whole capability either explicitly covered or completely absent. The relation-building implementation is absent, while the results that depend on it are explicitly promised. "Implicit dependency" is the correct forced single classification.

Suggested revision text: None.

## E. Source Capability and Licensing Claims

Severity: **Minor**

Main-document sections and statements:

* `Subagent Evidence`, line 93, says the six named sources were checked for capability and licensing.
* `Scenario 3` and `Scenario 4`, lines 270-325, accurately summarize Open Targets and ChEMBL.
* `Scenario 5`, line 351, accurately states Open Targets/HGNC CC0, ChEMBL CC BY-SA 3.0, DrugCentral CC BY-SA 4.0, and excludes Pharos while its data license remains unconfirmed.
* `Source Roles`, lines 515-522, contains Open Targets and ChEMBL but omits DrugCentral, Pharos, RxNorm, and PubChem as explicit boundary rows.

Issue:

No incorrect capability or license claim was found. The defect is consolidation completeness. A reader of the main document cannot see that DrugCentral is a direct target-drug/MoA supplement, Pharos is target-ligand/activity with unconfirmed data license and service boundary, RxNorm is name/RxCUI/brand normalization rather than target mapping, and PubChem BioAssay activity is not therapeutic mechanism. These boundaries exist only in the alternatives subagent document. The main document also abbreviates Open Targets as CC0 without repeating the official Terms warning about upstream data-owner rights.

Evidence locations:

* .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md:52-62, 64-72, 76-105, 191-203
* .copilot-tracking/research/2026-08-21/clinicaltrials-target-intervention-mapping-research.md:93, 270-355, 405-443, 513-522

Suggested revision text:

Add the following compact matrix after `Source Roles`:

| Source | Allowed role | Boundary | License or terms boundary |
|---|---|---|---|
| Open Targets | Ensembl target resolution and primary drug/clinical candidate generation | Not a complete pipeline; no complex/fusion target coverage; upstream source rights remain relevant | Platform output marked CC0 1.0; preserve release, attribution, and upstream provenance |
| ChEMBL | Curated mechanism/component and molecule alias supplement | Mechanism is preferred over assay activity; not a complete current pipeline | CC BY-SA 3.0; retain attribution and review ShareAlike for redistributed adaptations |
| DrugCentral | Optional direct target-drug/MoA supplement | Approved-drug and bioactivity focus; potency/activity is not automatically therapeutic mechanism | CC BY-SA 4.0; retain attribution and review ShareAlike before redistribution |
| Pharos/TCRD | Experimental target-ligand/activity investigation | Not automatically a therapeutic relation; production endpoint and data license remain unconfirmed | Do not package or redistribute until data license and service terms are confirmed |
| RxNorm | Clinical drug name, RxCUI, ingredient/product/brand, and NDC normalization | Does not create a target-to-drug edge | API is free for most RxNorm content with stated exceptions; full release requires UMLS licensing, Prescribable does not |
| PubChem | CID/SID, synonyms, structure, cross-references, and low-confidence BioAssay enrichment | Assay target/activity is not therapeutic mechanism, clinical phase, or indication | NCBI imposes no restriction on its own data but third-party contributed content can carry separate rights |

## F. Suitability for a One-to-Two-Week DEMO

Severity: **Major**

Main-document sections and exact statements:

* `Selected Approach`, lines 409-434, includes target resolution, two automated mapping sources, manual exceptions, dual ClinicalTrials.gov retrieval, dedupe, trial-level relation gating, exact verification, ranking, report eligibility, and decision synthesis.
* `Why This Is the Smallest Acceptable DEMO`, lines 437-443, labels this bundle the smallest acceptable scope.
* `Gold Set`, lines 553-560, adds eight scenarios, 40 main judgments, two blinded annotators, independent mechanism evidence, and adjudication.
* `Source Ablation`, lines 593-609, requires eight source combinations plus leave-one-out and multiple quality/cost metrics.
* `Implementation Order`, lines 642-650, makes the resolver, adapters, relation gate, run states, 40-record gold set, ablation, holdout gates, and Go/No-Go enablement part of one sequence.

Issue:

The architecture is a credible target design, but the document does not support calling the full build-and-validation package a one-to-two-week minimum DEMO. The workspace contains no application code, adapters, schemas, dependency manifest, UI, tests, or annotation assets. The alternatives study itself labels multi-source union the highest-complexity path and permits only a narrow union in the timebox. The evaluation study requires two domain annotators, 40 main records, 20 residual records, blinded labeling, adjudication, eight target-indication scenarios, source ablation, holdout evaluation, and failure fixtures; it also states that none of those measurements has been executed. The schedule has no staffing assumptions, work-day estimate, or explicit deferral boundary.

Evidence locations:

* .copilot-tracking/research/2026-08-21/clinicaltrials-target-intervention-mapping-research.md:79-82, 405-443, 551-609, 640-669
* .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md:191-203, 233-276
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-recall-evaluation-research.md:126-205, 251-317, 329-349, 435-449
* prd-v0.1.md:524-555

Suggested revision text:

> 一至两周实现边界分为“可演示功能切片”和“正式质量门禁”两层。首个可演示切片仅支持 PRD 的三个固定 target-indication pair，使用构建时冻结并人工复核的 versioned JSON relation snapshot，运行 direct `query.term` 与 mapped `query.intr`、NCT union/dedupe、exact-ID verification、基础 relation status、失败降级和 Top 5 展示。Open Targets/ChEMBL 在首版作为 snapshot 生成依据，不作为必须完成的通用运行时集成；DrugCentral、Pharos、RxNorm、PubChem、任意靶点解析、通用 ranker 和 condition-first 在线回退延后。首版未完成 40+20 双人标注、holdout 和 source ablation 前，不报告 proxy recall 百分比，也不让临床/竞争证据单独触发 Go 或 No-Go；完整结论保持 `NEED_MORE_DATA` 或明确标记为展示性规则输出。

Add an explicit staffing assumption:

> 时间估算假设一名全栈工程师负责 API、服务和 UI，另有一名药理/临床专家提供已复核 seed 与关键记录裁决。若没有领域专家并行投入，正式 gold-set 门禁不属于一至两周承诺。

## G. Task Researcher Success Criteria

Severity: **PASS**

Formal standard:

* `/Users/cominghe/.vscode/extensions/ise-hve-essentials.hve-core-all-3.3.101/.github/agents/hve-core/task-researcher.agent.md:70-78` requires scope/assumptions/success criteria, an evidence log, alternatives plus one selection, complete examples with references and line numbers, and actionable implementation steps.

Main-document coverage:

| Required element | Main-document location | Result |
|---|---|---|
| Scope, assumptions, success criteria | Lines 28-41 | PASS |
| Evidence log with sources, links, context | `Research Executed`, lines 61-132 | PASS |
| Evaluated alternatives | `Technical Scenarios`, lines 215-403 | PASS, seven paths |
| One selected approach and rationale | `Selected Approach`, lines 405-443; `Final Recommendation`, lines 671-677 | PASS |
| Complete examples and line-number references | Minimum data model and retrieval flow, lines 445-512; PRD file analysis, lines 63-75 | PASS |
| Actionable implementation next steps | `Implementation Order`, lines 640-651 | PASS |

Assessment:

The document satisfies the Task Researcher artifact standard. The minimum data model and retrieval flow constitute complete technical examples for this research topic, and the PRD references include line numbers. The feasibility correction under F must narrow which implementation steps belong to the first timebox, but it does not mean the research artifact lacks next steps.

Suggested revision text: None.

## Evidence Log

| Evidence | Review use | Result |
|---|---|---|
| prd-v0.1.md | Verify original requirement semantics and cited line ranges | Complete |
| .copilot-tracking/research/2026-08-21/clinicaltrials-target-intervention-mapping-research.md | Identify every reviewed conclusion and exact wording | Complete |
| .copilot-tracking/research/subagents/2026-08-21/prd-target-intervention-scope-coverage-research.md | Cross-check explicit/implicit/missing classification | Complete |
| .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-field-semantics-research.md | Cross-check logical necessity, field semantics, and counterexamples | Complete |
| .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-retrieval-comparison-research.md | Cross-check A/B definitions, counts, pagination, sampling, and recall boundaries | Complete |
| .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md | Cross-check seven paths and six-source capability/license boundaries | Complete |
| .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-recall-evaluation-research.md | Cross-check metric definitions, proposed gates, workload, and unexecuted validation | Complete |
| Task Researcher agent standard | Cross-check artifact success criteria | Complete |

## Recommended Next Research Not Completed

* [ ] Run a timeboxed implementation spike for the three fixed PRD scenarios and record engineer-days, API latency, failure rate, and review effort before retaining the one-to-two-week commitment.
* [ ] Execute the proposed 40-record gold set, 20-record residual audit, and source ablation before making any quantitative proxy-recall claim or enabling clinical/competition-driven Go/No-Go.
* [ ] Obtain project legal review for public display or redistribution of ChEMBL/DrugCentral-derived snapshots and confirm Pharos/TCRD data licensing before use.

## Clarifying Questions

None. The two required corrections can be made without additional user input. Product and staffing decisions are needed before implementation planning, not before correcting the research wording.

## Final Verdict

**NEEDS REVISION.** The evidence supports adding a traceable relation layer to the selected DEMO architecture and clearly shows that mapping alone is insufficient. Before planning, the main document must stop calling pre-query external mapping universally necessary for high-recall engineering and must split the proposed target architecture from a credible one-to-two-week implementation slice. The source matrix is a recommended consolidation improvement, not a blocker.