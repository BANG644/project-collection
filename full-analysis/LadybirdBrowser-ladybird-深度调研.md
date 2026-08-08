# 🔍 Ladybird 深度调研报告

> 调研日期：2026-08-09 ｜ 仓库：`LadybirdBrowser/ladybird` ｜ 星标：64,934 ⭐（2026-08-09，当日 Trending +79）｜ 协议：BSD 2-Clause ｜ 语言：C++（逐步引入 Rust）｜ 主页：ladybird.org

## 一、项目定位（一句话）

真正独立的网页浏览器——从零构建的引擎（非 Blink / WebKit / Gecko 任何 fork），源自 SerenityOS 的浏览器分支，现由独立 501(c)(3) 非营利「Ladybird Browser Initiative」运营，目标 Alpha 2026。

## 二、项目亮点（差异化，开篇呈现）

1. **全球唯一从零构建且资金充足、活跃开发的独立浏览器引擎**——web 标准的"第四套实现"，是 Blink/WebKit/Gecko 之外唯一可信的从零尝试（上一个 Servo 在 2020 被 Mozilla 裁撤团队）。
2. **多进程架构**：UI 主进程 + 多个 WebContent 渲染进程 + ImageDecoder 进程 + RequestServer 进程；每个 tab 独立渲染进程且沙箱化，图像解码与网络连接均 out-of-process 以增强对恶意内容的鲁棒性。
3. **完整自研核心库**：LibWeb（渲染）、LibJS（JS 引擎）、LibWasm（WASM）、LibGfx（2D 图形/图像解码）、LibHTTP、LibTLS/LibCrypto、LibIPC、LibMedia（音视频）、LibCore（事件循环/OS 抽象）等，继承自 SerenityOS。
4. **非营利"无捕获"治理**：明确禁止搜索默认、广告、"可接受广告"计划、VC 轮次——直指 Mozilla 80% 收入依赖 Google 搜索默认的"收入陷阱"。
5. **AI 加速的语言现代化**：2026 起用 Claude Code / Codex 把 LibJS 从 C++ 移植到 Rust（2.5 万行、零回归），后又探索 Swift（C++ 双向互操作）作为增量迁移路径。

## 三、核心架构

```
Libraries/            # 自研核心库（引擎组件）
  LibWeb/             # Web 渲染引擎
  LibJS/              # JavaScript 引擎（标准符合度全球第二，仅次于 Firefox）
  LibWasm/            # WebAssembly 实现
  LibGfx/             # 2D 图形 / 图像解码 / 渲染
  LibHTTP/            # HTTP/1.1 客户端
  LibTLS/LibCrypto/   # TLS / 加密原语
  LibIPC/             # 进程间通信
  LibMedia/           # 音视频播放
  LibCore/            # 事件循环 / OS 抽象层
  LibRegex/LibUnicode/LibXML/LibWebView/...
Services/             # 多进程组件（out-of-process）
  WebContent/         # 渲染进程（每 tab 一个，沙箱化）
  RequestServer/      # 网络进程
  ImageDecoder/       # 图像解码进程
  Compositor/ WebDriver/ WebWorker/
  RendererSandbox*.cpp  # 平台隔离（Linux/MacOS/Unimplemented）
Base/ Meta/(ladybird.py 构建入口) UI/ Utilities/ Tests/ Documentation/
```

- **构建**：CMake + CMakePresets；Rust 组件（`Cargo.toml` + `rust-toolchain.toml`）；`Meta/ladybird.py run` 是开发入口。
- **运行状态**：pre-alpha，仅适合开发者；Linux / macOS / Windows(WSL2) / 多数 *Nix 可构建。

## 四、源码深度解读

