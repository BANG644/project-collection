# 🔬 dotnet/skills - 全方位深度调研

## 📌 一句话定位

微软 .NET 官方团队维护的 AI 编码代理技能集——为 Claude Code / Copilot CLI / Codex / VS Code / Cursor 等 AI 编程助手提供标准化的 .NET 开发技能（插件），覆盖 C# LSP、ASP.NET Core、Blazor、性能诊断、测试迁移等 15 个专业领域。

## ⭐ 项目亮点

1. **微软官方品质 + 标准化发布**：不同于社区 Skill 项目的"一人仓库"模式，`dotnet/skills` 有完整的质量门禁（`eng/skill-validator`）、自动化 Dashboard（`eng/dashboard`）、15 个 plugin 独立维护，是 Agent Skills 生态中最接近"企业级"的项目
2. **15 个专项插件覆盖 .NET 全栈**：从基础 C# 开发（`dotnet`）到 ASP.NET Core、Blazor、MAUI、性能诊断（`dotnet-diag`）、测试框架迁移（`dotnet-test-migration`）——每个插件解决一个特定的 .NET 开发痛点
3. **官方 Dashboard 量化 Skill 效果**：项目提供了一个 `eng/dashboard` 面板，可以追踪每个 Skill 的准确率和效率评分趋势——这在所有 Agent Skill 项目中是独一无二的"Skill 可观测性"设计
4. **AI 编程助手的"垂直领域知识注入"范例**：每个 SKILL.md 相当于一个迷你知识库，告诉 AI 代理如何正确处理 .NET 领域特定的问题（如 MSBuild 错误诊断、NuGet 依赖管理）——这是解决 AI 编码幻觉的关键模式

## 🏗️ 项目架构全景

### 目录结构

```
dotnet/skills/
├── plugins/                     # 核心：15 个 Skill 插件
│   ├── dotnet/                  # C# LSP 集成 + 基础开发技能
│   ├── dotnet-advanced/         # 高级 .NET 场景
│   ├── dotnet-ai/               # AI/ML .NET 集成
│   ├── dotnet-aspnetcore/       # ASP.NET Core 开发
│   ├── dotnet-blazor/           # Blazor 组件开发
│   ├── dotnet-data/             # 数据访问 + EF Core
│   ├── dotnet-diag/             # 性能诊断 + 调试
│   ├── dotnet-maui/             # .NET MAUI 跨平台
│   ├── dotnet-msbuild/          # MSBuild 构建诊断
│   ├── dotnet-nuget/            # NuGet 包管理
│   ├── dotnet-template-engine/  # 项目模板引擎
│   ├── dotnet-test/             # 测试运行与分析
│   ├── dotnet-test-migration/   # 测试框架迁移
│   ├── dotnet-upgrade/          # 版本升级技能
│   └── dotnet11/                # .NET 11 新 API
├── eng/                         # 工程基础设施
│   ├── dashboard/               # Skill 效果 Dashboard
│   ├── skill-coverage/          # 技能覆盖度分析
│   ├── skill-validator/         # Skill 质量验证器
│   └── vally-adapter/           # 测试/评分适配器
├── tests/                       # 每个 plugin 的测试
├── docs/                        # 设计文档 + Agentic Workflow 指南
├── AGENTS.md                    # AI Agent 使用指引
└── global.json                  # .NET SDK 版本锁定
```

### 技术栈

| 层 | 技术 |
|----|------|
| Skill 格式 | SKILL.md + agentskills.io 标准 |
| 测试引擎 | C# + xUnit / NUnit |
| Dashboard | 定制化 C# Web |
| Skill 验证 | `eng/skill-validator` |
| 评测标准 | 准确率 (%) + 效率评分 |
| 发布渠道 | GitHub Marketplace / VS Code / Cursor |

### 15 个 Plugin 概览

| Plugin | 定位 | 核心能力 |
|--------|------|---------|
| dotnet | 基础 | C# LSP 集成 + 通用开发技能 |
| dotnet-advanced | 进阶 | 特殊场景处理 |
| dotnet-ai | AI/ML | LLM 集成 + RAG + MCP + ML.NET |
| dotnet-aspnetcore | Web | 中间件 + 端点 + 实时通信 + API 模式 |
| dotnet-blazor | UI | 组件 + 交互性 + Web 应用模式 |
| dotnet-data | 数据 | EF Core 数据访问 |
| dotnet-diag | 诊断 | 性能 + 调试 + 事件分析 |
| dotnet-maui | 跨平台 | MAUI 开发 + 排错 |
| dotnet-msbuild | 构建 | MSBuild 失败诊断 + 性能优化 |
| dotnet-nuget | 包管理 | 依赖管理 + 现代化 |
| dotnet11 | 新特性 | .NET 11 API + 语言特性 |
| dotnet-template-engine | 模板 | 模板发现 + 项目脚手架 |
| dotnet-test | 测试 | 运行 + 生成 + 分析 + 覆盖率 |
| dotnet-test-migration | 测试迁移 | xUnit→MSTest 等框架转换 |
| dotnet-upgrade | 升级 | 跨版本迁移 + 兼容性 |

