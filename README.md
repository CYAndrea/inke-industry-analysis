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

## 让 Agent 自动安装

仓库根目录就是完整的 `team-industry-research` Skill 包。安装时必须保留 `SKILL.md`、`agents/`、`assets/`、`references/`、`scripts/` 和 `subskills/`。不要只下载根目录的 `SKILL.md`，也不要把七个阶段模块分别安装为互不关联的 Skill。

### 通用安装指令

将下面的指令和仓库地址一起发送给支持 Skill 的 Agent：

```text
请从下面的公开 GitHub 仓库安装现有 Skill：
https://github.com/CYAndrea/inke-industry-analysis

安装要求：
1. 将仓库根目录作为一个完整 Skill 包。
2. 完整保留 SKILL.md、agents、assets、references、scripts 和 subskills。
3. 主入口使用根目录 SKILL.md，识别名称应为 team-industry-research。
4. 不要重新总结、改写或生成简化版本。
5. 已存在同名 Skill 时不要覆盖，先报告冲突和现有位置。
6. 安装后检查根目录及七个阶段子 Skill，并报告安装位置和验证结果。
7. 本次只完成安装与验证，不执行行业研究。
```

### Codex

在 Codex 对话中发送通用安装指令即可。Codex 应使用 GitHub Skill 安装流程，将仓库参数设为 `CYAndrea/inke-industry-analysis`，路径设为 `.`，并安装到个人 Skills 目录下的 `team-industry-research`。安装完成后，在新的任务中使用 `$team-industry-research`，或直接提出行业研究与公司研究请求。

Codex 安装器对应的核心参数如下：

```text
--repo CYAndrea/inke-industry-analysis --path . --name team-industry-research
```

### Claude Code

Claude Code 的个人 Skill 目录为 `~/.claude/skills/`，项目 Skill 目录为 `.claude/skills/`。将通用安装指令发送给 Claude Code，并补充安装范围：

```text
请将这个仓库安装为个人 Skill，目标目录为：
~/.claude/skills/team-industry-research

下载时使用临时目录，确认目标目录不存在后再复制完整仓库内容。安装后检查：
~/.claude/skills/team-industry-research/SKILL.md
```

需要仅在当前项目使用时，将目标目录改为：

```text
.claude/skills/team-industry-research
```

安装后可输入 `/team-industry-research` 调用，也可让 Claude Code 根据 `description` 自动识别相关任务。Claude Code 的官方 Skill 目录和调用说明见 [Claude Code Skills](https://code.claude.com/docs/en/skills)。

### Kimi Work

在 Kimi Work 的 Work 模式中新建任务并发送通用安装指令。Kimi Work 能够根据公开 GitHub 地址下载并配置开源 Skill。安装过程中允许必要的联网、下载和本地文件写入权限。完成后进入“技能”页面检查 `team-industry-research`，再在新任务中输入 `/` 搜索并调用。

Kimi 官方的 GitHub Skill 安装说明见 [Kimi 开源 Skills 指南](https://www.kimi.ai/resources/software-skills-for-agents)。

GitHub 自动下载失败时，使用下面的压缩包地址，将文件解压后上传完整目录：

```text
https://github.com/CYAndrea/inke-industry-analysis/archive/refs/heads/main.zip
```

### 其他 Agent

支持目录型 Agent Skills 的工具应将整个仓库复制到其个人或项目 Skills 目录。入口文件必须保持为根目录 `SKILL.md`，相关资源的相对路径不得改变。Agent 不支持多文件 Skill 时，不能保证该 Skill 的阶段编排、校验脚本和 Excel 交付能够正常运行。

### 安装验证

安装完成后向 Agent 发送：

```text
请验证 team-industry-research 的安装：
1. 读取根目录 SKILL.md。
2. 检查 references/output-profile-contracts.json。
3. 检查 assets/excel-reader-pages.json。
4. 检查 subskills 下七个阶段 Skill。
5. 列出识别到的九条输出路由。
6. 只报告安装状态、路径、缺失文件和依赖风险，不执行正式研究。
```

### 跨平台兼容性

研究方法、路由合同、证据规则和聊天交付依赖普通文件读取能力，在支持目录型 Skills 的 Agent 中具备较好的可移植性。Excel 生成器目前使用 Codex 环境中的 `@oai/artifact-tool`。Claude Code、Kimi Work 和其他 Agent 即使完成 Skill 安装，也可能因为缺少该依赖而无法直接执行 Excel 生成脚本。出现 `Cannot resolve @oai/artifact-tool` 时，应将其记录为运行依赖缺失，不能判断为 Skill 安装失败。

安装后，主入口统一使用根目录的 `SKILL.md`，七个阶段模块由主 Skill 按顺序读取。用户无需分别安装子 Skill。

用户已经指定聊天或 Excel 时直接进入对应路径。用户未指定时，Skill 先询问“本次希望以聊天格式还是 Excel 格式输出？”，收到选择后再开始正式研究与交付。

研究框架采用三级路由：具体公司先核验全球上市状态并区分一级或二级市场，再判断所属行业侧重消费、科技或消费科技融合，最后进入公司研究。融合方向结合消费与科技两套模板。用户只给行业时完成对应方向的深度行业研究，并在第二级结束路由。

每条输出路径都有固定的机器可读完成合同。研究在交付前逐模块核对规定要素、分析、证据和必要明细表。完整公司研究合并为八个读者页面，八页只限制工作表数量，不限制研究篇幅。完整叙事章节、模块分析与结构化表格均保留唯一可见位置。模块缺失、叙事缺失、证据无法回连、必要表格缺失或内容未进入成品时，校验器会阻止研究记录标记完成。
