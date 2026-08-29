# 🔬 tashfeenahmed/freellmapi - 全方位深度调研

> 调研日期：2026-08-30 ｜ 数据来源：GitHub API + README + 目录结构走读（gh api）
> 一句话定位：**把 34 家 LLM 免费额度聚合成一个 OpenAI 兼容 `/v1` 端点**的本地优先路由器——智能选路 + 自动故障转移 + 加密密钥，让你用「免费 tier 堆叠」跑通 AI 编码 Agent。

## 🌟 项目亮点（差异化）

1. **免费额度聚合**：把 Google/Groq/Cerebras/OpenRouter/Mistral/Cloudflare/Cohere/Zhipu/NVIDIA/HF/ModelScope 等 34 家免费 tier 叠成约 **7.4B tokens/月** 的有效算力（474 model families / 635 endpoints）。
2. **全 OpenAI 表面兼容**：`/v1/chat/completions`、`/v1/responses`（Codex 要的）、`/v1/images|videos|audio|embeddings`、`/v1/messages`（Anthropic 线）、Gemini `/v1beta`、甚至 Ollama 仿真，几乎任何 OpenAI 客户端即插即用。
3. **六种智能路由 + 故障转移**：实时给每个模型打速度/能力/可靠分，429/5xx 自动冷却重试下一节点；按 `(platform, model, key)` 学各家配额上限，永不踩 cap。
4. **本地优先 + 加密**：provider key 用 AES-256-GCM 存 SQLite、内存解密，App 只看到一个统一 `freellmapi-…` token；自带 React 仪表盘（60 语言）、MCP server、桌面托盘 App。

## 📌 项目全景

| 维度 | 观察 |
|---|---|
| 仓库 | `tashfeenahmed/freellmapi` |
| GitHub | https://github.com/tashfeenahmed/freellmapi |
| 官网 | https://freellmapi.co |
| Stars / Forks | 22,155 ⭐ / 3,102 🍴（2026-08-30 抽样） |
| 默认分支 | `main` |
| 主要语言 | TypeScript（Node 20+） |
| License | MIT（router 本体永久免费；Premium 仅售卖「实时模型目录」直播源） |
| Open issues | 70 |
| 最近活跃 | 2026-08-28 push |

## 🏗️ 核心架构

```text
OpenAI 客户端 / Claude Code / Codex / Cursor …
   │  base_url = http://localhost:3001/v1
   ↓
统一端点 (Express/Fastify on :3001)
   ├─ 智能路由器（6 策略：auto / auto:fast / auto:smart / profile / model-id / fusion）
   ├─ 每 (platform,model,key) 配额计数器（RPM/RPD/TPM/TPD）
   ├─ 故障转移：429/5xx → cooldown → 下一节点
   ├─ 自更新签名目录（每日两次从 freellmapi.co 拉取，Ed25519 校验）
   └─ 加密密钥库（AES-256-GCM in SQLite，内存解密）
   ↓
上游 34 家 provider（按启用 key 透明路由）
桌面托盘 App (desktop/) + React 仪表盘 (client/)
MCP server (/mcp) 供 Agent 自省可用模型/健康/策略
```

**关键解耦**：Router（路由+配额+故障转移）与 Provider 适配层分离；Provider 基类可扩展新方法，适配器声明自己支持哪些 surface。一次请求「最佳免费模型出，最坏情况自动降级」。

## 🔍 源码深度解读（真实路径，源自 README CONTRIBUTING）

- `server/src/providers/openai-compat.ts` — 新增 provider 的**模板基类**，定义各 OpenAI 兼容 surface 的调用方式。
- `server/src/providers/index.ts` — provider 注册装配入口，新 provider 在此接线。
- `server/src/db/index.ts` — 模型种子与配额/健康数据落库（SQLite）。
- `server/src/__tests__/providers/` — provider 适配器的测试约定。
- `client/src/i18n/locale-config.ts` 与 `client/src/i18n/locales/*.json` — 60 语言仪表盘的字典与注册逻辑（其余语言按需懒加载，RTL 自动翻转布局）。
- `desktop/` — 原生菜单栏 App，把 router + dashboard 跑在系统托盘，玻璃态弹窗显示实时请求统计。
- `docs/architecture.md` / `docs/api.md` / `docs/clients.md` — 路由内情、API 参考、各编码 Agent 接入配方（setup-claude/setup-codex/setup-aider… 等 12+ 生成器）。

