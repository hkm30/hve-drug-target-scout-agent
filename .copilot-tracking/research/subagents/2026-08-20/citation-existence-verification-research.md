<!-- markdownlint-disable-file -->

# Citation Existence Verification Research (PMID / NCT)

## Scope and Acceptance Target

- Date baseline: 2026-08-20
- Objective: design a programmatic mechanism to verify whether PMID and NCT identifiers **exist as records in authoritative sources**.
- Authoritative truth sources required by scope:
	- PMID: NCBI PubMed E-utilities
	- NCT: ClinicalTrials.gov API v2

## Research Questions

1. PMID existence: compare ESearch exact-ID, ESummary, EFetch for robustness and machine-readability.
2. NCT existence: compare single-resource endpoint (`/studies/{nctId}`) vs search endpoint behavior.
3. Error taxonomy: distinguish invalid format, not found, timeout, 429, 5xx.
4. System design: normalization, strict regex, exact echo-match, retry/cache/audit, batch strategy.
5. Deliverables: pseudocode, decision state machine, minimal acceptance test matrix.

## Evidence Log

### Official Documentation Evidence

- NCBI E-utilities official reference (updated 2026-03-04):
	- https://www.ncbi.nlm.nih.gov/books/NBK25499/
	- Evidence points used:
		- `ESearch` supports `db`, `term`, `retmode=json`.
		- `ESummary` supports `db`, `id`, `retmode=json`.
		- `EFetch` supports `db`, `id`, `retmode` (PubMed supports XML/text, etc.).
		- All three are legitimate PubMed authority endpoints under `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`.

- ClinicalTrials.gov official API docs and OpenAPI contract:
	- API overview page: https://clinicaltrials.gov/data-api/api
	- Official OAS endpoint (v2): https://clinicaltrials.gov/api/oas/v2
	- Evidence points used from OAS:
		- `GET /studies/{nctId}` path parameter pattern: `^[Nn][Cc][Tt]0*[1-9]\d{0,7}$`.
		- `GET /studies/{nctId}` declares responses `200`, `301`, `400`, `404`.
		- `GET /studies` supports `query.id` (Essie syntax) and `filter.ids` (regex-constrained NCT list).
		- `GET /studies` declares `200` and `400`.

- Local evidence artifacts (authoritative response snapshots, read-only):
	- `.copilot-tracking/research/subagents/2026-08-20/ctgov-oas-v2.yaml`
	- `.copilot-tracking/research/subagents/2026-08-20/pmid_*.meta`
	- `.copilot-tracking/research/subagents/2026-08-20/pmid_*.body`
	- `.copilot-tracking/research/subagents/2026-08-20/ct_*.meta`
	- `.copilot-tracking/research/subagents/2026-08-20/ct_*.body`

### Official Endpoint Read-Only Measurements

#### A) PMID / PubMed E-utilities comparison

Test IDs (small sample):
- Valid: `31452104`
- Syntax-invalid token: `ABC123`
- Numeric not-found candidate: `999999999`

1) `ESearch` exact-ID style (`term={id}[uid]`, `retmode=json`)

- Request example:
	- `GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term=31452104%5Buid%5D`
- Measured responses:
	- Valid: HTTP `200`, JSON `count="1"`, `idlist=["31452104"]`.
	- Invalid token `ABC123`: HTTP `200`, JSON `count="0"`, `idlist=[]`, warning `"No items found."`.
	- Not found `999999999`: HTTP `200`, JSON `count="0"`, `idlist=[]`, warning `"No items found."`.
- Parsing trap:
	- Invalid token and not-found numeric are semantically collapsed to identical `count=0` unless client pre-validates format.

2) `ESummary` (`id={id}`, `retmode=json`)

- Request example:
	- `GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=31452104&retmode=json`
- Measured responses:
	- Valid: HTTP `200`, JSON `result.uids=["31452104"]`, and `result["31452104"]` object exists.
	- Invalid token `ABC123`: HTTP `200`, JSON top-level `error="Invalid uid ABC123 at position= 0"`, `result.uids=[]`.
	- Not found `999999999`: HTTP `200`, JSON `result.uids=["999999999"]` but `result["999999999"].error="cannot get document summary"`.
- Parsing trap:
	- Existence cannot be judged by `uids` non-empty alone; must also check per-UID object has no `error`.

3) `EFetch` (`id={id}`, `retmode=xml`)

- Request example:
	- `GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=31452104&retmode=xml`
- Measured responses:
	- Valid: HTTP `200`, XML has `<PubmedArticleSet>` with article nodes.
	- Invalid token `ABC123`: HTTP `200`, XML still returns article content; extracted `<PMID Version="1">123</PMID>` from response body.
	- Not found `999999999`: HTTP `200`, XML empty set `<PubmedArticleSet></PubmedArticleSet>`.
