# 🛡️ SkillSpector — AI Agent Skills 安全扫描器（NVIDIA）

> **仓库:** [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector)
> **Stars:** 14,164 ⭐（2026-06-21 入库时 8,602 → 本轮校正 14,164，约 6 周 +5,562，增长迅猛）
> **最后推送:** 2026-08-04 ｜ **语言:** Python 3.12+ ｜ **许可:** Apache-2.0
> **定位:** 在安装 Agent Skills（Claude Code / Codex / Gemini CLI 的 SKILL.md）之前，检测漏洞、恶意模式与供应链风险的安全闸门

---

## 项目亮点（差异化）

- 🔱 **NVIDIA 官方出品 + OpenSSF Scorecard**：企业级维护，`.github/workflows/scorecard.yml` 跑供应链安全评分，背书度高。
- 🕸️ **LangGraph 状态机编排**：扫描流程是一个可观测、可扩展的图（`graph.py` + `langgraph.json`），而非一堆 if/else 脚本。
- 🧩 **两阶段分析（静态 + 可选 LLM 语义）**：先 24+ analyzer 模块秒级静态扫，再按需调 LLM 做意图/质量/安全发现，成本可控。
- 🔌 **MCP Server 模式 `skillspector mcp`**：把扫描本身暴露成 MCP 工具，让 Agent 在"装技能前先扫一遍"——安全左移到 agent 自身回路里。
- 📦 **SARIF 输出 + 批量扫描**：CI/CD 直接吃 SARIF；`contrib/batch_scan` 支持多 worker 语料级扫描。

---

## 项目全景

SkillSpector 回答一个越来越尖锐的问题：**"这个别人写的 Agent Skill 安全吗？"** 随着 Claude Code / Codex / Cursor 等大量安装第三方 SKILL.md，技能供应链成了新攻击面。NVIDIA 把它做成了一个**安装前闸门**：支持 git 仓库、URL、zip、本地目录、单文件输入，产出终端 / JSON / Markdown / **SARIF** 四种报告，并给出 0–100 风险分（51–80 HIGH、81–100 CRITICAL，均建议 DO NOT INSTALL）。

工程成熟度信号很强：`tests/` 下 unit / integration / nodes / provider 四类测试齐全，且内置 `malicious_skill` / `mcp_poisoned_tool` / `sdi` / `sqp` / `ssd` 等**对抗性 fixture**（覆盖语义注入、描述-行为 mismatch、MCP rug-pull 等），说明不是 PPT 项目。

---

## 核心架构

```
skill/zip/git/url
      │  resolve_input（含 ingest 上限，越界 fail-closed）
      ▼
 build_context ──► static_runner
                    ├─ static_patterns_*   (prompt_injection / data_exfiltration /
                    │                        privilege_escalation / excessive_agency /
                    │                        supply_chain / ssrf / tool_misuse / ...)
                    ├─ behavioral_ast / behavioral_taint_tracking
                    ├─ static_yara         (agent_skills / cryptominers / hacktools / webshells)
                    ├─ osv_client          (OSV.dev 实时 CVE 查询)
                    └─ mcp_*               (least_privilege / rug_pull / tool_poisoning)
      │
      ▼  （可选）meta_analyzer ── semantic_developer_intent /
      │                    semantic_quality_policy / semantic_security_discovery (LLM)
      ▼
 deduplicate ──► finalize_inspection_ledger ──► report (terminal/json/md/SARIF)
```

**关键设计 —— fail-closed 的 ingest 上限**：目录摄入有总大小/文件数上限，单文件分析有 `MAX_FILE_BYTES`（1 MB）下游上限；任一越界直接抛 `IngestLimitExceededError` 中止。这对"扫描不可信目录"这类供应链场景是必须的，避免扫描器自己被超大/恶意文件拖垮。

---

## 源码深度解读

### 1. 编排层 `src/skillspector/graph.py` + `langgraph.json`
用 LangGraph 把各节点串成有状态图。节点清单（来自 `src/skillspector/nodes/`）：`resolve_input` → `build_context` → `analyzers/static_runner` → `meta_analyzer`(可选) → `deduplicate` → `finalize_inspection_ledger` → `report`。每个 analyzer 是一个独立模块，新增规则 = 新增一个 `nodes/analyzers/*.py`，对扩展性友好。

### 2. Analyzer 分类（`nodes/analyzers/`）
- **静态模式** `static_patterns_*.py`：提示注入、数据外泄、权限提升、过度自主、供应链（curl|bash、未锁依赖）、SSRF、工具误用、anti_refusal、agent_snooping 等约 14 类。
- **行为分析** `behavioral_ast.py` / `behavioral_taint_tracking.py`：基于 AST 与污点追踪理解代码实际行为。
- **YARA** `static_yara.py` + `yara_rules/*.yar`：加密货币矿工、黑客工具、webshell、恶意软件签名。
- **CVE** `osv_client.py`：实时查 OSV.dev。
- **MCP 专属** `mcp_least_privilege` / `mcp_rug_pull` / `mcp_tool_poisoning`：针对"声明工具描述 ≠ 实际行为"、"装后再改权限"等 MCP 特有攻击。
- **LLM 语义** `semantic_*.py`：开发者意图、质量策略、安全发现，需配置 provider。

