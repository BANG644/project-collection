# 🔬 OpenCut-app/OpenCut — 深度调研

> 调研日期：2026-07-15 | 数据来源：GitHub API + README + 源码树
> ⭐ Stars：**68,972**（+4,349 当日 Trending） | 🍴 Forks：7,194 | 📅 创建：2025-06-22 | 🔤 语言：TypeScript | 📜 协议：MIT | 🏷️ topics：editor / oss / videoeditor

## 一、项目亮点（差异化）

1. **定位清晰：开源版 CapCut**——直接对标字节剪映/CapCut，主打"free & open source video editor for web, desktop, and mobile"，填补了开源视频编辑器中"现代化、跨端、AI 原生"的空白。
2. **Rust 核心 + 三端同源**——正在重构的版本用 Rust 核心统一驱动浏览器 / 桌面 / 移动端，避免 Electron 式臃肿，目标一个代码库覆盖全部平台。
3. **AI 原生设计**——明确规划 **MCP server（给 AI Agent 调用）** 与 **Headless 模式（自动化/批量渲染）**，是少数把"让 Agent 能剪视频"写进架构蓝图的开源编辑器。
4. **Plugin-first 架构**——插件作为一等公民，配合 Editor API 与编辑器内脚本标签页，走的是"可扩展创作工具平台"而非单纯编辑器路线。
5. **现代全栈栈**——Web 端用 TanStack Start + Cloudflare，桌面端用 Rust+GPUI（Zed 同款 UI 框架），monorepo 用 moon + proto 锁工具链，工程成熟度高于多数个人视频项目。

## 二、项目全景

OpenCut 是一个 2025 年中启动的开源视频编辑器，目标是成为 CapCut 的免费开源替代品。项目当前处于**从零重写**阶段：README 明确说明"OpenCut is being rewritten from the ground up"。生产可用的"经典版"在 `opencut-app/opencut-classic`，`opencut.app` 目前仍跑经典版，重写版在 `new.opencut.app` 孵化。

社区增长极快（约一年 6.9 万星），已有 Discord 与 X 社群，并获得 fal.ai 赞助。项目现阶段**暂不接受外部 PR**（架构仍在设计），典型的"作者主导 + 社群围观"的爆红早期项目。

## 三、核心架构

仓库是一个 **moon + proto 管理的 monorepo**，工具链通过 `.prototools` 固定（proto 自动安装 Node/Rust 等），保证可复现构建。

```
OpenCut/                      (monorepo, moon workspace)
├── Cargo.toml                Rust workspace（resolver=3, edition 2024）
├── apps/
│   ├── web/                  TanStack Start (React 19) + Cloudflare vite-plugin
│   ├── api/                  Cloudflare Workers (wrangler.jsonc, :8787)
│   └── desktop/             Rust + GPUI（Zed 同款框架）
└── packages/                (规划中的共享/Rust 核心)
```

- **Web 端**：`@tanstack/react-start`（全栈 React + SSR）、`@cloudflare/vite-plugin`（直接部署到 Cloudflare Workers）、React 19、Tailwind v4、shadcn / base-ui、zod、recharts、sonner。前端与服务端同仓库一体。
- **API 端**：Cloudflare Workers（`wrangler.jsonc`），负责渲染/导出等无服务器能力。
- **桌面端**：Rust + **GPUI**（Zed 编辑器用的高性能 UI 框架）。`Cargo.lock` 已提交，首编译从源码构建 GPUI。平台支持：macOS(Metal)、Windows(Win32+DirectWrite)、Linux(Vulkan/Blade + Wayland/X11)。
- **规划中的重写能力**：Editor API、plugin-first 插件、Rust 核心三端同源、MCP server、Headless 模式、编辑器内脚本标签页。

## 四、应用场景与启发

> 这个仓库可以用在哪些场景 / 给同类需求带来什么解决思路

- **"跨端同源"编辑器范式**：当你要做同时覆盖 Web/桌面/移动的工具时，用 Rust 核心 + 平台壳层的分层思路，比 Electron 更轻、比纯 Web 更强。OpenCut 的 desktop 用 GPUI 而非 Tauri，值得关注（GPUI 在 Zed 已验证可承载复杂编辑器 UI）。
- **AI 原生工具的设计前瞻**：把 MCP server + Headless 写入架构蓝图，意味着"让 Agent 直接操作我的创作工具"正在成为标配。做任何创作/生产力工具时，应尽早预留 Agent 接口。
- **monorepo 工具链治理**：moon + proto 的"声明式锁工具链"模式，对需要多语言（TS+Rust）协作的团队是可复用的工程模板。

