# 🔬 msitarzewski/agency-agents - 全方位深度调研

> 调研时间：2026-08-10 | Stars：⭐ 140,498 | 语言：Shell/Markdown | 协议：MIT | 默认分支：main

## 📌 一句话定位
agency-agents（"The Agency"）**不是一个软件项目，而是一份「AI 专家人设库」**——200+ 个结构化的 agent 角色 Markdown 文件，按 16-21 个"部门"组织，配一套把人设一键装进 Claude Code/Cursor/Codex/Gemini/OpenCode 等十余种工具的转换脚本，外加一个原生桌面 App。它定义的是"Agent-native Skill：不是代码，是教 AI 怎么工作的指令集"这一新软件形态。

## ⭐ 项目亮点
- **"岗位说明书"范式**：每个 agent 文件含身份/人格/工作流程/交付标准/示例代码/成功指标/沟通风格——把最麻烦的 Prompt Engineering 提前结构化，被中文社区称为"Prompt 界的 Terraform"。
- **多工具一键分发**：`scripts/convert.sh` + `scripts/install.sh` 生成并安装到 Claude Code、Cursor、Codex、Gemini CLI、OpenCode、Copilot、OpenClaw、Aider、Windsurf、Kimi、Osaurus、Hermes、Mistral Vibe 等；`divisions.json` 是部门集合的 single source of truth（CI `check-divisions.yml` 校验目录/脚本/过滤器的三方一致）。
- **原生 App 降低门槛**：agencyagents.app（macOS/Linux/Windows）图形化浏览整个花名册、一键装到各工具、自动更新——从 clone 脚本演进到原生 App，分发路径标准。
- **零代码、纯 MIT、社区驱动**：任何人可 fork/改/贡献，中文社区已衍生 agency-agents-zh（新增 26 翻译角色 + 4 中国市场专用角色）。

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学
```
academic/ design/ engineering/ finance/ game-development/ gis/ healthcare/ ...  # 各部门目录，每目录=一组 agent .md
integrations/   # scripts/convert.sh 的【输出】目录（非源 agent，被排除出部门计数）
strategy/       # playbooks/runbooks（无 agent frontmatter，也被排除）
examples/ scripts/  # 示例与安装/转换脚本
divisions.json   # 部门集合唯一真相源（label/icon/color），CI 校验
CONTRIBUTING_zh-CN.md  # 中文贡献指南，印证多语言社区
```

设计哲学：**"人设即资产"**——把"给 AI 一个角色"这件事从脆弱的临场 prompt 升级成可复用、可版本化、可协作的文件。每个 agent 文件带 frontmatter（身份/部门），`scripts/convert.sh` 把统一的 Markdown 源翻译成各工具的特定格式。

### 技术栈 & 依赖图谱
- 源格式：Markdown + YAML frontmatter（agent 定义）；
- 转换：Shell 脚本（`convert.sh`/`install.sh`/`lint-agents.sh`/`check-divisions.sh`）；
- 目标工具：十余种 AI 编码助手（通过各自 agent 目录约定，如 `~/.claude/agents/`）；
- 配套 App：原生三端（非 Web），Homebrew-cask 一行安装。

### 核心配置一览
- 安装：`brew install --cask msitarzewski/agency-agents/agency-agents`（App）或 `./scripts/install.sh --tool claude-code`；
- 选装子集：`--tool cursor --division engineering,security --agent frontend-developer,...`（装超量时安装器会警告，建议装子集）；
- 新增部门须同时改 `divisions.json` + `scripts/*` 的 `AGENT_DIRS` + lint 过滤器，否则 CI 失败。

## 💡 应用场景与启发（重点章节）

### 典型使用场景
- **角色漂移治理**：给 LLM"扮演资深安全工程师"常得到泛泛答复；用 agent 文件固化"工作流+沟通风格+成功标准"，让它更像干了 10 年的工程师。
- **多窗口协作模拟**：开多个窗口分别挂 CEO/CTO/市场/财务 agent 同时讨论一个项目，获得"管理虚拟团队"的体验。
- **团队工具标准化**：把精选 agent 子集装进团队共用的 Claude Code/Cursor 环境，统一协作范式。

