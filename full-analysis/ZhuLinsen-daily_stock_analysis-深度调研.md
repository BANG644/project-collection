# ZhuLinsen/daily_stock_analysis — LLM 驱动的多市场股票智能分析系统深度调研

> **调研更新**: 2026-07-31 | **Stars**: 59,613⭐ | **Forks**: 51,029（Fork 率异常高，Fork-to-run 模式）
> **语言**: Python | **许可**: MIT | **创建**: 2026-01-10（半年冲到 59K⭐）
> **仓库**: https://github.com/ZhuLinsen/daily_stock_analysis

## 项目定位（一句话）

把「每日看盘 + AI 研判 + 多端推送」压缩成一次 GitHub Actions 免费定时任务的开源自选股分析系统——用户 Fork 仓库、填 Secrets，即拥有一个零服务器成本的私人 AI 投研助理。

## 项目亮点（差异化）

1. **Fork 即部署的零成本架构** — 51,029 个 Fork（Fork/Star 比接近 0.86，极罕见）证明其主流用法不是 clone 而是 Fork：GitHub Actions 定时执行 + Secrets 存配置，全程无需服务器
2. **五市场覆盖** — A股/港股/美股/日股(.T)/韩股(.KS/.KQ)，同类开源项目最广
3. **通知系统做成了「路由 + 合约 + 降噪」三层工程** — 不是简单 webhook 转发（见源码解读）
4. **双 Guardrail 防幻觉设计** — `daily_market_context_guardrail.py` 与 `phase_decision_guardrail.py` 对 LLM 输出做事实约束，这是多数 AI 炒股项目缺失的工程自觉
5. **Agent 策略问股** — 15 种内置策略（均线/缠论/波浪/趋势/热点/事件/成长/预期等），仓库根目录含 `SKILL.md`/`CLAUDE.md`/`AGENTS.md`，已主动适配 Agent Skills 生态

## 核心架构

```
daily_stock_analysis/
├── main.py / server.py / webui.py   # 三入口：定时批处理 / API 服务 / Web 工作台
├── src/                             # 核心：约 30 个单一职责模块（非包目录，扁平化）
│   ├── analyzer.py / stock_analyzer.py / market_analyzer.py   # 个股/大盘分析
│   ├── market_context.py + market_phase_prompt.py             # 市场阶段上下文构建
│   ├── daily_market_context_guardrail.py                      # 大盘上下文防幻觉护栏
│   ├── phase_decision_guardrail.py                            # 阶段决策护栏
│   ├── notification_routing.py / _contracts.py / _noise.py / _capabilities.py  # 通知四件套
│   ├── search_service.py            # 新闻搜索聚合（7+ 搜索后端）
│   └── scheduler.py / storage.py / auth.py
├── data_provider/                   # 行情源适配（TickFlow/AkShare/Tushare/Pytdx/Baostock/YFinance/Longbridge）
├── strategies/                      # 15 种问股策略
├── bot/ + api/ + apps/              # IM 机器人 / API / 桌面端
└── .github/workflows                # 零成本运行的核心：Actions 定时任务
```

**架构决策**：LLM 层做成 OpenAI 兼容 + 多 Provider（Gemini/DeepSeek/通义/Claude/Ollama 本地），数据层做成多源 failover（免费源不稳时自动切换）——两层都不锁死单一供应商，这是它比同类「单 API 脚本」寿命长的根本原因。

## 应用场景与启发

**可用场景**：
- 个人投资者的每日自选股 AI 简报（企业微信/飞书/Telegram/邮件推送）
- 小团队的投研初筛流水线（Web 工作台 + 历史报告 + 回测）
- 作为「LLM + 金融数据」工程范式参考（护栏、通知路由、多源 failover 的实现样板）

**给同类需求的启发**：
1. **「Fork-to-run + Actions 定时 + Secrets 配置」是零成本 SaaS 化的成熟套路**——任何「每日定时跑一次、产出推送到 IM」的个人自动化需求（价格监控、舆情日报、RSS 摘要）都可以套用
2. **LLM 输出必须配 Guardrail 模块**：本项目把「大盘上下文」和「阶段决策」分别做成独立护栏文件，约束模型不得输出与事实数据冲突的结论——AI + 高风险决策领域（金融/医疗）的必备工程
3. **通知不是发消息，是「能力检测 → 合约校验 → 降噪 → 路由」**：多渠道推送做到工程级的拆法值得抄

## 源码深度解读

### 通知四件套（src/notification_*.py）

