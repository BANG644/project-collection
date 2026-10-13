# cathrynlavery/diagram-design 深度调研（重写升级）

> 定位一句话：一个 Agent Skill，把自然语言变成"一张自包含 HTML + SVG 文件"的社论级（editorial）图表，内置 45 种图型，无阴影、无 Mermaid 流水账。
> 抓取日期：2026-10-14（重写升级，原报告 2026-08-12）· 数据来源：gh API（README / SKILL.md / 目录树）· 星标约 53,852 · 许可 MIT · 形态 Agent Skill（Markdown + HTML 输出 + Python 脚本）· 技能版本 2.6

## 一、项目亮点（差异化）

- **Agent 原生，而非图表工具**：给 Claude Code / Codex / Copilot / Cursor / Gemini CLI / Cline / Windsurf / Amp / Factory Droid / Pi 等任意 Agent Skills 宿主用的技能包（`npx skills add` 一键装）。
- **自包含 HTML+SVG 输出**：成品是一个双击即开的 `.html`，内联 SVG、无外部依赖、可品牌化配色——比 Mermaid（需渲染器、样式不可控）更可移植、更"设计师友好"。
- **45 种图型 + 强类型参考体系**：架构图/时序图/状态机/ER/桑基图/Wardley 地图/甘特/象限/雷达/部署图/DP 安全矩阵…每种都有独立的 `references/type-*.md` 布局规范。
- **品牌门禁（style-guide gate）**：首次在新项目出图前强制确认风格指南是否定制，支持从网站 URL / 已装技能 / 本地设计系统 / 直接贴 token 四种方式 onboarding，保证"每个图都长在你的品牌里"。
- **双向互操作**：可导入 draw.io / Mermaid / Excalidraw，可导出 PNG / SVG——不把用户锁死。

## 二、核心架构

```
diagram-design/
├── skills/diagram-design/
│   ├── SKILL.md              # 技能入口（front matter + 哲学 + 工作流，常驻上下文）
│   ├── references/           # 45 个 type-*.md + 风格/导入/导出/图元规范（懒加载）
│   │   ├── type-architecture.md  type-sequence.md  type-er.md
│   │   ├── type-sankey.md  type-wardley.md  type-gantt.md  type-quadrant.md …
│   │   ├── style-guide.md  onboarding.md  profiles.md  output-spec.md
│   │   ├── import-drawio.md  import-mermaid.md  import-excalidraw.md
│   │   ├── export.md  export-registry.md  layout-budget.md
│   │   └── primitive-*.md  semantic-patterns.md  animation.md  doctor.md
│   ├── scripts/              # drawio/excalidraw/mermaid 提取 + svg 导出 + 自检
│   │   ├── drawio_extract.py  excalidraw_extract.py  mermaid_extract.py
│   │   ├── export_svg.py  self_check.py
│   └── assets/
├── .claude-plugin/ .codex-plugin/ .factory-plugin/ .cursor-plugin/  # 多宿主分发清单
├── commands/ prompts/ docs/ scripts/ assets/
├── skills-manifest.json  gemini-extension.json  plugin.json
└── CHANGELOG.md PRIVACY.md THIRD_PARTY_LICENSES.md
```

技能本体是 `SKILL.md`（front matter 标注 `name/description/license: MIT/metadata.version: "2.6"`）；配套 `references/` 把"知识"与"执行"解耦——SKILL.md 只讲哲学与流程，`type-*.md` 才讲每种图的精确布局。**核心思想：索引 + 懒加载引用 + 单一事实源样式表**，无论多少类型，Claude 每次只读本类型那一个文件，上下文极省。

## 三、应用场景与启发

- **AI 编码助手出图**：让 agent 在写架构文档/设计方案时直接产出可品牌化的图，替代潦草 Mermaid。
- **Skill 设计的可复用范式**：①"图型布局规范"与"语义模式"分离（`semantic-patterns.md` vs `type-*.md`）；②"首次门禁"机制保证一致性；③ 多宿主清单（`.claude-plugin`/`.codex-plugin`/`.factory-plugin`/`.cursor-plugin` + `npx skills`）统一分发。这套结构可直接套用到你自己的 WorkBuddy 图表类 skill。
- **"删减即质量"的设计哲学**：SKILL.md 明确"最高质量的动作通常是删除"，目标密度 4/10、超过 9 个节点多半该拆成两张图——对 AI 生成内容的"克制"很有启发。

## 四、源码深度解读（3 个核心模块）