### 可借鉴的解决方案模式
- **"角色即可复用文件 + 多工具翻译层"**：用一份源定义 + 转换脚本覆盖 N 种宿主工具，比"每个工具手写一遍"省维护——任何"同一份知识要分发到多平台"的系统都该学。
- **"single source of truth + CI 一致性校验"**：`divisions.json` 被 `check-divisions.yml` 校验，避免目录/脚本/过滤器三者漂移——知识库类项目的治理范本。

### 同类需求的可参考思路
如果要做"技能"而非"人设"，本库已收录 ComposioHQ/awesome-claude-skills（1000+ Claude Skills 策展）与 nextlevelbuilder/ui-ux-pro-max-skill；agency-agents 的差异在"完整人格 + 多部门组织 + 原生 App"，更偏"角色库"而非"能力库"。

## 🧠 核心源码解读（克制代码量）

### 入口与分发主流程（scripts/convert.sh + install.sh）
`convert.sh` 先扫描各部门 `.md` 的 frontmatter，按各工具格式生成集成文件到 `integrations/`；`install.sh` 交互式（或 `--tool/--division/--agent`）把生成的文件拷进对应工具的 agent 目录：

```bash
# 典型用法（README 摘录，精简化）
./scripts/convert.sh                       # 生成所有工具集成文件
./scripts/install.sh --tool claude-code    # 装到 Claude Code
./scripts/install.sh --tool cursor --agent frontend-developer,ui-designer
cp engineering/*.md ~/.claude/agents/       # 或手动拷贝单部门
```

### 关键模块：部门真相源（divisions.json）
```json
{ "divisions": {
  "academic":  {"label":"Academic","icon":"GraduationCap","color":"#8B5CF6"},
  "design":    {"label":"Design","icon":"PenTool","color":"#EC4899"},
  "engineering":{"label":"Engineering","icon":"Code","color":"#3B82F6"}
  /* finance / game-development / gis / healthcare ... */
}}
```
CI 用 `check-divisions.sh` 校验：磁盘目录、`AGENT_DIRS` 数组、`lint-agents.yml` 路径过滤器三方必须一致，否则构建失败——这是它"目录即配置"的治理核心。

### 隐藏功能 & 未文档化特性
- `strategy/` 里的 playbooks/runbooks 是"无 frontmatter 的剧本"，README 的 "Full Agency Product Discovery" 号称 8 部门并行，但点进去是"8 个 agent 被同时部署产出统一计划"——**人工调度 8 个 agent，不是 agent 间自主协作**（社区已戳穿）；
- `integrations/` 是转换**输出**，被明确排除在部门计数外，避免误算。

## 📐 架构决策与设计哲学
- **"Agent 不是自主智能体，是人设文件"**：作者明确它们是带结构的角色描述，能否交付完全取决于底层模型——"Agent 的天花板 = 人设下限 × 模型上限"。
- **不设真正编排**：项目只提供人设与安装，多 agent 协作要用户自己写编排或交给 Hermes Agent 类框架。
- **诚实标注边界**：装超量时警告、已知平台坑写进文档——社区赞赏这种"不装完美支持"的诚实。

## 🌐 全网口碑画像

