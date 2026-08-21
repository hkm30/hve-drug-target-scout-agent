---
description: "Pre-implementation security risk assessment for drug-target-scout-agent"
author: Security Reviewer
ms.date: 2026-08-21
ms.topic: assessment
keywords:
  - security
  - OWASP
  - pre-implementation
  - drug research
---

# OWASP Pre-Implementation Security Risk Assessment

**Date:** 2026-08-21
**Repository:** drug-target-scout-agent
**Agent:** Security Reviewer
**Mode:** plan
**Skills applied:** owasp-llm, owasp-agentic, owasp-top-10, owasp-infrastructure, owasp-cicd, secure-by-design, owasp-mcp
**Plan source:** [.copilot-tracking/security/2026-08-20/drug-target-scout-security-plan.md](../2026-08-20/drug-target-scout-security-plan.md)

---

## Executive Summary

The assessment evaluated 71 planned controls across seven security frameworks for a high-impact drug R&D decision-support system that consumes untrusted biomedical data and uses Microsoft Foundry for LLM synthesis. It identified 6 RISK and 37 CAUTION findings, while 26 controls are COVERED and 2 are NOT_APPLICABLE. The 43 actionable findings comprise 31 HIGH and 12 MEDIUM items, with no CRITICAL or LOW findings. Six RISK and 30 CAUTION findings apply to the current design; the remaining 7 CAUTION findings, comprising 6 HIGH and 1 MEDIUM, are conditional and activate only if MCP is introduced.

### Risk Summary

| Status         | Count  |
|----------------|--------|
| RISK           | 6      |
| CAUTION        | 37     |
| COVERED        | 26     |
| NOT_APPLICABLE | 2      |
| **Total**      | **71** |

### Severity Breakdown (RISK + CAUTION only)

| Severity | Count |
|----------|-------|
| CRITICAL | 0     |
| HIGH     | 31    |
| MEDIUM   | 12    |
| LOW      | 0     |

---

## Risk Findings by Framework

### owasp-llm

| ID    | Title                            | Status         | Severity | Risk Description                                                                                                                                    | Mitigation                                                                                                                                                  |
|-------|----------------------------------|----------------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| LLM02 | Sensitive Information Disclosure | CAUTION        | HIGH     | No work package detects PHI, PII, credentials, or other sensitive content before Foundry processing, logging, display, or export.                    | Add an application Sensitive Data Gateway with classified states, fail-closed inbound and outbound scanning, redaction, tests, and G-08/G-10 evidence.       |
| LLM10 | Unbounded Consumption            | CAUTION        | HIGH     | Source API limits do not enforce per-user Foundry token, concurrency, queue, retry, daily cost, or aggregate budget limits across replicas.           | Add atomic quotas, bounded queues and retries, 429 responses, budget circuit breakers, a cost kill switch, and G-05/G-08/G-09 evidence.                       |
| LLM01 | Prompt Injection                 | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| LLM03 | Supply Chain                     | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| LLM04 | Data and Model Poisoning         | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| LLM05 | Improper Output Handling         | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| LLM06 | Excessive Agency                 | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| LLM07 | System Prompt Leakage            | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| LLM09 | Misinformation                   | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| LLM08 | Vector and Embedding Weaknesses  | NOT_APPLICABLE | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |

The remaining reviewer-count ambiguity associated with LLM09 is tracked as actionable under ASI09, A06, SBD-01, and SBD-05 rather than counted twice.

### owasp-agentic

| ID    | Title                                  | Status         | Severity | Risk Description                                                                                                                                    | Mitigation                                                                                                                                                  |
|-------|----------------------------------------|----------------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ASI03 | Identity and Privilege Abuse           | CAUTION        | HIGH     | Environment identities are scoped, but authorization is not bound to the user, task, resource, action, purpose, or current revocation state.         | Require a signed, short-lived authorization context and re-authorize every privileged operation with replay and revocation checks.                          |
| ASI06 | Memory and Context Poisoning           | CAUTION        | HIGH     | Evidence persistence lacks a contract for purpose, namespace, expiry, reuse, rescanning, revocation, and model-output re-ingestion.                   | Separate audit-only and retrievable stores, namespace by task and subject, enforce lifecycle and taint rules, and prohibit untrusted model-output reuse.     |
| ASI09 | Human-Agent Trust Exploitation         | CAUTION        | HIGH     | Production approval requirements conflict between two mandatory domain reviewers and a pending one-or-two reviewer decision.                        | Make two distinct domain reviewers an invariant for production GO/NO_GO decisions and require security review for injection alerts.                         |
| ASI01 | Goal Hijack                            | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| ASI02 | Tool Misuse                            | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| ASI04 | Agentic Supply Chain                   | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| ASI05 | Unexpected Code Execution              | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| ASI08 | Cascading Failures                     | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| ASI10 | Rogue Agents                           | COVERED        | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |
| ASI07 | Insecure Inter-Agent Communication     | NOT_APPLICABLE | N/A      | N/A                                                                                                                                                 | N/A                                                                                                                                                         |

### owasp-top-10

| ID  | Title                             | Status  | Severity | Risk Description                                                                                                                                       | Mitigation                                                                                                                                                  |
|-----|-----------------------------------|---------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A01 | Broken Access Control             | CAUTION | HIGH     | General Entra ID and RBAC controls do not define deny-by-default endpoint, method, object-level, IDOR, CORS, or CSRF behavior.                           | Define a route, method, role, and object authorization matrix and test forced browsing, cross-tenant access, IDOR, CORS, and CSRF denial.                    |
| A04 | Cryptographic Failures            | CAUTION | HIGH     | The plan lacks TLS minimums, HSTS, certificate validation, encryption-at-rest and backup requirements, a CMK decision, and key lifecycle tests.         | Establish an automated cryptographic baseline covering transport, storage, keys, certificates, backups, cache controls, and local-auth disablement.         |
| A05 | Injection                         | CAUTION | HIGH     | SSRF, XXE, and XSS controls are detailed, but future SQL/NoSQL parameterization, interpreter boundaries, and SAST/DAST/IAST gates are absent.           | Define safe data-access and interpreter contracts and add static, dynamic, interactive, and fuzz testing gates before new execution surfaces are accepted.  |
| A06 | Insecure Design                   | RISK    | HIGH     | The contradictory reviewer count makes the production approval state machine ambiguous and may permit a single-reviewer GO or NO_GO decision.          | Require two distinct production domain identities, scope any single-reviewer flow to nonproduction, and add security review for injection-alert decisions.  |
| A07 | Authentication Failures           | CAUTION | HIGH     | JWT issuer, audience, scope, role, and tenant validation plus session timeout, logout invalidation, and secure cookie behavior are unspecified.         | Define and test a complete token and session validation contract, including revocation, inactivity, absolute timeout, and secure cookie attributes.          |
| A02 | Security Misconfiguration         | CAUTION | MEDIUM   | No concrete production baseline covers HTTP headers, CORS, debug features, API documentation, default endpoints, or trusted proxies.                  | Add a production runtime baseline and automated policy tests for headers, origins, proxy trust, diagnostics, documentation, and default routes.             |
| A09 | Logging and Alerting              | CAUTION | MEDIUM   | Log value encoding, CR/LF injection resistance, immutable centralized retention, and repeated-error aggregation are not defined.                       | Standardize structured event schemas and encoding, test log injection, centralize immutable retention, and aggregate repeated errors into alerts.           |
| A10 | Exceptional Conditions            | CAUTION | MEDIUM   | Global fallback handling, resource cleanup, atomic multi-step state, compensation, duplicate-error aggregation, and exhaustion tests are missing.      | Define exception boundaries, cleanup and compensation behavior, atomic transitions, bounded failures, and resource-exhaustion tests.                        |
| A03 | Software Supply Chain             | COVERED | N/A      | N/A                                                                                                                                                    | N/A                                                                                                                                                         |
| A08 | Software and Data Integrity       | COVERED | N/A      | N/A                                                                                                                                                    | N/A                                                                                                                                                         |

### owasp-infrastructure

