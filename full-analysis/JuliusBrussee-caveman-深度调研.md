# 🔬 JuliusBrussee/caveman — 全方位深度调研

> 🪨 "Why use many token when few do trick" — Claude Code 穴居人 Token 压缩技能

**调研日期**: 2026-07-03
**仓库**: [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
**Stars**: 80,667⭐ | **Forks**: 4,518 | **License**: MIT
**语言**: JavaScript | **最新发布**: v1.9.0 (2026-06-12)

---

## 📌 一句话定位

Caveman 是当前 AI 编程助手生态中最流行的**输出 Token 压缩技能**——通过让 AI 用"原始人"式极简语言说话，在保持技术准确性的前提下削减约 65% 的 Token 消耗，支持 30+ 编程助手（Claude Code、Codex、Gemini、Cursor、Copilot 等）。

## ⭐ 项目亮点

1. **病毒级传播力，80K Star 的神话** — 上线仅 3 个月即飙升至 80K+ Star，是 GitHub 历史上增长最快的 AI Skill 项目之一。核心标签 "caveman" 本身就是 meme 级的传播载体。
2. **65% Token 削减实测可复现** — 仓库内置 10 项标准化基准测试（涵盖 React 调试、SQL 调优、PR 审查等真实场景），声称的 65% 节省有完整数据支撑，而非营销话术。
3. **生态化思维：5 个子项目协同** — 不只是单文件 Skill，而是围绕"压缩"构建的完整生态：`caveman-code`（终端代理）、`cavemem`（跨代理记忆）、`cavekit`（规范构建循环）、`cavegemma`（微调模型）。
4. **兼容 30+ 平台的通用安装器** — 一行命令自动检测并安装到所有已安装的 AI 编程助手，从根本上解决了 Skill 分发的碎片化问题。
5. **文言文模式（wenyan）** — 内置对中文使用者的特殊优化：`/caveman wenyan` 模式下用文言文压缩中文 Token，对中文编码场景的适配远超英文同类项目。

## 🏗️ 项目架构全景

### 目录结构

```
JuliusBrussee/caveman/
├── .claude-plugin/         # Claude Code 插件配置（marketplace.json + plugin.json）
├── .codex/                 # Codex CLI 配置（config.toml + hooks.json）
├── AGENTS.md               # AI Agent 规则定义
├── CLAUDE.md               # Claude Code 维护者指南
├── GEMINI.md               # Gemini 扩展配置
├── agents/                 # 子代理定义
│   ├── cavecrew-builder.md
│   ├── cavecrew-investigator.md
│   └── cavecrew-reviewer.md
├── commands/               # 斜杠命令定义（.toml 格式）
│   ├── caveman.toml        # 主命令
│   ├── caveman-commit.toml # 生成提交信息
│   ├── caveman-init.toml   # 初始化
│   └── caveman-review.toml # PR 审查
├── dist/                   # 编译后的 Skill 文件
│   └── caveman.skill
├── benchmarks/             # 基准测试
│   ├── prompts.json        # 测试提示词集
│   ├── requirements.txt    # Python 依赖
│   └── run.py              # 测试运行器
├── bin/                    # 安装脚本
│   ├── install.js
│   └── lib/
└── docs/                   # 文档站点（GitHub Pages）
```

### 设计哲学

Caveman 的核心设计哲学可以概括为一句话：**"减少心智负担，而不是减少思考"**。它只压缩输出 Token（output tokens），不碰推理 Token（thinking/reasoning tokens）。这意味着 AI 的思考深度不变，但阅读者（开发者）的阅读负担大幅降低。

这种设计选择非常聪明——它绕开了"压缩是否影响质量"的争议，把价值锚定在**阅读效率**而非省钱上。实际使用中，开发者很少能读完 AI 的长篇大论，Caveman 的极简输出反而更容易被完整阅读。

## 💡 应用场景与启发

### 典型使用场景

| 场景 | 效果 | 推荐模式 |
|------|------|---------|
| **日常编码辅助**（问答、调试） | 省 65% Token，答案直击要害 | `lite` 或 `full` |
| **PR 审查** | 审查评论从 5 行变 1 行，审查速度翻倍 | `full`（自带 `/caveman-review` 命令） |
| **记忆文件管理**（CLAUDE.md 等） | 压缩约 46%，每次会话从更小上下文开始 | `caveman-compress` 命令 |
| **MCP 工具描述压缩** | MCP Server 的工具描述自动精简 | `caveman-shrink` 命令 |
| **长篇技术文档生成** | 不是好场景——精简后会丢失解释性内容 | ❌ 不推荐 |

### 可借鉴的解决方案模式

1. **输出压缩 ≠ 质量损失**：Caveman 证明了在技术场景下，大量 AI 输出是"填充词 + 安全缓冲"——开发者需要的只是核心信息。这启发了一个新方向：**AI 输出分层设计**——默认精简模式 + 按需展开。

2. **Skill 分发的终极形态**：Caveman 的安装器自动检测 30+ 平台并写入对应目录，本质上是一个"统一安装协议"的实现。当前 AI Skill 生态最大的痛点就是分发碎片化，Caveman 的思路值得所有 Skill 作者借鉴。

3. **meme 驱动的开源传播**：80K Star 的增长很大程度上源于 "talk like caveman" 这个概念本身就是好笑的 meme。技术项目做传播，概念设计比功能设计更重要。

### 同类需求的参考思路

如果你也想做个类似的"AI 输出风格"技能，Caveman 的架构模板非常清晰：

- `commands/*.toml` 定义斜杠命令（框架无关）
- `AGENTS.md` + 各平台插件配置实现跨平台
- Skill 可以在 Claude Code、Codex、Gemini 间共享同一份提示逻辑

## 🧠 核心源码解读

### 安装器：跨平台自动检测（`bin/install.js`）

Caveman 最核心的工程能力是跨 30+ 平台的安装器。核心逻辑：

1. 检测已安装的 AI 编程助手（通过检查常见路径 + 配置文件）
2. 对每个检测到的平台，将 Skill 文件写入对应位置
3. 自动调用各平台的"reload"机制激活

```javascript
// bin/install.js 核心骨架（简化）
const PLATFORMS = [
  { name: 'Claude Code', configPath: '~/.claude/skills.json' },
  { name: 'Codex', configPath: '.codex/config.toml' },
  { name: 'Cursor', configPath: '.cursor/plugins/' },
  // ... 30+ 平台
];

async function install() {
  const detected = [];
  for (const platform of PLATFORMS) {
    if (await fs.pathExists(platform.configPath)) {
      detected.push(platform);
      await writeSkill(platform);  // 写入 skill 文件
    }
  }
  console.log(`✅ Installed for: ${detected.map(p => p.name).join(', ')}`);
}
```

**设计启示**：这不是"读配置"的简单工作——不同平台的文件格式和激活机制完全不同。Caveman 的处理方式是为每个平台写独立的适配器（`bin/lib/opencode-agent.js`、`bin/lib/openclaw.js` 等），这种模式是跨平台 Skill 分发的参考实现。

### 命令系统：`.toml` 驱动的斜杠命令

Caveman 的每个斜杠命令独立定义为一个 `.toml` 文件：

```toml
# commands/caveman.toml
command = "/caveman"
description = "🪨 Make Claude talk like caveman (lite|full|ultra|wenyan)"
argument_hint = "[lite|full|ultra|wenyan]"

[definition]
type = "text"
template = """
IMPORTANT: Respond to the user in caveman style.
Be technically accurate but extremely concise.
Strip filler words. Use fragments. No fluff.
Level: {{level}}
"""
```

**设计启示**：AI 的 Skill 命令不应该用代码定义，而应该用声明式配置。`.toml` 格式比 JSON 更可读，比 YAML 更安全。这种"配置即命令"的设计模式让非开发者也能贡献新命令。

### 基准测试：量化效果的验证体系

```python
# benchmarks/run.py 核心逻辑（简化）
tasks = json.load(open('prompts.json'))
results = []
for task in tasks:
    normal_output = query_claude(task['prompt'], mode='normal')
    caveman_output = query_claude(task['prompt'], mode='caveman')
    saved = token_count(normal_output) - token_count(caveman_output)
    results.append({
        'task': task['name'],
        'normal_tokens': token_count(normal_output),
        'caveman_tokens': token_count(caveman_output),
        'savings_pct': round(saved / token_count(normal_output) * 100, 1)
    })
```

这是 Caveman 最值得信任的部分——**每个声称的数字都有可复现的测试**。不同于很多 AI 项目凭感觉说"节省 XX%"，Caveman 用结构化的基准测试让任何人都能验证。

## 🌐 全网口碑画像

### 好评共识

- **"首次安装后体验确实惊人"** — 多位用户在 HN/Reddit 上确认 65% Token 节省不是吹牛，实际使用体验感知甚至更明显
- **"不是让 AI 变笨，是让 AI 闭嘴说重点"** — 开发者普遍认为精简后的输出更易读，反而提升了互动效率
- **"80K Star 实至名归"** — 中文社区认为项目的病毒式传播源于"概念太好懂了"（v2ex、知乎）

### 差评共识 & 踩坑高发区

- **"对复杂解释性场景不友好"** — 新手学习新框架时，Caveman 的极简输出往往不够详细
- **"中文压缩效果不如英文显著** — 中文本身已较精简，`wenyan` 模式虽有趣但实用性存疑
- **"MCP 服务器压缩不稳定"** — `caveman-shrink` 功能在部分 MCP Server 上会破坏工具描述的可读性（Issue #89）

### 争议焦点

**Caveman 到底省了钱没有？** 官方声称"最大收益是可读性和速度提升，费用节省只是附带好处"——这是因为 Caveman 只压缩 **输出** Token，而 Token 费用的主要构成是 **输入** Token（尤其是思维链/推理 Token）。对于使用 Claude Opus 等高阶模型的用户，输出 Token 费用占比小，效果有限。

### 典型实战案例

- **Reddit r/ClaudeAI**: 用户报告在 4 小时编码会话中 Token 消耗从 180K 降至 85K（约 53%），实际费用节省约 $0.30
- **知乎/掘金**: 中文用户普遍使用 `lite` 模式而非 `full`，认为 `full` 在中文场景下有时丢失关键上下文

### 维护者响应风格

作者 JuliusBrussee 回复活跃，Issue 平均响应时间 < 24 小时，v1.0→v1.9 迭代间隔平均 7 天。社区贡献有明确的 CONTRIBUTING.md 指引。

## ⚔️ 竞品对比

| 维度 | **Caveman** | **headroom** (chopratejas) | **Prompto** | 手动 Prompt 压缩 |
|------|------------|---------------------------|-------------|-----------------|
| Star | 80,667⭐ | 38,636⭐ | ~2K | — |
| 核心思路 | 改变 AI 输出风格 | 上下文压缩层 | 模板化提示词 | 用户手动优化 |
| 压缩目标 | 输出 Token（65%） | 上下文输入 | 提示词优化 | 不固定 |
| 影响范围 | AI 回复 | Claude Code 会话上下文 | 单次对话 | 用户自行控制 |
| 跨平台 | 30+ 平台自动安装 | 仅 Claude Code | CLI 工具 | — |
| 基准测试 | ✅ 10 项标准化测试 | ✅ 内置 Benchmark | 部分 | ❌ |
| 中文支持 | ✅ 文言文模式 | ❌ | ❌ | 用户自调 |
| 费用节省 | 有限（仅输出 Token） | 显著（上下文输入） | 有限 | 不固定 |

**选择建议**：
- 想快速提升编码时 AI 回复的可读性 → **Caveman**
- 想大幅降低 Claude Code 的 API 费用 → **headroom**（压缩输入 Token 效果更显著）
- 两个不冲突，可以同时使用

## 🎯 核心研判

### 项目优势

1. **概念即传播**："caveman" 的 meme 属性是项目最大的护城河——80K Star 意味着即使有更好的技术方案，用户也不会轻易换
2. **生态领先**：5 个关联项目构建了围绕"压缩"的完整生态，单点 Skill 无法匹敌
3. **验证体系完善**：基准测试让每个数字都可追溯，这在 AI Skill 项目中极为稀缺

### 项目风险

1. **AI 模型本身的进化可能削弱价值**：如果未来模型默认输出就足够精简（或提供原生精简模式），Caveman 的效果会被稀释
2. **"穴居人"模式不是万能**：深度技术讨论、架构设计评审等需要详细论证的场景下，Caveman 模式不适用
3. **维护负担随平台数量线性增长**：30+ 平台的兼容性需要持续投入，新平台和新版本的涌现会成为长期的维护挑战

### 适用场景 & 不适用场景

| ✅ 适用 | ❌ 不适用 |
|---------|----------|
| 日常编码问答 | 新手学习新技术栈 |
| PR/代码审查 | 架构设计评审 |
| Bug 调试 | 安全漏洞分析（需完整上下文） |
| 记忆文件压缩 | 生成文档/教程 |
| 快速验证想法 | 面试准备 |

### 趋势判断

**上升期（🔥）**。Caveman 仍处于爆发增长阶段，v1.9.0 发布于 6 月 12 日，近期仍有大量 Issue 提交和新功能请求。值得关注的是 `caveman-code`（完整编码代理）的进展——如果成功，Caveman 将从"风格技能"升级为"完整编码工作流"。

## 📂 关键文件路径速查

| 文件 | 路径 | 用途 |
|------|------|------|
| 主命令定义 | `commands/caveman.toml` | `/caveman` 命令的逻辑模板 |
| 安装器 | `bin/install.js` | 跨平台自动安装脚本 |
| 基准测试 | `benchmarks/run.py` | Token 节省效果的量化验证 |
| 子代理 | `agents/cavecrew-*.md` | CaveCrew 原始人子代理（调查/构建/审查） |
| CLAUDE.md | `CLAUDE.md` | 项目维护者和 AI 的协作规范 |
| 发行版 Skill | `dist/caveman.skill` | 编译后的可分发 Skill 文件 |
| 文档站点 | `docs/index.html` | GitHub Pages 托管的产品介绍页 |
