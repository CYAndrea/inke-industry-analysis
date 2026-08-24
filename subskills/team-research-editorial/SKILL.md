---
name: team-research-editorial
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-editorial` 时使用。按照综合判断蓝图把研究改写为读者版咨询叙事，并保留页面、模块和证据归属；不补做检索、改变判断或制作最终文件。
---

# 团队研究叙事编辑

读取主 Skill 的 `references/consulting-narrative.md`、已经通过门禁的综合判断交接包和输出配置。仅在核对引用时按证据编号读取证据台账，不重新读取完整行业与公司研究材料。聊天路径形成可回复正文；Excel 路径输出 `narrative-draft.json`。

1. 先确认中心论点和论证顺序，再严格按照 `section_blueprint` 写各章节。不得从工作表、列标题或展示组件开始组织内容。
2. 每个章节保留蓝图中的 `reader_page_id`、`covered_module_ids` 和 `evidence_ids`。不得自行移动章节、重复分配模块或将证据交给不相关页面。
3. 每个章节只回答一个中心问题，使用结论式标题，并自然完成结论、形成机制、关键证据、投资含义和判断边界。段落数量由论证需要决定，不为满足固定段数填充文字；完整章节至少包含两个相互衔接的段落。
4. 每个段落至少新增一项信息：机制解释、证据解读、反向证据、决策含义或判断边界。删除重复转述、模块清单和只改变措辞的段落。
5. 模块审计内容通过 `covered_module_ids` 进入叙事。不得把完成审计中的 `analysis` 原文再次复制到正文。结构化表格只保留横向比较信息，并在 `table_justification` 中说明其阅读价值。
6. 删除内部标签、字段名和分析脚手架。“洞察”“驱动因素”“建议”“优势”“风险”等词不得作为重复出现的读者版板块标签或表头。项目符号只用于投资要点、参数、融资事件、来源和跟踪清单。
7. 将数字嵌入论证。章节、投资要点和可视化计划使用 `evidence_ids` 回连来源台账，不复制网址和来源字段。事实、估算、推演与待核验事项保持可识别边界。
8. 聊天路径人工核对中心论点、来源链接、判断边界和待核验项。Excel 路径先运行 `scripts/validate_artifact_bundle.py --narrative <narrative-draft.json> --synthesis-source <analysis-synthesis.json> --ledger <evidence-ledger.json>`，再运行 `scripts/validate_narrative_contract.py --input <narrative-draft.json>` 与 `scripts/validate_content_contract.py --input <narrative-draft.json>`。未通过时继续编辑。
9. 叙事稿只能使用综合判断交接包已纳入的中心判断、关键结论、页面归属、模块归属和证据编号。需要新增研究结论或关键证据时返回综合判断阶段。

输出中心论点、章节顺序、读者版正文、模块覆盖关系、数据依据、必要表格说明和编辑检查结果。
