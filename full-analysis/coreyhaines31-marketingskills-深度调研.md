# 🔬 coreyhaines31/marketingskills - 全方位深度调研

## 📌 一句话定位

AI 编码 Agent（Claude Code / Codex / Cursor 等）的营销领域技能集——45+ 结构化的营销 Skill，覆盖 CRO 转化率优化、文案、SEO、数据分析、增长工程等全链路营销场景，被业界视为 Agent Skill 在垂直专业领域的标杆案例。

## ⭐ 项目亮点

- **垂直领域的 Skill 标杆**：不是泛技能合集，而是聚焦营销领域的最完整 Skill 集——从 A/B 测试到 ASO、从冷邮件到社区营销，每个 Skill 附带 evals 和 references
- **严格的质量体系**：每个 Skill 有 PR 模板、验证 CI、versioned 发布、evals 评估文件，体现生产级质量控制
- **持续迭代能力**：2.6.0+ 版本，引入 marketing-loops（53 个循环）、marketing-council（顾问委员会）等创新模式
- **跨 Agent 兼容**：通过 AGENTS.md 和 CLAUDE.md 双重适配，同时支持 Claude Code、Codex、Cursor 等平台
- **社区治理成熟**：完整的 PR 流程（new-skill/skill-update/documentation 三类模板），志愿者友好

## 🏗️ 项目架构全景

### Skill 目录结构

```
├── AGENTS.md              # 跨 Agent 兼容声明
├── CLAUDE.md              # Claude Code 原生配置
├── VERSIONS.md            # 版本历史
├── skills/
│   ├── ab-testing/        # A/B 测试
│   │   ├── SKILL.md
│   │   ├── evals/         # 质量评估
│   │   └── references/    # 参考知识
│   ├── ad-creative/       # 广告创意
│   ├── ads/               # 广告投放
│   ├── ai-seo/            # AI SEO
│   ├── analytics/         # 数据分析
│   ├── aso/               # App Store 优化
│   ├── churn-prevention/  # 流失预防
│   ├── co-marketing/      # 联合营销
│   ├── cold-email/        # 冷邮件
│   ├── community-marketing/ # 社区营销
│   ├── competitor-profiling/ # 竞品画像
│   ├── content-strategy/  # 内容策略
│   ├── copy-editing/      # 文案编辑
│   └── ... (45+ 营销技能)
├── .github/
│   ├── workflows/
│   │   ├── sync-skills.yml      # 跨平台同步
│   │   └── validate-skill.yml   # 技能验证 CI
│   └── ISSUE_TEMPLATE/
│       └── skill-request.yml    # 技能请求模板
```

### 每个 Skill 的三层结构

每个 Skill 目录遵循 `SKILL.md` + `evals/` + `references/` 三层架构：

