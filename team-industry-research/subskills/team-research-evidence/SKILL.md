---
name: team-research-evidence
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-evidence` 时使用。建立行业研究的来源台账，完成行业定义、技术栈、产业链、供需和市场证据分析；不制作最终交付物或独立给出投资结论。
---

# 团队研究证据与市场

读取主 Skill 的 `references/research-blueprint.md` 与 `references/evidence-and-company-research.md`。

1. 先定义行业、细分环节、地区与时间口径。
2. 从主 Skill 的 `assets/evidence-ledger.json` 建立 `evidence-ledger.json`。字段固定使用 `id`、`claim`、`evidence_type`、`tier`、`source_name`、`source_title`、`published_at`、`url`、`geography`、`period`、`unit`、`scope`、`calculation`、`usage`、`limitations`、`source_role` 和 `independence`，不得创建同义字段。`source_role` 区分原始披露、公司自述、监管或交易所、媒体转述、数据库和模型推演；`independence` 标明是否存在独立交叉验证。
3. 解释行业概念；技术行业逐层分析路线、取舍、工程瓶颈与投资意义。
4. 分别分析供给、需求、产业链与价值分配；无标的时完成总体和细分 Market Overview。
5. 为市场数字标明地区、期间、单位、事实或预测属性；测算另列公式、输入和敏感项。总市场、细分市场、平台监测与公司数据不得混用。

市场关键数字至少保留一条 A 级或可复现来源；第三方测算必须明确标注。发生来源冲突时保留冲突表，不强行合并为单一数字。技术层级按执行合同六字段展开，每层至少一段完整论述。

精确财务、政策和市场数据优先使用原始披露与可复现来源；一级项目与竞争动态可使用指定高质量媒体。输出来源台账、行业证据摘要和跟踪清单。每项关键判断至少保留一条支撑证据，并说明证据不足时需要补充的材料类型。
