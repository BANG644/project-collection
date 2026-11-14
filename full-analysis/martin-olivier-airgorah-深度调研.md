# 🔬 martin-olivier/airgorah — 全方位深度调研

> 调研日期：2026-11-15 ｜ Stars：5,703 ｜ 语言：Rust（edition 2024） ｜ 许可：MIT ｜ 编号：#597

## 📌 一句话定位
**Airgorah** 是一个用 **Rust + GTK4** 编写的 **WiFi 安全审计软件**（仅 Linux）。它能捕获附近 WiFi 流量、发现接入点下的客户端、发起解除认证（deauthentication）攻击、抓取握手包（handshake）与 PMKID，并破解接入点密码——是一个面向安全研究人员、用现代 GUI 重写的 802.11 审计工具。

## ⭐ 项目亮点
- **底层能力扎实**：依赖 `libwifi`（802.11 帧解析）、`radiotap`（无线电元数据）、`nix`（signal/socket/user/fs——网络 socket、用户切换、文件操作）做 monitor mode 与包注入。
- **最小权限 + 特权分离**：GUI 以普通用户运行；需要特权操作时经 **`airgorah-agent` + polkit** 提权并只弹一次认证——避免整个 GUI 长期以 root 运行。
- **现代 GTK4 原生界面**：跨 X11 / Wayland；图形化呈现扫描、攻击、捕获、破解全流程，比纯命令行审计套件更友好。
- **清晰的 crate 工作区**：`common`（业务逻辑/共享模型）/ `agent`（特权进程）/ `gui`（GTK4 前端）三层拆分。
- **易分发**：上架 crates.io 与 AUR，安装成本低。

## 🏗️ 项目架构全景
Cargo workspace（`resolver = 3`，v0.9.0），三个成员 crate：
- `crates/common`：共享的业务逻辑与状态模型（扫描/攻击/捕获的结果与配置）。
- `crates/agent`：特权进程（`airgorah-agent` bin），**拥有无线接口、扫描、deauth、捕获操作**——`Cargo.toml` 暴露底层依赖：`libwifi 0.5`、`radiotap 1`、`nix 0.31`、`csv`（握手/PMKID 导出）、`ctrlc`（优雅退出）、`libc`。`src/` 含 `main.rs`（入口）、`server.rs`（与 GUI 的 IPC 服务端）、`backend/`（底层操作实现）、`validate.rs`（输入校验）、`globals.rs`。
- `crates/gui`：GTK4 前端，普通用户启动，负责展示与交互。

主流程：GUI（普通用户）启动 → 需要特权操作（起 monitor、注入包）时调用 **`airgorah-agent`**（经 polkit 提权一次）→ agent 持有无线接口，执行扫描 / Deauth / 捕获握手 / PMKID → 结果回传 GUI → CSV 导出并供破解。前提：支持 monitor mode 与 packet injection 的网卡。

## 💡 应用场景与启发
- **典型场景**：① 对自己拥有的网络做安全测试（发现弱密码、验证防护）；② Kali / 安全实训中的可视化审计演练。
- **可借鉴模式**：**「普通权限 GUI + 受控特权 agent + polkit 一次性提权」** 是 GUI 应用安全执行特权网络操作的典范——把危险能力收敛到一个短生命周期、可审计的特权进程，而非整个 GUI 以 root 常驻。
- **同类需求思路**：用 Rust + `libwifi` 重写经典 802.11 审计工具，既获得内存安全，又借 GTK4 提供现代交互；给「如何把危险网络能力做成用户友好的安全工具」提供了参考实现。

## 🧠 核心源码解读（克制代码量）
特权边界在 `crates/agent/Cargo.toml` 的依列表中暴露得最清楚——它不直接调用 syscall 堆，而是用 `libwifi`（帧解析）、`radiotap`（元数据）、`nix`（底层 socket/用户/文件）三件套构成 802.11 审计的底层能力面；`ctrlc` 保证捕获被中断时能优雅退出，`csv` 负责握手与 PMKID 的结构化导出。

`crates/agent/src/server.rs` 是 GUI 与特权进程之间的 IPC 服务端，`backend/` 是具体的扫描/Deauth/捕获实现，`validate.rs` 在特权操作前校验输入（例如目标 BSSID/信道合法性）。这种「**agent 只做被明确请求的特权动作 + 输入校验 + 一次性提权**」的结构，比把整个 GUI 跑在 root 下安全得多。

## 📊 社区口碑（外链）
- 5.7K⭐，在 Kali / 安全社区作为现代 GUI 审计工具被使用；crates.io + AUR 双渠道分发，迭代稳定（v0.9.0）。
- 定位为「经典 aircrack-ng 套件的现代 GTK4 替代」：比纯命令行友好，比 Python 写的 Fern 更轻、更现代。
- **法律边界（README 明确）**：仅用于你**拥有**的网络做测试，对他人 WiFi 发起攻击在几乎所有国家均属非法；作者不承担任何滥用责任。

## 🥊 竞品对比
| 维度 | airgorah | aircrack-ng | Wifite | Fern Wifi Cracker |
|------|----------|-------------|--------|-------------------|
| 形态 | Rust + GTK4 原生 GUI | 经典 CLI 套件 | Python 自动化 CLI | Python GUI |
| 特权模型 | 普通 GUI + polkit agent | 需 root | 需 root | 需 root |
| 差异化 | 现代 GUI + 内存安全 + 特权分离 | 功能最全但纯命令行 | 一键自动化 | 闭源/陈旧 |

## 🎯 核心研判
airgorah 是小众但**工程扎实**的 WiFi 审计工具，其「特权 agent + polkit 一次性提权 + 普通权限 GUI」的设计干净、值得安全工具借鉴。适用对象是安全研究人员与 Kali 用户；**法律边界必须严格遵守**（仅测自有网络）。它是「用 Rust 重写经典网络安全工具」的典型范例——在保留底层能力的同时获得内存安全与现代交互。

## 📁 关键文件路径速查
- 工作区：`Cargo.toml`（workspace，resolver 3）
- 特权进程：`crates/agent/Cargo.toml`、`crates/agent/src/{main.rs,server.rs,backend/,validate.rs,globals.rs}`
- 共享逻辑：`crates/common/`
- 前端：`crates/gui/`
- 说明文档：[GitHub Wiki（Installation / Usage / Credits）](https://github.com/martin-olivier/airgorah/wiki)
