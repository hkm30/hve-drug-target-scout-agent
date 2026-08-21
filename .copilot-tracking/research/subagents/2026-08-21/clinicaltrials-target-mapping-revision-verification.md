<!-- markdownlint-disable-file -->

# ClinicalTrials.gov Target Mapping Revision Verification

## Review Status

Status: Complete

Verdict: **FINAL PASS**

* Unclosed Major findings: 0
* Unclosed Minor findings: 0
* Closed findings: R1, R2, R3
* Files modified by this verification: only this verification file

The revised research closes both prior Major findings and the prior Minor finding. It now distinguishes mandatory trial-level relationship adjudication from non-universally-required pre-query external mapping, separates the target architecture from the fixed three-scenario one-to-two-week slice, defers formal quality gates beyond that first slice, and consolidates the six requested source capability and licensing boundaries without adding unsupported claims.

## Review Scope and Method

Read-only verification target:

* .copilot-tracking/research/2026-08-21/clinicaltrials-target-intervention-mapping-research.md

Comparison baseline:

* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-mapping-final-review.md

Original evidence set:

* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-recall-evaluation-research.md
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-retrieval-comparison-research.md
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-field-semantics-research.md
* .copilot-tracking/research/subagents/2026-08-21/prd-target-intervention-scope-coverage-research.md
* .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md

Method:

1. Re-read the revised main document and the complete final-review finding register.
2. Cross-checked each closure against the controlling sections of all five original evidence documents.
3. Scanned the revised document for residual universal-necessity language, first-slice quality-gate commitments, source-independence claims, licensing overstatements, and cross-section contradictions.
4. Verified the three original user questions against both the direct answer table and the implementation recommendation.

## Finding Closure Register

| ID | Prior severity | Current result | Closure basis |
|---|---|---|---|
| R1 | Major | CLOSED | Mandatory relationship adjudication is explicitly separated from recommended pre-query mapping, and condition-first plus relation classification remains an acknowledged counterexample architecture |
| R2 | Major | CLOSED | Target architecture and fixed three-scenario first slice are separate sections; 40+20 review, blinded dual annotation, holdout, and full ablation are explicitly deferred |
| R3 | Minor | CLOSED | A six-row capability and licensing matrix now covers Open Targets, ChEMBL, DrugCentral, Pharos/TCRD, RxNorm, and PubChem with the same boundaries as the source study |

## R1 Verification

Result: **CLOSED**

The revised `Executive Decision` makes the required distinction in three layers:

* All trials that drive clinical, competition, or Go / No-Go conclusions must undergo relationship adjudication.
* Mapping is not a universal logical requirement for every target-related study or every retrieval architecture.
* For the selected low-latency DEMO, pre-query target-to-intervention mapping is a recommended component that repairs verified direct-query misses and controls review cost, not the only proven implementation capable of meeting an unspecified recall threshold.

The same distinction is repeated without contradiction in `Working Hypothesis and Disconfirming Check`, the `Research Questions and Answers` row for whether mapping is required, `PRD Amendments Required Before Planning` item 2, and `Final Recommendation`.

This closes the exact issue in the final review. The revised document no longer copies the over-strong engineering wording from the field-semantics or alternatives source studies. Instead, it uses their verified observations while preserving the explicit condition-first counterexample from the alternatives and retrieval-comparison evidence.

Controlling evidence:

* .copilot-tracking/research/2026-08-21/clinicaltrials-target-intervention-mapping-research.md:8-19, 43-58, 659-661, 723-727
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-mapping-final-review.md:63-97
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-field-semantics-research.md:234-283
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-retrieval-comparison-research.md:26-86, 593-653
* .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md:219-292

Residual issue: None.

## R2 Verification

Result: **CLOSED**

`Selected Approach` now separates two scopes:

* `Target Architecture` describes the intended resolver, mapping sources, dual retrieval, relation gate, verification, ranking, and decision path.
* `One-to-Two-Week Demonstrable Slice` limits the first build to GLP1R, TNFSF15/TL1A, and PCSK9 scenarios with a reviewed, versioned build-time JSON relation snapshot, dual ClinicalTrials.gov retrieval, NCT deduplication, basic relation status, degradation states, and Top 5 evidence display.

The first-slice section explicitly defers arbitrary-target resolution, productized DrugCentral/Pharos/RxNorm/PubChem integration, a general ranker, online condition-first fallback, the 40-record main gold set, the 20-record residual audit, blinded dual annotation, holdout evaluation, and full source ablation. It also prohibits proxy-recall percentages and clinical- or competition-driven Go / No-Go before formal gates complete, keeping the full decision at `NEED_MORE_DATA`.

`Implementation Order` preserves the same split under separate lists for the one-to-two-week demonstrable slice and later formal quality gates. The staffing assumption is explicit: one full-stack engineer plus one pharmacology or clinical expert working in parallel. The gold-set and ablation sections remain defined as future acceptance work, not promised execution within the first-version window.

This is consistent with the evaluation evidence, which states that the 40+20 annotation program and source ablation have not been run, and with the alternatives evidence, which permits only a narrow multi-source slice in the timebox.

Controlling evidence:

* .copilot-tracking/research/2026-08-21/clinicaltrials-target-intervention-mapping-research.md:405-475, 581-652, 683-701
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-mapping-final-review.md:192-221
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-recall-evaluation-research.md:126-205, 251-351, 431-454
* .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md:191-276, 294-383

Residual issue: None.

## R3 Verification

Result: **CLOSED**

`Extended Source and License Boundaries` accurately consolidates all six requested source classes:

| Source | Verified boundary in the revised document | Evidence comparison |
|---|---|---|
| Open Targets | Ensembl resolution and primary candidate generation; not a complete pipeline; complex/fusion and modality/product gaps; CC0 output with upstream-rights and provenance caution | Matches the alternatives study |
| ChEMBL | Mechanism/component and alias supplement; assay activity is not automatically therapeutic mechanism; incomplete current pipeline; CC BY-SA 3.0 attribution and ShareAlike review | Matches the alternatives study |
| DrugCentral | Optional direct target-drug/MoA supplement; approved-drug and bioactivity emphasis; potency/activity is not automatically therapeutic mechanism; CC BY-SA 4.0 | Matches the alternatives study |
| Pharos/TCRD | Experimental target-ligand/activity investigation; not automatically a therapeutic relation; production endpoint, versioning, and data license remain unconfirmed; no packaging or redistribution before confirmation | Matches the alternatives study and preserves its unresolved status |
| RxNorm | Clinical drug-name, RxCUI, ingredient/product/brand, and NDC normalization; no target-to-drug edge; API exceptions plus full-release UMLS and Prescribable distinctions | Matches the alternatives study |
| PubChem | Identifier, synonym, structure, cross-reference, and low-confidence BioAssay enrichment; assay activity is not therapeutic mechanism, phase, or indication; third-party rights remain possible | Matches the alternatives study |

No new capability, completeness, independence, service-level, or licensing conclusion exceeds the original evidence. The revised document also preserves the important dependency warning that Open Targets and ChEMBL can share lineage, so dual-source agreement is not automatically independent mechanism evidence.

Controlling evidence:

* .copilot-tracking/research/2026-08-21/clinicaltrials-target-intervention-mapping-research.md:545-565, 596-605
* .copilot-tracking/research/subagents/2026-08-21/clinicaltrials-target-mapping-final-review.md:159-190
* .copilot-tracking/research/subagents/2026-08-21/target-intervention-mapping-alternatives-research.md:52-114, 191-203, 395-451

Residual issue: None.

## Cross-Section Consistency

Result: **PASS**

