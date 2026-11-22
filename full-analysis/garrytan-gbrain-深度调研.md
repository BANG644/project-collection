# 🧠 garrytan/gbrain 深度调研

> 调研日期：2026-11-23（全文重写，原稿停留 v0.30 时代） | 星标：33,416⭐（原稿 22,854） | Forks：5,011 | 语言：TypeScript | 许可：MIT | 默认分支：master | 最近推送：2026-11-22（当日活跃） | Open Issues：373

## 一句话定位

YC 总裁 Garry Tan 开源的「Agent 记忆层」——把明确事实连同**来源、更正、撤回**一起存进 markdown + Postgres，让 Codex / Claude Code / OpenClaw / Hermes 等多个 Agent 共享同一个「可控、可纠错」的大脑；一句话卖点是「我睡觉时它在整理我的知识，醒来我比睡前更聪明」。

## 项目亮点（差异化，先看这 5 条）

1. **Plain-text 为真相源**：知识以 markdown 存在 git 仓库里，可 diff、可分支、可重建；数据库只放索引/图谱/元状态。这决定了它「可迁移、 vendor 锁定低」，也是第三方评测公认的最大选择理由。
2. **零 LLM 调用的图谱抽取**：用 `works_at` / `invested_in` 这类 typed predicate（正则规则 + fail-improve 回环：LLM 兜底一次就沉淀成新 regex）建类型化知识图谱，摄取近乎免费；官方自测图谱层带来 **+31.4 点 P@5**（49.1% P@5 / 97.9% R@5，240 页自建语料）。
3. **`search` 返回页面，`think` 返回带引用的答案 + 差距分析**：差距分析（明确指出「大脑不知道什么」）是它区别于普通 RAG 的标志性能力。
4. **工程化的检索栈**：HNSW 向量 + 全文检索 + RRF 融合 + 重排 + CRAG 置信度分级 + query arms + source boost + evidence delivery 预算控制——把「个人 RAG」做到了生产级检索系统的细节密度（见源码解读）。
5. **Day-one 单操作员设计（也是双刃剑）**：作者自述生产大脑 155,795 页 / 24,589 人 / 5,340 公司 / 66 个定时 cron；但官方明确只把 OpenClaw / Hermes 当一等公民，无多租户隔离（共享凭证属「另一道信任边界」）。

## 核心架构

三层职责清晰，且每层都有大量独立子模块（仓库已达 v129 schema migration + Rust engine）：

```
存储层   markdown(git) 真相源  +  Postgres/pgvector 索引与图谱（本地起步用 PGLite，2 秒启动免 Docker）
   ↓
检索层   hybridSearch：keyword + vector → RRF 融合 → 归一化 → source boost → cosine 重排 → dedup
         + CRAG 置信度分级（低置信自动升级检索）+ query arms + evidence budget
   ↓
综合层   gbrain think：在检索结果上生成带引用答案 + 差距分析（gap analysis）
   ↓
自治层   Dream Cycle：夜间 cron 自动摄取/丰富/整合/修正引用；Signal Detector 每条消息捕获想法/实体/待办
```

关键目录：`src/core/search/`（检索流水线各阶段）、`src/core/engine-sql/`（SQL 排序/图谱）、`src/core/cycle/`（Dream 自治循环）、`src/core/ops/`（search/graph-query 等操作）、`src/cli/commands/`（think/search/dream/schema 等命令）。MCP 支持 stdio + HTTP 双模式。

## 应用场景与启发（重点）

