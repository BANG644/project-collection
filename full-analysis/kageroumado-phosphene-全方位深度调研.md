# kageroumado-phosphene - 全方位深度调研

## 项目全景
- **仓库**：`kageroumado/phosphene`
- **一句话定位**：A video wallpaper engine for macOS Tahoe
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=746 / Forks=21 / 默认分支=`main`
- **Topics**：animated-wallpaper, desktop-wallpaper, macos, macos-wallpaper
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：Phosphene(27), PhospheneExtension(18), Phosphene.xcodeproj(3), .github(1), .gitignore(1), .swift-version(1), .swiftformat(1), .swiftlint.yml(1), Info.plist(1), LICENSE(1)
- 关键文件候选：README.md

### 设计亮点研判
- 仓库包含 .github 自动化配置，通常代表 CI 或 issue 模板已被纳入工程流程。

## 源码深度解读
### README / 说明文档要点
# Phosphene

A video wallpaper engine for macOS Tahoe.

Phosphene is a menu bar app + wallpaper extension that plays your own video files as the macOS desktop and lock-screen wallpaper. It plugs into the system's native wallpaper picker, so videos appear alongside Apple's built-in Aerials in **System Settings → Wallpaper**.

It is built on top of Apple's private `WallpaperExtensionKit` framework — the same one Apple's own Aerials use — which means playback runs out-of-process, survives app quits, and integrates with the OS-level lock-screen / idle / sleep lifecycle.

> ⚠️ **Private framework.** Phosphene loads `WallpaperExtensionKit` via `dlopen` and uses Mirror-based runtime introspection to talk to its XPC types. Apple could change this at any major OS release. The project tracks macOS 26 (Tahoe).

## Features

- **Bring your own videos.** Import MP4 / MOV / any AVFoundation-readable file. They show up in the system wallpaper picker.
- **Gapless looping.** Frame-accurate loops by offsetting PTS/DTS across loop boundaries — no flush, no stutter.
- **Multi-display + per-Space selections.** Different wallpapers per display, persisted by macOS.
- **Power-aware playback.** A graduated `PlaybackPolicy` reduces work or pauses entirely based on thermal state, battery level, on-battery vs AC, Game Mode, and presentation mode (active / locked / idle).
- **Smooth lock-screen ramp.** When *Only on Lock Screen* is enabled, the wallpaper eases in/out with a cubic curve as you lock and unlock, matching Apple's own Aerials behavior.
- **Pause when occluded.** Detects when every display is fully covered by windows and pauses rendering until the desktop is visible again.
- **Adaptive variants.** Optionally pre-render lower-resolution / lower-fps variants of a video; the renderer swaps to the cheapest variant that satisfies the current policy at each loop boundary.
- **Menu bar control.** Preview the current wallpaper, toggle pause, switch displays, configure behavior, launch at login.

## Requirements

- **macOS Tahoe (26.0+).** Phosphene depends on the Wallpaper extension point introduced in macOS 14 but uses Tahoe-only SwiftUI and `glassEffect()` APIs.
- **Apple Silicon.** Ta
...[truncated]

