# Garden Skills 深度调研

> 仓库：`ConardLi/garden-skills` ｜ MIT ｜ 主语言 CSS ｜ 2026-08-26 抓取（last push 2026-07-12）
> 星标：10,862 ⭐（当日 Trending +136）｜ Fork：1,385 ｜ 作者：ConardLi（"code秘密花园"，前端 KOL）
> 安装：`npx skills add ConardLi/garden-skills` ｜ 兼容 Claude Code/Cursor/Codex/Gemini CLI/OpenCode

## 一、项目定位（一句话）

Garden Skills 是 ConardLi 出品的**生产级 Agent Skills 合集**——目前 5 个精心打磨的技能（web 设计 / 网页视频 / GPT 图像 / 本地知识库检索 / 美丽文章），每个都达到"设计引擎级"深度，面向 Claude Code、Cursor、Codex 等编码 agent。

## 二、项目亮点（差异化）

1. **5 个高质量 skill，每个都是"引擎"而非"提示词"**：`web-design-engineer`（6 设计学派 + 25 风格配方）、`web-video-presentation`（23 主题、可录屏级 Vite+React 演示）、`gpt-image-2`（18 类 / 79 模板、三运行时模式）、`kb-retriever`（本地知识库渐进检索）、`beautiful-article`（10 文章类型 + 11 主题档案）。
2. **多安装路径且可复现**：`npx skills` CLI / Claude Code plugin marketplace（4 个 plugin pack）/ GitHub Releases 的 **SHA-256 校验 immutable .zip** / git submodule / 手动拷贝——CI 与气隙环境可锁版本。
3. **硬协作检查点（checkpoint 必须停）**：关键流程在文章类型、主题、版式、配图、封面等处设置**逐项确认**，绝不静默默认——把"人类控制权"写进 skill 契约，防 AI 跑偏。
4. **设计深度远超通用 AI UI**：`web-design-engineer` 含 anti-cliché blocklist、Design Read 五维评估、25 个锚定风格配方（Linear/Aesop/Pentagram/Bloomberg/Stripe Press/Mid-Century…）；`beautiful-article` 用 reacticle 组件协议（语义组件 + 主题约束 Raw 层）。
5. **中文生态友好**：作者 B站/公众号/小红书/抖音全平台运营，文档中英日三语，对中文 AI 工程用户上手成本低。

## 三、核心架构（克制呈现）

标准 skill 结构（每个技能一个目录）：
```
skills/<name>/
  ├── SKILL.md        ← YAML frontmatter(description=触发契约) + 工作流
  ├── README.md       ← 人读文档
  ├── references/     ← agent 按需加载的扩展文档
  ├── scripts/        ← 确定性可执行助手
  └── assets/         ← 模板/字体/图标
```
- `.claude-plugin/marketplace.json` 声明 4 个 plugin pack（`presentation-skills` / `web-design-skills` / `knowledge-base-skills` / `image-generation-skills`），每个打包若干 skill。
- `scripts/release/` 发布流水线：`pack-skill.mjs`（打 zip）、`update-readme.mjs`（每次发版自动改写 README 内 Download 链接与校验和）、`list-skills.mjs`（校验 manifest）。
- `dist/prompts/claude-design-system-prompt.md` 保留 Anthropic Claude Design 原始 system prompt 作参考，体现"站在官方肩膀上"。

## 四、应用场景与启发（重点）

- **个人/小团队做"生产级 skill"的范本**：5 个 skill 展示了"一个 skill 如何做到设计引擎级"——不是堆提示词，而是**结构化的 references + scripts + 主题档案 + 检查点**。
- **checkpoint 协作模式可泛化**：`beautiful-article` 的 `source→plan→双确认→build→终审→repair` 小型 harness + 三处硬 checkpoint，可复用于任何"agent 生成内容"的场景（报告、PPT、代码），在"自动化"与"人类控制"间取得平衡。
- **可复现安装范式**：SHA-256 校验的 immutable release zip + 多安装通道，是"把 skill 当软件分发"的正确做法，值得 CI/生产环境借鉴。

## 五、源码深度解读（2 个核心模块）

**① `skills/beautiful-article/SKILL.md` — Phase harness（节选）**
```markdown
---
name: beautiful-article
description: "把用户提供的素材（URL/PDF/DOCX/Markdown/截图/粘贴）编辑、设计成
  一篇美丽的、可离线打开的单文件 HTML 网页文章...只生成文章，不生成后台/表单/dashboard。"
---
## 工作流总览
Phase 0  Intake            判断是否进入 + 初步文章类型
Phase 1  Source → Markdown 提取 source.md + extraction-notes
Phase 2  Editorial Planning plan.md（Brief/Outline/Theme/Assets）
Phase 3  Plan Checkpoint   ★必须停：逐项确认 5 件事（类型/主题/版式/配图/封面）
Phase 4  First Spread      首屏+第一节+代表视觉，SubAgent review
         ★Checkpoint 2 必须停：确认验收结论/开发模式
```
这段体现了"边界判断 + 双确认 checkpoint + SubAgent 审查"的严谨 harness 设计。

**② SKILL.md frontmatter — agent 触发契约**
```yaml
description: "把用户提供的素材...做成美丽的单文件 HTML 网页文章...
  触发场景：'render this as a beautiful web article / 把这篇做成网页文章'..."
```
frontmatter 的 `description` 是 agent 是否激活该 skill 的唯一契约——写清"做什么 + 不做什么（边界）"，避免误触发。

## 六、全网口碑

- **10.8k star、1.4k fork**，MIT；中文前端社区（ConardLi "code秘密花园"）号召力强，B站/公众号持续产出配套教程。
- 各 skill 有真实案例库（gpt-image-2 160+ 公开案例、web-design 25 风格画廊、beautiful-article 11 主题），可信度高。
- 局限：规模小（仅 5 个 skill）、更新偏慢（last push 2026-07-12）、单人维护，长期扩展与可持续性存疑。

## 七、竞品对比 + 核心研判

| 维度 | Garden Skills | anthropics/skills | nextlevelbuilder/ui-ux-pro-max-skill | ComposioHQ/awesome-claude-skills |
|---|---|---|---|---|
| 技能数 | 5（精） | 官方参考集 | 1（综合 UI/UX） | 1000+（清单） |
| 设计深度 | 引擎级（25 配方） | 中 | 高（84 风格） | 索引 |
| 中文生态 | ✅ 强 | 英文 | 英文 | 英文 |
| 安装可复现 | ✅ SHA-256 zip | ✅ | ✅ | npx |
| 维护者 | 单人 | Anthropic | 单人 | 社区 |

**核心研判**
- **优势**：质量高、设计/前端深度突出、中文友好、安装可复现、checkpoint 协作模式典范；在"垂直精品 skill 合集"细分里有清晰生存空间。
- **风险**：① 单人维护、规模仅 5 个、更新慢，扩展与可持续性风险；② 与官方 `anthropics/skills` 及大型 awesome 清单在"发现"层存在重叠；③ 偏前端/设计垂类，通用性有限。
- **趋势**：Agent Skills 生态将呈"官方参考 + 大型索引 + 垂直精品"三层并存；Garden Skills 代表"小而美、深而精"的垂类路线，对中文用户尤其友好。
- **启发**：做 skill 时不要贪多，把一个垂类做到"引擎级 + 检查点 + 可复现分发"，比铺一堆浅提示词更有长期价值。
