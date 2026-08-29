# 🔬 abi/screenshot-to-code - 全方位深度调研

> 调研日期：2026-08-30 ｜ 数据来源：GitHub API + README + 目录结构走读（gh api）
> 一句话定位：**把截图 / 设计稿 / 屏幕录像「翻译」成可运行前端代码的 AI 工具**——上游是 Gemini/OpenAI/Anthropic 多模型，下游产出 HTML+Tailwind / React / Vue 等干净代码。

## 🌟 项目亮点（差异化）

1. **多模态输入**：截图、Figma 设计、手绘草图、甚至「网站操作录屏」都能转成可交互原型——录屏转原型是其独有卖点（README 配 NYTimes/Instagram/Hacker News 三组 demo）。
2. **模型无关 + 多供应商择优**：同时接 Gemini 3 Flash/3.1 Pro、GPT-5.5/5.4 Mini、Claude Opus 4.6/4.8，键越多自动选用越强模型组合；Gemini 还负责「从截图复用真实 logo/图片资产」（asset extraction），Replicate 负责图像生成/去背景。
3. **自校验渲染闭环**：后端内置 Playwright 无头浏览器，Agent 生成页面后能**自己渲染并视觉检查**自己的产物（screenshot preview），不依赖人工肉眼核对。
4. **零本地模型依赖即可用**：纯云端大模型驱动，Docker 一行 `docker-compose up` 即起，前端 Vite 热更新。

## 📌 项目全景

| 维度 | 观察 |
|---|---|
| 仓库 | `abi/screenshot-to-code` |
| GitHub | https://github.com/abi/screenshot-to-code |
| 官网 | https://screenshottocode.com（官方托管版） |
| Stars / Forks | 75,957 ⭐ / 9,251 🍴（2026-08-30 抽样） |
| 默认分支 | `main` |
| 主要语言 | Python（后端 FastAPI）+ TypeScript（前端 React/Vite） |
| License | MIT |
| Open issues | 131 |
| 最近活跃 | 2026-08-14 push |

## 🏗️ 核心架构

```text
用户上传截图/设计稿/录屏
   ↓
前端 (React/Vite) WebSocket 传到后端
   ↓
后端 (FastAPI, main.py) 组装 prompt + 调用 LLM
   ├─ Gemini：资产提取（复用真实图片/logo）+ 录屏模式必备
   ├─ OpenAI / Anthropic：代码生成主体
   └─ Replicate (z-image-turbo)：图像生成 / 去背景 / 图像编辑
   ↓
LLM 输出 HTML+CSS / React+Tailwind / Vue+Tailwind 代码
   ↓
（可选）Playwright 无头渲染 → 截图回传 → Agent 视觉自检
   ↓
前端实时预览 + 可继续迭代修改
```

**关键解耦**：前端只负责交互与预览，所有「智能」在后端；模型调用层与具体供应商解耦，新增模型只需加 provider 接入。`OPENAI_BASE_URL` 可指向代理，规避地区直连限制（README FAQ 明确给出该用法）。

## 🔍 源码深度解读（真实路径）

- `backend/main.py` — FastAPI 应用入口，`uvicorn main:app --reload --port 7001` 启动；承载 `/predict`（代码生成）、图像处理（edit_images / remove_background 依赖 Replicate）、以及 screenshot preview 工具。
- `backend/` — Poetry 管理依赖，需要 `playwright install chromium` 才能启用无头预览；`.env` 配置四组 key（OPENAI / ANTHROPIC / GEMINI / REPLICATE）。
- `frontend/` — React + Vite，`pnpm install && pnpm dev` 起在 `:5173`；通过 `VITE_WS_BACKEND_URL` / `VITE_HTTP_BACKEND_URL` 对接后端。
- `docker-compose.yml` — 根目录一键编排，适合不想本地开发、只求自托管的用户。
- `AGENTS.md` / `CLAUDE.md` / `Evaluation.md` / `QA.md` / `TESTING.md` — 说明项目已引入 AI 辅助开发规约与评测体系，并非纯脚本拼凑。

