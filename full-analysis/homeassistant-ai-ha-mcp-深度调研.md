# homeassistant-ai/ha-mcp 深度调研

> 调研日期：2026-11-10 ｜ 编号：#580 ｜ Stars：5,792 ｜ License：MIT ｜ 语言：Python 3.13（内置 vendored FastMCP） ｜ 组织：`homeassistant-ai`（社区组织维护，非官方但属 HA 生态）

---

## 一、项目定位（一句话）

`homeassistant-ai/ha-mcp` 是 Home Assistant 社区维护（非官方、属 `homeassistant-ai` 组织）的 MCP 服务器，让 Claude、ChatGPT、Gemini 等 AI 助手用自然语言**配置、构建、调试**整个 Home Assistant 实例——不只是控制设备，还能创建/修改自动化、脚本、场景、仪表盘、备份，并管理集成与 HACS。

---

## 二、项目亮点（差异化，开篇呈现）

1. **最丰富的 HA MCP 工具集**：87 个工具横跨 24 个类别（设备控制、自动化、仪表盘、备份、历史、相机快照、能源、Add-on、HACS、注册表…），远超 HA 官方内置 MCP Server（仅暴露 Assist 已暴露的实体）。
2. **进程内服务器（in-process server）**：作为 HA 自定义组件运行，直接在 HA 进程内拉起 FastMCP 服务，全安装类型（OS / Supervised / Container / Core）功能对等，免单独运维进程与独立凭据生命周期。
3. **工具安全策略（Tool Security Policies）**：`PolicyMiddleware` 在 `tools/call` 层对敏感操作做审批闸门，支持「按工具要求人工 approval」「只读模式」「逐工具启停」，且 **fail-closed**。
4. **Agent Skills 系统**：以 MCP 资源形式下发领域最佳实践指南（如何写自动化、选 helper、安全重构配置），是其区别于纯控制类服务器的差异化能力。
5. **四种部署形态 + 15+ 客户端向导**：自定义组件（推荐）/ Add-on / Docker / PyPI·uvx stdio，配 Setup Wizard 覆盖 Claude Code、Gemini CLI、ChatGPT、Open WebUI、VSCode、Cursor 等。

---

## 三、核心架构（克制代码量）

整体分两层：

- `src/ha_mcp/`：核心 FastMCP 服务器包（含一份 vendored FastMCP 于 `src/ha_mcp/_vendor/fastmcp/`）。
- `custom_components/ha_mcp_tools/`：HA 自定义组件，把服务器以**进程内**方式跑起来，并暴露设置面板 / 文件 YAML 服务等第二类入口。

关键子系统：

- **进程内生命周期管理**（`embedded_server.py`）：`EmbeddedServerManager` 在独立线程 + 独立 asyncio loop 上启动服务器，避免重工具阻塞 HA 主事件循环；管理员长效 token 经 `ha_mcp.config.set_embedded_connection` **仅内存传递**，绝不进 `os.environ`。
- **策略闸门**（`policy/`）：`PolicyMiddleware`（FastMCP `on_call_tool` 中间件）→ `evaluator.evaluate()`（纯函数，返回 `ALLOW` / `REQUIRE_APPROVAL`）→ `ApprovalQueue`（待审批队列，`compute_args_hash` 去重）→ `mrtr`（多轮审批应答）。
- **逐工具暴露控制**（`llm_exposure.py`）：`LlmExposureMiddleware` 在 `tools/list` 的每个条目 `_meta.ha_mcp` 中**带内**盖章 `{llm_api_exposed, pinned, params, policy}`，组件据此过滤对话代理可见的工具，零额外往返；对危险集合（beta / dev / restart / reload / backup / `ha_manage_security_policy`）默认 deny-by-default。
- **自动备份护栏**（`backup_*` 系列）：破坏性写操作前自动备份；`redaction.py` / `read_only.py` 做脱敏与只读模式。

---

## 四、应用场景与启发

- **场景**：让 AI 帮家庭成员「在日落时打开门廊灯」「给仪表盘加天气卡」「排查某条自动化为什么没触发（读 trace）」「在改配置前先自动备份」。
- **启发（给同类需求）**：
  1. *本地优先 + 进程内架构*：把 AI 服务嵌进宿主进程、用独立线程 + 独立 loop 隔离，是「大模型能力接入既有长驻守护进程」的稳健范式——既省一个常驻进程，又避免 AI 调用拖垮主循环。
  2. *密钥绝不进环境变量*：用「内存内注入配置对象」而非 `os.environ`，是对抗凭据泄露的硬约束，值得任何 AI-接入型组件借鉴。
  3. *策略即数据 + fail-closed*：`Policy`/`Rule`/`Predicate` 用 Pydantic 建模、JSON 持久化、匹配即闸门，且任何解析异常都 fail-closed（如 `evaluator` 遇 `RecursionError` 直接拒呼）——把「降级即放行」的陷阱显式堵死。
  4. *带内元数据驱动 UI*：把服务端真实 gating 状态随 `tools/list` 一并下发给前端，避免「客户端配置」与「服务端实际策略」漂移。

