# 🦀 Dioxus — Rust 全栈跨平台应用框架

> **仓库**: [DioxusLabs/dioxus](https://github.com/DioxusLabs/dioxus)
> **Stars**: 37,947⭐ | **Forks**: 1,783 | **今日新增**: 数据不可用（Trending 当日上榜）
> **语言**: Rust | **许可证**: Apache-2.0 OR MIT（双协议）
> **官网**: [dioxuslabs.com](https://dioxuslabs.com) | **标签**: rust, wasm, web, desktop, mobile, ssr, ui, virtualdom

## 一、项目全景

Dioxus 是用 Rust 编写的**全栈应用框架**，一套代码库同时覆盖 Web、桌面、移动端、Server（甚至 TUI）。它吸收了 React、Solid、Svelte 的优点，用 `rsx!` 宏写类 JSX 的 UI，以 signals 做状态管理，并通过 Server Functions 与深度集成的 axum 提供全栈能力，再用 `dx` CLI 一键打包热重载。

**项目亮点**：
- 🌐 真正的「一套代码多端」：web / desktop / mobile / SSR / liveview / TUI 同一组件模型
- ⚡ signals 状态管理融合 React/Solid/Svelte 之长，零配置 + 亚秒级热重载（`dx serve --hotpatch`）
- 📦 hello world 约 50KB（与 React 相当），桌面可移植二进制 <3MB
- 🏢 有全职核心团队 + 企业资助（FutureWei），活跃的 Discord 社区

## 二、核心架构

Dioxus 是 **monorepo + 多 crate 分层** 架构，每个渲染目标/能力都是独立 package，由 `core` 统一调度：

```
packages/
├── core/        虚拟 DOM、hooks、组件运行时、diff 调度（fiber 批处理）
├── rsx/         rsx! 宏解析与代码生成（element/attribute/component/ifchain/forloop）
├── signals/     信号原语（signal/memo/map/selector）
├── web/         WASM → DOM 渲染器（dom.rs / mutations.rs / hydration/）
├── native/      桌面/移动渲染器（dioxus_application.rs / dioxus_renderer.rs）
├── ssr/         服务端渲染（renderer.rs / template.rs / hydration）
├── router/      路由（Routable / navigator / outlet）
├── fullstack/   axum 全栈 + Server Functions
├── cli/         dx 命令行（serve / build / hot-patch）
├── rsx-hotreload/  RSX 热重载 diff 引擎
├── subsecond/   亚秒级 Rust 热补丁
└── web / native-dom / manganis / wasm-split / ...
```

渲染后端可插拔：**web-sys**（WASM 直渲 DOM）、**webview**（桌面/移动）、**SSR**、**liveview**，以及实验性的 **WGPU/Blitz** 原生渲染器（可嵌入 Bevy、嵌入式 Linux）。

## 三、源码深度解读

**1. rsx! 宏（`packages/rsx/src/`）**
`rsx!` 不是字符串模板，而是编译期宏，关键文件：
- `element.rs` / `attribute.rs` — 元素与属性 AST 构建
- `ifchain.rs` / `forloop.rs` — 条件/循环编译为惰性节点
- `template_body.rs` — 生成「模板 + 动态槽位」结构，使静态部分零成本、动态部分精确更新
- `partial_closure.rs` — 闭包捕获处理

这套 codegen 让 Dioxus 在编译期区分静态模板与动态值，是「hello world 仅 50KB」的体积优势来源。

**2. signals（`packages/signals/src/`）**
- `signal.rs` — 基础可读写信号
- `memo.rs` — 派生记忆信号（依赖自动追踪）
- `map.rs` / `selector.rs` — 集合/选择性订阅，实现细粒度更新而不依赖虚拟 DOM 全量 diff

signals 是 0.6 引入的核心，使 Dioxus 从「React-like hooks」过渡到「Signals + RSX」，与 Solid/Svelte 趋同。

**3. 多端渲染器（`packages/web` vs `packages/native`）**
- `web/src/dom.rs` + `mutations.rs`：把虚拟 DOM 的 mutation 应用到真实 DOM，含 hydration 复用
- `native/src/dioxus_application.rs`：封装 tao/wry 窗口循环，把同一组件树渲染进原生 WebView 窗口
同一 `app()` 组件在 `dx serve --platform web/desktop/android/tui` 下无需改动即渲染到不同目标——这是 Dioxus 相对 Leptos/Yew 的差异化核心。

**4. 全栈（`packages/fullstack` + axum）**
Server Functions 让前端直接 `await` 调用后端 Rust 函数，编译期生成客户端桩 + 服务端端点，配合 axum 提供 WebSocket/SSE/Streaming/文件上传/SSR/Forms/Middleware。

## 四、社区口碑

- **成熟度共识**：2026 年多家对比（reintech、rustify、wrenlearnsrust）将其与 Leptos、Yew 并称 Rust 前端三强；评价「Dioxus 更成熟、生态更大、示例更多、文档更全」。
- **跨平台口碑突出**：社区普遍因「桌面/移动支持最完整、API 最 ergonomic」从 Leptos/Yew 转投；腾讯云技术号称其「Rust 程序员的降维打击」。
- **企业可用信号**：Dioxus 0.6 已用于生产，有商业支持与组件市场；FutureWei 资助的全职团队保障长期维护。
- **主要批评**：版本迭代快（已到 0.7+），移动端仍为 beta；纯 SSR 性能略逊 Leptos；WASM 包体（gzip ~120–300KB）大于 Leptos 的细粒度方案。

## 五、竞品对比

| 维度 | Dioxus | Leptos | Yew | Tauri | React Native |
|------|--------|--------|-----|-------|--------------|
| 主定位 | 跨平台 UI | 全栈 Web | Web (Elm) | 桌面壳 | 移动 UI |
| 渲染 | VDOM + 多后端 | 细粒度信号(无VDOM) | VDOM (Elm) | WebView 壳 | 原生桥 |
| 桌面 | ✅ 原生 | ⚠️ 需 Tauri | ⚠️ 弱 | ✅ | ❌ |
| 移动 | ✅ beta | ❌ | ❌ | ⚠️ | ✅ |
| SSR | ⚠️ 次优 | ✅ 一流 | ⚠️ | ❌ | ❌ |
| Web WASM | ~45–60KB | ~25–35KB | ~110KB | — | — |
| 信号 | ✅ 0.6+ | ✅ | ❌ | — | ✅ |

选型结论（多源一致）：**Web 优先全栈选 Leptos；跨平台（含桌面/移动）Rust 无竞争者选 Dioxus**。

## 六、核心研判

**优势**
- 跨平台覆盖是 Rust UI 生态中唯一完整的——Web/桌面/移动/TUI 同一组件模型，对独立开发者与企业内部工具极具吸引力。
- signals + rsx! + axum 全栈的组合成熟度高，开发体验（热重载/CLI）领先同类。

**风险**
- 仍 0.x 快速迭代，API 偶有不稳；移动端 beta、纯 SSR 性能弱于 Leptos，重 Web 场景需权衡。
- 生态组件库少于 React/Flutter，复杂企业 UI 仍需自研或依赖 Radix 风格原语。

**趋势**
- 原生渲染器（WGPU/Blitz）与 subsecond 热补丁推进，正在补齐「无 WebView 依赖」的原生路径；fullstack 与 Leptos 的正面竞争加剧，利好用户。

**启发**
- 对「一套 Rust 代码打多端」需求（工具类桌面 App、内网系统、跨端 SaaS 前端），Dioxus 是当前最省心的选择；其「宏层区分静态/动态、信号驱动细粒度更新」的架构值得其他 UI 框架借鉴。

## 七、关键文件速查

| 路径 | 作用 |
|------|------|
| `packages/core/` | 虚拟 DOM、hooks、组件运行时、diff 调度 |
| `packages/rsx/src/template_body.rs` | rsx! 模板+动态槽位 codegen |
| `packages/rsx/src/ifchain.rs` / `forloop.rs` | 条件/循环编译 |
| `packages/signals/src/signal.rs` / `memo.rs` | 信号原语与派生记忆 |
| `packages/web/src/dom.rs` / `mutations.rs` | WASM→DOM 渲染与 hydration |
| `packages/native/src/dioxus_application.rs` | 桌面/移动窗口与渲染循环 |
| `packages/ssr/src/renderer.rs` / `template.rs` | 服务端渲染 |
| `packages/router/src/routable.rs` | 路由定义 |
| `packages/fullstack/` | axum 全栈 + Server Functions |
| `packages/rsx-hotreload/src/diff.rs` | RSX 热重载 diff |
| `packages/subsecond/` | 亚秒级 Rust 热补丁 |

## 八、应用场景与启发

- **跨端工具**：开发者工具桌面 GUI、内网 SaaS 仪表盘（WASM）、嵌入式配置界面——一套代码交付三端。
- **独立产品**：轻量桌面 App、个人网站重写，利用其低二进制体积与原生性能。
- **组合启发**：Dioxus 的「宏层静态/动态分离 + 信号细粒度更新」是构建高性能 UI 运行时的经典范式；其多 crate monorepo 划分（core/rsx/signals/web/native/ssr 各司其职）也是大型 Rust 框架可复用的工程结构模板。
