# 🔬 hugohe3/ppt-master - 全方位深度调研

## 项目全景
- **仓库**：`hugohe3/ppt-master`
- **一句话定位**：AI generates a real, editable PowerPoint from any document — native shapes & animations, speaker notes voiced as audio narration, and the option to follow your own .pptx template, not slide images · by Hugo He
- **基础指标**：Stars=25604 / Forks=2312 / 默认分支=`main`
- **Topics**：ai-agent, powerpoint, pptx, presentation, office, slides, powerpoint-generation, ppt, slide, aippt
- **Homepage**：https://hugohe3.github.io/ppt-master/

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：skills(12110), examples(1250), docs(38), .github(5), .claude-plugin(1), .env.example(1), .gitignore(1), AGENTS.md(1), CLAUDE.md(1), CODE_OF_CONDUCT.md(1)
- 关键文件候选：requirements.txt, README.md, AGENTS.md, CLAUDE.md, CONTRIBUTING.md

### 设计亮点研判
- 存在 Python 工程入口，通常意味着自动化流水线、服务端或研究脚本由 Python 主导。
- 仓库包含 .github 目录，通常意味着 CI、issue 模板或自动发布流程已被工程化。

## 源码深度解读
### README / 说明文档要点
# PPT Master — AI generates natively editable PPTX from any document

