# 📊 9arm-skills 深度调研报告

> **仓库**: [thananon/9arm-skills](https://github.com/thananon/9arm-skills)  
> **Stars**: 2,714 | **Forks**: 375 | **语言**: Shell | **License**: 无  
> **创建时间**: 2026-05-20 | **最后推送**: 2026-05-26  
> **批次**: batch_03 (#43) | **调研日期**: 2026-06-17

---

## 一、项目定位

9arm-skills 是一个面向 Claude Code 的**个人 Agent Skill 合集**仓库。与 PaperSpine 等结构化 skill suite 不同，这个仓库记录的是一个工程师自己的日常 Agent 工作流——调试纪律、代码审查、任务委派、管理沟通等。

它不是产品级工具，而是一个**高度个人化的工作哲学体现**，但因其丰富的 skill 设计模式对 Claude Code 社区有很好的参考价值。

---

## 二、架构设计

### 仓库结构

```
9arm-skills/
├── skills/
│   ├── engineering/           # 日常编码工作流 skill
│   │   ├── debug-mantra/     # 四 mantra 调试纪律
│   │   ├── post-mortem/      # 故障事后分析记录
│   │   ├── scrutinize/       # 端到端代码审查
│   │   └── qwen-agent/       # Qwen 子 Agent 任务委派
│   ├── productivity/         # 日常非编码工作流工具
│   │   ├── management-talk/  # 工程师→管理层的沟通转换
│   │   └── qwenchance/       # 长任务上下文预算管理
│   ├── misc/                 # 保留但不常用
│   ├── personal/             # 绑定个人环境的 skill（不推广）
│   ├── in-progress/          # 草稿中 skill
│   └── deprecated/           # 废弃 skill
├── scripts/
│   ├── link-skills.sh        # 符号链接所有可发布 skill 到 ~/.claude/skills/
│   └── list-skills.sh        # 列出仓库中所有 SKILL.md
├── CLAUDE.md                 # 顶层指令，加载 agent 上下文
└── README.md
```

### 核心设计模式

1. **按成熟度分组**：engineering（已发布）→ in-progress（草稿）→ deprecated（废弃），体现 skill 生命周期管理
2. **YAML frontmatter**：每个 `SKILL.md` 包含 `name` 和 `description` 元数据，便于自动发现
3. **单一 CLI 安装**：`npx skills add thananon/9arm-skills` 即可安装全部 skill

---

## 三、Skill 详解

### Engineering 组

#### 1. debug-mantra — 四 mantra 调试纪律
- **核心理念**：调试不是碰运气，而是可重复的思维模式
- **四步骰咒**：复现 → 追踪失败路径 → 证伪假设 → 交叉核对每一条面包屑
- **行为约束**：session 开始时逐字背诵，然后按顺序应用后才开始修复
- **适用**：任何需要系统化调试的场景，防止"随手改试试"式调试

#### 2. post-mortem — 故障事后分析
- **核心理念**：每个修复过的 Bug 都值得成为知识资产
- **产出结构**：根因分析 → 机制描述 → 修复方案 → 验证结果 → 漏网原因
- **质量门槛**：没有可靠复现、已知原因和已验证的修复，拒绝动笔
- **适用**：团队协作中需要记录工程事故事实的场景

#### 3. scrutinize — 端到端代码审查
- **核心理念**：以局外人视角审查计划、PR 或代码变更
- **审查维度**：意图（是否有更简单的方式？）→ 实际代码路径追踪 → 变更效果验证
- **输出要求**：简洁、可操作、附带理由
- **适用**：任何需要第二双眼睛的代码变更

#### 4. qwen-agent — Qwen 子 Agent 委派
- **核心理念**：把重复性、界定清晰的小任务交给便宜的 Qwen 模型
- **命令**：`claude-9arm` 命令启动 Qwen 子 agent
- **适用任务**：批量重命名、格式化、样板代码、grep 式摘要、脚手架、构建/测试报告
- **价值**：节省 Claude Code 的昂贵 token，加速日常杂务

### Productivity 组

#### 5. management-talk — 工程师→管理层沟通转换
- **核心理念**：工程师不懂管理层的语言，需要翻译层
- **转换维度**：渠道适配（JIRA / Slack / 异步站会 / 邮件 / 会议发言要点）
- **适用**：需要向非技术团队汇报进度或问题的场景

#### 6. qwenchance — 长任务上下文预算管理
- **核心理念**：Claude Code 长任务容易偏离轨道，需要看门狗
- **职责**：打断循环、约束内部推理、监控上下文预算、在窗口填满前触发干净的交接
- **适用**：持续数小时的大型编码任务

---

## 四、技术亮点

### 1. Skill 生命周期管理
通过 `engineering → in-progress → deprecated` 分组，让 skill 仓库随人和项目自然演进，而不会变成垃圾堆。

### 2. 低成本的"个人 skill 生态"
整套仓库仅 1.3KB Shell 代码，Skill 都以 Markdown 指令为主，几乎零代码维护成本。

### 3. 子 Agent 委派模式（qwen-agent）
开创性地使用便宜模型（Qwen）处理非核心任务，保留 Claude 注意力给高价值工作——这是 Agent 协作领域的实用模式。

### 4. "预算看门狗"模式（qwenchance）
识别并解决长任务 Agent 中最常见的问题：token 窗口耗尽前的任务完成度和质量下降。

---

## 五、关键优势与不足

### 优势
- 🧠 **工作哲学而非工具**：每个 skill 都是可复用的思维方式，不绑定特定工具
- ⚡ **轻量级**：纯 Markdown 指令，零依赖、零构建
- 🏗️ **可扩展的 skill 生态**：可以按生命周期自然管理
- 📦 **一键安装**：`npx skills add` 即可完整引入

### 不足
- 👤 **高度个人化**：绑定作者的工作习惯，其他人可能需要修改
- 📝 **文档有待完善**：CLAUDE.md 仅 810 字节，缺少详细上下文说明
- 🔒 **无 License**：社区复用存在法律不确定性
- 🐚 **仅 Shell 实现**：缺少更成熟的安装/卸载/更新机制