### 3. Provider 抽象 `src/skillspector/providers/`
覆盖 `openai` / `anthropic` / `anthropic_proxy` / `bedrock` / `nv_build`（默认，走 build.nvidia.com 的 DeepSeek）/ `claude_cli` / `codex_cli` / `gemini_cli`。`registry.py` 做凭证瀑布（active provider 失败回退 OPENAI_API_KEY）。CLI-API 双覆盖，本地 CLI 模式还免 API key。

### 4. 批量扫描 `contrib/batch_scan/`
`batch_scan.py` + `api_pool.py`（多 key 并发）+ `discovery.py` / `detection.py` / `annotation.py` / `gap_fill.py` / `reports.py`，支持 `--workers 20` 语料级扫描，用于大规模技能库体检。

---

## 应用场景与启发

- **技能市场/注册表**：发布前用 `skillspector scan --format sarif` 当 CI 闸门，SARIF 直接进 GitHub code scanning。
- **自托管 Agent 平台**：用 `skillspector mcp` 暴露 `scan_skill` 工具，让 Agent 在"自动装技能"前先扫一遍，实现**安全左移到 agent 回路**。
- **可借鉴的工程模式**：① 两阶段（静态快扫 + LLM 深扫）成本分层；② ingest 上限 fail-closed；③ analyzer 即插即换的模块架构；④ 多 provider 凭证瀑布。这套范式可复用到任何"扫描不可信第三方内容"的场景（插件、模板、prompt 库）。

---

## 社区口碑

- NVIDIA 背书 + OpenSSF Scorecard，信任基础扎实；星标从 8.6k（6 月底）涨到 14.2k（8 月初），增速在"Agent 安全"细分赛道居前。
- 测试与 fixture 体系完善，工程口碑偏"严肃工具"而非玩具。
- 短板：定位窄（只扫 Agent Skill/MCP），非通用 SAST；LLM 语义分析默认走 `nv_build`，社区更想要 Ollama/vLLM 等完全本地的后端（README 已留下 TODO）。

---

## 竞品对比

| | SkillSpector | 通用 SAST (Semgrep/CodeQL) | 提示注入扫描 (Lakera/Rebuff) | 镜像/CVE 扫描 (Trivy/Grype) |
|---|---|---|---|---|
| Agent Skill 专属规则 | ✅ 24+ 模块 | ❌ 通用代码漏洞 | ❌ 仅注入层 | ❌ |
| MCP 安全（rug-pull/最小权限） | ✅ | ❌ | ❌ | ❌ |
| SARIF / CI 集成 | ✅ | ✅ | ⚠️ | ✅ |
| LLM 语义评估 | ✅ 可选 | ❌ | ✅ | ❌ |
| NVIDIA 背书 + 供应链评分 | ✅ | 视工具 | ❌ | 视工具 |

**结论**：横向没有真正同赛道对手；它在"Agent 技能供应链"这个刚出现的垂直领域里是事实标准候选。

---

## 核心研判

| 维度 | 评价 |
|------|------|
| 创新性 | ⭐⭐⭐⭐ 首个把 Agent Skill + MCP 当一等公民的安全扫描器 |
| 工程成熟度 | ⭐⭐⭐⭐⭐ 测试/fixture/Scorecard/CHANGELOG 齐全 |
| 实用性 | ⭐⭐⭐⭐⭐ 一键 CLI、Docker、MCP、SARIF 四种落地姿势 |
| 生态前景 | ⭐⭐⭐⭐ Agent 越多，技能供应链安全越刚需 |

**研判**：随着 Agent 大量消费第三方技能，SkillSpector 大概率成为"安装前必扫"的基础设施。建议：技能开发者把它接进发布流水线；平台方用 MCP 模式做运行时闸门。当前唯一顾虑是 LLM 后端默认依赖 NVIDIA 云，完全离线场景需等社区补 Ollama/vLLM。

---

## 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `src/skillspector/graph.py` | LangGraph 工作流定义 |
| `langgraph.json` | 图配置 |
| `src/skillspector/nodes/analyzers/` | 全部 analyzer 模块 |
| `src/skillspector/cli.py` | CLI 入口（`scan` / `mcp`） |
| `src/skillspector/providers/` | LLM provider 注册表 |
| `contrib/batch_scan/batch_scan.py` | 语料级批量扫描 |
| `docs/DEVELOPMENT.md` | 架构与扩展指南 |
| `src/skillspector/yara_rules/` | YARA 恶意软件签名 |
| `tests/fixtures/` | 对抗性恶意/干净技能样本 |

---

*调研日期: 2026-08-05 ｜ 数据来源：GitHub API + 仓库文件树 + README（v2.5.x）*
