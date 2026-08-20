---
name: team-research-intake
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-intake` 时使用。为行业研究建立并校验任务卡、研究边界、核心判断、反证条件和少量必要追问；不负责检索、公司分析或交付制作。
---

# 团队研究启动

从主 Skill 的 `assets/research-brief.json` 创建任务卡。

1. 先判断交付路径。用户已经选择聊天或 Excel 时直接使用；用户未选择时，只询问“本次希望以聊天格式还是 Excel 格式输出？”，暂停后续工作。收到选择后，再填写行业、地区、细分边界、截止时间、标的和决策问题。
2. 判断用户给出行业还是具体公司，填写 `research_subject`。只有行业时使用 `industry_overview`，资本市场与上市字段填写 `not_applicable`，并在第二级结束路由。
3. 有标的公司时，识别准确法律主体、上市主体和品牌关系，核验全球任一证券交易所的上市状态。已挂牌交易填写 `listed`、`secondary_market`、交易所和证券代码；未挂牌交易填写 `unlisted` 与 `primary_market`。Pre-IPO、IPO 辅导、交易所受理或招股阶段在挂牌前仍归一级市场。
4. 按产业链位置、主要客户、销售对象、利润来源和购买决策判断 `industry_orientation`。终端消费者、品牌和渠道主导时选择 `consumer`，并填写 `analysis_dimensions=[consumer]`；产业客户和工程指标主导时选择 `technology`，并填写 `[technology]`；消费需求、品牌渠道与技术路线、核心器件、工程能力同时直接影响购买、毛利和竞争壁垒时选择 `hybrid`，并填写 `[consumer, technology, integration]`。融合方向的判断理由必须分别说明消费驱动、科技驱动及二者的商业连接。
5. 根据研究对象、资本市场阶段和行业方向生成九个固定 `output_profile` 之一，再填写公司成熟度、信息完整度、必需章节和验收条件。
6. 只追问会改变结果的缺口，最多三项；用户已提供的信息不得重复询问。
7. 写出可被证据推翻的核心判断与反证条件，并从输出配置写入必覆盖竞争簇、必需章节和交付验收项。
8. 科技方向把技术路线与工程瓶颈列为必需章节；消费方向将技术内容限制在产品体验、成本、质量、供应链和合规直接相关的范围；融合方向同时纳入消费与科技必需章节，并增加技术向消费者价值、定价能力、毛利和品牌差异转化的分析。
9. 聊天路径在内部形成精简任务卡并继续研究，不要求保存 JSON。Excel 路径按主 Skill 的 Schema 写入 `schema_version=3` 与 `artifact_type=brief`，运行 `scripts/validate_artifact_bundle.py --brief <文件>`。

聊天路径输出研究边界、核心判断和必要待确认项。Excel 路径输出 `brief.json` 路径；未通过校验时不得开始正式检索。
