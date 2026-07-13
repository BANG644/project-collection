# 🔍 moeru-ai/airi — 全方位深度调研

> **调研日期**: 2026-07-14 | **Stars**: 41,798 ⭐ | **Forks**: 4,191 | **Open Issues**: 178 | **License**: MIT
> **语言**: TypeScript（pnpm monorepo）| **背景**: 复刻 Neuro-sama 的开源"数字人/赛博生命"容器
> **最新发布**: v0.11.0（2026-07-08）| **创建**: 2024-12-01（项目较老、持续活跃）

---

## 一、项目定位（一句话）

Project AIRI 是一个**自托管的 AI VTuber / 数字人容器**——目标是在浏览器、桌面、移动端跑起一个能实时语音聊天、能玩 Minecraft / Factorio、能看代码的多模态"赛博生命"，并且**你拥有它、随时随地可交互**（不像 Neuro-sama 直播结束就离线）。

## 二、项目亮点（差异化）

1. **第一天就 Web 原生**：全程基于 WebGPU / WebAudio / Web Workers / WebAssembly / WebSocket / Three.js / Live2D / VRM——所以能直接在浏览器跑、有 PWA、能上手机，而非绑死某个原生运行时。
2. **桌面版不妥协性能**：虽用 Web 技术做图形/动画/布局，桌面端（Electron）默认走原生 **NVIDIA CUDA / Apple Metal**（借 HuggingFace `candle`），无需复杂依赖管理。
3. **Brain / Ears / Mouth / Body 四件套模块化**：大脑（LLM+记忆+游戏 Agent）、耳朵（音频输入+端侧 ASR）、嘴（多厂商 TTS）、身体（VRM/Live2D 控制+自动眨眼/注视/空闲眼动），各模块独立可替换。
4. **跨 30+ LLM 厂商**：经自研 `xsAI`（类 Vercel AI SDK 但更轻）统一接入 OpenAI / Claude / Gemini / DeepSeek / Qwen / Ollama / 智谱 / 硅基 / MiniMax 等，含国内厂商。
5. **庞大子项目星系**：`@proj-airi` 组织下衍生出 unspeech（ASR/TTS 通用代理）、xsai、duckdb-wasm 驱动、airi-factorio / airi-domekeeper 游戏 Agent、mcp-launcher 等，是"一个想法长出一个生态"的典型。

## 三、核心架构

pnpm monorepo，按"能力"分包。README 的 mermaid 图揭示了核心依赖流向：

```
UI → StageUI → Stage → Core
DB1(duckdb-wasm) → DBDriver → MemoryDriver(WIP Alaya) → Memory → Core
Core → STT(unspeech) / SVRT(server-runtime)
SVRT →|玩 Factorio| Factorio Agent(RCON API + autorio)
SVRT →|玩 Minecraft| Minecraft Agent(Mineflayer)
xsAI → Core / Factorio Agent / Minecraft Agent
```

关键分层（来自包目录与图）：
- **Core（`@proj-airi/...` 核心）**：编排 LLM、记忆、语音、游戏 Agent。
- **Stage（表现层）**：`stage-web`（浏览器）/ `stage-tamagotchi`（桌面 Electron）/ 移动（Capacitor）；UI 走 `@proj-airi/ui` + `stage-ui`。
- **记忆**：浏览器内 DuckDB WASM / `pglite` 做纯本地库；`memory-pgvector` 接 PGVector；"Memory Alaya" 仍在 WIP。
- **语音链路**：`unspeech`（通用 `/audio/transcriptions` + `/audio/speech` 代理，类 LiteLLM 但专做 ASR/TTS）；TTS 支持 ElevenLabs / Azure / OpenAI 兼容 / 阿里 / 本地 Kokoro。
- **游戏 Agent**：Factorio 用 `autorio` + Factorio RCON API；Minecraft 用 `Mineflayer`。

**能力进度（当前）**：Brain 已能玩 Minecraft/Factorio/KSP(预告)、Telegram/Discord 聊天、端侧 ASR；Mouth 多厂商 TTS；Body VRM+Live2D 动画；纯浏览器本地推理（WebGPU）仍在做。

## 四、应用场景与启发

- **"多模态 Agent 表现层"的参考架构**：airi 把"大脑(LLM)/耳朵(ASR)/嘴(TTS)/身体(渲染)"拆成可替换模块，且用 `xsAI` 统一 LLM 接入——任何想做"有形象、能对话、能操作环境的 Agent"的团队，都可直接参考这个四件套切分，而不是把逻辑糊在一个 prompt 里。
- **Web 技术做重型客户端的可行性样本**：它证明 WebGPU+WASM 足以支撑"实时数字人"，桌面端再补 CUDA/Metal。对"既要跨端、又要性能"的产品，这条"Web 打底 + 原生加速可选"的路线值得借鉴。
- **子项目裂变模式**：airi 把一个核心想法（数字人）拆出 unspeech/xsai/各游戏 Agent 等独立可复用包，每个都能单独被别的项目用。想做平台型开源，这种"主项目孵化卫星包"的组织方式很高效。
- **⚠️ 注意**：仓库明确警告"**没有任何官方加密货币/代币**"，调研与二次开发时需警惕冒名 Token 诈骗。

