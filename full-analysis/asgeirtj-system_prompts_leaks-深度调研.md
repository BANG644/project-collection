# 🔬 asgeirtj/system_prompts_leaks - 全方位深度调研

## 📌 一句话定位

全球最大（49,819⭐）的 AI 系统提示词泄露仓库——定期提取并公开 Anthropic/OpenAI/Google/xAI 等 10+ 厂商 50+ 主流 AI 产品的底层 System Prompt，曾获《华盛顿邮报》报道，是 AI 透明度和 Prompt Engineering 领域的事实参照标准。

## ⭐ 项目亮点

- **透明度标杆**：被《华盛顿邮报》引用的 AI 黑盒揭秘项目（2026-05-11报道），远高于是"提示词收集"范畴，已经成为 AI 行业透明度运动的标志性仓库
- **极广的覆盖度**：Anthropic（Fable 5/Opus 4.8）、OpenAI（ChatGPT 5.5/GPT 5.5/Codex）、Google（Gemini 3.5 Flash/3.1 Pro/Antigravity）、xAI（Grok）、Cursor、Copilot、VS Code、Perplexity 等全面覆盖
- **刷新即热点**：每次大模型升级后数小时内就出现新版 prompt 泄露，自动吸引媒体关注（头条、知乎、QQ 新闻等主流媒体覆盖）
- **作为 Prompt Engineering 学习素材**：顶级 AI 公司实战打磨的 System Prompt 设计范式被完整暴露，是业界最佳的"反向学习"材料
- **CC0 许可证**：完全公有领域，无任何使用限制

## 🏗️ 项目架构全景

### 技术本质

这不是传统意义上的代码项目（主要语言 JavaScript 仅用于少量辅助脚本），而是一个**结构化文档仓库**。核心资产是按厂商分类的 Markdown 文件集合。

### 目录结构

```
├── Anthropic/
│   ├── Claude Code/              # Claude Code 系统提示词
│   │   ├── bundled-skills/       # 内置技能文件完整 dump
│   │   │   ├── artifact-design.md
│   │   │   ├── dataviz/SKILL.md  # 数据可视化技能
│   │   │   ├── deep-research/SKILL.md
│   │   │   └── ... (20+ 内置技能)
│   │   ├── claude-code-2.1.172-*.md  # 多版本 prompt
│   │   └── grep-tool.md, list-files.md, glob-tool.md, ...
│   ├── Claude Design/            # Claude Design 设计系统 prompt
│   ├── Claude Fable 5/           # 最新版 Claude Fable
│   └── Official/                 # 官方历史版本
├── OpenAI/
│   ├── ChatGPT 5.5/             # 含 thinking 层
│   ├── GPT 5.5/                 
│   ├── Codex/                   # Codex 编码助手
│   └── ...
├── Google/
│   ├── Gemini 3.5 Flash/
│   ├── Antigravity/
│   └── Gemini Code Assist/
├── xAI/Grok/                    # Grok 系统提示词
├── Cursor/                      # Cursor IDE
├── Microsoft/
│   ├── Copilot/                 # GitHub Copilot
│   └── VS Code/
├── Perplexity/
└── github/workflows/            # 流量徽章自动化
```

### 核心模式：精准的版本标注

每个 prompt 文件的命名都包含具体版本号，如 `claude-code-2.1.172-opus-4.8.md`，这使得读者可以精确追溯到该 prompt 对应的模型版本。仓库还会注明泄露来源和验证方式。

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 说明 |
|------|------|
| **Prompt Engineering 教学** | 直接学习头部公司如何定义角色、边界、输出格式 |
| **竞品分析** | 了解不同 AI 产品的"母语提示词"设计哲学差异 |
| **安全教育** | 理解系统提示词的安全性设计——哪些防护手段被攻破了 |
| **自主 AI 产品设计** | 参考行业标杆的 System Prompt 结构和优先级 |

### AI 透明度的范式启发

该项目引发的思考远超技术层面：当商业 AI 把核心行为规则藏在黑盒中，社区通过"泄露"实现了事实上的透明度。这对 AI 安全治理有深远影响——公司需要重新思考：是默认开放 prompt 获取信任，还是继续封闭但面对持续泄露？

### 对比不同公司的 Prompt 设计风格

- **Anthropic**：极度详细的角色设定 + 长篇幅的伦理约束 + 详细的工具使用规范
- **OpenAI**：相对简洁，更注重输出格式规范和安全边界
- **Google**：偏向指令式，较少的角色扮演元素
- **xAI/Grok**：短而精炼，核心强调"技术准确性和原创性"

## 🧠 核心源码解读（克制代码量）

### 核心数据层

项目的核心资产在 `Anthropic/` 下的 Claude Code bundled-skills 目录。以 `init.md` 为例，它揭示了 Claude Code 初始化时的完整心智模型：

