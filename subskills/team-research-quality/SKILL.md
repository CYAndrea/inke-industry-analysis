---
name: team-research-quality
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-quality` 时使用。检查行业研究的边界、证据、投资判断、竞品覆盖和交付质量，并校验研究记录；不重新撰写整份研究。
---

# 团队研究质量验收

读取主 Skill 的 `references/quality-gates.md`，按阻断、重大、一般、轻微缺陷分类问题。

1. 检查研究边界、研究对象、全球上市状态、资本市场阶段、行业方向、公司成熟度、信息可得性和输出配置是否一致。只有行业时路由必须在第二级结束；具体公司必须完成“全球上市状态与一级或二级市场 → 消费、科技或消费科技融合方向 → 公司研究”的三级判断。融合方向必须同时存在消费、科技和二者商业连接的分析。
2. 检查来源、数字口径、事实与推演边界，以及直达链接完整性。
3. 检查投资要点是否具有证据、失效条件和验证动作；检查竞品类别和非制造商角色覆盖；一级项目指标是否现实可得。硬科技工程瓶颈必须写清具体问题、形成原因、当前解决状态和投资影响，不能用关键词串替代分析。
4. 检查阶段门禁和职责分离。行业交接包必须先于公司分析，公司任务必须形成公司交接包，综合判断必须处理冲突和失效条件，叙事稿不得引入综合判断之外的新证据，交付阶段不得新增研究内容。
5. 聊天路径检查核心判断、直达链接、事实与推演边界以及待核验项。Excel 路径检查版式、可视化和可读性；市场数据图必须追溯到底层数据和直达链接。
6. Excel 路径检查 `brief.json`、`evidence-ledger.json`、`industry-analysis.json`、适用时的 `company-analysis.json`、`competition-map.json`、`analysis-synthesis.json`、`narrative-draft.json`、`delivery-check.json` 是否齐备并使用 Schema v3；填写 `research-record.json`，运行 `scripts/validate_artifact_bundle.py --record <文件>`。聊天路径不要求建立上述文件。

阻断或重大缺陷未修复时不得交付。聊天路径直接修订回复；Excel 路径输出修订清单、通过项和剩余限制条件。
