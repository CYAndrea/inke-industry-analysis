---
name: team-research-competition
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-competition` 时使用。建立竞品地图、比较标的公司与主要玩家，并形成投资要点和待验证事项；不负责市场规模测算或成品文件制作。
---

# 团队研究竞品与公司

读取主 Skill 的 `references/evidence-and-company-research.md`、任务卡和已经通过门禁的行业交接包。优先使用行业交接包中的结论与证据编号，不重新开展完整行业研究。

1. 先写用户购买旅程：发现、体验、购买、交付、持续使用与服务。
2. 按任务卡建立二至五个检索簇：直接产品、相邻替代、体验与渠道、内容与软件、持续服务。每个必覆盖簇至少确认两家强相关项目，再按停止规则追加检索。
3. 项目只有共享目标用户、购买预算、使用场景、技术或供应链约束、渠道或转化机制中的两项时才进入比较表；列出类别与可比原因。
4. 连续两次检索没有新增强相关项目时停止该簇。聊天路径保留会影响判断的比较对象、纳入理由和直达链接。Excel 路径按照主 Skill Schema 输出 `competition-map.json`，记录检索词、纳入项目、`searched_but_excluded` 和停止原因；每个纳入项目使用 `evidence_ids` 回连证据台账。
5. 有标的时，以三至五条有标题的投资要点开场，再比较战略、产品、渠道、定价与商业化状态，写清优势、限制、待验证事项与失效信号。
6. 有标的时形成公司交接包，记录公司结论、与行业结论的关系、证据编号、反向证据、判断边界、未决问题和下一阶段重点。只有行业时将公司分析标记为不适用，不创建虚构公司结论。

一级项目初步阶段仅提出少量现实可得的核验动作，不罗列上市公司式指标。聊天路径在内部形成公司交接包或不适用标记；Excel 路径从主 Skill 的 `assets/competition-map.json` 创建 `competition-map.json`，公司任务额外从 `assets/company-analysis.json` 创建 `company-analysis.json`，并运行 `scripts/validate_artifact_bundle.py --company-analysis <company-analysis.json> --ledger <evidence-ledger.json>`。公司任务缺少公司结论、行业关联、反向证据或未决问题时不得进入综合判断阶段。
