# 🦀 kvcache-ai/AgentENV — 基于 Firecracker 的分布式 Agent 沙箱平台

> 深度调研日期：2026-07-29 ｜ 数据来源：gh api 实时抓取 + `CLAUDE.md` 架构文档走读
> 一句话：kvcache-ai（ktransformers 同门）开源的 **E2B 兼容 Agent 沙箱运行时**——用 Firecracker 微虚机 + overlaybd 分层镜像 + ublk 块设备 + 内存快照，让 Agent 在隔离、可暂停/恢复/复用的环境中跑代码。

## 一、项目亮点（差异化）

- **E2B 兼容 HTTP API**：暴露与 E2B 一致的沙箱 CRUD / 快照 / 模板接口，现有 E2B 客户端可近乎零改接入——直接吃 E2B 生态。
- **Firecracker 微虚机隔离**：每个沙箱是真正的 VM（`/dev/kvm` 必需），比容器隔离更强，适合跑不可信 Agent 代码。
- **overlaybd + ublk 分层存储**：LSMT 分层镜像格式 + 用户态 ublk 块设备，只读层共享、可写层 COW，镜像拉取/启动极快。
- **内存快照（memory snapshot）**：Firecracker diff 快照打包成 overlaybd 层，pause/resume 用 ublk 文件后端内存，多沙箱共享单内存设备（引用计数）→ 页面缓存复用。
- **分布式控制面原型**：Go 写的 gateway + scheduler，支持多节点调度、心跳、P2P 制品传输，向"Agent 环境即服务"演进。

## 二、项目全景

| 维度 | 数据 |
|------|------|
| 🌐 GitHub | https://github.com/kvcache-ai/AgentENV |
| 📦 Stars | ⭐ 1,393（抓取日 2026-07-28） |
| 🏷️ 语言 | Rust（主）+ Go（控制面）+ C（ublk/overlaybd 底层） |
| 📜 License | MIT |
| 🗓️ 创建 / 推送 | 2026-07-23 / 2026-07-28 |
| 🔧 形态 | Agent 沙箱运行时（Firecracker） |

**定位**：kvcache-ai 把"Agent 执行环境"从"起个容器"升级为"可快照、可 fork、可池化、可分布"的微虚机平台。同门 ktransformers 是推理侧，AgentENV 是执行侧，合起来是"给 Agent 的本地云"。

## 三、核心架构（来自 CLAUDE.md）

存储子系统是核心，两条正交数据路径：

```
Block device 路径:  overlaybd 层 → ublk 用户态块设备 → /dev/ublkbN (VM 内)
Memory snapshot 路径: Firecracker diff 快照 → sparse mem.bin → overlaybd 层 → 只读 ublk → Firecracker 文件后端内存
```

关键组件：
- **`storage/overlaybd/`**：LSMT 分层镜像格式，可插拔后端（LocalFile/registryfs_v2/tar），zstd 随机访问跳转表。
- **`storage/ublk/`**：Linux ublk 异步块设备原语，`OverlaybdTarget` + `BasicCowTarget`（分块 COW）。
- **`storage/ublk-daemon/`**：单进程管理所有 ublk 设备，Unix socket + 长度前缀 JSON 协议，含 warm pool。
- **`src/sandbox/`**：Firecracker VM 编排、网络命名空间隔离、MMDS 元数据服务。
- **`src/orchestrator/`**：沙箱生命周期状态机（Creating→Running→…→Paused），支持 fork/pause/resume/snapshot。
- **`services/`**（Go）：gateway（反向代理 + 节点视图）+ scheduler（gRPC 调度、心跳、P2P 制品索引）。

## 四、应用场景与启发

- **Agent 代码执行后端**：给编码 Agent（Claude Code / Codex / Kimi Code）提供"炸了也不污染宿主机"的隔离执行环境，且 pause/resume 让"长任务可中断续跑"。
- **给同类需求的启发**：
  1. **快照 > 重启**：Agent 长任务用 memory snapshot 而非每次冷启动，省下的启动成本在多 Agent 并发时放大。
  2. **overlaybd 分层 + ublk** 是"镜像秒开"的关键——只读层全局共享，只写层 COW，比 docker layer 更贴近块设备。
  3. **fork 沙箱**（`fork_sandbox`）让"一个环境派生多子环境"变成一等能力，适合并行实验/评估。

## 五、源码深度解读

### 5.1 `src/orchestrator/service.rs` — 生命周期状态机

