# xbtlin/ai-berkshire - 全方位深度调研

> 调研日期：2026-06-27 | Stars: ~3,000 (快速上涨中，2026 年 4 月立项) | 语言：Python | 许可证：MIT
> GitHub: https://github.com/xbtlin/ai-berkshire

## 一句话定位

**AI Berkshire 是一套基于 Claude Code Skill 范式构建的价值投资研究框架**——它不推荐股票，而是将巴菲特、芒格、段永平、李录四位大师的方法论工程化为 16 个可执行的 AI Skill，通过 "4 Agent 并行对抗 + Python 精确计算 + 镜子测试决策纪律"，把 "AI 看起来对的投研分析" 变成 "可验证、可决策的研究报告"。

---

## 项目架构全景

### 目录结构

```
ai-berkshire/
├── skills/                    ← 16 个 Skill 定义（.md），复制到 ~/.claude/commands/ 使用
│   ├── investment-research.md ← 单公司全方位深度研究（7 模块）
│   ├── investment-team.md    ← 4 Agent 并行多视角
│   ├── investment-checklist.md ← 巴菲特 6 关 Checklist
│   ├── industry-research.md  ← 产业链全景扫描
│   ├── industry-funnel.md    ← 行业漏斗 30→10→3
│   ├── earnings-review.md    ← 财报精读
│   ├── earnings-team.md      ← 四大师并行财报解读
│   ├── portfolio-review.md   ← 组合审视+再平衡
│   ├── thesis-tracker.md     ← 买入后纪律跟踪
│   ├── news-pulse.md         ← 股价异动快速归因
│   ├── management-deep-dive.md ← 管理层纵深研究
│   ├── private-company-research.md ← 未上市公司研究
│   ├── deep-company-series.md ← 公众号级 8 篇长文
│   ├── dyp-ask.md            ← 段永平问答
│   ├── quality-screen.md     ← 去劣快速筛选
│   └── financial-data.md     ← 财务数据获取+交叉验证
├── tools/
│   └── financial_rigor.py    ← Python CLI：精确十进制计算/市值验算/三情景/Benford
├── reports/                   ← 投资研究报告输出（按公司名建文件夹）
│   ├── 拼多多/               ← /investment-team 真实输出
│   ├── 腾讯/                 ← /investment-research 真实输出
│   ├── AI产业研究/            ← AI 五层蛋糕全产业链
│   └── ...
├── data/                      ← 基础数据文件
├── assets/                    ← 图片/架构图
├── CLAUDE.md                  ← Claude Code 项目指令（客观性原则+命名规范）
├── ai_CLAUDE.md              ← AI Agent 专用配置
├── docs/ROADMAP.md            ← 路线图
└── RKLB-investment-research.md ← 火箭实验室单公司研究
```

### 三层架构设计