- **多进程隔离是安全核心**：`Services/WebContent` 每 tab 一个渲染进程；`RendererSandboxLinux.cpp / RendererSandboxMacOS.cpp` 按平台实现渲染进程沙箱，恶意网页输入被限制在独立进程内，主进程与系统不被直接暴露。
- **LibJS 是工程标杆**：2025-03 在 Web Platform Tests 一致性套件排第四，JS 引擎标准符合度全球第二（仅次于 Firefox）；这也是 AI 能安全做 C++→Rust 移植的基础——海量 test262 覆盖让"逐字节相同输出"可被验证。
- **治理转向 per-subsystem approvers**：2026-06-05 起**不再接受公开 PR**，仅维护者可合入。Kling 的理由——AI 让"看起来像正经贡献"的 PR 变得廉价且可批量伪造，而浏览器要在用户机器上跑不可信输入，一个伪装够好的漏洞即可致命。这是开源"信任信号"在 AI 时代失效的典型应对。

## 五、应用场景与启发

- **适用**：需要真正引擎多样性的 web 平台、开发者预 alpha 试用、教学（完整自研引擎源码可读）、作为"无公司议程"的开放 web 公共品。
- **启发**：
  1. 浏览器引擎多样性是结构性问题——实现者谈判标准，单一引擎导致规范被单一厂商行为橡皮图章。
  2. 非营利"无捕获"治理模型（禁搜索默认/广告/VC）是避免 Mozilla 式收入陷阱的可复制范本。
  3. 开源项目的"陌生人好补丁→贡献者"转化链路在 AI 时代失效，贡献门槛治理需重构（per-subsystem approvers）。

## 六、社区口碑

- **HN 高度关注**：治理改革帖 323 分，被社区视为项目从"志愿者爱好"走向"可发货软件"的必要成熟步骤（"最后非 Chromium 引擎长大"）。
- **争议焦点**：2026-06-05 关闭公开 PR 被批评"近乎异端"——对一个身份建立在开放之上的项目，关闭正门削弱了社区贡献管道。Kling 的回应被普遍视为合理但痛苦。
- **资金与路线图**：Shopify CEO Tobi Lütke $1M 捐赠 + GitHub / ProtonMail / Cloudflare / 37signals 赞助；目标 Alpha 2026（Linux/macOS）、Beta 2027、Stable 2028；保持 18 个月 runway。
- **状态共识**：pre-alpha，还远不能当日常浏览器。

## 七、竞品对比

| 引擎 | 控制方 | 性质 | 与 Ladybird 关系 |
|------|--------|------|------------------|
| Blink | Google（Chrome/Edge/Brave/Opera/Arc…） | 厂商引擎 | Ladybird 从零写、无 Google 议程 |
| Gecko | Mozilla（Firefox） | 厂商引擎 | Mozilla 80% 收入靠 Google 搜索默认（受 DOJ 威胁） |
| WebKit | Apple（Safari） | 硬件 moat | Apple 硬件绑定 |
| **Ladybird** | **独立 501(c)(3)** | **从零 + 非营利** | **唯一可信的第四引擎尝试** |
| Servo | （Mozilla 已裁团队） | 2012 从零 | 前车之鉴 |

## 八、核心研判

- **优势**：唯一独立引擎、非营利无捕获、治理现代化、AI 加速移植、社区热情高。
- **风险**：pre-alpha 远未生产可用；关闭公开 PR 损害社区贡献管道；Swift/Rust 语言路线摇摆增加不确定性；与 Chromium 十年工程积累差距巨大。
- **趋势**：Alpha 2026 是分水岭；治理改革（更小圈子的 approvers + 明确里程碑）是"能发货"的前提条件。
- **启发**：浏览器引擎是数字公共品，单一引擎垄断对全体 web 开发者有结构性后果；非营利 + 捐赠模型能否撑起一款真正可用的浏览器，将是未来三年的关键实验。

## 九、关键文件路径速查

- `Libraries/LibWeb/` — Web 渲染引擎（布局/样式/解析）
- `Libraries/LibJS/` — JavaScript 引擎（test262 高覆盖）
- `Services/WebContent/` — 渲染进程（多进程架构核心，每 tab 沙箱化）
- `Services/RequestServer/` — 网络进程
- `Services/RendererSandbox*.cpp` — 渲染进程平台沙箱
- `Meta/ladybird.py` — 构建/运行入口
- `Documentation/BuildInstructionsLadybird.md` — 构建说明
