# 🔬 tastyeffectco/sandboxd - 全方位深度调研

- GitHub：https://github.com/tastyeffectco/sandboxd
- 调研时间：2026-11-25
- 仓库规模：⭐ 1,002 / Go（+ React console / Electron desktop）/ MIT / 最近推送 2026-11-22 / v0.3.28（2026-11-22）
- 调研口径：以 `ARCHITECTURE.md`、`docs/isolation.md`、`docs/production-safety.md` 与控制面源码为准；README 的营销表述只作为对照

## 📌 一句话定位

sandboxd 是**单主机、可自托管的"AI 应用工厂"引擎**：一个 Go 控制面驱动 Docker，为每个应用开一个隔离沙箱、在里面跑编码 Agent、给生成的应用分配可访问的 preview URL；控制台只是它的 `/v1` API 客户端，你也可以完全绕过 UI 自己编排。

> 核心判断：真正的价值不是"一句话生成 App"，而是**把沙箱生命周期、凭证隔离、任务可回滚、预览路由这几件事压缩成一套可自托管的小栈**（Go + Docker + Traefik + SQLite，无 K8s、无队列、无独立数据库）。但它的安全边界写得比多数项目诚实：容器不是 VM，控制面等同 host-root，默认 API 无认证——上生产前必须自己补。

## ✨ 项目亮点（先看这 5 条）

1. **栈极薄**：一个 Go 程序 + Docker CLI + SQLite(WAL) + Traefik，控制台与桌面端都只是 `/v1` 客户端；这是它能在单命令安装、单主机跑起来的根本原因。
2. **凭证不进沙箱**：Agent 进程拿到的只是 `dummyKey`，真实 key/订阅 token 由控制面持有的 auth proxy 在 HTTP 层注入；源码里有显式的密钥形状变量擦除逻辑。
3. **空闲休眠 + 按需唤醒**：idle reaper 停容器省内存，pressure reaper 在主机内存紧张时停沙箱；预览 URL 首次访问走 Traefik 低优先级 catch-all，由控制面 `docker start` 并显示自动刷新的 warming-up 页。
4. **任务可回滚、应用可分叉**：每个任务有 checkpoint，支持 revert；应用支持 snapshot / fork / restore，事件时间线是一等子系统。
5. **安全模型写得异常坦白**：`docs/isolation.md` 直接写"container is a strong isolation boundary and a weak security boundary"，并列出 nftables 出口管控在自托管构建里**被编译关闭**这一事实——这种自曝短板的文档在 AI 建站工具里极少见。

## 🏗️ 项目架构全景

### 1. 一张图看懂运行时边界

```
浏览器 ──HTTP──▶ :80 Traefik ─┬─▶ s-<id>-3000  应用沙箱（开发服务器）
API/CLI ─HTTP─▶ :9090 sandboxd┼─▶ /forward-auth, /wake（低优先级 catch-all）
                              ├─◀ :9100 agent proxy（MCP 工具 + inbox）
                              │      ▲ a-<id> 常驻 Agent 容器（Hermes/OpenClaw/OpenMausBot）
                              ├─ SQLite（唯一真源）
                              ├─ reapers：idle(停容器) + pressure(内存压力)
                              └─ workspaces/<id>/（bind mount，持久）
```

- **控制面** `sandboxd`：拥有沙箱 create/list/exec/stop/destroy，`internal/docker` 直接 shell out `docker` CLI（不用 SDK）；`internal/reconcile` 启动时对 Docker 与 SQLite 做 diff，以 DB 为准收敛。
- **runtimed**：烤进基础镜像的 in-sandbox supervisor，读取应用的 `sandbox.yaml`，模型是 1 个 web 进程 + N 个 worker，各自带重启退避；任务后跑 build，无热更新的运行时按 `restart_after_task` 重启。
- **Traefik**：Docker label provider，只接管 `sandboxd.managed=true` 的容器；运行中的沙箱优先级 100，唤醒 catch-all 优先级 1。
- **Console**：React SPA，纯 `/v1` 客户端，从不直接碰 DB 或 workspace；能浏览/编辑文件、看 diff、git commit/push、管 secrets、看日志与事件、做快照恢复。
- **Desktop**：Electron 包裹同一 console；Windows 上会创建专用 WSL2 发行版并在其中装 Docker Engine，每个桌面版本 pin 一个引擎版本并支持回滚。
- **两类 Agent 要分清**：① *编码 Agent*（OpenCode / Claude Code / Codex / Pi）跑在一次性沙箱内，负责建一个应用；② *operator agents*（Hermes / OpenClaw / OpenMausBot）跑在独立的 `a-<id>` 容器，跨应用常驻，通过 MCP 调用 `list_apps` / `create_app` / `ask_app` / `share_file` / `message_user` 等工具。

