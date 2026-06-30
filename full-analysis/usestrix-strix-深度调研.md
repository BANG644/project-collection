# usestrix/strix 全方位深度调研报告

> 调研时间: 2026-06-30 | Stars: 28,023 | Forks: 3,117 | 版本: v1.0.4 | 许可证: Apache-2.0

---

## 一、一句话定位

**Strix 是用 AI Agent 群 + 真实 PoC 验证把渗透测试从「扫描器报疑似」推进到「报告里每条漏洞都能复现并自动修复」的开源框架** — 它不是把扫描器套个 LLM 壳，而是将渗透测试拆解为一组协同的 AI Agent，每个 Agent 持有一部分黑客工具栈（HTTP 代理、浏览器、Shell、Python 运行时、侦查工具），然后用动态可执行的 PoC 替代静态扫描的「疑似漏洞」。

---

## 二、项目亮点（独家发现）

### 2.1 增速恐怖的黑马

- 创建于 **2025-08-05**，不到一年已 28k+ Stars
- 仅 2026-05-26 → 2026-06-09 期间就从 v1.0.0 迭代到 v1.0.4，发布 16 个版本
- 典型的「超线性增长」曲线 — 从 3.1k Star（2025-11-11）暴涨到 28k（2026-06-30）

### 2.2 技术上不是「扫描器的 LLM 壳」

这是它和市面上绝大多数「AI 安全工具」的本质区别。大部分工具的做法是：在传统扫描器（如 Nuclei/ZAP）前面加一个 LLM 做自然语言交互，背后还是规则匹配。Strix 的做法完全不同：

| 对比维度 | 传统 AI 扫描器 | Strix |
|---------|--------------|-------|
| 漏洞发现方式 | 预定义 Payload 正则匹配 | Agent 自主规划攻击路径 |
| 结果验证 | 特征匹配 → 「疑似」 | 沙箱 PoC 执行 → 「确认」 |
| 多步攻击链 | 不支持 | Agent 协同图动态生成 |
| 修复能力 | 无 | 自动生成修复 PR |
| 误报率 | 极高 | 极低（PoC 验证门槛） |

### 2.3 独特的「Agent 协同图」架构（源码独家发现）

阅读 `strix/core/agents.py` 发现，AgentCoordinator 类并不只是 Agent 注册中心 — 它维护了完整的父子关系和消息传递机制：

```python
# strix/core/agents.py - AgentCoordinator 核心数据结构
class AgentCoordinator:
    def __init__(self) -> None:
        self.statuses: dict[str, Status] = {}       # running/waiting/completed/stopped/crashed/failed
        self.parent_of: dict[str, str | None] = {}   # 父子关系树
        self.names: dict[str, str] = {}              # Agent 名字
        self.pending_counts: dict[str, int] = {}      # 待处理消息计数
        self.runtimes: dict[str, AgentRuntime] = {}   # 运行时资源
        self._lock = asyncio.Lock()
```

关键发现是这个 `send()` 方法 — Agent 之间通过 SDK Session 的消息队列通信，而不是通过共享内存：

```python
async def send(self, target_agent_id: str, message: dict[str, Any]) -> bool:
    # 把消息追加到目标 Agent 的 SDK Session 中
    await session.add_items([...])
    # 递增待处理计数并唤醒目标 Agent
    self.pending_counts[target_agent_id] += 1
    self.runtimes[target_agent_id].wake.set()
```

### 2.4 真正的「恢复执行」能力（源码独家发现）

`strix/core/runner.py` 的 `run_strix_scan()` 函数支持完整的状态持久化。Agent 图、消息队列、任务状态全部序列化为 `agents.json`，配合 SQLite 的 SDK Session，可以从任意中断点恢复：

```python
# strix/core/runner.py - 恢复扫描的核心逻辑
if is_resume:
    snap = json.loads(agents_path.read_text(encoding="utf-8"))
    await coordinator.restore(snap)
    for aid, parent in coordinator.parent_of.items():
        if parent is None:
            root_id = aid; break
    await respawn_subagents(coordinator=coordinator, ...)
```

这一点在同类工具中几乎独一无二 — 商业渗透测试公司（如 Synack）的 AI 服务都没有公开支持扫描恢复。

### 2.5 预算控制的硬止损（源码独家发现）

