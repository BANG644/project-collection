# 🔧 revfactory/harness — Agent 团队编排元技能框架

> **调研时间**: 2026-06-24 | **Stars**: 7,412⭐ | **Today +123⭐**
> **语言**: HTML | **许可**: MIT
> **仓库**: https://github.com/revfactory/harness

---

## 项目全景

Harness 是一个**元技能（meta-skill）框架**，它能根据任务需求自动设计领域专精的 Agent 团队、定义专业 Agent 角色、并生成它们所需的技能文件。可以理解为"Agent 团队的编译器"——输入任务描述，输出完整的 Agent 协作团队配置。

当前 7.4K+ stars，虽然体量不大，但其"元技能"理念在 Claude Code 生态中属于创新定位。

## 核心架构

```
harness/
├── harness.md          # 元技能主入口（被 Claude Code 加载的入口文件）
├── templates/          # Agent 角色模板
│   ├── architect.md    # 架构师 Agent
│   ├── developer.md    # 开发者 Agent
│   ├── reviewer.md     # 审查者 Agent
│   └── tester.md       # 测试者 Agent
├── workflows/          # 工作流定义
│   └── standard.md     # 标准开发工作流
├── generators/         # 技能生成器
│   └── skill-gen.md    # 自动生成技能文件
└── examples/           # 使用案例
```

## 核心创新点

### 元技能（Meta-Skill）概念
- 传统 Agent Skills 专注于解决特定领域问题
- Harness 的技能是"设计技能"的技能——它定义如何生成其他 Agent 的技能
- 类似于编程中的元编程（metaprogramming）概念

### 运行流程
1. **需求分析** — 输入任务描述，Harness 解析领域特征
2. **团队设计** — 自动确定需要哪些 Agent 角色
3. **技能生成** — 为每个 Agent 生成专用技能文件
4. **团队编排** — 定义 Agent 间的协作流程和通信方式
5. **执行监督** — 监控多 Agent 协作执行过程

### Agent 角色模板
- **Architect**: 整体架构设计，技术选型，模块划分
- **Developer**: 编码实现，遵循架构设计
- **Reviewer**: 代码审查，质量标准把控
- **Tester**: 测试策略，用例生成，自动化测试

## 社区口碑

- **理念创新**：多 Agent 编排的元层级抽象受到关注
- **学习曲线**：需要先理解元技能概念才能充分发挥
- **实用性**：适合复杂项目需要多个专业 Agent 协作的场景
- **生态兼容**：与 Claude Code、Cursor、Codex 等主流 AI 编程工具兼容

## 竞品对比

| 特性 | Harness | Swift (OpenAI) | AutoGPT |
|------|---------|----------------|---------|
| 元技能/元编程 | ✅ 核心 | ❌ | ❌ |
| Agent 团队设计 | ✅ 自动 | ❌ 固定 | 手动 |
| 技能自动生成 | ✅ | ❌ | ❌ |
| 多 Agent 编排 | ✅ | ✅ | 部分 |
| 模板化角色 | ✅ | ❌ | ❌ |

## 核心研判

**优势**：
- 创新性的元技能设计理念，填补了多 Agent 编排的空白
- 自动生成技能文件的能力降低了团队构建成本
- 模板化 Agent 角色设计，易于扩展
- 与主流 AI 编程工具兼容

**局限**：
- 项目较新，文档和案例尚不丰富
- 元技能概念的抽象层级较高，普通开发者理解门槛不低
- 实际生产环境中的稳定性未得到充分验证
- 缺乏性能基准和大型案例验证

**定位**: 面向进阶开发者的多 Agent 编排框架，是 Agent 团队自动化的早期探索者

## 关键文件速查

| 文件路径 | 功能 |
|----------|------|
| `harness.md` | 元技能主入口（核心文件） |
| `templates/architect.md` | 架构师 Agent 模板 |
| `templates/developer.md` | 开发者 Agent 模板 |
| `templates/reviewer.md` | 审查者 Agent 模板 |
| `templates/tester.md` | 测试者 Agent 模板 |
| `generators/skill-gen.md` | 技能自动生成器 |
| `workflows/standard.md` | 标准开发工作流 |
