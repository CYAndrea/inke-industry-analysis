---
name: team-research-synthesis
description: 仅在主 Skill `$team-industry-research` 编排，或用户明确调用 `$team-research-synthesis` 时使用。整合已经完成的行业、公司与竞争分析，处理证据冲突并形成写作交接包；不补做大范围检索或撰写最终报告。
---

# 团队研究综合判断

读取任务卡、`industry-analysis.json`、适用时的 `company-analysis.json`、`competition-map.json`，并通过证据编号核对 `evidence-ledger.json`。不得重新开展完整行业或公司检索。

1. 回答任务卡中的决策问题，形成单一中心判断。
2. 对行业结论、公司结论和竞争定位进行交叉验证，检查公司是否真正受益于行业变化。
3. 列出相互冲突的证据或判断，说明采用哪项结论、采用理由和仍需观察的信息。
4. 将事实、估算、推演和待核验事项分开，形成关键结论、反向证据、失效条件和决策含义。
5. 规划读者版章节，每章只保留一个中心问题和必要证据编号。
6. 生成压缩交接包，只包含中心判断、决策回答、关键结论、冲突处理、反向证据、失效条件、章节蓝图和下一阶段重点。

聊天路径在内部保留综合判断交接包。Excel 路径从主 Skill 的 `assets/analysis-synthesis.json` 创建 `analysis-synthesis.json`，行业任务运行 `scripts/validate_artifact_bundle.py --synthesis <analysis-synthesis.json> --industry-source <industry-analysis.json> --ledger <evidence-ledger.json>`，公司任务额外传入 `--company-source <company-analysis.json>`。关键结论没有证据编号、公司任务缺少公司结论、行业与公司判断存在未处理冲突时不得进入叙事编辑阶段。
