# 🔬 trycua/cua 深度调研报告

> **仓库**: [trycua/cua](https://github.com/trycua/cua)  
> **Stars**: 20,200 | **语言**: HTML（monorepo：Rust driver + Python SDK + Swift lume）| **License**: MIT  
> **组织**: Cua AI, Inc.（YC X25）  
> **最后推送**: 2026-07-19 | **最新发布**: cua-driver-rs 0.9.0（2026-07-19）  
> **调研日期**: 2026-07-20 | **来源**: README + trycua.com blog + 中文技术评测

---

## 一、项目定位（一句话）

**Cua 不是又一个 Computer-Use 模型，而是 Computer-Use 2.0 的「开源基础设施栈」**——它把沙箱环境、后台驱动、Agent 框架、跨 OS 舰队、基准评测与训练数据生成全部打包，让开发者能在安全隔离的真实桌面里跑、评测、训练计算机操作 Agent，而不用自己造轮子。

它补的是 computer-use 落地最缺的「管道（plumbing）」：环境 + 评测闭环，而非单一的 VLM。

---

## 二、项目亮点（差异化）

1. **完整基础设施栈（核心差异化）**：`cua-driver`（后台计算机操作 Agent，不夺光标）+ `cua-sandbox`（统一 VM/容器 API）+ `cua-bench`（OSWorld/ScreenSpot/Windows Arena 基准 + 轨迹录制导出）+ `lume`（Apple Silicon macOS VM 近原生）+ `cua-agent`（Agent 框架）。
2. **后台执行、不夺焦点**：cua-driver 让原生桌面应用在后台运行，Agent 点击/输入/验证而不抢占用户光标——这是多任务自动化的关键体验。
3. **4 种 Agent Loop 抽象**：`OPENAI`(computer_use_preview) / `ANTHROPIC`(Claude Computer Use) / `UITARS`(ByteDance UI-TARS) / `OMNI`(OmniParser + 任意 VLM)，切换 provider 不改应用代码。
4. **Daemon 唯一执行边界**：近期重构（#2337/#2338）把 CLI、配置、诊断、MCP 调度统一为 daemon，移除了无守护进程回退——执行边界清晰、可审计。
5. **跨 OS 舰队（Fleets）**：云端/本地统一 API 控制 Linux 容器/VM、macOS、Windows、Android、BYOI（.qcow2/.iso）。
6. **广泛客户端接入**：通过同一 CLI 与 MCP 服务器供 Claude Code、Cursor、Codex、OpenClaw 及自定义客户端使用。

---

## 三、核心架构

```
cua (monorepo)
├── libs/cua-driver/        # 后台计算机操作 Agent（Rust, cua-driver-rs 0.9.0）
│   └── nix/cua-driver      # Nix 集成测试（systemd-nspawn，启动远快于 QEMU VM）
├── libs/cua-agent/         # AI Agent 框架（4 种 agent loop）
├── libs/cua-sandbox/       # 沙箱 SDK（VM/容器统一 API）
├── cua-bench/              # 基准 + RL 环境（OSWorld/ScreenSpot/Windows Arena）
├── lume/                   # macOS/Linux VM 管理（Swift, Apple Virtualization.Framework）
├── lumier/                 # Lume VM 的 Docker 兼容接口
├── skills/gui-automation/  # GUI 自动化技能
├── docs/ blog/ samples/    # 文档与示例
└── AGENTS.md / CONTRIBUTING.md / CITATION.cff
```

**组件矩阵**：

| 组件 | macOS | Windows | Linux | Android | 说明 |
|------|:---:|:---:|:---:|:---:|------|
| cua-driver | ✅ | ✅ | ✅(X11/Wayland) | — | 后台操作 Agent |
| cua-sandbox | ✅ | ✅ | ✅ | ✅ | VM/容器统一 API |
| lume | ✅(Apple Silicon) | — | ✅(VM) | — | 近原生 macOS VM |
| cua-bench | 镜像 | 镜像 | ✅ | — | 基准/RL 环境 |

---

## 四、源码深度解读（2 个关键设计）

### 1. Agent Loop 抽象（cua-agent）

所有 computer-use 模型共享同一循环骨架，差异被封装进各 provider 专属 loop：

```text
Agent Loop（cua-agent 核心抽象）:
  capture screenshot  →  process(UI detection)  →  send(screenshot + task) to model
       →  receive action  →  execute safely in env  →  repeat until done
# 4 种实现：OPENAI / ANTHROPIC / UITARS / OMNI
# OMNI: OmniParser 做 Set-of-Marks 像素标注 → 任意 VLM 可驱动（含 Ollama 本地模型）
```

`OMNI` 模式用 OmniParser 把 UI 元素检测和推理拆开，理论上用本地 Ollama 也能驱动桌面——对「截图不想出云端」的场景价值很大。

### 2. Daemon 唯一执行边界

近期提交（#2337/#2338）把所有动作收敛到 daemon：CLI 命令、配置加载、诊断、MCP 调度全部经 daemon 派发，不再有「无守护进程回退路径」。这让执行可审计、状态可集中管理，也简化了跨客户端（MCP）的一致性。

> `cua-driver` 还支持 capability-aware browser tools（#2257）：Chromium / Electron / WebView2 / Tauri / Edge 的路由与隔离。

---

## 五、应用场景与启发（重点）

**能解决什么**：
- **安全沙箱里的 CUA Agent**：自动化测试、RPA、桌面操作流水线——Agent 在隔离 VM/容器中跑，不动主环境。
- **后台驱动多任务**：不夺光标的操作让「人+Agent 并行」成为可能（Agent 在后台填表，人继续干活）。
- **训练数据生成**：cua-bench 录制多步 Agent 轨迹、生成带 ground-truth 的 UI 截图数据集，一键导出 Arrow/Parquet 推到 HuggingFace。
- **标准化评测**：OSWorld / ScreenSpot / Windows Arena 统一跑分，知道 Agent 到底行不行。

**给同类需求的启发**：
- **Computer-use 的工程瓶颈是「环境+评测」，不是模型**。Cua 的价值 precisely 在补 plumbing——有了可靠环境 + 可复现基准，模型迭代才有意义。
- **「基础设施」比「单一模型」更持久**：模型会换（OpenAI/Anthropic/UI-TARS/本地 VLM），但环境+评测栈是横切的、可复用的。
- **后台执行 + 不夺焦点**是桌面 Agent 体验的关键分水岭，远比「截图→点击」的 demo 重要。

> 下次做「让 AI 操作电脑/手机」的需求，先评估：环境隔离、轨迹录制、评测闭环有没有——Cua 把这三者都开源了。

---

## 六、社区口碑

- **YC X25 背书**，GitHub 15K+ stars（社区活跃度 🔥），MIT 许可，3,865 commits、693 tags。
- **Cua-Bench 标准化评测**被多篇技术分析引用。官方 blog 有《A Story of Computer-Use》长文梳理 OSWorld→Windows Agent Arena→OmniParser→Claude Computer Use→Operator→Manus 的演进史，行业叙事能力强。
- **基准对比（社区整理）**：OSWorld(100 steps) UI-TARS-1.5 42.5 / OpenAI CUA 36.4 / Claude 3.7 28；Windows Agent Arena(50) UI-TARS 42.1 / Claude 29.8。
- **云 + 开源双轨**：cua.ai 提供按 credits 计费的云沙箱 + VLM 推理（Claude/Gemini/UI-TARS 等 100+ 模型），开源部分全在 GitHub。

---

## 七、竞品对比 + 核心研判

### 竞品对比

| 维度 | Cua (trycua) | Anthropic Computer Use | OpenAI Operator | OmniParser | UI-TARS | browser-use |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| 开源 | ✅ MIT | ✅(工具) | ❌闭源 | ✅ | ✅模型 | ✅ |
| 跨平台 | ✅ Mac/Lin/Win | ⚠️ Linux only | ⚠️ Web only | — | 模型 | ⚠️ Web only |
| 沙箱环境 | ✅ | ❌ | N/A | ❌ | ❌ | ❌ |
| 评测基准 | ✅ cua-bench | ❌ | N/A | ❌ | ❌ | ❌ |
| 训练数据生成 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| 定位 | 基础设施栈 | 单一能力 | 闭源服务 | 解析模块 | 模型 | Web 自动化 |

**核心区分**：Anthropic/OpenAI 给的是「模型能力」，OmniParser 给的是「解析模块」，browser-use 限于 Web；Cua 给的是**从沙箱→SDK→评测→训练**的完整路径。

### 核心研判

- **优势**：唯一把 computer-use 当「基础设施」做的开源项目；跨平台 + MIT + YC 背书；daemon 执行边界清晰；provider 无关（OMNI 接任意 VLM）。
- **风险/不足**：
  - **本地推理依赖云 VLM**：不开 cua.ai 付费云，需自备 Claude/Gemini/本地模型，本地 OmniParser 链路体验与成本需自担。
  - **工程复杂度高**：Rust driver + Python SDK + Swift lume + Nix，贡献/二次开发门槛不低。
  - **Windows/Linux driver 仍预发布**：X11/Wayland 后台输入有明确限制。
- **趋势**：computer-use 从研究基准（2024）走向消费级（Manus/Operator，2025），基础设施竞赛开启；「环境+评测」会成为 Agent 平台的标准件。
- **对同类项目的启发**：做 Agent 产品，先夯实「隔离环境 + 可复现评测 + 轨迹数据」三件套，模型能力交给生态；切勿只做 demo 级截图点击。

---

## 八、关键文件速查

| 路径 | 作用 |
|------|------|
| `libs/cua-driver/` | 后台计算机操作 Agent（Rust, cua-driver-rs 0.9.0） |
| `libs/cua-agent/` | AI Agent 框架（4 种 agent loop 实现） |
| `cua-bench/` | 基准 + RL 环境（OSWorld/ScreenSpot/Windows Arena） |
| `lume/` | macOS/Linux VM 管理（Swift, Apple Virtualization.Framework） |
| `lumier/` | Lume VM 的 Docker 兼容接口 |
| `skills/gui-automation/` | GUI 自动化技能 |
| `nix/cua-driver` | NixOS 集成测试（systemd-nspawn，替代 QEMU VM） |
| `docs/` `blog/` `samples/` | 文档、计算机使用史长文、示例 |
| `AGENTS.md` | Agent 协作约定 |
| `CITATION.cff` | 学术引用元数据 |