`Orchestrator` 管 create/fork/pause/resume/snapshot/delete，状态机 `Creating → Running → Forking|Snapshotting|Pausing → Paused,Resuming,Killing`；`capture_snapshot` 驱动 `Running → Snapshotting → Running`，可恢复失败回滚到 Running，terminal 失败才拆沙箱。`SandboxPersister` trait 抽象跨重启持久化——优雅关闭时把运行中沙箱 pause 持久化而非删除。

### 5.2 `storage/overlaybd/` — 分层镜像

`DiskSegmentMapping` 用 16 字节位打包记录把虚拟块区间映射到物理位置；读自顶向下解析层栈，写追加到上层。`image/image_file.rs` 是高层入口，`lsmt/file/` 下 `readonly.rs`/`readwrite.rs`/`stack.rs` 实现 LSMT 打开/合并。

### 5.3 `src/sandbox/ublk/device.rs` — `UblkDeviceManager`

进程内全局单例，包 ublk-daemon 客户端 + 节点本地共享内存设备缓存；`extra_drive.rs` 准备用户额外盘并在失败时回滚，pause/resume 后盘状态用 `drives/<id>/image.json` 导出以存活。

> 代码克制：crates 共 9 个（agentenv/aenv/linux-cap/object-store-operator/test-support/shell-util/warm-pool + 第三方 firecracker/envd 生成客户端），本文只取最能体现架构的三处。

## 六、社区口碑

- **正面**：E2B 兼容被视作"降维打击"——直接复用 E2B 客户端生态；Firecracker 隔离 + 快照被编码 Agent 社区高度期待；kvcache-ai 在推理侧的口碑（ktransformers）为项目背书。
- **争议 / 局限**：
  - 强依赖 `/dev/kvm`（Linux 独占），macOS/Windows 无法直接跑，需远端 Linux 节点——部署门槛高于 E2B 的托管服务。
  - 分布式控制面明确标注为 **prototype**，scheduler 绑定默认内存态、重启即丢（需 `redis_addr` 才 HA）。
  - 重 C/Rust/Go 多语言栈，contributor 上手成本不低。

## 七、竞品对比

| 项目 | 隔离 | 快照/fork | 兼容 | 部署 |
|------|------|----------|------|------|
| **AgentENV** | Firecracker VM | 是（内存快照+fork） | E2B API | 自托管（需 KVM） |
| E2B | Firecracker VM | 是 | 原生 | 托管/SaaS |
| Modal | 容器/gVisor | 是 | 原生 | 托管 |
| Daytona | 容器 | 部分 | 原生 | 自托管/云 |
| microsandbox | 微虚机 | 部分 | 原生 | 轻量自托管 |

**判断**：AgentENV 在"开源 + E2B 兼容 + Firecracker 深度（快照/fork/overlaybd）"上最完整；短板是 KVM 硬依赖与分布式面仍原型。

## 八、核心研判

- **优势（Moat）**：overlaybd+ublk+内存快照这套存储栈是多年系统沉淀，复制成本高；E2B 兼容让它免生态建设。
- **风险**：KVM 独占限制本地开发体验；分布式控制面原型化，距离"生产级 Agent 云"还有距离；与 E2B 托管比运维负担重。
- **趋势**：Agent 执行环境正从"容器"升级为"可快照微虚机"，AgentENV 与 E2B、Modal 同处这一浪；kvcache-ai 的"推理+执行"双线布局值得跟踪。
- **启发**：做 Agent 沙箱，先把"快照/恢复/fork"当一等公民设计，而不是事后补——AgentENV 的存储栈就是为这三者从底层重写的。

## 九、关键文件速查

| 路径 | 作用 |
|------|------|
| `CLAUDE.md` (28KB) | 架构与开发约定（最佳阅读起点） |
| `src/orchestrator/service.rs` | 沙箱生命周期状态机 |
| `storage/overlaybd/` | 分层镜像格式（LSMT） |
| `storage/ublk/` + `storage/ublk-daemon/` | 用户态块设备 + 守护进程 |
| `src/sandbox/` | Firecracker VM 编排 |
| `src/api/` + `src/api/generated/` | Axum HTTP + OpenAPI 生成 |
| `services/` (Go) | gateway + scheduler 控制面 |
| `crates/` | aenv/linux-cap/object-store-operator/warm-pool 等 |
| `Cargo.toml` / `Makefile` | 工作区与构建 |
