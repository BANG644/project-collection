# Browser Use 深度调研

> 仓库：`browser-use/browser-use` ｜ MIT ｜ 主语言 Python（≥3.11）｜ 2026-08-26 抓取
> 星标：110,829 ⭐（当日 Trending +135）｜ Fork：12,180 ｜ 安装：`uv add browser-use` 或 `browser-use skill install`
> 官网：https://browser-use.com ｜ 文档：https://docs.browser-use.com

## 一、项目定位（一句话）

Browser Use 让 AI Agent **像人一样操作网页浏览器**——打开页面、点击、输入、填表、抽取数据；既提供开源 Python 库（自带 LLM、深度可控），也提供全托管云 Agent（1000+ 集成、stealth、代理轮换、规模化）。

## 二、项目亮点（差异化）

1. **基准领先**：自研 **BU Bench V1**（100 个真实 web 任务）开源；并在 **Odysseys leaderboard #1（87.4% 平均，200 个长程任务）**，超过 OpenAI / Anthropic / Google / Microsoft 的 computer-use agent。
2. **双形态交付**：开源库（免费、本地、可定制 LLM 与 agent 行为）vs 全托管云 Agent（更强模型 `bu-*`、持久文件系统与记忆、可重跑脚本拉取实时数据）。
3. **统一 LLM 接口 `ChatBrowserUse`**：provider-prefixed model id（`anthropic/claude-sonnet-4-6`、`openai/gpt-5.5`、`google/gemini-3-pro`），一个 `BROWSER_USE_API_KEY` 打通所有厂商，无需分别配 key；官方称比其它模型快 3–5× 且 SOTA 准确。
4. **语义级 DOM 抽象 + 自循环 Agent**：把页面压缩成 LLM 友好的元素树（而非像素），配合结构化动作空间与事件总线，构成稳定可控的 web agent 主循环。
5. **工程化扩展点**：自定义 `Tools`（`@tools.action` 装饰器）、MCP、真实浏览器 profile 复用登录态、AgentMail 临时账号、云侧 CAPTCHA/stealth/proxy 解决生产痛点。

## 三、核心架构（克制呈现）

```
Agent (agent/service.py)            ← LLM 主循环编排
  ├─ LLM: ChatBrowserUse / ChatOpenAI / ChatAnthropic ...
  ├─ BrowserSession + DomService    ← CDP 取 AX tree + DOM，序列化
  ├─ Tools / Registry (ActionModel) ← 动作空间（pydantic）
  ├─ MessageManager                 ← 历史/上下文压缩（compaction）
  ├─ judge.py                       ← LLM-as-judge 评估
  └─ bubus EventBus                 ← 事件驱动（step/session/output 事件）
```

- `Agent`（`browser_use/agent/service.py`）是核心：接收 `task` + `llm`，循环产出结构化 `AgentOutput`（动作），执行后把观测写回，再进入下一轮，直到任务完成或步数上限。
- `DomService`（`browser_use/dom/service.py`）通过 `cdp_use` 走 CDP 协议取 accessibility tree + DOM，交给 `DOMTreeSerializer`（`dom/serializer/`）压成简化、带可点击标注的元素树，喂给 LLM——这是"语义级"而非"像素级"的关键。
- `Tools`（`tools/registry` + `tools/service.py`）定义动作模型 `ActionModel`，支持用户 `@tools.action` 扩展。

## 四、应用场景与启发（重点）

- **Web 自动化总入口**：填表、数据抽取、监控、QA、RPA 替代；规则——一次性任务走 CLI/Skill（接 Claude Code/Codex/Cursor），可重复规模化走 Python 库。
- **给"Agent 控制 GUI"提供标准参考架构**：`DOM 语义抽象 + 结构化动作空间 + 自循环 + 上下文压缩` 四件套，可直接借鉴到任何"agent 操作图形界面"的场景（桌面、移动、native app）。
- **可复用于"长程任务可靠性"**：`MessageManager` 的 history compaction、`judge.py` 的 LLM 评估、`CloudEvents` 的 step/session 遥测，构成可观测、可复盘的多步 agent 骨架，值得长程 agent 项目参考。

## 五、源码深度解读（2 个核心模块）

**① `browser_use/agent/service.py` — Agent 主循环装配**
```python
# 头部依赖（节选，体现架构分层）
from bubus import EventBus
from browser_use.agent.message_manager.service import MessageManager
from browser_use.agent.prompts import SystemPrompt
from browser_use.agent.views import AgentOutput, AgentHistoryList, ActionResult
from browser_use.browser.session import BrowserSession
from browser_use.tools.service import Tools
from browser_use.llm.base import BaseChatModel
...
def log_response(response: AgentOutput, registry=None, logger=None) -> None:
    """Utility function to log the model's response."""
```
可见 Agent 由事件总线、消息管理、系统提示、工具注册、LLM 抽象与浏览器会话组合而成，`AgentOutput` 是 LLM→动作的结构化契约。

**② `browser_use/dom/service.py` — DOM 语义序列化**
```python
class DomService:
    """Service for getting the DOM tree and other DOM-related information."""
    # 通过 cdp_use 走 CDP accessibility + DOM 协议
    from browser_use.dom.serializer.serializer import DOMTreeSerializer
    from browser_use.dom.serializer.clickable_elements import ClickableElementDetector
    # 跨源 iframe 仅当 ≥10px 才纳入；click listener 超 100 元素触发溢出标记
```
`DomService` 把原始 DOM/AX 转成 LLM 友好的精简树，`ClickableElementDetector` 标注可交互元素——这是 Browser Use 比"截图+视觉模型"更稳、更省 token 的根本原因。

## 六、全网口碑

- **110k+ star、12k+ fork**，MIT，作者 Magnus Müller 与 Gregor Žunič（苏黎世 + 旧金山），社区与商业双轨运转。
- 基准仓库 `browser-use/benchmark` 开源，社区可复跑；Discord 活跃，云产品 `cloud.browser-use.com` 已商业化（API v4）。
- 争议点：开源库本地跑 Chrome 内存占用大、并行难管；CAPTCHA / anti-bot 检测需付费云（stealth + 代理轮换）；网站结构变化会让 selector 类逻辑脆弱。

## 七、竞品对比 + 核心研判

| 维度 | Browser Use | Playwright/Selenium | LangChain browser tool | OpenAI Operator / Claude Computer Use |
|---|---|---|---|---|
| 控制粒度 | DOM 语义元素 | 选择器/协议 | 工具封装 | 像素级视觉 |
| Agent 自循环 | ✅ 内置 | ❌ 自写 | 部分 | ✅ |
| 多 LLM | ✅ ChatBrowserUse | n/a | ✅ | 厂商锁定 |
| 云托管/规模化 | ✅ 官方云 | ❌ | ❌ | ✅ 厂商云 |
| 反检测/代理 | 云侧提供 | 需自建 | 无 | 厂商内置 |

**核心研判**
- **优势**：web agent 事实标准开源实现，生态最大、基准领先、LLM 无关、开源+云双轨，企业可本地控也可上云扩展。
- **风险**：① 本地规模化资源与并行管理成本高；② anti-bot/CAPTCHA 实为付费墙；③ 强依赖页面结构，脆弱性随目标站点变化。
- **趋势**：web agent 正成为 agent 基础设施标配，Browser Use 凭"语义 DOM + 自循环 + 云双轨"占据开源心智；将来竞争焦点在可靠性、成本与反检测。
- **启发**：做"控制某个 GUI"的 agent 时，优先语义抽象而非像素识别；把"动作空间 + 上下文压缩 + 可观测事件"作为骨架先行设计。
