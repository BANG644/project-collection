# 🔬 Unclecheng-li/VulnClaw — 全方位深度调研

## 📌 一句话定位

**中文社区最完整的 AI 驱动渗透测试 CLI 工具** — 基于 LLM Agent + MCP 工具链 + 渗透 Skill 编排，自然语言输入即可自动完成信息收集 → 漏洞发现 → 漏洞利用 → 报告生成全流程。核心从 v0.4.0 起重构为"目标驱动求解引擎"（黑板图 + OODA 循环），结构上杜绝了固定轮数工作流的"原地打转"问题。

## ⭐ 项目亮点

1. **目标驱动求解（Solve Engine）取代固定轮数** — v0.4.0 重构的核心：将渗透测试建模为从 origin 向 goal 的 Fact/Intent 黑板图状态空间搜索，以"目标达成/探索前沿耗尽/安全预算"为终止条件，不再空跑 N 轮。这是同类 AI 渗透工具中罕见的架构设计
2. **证据级反幻觉闸门** — 所有工具输出（HTTP 响应体、`python_execute` 输出等）被录制为唯一可信证据，声称的 flag 必须逐字符出现在真实输出中才被采信。对弱模型尤其友好——DeepSeek/MiniMax 等开源模型不再凭空编造 flag
3. **13 个 LLM Provider 一键切换** — 从 OpenAI/GPT-4o 到 MiniMax-M3/DeepSeek-V4/GLM-4.7/Kimi-K2.6/豆包/百川/阶跃星辰/商汤/零一万物。LLM 不绑死在单一厂商
4. **极低调的 Docker 就绪** — 内置 Docker Compose + 开箱即用的 MCP 服务（fetch + memory），`docker compose up` 即可启动 Web UI
5. **21 个渗透 Skill + 180 个参考文档** — 7 核心 + 14 专项 Skill（含 CTF Web/Crypto/Misc、OSINT、AI/MCP 安全测试），SEO/GAARM/OWASP 方法论全覆盖

## 🏗️ 项目架构全景

### 架构分层

```
vulnclaw/
├── cli/                # CLI/TUI 入口
├── agent/              # Agent 核心（最重）
│   ├── solver.py       #   OODA 求解引擎（v0.4.0 新增）
│   ├── blackboard.py   #   Fact/Intent 黑板图
│   ├── reasoning_state.py  # 结构化推理状态
│   ├── reflexion.py    #   自适应反思引擎
│   └── recon_tools.py  #   v0.4.1 新增信息收集工具链
├── mcp/                # MCP 编排
│   ├── registry.py     #   服务注册
│   ├── lifecycle.py    #   生命周期管理
│   └── router.py       #   自然语言→工具路由
├── skills/             # 21 个渗透 Skill
│   ├── core/           # 7 核心 Skill
│   └── specialized/    # 14 专项 Skill
├── plugins/            # 漏洞检测插件体系（v0.4.0 新增）
├── kb/                 # 安全知识库
├── report/             # 报告生成器
├── config/             # Pydantic 配置
├── web/                # FastAPI Web UI
└── target_state/       # 目标状态继承
```

### 求解引擎 v0.4.0 核心重构

这是读懂 VulnClaw 最重要的模块。用 README 没有直接说的方式解释：

**固定轮数工作流（旧版，`session.engine=rounds`）：**
```
循环 N 轮：
  1. 提一个 action
  2. 执行工具
  3. 分析结果
  → 如果模型笨，可能 Round 3 还在看 Round 1 看过的页面
```

**目标驱动求解（新版，默认）：**
```
黑板图状态：
  - Fact: 已确认的事实（"目标是 example.com"、"端口 8080 开放"）
  - Intent: 待验证的探索方向（"测 SQL 注入"、"查 CVE-2024-xxx"）

OODA 循环：
  REASON → 读取全图，当前目标接近程度
  → 达成? / 提出新 Intent / 不提出
  → EXPLORE → 取一个 Intent → 工具执行 → 写回 Fact
  → 终止：目标达成 / 探索前沿耗尽 / 超预算

结构杜绝打转：
  "首页是登录框"一旦成为 Fact → Reason 不会再提"去看首页"
  → 而是提"测 SQL 注入"。每个 Intent 领取后标记 concluded/abandoned
```

### 证据闸门（核心代码，`solver.py` 简化）

```python
# 关键设计：所有工具输出写入 evidence_buffer
# explore() 结论中的 flag 必须与 evidence_buffer 文本逐字符匹配
# 不匹配 → 判定幻觉，丢弃，标记 [未验证]
# 完成闸门：Reason 声称"目标达成"时
#   若目标需要 flag 但 evidence 中未出现 → 拒绝完成、继续探索
```

### 自适应反思引擎（L0-L4 Payload 升级策略）

```
失败自动分类：
  - 环境限制（WAF/防火墙）
  - 路径错误（端点不存在）
  - 参数错误（payload 格式不对）
  - 信息不足（需要更多信息）

Payload 升级路径：
  L0: 原始 payload
  L1: URL 编码
  L2: 双写注释
  L3: Unicode/hex 编码
  L4: 多层混淆 / 换攻击面

Persistent 模式跨周期保留失败记忆（reflexion 引擎）
```

