# Sylinko/Everywhere 深度调研

> 调研日期：2026-09-29 ｜ 数据源：gh API（README / 目录树 / AGENTS.md / topics）｜ 定位：桌面端"屏幕感知"AI 助手

## 一、项目定位（一句话）

**Everywhere** 是一个用 C# + Avalonia 打造的跨平台桌面 AI 助手，核心卖点是"屏幕感知"——无需截图、复制或切换应用，按一个快捷键就能理解当前屏幕上的任何内容并就地给出帮助。

## 二、项目亮点（差异化）

1. **真正的"就地感知"，而非截图式**：主打"instantly perceives and understands anything on your screen"，强调不需要截图/复制/切应用，直接在当前上下文旁唤起助手。
2. **多模型生态齐备**：内置 Everywhere Cloud，并兼容 OpenAI、Anthropic(Claude)、Google(Gemini)、DeepSeek、Moonshot(Kimi)、MiniMax、本地 Ollama，以及自定义 API endpoint。
3. **MCP + Skills 原生支持**：topics 直接带 `mcp`/`skills`/`hermes-agent`/`openclaw`，是少数把"屏幕感知 + MCP 工具调用 + Agent 技能"三者合一的桌面壳。
4. **工程纪律扎实**：仓库自带 `AGENTS.md`、CI、`.NET 10` + 源码生成器（I18N / Configuration SourceGenerator）、Watchdog 看门狗进程，跨 Windows / macOS / Linux 三套 `.slnx` 解决方案。
5. **社区曝光强**：Trendshift / Product Hunt / HelloGitHub 三平台联合推荐，文档站 `everywhere.sylinko.com` 与中文/日文 README 齐备。

## 三、核心架构

- **技术栈**：.NET 10 + Avalonia UI（跨平台 XAML 框架），客户端形态覆盖 Windows / macOS / Linux。
- **分层项目结构**（`src/`）：
  - `Everywhere.Core` — 核心逻辑（屏幕上下文抓取、模型调度、策略引擎）
  - `Everywhere.Cloud` — 云端服务对接层
  - `Everywhere.Windows` / `Everywhere.Mac` / `Everywhere.Linux` — 各平台原生集成（无障碍/窗口上下文）
  - `Everywhere.Terminal` — 终端入口
  - `Everywhere.Watchdog` — 看门狗保活进程（`Build.Watchdog.targets`）
  - `Everywhere.I18N.*` / `Everywhere.Configuration.SourceGenerator` — 源码生成器（i18n 与配置类型安全）
- **AGENTS.md 定规矩**：明确要求"未显式指令不改动代码""改前先查实现与调用点""不全局格式化制造无关 diff""引入 NuGet 先与用户讨论"，并强制按任务领域读取 `docs/References/*` 再动手。

## 四、应用场景与启发

- **场景**：报错即时诊断、长文原地总结、划词翻译、邮件/文档润色、信息真伪核查——本质是"悬浮在任意窗口上的上下文感知副驾驶"。
- **启发（对同类需求）**：
  - 想做"AI 读懂当前屏幕"类产品，Everywhere 给出了**Avalonia 跨平台 + 平台原生上下文抓取 + 多 LLM 抽象 + MCP 工具总线**的成熟骨架，可直接 fork 改造成内部助手。
  - 其 `AGENTS.md` 的"任务域引用文档按需加载"模式值得抄：把厚重设计文档拆到 `docs/References/`，由 AGENTS.md 指路，避免 AI 一次读爆上下文。
  - 对用户的 WorkBuddy 技能体系而言，Everywhere 是"桌面端 MCP 客户端 + 屏幕感知"的现成参照，可与已有 agent skill 思路对照。

## 五、源码深度解读（核心模块）

**1. 平台原生上下文层（`Everywhere.Windows` / `Everywhere.Mac` / `Everywhere.Linux`）**
三套平台工程分别实现"当前窗口/控件上下文提取"。这是 Everywhere 区别于纯截图方案的关键——通过系统无障碍/窗口 API 拿到结构化上下文，而非位图。

**2. 配置源码生成器（`Everywhere.Configuration.SourceGenerator`）**
用 Roslyn Source Generator 在编译期把配置 schema 生成强类型绑定，避免运行时反射与字符串键错误，是大型 .NET 客户端常见的"配置即类型"实践。

**3. 看门狗（`Everywhere.Watchdog` + `Build.Watchdog.targets`）**
独立进程保活主程序，构建期通过 MSBuild targets 注入，保证助手常驻不被系统回收——桌面常驻 AI 的必选项。

## 六、社区口碑

- 三平台联合推荐（Trendshift 徽章、Product Hunt 精选、HelloGitHub 推荐），说明在国内外独立开发者圈层都有传播。
- Discord + QQ 双社群运营，中文/日文文档齐全，对国内用户友好。
- 星标增长快（6.3k⭐，pushed_at 2026-09-28，高度活跃）。
- 数据合规：`DATA_AND_PRIVACY.md` 单列，说明团队对"屏幕读取"的隐私敏感点有意识。

## 七、竞品对比 + 核心研判

| 维度 | Everywhere | Maccy/面是之类截图工具 | Raycast AI | 各类"截图→LLM"脚本 |
|---|---|---|---|---|
| 屏幕感知 | 结构化上下文（非截图） | 仅截图 | 无 | 截图 |
| 多 LLM | ✅ 8+ | ❌ | ✅ 有限 | 自接 |
| MCP/技能 | ✅ 原生 | ❌ | 部分 | ❌ |
| 跨平台 | ✅ | ❌ | ❌(Mac) | ✅ |

**研判**：Everywhere 卡位"桌面端上下文感知 AI 壳"是正确的差异化方向，技术成熟度（Avalonia + 源码生成器 + AGENTS.md）高于同类个人项目。**最大风险是许可证**——`spdx_id: NOASSERTION`（仓库 LICENSE 为 "Other"），并非标准 OSI 许可，二次分发/商用前需向作者确认条款。整体值得作为"桌面 MCP 客户端"方向的范本库长期跟踪。

## 八、关键文件路径速查

- 仓库根：`https://github.com/Sylinko/Everywhere`
- 文档站：`https://everywhere.sylinko.com`
- 工程规约：`AGENTS.md`、`docs/References/`（Avalonia 视图/虚拟化/动画等）
- 核心层：`src/Everywhere.Core/`、`src/Everywhere.Cloud/`
- 平台层：`src/Everywhere.Windows/`、`src/Everywhere.Mac/`、`src/Everywhere.Linux/`
- 基础设施：`src/Everywhere.Watchdog/`、`src/Everywhere.Configuration.SourceGenerator/`、`src/Everywhere.I18N.SourceGenerator/`
- 隐私说明：`DATA_AND_PRIVACY.md`
- 解决方案：`Everywhere.Windows.slnx` / `Everywhere.Mac.slnx` / `Everywhere.Linux.slnx`