| ID    | Title                                       | Status  | Severity | Risk Description                                                                                                                                       | Mitigation                                                                                                                                                   |
|-------|---------------------------------------------|---------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ISR02 | Insufficient Threat Detection               | CAUTION | HIGH     | Application telemetry does not define SIEM and Defender coverage across identity, control plane, network, container, and data-plane logs.               | Create a cross-layer log-source and detection matrix, coverage metrics, correlated rules, alert ownership, and logging-interruption detection.               |
| ISR03 | Insecure Configurations                     | CAUTION | HIGH     | Policy automation is vague and omits deny rules, drift and exception handling, RPO/RTO, zones, probes, backup/PITR, and restore testing.                | Implement Azure Policy plus PSRule or OPA gates, formal exceptions, drift detection, resilience targets, health probes, backups, and restore evidence.       |
| ISR05 | Insecure Cryptography                       | CAUTION | HIGH     | Infrastructure cryptographic requirements omit Key Vault RBAC, soft delete, purge protection, local-auth disablement, and the broader A04 baseline.    | Apply the shared cryptographic baseline to Azure resources and enforce Key Vault lifecycle, managed identity, RBAC, and recovery controls through policy.     |
| ISR07 | Insecure Authentication and Default Credentials | CAUTION | HIGH | MFA and Conditional Access are explicit only for approvers and admins, while local or shared-key auth remains possible for service resources.          | Cover every interactive user with Conditional Access and disable local or shared-key authentication for ACR, storage, Cosmos DB, Foundry, and similar services. |
| ISR08 | Information Leakage                         | CAUTION | HIGH     | No DLP package protects Foundry inputs and outputs, stores, telemetry, reports, downloads, retention, or allowed egress.                                | Add a data-protection package with classification, DLP enforcement, immutable audit storage, retention decisions, download controls, and egress allowlists.  |
| ISR10 | Asset Management                            | CAUTION | MEDIUM   | The plan lacks complete Azure asset inventory, continuous discovery and IaC reconciliation, criticality, orphan detection, and secure retirement.      | Build an authoritative inventory tied to IaC, continuously reconcile deployed assets, classify criticality, alert on orphans, and record retirement proof.   |
| ISR01 | Outdated Software                           | COVERED | N/A      | N/A                                                                                                                                                    | N/A                                                                                                                                                          |
| ISR04 | Resource and User Management                | COVERED | N/A      | N/A                                                                                                                                                    | N/A                                                                                                                                                          |
| ISR06 | Network Access                              | COVERED | N/A      | N/A                                                                                                                                                    | N/A                                                                                                                                                          |
| ISR09 | Management Components                       | COVERED | N/A      | N/A                                                                                                                                                    | N/A                                                                                                                                                          |

### owasp-cicd

| ID         | Title                         | Status  | Severity | Risk Description                                                                                                                                     | Mitigation                                                                                                                                                    |
|------------|-------------------------------|---------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CICD-SEC-1 | Flow Control                  | CAUTION | HIGH     | Branch protection, required reviews, CODEOWNERS, bypass prohibition, auto-merge limits, and commit/deploy separation are unspecified.                | Enforce protected branches and environments, independent approvals, CODEOWNERS, no bypass, bounded auto-merge, and separation of commit and deploy authority. |
| CICD-SEC-2 | Identity and Access Management | CAUTION | HIGH     | SCM and CI identity lifecycle plus exact OIDC issuer, audience, repository, ref, workflow, and environment claim restrictions are missing.            | Require SSO/SCIM lifecycle controls and constrain federated credentials to explicit protected workflow claims with short-lived least privilege.               |
| CICD-SEC-3 | Dependency Chain Abuse        | CAUTION | HIGH     | Python dependency installation lacks an approved proxy/index, hash enforcement, dependency-confusion protection, and install-time credential isolation. | Use a curated proxy, lock and verify hashes, reserve internal names, disable fallback indexes, and prevent secrets or OIDC access during installation.        |
| CICD-SEC-4 | Poisoned Pipeline Execution   | RISK    | HIGH     | Untrusted PR, fork, workflow, and build-file changes could obtain OIDC privileges and create or sign malicious deployable images.                    | Split secretless untrusted PR validation from protected-ref build, sign, and deploy workflows; only trusted immutable refs may receive OIDC.                  |
| CICD-SEC-5 | Pipeline-Based Access Controls | CAUTION | HIGH    | Runner ephemerality, sharing, host privileges, cache cleanup, Docker socket access, patching, network policy, and duty isolation are unspecified.      | Use isolated ephemeral runners, deny host-level privileges, sanitize caches, restrict egress, patch images, and separate build, signing, and deployment.       |
| CICD-SEC-7 | System Configuration          | CAUTION | MEDIUM   | SCM, CI, ACR, signing, and runner baselines do not define default token permissions, debug behavior, or self-hosted runner requirements.              | Publish hardened baselines, default workflow tokens to read-only, prohibit debug leakage, and continuously test runner and service configuration.             |
| CICD-SEC-8 | Third-Party Services          | CAUTION | MEDIUM   | Actions, Apps, OAuth integrations, webhooks, scanners, and signing services lack admission, inventory, permission, expiry, and review requirements.    | Establish an allowlisted third-party service registry with owner, purpose, permissions, pinned version, expiry, review cadence, and removal process.           |
| CICD-SEC-10 | Logging and Visibility       | CAUTION | MEDIUM   | SCM audit, protection changes, approvals, workflows, OIDC, runners, ACR, and signing events lack end-to-end correlation and alerting.                  | Centralize CI/CD audit sources, assign correlation identifiers, detect control changes and anomalous issuance, and test alert delivery.                        |
| CICD-SEC-6 | Credential Hygiene            | COVERED | N/A      | N/A                                                                                                                                                  | N/A                                                                                                                                                           |
| CICD-SEC-9 | Artifact Integrity             | COVERED | N/A      | N/A                                                                                                                                                  | N/A                                                                                                                                                           |

### secure-by-design

| ID     | Title                      | Status  | Severity | Risk Description                                                                                                                                        | Mitigation                                                                                                                                                    |
|--------|----------------------------|---------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| SBD-01 | Governance                 | CAUTION | HIGH     | SEC-404 permits formal risk acceptance while mandatory gates allow only PASS/FAIL, and the production reviewer-count contradiction remains unresolved. | Prevent risk acceptance from overriding gates, require two production reviewers, assign a senior risk owner, and add training and maturity metrics.          |
| SBD-03 | Secure Product Development | RISK    | HIGH     | The plan lacks a secure SDLC package and creates a cycle where SEC-104 needs a candidate model/region while SEC-301 final selection depends on SEC-104. | Add secure coding, review, SAST, DAST, IaC, and developer hardening controls; split candidate capability probing from final selection.                         |
| SBD-05 | Usable Controls            | CAUTION | HIGH     | Session, token, and cookie baselines, degraded-state warnings, approval usability metrics, and an unambiguous dual-review experience are missing.      | Define secure session controls and explicit degraded states, make dual review unavoidable in production, and measure approval quality and operator errors.    |
| SBD-06 | Detect and Respond         | RISK    | HIGH     | SEC-404 must collect G-09 evidence from SEC-405, but SEC-405 depends on SEC-404, creating a cycle that can block or bypass final security approval.      | Split evidence freeze and pre-review from final signing, run SEC-405 before final SEC-404 approval, and select immutable centralized audit storage.            |
| SBD-10 | Continuous Assurance       | RISK    | HIGH     | Per-commit security gates, periodic dynamic assurance, deployed-SBOM monitoring, disclosure, feedback, and a fixed evaluation cadence are absent.      | Add continuous assurance work packages and an explicit candidate deployment prerequisite for SEC-402, with measurable gates and post-launch cadence.         |
| SBD-02 | Risk-Driven                | CAUTION | MEDIUM   | Risk appetite is not quantified, while jurisdiction, retention, and evidence-quality authority remain unresolved.                                      | Define measurable risk thresholds and make jurisdiction, retention, and evidence-quality ownership hard deployment blockers.                                 |
| SBD-04 | Supply Chain               | CAUTION | MEDIUM   | Third-party admission, vendor due diligence, AI-generated code review, deployed-SBOM monitoring, and quantified remediation SLAs are missing.          | Add supplier admission and review controls, mandatory human review for AI-generated code, runtime SBOM monitoring, and severity-based remediation SLAs.       |
| SBD-07 | Flexible Architecture      | CAUTION | MEDIUM   | Security components cannot be independently upgraded or rolled back, and interfaces, cryptography, and blue/green security updates are not planned.    | Version security interfaces, isolate security component releases, support rollback and cryptographic agility, and test blue/green security updates.           |
| SBD-11 | Secure Deprecation         | RISK    | MEDIUM   | No end-of-life process covers services, data sources, APIs, features, stores, identities, credentials, networks, backups, or destruction evidence.      | Add secure deprecation work packages with inventory, migration, destruction, access cleanup, backup verification, owner approval, and retained proof.         |
| SBD-08 | Minimize Attack Surface    | COVERED | N/A      | N/A                                                                                                                                                     | N/A                                                                                                                                                           |
| SBD-09 | Defense in Depth           | COVERED | N/A      | N/A                                                                                                                                                     | N/A                                                                                                                                                           |

