# inke-industry-analysis

团队行业研究 Skill 套件，面向中文行业研究、公司研究、竞品分析与投资判断，专门支持聊天和 Excel 两种交付。

## 目录

- `SKILL.md`：主编排 Skill
- `subskills/team-research-intake`：任务卡与研究边界
- `subskills/team-research-evidence`：证据台账、市场与技术研究
- `subskills/team-research-competition`：竞品地图与竞争判断
- `subskills/team-research-synthesis`：行业、公司与竞争分析的综合判断门禁
- `subskills/team-research-editorial`：咨询叙事稿
- `subskills/team-research-delivery`：聊天与 Excel 交付
- `subskills/team-research-quality`：证据、结构与版式验收

## 安装

## 跨 Agent 下载约定

当用户提供本仓库 GitHub 地址并要求“下载、安装或使用这个 Skill”时，将仓库根目录视为完整 Skill 包：下载或复制整个仓库，保留 `SKILL.md`、`subskills/`、`references/`、`assets/` 和 `scripts/`，不要只下载单个 Markdown 文件。

- Claude：将仓库根目录复制到 Claude 的 Skills 目录。
- ChatGPT / Codex：将仓库根目录作为 Skill 路径安装。
- Kimi Work：在 Work 模式的 Skills 面板上传仓库根目录或 ZIP 压缩包。

安装后，主入口统一使用根目录的 `SKILL.md`，七个阶段模块由主 Skill 按顺序读取。用户无需知道内部目录结构，也无需分别安装子 Skill。

用户已经指定聊天或 Excel 时直接进入对应路径。用户未指定时，Skill 先询问“本次希望以聊天格式还是 Excel 格式输出？”，收到选择后再开始正式研究与交付。

研究框架采用三级路由：具体公司先核验全球上市状态并区分一级或二级市场，再判断所属行业侧重消费、科技或消费科技融合，最后进入公司研究。融合方向结合消费与科技两套模板。用户只给行业时完成对应方向的深度行业研究，并在第二级结束路由。

每条输出路径都有固定的机器可读完成合同。研究在交付前逐模块核对规定要素、分析、证据和必要明细表；Excel 生成器为每个核心模块建立可见页面。模块缺失、证据无法回连、必要表格缺失或模块未进入成品时，校验器会阻止研究记录标记完成。

在 Codex Skill 安装器中，将仓库设为 `CYAndrea/inke-industry-analysis`，路径设为 `.`。其他 Agent 采用其原生的本地 Skill 导入方式，并保持仓库根目录结构不变。
