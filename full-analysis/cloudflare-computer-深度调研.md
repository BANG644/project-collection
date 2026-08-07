# 🔍 深度调研报告：cloudflare/computer

> **Stars**: 5,435 ⭐ | **Forks**: 279 | **语言**: TypeScript | **License**: MIT | **创建**: 2026-06-05 | **默认分支**: main
> **定位**：住在 Durable Object 里的虚拟文件系统 + 可插拔执行运行时，给每个 Agent 一台「计算机」而非一个容器
> **调研日期**：2026-08-08（GitHub Trending）

## 一、项目亮点（差异化）

- **「Agent 需要计算机，不是容器」**：Cloudflare 的核心论点——为每个 Agent 分配专属容器在全球算力下无法扩展到数十亿并发；Isolate 可无限横向扩展、毫秒启停、空闲休眠、还能派生子 Isolate 跑不可信代码。
- **单一 SQLite 支撑的虚拟文件系统（VFS）**：权威状态在 Durable Object 的 SQLite 里；isolate 路径与 container 路径看到**同一棵工作树**（git clone 在 isolate、pip install 在 container 互不割裂）。
- **一个入口，多后端**：`workspace.runtime.exec(source, { backend })` 是唯一执行入口，后端懒加载、按需选择——把「isolate OR 容器」的强制选择下沉为运行时细节。
- **三后端开箱**：Container（FUSE 挂载真实 Linux userland）、Isolate shell（`just-bash` 于 Dynamic Worker）、Isolate JavaScript（新鲜 Dynamic Worker 跑 ES module，`ws:git` / `ws:artifacts` 受信模块）。
- **可审计的执行面**：所有操作 gated / audited / observed；与 `@cloudflare/sandbox` 形成「快廉价持久 FS + 偶尔真 Linux」的互补定位。

## 二、项目全景

`@cloudflare/computer` 是 Cloudflare 在 **2026-08-03 Agents Week** 开源的**早期预览** Agent 运行时。它把「文件系统 + shell + 执行运行时」打包成一个 Workspace，实例化进任意 Durable Object：

```ts
import { Workspace } from "@cloudflare/computer";
export class Agent {
  workspace = new Workspace({ storage: this.ctx.storage });
}
```

Workspace 可注册多个后端（稳定 ID），`exec` 按任务选后端（shell 命令 or ES module）。也可完全不带后端，只拿文件系统本身。README 明确标注 **PREVIEW ONLY、API 不稳定、暂不适合生产**。

发布当天冲上 GitHub Trending #1（+2,802 stars/24h），四个月后其兄弟产品 `@cloudflare/sandbox` 才 GA（2026-04-13）。

## 三、核心架构

- **Durable Object = 权威状态**：SQLite 持有 VFS 状态，是 isolate 与 container 共享的单一真相源。
- **Container 后端**：把 SQLite 状态投射成沙箱容器内的真实 FUSE 挂载；沙箱侧 daemon（`computerd`）挂载为文件系统，经 **capnweb RPC** 通道把变更同步回 DO。完整 Linux userland、真实二进制、真实网络。
- **Isolate shell 后端**：在 Dynamic Worker 里跑 `just-bash`，经 **Workers RPC** 直连权威 Workspace——无第二存储、无同步往返。
- **Isolate JS 后端**：在新鲜 Dynamic Worker 里跑 ES module，结构化输入/结果、持久相对 import、配置库、`node:fs/promises` 走 Workspace、受信 `ws:git` / `ws:artifacts`。

性能上：computerd 的 FUSE 挂载在**元数据密集**工作超过真实磁盘，大顺序 I/O 落后（见 `docs/19_performance.md` 的 `fs-bench`）。

Monorepo 包（`packages/`）：

- `dofs` (`@cloudflare/dofs`) — DO SQLite 支撑的 VFS + 同步协议构件 + `@platformatic/vfs` 的 Node provider
- `rpc` (`@cloudflare/computer-rpc`) — capnweb 线类型 + DO 与 computerd 间共享的 server/client helper
- `computerd` (`@cloudflare/computerd`) — FUSE 挂载 + HTTP/WebSocket RPC server，跑在沙箱容器内
- `computer` (`@cloudflare/computer`) — 被 Durable Object 消费的最顶层包（WIP）
- `computer-computerd-linux-x64` — 预编译 `computerd` linux-x64 二进制的私有 Docker 镜像上下文（**镜像而非 npm 包才是发布产物**）

## 四、应用场景与启发