### owasp-mcp (Conditional)

> [!IMPORTANT]
> MCP is not part of the MVP and the model tool count is zero. The seven CAUTION findings in this section do not describe current exposure; they become mandatory admission criteria only if MCP is introduced.

| ID    | Title                | Status  | Severity | Risk Description                                                                                                                                       | Mitigation                                                                                                                                               |
|-------|----------------------|---------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| MCP01 | Token Mismanagement  | CAUTION | HIGH     | Conditional on MCP adoption: the future gate does not require short-lived tokens bound to audience, tool, user, and session.                            | Require short-lived, least-privilege, audience/tool/session-bound tokens with rotation, revocation, replay protection, and negative tests.                |
| MCP03 | Tool Poisoning       | CAUTION | HIGH     | Conditional on MCP adoption: trusted server identity, signed tool descriptions, schema hash pinning, and runtime drift rejection are absent.           | Verify server identity, sign and pin tool metadata and schemas, reject drift, and require re-approval after any tool contract change.                     |
| MCP04 | Supply Chain         | CAUTION | HIGH     | Conditional on MCP adoption: SDKs, connectors, remote servers, plugins, and manifests are not explicitly included in SBOM and provenance controls.     | Extend admission, SBOM, provenance, signature, vulnerability, and update controls to every MCP component and remote server.                              |
| MCP07 | Authentication and Authorization | CAUTION | HIGH | Conditional on MCP adoption: mutual identity, server-side token validation, anonymous disablement, session binding, and mTLS or equivalent are missing. | Require mutual authenticated identities, validated scoped tokens, anonymous denial, session binding, and mTLS or equivalent workload identity.          |
| MCP09 | Shadow MCP           | CAUTION | HIGH     | Conditional on MCP adoption: no central registry, IaC admission, deployment enforcement, or network discovery prevents unauthorized MCP servers.       | Establish an authoritative MCP registry, require approved IaC deployment, block unknown endpoints, and continuously discover and quarantine shadow MCP. |
| MCP10 | Context Over-Sharing | CAUTION | HIGH     | Conditional on MCP adoption: context lacks user, agent, and session namespaces, TTL, purge behavior, and cross-session isolation tests.                 | Isolate context by user, agent, task, and session; minimize fields; enforce TTL and purge; and test cross-namespace denial.                              |
| MCP08 | Audit                | CAUTION | MEDIUM   | Conditional on MCP adoption: server, tool, schema, auth, approval, request, and result details are absent from call-level audit requirements.           | Record tamper-resistant MCP call events with correlation, redaction, retention, alerting, and explicit approval evidence.                               |
| MCP02 | Scope Creep          | COVERED | N/A      | N/A                                                                                                                                                    | N/A                                                                                                                                                      |
| MCP05 | Command Execution    | COVERED | N/A      | N/A                                                                                                                                                    | N/A                                                                                                                                                      |
| MCP06 | Context Prompt Injection | COVERED | N/A  | N/A                                                                                                                                                    | N/A                                                                                                                                                      |

---

## Mitigation Guidance

### CRITICAL Severity

None identified.

### HIGH Severity

#### LLM02 Sensitive Information Disclosure

**Risk description:** Sensitive biomedical content, credentials, or unexpected personal data could reach Foundry, telemetry, reports, or exports without detection or policy enforcement.

**Attack scenario:** A compromised upstream API embeds credentials or personal data in a record; the application sends it to the model and persists the value in logs and an analyst download.

**Mitigation steps:**

1. Define PHI, PII, credential, secret, and allowed biomedical-data classifications with explicit allow, redact, quarantine, and reject states.
2. Place a fail-closed Sensitive Data Gateway before Foundry and on every model output, log, UI, report, and export path.
3. Generate G-08 and G-10 evidence from positive, negative, encoded, fragmented, and outage-path tests.

**Implementation checklist:**

* [ ] Gateway decisions are deterministic, auditable, and enforced before every sensitive sink.
* [ ] Tests prove fail-closed behavior when classifiers or policy services are unavailable.

#### LLM10 Unbounded Consumption

**Risk description:** The plan cannot enforce per-user or aggregate model consumption and cost limits across concurrent Container Apps replicas.

**Attack scenario:** An authenticated user fans out expensive prompts while retries amplify load, exhausting the Foundry budget and starving legitimate research tasks.

**Mitigation steps:**

1. Define per-user, per-task, tenant, daily cost, token, concurrency, queue, and retry ceilings.
2. Enforce limits atomically in a shared store and return deterministic 429 responses with bounded retry guidance.
3. Add budget circuit breakers, an operator kill switch, alerts, and G-05/G-08/G-09 load and failure tests.

**Implementation checklist:**

* [ ] Multi-replica race tests prove quotas cannot be bypassed.
* [ ] Budget exhaustion blocks new model work without corrupting in-flight task state.

#### ASI03 Identity and Privilege Abuse

**Risk description:** Workload identity alone does not prove that each privileged action remains authorized for the initiating user, task, resource, and purpose.

**Attack scenario:** A valid task token is replayed against another report or reused after the user's access is revoked, allowing unauthorized evidence retrieval or approval mutation.

**Mitigation steps:**

1. Define a signed authorization context containing subject, taskId, resource, action, purpose, audience, issued-at, expiry, and unique nonce.
2. Re-authorize every privileged operation and verify current user, tenant, role, resource ownership, purpose, expiry, audience, and revocation state.
3. Store replay state atomically and add cross-task, expired, revoked, and mid-task privilege-change tests.

**Implementation checklist:**

* [ ] Every privileged handler consumes and validates the authorization context.
* [ ] Revocation and replay tests fail closed across all replicas.

#### ASI06 Memory and Context Poisoning

**Risk description:** Persisted evidence can become a cross-task poisoning channel because retrieval purpose, taint, expiry, and reuse rules are undefined.

**Attack scenario:** Adversarial content from one source record is retained and later reintroduced into another model context without rescanning, changing an unrelated target recommendation.

**Mitigation steps:**

1. Classify stores as audit-only or retrievable and document the allowed reader, purpose, namespace, retention, and deletion contract for each.
2. Namespace retrievable evidence by tenant, subject, task, source, and policy version; preserve taint and rescan after policy or scanner changes.
3. Prohibit model-output re-ingestion unless an explicit reviewed transformation removes taint and produces traceable evidence.

**Implementation checklist:**

* [ ] Cross-task and cross-tenant retrieval tests prove namespace isolation.
* [ ] Expired, revoked, or unrescanned evidence cannot enter a new model context.

#### ASI09 Human-Agent Trust Exploitation

**Risk description:** Conflicting approval requirements can make a single review appear sufficient for a high-impact drug R&D decision.

**Attack scenario:** A persuasive but unsupported model summary is approved by one reviewer because the implementation follows the unresolved one-or-two reviewer branch.

**Mitigation steps:**

