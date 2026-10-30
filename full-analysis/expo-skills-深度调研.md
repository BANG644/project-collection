# expo/skills 深度调研

> 调研日期：2026-10-31 ｜ 数据来源：GitHub API（README / `.claude/skills/` 结构 / marketplace 配置）
> 许可证：**MIT** ｜ 形态：Expo 官方出品的 Agent Skills 集合（Shell 脚手架 + SKILL.md，覆盖 Expo/EAS/RN 全栈）

## 项目亮点（差异化）

- **官方出品、权威来源**：由 Expo 团队维护，Expo 文档/CLI/EAS CLI 是「真相源」，skills 只帮 Agent **正确应用**它们——不是社区二手知识。
- **双分发通道**：Claude Code / Codex 走**官方 plugin marketplace**（更新由市场托管）；Cursor/OpenCode/Copilot/Windsurf/Gemini/Cline 等走 **skills CLI**（`npx skills add expo/skills --skill '*'`），覆盖极广。
- **免费/付费边界显式标注**：skill 分「Framework（开源免费）」与「Services（EAS 付费）」两组，每个 services skill 开头带 costs/plan-limits 提示，避免 Agent 误用收费能力。
- **内建评测 skill**：`expo-skill-eval` 带 `design-rubric.md` / `runtime-matrix.md` 与 snapshot 脚本，能对所有 Expo skill 做视觉评分与平台矩阵校验——把「skill 质量」也工程化。
- **Agent 自主选 skill**：每个 skill 的 description 自带使用场景标签，Agent 据任务上下文自动路由，无需用户点名。

## 项目定位（一句话）

expo/skills 是 **Expo 官方为 AI 编码 Agent 打造的技能集合**——把 Expo SDK / React Native / EAS 的正确用法、项目结构、导航、动画、原生模块等封装成一个个可被 Agent 自动调用的 skill，让「用 Agent 写 Expo 应用」不再踩框架陷阱。

> **3.8k⭐**（2025-11 创建、2026-10-29 仍活跃，当日 Trending 上榜），MIT，Shell，244 fork / 102 open issues。

## 核心架构

- **入口 `expo-overview`**：任何 Expo/EAS 任务的「先加载」路由 skill；请求模糊或用户没点名具体工具时，由它分流到下方专精 skill。
- **Framework 组（开源免费）**：`expo-project-structure`（新项目 `src/`/`app/` 布局）、`expo-router`（文件路由/原生栈/modal/sheet/tab/header）、`expo-animation`（Reanimated+Gesture Handler 动效）、`expo-native-ui`（原生风样式/语义色/控件）、`expo-design-system`（token 主题+设计系统漂移审计）、`expo-ui`（`@expo/ui` 跨平台原生组件）、`expo-data-fetching`（React Query/SWR/离线/loader）、`expo-dom`（渐进用 web 代码）、`expo-web-to-native`（Next/Vite/CRA→原生迁移）、`expo-module`（Swift/Kotlin/TS 原生模块+config plugin+autolinking）、`expo-brownfield`（向现有原生 App 加 Expo）等。
- **Services 组（EAS 付费）**：EAS Build/Submit/Update/Workflows 等，开头带成本/额度提示。
- **分发配置**：`.claude-plugin/marketplace.json`、`.agents/plugins/marketplace.json`（plugin 市场）、`.claude/skills/expo-skill-eval/`（评测 skill，含 `references/design-rubric.md` + `scripts/{snapshot-ios,snapshot-android,snapshot-web,make-fixture,check-static}.sh` + `generate_viewer.py`）。
- **`.github/workflows/check.yml` + `eas/workflows/skill-eval-*.yml`**：CI 跑静态检查与评测基线。

## 源码深度解读（核心模块：expo-skill-eval 评测闭环）

**1. 每个 skill 自带「何时用」标签，Agent 自动路由（README 描述）**

```text
# 用户只需说：
"Build a native-feeling Expo Router screen with tabs, modals, and animations."
"Create an EAS workflow that builds previews on pull requests."
"Help me upgrade this app to the latest Expo SDK."
# Agent 据 skill description 自动选 expo-router / expo-animation / expo-... 
```
skill 的 `description` 字段承载使用场景标签，Agent 按任务上下文挑最合适的，用户无需点名——这是「skill 即可发现能力」的标准做法。

