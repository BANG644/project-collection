# Usagi-org/ai-goofish-monitor 深度调研

> 调研日期：2026-11-04 ｜ 定位：基于 Playwright + 多模态 AI 的闲鱼多任务实时监控系统（AI Xianyu Hunter）
> 仓库：https://github.com/Usagi-org/ai-goofish-monitor ｜ Stars：≈16.3k ｜ 语言：Python ｜ 许可：MIT
> 关键词：playwright / ai-monitor / xianyu / fastapi / cron / notification

## 一、项目定位（一句话）

ai-goofish-monitor（代号 AI Xianyu Hunter）是一个自托管的闲鱼智能监控系统：你用大白话写下「想买什么」，它 7×24 小时用 Playwright 驱动 Chromium 盯闲鱼，把商品图文 + 卖家行为丢给多模态模型做「画像优先」分析，命中后用 ntfy / 企业微信 / Bark / Telegram / Webhook 等渠道推送。它不是关键词爬虫，而是一条「采集→去重→补上下文→沉淀价格历史→AI/关键词判断→通知」的完整本地后台。

## 二、项目亮点（差异化，开篇先看）

1. **画像优先的 AI 判断**：`prompts/base_prompt.txt` 里代号 EagleEye-V6.4 的提示词核心是「先判断卖家的故事是否自洽（个人玩家 vs 职业贩子），再判断商品」——带豁免条款（长期体验—升级—出售闭环可豁免「频率偏高」）与一票否决（行话/批量配件），逼模型逐项给证据而非「我感觉像贩子」。
2. **AI 不是主角，脏活才是**：真正的核心是稳定的采集、去重、价格历史沉淀与风控规避；AI 只是最后一段筛选器。Chinese 技术博客评价「真正难的不是 AI」。
3. **双模式判断**：AI 模式（多模态，需看图模型）与关键词模式（不调模型，纯规则拼匹配）并存；并对 `q1`/`q1r5` 这类英文数字边界做专门处理，细节真实。
4. **完整工程后台**：FastAPI 后端 + Vue 管理台 + SQLite 存储 + 账号/代理轮换 + Cron 调度 + 失败保护（连续失败 3 次自动暂停 24h）+ 运行日志自动清理（默认 7 天）。
5. **自托管隐私**：登录态、商品结果、提示词全在你控制的机器上；MIT 可随便改。

## 三、核心架构（克制呈现）

`src/` 下分层清晰，呈「Web 层 / 领域层 / 基础设施层 / 采集脚本」：

- **`src/app.py`**：FastAPI 主入口，装配 `dashboard/tasks/logs/settings/prompts/results/login_state/websocket/accounts` 路由，全局 `ProcessService` / `SchedulerService` / `TaskGenerationService`，启动时 `bootstrap_sqlite_storage` 建库并自动从旧 `config.json/jsonl/price_history` 迁移。
- **`src/api/routes/`**：各 REST/WebSocket 路由（任务、结果、日志、账号、提示词、登录态）。
- **`src/core/cron_utils.py`**：基于 APScheduler 的 Cron 解析与校验（`CronTrigger`、别名 `@daily/@hourly`、5/6 段兼容）。
- **`src/domain/`**：`models/`（task、task_generation）、`repositories/`（任务仓储）。
- **`src/infrastructure/`**：`config/`（env_manager、settings）、`external/`（ai_client、notification_clients：bark/base/企业微信/…）。
- **`src/ai_handler.py` + `src/ai_message_builder.py`**：AI 分析编排与提示词拼装。
- **`spider_v2.py`**：Playwright 爬虫主脚本（asyncio + argparse + `SqliteTaskRepository` + `scrape_xianyu`），可按 `--task-name` 被调度器单任务调用。
- **`chrome-extension/`**：导出闲鱼登录态 JSON 的浏览器扩展；`prompts/`：分析标准提示词。

## 四、应用场景与启发

- **二手捡漏 / 竞品追踪 / 库存补货提醒 / 二手市场研究**：监控指定型号的目标价位，用 AI 过滤「像贩子」「成色不符」的噪音。
- **给同类需求的启发**：① 在「二手交易 / 招聘 / 舆情」这类**非结构化但需判断**的场景，正确的顺序是「先把商品+卖家数据拿齐、沉淀价格历史，最后才让 AI 判断」——AI 单独上场极易乱判；② 把专家经验拆成「画像优先 + 豁免条款 + 一票否决 + 逐项证据」的可执行提示词，比一句「判断是不是贩子」强得多；③ `prompts/base_prompt.txt` 里 `V6.3 逻辑修正 / V6.4 逻辑修正` 的注释，说明好提示词是拿真实案例一条条怼出来的，不是想出来的。

## 五、源码深度解读

**1) 调度核心——`src/core/cron_utils.py`**
把 5 段/6 段 Cron 与常见别名归一化为 APScheduler 的 `CronTrigger`，带时区与格式校验：

```python
CRON_ALIASES = {"@daily": "0 0 * * *", "@hourly": "*/1 * * * *", ...}
def normalize_cron_expression(value):
    normalized = " ".join(str(value).strip().split())
    return CRON_ALIASES.get(normalized.lower(), normalized)
def build_cron_trigger(expression, *, timezone=None) -> CronTrigger:
    parts = normalized.split()
    if len(parts) == 5: return CronTrigger.from_crontab(normalized, timezone=timezone)
    if len(parts) == 6: return CronTrigger(second=..., minute=..., ...)  # 带秒
```
这是「配置即调度」的干净实现，让 Web UI 里填一段 Cron 就能周期跑任务。

