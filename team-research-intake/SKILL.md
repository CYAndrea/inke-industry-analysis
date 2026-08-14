---
name: team-research-intake
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-intake` 时使用。为行业研究建立并校验任务卡、研究边界、核心判断、反证条件和少量必要追问；不负责检索、公司分析或交付制作。
---

# 团队研究启动

从主 Skill 的 `assets/research-brief.json` 创建任务卡。

1. 先检查用户是否提供交付格式。缺少时只询问飞书文档、Word、Excel 或 PDF 四个选项并暂停，不自行选择默认格式。格式确认后，再填写行业、地区、细分边界、截止时间、标的和决策问题，并为有标的与无标的任务填写研究对象类型、技术重要性、公司成熟度和信息完整度。每次研究只建立一个完整交付版本。
2. 有标的公司时，先核验上市状态和融资语境，填写 `capital_market_stage`；上市公司按二级市场处理，未上市投资项目按一级市场处理。
3. 在资本市场阶段确定后，填写 `research_archetype` 与 `technology_materiality`，再根据执行合同生成 `output_profile` 和必需章节。
4. 按执行合同选择研究模式并记录 `mode_rationale`；用户没有标的时使用 `industry_overview`。
5. 只追问会改变结果的缺口，最多三项；用户已提供的信息不得重复询问。
6. 写出可被证据推翻的核心判断与反证条件，并从输出配置写入必覆盖竞争簇、必需章节和交付验收项。
7. 若 `technology_materiality=核心护城河`，把技术路线与工程瓶颈列为必需章节；若为 `非核心` 或 `支持性`，将技术内容限制在产品体验、成本、质量、供应链和合规直接相关的范围。
8. 按主 Skill 的 `references/research-artifact-schema.json` 写入 `schema_version=3` 与 `artifact_type=brief`，运行 `scripts/validate_artifact_bundle.py --brief <文件>`。

输出 `brief.json` 路径、核心判断和待确认项。未通过校验时不得开始正式检索。
