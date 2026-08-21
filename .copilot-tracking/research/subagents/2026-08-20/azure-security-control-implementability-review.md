---
title: Azure 安全控制可实施性只读审查研究
description: 对 Drug Target Scout 安全规划中的 Azure 身份、网络、日志和供应链控制进行官方文档证据核查
author: GitHub Copilot
ms.date: 2026-08-20
ms.topic: research
---

## 研究范围

严格只读审查 `.copilot-tracking/security/2026-08-20/drug-target-scout-security-plan.md`，不修改被审查文件。

## 研究问题

* Azure Container Apps 内置 Microsoft Entra 身份认证与应用业务授权的边界是否准确且可执行
* 内部或外部 ingress、Private Endpoint、关闭公网、Workload Profiles、VNet、UDR 和 Azure Firewall 出站组合是否写明必要前置条件
* Container Apps 托管身份访问 Microsoft Foundry、Key Vault、ACR 和监控是否具备明确的数据面角色与实现边界
* 诊断日志与不可篡改审计是否被正确区分
* 镜像扫描、SBOM、签名和部署前阻断是否具有明确执行点

## 审查门槛

只保留可由截至 2026-08-20 的官方 Microsoft Learn 证实、置信度不低于 8/10 的设计缺口。待定平台选型本身不作为缺陷。

## 证据记录

待补充。

## 候选发现

待补充。

## 未决澄清问题

无。
