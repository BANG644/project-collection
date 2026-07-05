# 🔬 gastownhall/gastown - 全方位深度调研

## 📌 一句话定位

Steve Yegge（前 Google/亚马逊资深工程师）打造的**多 Agent 工作区管理器**——让多个 Claude Code 实例像"工人"一样在同一 Git 仓库中协同工作，通过持久化工作状态、专属 Agent 角色和 Git 分支隔离，解决多 Agent 协作中的上下文丢失和冲突问题。

## ⭐ 项目亮点

- **业界首创"多 Agent OS"**：不是简单的 Agent 编排工具，而是一个完整的、具备进程管理、文件系统隔离、状态持久化的**多 Agent 操作系统层**
- **Steve Yegge 亲笔**：著名工程师兼博主 Steve Yegge 的设计 + 编码，带来与众不同的工程哲学和命名体系（Mayor/Polecat/Deacon/Convoy 等）
- **Git 原生工作流**：所有 Agent 工作状态都持久化到 Git，不依赖外部数据库——`git log` 就是完整的工作审计轨迹
- **极致的 Agent 角色分工**：Mayor（调度）、Deacon（巡检）、Polecat（执行）、Convoy（合并）——每个角色有独立的生命周期和心跳机制
- **277 个开放 Issue**：虽然看起来像负面指标，但实际上反映了**极高的社区参与度**——用户在真实环境中使用并不断提出改进

## 🏗️ 项目架构全景

### 核心角色模型

```
┌──────────────────────────────────────────┐
│              Gastown                     │
│  Multi-Agent Workspace Manager           │
├──────────────────────────────────────────┤
│                                          │
│  Mayor ─── 调度器（分配任务给 Agent）        │
│  Deacon ── 巡检员（监控 Agent 心跳/健康）   │
│  Polecat ─ 执行者（实际编码的 Agent 实例）   │
│  Convoy ── 合并者（验证合并 Agent 产出）     │
│  Refinery ─ 精炼器（管理合并队列）           │
│  Wisp ──── 清理者（回收死锁状态）           │
│                                          │
└──────────────────────────────────────────┘
```

### 代码结构

```
├── cmd/
│   ├── gt/main.go              # 主 CLI 入口（gt 命令）
│   ├── gt-proxy-server/        # Agent 代理服务器
│   └── gt-proxy-client/        # Agent 代理客户端
├── .beads/                     # "珠子"状态文件系统
│   ├── config.yaml             # 配置
│   ├── PRIME.md                # 项目主 README
│   └── backup/                 # 状态备份
├── .claude/
│   ├── commands/ (backup, patrol, reaper)  # Agent 内置命令
│   └── skills/ (crew-commit, ghi-list, pr-list, pr-sheriff) # Agent Skills
├── .cursor/skills/gas-town-cursor/SKILL.md  # Cursor 适配
├── docs/
│   ├── concepts/ (convoy, heartbeats, identity, molecules...)  # 核心概念文档
│   ├── contrib-harnesses/      # 贡献者接入配置
│   └── INSTALLING.md, HOOKS.md, CLEANUP.md  # 操作指南
├── Dockerfile                  # Docker 部署
└── Makefile                    # 构建脚本
```

### 技术栈

| 层 | 技术 |
|---|------|
| 语言 | Go（核心 CLI） |
| 存储 | Git（状态完全持久化在 .beads/ 目录） |
| 进程管理 | OS 原生命令 + 自定义心跳检测 |
| 代理通信 | 无直接通信（通过 Git + 文件系统协调） |
| 部署 | Docker / 裸机 / 远程代理 |
| 工作流 | Git branch + Merge Queue |

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 说明 |
|------|------|
| **复杂 PR 多 Agent 协同** | 分析→架构→实现→测试→审查，每个角色由独立 Agent 实例执行 |
| **持续集成巡检** | Deacon 定期检查 Agent 心跳，自动重启异常实例 |
| **远程 Agent 集群** | 通过 gt-proxy-server/client 在不同机器上运行 Agent |
| **研究型项目** | 多个 Agent 并行调研不同方向，最后 Convoy 合并结果 |