1. Remove the pending reviewer-count decision for production and require two distinct domain reviewer identities for every GO or NO_GO outcome.
2. Prevent self-review, duplicate identity, delegated-session reuse, and approval before evidence freeze.
3. Require an additional security review when injection or data-integrity alerts remain associated with the task.

**Implementation checklist:**

* [ ] The state machine cannot reach an approved production state with fewer than two distinct domain signatures.
* [ ] UI and API tests expose uncertainty and block approval while required reviews remain outstanding.

#### A01 Broken Access Control

**Risk description:** General RBAC language does not establish route, method, object, tenant, and workflow-state authorization for APIs and downloads.

**Attack scenario:** A user changes a task or report identifier and reads another team's evidence because the endpoint checks authentication but not object ownership and purpose.

**Mitigation steps:**

1. Create a deny-by-default matrix for every route and method covering role, tenant, object relationship, task state, purpose, and response behavior.
2. Enforce object-level checks in a shared authorization policy layer and constrain CORS and CSRF protections by client type.
3. Test forced browsing, IDOR, cross-tenant identifiers, method changes, stale grants, and hidden endpoints.

**Implementation checklist:**

* [ ] Every endpoint maps to a named authorization policy and negative tests.
* [ ] Report, task, approval, evidence, and download objects enforce ownership and tenant isolation.

#### A04 Cryptographic Failures

**Risk description:** Missing transport, storage, certificate, key, and cache requirements allow implementations that expose sensitive research evidence or weaken integrity.

**Attack scenario:** A service accepts an obsolete TLS configuration or caches a sensitive report while unmanaged keys and backups lack tested rotation and recovery.

**Mitigation steps:**

1. Set minimum TLS, HSTS, certificate and hostname verification, secure cipher, and no-plaintext communication requirements.
2. Define encryption for data, logs, backups, queues, and caches; decide CMK usage through threat and compliance analysis.
3. Automate key rotation, expiry, revocation, backup recovery, cache-control, and configuration tests.

**Implementation checklist:**

* [ ] Policy and integration tests reject weak transport and invalid certificates.
* [ ] Key lifecycle and encrypted restore evidence are required before deployment approval.

#### A05 Injection

**Risk description:** Future database or interpreter features could bypass the plan's strong SSRF, XXE, and XSS controls because safe execution contracts are incomplete.

**Attack scenario:** A later search feature concatenates an untrusted biomedical identifier into a SQL or NoSQL query, enabling data extraction or policy bypass.

**Mitigation steps:**

1. Require parameterized APIs for every SQL, NoSQL, shell, template, expression, and interpreter boundary, with explicit forbidden APIs.
2. Add secure coding examples and mandatory security review for any new parser, query, template, or execution surface.
3. Run per-commit SAST and targeted fuzzing, plus scheduled DAST and IAST where supported.

**Implementation checklist:**

* [ ] Unsafe data-access and execution APIs are blocked by lint or policy rules.
* [ ] Injection test corpora cover encoded, nested, delayed, and second-order payloads.

#### A06 Insecure Design

**Risk description:** The approval state machine has two incompatible definitions for the number of production reviewers.

**Attack scenario:** An implementation selects the weaker interpretation and allows one compromised or over-trusting reviewer to authorize a consequential recommendation.

**Mitigation steps:**

1. Make two distinct domain reviewers a production invariant for GO and NO_GO decisions.
2. Restrict any single-reviewer workflow to clearly labeled nonproduction evaluation and prevent its data from becoming a production decision.
3. Require security sign-off for unresolved injection alerts and test every invalid state transition.

**Implementation checklist:**

* [ ] Production transition guards enforce two unique domain identities at the data layer.
* [ ] Concurrency tests prevent duplicate or stale approvals from satisfying the invariant.

#### A07 Authentication Failures

**Risk description:** Authentication implementation can accept tokens or sessions with incorrect issuer, audience, tenant, role, scope, lifetime, or revocation state.

**Attack scenario:** A token minted for another audience or tenant reaches an API that validates only the signature and grants access to protected task data.

**Mitigation steps:**

1. Specify issuer, audience, tenant, signature algorithm, key rollover, scope, role, subject, and lifetime validation.
2. Define inactivity and absolute session timeouts, logout and revocation semantics, secure cookie attributes, and reauthentication for approval.
3. Test wrong-audience, wrong-tenant, expired, future, revoked, key-rollover, fixation, and logout cases.

**Implementation checklist:**

* [ ] Authentication middleware fails closed on every omitted or unexpected claim.
* [ ] Approval actions require recent authentication and cannot reuse invalidated sessions.

#### ISR02 Insufficient Threat Detection

**Risk description:** Application logs alone cannot detect attacks that span identity, Azure control plane, network, container, and data services.

**Attack scenario:** An attacker changes a federated credential, deploys a modified image, and exfiltrates reports while each layer records isolated events that never trigger a correlated alert.

**Mitigation steps:**

1. Inventory required Entra, Azure Activity, Defender, Container Apps, network, Key Vault, registry, storage, database, Foundry, and application log sources.
2. Define cross-layer detection rules, severity, owners, response SLAs, correlation identifiers, and measurable source coverage.
3. Alert when expected telemetry stops and run end-to-end attack simulations that prove detection and routing.

**Implementation checklist:**

* [ ] SIEM onboarding and detection coverage are deployment gates.
* [ ] Logging interruption and cross-layer attack simulations produce owned alerts.

#### ISR03 Insecure Configurations

**Risk description:** Vague policy automation and absent resilience requirements permit insecure drift and untested recovery in production Azure resources.

**Attack scenario:** A manual change exposes a service or disables backup; no deny policy or drift alert fires, and restoration fails during an incident.

**Mitigation steps:**

1. Codify deny and audit rules with Azure Policy plus PSRule or OPA for identity, network, encryption, diagnostics, public access, and approved SKUs.
2. Define exception ownership, expiry, evidence, remediation, and continuous IaC-to-runtime drift reconciliation.
3. Set RPO/RTO, zone, probe, backup/PITR, and restore requirements and validate them through scheduled exercises.

**Implementation checklist:**

* [ ] Noncompliant resources cannot pass deployment without an approved expiring exception.
* [ ] Restore tests demonstrate the documented RPO and RTO before production launch.

#### ISR05 Insecure Cryptography

**Risk description:** Azure resources can retain local authentication or weak key recovery settings even if application cryptography is correctly implemented.

**Attack scenario:** A leaked storage key bypasses managed identity, while disabled purge protection allows an attacker to destroy the key needed for recovery.

**Mitigation steps:**

1. Reuse the A04 cryptographic baseline for every Azure service and infrastructure module.
2. Enforce Key Vault RBAC, soft delete, purge protection, rotation, recovery, diagnostic logging, and separation of duties.
3. Disable local or shared-key authentication wherever managed identity is supported and test policy compliance.

**Implementation checklist:**

* [ ] IaC and Azure Policy enforce Key Vault recovery and access requirements.
* [ ] Local-auth denial is tested for each data, registry, and AI service.

#### ISR07 Insecure Authentication and Default Credentials

**Risk description:** Interactive identities and service resources can fall outside Conditional Access or continue accepting default and shared credentials.

**Attack scenario:** A non-approver account without MFA is compromised and uses a shared storage or registry key to access data outside normal RBAC checks.

**Mitigation steps:**

1. Apply MFA and risk-based Conditional Access to all interactive users, with documented emergency-access controls.
2. Disable local, password, and shared-key authentication for ACR, storage, Cosmos DB, Foundry, and every service that supports managed identity.
3. Continuously detect credential re-enablement, stale accounts, shared principals, and unmanaged exceptions.

**Implementation checklist:**

* [ ] Identity policy coverage includes every interactive role, not only approvers and administrators.
* [ ] Runtime tests prove shared keys and local credentials are rejected.

#### ISR08 Information Leakage

**Risk description:** Data protection is not implemented across model, storage, telemetry, report, download, retention, and egress paths.

**Attack scenario:** A report containing sensitive source data is retained indefinitely, indexed in telemetry, and downloaded to an unmanaged client.

