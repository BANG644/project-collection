# 🔬 clash-verge-rev/clash-verge-rev — 全方位深度调研

> 调研日期：2026-09-01 ｜ 星标：141,364 ⭐ ｜ Fork：10,176 ｜ 语言：TypeScript（前端）+ Rust（Tauri 后端）｜ 协议：GPL-3.0 ｜ 默认分支：dev ｜ 实时状态：极活跃（pushed 2026-08-31）

## 📌 项目定位

`clash-verge-rev/clash-verge-rev` 是基于 **Tauri（Rust + WebView）** 的跨平台代理 GUI 客户端，底层驱动 **Mihomo（Clash Meta）** 内核。它把"订阅管理 / 规则分流 / 系统代理 / TUN 模式 /  profiles"做成了一套现代桌面体验，是 Clash for Windows 停更后的主流继承者之一。

> 核心判断：它的本质是一个 **"Mihomo 内核的桌面外壳"**——Rust 负责进程/系统/权限，前端 React 负责配置与交互，真正干网络活的是被它拉起（sidecar）的 mihomo 二进制。理解这点，就不会把它当成"自己实现了代理协议"的项目。

## 🏆 项目亮点（差异化）

1. **Tauri 而非 Electron**：Rust 后端 + 系统 WebView，安装包体积小、内存占用低，比传统 Electron 代理 GUI 轻得多。
2. **Mihomo（Clash Meta）内核**：支持 Clash 全套规则、SSR/v2ray/trojan 等协议与 Meta 特有功能（如 hy2、tuic、mihomo 规则集），生态最新。
3. **Profiles（订阅/配置）即核心抽象**：把订阅 YAML、本地覆盖、脚本转换（script 处理器）统一管理，支持远程规则集与自动更新。
4. **系统级能力齐全**：系统代理开关、TUN 虚拟网卡（全局接管）、开机自启、托盘菜单、开机自动连接——桌面体验完整。
5. **Rust workspace 自研组件**：把媒体解锁检测、日志、信号、i18n、限流、系统信息插件拆成独立 crate，工程结构清晰、可维护。

## 🏗️ 核心架构（克制版）

```
┌──────────────────────────────────────────────┐
│  React + TypeScript 前端 (src/)                │
│  pages / components / hooks / services / utils  │
│  └─ 通过 Tauri invoke 与 Rust 后端通信          │
└───────────────┬──────────────────────────────┘
                │ Tauri IPC (invoke / events)
┌───────────────▼──────────────────────────────┐
│  src-tauri/ (Rust workspace)                   │
│  ├─ clash-verge-draft      配置草稿/合并        │
│  ├─ clash-verge-media-unlock 流媒体解锁探测     │
│  ├─ clash-verge-logging     日志               │
│  ├─ clash-verge-signal      进程信号控制        │
│  ├─ clash-verge-i18n        多语言             │
│  ├─ clash-verge-limiter     限流               │
│  ├─ tauri-plugin-clash-verge-sysinfo 系统信息  │
│  ├─ tauri-plugin-clipboard-manager 剪贴板      │
│  └─ tauri (窗口 + 系统能力)                     │
└───────────────┬──────────────────────────────┘
                │ 拉起 / 守护 sidecar 进程
┌───────────────▼──────────────────────────────┐
│  mihomo (Clash Meta) 内核二进制                │
│  ├─ 监听 mixed-port (HTTP/SOCKS)              │
│  ├─ TUN 模式（虚拟网卡全局接管）               │
│  ├─ 规则分流 (rules) / 代理组 (proxies)        │
│  └─ 订阅 YAML / 外部规则集                     │
└───────────────────────────────────────────────┘
        ↑ 外部订阅 / 代理节点配置（用户导入）
```

前端 `src/` 结构：`assets / components / hooks / locales / main.tsx / pages / polyfills / providers / services / types / utils`——标准 React SPA。

## 💡 应用场景与启发（重点）

- **"内核与壳分离"的桌面架构范式**：需要做一个"控制某个本地/第三方二进制"的 GUI 时，Tauri + sidecar 是比 Electron 更轻的成熟方案，Rust 端只管进程/权限/系统，前端管交互。
- **Profiles 抽象值得借鉴**：把"远程订阅 + 本地覆盖 + 转换脚本"统一成一份可版本化的配置，比让用户直接改大 YAML 友好得多。做任何"配置驱动"的工具都应参考。
- **Tauri 插件化**：把媒体解锁、系统信息、剪贴板拆成 tauri-plugin-*，既解耦又易单测，是 Tauri 项目的标准做法。
- **注意合规边界**：代理工具本身中立，但务必遵守所在地区法律法规与网络使用规范；本项目仅作技术架构研究。

## 🧠 源码深度解读（3 个核心模块）

### 1) Rust 依赖与 workspace 拆分 — `src-tauri/Cargo.toml`
所有能力拆成 workspace 内部 crate，主包只声明依赖：

```toml
[dependencies]
clash-verge-draft        = { workspace = true }  # 配置草稿/合并
clash-verge-media-unlock = { workspace = true }  # 流媒体解锁探测
clash-verge-logging      = { workspace = true }
clash-verge-signal       = { workspace = true }  # 控制 mihomo 进程信号
clash-verge-i18n         = { workspace = true }
clash-verge-limiter      = { workspace = true }
tauri-plugin-clash-verge-sysinfo = { workspace = true }
tauri-plugin-clipboard-manager   = { workspace = true }
tauri = { workspace = true, features = [...] }
```