```markdown
# Identity and Purpose
You are Claude, created by Anthropic.
You are a highly capable software engineering assistant...
```

而 `deferred-tools.md` 揭示了 Claude Code 的延迟工具调用机制，这是一个 README 未说明的关键设计：

```markdown
You have access to a set of tools you can use to answer questions.
You are responsible for deciding when to use each tool based on the user's request.
The `globbing` tool searches for files matching patterns.
The `grep` tool searches file contents for patterns.
```

### 自动化工作流

`.github/workflows/traffic-to-badge.yml` 每天自动采集仓库流量统计并生成徽章，这是该项目唯一的技术性创新——用自动化维持项目的可见度和信誉。

## 🌐 全网口碑画像

### 好评共识

- **"AI 透明度的里程碑"** ——《华盛顿邮报》直接引用了该仓库的数据作为报道素材
- **"反转 AI 黑盒"**—— 知乎/头条大量文章称赞项目让普通人看到了"AI 背后的规则"
- **"Prompt Engineering 的宝藏"**—— 开发者社区认为它是学习提示词工程的最佳反面教材
- **"更新极快"**—— 每次大模型升级后，新版 prompt 几乎同步就出现了

### 差评共识 & 争议

- **伦理争议**：部分评论认为持续"泄露"可能触发 AI 公司修改防护策略，反而导致更严密的封锁
- **"窃取"还是"研究"**：有分歧认为这不属于严格意义上的"泄露"（因为 prompt 在模型交互中已经暴露给用户），而是合法提取
- **质量参差**：部分 prompt 是早期版本或不完整版本，容易误导读者

### 媒体关注

被《华盛顿邮报》、腾讯新闻、今日头条、CSDN 等主流媒体广泛报道，在中文互联网上引发了关于 AI 透明度的大讨论。

## ⚔️ 竞品对比

| 维度 | system_prompts_leaks | 各厂商官方文档 | Awesome Prompts |
|------|---------------------|--------------|----------------|
| 核心内容 | 真实泄露的 System Prompt | 官方公开的 API 文档 | 用户自创的 Prompt 示例 |
| 真实度 | 极高（实测可用） | 官方认证 | 来源不明 |
| 覆盖范围 | 50+ 核心 AI 产品 | 仅自家产品 | 泛 LLM 用户 |
| 更新速度 | 天级（大版本更新后数小时） | 月/季度 | 不定 |
| 法律风险 | ⚠️ 灰色地带 | 无 | 无 |
| 学习价值 | 极高（教你大厂怎么"想"） | 中（教你大厂希望你怎么做） | 低（用户经验分享） |

## 🎯 核心研判

### 项目优势

- **信息优势**：在 AI 透明度领域几乎是唯一的高质量、实时更新的信息来源
- **媒体影响力**：已经被主流媒体背书，形成了"泄露→报道→更多关注"的正反馈循环
- **学习价值**：对于任何想深入了解 Prompt Engineering 的人来说，这是不可替代的素材库

### 项目风险

- **法律灰色地带**：虽然 AI 公司目前未采取法律行动，但随时可能面临 DMCA 下架或法律挑战
- **信息可靠度**：无法验证每个 prompt 100% 真实——部分可能是社区模拟或旧版
- **AI 公司可能加码防护**：持续的泄露可能导致 AI 公司采用更强的 prompt 混淆/加密措施

### 适用场景

✅ 需要了解头部 AI 产品行为规则时
✅ 研究 Prompt Engineering 最佳实践时
✅ 设计自主 AI 产品的 System Prompt 时
✅ AI 安全研究和透明度报告编制

❌ 商业产品直接复制（可能含版权或保密内容）
❌ 作为学术引用（来源不明确）
❌ 评估当前活跃产品行为（某些 prompt 可能已过时）

### 趋势判断

**高速增长期** ⬆️ —— 随着 AI 监管议题升温，该项目的社会价值和关注度将继续上升。但最大的风险来自于法律层面的不确定性。

## 📂 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `Anthropic/Claude Code/bundled-skills/` | Claude Code 内置 20+ 技能的完整 prompt dump |
| `Anthropic/Claude Code/claude-code-2.1.172-opus-4.8.md` | Claude Code Opus 4.8 系统提示词 |
| `Anthropic/Claude Design/` | Claude Design 设计系统的提示词 |
| `OpenAI/ChatGPT 5.5/` | ChatGPT 5.5 含 thinking 层的完整 prompt |
| `OpenAI/Codex/` | OpenAI Codex 编程助手的系统提示词 |
| `Google/Antigravity/` | Google Antigravity 系统提示词 |
| `xAI/Grok/` | xAI Grok 系统提示词 |
| `Cursor/` | Cursor IDE 的编码 Agent prompt |
| `.github/workflows/traffic-to-badge.yml` | 流量统计自动化（唯一技术性代码） |
