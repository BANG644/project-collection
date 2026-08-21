# agent-substrate/substrate 深度调研

> 调研日期：2026-08-22 ｜ 调研方式：gh API 抓取 README + 仓库树 + 命令/文档路径核验
> 星标：1,571 ⭐ ｜ 语言：Go ｜ 协议：Apache-2.0 ｜ 默认分支：main ｜ 归属：Google（非官方支持产品）
> ⚠️ 项目处于早期开发，API 几乎必然变更，向后兼容无保证。

## 一、项目定位

Agent Substrate（内部代号 **ATE / Agentic Infrastructure**）是 Google 开源的**大规模 Agent 部署运行时（runtime）**——一个**高性能、高密度**的控制平面，为 Agent 沙箱提供完整生命周期管理：亚秒级 resume/suspend、在少量物理 worker 上**重度多路复用（oversubscription）**大量 actor。

一句话：它不教你"怎么写 Agent"，而是解决"**怎么把成千上万个有状态 Agent 跑在同一堆机器上还不崩**"——把 Agent 当 actor，把 worker 当可调度资源池。

## 二、项目亮点（差异化）

1. **Actor/Worker 解耦的重度多路复用**：核心洞察是 Agent 类应用"大部分时间闲置"，于是把大量 actor 映射到少量常驻 worker，demo 中 **~250 个有状态 actor 跑在 8 个物理 pod 上（30x+ oversubscription）**。
2. **亚秒级状态快照/恢复**：通过完整状态快照（volatile RAM 工作记忆 + 文件系统）实现 suspend/resume，跨休眠周期完美保留终端与文件系统状态。
3. **框架/Harness 无关**：底层用 gVisor microVM 管理标准 OCI 容器，因此可宿主任意栈的 Agent——原生支持 ADK、LangChain、Claude Code/Codex、MCP server。
4. **构建于 Kubernetes 之上**：复用 Pod / Pod autoscaling，在其上叠加 Agent 专属调度与控制，降低延迟；同时让 agentic / inference / training 的 RL 场景能做整体基础设施优化。
5. **多沙箱技术统一**：同时支持 microVM（cloud-hypervisor）与 gVisor，所有沙箱类型提供一致的 lifecycle 操作。

## 三、核心架构

控制平面由多个 Go 命令组成（见 "Tour/Commands"）：

- **`cmd/ateapi`**：核心控制平面 API server（gRPC），管理 actor/worker 生命周期、调度、快照。
- **`cmd/atelet`**：节点级 DaemonSet，监督物理 worker pod，协调 snapshotting、状态转移。
- **`cmd/atecontroller`**：K8s controller，调谐 WorkerPool 与 ActorTemplate 自定义资源（CRD）。
- **`cmd/atenet`**：合并的网络控制器，提供 DNS + Envoy 路由 + proxy sidecar——动态把入站流量路由到被 suspend/resume 的 actor。
- **`cmd/ateom-gvisor` / `cmd/ateom-microvm`**：沙箱 pod 内部的 helper，执行 `runsc` checkpoint/restore（gVisor）或将 actor 作为 cloud-hypervisor VM 运行（microVM）。
- **`cmd/kubectl-ate`**：CLI，面向用户的资源管理入口。
- **`cmd/podcertcontroller`**：为上游 K8s 尚未合入的 Pod Certificate signer 提供 polyfill。

关键概念（Glossary）：**Actor**（被托管的应用，如一个 Agent 实例）、**Atespace**（actor 命名空间，创建 actor 前必须先建）、**ActorTemplate**（actor 模板）、**WorkerPool**（物理 worker 池）、**Worker**、**ate-api-server / atenet / atelet / ateom**。

多路复用机制：actor 空闲时其 worker 被回收去跑别的 actor；当请求到达，router 通过 **Request Parking** 把入站请求"停泊"在 worker 池饱和时，而非直接返回 503。

## 四、应用场景与启发

- **高密度 Agent 服务**：需要同时托管海量长会话 Agent（如 coding agent、客服 Agent）的厂商，用 Substrate 把空闲算力回收，省下 30x 机器成本。
- **RL / 训练-推理-部署一体**：因为建在 K8s 上，可让 agentic、inference、training 周期共享基础设施并整体优化。
- **给同类需求的解决思路**：
  - 「无状态请求 + 有状态 actor」的**暂停/恢复 + 请求停泊**范式，是突破"每个会话占一个进程"成本墙的关键；
  - 把调度层**架在 K8s 之上而非另起炉灶**，复用成熟编排，只在 Agent 专属维度（快照、亚秒恢复、按 actor 路由）做加法——比从零写调度器务实得多；
  - 多沙箱（microVM + gVisor）统一接口，给"安全边界 vs 启动速度"提供了可切换的权衡旋钮。

## 五、源码深度解读

### 1. 控制平面 API server `cmd/ateapi/internal/controlapi/`
`controlapi` 是 actor/atespace/worker 生命周期的真相源。以 `actor.go` 为入口，`converter.go` 在 CRD 与外部 API 间转换，`syncer.go` 负责状态同步，`service.go` 暴露 gRPC。