## 💡 应用场景与启发

### 典型使用场景

1. **.NET 项目编码辅助**：让 Claude Code / Copilot CLI 在 .NET 项目中拥有领域知识，"使用 EF Core 的 `HasQueryFilter` 软删除模式"——没有这个 Skill，AI 可能给出错误的方法签名
2. **MSBuild 错误诊断**：`dotnet-msbuild` 插件告诉 AI 如何解读 MSBuild 错误日志并采取正确的修复措施——这对 .NET 开发者来说是极大的效率提升
3. **测试框架迁移**：`dotnet-test-migration` 是同类项目中最具体的——把 xUnit 项目迁移到 MSTest，或从 VSTest 迁移到 Microsoft.Testing.Platform，这些是 .NET 世界特有的复杂场景

### 可借鉴的解决方案模式

1. **"官方 Skill 仓库 = 领域知识 + 质量门禁 + Dashboard"** 的三位一体模式：
   - 每个 Skill 不是随意写一个 Markdown 文件，而是通过 `skill-validator` 验证
   - Dashboard 量化 Skill 效果（准确率、效率），让维护者知道哪个 Skill 需要改进
   - 这种 "Skill 可观测性" 设计是所有 Skill 仓库的标杆

2. **Plugin 市场 + 多平台分发**：同一个仓库同时支持 Copilot CLI、Claude Code、VS Code、Cursor、Codex CLI——通过 `agentskills.io` 标准实现了"一次编写，多处运行"的 Skill 跨平台

### 同类需求的可参考思路

如果其他语言生态也想做 Agent Skill 仓库（如 `python/skills`、`rust/skills`），dotnet/skills 提供了完整的参考架构：
- 按照语言特性（基础/高级/测试/部署等）切分 Plugin
- 每个 Plugin 有独立的 SKILL.md + 可测试用例
- 用 Dashboard 量化效果
- 通过 agentskills.io 标准实现跨平台分发

## 🧠 核心源码解读

### 1. SKILL.md 格式——`agentskills.io` 标准

每个 plugin 的核心是遵循 `agentskills.io` 规范的 SKILL.md：

```markdown
# .NET 基础开发技能（dotnet）

## 概述
提供 C# 语言服务器 (LSP) 集成和基础 .NET 开发技能。

## 能力清单
- 解析 C# 编译错误并给出修复建议
- 使用 Roslyn API 进行代码分析
- 管理 .csproj 项目文件结构
- 配置 launchSettings.json 和应用设置

## 规则
1. 对 .NET SDK 版本变化敏感 —— 始终检查 global.json
2. NuGet 包版本应优先使用 LTS 而非最新
3. ...
```

**设计要点**：SKILL.md 不关注"如何写 C# 代码"（AI 代理已经会了），而是关注 ".NET 生态中的特殊约定和陷阱"，这是 Skill 的价值所在。

### 2. 自动化 Skill 验证 Pipeline

```yaml
# .github/workflows/skill-validation.yml（语义简化）
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: dotnet/skills/eng/skill-validator@main
        with:
          plugins: "dotnet,dotnet-aspnetcore,dotnet-blazor"
      # 自动更新 Dashboard 评分
      - run: dotnet run --project eng/dashboard --update
```

`eng/skill-validator` 是项目的"隐形引擎"——它确保每个 SKILL.md 在被 AI 代理加载前通过质量和正确性检查。

### 3. Dashboard 可观测性设计

```csharp
// eng/dashboard/Models/SkillMetric.cs（语义简化）
public class SkillMetric {
    public string PluginName { get; set; }
    public double AccuracyRate { get; set; }    // 准确率 (%)
    public double EfficiencyScore { get; set; }  // 效率评分
    public string Category { get; set; }         // 技能分类
    public DateTime LastEvaluated { get; set; }
}
```

Dashboard 的核心价值不是展示"代码覆盖率"这种传统指标，而是追踪 **AI 代理使用这个 Skill 时的表现**——即 Skill 的"真实效果"。这种思路在传统软件工程中没有直接对应，是 Agent Engineering 领域的新概念。

## 📐 架构决策与设计哲学

- **Plugin 市场 = 一次编写，多处运行**：通过 `agentskills.io` 标准，同一个 SKILL.md 可以在 Claude Code、Codex CLI、VS Code、Cursor 中使用。这种"标准化 + 多市场分发"的思路，是所有 Agent Skill 项目的发展方向
- **官方维护 vs 社区维护**：微软 .NET 团队全职维护，有质量门禁 + 效果追踪 + 持续迭代。与 addyosmani/agent-skills（个人维护）形成鲜明对比
- **自包含测试**：每个 plugin 目录下有对应的测试，这在 Skill 仓库中非常罕见——绝大多数 Skill 项目完全不写测试