[![Version](https://img.shields.io/badge/version-v2.9.0-blue.svg)](https://github.com/hugohe3/ppt-master/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/hugohe3/ppt-master.svg)](https://github.com/hugohe3/ppt-master/stargazers)
[![AtomGit stars](https://atomgit.com/hugohe3/ppt-master/star/badge.svg)](https://atomgit.com/hugohe3/ppt-master)

English | [中文](./README_CN.md)

<p align="center">
  <sub>This project is kept free and open source with the support of <a href="https://www.packyapi.com/register?aff=ppt-master">PackyCode</a>, <a href="https://apikey.fun/register?aff=PPT-MASTER">APIKEY.FUN</a> and other sponsors.</sub>
</p>

<table>
  <tr>
    <td width="180"><a href="https://www.packyapi.com/register?aff=ppt-master"><img src="docs/assets/sponsors/packycode.png" alt="PackyCode" width="150"></a></td>
    <td>Thanks to PackyCode for sponsoring this project! PackyCode is a reliable and efficient API relay service provider, offering relay services for Claude Code, Codex, Gemini, and more. PackyCode provides special discounts for our project users: register using <a href="https://www.packyapi.com/register?aff=ppt-master">this link</a> and enter the promo code <strong>ppt-master</strong> during recharge to get 10% off.</td>
  </tr>
  <tr>
    <td width="180"><a href="https://apikey.fun/register?aff=PPT-MASTER"><img src="docs/assets/sponsors/apikey-fun.png" alt="APIKEY.FUN" width="150"></a></td>
    <td>Thanks to APIKEY.FUN for sponsoring this project! APIKEY.FUN is a professional enterprise-grade AI relay service committed to stable, efficient, and low-cost AI access for businesses and developers. The platform supports mainstream models including Claude, OpenAI, and Gemini, with prices as low as <strong>7% of official rates</strong>. Register through <a href="https://apikey.fun/register?aff=PPT-MASTER">our dedicated link</a> for an exclusive perk: <strong>up to 5% off on top-ups, permanently</strong>.</td>
  </tr>
</table>

> [!IMPORTANT]
> ### This is a tool, not a wishing well
> Don't expect it to hand you a finished, perfect deck in one shot. Its real value is taking most of the tedious work off your plate; the polishing that's left is yours — a natively editable deck exists precisely so you can keep working on it, not a flat image you can't touch. The cheaper the m
...[truncated]

### 关键文件精读
### `requirements.txt`
```
# PPT Master Dependencies / PPT Master 依赖
# =============================================
#
# Full list lives inside the skill so installing the skill alone gives full capability.
# 完整依赖列表已内置于 skill 内部，单独安装 skill 即可获得完整能力。
#
# Install / 安装方式：
#   pip install -r requirements.txt                     # from repo root / 仓库根目录
#   pip install -r skills/ppt-master/requirements.txt   # from anywhere / 任意位置
#
-r skills/ppt-master/requirements.txt
```

### `README.md`
```
# PPT Master — AI generates natively editable PPTX from any document

[![Version](https://img.shields.io/badge/version-v2.9.0-blue.svg)](https://github.com/hugohe3/ppt-master/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/hugohe3/ppt-master.svg)](https://github.com/hugohe3/ppt-master/stargazers)
[![AtomGit stars](https://atomgit.com/hugohe3/ppt-master/star/badge.svg)](https://atomgit.com/hugohe3/ppt-master)

English | [中文](./README_CN.md)

<p align="center">
  <sub>This project is kept free and open source with the support of <a href="https://www.packyapi.com/register?aff=ppt-master">PackyCode</a>, <a href="https://apikey.fun/register?aff=PPT-MASTER">APIKEY.FUN</a> and other sponsors.</sub>
</p>

<table>
  <tr>
    <td width="180"><a href="https://www.packyapi.com/register?aff=ppt-master"><img src="docs/assets/sponsors/packycode.png" alt="PackyCode" width="150"></
...[truncated]
```

### `AGENTS.md`
```
# AGENTS.md

This file is the project entry point for general AI agents.

**You MUST read [`skills/ppt-master/SKILL.md`](skills/ppt-master/SKILL.md) before any PPT generation task or repo modification.** This repository exists to generate presentations; SKILL.md is the authoritative workflow that owns project creation, role switching, serial execution, quality gates, post-processing, export, and every per-step command. The rest of this file only points to where related material lives — it never substitutes for SKILL.md.

## Project Overview

PPT Master is an AI-driven presentation generation system. Multi-role collaboration (Strategist → Image_Generator → Executor) converts source documents (PDF/DOCX/URL/Markdown) into natively editable PPTX with real PowerPoint shapes (DrawingML).

**Core Pipeline**: `Source Document → Create Project → [Template] → Strategist Eight Confirmations → [Image_Generator] → Executor Live Preview → Quality Check → Post-processing → Export PPTX`

> Topic-only 
...[truncated]
```

### `CLAUDE.md`
```
# CLAUDE.md

This file is the project entry point for Claude Code.

**You MUST read [`skills/ppt-master/SKILL.md`](skills/ppt-master/SKILL.md) before any PPT generation task or repo modification.** This repository exists to generate presentations; SKILL.md is the authoritative workflow that owns project creation, role switching, serial execution, quality gates, post-processing, export, and every per-step command. The rest of this file only points to where related material lives — it never substitutes for SKILL.md.

## Project Overview

PPT Master is an AI-driven presentation generation system. Multi-role collaboration (Strategist → Image_Generator → Executor) converts source documents (PDF/DOCX/URL/Markdown) into natively editable PPTX with real PowerPoint shapes (DrawingML).

**Core Pipeline**: `Source Document → Create Project → [Template] → Strategist Eight Confirmations → [Image_Generator] → Executor Live Preview → Quality Check → Post-processing → Export PPTX`

> Topic-only reques
...[truncated]
```

### `CONTRIBUTING.md`
```
# Contributing to PPT Master

Thank you for your interest in contributing! This guide will help you get started.

## Ways to Contribute

- **Templates** — New layout templates or visual styles
- **Charts** — Additional chart types or SVG chart templates
- **Icons** — Vector icons for the icon library
- **Scripts** — Improvements to conversion or post-processing scripts
- **Docs** — Clarifications, translations, or new guides
- **Bug reports** — Reproducible issues with clear descriptions
- **Ideas** — Feature requests and design suggestions

## Getting Started

### Prerequisites

- **Python 3.10+** — the only required dependency
- **Node.js 18+** and **Pandoc** are edge-case fallbacks that 99% of contributors never need; install only if you're working on the specific paths that require them. See the [README Quick Start](./README.md#1-prerequisites) for when each applies.

### Setup

```bash
git clone https://github.com/hugohe3/ppt-master.git
cd ppt-master
pip install -r requirements.tx
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #152 [CLOSED] Showcase inquiry for an AI PowerPoint generation workflow（comments=[{'id': 'IC_kwDOQl_Gys8AAAABFcbwaw', 'author': {'login': 'hugohe3'}, 'authorAssociation': 'OWNER', 'body': 'Thanks for reaching out. At the moment, I only share and maintain ppt-master on GitHub. I’ll close this issue since it’s not related to project development.', 'createdAt': '2026-06-09T13:38:23Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/hugohe3/ppt-master/issues/152#issuecomment-4660326507', 'viewerDidAuthor': False}] labels=无）
- #151 [OPEN] 默认生成的ppt单一没有图片图标等（comments=[{'id': 'IC_kwDOQl_Gys8AAAABFY-CVg', 'author': {'login': 'hugohe3'}, 'authorAssociation': 'OWNER', 'body': '什么模型？推测第一原因为模型能力太差。', 'createdAt': '2026-06-09T06:16:19Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/hugohe3/ppt-master/issues/151#issuecomment-4656693846', 'viewerDidAuthor': False}] labels=enhancement）
- #144 [CLOSED] [Bug] 通过 npx skills 安装时，projects/ 目录被创建在技能目录内部而非项目根目录（comments=[{'id': 'IC_kwDOQl_Gys8AAAABEVVQ3Q', 'author': {'login': 'hugohe3'}, 'authorAssociation': 'OWNER', 'body': '分析后确认：这个 issue 描述的现象是有效的，但根因不应归结为 `REPO_ROOT = SKILL_DIR.parent.parent` 直接影响 `init` 输出目录。\n\n`project_manager.py init` 的默认输出目录本质上应该跟随调用者当前工作区，也就是 IDE / agent 执行命令时的 `cwd`：\n\n```text\n<当前工作区>/projects/<project_name>_<format>_<date>/\n```\n\n原实现里默认值是裸相对路径 `projects`，语义上也是依赖 `cwd`，但代码和 CLI 默认参数没有把这个意图表达清楚；如果 agent 在 skill 自身目录里执行命令，就会落到 skill 目录内部。\n\n已做最小修复：\n\n- `ProjectManager()` 默认目录改为 `Path.cwd() / "projects"`\n- `parse_init_args()` 不再把默认 `--dir` 固化为 `"projects"`，未显式传 `--dir` 时交给 `ProjectManager` 使用当前工作区默认值\n- `--dir <path>` 仍保留为显式覆盖\n- 不从 `.agents` / skill 安装路径反推 workspace root，也不引入环境变量\n\n验证：\n\n```bash\npython3 -m py_compile skills/ppt-master/scripts/project_manager.py\ngit diff --check -- skills/ppt-master/scripts/project_manager.py\n```\n\n结论：默认行为应由执行时的工作区 `cwd` 决定；agent/IDE 侧需要确保从用户项目根目录执行初始化命令。\n', 'createdAt': '2026-05-31T05:09:53Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/hugohe3/ppt-master/issues/144#issuecomment-4585771229', 'viewerDidAuthor': False}, {'id': 'IC_kwDOQl_Gys8AAAABEVXnUg', 'author': {'login': 'hugohe3'}, 'authorAssociation': 'OWNER', 'body': '补充 commit 链接：\n\nhttps://github.com/hugohe3/ppt-master/commit/c5f0090e57c0563cc9e452b35b61cdd7e335b190\n', 'createdAt': '2026-05-31T05:27:57Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/hugohe3/ppt-master/issues/144#issuecomment-4585809746', 'viewerDidAuthor': False}, {'id': 'IC_kwDOQl_Gys8AAAABEWeyTg', 'author': {'login': 'mars171'}, 'authorAssociation': 'NONE', 'body': '感谢作者的快速响应和修复！已将 commit c5f0090 同步到本地，问题已解决。', 'createdAt': '2026-05-31T14:15:03Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/hugohe3/ppt-master/issues/144#issuecomment-4586975822', 'viewerDidAuthor': False}] labels=无）
- #143 [CLOSED] PPT 中的文字渐变填充效果在 SVG 转换时丢失（comments=[{'id': 'IC_kwDOQl_Gys8AAAABEVXcCA', 'author': {'login': 'hugohe3'}, 'authorAssociation': 'OWNER', 'body': '已确认并修复。\n\n这个问题发生在 PPTX → SVG 导入链路，也就是 `/create-template` 中 `pptx_template_import.py` 调用 `pptx_to_svg` 时，PowerPoint 文本 run 上的 `a:gradFill` 没有被转换到 SVG 文本的 `fill="url(#...)"`。\n\n修复没有采用模块级累加器 / reset 的方案，而是复用现有转换管线：\n\n- `txbody_to_svg.py`\n  - 文本 run 解析时识别 `a:gradFill`\n  - 复用现有 `fill_to_svg.resolve_fill()` 生成 `linearGradient` / `radialGradient`\n  - 通过 `TextResult.defs` 返回文本渐变 defs\n- `slide_to_svg.py`\n  - 将 shape 文本的 `TextResult.defs` 汇总进 slide `<defs>`\n- `tbl_to_svg.py`\n  - 表格单元格文本同样传递和汇总文本渐变 defs，避免只修普通文本框\n\n验证覆盖：\n\n```bash\npython3 -m py_compile \\\n  skills/ppt-master/scripts/pptx_to_svg/txbody_to_svg.py \\\n  skills/ppt-master/scripts/pptx_to_svg/slide_to_svg.py \\\n  skills/ppt-master/scripts/pptx_to_svg/tbl_to_svg.py\n\npython3 skills/ppt-master/scripts/pptx_template_import.py \\\n  projects/issue143_text_gradient_repro/text_gradient.pptx \\\n  -o /tmp/issue143_template_import_final\n\ngit diff --check -- \\\n  skills/ppt-master/scripts/pptx_to_svg/txbody_to_svg.py \\\n  skills/ppt-master/scripts/pptx_to_svg/slide_to_svg.py \\\n  skills/ppt-master/scripts/pptx_to_svg/tbl_to_svg.py\n```\n\n复现样例修复后的输出已确认包含：\n\n```xml\n<linearGradient id="txtgrad1" ...>\n...\n<tspan fill="url(#txtgrad1)" ...>GRADIENT TEXT</tspan>\n```\n\n提交：\n\n```text\n45b6eab9 fix(pptx-to-svg): preserve text gradient fills\n```\n', 'createdAt': '2026-05-31T05:26:07Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/hugohe3/ppt-master/issues/143#issuecomment-4585806856', 'viewerDidAuthor': False}, {'id': 'IC_kwDOQl_Gys8AAAABEVXnUw', 'author': {'login': 'hugohe3'}, 'authorAssociation': 'OWNER', 'body': '补充 commit 链接：\n\nhttps://github.com/hugohe3/ppt-master/commit/45b6eab96f0ec82d0546b9ccb1454992aea3252e\n', 'createdAt': '2026-05-31T05:27:57Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/hugohe3/ppt-master/issues/143#issuecomment-4585809747', 'viewerDidAuthor': False}] labels=bug）
- #142 [CLOSED] 默认使用的python3命令报错（comments=[{'id': 'IC_kwDOQl_Gys8AAAABESCtzQ', 'author': {'login': 'hugohe3'}, 'authorAssociation': 'OWNER', 'body': '感谢反馈，已定位到原因 👇\n\npython.org 的 Windows 安装包只装了 `python.exe`，**不会装 `python3.exe`**。所以 `python3` 命令落到了系统 `WindowsApps\\python3.exe` 这个占位 stub 上，而它只转发到 Microsoft Store 版 Python，不转发 python.org 版，没装 Store 版就报 exit 49——你截图里 `python` 能跑、`python3` 报错正是这个原因。\n\n关于「根据环境自动判断命令」：命令是 AI agent 从文档里读出来、再丢进 PowerShell/cmd/bash 执行的，中间没有可做判断的程序层，几种 shell 也没有统一写法，所以没法在命令层真正做到自动判断。不过实际上 agent 通常会自愈——探测到 `python3` 失败会自动改用 `python` 继续（你截图最后一步就是），功能并不受影响。\n\n已做的处理（commit https://github.com/hugohe3/ppt-master/commit/8abb484e1826e59b0b9398f5dc8ec4c5b1bb73fa ）：\n- SKILL.md 加了 Windows 说明：`python3` 报错就改用 `python`；\n- Windows 安装文档(中/英)各加了一条 FAQ 解释这个现象。\n\n**你这边的即时解法**：把命令里的 `python3` 换成 `python` 即可，其余完全一样。', 'createdAt': '2026-05-30T08:51:07Z', 'includesCreatedEdit': True, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/hugohe3/ppt-master/issues/142#issuecomment-4582321613', 'viewerDidAuthor': False}] labels=enhancement）
- #137 [CLOSED] 大佬请问将来是否会支持docker部署（comments=[{'id': 'IC_kwDOQl_Gys8AAAABD3V6mw', 'author': {'login': 'hugohe3'}, 'authorAssociation': 'OWNER', 'body': '暂时没有 Docker 计划。PPT Master 的产品形态是一个跑在 AI IDE（Claude Code / Cursor / VS Code + Copilot / Codebuddy）里的 skill，不是常驻服务，没有需要容器化的后端进程——所谓"部署"在这里就是在 IDE 里安装 skill + 装一下 Python 脚本依赖，Docker 反而会把链路变长。', 'createdAt': '2026-05-27T12:05:26Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/hugohe3/ppt-master/issues/137#issuecomment-4554324635', 'viewerDidAuthor': False}] labels=enhancement）

### Pull Requests 抽样
- PR #150 [MERGED] fix(svg_to_pptx): treat digits as tabular width in estimate_text_width
- PR #146 [MERGED] fix(pptx_to_svg): resolve font-size from pPr/defRPr in PPTX→SVG text export
- PR #140 [CLOSED] feat(svg-quality): add layout geometry warnings
- PR #130 [CLOSED] fix(svg): require width+height+viewBox on SVG root element
- PR #129 [CLOSED] feat(latex): add LaTeX formula rendering via CodeCogs API

### Releases 抽样
- v2.9.0（published=2026-05-31T13:42:05Z latest=True）
- v2.8.0（published=2026-05-22T13:55:11Z latest=False）
- v2.7.0（published=2026-05-13T09:31:31Z latest=False）
- v2.6.0（published=2026-05-05T11:47:57Z latest=False）
- v2.5.0（published=2026-04-30T12:12:54Z latest=False）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 1/7，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 3 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者具备版本化交付意识。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | ppt-master | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | Coqui TTS / Piper / Bark 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 项目优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 项目风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `requirements.txt`
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`

## 3 条关键发现
- 代码入口/骨架集中在：requirements.txt, README.md, AGENTS.md, CLAUDE.md, CONTRIBUTING.md
- Issue 抽样显示近期关注点包括：Showcase inquiry for an AI PowerPoint generation workflow；默认生成的ppt单一没有图片图标等
- 版本交付可从最新 release 观察：v2.9.0

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