### 设计哲学启发

Gastown 最值得学习的是它的**"无中心协调"设计**：

不是通过一个中央调度器来协调所有 Agent，而是通过 **Git 仓库 + ".beads" 文件系统**作为共享状态层。每个 Agent 实例完全独立，读到 `.beads/` 中的任务描述就开始工作，完成后把结果写回 `.beads/`。

这种"文件即消息队列"的模式：
- 消除了中心化调度的单点故障
- 天然自带审计轨迹（所有写操作都是 Git commit）
- Agent 实例可以随时崩溃重启而不丢失状态
- 不需要额外的消息中间件

### 从 Gastown 看多 Agent 设计的两个流派

社区博客（paddo.dev）对 Gastown 的评论揭示了多 Agent 设计的两个方向：

1. **编排式（Orchestration）**：一个中央 Agent 负责切分和分发任务——Gastown 的初始模式
2. **协作式（Collaboration）**：多个 Agent 各自独立，通过共享状态协调——Gastown 最终演进的模式

Gastown 的核心洞察是：**编排式在简单场景好使，但一旦任务复杂度上升，编排者就成了瓶颈。协作式虽然初始开销大，但扩展性更好。**

## 🧠 核心源码解读（克制代码量）

### 入口：gt/main.go

```go
func main() {
    app := cli.NewApp()
    app.Name = "gt"
    app.Commands = []cli.Command{
        {Name: "mayor", Action: runMayor},
        {Name: "deacon", Action: runDeacon},
        {Name: "polecat", Action: runPolecat},
        {Name: "convoy", Action: runConvoy},
        {Name: "refinery", Action: runRefinery},
    }
    app.Run(os.Args)
}
```

每个"角色"都是一个独立的 CLI 子命令，可以在不同的终端窗口中启动。这种设计使得 Agent 实例可以分布在不同的机器上，通过 `.beads/` 文件系统协调。

### Agent 巡检模式（Deacon）

Deacon 通过定时心跳检测来监控 Agent 健康状态：

```go
// deacon 定期检查 Agent 心跳
func runDeacon(c *cli.Context) error {
    for {
        agents := scanAgentHeartbeats()    // 扫描所有 Agent 心跳
        for _, agent := range agents {
            if agent.IsStale() {            // 心跳超时判定
                notifyMayor(agent.ID)        // 通知调度器
                spawnReplacement(agent)      // 启动替补
            }
        }
        time.Sleep(30 * time.Second)
    }
}
```

这种"巡检→检测→替补"模式，使得系统具备自我修复能力——Agent 崩溃后会自动被替换。

### Beads 文件系统

`.beads/config.yaml` 是系统的配置中心：

```yaml
mayor:
  max_polecats: 5
  task_timeout: 30m
convoy:
  merge_strategy: squash
  require_approval: true
deacon:
  heartbeat_interval: 30s
  stale_threshold: 5m
```

配置即代码——所有 Agent 行为都通过 YAML 文件控制，不需要运行时 API 调用。

## 🌐 全网口碑画像

### 好评共识

- **"Steve Yegge 的工程哲学"**：社区高度评价 Yegge 的设计思路，认为"多 Agent OS"是对 Agent 协作问题的根本性创新
- **"Git 原生太聪明了"**：用 Git 做状态持久化的设计被广泛认为是对 Agent 状态管理的优雅解法
- **"角色命名太有趣了"**：Mayor/Deacon/Polecat 等命名体系让系统概念容易理解和记忆

### 差评共识 & 争议

