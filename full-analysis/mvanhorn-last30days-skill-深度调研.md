# mvanhorn/last30days-skill — 「搜人不搜编辑」的 Agent 情报引擎深度调研

> **调研时间**: 2026-07-31 | **Stars**: 55,428⭐ | **Forks**: 4,779
> **语言**: Python | **许可**: MIT | **创建**: 2026-01-23（半年冲到 55K⭐，曾 GitHub Trending 日榜 #1）
> **仓库**: https://github.com/mvanhorn/last30days-skill

## 项目定位（一句话）

一个跨 50+ Agent Harness 安装的调研技能：`/last30days <话题>` 并行搜 14 个平台（Reddit/X/YouTube/TikTok/HN/Polymarket/GitHub/arXiv…），按**真实人类互动量**（upvote/点赞/真金白银的赔率）排序，AI 评审合成一份带引用的 30 天简报——「Google 聚合编辑，它搜索人」。

## 项目亮点（差异化）

1. **排序信号是钱和注意力，不是 SEO** — Polymarket 赔率有真金白银背书；1500 upvote 的 Reddit 帖 > 没人读的博客；这个信号体系是所有「AI 搜索」里独一份
2. **打通 14 个互相封闭的围墙花园** — ChatGPT 有 Reddit 协议但搜不了 X；Gemini 有 YouTube 但没 Reddit；Claude 全都没有。它用 BYO keys + 浏览器 cookie 把全部桥接给任意 Agent
3. **零配置免费层可用** — Reddit/HN/Polymarket/GitHub 无需任何 key 即跑（公共 JSON/Algolia/Gamma API），30 秒 setup 向导再解锁 X/YouTube/TikTok
4. **SKILL.md 与引擎之间的「契约」工程** — prose 契约 + Python 引擎的分工被明确定义（见源码解读），是 Agent Skills 规范工程化的最佳样本
5. **CONCEPTS.md 定义项目专属词汇表** — Entity grounding、Confidence floor、Nothing-solid 等概念精确到「失败模式往哪个方向退化」的程度，工程文档成熟度罕见

## 核心架构

```
skills/last30days/
├── SKILL.md                       # Agent 面向的 prose 契约（source of truth）⭐
├── scripts/
│   ├── last30days.py              # 引擎主入口（--plan/--competitors-plan/--emit=compact…）
│   ├── briefing.py                # 简报渲染
│   ├── evaluate_search_quality.py # 搜索质量评估（1000+ 测试）
│   └── lib/                       # 平台适配层
│       ├── backends.py / cluster.py / competitors.py
│       ├── bird_x.py（X cookie 认证）/ bluesky.py / arxiv.py
│       └── chrome_cookies.py      # 浏览器会话复用 ⭐
├── agents/openai.yaml             # Codex 适配
└── references/save-html-brief.md
多 Harness 清单：.claude-plugin/ .codex-plugin/ .grok-plugin/ .agents/（一仓四清单）
```

**管线**：话题 → 先做功课（识别相关人物/GitHub 账号/subreddit/X 账号）→ 14 平台并行抓取 → Entity grounding 过滤离题内容 → 跨平台同源合并（cluster）→ 互动量评分排序 → AI 评审合成简报。

## 应用场景与启发

**可用场景**：
- 会前尽调：`/last30days Peter Steinberger` 给出对方近 30 天真实动态（PR 速率/X 争论/播客字幕），LinkedIn 2023 陈旧信息的对立面
- 技术选型/竞品：`A vs B` 一趟并排对比；`--competitors` 自动发现同赛道玩家再跑一轮
- 内容选题：Discovery 模式（无话题）自动从各平台热榜提名「值得研究什么」
- 投资情绪扫描：社群情绪 + Polymarket 赔率的组合视角

**给同类需求的启发**：
1. **「SKILL.md 契约 + 引擎实现」的分层定义**——SKILL.md 告诉模型传什么 flag，引擎产出固定 shape（badge 行/排名证据簇/emoji 树页脚），模型**契约性地必须透传**。做「技能包着脚本」的项目都该这样定义边界，防止模型自由发挥破坏输出
2. **Entity grounding 的保守失败设计**：命中判定只 key 在实体头词上（尾词常是搜索修饰词）；未命中给「决定性降权」使高互动救不回离题内容；但判定门槛刻意保守——失败模式退化为「不罚」，绝不退化为「埋掉正确内容」。任何相关性过滤器都该这样声明退化方向
3. **Nothing-solid 一等公民**：Discovery 零命中时诚实报告「本窗口无可称为趋势的信号」并指出最接近的次阈值候选，而非渲染垃圾——AI 产品「宁可空手不可编造」的范本
4. **Checkpoint 身份绑定**：多腿协议的断点续跑要求每个 host 写入文件回显 bundle id，mock 与 real 状态永不交叉，空状态视为损坏 fail-closed——长流程 Agent 管线的状态管理教科书

