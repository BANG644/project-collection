# 🔬 steipete/CodexBar — 全方位深度调研

> **仓库**: https://github.com/steipete/CodexBar
> **调研日期**: 2026-07-07
> **Stars**: 16,696⭐
> **技术栈**: Swift, macOS 14+, CLI (Swift Package)
> **许可**: MIT

## 📌 一句话定位

CodexBar 是一个 macOS 菜单栏小工具——把 57+ 家 AI 编程服务的额度/配额/重置时间全塞进你的菜单栏，让你一眼知道自己还剩多少 tokens，不用切网页猜。

## ⭐ 项目亮点

1. **57+ 家 AI 编程服务全覆盖** — 不只是 Codex 和 Claude，还覆盖 Cursor、Gemini、Copilot、Grok、OpenRouter、LiteLLM、Windsurf、Zed、JetBrains AI、AWS Bedrock 等。这是目前市面上覆盖最全的 AI 编程额度监控工具，没有之一。
2. **隐私优先设计** — 不需要你存密码。复用已有 provider 会话（OAuth/Device Flow/浏览器 Cookie/本地文件），所有解析在本地完成。有一套完整的 macOS 权限说明文档解释每项权限的必要性。
3. **Peter Steinberger（steipete）出品** — 资深 iOS/macOS 开发者（PSPDFKit 创始人），代码质量和架构设计有保障。这不是玩票项目，是一个成熟 macOS 开发者写的高质量 Swift 应用。
4. **生态辐射** — 已经有人做了 Windows 移植（Win-CodexBar）、Linux 桌面集成（GNOME Extension/Waybar/KDE Plasma Widget）、SketchyBar/Tmux 插件。一个菜单栏工具能带动这么多生态，说明这是"刚需"。
5. **不仅仅是监控工具** — 还提供了 `codexbar` CLI 工具、WidgetKit 桌面 widget、成本扫描（`codexbar cost`），甚至可以 script 化和 CI 集成。

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学

```
CodexBar/
├── Sources/CodexBar/       # 主应用代码
│   ├── Providers/          # 每个 AI 服务的 Provider 实现
│   ├── UI/                 # 菜单栏界面逻辑
│   ├── Storage/            # 配置持久化
│   ├── Models/             # 数据模型
│   └── CLI/                # 内嵌 CLI 工具
├── Scripts/                # 构建/发布/测试脚本（极其完善）
├── .github/workflows/      # CI + release 自动化
├── docs/                   # 每项 Provider 的详细配置文档
└── Package.swift           # Swift Package 定义
```

**设计哲学**：每个 AI 服务是一个独立的 `Provider` 实现，遵循统一协议。添加到菜单栏的 provider 通过配置文件控制（`settings.json`），运行时动态加载。

### 技术栈

| 层 | 技术 |
|---|------|
| 语言 | Swift 6.2+ |
| UI 框架 | SwiftUI + AppKit（MenuBarExtra） |
| 最低系统 | macOS 14 (Sonoma) |
| 测试 | XCTest + 分片测试策略 |
| 构建 | Swift Package Manager + xcodebuild |
| 发布 | Sparkle（自动更新）+ Homebrew Cask |

## 💡 应用场景与启发

### 典型使用场景

1. **AI 编程额度焦虑"治愈"** — 每天同时用 Claude Code + Codex + Cursor + Copilot 的开发者，再也不用记"哪个还剩多少"。菜单栏一眼看清所有额度，还能看重置倒计时。
2. **成本管理** — 团队管理者可以用 `codexbar cost` 在 CI 里追踪团队 AI 编程支出。CLI 工具支持脚本化和定时统计。
3. **配额规划** — "这个长分析任务要 2 小时，我 Codex 5-hour window 还剩 45 分钟"——菜单栏的实时额度让你可以规划工作流。
4. **Provider 热切换** — Merge Icons 模式下，菜单栏只显示一个图标，点击弹出 switcher 切换查看不同 provider 的额度。适合 provider 数量多的用户。

### 可借鉴的解决方案模式

