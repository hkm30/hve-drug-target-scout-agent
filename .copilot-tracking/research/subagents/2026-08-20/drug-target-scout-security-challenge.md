---
title: Drug Target Scout 安全规划只读挑战
description: 对安全规划与技术假设研究进行证据驱动的只读安全挑战
author: GitHub Copilot
ms.date: 2026-08-20
ms.topic: security-review
keywords:
  - indirect prompt injection
  - evidence quality
  - high impact decision
  - red teaming
estimated_reading_time: 8
---

## 研究范围

只读审查以下材料，不修改源文件：

* .copilot-tracking/security/2026-08-20/drug-target-scout-security-plan.md
* .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md

重点路径是第三方学术 API 与公开网页返回的标题和摘要进入 LLM，并影响
`GO`、`NO_GO` 或 `NEED_MORE_DATA` 建议。

## 研究问题

* 是否分别定义并验证 Citation existence、内容安全、论断相关性和证据质量
* 是否覆盖 indirect prompt injection、payload splitting、编码和多语言绕过
* 是否覆盖工具越权、输出处理、评测误报与漏报和人工过度依赖
* Prompt Shields 与 Spotlighting 是否被定位为非唯一防线
* 红队测试与上线门禁是否具有可验收条件
* 技术研究事实与安全规划中的架构假设是否一致

## 当前假设

安全规划已正确识别主要攻击路径和分层防御原则，但可能把若干门禁写成
无法直接验证的绝对条件，或没有把证据质量与内容安全落实为独立的确定性状态和
可量化验收标准。

## 发现

### 高：相关性与证据质量只有声明，没有可执行门禁

安全规划准确声明 `EXISTS` 不代表相关、可靠或足以支持立项，也写明未通过相关性或
证据质量门禁的记录不得支撑关键结论。但是，计划没有为这两类门禁定义独立状态、
判定组件、失败语义、阈值或上线验收值。人工审批门禁只明确要求 ID 回查、内容安全
处置、引用片段、主源覆盖和 schema 校验。决策评测也没有测量撤稿识别、研究设计质量、
证据等级或质量门禁的误判率。

这与技术研究的边界一致但没有完成安全闭环。技术研究明确把药理学相关性、撤稿状态、
试验可信度、证据质量和 Go/No-Go 决策质量留给后续独立评测。因此，一条真实、无注入、
可精确引用但与靶点机制弱相关或质量很低的记录，仍可能满足当前显式门禁并影响 `GO`。

最小修正：为每条记录和每条关键论断增加四个正交状态及 reason code：
`existenceStatus`、`contentSafetyStatus`、`claimRelevanceStatus` 和
`evidenceQualityStatus`。定义各自的判定责任、版本、权威数据源、失败关闭规则和最低阈值。
只有四项均满足批准策略的记录才能进入关键论断。把相关性、论断蕴含、撤稿或关注声明、
研究设计质量和证据等级加入 Deterministic Decision Policy Gate、G-02 和发布评测。

### 高：隔离策略可通过选择性移除负面证据改变结论

PI-08 只在“文档攻击被检测且隔离后证据覆盖不足”时强制 `NEED_MORE_DATA`。这允许系统在
隔离一条决策相关的负面主证据后，只要剩余记录数量仍达标，就继续基于偏斜后的证据集
形成 `GO`。同一问题也会由 Prompt Shields 误报触发。查看“被排除记录数量和原因”不能
恢复已经从模型上下文移除的反证，也不能证明剩余样本没有方向性偏差。

最小修正：任何被隔离的主证据或高相关证据，只要可能改变证据方向、冲突状态或建议标签，
都必须在独立安全裁决前强制 `NEED_MORE_DATA`。覆盖门禁应按来源层级、正向和负向方向、
时间与证据等级分层计算，并比较隔离前后的建议敏感性。增加“负面主证据被恶意文本或
误报隔离，但剩余数量仍达标”的回归用例，要求不得输出可签署的 `GO` 或 `NO_GO`。

### 高：逐文档检测和两阶段结构化会遗漏组合载荷并洗白不可信语义

计划把 payload splitting 列入对抗集，但实施控制只明确要求每条外部文本在进入模型前
接受文档攻击检测。跨标题、摘要和多条记录拆分的载荷可能在单条扫描时均为阴性，只有
Evidence Assembler 组合后才形成完整指令。第一阶段 LLM 又直接读取原始不可信文本，
其输出虽然通过 schema 和引用字段校验，仍可能把恶意指令造成的歪曲包装成看似可信的
结构化事实，供第二阶段使用。结构化格式和真实引用片段不能证明事实方向或论断蕴含正确。

最小修正：保留不可信 taint，不得因第一阶段结构化而升级信任。分别在单记录规范化结果、
组装后的完整上下文和最终输出三个边界执行检测与策略检查。引用片段必须由确定性代码验证
为原文的精确子串并记录位置和哈希；关键论断再由独立的论断相关性或蕴含检查验证，检查
分歧时强制 `NEED_MORE_DATA`。对抗测试必须包含同字段拆分、跨记录拆分、跨来源拆分、
编码和中英文混合组合，并在真实 Evidence Assembler 顺序与 token 截断条件下运行。