- Parsing trap (critical):
	- `ABC123` was coerced/interpreted into PMID `123`; this can create false positives for existence checks.

#### B) NCT / ClinicalTrials.gov API v2 comparison

Test IDs (small sample):
- Valid: `NCT04280705`
- Syntax-invalid token: `ABC123`
- Not-found candidate: `NCT99999999`

1) Single-record endpoint `GET /studies/{nctId}`

- Request examples:
	- `GET https://clinicaltrials.gov/api/v2/studies/NCT04280705`
	- `GET https://clinicaltrials.gov/api/v2/studies/ABC123`
	- `GET https://clinicaltrials.gov/api/v2/studies/NCT99999999`
- Measured responses:
	- Valid: HTTP `200`, JSON includes `protocolSection.identificationModule.nctId="NCT04280705"`.
	- Invalid format: HTTP `400`, plain text `Parameter \`nctId\` has incorrect format`.
	- Not found: HTTP `404`, plain text `NCT number NCT99999999 not found`.

2) Search endpoint `GET /studies`

- `filter.ids` mode (ID list)
	- Valid (`filter.ids=NCT04280705`): HTTP `200`, `studies` contains matching record.
	- Invalid (`filter.ids=ABC123`): HTTP `400`, `Item 1 in parameter \`filter.ids\` has incorrect format`.
	- Not found (`filter.ids=NCT99999999`): HTTP `200`, `{"studies":[  ]}`.

- `query.id` mode (Essie query)
	- Valid (`query.id=NCT04280705`): HTTP `200`, returns matching study.
	- `query.id=ABC123`: HTTP `200`, returned unrelated record where `ABC123` appeared as secondary/registry ID (`NCT03470298` observed in sample).
	- Not found (`query.id=NCT99999999`): HTTP `200`, empty studies.
- Parsing trap:
	- `query.id` is search-expression semantics, not strict identity semantics.

#### C) Rate-limit and operational hints from live headers

- NCBI E-utilities headers in measured calls contained `x-ratelimit-limit: 3` and `x-ratelimit-remaining` (values varied by call).
- Both ecosystems can return HTTP `200` for multiple semantic outcomes, so JSON/XML content checks are mandatory.

## Findings and Conclusions (Tagged)

1) PMID verification should not use `EFetch` as primary existence check. `[已验证]`
- Reason: official endpoint real test showed `id=ABC123` produced article with PMID `123` (coercion risk), causing false positives.

2) PMID preferred method: `ESummary` (`retmode=json`) with strict pre-validation + exact key check + per-record error check. `[已验证]`
- Why:
	- Valid ID returns keyed object.
	- Invalid syntax returns explicit `error`.
	- Not found returns UID with nested `error`, distinguishable from format error.

3) PMID alternative method: `ESearch` exact-ID (`term={id}[uid]`) is acceptable but weaker alone. `[已验证]`
- Why weaker:
	- Invalid syntax token and numeric-not-found both collapse to `count=0` unless client pre-validates format.

4) NCT single-item verification should prefer `GET /studies/{nctId}`. `[已验证]`
- Why:
	- Distinct status semantics measured directly: `200` (exists), `400` (format invalid), `404` (not found).

5) NCT search endpoint should use `filter.ids` for batch identity checks, not `query.id`. `[已验证]`
- Why:
	- `query.id` is search-language behavior and can match aliases/secondary identifiers; observed false-positive-style match for `ABC123`.

6) Input normalization + strict regex gate is mandatory before network call. `[条件性]`
- NCT regex is contract-backed (`^[Nn][Cc][Tt]0*[1-9]\d{0,7}$`) from official OAS.
- PMID regex is not explicitly published as a contract in the consulted E-utilities reference; project must adopt a strict numeric policy (see algorithm) and keep it configurable.

7) `HTTP 200` cannot be interpreted as “record exists” in either ecosystem. `[已验证]`
- Must inspect response body semantics (fields and error nodes).

8) “记录存在”不等于“文献未撤稿”“证据正确”“试验结果可信”。 `[条件性]`
- This mechanism only proves identifier-resolvable record existence in authority sources.
- Retraction status, evidence relevance/quality, methodological trustworthiness require separate downstream validators.

9) `301` alias-redirect behavior for `/studies/{nctId}` is documented but not empirically exercised in this run. `[仍是假设]`

## Algorithm and State Machine

### Input normalization and regex policy