### 2. 创建链：preset → manifest → 沙箱 → preview

官方 API 示例（README）：

```bash
API=http://127.0.0.1:9090
ID=$(curl -s -XPOST $API/sandbox -d '{"ports":[3000]}' | ...)
curl -s -XPOST $API/v1/sandboxes/$ID/tasks \
  -d '{"prompt":"build a todo app on port 3000","agent":"opencode"}'
# http://s-$ID-3000.preview.localhost
```

`internal/preset` 把"模板 + 生成的 sandbox.yaml + capabilities"打成创建时的 runtime preset；Free apps 目录（`console/src/catalog.ts`）里的条目 pin 到经过测试的 release，安装过程本身就是普通 `/v1` 调用 + 写 manifest + 重启，**不需要 AI 参与，也不需要核心代码为新应用开后门**——这是很值得抄的扩展机制。

## 🧠 核心源码解读（只挑架构关键点）

### ① 凭证代理：`dummyKey` + 环境变量擦除

`control-plane/cmd/runtimed/agentenv.go` 把"密钥不进沙箱"落到了两处：

```go
const dummyKey = "sandboxd-proxy-injected"

if proxy := os.Getenv("RUNTIMED_ANTHROPIC_PROXY"); proxy != "" {
    base := strings.TrimRight(proxy, "/") + "/" + agentName
    switch agentName {
    case "claude-code":
        overlay["ANTHROPIC_BASE_URL"] = base + "/anthropic"
        overlay["ANTHROPIC_API_KEY"] = dummyKey
    case "opencode":
        overlay["OPENCODE_API_KEY"] = dummyKey
        // ...
    }
}
```

`buildAgentEnv()` 随后遍历继承环境，凡是 `isSecretEnvKey()` 命中的一律丢弃：前缀 `RUNTIMED_`，后缀 `_KEY / _TOKEN / _SECRET / _PASSWORD / _CREDENTIALS / _APIKEY`。注释特别解释了为什么可以放心擦除：managed agent auth 把凭证作为 HOME 下的不透明文件（bind mount）交付，Agent 从文件读，不从继承环境读。

`control-plane/internal/authproxy/proxy.go` 的 URL 约定是 `<proxy>/<agent>/<upstream>/...`，例如 `/claude-code/anthropic/v1/messages`；`credFor(agent, up)` 从 store 取该 agent 的凭证，用 `Authorization: Bearer ...` 注入后转发。`terminalProviderError()` 还会把永久性上游失败转成人类可读提示，让 Agent 说"重新连接这个 agent"而不是抛晦涩的 401。

**借鉴点**：这是"不可信代码需要调用付费 API"这一普遍难题的干净解法——把密钥留在可信侧，用路径充当能力边界，并主动清洗子进程环境。比在容器里挂 `.env` 高一个量级。

### ② 隔离模型：文档直说容器不是安全边界

`docs/isolation.md` 原文要点：

- Agent 与它写的代码跑在沙箱容器里，带 `--dangerously-skip-permissions`；**边界是容器，不是 Agent 自身**。
- 沙箱侧加固：`--cap-drop=ALL`、`--security-opt no-new-privileges`、只读 rootfs（写入走 tmpfs + workspace）、memory/PID/fd 限制、非 root uid 1000 + `--userns` 重映射。
- 控制面挂载 host Docker socket，"effectively host-root"，因此**不能把不可信代码放到控制面**。
- **网络出口默认开放**：代码里有 nftables 出口子系统（per-sandbox source tracking、连接日志、drop metrics），但 docker-compose 构建里 `egressMgr = nil` 把它编译掉了，因为缺少 `inet sandbox_platform` 主机侧脚手架；`/v1/settings` 会诚实报告 egress `disabled`。当前实现还是 source-based，不是 per-sandbox 域名白名单。
- 多租户结论明确：容器逃逸即跨租户逃逸，建议每租户一台机器/VM，或等 VM 隔离落地。