**Mitigation steps:**

1. Add a data inventory and flow model with classification, purpose, residency, retention, and approved destination for every field.
2. Apply the Sensitive Data Gateway, field-level logging rules, immutable audit retention, download authorization, and egress allowlists.
3. Select Evidence and Audit store controls, retention periods, deletion workflows, and DLP evidence before deployment.

**Implementation checklist:**

* [ ] Every data sink has an owner, classification, retention period, and enforcement control.
* [ ] Tests prove blocked data cannot reach Foundry, logs, reports, exports, or unapproved egress.

#### CICD-SEC-1 Flow Control

**Risk description:** Repository and deployment workflows lack enforceable governance for protected changes and authority separation.

**Attack scenario:** A contributor merges a workflow change through a bypass or permissive auto-merge path and immediately deploys it using the same authority.

**Mitigation steps:**

1. Require protected branches, signed or attributable commits, status checks, CODEOWNERS, independent PR approvals, and conversation resolution.
2. Prohibit bypass except through a monitored emergency process and restrict auto-merge to policy-compliant low-risk changes.
3. Separate commit, approval, environment approval, and production deployment authority.

**Implementation checklist:**

* [ ] Protection settings and bypass changes are monitored and tested.
* [ ] No identity can author, solely approve, and deploy the same production change.

#### CICD-SEC-2 Identity and Access Management

**Risk description:** Broad or stale SCM and CI identities plus weak OIDC claim restrictions can grant unintended deployment access.

**Attack scenario:** An external collaborator or alternate workflow obtains a cloud token because federation checks only the repository and not the protected ref, workflow, and environment.

**Mitigation steps:**

1. Enforce SSO, SCIM lifecycle, least privilege, external collaborator sponsorship and expiry, and periodic access review.
2. Restrict OIDC by issuer, audience, organization, repository, immutable workflow identity, protected ref, and environment.
3. Use short token lifetimes, separate identities per environment, and alert on unusual token issuance.

**Implementation checklist:**

* [ ] Federated credentials cannot be invoked from forks, pull requests, or unapproved workflows.
* [ ] Departed and expired collaborators lose SCM, CI, and cloud access automatically.

#### CICD-SEC-3 Dependency Chain Abuse

**Risk description:** Uncontrolled Python resolution can install attacker-owned packages or mutable artifacts during a privileged build.

**Attack scenario:** A public package matching an internal name is selected from a fallback index and executes while OIDC or signing credentials are available.

**Mitigation steps:**

1. Route dependencies through an approved proxy or private index with explicit upstream policy and internal namespace reservation.
2. Lock direct and transitive versions, require hashes, verify provenance where available, and block dependency fallback behavior.
3. Run installation in a network-constrained phase without secrets, OIDC, signing access, or deployment permissions.

**Implementation checklist:**

* [ ] Builds fail on missing or mismatched hashes and unapproved indexes.
* [ ] Dependency installation cannot access cloud or signing credentials.

#### CICD-SEC-4 Poisoned Pipeline Execution

**Risk description:** The trust boundary between untrusted contribution testing and trusted artifact production is undefined.

**Attack scenario:** A fork changes a workflow or build script, receives OIDC in a privileged job, and publishes a signed malicious image that appears legitimate.

**Mitigation steps:**

1. Run fork and pull-request validation with read-only source access, no secrets, no OIDC, no registry push, and no persistent runner state.
2. Build, attest, sign, and deploy only from protected immutable refs using trusted workflow definitions and isolated identities.
3. Prevent untrusted artifacts, caches, outputs, or workflow code from crossing into trusted jobs without reconstruction and verification.

**Implementation checklist:**

* [ ] Adversarial fork tests cannot obtain credentials, publish artifacts, or influence trusted caches.
* [ ] Signed production images trace to a protected commit and trusted workflow identity.

#### CICD-SEC-5 Pipeline-Based Access Controls

**Risk description:** Runner and job isolation requirements are absent, allowing one build to affect hosts, caches, credentials, or later jobs.

**Attack scenario:** A malicious build accesses the Docker socket, modifies a shared runner, and steals signing material from a subsequent protected job.

**Mitigation steps:**

1. Use ephemeral single-job runners or equivalent isolation and prohibit privileged containers, host mounts, and unrestricted Docker socket access.
2. Separate validation, build, signing, and deployment into distinct trust zones, identities, and network policies.
3. Patch runner images, sanitize scoped caches, restrict egress, inventory tooling, and verify teardown after every job.

**Implementation checklist:**

* [ ] Runner isolation tests prove no cross-job filesystem, process, cache, or credential persistence.
* [ ] Signing and deployment environments cannot execute untrusted contribution code.

#### SBD-01 Governance

**Risk description:** Ambiguous gate semantics allow formal risk acceptance or inconsistent reviewer rules to weaken mandatory production controls.

**Attack scenario:** A delivery owner records risk acceptance instead of satisfying a failed gate and proceeds with only one domain approval.

**Mitigation steps:**

1. State that mandatory G-series gates remain binary and cannot be overridden by risk acceptance.
2. Assign a senior accountable risk owner for non-gate residual risks and require documented scope, expiry, treatment, and review.
3. Resolve dual review, provide role-based security training, and publish gate, exception, incident, and remediation maturity metrics.

**Implementation checklist:**

* [ ] SEC-404 cannot sign final approval when any mandatory gate is not PASS.
* [ ] Governance metrics and expiring residual-risk decisions have named owners.

#### SBD-03 Secure Product Development

**Risk description:** Secure engineering controls are absent and the SEC-104/SEC-301 dependency cycle makes model capability validation and final selection impossible to order safely.

**Attack scenario:** The team selects a model without completing required security capability tests, while insecure code reaches deployment because no secure SDLC gates exist.

**Mitigation steps:**

1. Add secure coding standards, threat-focused code review, SAST, DAST, dependency and IaC scanning, secret scanning, and developer workstation hardening.
2. Create a candidate model and region capability probe that precedes SEC-104 without constituting final selection.
3. Make SEC-301 final selection consume the completed SEC-104 evidence and record an acyclic dependency graph.

**Implementation checklist:**

* [ ] Secure SDLC controls run on every protected change and block defined severities.
* [ ] The candidate probe and final model selection are distinct, ordered work packages.

#### SBD-05 Usable Controls

**Risk description:** Security controls may be bypassed or misunderstood because session rules, degraded-state communication, and approval ergonomics are unspecified.

**Attack scenario:** A reviewer approves using a stale session while a scanner is degraded, and the interface does not clearly show that a second independent signature remains required.

**Mitigation steps:**

1. Define secure session, token, reauthentication, and cookie behavior for all reviewer interactions.
2. Display explicit, non-dismissable degraded-state and missing-evidence warnings and block consequential actions when required controls are unavailable.
3. Design the production approval flow around two distinct reviewers and measure errors, abandonment, overrides, and warning comprehension.

**Implementation checklist:**

* [ ] Usability tests prove reviewers can identify provenance, uncertainty, degraded controls, and outstanding approvals.
* [ ] UI behavior cannot weaken API and state-machine enforcement.

#### SBD-06 Detect and Respond

**Risk description:** The SEC-404/SEC-405 dependency cycle can prevent evidence completion or encourage final approval before red-team evidence exists.

**Attack scenario:** SEC-404 is signed without G-09 because SEC-405 cannot run until SEC-404 is complete, leaving production without validated attack detection and response evidence.

**Mitigation steps:**

1. Split SEC-404 into evidence freeze and pre-review, followed by final approval and signing.
2. Run SEC-405 after evidence freeze but before final approval, then attach G-09 results to the immutable evidence set.
3. Select centralized immutable audit storage and test incident triage, containment, recovery, and evidence preservation.

**Implementation checklist:**

* [ ] The work-item graph is acyclic and requires SEC-405 before final SEC-404 signing.
* [ ] Final approval binds to the immutable hash of all G-01 through G-10 evidence.

#### SBD-10 Continuous Assurance

