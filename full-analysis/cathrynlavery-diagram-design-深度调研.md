# cathrynlavery/diagram-design 深度调研报告

> 调研日期：2026-08-12 ｜ 星标：6,389 ⭐ ｜ 协议：MIT ｜ 语言：HTML(主)/Python ｜ 默认分支：main ｜ 创建：2026-04-16

## 一、项目定位

**Diagram Design 是一个为 Claude Code 打造的"编辑级图表"技能**——提供 27 种图表类型（架构图/流程图/时序图/象限图…），全部以**自包含 HTML + SVG** 输出（无阴影、无 Mermaid-slop），并能在 60 秒内读取你的网站、把品牌色与字体映射进每一张图，让 AI 生成的图"不像 AI 生成"。

## 二、项目亮点

1. **27 种编辑级图表 × 3 种变体**：每种图都有 minimal-light / minimal-dark / full-editorial 三套风格，开箱即浏览器打开，无构建、无 JS、无外链图片。
2. **品牌自 onboarding**：一句"onboard 到 https://yoursite.com"，技能抓取主页配色与字体栈，映射成语义 token（paper/ink/accent/link…），全图统一换肤。
3. **渐进式披露（Progressive Disclosure）架构**：`SKILL.md` 仅做索引，34 个 reference 文件按类型懒加载——无论多少类型，Claude 每次只读本类型那一个，上下文极省。
4. **WCAG AA 对比度自动校验**：写入 token 前自动验证 ink/paper 对比度，失败则提议修正值并解释原因，把"可访问性"内建进生成流程。
5. **反 AI 味设计系统**：单一强调色、1–2 个焦点元素、1px 发丝边框、无阴影、坐标/Gap 全部 4 的倍数——一套克制规范专治"AI 圆角盒子病"。

## 三、核心架构

```
diagram-design/
├── SKILL.md                    # 顶层索引：哲学 / 选型指南 / 检查清单（常驻上下文）
├── references/                 # 按需加载（仅在选定类型/原语时读取）
│   ├── style-guide.md          # 颜色+字体的单一事实源（semantic tokens）
│   ├── onboarding.md           # URL→tokens 流程规约
│   ├── type-architecture.md … type-quadrant.md …  # 27 个类型定义文件
│   ├── primitive-annotation.md # 斜体衬线编辑级旁注
│   ├── primitive-sketchy.md    # 手绘 SVG 滤镜变体
│   └── primitive-terminal.md   # 炭黑 CLI 窗口变体
├── assets/
│   ├── index.html              # 实时画廊（light/dark/full 三 tab 切换）
│   ├── template*.html          # 新图脚手架
│   └── example-<type>.html     # 3 变体 × 27 类型示例
├── scripts/
│   ├── lint-skin.py            # 皮肤 lint：坐标/Gap 4 倍数、对比度等静态校验
│   └── build-icons.py          # 55 个 IT/云图标 regen
├── commands/export-diagram.md # 导出 PNG/SVG 的斜杠命令
└── docs/screenshots/           # README 配图
```

**核心思想**：技能 = **索引 + 懒加载引用 + 单一事实源样式表**。SKILL.md 永远在上下文，但 34 个 reference 只在真正用到某类型时才被读取——这是"大模型技能该有的形态"，避免了把全部知识一次性塞进 prompt。

## 四、应用场景与启发

- **给 Claude/Codex 配"设计感"**：写文档、README、技术方案时，让 Agent 直接产出能放进slides/官网的编辑级图，而非 Mermaid 代码块。
- **品牌一致性自动化**：onboarding 把网站 Design Token 抽成图表语义色，多项目多风格零摩擦切换。
- **对"Agent 技能设计"的启发（高价值）**：本项目是**渐进式披露 + 单一事实源 + 静态 lint 守护**三原则的最佳范本。我们仓库中大量 Skills 类项目（anthropics/skills、google/skills、ComposioHQ/awesome-claude-skills）都在讲"技能怎么组织"，而 diagram-design 用 34 文件懒加载给出了**可扩展、上下文友好**的具体实现答案。
- **局限**：仅覆盖"图"这类可视化输出；品牌提取依赖首页可访问；sketchy/terminal 等变体更适合随笔而非技术文档。

## 五、源码深度解读