### 好评共识
- 中文社区（[CSDN/DeepSeek](https://deepseek.csdn.net/6a4341d3662f9a54cb8655ae.html)、[头条](https://www.toutiao.com/article/7664480307722207787/)）普遍认可"从单兵到团队协作的视角转换"与"原生 App 极低门槛"；
- 被评价为"GitHub 上最有影响力的 Meta-Project 之一"，定义了 Agent-native Skill 新形态；
- 多 agent 同台讨论带来的"管理虚拟团队"体验被反复称道。

### 差评共识 & 踩坑高发区（来自 [wangruofeng007 诚实拆解](https://wangruofeng007.com/blog/2026-06/agency-agents-232-personas-org-chart)）
- **"232 个 agent"有水分**：Marketing 部门一个中国平台一个 agent（小红书/抖音/快手只是同套方法论换参数），真算"方法论"约 60-80 个，剩下是变体——别被数字唬住；
- **静态文件非自主**：agent 能不能交付取决于你用的模型本身能力，人设再好也救不了弱模型；
- **无真正编排**：8 部门"并行"是人工同时部署，不是自主协作；
- **Fork 比例偏高（~16%）**：纯 Markdown 仓库这么高 fork 比，大概率大量是 fork 自用改一份，真正活跃贡献者少数（主流语言版本基本出自 2 人之手）。

### 争议焦点
- **星标通胀质疑**：140k⭐ / 20k+ fork，增长速度异常（源于 Reddit 病毒传播 + Theo 类 KOL 效应），部分声音质疑"热度≠质量"。但社区共识是"形态有价值，数字有水分"。

### 维护者响应风格
作者 Michael Sitarzewski（30 年 Builder、Techstars 校友），无融资无团队，从 Reddit 帖子迭代而来；多语言贡献指南（含中文）显示对社区分发的重视。

## ⚔️ 竞品对比

| 维度 | agency-agents | ComposioHQ/awesome-claude-skills | nextlevelbuilder/ui-ux-pro-max-skill |
|------|---------------|-----------------------------------|--------------------------------------|
| 形态 | 人设库(角色) | 技能库(能力) | 单一设计技能 |
| 规模 | 200+ agent/16-21 部门 | 1000+ skills | 1 大技能 |
| 多工具分发 | 十余种+原生App | Claude 生态为主 | Claude |
| 组织方式 | 部门树 | 策展清单 | 单文件 |
| 定位 | "虚拟公司" | "技能超市" | "设计智能" |

**选择建议**：要"完整人格 + 多部门组织 + 一键装 App" → agency-agents；要"细粒度能力复用" → awesome-claude-skills；要"专项设计能力" → ui-ux-pro-max-skill。三者互补，本库均已收录。

## 🎯 核心研判

### 项目优势（不可替代的价值点）
- 率先把"人设即文件 + 多工具翻译 + 原生 App"做成完整范式，定义了 Agent-native Skill 这一新形态；
- 极低的采用门槛（MIT、App、npx 式分发）让它成为"AI 角色库"的事实标准候选。

### 项目风险（潜在隐患和局限性）
- **形态轻、护城河浅**：纯 Markdown，任何模型/工具厂商都能内置类似人设市场；
- **数字有水分 + 无真编排**：232 含大量变体，多 agent 协作需自备框架，别高估"自动组队"；
- **质量取决于底层模型**：人设天花板受模型上限约束，弱模型下交付打折。

### 适用场景 & 不适用场景
- ✅ 想给 AI 编程助手建立"专业角色层"、团队标准化协作范式、快速体验多 agent 讨论；
- ❌ 想要真正自主协作的 agent 系统（需另接编排框架）、闭源可控企业版。

### 趋势判断
**现象级但需冷静看待**。它验证了"人设/技能结构化"的需求真实存在，但作为"库"而非"引擎"，长期价值取决于能否从"角色分发"演进到"角色编排 + 质量评测"——否则易沦为被官方原生能力吸收的形态先行者。

## 📂 关键文件路径速查
- 部门真相源：`divisions.json`
- 各部门的 agent 人设：`academic/` `design/` `engineering/` `finance/` `game-development/` `gis/` `healthcare/` ...（每目录含带 frontmatter 的 `.md`）
- 转换/安装/校验脚本：`scripts/convert.sh` `scripts/install.sh` `scripts/lint-agents.sh` `scripts/check-divisions.sh`
- 集成输出（非源）：`integrations/`
- 剧本（无 agent frontmatter）：`strategy/`
- 中文贡献指南：`CONTRIBUTING_zh-CN.md`
- 发布：https://github.com/msitarzewski/agency-agents ｜ 官网/App：https://agencyagents.app