### 关键文件精读
### `README.md`
```
# Phosphene

A video wallpaper engine for macOS Tahoe.

Phosphene is a menu bar app + wallpaper extension that plays your own video files as the macOS desktop and lock-screen wallpaper. It plugs into the system's native wallpaper picker, so videos appear alongside Apple's built-in Aerials in **System Settings → Wallpaper**.

It is built on top of Apple's private `WallpaperExtensionKit` framework — the same one Apple's own Aerials use — which means playback runs out-of-process, survives app quits, and integrates with the OS-level lock-screen / idle / sleep lifecycle.

> ⚠️ **Private framework.** Phosphene loads `WallpaperExtensionKit` via `dlopen` and uses Mirror-based runtime introspection to talk to its XPC types. Apple could change this at any major OS release. The project tracks macOS 26 (Tahoe).

## Features

- **Bring your own videos.** Import MP4 / MOV / any AVFoundation-readable f
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像是**围绕单一目标组织的任务流水线/工具链**，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #11 [OPEN] Validate WallpaperExtension XPC callers before accepting connections（comments=[] labels=无）
- #10 [OPEN] Reduce filesystem blast radius with app sandbox and a documented shared container（comments=[] labels=无）
- #8 [OPEN] Harden private runtime bridging and unsafe WallpaperExtensionKit shims（comments=[] labels=无）
- #9 [OPEN] Validate library metadata and prevent path traversal（comments=[] labels=无）
- #2 [OPEN] Grey/black wallpaper after resuming from hibernation（comments=[{'id': 'IC_kwDOSjbwsM8AAAABDQ2-GQ', 'author': {'login': 'kageroumado'}, 'authorAssociation': 'OWNER', 'body': "Thanks for the report.\n\nI couldn't reproduce this locally — without triggering true hibernation, the `screensDidWake` recovery path seems to work. My current theories:\n\n1. After hibernation, `NSWorkspace.screensDidWakeNotification` may not fire, so the extension never recomputes its policy → renderer stays paused.\n2. The notification *does* fire, but the `CAContext` / render surface has been invalidated by WindowServer during hibernation, so we end up rendering into a layer that's no longer presented → grey/black.\n3. `AVAssetReader` fails to restart after wake.\n\nTo narrow this down, I've pushed a debug branch with extra logging around the sleep/wake/recreate path: [`debug/hibernation-diagnostics`](https://github.com/kageroumado/phosphene/tree/debug/hibernation-diagnostics).\n\nIf you can build from source and reproduce, that log would be very helpful:\n\n1. Clone the branch and open it in Xcode:\n   ```sh\n   git clone -b debug/hibernation-diagnostics https://github.com/kageroumado/phosphene.git\n   cd phosphene\n   open Phosphene.xcodeproj\n   ```\n   Set your own development team under Signing & Capabilities (the extension has to be signed for macOS to load it), then Run.\n\n2. Reproduce the issue — hibernate the machine, wake it, confirm the grey wallpaper.\n\n3. Attach the extension log here:\n   ```\n   ~/Library/Containers/glass.kagerou.phosphene.extension/Data/Documents/extension.log\n   ```\n   Lines tagged `[Diag #2]` should tell us which notifications fired on wake and whether the asset reader was able to start again.\n\nIf building from source isn't an option, let me know and I'll cut a signed debug DMG instead.", 'createdAt': '2026-05-22T00:46:52Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/kageroumado/phosphene/issues/2#issuecomment-4513971737', 'viewerDidAuthor': False}, {'id': 'IC_kwDOSjbwsM8AAAABEIeJ6A', 'author': {'login': 'lfuelling'}, 'authorAssociation': 'NONE', 'body': "Hi, I was able to reproduce the issue today, but I don't see any obvious issue in the log:\n\n<details>\n<summary>Output in <code>extension.log</code></summary>\n<pre>\n[2026-05-28T16:20:15Z]   VideoRenderer started (reply deferred 500ms for render pipeline)\n[2026-05-28T16:20:15Z]   [BMPCache] Rendering 1280x720 BGR24 (2764800 bytes, row=3840)\n[2026-05-28T16:20:15Z]   [BMPCache] Wrote 2764854 bytes → 8aecb3b02bb6269d1560446400ddfb12bc8960921517ea3f1b14a4476bedd2cd-5120-2880-0-41c7e4515fec3a5c.bmp\n[2026-05-28T16:20:16Z]   Replying to acquire [pipeline ready] (contextId: 3527855915)\n[2026-05-28T16:20:16Z]   WARNING: No context found for wallpaperID BEDA6354-6ACB-4EF3-8895-D467EBDE1A59\n[2026-05-28T16:20:16Z] === INVALIDATE === (cleaned: false, remaining: 2)\n[2026-05-28T16:20:16Z] === INVALIDATE === (cleaned: false, remaining: 2)\n[2026-05-28T16:20:16Z] === SNAPSHOT ===\n[2026-05-28T16:20:16Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:16Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:20Z] === UPDATE === mode: default, activity: active\n[2026-05-28T16:20:20Z] === SNAPSHOT ===\n[2026-05-28T16:20:20Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:20Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:22Z] === UPDATE === mode: idle, activity: active\n[2026-05-28T16:20:22Z] === SNAPSHOT ===\n[2026-05-28T16:20:22Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:22Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:27Z] === UPDATE === mode: default, activity: active\n[2026-05-28T16:20:27Z] === SNAPSHOT ===\n[2026-05-28T16:20:27Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:27Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:32Z] === INVALIDATE === (cleaned: true, remaining: 1)\n[2026-05-28T16:20:32Z] === SNAPSHOT ===\n[2026-05-28T16:20:32Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:32Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:38Z] === SNAPSHOT ===\n[2026-05-28T16:20:38Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:38Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:38Z] === SNAPSHOT ===\n[2026-05-28T16:20:38Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:38Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:38Z] === SNAPSHOT ===\n[2026-05-28T16:20:38Z] === UPDATE === mode: locked, activity: active\n[2026-05-28T16:20:38Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:38Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:38Z] === SNAPSHOT ===\n[2026-05-28T16:20:38Z] [Extension] Screen locked\n[2026-05-28T16:20:38Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:38Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:40Z] === UPDATE === mode: default, activity: active\n[2026-05-28T16:20:40Z] === SNAPSHOT ===\n[2026-05-28T16:20:40Z] [Extension] Screen unlocked — recomputed policy\n[2026-05-28T16:20:40Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:40Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:40Z] === SNAPSHOT ===\n[2026-05-28T16:20:40Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:40Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:44Z] === SNAPSHOT ===\n[2026-05-28T16:20:44Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:44Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:44Z] === SNAPSHOT ===\n[2026-05-28T16:20:44Z] === UPDATE === mode: locked, activity: active\n[2026-05-28T16:20:44Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:44Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:44Z] [Extension] Screen locked\n[2026-05-28T16:20:44Z] === SNAPSHOT ===\n[2026-05-28T16:20:44Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:44Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:20:52Z] === PROVIDE SETTINGS VIEW MODELS ===\n[2026-05-28T16:20:52Z] [VideoLibrary] Scanned: 1 video(s)\n[2026-05-28T16:20:52Z]   [Settings] Remapped to WallpaperSettingsViewModelsXPC\n[2026-05-28T16:20:58Z] === UPDATE === mode: locked, activity: suspended\n[2026-05-28T16:20:58Z] === SNAPSHOT ===\n[2026-05-28T16:20:58Z]   [Renderer] Failed to generate still frame\n[2026-05-28T16:20:58Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:20:58Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:21:28Z]   [Renderer] Deep-paused — freed asset readers\n[2026-05-28T16:22:00Z] === UPDATE === mode: locked, activity: active\n[2026-05-28T16:22:00Z] === SNAPSHOT ===\n[2026-05-28T16:22:00Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:22:00Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:22:05Z] === UPDATE === mode: default, activity: active\n[2026-05-28T16:22:05Z] === SNAPSHOT ===\n[2026-05-28T16:22:05Z] [Extension] Screen unlocked — recomputed policy\n[2026-05-28T16:22:05Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:22:05Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:22:05Z] === SNAPSHOT ===\n[2026-05-28T16:22:05Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:22:05Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:22:08Z] === SNAPSHOT ===\n[2026-05-28T16:22:08Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:22:08Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:22:08Z] === SNAPSHOT ===\n[2026-05-28T16:22:08Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:22:08Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:22:08Z] === SNAPSHOT ===\n[2026-05-28T16:22:08Z] === UPDATE === mode: locked, activity: active\n[2026-05-28T16:22:08Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:22:08Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:22:08Z] === SNAPSHOT ===\n[2026-05-28T16:22:08Z] [Extension] Screen locked\n[2026-05-28T16:22:08Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:22:08Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:22:08Z] === UPDATE === mode: locked, activity: suspended\n[2026-05-28T16:22:08Z] === SNAPSHOT ===\n[2026-05-28T16:22:08Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-28T16:22:08Z]   Snapshot replied (IOSurface)\n[2026-05-28T16:22:38Z]   [Renderer] Deep-paused — freed asset readers\n[2026-05-28T16:25:33Z] [WallpaperPrefs] setActive(false, video: nil)\n[2026-05-28T16:25:33Z] XPC invalidated — cleaned up 1 active context(s)\n[2026-05-28T22:00:00Z] handleNotification(SignificantTimeChangeNotification)\n[2026-05-29T07:47:50Z] === UPDATE === mode: locked, activity: active\n[2026-05-29T07:47:50Z] === SNAPSHOT ===\n[2026-05-29T07:47:50Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-29T07:47:50Z]   Snapshot replied (IOSurface)\n[2026-05-29T07:47:50Z] === UPDATE === mode: default, activity: active\n[2026-05-29T07:47:50Z] === SNAPSHOT ===\n[2026-05-29T07:47:50Z] [Extension] Screen unlocked — recomputed policy\n[2026-05-29T07:47:50Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-29T07:47:50Z]   Snapshot replied (IOSurface)\n[2026-05-29T07:47:50Z] === SNAPSHOT ===\n[2026-05-29T07:47:50Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-29T07:47:50Z]   Snapshot replied (IOSurface)\n[2026-05-29T07:48:26Z] === SNAPSHOT ===\n[2026-05-29T07:48:26Z]   [Snapshot] Created WallpaperSnapshotXPC 1280x720\n[2026-05-29T07:48:26Z]   Snapshot replied (IOSurface)\n</pre>\n</details>\n\nWhile the main monitor was showing the video and after waking up today only a grey wallpaper, the second monitor always shows the (apple) video wallpaper that was selected before (some space scene).", 'createdAt': '2026-05-29T07:54:55Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/kageroumado/phosphene/issues/2#issuecomment-4572285416', 'viewerDidAuthor': False}] labels=无）
- #1 [OPEN] 2 monitor setup: it switches the other monitor to the last chosen wallpaper after 1 loop.（comments=[{'id': 'IC_kwDOSjbwsM8AAAABDQcnmQ', 'author': {'login': 'kageroumado'}, 'authorAssociation': 'OWNER', 'body': 'Could you please confirm the fix? I don’t have two monitors so I can’t test', 'createdAt': '2026-05-21T23:19:41Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/kageroumado/phosphene/issues/1#issuecomment-4513539993', 'viewerDidAuthor': False}, {'id': 'IC_kwDOSjbwsM8AAAABDQ1fgA', 'author': {'login': 'yourdallaness'}, 'authorAssociation': 'NONE', 'body': "i tried building but after that the phosphene wallpapers group disappeared for system settings wallpapers screen. tried removing and adding the videos back in phosphene. didn't work. even opening the downloaded installed 1.0 .app file in my applications folder is not working anymore.", 'createdAt': '2026-05-22T00:43:31Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/kageroumado/phosphene/issues/1#issuecomment-4513947520', 'viewerDidAuthor': False}, {'id': 'IC_kwDOSjbwsM8AAAABDQ327g', 'author': {'login': 'kageroumado'}, 'authorAssociation': 'OWNER', 'body': 'Oh that’s because the loader is confused about which extension to load. To fix the issue, clear DerivedData for phosphene, specifically you want the Products folder to be empty.\n\nTo test the debug version, drag that version to your applications folder and overwrite, then remove the duplicate files if any are present, launch the new app then open-close the wallpaper section in Settings. This will trigger a reload. Then it should work.', 'createdAt': '2026-05-22T00:50:18Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/kageroumado/phosphene/issues/1#issuecomment-4513986286', 'viewerDidAuthor': False}, {'id': 'IC_kwDOSjbwsM8AAAABDXQj5Q', 'author': {'login': 'yourdallaness'}, 'authorAssociation': 'NONE', 'body': "i don't know anything about mac os dev. Based on your info, I did:\n\nI replaced `/Applications/Phosphene.app` with `/Users/yourdallaness/Library/Developer/Xcode/DerivedData/Phosphene-cfxituszgafgdqbuucgqnnhovkbi/Build/Products/Debug/Phosphene.app`.\n\nThen deleted `/Users/yourdallaness/Library/Developer/Xcode/DerivedData/Phosphene-cfxituszgafgdqbuucgqnnhovkbi/Build/Products`.\n\nNothing changed even after restarting the computer and opening phosphene.", 'createdAt': '2026-05-22T16:37:06Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/kageroumado/phosphene/issues/1#issuecomment-4520682469', 'viewerDidAuthor': False}] labels=无）

### Pull Requests 抽样
- PR #12 [OPEN] Fix multi-monitor wallpaper flip after loop boundary
- PR #7 [CLOSED] Capture per-context videoID in variantSelector (fixes #1)
- PR #6 [MERGED] Document headless build instructions
- PR #5 [OPEN] Clean up renderer layers on stop
- PR #4 [OPEN] Rotate extension logs

### Releases 抽样
- v1.0（published=2026-05-21T01:30:59Z latest=True）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 6/0，可作为维护者响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 2 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者有版本化交付意识。
- 由于本批处理以 GitHub 官方数据为主，若外部搜索结果缺失，应把 GitHub issue/PR 视为最可信的一手社区反馈源。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## 竞品对比
| 维度 | phosphene | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | LangGraph / AutoGen / CrewAI 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `README.md`

## 3 条关键发现
- 代码入口/骨架集中在：README.md
- 近期开源反馈以 issue 为主，典型议题包括：Validate WallpaperExtension XPC callers before accepting connections；Reduce filesystem blast radius with app sandbox and a documented shared container
- 发布节奏可从最新 release 观察：v1.0

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
