# HKUDS/DeepTutor 深度调研

> **调研日期**：2026-07-17
> **仓库地址**：https://github.com/HKUDS/DeepTutor
> **Stars**：26,781 | **Forks**：3,608 | **协议**：Apache 2.0 | **语言**：Python 3.11+（后端 FastAPI）+ Next.js 16 / React 19（前端）
> **定位**：Lifelong Personalized Tutoring（终身个性化辅导）——一个 agent-native 的学习工作空间，把辅导、解题、出题、研究、可视化、掌握度练习收进同一套可扩展系统。HKUDS 出品，论文 arXiv:2604.26962。

---

## 目录

1. [项目全景](#1-项目全景)
2. [项目亮点](#2-项目亮点)
3. [核心架构深度拆解](#3-核心架构深度拆解)
4. [应用场景与启发](#4-应用场景与启发)
5. [源码精读（独家发现）](#5-源码精读独家发现)
6. [全网口碑交叉验证](#6-全网口碑交叉验证)
7. [竞品深度对比](#7-竞品深度对比)
8. [核心研判](#8-核心研判)
9. [附录：关键资源链接](#9-附录关键资源链接)

---

## 1. 项目全景

DeepTutor 由 HKUDS（香港大学数据智能实验室）的 Bingxi Zhao 主导，2025-12 发布，111 天冲到 20K⭐，是典型的「学术驱动 + 开源狂奔」项目。它想解决的核心痛点是：**今天的 Agent 是一次性、任务导向、彼此孤立、记忆浅且不可见**。DeepTutor 的答案是——把所有学习相关能力跑在**同一个 agent loop** 上，并给记忆一个**可读、可审计、可追溯证据**的文件化三层结构。

六大主面（Chat / Quiz / Research / Visualize / Solve / Mastery Path）共享一个运行时：你切换的是「目标」，不是「引擎」，上下文随学习者走。与之相连的是知识库、书籍、Co-Writer 草稿、笔记本、题库、人设与 Memory——它们跨所有工作流可用，而非锁在孤立工具里。

技术底座是 **FastAPI 后端 + Next.js 16 前端**，单容器只暴露 `:3782`（前端），由 `web/proxy.ts` 中间件把 `/api/*`、`/ws/*` 转发到容器内后端。CLI 是 agent-native 的：任何 `run` 加 `--format json` 即输出 NDJSON，可被别的 Agent 当作工具驱动。

---

## 2. 项目亮点

### 2.1 独家发现：一套 agent loop 承载所有模式
Chat/Quiz/Research/Visualize/Solve/Mastery Path 不是六套引擎，而是同一 `ChatOrchestrator` 上的不同 capability。`ask_user` 是特殊的——Agent 可暂停本轮、问结构化澄清问题、你回答后恢复。这把「多能力产品」的复杂度压到了一个循环里。

### 2.2 文件化、可审计的三层记忆
L1 工作区镜像 + 追加式事件 trace（`trace/<surface>/<date>.jsonl`）；L2 每面精选事实（`L2/<surface>.md`）；L3 跨面综合（`L3/<profile|recent|scope|preferences>.md`）。因为 L2 引用 L1、L3 引用 L2，**任何综合结论都能追溯到原始事件**——这是黑盒向量记忆做不到的。

### 2.3 多引擎知识库 + 版本化索引
RAG 引擎可任选：LlamaIndex（默认，本地向量+BM25）、PageIndex（托管、带页码引用的推理检索）、GraphRAG / LightRAG（知识图谱）、LightRAG Server（外挂实例）、或直连 Obsidian  vault。重建索引写新的 `version-N` 目录并保留旧版——**工作中的索引永不在重建中途被销毁**。

### 2.4 Partners：同一大脑上的持久伙伴
Partner 不是独立 bot 引擎，而是「一个有性格、有电话号码的聊天」。每条入站 Web/IM 消息都变成 partner 作用域内的普通 `ChatOrchestrator` 回合；它读主人的记忆、只写自己的记忆。渠道层 schema 驱动，可接 Feishu/Telegram/Slack/Discord/DingTalk/QQ/WeCom/WhatsApp/Zulip/Mattermost/Matrix/Mochat/Teams 等 15+ 渠道。

### 2.5 技能导入安全门
所有技能导入（无论 EduHub 还是 ClawHub）过同一道闸：先查注册表安全裁决、防御性解压（zip-slip/zip-bomb 防护 + 文本/脚本后缀白名单）、**剥离 `always:`**（防止下载的技能强行塞进每个系统提示）、并把来源写入 `.hub-lock.json` 供审计。

---

## 3. 核心架构深度拆解

```
DeepTutor/
  web/                      # Next.js 16 (React 19) 前端；web/proxy.ts 转发 /api/*、/ws/* 到后端
  backend (FastAPI)         # ChatOrchestrator + capabilities + tools + memory 整合器
  packaging/deeptutor-cli/  # CLI-only 发行包（无 Web 资产）
  SKILL.md                  # ~150 行 handover doc，教会任意工具型 LLM 整个 surface
  data/user/settings/       # 纯 JSON/YAML 配置（推荐用浏览器 Settings 编辑）
    model_catalog.json      # LLM/embedding/search 提供商、API key、活跃模型
    system.json             # 前后端端口、CORS、SSL、附件目录
    auth.json / integrations.json / interface.json
    main.yaml / agents.yaml # 运行时默认、capability/tool 温度与 token
  data/
    user/  users/<uid>/  partners/<id>/workspace/  system/   # 多用户隔离布局
```

- **部署**：PyPI `pip install -U deeptutor` + `deeptutor init` + `deeptutor start`；或源码装；或 Docker `ghcr.io/hkuds/deeptutor:latest`（只发布 `:3782`）。
- **工具两类**：用户可切换的 `brainstorm/web_search/paper_search/reason/geogebra_analysis/imagegen/videogen`；上下文自动挂载的 `rag/read_source/read_memory/write_memory/consult_subagent/exec/ask_user/...`。
- **沙箱**：office 技能（docx/pdf/pptx/xlsx）让模型写短 Python 脚本经 `exec` 运行；默认受限子进程沙箱，`sandbox_allow_subprocess=false` 可关。
- **HKUDS 血统**：原 TutorBot 基于 nanobot；复用 LightRAG、AutoAgent、AI-Researcher；CLI 工作流受 Claude Code / Codex 启发；ClawHub 兼容（OpenClaw 是其技能生态后端）。

---

## 4. 应用场景与启发

1. **「一循环多能力」范式**：如果你在做多面 Agent 产品，别为每种能力写一套引擎——用 capability 切目标、共享 agent loop，上下文随用户走。
2. **可审计记忆是信任基石**：L1→L2→L3 的引用链让「个性化」可被用户审阅/纠错，比黑盒向量记忆更适合教育、医疗、法律等高风险场景。
3. **版本化 RAG 索引**：重建绝不破坏工作中的索引（写 `version-N` + 保留旧版），是高可用知识库的必学模式。
4. **Agent-native CLI（NDJSON）**：把产品做成「能被别的 Agent 驱动的工具」——`--format json` + `session_id` 复用，直接塞进 LangChain/AutoGen 循环。
5. **技能安全门**：任何「从社区拉技能/插件」的产品都该抄这道闸（安全裁决 + 防御解压 + 剥 `always:` + 来源锁）。
6. **Partner 模型**：「有性格、有电话号码的聊天」——把持久陪伴 Agent 跑在和主 Agent 同一套大脑上，降低维护成本。

---

## 5. 源码精读（独家发现）

### 5.1 单一 agent loop 的 tool 编排
Chat 循环中模型按轮思考 → 调工具 → 观察 → 以无工具消息收尾。`ask_user` 是例外路径：暂停回合、问结构化问题、恢复。上下文分两种——**sticky session context**（subagent/KB/persona/model/voice，驻留工具条跨轮）与 **one-time references**（`+` 菜单选文件/历史/书/笔记本/题库，仅本轮）。

```text
# 典型 loop 伪结构
think(round) → call_tool(when useful) → observe(result)
  → ask_user(structured)  # 例外：暂停→恢复
  → finish(tool_free_message)
```

### 5.2 三层记忆的文件化金字塔
L3 综合居中、L2 中环、L1 trace 外环；Memory Graph 把整座金字塔画出来，任一综合结论可点回原始事件。整合器的 Update/Audit/Dedup 预算在 Settings → Memory 可调。

### 5.3 技能导入安全门（防御性）
```text
import skill:
  1. check registry security verdict   # 被标记则拒（除非 --allow-unverified）
  2. defensive extract (zip-slip/bomb guard + suffix whitelist)  # 二进制永不进工作区
  3. strip `always:` from frontmatter  # 下载的技能不能强塞进每个系统提示
  4. write .hub-lock.json (hub, version, verdict, time)  # 审计/更新用
```

---

## 6. 全网口碑交叉验证

- **正面**：功能完整性在开源 AI tutor 里罕见（辅导/解题/出题/研究/可视化/掌握度 + 多引擎 RAG + 三层记忆）；Apache 2.0 全开源、无付费产品；HKUDS 学术背书 + 论文；ClawHub/EduHub 技能生态互通；迭代极快（几乎日更）。
- **负面/摩擦**：项目年轻（2025-12 发布），API/结构仍可能变动；全栈较重（Next.js 16 + FastAPI + 多 RAG 引擎），资源占用不低；多用户 auth 默认关闭，企业落地需自己加固；「20K⭐ in 111 days」的成长速度伴随一定营销色彩。
- **社区信号**：26.7K⭐、3.6K fork，TrendShift 日/周榜常客；Discord/飞书/微信多社群活跃。

---

## 7. 竞品深度对比

| 维度 | DeepTutor | NotebookLM | 私有 GPT / AnythingLLM | ChatGPT/Claude 当 tutor | LangChain/AutoGen |
|------|-----------|------------|------------------------|--------------------------|-------------------|
| 定位 | agent-native 学习工作空间 | 知识笔记本 | 本地 RAG 聊天 | 通用聊天 | 开发者框架 |
| 多能力一体 | ✅ 同 loop | ❌ | ❌ | 部分 | 自组 |
| 可审计记忆 | ✅ L1/L2/L3 + 证据链 | ❌ | ❌ | ❌ 黑盒 | 自管 |
| 多引擎 RAG | ✅ 5+ 引擎 | ❌ | 有限 | ❌ | 自接 |
| 版本化 KB 索引 | ✅ | ❌ | 部分 | ❌ | 自管 |
| 持久 Partner/IM | ✅ 15+ 渠道 | ❌ | ❌ | ✅ App | ❌ |
| Agent-native CLI | ✅ NDJSON | ❌ | 部分 | ❌ | ✅ |
| 开源 | ✅ Apache 2.0 | ❌ | ✅ | ❌ | ✅ |

**结论**：DeepTutor 在「开源 + agent-native + 可审计记忆 + 多引擎 RAG」组合上几乎无直接对手。NotebookLM 体验好但闭源且非 agentic；本地 RAG 方案缺辅导闭环；通用聊天缺持久记忆与学习工作流。它的真正对手是「用户自己拼 Claude Code + 知识库」的 DIY 方案。

---

## 8. 核心研判

### 优势
- 全功能 agent-native 学习空间，且全开源、有论文背书。
- 三层可审计记忆是教育场景的信任护城河。
- 版本化 RAG + 多引擎选择，工程成熟度高于多数学术项目。
- CLI agent-native + ClawHub 互通，天然可嵌入更大 Agent 生态。

### 风险
- 年轻项目，稳定性/API 锁定度待观察。
- 全栈重，自托管资源成本不低。
- 学术项目可持续性与商业化路径不明确（目前明确无付费产品）。

### 入场建议
- 想要开源、可自托管的「AI 私教 + 研究 + 知识管理」一体化 → DeepTutor 是当前最优选。
- 想借鉴架构 → 重点抄「单 loop 多能力」「L1/L2/L3 可审计记忆」「版本化 RAG 索引」「技能导入安全门」。
- 生产嵌入 → 用 `--format json` 的 CLI 把它当工具接进你的 Agent 编排。

### 一句话总结
> DeepTutor 把「辅导、研究、记忆、知识」焊进同一个可审计的 agent 循环，是开源世界里最接近「终身个性化私教」的实现，架构纪律远超一般学术项目。

---

## 9. 附录：关键资源链接

- 仓库：`https://github.com/HKUDS/DeepTutor`
- 文档：`https://deeptutor.info`；论文：`https://arxiv.org/abs/2604.26962`
- 关键目录：`web/`（Next.js 16，含 `web/proxy.ts`）、后端 FastAPI、`packaging/deeptutor-cli/`、`SKILL.md`、`data/user/settings/*.json`、`data/{user,users,partners,system}/`
- 生态：EduHub（`eduhub.deeptutor.info`，默认 hub）、ClawHub（兼容）；技能格式为 open Agent-Skills（`SKILL.md` + 引用文件）
- 同源 HKUDS：`nanobot` / `LightRAG` / `AutoAgent` / `AI-Researcher`

*本报告由 GitHub 深度调研员基于仓库 README、发布记录与 gh API 元数据深度整理 🔍🐙*
