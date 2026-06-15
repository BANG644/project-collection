# pbakaus/impeccable 深度调研报告

> 调研日期：2026-06-15 | 协议：MIT | 核心功能：AI 编码助手的前端设计技能包

## 一、项目定位

**Impeccable** 是一个专为 AI 编码助手设计的前端设计技能包（Design Skill），由 Google Chrome DevTools 前产品经理 Paul Bakaus 创建。它提供了一套完整的"设计引导系统"——包含 23 个命令、41 条确定性检测规则和浏览器实时迭代能力，帮助 AI 编码助手生成更高质量的前端 UI。

### 核心定位
- **AI 设计导师**：不是模板库或组件库，而是一套设计决策框架
- **多工具兼容**：支持 Claude Code、Cursor、Gemini CLI、Codex CLI、GitHub Copilot 等主流 AI 编码工具
- **确定性 + LLM 混合检查**：41 条规则可离线运行，无需 API Key

### 项目起源
受 Anthropic 的 [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) 启发。Impeccable 从那里出发，但显著扩展了设计覆盖面和工具集成深度。

## 二、核心架构

```
impeccable/
├── skills/              # 各 AI 工具的技能文件
│   ├── claude/         # Claude Code
│   ├── cursor/         # Cursor
│   ├── gemini/         # Gemini CLI
│   ├── codex/          # Codex CLI
│   └── github/         # GitHub Copilot
├── dist/               # 编译后的分发文件
├── src/
│   ├── rules/          # 41 条确定性检测规则
│   ├── commands/       # 23 个设计命令实现
│   └── detectors/      # LLM-only 检查器
└── agents/             # Codex 子 Agent
```

### 技术特性
- **无依赖检测**：CLI 和浏览器扩展可以直接运行确定性规则，无需 LLM 调用
- **跨平台安装**：自动检测 AI 工具类型并安装到正确位置
- **Git 友好**：支持作为子模块 vendored 到项目中

## 三、23 个命令全景

| 命令 | 功能 | 使用场景 |
|------|------|----------|
| `init` | 一次性设置：写 PRODUCT.md 和 DESIGN.md | 新项目启动 |
| `craft` | 完整的"塑形→构建"流程 | 从零开始设计 |
| `polish` | 最终打磨、设计系统对齐 | 发布前检查 |
| `audit` | 技术质量检查（a11y、性能、响应式） | 代码审查 |
| `critique` | UX 设计评审 | 设计审查 |
| `shape` | 写代码前的 UX/UI 规划 | 设计阶段 |
| `distill` | 剥离到核心本质 | 过度设计 |
| `bolder` | 增强平淡设计 | 视觉提升 |
| `quieter` | 调低过度设计 | 视觉降噪 |
| `animate` | 添加有目的的运动 | 动效设计 |
| `colorize` | 引入战略性色彩 | 配色优化 |
| `typeset` | 修复字体选择、层级、大小 | 排版优化 |
| `layout` | 修复布局、间距、视觉节奏 | 布局优化 |
| `harden` | 错误处理、国际化、文本溢出 | 健壮性 |
| `onboard` | 首次运行流程、空状态 | 用户体验 |
| `clarify` | 改善模糊的 UX 文案 | 文案优化 |
| `adapt` | 适配不同设备 | 响应式 |
| `optimize` | 性能优化 | 性能 |
| `delight` | 添加愉悦瞬间 | 微交互 |
| `overdrive` | 添加技术惊艳效果 | 炫技 |
| `extract` | 提取可复用组件和 tokens | 设计系统 |
| `document` | 从现有代码生成 DESIGN.md | 文档化 |
| `live` | 浏览器中实时迭代变体 | 实时设计 |

## 四、41 条检测规则

### 设计禁忌（Detector Rules）
- ❌ 不要使用过时字体（Arial、Inter、系统默认）
- ❌ 不要在彩色背景上使用灰色文字
- ❌ 不要使用纯黑/灰色（务必加色相）
- ❌ 不要把一切包装在卡片里，或卡片套卡片
- ❌ 不要使用弹跳/弹性缓动（显得过时）

### 设计原则
- ✅ 选择与品牌匹配的特色字体
- ✅ 使用有色的中性色（never pure gray/black）
- ✅ 有目的的留白和呼吸空间
- ✅ 一致的间距节奏
- ✅ 清晰的视觉层级

## 五、社区口碑

### 优势
- **设计思维系统化**：将 UI 设计原则编码为 AI 可理解的命令和规则
- **工具无关**：支持 10+ AI 编码工具，覆盖面广
- **确定性检查**：41 条规则可离线运行，无需 LLM，节省成本
- **实战验证**：附有 before/after 案例研究

### 局限
- **学习成本**：23 个命令较多，需要时间熟悉
- **AI 依赖**：部分命令（如 critique）仍需要 LLM 支持
- **CSS 偏重**：更多关注视觉设计，后端/数据流设计覆盖不足

## 六、竞品对比

| 特性 | Impeccable | Anthropic frontend-design | Tailwind CSS |
|------|:---:|:---:|:---:|
| 命令数 | 23 | 1 | N/A |
| 检测规则 | 41 | 无 | 无 |
| 多工具支持 | 10+ | 仅 Claude | 所有 |
| 确定性检查 | ✅ | ❌ | ✅ |
| 浏览器实时迭代 | ✅ | ❌ | ❌ |
| 设计系统提取 | ✅ | ❌ | ✅ |

## 七、核心研判

1. **设计引导的范式创新**：Impeccable 代表了 AI 编码领域从"代码生成"到"设计引导"的演进方向
2. **确定性 + LLM 混合架构**：41 条规则 + LLM 检查的混合模式是实用主义的最佳实践
3. **反 SaaS 模板陷阱**：针对"所有 AI 看起来都一样"的问题提供了系统化解决方案
4. **作者背书**：Paul Bakaus 的 Chrome DevTools 背景为项目增添了可信度

## 八、关键文件路径

- **主仓库**：`https://github.com/pbakaus/impeccable`
- **官网**：`https://impeccable.style`
- **安装方式**：`npx impeccable skills install`
- **案例研究**：`https://impeccable.style#casestudies`
- **许可证**：MIT