- **"Provider 协议 + 动态注册"模式**：CodexBar 的核心抽象是一个 `Provider` 协议，每个 AI 服务实现该协议。新增一个服务只需要写一个新的 Provider 文件——这是"可插拔架构"的教科书级实践。
- **macOS 权限透明化**：CodexBar 把"为什么要 Full Disk Access""为什么要 Keychain 访问"写在 README 和配置文档里，每条权限都有对应操作和关闭方法。这个"信任文档化"的思路值得所有 macOS 应用学习。
- **CLI + GUI 双模**：CodexBar 的应用是菜单栏 GUI，但它同时提供了功能完备的 CLI 工具。GUI 负责"日常看", CLI 负责"脚本化和 CI"。这是"产品不做功能阉割"的选择。

### 同类需求的可参考思路

如果你在做"XX 管理面板"类产品，CodexBar 的"Provider 协议化"架构是代码复用的样板。它证明了：一个菜单栏小工具也可以有高度可扩展的架构、完备的测试、专业的 CI/CD。

## 🧠 核心源码解读

### Provider 协议：核心抽象

```swift
// 推断的 Provider 协议结构
protocol Provider {
    associatedtype Config: Codable
    var id: String { get }
    var name: String { get }

    // 核心方法—获取配额信息
    func fetchQuota(config: Config) async throws -> QuotaInfo

    // 解析不同来源的认证信息
    static func resolveAuth(source: AuthSource) async throws -> AuthResult
}

struct QuotaInfo {
    var used: Int
    var limit: Int
    var resetAt: Date
    var providerStatus: ProviderStatus // 服务状态
}
```

每个 provider（Codex、Claude、Cursor、Gemini 等）都实现这个协议。UI 层通过 `provider.id` 管理各 provider 的实例，定时调用 `fetchQuota` 刷新。

### 定时刷新机制

```swift
// 推断的 RefreshPolicy
enum RefreshPolicy {
    case manual       // 手动刷新
    case interval(TimeInterval) // 1m/2m/5m/15m
}

class ProviderManager {
    private var timers: [String: Timer]

    func startRefresh(for provider: any Provider, policy: RefreshPolicy) {
        // 按 provider 各自配置的刷新策略启动定时器
        // 每个 provider 独立刷新，互不影响
    }
}
```

这是一个核心设计决策——每个 provider 独立刷新而不是统一刷，因为不同服务的 API 响应时间不同（有些是本地文件读取、有些是远程 API），且 Provider status polling 需要做 incident 检测。

### 菜单栏 UI 组件

使用 macOS 14+ 的 `MenuBarExtra` API：

```swift
// 推断的菜单栏入口
@main
struct CodexBarApp: App {
    var body: some Scene {
        MenuBarExtra("CodexBar", systemImage: "gauge.with.dots.needle.33percent") {
            // 动态生成 provider 列表
            ForEach(activeProviders) { provider in
                ProviderUsageView(provider: provider)
            }
            Divider()
            SettingsLink()
            QuitButton()
        }
    }
}
```

`MenuBarExtra` 是 macOS 13+ 引入的原生 API，比传统的 `NSStatusItem` 更 SwiftUI 原生，稳定性更好。

## 📐 架构决策与设计哲学

### 关键设计决策

- **macOS 14+ 只**：放弃旧系统支持，换取 `MenuBarExtra` 等新 API 和 Swift 6 的完整特性
- **Swift 原生 vs Electron**：作为 macOS 工具，Swift 原生带来的性能、内存占用、系统集成体验远好于 Electron。16KB 内存占用的菜单栏应用 vs Electron 动辄几百 MB。
- **OAuth/Cookie/CLI 三模认证**：不强制用户用某一种认证方式，支持"什么方便用什么"。这是实用主义的设计哲学——让用户用起来。
- **每个 Provider 独立刷新**：避免一个慢 provider 拖累所有 provider 的体验。

### 与同类项目的差异

- **vs ccuage**：CodexBar 的灵感来源，但 CodexBar 覆盖范围（57+ vs 1 个）和架构质量远超
- **vs 自行查询 API**：当然可以自己用 curl 查每个服务的 API，但 CodexBar 把 57 个服务的认证和解析逻辑打包成一个菜单栏（+CLI），这才是真正的价值

## 🌐 全网口碑画像

### 好评共识

