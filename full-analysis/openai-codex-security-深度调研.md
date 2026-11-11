# openai/codex-security 深度调研报告

> 数据来源：`gh` CLI（repo 元数据、文件树、源码）、OpenAI 官方研究预览博客、掘金/Hacker News/多家技术博客。抓取日期 2026-11-12。

## 1. 📌 一句话定位

OpenAI 把「Codex 编码智能体」包装成一个**应用安全智能体**：用前端 TypeScript CLI/SDK + 后端 Python Codex 插件，做「发现 → 验证 → 修复 → 跟踪」的漏洞闭环，并刻意定位为**传统 SAST 的补充层**而非替代品。

## 2. ⭐ 项目亮点

1. **闭环而非单点扫描**：`scan → validate → patch → verify-fix`，一条命令串起发现、去重、定级、生成补丁、验证补丁（`cs scan .` / `cs patch` / `cs verify-fix`）。来源：`README.md`、`docs/agent-workflows.md`。
2. **第三方扫描器聚合层**：能把 Snyk、Semgrep、Trivy、GitHub code-scanning、Wiz、Checkmarx、Tenable、Black Duck、Veracode 等 **15+ 厂商格式归一化**成统一 schema 并保留稳定身份键，做去重与统一定级（`docs/scanner-imports/schema-guide.md`）。这是它和纯扫描器最大的差异。
3. **多模型后端、可换供应商**：OpenAI 之外支持 Amazon Bedrock（用 AWS 凭证、无需 OpenAI Key）、OpenRouter、Fireworks AI、Cheaper Inference（`README.md` "Other providers"）。
4. **预算与范围可控**：`--max-cost`、`--max-time`、`--diff`、`--mode deep`、批量扫描、Docker Compose 多仓编排，把"花多少钱"做成一等公民。
5. **自带评测基准**：用 `promptfoo` + 真实 **SASTBench**（2,737 条、299 真阳性）做 triage 精度评测，且严格隔离 ground-truth 不进 prompt（`evals/triage-finding/sastbench/DESIGN.md`）。**这点 README 完全没提，是判断它"是不是真 SAST"的关键证据。**

## 3. 🏗️ 项目架构全景

```
codex-security/
├── sdk/typescript/      # CLI + SDK（TypeScript，npm 包主体）
│   ├── src/cli.ts        # 命令入口（巨大，signal/abort/子进程管理）
│   ├── src/deep-scan*.ts # 深度扫描 agentic 循环
│   ├── src/deduplication/# LLM + embedding 去重审查
│   ├── src/classify-severity.ts, severity-review.ts # 多轮投票定级
│   ├── src/external-findings-*.ts  # 15+ 厂商格式归一化
│   └── docs/*.md         # CLI/SDK/去重/定级文档
├── plugins/codex-security/  # 真正的"引擎"：Python Codex 插件 + MCP app + Skills
├── evals/               # promptfoo 评测（triage、sastbench、secret-discovery…）
├── github-action/       # GitHub Action 封装
├── docker/ wolfi/       # 容器化/wolfi 供应链构建
└── docs/ examples/      # 工作流、扫描器导入、集成示例
```

**设计哲学（来自 `AGENTS.md`）：** "thin wrapper around Codex"——信任本地工具，把仓库内容/模型输出/导入产物都当**数据**而非提权依据；反对臆测性防御（"Do not add sanitization… for hypothetical problems"）。最反直觉的一条：**明确禁止对诊断信息做凭据脱敏**——"Do not mask credential-shaped substrings… Do not add `[redacted]`"。理由是凭据保护已由上游 Codex 与权限边界负责，wrapper 不应自行加脱敏逻辑。这是 README 之外的真实工程抉择。

**技术栈：** TypeScript（ESM，Node 22.13+/24/26，还需 Python 3.10+）；依赖 `@openai/codex@0.167.1`、`zod@4`、`ink`/`react` 做 TUI、`papaparse`/`pdfjs-dist`/`saxes` 解析报告；测试用 `bun` + `promptfoo`；容器走 Wolfi/melange/apko 自构建。注意：**核心 Skills/插件逻辑是 Python**，所谓 "TypeScript 项目" 只是前端壳。

**关键配置：** `deep-scan-defaults.ts`（见 §5）、`config.ts`（凭证/路径/权限隔离）、`compose.yaml`（带 AppArmor/seccomp 的容器化批量扫描）。

## 4. 💡 应用场景与启发

