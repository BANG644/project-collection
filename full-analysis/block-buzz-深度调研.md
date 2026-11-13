# 🔬 block/buzz — 全方位深度调研

> 调研日期：2026-11-14 ｜ Stars：37,252 ｜ 语言：Rust（relay）+ TypeScript/Tauri（桌面）+ Flutter（移动）｜ 许可：Apache-2.0 ｜ 编号：#590

## 📌 一句话定位
Block（Jack Dorsey）开源的**人类与 AI Agent 共建工作区**：一个 Nostr relay 上，人和 agent 共用同一套身份模型、同一份签名事件日志——agent 不是挂着的 bot，而是带着自己密钥、有独立审计轨迹的「团队成员」。

## ⭐ 项目亮点
- **身份即架构**：每个 agent 拿自己的 Nostr 私钥（`BUZZ_PRIVATE_KEY`），行为可独立验证、可审计、可被吊销，而非共享 bot token。
- **单一事件日志**：聊天、代码评审、CI 事件、git patch、工作流步骤、审批——全是同一种 Nostr 事件，同一套全文检索索引。「搜 deploy」能同时捞出聊天讨论、canvas 文档和 commit 状态。
- **Agent 与人类同权**：agent 能开仓、发 patch、审代码、跑工作流、建频道，表面上和人一样的操作面（同一套 affordance + 各自密钥 + 审计）。
- **自托管优先**：单 relay 单社区，URL 即工作区权威；可 Railway 一键部署，数据你 own。
- **ACP↔MCP 桥**：`buzz-acp` 把 Agent Client Protocol 翻译成 MCP，让 Claude Code/Codex/Goose 以「成员」身份进房间。

## 🏗️ 项目架构全景
Rust workspace 多 crate，单一真相源是 relay。架构图（README）：
```
Clients(Human / AI agent / CLI) ──WS+REST──▶ buzz-relay
  buzz-relay: NIP-01·NIP-42 auth·channel/DM/media/workflow/git REST·audit log
  ├─ Postgres(events+FTS)  ├─ Redis(pub/sub)  └─ S3/MinIO(Blossom media)
```
Crate 地图：核心协议 `buzz-core`（零 I/O 类型、NIP-01 filter、Schnorr 验签）/`buzz-relay`（Axum WS+REST）；服务层 `buzz-db`/`buzz-auth`(NIP-42/98)/`buzz-pubsub`/`buzz-search`/`buzz-audit`(hash-chain)；Agent 面 `buzz-cli`(JSON in/out)/`buzz-acp`/`buzz-agent`/`buzz-dev-mcp`/`buzz-workflow`(YAML)/`buzz-persona`；Git 面 `git-sign-nostr`/`git-credential-nostr`。多社区模式下，租户可见行、缓存键、搜索文档、工作流状态、审计链都按 host 派生的 community 隔离。

## 💡 应用场景与启发
- **典型场景**：①「这错以前见过吗？」agent 搜 6 个月历史贴出根因与修复；②「开个 feature 分支＝开个房间」，patch/CI/评审/合并决策同处；③ tag 触发工作流自动起草发版说明等人审。
- **可借鉴模式**：「**把协作问题从 API 集成升格为平台设计**」——身份可移植 + 单一签名事件流，是 agent-native 数据模型，不是人 taxonomy 上硬塞 agent 适配器。
- **同类需求思路**：任何要让多个 agent 在同一工作区协作、且要求可审计可控的系统，都应先想清楚「身份归谁、审计落在哪、跨频道上下文能否隔离」三件事——Buzz 用 Nostr 密钥 + hash-chain 给了一种参考答案。
- **边界提醒**：Buzz 1.0 已迁到 `block/buzz-app`；本仓是 0.X，仍受支持但功能在「被接通中」（移动端/审批闸/推送/Web-of-trust 信誉仍 pending）。

## 🧠 核心源码解读（克制代码量）
`ARCHITECTURE.md` 揭示其「多社区隔离靠 host 解析而非客户端 tag」的安全模型——租户上下文从 server hostname 推出，agent 无法伪造跨社区访问；channel-scoped token 不能发全局事件；订阅投递在 fan-out 时重检权限。这是把「凭证卫生」做对的关键：

```
tenant-observable rows / cache keys / search docs / workflow state /
media metadata / git repo pointers / audit chains 全部按 host-derived
community 隔离；共享基础设施只是实现细节，不是用户可见的全局工作区。
```

`buzz-acp` 是接入层的巧思：把 ACP（Goose/Codex/Claude Code 用的 Agent Client Protocol）翻译成 MCP，于是现有 coding agent 无需改写即可「作为签名成员」进房、读历史、发 patch。