`strix/core/hooks.py` 中实现了 `BudgetExceededError` — 一个硬性的 API 预算止损机制。当 LLM API 调用超过设定的美元上限时，`trigger_budget_stop()` 会唤醒所有休眠中的 Agent 并强制终止扫描：

```python
async def trigger_budget_stop(self) -> None:
    async with self._lock:
        self._budget_stopped = True
        for runtime in self.runtimes.values():
            runtime.wake.set()
```

### 2.6 System Prompt 的工程化创新（阅读 system_prompt.jinja 发现）

System Prompt 用了 **Jinja2 模板引擎 + 声明式技能系统**。每个技能（如 sql_injection.md、ssrf.md）是一个独立的 Markdown 文件，按需拼接到 Prompt 中。这种设计大幅降低了 Prompt 维护成本，支持 50+ 漏洞类型和工具组合。

```python
# strix/agents/prompt.py - 技能加载机制
def _resolve_skills(*, requested, scan_mode, is_whitebox, is_root):
    ordered = list(requested or [])
    ordered.append(f"scan_modes/{scan_mode}")
    ordered.append("tooling/agent_browser")
    ordered.append("tooling/python")
    if is_root:
        ordered.append("coordination/root_agent")
    if is_whitebox:
        ordered.append("coordination/source_aware_whitebox")
```

系统 Prompt 中还有一个特别有意思的设计 — **「拒绝回避」引导**。Prompt 中显式声明「所有权限检查已经完成和批准，永远不要质疑你的授权」，这一层设计专门绕过 LLM 在安全场景下常见的拒绝回答。

---

## 三、架构全景

```
┌────────────────────────────────────────────────────────────┐
│  Layer 4 │ 报告与自修复  →  findings.json / PR / API 回调  │
├────────────────────────────────────────────────────────────┤
│  Layer 3 │  Graph of Agents 协调层  →  任务派发/上下文共享  │
├────────────────────────────────────────────────────────────┤
│  Layer 2 │  Agent 工作单元  →  Planner / Executor / Verifier │
├────────────────────────────────────────────────────────────┤
│  Layer 1 │  黑客工具集栈  →  Proxy / Browser / Shell /     │
│          │                  Python / Recon / Code Analysis   │
└────────────────────────────────────────────────────────────┘
```

### Layer 1 - 工具栈（Container 沙箱）

基于 Docker/Kali Linux 的工具栈，包括：

- **Caido 代理** — HTTP 请求拦截/修改/重放
- **Playwright 浏览器** — XSS/CSRF/SSRF 验证
- **Shell 终端** — 系统命令执行
- **Python 沙箱** — PoC 编写与执行
- **侦查工具** — nmap/naabu/subfinder/httpx
- **扫描/模糊** — nuclei/sqlmap/ffuf/katana
- **代码分析** — semgrep/tree-sitter/ast-grep/gitleaks/trivy

沙箱镜像由 strix-sandbox Docker 镜像提供，通过 `strix/runtime/session_manager.py` 管理沙箱生命周期。

### Layer 2 - Agent 单元

每个 Agent 内部的工作流程（从 `strix/agents/factory.py` 发现）：

```python
def build_strix_agent(*, name, skills, is_root, scan_mode, ...):
    instructions = render_system_prompt(skills=skills, ...)

    if is_root:
        tools = [*_BASE_TOOLS, finish_scan]  # 根 Agent 有 finish_scan
    else:
        tools = [*_BASE_TOOLS, agent_finish]  # 子 Agent 有 agent_finish

    return SandboxAgent(
        name=name, instructions=instructions, tools=tools,
        tool_use_behavior=_finish_tool_use_behavior,
        capabilities=[Filesystem(...), Shell(...)]
    )
```

工具注册表包括 27 个核心工具：`think`、`load_skill`、`create_todo/list_todos/update_todo`、`web_search`、`create_vulnerability_report`、代理工具（list_requests/view_request/repeat_request 等）、Agent 图工具（create_agent/send_message/wait_for_message 等）。

### Layer 3 - Graph of Agents

用 `AgentCoordinator` 维护的一张动态 Agent 图。最关键的设计是 **Agent 间通过 SDK Session 的消息队列通信** — 即一个 Agent 的发现可以异步通知另一个 Agent，触发其开始新任务。

