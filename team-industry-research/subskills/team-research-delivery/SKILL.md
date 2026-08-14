---
name: team-research-delivery
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-delivery` 时使用。将已完成的行业研究内容制作成飞书文档、Word、Excel 或 PDF，并完成相应的版式和视觉检查；不补做基础检索或替代质量验收。
---

# 团队研究交付制作

读取主 Skill 的 `references/deliverable-specs.md`、`references/visualization-system.md` 和已经通过校验的 `narrative-draft.json`。Excel 额外读取 `references/excel-design-system.md`、`assets/excel-style.json` 与 `assets/excel-build-config.json`。缺少叙事稿时暂停制作并返回叙事编辑阶段。

- 飞书：使用可用的飞书 CLI；关键趋势、关系、路线、定位和时间线选用图表、关系图或表格，并标注口径与来源。
- Word 与 PDF：使用结论在前的章节结构；PDF 在交付前完成页面渲染核验。
- Excel：先加载工作区依赖，将返回的 Node packages 路径写入配置文件的 `node_modules_path`。复制 `assets/excel-build-config.json` 并调用 `scripts/build_research_excel.mjs --config <配置文件>`。生成器负责统一字号、低饱和配色、横向标题、正文长文本区、来源台账、跟踪清单、实际使用区域和逐页渲染。项目需要特殊数据图时，在叙事稿 `visualizations` 中提供底层数据、图形类型和 `evidence_ids`，不要重新建立整套样式。技术、竞争与投资判断不得直接转成字段大表。

输出成品路径和符合 Schema 的 `delivery-check.json`。每项可视化记录工作表、图形类型、证据编号、底层数据范围、来源链接、验收状态和限制条件。
