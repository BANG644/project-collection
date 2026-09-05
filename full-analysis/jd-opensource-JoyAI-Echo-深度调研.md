# 🔬 jd-opensource/JoyAI-Echo - 全方位深度调研

> 调研日期：2026-09-06 ｜ 重写自模板化旧报告（原"四层组成"通用 boilerplate，无真实源码/架构/外链）
> 数据来源：GitHub 仓库 `jd-opensource/JoyAI-Echo` 真实 README / `echo_longvideo/Director_Agent/README.md` 抓取（stars 2,002，pushed 2026-09-04）

## 📌 一句话定位

`jd-opensource/JoyAI-Echo` 是**京东开源的长时序音视频生成 + 可交互世界模型**研究仓库，包含两个独立项目：**Echo-LongVideo**（10+ 分钟长镜头、带音视频记忆库的持续性故事生成）与 **Echo-WM**（响应连续导航的全模态世界模型），均基于 Lightricks 的 LTX-2。

> 核心判断：它既是**模型权重/推理仓库**（Echo-LongVideo / Echo-WM），也配套了**Director Agent 编排运行时**（把故事想法变成多镜头视频工作流）。技术含量在"长时序一致性"——用 paired audio-video memory bank 跨镜头携带连续性，这是短视频生成最难的一段。

## 🏆 项目亮点（差异化）

1. **长时序生成**：Echo-LongVideo 支持 10+ 分钟长镜头、多 shot 音频-视频生成，paired audio-video memory bank 跨镜头携带角色/声音连续性。
2. **可交互世界模型**：Echo-WM 是全模态世界模型，视频/环境声/音乐/语音随连续导航共同演化。
3. **Director Agent 编排**：`echo_longvideo/Director_Agent` 把"故事想法→分镜→生成→记忆审查→合并成片"做成可交互工作流，含 WebUI 与 human-in-loop 记忆审查。
4. **学术完整度**：配套 3 篇 arXiv（1.5: 2608.23383 / Echo-WM: 2608.23189 / UE Pipeline: 2609.03557）、HuggingFace 权重、ComfyUI 节点，引用链清晰。
5. **Local-first 资产架构**：工作文件留本地，只把外部服务必须访问的文件经 S3 映射外发；存储层对 vendor（bucket/endpoint）无感知，逻辑 asset URL 解耦。

## 🏗️ 核心架构

仓库拆成两个互不共享 Python 环境/权重的独立项目：

```
JoyAI-Echo/
├── echo_longvideo/   # 长视频：inference.py, configs/, prompts/, ltx-*, Director_Agent/
└── echo_wm/          # 世界模型：inference_wm.py, Gradio demo, 自带 ltx-core/ltx-pipelines
```

### Echo Director Agent 架构（来自 Director_Agent/README.md）

```
┌──────────────────────┐
│ Browser / Echo WebUI │
└──────────┬───────────┘
           │ HTTP + WebSocket
           ▼
┌──────────────────────┐       ┌────────────────────────┐
│ nanobot AgentLoop    │──────▶│ Configured LLM / VLM   │
│ + Director tools     │       │ provider               │
└──────────┬───────────┘       └────────────────────────┘
           │
           ├──────── HTTP ─────▶ Echo-compatible service
           │                         │◀────── callback ────────┘
           ▼
┌──────────────────────┐
│ Local workspace      │
│ stories · shots · memory · final media │
└──────────────────────┘
```

