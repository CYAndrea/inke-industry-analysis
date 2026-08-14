---
name: team-research-quality
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-quality` 时使用。检查行业研究的边界、证据、投资判断、竞品覆盖和交付质量，并校验研究记录；不重新撰写整份研究。
---

# 团队研究质量验收

读取主 Skill 的 `references/quality-gates.md`，按阻断、重大、一般、轻微缺陷分类问题。

1. 检查研究边界、资本市场身份、研究对象类型、技术重要性、公司成熟度、信息可得性和输出配置是否一致；有标的公司必须先完成“一级／二级 → 对象类型 → 技术重要性 → 公司成熟度与信息可得性 → 输出配置”的决策链。
2. 检查来源、数字口径、事实与推演边界，以及直达链接完整性。
3. 检查投资要点是否具有证据、失效条件和验证动作；检查竞品类别和非制造商角色覆盖；一级项目指标是否现实可得。硬科技工程瓶颈必须写清具体问题、形成原因、当前解决状态和投资影响，不能用关键词串替代分析。
4. 按交付格式检查版式、可视化和可读性。市场数据图必须追溯到底层数据和直达链接；技术图必须核对层级、术语、连接方向和精确参数；外部图片必须保留出处；生成式图片不得承担精确数字证明。
5. 检查 `brief.json`、`evidence-ledger.json`、`competition-map.json`、`narrative-draft.json`、`delivery-check.json` 是否齐备并使用 Schema v3；检查来源等级、口径、反证、竞品覆盖和交付渲染。填写主 Skill 的 `assets/research-record.json`，不复制来源台账。运行 `scripts/validate_artifact_bundle.py --record <文件>`，确认正文、投资要点、竞品、图表和研究结论的 `evidence_ids` 均存在且来源统计一致。

阻断或重大缺陷未修复时不得交付。输出修订清单、通过项和剩余限制条件。