`clash-verge-signal` 是关键：它负责向 mihomo 进程发 SIGHUP/重启、读取其配置，是"壳控制内核"的桥梁。

### 2) 内核 sidecar 拉起（Rust 端）
Tauri 通过 `tauri-plugin-shell` 以 sidecar 形式拉起打包内的 mihomo 二进制，并把生成的 `config.yaml` 路径、mixed-port 等传给它：

```rust
// 伪代码：拉起 mihomo sidecar
let sidecar = Command::new_sidecar("mihomo")?
    .args(["-f", &config_path, "-d", &work_dir]);
let (mut rx, _child) = sidecar.spawn()?;  // 守护进程，监听其 stdout/stderr
```

前端改完配置 → 调 Rust 重新生成 YAML → 通过 signal crate 让 mihomo 热重载或重启。

### 3) 前端配置服务 — `src/services`
前端把"profiles / proxies / rules / settings"建模成 store，封装成对 Rust 的 `invoke` 调用：

```ts
// src/services 中典型的调用形态
const { data } = await invoke("get_profiles");
await invoke("patch_profile", { uid, patch });
await invoke("restart_core");   // 触发 Rust 端 signal → mihomo 重载
```

UI 层（pages/components）只消费 store，不直接碰 Tauri API，分层清晰。

## 🌐 全网口碑画像

- **正面**：Clash for Windows 停更后，clash-verge-rev 是社区最活跃的继承者之一；Tauri 带来小体积/低占用；Mihomo 内核保证协议最新；订阅/脚本/规则集生态完善；中文社区支持强。
- **中性/风险**：GPL-3.0 协议（修改分发需开源）；TUN 模式在个别系统/杀软下需提权或冲突；mihomo 内核需随上游更新，跟进节奏影响新协议支持；订阅安全（节点/密码）需用户自行保管。
- **对比同类**：与 FlClash（也是 Tauri + mihomo）、NekoBox、v2rayN、Stash(iOS)、Surge(商业) 相比，clash-verge-rev 在"桌面跨平台 + 现代化 UI + 配置灵活度"上综合占优。

> 数据来源：GitHub 元数据（141k⭐、10k fork、GPL-3.0、每日 push）、`src-tauri/Cargo.toml` 依赖真实抓取、`src/` 前端结构、公开社区反馈。未编造具体评测数字。遵守所在地区法律法规，本项目仅作技术架构研究。

## ⚔️ 竞品对比

| 方案 | 技术栈 | 优势 | 风险/短板 |
|---|---|---|---|
| **clash-verge-rev** | Tauri(Rust)+React / mihomo | 轻量、跨平台、UI 现代、配置灵活 | GPL-3.0、TUN 偶有提权问题 |
| **FlClash** | Tauri / mihomo | 同样轻量、界面简洁 | 社区规模略小 |
| **NekoBox** | Qt / sing-box | 多内核、协议广 | UI 偏技术向 |
| **v2rayN** | .NET / Windows | Windows 上极成熟 | 仅 Windows |
| **Stash** | iOS 原生 | iOS 体验最佳 | 仅 iOS、闭源商业 |
| **Surge** | 商业闭源 | 功能全家桶、稳定 | 贵、闭源、平台受限 |

## 🎯 核心研判

- **采用建议**：需要跨平台、轻量、现代化的 Clash Meta 桌面客户端 → clash-verge-rev 是当前首选之一；仅 Windows 重度用户也可看 v2rayN，iOS 看 Stash。
- **最大风险**：TUN 模式涉及系统网络层改动，需理解提权与冲突；订阅/节点凭据务必来自可信源并本地保管；GPL-3.0 意味着分发修改版需开源。
- **借鉴价值**：① Tauri + sidecar 控制本地二进制的轻量桌面范式；② 把"订阅+覆盖+脚本"统一为 Profiles 的配置抽象；③ Rust 端按能力拆 workspace crate。
- **一句话**：clash-verge-rev 的精髓不是"自研代理"，而是用 Tauri 把一个强大的 Mihomo 内核，包装成现代、轻量、好配置的桌面外壳。

## 📂 关键文件路径速查

- `src-tauri/Cargo.toml` — Rust workspace 依赖（各 clash-verge-* crate）
- `src-tauri/src/` — Tauri 命令、mihomo sidecar 控制、系统代理/TUN 逻辑
- `src/services/` — 前端对 Rust 的 invoke 封装（profiles/proxies/settings）
- `src/pages` `src/components` `src/hooks` — React UI 与状态
- `src-tauri/tauri.conf.json` — Tauri 窗口/sidecar/权限配置
- `.github/workflows/release.yml` — 跨平台构建与发布

## 🧪 研究方法与数据来源

- GitHub API 元数据（stars/forks/license/default_branch/topics 含 clash/mihomo/tauri-app）
- `src-tauri/Cargo.toml` 依赖清单真实抓取（workspace crates + tauri plugins）
- `src/` 前端目录结构真实抓取
- 公开社区长期反馈（非编造评测数字）；本项目仅作技术架构研究，使用请遵守当地法律法规