## 五、源码解读（关键模块）

**1. 包结构即架构**（来自 `packages/` 目录）
```
packages/
├── core-agent/        core-character/   # 大脑 + 角色模型
├── audio/  audio-pipelines-transcribe/  # 耳朵（端侧 ASR）
├── model-driver-*/    # 嘴/脸驱动：lipsync / mediapipe
├── memory-pgvector/  duckdb-wasm/  drizzle-duckdb-wasm/  # 记忆层
├── scenarios-stage-tamagotchi-*/  # 桌面/浏览器表现场景
├── plugin-sdk/  plugin-protocol/  # 插件扩展协议
└── i18n/  font-*/  # 国际化与字体（含中文 CJK 字体）
```
要点：能力按"可独立发包"切分，Core 通过 `@proj-airi/*` 依赖组合，游戏 Agent 走独立子仓库（airi-factorio）。

**2. 大脑与游戏 Agent 的桥接**（mermaid 提炼）
```text
Core ──xsAI──> Factorio Agent ──Factorio RCON API──> factorio-server
Core ──xsAI──> Minecraft Agent ──Mineflayer────────> minecraft-server
SVRT(server-runtime) 负责把"玩 Factorio/Minecraft"的意图转成 Agent 调用
```
要点：`xsAI` 是统一 LLM 接入层，游戏 Agent 通过 RCON / Mineflayer 操作真实游戏进程——这是"Agent 操控 GUI/游戏"的干净抽象，比直接截图+点击更稳。

## 六、全网口碑

- **社区信号**：41.8K⭐ / 4.2K forks / 178 open issues，Discord + Telegram + 微信/QQ 多社群，Product Hunt 与 Trendshift 均有上榜；有 Crowdin 翻译项目、持续 DevLog（到 2026.03）。
- **口碑倾向**：正面集中在"开源复刻 Neuro-sama 最完整之一""Web 原生跨端""子项目生态丰富"；常见顾虑是项目早期、模块仍在 WIP（尤其 Memory Alaya、纯浏览器本地推理）、对 Vue/TS 技术栈有偏好（但欢迎 React/Svelte 贡献者开子目录）。
- **数据不可用**：具体 Twitter/YouTube 单视频播放量、Reddit 讨论评分未抓取；以上基于仓库元数据 + README 自述推断。

## 七、竞品对比 + 核心研判

| 维度 | airi (moeru-ai) | elizaOS/eliza | semperai/amica | SillyTavern |
|------|-----------------|---------------|----------------|-------------|
| 定位 | 数字人/VTuber 容器 | 通用 Agent 框架 | VRM/WebXR VTuber | 聊天前端 |
| 游戏操控 | ✅ Factorio/Minecraft | 靠集成 | ❌ | ❌ |
| 渲染 | WebGPU+VRM/Live2D | 无 | VRM/WebXR | 无 |
| 跨端 | 浏览器/桌面/移动 | 服务端 | 浏览器 | 浏览器 |
| LLM 接入 | xsAI(30+厂商) | 多 | 少 | 多 |

README 自列的近似开源项目：kimjammer/Neuro（7天复刻，完成度高）、SugarcaneDefender/z-waif（游戏强）、semperai/amica（VRM/WebXR 强）、t41372/Open-LLM-VTuber 等。

**核心研判**：
- **优势**：目前开源"能玩游戏的 AI VTuber"里最完整、跨端最广、生态最茂盛的实现；Web 原生 + 原生加速的混合路线务实；子项目裂变让能力可复用。
- **风险**：仍早期，关键模块（记忆 Alaya、浏览器本地推理）WIP；架构复杂（monorepo 多包），上手与二次开发门槛不低；需警惕冒名加密代币诈骗。
- **趋势判断**："可拥有的数字人"是陪伴型 AI 的明确方向，airi 在"开源 + 能玩游戏 + 跨端"上占位领先。若你做陪伴/虚拟主播/游戏交互 Agent，它是最该直接读源码（尤其 `core-agent` + 游戏 Agent 桥接）的参考实现。

## 八、关键文件路径速查

- `packages/core-agent/` `packages/core-character/` — 大脑与角色模型核心
- `packages/audio/` `packages/audio-pipelines-transcribe/` — 端侧 ASR（耳朵）
- `packages/memory-pgvector/` `packages/duckdb-wasm/` — 记忆层（DuckDB WASM / PGVector）
- `packages/model-driver-lipsync/` `packages/model-driver-mediapipe/` — 嘴型/脸驱动
- `packages/scenarios-stage-tamagotchi-electron|browser/` — 桌面/浏览器表现场景
- `packages/plugin-sdk/` `packages/plugin-protocol/` — 插件扩展协议
- 子项目：`moeru-ai/airi-factorio`、`moeru-ai/unspeech`、`moeru-ai/xsai`、`proj-airi/*`
- `.github/CONTRIBUTING.md` — 开发与各端（web/tamagotchi/pocket）启动说明