- PMID normalization:
	- `trim` whitespace.
	- reject any non-digit character.
	- keep as canonical digit string (no sign, no decimals, no separators).
- NCT normalization:
	- `trim` whitespace.
	- uppercase prefix to `NCT`.
	- do not strip internal digits except optional leading zeros handling per policy.

Recommended strict regex gates:
- PMID (project policy, configurable): `^[1-9][0-9]{0,8}$` `[条件性]`
	- Note: upper bound chosen as defensive implementation policy; keep configurable because consulted E-utilities docs do not publish a strict PMID length contract.
- NCT (official OAS contract): `^[Nn][Cc][Tt]0*[1-9]\d{0,7}$` `[已验证]`

### Recommended verification algorithms (language-agnostic pseudocode)

```text
function verify_pmid_exists(raw_id):
	id = normalize_pmid(raw_id)
	if !regex_match(PMID_REGEX, id):
		return INVALID_FORMAT

	resp = http_get(
		"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
		query={db:"pubmed", id:id, retmode:"json", tool:TOOL, email:EMAIL},
		timeout=REQUEST_TIMEOUT
	)

	if resp.timeout:
		return TRANSIENT_TIMEOUT
	if resp.http_status == 429:
		return TRANSIENT_RATE_LIMIT
	if 500 <= resp.http_status <= 599:
		return TRANSIENT_SERVER_ERROR
	if resp.http_status != 200:
		return UPSTREAM_PROTOCOL_ERROR

	json = parse_json(resp.body)

	# explicit syntax error path
	if has(json.error):
		if contains_ignore_case(json.error, "invalid uid"):
			return INVALID_FORMAT
		return UPSTREAM_SEMANTIC_ERROR

	# existence path must require exact echo and no nested error
	if id not in json.result.uids:
		return NOT_FOUND
	rec = json.result[id]
	if !rec:
		return NOT_FOUND
	if has(rec.error):
		if contains_ignore_case(rec.error, "cannot get document summary"):
			return NOT_FOUND
		return UPSTREAM_SEMANTIC_ERROR

	return EXISTS


function verify_nct_exists(raw_id):
	id = normalize_nct(raw_id)
	if !regex_match(NCT_REGEX, id):
		return INVALID_FORMAT

	resp = http_get(
		"https://clinicaltrials.gov/api/v2/studies/" + url_encode(id),
		timeout=REQUEST_TIMEOUT
	)

	if resp.timeout:
		return TRANSIENT_TIMEOUT
	if resp.http_status == 429:
		return TRANSIENT_RATE_LIMIT
	if 500 <= resp.http_status <= 599:
		return TRANSIENT_SERVER_ERROR

	if resp.http_status == 400:
		return INVALID_FORMAT
	if resp.http_status == 404:
		return NOT_FOUND
	if resp.http_status == 301:
		# follow redirect by policy or treat as EXISTS_ALIAS
		return EXISTS_ALIAS_REDIRECT
	if resp.http_status != 200:
		return UPSTREAM_PROTOCOL_ERROR

	json = parse_json(resp.body)
	observed = json.protocolSection.identificationModule.nctId
	if observed is null:
		return UPSTREAM_SEMANTIC_ERROR
	if to_upper(observed) != to_upper(id):
		# if redirect was already followed, this can still be valid alias resolution
		return EXISTS_ID_MISMATCH_REVIEW

	return EXISTS
```

### Batch strategy

- PMID batch:
	- Use bounded concurrency (e.g., 2-3 in-flight per source host by default).
	- Prefer per-ID `ESummary` for deterministic auditability; if throughput pressure exists, multi-ID calls are possible but require robust response partitioning.
- NCT batch:
	- Preferred: `GET /studies` with `filter.ids` chunked lists for throughput, then exact-match each returned `nctId` against requested set.
	- Never use `query.id` for strict batch existence.

### Retry, timeout, cache, and status mapping

- Timeout class:
	- connect/read timeout -> `TRANSIENT_TIMEOUT`.
- Retryable statuses:
	- `429`, `5xx`, timeout.
	- exponential backoff with jitter, capped attempts (e.g., 3).
- Non-retryable statuses:
	- `400` invalid format (NCT single/filter.ids), semantic invalid UID in PMID response.
	- `404` not found (NCT single).
- Cache policy (implementation recommendation):
	- `EXISTS`: longer TTL (e.g., 24h) `[条件性]`
	- `NOT_FOUND`: shorter TTL (e.g., 1h) `[条件性]`
	- transient errors: no cache or ultra-short negative cache.

### Audit evidence fields (must persist per check)