---

## 五、源码深度解读

### 1. 进程内服务器生命周期 — `custom_components/ha_mcp_tools/embedded_server.py`

`EmbeddedServerManager` 负责人/生命周期：确保 `ha-mcp` 包可导入（必要时按 options-flow 的 pip-spec 运行时重装），把管理员长效 token 经 loopback 交给 HA core（REST+WS），在专属线程起服务。文档字符串明确：

```python
# the admin token can never be read from the shared HA process environment …
# handed to ha-mcp **in memory** via ha_mcp.config.set_embedded_connection
# — never through os.environ
# runs the server on a dedicated thread with its own asyncio loop —
# a heavy tool can never stall HA's event loop
```

就绪探针用「模块落地进度 + 阶段推进」而非固定 90s 死线（修复 HA Green 冷导入数分钟导致的僵尸线程 / 端口抢占级联，issue #1904）。

### 2. 工具调用策略闸门 — `src/ha_mcp/policy/middleware.py` + `evaluator.py`

`PolicyMiddleware(Middleware)` 在每次 `tools/call` 前用 `policy_provider()` 取当前 `Policy`，经 `ApprovalQueue` 闸门；代理元工具（`ha_search_tools` 等）与队列管理调用豁免。核心判定在 `evaluator.evaluate()`——**纯函数、无 I/O 无状态**，返回 `Verdict.ALLOW` 或 `Verdict.REQUIRE_APPROVAL`：

```python
class Verdict(StrEnum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"

def evaluate(...) -> Verdict: ...
```

其 `normalize_stringified_containers` 会先修复客户端把 JSON 容器当字符串传的退化形态（Claude Desktop stdio 已知问题），**但若深层嵌套 INPUT 触发 `RecursionError` 则故意不吞掉、交由 `on_call_tool` fail-closed 拒呼**——作者注释直陈这是避免「降级即放行」的同一类错误。

`policy/model.py` 定义 `Policy`/`Rule`/`Predicate`：`PredicateOp` 支持 `eq/neq/in/not_in/regex/contains/exists/gt/lt`；`RuleEffect` 为 `require_approval`（默认，匹配则闸门、其余放行）或 `allow`（反之）。`POLICY_SCHEMA_VERSION=2` 表示 ANY 匹配语义（每条 UI 条件独立成 rule，谓词间 AND）。模型用 `field_validator` 在保存时即拒绝非法正则 / 空值，确保「坏策略文件 → 每条调用都被拒」这类最坏情况不会发生（除非解析本身崩溃，那也 fail-closed）。

### 3. 逐工具暴露与带内盖章 — `src/ha_mcp/llm_exposure.py`

`LlmExposureMiddleware` 给 `tools/list` 每个条目盖 `_meta.ha_mcp = {"llm_api_exposed": bool, "pinned": bool, "params": str, "policy": {...}}`。组件作为「又一个 loopback MCP 客户端」直接据此过滤，单一事实源随 `tools/list` 在带内流动，2s 合并缓存，设置 UI 改动在代理下一轮对话即生效、无需重启：

```python
META_NAMESPACE = "ha_mcp"
META_EXPOSED_KEY = "llm_api_exposed"
META_POLICY_KEY = "policy"   # 实际 gating 状态：配置 flag + 活跃中间件 + 规则数 + 部署模式
```

`LLM_API_DEFAULT_OFF_TOOLS` 冻结 `ha_restart` / `ha_reload_core` / `ha_manage_backup` / `ha_manage_security_policy` 等运维高危工具默认对对话代理隐藏，用户需显式开启。

（工具本体位于 `src/ha_mcp/tools/*.py`，约百个模块，由 `server.py` 的 `HomeAssistantSmartMCPServer` 懒加载发现——启动时只发现模块、首次调用才导入，缩短冷启动。）

---

## 六、全网口碑

