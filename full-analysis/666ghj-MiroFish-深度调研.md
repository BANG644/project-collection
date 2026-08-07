# 🔍 深度调研报告：666ghj/MiroFish

> **Stars**: 70,409 ⭐ | **Forks**: 10,985 | **语言**: Python（后端）/ TypeScript（前端）| **License**: AGPL-3.0 | **创建**: 2025-11-26 | **默认分支**: main
> **定位**：多智能体社会模拟预测引擎——用真实世界种子信息构建高保真平行数字世界，在沙箱里「预演未来」
> **调研日期**：2026-08-08（GitHub Trending）

## 一、项目亮点（差异化）

- **「群体智能镜像」预测范式**：不是训练一个预测模型，而是构建有独立人格、长期记忆、行为逻辑的数千智能体，让其在数字世界自由交互、社会演化，再从「上帝视角」注入变量推导未来轨迹。
- **双价值定位**：宏观上是决策者的零风险推演实验室（政策 / 公关预演），微观上是个人创意沙箱（推演小说结局、脑洞场景）。
- **五步可复现工作流**：Graph Building → Environment Setup → Simulation → Report Generation → Deep Interaction，每条都可被复现与交互。
- **站在 OASIS 肩上**：仿真引擎由 **CAMEL-AI 的 OASIS（Open Agent Social Interaction Simulations）** 驱动，站在成熟开源社会模拟底座上。
- **盛大集团战略孵化**：获 Shanda Group 战略支持与孵化，中文社区势能强（B 站演示、QQ 群、Trendshift 徽章）。

## 二、项目全景

MiroFish（「简洁通用的群体智能引擎，预测万物」）由 666ghj 于 2025-11-26 创建，AGPL-3.0，至 2026-08 已达 **70,409⭐ / 10,985 forks**，是今日 Trending 中星标最高的未入库项目之一。

核心理念：从真实世界抽取种子信息（突发新闻、政策草案、金融信号），自动构建高保真平行数字世界；注入变量即可精确推导未来轨迹——**在数字沙箱里预演未来，在无数次模拟后赢得决策**。

工作流：
1. **Graph Building**：种子抽取 + 个体/集体记忆注入 + GraphRAG 构建
2. **Environment Setup**：实体关系抽取 + 人格生成 + Agent 配置注入
3. **Simulation**：双平台并行模拟 + 自动解析预测需求 + 动态时序记忆更新
4. **Report Generation**：ReportAgent 带丰富工具集与仿真后环境深度交互
5. **Deep Interaction**：与模拟世界中任意 Agent 对话、与 ReportAgent 交互

演示案例：武汉大学舆论模拟（用 BettaFish 生成的舆论报告）、红楼梦丢失结局推演（基于前 80 回数十万字）、金融 / 政治预测（coming soon）。

## 三、核心架构

- **仿真底座**：OASIS（camel-ai/oasis）——开源多 Agent 社会交互模拟框架，提供 Agent 社交演化原语。
- **知识层**：GraphRAG 构建 + 个体/集体记忆注入；记忆后端用 **Zep Cloud**（免费额度够简单用）。
- **技术栈**：
  - 前端：Node.js 18+（端口 3000），npm 管理
  - 后端：Python ≥3.11 ≤3.12（端口 5001），用 `uv` 包管理、自动建虚拟环境
  - 一键 `npm run setup:all` 装齐前后端依赖；`npm run dev` 同启
  - Docker Compose 部署（映射 3000/5001）
- **LLM 接入**：任意兼容 OpenAI SDK 的 API（推荐阿里 Qwen-plus via 百炼），`.env` 配置；高消耗建议 <40 轮模拟先试。
- **仓库结构**：`backend/`（Python 仿真 + API）、`frontend/`（Node 交互界面）、`scripts/`、`tests/`、`static/`（logo / 截图 / star-history）、`locales/`（中英双语）、`Dockerfile` / `docker-compose.yml`。

> 注：666ghj 另有 **BettaFish**（本仓库体系已入库，纯 Python 零框架多 Agent 舆情助手），二者不同——MiroFish 是更上层的「社会模拟预测平台」，BettaFish 是舆情采集/分析的下游组件。

## 四、应用场景与启发

