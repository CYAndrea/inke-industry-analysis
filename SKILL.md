---
name: team-industry-research
description: 当用户明确提到“行业研究”“行业分析”“行研”“赛道研究”“公司研究”“竞品研究”“项目筛选”或“映客”，或者使用“研究、调研、分析、筛选”并同时提供行业、公司、投资、竞品或交付格式信息时，使用团队方法完成中文行业研究、公司投资研究和项目筛选，并交付飞书文档、Word、Excel 或 PDF。单一事实查询、短摘要和纯文字润色不触发完整流程。
---

# 团队行业研究

本 Skill 负责研究编排与最终门禁。先读取 `references/execution-contracts.md` 与 `references/research-artifact-schema.json`，按任务卡选择研究模式并建立阶段产物。所有阶段产物统一使用 `schema_version=3`，字段不得自行改名或重复保存来源台账。

| 阶段 | 内置阶段模块 | 产出 |
| --- | --- | --- |
| 启动 | `subskills/team-research-intake/SKILL.md` | `brief.json`、研究模式、核心判断、反证条件 |
| 证据与市场 | `subskills/team-research-evidence/SKILL.md` | `evidence-ledger.json`、市场与技术分析 |
| 竞品与公司 | `subskills/team-research-competition/SKILL.md` | `competition-map.json`、投资要点、标的比较 |
| 叙事编辑 | `subskills/team-research-editorial/SKILL.md` | `narrative-draft.json`、中心论点与读者版正文 |
| 交付制作 | `subskills/team-research-delivery/SKILL.md` | 成品文件、`delivery-check.json` |
| 质量验收 | `subskills/team-research-quality/SKILL.md` | `research-record.json`、修订清单与通过结果 |

按顺序读取并执行 `subskills/` 下的阶段模块。它们随主 Skill 一起安装，不要求用户额外安装六个并列目录；只有用户明确需要独立调用某一阶段时，才将对应模块另行封装为独立 Skill。启动时先确认交付格式；用户未指定格式时，只询问交付为飞书文档、Word、Excel 还是 PDF，并暂停后续研究。每次研究只交付一个完整版本，不设置快速版与完整版。任务卡未通过校验时不开始正式检索；交付制作前必须完成证据、竞品或公司分析与叙事编辑；叙事稿未通过合同校验时不得开始制作成品；交付前运行 `scripts/validate_artifact_bundle.py --record <research-record.json>`，对账失败时不得交付。

主 Skill 资源按需读取：`references/research-blueprint.md` 用于研究结构，`references/output-profiles.md` 用于输出路由，`references/evidence-and-company-research.md` 用于证据与公司信息路由，`references/consulting-narrative.md` 用于读者版叙事，`references/semantic-quality.md` 用于语义验收，`references/deliverable-specs.md` 用于交付，`references/visualization-system.md` 用于图表、技术图和外部素材决策，`references/quality-gates.md` 用于质量门禁。Excel 使用 `assets/excel-style.json` 与 `scripts/build_research_excel.mjs`，不得为常规研究重新编写整套格式系统。

## 固定约束

- 事实、估算、推演与待核验事项分开表达。
- 有标的公司时先判断一级或二级市场，再判断研究对象类型与技术重要性，最后生成输出配置；不得先套用行业模板。
- 先判断研究对象类型与技术重要性，再决定技术栈的篇幅和深度；不要把面向消费者的产品自动归入混合型，也不要因消费属性削弱核心技术分析。
- 公司研究以三至五个有标题的“投资要点”开场。
- 成品报告以连贯咨询叙事为主体。分析标签、内部字段、检索步骤和项目符号不得替代读者版正文；数据表只承载横向比较信息。
- 竞品比较写明类别与可比原因，并覆盖用户购买旅程中的非制造商角色。
- 一级投资初步阶段只保留三至六个现实可得的核验动作。
- 不输出综合打分、伪精确评分或无来源估值结论。
- 关键数字与结论保留完整直达链接。
- 正文、投资要点、竞品和图表仅通过 `evidence_ids` 引用 `evidence-ledger.json`；`research-record.json` 不复制来源台账。
- 每个关键市场趋势、技术结构、产业链关系、竞争定位或商业闭环至少评估一次可视化价值。精确数据使用可追溯的原生图表；技术与硬件关系使用经过术语和连接校验的示意图；真实产品优先官方素材；外部报告图用于口径发现和重绘参考。
- 图片生成模型不得生成需要精确核验的市场数字、坐标、参数和复杂中文标签。生成式图片只承担结构、场景和物理形态表达，精确文字与数字在交付工具中叠加。
- 优先使用团队日常研究语言。消费品研究默认写“终端销售表现”“实际销售进度”“渠道出货与终端消化”“门店销售反馈”等具体表述，不将“动销”作为默认术语；仅在来源原文、客户访谈或数据口径明确使用“动销”时保留，并说明其定义与统计范围。
- Excel、飞书、Word 与 PDF 遵循各自交付规范并完成视觉核验。
- 团队经验仅在用户确认后写入日志。
- 缺少阶段必交产物时，停留在当前阶段并补齐，不以成文报告替代证据台账或竞品覆盖。