### 5.1 渐进式披露：`SKILL.md` 只做索引
```markdown
# SKILL.md（精简）
你是图表专家。用户要图时：
1. 用"选型指南"判断该用 27 种里的哪一种
2. 读取 references/type-<选定类型>.md 拿该类型的结构模板
3. 从 references/style-guide.md 取语义色板
4. 生成自包含 HTML，存盘
```
洞察：SKILL.md 不含任何图表细节，只含"去哪找细节"的指针。新增一种图 = 丢一个 `type-xxx.md` 并在选型指南加一行，**其余 33 个文件完全不变**。这是技能可扩展性的关键。

### 5.2 `style-guide.md`：语义 token 单一事实源
```markdown
| 检测自网站 | 成为 token |
| <body> 背景 | paper |
| 主文本色   | ink   |
| CTA/链接色 | accent |
| <h1> 字体  | title |
```
所有 27 图、注解原语、画廊都继承 `accent` 而非 `#eb6c36` 这种硬编码——换肤只需改一处。onboarding 流程在写入前还会跑 WCAG AA 对比度检查（`ink` over `paper`），失败则提议修正值。

### 5.3 `scripts/lint-skin.py`：皮肤静态守护
```bash
python3 scripts/lint-skin.py my-diagram.html          # 单文件
python3 scripts/lint-skin.py --all --baseline          # 全量门禁
```
校验坐标/宽度/Gap 是否 4 的倍数、对比度是否达标——**用脚本把"设计纪律"变成 CI 可卡门槛**，保证 34 文件长期风格一致。这是"AI 生成物质量门禁"的轻量范例。

## 六、社区口碑

- **地位**：6.3k+ ⭐、419 forks，2026-04 创建，是 Claude Code Skills 生态里"设计感图表"方向的代表项目，常被 Skills 合集引用。
- **评价基调**：正面为主——"终于有不丑的 AI 图了""onboarding 换肤很惊艳"。少数反馈是类型虽多但仍有覆盖空白、品牌提取对 SPA 站点偶有偏差。
- **工程信号**：MIT、含 `.claude-plugin` + `.codex-plugin` 双插件声明、THIRD_PARTY_LICENSES 完整（Tabler/Simple Icons）、lint 脚本守护——作者（Cathryn Lavery，BestSelf.co 创始人）以"产品化思维"做开源技能，质量意识强。

## 七、竞品对比 + 核心研判

| 维度 | diagram-design | Mermaid | Excalidraw | tldraw |
|---|---|---|---|---|
| 形态 | Claude Code 技能 | 文本 DSL | 手绘白板 | 白板 SaaS |
| 产出 | 自包含 HTML/SVG | SVG/图 | 手绘风 PNG | 矢量 |
| 品牌换肤 | ✅ 自动 onboarding | ❌ | 半手动 | 半手动 |
| AI 原生 | ✅ 懒加载技能 | 需手敲语法 | 需手画 | 需手画 |

**核心研判**：
- **优势**：把"编辑级图表 + 品牌一致性 + 渐进式技能架构"打包成可复用技能，是 Skills 工程化的高质量样本。
- **风险**：依赖 Claude Code/Codex 生态；非技术场景（手绘/白板）被 Excalidraw 更擅长；类型覆盖有上限。
- **趋势**：随 Agent Skills 成为标配，此类"垂直场景精品技能"会大量涌现，diagram-design 在"设计感"细分已占先机。
- **启发**：写 Agent 技能时，**SKILL.md 做索引 + references 懒加载 + 单一事实源配置 + lint 守护**这套组合，是避免技能"越写越胖、越用越慢"的正确范式，值得所有 Skills 项目借鉴。

## 八、关键文件速查

- `skills/diagram-design/SKILL.md` — 顶层索引（选型指南 + 检查清单）
- `skills/diagram-design/references/style-guide.md` — 颜色/字体语义 token 单一事实源
- `skills/diagram-design/references/onboarding.md` — URL→tokens 流程
- `skills/diagram-design/references/type-*.md` — 27 个图表类型定义（懒加载）
- `skills/diagram-design/assets/index.html` — 实时画廊（三变体 tab）
- `skills/diagram-design/scripts/lint-skin.py` — 皮肤静态校验（4 倍数/Gap/对比度）
- `commands/export-diagram.md` — 导出 PNG/SVG 斜杠命令