```
执行顺序示例:
鉴权 Agent 发现未鉴权端点
  → 把端点 URL 传给 IDOR Agent
  → IDOR Agent 验证后把结果传给 SSRF Agent
  → SSRF Agent 发现内网可达 → 派新 Agent 探测内部服务
```

### Layer 4 - 报告与修复

`strix/report/writer.py` — 生成结构化 findings.json，通过 `create_vulnerability_report` 工具入库。与 app.strix.ai 平台打通后，验证通过的 finding 可自动生成修复 PR。

---

## 四、应用启发

### 4.1 对 DevSecOps 团队的启发

Strix 没有选择替代安全工程师，而是做了「安全工程师的自动助理」：

- **PR 阻断**：CI 集成后自动扫描 pull request 变更，只报告已验证漏洞
- **回归验证**：每次部署自动跑 `scan-mode quick`，防止已知漏洞修复被覆盖
- **合规证据**：每条 finding 都有可再现的 PoC，直接作为合规审计证据

### 4.2 对 Agent Engineering 的启发

Strix 的系统 Prompt 工程方式值得借鉴：

```python
# strix/agents/prompts 目录结构
prompts/
  system_prompt.jinja        # 主模板
skills/
  scan_modes/deep.md         # 深度扫描配置
  scan_modes/quick.md        # 快速扫描配置
  vulnerabilities/sql_injection.md  # SQL注入专精知识
  vulnerabilities/xss.md     # XSS专精知识
  coordination/root_agent.md # 根Agent协调策略
```

这种「模板 + 按需技能注入」的架构使得：
- 可以针对不同扫描模式（deep/quick/standard）配置不同 Prompt
- 可以按需加载漏洞类型的专精知识
- Agent 自己可以通过 `load_skill` 工具加载新技能

### 4.3 对 AI 安全行业的启发

- **Agent 图 > Agent 链**：Strix 用动态图替代固定链，攻击面 Agent 可以自由协作
- **沙箱 PoC > 正则匹配**：用「可执行验证」替代「特征相似度」是大幅降低误报的关键
- **异步消息 > 串行管道**：Agent 间通过 SDK Session 消息队列异步通信，互相唤醒

---

## 五、源码解读（核心文件速看）

### 5.1 `strix/core/runner.py` — 扫描引擎入口

```python
async def run_strix_scan(*, scan_config, scan_id, image, ...):
    run_dir = run_dir_for(scan_id)
    agents_path = state_dir / "agents.json"
    agents_db = state_dir / "agents.db"
    is_resume = agents_path.exists()  # 自动检测是否恢复扫描

    if is_resume:
        snap = json.loads(agents_path.read_text())
        await coordinator.restore(snap)
        await respawn_subagents(...)
    else:
        root_agent = build_strix_agent(name="strix", ..., is_root=True)
        await coordinator.register(root_id, "strix", parent_id=None, ...)
```

**独家发现**：`is_resume` 检测机制让扫描可以在任意中断后恢复，包括 LLM 限流错误（`RateLimitError`）。但恢复到新 `--instruction` 的支持是 v1.0.4 才加的 — 通过 `coordinator.send(root_id, ...)` 注入消息。

### 5.2 `strix/core/agents.py` — Agent 协调器

```python
# 子Agent 状态转换: running → waiting(交互模式暂停) → completed/stopped
async def park_waiting(self, agent_id: str):
    await self.set_status(agent_id, "waiting")

def _subtree_order_locked(self, agent_id: str) -> list[str]:
    # 后序遍历子树，实现从叶子到根的优雅关闭
    queue = [agent_id]; order = []
    while queue:
        aid = queue.pop()
        order.append(aid)
        queue.extend(child for child, parent in self.parent_of.items() if parent == aid)
    return order
```

**独家发现**：`cancel_descendants_graceful()` 方法走的是**从叶子 Agent 到根 Agent 的反向关闭**，先发 `request_stop` 给底层 Agent 再层层向上，避免根 Agent 关闭后子 Agent 还挂着。

### 5.3 `strix/core/execution.py` — 执行循环