- **构建在 Cloudflare 上的 Agent**：想要一个横跨「快廉价」与「完整 Linux」的工作区，又不愿运维两套系统——Computer 把两者收进同一个 Workspace。
- **沙箱栈的解耦**：把「双手（执行沙箱）」与「大脑（Agent 循环）」分离是 2026 年 Agent 框架的明确转向；Computer 进一步把这个选择下沉到**每命令**粒度。
- **给同类需求的解法**：想做「Agent 运行时即原语」的产品，优先用 Durable Object 存 VFS 状态 + 多后端懒路由，而不是让用户上线前就定死 isolate/microVM/container。
- **架构借鉴**：VFS 单一真相源 + FUSE 投射 + capnweb RPC 的「状态在边缘、执行在沙箱」模式，比「每 Agent 一容器」更省算力。

## 五、源码深度解读

### 1. VFS 与同步协议（`packages/dofs`）

`@cloudflare/dofs` 是核心：DO 内 SQLite 是权威 VFS，提供同步协议构件与 `@platformatic/vfs` 的 Node provider。Container 后端就是把这棵 SQLite 树**投射**成沙箱里的真实挂载，再经 RPC 把写回同步——思路是「状态在边缘，执行在沙箱」。

### 2. capnweb 线类型与 RPC（`packages/rpc`）

`@cloudflare/computer-rpc` 定义 DO 与 `computerd` 之间的 capnweb wire types 与 server/client helper。这是 Container 后端「FUSE 挂载 ↔ DO 状态」双向同步的传输层，零拷贝、结构化。

### 3. `computerd` 守护进程（`packages/computerd`）

`@cloudflare/computerd` 是跑在沙箱容器内的 FUSE 挂载 + HTTP/WebSocket RPC server。它把 DO 的 SQLite 状态呈现为真实文件系统，并把变更经 capnweb 通道回写——是「完整 Linux userland」得以成立的落点。

## 六、社区口碑

- **发布即 Trending #1**：2026-08-03 开源，单日 +2,802 stars；同期 Cloudflare 又推 Cloudflare OS（企业级开源 Agent 工作区），HN 648 点 / 321 评论。
- **第三方定位清晰**：dreaming.press 等评测点明——isolate 冷启比容器快约 **100×**（V8 毫秒级），Container 路径仅在任务需要 Linux 时才走；计费按 10ms 活跃运行，非空闲。
- **文档真空被吐槽**：rohitraj.tech 指出 Cloudflare 自己的 Sandbox 文档**零提及** Computer，第三方对比文多无代码块；「两个运行时怎么选」官方没给决策表。
- **成熟度警告**：全网点明 PREVIEW ONLY、暂不适合生产，建议 pin 住 API 再观望。

## 七、竞品对比

| 维度 | @cloudflare/computer | @cloudflare/sandbox (GA) | E2B / Modal / Fly |
|---|---|---|---|
| Agent 得到 | 一台持久计算机（共享 FS + 多运行时） | 每次真实 Linux 盒 | 你选的一个执行环境 |
| isolate vs 容器 | Agent 每命令选，平台路由 | 固定容器 | 你上线前定 |
| 跨运行时 FS | 单一 SQLite VFS，完全一致 | 分离，需手动拷状态 | 分离 |
| 运行位置 | Cloudflare 边缘（你控制的 DO） | Cloudflare 容器 | 厂商云 |
| 成熟度 | Preview（原型） | GA（2026-04） | GA |

### 核心研判

- **优势**：把「isolate OR 容器」下沉为运行时细节、共享 VFS 跨后端一致、边缘 DO 控状态——算力效率叙事极强，契合数十亿并发 Agent 的Scaling 命题。
- **风险**：Preview 状态、API 漂移；与自家 sandbox 定位重叠、官方决策表缺失，易让开发者困惑；FUSE 大顺序 I/O 落后真实磁盘。
- **趋势**：「Agent 运行时即原语」会成云厂商标配，Computer 是 Cloudflare 用 Isolate 押注的回答。
- **启发**：做 Agent 执行沙箱时，优先「共享 VFS + 多后端懒路由」，而非让用户上线前定死执行环境；同时注意与既有 GA 产品的定位区分，别留文档真空。

## 八、关键文件速查

- `packages/dofs/README.md` — `@cloudflare/dofs`：DO SQLite VFS + 同步协议
- `packages/rpc/README.md` — `@cloudflare/computer-rpc`：capnweb 线类型
- `packages/computerd/README.md` — `@cloudflare/computerd`：FUSE 守护进程
- `packages/computer/README.md` — `@cloudflare/computer`：顶层消费包
- `docs/19_performance.md` — `fs-bench` 文件系统基准
- `examples/` — container / worker-shell / worker-javascript / think / tutorial / artifacts / assets 可跑样例
- `AGENTS.md` + `.agents/skills/` — 供 Agent 协作的仓库约定