## 五、源码深度解读

### 1) Web 端技术选型（`apps/web/package.json`）

```jsonc
// 全栈 React（SSR + 路由 + 数据获取一体）
"@tanstack/react-start": "latest",
"@tanstack/react-router": "latest",
// 直接部署到 Cloudflare Workers
"@cloudflare/vite-plugin": "^1.26.0",
// UI：Tailwind v4 + shadcn + base-ui
"tailwindcss": "^4.1.18", "shadcn": "^4.7.0", "@base-ui/react": "^1.4.1"
```

要点：用 TanStack Start 替代 Next.js 走 Cloudflare 边缘部署路线；Tailwind v4（CSS-first 配置）是当前最新范式。

### 2) 桌面端 Rust 框架选型（`apps/desktop/README.md` + 根 `Cargo.toml`）

```toml
# 根 Cargo.toml
[workspace]
resolver = "3"
members = ['apps/desktop']
[workspace.dependencies]
gpui = "0.2.2"   # Zed 编辑器同款 UI 框架
```

桌面端没有用 Tauri/Electron，而是直接基于 **GPUI** 自绘。这是 OpenCut 与多数"网页套壳桌面"视频编辑器（如基于 Tauri 的 Clypra）在架构哲学上的分叉点。

## 六、社区口碑

- **增长势头**：约 13 个月冲到 6.9 万星、7,194 fork，是当下视频编辑器赛道最热的开源项目之一；当日 Trending +4,349 星。
- **社群与资本**：已建 Discord（13.8k+ 成员）、X 官方号；获得 **fal.ai**（生成式图像/视频/音频模型平台）赞助——暗示未来会深度集成 AI 生成能力。
- **成熟度 caveat**：README 明确"暂不接受外部贡献，架构仍在设计"，341 个 open issues 多为功能期待与路线图讨论；当前生产版仍是 classic 分支，重写版功能尚不完整。

## 七、竞品对比 + 核心研判

| 维度 | OpenCut | Shotcut/OpenShot/Kdenlive | LosslessCut | CapCut(剪映) | Descript |
|------|---------|--------------------------|-------------|--------------|----------|
| 开源 | ✅ MIT | ✅ | ✅ | ❌ | ❌ |
| 跨端(Web/桌面/移动) | ✅(规划中) | ❌ 桌面为主 | ❌ | ✅ | ✅(桌面/Web) |
| AI 原生(MCP/Headless) | ✅(蓝图) | ❌ | ❌ | ✅(闭源) | ✅(闭源) |
| 现代化 UI | ✅ React19/Tailwind4 | ⚠️ 偏传统 | 极简 | ✅ | ✅ |

**核心研判**：
- **机会**：开源视频编辑器长期被 Shotcut/OpenShot 这类"能用的老工具"占据，OpenCut 用现代 Web 栈 + 跨端 Rust 核心 + AI 原生蓝图，精准击中"想要 CapCut 体验但不想被锁定/付费"的用户群，差异化成立。
- **风险**：① 重写期架构未稳、不收外部贡献，进度强依赖核心作者；② CapCut 本就免费，OpenCut 的"开源"卖点对普通用户的吸引力弱于对开发者/隐私党；③ 视频编辑器的渲染/编解码/性能门槛极高，Rust 核心能否如期落地三端同源是关键未知数。
- **结论**：值得持续跟踪的"AI 时代创作工具"样本，但当前处于早期重写，生产可用版仍是 classic 分支；若其 MCP server + Headless 落地，会成为"Agent 剪辑视频"的事实标准候选。

## 八、关键文件速查

| 路径 | 说明 |
|------|------|
| `README.md` | 项目状态、重写蓝图、开发指引 |
| `Cargo.toml` | Rust workspace（GPUI 桌面端） |
| `apps/web/package.json` | Web 端：TanStack Start + Cloudflare + Tailwind v4 |
| `apps/api/wrangler.jsonc` | Cloudflare Workers 配置 |
| `apps/desktop/README.md` | GPUI 桌面端运行/构建说明 |
| `opencut-app/opencut-classic` | 当前生产可用的经典版（独立仓库） |
| `.prototools` / `.moon/` | 工具链与 monorepo 任务定义 |