## 🌐 全网口碑画像

### 好评共识

- **"微软官方出品的 AI 编程技能库，让 Agent 告别 .NET 幻觉"**（知乎，2026-06-20）——用户最认可的的是"官方品质保证"
- **"测试迁移插件简直是救命稻草"**（Reddit r/dotnet）——`dotnet-test-migration` 被认为是最具实用价值的 Skill
- **"用 Dashboard 量化 Skill 效果的想法很妙"**（HN 讨论）——对可观测性设计的认可
- **"终于不用每次跟 Claude 解释 .NET 的特殊用法了"**（Twitter/X）

### 差评共识&踩坑高发区

- **Skill 安装流程相对复杂**：需要先添加 marketplace 再安装 plugin，比 `@dotnet` 这类简单命令复杂
- **Dashboard 的评分标准不够透明**：用户不清楚"准确率"和"效率评分"是如何计算的
- **仅覆盖 .NET 单一生态**：与 addyosmani/agent-skills（41 种语言/框架全覆盖）形成对比，使用场景相对狭窄
- **75 个 open issues 不少**：主要集中在 plugin 兼容性和特定 .NET 版本的边界情况

### 争议焦点

- "Skill 到底该多细？"——dotnet/skills 有 15 个 plugin，每个都很专；而 addyosmani/agent-skills 每个 Skill 覆盖面更广。两种哲学各有利弊：细粒度更精准但管理成本高，粗粒度更方便但可能不够深

## ⚔️ 竞品对比

| 维度 | dotnet/skills | addyosmani/agent-skills | anthropics/skills |
|------|--------------|------------------------|-------------------|
| Stars | 4,274⭐ | 71,998⭐ | 未单独统计 |
| 维护方 | 微软 .NET 团队 | Addy Osmani（个人） | Anthropic（官方） |
| Plugin 数 | 15 | 41 语言/框架 | ~15 示例 |
| 覆盖范围 | .NET 全栈 | 通用（41种技术） | 通用示例 |
| 跨平台 | ✅ 5 个平台 | ✅ 多个 | ✅ Claude Code |
| 测试 | ✅ 有 | ❌ 无 | ❌ 无 |
| Dashboard | ✅ 有 | ❌ 无 | ❌ 无 |
| 质量门禁 | ✅ skill-validator | ❌ 无 | ❌ 无 |
| 适合人群 | .NET 开发者 | 全栈开发者 | Claude Code 用户 |

## 🎯 核心研判

### 项目优势（不可替代的价值点）

1. **企业级 Skill 仓库的唯一标杆**：在所有 Agent Skill 项目中，dotnet/skills 是唯一一个有自动化验证 + Dashboard + 分 Plugin 独立管理的——这对需要保证 AI 编码质量的团队来说是参考范本
2. **.NET 领域知识最全的 Skill 集**：覆盖从 ASP.NET Core 到 Blazor 到性能诊断的全栈，对 .NET 生态的覆盖深度无出其右
3. **"Skill 可观测性"的设计先驱**：Dashboard 追踪 Skill 的准确率和效率，这是 Agent Engineering 领域的领先实践

### 项目风险

1. **跨平台性提升空间大**：虽然支持 5 个平台，但安装流程在不同平台上差异较大
2. **仅限 .NET 生态**：非 .NET 开发者没有使用价值
3. **Dashboard 标准不透明**：评分标准没有公开文档，可能影响可信度

### 适用场景 & 不适用场景

✅ **适合**：.NET/C# 开发团队、需要 AI 辅助 MSBuild/EF Core/测试迁移等.DOT NET 特定场景
❌ **不适合**：非 .NET 开发者、全栈项目（需要结合其他 Skill 仓库）

### 趋势判断

📈 **上升期**：微软正在持续投入 AI 编码辅助领域，dotnet/skills 作为官方项目会获得持续资源。随着 Agent Skills 标准（`agentskills.io`）的推广，这种"官方 Plugin 市场"模式可能会被更多语言生态效仿。

## 📂 关键文件路径速查

| 文件 | 用途 |
|------|------|
| `plugins/dotnet/SKILL.md` | C# LSP + 基础开发技能 |
| `plugins/dotnet-aspnetcore/SKILL.md` | ASP.NET Core 开发技能 |
| `plugins/dotnet-test-migration/SKILL.md` | 测试框架迁移技能 |
| `plugins/dotnet-diag/SKILL.md` | 性能诊断技能 |
| `eng/skill-validator/` | Skill 质量自动验证器 |
| `eng/dashboard/` | Skill 效果评分 Dashboard |
| `AGENTS.md` | AI Agent 使用指引 |
| `docs/agentic-workflows.md` | Agent 工作流设计文档 |