| Section | Controlling statement | Consistency result |
|---|---|---|
| Executive Decision | Relationship adjudication is mandatory for target-level conclusions; mapping is recommended for the selected low-latency slice and is not universally necessary | Establishes the governing distinction |
| Selected Approach | Target architecture uses a traceable resolver and dual retrieval; the first slice uses a reviewed frozen snapshot for three scenarios | Implements the governing distinction at architecture and timebox levels |
| PRD Amendments Required Before Planning | Makes relationship adjudication explicit, defines the selected slice's snapshot, preserves provenance, degradation, UI warnings, and later quality criteria | Converts the decision into requirements without expanding the first-slice commitment |
| Implementation Order | Separates seven first-slice steps from five formal-gate and enhancement steps | Preserves the delivery boundary |
| Final Recommendation | Requires traceable relationship adjudication, selects the fixed-scenario snapshot, rejects universal necessity, and defines the no-relation downgrade | Restates the same policy and implementation boundary |

No section re-promotes pre-query external mapping to a universal necessity. No section puts the 40+20 annotation program, holdout evaluation, or full source ablation back into the one-to-two-week first-version commitment.

## Coverage of the Three User Questions

Result: **PASS**

1. Whether mapping is required is answered directly in `Executive Decision` and the `Research Questions and Answers` table: relationship adjudication is required for target-level conclusions, while pre-query mapping is the selected low-latency implementation rather than a universal necessity.
2. Feasible paths, sources, engineering complexity, and recall costs are answered across all seven `Technical Scenarios`, the selected target architecture, the fixed first slice, source-role tables, degradation rules, and proposed evaluation design.
3. Original PRD coverage is answered directly in `PRD 覆盖判定`, `PRD Amendments Required Before Planning`, and `Final Recommendation`: user-visible results are explicit, relationship/mapping capability is an implicit dependency, and engineering contracts plus quality acceptance are missing.

The answers remain explicit even after the necessity and timebox qualifications. The revision narrows claim strength without weakening or obscuring any of the three answers.

## Open Findings

None.

There is no remaining section requiring a severity assignment or minimum revision. Major count is 0 and Minor count is 0.

## Evidence Log

| Evidence | Verification use | Result |
|---|---|---|
| Main revised research | Checked every revised conclusion, selected design, delivery split, source matrix, PRD changes, implementation sequence, and final recommendation | Complete |
| Final independent review | Reconstructed the exact acceptance conditions for R1, R2, and R3 | Complete |
| ClinicalTrials.gov field-semantics research | Checked the missing target-field fact, query limitations, and necessary-versus-sufficient boundaries | Complete |
| Retrieval-comparison research | Checked A/B set semantics, condition-first counterexample, fixed counts, and recall limitations | Complete |
| Mapping-alternatives research | Checked all seven paths, narrow-union feasibility, and six-source capability/licensing claims | Complete |
| Recall-evaluation research | Checked the unexecuted 40+20 workload, dual annotation, holdout, ablation, and gate boundaries | Complete |
| PRD scope-coverage research | Checked the explicit-result, implicit-dependency, and missing-contract classification | Complete |

## Recommended Next Research Not Completed

* [ ] Run the fixed three-scenario implementation spike and record engineer-days, latency, failure rate, and expert-review effort before treating the one-to-two-week estimate as measured rather than assumed.
* [ ] Execute the 40-record main gold set, 20-record residual audit, target-level holdout, and source ablation before reporting proxy-recall percentages or enabling clinical/competition-driven Go / No-Go.
* [ ] Obtain project legal review for public display or redistribution of ChEMBL- or DrugCentral-derived snapshots, and confirm Pharos/TCRD data licensing before use.

## Clarifying Questions

None. Product, staffing, and legal decisions remain implementation prerequisites, but no additional input is required to verify this revision.

## Final Verdict

**FINAL PASS.** R1, R2, and R3 are closed. The revised document is evidence-bounded, internally consistent across the five controlling decision and implementation sections, and continues to answer the user's three questions directly. No Major or Minor finding remains open.