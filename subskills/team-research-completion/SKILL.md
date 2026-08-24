---
name: team-research-completion
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-completion` 时使用。按照输出配置审计核心模块、规定要素、证据和必要表格，并形成完成度门禁；不检查最终文件版式，也不重新研究或改写正文。
---

# 团队研究完成度审计

读取主 Skill 的 `references/output-profile-contracts.json`、任务卡、全部已通过门禁的阶段产物和叙事稿。此阶段只回答研究内容是否完整，不评价 Excel 视觉质量。

1. 根据任务卡中的 `output_profile` 取得唯一核心模块集合，不得增删模块或用自拟章节名称替代。
2. 逐模块核对规定要素、可阅读分析、证据编号、上游阶段产物和必要结构化表格。未披露事项继续保留在规定要素中，并形成明确核验动作。
3. 核对叙事稿的 `covered_module_ids`。每个适用核心模块必须进入一个明确的叙事章节、投资要点或来源与限制区域；不得通过重复复制模块分析制造表面完整。
4. 任何模块缺少规定要素、分析正文、证据回连、必要表格或明确内容归属时，将该模块标记为 `incomplete`，并写入 `blocking_gaps`。
5. 只有模块集合完全一致、全部模块通过且 `blocking_gaps` 为空时，整体状态才能写为 `complete`。

聊天路径在内部逐项完成同一审计，不要求保存文件。Excel 路径从主 Skill 的 `assets/completion-audit.json` 创建 `completion-audit.json`，随后运行 `scripts/validate_artifact_bundle.py` 的完整记录校验。发现缺口时返回产生该内容的上游阶段补齐，完成度审计不得代写研究内容。