## 💡 应用场景与启发

### 典型使用场景

- **授权渗透测试**：`vulnclaw run target.com` 一键进入自动渗透，适合红队快速摸底
- **CTF 竞赛**：内置 CTF Web/Crypto/Misc 专项 Skill + War Stories（实战复盘记录），命令 `vulnclaw solve ctf.site --goal "拿到flag"`
- **安全教学**：TUI 工作台的"安全边界"配置（允许/禁止动作），适合教学环境安全演示
- **SRC 漏洞挖掘**：secknowledge-skill + 180 文档的 OWASP/AI/MCP 安全知识库
- **持续性红队**：`vulnclaw persistent target.com` 每周期 100 轮，最多 10 周期，自动生成增量报告

### 可借鉴的解决方案模式

1. **"状态空间搜索"取代"轮数工作流"** — 这是 VulnClaw 最有启发的一点。任何需要 Agent 持续探索的任务（渗透测试、漏洞扫描、数据采集）都可能受益于 Fact/Intent 黑板图模式——比固定轮数更鲁棒、不会空转
2. **证据闸门模式** — 所有 Agent 产出必须与工具实际输出交叉验证。这个模式适用于任何需要 Agent 精确报告结果的场景（财务分析、代码审查、学术研究）
3. **L0-L4 Payload 渐进升级** — 失败不是一次性的，而是分层升级策略。这是 Agent 弹性设计的模板

### 同类需求的可参考思路

如果你也在做"AI + 安全"类工具（或任何 AI 执行关键任务的工具）：

- **不要相信 Agent 的自我报告** — 证据闸门是必需品。Agent 会编造结果（LLM hallucination），必须用实际工具输出验证
- **把失败分类，而不是统一重试** — L0-L4 渐进策略比"重试 3 次"聪明多了。环境限制就换攻击面，参数错误就改 payload 格式
- **中文社区是一个差异化优势** — 中文 Issue 讨论（QQ 群 954402631）、中文 README、中文 war stories。VulnClaw 是少数深度拥抱中文安全社区的 AI 渗透工具

## 🧠 核心源码解读（克制代码量）

### 模块 1：solver.py — OODA 求解引擎（v0.4.0 核心）

```python
# 简化骨架：solve() 主循环
async def solve(self, goal: str):
    while steps < max_steps:
        # REASON: 读全图，判断下一步
        action = await self.reason(blackboard, goal)

        if action.type == "complete":
            if self.evidence_contains(goal_flag):
                return Verdict(success=True, ...)
            else:
                continue  # 拒绝假完成

        if action.type == "intent":
            intent = action.intent
            # EXPLORE: 执行探索
            evidence = await self.explore(intent)
            # 写回 Fact
            blackboard.add_fact(intent.target, evidence)
            intent.mark_concluded()

        if action.type == "stuck":
            return Verdict(success=False, ...)
```

关键设计：证据闸门 `evidence_contains()` 扫描所有录制输出，不是 Agent 自己说"拿到了"就算数。

### 模块 2：blackboard.py — Fact/Intent 黑板图

```python
# 简化骨架
class Fact:
    content: str          # 事实内容
    source: str           # 来源工具
    confidence: float     # 置信度

class Intent:
    target: str           # 探索目标
    status: str           # pending/concluded/abandoned
    evidence: list[str]   # 执行证据

class Blackboard:
    facts: dict[str, Fact]
    intents: dict[str, Intent]
    concluded: set[str]   # 已完成的 Intent（防止重复）
```

### 模块 3：reflexion.py — L0-L4 自适应升级

```python
# 简化骨架
LEVELS = ["raw", "url_encode", "double_comment", "unicode_hex", "multi_obfuscation"]

class ReflexionEngine:
    def classify_failure(self, error: str) -> str:
        if "WAF" in error or "blocked" in error:
            return "env_limit"
        if "404" in error or "not found" in error:
            return "path_error"
        if "syntax" in error or "invalid" in error:
            return "param_error"
        return "info_missing"

    def escalate(self, failure_type: str, current_level: int):
        if current_level < 4:
            return LEVELS[current_level + 1]
        return "switch_attack_surface"
```

## 📐 架构决策与设计哲学

### v0.4.0 — "求解引擎"取代"工作流"

这是最核心的设计转变。从 15 行配置可开关：

```
session.engine = solve    # 目标驱动（默认）
# session.engine = rounds  # 旧固定轮数（回退选项）
```

作者在 README 中明确说：**"为什么结构上杜绝打转"**——这不是调参问题，而是架构问题。一旦一个 Fact 被确认，Reason 不会重复提出同一个方向。

### 中文生态定位

VulnClaw 是目前唯一一个：
- 所有 LLM Provider 都有中文厂商（MiniMax/DeepSeek/智谱/千问/豆包）
- 中文 Issue 活跃，"报告在哪里看？"（Issue #5）、"工具被约束了"（Issue #45）显示真实的用户使用反馈
- 没有强调"出海"而是深耕中文安全社区

