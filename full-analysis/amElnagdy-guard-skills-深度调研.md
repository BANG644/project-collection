# 🔍 深度调研报告：amElnagdy/guard-skills

> **调研日期**: 2026-06-18
> **Stars**: 467 ⭐ (2026-06-09 Trending)
> **语言**: Markdown (Agent Skills)
> **简介**: AI Agent 代码的质量关卡——捕获 AI 生成代码中的系统性失败模式

---

## 一、项目概述

guard-skills 是一组针对 AI 编码 Agent 的"防守型"技能包。它的核心理念很简单：让 Agent 干完活之后，再让另一个专门的质量关卡检查它做的事。这些关卡捕获的是 AI 生成代码的系统性失败模式——不是常规的 lint 或格式化问题，而是更深层的"AI 常见病"。

**最佳实践**: 先让 Agent 干活，然后在对 diff 提交/合并前调用对应的 guard 做审阅。

## 二、技能体系

```
skills/
├── clean-code-guard/        # 代码质量关卡 — 通用
│   ├── SKILL.md
│   └── references/
├── test-guard/              # 测试关卡
│   ├── SKILL.md
│   └── references/
├── docs-guard/              # 文档准确性关卡
│   ├── SKILL.md
│   └── references/
├── wp-guard/                # WordPress 关卡
│   ├── SKILL.md
│   └── references/
└── woo-guard/               # WooCommerce 关卡
    ├── SKILL.md
    └── references/
```

## 三、各技能详述

### 1. clean-code-guard 🧹（最核心）
**捕获**: 
- 全面的错误吞吃（catch-all "return ok"）
- 硬编码的"success"返回
- 幻觉 API 调用
- 过早抽象
- 注释污染（生硬的注释说明）
- 复制相似代码导致的 bug
- SOLID/DRY/KISS/YAGNI 违反

**AI 特殊层**: 引用了 AI 代码重复增长、包幻觉和 Agent 在测试失败时仍然声明成功的研究成果。

**使用感受**: Agent 重构时不静默改变行为 → 修改合约前主动询问 → 解释故意省略了什么 → 停止用 try/catch 包裹全部内容然后 return ok。

### 2. test-guard 🧪
**捕获**:
- Mock 滥用（mock 自身状态对象）
- 重复测试体
- 实现细节断言
- 什么也测不到的测试

**框架支持**: pytest、PHPUnit/Pest、Jest/Vitest、Go Tests、WordPress/WooCommerce Tests

**使用感受**: 一个包含 MagicMock() 状态、重复测试体和日志消息断言的测试文件 → 返回"禁止合并"并附带逐条修复建议。

### 3. docs-guard 📝
**核心思路**: 将文档视作一份声明列表，逐条验证代码库中是否存在。
**捕获**:
- 不存在的函数/符号
- 参数标签与实际签名不匹配
- 无法在干净机器上运行的示例
- 不可核实的性能声明

### 4. wp-guard & woo-guard 🔌
针对 WordPress 和 WooCommerce 生态的专项防护。

## 四、AI 层质量差异（为什么这个有用）

常规 lint 工具（ESLint、Pylint 等）可以捕获语法和代码风格问题，但捕获不了：
- Agent 写了 `try { ... } catch { return { success: true } }` 然后"声名"成功了
- Agent 引用了不存在的 API 函数
- Agent 重构时静默改变了行为
- Agent 创建了大量同质化的重复测试

guard-skills 的 AI 层专门针对这些模式，且设计为"反应式审阅"（post-hoc review）而非"主动式约束"（proactive constraint）。

## 五、安装方式

```bash
# 安装全部
npx skills add amElnagdy/guard-skills

# 或安装单个
npx skills add amElnagdy/guard-skills --skill clean-code-guard
npx skills add amElnagdy/guard-skills --skill test-guard
npx skills add amElnagdy/guard-skills --skill docs-guard
```

## 六、设计哲学

- **SKILL.md 保持小巧** → 快速加载；深层指导只在需要时加载
- **可审查性优先** → 全部是 Markdown + 轻量 YAML 元数据，无可执行脚本、无网络调用
- **渐进式揭示** → Agent 只在相关时加载特定框架的参考文档

## 七、同类项目对比

| 特性 | guard-skills | ESLint/Pylint | SonarQube |
|------|-------------|---------------|-----------|
| AI 代码特殊检测 | ✅ | ❌ | ❌ |
| 测试质量关卡 | ✅ | ❌ | ✅ |
| 文档真实性验证 | ✅ | ❌ | ❌ |
| 本地运行 | ✅ | ✅ | ❌ |
| Agent 原生集成 | ✅ | ❌ | ❌ |

## 八、核心结论

guard-skills 填补了一个重要的空白：传统 lint 工具和代码审查工具都不是为 AI 生成代码的特定失败模式设计的。当 Agent 写出"try/catch → return success" 或引用不存在的 API 时，常规工具不会发现。guard-skills 将这些模式显式编码为可审查的技能，是 Agent 工作流中"第二道防线"的实用补充。

**局限**: 目前覆盖的生态较少（仅 WP/WooCommerce 作为特定平台）；需要人工决定何时调用 guard；依赖 Skills CLI 生态。