- `source_system`: `pubmed_eutils` | `clinicaltrials_gov_v2`
- `method`: `esummary` | `esearch_uid` | `efetch` | `studies_by_id` | `studies_filter_ids`
- `input_raw`, `input_normalized`
- `request_url` (without secrets), `request_query`
- `http_status`, `content_type`, `latency_ms`, `attempt_index`
- `response_body_hash` (sha256), optional truncated body snippet
- `parsed_signals` (e.g., `count`, `idlist`, `error_text`, `observed_nct_id`)
- `decision_state` (EXISTS / NOT_FOUND / INVALID_FORMAT / TRANSIENT_* / UPSTREAM_*)
- `decision_reason_code` (machine enum)
- `timestamp_utc`

### Decision state machine

```text
START
	-> NORMALIZE
		-> REGEX_GATE_FAIL ---------------------------> INVALID_FORMAT (terminal)
		-> REGEX_GATE_PASS -> CALL_AUTHORITY
			-> TIMEOUT/429/5xx ------------------------> TRANSIENT_RETRYABLE
			-> OTHER_NON_200 (protocol-specific) ------> UPSTREAM_PROTOCOL_ERROR
			-> 200/expected-status -> PARSE_BODY
				-> explicit invalid syntax signal -------> INVALID_FORMAT
				-> explicit not-found signal ------------> NOT_FOUND
				-> exact-ID echo mismatch ---------------> UPSTREAM_SEMANTIC_ERROR (or REVIEW)
				-> exact-ID echo match + no error -------> EXISTS
```

## Minimal Acceptance Test Matrix

Small mandatory acceptance suite (read-only; can run in CI smoke profile with rate limits):

| Case ID | Identifier Type | Method | Input | Expected Status | Expected Semantic Check |
|---|---|---|---|---|---|
| PMID-01 | PMID | ESummary | `31452104` | `EXISTS` | `result.uids` contains `31452104`, `result[31452104]` has no `error` |
| PMID-02 | PMID | ESummary | `ABC123` | `INVALID_FORMAT` | JSON top-level `error` contains `Invalid uid` |
| PMID-03 | PMID | ESummary | `999999999` | `NOT_FOUND` | `result[999999999].error` contains `cannot get document summary` |
| PMID-04 | PMID | ESearch | `term=31452104[uid]` | `EXISTS` | `count=1` and `idlist == [31452104]` |
| PMID-05 | PMID | EFetch (safety test) | `ABC123` | `UNSAFE_METHOD_DETECTED` | body contains coerced PMID `123` (method should be rejected for existence) |
| NCT-01 | NCT | `/studies/{nctId}` | `NCT04280705` | `EXISTS` | payload `identificationModule.nctId` equals `NCT04280705` |
| NCT-02 | NCT | `/studies/{nctId}` | `ABC123` | `INVALID_FORMAT` | HTTP `400` with format error text |
| NCT-03 | NCT | `/studies/{nctId}` | `NCT99999999` | `NOT_FOUND` | HTTP `404` with not-found text |
| NCT-04 | NCT | `/studies?filter.ids=` | `ABC123` | `INVALID_FORMAT` | HTTP `400` |
| NCT-05 | NCT | `/studies?filter.ids=` | `NCT99999999` | `NOT_FOUND` | HTTP `200` and `studies=[]` |
| NCT-06 | NCT | `/studies?query.id=` (guardrail) | `ABC123` | `METHOD_NOT_ALLOWED_FOR_EXISTENCE` | can return unrelated hit; test ensures method is blocked |

Operational acceptance checks:
- Retry policy test: simulate `429`/`5xx` and verify bounded exponential retry.
- Timeout classification test: forced timeout classified as transient, not not-found.
- Audit test: every terminal decision must contain complete evidence fields.

## Limits and Non-Goals

- This mechanism verifies **record resolvability/existence only** at authority endpoints. `[已验证]`
- It does not determine:
	- whether a paper is retracted,
	- whether cited evidence is the correct evidence for the claim,
	- whether trial outcomes are methodologically credible.
	These require additional downstream validators and domain review. `[条件性]`

- Endpoint behavior can evolve; regex, error strings, and response schemas should be monitored by contract tests. `[条件性]`

## Open Clarifications

1. PMID regex final policy: should we enforce a hard max length in gateway (current recommendation is configurable)?
2. Alias handling for NCT `301`: follow redirect automatically and mark `EXISTS_ALIAS_REDIRECT`, or require strict non-alias matching?
3. Cache TTL policy: what staleness tolerance is acceptable for `NOT_FOUND` and `EXISTS` decisions in your production workflow?
4. Should batch mode prefer pure single-check determinism (one request per ID) or throughput-optimized grouped checks with stricter audit joins?