## 源码深度解读

### Keyless path（免费层）的工程取舍

无 key 时数据靠爬虫 + RSS，排序退化为本地词法评分（无 LLM 重排）。因此 Entity grounding 等词法防线在免费层最关键——**分层降级时，越往下的层越依赖确定性防线**。Reddit 评论增补预算（comment-enrichment slots）按相关性分配：先过 grounding 的帖子先占坑，不把预算浪费在终将被降权的高热离题帖上。

### 多 Harness 分发（一仓四清单）

`.claude-plugin/`（marketplace）、`.codex-plugin/`、`.grok-plugin/`、`.agents/plugins/` 四套清单指向同一 `skills/` 目录，配合 `npx skills add` 通用安装器覆盖 50+ Harness。AGENTS.md 明言：「这是 Agent Skills 包不是 CLI 工具，产品是斜杠命令，Python 是实现」——定位纪律清晰。

### chrome_cookies.py

X/Twitter 无需 API key：从用户已登录的浏览器提取 cookie 完成认证。「用户已有的会话就是最好的凭证」——绕过平台 API 收费墙的通用思路（合规敏感，项目将选择权交给用户）。

## 全网口碑

- 曾 GitHub Trending 日榜 #1（README 挂 badge），skills.sh 安装量 18K+，评测称「+441 star/天」增长期
- **正面共识**：信息源视角比传统搜索「更全、更具体、更真实」；对开发者话题 Reddit+HN+GitHub 免费层已胜过 Perplexity 免费档（第三方评测原话）；v3「先做功课再搜索」显著提升准确率
- **已核实的问题**（社区评测列举）：实体歧义仍偶发（共享名词拉错实体，首跑建议 sanity check）；输出文件在 `~/Documents/Last30Days/` 无限堆积无内置清理；YouTube 静默丢弃 bug；X 的 CT0 cookie 陷阱
- **风险提示被反复引用**：热度继承热度的毛病——爆红帖可能通篇是错的，社群信号是「值得查证的线索」而非结论

## 竞品对比

| 维度 | last30days | Perplexity | ChatGPT Search | blader/humanizer 等单点技能 |
|------|-----------|-----------|----------------|---------------------------|
| 社交平台覆盖 | ✅ 14 平台含 X/TikTok | ⚠️ 网页为主 | ⚠️ Reddit 协议内 | ❌ |
| 排序信号 | ✅ 真实互动+赔率 | ❌ 相关性 | ❌ | — |
| 运行位置 | ✅ 用户自己的 Agent 内 | ❌ SaaS | ❌ SaaS | ✅ |
| 成本 | ✅ 免费层可用（BYOK 增强）| 免费层受限 | 需订阅 | — |
| 时间窗口 | ✅ 强制 30 天新鲜度 | ⚠️ | ⚠️ | — |

**本仓库关联阅读**：与已入库 `addyosmani-agent-skills`、`obra-superpowers` 同属 Agent Skills 生态顶流，但那些是「工作流技能」，本项目是把**数据获取能力**做成技能的代表——技能生态从「教模型做事」扩展到「给模型接管数据源」的标志。

## 核心研判

**优势**：信号体系（人+钱投票）差异化清晰不可替代；免费层诚意 + 50+ Harness 覆盖带来病毒式增长；工程文档（CONCEPTS/契约/失败模式声明）质量为技能类项目天花板。

**风险/局限**：
1. 平台反爬/API 变更是永恒军备竞赛（X cookie 方案尤其脆弱）
2. 浏览器 cookie 提取的授权边界处于灰色地带，企业环境慎用
3. 热度排序固有偏差：红≠对，投资决策场景必须二次核实
4. 单人维护（Matt Van Horn），55K⭐ 体量下的 bus factor 风险

**趋势判断**：「Agent 技能 = 数据源桥接器」这一形态会被大量复制（垂直版：论文版/财报版/本地生活版）。其 SKILL.md 契约工程和保守失败设计将成为后来者的隐性标准。

## 关键文件路径速查

| 路径 | 作用 |
|------|------|
| `skills/last30days/SKILL.md` | Agent 面向契约（source of truth）⭐ |
| `skills/last30days/scripts/last30days.py` | 引擎主入口 |
| `skills/last30days/scripts/lib/chrome_cookies.py` | 浏览器会话复用认证 ⭐ |
| `skills/last30days/scripts/lib/cluster.py` | 跨平台同源合并 |
| `skills/last30days/scripts/evaluate_search_quality.py` | 搜索质量回归测试 |
| `CONCEPTS.md` | 项目词汇表（Entity grounding / Confidence floor / Nothing-solid）⭐⭐ |
| `CONFIGURATION.md` | 全部 key/cookie 配置说明 |
| `.claude-plugin/` `.codex-plugin/` `.grok-plugin/` `.agents/` | 多 Harness 分发清单 |
