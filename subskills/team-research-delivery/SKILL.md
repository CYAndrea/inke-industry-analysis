---
name: team-research-delivery
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-delivery` 时使用。将已完成的行业研究以聊天回复或 Excel 工作簿交付，并完成相应的来源、版式和视觉检查；不补做基础检索或替代质量验收。
---

# 团队研究交付制作

读取主 Skill 的 `references/deliverable-specs.md`。聊天路径只读取已经完成的研究叙事；Excel 路径额外读取 `references/visualization-system.md`、`references/excel-design-system.md`、`assets/excel-style.json`、`assets/excel-build-config.json`、已经通过校验的 `narrative-draft.json` 和 `completion-audit.json`。缺少叙事稿或模块完成审计未通过时返回对应阶段。交付阶段不得重新检索、改写中心判断或加入审计之外的新结论。

- 聊天：先给核心判断，再给依据、风险和待核验项；关键数字和结论附直达链接。只有横向比较明显提高理解效率时使用 Markdown 表格。
- Excel：加载工作区依赖，将返回的 Node packages 路径写入配置文件的 `node_modules_path`。复制 `assets/excel-build-config.json`，填写叙事稿、证据台账、行业分析、适用时的公司分析、竞争地图、综合判断和模块完成审计路径，再调用 `scripts/build_research_excel.mjs --config <配置文件>`。生成器会在制作工作簿前核对模块集合、规定要素、必要表格及证据与上游产物的关系，然后依据每个章节的 `reader_page_id` 写入最多八个读者页面。八页只负责组织阅读顺序，叙事稿全部章节、结构化表格、反向证据和判断边界均须完整写入。已经由叙事覆盖的模块不重复写入审计正文，没有叙事覆盖的摘要与来源模块继续保留分析。模块完成审计继续保留全部核心模块，读者版不生成逐模块独立工作表。样式文件默认由生成器从 Skill 根目录解析，无需填写个人路径。项目需要特殊数据图时，在叙事稿 `visualizations` 中提供底层数据、图形类型和 `evidence_ids`。

聊天路径直接输出最终回复。Excel 路径输出成品路径和符合 Schema 的 `delivery-check.json`；每项可视化记录工作表、图形类型、证据编号、底层数据范围、来源链接、验收状态和限制条件。`module_locations` 与 `narrative_locations` 必须由生成器写入，每个模块和每个叙事章节只存在一个可见位置，多个模块与章节允许位于同一读者页的不同区域。