**Risk description:** The plan lacks continuous and post-launch security validation and leaves SEC-402 dependent on an undefined candidate deployment.

**Attack scenario:** A secure launch gradually degrades through dependency, policy, model, or infrastructure drift because no recurring tests or deployed-SBOM monitoring detect it.

**Mitigation steps:**

1. Add per-commit SAST, SCA, secret, IaC, and policy gates with explicit blocking thresholds.
2. Define periodic DAST, penetration tests, red-team evaluations, deployed-SBOM monitoring, disclosure intake, and root-cause feedback.
3. Create an explicit candidate deployment work package before SEC-402 and set a fixed post-launch evaluation cadence with owners and evidence.

**Implementation checklist:**

* [ ] Continuous and periodic controls have schedules, owners, thresholds, and retained results.
* [ ] SEC-402 references a defined, isolated, and reproducible candidate deployment.

#### MCP01 Token Mismanagement (Conditional)

**Risk description:** If MCP is introduced, generic service tokens could be reused across users, tools, audiences, or sessions.

**Attack scenario:** A token issued for one MCP tool is replayed against another server or after a session ends, exposing context or invoking unintended capabilities.

**Mitigation steps:**

1. Issue short-lived tokens bound to user or workload, audience, server, tool, task, and session.
2. Enforce least privilege, nonce or proof-of-possession replay controls, rotation, revocation, and no token forwarding in context.
3. Add wrong-tool, wrong-audience, cross-session, expired, revoked, and replay tests to the MCP admission gate.

**Implementation checklist:**

* [ ] This control is activated before any MCP client or server reaches a shared environment.
* [ ] Tokens cannot be logged, persisted in context, or accepted outside their binding.

#### MCP03 Tool Poisoning (Conditional)

**Risk description:** If MCP is introduced, mutable or unauthenticated tool metadata could silently change model-visible instructions and schemas.

**Attack scenario:** A remote MCP server alters a tool description to induce data exfiltration while retaining the same endpoint and tool name.

**Mitigation steps:**

1. Authenticate each server and approve canonical tool descriptions, schemas, capabilities, and owners.
2. Sign metadata, pin schema and description hashes, compare at connection and invocation, and reject runtime drift.
3. Require review, version change, and regression tests before accepting any metadata update.

**Implementation checklist:**

* [ ] This control is activated before any MCP server is registered.
* [ ] Drift tests prove changed descriptions or schemas cannot execute silently.

#### MCP04 Supply Chain (Conditional)

**Risk description:** If MCP is introduced, its SDKs, plugins, manifests, connectors, and remote servers could escape existing supply-chain controls.

**Attack scenario:** An untracked connector update introduces malicious code or redirects calls to an unapproved server without changing the main application lockfile.

**Mitigation steps:**

1. Include all MCP software, manifests, tool schemas, server identities, and hosted dependencies in inventory and SBOM scope.
2. Require provenance, signatures, pinned versions, vulnerability review, vendor assessment, and controlled updates.
3. Monitor runtime versions and revoke servers or components that drift from approved evidence.

**Implementation checklist:**

* [ ] This control is activated before MCP dependency or server admission.
* [ ] Deployed MCP inventory continuously reconciles with approved provenance.

#### MCP07 Authentication and Authorization (Conditional)

**Risk description:** If MCP is introduced, missing mutual authentication and session-bound authorization could allow anonymous, impersonated, or cross-session calls.

**Attack scenario:** A rogue server accepts bearer tokens without validating issuer or audience and returns another user's tool result to the active agent session.

**Mitigation steps:**

1. Require mutual client and server identity using mTLS or equivalent workload identity and disable anonymous access.
2. Validate token issuer, audience, subject, scope, tool, session, lifetime, and revocation at the server for every call.
3. Authorize each tool and resource independently and test impersonation, confused deputy, and cross-session cases.

**Implementation checklist:**

* [ ] This control is activated before MCP network access is allowed.
* [ ] Client and server negative-authentication tests fail closed.

#### MCP09 Shadow MCP (Conditional)

**Risk description:** If MCP is introduced, unregistered servers can bypass approved tool, identity, network, and audit controls.

**Attack scenario:** A developer deploys an unofficial remote MCP server and configures an agent to use it, leaking research context outside approved egress paths.

**Mitigation steps:**

1. Maintain a central MCP registry with owner, purpose, identity, tools, data classes, network location, version, and expiry.
2. Permit deployment only through approved IaC and block unregistered endpoints through egress and admission policies.
3. Discover MCP traffic and manifests continuously, alert on unknown services, and quarantine or retire unauthorized instances.

**Implementation checklist:**

* [ ] This control is activated before MCP endpoints are permitted by network policy.
* [ ] Registry and runtime discovery reconcile with no unmanaged exceptions.

#### MCP10 Context Over-Sharing (Conditional)

**Risk description:** If MCP is introduced, context without strict namespaces and lifecycle controls could expose one user's or task's evidence to another.

**Attack scenario:** A shared MCP server retains prior tool context and returns confidential evidence when a different user invokes the same tool.

**Mitigation steps:**

1. Namespace context by tenant, user, agent, task, tool, and session and authorize every read and write.
2. Minimize shared fields, preserve taint, set TTL, support targeted purge, and prohibit hidden server-side reuse.
3. Test cross-user, cross-agent, cross-task, cross-session, expired, and purged context access.

**Implementation checklist:**

* [ ] This control is activated before MCP context persistence is enabled.
* [ ] Isolation and purge tests cover both client and server state.

### MEDIUM Severity

#### A02 Security Misconfiguration

**Risk description:** Production HTTP and framework defaults are not constrained by a testable baseline.

**Attack scenario:** Debug endpoints, permissive CORS, API documentation, or incorrect proxy trust expose internals or weaken authentication in production.

**Mitigation steps:**

1. Define required security headers, exact CORS origins and methods, trusted proxy ranges, host validation, and request-size limits.
2. Disable debug, development errors, sample routes, default credentials, unnecessary methods, and production API documentation unless explicitly authorized.
3. Test the running candidate configuration and fail deployment on baseline drift.

**Implementation checklist:**

* [ ] Production configuration tests run against the deployed candidate.
* [ ] Every exception has an owner, purpose, expiry, and compensating control.

#### A09 Logging and Alerting

**Risk description:** Unencoded or fragmented logging can permit log injection and hide repeated attacks across replicas.

**Attack scenario:** An attacker inserts CR/LF characters into a source identifier to forge events while repeated failures remain below per-instance alert thresholds.

**Mitigation steps:**

1. Use structured schemas, canonical field names, safe value encoding, bounded lengths, and explicit secret and sensitive-data exclusions.
2. Centralize logs in immutable storage with retention, access control, correlation, time synchronization, and health monitoring.
3. Test CR/LF and parser injection and aggregate repeated errors across users, sources, tasks, and replicas.

**Implementation checklist:**

* [ ] Adversarial values cannot create or alter log records.
* [ ] Repeated-error tests trigger a single correlated, owned alert.

#### A10 Exceptional Conditions

**Risk description:** Undefined exception and compensation behavior can leave partial approvals, leaked resources, or cascading failures.

**Attack scenario:** A timeout occurs after evidence is stored but before task state commits, causing duplicate retries and an inconsistent approval record.

**Mitigation steps:**

1. Add a global safe exception fallback with stable error codes, correlation identifiers, and no internal detail leakage.
2. Define transaction, idempotency, compensation, timeout, cancellation, and local resource cleanup for each multi-step workflow.
3. Test duplicate failures, exhaustion, partial dependencies, queue saturation, and recovery across replicas.

**Implementation checklist:**

* [ ] Multi-step state changes are atomic or have tested compensation.
* [ ] Failure storms remain bounded and produce aggregated telemetry.

#### ISR10 Asset Management

**Risk description:** Unreconciled assets can remain unowned, unpatched, publicly reachable, or active after retirement.

**Attack scenario:** A temporary candidate deployment survives testing with stale credentials and an exposed endpoint because it is absent from the authoritative inventory.

**Mitigation steps:**

