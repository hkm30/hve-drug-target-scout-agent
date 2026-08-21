<!-- markdownlint-disable-file -->

# ClinicalTrials.gov API 研究（2026-08-20）

观察时间（UTC）: 2026-08-20T09:15:10Z

## 结论总览
1. 当前主 API 为 v2，base URL 为 `https://clinicaltrials.gov/api/v2`。  
结论标签: 官方规范已验证 + 端点实测已验证
2. 主要研究端点为 `GET /studies` 与 `GET /studies/{nctId}`。  
结论标签: 官方规范已验证 + 端点实测已验证
3. 检索“靶点/药物机制”在 CT.gov API 中本质上是文本/干预相关字段检索（含 InterventionName、InterventionMeshTerm、Keyword、描述字段等），不是独立分子靶点 ontology 查询。  
结论标签: 官方规范已验证 + 条件性/仍是假设（关于“完全不存在任何可等价 target ontology 的隐藏域”，仅能据公开结构与 OpenAPI 断言）
4. `OverallStatus` 与 `Phase` 路径可准确定位；两者为枚举，但在单条 study JSON 中字段可能缺失（例如 `Phase` 对部分研究缺失）。  
结论标签: 官方规范已验证 + 端点实测已验证
5. 分页与字段裁剪约束以 OpenAPI 为准：`pageSize` 默认 10、>1000 会被压到 1000；`pageToken` 来自 `nextPageToken`；`fields` 未指定则返回全字段。  
结论标签: 官方规范已验证 + 端点实测已验证
6. classic 路径 `/api/query/*` 在实测样例为 404；迁移指南明确 legacy 支持路径为 `/api/legacy/*`。  
结论标签: 官方规范已验证 + 端点实测已验证（但“全部 classic 端点均退役”仍需更广覆盖才可绝对化）

## 证据分级标签
- 官方规范已验证
- 端点实测已验证
- 条件性/仍是假设

## 1) 当前 API 主版本、base URL、classic 迁移状态

### 1.1 v2 与 base URL
- 官方页面 `https://clinicaltrials.gov/data-api/api` 明确 REST 端点组（`GET /studies`, `GET /studies/{nctId}` 等）与 OpenAPI 规范地址 `https://clinicaltrials.gov/api/oas/v2`。  
	结论标签: 官方规范已验证
- OpenAPI 原文 `ctgov-oas-v2.yaml` 顶部 `servers.url` 为 `https://clinicaltrials.gov/api/v2`。  
	证据文件: .copilot-tracking/research/subagents/2026-08-20/ctgov-oas-v2.yaml  
	结论标签: 官方规范已验证
- `GET https://clinicaltrials.gov/api/v2/version` 实测返回:
	- `apiVersion: "2.0.5"`
	- `dataTimestamp: "2026-08-19T09:00:06"`
	证据文件: .copilot-tracking/research/subagents/2026-08-20/version.json  
	结论标签: 端点实测已验证

### 1.2 classic / legacy 状态
- 迁移指南 `https://clinicaltrials.gov/data-api/about-api/api-migration` 明确:
	- classic 路径: `/api/info/*`, `/api/query/*`
	- 新 API 路径: `/api/v2/*`
	- legacy 支持路径: `/api/legacy/*`
	结论标签: 官方规范已验证
- 实测:
	- classic 示例 `GET /api/query/study_fields?...` 返回 HTTP 404。
		- 证据文件: .copilot-tracking/research/subagents/2026-08-20/classic-study-fields.headers
		- 证据文件: .copilot-tracking/research/subagents/2026-08-20/classic-study-fields.body
	- legacy 示例 `GET /api/legacy/study-fields?...` 返回 HTTP 200（XML）。
		- 证据文件: .copilot-tracking/research/subagents/2026-08-20/legacy-study-fields.headers
		- 证据文件: .copilot-tracking/research/subagents/2026-08-20/legacy-study-fields.body
	结论标签: 端点实测已验证

## 2) `GET /studies` 与单条 NCT 端点

- 列表检索: `GET https://clinicaltrials.gov/api/v2/studies`
- 单条记录: `GET https://clinicaltrials.gov/api/v2/studies/{nctId}`
- 单条记录说明（OpenAPI）: 若 `nctId` 命中 `NCTIdAlias`，可返回 HTTP 301 到实际 NCT。

结论标签: 官方规范已验证

实测单条记录（已知 NCT）:
- 请求: `GET https://clinicaltrials.gov/api/v2/studies/NCT04280705?fields=NCTId,OverallStatus,Phase,InterventionName&format=json`
- 响应摘录:
	- `protocolSection.identificationModule.nctId = "NCT04280705"`
	- `protocolSection.statusModule.overallStatus = "COMPLETED"`
	- `protocolSection.designModule.phases = ["PHASE3"]`
	- `protocolSection.armsInterventionsModule.interventions[*].name = "Placebo", "Remdesivir"`