**2. 评测 skill 把质量工程化（`expo-skill-eval`）**

```bash
# .claude/skills/expo-skill-eval/scripts/
snapshot-ios.sh  snapshot-android.sh  snapshot-web.sh   # 三端截图
make-fixture.sh  make-workspace.sh                      # 造 fixture/工作区
check-static.sh                                        # 静态检查
generate_viewer.py                                     # 生成可视图
# references/design-rubric.md  + runtime-matrix.md      # 评分卡 + 平台矩阵
```
`expo-skill-eval` 用 design-rubric 对生成结果做视觉评分、`runtime-matrix` 跑 iOS/Android/Web 三端，CI（`eas/workflows/skill-eval-main-baseline.yml`）守基线。把「Agent 产出的 Expo 代码对不对、好不好看、三端通不通」变成可自动回归的闸门——**官方自己先给 skill 做 QA**，是 skills 生态里少见的成熟度。

## 应用场景与启发

- **「用 Agent 写 Expo/React Native 应用」**：装了 expo/skills 后，Agent 自动避开 Expo API 误用、项目结构混乱、导航/动画/原生模块陷阱，直接产出符合官方规范的代码。
- **「官方做 QA 的 skills 分发」范式**：plugin marketplace（更新托管）+ skills CLI（广覆盖）+ 内建 eval skill，是「如何大规模运维一套 agent skills」的范本——任何团队做内部 skills 仓库都该抄。
- **付费/免费边界显式化**：services skill 开头标 costs，避免 Agent 静默调用收费能力，值得所有含付费能力的 skill 借鉴。
- **对用户的启发**：用户在 WorkBuddy 维护 `paper-companion`/`ui-ux-super-optimizer` 等技能，expo 的「eval skill + marketplace + 场景标签路由」可直接套用到自家技能仓库的质量门控。

## 社区口碑

- **官方背书、信任度高**：**3.8k⭐**、MIT，Expo 团队官方出品，Trending 上榜，被 Agent 生态视为「Expo 知识的一手来源」；安装矩阵清晰（plugin + CLI），社区反馈以「省去查文档、少踩坑」为主。
- **主要局限**：仅服务 Expo/RN 技术栈，非该栈无收益；services 组依赖 EAS 付费，eval 主要覆盖官方样例；复杂跨栈问题仍需人判断。
- **主观满意度数据不可用**：精确 NPS 无第三方统计；上述基于 README 自述与 Trending 表现。

## 竞品对比

| 维度 | expo/skills | 社区 Expo 提示词 | 通用 React Native 文档 | 手查 Expo Docs |
|------|------------|------------------|------------------------|----------------|
| 权威性 | 官方一手 | 二手 | 官方（非 Agent 向） | 官方 |
| Agent 可调用 | 是（自动路由） | 需拼装 | 否 | 否 |
| 质量保障 | 内建 eval skill | 无 | 无 | 无 |
| 更新 | marketplace 托管 | 手动 | 手动 | 手动 |

## 核心研判

- **价值清晰**：在「Agent 写 Expo 应用」这一明确场景里，官方一手 + 自动路由 + 内建评测的组合几乎没有替代；其「skills 仓库的运维成熟度」（marketplace + CLI + eval）是任何内部 skills 平台的范本。
- **边界明确**：**仅限 Expo/RN 栈**，非该栈无收益；services 依赖 EAS 付费。
- **采用建议**：做 Expo 开发时必装；更值得的是抄其「eval skill + marketplace 分发 + 场景标签路由 + 付费显式标注」的 skills 运维范式到自家技能仓库。

## 关键文件路径速查

- `expo-overview`（SKILL）— 任何 Expo/EAS 任务的入口路由
- `expo-router` · `expo-animation` · `expo-native-ui` · `expo-design-system` · `expo-data-fetching` · `expo-module` · `expo-web-to-native` · `expo-brownfield` … — Framework 组技能
- `.claude-plugin/marketplace.json` · `.agents/plugins/marketplace.json` — plugin 市场分发
- `.claude/skills/expo-skill-eval/` — 评测 skill（`references/design-rubric.md` + `runtime-matrix.md` + `scripts/`）
- `.github/workflows/check.yml` · `eas/workflows/skill-eval-*.yml` — CI 静态检查与评测基线
- `README.md` — 安装矩阵（plugin / skills CLI / 更新）