## 🌐 全网口碑画像

### 好评共识

| 来源 | 评价 |
|------|------|
| TxtMix 技术博客 | "把渗透测试建模为黑板图 + OODA 状态空间搜索" — 架构设计受认可 |
| CSDN（2026-04） | "让安全测试像聊天一样简单" — 入门门槛低是最大卖点 |
| CSDN 深度评测（2026-04） | "传统自动化工具依赖预定义脚本，缺乏动态调整能力" — VulnClaw 的 LLM 驱动能力被认可 |
| GitHub | 1.1k Star / 168 Fork / 活跃的 Issue 讨论（8 个 open，其中多个有讨论） |

### 差评共识 & 踩坑高发区

- **弱模型能力边界** — Issue #3 讨论 DeepSeek V4-Pro 的 Max 模式和 1M 上下文激活问题，说明国产模型对接有适配成本
- **约束漂移** — Issue #4 "渗透限制在随着 round 次数增加约束力不断下降" — 长会话中 Agent 可能逐渐偏离安全边界
- **工具冲突** — Issue #45 "工具被约束了" — 动作约束有时误拦截合法工具调用

### 活跃的社区互动

作者响应积极（v0.4.1 已修复 #45 工具约束问题）。Issue 分为两类：功能请求（#25 动态注入提示词、#39 登录后内容测试）和 Bug 报告——反映出真实用户的使用场景。

## ⚔️ 竞品对比

| 维度 | VulnClaw | PentestGPT | burpgpt (PortSwigger) |
|------|---------|-----------|---------------------|
| **核心定位** | 独立 CLI AI 渗透测试 Agent | ChatGPT 辅助渗透 | Burp Suite 插件 |
| **语言** | Python（原生）| 提示词集 | Java（插件）|
| **MCP** | ✅ 内置 4 服务（fetch/memory/chrome/burp）| ❌ | ❌ |
| **LLM 提供商** | 13 个（含 10 个中文厂商）| 限 OpenAI | 限 OpenAI |
| **求解引擎** | 目标驱动（Fact/Intent OODA）| 固定轮数 | 固定轮数 |
| **反幻觉** | ✅ 证据闸门 | ❌ | ❌ |
| **PoC 生成** | ✅ 结构化 + Python | ❌ | ❌ |
| **Web UI** | ✅ FastAPI | ❌ | ✅ Burp 原生 |
| **中文社区** | ✅ 深度（QQ 群 + 中文 README）| ❌ | ❌ |

**选择建议**：要独立运行的 AI 渗透 Agent → VulnClaw。只想 ChatGPT 辅助 → PentestGPT。已经深度使用 Burp → burpgpt。

## 🎯 核心研判

### 项目优势
- **v0.4.0 求解引擎是差异化的关键** — "目标驱动"而非"轮数计数"让 VulnClaw 对弱模型比竞品更友好
- **最深的中文安全 AI 集成** — 13 个 Provider 中有 10 个是国内厂商，是真正的"国产替代"选择
- **社区活跃度健康** — 真实的 Issue 讨论、活跃的 QQ 群、持续的版本迭代（v0.3.2 → v0.4.1 在 2 个月内完成）

### 项目风险
- **持续发展依赖作者单人维护** — `iamloli@foxmail.com` 的单人项目，长期可持续性存在不确定性
- **"Alpha"状态** — pyproject.toml 标记 Development Status 3-Alpha，距生产级还有距离
- **弱模型适配仍不完美** — DeepSeek/MiniMax 的「证据闸门」虽然减少幻觉，但弱模型"无新发现就空转"的问题需要更多优化
- **法律风险** — 作为渗透工具，存在滥用风险。作者有安全声明但缺乏技术层面的约束（如目标授权验证）

### 趋势判断
- **快速上升期** — 2026-04 创建至今 1.1k Star，v0.4.0→v0.4.1 迭代快，有明确的版本规划。专注中文安全社区的策略非常讨巧
- 潜在增长点：Web UI（v0.4.1 新增）和持续渗透模式（persistent mode）让非技术用户也能使用

## 📂 关键文件路径速查

| 文件 | 说明 |
|------|------|
| `vulnclaw/agent/solver.py` | 核心求解引擎（OODA + Fact/Intent 黑板图）|
| `vulnclaw/agent/blackboard.py` | 黑板图数据结构 |
| `vulnclaw/agent/reflexion.py` | 自适应反思引擎（L0-L4）|
| `vulnclaw/agent/recon_tools.py` | v0.4.1 信息收集工具链 |
| `vulnclaw/agent/builtin_tools.py` | 内置工具（crypto_decode 等）|
| `vulnclaw/mcp/lifecycle.py` | MCP 服务生命周期管理 |
| `vulnclaw/cli/main.py` | Typer CLI 入口 |
| `vulnclaw/kb/store.py` | 安全知识库 |
| `vulnclaw/plugins/` | 漏洞检测插件目录 |
| `vulnclaw/skills/specialized/` | 14 个专项渗透 Skill |
| `pyproject.toml` | 依赖 + 发布配置 |
| `docs/mcp-deployment.md` | MCP 部署文档 |