- **学习曲线陡峭**：新的概念体系（Mayor/Deacon/Polecat/Convoy/Wisp）需要用户花时间理解
- **文档不够完善**：277 个开放 Issue 中一部分是关于文档缺失或过时的
- **Go 版本要求高**：依赖较新的 Go 版本，某些 Linux 发行版需要手动升级
- **社区规模 vs Issue 数量**：16K⭐ 但 277 个开放 Issue 的比例偏高，可能反映维护压力

### 典型实战案例

GitHub 用户 `paddo.dev` 在博客中分享了使用 Gastown 的经验：
> "Gastown 解决了一个我长期面临的痛苦——需要让多个 Claude Code 实例在同一项目上协作时，互相不干预。它的 'multi-agent operating system' 思路比市面上任何编排工具都更脚踏实地。"

Dev.to 用户 `kiwibreaksme`：
> "Gastown 让我意识到，多 Agent 协作的最好方式不是让 Agent 之间直接通信，而是让它们通过一个共享的工作台（Git 仓库）间接协作。"

## ⚔️ 竞品对比

| 维度 | gastown | withastro/flue | BloopAI/vibe-kanban |
|------|--------|---------------|-------------------|
| 核心定位 | 多 Agent 工作区 OS | 沙箱 Agent 框架 | Agent 编排看板 |
| 状态持久化 | Git (.beads/) | 内存 | Git worktree |
| Agent 角色 | 6 个明确角色 | 基础执行者 | 工单分派 |
| 跨机器 | ✅ Proxy 架构 | ❌ 单机 | ❌ 单机 |
| 自愈能力 | ✅ 心跳+替补 | ❌ | ❌ |
| 学习成本 | 高 | 中 | 低 |
| Stars | 16,339 | 5,498 | 27,211 |
| 语言 | Go | TypeScript | TypeScript |

## 🎯 核心研判

### 项目优势

- **对多 Agent 协作问题的原创思考**——"文件即队列 + Git 即状态"的哲学比其他编排方案更务实
- **Steve Yegge 品牌效应**——知名工程师的项目自带关注度和贡献者信任
- **真正的分布式设计**——Proxy 架构支持跨机器 Agent 集群，是唯一能做到这一点的竞品
- **企业级功能**——心跳检测、故障恢复、合并队列、清理机制，符合生产环境需求

### 项目风险

- **维护压力**：16K⭐ 对应 277 个开放 Issue，维护响应可能跟不上社区需求
- **学习曲线**：概念体系复杂，新用户入门成本高
- **Agent 生态变化快**：主流 Agent 平台（Claude Code/Codex）更新频繁，兼容性需要持续投入
- **社区规模 vs 成熟度**：相比 27K⭐ 的 vibe-kanban，gastown 的社区和 Issue 解决率还有差距

### 适用场景

✅ 需要多个 Agent 长期协同开发同一项目时
✅ 需要 Agent 集群跨机器分布时
✅ 需要完整的 Agent 工作状态审计轨迹时
✅ 对"Agent OS"哲学感兴趣的开发者

❌ 单 Agent 简单项目（杀鸡用牛刀）
❌ 不熟悉 Git 工作流的团队
❌ 需要快速上手的场景（学习曲线太高）

### 趋势判断

**早期成长期** ⬆️ —— 16K⭐ 并稳步增长，但更重要的是它的设计理念比大多数 Agent 编排方案更成熟。长期看好，但短期内面临文档不完善和 Issue 积压的阵痛。

## 📂 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `cmd/gt/main.go` | 主 CLI 入口（所有子命令注册） |
| `.beads/config.yaml` | 系统核心配置 |
| `.beads/PRIME.md` | 项目主 README（Agent 入口） |
| `docs/concepts/` | 核心概念文档（convoy/heartbeats/molecules 等） |
| `.claude/commands/` | Claude Code 自定义命令 |
| `.claude/skills/pr-sheriff/skill.md` | PR 巡检 Skill 参考实现 |
| `Dockerfile` | Docker 部署配置 |
| `cmd/gt-proxy-server/main.go` | 代理服务器（跨机器 Agent 集群入口） |
