# manaflow-ai/cmux — 深度调研

> 调研日期：2026-10-08 ｜ 来源：GitHub Trending（当日新增，未入库）
> ⚠️ star 数 27.8k 短期激增，疑似 viral，引用时建议打折看待。

## 1. 项目定位（一句话）
cmux 是一个**为 AI 编程 Agent 打造的 macOS 原生终端**——基于 Ghostty（libghostty 渲染），用侧边栏标签页 + 通知环 + 内嵌可编程浏览器，把多 Agent 会话变成"看得见、叫得应、可脚本化"的工作面。

## 2. 项目亮点（差异化，开篇呈现）
- **原生 Swift/AppKit，非 Electron**：启动快、内存低；渲染复用 libghostty，直接读 `~/.config/ghostty/config` 的主题/字体/配色，Ghostty 用户零迁移成本。
- **通知环 + 侧边栏元数据**：每个 workspace 的标签页显示 git 分支、关联 PR 状态/编号、工作目录、监听端口、最新通知文本；Agent 等待输入时面板亮蓝环、侧栏高亮，`Cmd+Shift+U` 跳最近未读。
- **内嵌可编程浏览器**（API 移植自 vercel-labs/agent-browser）：Agent 可快照无障碍树、取元素引用、点击、填表、eval JS，把 dev server 验证留在终端旁。
- **完全可编程**：CLI + Unix socket API 可创建 workspace、开 split、发键击、读屏、截图、驱动浏览器；`cmux.json` 自定义命令、`cmux-skills` 开放技能集合。
- **多 Agent 编排可见化**：Claude Code Teams / oh-my-opencode 多模型编排的子 agent 直接变成原生 split，而非隐藏后台进程。

## 3. 核心架构
一句话哲学："**cmux is a primitive, not a solution**" —— 只给终端+浏览器+通知+workspace+splits+tabs+CLI 原始积木，不强制工作流。

```
cmux (Swift/AppKit, libghostty)
 ├─ Terminal surface  ← 读 Ghostty config（主题/字体/快捷键）
 ├─ Sidebar (垂直 tabs: git/PR/wd/port/last-notify)
 ├─ Notification (OSC 9/99/777 转义序列 + `cmux notify` CLI + agent hooks → 蓝环/角标/弹窗/桌面通知)
 ├─ In-app Browser (agent-browser API: a11y tree / click / fill / evalJS)
 ├─ SSH workspace (`cmux ssh` → 远程 network 透传, 拖图 scp 上传)
 └─ Programmable layer (CLI + Unix socket: create/split/send-key/drive-browser)
```
通知核心：捕捉标准终端转义序列 OSC 9/99/777，或经 `cmux notify` 接入 Claude Code/OpenCode 等 agent hooks；任意支持 hooks/OSC 的 agent 都能触发。

## 4. 应用场景与启发
- **给同类需求的解法**：多 Agent 并行时"哪个会话在等我"是真实痛点。cmux 的启发是——**不要做又一个 GUI 编排器，而是把通知/可见性做进终端原语**，用 OSC 转义序列这层"已有标准"而非私有协议打通 agent 与 UI。
- 远程开发：`cmux ssh user@remote` 建远程 workspace，浏览器 pane 走远程网络、localhost 直接可用；拖图进远程会话经 scp 上传。
- 会话恢复：重开时还原窗口/workspace/pane/工作目录/尽力 scrollback；配合 `cmux local-tmux`/`ssh-tmux` 做真正的 live detach/reattach。

## 5. 源码深度解读
**① Swift Package 分层（Packages/）**
`Packages/` 仅 `Shared / iOS / macOS` 三层——`macOS` 是主 App 壳、`Shared` 放跨平台逻辑、`iOS` 预留移动端。这种与 Xcode `.xcode-version`/`.asc`(asc 证书) 配套的纯 SwiftPM 结构，区别于 Electron/Tauri 系，是"快而轻"的工程根基。

**② 通知与 agent hook 桥（CLI + socket）**
README 明确：`cmux notify` CLI 可被接到 agent hooks。关键不是某段源码，而是**把"agent 等待人类"这一事件标准化为 OSC 转义 + CLI 触发**——任何 agent（Claude Code/Codex/OpenCode/pi）都能零侵入接入，无需改 agent 本体。

**③ 浏览器自动化面（agent-browser 移植）**
内嵌浏览器 API 直接移植 vercel-labs/agent-browser，提供 `snapshot a11y tree / click / fill / evalJS / read console+network`。Agent 用它"自己验证自己改的网页"，是 cmux 区别于普通多路复用器的杀手锏。

## 6. 社区口碑
- 当日 Trending 高曝光（27.8k⭐、2.4k forks、3190 open issues——issue 多说明社区活跃也在快速反馈）；作者自述"并行跑大量 Claude Code/Codex，原生通知无上下文"的真实痛点驱动，共鸣强。
- "primitive not solution" 的克制哲学在 HN/社媒获赞，被认为"对抗封闭 agent IDE 的正确路线"。
- 争议点：仅 macOS、GPL 但 GitHub license 检测为 NOASSERTION（LICENSE 文件可能非标准 SPDX 头，README 宣称 GPL）——合规声明待核实。

## 7. 竞品对比 + 核心研判
| 维度 | cmux | tmux | Ghostty | Warp/Zed | Zellij |
|------|------|------|---------|-----------|--------|
| GUI 侧边栏/通知 | ✅ 原生 | ❌ | ❌ | 部分 | ❌ |
| 内嵌可编程浏览器 | ✅ | ❌ | ❌ | 部分 | ❌ |
| Agent hook 通知 | ✅ OSC+CLI | 需自配 | ❌ | 部分 | ❌ |
| 原生性能 | ✅ Swift | ✅ C | ✅ | Electron 重 | ✅ Rust |

**研判**：cmux 抓住的是"agent 时代终端的可见性/可唤性缺口"，定位精准且工程克制。最大护城河是**原生 + Ghostty 兼容 + 可编程原语**的组合，而非功能堆叠。风险：① 仅 macOS，Windows/Linux 用户无福；② star 激增含 viral 水分，需观察留存；③ 与 tmux/Ghostty 长期是"互补而非替代"，若 Ghostty 自身加 GUI 侧栏会被部分吸收。对想做"agent 工作台"的人，cmux 是最好的架构参考样本。

## 8. 关键文件路径速查
- 工程入口：`Packages/macOS/`、`Packages/Shared/`、`Packages/iOS/`、`AppIcon.icon`、`Assets.xcassets`
- Agent 集成文档：`.agents/`、`AGENTS.md`、`CLAUDE.md`、`PROJECTS.md`、`.claude/`
- 配置与扩展：`cmux.json`（用户 `~/.config/cmux/`）、`CLI/`、`Native/`、`Examples/`、`KeyboardPinningLab/`
- 文档与治理：`README.md`(多语种)、`CHANGELOG.md`、`PR-10599-AUDIT.md`、`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`
- 配套技能：`manaflow-ai/cmux-skills`（开放集合）