- **舆情 / 公关零风险推演**：政策发布、品牌危机前先在数字世界跑数千 Agent 的社会演化，看舆情走向再决策——武汉大学案例已验证。
- **创意沙箱**：小说结局推演、脑洞场景模拟，把「what if」变成可交互的平行世界。
- **金融 / 政治预测（规划中）**：用种子信号 + 群体智能推演市场 / 事件走向。
- **给同类需求的解法**：想做「社会级预测」，优先用成熟社会模拟底座（OASIS）+ GraphRAG + 长期记忆（Zep），而非从零训模型——把精力放在「种子抽取 + 人格生成 + 报告 Agent」上。
- **架构借鉴**：前后端分离（Node 交互 + Python 仿真）、`uv` 自动虚拟环境、Docker 一键部署，是 LLM 应用工程的务实范本。

## 五、源码深度解读

### 1. 仿真引擎继承 OASIS（`backend/`）

README 明确致谢：仿真引擎由 `camel-ai/oasis` 驱动。MiroFish 在其上叠加「种子抽取 → 记忆注入 → GraphRAG → 人格生成 → 双平台并行模拟 → ReportAgent」流水线，而非重写社会模拟内核——**站在开源肩膀上是它快速冲 70k 星的关键**。

### 2. 记忆与图谱层（GraphRAG + Zep）

```
# 概念骨架（源自 README 工作流）
Graph Building:   seed_extract + memory_inject + GraphRAG
Environment:      relation_extract + persona_generate + agent_config
Simulation:       dual_platform_parallel + temporal_memory_update
Report:           ReportAgent(interactive tools over post-sim world)
```

个体/集体记忆注入 + 动态时序记忆更新，使 Agent 在长模拟中保持一致人格与演化逻辑；Zep Cloud 提供长期记忆后端。

### 3. 部署与运行入口（`package.json` + `docker-compose.yml`）

`npm run setup:all` 一键装齐 root+frontend+backend；`npm run dev` 同启 3000/5001；Docker 路径读根 `.env`、映射双端口。`.env.example` 给出 LLM（OpenAI SDK 格式）+ Zep 两套必填。这种「源码 / Docker 双路径 + 显式环境变量」降低了采用门槛。

## 六、社区口碑

- **星标爆发**：70k+ stars、11k forks，Trendshift 徽章，B 站演示视频（武大模拟、红楼梦推演）在中文圈传播广。
- **资本与背书**：盛大集团（Shanda）战略支持与孵化，团队公开招聘多 Agent 模拟 / LLM 方向全职与实习。
- **生态联动**：与同作者 BettaFish（已入库）形成「舆情采集 → 社会模拟预测」上下游；OASIS 开源社区为其提供技术信用。
- **使用门槛提示**：官方提醒高消耗，建议先跑 <40 轮；需自备 LLM API Key + Zep Key，非纯开箱即用的 SaaS。

## 七、竞品对比

| 维度 | MiroFish | Generative Agents (Stanford) | OASIS (CAMEL-AI) | BettaFish (同作者) |
|---|---|---|---|---|
| 定位 | 社会模拟预测平台 | 学术小型社会模拟 | 开源社会模拟底座 | 舆情采集/分析助手 |
| 记忆 | Zep + GraphRAG | 本地记忆流 | 可插拔 | 日志总线 |
| 交互 | 与 Agent 对话 + 报告 | 观察为主 | 编程接口 | 命令行 |
| 部署 | Node+Py+Docker | 研究代码 | 库 | 纯 Python |
| 商业 | 盛大孵化 | 学术 | 开源社区 | 个人 |

### 核心研判

- **优势**：70k 星盘、盛大背书、OASIS 成熟底座、五步可复现工作流 + 深度交互，是社会级「预演未来」方向最具势能的开源实现之一。
- **风险**：AGPL-3.0 对闭源商用不友好；高 LLM 消耗、需自备 Key；预测科学性（社会模拟能否真预测）尚待验证；fast-moving，API 可能变。
- **趋势**：「多 Agent 社会模拟 + 长期记忆」正从学术走向产品化，MiroFish 是中文圈这一波的旗帜。
- **启发**：做社会/舆情预测类产品，优先组合 OASIS + GraphRAG + Zep，而非自研模拟内核；注意 AGPL 对商业化的约束，闭源场景需另寻授权。

## 八、关键文件速查

- `README.md` / `README-ZH.md` — 中英双语文档与五步工作流
- `backend/` — Python 仿真引擎 + API（端口 5001）
- `frontend/` — Node.js 交互界面（端口 3000）
- `scripts/` / `tests/` — 脚本与测试
- `docker-compose.yml` / `Dockerfile` — 容器化部署
- `.env.example` — LLM（OpenAI SDK 格式）+ Zep 配置模板
- `static/` — logo / 运行截图 / star-history