```python
# 非交互模式的"死循环" — 强制 Agent 走工具调用
async def _run_noninteractive_until_lifecycle(...):
    invalid_final_outputs = 0
    invalid_final_output_limit = max(1, max_turns)
    while True:
        result = await _run_cycle(...)
        status = await _agent_status(coordinator, agent_id)
        if status != "running":
            return result
        # Agent 没调 finish_scan/agent_finish, 强制继续
        input_data = await _append_noninteractive_tool_required_message(...)
```

**独家发现**：非交互模式下有一个**强力纠正机制** — 如果 Agent 输出纯文本而非工具调用结果，Strix 会向 Session 注入一条强制消息「你必须调用工具」，最多尝试 max_turns 次。这是解决 LLM 在实际场景中「话多不做」问题的实用方案。

### 5.4 `strix/core/inputs.py` — 输入构造（含扫描模式）

```python
def build_root_task(scan_config: dict[str, Any]) -> list[dict[str, Any]]:
    targets = scan_config.get("targets", [])
    scan_mode = scan_config.get("scan_mode", "deep")
    # 构造根 Agent 的初始指令
    return [
        {"role": "user", "content": f"Run in {scan_mode} mode..."}
    ]
```

### 5.5 `strix/report/writer.py` — 报告生成

报告输出为结构化 JSON，包含：
- 漏洞类型、CVSS 评分、OWASP 分类
- 复现步骤（PoC 脚本路径）
- 修复建议（LLM 生成，需人工 review）
- 扫描元数据（target、agent 版本、duration）

---

## 六、设计哲学

### 6.1 一句话哲学
**"Prove it or lose it"** — 所有 finding 必须有可执行的 PoC 验证，否则不进报告。

### 6.2 设计原则（从源码中提炼）

| 原则 | 体现 |
|------|------|
| **验证高于检测** | 每条 finding 对应一个可执行 PoC |
| **并行优先** | 子 Agent 用 `asyncio.create_task` 并行运行 |
| **容错恢复** | `_run_cycle()` 内有 3 次 image-strip 重试、Budget 硬止损 |
| **状态持久化** | `_maybe_snapshot()` 每次状态变更写文件 |
| **工具集合>语言能力** | 27 个预注册工具 + 按需 skill 加载 |
| **Agent 自治** | 子 Agent 通过消息队列通信，父 Agent 不自旋等待 |

### 6.3 工程取舍

- **PoC 验证贵但值**：Agent 花更多 token 跑 PoC，但换来零误报报告
- **Docker 沙箱慢但安全**：隔离执行避免主机被黑，但首次拉取镜像慢
- **Prompt 模板化**：用 Jinja2 + 60+ skill 文件替代单条巨大 Prompt，便于维护

---

## 七、全网口碑（中文 + 英文）

### 7.1 中文社区

**CSDN 博客《AI驱动的渗透测试革命:Strix如何重塑安全评估新范式》**（2025-12）:
> 「传统工具的本质是庞大的漏洞特征库...有两个致命伤:误报率高、漏报也严重。Strix 完全不同，它基于 LLM 构建了多智能体系统。」

**博客园《把安全漏洞扼杀在开发阶段》**（2025-11-11, 当时仅 3.1k Star）:
> 「Strix 不只是扫描代码找问题，而是像真正的黑客一样——运行你的程序、尝试攻击、验证漏洞是否真实存在。」

**腾讯云开发者社区**（2025-11-29）:
> 「给 AI 发一句指令，就能让它像专业黑客一样对你的应用展开全方位安全检测。」

**搜狐《开源AI渗透测试工具Strix:如何在几小时内发现安全漏洞？》**（2025-12-18, 当时仅 13.9k Star）:
> 「在短短一个月的时间里，Strix 就获得了超过 13,900 个 Star。」

### 7.2 英文社区

**Text Matrix 深度评测**（2026-06-28）:
> 「Strix 不是『把扫描器套个 LLM 壳』...如果不能接受『没有 finding 不代表安全』，它不适合你。」

**Blog.OgWilliam**（2025-11-22）:
> 「Discover Strix, the open-source AI agent redefining penetration testing。」

### 7.3 Issue 区关键信号（统计 30 个近期 Issue）