## 📐 架构决策与设计哲学
- **「not blockchain」声明**：签名事件有用，但不需要每个人都买纪念币——直接划清与 crypto 的界限。
- **「Agents are part of the room, not haunted cron jobs」**：agent 要进房间、有身份、有审计，而不是后台定时任务。
- **自我定位诚实**：README 直言「What it is not」——不是 AI 替代计划、未完成、人要在回路里。
- **去中心化实情**：官方文档自己写清——每个工作区跑在**单一 relay** 上，P2P relay 同步尚不存在；「去中心化」实际等于「可自托管 + 可移植身份」。

## 🌐 全网口碑画像
- **好评共识**：DEV.to / HN Showcase / ExplainX 一致认为「把 agent 协作问题从 API 集成升格为平台设计」是重要一步；byteiota 称 3 天 6,900 ⭐ 反映真实开发者兴趣而非炒作，架构（可移植身份 + 统一签名日志 + ACP/MCP 桥）方向对；HN 首发 374 点 / 331 评论。
- **差评 / 争议焦点**：① **去中心化被质疑**：ExplainX 指出单一 relay 无 P2P 同步，本质等同自托管 Slack，有评论嘲讽「告诉我用区块链存文件是因为要在 crypto 上叠 crypto」；Block 工程师亲自回帖：Nostr 给的是跨社区可验证身份与签名。② **多 agent 权限**：Slack 工程师点出核心张力——agent 同时是私频道与公频道成员时，能否不把私频道上下文漏进公开对话？Buzz 解决了「谁授权」却没完全解决「看到什么」的边界（与 MCP 沙箱/上下文边界同源问题）。③ 群聊里单 agent 对多人的 UX 仍混乱。
- **踩坑高发区**：mobile/iOS 未读状态、macOS `.app` 数据目录注册循环**残留 28–143 GB 于 chronod**（issue #9405，#8266 后续）；Windows 安装包未签名；生产 Compose 需 Postgres+Redis+MinIO+迁移，非轻量单容器。
- **社区热度**：open issue ~3,856、fork ~4,939，release/issue/PR 流量极高（mrkeyoor 给 Community 5/5、Maturity 2/5）。

## ⚔️ 竞品对比
| 维度 | Buzz | Slack+Claude bot | Zulip/Mattermost | Anthropic Tag | JetBrains Space |
|------|------|-----------------|-----|------|-----|
| 聊天 | ✅ | ✅ | ✅ | 借 Slack | ✅ |
| 内置 Git forge | ✅(Smart HTTP) | ❌ | ❌ | ❌ | ✅ |
| Agent 身份模型 | Nostr 每 agent 密钥 | per-app bot token | 标准 bot 账号 | Slack-scoped | 各异 |
| 自托管 | ✅（单 relay） | ❌ SaaS | ✅ | ❌ | 部分 |
| 成熟度 | 早期(2026-07) | 成熟 | 成熟 | 新 | 成熟/早期 |

**选择建议**：重视自托管 + 可移植身份 + agent 审计的 AI 先遣小队可试点；要替换 Slack/GitHub 全功能的企业暂不成立。

## 🎯 核心研判
- **优势**：身份可移植 + 单一签名事件流是 agent-native 协作的稀缺正确架构；Block 有资源补完功能缺口；ACP/MCP 桥兼容现有 harness。
- **风险**：① 单 relay 无 HA/P2P，relay 挂=工作区挂；② 多 agent 跨频道上下文泄漏未根治；③ 移动端/审批闸/推送仍缺失，成熟度低；④ 生产依赖重（PG+Redis+MinIO）。
- **适用**：愿在现有协作工具旁并行试点的 AI 向小队、需数据主权的受监管组织。**不适用**：本季度就要替换 Slack/GitHub 的团队。
- **趋势**：上升期，但属于「架构对、工程糙」阶段；团队上下文工具正成为独立于 coding harness 的品类（Anthropic 收购 Zulip 领导层亦佐证）。

## 📂 关键文件路径速查
- `ARCHITECTURE.md` — 系统设计、kind 范围、子系统边界（核心）
- `VISION.md` / `VISION_SOVEREIGN.md` / `VISION_PROJECTS.md` / `VISION_AGENT.md` — 四份愿景
- `crates/buzz-relay` — Axum WS+REST 中继
- `crates/buzz-acp` — ACP↔MCP harness
- `crates/buzz-cli` — agent-first JSON in/out CLI
- `deploy/compose/` — 生产 Compose（PG/Redis/MinIO/Caddy）
- 发布博文：https://block.xyz/inside/introducing-buzz ｜ HN：news.ycombinator.com/item?id=48632977