- 证据文件: .copilot-tracking/research/subagents/2026-08-20/study-nct04280705.json

结论标签: 端点实测已验证

## 3) 靶点/干预检索参数与高级查询

### 3.1 参数语义（v2）
来自 OpenAPI `ctgov-oas-v2.yaml`:
- `query.cond`: Conditions or disease（ConditionSearch）
- `query.term`: Other terms（BasicSearch）
- `query.intr`: Intervention / treatment（InterventionSearch）
- `filter.overallStatus`: 状态过滤（数组，pipe 或 comma）
- `filter.geo`, `filter.ids`, `filter.advanced`, `filter.synonyms`
- `postFilter.*` 同类参数（当前无聚合时与 `filter.*` 等效）

结论标签: 官方规范已验证

### 3.2 高级查询语法
- `query.*` 使用 Essie 表达式语法；官方说明在:
	- `https://clinicaltrials.gov/find-studies/constructing-complex-search-queries`
- 支持 `AREA[...]`, `SEARCH[...]`, `RANGE[...]`, Boolean 等。
- API 页面注明：`COVERAGE` 与 `EXPANSION` 在 modernized CT.gov 上“not fully implemented”。

结论标签: 官方规范已验证

### 3.3 是否存在独立“分子靶点”结构化字段
- 在 Study Data Structure 与 OpenAPI 中可见干预相关结构化字段主要为:
	- `InterventionName`
	- `InterventionOtherName`
	- `InterventionType`
	- `InterventionMeshTerm`
	- `InterventionAncestorTerm`
	- 干预描述/标题/关键字等文本
- 未发现独立的 target ontology 字段（例如“molecular target id / gene target id / protein target ontology id”类型字段）。

因此: 在 ClinicalTrials.gov 里查“药物靶点名”通常是通过 `query.intr` / `query.term` / `filter.advanced(AREA[...])` 对干预名、MeSH、文本字段做检索，不是真正“靶点本体库”查询。

结论标签: 官方规范已验证 + 条件性/仍是假设

## 4) 试验阶段与总体状态的 JSON 路径、枚举、缺失可能

### 4.1 准确路径
- 总体状态: `protocolSection.statusModule.overallStatus`
- 试验阶段: `protocolSection.designModule.phases`（数组）

来源: Study Data Structure + OpenAPI Schema。  
结论标签: 官方规范已验证

### 4.2 枚举
- `Status`:
	- `ACTIVE_NOT_RECRUITING`, `COMPLETED`, `ENROLLING_BY_INVITATION`, `NOT_YET_RECRUITING`, `RECRUITING`, `SUSPENDED`, `TERMINATED`, `WITHDRAWN`, `AVAILABLE`, `NO_LONGER_AVAILABLE`, `TEMPORARILY_NOT_AVAILABLE`, `APPROVED_FOR_MARKETING`, `WITHHELD`, `UNKNOWN`
- `Phase`:
	- `NA`, `EARLY_PHASE1`, `PHASE1`, `PHASE2`, `PHASE3`, `PHASE4`

来源: OpenAPI components schemas。  
结论标签: 官方规范已验证

### 4.3 缺失可能性
- OpenAPI 的 `Study` / `StatusModule` / `DesignModule` 未声明 `overallStatus` 或 `phases` 为 required 字段。
- 实测 observational 样例中 `studyType` 存在但 `phases` 缺失:
	- 请求: `GET /api/v2/studies?query.term=AREA[StudyType]OBSERVATIONAL&pageSize=1&fields=NCTId,StudyType,Phase,OverallStatus&format=json`
	- 响应摘录: `designModule.studyType = "OBSERVATIONAL"`，未出现 `designModule.phases`
	- 证据文件: .copilot-tracking/research/subagents/2026-08-20/observational-phase-check.json

结论标签: 端点实测已验证

## 5) `pageSize` / `pageToken` / `format` / `fields` 约束

### 5.1 `GET /studies`
- `format`: `csv|json`，默认 `json`
- `fields`:
	- 不指定 -> 返回所有字段
	- 指定时必须非空列表（`minItems: 1`）
- `pageSize`:
	- `minimum: 0`，`default: 10`
	- 描述明确：若 >1000 会被强制压到 1000
- `pageToken`:
	- 使用上页 `nextPageToken` 取下一页
- `countTotal`:
	- 首页面可返回 `totalCount`（JSON）或 `x-total-count`（CSV）
- 续页请求必须与首页参数保持一致（除 `countTotal/pageSize/pageToken`）

结论标签: 官方规范已验证

### 5.2 `GET /studies/{nctId}`
- `format` 支持: `csv|json|json.zip|fhir.json|ris`（默认 `json`）
- `fields` 对 `json/json.zip` 可裁剪；`fhir.json` 要求不指定 `fields`

结论标签: 官方规范已验证

