# 🚂 xiaotianfotos/homerail — 语音优先的本地 Agent 编排运行时（可审计 DAG）

> **仓库**: [xiaotianfotos/homerail](https://github.com/xiaotianfotos/homerail)
> **Stars**: 357 | **Forks**: 76 | **语言**: TypeScript | **License**: MIT
> **创建**: 2026-07-07 | **最后推送**: 2026-07-09 | **Open Issues**: 4
> **调研日期**: 2026-07-10 | **数据来源**: GitHub API + README + 源码树逐层解读

---

## 一、项目定位

HomeRail 是一个 **TypeScript 运行时**，把一次性的 Agent 聊天变成**可审计、可复用的工作流**。名字拆解即设计哲学：**Home**（跑在你自己的 homelab / NAS / 家庭服务器，服务住在里面的人）+ **Rail**（DAG 的轨道形状，Agent 工作沿显式边从一个节点流到下一个，而不是堆在一个聊天框里）。

核心赌注：**人的注意力是任何自动化里最稀缺的资源，所以系统应该尽量少占用它**。长期形态是一个"驻家数据中心 Agent"——语音进、生成式界面出、背后是一张 Agent DAG 在干活。当前仓库是它赖以运行的基座：DAG 引擎、CLI、语音面、以及生成式 UI 的初步形态。

---

## 二、项目亮点

1. **「聊天黑箱」→「可检视 DAG」的范式转换** — 普通 chat 是不可复现的黑盒，HomeRail 把它变成一张可 inspect、replay、improve 的图；每次 handoff 都被 trace，每次 run 都可回放。
2. **语音优先，但文本永远可用** — 语音是首选输入（占用你最少），ASR/TTS/VAD 的 Voice Surface Contract 默认中文；安静/精确场景仍可切文本。Agent 会跨轮收集意图、确认、消歧后再行动。
3. **生成式 UI 而非日志倾倒** — Agent 不为你 dump JSON/日志，而是为当下时刻生成"一眼能读"的结构化视图（widget 集合仍在随真实用例演化）。
4. **Docker Worker 隔离** — Manager + Node 作为本地服务跑；Node 用 Docker 为每个 DAG 节点起一个 Worker 容器，每次 run 共享一个 workspace，天然隔离。
5. **Agent 可读的 README** — README 本身就是 runbook，命令全是自描述的 `hr` 调用，可直接整篇丢给 Agent（Claude Code / Codex）让它照着装好、配好、验证。

---

## 三、核心架构

HomeRail 是一个 **pnpm-style monorepo**，按职责拆成多个独立包：

```
homerail/
├── homerail_cli/          # `hr` CLI（TypeScript）—— 主要操作入口
│   ├── src/cli.ts         # 命令注册
│   ├── src/dag.ts         # DAG 引擎核心
│   ├── src/commands/      # start / run / replay / scorecard / eval-run / voice / dag-* ...
│   └── tests/             # vitest 单测（dag / scorecard / resume / no-internal-hostnames ...）
├── homerail_protocol/     # 节点间通信协议（类型/序列化）
├── homerail_manager/      # 编排管理进程（调度 DAG、管理 run）
├── homerail_node/         # 节点进程（接入 Docker Worker）
├── homerail_worker/       # Worker 运行时（容器内执行单元）
├── agent-ui/              # React 生成式前端（仪表盘/视图）
└── assets/
    ├── orchestrations/    # DAG 最佳实践 SKILL + YAML 模板（2-node / 5-node / 本地部署）
    └── profiles/          # 运行时 profile 模板
```

**执行模型**：CLI `hr` 驱动 → Manager 解析 DAG → 为每个节点在 Node 上起一个 Docker Worker（共享 run workspace）→ 节点间按显式边 handoff → 每步产出 evidence/trace → run 结束生成 scorecard 并支持 `replay`。

**CLI 命令面（已暴露）**：`start` `config` `doctor` `run` `smoke` `dag supervise` `scorecard` `eval-run` `replay` `voice` `resume` `trace` `evidence` `runs` `status` `stop` `profile` `provider` `model` `llm-settings` `templates` `stats` `inject` `dag-chats` `dag-handoffs` `dag-quick` `dag-watch`。

---

## 四、应用场景与启发

**适用场景**
- 家庭/小团队本地 Agent 自动化：把"让 Agent 帮我做 X"从临时对话沉淀成可回放、可评分的固定流水线。
- 多 Agent 协作编排：多个角色（多个环境）沿 DAG 显式 handoff，且每次交接可追溯——适合"研究→草稿→复审→发布"这类多阶段任务。
- 语音驱动的家庭助手后端：语音进、生成界面出，中间 DAG 干活。

**给同类需求的解决思路（启发）**
- **"窄在人、宽在机器"的倒漏斗设计** —— 人在最窄处（只需语音/少量确认），机器在最宽处（多 Agent 多节点）。做本地 Agent 产品时，把"减少人的决策点"当一等目标。
- **DAG 优于 chat 做可审计自动化** —— 任何"我希望以后能复盘/重跑"的 Agent 流程，都该建模成图而非对话；HomeRail 的 `replay`/`scorecard`/`trace` 三件套是可复用的最小闭环。
- **Docker-per-node 隔离** —— 用"一个容器一个 DAG 节点"换取干净的副作用边界，比在单进程里靠命名空间隔离更稳。
- **README-as-runbook** —— 把文档写成 Agent 可直接执行的命令序列，等于白送一份"自部署 agent 技能"。

---

## 五、源码深度解读

### 1. DAG 引擎与命令面（homerail_cli）

`homerail_cli/src/dag.ts` 是 DAG 引擎核心；`src/commands/` 下每个 `*.ts` 对应一条 CLI 子命令，职责单一：

```ts
// 节选自 src/commands/ 的命令划分（实际文件）
dag.ts            // DAG 解析与执行编排
dag-supervise.ts  // 监督模式：长任务看门
dag-handoffs.ts   // 节点间 handoff 追踪
replay.ts         // 回放历史 run
scorecard.ts      // 本次 run 评分卡
eval-run.ts       // 评估某次 run 质量
voice.ts          // 语音面入口（ASR/TTS/VAD）
```

命令面异常完整（30+ 子命令 + 对应 vitest 测试），说明作者把它当**严肃的基础设施**在搭，而非 demo。

### 2. 语音面契约

`commands/voice.ts` 实现 **Voice Surface Contract**：抽象出 ASR / TTS / VAD 三层，默认中文，通过桌面 voice shell 提供服务；Agent 在跨轮对话里**先收集意图再行动**，避免"听到半句就开干"。

### 3. 编排包分工

`homerail_protocol`（通信契约）/ `homerail_manager`（调度）/ `homerail_node`（接入 Worker）/ `homerail_worker`（容器内执行）四包分离，符合"控制面与数据面解耦"的成熟微服务思路，也为后续分布式/多机扩展留了口子。

---

## 六、全网口碑

项目极新（创建于 2026-07-07，调研时仅 3 天，357⭐ / 76 forks）。**社区口碑数据尚在形成期，无集中评测/第三方文章（数据不可用）**。可观测的工程信号：
- 已具备完整 CLI + 单测套件（vitest）+ `doctor`/`smoke` 自检命令 + 多包 monorepo，工程完成度高于同年龄项目；
- `assets/orchestrations` 已带 DAG 最佳实践 SKILL 与多套 YAML 部署模板，说明作者想把它做成"可教 Agent 自部署"的体系；
- 4 个 open issues，社区参与刚起步。

---

## 七、竞品对比 + 核心研判

| 维度 | **HomeRail** | n8n / 工作流自动化 | AutoGen/CrewAI 多 Agent | 单纯 Agent 聊天 |
|------|-------------|-------------------|------------------------|----------------|
| 形态 | 本地 DAG 运行时 + 语音 + 生成 UI | 可视化工作流 | 代码内多 Agent | 对话 |
| 可审计/replay | ✅ trace + replay + scorecard | ⚠️ 有执行日志 | ❌ 多靠日志 | ❌ 黑盒 |
| 语音优先 | ✅ | ❌ | ❌ | 部分 |
| 本地/隐私 | ✅ 全本地 + Docker | ⚠️ 多需云端 | ⚠️ 看部署 | ⚠️ |
| 隔离模型 | ✅ 每节点一容器 | ❌ | ❌ | ❌ |
| 成熟度 | 🐣 极早期 | ✅ 成熟 | ✅ 成熟 | ✅ |

**核心研判**
- **优势**：把"可审计 DAG + 语音优先 + 本地隐私 + 容器隔离"四个稀缺属性组合得相当干净；README-as-runbook 与 DAG 最佳实践 SKILL 显示清晰的"Agent 自部署"产品直觉。
- **风险**：极早期（v0.1.0）、单一作者主导、无 release、API 仍在快速变化；生成式 UI 自承"形状还会变"。生产可用性待验证。
- **趋势**：本地优先 + 语音 + 多 Agent 编排是 2026 年明确热点。若作者能保持工程节奏并补齐文档/示例，HomeRail 有机会在"家庭/小团队本地 Agent 运行时"这一细分里占领先机。

**一句话结论**：一个野心很大、地基很正的"本地 Agent 操作系统"早期胚胎——值得持续关注，但当前只适合爱尝鲜、能读源码自己跑的人。

---

## 八、关键文件路径速查

| 路径 | 说明 |
|------|------|
| `homerail_cli/src/dag.ts` | DAG 引擎核心 |
| `homerail_cli/src/commands/` | 全部 CLI 子命令（run/replay/scorecard/voice/dag-* …） |
| `homerail_cli/src/commands/voice.ts` | 语音面契约（ASR/TTS/VAD） |
| `homerail_protocol/` | 节点间通信协议 |
| `homerail_manager/` `homerail_node/` `homerail_worker/` | 编排/节点/Worker 运行时 |
| `agent-ui/` | React 生成式前端 |
| `assets/orchestrations/` | DAG 最佳实践 SKILL + YAML 部署模板 |
| `ROADMAP.md` | 长期路线图 |