- **Vibe Coding 上线前自检**：掘金实测埋 8 个坑（明文密钥、XSS 等）基本都能定位并给出精确到行的修复建议；适合独立开发者上线前跑 `cs scan .`。（来源：juejin.cn/post/7671189079686578185）
- **PR 级增量安全门禁**：`cs scan . --diff origin/main` + 成本上限，接 GitHub Action（官方样例约 $5/次且不因发现而失败），只对本次改动做语义级审查。
- **已有 SAST 结果的统一研判**：把 Snyk/Semgrep 报告导入，统一去重、按自有 rubric 定级、建议 owner，减少多工具告警疲劳。
- **可复用模式：** ① agentic 扫描的"预算旋钮"（`stopAfterNoNew`/`maxDiscoveryRuns`/`maxTimeHours`）值得任何 AI 审计工具借鉴；② `coverage.json` 显式标记 `complete/partial/unknown` 覆盖盲区，比只报发现的工具更诚实（觉醒学院评测）；③ 把多厂商扫描结果**归一化+稳定身份键**的思路，可用于自建安全中台。

## 5. 🧠 核心源码解读

**(a) 深度扫描是迭代 agentic 循环，而非一次性规则集** — `sdk/typescript/src/deep-scan-defaults.ts`：

```ts
export const DEFAULT_DEEP_SCAN_SETTINGS = {
  workers: 4, subagents: 3,
  stopAfterNoNew: 4,          // 连续 4 轮无新发现即停
  stopAfterConsecutiveErrors: 3,
  maxDiscoveryRuns: 40,       // 硬上限
  maxTimeHours: 96,
} as const;
```

**为什么重要**：扫描靠"反复发现→验证"收敛，资源/成本是第一类约束，用户能用旋钮封顶。这也是它非确定性的根源（掘金指出"扫两次结果未必一致"）。

**(b) 严重度定级用多轮独立投票 + 严格 schema 防幻觉** — `sdk/typescript/src/severity-review.ts`：

```ts
export const DEFAULT_REVIEW_RUNS = 3; // classificationRuns 1–10
// 指令明确："Do not anchor on the report's existing severity…
//  Missing verification does not automatically mean low severity."
export const severityDecisionSchema = z.object({
  decision: z.enum(["assessed","excluded"]),
  level: levelSchema.nullable(), rationale: textSchema,
  confidence: z.enum(["high","medium","low"]).nullable(),
}).strict();
```

**为什么**：多次独立评估取共识，且强制"缺失验证≠低危"，直接对抗 LLM 常见的严重度虚高（官方称过度上报严重度已降 90%）。

**(c) 第三方扫描器归一化——它本质是编排层** — `sdk/typescript/src/external-findings-import.ts` + `docs/scanner-imports/schema-guide.md`：

```ts
export async function prepareLocalExternalImport(
  path: string, options, dependencies = {}) {
  const settings = snapshotImportOptions(options);
  const readerSources = distinctSourceRepositories(
    snapshotSourceRepositories(dependencies.sourceRepositories));
  const requested = resolveInputPath(settings.repository, process.cwd(), …);
  // → 读厂商格式 → 归一化为统一 evidence schema → 以稳定 source key 去重
```

**非显而易见点**：每条记录以 `provider + source key + 厂商 finding ID` 作为稳定身份，**重复导入只更新证据、不新建记录**；导入记录初始 `assessment.state = not_assessed`，需经 Codex 二次研判才计入。这意味着它把"别家扫描器"当证据源而非权威，自己掌握最终定级——这是和 Snyk/Semgrep 竞争的核心打法。**公开资料几乎不强调这点。**

## 6. 🌐 全网口碑画像

- 🟢 掘金实测（埋 8 坑）："修复建议…比我见过的很多静态扫描报告强""对 Vibe Coding 做产品的人来说，上线前跑一遍值得" — juejin.cn/post/7671189079686578185
- 🟡 掘金另一篇（三坑）："OpenAI 开源了客户端，把扫描器留在自家云上…这是分发，不是开放"；成本不可预测、`--max-cost` 默认关闭、非确定性、数据出网 — juejin.cn/post/7682968536331354158
- 🟢 HN 高赞（agentbeam 整理，原帖 316 点）：`knighthacker` 认为"去重、误报追踪、预算控制、CI 门禁才是持久价值，不是那次裸模型调用" — agentbeam.com/blog/openai-codex-security-cli-open-source-november-2026
- 🔴 生产实测（FlipFactory）："对 LLM 生成代码审查强，对提示注入脆弱，对供应链风险完全沉默"；调参后误报率 22%→13%，约 $0.004/文件 — devaitoolkit.com/blog/is-openai-codex-security-actually-safe-for-prod
- 🟡 安全审计（greenlitbooks）："扫描默认 `approvalPolicy=never`、不暂停等你确认，代码会发到 OpenAI；建议只扫自有的、放进容器、清掉无关云凭证" — greenlitbooks.com/field-notes/is-codex-security-safe
- 🔴 争议点：多名 HN 用户（andreagrandi、ryanto）报告扫描被 `chatgpt.com/cyber` 标记为"可能的网络安全风险"而中断——Trusted Access for Cyber / Daybreak 是硬性门槛，非 bug。
- 🟢 官方数据（研究预览博客，前身 Aardvark）：30 天扫描 120 万次提交，发现 792 关键 + 10,561 高危；噪声降 84%、误报降 50%+ — openai.com/index/codex-security-now-in-research-preview