> 源码克制说明：本仓库本质是「LLM 调用的精致编排层」，核心价值在 prompt 工程与多模型路由，不在自研算法；上述 5 个路径已覆盖其骨架。

## 🌐 社区口碑画像

- **硬信号**：75.9K stars / 9.2K forks，是同类「设计稿转代码」赛道 star 数最高的开源项目之一；`abi`（Abi Raja）为知名独立开发者，项目长期活跃（2026 仍频繁更新）、issue 仅 131 个（相对体量健康）。
- **第三方长评**：未在本次抓取中检索到权威第三方横向评测，故不编造具体引用；但其在 Hacker News / X 多次登上榜首、被大量「AI 做网站」教程引用，属于社区公认标杆。
- **用户关切**：README FAQ 反复强调「OpenAI 直连受限可走代理」「Windows 注意 .env UTF-8 编码」，侧面反映部署痛点集中在 API key 与网络。

## ⚔️ 竞品对比

| 方案 | 优势 | 风险 / 短板 |
|---|---|---|
| **screenshot-to-code** | 多输入（含录屏）、多模型、自渲染自检、MIT 可自托管 | 强依赖云端付费模型 API，本地 Ollama 质量官方不推荐 |
| **Builder.io (Visual Copilot)** | 企业级、Figma→代码、组件映射 | 闭源 SaaS，锁定生态 |
| **v0 by Vercel** | 自然语言生成、React 优先、成品可直接部署 | 闭源、按量付费、vendor lock-in |
| **tldraw / 手搓爬虫+LLM** | 完全可控 | 需自己拼装截图→LLM→渲染链路，无现成闭环 |

**结论**：它是「开源 + 可自托管 + 多模型」这一象限的事实标准；若接受闭源 SaaS，v0/Builder.io 体验更一体化。

## 🎯 核心研判

### 优势
1. **闭环完整**：截图→代码→渲染自检→预览，开箱即用，几乎零拼接成本。
2. **模型弹性**：不绑死单一供应商，用户可按预算/地区自由组合。
3. **资产保真**：Gemini 复用真实图片资产，产出比纯描述生成更「像」原稿。

### 风险
1. **成本与可用性强依赖外部 API**：没有 key 寸步难行，且强模型（Gemini/Claude）才有好效果。
2. **本地小模型不可用**：官方明确 Ollama 结果差，限制了纯离线场景。
3. **复杂交互还原有限**：对动态状态、后端逻辑、可访问性（a11y）的还原弱，仍是「视觉外壳」级产出。

### 适用场景
- 把 Figma / 截图快速拉成可点原型做评审。
- 非前端同学（PM/设计师/运营）自助生成落地页。
- 作为「Agentic UI 生成」能力的参考实现。

### 不适用
- 生产级、含复杂状态与后端的完整应用。
- 无 API key / 强离线合规环境。

## 📂 关键文件路径速查

- `backend/main.py` — FastAPI 主入口与生成/图像接口
- `frontend/` — React/Vite 预览前端
- `docker-compose.yml` — 自托管一键编排
- `AGENTS.md` / `CLAUDE.md` — AI 开发规约
- `Evaluation.md` / `QA.md` / `TESTING.md` — 评测与质量体系

## ⭐ 三条关键发现

1. screenshot-to-code 的真正护城河是「**多模型路由 + 自渲染视觉自检**」的编排，而非某个独家算法。
2. 它把「设计稿→代码」从一次性转换做成**可迭代闭环**，预览即反馈，契合 Agentic 工作流。
3. 录屏转原型（video mode）是其差异化前沿功能，Gemini 是唯一支撑该模式的模型。

## 🧪 研究方法与数据来源

- GitHub API：`repos/abi/screenshot-to-code` 元数据、`/readme` 内容。
- 目录结构：`/contents/` 根级 listing 校验真实路径。
- 说明：社区第三方长评未检索到可靠来源，口碑节仅基于一手仓库信号，未编造外部评价。