### 高：红队和上线门禁的“零次成功”没有统计可验收性

G-06 和决策安全评测要求发布攻击集出现 0 次严重成功攻击，但没有定义攻击集规模、各攻击
类别和语言的最小覆盖、隐藏留出集、随机重复次数、模型采样配置、失败裁决规则或置信界限。
一次没有成功的运行即可字面满足门禁。计划只要求持续测量检测器召回率，没有为召回率、
误报率、漏报率或业务级 Attack Success Rate 设发布阈值。

Microsoft 官方资料说明 AI Red Teaming Agent 使用合成分布和生成式评判，结果非确定且可能
误报；部分 agentic 风险为单轮、仅英语，且不支持非 Foundry agent、函数工具和浏览器工具。
Microsoft 也明确指出红队不是系统化测量的替代品。因此，只记录这些限制不能让 G-06
成为可重复的发布门禁。

最小修正：建立版本化覆盖矩阵，至少按来源、攻击类型、编码、多语言、payload splitting、
工具目标和输出影响分层；保留开发集与隐藏发布集；固定端点、提示词、Guardrail 和评判器
版本；对随机模型重复运行。为严重业务级 ASR、检测召回率、良性生物医学语料误报率和
人工裁决后的评判误差设风险负责人批准的阈值与置信上界。若观察到 0 次成功，可使用
95% 上界近似 `3/n` 反推所需样本量，而不是把观测零当作风险为零。自动评判的所有严重
阳性和代表性阴性都需双人裁决，并在生产等价的完整应用路径复测。

### 中：人工签署是被动确认，不能有效控制自动化偏见

计划要求评审人查看不确定性、反对证据和被排除记录，并承认自动化偏见，但“查看”没有
可验证的认知动作。计划没有要求评审人在看到模型标签前形成独立判断，没有定义关键原文
核验比例、注入告警的第二角色裁决、双人审批条件或评审质量阈值。真实 PMID 或 NCT 的
可信外观会放大确认偏见，使人工签署退化为点击门禁。

最小修正：在展示模型建议标签前，要求领域评审人基于证据记录独立的初始判断和理由；
对所有决定性论断确认原文片段、方向和限制。注入告警或证据隔离任务增加独立安全评审，
高影响 `GO` 采用第二领域审批人。记录初始判断、模型建议和最终判断之间的变化，设置
抽样复核、高严重性漏检率和无理由快速确认的上线及持续监控阈值。

## 证据与参考

### 项目证据

* .copilot-tracking/security/2026-08-20/drug-target-scout-security-plan.md:78-88
* .copilot-tracking/security/2026-08-20/drug-target-scout-security-plan.md:328-418
* .copilot-tracking/security/2026-08-20/drug-target-scout-security-plan.md:452-475
* .copilot-tracking/security/2026-08-20/drug-target-scout-security-plan.md:580-616
* .copilot-tracking/security/2026-08-20/drug-target-scout-security-plan.md:681-739
* .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:14-36
* .copilot-tracking/research/2026-08-20/drug-target-scout-technical-assumptions-research.md:621-637

### 外部依据

* [Prompt Shields in Microsoft Foundry](https://learn.microsoft.com/azure/foundry/openai/concepts/content-filter-prompt-shields)
  明确区分用户攻击和文档攻击，承认误报；Spotlighting 是默认关闭、仅 Chat Completions
  可用且增加 token 的预览附加防线
* [AI Red Teaming Agent](https://learn.microsoft.com/azure/foundry/concepts/ai-red-teaming-agent)
  说明合成数据、工具支持、语言和单轮限制，以及生成式 ASR 评判的非确定性和误报风险
* [Planning red teaming for LLMs and their applications](https://learn.microsoft.com/azure/foundry/openai/concepts/red-teaming)
  明确红队用于发现风险面，不能替代系统化测量；要求测试完整应用和生产等价路径
* [OWASP LLM01:2025 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
  明确列出 indirect injection、payload splitting、编码、多语言绕过、最小权限、输出验证和
  高风险动作人工批准

### 已确认覆盖，无需修正

* Prompt Shields 被定位为概率性文档攻击检测层，而不是唯一安全保证
* Spotlighting 被准确标为预览、默认关闭、增加 token 且 API 支持受限的附加层
* MVP 模型零工具权限、确定性输出 schema、安全渲染和规范链接规则覆盖了工具越权与
  improper output handling 的主要路径
* 对抗语料已经列出编码、多语言、payload splitting、引用洗白和合法安全论文误报样本

## 后续问题

本轮原始问题均已回答。以下事项应在实施前由风险负责人给出数值，而不是继续依赖文字性
门禁：

* 每类发布攻击样本量、重复次数、ASR 上界和误报率阈值
* 相关性、论断蕴含和证据质量的领域金标准、评判责任人与最低通过值
* 哪些隔离事件需要安全评审、第二领域审批或直接强制 `NEED_MORE_DATA`