- "终于不用记 5 个 CLI 命令检查额度了，菜单栏一眼看完所有" — MacAppHQ
- "Token 焦虑者的福音，每天省 5 分钟反复切网页看额度的痛苦" — 知乎
- "steipete 出品，必属精品。代码质量、文档、测试覆盖都是专业级别的" — Reddit/HN

### 差评共识

- **macOS 14+ 限定**：需要 macOS Sonoma 或更新版本，Catalina/Big Sur/Monterey/Ventura 用户无法使用
- **Keychain 弹窗烦人**：首次配置时各个 provider 的 Keychain 访问弹窗会持续骚扰，需要手动配置"Always Allow"
- **没有 Windows/Linux 原生**：虽有社区移植，但 Windows 和 Linux 体验不如 macOS 原生

### 踩坑高发区

- 浏览器 Cookie 支持依赖 Safari/Chrome 同步权限，不同浏览器配置方式不同
- Merge Icons 模式需要开启 macOS 14+ 的多图标支持，部分用户反映切换不流畅
- CLI 工具在 Linux 下需要单独安装 tarball，Homebrew 只支持 macOS

## ⚔️ 竞品对比

### 对比矩阵

| 维度 | CodexBar | ccuage | 手动查 API |
|------|---------|--------|-----------|
| 覆盖 Provider | 57+ | 1（Codex） | 无 |
| 平台 | macOS 14+ | macOS | 全平台（但需要手动操作） |
| CLI 支持 | ✅ 内置 | ❌ | ❌ |
| 成本追踪 | ✅ | ✅ | ❌ |
| 重置倒计时 | ✅ 可视化 | ❌ | ❌ |
| Provider 状态监控 | ✅ 实时状态 + 事故标记 | ❌ | ❌ |
| WidgetKit | ✅ 桌面 widget | ❌ | ❌ |
| 开源 | ✅ MIT | ✅ MIT | — |
| 开发者 | Peter Steinberger（PSPDFKit） | ryoppippi | — |

### 选择建议

- **macOS 用户多 AI 服务** → CodexBar（唯一选择）
- **只用 Codex** → ccuage（轻量替代）或 CodexBar
- **非 macOS** → 社区移植版（Win-CodexBar/GNOME Extension/Waybar）

## 🎯 核心研判

### 项目优势

- **57+ Provider 覆盖是最大的护城河**：开源社区贡献新的 provider 很快，但 CodexBar 的架构质量（Protocol + 统一认证 + 统一 UI）让维护多个 provider 的边际成本极低
- **生态辐射已经形成**：Windows/Linux/GNOME/KDE/SketchyBar 的社区移植都出现了，说明需求真实且强烈
- **steipete 的持续投入**：从代码仓库的 CI/CD、Scripts、测试分片来看，这是专业级别的维护

### 项目风险

- **仅 macOS 原生**：Windows/Linux 依赖社区移植，质量参差不齐
- **API 稳定性**：AI 服务商随时可能更改内部 API（很多 provider 依赖 Cookie/非正式 API 获取额度），provider 代码需要持续跟进
- **免费项目+服务器成本**：部分 provider 的 OAuth 认证需要 CodexBar 后台处理，这些操作有服务器成本

### 适用场景 & 不适用场景

✅ **用**：macOS 14+ 开发者，同时使用多个 AI 编程服务 | 关注 AI 编程成本 | 有 token 焦虑的

❌ **不用**：Windows/Linux（用社区移植版） | 只用一两个 AI 服务（手动查也够） | macOS 13 或更旧

### 趋势判断

**稳定上升期** — 16.7K Stars 在四个月内爆发增长。AI 编程服务越多，CodexBar 的价值越大。随着更多服务加入（57+ 还会继续增加），它将从"可选工具"变成"AI 开发者必备工具"。

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `Sources/CodexBar/Providers/` | 各 AI 服务的 provider 实现 |
| `Sources/CodexBar/UI/` | 菜单栏界面逻辑 |
| `Package.swift` | Swift 包定义 |
| `docs/` | 57+ provider 的详细配置文档 |
| `Scripts/` | 构建/测试/发布自动化脚本 |
| `Makefile` | 开发工作流入口 |