```go
// controlapi/actor.go（简化骨架）
type ActorService struct {
    store Store          // atepg(Postgres) / ateredis(Valkey) 二选一
    scheduler *Scheduling
}
func (s *ActorService) Create(ctx, req) (*Actor, error) {
    actor := convert(req)          // converter.go: CRD <-> API
    return s.store.PutActor(ctx, actor)  // atepg/ateredis 持久化
}
```

### 2. 调度 `cmd/ateapi/internal/scheduling/scheduling.go`
Actor→Worker 的实时分配、过载时把 actor 漂移到空闲 worker，是"亚秒恢复 + 重度多路"的实现核心。`metrics.go` 采集调度指标。

### 3. 存储抽象 `cmd/ateapi/internal/store/atepg/` 与 `ateredis/`
`atepg`（Postgres，含 `schema.go` / `contract_test.go`）与 `ateredis`（Valkey）都实现同一 `Store` contract（`contract_test.go` 保证两者行为一致），让控制平面存储可插拔——这是 K8s 生态常见的「接口 + 多后端」工程实践。

## 六、社区口碑

- 出自 **Google**（ate-dev Google Group、CNCF Slack `#substrate-users`/`#substrate-dev`、每周四社区会），背书强但**明确声明非官方支持产品、无漏洞赏金资格**。
- 配套 **Agent Executor（`google/ax`）** 作为"在其上构建安全超可扩展 Agent harness"的参考实现，并有 Cloud Blog 公告——生态起点高于一般个人项目。
- 文档体系完整：`docs/architecture.md`、`glossary.md`、`api-guide.md`、`threat-model.md`、`observability.md`、`roadmap.md`、6 个 demo（counter / sandbox / claude-code-multiplex / multi-template / parking / autoscaled-workerpool）。
- 数据不可用：具体 star 增长曲线、外部评测文章本次未抓取，未编造。

## 七、竞品对比 + 核心研判

| 维度 | Agent Substrate (ATE) | E2B | Fly.io | Kubernetes + 自研调度 |
|------|----------------------|-----|--------|----------------------|
| 定位 | Agent 高密度运行时 | Agent 代码执行沙箱 | 通用应用部署 | 通用编排 |
| 有状态快照 | ✅ 亚秒级 | ✅（Firecracker） | ❌（无状态优先） | 需自研 |
| 多路复用 | 30x+ 核心特性 | 中等 | 弱 | 弱 |
| 框架无关 | ✅（OCI+gVisor） | ✅ | ✅ | ✅ |
| 成熟度 | ⚠️ 早期/不稳定 | 较成熟 | 成熟 | 成熟 |

**核心研判**：
- **优势**：把"Agent 基础设施"作为独立关注点抽象出来，且站在 K8s 肩膀上，工程起点高；Request Parking + 亚秒快照是多租户 Agent 服务的刚需。
- **风险**：① 明确 early-dev、API 必变、无向后兼容承诺；② 强绑定 GCP/K8s 生态，落地重；③ 非官方 Google 产品，长期维护承诺存疑。
- **趋势**：随着 coding/客服类长会话 Agent 规模化，"Agent 基础设施层"会从"业务自己造轮子"走向"标准件"——Substrate 与 E2B 是这条赛道的两端代表。
- **启发**：做 Agent 平台时，先把"空闲即回收 + 快照恢复 + 请求停泊"三件套设计进调度层，远比"每会话一进程 + 无上限堆机器"可持续。

## 八、关键文件路径速查

- `cmd/ateapi/` — 核心控制平面 API server（gRPC）
  - `internal/controlapi/actor.go` / `atespace.go` / `worker.go` / `converter.go` / `syncer.go` / `service.go`
  - `internal/scheduling/scheduling.go` — Actor→Worker 实时调度
  - `internal/store/atepg/`（`schema.go`/`contract_test.go`）、`internal/store/ateredis/` — 可插拔存储后端
  - `internal/actoridentity/`、`internal/oidcjwt/`、`internal/debugapi/` — actor 身份 / JWT / 调试 API
- `cmd/atelet/` — 节点 DaemonSet（supervise worker pod、snapshot）
- `cmd/atecontroller/` — WorkerPool / ActorTemplate CRD controller
- `cmd/atenet/` — DNS + Envoy 路由 + proxy（动态 actor 路由）
- `cmd/ateom-gvisor/` / `cmd/ateom-microvm/` — 沙箱内部 checkpoint/restore helper
- `cmd/kubectl-ate/` — 用户 CLI
- `cmd/benchmarking/` — Locust 压测（含 `glutton` 吃资源合成负载）
- `docs/architecture.md` / `docs/glossary.md` / `docs/api-guide.md` / `docs/threat-model.md` / `docs/observability.md` / `docs/roadmap.md`
- `demos/` — counter / sandbox / claude-code-multiplex / multi-template / parking / autoscaled-workerpool
- `hack/`（`create-kind-cluster.sh` / `install-ate-kind.sh` / `install-ate.sh` / `teardown.sh`）— 本地 kind / GKE 部署脚本
- `tools/setup-gcp` — GCP 资源制备（GKE/GCS/IAM）