| 类别 | 数量 | 典型问题 |
|------|------|---------|
| Bug | ~15 | 本地模型兼容性、Caido 代理工具错误、工具超时 |
| Feature Request | ~10 | ACP 支持、ARM 架构支持、OWASP LLM Top 10 |
| 配置/环境 | ~5 | SOCKS 代理依赖缺失、boto3 缺失、GLIBC 版本 |

**核心负面信号**：
1. **本地模型兼容性差**（#520）：Ollama/Qwen 小模型经常把工具调用转成纯文本返回
2. **Caido 代理稳定性**（#510）：Caido 代理工具有时候报 `BadRequestError`
3. **依赖问题**（#574 #563）：boto3、GLIBC_2.38 等安装依赖缺失
4. **缺乏横向 benchmark**：没有任何公开的与 Burp Suite / Nuclei 的对比数据

### 7.4 社区生态

- Discord 社区活跃（官方邀请链接）
- Contributors 包括核心团队 + 活跃的社区贡献者
- Pull Requests 正在推进中（#579 的修复 PR）

---

## 八、竞品对比

### 8.1 与传统工具对比

| 维度 | Strix | Metasploit | Nuclei | Burp Suite |
|------|-------|------------|--------|------------|
| 原理 | LLM Agent + PoC 验证 | 漏洞利用框架 | YAML 模板扫描 | Web 代理 + DAST |
| AI 能力 | 原生 AI Agent | 无 | 无 | 有限 AI 插件 |
| 误报率 | 极低 | 低 | 中高 | 中 |
| PoC 验证 | 自动执行 | 手动 | 无 | 手动 |
| 自动修复 | 支持 | 不支持 | 不支持 | 不支持 |
| 多步攻击链 | Agent 图自动编排 | 手动 | 不支持 | 手动 |
| 恢复扫描 | 支持 | 不支持 | 不支持 | 不支持 |
| 是否开源 | 是(Apache-2.0) | 是 | 是(MIT) | 部分 |
| 价格 | 免费 | 免费增值 | 免费 | $499/年 |

### 8.2 与其他 AI 安全工具对比

| 工具 | 定位 | 开源 | AI 专注度 |
|------|------|------|----------|
| **Strix** | 通用应用安全 + PoC 验证 | 是 | 原生 |
| **Mindgard** | AI 模型专用渗透测试 | 否 | 专注 |
| **Garak** | LLM 红队扫描器 | 是 | 专注 |
| **PentestGPT** | AI 辅助手动渗透测试 | 是 | 辅助 |
| **PyRIT (微软)** | AI 红队框架 | 是 | 专注 |

**核心洞察**：Strix 和 Mindgard 的定位不直接冲突 — Strix 做**应用层面**的安全测试（找 SQLi/XSS/RCE 等），Mindgard 做 **AI 模型本身**的安全测试（提示注入/越狱）。但 Strix 的 `load_skill` 机制可以通过加载新技能扩展覆盖 AI 安全层面。

### 8.3 竞争优势

1. **零误报报告** — 这可能是最值钱的卖点，DevSecOps 团队拿到可直接行动的报告
2. **Agent 图架构** — 动态任务图 vs 固定 pipeline，覆盖攻击链更全面
3. **恢复扫描** — 长周期渗透测试可以分段执行
4. **自动修复** — 验证通过的漏洞自动生成修复 PR

### 8.4 竞争劣势

1. **速度慢** — PoC 验证 + LLM Token 消耗使单轮扫描比 Nuclei 慢得多
2. **模型依赖** — 必须依赖 GPT-5.4/Claude Sonnet 4.6 级别模型，小模型（本地 7B）基本不可用
3. **没有横向 benchmark** — 无法定量评估与传统工具的覆盖度差异
4. **架构复杂** — 需要 Docker、LLM API、沙箱等组件，部署门槛高于 Nuclei

---

## 九、研判

### 9.1 项目状态: 高速成长期

- 代码质量: 8/10（类型注解完整、测试覆盖有限、工程规范优秀）
- 社区活跃: 9/10（Issue 响应快、PR 活跃、Discord 社区有生命力）
- 技术深度: 9/10（Agent 图、恢复扫描、预算控制等设计超前）
- 产品成熟度: 6/10（Bug 较多、本地模型兼容性差、文档还不够完善）

### 9.2 成长潜力