同类项目通知就是一个 `send_wechat()` 函数；本项目拆成四个模块：

- `notification_capabilities.py` — 每个渠道声明能力（支持 Markdown？图片？消息长度上限？）
- `notification_contracts.py` — 定义消息合约（结构化 payload），渠道适配器各自渲染
- `notification_noise.py` — 降噪：重复告警合并、静默窗口
- `notification_routing.py` — 按消息类型/严重级路由到不同渠道

这套「能力协商 + 合约 + 路由」结构可直接迁移到任何多渠道通知系统。

### 防幻觉护栏（daily_market_context_guardrail.py / phase_decision_guardrail.py）

分析管线在 LLM 生成结论后跑护栏校验：市场阶段判断必须与真实指数数据一致，决策评分必须在与上下文兼容的区间内，否则拒绝/重试。**Prompt 内嵌约束不可靠，独立护栏模块二次校验才可靠**——这是该项目最值得借鉴的一课。

### 报告渲染（md2img.py + report_language.py）

分析报告 Markdown → 图片（md2img），解决企业微信/飞书对长 Markdown 支持差的问题；`report_language.py` 支持多语言报告输出。细节工程完整度高于绝大多数同类。

## 全网口碑

- 中文 AI 投资社区高频推荐项目，「零成本部署」是最常被引用的卖点（数据可用性有限，独立深度评测少）
- 51K Fork 的真实含义：用户基数远大于 Star 数所示，且大多以 Fork 私有化方式使用
- 常见吐槽方向：免费数据源（AkShare 等）不稳定、深度配置需要读大量文档（README 也自认）
- 49 个 open issues 相对 51K Fork 极少——说明 Fork 用户大多静默使用，社区反馈集中于数据源失效类问题

## 竞品对比

| 维度 | daily_stock_analysis | ai-hedge-fund (virattt) | FinGPT | dexter (virattt) |
|------|---------------------|------------------------|--------|------------------|
| 定位 | 每日自选股 AI 简报 | 多 Agent 投资大师模拟 | 金融 LLM 训练/微调 | 金融研究自主 Agent |
| 零成本运行 | ✅ GitHub Actions | ❌ 本地/需 API 费用 | ❌ 需 GPU | ❌ |
| 市场覆盖 | ✅ A/H/US/JP/KR | ⚠️ 美股为主 | ⚠️ | ⚠️ 美股为主 |
| 推送/日报形态 | ✅ 6 渠道 | ❌ | ❌ | ❌ |
| A 股生态适配 | ✅ 深度（缠论/龙虎榜语境）| ❌ | ⚠️ | ❌ |
| 教育/研究价值 | ⚠️ 工程范式 | ✅ Agent 编排范式 | ✅ 学术 | ✅ |

**结论**：与 ai-hedge-fund/dexter 不构成直接竞争——那两者是「Agent 研究范式」，本项目是「日常可用的生产工具」。在「中文用户 + 零成本 + 日报形态」这个组合上目前无对手。

## 核心研判

**优势**：零成本运营模式契合个人投资者；五市场覆盖 + 多模型 + 多渠道的「全都要」产品形态；护栏与通知层工程质量显著高于同类。

**风险/局限**：
1. 免费数据源依赖是最大脆弱点（上游 API 变更即批量失效）
2. 定位是辅助分析非量化交易，策略深度有天花板
3. 51K Fork 意味着大量过期副本存在，上游修复难以触达
4. AI 荐股类项目固有的合规敏感性（项目自身仅做分析不做交易，风险相对可控）

**趋势判断**：仓库根目录已放 SKILL.md/AGENTS.md，正在从「定时脚本」向「Agent 可调用的金融分析能力」演进——这是 2026 年工具类开源项目的标准转型路径。

## 关键文件路径速查

| 路径 | 作用 |
|------|------|
| `main.py` | 定时批处理主入口（Actions 调用） |
| `src/analyzer.py` / `src/stock_analyzer.py` | 个股分析核心 |
| `src/daily_market_context_guardrail.py` | 大盘上下文防幻觉护栏 ⭐ |
| `src/phase_decision_guardrail.py` | 阶段决策护栏 ⭐ |
| `src/notification_routing.py` 等四件套 | 多渠道通知工程 ⭐ |
| `data_provider/` | 多行情源 failover 适配层 |
| `strategies/` | 15 种 Agent 问股策略 |
| `SKILL.md` / `AGENTS.md` / `CLAUDE.md` | Agent 生态适配入口 |
| `docs/full-guide.md` | 完整部署指南 |
