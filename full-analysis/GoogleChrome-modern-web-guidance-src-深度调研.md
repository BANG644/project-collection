# GoogleChrome/modern-web-guidance-src 深度调研

> 调研日期：2026-11-13 ｜ Stars：2,629 ｜ License：Apache-2.0 ｜ 语言：TypeScript
> 定位：Chrome / Edge / Firefox / MDN **四家联合维护**的"现代 Web 平台最佳实践"技能源仓库——把 Web 专家策展的指南，通过 CLI 注入到你的编码 Agent 上下文，纠正模型"偏爱旧写法"的惯性。

---

## 一、项目定位

一个**为编码 Agent 而生**的 Web 平台最佳实践知识库：不是给人读的文档，而是 token 高效的"技能"，直接 `install` 进 Claude / Codex 等 Agent 的技能目录。源仓库（`-src`）含生成、校准、评测代码，分发给 Agent 的是构建产物。

---

## 二、项目亮点

1. **浏览器厂商联合背书**：Google Chrome、Microsoft Edge、Mozilla Firefox、MDN 共同 stewardship——权威性远高于个人或社区清单。
2. **Agent-native 形态**：指南是 token 高效的"技能"，直接注入 Agent 技能目录，而非人读长文档。
3. **RAG 式精准检索**：`search` / `retrieve` 按用例定位指南，`legacy-scan` 扫描代码库里的过时模式并给出现代化建议。
4. **Eval 驱动修剪**：README 明确"我们跑 eval 来剪掉模型已经知道的冗余内容"——内容随模型能力演进而动态瘦身。
5. **覆盖广且前沿**：从 View Transitions、容器查询、subgrid、oklch 到 Popover、Anchor Positioning、Scrollbar-Color，覆盖近年 Web 平台新特性。

---

## 三、核心架构

pnpm monorepo：

- `src/cli/` — CLI 实现（`modern-web.ts`：install / search / retrieve / legacy-scan）
- `src/rag/` — 检索层（`retrieve.ts`、`guides.ts`、`logger.ts`，把指南索引化供 Agent 取用）
- `src/core/` — 路径、配置（`.mwgrc`）、特性门控、配色等原语
- `features/` — 单特性指南（`popover.md`、`anchor-positioning.md`、`scrollbar-color.md`…）
- `guides/` — 主题指南（`accessibility`、`css`、`forms`、`html`、`js`、`performance`、`security`、`ui-components`…）
- `src/{analyzing,authoring,build,ci,grading,harness,dashboard}/` — 作者工作流与评测

"源码 + 评测 + 分发"三分法是高质量技能库的典型结构：源仓库负责策展与校准，构建产物才进 Agent。

---

## 四、应用场景与启发

- **给编码 Agent 装"Web 平台常识"**：模型训练数据充斥旧写法，本项目用专家策展内容把 Agent 拉回现代 API——任何"AI 写前端"场景都可借鉴。
- **"Eval 驱动的技能库"范式**：不堆量、用评测删冗余，避免上下文污染；对自建 Agent 技能库是直接方法论。
- **厂商中立协作样板**：四家竞争关系的浏览器厂商联合维护一份指南，说明"Web 标准最佳实践"是共同利益。
- **局限**：聚焦 Web 前端；非 Web 领域（后端 / ML / DevOps）不适用；内容随标准演进需持续维护。

---

## 五、源码深度解读

**① CLI 入口与 RAG 检索** `src/cli/modern-web.ts`

```ts
import { retrieveUseCase, FeatureGateError } from "../rag/retrieve.ts";
import { USE_CASES } from "../rag/guides.ts";
// parseArgs: --choose / --skill-version / help / version
// 子命令: install(交互向导) / search(语义检索) / retrieve(按 ID 取指南) / legacy-scan(扫过时模式)
```

CLI 把"检索用例 → 注入技能"串成一条命令链，`USE_CASES` 是检索索引入口，`FeatureGateError` 处理 origin-trials / volatile 特性的门控。

**② 单特性指南示例** `features/popover.md`（节选）

```md
# Popover API
## Fallbacks
The Popover API is mostly **progressive enhancement**...
**MANDATORY:** Feature detect by checking for the `popover` property on `HTMLElement.prototype`,
and load the polyfill **only** when native support is missing.
```

指南用"MANDATORY / 建议"等强指令语气 + 特性探测代码，确保 Agent 产出"渐进增强、不盲目 polyfill"的现代写法。

**③ 特性门控与配置** `src/core/mwgrc.ts` / `src/harness/lib/secret-guard.ts`

`writeMwgrc` 写入本地配置，`loadAllowedEnvFile` 只加载白名单环境变量（secret-guard），体现"把指南分发给 Agent 时也要守住安全边界"的工程素养。

---

## 六、社区口碑

- Stars **2,629**，License Apache-2.0，由四大浏览器 / 标准组织 stewardship，可信度极高。
- 提供公开 Eval Dashboard（googlechrome.github.io/modern-web-guidance-src），用数据而非口号证明指南有效。
- 口碑正向：被社区视为"官方给 Agent 的 Web 最佳实践"，但尚新、采用面待观察；与 `addyosmani/agent-skills` 互补（前者通用工程、本项聚焦 Web 平台）。

---

## 七、竞品对比 + 核心研判

| 维度 | modern-web-guidance | addyosmani/agent-skills | web.dev / MDN 文档 |
|------|---------------------|-------------------------|------------------|
| 维护方 | Chrome/Edge/FF/MDN | 个人(Addy Osmani) | 官方文档站点 |
| 形态 | Agent 技能(可注入) | Agent 技能 | 人读文档 |
| 检索 | ✅ RAG search/retrieve | ⚠️ 目录浏览 | ❌ |
| Eval 修剪 | ✅ | ❌ 明确 | — |

**研判**：本项目的护城河是**四厂联合的权威背书 + Eval 驱动的精简内容 + Agent-native 分发**。它不是"又一个前端清单"，而是把 Web 标准组织的共识编译成"模型能直接消费的技能"。结论：做前端 / Agent 产品的团队应直接采用；做其他领域技能库的可借鉴其"源码 + 评测 + 分发"三分法与 eval 修剪思路。

---

## 八、关键文件路径速查

- 源仓库入口：`README.md`（声明为 modern-web-guidance 的源）
- CLI：`bin/gd.ts`、`src/cli/modern-web.ts`、`src/cli/install-*.ts`、`src/cli/skill-version.ts`
- 检索层：`src/rag/{retrieve,guides,logger}.ts`、`src/harness/lib/secret-guard.ts`
- 核心原语：`src/core/{mwgrc,paths,colors}.ts`、`src/core/guide-validation.ts`
- 特性指南：`features/*.md`（popover / anchor-positioning / scrollbar-color / temporal…）
- 主题指南：`guides/`（accessibility / css / forms / html / js / performance / security / ui-components…）
- 评测 / 构建：`src/{grading,analyzing,authoring,build,ci,dashboard}/`
- 治理：`GOVERNANCE.md`、`CONTRIBUTING.md`、`AGENTS.md`