```
┌─────────────────────────────────────────────────────────┐
│              Skill 层（16 个入口）                        │
│  封装 5 类场景的完整工作流：深度研究/财报分析/行业筛选/    │
│  持仓管理/思维工具                                         │
├─────────────────────────────────────────────────────────┤
│              Agent 层（4 个并行视角）                      │
│  段永平(商业模式) 巴菲特(财务估值) 芒格(逆向思考) 李录(长期) │
│  独立搜索 → 独立分析 → 独立判断 → 独立评分                │
│  Team Lead 汇总综合报告                                   │
├─────────────────────────────────────────────────────────┤
│              工具层（Python decimal.Decimal）              │
│  financial_rigor.py: 市值验算/三情景估值/多源交叉/Benford  │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

- **Skill 定义**：Markdown + YAML Front Matter（Claude Code Skill 规范）
- **计算工具**：Python 3 + `decimal.Decimal`（精确十进制，避免浮点误差）
- **输出格式**：Markdown 报告（按公司名建文件夹）
- **数据源**：WebSearch 多源交叉验证

---

## 核心源码解读

### 4 Agent 并行对抗机制

这是 AI Berkshire 区别于 "用 AI 问巴菲特怎么看某公司" 的核心设计。以拼多多为例，4 个 Agent 的独立判断和真实冲突：

| Agent | 视角问题 | 拼多多评分 | 核心判断 |
|-------|---------|-----------|---------|
| **段永平** | 这门生意本质是什么？用户为什么用？ | 3.7/5 | C2M 模式难以复制，平台型生意 |
| **巴菲特** | 护城河多宽？现金流多稳？估值多便宜？ | 4.4/5 | 扣现金 PE 仅 6.3x，印钞机级别 |
| **芒格** | 什么情况下这家公司会死？护城河太浅？ | 3.5/5 | 抖音 3 年做到 4 万亿 GMV，护城河比想象浅 |
| **李录** | 管理层文化如何？10 年后还在吗？ | 2.0/5 | 管理层文化有隐患，10 年确定性不足 |

**关键设计**：
- 每个 Agent 拿独立的 context window + 独立 system prompt + 独立工具集
- **不是**一个 prompt 拆 4 段，而是**真的独立搜索**——4 个 Agent = 4 倍搜索量 + 4 个独立视角
- Team Lead 综合时保留冲突，不强行 "平均" ——巴菲特说 "真便宜"（4.4），李录说 "不确定就不买"（2.0），这种**视角冲突才是投资决策的真实状态**

### financial_rigor.py 工具详解

这是解决 "LLM 心算不可靠" 的工程利器。5 个核心命令：

| 命令 | 解决的问题 | 示例使用 |
|------|-----------|---------|
| `verify-market-cap` | 股价 × 总股本精确验算，检测单位错误（港币/人民币混淆） | `python3 tools/financial_rigor.py verify-market-cap --price 510 --shares 9.11e9 --reported 4.65e12 --currency HKD` |
| `verify-valuation` | PE/PB/ROE/FCF Yield 精确十进制替换 LLM 浮点近似 | `decimal.Decimal` 确保 0.1+0.2=0.3 |
| `cross-validate` | N 个来源同一数据自动比对，>1% 告警 | 多家数据源 PE 对比 |
| `three-scenario` | 乐观/中性/悲观三情景精确计算目标价 | 估值必用 |
| `benford` | Benford 定律检测财务数据首位数字分布异常 | 财报造假检测 |

**设计原则**：所有计算用 Python `decimal.Decimal` 精确十进制，不用 `float` 浮点近似。这是一个被绝大多数 AI 投研工具忽略的细节——LLM 直接心算 PE，市值单位搞混港币人民币，整个分析可能都是错的。

### 镜子测试（Mirror Test）

所有 Skill 的最终输出都强制通过 "镜子测试"——5 句话说不清就不买：

> "我以 380 港元买入腾讯，因为：
> 1. 这门生意的本质是**社交网络+数字内容平台**，我理解它
> 2. 它的护城河是**12 亿用户的社交关系链**，而且在变宽
> 3. 管理层 **Pony Ma 低调务实、资本配置优秀**，值得信赖
> 4. 当前价格相当于内在价值的 **8 折**，有一定安全边际
> 5. 即使我错了，下行风险可控，因为**账上净现金超 2000 亿、游戏现金流强劲**"

这是反 AI 幻觉的关键设计——AI 分析看起来都对，但没法用来决策，因为答案里没有 "我愿意为这个判断押多少钱"。

### 投研分析核心原则（CLAUDE.md 第一条）

```
- 客观、客观、客观——所有分析必须基于事实和数据
- 严格区分"事实"与"观点"
- 不预设立场——先摆数据、再推逻辑、最后得结论
- 禁止"我认为""我觉得""显然"
- 呈现正反两面——每个核心判断附带反面论据
- 对不确定的事情诚实说"不确定"或"数据不足"
```

### 16 个 Skill 按场景分类

| 分类 | Skill | 说明 |
|------|-------|------|
| **深度研究**(5) | `/investment-research` `/investment-team` `/management-deep-dive` `/private-company-research` `/deep-company-series` | 从单公司快速研究到公众号级 12 万字长文 |
| **财报分析**(2) | `/earnings-review` `/earnings-team` | 只读原始财报，不依赖二手研报 |
| **行业筛选**(4) | `/industry-research` `/industry-funnel` `/quality-screen` `/investment-checklist` | 全市场→10→3→1 的漏斗流程 |
| **持仓管理**(3) | `/portfolio-review` `/thesis-tracker` `/news-pulse` | 买入后的纪律系统 |
| **思维工具**(2) | `/dyp-ask` `/financial-data` | 段永平思维 + 数据严谨性 |

### 行业漏斗机制

`/industry-funnel` 是 "AI 漏斗" 做对的关键——强制每层留下/淘汰标准，淘汰的标的写明理由：

```
全市场 → 粗筛≤10 → 精细≤10 → 终选 3 家（高确定性 + 中等弹性 + 高弹性）
```

终选按 "组合互补性" 而非 "打分前 3 名" ——这是单一 Agent 做不到的组合配置视角。

---

## 全网口碑画像

### 好评共识

1. **"不是 AI 推荐股票，是把投资纪律工程化"** — txtmix 深度分析的核心判断：AI Berkshire 解决的不是 "AI 能不能分析公司"（AI 本就能），而是 "AI 给的能不能用来做决策"（这需要工程化纪律）
2. **4 Agent 对抗机制解决了单一视角盲点** — 多 Agent 并行在投研场景的适配度极高，每个 Agent 的系统 prompt 极简（只需写清大师的思维锚点），不需要 2000 字复杂 prompt
3. **financial_rigor.py 是 "隐形杀手"** — 浮点近似误差在 AI 投研场景被严重低估，Decimal 精确计算 + 多源交叉验证才是这类工具的护城河
4. **实盘收益佐证** — README 展示 2024 年 +69.29%、2025 年至今 +66.38% 的真实账户截图，虽不是投资建议，但为方法论提供了实证锚点
5. **"镜子测试"是反 AI 幻觉的优雅设计** — 5 句说不清就不买，把研究和决策强制绑定

### 争议与风险

1. **实盘收益的因果归属** — +69.29% 的 2024 年收益在 AI 科技股牛市中是否主要来自市场 Beta 而非框架 Alpha？披露不足
2. **高质量投资研究的门槛** — 这套框架假设用户理解价值投资基础概念（护城河、安全边际、能力圈），完全不读价值投资经典的用户可能使用不当
3. **数据获取依赖 WebSearch** — 当前版本通过 WebSearch 获取财务数据，路线图中的 "Wind/Bloomberg/Yahoo Finance MCP 接入" 尚未实现
4. **投资决策的法律责任边界模糊** — AI 生成的研究报告如果被用户当作投资建议并造成损失，责任的归属未明确

### 社区活跃度

- 2026 年 4 月 7 日立项，不到 3 个月 3K+ Stars
- 快速出现在 GitHub Trending (Python)
- txtmix、ngjoo、opensource-hub 等独立技术博客深度分析
- reports/ 目录有大量真实研究报告产出（腾讯、拼多多、AI 产业等）

---

## 竞品对比

| 维度 | AI Berkshire | FinGPT | OpenBB Terminal | 通用 LLM 投研 |
|------|-------------|--------|----------------|--------------|
| **定位** | 价值投资研究框架 | AI 金融大模型 | 开源 Bloomberg 终端 | Prompt 工程 |
| **架构** | Skill+Agent+Tool 三层 | 单模型微调 | GUI+SDK | 单次对话 |
| **视角对抗** | ★★★★★ 4 大师并行 | ★ 无 | ★ 无 | ★ 无 |
| **金融精确度** | ★★★★★ Decimal 计算 | ★★★★ 模型固有 | ★★★★★ 终端级 | ★ 心算不可靠 |
| **决策纪律** | ★★★★★ 镜子测试 | ★ 无 | ★ 无 | ★ 无 |
| **学习曲线** | ★★★★ 需懂价值投资 | ★★★ 需懂 FinGPT API | ★★★★★ 需要金融知识 | ★★ 低 |
| **数据源** | ★★★ WebSearch | ★★★★ 内部数据 | ★★★★★ 多源 API | ★★ 训练截止 |
| **实盘验证** | ★★★ README 展示 | ★ 无 | ★ 无 | ★ 无 |
| **开源** | ✅ MIT | ✅ Apache 2.0 | ✅ MIT | ❌ |

### 选择建议

- **选 AI Berkshire**：你认同价值投资框架，想用 AI 把研究流程系统化、可复用
- **选 FinGPT**：你需要一个可微调的金融 NLP 模型做情感分析/新闻摘要
- **选 OpenBB**：你需要 Bloomberg 级别的数据终端功能
- **用通用 LLM**：你只是偶尔想问 "某公司怎么样"

---

## 核心研判

### 项目优势（不可替代的价值）

1. **4 Agent 对抗视角是真正的方法论创新**——解决了 "单一 AI 视角给出看似正确但缺盲点的分析" 这一核心问题
2. **financial_rigor.py 是工程壁垒**——Decimal 精确计算 + 多源交叉验证 + Benford 检测，把 LLM 投研最易出错的环节（浮点误差/单位混淆）工程化杜绝
3. **镜子测试把研究→决策的最后一公里打通**——AI 分析质量再高，不能用来做决策就是无效的
4. **Skill 分类覆盖完整投研周期**——从发现→研究→决策→跟踪→退出，16 个 Skill 全覆盖

### 项目风险

1. **收益归因不足**——实盘收益未做 Beta/Alpha 拆解，无法区分框架贡献 vs 市场贡献
2. **数据源瓶颈**——WebSearch 作为唯一数据来源在严谨性上不足，Wind/Bloomberg MCP 接入是关键
3. **单人维护**——xbtlin 作为主要维护者，社区贡献结构不透明
4. **在熊市中的表现未知**——框架主要在 2024-2025 牛市中运行，逆向市场中的效果未经验证

### 趋势判断

**快速上升期，有望成为 AI + 价值投资研究的范式示范**。3K Stars 在 3 个月内积累，增长曲线陡峭。关键变量：能否接入权威金融数据源（Wind/Bloomberg），以及在下一轮熊市中能否证明框架的逆向投资价值。

### 适用场景
- 认同价值投资框架的独立投资者
- 需要把投研流程系统化的研究团队
- 想学习"如何用 AI Agent 做深度研究"的技术人员（架构示范价值高）

### 不适用场景
- 短线/量化/高频交易
- 完全没读过《聪明的投资者》或巴菲特致股东信的用户
- 寻找 "AI 推荐股票" 的工具（它不推荐，只生成可决策的研究报告）
- 投资金额 < 100 万的研究深度边际效益不够

---

## 关键文件路径速查

| 文件 | 用途 | 重要度 |
|------|------|--------|
| `CLAUDE.md` | Claude Code 项目指令（客观性原则） | ⭐⭐⭐⭐⭐ |
| `skills/investment-team.md` | 4 Agent 并行旗舰 Skill | ⭐⭐⭐⭐⭐ |
| `skills/investment-research.md` | 单公司 7 模块深度研究 | ⭐⭐⭐⭐ |
| `tools/financial_rigor.py` | 金融精确计算 CLI | ⭐⭐⭐⭐⭐ |
| `assets/architecture.mmd` | Mermaid 架构图源码 | ⭐⭐⭐⭐ |
| `docs/ROADMAP.md` | 路线图（MCP 数据源接入等） | ⭐⭐⭐ |
| `reports/拼多多/` | /investment-team 真实输出 | ⭐⭐⭐⭐⭐ |
| `reports/腾讯/` | /investment-research 真实输出 | ⭐⭐⭐⭐ |
| `reports/AI产业研究/` | AI 五层蛋糕全产业链 | ⭐⭐⭐⭐ |
| `data/watchlist.json` | 自选股配置 | ⭐⭐⭐ |
| `README.md` | 项目总览 + 实盘收益 | ⭐⭐⭐⭐⭐ |