`docs/gvisor.md` 给出近路：`SANDBOXD_RUNTIME=runsc` 切 gVisor，代价是官方自测包安装约慢 **1.7x**、系统调用密集任务约慢 **4x**。

### ③ 生产安全：三个默认必须改

`SECURITY.md` + `docs/production-safety.md` 列出：

- 控制面挂载 Docker socket = host-root，只能跑在自己控制的主机上；
- `SANDBOXD_API_AUTH_DISABLED` 默认为 `true`，API 只绑 loopback；把它暴露到公网属于配置错误，不算漏洞；
- 公共 preview 路由刻意可被 iframe 嵌套（边缘剥离 `X-Frame-Options`），**不要假设 preview URL 是私密的**。

### ④ 唤醒与回收：让一台机器承载很多闲置应用

`ARCHITECTURE.md` 描述：idle reaper `docker stop` 超时沙箱（保留文件、释放内存）；pressure reaper 在主机内存吃紧时停容器；Traefik catch-all 把对已停沙箱 preview URL 的首个请求转给控制面的 `/wake`，控制面起容器、等端口就绪，返回自动刷新的"warming up"页面。这套机制决定了它适合"很多应用、少量同时活跃"的个人/小团队场景，而不是高并发生产流量。

## 🎯 应用场景与启发

1. **个人/小团队的自托管"AI 建站台"**：一句话生成应用、给每个应用独立 URL、随时回退；代码与数据都在自己机器上。
2. **给自有产品嵌入"每用户预览环境"**：控制台只是 `/v1` 客户端，所以完全可以把 sandboxd 当后端，用自己的 UI 调 API；README 直接列了 AI app-builder、agent platform、coding playground、per-user preview 四种目标。
3. **Agent 工作台的工程范本**：想解决"不可信 Agent 怎么安全调付费 API""闲置容器怎么回收""任务怎么可回滚"，这三个问题的答案都能在它的架构文档里直接抄。
4. **反面启发**：如果你要做多租户 SaaS，不能照搬这套容器边界；要么每租户独立 VM，要么上 gVisor 并接受性能损失，同时必须打开 token auth、关掉公网裸奔的 preview。

## 🌍 全网口碑（含真实评价与风险提示）

- **Archestack**（https://archestack.com/best-of-vibe-coding/projects/sandboxd，2026-11-24 核对）强项列得具体：栈小（无 K8s/队列）、支持四种编码 Agent、凭证由代理注入、任务可 checkpoint/revert、含 snapshot/fork/restore；弱点同样直白：**Beta 0.x、容器而非 VM 隔离、API 认证默认关闭、单机设计、公网 preview 需自有域名与 TLS**。
- **Grasppy Radar**（https://grasppy.com/radar/repo/tastyeffectco/sandboxd，2026-10-27）分项打分：Alive 100 / Releases 100 / Maturity **10**（公开才 4 个月）/ Adoption 60（当时 973⭐ 69 fork）/ Activity 65（90 天 96 commits、15 个新 issue）/ Community 60（16 contributors、26 PR 合并）/ Security 80（有安全政策、无 advisories）。
- **稀土掘金《开源雷达周刊》**（https://juejin.cn/post/7692705360347398179）把它列为"技术试验阶段"，明确写：仍是 0.x/Beta；默认容器隔离不是 VM，多租户不可信代码需要额外 hardening、gVisor 或更强隔离策略。
- **SSD Nodes VPS 教程**（https://www.ssdnodes.com/learn/lang/zh-hant/self-host-sandboxd-ai-app-builder）给出运维细节：移除应用会永久删除数据；`docker image prune` 前先看 `GET /v1/apps`；建议 `SANDBOXD_API_AUTH_DISABLED` 保持 false，并强调控制面 API 实际等同 host root。
- **hub.o.cafe 项目页**（https://hub.o.cafe/project/tastyeffectco/sandboxd）中文摘要也点出 0.x 测试版、容器非 VM、多租户上线前需加固。
- **Issue 侧需求信号**：#118（按请求结算外部 API 调用，HTTP 402）、#22（生成应用 push 到用户自己的 GitHub）、#7（每沙箱磁盘配额）、#213（OpenCode 分段消息串行问题）——前三条说明"计量、归属、资源上限"是它走向产品化的三道坎。