1. **SKILL.md** — Agent 可执行指令（核心，机器可读）
2. **evals/evals.json** — 自我评估用例，用于验证 Skill 正确性
3. **references/** — 人类撰写的参考知识（平台规范、模板库、最佳实践）

这种架构允许 Skill 在 Agent 执行时可以"自我验证"——运行 eval 确认指令有效，是一种 Agent 时代的 TDD 实践。

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 对应 Skill | 典型输出 |
|------|-----------|---------|
| 新站 SEO 诊断 | `ai-seo` | 完整的 SEO 审计报告 + 优化优先级列表 |
| Landing Page A/B 测试 | `ab-testing` | 测试方案 + 样本量计算 + 统计显著性判断 |
| 产品发布文案 | `copy-editing` | 7 轮精编（七轮扫描法） |
| 竞品分析报告 | `competitor-profiling` | 结构化竞争对手画像 + 差距分析 |
| 用户留存优化 | `churn-prevention` | 取消流程审计 + Dunning 策略 |
| App Store 上架 | `aso` | Apple/Google Play 双平台完整优化检查清单 |

### 可借鉴的 Skill 架构思路

这份仓库的 Skill 结构（SKILL.md + evals + references 三层分离）是**Agent Skill 的"最佳实践模板"**，任何想构建领域专业技能集的开发者都可以参考：

- **执行层 vs 知识层分离**：SKILL.md 保持纯执行逻辑，references/存放知识库——便于更新任一层不影响另一层
- **嵌入 evals**：每个 Skill 自带自动化评估，让 Agent 可以"自我验证"执行质量
- **跨平台声明**：通过 AGENTS.md 声明兼容性，让同一个 Skill 可以在多个 Agent 平台上无痛迁移

### 营销自动化的新范式

markertingskills 展示了一种新工作方式：不是用模板生成营销内容，而是**教会 Agent 营销方法论**。每个 Skill 不是问你"要什么文案"，而是执行一套完整的营销分析流程——这比传统的 ChatGPT 对话式营销要深入一个量级。

## 🧠 核心源码解读（克制代码量）

### SKILL.md 结构设计（以 ai-seo 为例）

每个 SKILL.md 的核心流程：

```markdown
# AI SEO Optimization Skill

You are an AI SEO expert...
Your task is to audit and optimize content for AI search engines.

## Workflow
1. Analyze content for AI search intent matching
2. Check OKF (Originality, Knowledge, Factuality) scoring
3. Optimize heading structure for AI extraction
4. Implement platform-specific ranking factors
5. Generate structured data markup
```

这种"角色定义 + 分步工作流 + 检查项"的结构，是 Agent Skill 设计的事实标准——不要求 Agent 从头推理，而是用结构化模板引导 Agent 行为。

### 循环机制（marketing-loops）

marketing-loops Skill 引入了一个超越静态 SKILL.md 的创新——**周期性执行循环**。仓库 ISSUE #379 揭示了详细设计：

- 53 个循环（Daily 10 / Weekly 23 / Monthly 16 / Quarterly 4）
- 覆盖 AARRR 每个阶段
- 每个循环对应一个营销领域 Skill
- 通过 GitHub Actions 或 Agent 内置调度触发

这实际上把营销从"反应式任务"变成了"策略式运营"——Agent 定期执行分析循环，而不是等待被触发。

## 🌐 全网口碑画像

### 好评共识

- **"最实用的 Skill 仓库"** —— 社区公认在垂直领域（营销）的完成度最高
- **"Agent Skill 的设计参考"** —— 被多个 Agent 技能开发教程引为最佳实践
- **"从模仿到创新"** —— 早期借鉴 uber-agent/caveman 的风格，后期形成自己的一套方法论（marketing-loops、marketing-council）
- **快速响应**：Issues 通常 24h 内回复，owner actively engaged

### 差评共识 & 争议

- **门槛偏高**：部分用户反馈 Skill 的 workflow 设计过于复杂，入门需要时间
- **过度模板化**：少数 Skill 的内容结构高度相似，存在模板化痕迹
- **多语言支持不足**：目前仅英文构建，非英文市场的营销场景覆盖有限
- **外部依赖**：部分 Skill 引用了外部工具（如特定分析平台），通用性受限

### 典型实战案例

一位独立开发者用 marketingskills 的 `cold-email` + `competitor-profiling` 完成了 B2B SaaS 的冷启动营销计划（来源：idao.fun 博客评测）。结果显示：Agent 的营销方案比 Freelance Marketer 的报价低 90%+，且生成速度是秒级。

## ⚔️ 竞品对比

| 维度 | marketingskills | phuryn/pm-skills | addyosmani/agent-skills |
|------|----------------|-----------------|----------------------|
| 领域 | 营销（垂直深耕） | 产品管理（垂直） | Engineering（生产级） |
| Skill 数量 | 45+ | 100+ | 30+ |
| 质量体系 | evals + CI + PR templates | 基础 CI | CI + CLAUDE.md 绑定 |
| 跨平台 | Claude Code + Codex + Cursor | Claude Code 为主 | Claude Code 为主 |
| 独特创新 | marketing-loops、营销委员会 | PM 全流程覆盖 | 工程质检 |
| Stars | 36,374 | 17,514 | 64 |
| 社区活跃度 | 极高（45 开放 Issue） | 中 | 低 |

## 🎯 核心研判

### 项目优势

- **营销垂直领域最完整的 Agent Skill 库**——没有竞品在这方面的完成度能比
- **创新的 Skill 设计范式**——SKILL.md 三层结构 + evals 自我验证 + 循环机制
- **高速增长**——2026-01 开始，短短几个月从零到 36K⭐，呈现爆发式增长
- **可复制性强**——Skill 架构和治理模式可以作为垂直领域 Skill 库的模板

### 项目风险

- **OpenAI/Anthropic 可能改变 Skill 规范**——Agent Skill 标准仍在演进中，当前格式可能被平台升级破坏兼容性
- **营销自动化价值争议**——AI 生成的营销方案质量是否真正等于人肉方案，目前缺乏系统性的对比评测
- **过度膨胀风险**——当 Skill 增加到 100+、200+ 时，维护和质量控制将成为巨大挑战

### 适用场景

✅ 创业团队需要低成本营销方案时
✅ 技术创始人需要"AI 营销搭档"而非"人肉 Marketer"时
✅ 研究 Agent Skill 最佳实践的开发者
✅ 构建垂直领域 Agent Skill 库的模板参考

❌ 需要高端品牌战略制定时（Agent 不擅长战略定性）
❌ 需要深度行业洞察时（Agent 缺乏行业经验积累）
❌ 非英语市场的本地化营销

### 趋势判断

**高速增长期** ⬆️ —— 36K⭐ 仍处于快速增长阶段，随着 Agent 生态成熟和更多营销从业者接触 AI 编码 Agent，这个仓库的关注度有望继续攀升。

## 📂 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `AGENTS.md` | 跨 Agent 兼容性声明（必读） |
| `CLAUDE.md` | Claude Code 原生适配配置 |
| `VERSIONS.md` | 版本历史和变更日志 |
| `skills/ab-testing/SKILL.md` | A/B 测试技能参考实现 |
| `skills/ai-seo/SKILL.md` | AI SEO 优化技能 |
| `skills/cold-email/references/` | 冷邮件参考知识库（模板+序列+基准数据）|
| `.github/workflows/validate-skill.yml` | Skill 质量验证 CI |
| `.github/ISSUE_TEMPLATE/skill-request.yml` | 技能请求模板 |
