<!-- markdownlint-disable-file -->
# PRD 本地技术假设审计（PubMed / ClinicalTrials / Scholar / 引用回查）

## 研究状态

* 状态: Complete
* 日期: 2026-08-20
* 范围: 仅审计工作区内 PRD 与现有文件，不修改产品文件

## 研究对象与方法

* 目标文档: prd-v0.1.md
* 证据提取方式: 按 1-based 行号逐段审计显式声明、隐含技术假设、验收指标、数据流、约束
* 工作区核验: 全量文件枚举（含隐藏文件）+ 常见原型/配置/测试命名模式检索

## 工作区核验结果（是否存在原型/配置/测试）

### 发现文件

* prd-v0.1.md
* .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md
* .copilot-tracking/research/subagents/2026-08-20/clinicaltrials-api-research.md
* .copilot-tracking/research/subagents/2026-08-20/citation-existence-verification-research.md
* .copilot-tracking/research/subagents/2026-08-20/scholarly-discovery-alternatives-research.md
* .git/*（标准 Git 元文件与 hooks）

### 结论

* 未发现应用原型代码（如 src/app 服务代码）
* 未发现工程配置（如 package.json、pyproject.toml、requirements.txt、Dockerfile、azure.yaml 等）
* 未发现测试文件（如 test/spec/pytest/jest/vitest）
* 当前可审计的产品定义来源仅为 prd-v0.1.md

## 一、PRD 已显式声明内容（按主题）

### A. PubMed E-utilities 相关

* 数据源必选包含 PubMed，且用于科学文献检索与输出结构化字段（标题、摘要、PMID、链接）
  * 证据: prd-v0.1.md:165-167
* 文献 Agent 最低要求支持 PubMed 检索
  * 证据: prd-v0.1.md:215
* 工程建议中明确 PubMed 优先用官方 API / E-utilities
  * 证据: prd-v0.1.md:223
* 搜索接入建议将 PubMed API / E-utilities定义为“主文献证据来源”
  * 证据: prd-v0.1.md:373

### B. ClinicalTrials.gov 相关

* 数据源必选包含 ClinicalTrials.gov，用于临床试验检索并提取阶段、状态、适应症、干预
  * 证据: prd-v0.1.md:168-170
* 临床试验 Agent 最低要求支持 ClinicalTrials.gov 检索
  * 证据: prd-v0.1.md:245
* 明确提取字段包含 NCT 号、阶段、状态、适应症、干预
  * 证据: prd-v0.1.md:246
* 搜索接入建议将 ClinicalTrials.gov API定义为“主临床试验证据来源”
  * 证据: prd-v0.1.md:374

### C. Google Scholar / OpenAlex / Europe PMC 相关

* Google Scholar 是必选数据源，用于补充学术搜索广度
  * 证据: prd-v0.1.md:171-173
* Scholar 检索优先通过搜索代理、第三方搜索 API 或宿主 web search，不建议 DEMO 阶段直接爬虫
  * 证据: prd-v0.1.md:178,224
* 通用搜索主要用于补充综述、公开网页、竞争情报和 Scholar 线索
  * 证据: prd-v0.1.md:185,375
* 可选补充源（本次不建议做）包括 OpenAlex 与 Europe PMC
  * 证据: prd-v0.1.md:188-194

### D. 引用真实性 / PMID / NCT 回查相关

* 输出需要“带引用”且附原文链接
  * 证据: prd-v0.1.md:39
* 文献 Agent 输出应含引用列表与引用链接
  * 证据: prd-v0.1.md:211,219
* 临床试验输出字段显式包含 NCT 号
  * 证据: prd-v0.1.md:246
* 最终输出结构含“引用列表”
  * 证据: prd-v0.1.md:301
* 前端引用区需展示 PubMed / ClinicalTrials / Scholar(Web) 链接
  * 证据: prd-v0.1.md:482-487
* 非功能“可解释性”要求关键结论必须有来源，不能无证据给结论
  * 证据: prd-v0.1.md:510-512
* 成功标准要求结果里有明确引用来源
  * 证据: prd-v0.1.md:552

## 二、从文本推断的隐含技术假设

### A. PubMed / E-utilities

* 假设可通过 PubMed 官方接口稳定获得 PMID + 摘要级证据，足以支持 DEMO 结论生成
  * 依据: prd-v0.1.md:165-167,223,225
* 假设“标题+摘要+元数据”在本期足够，不需全文解析
  * 依据: prd-v0.1.md:225
* 假设检索结果数量受控后仍能维持结论质量
  * 依据: prd-v0.1.md:217,515

### B. ClinicalTrials.gov

* 假设单次检索可提取足够结构化字段形成阶段分布、状态信号与趋势总结
  * 依据: prd-v0.1.md:237-248
* 假设 NCT 可作为临床证据主键，在引用层可追溯
  * 依据: prd-v0.1.md:246,301

### C. Scholar / OpenAlex / Europe PMC

* 假设无需直连 Scholar 页面即可得到可用补充线索（通过 web search/第三方 API）
  * 依据: prd-v0.1.md:178,224
* 假设 OpenAlex/Europe PMC 可延后，不影响 MVP 闭环
  * 依据: prd-v0.1.md:188-194,528-537
* 假设补充层主要提升“覆盖面”而非“主证据权威性”
  * 依据: prd-v0.1.md:177-186

### D. 引用真实性回查

* 假设“有链接+有标识符（PMID/NCT）”可满足可解释性与初步可信性
  * 依据: prd-v0.1.md:39,246,510-512
* 假设 LLM 总结不会显著引入不可追溯或错配引用
  * 依据: prd-v0.1.md:218,248,305,329-333

## 三、尚未定义的实现细节（关键缺口）

### A. PubMed E-utilities

* 未定义具体端点组合（esearch/esummary/efetch）与字段映射规范
  * 相关声明位置: prd-v0.1.md:223,373
* 未定义检索式模板（靶点同义词、疾病布尔逻辑、时间过滤）
  * 相关输入位置: prd-v0.1.md:154-157
* 未定义速率限制、重试、退避、缓存策略
  * 相关稳定性要求: prd-v0.1.md:519-523

### B. ClinicalTrials.gov

* 未定义采用哪个 API 版本与查询语法
  * 相关声明位置: prd-v0.1.md:245,374
* 未定义“积极/失败信号”判定规则（状态映射、终止原因权重）
  * 相关输出位置: prd-v0.1.md:240-241
* 未定义多条试验去重与同一机制聚合口径
  * 相关任务位置: prd-v0.1.md:92-94,237-248

### C. Scholar / OpenAlex / Europe PMC

* 未定义 Scholar 补充层的可接受来源白名单与排序逻辑
  * 相关声明位置: prd-v0.1.md:178,185,224
* 未定义在何种条件下启用 OpenAlex / Europe PMC 替补路径
  * 相关声明位置: prd-v0.1.md:188-194
* 未定义 Scholar/Web 结果与 PubMed 主证据的冲突处理策略
  * 相关汇总位置: prd-v0.1.md:266-268,422-424

### D. 引用真实性 / PMID / NCT 回查

* 未定义回查算法（存在性校验、字段一致性校验、失效链接处理）
  * 相关声明位置: prd-v0.1.md:39,246,510-512
* 未定义验收阈值（例如引用有效率、坏链容忍度、回查失败降级）
  * 相关成功标准位置: prd-v0.1.md:549-555
* 未定义导出报告中的引用标准格式（排序、去重、标识符必填）
  * 相关输出位置: prd-v0.1.md:498-504

## 四、验收指标与约束（与四项技术查证直接相关）

### 显式验收指标

* 结果需在 10 分钟内产出
  * 证据: prd-v0.1.md:551
* 结果需有明确引用来源
  * 证据: prd-v0.1.md:552
* 能体现文献支持与临床信号
  * 证据: prd-v0.1.md:553
* 需给出 Go / No-Go / Need More Data
  * 证据: prd-v0.1.md:554

### 显式约束

* 医学主证据优先官方来源与结构化字段
  * 证据: prd-v0.1.md:177,184
* 不应全部依赖通用 web search
  * 证据: prd-v0.1.md:183
* Scholar 不建议直爬，偏向代理/API/宿主能力
  * 证据: prd-v0.1.md:178,224
* 要支持数据源部分失败并返回部分结果
  * 证据: prd-v0.1.md:521-523
* 成本控制要求只抓前5条，避免无限深研
  * 证据: prd-v0.1.md:515-517

### 发现的潜在冲突（需澄清）

* 文献 Agent 最低要求“前 N 条（10~20）”与非功能“只抓前5条”冲突
  * 证据: prd-v0.1.md:217,515
* 数据源“必选 Google Scholar”与“不可控 web search 时回退第三方 API”之间缺少强一致策略
  * 证据: prd-v0.1.md:171-173,186

## 五、数据流审计（从输入到引用输出）

### 端到端数据流

1. 用户输入靶点、适应症、查询目标
   * 证据: prd-v0.1.md:393-397
2. Orchestrator 解析并进行两轮 Human-in-the-loop 确认
   * 证据: prd-v0.1.md:278-282,399
3. Orchestrator 规划到 PubMed / Scholar / ClinicalTrials / 竞争风险任务
   * 证据: prd-v0.1.md:405-408
4. 各 Sub-Agent 返回统一结构化 JSON（含来源类型、摘要、关键发现、链接、结构化字段、置信度/风险）
   * 证据: prd-v0.1.md:412-420
5. Orchestrator 汇总并生成最终报告
   * 证据: prd-v0.1.md:422-424
6. 前端展示结论、关键证据、引用、建议，并支持导出报告
   * 证据: prd-v0.1.md:428-434,498-504

### 四项技术查证在数据流中的落点

* PubMed E-utilities: Step 3/4 的主文献输入管道
  * 证据: prd-v0.1.md:405,415,531,563
* ClinicalTrials.gov API: Step 3/4 的主临床输入管道
  * 证据: prd-v0.1.md:407,415,532,564
* Scholar/OpenAlex/Europe PMC: Step 3/4 的补充证据管道
  * 证据: prd-v0.1.md:406,533,565,190-194
* PMID/NCT 回查: Step 4 输出规范 + Step 6 引用展示 + 成功标准可解释性
  * 证据: prd-v0.1.md:246,482-487,510-512,552

## 六、会影响“四项技术查证”的问题清单

### 1) PubMed E-utilities 查证前置问题

* PMID 回查是否只要求“存在性”，还是必须校验“靶点/适应症语义匹配”
* 文献抓取上限以 5 条还是 10~20 条为准
* 时间范围过滤是硬过滤（API参数）还是软过滤（后处理）
* 摘要缺失或仅有题录时是否允许进入结论

### 2) ClinicalTrials.gov 查证前置问题

* 采用哪一版 API 与字段模型作为长期契约
* NCT 回查是否要求校验阶段/状态与报告一致
* “失败信号”是否将 Withdrawn/Suspended/Terminated 等等价处理
* 多试验同机制聚合后，是否保留单试验可追溯明细

### 3) Scholar / OpenAlex / Europe PMC 查证前置问题

* Scholar 补充层优先顺序: 宿主 web search vs 第三方 API vs OpenAlex/Europe PMC
* OpenAlex/Europe PMC 是否在 Scholar 信号不足时自动触发
* 补充源是否允许作为“主证据”进入 Go/No-Go 判定
* 补充源链接失效时是否可用元数据替代引用

### 4) 引用真实性（PMID/NCT）查证前置问题

* 引用有效性的定义: 仅标识符存在，还是存在+字段一致+链接可达
* 回查失败时系统行为: 阻断结论、降级为 Need More Data、还是标记低置信度继续
* 导出报告是否必须包含 PMID/NCT 规范字段
* 是否要求记录“回查时间戳/来源端点/回查结果”以便审计复现

## 七、结论摘要

* PRD 对四项技术查证给出了方向性强约束: 主证据优先官方结构化 API，补充层避免直爬，结论必须可引用可解释。
* PRD 仍缺少可执行级契约: API 版本、字段映射、回查算法、失败语义、验收阈值、冲突策略未被定义。
* 在当前工作区中，除 PRD 与研究记录外不存在原型/配置/测试，意味着后续技术查证需要先补齐“规范即实现”的接口与验收定义文档。
