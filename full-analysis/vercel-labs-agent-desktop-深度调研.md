# vercel-labs/agent-desktop 深度调研

> 调研日期：2026-11-04 ｜ 定位：让 AI Agent「看见并操作」桌面应用的计算机使用 CLI（无障碍树，非截图）
> 仓库：https://github.com/vercel-labs/agent-desktop ｜ Stars：≈12.3k ｜ 语言：Rust ｜ 许可：Apache-2.0
> 关键词：computer-use / accessibility-tree / ai-agents / cli / rust / mcp

## 一、项目定位（一句话）

agent-desktop 是 Vercel Labs 开源的**计算机使用（computer use）CLI + C 库**：它不截图、不靠视觉模型猜坐标，而是读取操作系统的**无障碍树（accessibility tree）**——macOS AX API、Windows UI Automation、Linux AT-SPI——把每个可操作元素编成带 `ref` 的 JSON 快照，让任意 AI agent 以「观察→对 ref 操作→再观察验证」的循环驱动原生桌面应用。它是 agent-browser（Web 版）的桌面孪生兄弟。

## 二、项目亮点（差异化，开篇先看）

1. **结构化观察，告别像素**：用 OS 原生无障碍树替代截图，密集应用（Slack / VS Code / Notion）自报可省 78%–96% token（官方数据）。
2. **无头默认、不抢焦点**：ref 操作默认走无障碍 API，**不移动鼠标、不抢窗口焦点**，agent 可在你继续用电脑时后台干活；`--headed` 才用物理输入。
3. **ref 契约 + 诚实失败**：元素带 `@<snapshot>:<ref>` 形式的引用；UI 变了返回 `STALE_REF` / `AMBIGUOUS_TARGET` 逼 agent 重新 snapshot，而非点错行；裸 `@e8` 直接 `INVALID_ARGS`。
4. **模型无关、无内置 LLM**：本身不含任何大模型、无 GUI，每条命令打印一个 JSON 信封后退出——observe/act/verify 循环完全留在调用方 agent 里，可换任意模型。
5. **跨平台 + 60 命令 + 技能包**：macOS/Windows/Linux 一套 CLI；~60 个命令名（observe/act/window/clipboard/notification/session…）；`agent-desktop skills get desktop` 下发 loop/ref/retry 规则。

## 三、核心架构（克制呈现）

Rust workspace，核心抽象在 `crates/`：

- **`crates/core/`**：平台无关的「大脑」——`adapter/`（能力特质）、`snapshot/`（快照生成）、`refs/`（ref 分配与解析）、`tree/`（节点遍历）、`locator/`（元素定位）、`actionability/`（可点击性/稳定性判定）、`actions/`、`input/`、`session/`、`trace/`、`system/`、`commands/`。
- **`crates/macos` / `crates/windows` / `crates/linux`**：各平台**只**实现 `PlatformAdapter` 特质，分别对接 AX / UI Automation / AT-SPI。
- **`crates/ffi/`**：C 库，供进程内调用。
- **`src/`**：CLI 二进制（`main.rs` + `cli/` + `dispatch/` + `command_policy/`）。

## 四、应用场景与启发

- **桌面应用自动化 Agent**：让 Claude Code / Cursor / 自写脚本驱动 Finder、System Settings、Slack、本地 GUI 工具，无需脆弱的截图栈或逐平台脚本。
- **无障碍/UI 自动化测试**：用 ref 做确定性点击与断言，比「截图+视觉模型」稳且省 token。
- **给同类需求的启发**：① 计算机使用的正确抽象是「OS 给的结构化树 + 稳定 ref」，而非「图像 + 坐标」；② **core 永不 import 平台 crate**，每个二进制只编一个 OS，是干净的可移植设计；③ 把「观察/行动/验证」循环留在 agent 侧、工具只做确定性执行，是最少耦合的分工。

## 五、源码深度解读

**1) 平台抽象——`crates/core/src/adapter/mod.rs`**
四个能力特质组合成 `PlatformAdapter`，core 只依赖它，平台 crate 各自实现：

```rust
pub trait PlatformAdapter: ObservationOps + ActionOps + InputOps + SystemOps {}
impl<T: ObservationOps + ActionOps + InputOps + SystemOps> PlatformAdapter for T {}
```
`ObservationOps` 产快照、`ActionOps` 执行 ref 操作、`InputOps` 管键鼠、`SystemOps` 管窗口/剪贴板——core 通过这层与 OS 解耦，编译期即锁定单平台。