## 7. ⚔️ 竞品对比

| 维度 | Codex Security | Semgrep | GitHub Advanced Security (CodeQL) | Snyk |
|---|---|---|---|---|
| 检测方式 | LLM 语义/上下文理解 | 规则+部分 AI | 数据流/污点分析(确定性) | SAST+SCA+AI |
| 确定性/离线 | 否，需云端/供应商 | 规则离线可跑 | 离线可跑 | 需账号/云端 |
| 误报治理 | 沙箱验证+多轮定级+去重 | 中（规则误报） | 低（确定性强） | 中 |
| 修复建议 | 生成补丁+验证 | 有限 | 有限 | 有（依赖项） |
| 供应链(SCA) | 弱（靠导入别家） | 弱 | Dependabot | **强** |
| 数据出网 | **是（OpenAI 云）** | 可自托管 | GitHub 内 | 是 |
| 成本模型 | 按 token/订阅 | 免费层+付费 | GitHub 席位 | 订阅 |
| 定位 | 语义层补充 | 快扫主力 | CI 主力 | 全栈 |

**选型建议：** 已有 Semgrep/CodeQL 做快扫与门禁的团队，把 Codex Security 放在**关键路径/PR 审查/难定性的上下文漏洞**上做"第二轮语义研判"；供应链与合规强约束（金融/政务）场景暂不宜直接接生产仓（数据出网 + 非确定性）。它**不是** Snyk 的 SCA 替代品。Claude Code 安全能力偏"编码时护栏"，与 Codex Security 的"后验审计闭环"互补而非直接竞争。

## 8. 🎯 核心研判

**优势：** ① 上下文/语义级发现能力强，能抓规则型工具漏掉的逻辑漏洞；② 闭环（验证+补丁+验证）与多厂商聚合定位独特；③ 自带 SASTBench 评测，工程严谨度高于一般"AI 包装"项目；④ 多供应商后端降低锁定。

**风险：** ① **数据出网 + 非确定性**，企业合规存疑；② 成本不可预测、`--max-cost` 默认关闭；③ 部分能力受 Daybreak/Cyber 访问限制，公开"开源"≠人人可用（appreviewlab 称"开源的是前门，产品锁在云上"）；④ 供应链/SCA 弱，对提示注入脆弱；⑤ 仍 pre-1.0（v0.9.1），minor 版本可能改公共 API；⑥ 本地 `serve`/看板已被移除，findings service 转 Cloud 预览。

**适用 / 不适用：** 适用=独立开发者、Vibe Coding 产物、AI 生成代码审查、PR 级语义门禁、已有 SAST 的二次研判。不适用=强合规/涉密仓库、纯离线环境、需要稳定可复现结果的合规审计、SCA 主力。

**趋势判断：上升期（但非爆发式成熟）。** 4 个月 1.1 万+ star、920 fork、活跃迭代（issue #2600+），官方将其并入 Codex 生态并推 Cloud；但访问门槛、成本与确定性三大问题未解，短期是"强补充"而非"替代品"。值得持续跟踪其定价与本地/自托管路线。

## 📂 关键文件路径速查

- `README.md` — 功能总览与 Quick Start
- `AGENTS.md` — 设计哲学（含"禁止诊断脱敏"反直觉条款）
- `sdk/typescript/src/cli.ts` — CLI 主入口与进程/信号管理
- `sdk/typescript/src/deep-scan-defaults.ts` — 深度扫描迭代循环默认参数
- `sdk/typescript/src/severity-review.ts` — 多轮投票定级与严格 schema
- `sdk/typescript/src/classify-severity.ts` — 基于 rubric 的严重度分类
- `sdk/typescript/src/deduplication/deduplication.ts` — LLM+并发去重审查
- `sdk/typescript/src/external-findings-import.ts` — 第三方扫描器归一化导入
- `docs/scanner-imports/schema-guide.md` — 15+ 厂商格式身份键与字段定义
- `evals/triage-finding/sastbench/DESIGN.md` — SASTBench 精度评测设计与标签隔离
- `plugins/codex-security/` — 真正的 Python Codex 插件/Skills/MCP 引擎
- `github-action/README.md` — GitHub Action 接入（含 $5 上限样例）
- `compose.yaml` + `docker/` — 容器化批量扫描与 AppArmor/seccomp 沙箱
- `CHANGELOG.md` — 版本演进（v0.8.3 起 Daybreak 预算、helper 迁移等）
- `docs/agent-workflows.md` — 在 Codex 中选用扫描/修复/验证等任务映射