## ⚔️ 竞品对比

| 维度 | sandboxd | Lovable / v0 / Bolt.new | E2B / Daytona | Vibe Kanban 类 Agent 工作台 | 手工 Docker + Claude Code |
|---|---|---|---|---|---|
| 部署 | 自托管单机，一条命令 | 云服务，无自托管 | 沙箱 API 服务 | 本地/云工作区 | 完全自己搭 |
| 生成应用 | 内置编码 Agent + 实时预览 | 强，云端一体化 | 不负责生成 | 负责编排不负责运行 | 自己写脚本 |
| 状态/回滚 | SQLite + snapshot/fork/revert | 平台内部，不可迁移 | 沙箱快照 | 多为 git worktree | 自己实现 |
| 凭证 | proxy 注入，不进沙箱 | 平台托管 | 调用方持有 | 视实现 | 容易漏进容器 |
| 隔离 | 容器（可选 gVisor）；非 VM | 云多租户 | 沙箱 VM/容器产品化 | 容器/分支隔离 | 取决于配置 |
| 成熟度 | 0.x，16 contributors | 商业成熟 | 产品化但收费 | 生态变动（有项目已停运） | N/A |

**结论**：sandboxd 的独特位置是"自托管 + 完整建站闭环 + 小栈"，不是功能最全，也不是最安全。E2B/Daytona 更适合把沙箱当基础设施采购；Lovable/v0 更适合不想运维的人；sandboxd 给的是"我要自己掌控机器、代码和数据"这一档选择。

## 🧭 核心研判

- **工程价值高于产品成熟度**：架构文档与 SECURITY.md 的信息密度远超同类 1K⭐ 项目，值得作为"Agent 沙箱平台怎么设计"的参考实现来读。
- **别被"隔离沙箱"四个字麻痹**：默认网络出口开放、控制面 host-root、preview 公开可嵌套、Agent 带 skip-permissions——四件事叠加，意味着它适合可信单机，不适合开放注册的多租户。
- **0.x 风险要计入**：v0.3.x 迭代很勤（11 月内多个版本），破坏性变更预期内；Grasppy 给成熟度打 10/100 不是贬低，是准确描述。
- **最值得抄的两个设计**：凭证代理（路径即能力边界 + 环境变量清洗）与"Free apps 只靠 `/v1` 调用安装"（扩展不需要改核心）。这两个模式可以脱离 sandboxd 单独复用。
- **一句话**：想快速体验"自己的 AI 应用工厂"可以装；想拿它做对外服务，先按 gVisor + token auth + 出口防火墙三件套加固，或者干脆每租户一台 VM。

## 📁 关键文件路径速查

| 路径 | 看什么 |
|---|---|
| `ARCHITECTURE.md` | 组件全景、Traefik 路由、reaper/唤醒、两类 Agent 区别 |
| `docs/isolation.md` | 真实信任模型、容器非安全边界、egress 被编译关闭 |
| `docs/production-safety.md` / `SECURITY.md` | 三个危险默认值与漏洞上报流程 |
| `docs/gvisor.md` | runsc 切换方式与 1.7x/4x 性能实测 |
| `control-plane/cmd/runtimed/agentenv.go` | dummyKey、密钥形状变量擦除、provider base URL 改写 |
| `control-plane/internal/authproxy/proxy.go` | `<agent>/<upstream>` 路径约定与 header 注入 |
| `control-plane/internal/docker/docker.go` | 控制面通过 docker CLI 管理沙箱 |
| `control-plane/cmd/runtimed/main.go` / `task.go` | 沙箱内 supervisor 与任务执行 |
| `docs/sandbox-manifest.md` | `sandbox.yaml` 的 web/workers/build/health/restart_after_task |
| `docs/openapi.yaml` | `/v1` API 契约（控制台也只用这套） |
| `console/src/catalog.ts` / `docs/free-apps.md` | 一键安装开源应用的目录与扩展规则 |
