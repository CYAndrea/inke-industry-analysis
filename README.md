# inke-industry-analysis

团队行业研究 Skill 套件，面向中文行业研究、公司研究、竞品分析与投资判断。

## 目录

- `SKILL.md`：主编排 Skill
- `subskills/team-research-intake`：任务卡与研究边界
- `subskills/team-research-evidence`：证据台账、市场与技术研究
- `subskills/team-research-competition`：竞品地图与竞争判断
- `subskills/team-research-editorial`：咨询叙事稿
- `subskills/team-research-delivery`：飞书、Word、Excel、PDF 交付
- `subskills/team-research-quality`：证据、结构与版式验收

## 安装

## 跨 Agent 下载约定

当用户提供本仓库 GitHub 地址并要求“下载、安装或使用这个 Skill”时，将仓库根目录视为完整 Skill 包：下载或复制整个仓库，保留 `SKILL.md`、`subskills/`、`references/`、`assets/` 和 `scripts/`，不要只下载单个 Markdown 文件。

- Claude：将仓库根目录复制到 Claude 的 Skills 目录。
- ChatGPT / Codex：将仓库根目录作为 Skill 路径安装。
- Kimi Work：在 Work 模式的 Skills 面板上传仓库根目录或 ZIP 压缩包。

安装后，主入口统一使用根目录的 `SKILL.md`，六个阶段模块由主 Skill 按需读取。用户无需知道内部目录结构，也无需分别安装子 Skill。

在 Codex Skill 安装器中，将仓库设为 `CYAndrea/inke-industry-analysis`，路径设为 `.`。其他 Agent 采用其原生的本地 Skill 导入方式，并保持仓库根目录结构不变。