1. Inventory every Azure resource, identity, endpoint, data store, model deployment, certificate, and external dependency with owner and criticality.
2. Reconcile runtime discovery against IaC and approved exceptions, alerting on drift, orphaned assets, and unsupported versions.
3. Define secure retirement that removes data, backups as authorized, identities, credentials, DNS, network access, and monitoring entries.

**Implementation checklist:**

* [ ] Continuous discovery reports unmatched IaC and runtime assets.
* [ ] Retirement evidence is retained and approved by the asset owner.

#### CICD-SEC-7 System Configuration

**Risk description:** SCM, CI, registry, signing, and runner defaults can grant excessive permissions or expose sensitive debug output.

**Attack scenario:** A workflow inherits write permissions and debug logging prints token-bearing headers on a persistent self-hosted runner.

**Mitigation steps:**

1. Define hardened baselines for SCM, workflow tokens, environments, ACR, signing, logs, caches, and runners.
2. Default workflow permissions to read-only, grant job-specific access, prohibit secret-bearing debug, and restrict self-hosted runners.
3. Continuously compare live settings to baseline and alert on privileged changes.

**Implementation checklist:**

* [ ] Baseline checks block protected workflows with excessive token permissions.
* [ ] Runner and service drift is detected independently of repository code.

#### CICD-SEC-8 Third-Party Services

**Risk description:** Unreviewed integrations can gain durable access to source, workflows, artifacts, identities, and deployment events.

**Attack scenario:** An abandoned GitHub App or webhook retains organization-wide permissions and sends repository events to a compromised vendor endpoint.

**Mitigation steps:**

1. Register Actions, Apps, OAuth grants, webhooks, scanners, and signing services with owner, purpose, data, permissions, and vendor evidence.
2. Pin code by immutable digest, minimize scopes, verify webhook signatures, and set review and expiry dates.
3. Monitor changes and usage, reassess vendors, and remove inactive or unsupported integrations.

**Implementation checklist:**

* [ ] Unregistered third-party services cannot run in protected workflows.
* [ ] Expired or ownerless integrations are disabled automatically or through an enforced SLA.

#### CICD-SEC-10 Logging and Visibility

**Risk description:** CI/CD events cannot be correlated from source approval through cloud identity, artifact signing, registry publication, and deployment.

**Attack scenario:** A branch protection change and anomalous OIDC issuance enable a malicious image, but investigators cannot link the events or distinguish the trusted deployment chain.

**Mitigation steps:**

1. Collect SCM audit, branch and environment protection, review, workflow, OIDC, runner, ACR, attestation, signing, and deployment logs.
2. Propagate repository, commit, workflow, run, artifact digest, identity, environment, and deployment correlation fields.
3. Alert on protection weakening, unusual federation, runner changes, failed verification, and log-source interruption.

**Implementation checklist:**

* [ ] A production artifact can be traced end to end from approved commit to deployment.
* [ ] Detection tests cover control changes and anomalous OIDC issuance.

#### SBD-02 Risk-Driven

**Risk description:** Unquantified risk appetite and unresolved legal and evidence decisions prevent consistent deployment decisions.

**Attack scenario:** Teams interpret acceptable residual risk differently and launch before jurisdiction, retention, or evidence authority is settled.

**Mitigation steps:**

1. Define measurable risk appetite and tolerances for data exposure, model error, downtime, supply-chain findings, and unresolved controls.
2. Assign accountable decision owners for jurisdiction, retention, and evidence-quality authority.
3. Make unresolved decisions explicit deployment blockers with required evidence and deadlines.

**Implementation checklist:**

* [ ] Every gate maps to a documented risk threshold and accountable owner.
* [ ] Jurisdiction, retention, and evidence authority are resolved before production approval.

#### SBD-04 Supply Chain

**Risk description:** Supplier and generated-code controls do not cover admission, deployed-state monitoring, or time-bound remediation.

**Attack scenario:** An approved dependency later becomes vulnerable or AI-generated code introduces an insecure pattern that passes functional review and remains deployed.

**Mitigation steps:**

1. Define third-party and vendor admission criteria, ownership, data access, provenance, support, and exit requirements.
2. Require human security review and the same automated gates for AI-generated code as for human-authored code.
3. Monitor deployed SBOMs continuously and enforce severity-based remediation and exception SLAs.

**Implementation checklist:**

* [ ] Supplier and AI-generated changes cannot bypass standard review and testing.
* [ ] Deployed vulnerable components trigger tracked remediation within defined SLAs.

#### SBD-07 Flexible Architecture

**Risk description:** Coupled security components and unversioned interfaces increase the chance that urgent updates cause outages or remain delayed.

**Attack scenario:** A scanner vulnerability cannot be patched independently, forcing a full application release and leaving the unsafe version active.

**Mitigation steps:**

1. Define versioned contracts for policy, scanning, identity, evidence, audit, and model gateway components.
2. Support independent upgrade, rollback, compatibility testing, and feature-gated blue/green rollout for security services.
3. Add cryptographic agility for algorithms, certificates, keys, and provider changes without data loss.

**Implementation checklist:**

* [ ] Security components have tested independent rollback and compatibility paths.
* [ ] Cryptographic and policy migrations preserve verifiability of existing evidence.

#### SBD-11 Secure Deprecation

**Risk description:** Services, APIs, stores, and identities may remain accessible or retain data after end of life.

**Attack scenario:** A retired biomedical API integration leaves credentials, cached source records, backups, and network rules active after the feature disappears from the UI.

**Mitigation steps:**

1. Define end-of-life triggers, owners, communication, migration, retention, and destruction requirements for every component and data source.
2. Revoke identities and credentials, remove network and DNS access, disable jobs, and update asset and SBOM inventories.
3. Verify authorized backup handling and data destruction, then retain signed retirement evidence.

**Implementation checklist:**

* [ ] Each asset class has a tested deprecation runbook and accountable owner.
* [ ] Retirement cannot close until access, data, backup, and inventory evidence is complete.

#### MCP08 Audit (Conditional)

**Risk description:** If MCP is introduced, incomplete call-level audit could prevent attribution and investigation of tool misuse or context leakage.

**Attack scenario:** A tool returns unauthorized data, but logs contain only the agent request and omit server identity, schema version, authorization, approval, and result classification.

**Mitigation steps:**

1. Record timestamp, correlation, user and workload identity, session, server, tool, schema hash, authorization decision, approval, result class, latency, and outcome.
2. Redact secrets and sensitive payloads while preserving tamper-resistant evidence, retention, access control, and clock integrity.
3. Alert on denied calls, schema drift, unusual tools, cross-session attempts, and audit-source interruption.

**Implementation checklist:**

* [ ] This control is activated before MCP calls are enabled outside isolated development.
* [ ] Audit tests reconstruct an MCP call without storing prohibited payload data.

### LOW Severity

None identified.

---

## Implementation Security Checklist

