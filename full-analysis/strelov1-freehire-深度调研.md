# strelov1/freehire 深度调研

> 调研日期：2026-10-22 ｜ 星标：2,253 ⭐ ｜ 语言：Go ｜ 许可：MIT ｜ 默认分支：main
> 定位：**自托管的开源求职搜索引擎 —— 直接从公司 ATS 抓取 3.3M+ 实时职位，无中介、无 repost、无死链**

## 一、项目亮点（差异化）

1. **从源头直采，单一 schema 去重**：从 124 个 ATS 平台（Workday/Greenhouse/Lever/iCIMS…）+ 97 个 Telegram 频道 + 52 个公司官网 career 页，抓取 3.37M+ 唯一在招职位；同一职位跨 Board 自动归一为一个条目（稳定指纹去重）。
2. **"理解职位"的 faceted 搜索**：基于 Meilisearch 的区域 / 远程 / 职能 / 资历 / 技能 / 薪资多维分面检索，字典由人工策展（不靠模型猜测），无命中不出字段。
3. **确定性 CV↔职位评分 + 上层 LLM 拟合**：`cvmatch` 做可复现的确定性匹配分，LLM 仅做"拟合分析"且不编造；CV 润色明确"发明零内容"。
4. **内建 agent 但零凭证零 shell**：应用内 agent 含 5 个预设（chat / browse / profile / CV 润色 / 面试演练），进程内运行、无 shell、无铸造凭证；另提供 MCP server、CLI、浏览器扩展、ChatGPT Actions。
5. **全栈 MIT 自托管**：pipeline 与数据双双开源，Docker Compose 一键起。

## 二、核心架构

- **服务**：Go + Fiber v2（HTTP）；PostgreSQL + pgvector（存储 + 过滤 + 语义向量）；sqlc（由 SQL 生成类型安全 DB 访问，无 ORM）；Meilisearch（全文 + 分面）；SvelteKit 2（Svelte 5 runes + Tailwind 4）前端；Redis（限流 + 实时扇出）；S3 兼容对象存储（CV/头像/预览）。
- **LLM 层**：`langchaingo`（接任意 OpenAI 兼容端点，不绑定厂商）+ `Bifrost`（网关：每用户虚拟 key、跨供应商 fallback、花费追踪）+ Langfuse（调用追踪）。
- **Worker 模型**：服务只暴露 API；抓取/富集/索引/通知都是 `cmd/` 下"跑一次即退出"的独立 worker（`ingest`/`enrich`/`embed`/`search-drain`/`reindex`/`tg-ingest`/`tg-extract`/`capture-apply-form`/`backfill-derive`），cron 调度；worker 失败非零退出、不硬删职位（仅软关闭）。
- **领域包**：`internal/` 约 130 个包，关键者：`sources/`（ATS 适配 + 注册表）、`pipeline/`（fetch→normalize→dedup→upsert）、`search/`/`searchdrain/`（Meilisearch 索引与查询）、`enrich/`（AI 富集契约 + 队列）、`cvmatch/`/`matchanalysis/`（确定性评分 + LLM 拟合）、`assistant/`（agent 循环）、`inbox/`（ recruiter 邮件→关联申请）、`ghost/`（"职位是否真实"信号）。

## 三、应用场景与启发

- **"垂直领域聚合 + AI 增强 + 自托管"的完整样本**：从多源抓取、归一去重、实时索引到 AI 辅助申请/追踪，是一条可复用的端到端范式，适合任何"公共数据聚合 + 私有 AI 增强"的场景（房产、招标、论文等）。
- **确定性优先的混合评分设计值得借鉴**：把"可复现的确定性匹配"放在底层、"LLM 拟合分析"放在上层且声明不编造——既享 LLM 表达力又保可审计，避免纯 LLM 评分不可复现。
- **对求职/招聘类需求**：与用户已调研的 `career-ops-hq/career-ops`、`MadsLorentsen/ai-job-search` 同赛道但更偏"数据底座 + 自托管"，互补而非替代。

## 四、源码深度解读

**1) `internal/ingest/sources` —— 统一 `Source` 接口 + `sources.All` 注册表**
加一个新 ATS 平台只需实现一个 adapter（同一 `Source` 接口），并在 `sources.All` 注册一行；adapter 的 Go 类型自带"来源种类"属性，无需网络调用即可分类。Board 目录（`company`+`provider`+`board`）进注册表前先校验：

```go
// 新增 ATS 平台 = 新 adapter + 一行注册（伪代码示意）
type Source interface { Fetch(ctx, board) ([]Job, error); Normalize(...) Job }
// sources.All 聚合所有 adapter；board 进目录前对照注册表校验
```

**2) `internal/pipeline` —— 摄取主流程**
`fetch → normalize → dedup → upsert` 四段式，是"多源 → 单一 schema」的骨架；确定性列（facet / fingerprint / slug）由 `backfill-derive` 一次性 keyset 重算，再 `make reindex` 重建搜索索引。

**3) `internal/cvmatch` + `internal/matchanalysis` —— 确定性评分在上、LLM 在下**
`cvmatch` 产出可复现的 CV↔vacancy 分数；`matchanalysis` 在此基础上叠加 LLM 拟合分析。README 明确："CV tailoring that invents nothing"——这是可信 AI 应用的纪律样板。

## 五、社区口碑

- 2.2k ⭐（快速上升），Product Hunt 发布（2026-08-26）、Trendshift 上榜；MIT、贡献开放（无 allowlist，issue/PR 人人可提）。
- 文档完整（`docs/features.md` / `docs/architecture.md` / `docs/api.md` / `docs/sources.md`），每包附 `AGENTS.md`；"免费托管站 freehire.me" 提供开箱体验。

## 六、竞品对比 + 核心研判

| 项目 | 类型 | 差异 |
|---|---|---|
| **freehire** | 开源 + 自托管 | 源头直采 + 去重 + 确定性评分 + 内置 agent |
| LinkedIn / Indeed | 商业 job board | 闭源、含 repost/死链、不开放数据 |
| 其他开源聚合 | 列表/抓取 | 多缺去重与 AI 辅助申请闭环 |
| career-ops / ai-job-search | agent 工作流 | 偏"申请流程自动化"，非数据底座 |

**研判**：对个人求职者、研究者、以及想搭"招聘数据平台"的团队都有价值，MIT 可自托管是硬优势。主要依赖社区贡献 source 维持数据广度；LLM 功能需自配 key（经 Bifrost 虚拟 key 做花费归因）。对"纯看职位"用户，免费托管站即够；对"要可控数据/接自有 agent"用户，自托管价值最大。

## 七、关键文件速查

- `cmd/` —— server + 各独立 worker 入口（ingest/enrich/embed/search-drain/reindex/tg-ingest…）
- `internal/ingest/sources/` —— ATS adapter + `sources.All` 注册表
- `internal/pipeline/` —— fetch→normalize→dedup→upsert 主流程
- `internal/search/` `internal/searchdrain/` —— Meilisearch 索引与查询
- `internal/cvmatch/` `internal/matchanalysis/` —— 确定性评分 + LLM 拟合
- `internal/assistant/` —— 进程内 agent 循环（无 shell/无凭证）
- `web/` —— SvelteKit 前端；`extension/` —— Chrome 侧栏扩展
- `docs/architecture.md` —— crawl→search 拓扑与三主流程走查
- `migrations/` —— SQL schema（sqlc 与 initdb 共用源）
