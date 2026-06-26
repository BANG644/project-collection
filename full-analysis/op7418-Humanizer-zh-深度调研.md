# op7418/Humanizer-zh 深度调研

> **调研日期**: 2026-06-19 | **Stars**: ★ Trending | **语言**: Markdown/SKILL | **许可**: 参照原项目

## 项目定位

**Humanizer-zh 是一个用于去除中文文本中 AI 生成痕迹的 Claude Code 技能（Skill）**，帮助用户将 AI 生成的内容改写得更自然、更像人类书写的文本。

本项目是 [blader/humanizer](https://github.com/blader/humanizer) 的汉化版本，同时参考了 [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) 的实用工具部分。核心理论基础来自维基百科的 [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) 指南。

## 核心架构

### 技术原理

Humanizer-zh 不是一个大模型或复杂系统，而是一个 **Claude Code 技能定义文件（SKILL.md）**，通过规则提示词引导 AI 识别并修复 AI 写作痕迹。

### 可识别的 24 种 AI 写作痕迹（四大类）

| 类别 | 具体模式 | 示例 |
|------|---------|------|
| **空洞概括类** | 过度强调意义/遗产/趋势、模糊归因、泛泛而谈 | "作为……的证明"、"在不断发展中" |
| **AI 词汇类** | 高频 AI 词、同义词循环、填充短语 | 此外、至关重要、深入探讨、无缝 |
| **结构痕迹类** | 三段式法则、否定式排比、提纲式展望、系动词回避 | "不仅仅……而是……" |
| **格式痕迹类** | 破折号过度、粗体滥用、内联标题、标题大写、表情符号、弯引号 | — 连续使用、**粗体**泛滥 |

### 中文高频 AI 词汇黑名单

- 此外、至关重要、深入探讨、强调
- 持久的、增强、培养、获得
- 突出、相互作用、复杂/复杂性
- 格局（抽象名词）、关键性的、展示
- 织锦（抽象名词）、证明、强调
- 宝贵的、充满活力的

## 安装与使用

```bash
# 方式一：通过 npx 安装（推荐）
npx skills add https://github.com/op7418/Humanizer-zh.git

# 方式二：手动安装到 Claude Code skills 目录
git clone https://github.com/op7418/Humanizer-zh.git ~/.claude/skills/humanizer-zh
```

使用方式：
```
/humanizer-zh 请帮我人性化以下文本：
[粘贴你的 AI 生成文本]
```

### 实际效果对比

**改写前（AI 味道）：**
> 坐落在风景如画的杭州市中心，这家咖啡馆拥有丰富的文化底蕴和令人叹为观止的装饰。

**改写后（人性化）：**
> 这家咖啡馆在杭州市中心开了三年，以手冲咖啡和老建筑改造的空间出名。

## 社区与口碑

- 来自同一作者 [op7418](https://github.com/op7418) 的 **guizang-social-card-skill** 也已被星标
- 中文 AI 写作社区需求强烈，AI 文本"人性化"是高频刚需
- 基于维基百科权威指南，理论扎实
- LinuxDO 社区支持

## 竞品对比

| 特性 | Humanizer-zh | blader/humanizer | hardikpandya/stop-slop | GPTZero |
|------|-------------|------------------|----------------------|---------|
| 语言 | 中文 | 英文 | 英文 | 多语言 |
| 形式 | Claude Code Skill | Claude Code Skill | 规则清单 | 在线检测器 |
| 模式数 | 24 种 | 24 种 | 规则集 | 检测模型 |
| 定位 | 改写去 AI 味 | 改写去 AI 味 | 质量检查 | AI 内容检测 |
| 开源 | ✅ | ✅ | ✅ | ❌ |
| 中文适配 | ✅ 深度 | ❌ | ❌ | 有限 |

## 核心研判

**价值**: ⭐⭐⭐⭐ (高)
- 精准满足中文 AI 写作社区的核心刚需
- 基于维基百科权威指南，理论扎实
- 安装和使用极其简单，零门槛
- 24 种 AI 痕迹识别覆盖面广

**适用场景**:
- 编辑和审阅 AI 生成的中文内容
- 提升文章的人性化程度
- 学习识别 AI 写作的常见模式
- 自媒体/博客作者优化 AI 辅助写作

**核心观点**: 工具的目的不是为了"欺骗"AI 检测器，而是真正提升写作质量。最好的"去 AI 化"方法是让文字有真实的人类思考和声音。

## 关键文件路径

- `SKILL.md` — 技能定义文件（中文版，核心）
- `README.md` — 说明文档
- `SKILL.md` 中定义了 24 种 AI 模式的检测和修复规则

---

*报告由 AI 自动生成，基于 GitHub README、项目文档和社区反馈*