| ID          | Risk                                      | Severity | Mitigation Required                                                                                         | Status      |
|-------------|-------------------------------------------|----------|-------------------------------------------------------------------------------------------------------------|-------------|
| LLM02       | Sensitive Information Disclosure          | HIGH     | Implement and test the fail-closed Sensitive Data Gateway across all data sinks.                            | NOT_STARTED |
| LLM10       | Unbounded Consumption                     | HIGH     | Enforce atomic model quotas, budgets, bounded retries, 429 behavior, and kill switches.                     | NOT_STARTED |
| ASI03       | Identity and Privilege Abuse              | HIGH     | Bind and re-authorize every privileged operation using signed, revocable authorization context.            | NOT_STARTED |
| ASI06       | Memory and Context Poisoning              | HIGH     | Define audit and retrieval store contracts, namespaces, taint, expiry, rescanning, and revocation.          | NOT_STARTED |
| ASI09       | Human-Agent Trust Exploitation            | HIGH     | Enforce two distinct production domain reviewers and security review for injection alerts.                 | NOT_STARTED |
| A01         | Broken Access Control                     | HIGH     | Implement the route, method, object, tenant, and workflow authorization matrix with negative tests.         | NOT_STARTED |
| A04         | Cryptographic Failures                    | HIGH     | Codify and test transport, storage, backup, key, certificate, cache, and local-auth controls.               | NOT_STARTED |
| A05         | Injection                                 | HIGH     | Add safe data-access and interpreter contracts plus SAST, DAST, IAST, and fuzzing gates.                    | NOT_STARTED |
| A06         | Insecure Design                           | HIGH     | Remove reviewer ambiguity and enforce the production approval state-machine invariant.                     | NOT_STARTED |
| A07         | Authentication Failures                  | HIGH     | Define and test complete token, tenant, session, revocation, logout, and cookie validation.                 | NOT_STARTED |
| ISR02       | Insufficient Threat Detection             | HIGH     | Build cross-layer SIEM and Defender coverage, correlation, interruption detection, and simulations.         | NOT_STARTED |
| ISR03       | Insecure Configurations                   | HIGH     | Enforce cloud policy and drift controls plus RPO/RTO, probes, backups, PITR, and restore tests.             | NOT_STARTED |
| ISR05       | Insecure Cryptography                     | HIGH     | Apply the crypto baseline and Key Vault recovery, RBAC, lifecycle, and local-auth policy.                   | NOT_STARTED |
| ISR07       | Insecure Authentication and Defaults      | HIGH     | Extend Conditional Access to all users and disable service local and shared-key authentication.             | NOT_STARTED |
| ISR08       | Information Leakage                       | HIGH     | Implement end-to-end data classification, DLP, retention, download, audit-store, and egress controls.       | NOT_STARTED |
| CICD-SEC-1  | Flow Control                              | HIGH     | Enforce branch and environment protection, reviews, CODEOWNERS, no bypass, and duty separation.            | NOT_STARTED |
| CICD-SEC-2  | CI/CD Identity and Access Management      | HIGH     | Add identity lifecycle and exact protected OIDC claim restrictions.                                         | NOT_STARTED |
| CICD-SEC-3  | Dependency Chain Abuse                    | HIGH     | Use a curated Python index, hashes, namespace protection, and secretless dependency installation.           | NOT_STARTED |
| CICD-SEC-4  | Poisoned Pipeline Execution               | HIGH     | Separate untrusted secretless PR validation from protected build, sign, and deploy workflows.              | NOT_STARTED |
| CICD-SEC-5  | Pipeline-Based Access Controls            | HIGH     | Isolate ephemeral runners, caches, networks, privileges, signing, and deployment duties.                    | NOT_STARTED |
| SBD-01      | Governance                                | HIGH     | Prevent risk acceptance from overriding gates and add ownership, training, and maturity metrics.           | NOT_STARTED |
| SBD-03      | Secure Product Development                | HIGH     | Add the secure SDLC package and split candidate capability probing from final model selection.             | NOT_STARTED |
| SBD-05      | Usable Controls                           | HIGH     | Add session baselines, degraded-state UX, dual-review UX, and approval usability metrics.                  | NOT_STARTED |
| SBD-06      | Detect and Respond                        | HIGH     | Break the SEC-404/SEC-405 cycle and bind final approval to immutable complete evidence.                     | NOT_STARTED |
| SBD-10      | Continuous Assurance                     | HIGH     | Add continuous and periodic assurance plus an explicit candidate deployment before SEC-402.                | NOT_STARTED |
| MCP01       | Token Mismanagement (conditional)         | HIGH     | If MCP is adopted, require short-lived user, audience, tool, task, and session-bound tokens.                | NOT_STARTED |
| MCP03       | Tool Poisoning (conditional)              | HIGH     | If MCP is adopted, authenticate servers and sign, pin, and drift-check tool metadata.                       | NOT_STARTED |
| MCP04       | Supply Chain (conditional)                | HIGH     | If MCP is adopted, extend SBOM, provenance, signature, and admission controls to all MCP components.        | NOT_STARTED |
| MCP07       | Authentication and Authorization (conditional) | HIGH | If MCP is adopted, require mutual identity, server-side validation, session binding, and anonymous denial.  | NOT_STARTED |
| MCP09       | Shadow MCP (conditional)                  | HIGH     | If MCP is adopted, require a registry, IaC admission, egress enforcement, and continuous discovery.         | NOT_STARTED |
| MCP10       | Context Over-Sharing (conditional)        | HIGH     | If MCP is adopted, enforce context namespaces, minimization, TTL, purge, and isolation tests.               | NOT_STARTED |
| A02         | Security Misconfiguration                 | MEDIUM   | Establish and test production headers, CORS, proxy, debug, documentation, and endpoint baselines.           | NOT_STARTED |
| A09         | Logging and Alerting                      | MEDIUM   | Add structured encoding, injection tests, immutable retention, correlation, and error aggregation.          | NOT_STARTED |
| A10         | Exceptional Conditions                   | MEDIUM   | Add global fallback, cleanup, atomicity or compensation, bounded failure, and exhaustion tests.             | NOT_STARTED |
| ISR10       | Asset Management                          | MEDIUM   | Build continuous asset discovery, IaC reconciliation, ownership, criticality, and retirement proof.         | NOT_STARTED |
| CICD-SEC-7  | System Configuration                     | MEDIUM   | Harden SCM, CI, registry, signing, token, debug, and runner defaults and monitor drift.                     | NOT_STARTED |
| CICD-SEC-8  | Third-Party Services                     | MEDIUM   | Add admission, inventory, permissions, version pinning, expiry, review, and removal controls.               | NOT_STARTED |
| CICD-SEC-10 | Logging and Visibility                   | MEDIUM   | Correlate SCM, approval, workflow, OIDC, runner, registry, signing, and deployment events.                  | NOT_STARTED |
| SBD-02      | Risk-Driven                              | MEDIUM   | Quantify risk appetite and block deployment on unresolved jurisdiction, retention, or evidence authority.  | NOT_STARTED |
| SBD-04      | Supply Chain                             | MEDIUM   | Add vendor admission, AI-code review, deployed-SBOM monitoring, and remediation SLAs.                      | NOT_STARTED |
| SBD-07      | Flexible Architecture                   | MEDIUM   | Support versioned security interfaces, independent upgrade and rollback, crypto agility, and blue/green.   | NOT_STARTED |
| SBD-11      | Secure Deprecation                       | MEDIUM   | Add EOL work packages for data destruction, access cleanup, backup handling, inventory, and proof.          | NOT_STARTED |
| MCP08       | Audit (conditional)                      | MEDIUM   | If MCP is adopted, add tamper-resistant call-level audit, correlation, redaction, retention, and alerts.    | NOT_STARTED |

---

## Appendix: Skills Used

| Skill                 | Framework                                              | Version | Reference                                                                                                                                            |
|-----------------------|--------------------------------------------------------|---------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| owasp-llm             | OWASP Top 10 for LLM Applications (2025)              | 1.0.0   | [OWASP LLM Top 10](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/)                                                         |
| owasp-agentic        | OWASP Top 10 for Agentic Applications (2026)          | 1.0.0   | [OWASP Agentic Top 10](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)                                             |
| owasp-top-10         | OWASP Top 10 for Web Applications (2025)              | 1.0.0   | [OWASP Top 10](https://owasp.org/Top10/2025/)                                                                                                        |
| owasp-infrastructure | OWASP Infrastructure Security Top 10 (2024)           | 1.0.0   | [OWASP Infrastructure Security Risks](https://owasp.org/www-project-top-10-infrastructure-security-risks/)                                           |
| owasp-cicd           | OWASP Top 10 CI/CD Security Risks                      | 1.0.0   | [OWASP CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/)                                                             |
| secure-by-design     | Secure by Design, UK Government and Australian ASD/ACSC | 1.0.0 | [UK Government principles](https://www.security.gov.uk/policy-and-guidance/secure-by-design/principles/); [Australian foundations](https://www.cyber.gov.au/business-government/secure-design/secure-by-design/secure-by-design-foundations) |
| owasp-mcp            | OWASP MCP Top 10                                       | 1.0.0   | [OWASP MCP Top 10](https://owasp.org/www-project-mcp-top-10/)                                                                                        |