- **「Agent 记忆不该被锁在产品里」的参考实现**：换 Agent（Codex→Claude→Hermes）不必重新交代上下文，因为记忆在 markdown + 自己的库里。做任何长期个人助理/知识 Agent，这套「plain-text 真相源 + 可插拔检索」是范本。
- **「规则抽实体、LLM 只兜底」的成本哲学**：不是所有知识抽取都要调 LLM。typed predicate + fail-improve 回环值得借鉴到任何「结构化落库」场景（错题归因的知识点抽取、日志实体识别同理）。
- **「tidy ≠ trustworthy」是整类产品的开放问题**：Slite 的锐评点破——GBrain 夜里把大脑整理得井井有条（fresh、links 完整），但几乎不验证内容「对不对、全不全」。做记忆/RAG 系统要主动补事实校验与来源可信度，否则「整洁的错记忆」比没有更危险。
- **差距分析（gap analysis）是被低估的产品点**：不只会答，还会说「这块我不知道」。任何面向决策的检索系统都应显式暴露不确定性，而不是硬凑一个答案。
- **别拿它当团队/wiki 方案**：单操作员、无真正权限模型、本地文件与共享库凭证是两道信任边界——团队场景要么自建隔离，要么选 Mem0 这类带租户概念的方案。

## 源码解读（3 个最核心模块，精炼骨架）

### 1. 混合检索 RRF 融合（`src/core/search/hybrid.ts`）

文件头注释直接写明了整条流水线与打分公式，是全仓最值得读的一段：

```ts
/**
 * Pipeline: keyword + vector → RRF fusion → normalize → boost → cosine re-score → dedup
 * RRF score = sum(1 / (60 + rank_in_list))       // 标准 RRF，k=60
 * Compiled truth boost: 2.0x after RRF normalization
 * Cosine re-score: blend 0.7*rrf + 0.3*cosine for query-specific ranking
 */
export const RRF_K = 60;
// 关键设计：归一化后 100 深池的 RRF 范围仅 1/60→1/160，
// 因此 2x boost 只在「boost 行落进前 60 名」时才可能反超 rank-1 行（#3695 注释自证）
```

启发：boost 与 RRF 归一化范围的**量纲关系**被显式建模，避免「加权把排序炸掉」——这是很多自研混合检索会踩的坑。

### 2. 检索分级与预算（`src/core/ops/search.ts`，94KB）

search 操作簇把「检索质量」拆成十几个独立阶段，每阶段一个模块：

```ts
import { gradeRetrievalConfidence, shouldEscalateRetrieval, confidenceRank } from '../search/crag.ts'; // CRAG：置信度分级 + 自动升级检索
import { applyQueryArms } from '../search/query-arms.ts';        // 多路 query 并行召回
import { resolveBoostMap, resolveHardExcludes } from '../search/source-boost.ts'; // 来源加权/硬排除
import { deliverEvidence, capEvidenceToBudget, countEvidenceTokens } from '../search/evidence-delivery.ts'; // 证据按 token 预算投递
// #4356：文本路径不再硬编码默认 20 条；cheap-hybrid 默认走「向量+关键词+RRF+池+标题+别名」
```

值得抄的点：证据投递按 **token 预算**控制（`capEvidenceToBudget`/`countEvidenceTokens`），而不是拍脑袋定返回条数。

### 3. 图谱排序的可读性/成本约束（`src/core/engine-sql/graph-rank.ts`）

`rank_entities` 聚合把工程严谨性写进注释：

- 一条边 = 活端点间去重后的 `(from, to, link_type)` 三元组；mention 边仅在 `includeMentions` 时计入（反向链接计数惯例）。
- **retirement fold**：被 `superseded_by`/`merged_into` 的页面在 `MAX_RETIREMENT_HOPS` 内把边折叠给活页面，折叠后去重、自环丢弃、环靠跳数上限终止。
- 成本注释给实测：Postgres 16 / 20 万页 / 98.5 万边，全图排序本地与远程各约 **3 秒**，因此放在 statement deadline 下跑。

这三点（边定义精确、重定向折叠、大数据量下的成本透明）是「能上生产的图谱排序」和 demo 级实现的分水岭。

## 全网口碑（真实外链 + 争议）