### 5.3 分页实测
- 第 1 页请求（`pageSize=1`）返回 `nextPageToken`
- 第 2 页使用该 token 成功返回下一条 study
- 证据文件:
	- .copilot-tracking/research/subagents/2026-08-20/search-page1.json
	- .copilot-tracking/research/subagents/2026-08-20/search-page2.json

结论标签: 端点实测已验证

## 6) 最小只读验证日志（URL/命令/摘录）

### 6.1 API 版本
- URL: `https://clinicaltrials.gov/api/v2/version`
- 命令:
	- `curl -sS 'https://clinicaltrials.gov/api/v2/version'`
- 响应摘录:
	- `{ "apiVersion": "2.0.5", "dataTimestamp": "2026-08-19T09:00:06" }`
- 证据文件: .copilot-tracking/research/subagents/2026-08-20/version.json

### 6.2 已知 NCT 单条记录
- URL: `https://clinicaltrials.gov/api/v2/studies/NCT04280705?fields=NCTId,OverallStatus,Phase,InterventionName&format=json`
- 命令:
	- `curl -sS 'https://clinicaltrials.gov/api/v2/studies/NCT04280705?fields=NCTId,OverallStatus,Phase,InterventionName&format=json'`
- 响应摘录:
	- `overallStatus: "COMPLETED"`
	- `phases: ["PHASE3"]`

### 6.3 检索请求（干预+疾病）
- URL: `https://clinicaltrials.gov/api/v2/studies?query.intr=imatinib&query.cond=leukemia&pageSize=1&fields=NCTId,InterventionName,OverallStatus,Phase&format=json`
- 命令:
	- `curl -sS 'https://clinicaltrials.gov/api/v2/studies?query.intr=imatinib&query.cond=leukemia&pageSize=1&fields=NCTId,InterventionName,OverallStatus,Phase&format=json'`
- 响应摘录:
	- `studies[0].protocolSection.identificationModule.nctId: "NCT04006847"`
	- `nextPageToken: "..."`

### 6.4 高级查询 + filter.overallStatus
- URL: `https://clinicaltrials.gov/api/v2/studies?query.term=AREA%5BInterventionName%5Dimatinib%20AND%20AREA%5BCondition%5Dleukemia&filter.overallStatus=RECRUITING&pageSize=1&fields=NCTId,OverallStatus,InterventionName,Condition&format=json`
- 命令:
	- `curl -sS 'https://clinicaltrials.gov/api/v2/studies?query.term=AREA%5BInterventionName%5Dimatinib%20AND%20AREA%5BCondition%5Dleukemia&filter.overallStatus=RECRUITING&pageSize=1&fields=NCTId,OverallStatus,InterventionName,Condition&format=json'`
- 响应摘录:
	- `overallStatus: "RECRUITING"`
	- 干预列表含 `Imatinib`
- 证据文件: .copilot-tracking/research/subagents/2026-08-20/search-advanced-filter.json

### 6.5 classic/legacy 探针
- classic URL: `https://clinicaltrials.gov/api/query/study_fields?expr=NCT04280705&fields=NCTId,OverallStatus,Phase&min_rnk=1&max_rnk=1&fmt=json`
	- 结果: HTTP 404
- legacy URL: `https://clinicaltrials.gov/api/legacy/study-fields?expr=NCT04280705&fields=NCTId,OverallStatus,Phase&min_rnk=1&max_rnk=1&fmt=xml`
	- 结果: HTTP 200 + XML 返回 `NCTId/OverallStatus/Phase`

## 回答用户 6 个重点（逐条）
1. 主版本与 base URL: v2 / `https://clinicaltrials.gov/api/v2`；classic API 已迁移为 legacy 支持层（实测 classic 样例 404，legacy 可用）。
2. 端点: `GET /studies` 与 `GET /studies/{nctId}`。
3. 靶点与干预检索:
	 - 参数使用 `query.intr`、`query.term`、`query.cond`、`filter.*`、`filter.advanced`（Essie 语法）
	 - 无独立“分子靶点”结构化字段；属于文本/干预字段检索范畴。
4. 路径:
	 - 阶段: `protocolSection.designModule.phases`
	 - 总体状态: `protocolSection.statusModule.overallStatus`
	 - 枚举见 OpenAPI；字段可缺失（`phases` 已实测缺失样例）。
5. 约束:
	 - `pageSize` 默认 10，>1000 强制为 1000
	 - `pageToken` 使用 `nextPageToken`
	 - `format` 与 `fields` 规则按 `/studies` 与 `/studies/{nctId}` 各自定义。
6. 实测:
	 - 已完成 1 条已知 NCT、1 条检索请求、1 条字段缺失/路径验证，并记录 URL/命令/响应摘录与观察时间。

## 仍需谨慎的点
- “classic API 完全退役”若要下绝对结论，建议再抽样 `/api/info/*` 与更多 `/api/query/*` 端点；当前仅对 `/api/query/study_fields` 样例做了 404 实测。

结论标签: 条件性/仍是假设