> 资源占用：README 标注空闲 ~40MB RSS，Node 20+ 即可，可跑在树莓派等 ARM SBC；scope 刻意收窄（不做训练/不做自有模型）。

## 🌐 社区口碑画像

- **硬信号**：22.2K stars / 3.1K forks，70 open issues（相对体量很低，说明质量稳定）；2026-08-28 活跃，属于 2026 年夏快速上升的「免费 LLM 网关」赛道代表。
- **定位口碑**：README 自陈「personal experimentation, not production」，诚实列出局限（无前沿模型、延迟波动、无 SLA、UTC 午夜额度重置后智能下降）——这种透明性在同类「薅免费额度」项目里较罕见，加分。
- **第三方长评**：本次抓取未覆盖权威第三方横向评测，故不编造；但其 setup 生成器覆盖 Claude Code/Codex/Cline/Continue/Aider/opencode/Cursor/Zed/JetBrains 等主流 Agent，社区采用意愿强。

## ⚔️ 竞品对比

| 方案 | 优势 | 风险 / 短板 |
|---|---|---|
| **FreeLLMAPI** | 免费 tier 聚合、OpenAI 全表面、本地优先加密、MIT | 无前沿模型、依赖各家免费政策（随时变）、非生产级 |
| **OpenRouter** | 统一付费端点、模型极全、稳定 SLA | 按量付费、不聚焦免费额度 |
| **LiteLLM** | 企业级网关、多后端、可自托管、生产可用 | 配置重、不专门做「免费聚合」 |
| **Portkey** | 可观测性 + 路由、企业特性强 | 商业 SaaS 为主 |

**结论**：FreeLLMAPI 卡位「**零成本原型 + 编码 Agent 即插即用**」；若要生产/稳定，OpenRouter/LiteLLM 更合适。它本质是 LiteLLM 的「免费 tier 特化版」。

## 🎯 核心研判

### 优势
1. **零成本撬动 AI 编码**：把散落各家的免费额度合成可用算力，学生/个人 prototyping 极佳。
2. **Agent 友好**：Anthropic `/v1/messages` + Codex `/v1/responses` + MCP server，主流编码 Agent 一行接入。
3. **本地优先安全**：密钥加密、统一 token、可离线运行，隐私边界清晰。

### 风险
1. **供给侧风险**：免费 tier 随时调整/下线，路由目录需持续维护（靠 Premium 直播源 Funding）。
2. **能力天花板**：没有 frontier 模型，复杂任务质量受限；傍晚额度耗尽后智能下降。
3. **合规灰区**：README 明确「个人实验，非生产」，商用需自担各家 ToS 责任。

### 适用场景
- 个人学习、原型验证、编码 Agent 免费跑通。
- 给本地 Agent 套一层统一 OpenAI 兼容网关。
- 教学演示「LLM 路由 / 故障转移 / 配额治理」架构。

### 不适用
- 生产环境、SLA 敏感业务。
- 需要前沿模型能力的严肃任务。

## 📂 关键文件路径速查

- `server/src/providers/openai-compat.ts` — provider 模板基类
- `server/src/providers/index.ts` — provider 注册入口
- `server/src/db/index.ts` — 模型/配额数据库
- `client/src/i18n/` — 多语言仪表盘
- `desktop/` — 桌面托盘 App
- `docs/architecture.md` — 路由与局限详解

## ⭐ 三条关键发现

1. FreeLLMAPI 的巧思是「**把 34 份不稳定免费额度，包装成一个稳定统一的接口**」——价值在路由/配额/故障转移，不在模型本身。
2. 它用 Premium 直播源（Ed25519 签名目录）解决「免费 tier 每周变」的信息滞后，是可持续运维的关键设计。
3. 对 AI 编码 Agent 用户，它是「零成本接入 Claude Code/Codex/Cursor」的捷径，但务必记住其「非生产」自我定位。

## 🧪 研究方法与数据来源

- GitHub API：`repos/tashfeenahmed/freellmapi` 元数据、`/readme` 内容（53KB 完整 README）。
- 目录结构：`/contents/` 根级 listing 校验真实路径（server/、client/、desktop/、shared/、docs/）。
- 说明：具体第三方评测未逐条抓取，口碑节基于一手仓库信号，未编造外部引用。