**1）`skills/diagram-design/SKILL.md` —— 哲学与工作流**

```markdown
## 1. Philosophy
- Every node represents a distinct idea. Two nodes that always travel together are one node.
- Target density: 4/10. Above 9 nodes, it's probably two diagrams.
## 0. First-time setup — style guide gate
  解析项目 .diagram-design marker（profiles.md）；
  若仍是默认 token（paper #f5f5f5 / ink #2d3142 / accent #bf4520）→ 暂停询问用户
  分支：(a)网站URL (b)已装技能 (c)本地文件夹 (d)贴token (e)保持默认 (f)载入存档
```

**2）`references/` —— 45 个图型的布局即代码**

`type-architecture.md`/`type-sequence.md`/`type-er.md`/`type-sankey.md`/`type-wardley.md`/`type-dp-security-matrix.md`… 每种图一个文件，描述节点/连线/布局约束；另有 `primitives-core.md`、`primitive-sketchy.md`、`primitive-terminal.md`、`primitive-icons.md` 定义可复用图元，`layout-budget.md` 控制密度，`import-*.md`/`export*.md` 定义互操作契约。把"设计知识"沉淀为机器可读规范，是它可维护 45 种图的关键。

**3）`scripts/` —— 导入/导出与自检**

`drawio_extract.py` / `excalidraw_extract.py` / `mermaid_extract.py` 把外部图逆向抽取为自家 SVG 结构；`export_svg.py` 出 PNG/SVG；`self_check.py` 做产出自检（守住"无阴影、密度可控"的纪律）。脚本层让"互操作"不只是文档承诺，而是可执行能力。

## 五、社区口碑

- GitHub Trending 高位（约 53.8k stars，周增约 9.2k），`skills.sh` 安装量可观，登上 Trendshift；作者 Cathryn Lavery 有设计背景，成品审美在社区评价高。
- 多宿主分发成熟：Claude Code 插件市场 + Codex 市场 + `npx skills` 跨宿主 symlink 安装（`.claude-plugin`/`.codex-plugin`/`.factory-plugin`/`.cursor-plugin` 四套清单 + `skills-manifest.json` + `gemini-extension.json`）；PRIVACY.md 明确技能会发往网络的内容，合规透明度好。
- 反馈多集中在"终于不用看 Mermaid 丑图"，以及"品牌门禁很省心"。

## 六、竞品对比与核心研判

| 维度 | diagram-design | Mermaid | draw.io | Excalidraw | PlantUML |
|---|---|---|---|---|---|
| Agent 原生 | ✅ | 文本可写 | ❌ | 需插件 | 文本可写 |
| 品牌可定制 | ✅ 门禁 | ❌ | 手动 | 手动 | 主题有限 |
| 图型数 | 45 | 少 | 多(手绘) | 手绘 | 多 |
| 导入互操作 | ✅ drawio/mermaid/excalidraw | — | 原生 | 原生 | — |
| 输出可移植 | ✅ 单 HTML | 需渲染器 | 文件 | 文件 | 需渲染器 |

**核心研判**：它是"把图表当作 Agent 一等公民产物"的标杆级 skill。最值钱的是**知识解耦架构**（SKILL 讲流程、type-*.md 讲布局、style-gate 保一致）与**多宿主分发清单**——这两点可直接复用到任何 WorkBuddy 图表/文档类 skill。需注意：① 成品是 HTML+SVG，虽可导入 drawio 但原生不在 drawio 里编辑；② 图质量上限取决于 agent 执行 SKILL 的遵从度，复杂图仍需人校。相对 2026-08 初版，已从 27 图扩展到 45 图、新增三向导入脚本与四宿主清单，工程化程度继续领先。

## 七、关键文件路径速查

- `skills/diagram-design/SKILL.md` —— 技能入口（哲学/门禁/工作流）
- `skills/diagram-design/references/type-*.md` —— 45 种图的布局规范
- `skills/diagram-design/references/style-guide.md` `onboarding.md` `profiles.md` —— 品牌门禁与 onboarding
- `skills/diagram-design/scripts/*.py` —— drawio/excalidraw/mermaid 导入、SVG 导出、自检
- `.claude-plugin/` `.codex-plugin/` `.factory-plugin/` `.cursor-plugin/` `skills-manifest.json` `gemini-extension.json` —— 多宿主分发清单
- `PRIVACY.md` `THIRD_PARTY_LICENSES.md` —— 透明合规文档