- **ChatForest（IoT/嵌入式 MCP 综述，2026-08 再审计）**：称其为「最丰富功能的智能家居 MCP 服务器」「整个 IoT 品类发布节奏最激进」；星数 2.5K→3.3K→4.3K→（现 5.8K）持续高增，窗口内 5 个主版本；Agent Skills 是差异化点。
- **AgentRank**：评分 93.13（家居自动化品类最高之一），「clear leader，本类无竞争，从这里开始」；18 贡献者、积极 issue 管理。
- **AgentIndex**：状态 Active，近 90 天 100+ 提交、16 次发布；盛赞 Read Only / 逐工具启停 / 审批策略 / 自动备份等安全设计；也直陈权衡——非官方、84 个带写权限的工具「改得动你家的设置」，建议在信任前先开只读或审批策略。
- **负面 / 中立信号（mrkeyoor 实测）**：沙箱里 pytest 出现 200 个 collection/setup 错误（asyncio marker 未配置），未能在其环境复现真实 HA 部署；README 快速开始指向的版本（v9.0.0+）有时超前于 latest-release 端点返回的版本，存在文档漂移；`/readonly` URL 与常规端点**共享同一凭据**（只读只是行为限制，不是独立受限凭证）。

---

## 七、竞品对比 + 核心研判

| 项目 | 语言/许可 | 工具数 | 定位 | 状态 |
|---|---|---|---|---|
| **homeassistant-ai/ha-mcp** | Python/MIT | 87 | 配置·构建·调试全家桶，进程内+多种部署 | 活跃（社区组织维护） |
| Home Assistant 内置 MCP Server | Python/Apache-2.0 | 有限 | 仅暴露 Assist 已暴露的实体，偏只读控制 | 官方、随 HA core 发货 |
| allenporter/mcp-server-home-assistant | Python | — | 早期社区服务器 | **已归档**，已并入 HA Core（即上面的内置集成） |
| tevonsb/homeassistant-mcp | TS/Apache-2.0 | 20+ | 原始社区服务器，SSE 实时推送 | 慢维护 |
| voska/hass-mcp | Python | — | 第三选项 | 较小 |
| Coolver/home-assistant-vibecode-agent | Python | — | 开发期 IDE 辅助（写/调自动化） | 互补 |

**核心研判**：

1. **它是当前 HA×AI 控制面的事实标准候选**，生态位清晰：官方内置集成只解决「用 AI 控设备」，而 ha-mcp 把「配置/构建/调试」也纳入，且安全护栏（策略、只读、自动备份、逐工具暴露）明显更完整。
2. **风险点在「信任边界」**：84+ 个带写权限的工具意味着 AI 能改写你的家；尽管有审批策略，但 `/readonly` 与常规端点共享凭据、且策略文件若被破坏会 fail-closed（好），可一旦放行即改动真实家居——生产自用建议默认开只读 + 关键操作审批。
3. **工程成熟度高于多数 MCP 服务器**：进程内隔离、密钥内存注入、策略 fail-closed、带内元数据——这些不是 demo 级代码，反映出 HA 社区级工程水准；但第三方实测的测试集未跑通（沙箱 marker 问题）提示 CI / 本地复现门槛略高。
4. **与自建 MCP 服务的借鉴**：其「宿主进程内嵌 + 独立线程隔离 + 密钥内存注入 + 策略即数据且 fail-closed + 带内元数据驱动 UI」五件套，是任何「给既有长驻系统（数据库/ERP/工单/网管）接 AI 控制面」项目的可直接复用蓝图。

---

## 八、关键文件路径速查

- `src/ha_mcp/server.py` — `HomeAssistantSmartMCPServer`，懒加载工具注册
- `src/ha_mcp/tools/*.py` — 约百个工具模块（设备控制/自动化/备份/蓝图/配置流…）
- `src/ha_mcp/policy/middleware.py` — `PolicyMiddleware` 调用闸门
- `src/ha_mcp/policy/evaluator.py` — `evaluate()` 纯函数判定
- `src/ha_mcp/policy/model.py` — `Policy`/`Rule`/`Predicate` Pydantic 模型
- `src/ha_mcp/policy/approval_queue.py` — `ApprovalQueue` / `PendingApproval` / `compute_args_hash`
- `src/ha_mcp/llm_exposure.py` — `LlmExposureMiddleware` 带内盖章
- `src/ha_mcp/backup_*.py` — 破坏性写前自动备份
- `src/ha_mcp/redaction.py` / `read_only.py` — 脱敏 / 只读模式
- `custom_components/ha_mcp_tools/embedded_server.py` — `EmbeddedServerManager` 进程内生命周期
- `custom_components/ha_mcp_tools/websocket_api/` — 设置面板用的 HA WS 命令
- `custom_components/ha_mcp_tools/config_flow.py` — 安装向导 / 管理员账户选择
- `AGENTS.md` / `CLAUDE.md` / `SECURITY.md` — 贡献与安全威胁模型