**2) 入口装配——`src/app.py`**
FastAPI 启动时拉起服务并做 SQLite 引导迁移，全局单例被路由共享：

```python
process_service = ProcessService()
scheduler_service = SchedulerService(process_service)
task_generation_service = TaskGenerationService()
# lifespan 内 bootstrap_sqlite_storage() 建库 + 旧数据一次性导入
```
体现「持久化 + 旧格式兼容」的工程取舍——升级不丢历史。

**3) 采集主循环——`spider_v2.py`**
`asyncio main()` 从 `SqliteTaskRepository` 取任务，按任务归一化关键词、绑定账号、可单任务调度；真实链路是 Playwright 开闲鱼→监听搜索/详情接口→补卖家信息/图片/价格快照→最后才交给 AI 或关键词规则。风控命中（`baxia-dialog` / `J_MIDDLEWARE_FRAME_WIDGET` / `FAIL_SYS_USER_VALIDATE`）时打印 `CRITICAL BLOCK DETECTED`、随机休眠并抛 `RiskControlError`，不硬扫。

**4) AI 分析编排——`src/ai_handler.py`**
兼容 Chat Completions / Responses API（`CHAT_COMPLETIONS_API_MODE` / `RESPONSES_API_MODE`），模型不稳时空响应重试、JSON 格式不支持就退一步；支持 DeepSeek `enable_thinking`、豆包关 `response_format` 等开关——AI 在这里是**依赖项而非免维护能力**。

## 六、社区口碑（全网口碑）

- **正面**：GitHub 13.5k–16.3k stars、2k+ forks，被多个中文技术博客（微信/ GitCode）详细拆解，称赞其「画像优先原则」提示词设计与「先数据后 AI」的工程顺序；飞牛 NAS 部署教程证明其易自托管。
- **冷静面（第三方）**：① 仓库近期提交停滞（末次提交约 2026-05、release 2.4 停在 4 月），issue 区挂 ~55 个未关，更像「可 fork 的工程样板」；② 需导出闲鱼登录态，**账号风险在代码之外**（README 已提示遵守协议、别高频）；③ 风控是天花板——它适合长期观察合适商品，不保证抢到热门货；④ OpenAlt 综合评 66/100（功能性尚可、生态/文档偏弱）；⑤ `prompts` 接口曾存在 Windows 路径穿越（**CVE-2026-10044**，PR #489 已用 `Path.resolve` + 目录包含性检查修复），建议部署在内网并改默认口令。

## 七、竞品对比

| 维度 | ai-goofish-monitor | 纯关键词爬虫脚本 | 市面 SaaS 监控 | 人工刷闲鱼 |
|------|-------------------|----------------|---------------|-----------|
| 分析能力 | 多模态 AI + 卖家画像 | 仅关键词匹配 | 视产品 | 靠人脑 |
| 用户友好 | Web 管理台可视化 | 需写代码 | 开箱即用 | — |
| 成本 | 开源+自托管（仅 AI token 费） | 几乎零 | 订阅费 | 时间成本 |
| 隐私/可控 | 全本地、可改 | 本地 | 云端 | — |
| 平台 | 仅闲鱼 | 任意（需自写） | 多平台 | 全平台 |

优势在「AI 画像 + 私有自托管 + 零许可费」；短板在「仅闲鱼、需技术配置、维护节奏放缓」。

## 八、核心研判

- **价值判断**：对长期盯相机/显卡/手机/手表等高价二手品、且愿意当本地私有系统维护的人，它值得 fork 学习——真正可借鉴的是那条「先拿齐数据、沉淀价格历史、最后 AI 判断」的顺序与提示词工程方法，而非某个模型。
- **风险点**：① 维护停滞 + 未关 issue，别按「成品软件」预期；② 登录态/风控/频率是真实上限，模型接口与闲鱼策略都会变；③ 安全上务必内网部署、改默认口令、及时拉最新修复（含 CVE-2026-10044）。
- **采用建议**：Docker 起一个 → 扩展导出登录态 → 写一段自然语言需求跑通；把它当「工程样板 + 提示词素材库」而非「全天候抢货机器」。

## 九、关键文件路径速查

- `src/app.py` — FastAPI 主入口与服务装配、SQLite 启动迁移
- `src/core/cron_utils.py` — APScheduler Cron 解析/校验（别名+5/6 段）
- `src/ai_handler.py` / `src/ai_message_builder.py` — AI 分析编排与提示词拼装
- `src/api/routes/` — dashboard/tasks/results/accounts/login_state/websocket 等路由
- `src/infrastructure/external/ai_client.py` / `notification_clients/` — AI 客户端与多通道通知
- `src/domain/repositories/task_repository.py` / `src/infrastructure/persistence/sqlite_*.py` — 任务仓储与 SQLite 持久化
- `spider_v2.py` — Playwright 采集主脚本（风控识别 + 单任务调度）
- `prompts/base_prompt.txt` — EagleEye-V6.4「画像优先原则」提示词（核心资产）
- `chrome-extension/` — 闲鱼登录态导出扩展
- `DISCLAIMER.md` / `CLAUDE.md` / `AGENTS.md` — 合规声明与 AI 接入说明