**正面**
- [Slite 深度评测](https://slite.com/learn/gbrain-review)：读完全仓代码，评价「工程确实好」，连续摄取 + 夜间 dream cycle + 零 LLM 图谱是真实强项；发布 1 天破 5,000⭐，属「company brain 运动的参考设计」。
- [TechMoon 中文解析](https://techmoon.xyz/gbrain-garry-tan-agent-memory)：梳理作者三次亲自定调（4/15 开源、4/30 日用在 OpenClaw+Hermes、5/16「这是知识系统，不是盒装 RAG」），强调 plain-text 真相源与「有主见（opinionated）」的产品立场。
- [HN 讨论](https://news.ycombinator.com/)：多条帖子（「most important idea of the year」等），社区热度真实。

**争议 / 局限（独家）**
- **tidy vs trustworthy**：Slite 的核心批评——它把大脑「整理得整洁」，但**几乎不验证内容正确性与完整性**；这是整类记忆系统的开放问题。
- [mrkeyoor 沙箱实测](https://mrkeyoor.com/repos/gbrain)：295 包 87 秒装完、10 秒构建，但**测试跑满 900 秒未完成**（无绿测）；并指出 keyless ≠ 全本地（harness 仍看到召回内容、云 provider 可收到文本）、issue #5858「frontmatter 触发器到不了模型、resolver 文件缺失」。
- [BorjaIP 诚实评测](https://borjaip.github.io/pkm/articles/webs/GBrain-Review---An-Honest-Assessment-of-Garry-Tan's-Brain)：肯定复利机制，但点明 ~v0.30 有破坏性变更、仅支持单一 Agent、纯自托管无多租户；**评测者在卖竞品 Hindsight，推荐带立场，需打折看**。
- 规模数据（15.5 万页等）均为**作者自述、非独立审计**；benchmark 语料自建，与其他系统分数不可直接横比。

## 竞品对比 + 核心研判

| 维度 | gbrain | Mem0 | Letta (MemGPT) | Graphiti | Notion AI / mem.ai |
|------|--------|-------|----------------|----------|--------------------|
| 真相源 | markdown+git（可 diff/迁移） | 托管向量/图 | 内存状态机 | 图+向量（时序） | 厂商云内 |
| 抽取成本 | 规则零 LLM + 兜底 | 依赖 LLM 抽取 | 依赖 LLM | LLM 抽实体边 | 封闭 |
| 图谱 | typed predicates，零调用 | 有限 | 无 | 时序图（强项） | 弱/无 |
| 差距分析 | ✅ 独有卖点 | ❌ | ❌ | ❌ | ❌ |
| 多租户/权限 | ❌ 单操作员 | ✅ | ✅ | 部分 | ✅ |
| 许可 | MIT 自托管 | 混合 | 开源 | Apache | 闭源 |

**研判**：GBrain 的护城河不是「技术不可替代」，而是「plain-text 真相源 + 零成本图谱 + 差距分析 + YC CEO 背书」的组合拳，恰击中了「Agent 换得快、记忆被锁死」的痛点。它最优的场景是**单操作员、markdown 重度用户、愿意自托管**；短板同样清晰——无多租户、无事实校验、破坏性变更频繁、测试套件不稳。趋势判断：作为「个人 Agent 记忆层的事实参考设计」价值很高，作为「团队可信知识库」仍需补权限与 truthfulness 两课。适合借鉴架构思想，慎作生产依赖。

## 关键文件路径速查

- `src/core/search/hybrid.ts` — RRF_K=60 / 2x compiled-truth boost / 0.7·rrf+0.3·cosine 重排
- `src/core/ops/search.ts` — 94KB 检索操作簇：CRAG 置信度、query arms、source boost、evidence 预算
- `src/core/engine-sql/graph-rank.ts` — rank_entities 边计数、retirement fold、全图排序成本注释
- `src/core/cycle/` — Dream Cycle 自治（dream-breaker / dream-taint / dream-write-deferral）
- `src/commands/think.ts` — 带引用综合答案 + 差距分析入口
- `README.md` / `ORIGIN.md` — 产品立场与规模自述（ORIGIN 记录早期 17,888 页规模）

> 本报告由 GitHub 深度调研员于 2026-11-23 全文重写：基于当日 API 元数据、仓库 v129 真实源码与 5 篇第三方评测，修正了原稿过时的星标数（22,854→33,416）、缺失的铁律章节与空泛口碑。🔍🐙