**2) ref 分配与解析——`crates/core/src/refs/mod.rs`**
每个快照分配一批 ref，`RefPath` 用 `SmallVec<[usize;8]>` 表示树路径，`RefMap` 有 `MAX_REFMAP_BYTES = 1_048_576` 上限，快照号由 `SNAPSHOT_COUNTER: AtomicU64` 生成：

```rust
pub type RefPath = SmallVec<[usize; 8]>;
pub(crate) const MAX_REFMAP_BYTES: u64 = 1_048_576;
static SNAPSHOT_COUNTER: AtomicU64 = AtomicU64::new(0);
// try_allocate -> validate_ref_entry -> allocate_validated
```
ref_id 形如 `@s8f3k2p9:e8`，snapshot 段自描述；bare `@e8` 被 `validate_ref_id` 拒掉，UI 变化导致的失效由 action 层返回 `STALE_REF`，**失败闭合（fail-closed）**而非猜测。

**3) CLI 入口——`src/main.rs`**
`run_command()` 用 clap 解析，经 `dispatch` 落到具体命令；`#[cfg(target_os="linux")] agent_desktop_linux::end_input_session()` 在 Linux 上归还输入会话——体现「无头默认、用完即放」的设计。

## 六、社区口碑（全网口碑）

- **强正面、覆盖广**：nvdium、MarkTechPost、AITopic、aiboss88 等多家媒体在 2026-10 末集中报道，普遍评价为「把计算机使用从『能点浏览器』扩展为『能驱动整台机器』的可复现路径」，赞赏其模型无关、token 省、跨平台。
- **官方作者自报**：Slack/VS Code/Notion 上 78%–96% token 下降，Apple Maps 单次观察 3,811→273 token，52 步任务 198k→31k token（均**自报，尚无独立基准**）。
- **局限（第三方指出）**：① 只看无障碍树——**没有树的应用对它不可见**；② 冷启动的 Electron 应用暴露 web 树要 10–25s；③ 快照/剪贴板/截图可能含隐私，勿进公开日志；④ 多 agent 光标仅展示层，机器级交互仍被单一 lease 串行化；⑤ 基准缺乏独立验证。

## 七、竞品对比

| 维度 | agent-desktop | Anthropic Computer Use | agent-browser（同门） | 传统 RPA |
|------|---------------|----------------------|----------------------|----------|
| 观察方式 | 无障碍树（JSON） | 截图+视觉模型 | 网页 DOM/可访问性 | 坐标/选择器 |
| 内置 LLM | 无 | 有 | 无 | 无 |
| 跨平台桌面 | ✓（mac/win/linux） | 视实现 | ✗（仅 Web） | 部分 |
| token 成本 | 低（结构化） | 高（图像） | 低 | 低 |
| 模型锁定 | 否 | 是（Claude） | 否 | 否 |

agent-browser 管 Web、agent-desktop 管桌面，二者共享「结构化而非像素」理念；与 Anthropic 截图式 computer use 是路线之争。

## 八、核心研判

- **价值判断**：是「agent 驱动的桌面自动化」目前最干净的基础设施之一——模型无关、确定性、跨平台。适合想把原生 App 纳入 agent 工作流的团队，也适合做无障碍自动化测试。
- **风险点**：① 无障碍树覆盖取决于 App 是否暴露语义（游戏/Canvas/未标注控件是盲区）；② 隐私（快照含桌面内容）需在部署层管控；③ 基准多为自报，生产前自测。
- **采用建议**：先用 `agent-desktop snapshot --app Finder -i` + `click @...` 跑通最小循环，再把 `skills get desktop` 的规则接进你的 agent harness；涉及物理输入时显式 `--headed` 并限定作用域。

## 九、关键文件路径速查

- `crates/core/src/adapter/mod.rs` — `PlatformAdapter` 特质定义（四能力组合 + blanket impl）
- `crates/core/src/refs/mod.rs` — ref 分配/解析、`RefPath`、`MAX_REFMAP_BYTES`、snapshot 计数
- `crates/core/src/snapshot/mod.rs` / `snapshot/snapshot_ref.rs` — 快照生成与 ref 绑定
- `crates/core/src/actionability/` — 可点击性/稳定性/遮挡判定
- `crates/core/src/commands/snapshot.rs` / `execute_by_ref.rs` — 快照与按 ref 执行
- `crates/macos` / `crates/windows` / `crates/linux` — 三平台 AX / UI Automation / AT-SPI 实现
- `crates/ffi/` — C 库（进程内调用）
- `src/main.rs` / `src/dispatch.rs` / `src/command_policy.rs` — CLI 入口与调度
- `CONCEPTS.md` / `AGENTS.md` — 领域词汇表与 agent 接入规约