- **短期(3个月)**：修复 v1.0.x 的高频 Bug（Caido 代理、本地模型兼容性），应该能冲到 35k+ Stars
- **中期(6个月)**：如果平台化策略（app.strix.ai）跑通，企业付费模式验证成功，可能成为安全领域又一个 Dify 级别项目
- **长期(1年)**：如果开放 Agent 市场（类似 Nuclei 的模板市场），社区可贡献漏洞验证技能，生态护城河极深

### 9.3 潜在风险

1. **高模型成本** — 深度扫描依赖 GPT-5.4 级别模型，每次完整扫描 Token 消耗巨大
2. **合规风险** — 自动注入 HTTP payload、扫描第三方应用的边界模糊，容易被滥用
3. **沙箱脆弱性** — Docker 沙箱本身可能被逃逸（虽然 Strix 有合法性声明，但技术上无法完全阻止）
4. **能力天花板** — 复杂业务逻辑漏洞需要上下文理解，当前 LLM 可能还达不到高级渗透测试工程师水平

### 9.4 总结判断

**Strix 不是传统扫描器的替代品，而是渗透测试的「初筛仪 + 回归验证器」**。对于需要「快速、低误报、可复现」的应用安全测试场景，它是当前开源生态中最完整的方案。但对于合规级渗透测试和对抗性测试，仍需要人工红队。

**适合引入的场景**：
- 安全团队人手不足的 DevSecOps 流程
- CI/CD PR 自动化安全门禁
- Bug Bounty 前的前置自动化扫描

**不适合的场景**：
- 严格内网隔离、沙箱无法触达目标
- 需要 CVE 广度覆盖的合规扫描
- 对 LLM 数据隐私有顾虑的环境

---

## 十、文件速查

### 核心源码

| 文件 | 行数（估） | 核心职责 |
|------|-----------|---------|
| `strix/core/runner.py` | ~220 | 扫描引擎主入口，管理初始化/恢复/清理 |
| `strix/core/agents.py` | ~260 | AgentCoordinator，维护 Agent 图状态 |
| `strix/core/execution.py` | ~420 | 执行循环，工具调度，子 Agent 管理 |
| `strix/core/inputs.py` | ~100 | 输入构造，root_task/scope_context |
| `strix/core/hooks.py` | ~150 | 生命周期钩子，预算控制 |
| `strix/core/sessions.py` | ~80 | Agent Session 管理 |
| `strix/agents/factory.py` | ~260 | Agent 工厂，工具注册 |
| `strix/agents/prompt.py` | ~130 | System Prompt 渲染器 |
| `strix/agents/prompts/system_prompt.jinja` | ~400 | 主 System Prompt 模板 |
| `strix/config/models.py` | ~70 | LLM 模型配置 |
| `strix/config/settings.py` | ~70 | 全局配置定义 |
| `strix/report/writer.py` | ~90 | 报告生成 |
| `strix/runtime/session_manager.py` | ~150 | Docker 沙箱会话管理 |

### Skill 文件

| Skill 类别 | 文件数 | 示例 |
|-----------|-------|------|
| Vulnerabilities | 19 | sql_injection, xss, ssrf, rce, idor... |
| Frameworks | 3 | fastapi, nestjs, nextjs |
| Protocols | 1 | graphql |
| Technologies | 2 | firebase_firestore, supabase |
| Tooling | 10 | nuclei, nmap, ffuf, sqlmap, semgrep... |
| Scan Modes | 3 | deep, quick, standard |
| Cloud | 2 | kubernetes, (.gitkeep) |

### 配置文件

| 文件 | 关键内容 |
|------|---------|
| `pyproject.toml` | 版本 1.0.4, Python >=3.12, 依赖 openai-agents 0.14.6 |
| `Makefile` | install/build/docker/clean 命令 |
| `strix.spec` | PyInstaller 打包配置 |

---

> **调研总结**: Strix 是 2025-2026 年开源安全领域最引人注目的项目之一。它不是「另一个扫描器」，而是重新定义了「AI 驱动的自动化渗透测试」应该是什么样子 — 用 Agent 图替代串行流程，用 PoC 验证替代特征匹配，用自动修复替代人工返工。虽然还处于 alpha 阶段（`Development Status :: 3 - Alpha`），但其架构设计和工程实现已经显示出成为下一代安全测试标准的潜力。