- **Agent runtime**：基于 [nanobot](https://github.com/HKUDS/nanobot)（HKUDS）的通用 Agent 运行时（agent loop / context / memory / skills / tools）。
- **生成服务解耦**：Director 只通过 HTTP 调独立部署的 Echo 视频服务，**不打包权重、不内嵌生成服务**；任务经 callback 异步完成，长生成不阻塞对话。
- **存储层在流程之下**：Director/memory 操作逻辑 asset URL，不含 vendor 特定 bucket/endpoint 逻辑；默认 local-first，`inline` 仅在外发时转 data URI，可选 S3 映射。

### 工作流

```
Interactive Director:  idea → story → shot prompts → generation → asset profile
   → shot acceptance → Agent Memory recommendation → Build Memory approval → next shot → merge
Quick Film: 同 Director 工作流，仅 WebUI 改变"请求多少人工审批"
```

## 🧠 源码深度解读

### 1. `nanobot/` —— Agent 运行时（agent loop + 工具 + 记忆）

`echo_longvideo/Director_Agent/nanobot/` 是复用 nanobot 的通用运行时，关键模块：
- `nanobot/agent/loop.py`：Agent 主循环（autocompact / context / memory / skills / subagent / tools）。
- `nanobot/agent/memory.py`：跨会话记忆；`nanobot/agent/tools/`：工具基类（`base.py` / `ask_user.py`）。
- `bridge/`（TypeScript）：`src/{index,server,whatsapp}.ts` + `types.d.ts` —— WebSocket / 频道桥接（含 WhatsApp 频道），把外部消息接到 AgentLoop。

Director 的工具（如 `echoGenerator`）配置在 `.config.local.json` 的 `tools` 下，`baseUrl`/`callbackBaseUrl` 指向本地 Echo 服务（默认 `127.0.0.1:8221` / `:18791`）。

### 2. `docs/director-merge-protocol.md` 与记忆审查

Director 的"记忆审查"（Memory Review）是 human-in-loop 设计：`autoApprove:false` 时工作流在下一镜头前暂停，用户在 WebUI 审核候选 Memory 槽；VLM 路由复用 `providers.<name>`，没有 VLM 时资产仍可用但不进推荐。`reference_shot_ids` 只作叙事上下文，**永不**追加进 approved Memory slots——这是"防止参考镜头污染角色记忆"的明确边界。

### 3. Workspace 布局（持久状态）

```
<workspace>/
├── director/assets/
└── works/<work_id>/
    ├── state.json · story.md · story_profile.json
    ├── shots/ · jobs/ · memory/ · outputs/
└── sessions/
```

每个 work 的全部状态落盘（`state.json` / `story.md` / `shots/`），支持断点续跑与人工审阅——符合"长时序生成必须可恢复"的工程要求。

## 🌐 全网口碑画像

- GitHub：2k⭐、京东（jd-opensource）官方开源，2026-08 至 09 密集发布（1.5 / Echo-WM / UE Pipeline），学术活跃度高。
- 学术界：3 篇 arXiv + HuggingFace 权重 + ComfyUI 生态，定位"学术与研究用途"，社区以研究者为主。
- 暂无可靠第三方长测评；但以"京东出品 + LTX-2 衍生 + 完整论文链"看，是长视频生成方向的高信号开源项目。

## ⚔️ 竞品对比

| 方案 | 优势 | 风险 |
|---|---|---|
| JoyAI-Echo | 长时序(10+min)+音视频记忆、世界模型、Director Agent 编排、论文齐全 | 仅学术/非商用（LTX-2 协议），权重需另下，部署重 |
| LTX-2 (Lightricks) | 原生基座，商用需授权 | 衍生项目商用受限 |
| 商用视频生成 API (Sora/Kling) | 开箱即用、质量高 | 不开放权重、长时序一致性受限、成本 |
| 其他开源长视频 (CogVideoX 等) | 权重大、社区大 | 多数缺"交互式 Director + 记忆审查"编排层 |

## 🎯 核心研判

**优势**：① "长时序一致性 + 音视频记忆库"是当前视频生成的真难题，Echo 给出了可复现路径；② Director Agent 把生成变成可交互、可审阅、可续跑的工作流，工程完成度高；③ Local-first + 逻辑 asset URL 解耦，部署干净。

**风险**：① **许可证为非标准 LTX-2 Community License，明确"仅学术/研究用途、禁止商用"**，商用需联系 Lightricks；② 两个子项目环境/权重互不共享，部署门槛高（conda + 权重下载 + 独立 Echo 服务）；③ 体量大、研究向，非开箱产品。

**适用场景**：长视频/世界模型学术研究；自建"故事→多镜头视频"编排管线；作为 LTX-2 衍生的实验基座。

**不适用场景**：商业产品直接集成（许可限制）；无 GPU/权重下载条件的轻量试用；要"输入一句话出成片"的纯产品体验。

## 📂 关键文件路径速查

- `README.md`：两项目总览、Quickstart、License（LTX-2 Community）。
- `echo_longvideo/README.md`：长视频推理、消费级 GPU profile、Director Agent 入口。
- `echo_longvideo/Director_Agent/README.md`：Director 架构、配置、工作流、安全。
- `echo_longvideo/Director_Agent/nanobot/`：Agent 运行时（loop/context/memory/skills/tools）。
- `echo_longvideo/Director_Agent/bridge/`：TS WebSocket/频道桥接（含 WhatsApp）。
- `echo_longvideo/Director_Agent/docs/`：director-merge-protocol.md / memory.md / websocket.md / cli-reference.md。
- `echo_longvideo/Director_Agent/.config.local.example.json`：secret-free 配置模板（`${VAR}` 启动解析）。
- `echo_wm/README.md` / `echo_wm/README_CAUSAL.md`：世界模型（双向 / chunk-causal KV-cache）。
- `THIRD_PARTY_NOTICES.md` / `SECURITY.md`：第三方声明与安全指南。

## ⭐ 三条关键发现

1. 真正的技术护城河是**"长时序一致性"**——paired audio-video memory bank 跨镜头携带连续性，这比单镜头画质更难也更有价值。
2. Director Agent 把视频生成从"一次性推理"升级为**"可交互、可审阅、可续跑的工作流"**，local-first + 逻辑 asset URL 解耦是干净的工程取舍。
3. **许可证是硬约束**：LTX-2 Community License 只允许学术/研究，商用必须走 Lightricks 授权——任何想产品化的团队先过这一关。
