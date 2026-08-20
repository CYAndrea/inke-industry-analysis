---
name: team-research-delivery
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-delivery` 时使用。将已完成的行业研究以聊天回复或 Excel 工作簿交付，并完成相应的来源、版式和视觉检查；不补做基础检索或替代质量验收。
---

# 团队研究交付制作

读取主 Skill 的 `references/deliverable-specs.md`。聊天路径只读取已经完成的研究叙事；Excel 路径额外读取 `references/visualization-system.md`、`references/excel-design-system.md`、`assets/excel-style.json`、`assets/excel-build-config.json` 和已经通过校验的 `narrative-draft.json`。缺少叙事稿时返回叙事编辑阶段。交付阶段不得重新检索、改写中心判断或加入叙事稿之外的新结论。

- 聊天：先给核心判断，再给依据、风险和待核验项；关键数字和结论附直达链接。只有横向比较明显提高理解效率时使用 Markdown 表格。
- Excel：加载工作区依赖，将返回的 Node packages 路径写入配置文件的 `node_modules_path`。复制 `assets/excel-build-config.json` 并调用 `scripts/build_research_excel.mjs --config <配置文件>`。样式文件默认由生成器从 Skill 根目录解析，无需填写个人路径。项目需要特殊数据图时，在叙事稿 `visualizations` 中提供底层数据、图形类型和 `evidence_ids`。

聊天路径直接输出最终回复。Excel 路径输出成品路径和符合 Schema 的 `delivery-check.json`；每项可视化记录工作表、图形类型、证据编号、底层数据范围、来源链接、验收状态和限制条件。
