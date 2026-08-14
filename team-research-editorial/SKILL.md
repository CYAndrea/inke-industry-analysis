---
name: team-research-editorial
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-editorial` 时使用。把已完成的证据、市场、竞品和公司分析改写为连贯的中文咨询叙事稿，隐藏分析脚手架，并为飞书、Word、Excel 或 PDF 交付提供读者版正文；不补做基础检索或制作最终文件。
---

# 团队研究叙事编辑

读取主 Skill 的 `references/consulting-narrative.md`。输入任务卡、证据台账、竞品地图和投资判断，输出 `narrative-draft.json`。

1. 先写整份报告的中心论点和论证顺序，再写各章节正文。不要从工作表、列标题或展示组件开始组织内容。
2. 每个章节只回答一个中心问题，使用结论式标题，并按“结论 → 形成机制 → 关键证据 → 投资含义 → 判断边界”推进。
3. 每个章节形成二至四个相互衔接的完整段落。段落开头承接前文，段落结尾引向下一层判断。
4. 删除内部标签、项目符号和字段名。“洞察”“驱动因素”“建议”“优势”“风险”等词不得作为读者版板块标签或表头。
5. 只有横向比较会显著提高理解效率时才保留表格，并在 `table_justification` 中说明原因。技术路线、工程瓶颈、行业观点和投资判断默认写成正文。
6. 将数字嵌入论证，段落下方另设轻量数据依据；章节、投资要点和可视化计划使用 `evidence_ids` 回连来源台账，不复制网址和来源字段。
7. 运行主 Skill 的 `scripts/validate_narrative_contract.py --input <narrative-draft.json>`。未通过时继续编辑，不进入交付制作。

输出中心论点、章节顺序、读者版正文、数据依据、必要表格说明和编辑检查结果。
