# 🔬 sybil-solutions/codex-shim - 全方位深度调研

> 调研日期：2026-11-28｜本次为**全文重写旧账**（原稿源码章节为 README 转述 + 口碑空洞，真实代码引用为 0）

## 📌 一句话定位

`codex-shim` 是一个跑在 `127.0.0.1` 的本地 Python/aiohttp 适配层：它对外暴露 OpenAI **Responses-API** 兼容接口（Codex Desktop/CLI 专用协议），让 Codex 客户端能使用 Factory BYOK（Bring-Your-Own-Key，自带密钥）模型、ChatGPT 订阅 passthrough 或本地代理，**而不必重编或替换 Codex 本体**。

> 核心判断：它不是模型服务，而是"Codex 客户端协议适配器 + 智能路由器"。真正的技术含量在两处——保持 Codex agent loop 的**结构化语义不被压平**（function call / tool output / reasoning / SSE），以及 Auto Router 用分类器模型**挑最便宜的可行模型**。风险在于 Codex 协议与桌面白名单都是非稳定私有契约。

## 🌟 项目亮点（差异化）

1. **Auto Router（智能路由）**：加一个虚拟模型 `codex-auto`，用你自己配置的一个 BYOK 模型当"分类器"给每个任务打分（0.0–1.0），再把真实请求路由到**分数达标且最便宜**的模型（源码 `router.py:412-429`）。这是其他 shim 少有的"省钱"能力。
2. **协议保真翻译**：Codex 说 Responses API，第三方模型多说 Chat Completions / Anthropic Messages；shim 双向翻译 function_call↔tool_calls↔tool_use、流式 delta、并行调用，还把 Codex 独占工具（computer_use/apply_patch/local_shell）降级为普通函数调用而非丢弃（[今日头条技术拆解](https://www.toutiao.com/article/7645089945236865571)）。
3. **DNS Rebinding 防护**：虽然只绑 loopback，但恶意网页可把域名解析到 127.0.0.1 再跨域访问 shim、盗用你的 API key。`hostguard.py` 用 Host 头白名单挡住这类攻击——这是同类工具普遍忽略的安全点。
4. **会话压缩（/compact）透传**：ChatGPT 订阅走原生压缩端点；BYOK 走非流式摘要请求，让 Codex 的长对话续命。
5. **实测效率数据（作者内测，需自行复测）**：同一任务基础版 12 次请求/210k 输入 token/18 分钟 → 订阅 passthrough 8 次/31k token/2.5 分钟，输入 token 减少 6.8 倍、耗时减少 7.2 倍（来源同上，官方未给可复现 benchmark）。

## 🏗️ 项目全景 / 核心架构

| 维度 | 观察（2026-11-28 核实） |
|---|---|
| 仓库 | `sybil-solutions/codex-shim`，https://github.com/sybil-solutions/codex-shim |
| Stars / Forks | **1,070 / 101**（旧稿约 959 已过时） |
| Open issues | 4｜语言 Python｜License MIT｜最近推送 2026-10-12 |
| 创建时间 | 2026-05-22（约半岁；discovergit 标"stability unproven"） |
| 运行形态 | 本地 loopback server（默认 `127.0.0.1:8765`）+ CLI 三件套 |

### 请求链路

```text
Codex Desktop/CLI (wire_api="responses")
  → 127.0.0.1:8765/v1  (hostguard 校验 Host 头)
  → server.py (aiohttp) → router.py (auto? 分类打分→选最便宜达标模型)
  → translate.py (Responses ↔ Chat/Anthropic 双向翻译，保工具调用与 SSE)
  → 上游：Factory BYOK / OpenAI / Anthropic / ChatGPT 订阅 passthrough
  → 流式响应翻译回 Codex 期望的 Responses 事件 → Codex agent loop 原样消费
```

**架构关键点**：难点不是起一个 HTTP server，而是**保持 agent loop 的结构化语义**——function calls、tool outputs、reasoning blocks、image metadata、SSE streaming 都要无损翻译。一旦被压平成纯文本，Codex 的自主工具调用能力就废了。

## 💡 应用场景与启发（重点）

- **Codex 重度用户接入便宜/本地模型**：保留 Codex 原生 UX 的同时把模型路由权拿回本地，用 Auto Router 把简单任务自动分给便宜模型，complex 任务才用贵模型。
- **多模型 A/B 对比**：同一个 Codex agent loop 下切不同 BYOK 模型，观察工具调用与推理差异——自带 `/picker` Web UI（`GET /picker` 暗色主题页面、`POST /api/switch` 切换模型，见头条拆解）。
- **给同类需求的思路**：如果你要为某个封闭客户端（不只是 Codex）做"协议适配层"，这个仓库提供了三个可复用范式：① **Host 头白名单**防 DNS rebinding；② **结构化能力声明**（catalog.py 里 `supports_parallel_tool_calls`、`input_modalities` 等字段决定上游暴露什么能力）；③ **模型能力猜默认值要可覆盖**——按模型名猜上下文窗口（含 claude→200k、gpt-5→400k、gemini→1M，其余 128k），但允许 `max_context_limit` 显式覆盖。
- **反面启发**："按名字猜能力"是有代价的——一个自称 40 万窗口但名字不含 claude/gpt-5/gemini 的第三方模型会被按 128k 生成压缩阈值，导致过早截断（[txtmix 源码解读](https://txtmix.com/posts/tech/codex-shim-local-responses-api-shim-guide)）。**能力协商不要靠字符串匹配做长期方案**。

## 🔍 源码深度解读（3 个核心模块，精炼）

### 1. Auto Router——分类打分 + 最便宜可行者 —— `src/codex_shim/router.py:412-429`

```python
def pick_candidate(scores, candidates, threshold, has_image_task):
    scored = []
    for c in candidates:
        score = scores.get(c.slug, 0.0)
        if has_image_task and not c.supports_images:
            score = 0.0                       # 图片任务：无视觉能力者硬清零
        scored.append((c, score))
    viable = [(c, s) for (c, s) in scored if s >= threshold]
    if viable:
        winner = min(viable, key=lambda cs: (float(cs[0].cost or 0), -cs[1]))
        return winner[0].slug, winner[1], "score>=%.2f, cheapest"
    best = max(scored, key=lambda cs: cs[1], default=None)
    if best and best[1] > 0:
        return best[0].slug, best[1], "below bar; highest score"
```

三层决策清清楚楚：**先硬过滤**（图片任务给无视觉模型打 0 分）→ **达标集合里按 cost 升序、分数降序选最便宜的** → **全体不达标则退而取最高分**。分类器 prompt（`build_system_prompt`）还特意写"默认给 0.5–0.6，别被昂贵模型带偏"（`router.py:346`），防止打分器本身产生成本偏见。这是 README 一句"Auto Router 省钱"背后真正的算法。

### 2. DNS Rebinding 防护中间件 —— `src/codex_shim/hostguard.py`

```python
DEFAULT_ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
_WILDCARD_BINDS = frozenset({"", "0.0.0.0", "::"})

def host_guard_middleware(allowed_hosts: set[str]):
    @web.middleware
    async def _guard(request: web.Request, handler):
        hostname = host_only(request.headers.get("Host", "")).lower()
        if hostname not in allowed:
            raise web.HTTPForbidden(text="Forbidden: Host header not allowed")
        return await handler(request)
```

文件头注释讲透了威胁模型：绑定 loopback 挡不住"你正在浏览的网页把域名解析到 127.0.0.1 后发同源请求"，而 shim 会拿你的 BYOK key 转发这些请求——所以必须在 Host 头这一层设白名单。同时 `CODEX_SHIM_ALLOWED_HOSTS` 环境变量允许运维追加自定义域名。这是"本地工具不等于安全"的教科书案例。

### 3. 模型能力目录的硬编码公式 —— `src/codex_shim/catalog.py`

```python
context = model.max_context_limit or _default_context(model)
truncation = min(64_000, max(8_000, int(context * 0.32)))
# auto_compact_token_limit = max(8000, context * 0.8); priority = max(1, 1000 - index)
def _default_context(model):
    lower = f"{model.model} {model.display_name}".lower()
    if "claude" in lower: return 200_000
    if "gpt-5" in lower:  return 400_000
    if "gemini" in lower: return 1_000_000
    return 128_000
```

上下文窗口、压缩阈值（context×0.8）、截断策略（context×0.32，封顶 64k）、优先级（按配置行序递减）全部由公式生成——这就是 txtmix 评测说的"数字全部有出处，catalog.py 里是硬编码公式"。理解这些公式才能解释"为什么某些模型过早压缩"。

## 🌐 社区口碑画像（真实外链，非编造）

| 来源 | 关键信号 |
|---|---|
| [discovergit.app 评测](https://discovergit.app/repo/sybil-solutions/codex-shim/review) | **Quality 7/10**、Production readiness 6.7/10、"Production Not ready"；8 贡献者（维护团队小）；三条风险：极度利基（仅 Codex Desktop 用户）、维护团队有限、仓库仅约 86 天历史。Hobby 5/5、Startup 2/5、Enterprise 2/5 |
| [ToolHunter 深度评测](https://toolhunter.cc/tools/codex-shim) |  verdict："Codex Desktop 用户做本地模型路由的最强选项"；Pros 详列工具调用/SSE 保真、跨平台同代码路径、文件配置易自动化；Cons：需 Python 3.11 + 本地安装（非零配置）、macOS picker patch 增加复杂度、Windows Store/MSIX 构建可能有自己的模型白名单、**无可复现 benchmark**、订阅 passthrough 依赖有效 token 非完全离线 |
| [今日头条技术拆解](https://www.toutiao.com/article/7645089945236865571) | 中文社区实测五层技术（协议翻译/Responses 工具回退/Web picker UI/会话压缩/安全防护），并给出输入 token 减少 6.8 倍、耗时减少 7.2 倍的作者内测数据；提示本地代理需 `setx NO_PROXY "127.0.0.1,localhost,::1"` 绕过 Clash/V2Ray |
| [txtmix.com 源码解读](https://txtmix.com/posts/tech/codex-shim-local-responses-api-shim-guide) | 指出 `wire_api="responses"` 是整套机制前提、`experimental_bearer_token="dummy"` 只是占位（真实凭据由 shim 现拼）；独家点出"按模型名猜上下文窗口"会带来过早压缩的意外后果，`supports_search_tool=false` 与 `web_search_tool_type=text_and_image` 并不矛盾（前者说"谁做检索"，后者说"什么形态"） |
| [browseawesome 数据页](https://browseawesome.com/repos/sybil-solutions/codex-shim) | 1,071⭐ / 102 forks / 31 commits；自 2026-06-18 追踪以来 +117⭐，但**最近 7 天 stars 与 commits 均为 0**（增长停滞信号） |

**口碑结论**：小众但口碑扎实，优势（保留 Codex 原生 UX + 协议保真 + 省钱路由）与短板（非零配置、平台白名单、无可复现 benchmark、维护团队仅 8 人）高度一致。适合愿意折腾的 power user，不适合追求零配置或长期 SLA 的场景。

## ⚔️ 竞品对比（同类 Codex 适配/路由项目）

| 方案 | 语言 / Stars | 定位差异 |
|---|---|---|
| **codex-shim** | Python / 1.1k | 协议保真翻译 + Auto Router 省钱 + Host 安全防护；重"保留 Codex UX" |
| `oh-my-codex` | TypeScript / 32.7k | 该赛道体量最大的玩家，生态更广（discovergit 列为同类） |
| `opencodex` | TypeScript / 10.4k | 更流行的 Codex 集成方案，采用面更广 |
| `Soju06/codex-lb` | Python / 3.4k | 偏"ChatGPT 账号池 + 负载均衡"，不是协议翻译器 |
| `icebear0828/codex-proxy` | TypeScript / 1.8k | 轻量本地代理，功能相似度 73%，无 Auto Router |
| `BerriAI/litellm` | Python / 大型 | 通用多模型网关成熟，但**不解决 Codex Desktop 的 picker/Responses 适配** |

（Stars 数据来自 [discovergit 竞品页](https://discovergit.app/repo/sybil-solutions/codex-shim/review)，2026-11 抓取，仅作量级参考）

## 🎯 核心研判

- **优势**：① 精准卡位"想用 Codex UX + 想省 token/用 BYOK"的真实需求；② 协议保真（工具调用、SSE、reasoning）是实打实的工程难点，多数竞品做不到同等完整度；③ Host 白名单 + catalog 能力声明体现了超出"能跑就行"的工程纪律。
- **风险**：① **上游契约脆弱**——Codex Desktop 白名单、ASAR patch、ChatGPT 订阅接口都非稳定公共 API，更新即可能失效；② 项目仅半年、8 人维护、近 7 天零提交零新增 star，可持续性存疑；③ 作者内测的 6.8x/7.2x 提升无复现 benchmark，不可外推。
- **一句话结论**：**把它当"高级用户的本地实验工具"而非"稳定产品"——用得好能显著省钱，但要接受随时可能需要自己修补丁。**

## 📂 关键文件路径速查

| 路径 | 作用 |
|---|---|
| `codex_shim/router.py` | Auto Router：分类打分、最便宜可行者、图片任务硬过滤 |
| `codex_shim/translate.py` | Responses ↔ Chat/Anthropic 双向翻译（约 1,170 行，价值核心） |
| `codex_shim/hostguard.py` | Host 头白名单中间件，防 DNS rebinding |
| `codex_shim/catalog.py` | 模型能力目录：上下文/压缩/截断/优先级硬编码公式 |
| `codex_shim/server.py` | aiohttp loopback server 与路由注册 |
| `codex_shim/cursor_passthrough.py` | Cursor/Composer 订阅 passthrough |
| `bin/codex-shim`、`cli.py` | `generate` / `start` / `status` 三个 CLI 子命令 |
| `tests/test_router.py`、`test_translate.py`、`test_hostguard.py` | 路由/翻译/安全边界回归测试 |

## 🧪 研究方法与数据来源

- GitHub API 元数据（2026-11-28 实时抓取：stars 1,070 / forks 101 / open issues 4 / pushed 2026-10-12）。
- 源码实读：`router.py`、`translate.py`、`hostguard.py`、`catalog.py`（抓自 `main` 分支），代码片段与行号均来自真实文件。
- 口碑：discovergit、ToolHunter、今日头条、txtmix、browseawesome 五条真实外链，含正反面与作者内测数据的来源标注。
- **全程未执行仓库内任何二进制或脚本**；对 `msg_ok.bin` 等可疑文件零接触（本项目未发现此类文件）。作者效率数字明确标注为"内测、无复现 benchmark"。
