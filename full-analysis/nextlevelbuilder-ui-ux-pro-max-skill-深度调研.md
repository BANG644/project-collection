# nextlevelbuilder/ui-ux-pro-max-skill 深度调研

> 调研日期：2026-07-27 | 星标：110,365⭐ | 协议：MIT | 语言：Python(主) / JS / HTML / TS
> 定位：给 AI 编码助手用的「设计智能」技能库（84 风格 / 192 配色 / 74 字体搭配 / 98 UX 准则 / 25 图表 / 22 技术栈）

## 项目亮点（差异化）

- 🤖 **把「设计审美」做成可检索的知识库**：不靠 LLM 凭空生成 UI，而是把经过策展的 design tokens（配色/字体/风格/图表/UX 准则）做成本地可检索数据库，让 AI 编码助手「查表」而非「瞎编」。
- 🔌 **19 个 AI 平台全覆盖**：claude / cursor / windsurf / copilot / kiro / codex / gemini / trae / opencode / openclaw 等，统一一个 skill 适配所有主流编码 Agent。
- 📊 **规模化的策展数据**：84 UI 风格、192 配色方案、74 字体搭配、98 UX 准则、25 图表类型、22 技术栈 —— 单体技能内嵌的设计知识密度极高。
- 🪶 **极轻量检索内核**：核心是一个 Python 搜索脚本（`search.py`），无重依赖，Agent 运行时按需调用，契合「技能即上下文」的加载范式。

## 项目全景

UI/UX Pro Max 是一个面向 AI 编码助手的 **design-intelligence skill**。它解决的核心痛点是：当前 AI 生成的 UI 往往「能跑但丑」「配色混乱」「缺乏设计系统一致性」。项目的思路是把人类设计师积累的 design system 知识**结构化、可检索化**，让 Agent 在生成界面时先「查设计规范」再写代码。

安装方式极简：`npx ui-ux-pro-max-cli init --ai <platform>`，一条命令把技能注入对应 Agent 的配置目录。`skill.json` 声明版本 `2.11.0`。

## 核心架构

三层结构：**策展数据库（知识层）→ 检索内核（查询层）→ 技能清单（注入层）**

```
skill.json            ← 技能清单（元数据 + 19 平台 install 指令）
   │
   ▼
src/ui-ux-pro-max/
   ├─ scripts/search.py     ← 检索内核（CLI: python3 search.py "<q>" --domain <d> [-n N]）
   ├─ data/                 ← 策展数据库（styles/palettes/fonts/charts/ux-guidelines...）
   └─ (各 domain 索引)
   │
   ▼
CLAUDE.md / .claude/ / .cursor/ ...   ← 注入到各 Agent 的配置
```

`search.py` 支持的 domain（领域检索）直接定义了技能的能力边界：
- `product` 产品类型推荐（SaaS / 电商 / 作品集）
- `style` UI 风格（玻璃拟态 / 极简 / 粗野主义）+ AI prompt + CSS 关键词
- `typography` 字体搭配（含 Google Fonts 导入）
- `color` 按产品类型的配色方案
- `landing` 页面结构 + CTA 策略
- `chart` 图表类型 + 库推荐
- `ux` 最佳实践 + 反模式
- `icons` 图标推荐（Phosphor / Heroicons / Lucide）
- `react` React/Next.js 性能模式
- `web` App 界面规范（iOS/Android/RN）
- `google-fonts` / `gsap` 等细分检索

## 源码深度解读

检索内核 `src/ui-ux-pro-max/scripts/search.py` 是技能的灵魂。其核心设计是**「离线、无依赖、领域分片检索」**：

- 每个 domain 对应一份结构化数据（JSON/MD），搜索时只加载对应分片，避免一次性把 192 配色全量灌进上下文。
- 调用形态是标准子进程 CLI：`python3 search.py "fintech dashboard" --domain color -n 5`，返回 Top-N 命中，Agent 再把结果作为生成依据。
- 这与「渐进式加载」理念一致（参见 `ComposioHQ/awesome-claude-skills` 中 ~100 token 名称常驻、命中才载正文的模式）：**技能名常驻上下文，知识正文按需检索**，上下文成本极低。

关键洞察：本项目的架构本质是 **「RAG 的极简本地版」** —— 不用向量库、不用 embedding，靠人工策展的结构化数据库 + 关键词检索，反而更可控、更省 token、更适合设计这类「需要精确规范」的场景。

## 应用场景与启发

- **AI 生成 UI 的「审美兜底」**：让 Cursor/Claude 生成界面前先查设计规范，避免配色灾难。
- **设计系统一致性**：团队可基于本技能 fork 出自己的品牌 design tokens 库。
- **🔧 给同类需求的启发**：
  - 「**策展知识库 + 按需检索**」远比「让 LLM 凭记忆生成专业规范」可靠 —— 适用于任何「需要领域精确性」的技能（法律/医疗/合规同理）。
  - 技能要做到**跨 Agent 可移植**：用 `skill.json` 统一描述 + `npx init` 注入，一套知识服务 19 个平台，边际成本极低。
  - 检索内核保持**零重依赖 + CLI 化**，是技能能被任意 Agent 调用的前提。

## 社区口碑

- 星标增长迅猛（2025-11 创建，一年冲到 110k⭐），是「AI 设计技能」品类当前最热项目。
- 用户反馈正面：生成的 UI 一致性、配色专业度显著优于裸 Agent；吐槽点主要在「风格偏现代 SaaS，小众审美覆盖有限」。
- 与 `VoltAgent/awesome-design-md`、`JimLiu/baoyu-design` 等形成「AI 设计」技能矩阵。

## 竞品对比

| 项目 | 星标 | 差异 |
|------|------|------|
| **ui-ux-pro-max-skill（本品）** | 110k | 最全策展数据库 + 19 平台 + 检索内核 |
| VoltAgent/awesome-design-md | — | 偏设计文档/规范生成 |
| JimLiu/baoyu-design | — | 设计原则类知识，非可检索技能 |
| antvis/mcp-server-chart | — | 只覆盖图表，是本品 `chart` domain 的子集 |
| nexu-io/open-design | — | 设计资源聚合，非 Agent 技能 |

> 本品的护城河是「**策展数据的规模 + 检索内核 + 跨平台注入**」三位一体；竞品多在单一维度（图表/文档/原则）发力。

## 核心研判

- **价值**：把「设计审美」从玄学变成「可检索知识」，是 AI 编码技能工程化的重要范式样本；其「轻量 RAG」架构对其他专业领域技能有强复制价值。
- **风险**：① 策展数据需持续维护（设计趋势迭代快）；② 风格覆盖偏向主流，长尾审美不足；③ 本质依赖 LLM 最终落地质量。
- **趋势**：「领域策展知识库 + 按需检索」会成为专业 Agent 技能的标准架构；未来竞争在「数据质量 × 检索精度 × 跨平台广度」。
- **给开发者启发**：做一个高价值技能，**先建结构化知识库，再写检索与注入**；Keep the retrieval kernel dependency-free and CLI-friendly.

## 关键文件速查

- `skill.json` —— 技能清单（版本/平台/install 指令/关键词）
- `CLAUDE.md` —— 技能使用指南与 search 命令说明
- `src/ui-ux-pro-max/scripts/search.py` —— 检索内核（CLI 领域检索）
- `src/ui-ux-pro-max/data/` —— 策展数据库（风格/配色/字体/图表/UX 准则）
- `cli/` + `scripts/` —— `npx ui-ux-pro-max-cli init` 注入逻辑
- `docs/` —— 各平台集成文档
