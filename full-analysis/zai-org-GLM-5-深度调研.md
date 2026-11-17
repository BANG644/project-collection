# 🔬 zai-org/GLM-5 — 全方位深度调研（2026-11 重写版）

> GitHub: [zai-org/GLM-5](https://github.com/zai-org/GLM-5)
> ⭐ 7,466 ｜ 🍴 1,024 ｜ 抓取日期 2026-11-18（上次调研 2026-07-24）
> 协议：主体 MIT（GLM-5 / 5.1 / 5.2）；**GLM-5.3 起改为自定义 GLM-5.3 License**
> 一句话定位：智谱（Z.ai）以"复杂系统工程 + 长周期 Agent 任务"为靶心开源的旗舰 MoE 模型家族，用一个仓库承载 GLM-5 → 5.1 → 5.2 → 5.3 → 5.3-Flash 五代权重与部署配方，主打"开源权重逼近闭源前沿的编码/Agent 能力"。
>
> ⚠️ **本次重写相对旧版的核心修正**：旧版停留在 GLM-5.2；仓库主线已迭代到 **GLM-5.3 / 5.3-Flash**（新增混合稀疏+线性注意力、mHC、30T 多模态语料）。旧版缺"项目亮点 / 应用场景与启发"章节、口碑仅链接列表、未说明参数口径分歧——本版全部补齐。

---

## 📌 一句话定位

GLM-5 不是"又一个聊天模型"，而是智谱把全部赌注压在"**让开源模型能像工程师一样连续工作几小时**"的产物：744B 总参 / 40B 激活的 MoE，配合稀疏注意力把长上下文推理成本压到闭源前沿的 1/6～1/20，目标场景是长周期编码 Agent、仓库级改造与多步工具编排。

## ⭐ 项目亮点

1. **长周期 Agent 能力是第一性目标，不是副产品**：官方明确对比"GLM-5 这类模型早早耗尽招式、给更多时间也无济于事"，GLM-5.1 起专门做到"数百轮迭代 + 数千次工具调用 + 单任务持续 8 小时仍持续优化"（README）。这决定了它和"刷单轮 benchmark"的模型根本不在一个赛道。
2. **IndexShare 把 1M 上下文从"规格表数字"变成"用得起"**：每 4 个稀疏注意力层复用同一个 indexer，1M 上下文下单 token FLOPs 降 **2.9×**，是 GLM-5.2 能把上下文从 200K 拉到 1M 的经济性前提（[arXiv 2603.12201](https://arxiv.org/abs/2603.12201)）。
3. **Vending Bench 2 长程经营基准开源第一**：模拟经营一年自动售货机，GLM-5 期末余额 **$4,432.12**，逼近 Claude Opus 4.5（$4,967.06），远超同族 DeepSeek-V3.2（$1,034）（[Hugging Face 模型卡](https://huggingface.co/zai-org/GLM-5)）。
4. **一家公司、五代模型、全部开放权重 + 全栈部署生态**：vLLM / SGLang / KTransformers / Transformers / xLLM / Unsloth 全部适配，还专门覆盖昇腾等 **7 个国产加速器平台** 的 W4A8 量化方案（技术报告）。自托管派系几乎零锁定。
5. **一个仓库 = 权重索引 + 部署配方 + 官方 Skill 目录**：`skills/glm-master-skill/SKILL.md` 是 OpenClaw 生态的 documentation-only 导航技能，串起 GLM-OCR / GLM-Image / GLM-V 全家桶——模型仓本身在往"Agent 能力入口"演化。

---

## 🏗️ 项目架构全景

### 目录结构 + 设计哲学

仓库本体极轻（无训练代码），是**模型分发 + 部署配方仓**，真正的架构在权重与技术报告里：

```
README.md / README_zh.md           # 五代模型介绍 + 基准 + 下载/部署表
example/ascend.md                  # 国产 NPU 部署专章
requirements.txt                   # 工具链依赖
resources/*.png                    # bench / vending / realworld 基准图
skills/glm-master-skill/SKILL.md   # OpenClaw 官方技能导航（不执行脚本）
.github/ISSUE_TEMPLATE/*           # 结构化反馈入口
```

设计哲学很清晰：**把算力花在权重上，把仓库做成最薄的"说明书 + 传送门"**。训练细节（slime 异步 RL、RepoLaunch 环境扩展）外链到独立论文与仓库，本仓只负责"下哪个权重、怎么起服务"。

### 技术栈 & 架构要点

| 项 | GLM-5 / 5.1 / 5.2 | GLM-5.3-Flash（新分支） |
|---|---|---|
| 总参/激活 | 744B / 40B | 320B / 18B |
| 注意力 | MLA + DeepSeek Sparse Attention（DSA）；5.2 加 IndexShare | **稀疏 + 线性混合注意力** + mHC（流形约束超连接） |
| 上下文 | 200K（5/5.1）→ 1M（5.2） | 长上下文服务成本再降 |
| 预训练语料 | 28.5T tokens | **30T token 多模态语料** |
| 权重许可 | MIT | MIT（5.3 本体改为自定义许可，见风险） |

### 参数口径分歧（旧版未提及的独家发现）

官方口径一律写 **744B-A40B**，但 Hugging Face safetensors 组件对 GLM-5 / 5.1 报 **753.9B**，GLM-5.2 四舍五入为 753B——两者 config 文件相同（[morphllm 版本全解](https://morphllm.com/glm-5)）。这不是数据打架，而是"含 embedding / 共享专家的权重计数 vs 官方标称激活规模"两套算法；benchr 直接采用 753B 口径（[benchr 评测](https://benchr.org/ar/articles/glm-5-2-review)）。引用参数时务必注明口径。

---

## 💡 应用场景与启发（重点章节）

### 典型使用场景

- **仓库级长周期编码 Agent**：跨数百文件的大型重构、从 PRD 到可运行全栈项目、连续数小时的调试-修复循环——这是 GLM-5 系列被设计出来的"主场"。GLM-5.2 的 1M 上下文正好装得下整个中型代码库。
- **成本敏感的规模化 Agent 集群**：GLM-5.2 官方 API 定价 **$1.40 输入 / $4.40 输出（每 1M token）**，缓存输入低至 $0.26；对比 Claude Opus 4.8 的 $5/$25，输出侧差 5 倍以上（[orcarouter 评测](https://cms.orcarouter.ai/posts/glm-5-2-review)）。高频工具调用场景下这个差距会被 token 数放大成数量级差异。
- **自托管 / 数据不出域**：MIT 权重 + vLLM/SGLang 全适配 + 昇腾 NPU 方案，适合金融、政务、内网代码库等强合规场景。FP8 版本可落在单节点 8×H200/H20 上（[aiwiki 配置表](https://aiwiki.ai/wiki/glm_5/revisions/4)）。
- **安全研究 / 漏洞发现**：GLM-5.3 在 CyberGym 达 SOTA，官方称用它发现 269 个开源项目的 2,436 个漏洞并建了披露账本 `cvd.z.ai`（[morphllm](https://morphllm.com/glm-5)）。

### 可借鉴的解决方案模式

1. **"能力靠后训练、架构只做一次"的迭代经济学**：GLM-5.3 明确复用 GLM-5.2 的 base 模型，全部增益来自 post-training（Z.ai Code Bench +50%）。这给资源有限团队的启发是——**与其反复预训练，不如把预算压在 RL/后训练环境与数据上**。技术报告披露他们构建了 **10,000+ 可验证可执行 SWE 环境**（9 种语言，RepoLaunch + Harbor 格式终端环境），这才是"后训练杠杆"的真正底座。
2. **上下文成本要靠架构而不是靠堆卡**：从 DSA → IndexShare → GLM-5.3-Flash 的线性/稀疏混合注意力，三代都在攻同一个点——把注意力从 O(L²) 拉向线性。**结论：长上下文产品的胜负手是注意力索引策略，不是显存采购预算。**
3. **上下文管理 > 模型本身**：技术报告指出，仅靠改进 context-management 策略就把 BrowseComp 从 55.3 提到 62.0。做 Agent 应用时，"给模型看什么"往往比"换更大的模型"更划算。

### 同类需求的可参考思路

- 想做**国产化替代**：GLM-5 的 7 平台适配 + W4A8 量化章节，是一份罕见的"前沿模型落到国产芯"工程范本，值得逐节抄作业。
- 想做**Agent 评测体系**：Vending Bench 2（长程经营）、Terminal-Bench 2.1（真实终端任务）、MCP-Atlas、τ²-Bench 这套"agent-shaped benchmark"组合，比传统静态 QA 更贴近生产。可以照搬它的评测维度设计自己的 Agent 回归测试。
- 想做**模型家族技能生态**：`skills/glm-master-skill` 用"documentation-only master skill + Clawhub 分发"的轻模式串起十多个官方技能，是"一个入口技能导航全家桶"的可复用范式。

### 可复用片段

vLLM 启动配方（README 原文骨架）——投机解码 + 工具解析 + 推理解析缺一不可，是 GLM-5 系列跑 Agent 的标准姿势：

```bash
vllm serve zai-org/GLM-5 \
  --tensor-parallel-size 8 \
  --gpu-memory-utilization 0.85 \
  --speculative-config.method mtp \
  --speculative-config.num_speculative_tokens 3 \
  --tool-call-parser glm47 \
  --reasoning-parser glm45 \
  --enable-auto-tool-choice \
  --served-model-name glm-5
```

---

## 🧠 核心源码解读（克制代码量：本仓无训练代码，精读部署契约与技能骨架）

### 入口与主流程

README 是唯一主入口；真正的"可执行逻辑"藏在两个契约里：**推理努力度参数**（`reasoning_effort` / `clear_thinking`）与 **SKILL.md 导航契约**。

### 关键模块 1：推理努力度契约（README "Note" 段）

这是最容易被忽略、却直接影响成本与复现的隐藏规则：

| 模型 | `reasoning_effort` 取值 | 默认值 | 行为 |
|---|---|---|---|
| GLM-5.2 | 仅 `high` / `max` | `max` | 传其他值走 fallback |
| GLM-5.3 / 5.3-Flash | `low` / `high` / `max` | 未传或非法值 → `max` | 需显式传 `low`/`high` 才生效 |
| chat 模板 | `clear_thinking` 默认 `false` | 聊天场景须显式传 `true` | 否则思考链残留 |

设计意图很清楚：**默认保 benchmark 可复现性（max），把省钱/加速的选择权交给调用方显式声明**。做集成时若不显式设置，你付的是"最贵但最稳"的档位——这是账单失控的常见根因。

### 关键模块 2：`skills/glm-master-skill/SKILL.md`（文档型主技能）

```yaml
name: glm-master-skill
description: Documentation-only master skill for GLM ecosystem discovery
---
# 三条硬约束
✅ 介绍可用技能   ✅ 提供官方安装链接/命令   ❌ 不执行任何本地脚本 / subprocess
metadata.openclaw.requires: { env: [], bins: [] }   # 零依赖声明
```

它把 GLM-OCR（5 技能）、GLM-Image（1）、GLM-V（9，含 resume-screen / pdf-to-ppt / prd-to-app / web-replication）编成目录，安装走 `npx clawhub@latest install <skill-name>`。**模式亮点**：用 `requires: {env:[], bins:[]}` 显式声明零环境依赖，让"—技能只是导航，不碰你的系统"成为可被工具链校验的契约，而非一句口头承诺。

### 隐藏功能 & 未文档化特性

- 仓库 `example/ascend.md` 藏着完整的昇腾 NPU 部署路径（vLLM-Ascend / xLLM / SGLang），README 只给了一行链接——做国产化落地时这是必读文件。
- 微调侧除官方 slime（v0.3.0+）外，README 还列了 ms-swift（v4.4.0+）支持 SFT/PPO/GRPO，但没展开——实际是给"不想碰 RL 框架"的团队留的 SFT 捷径。
- `resources/bench_53.png`、`realworld_bench.png` 等图是官方唯一公开的长程/真实世界评测可视化，文字版基准表并不包含这些维度。

---

## 📐 架构决策与设计哲学

- **决策一：MoE 堆总参、压激活数**（744B / 40B，256 路由专家 + 1 共享，80 层）。层数是特意压到 80 以减少专家并行通信开销（aiwiki）。取舍是：训练容量拉满，但自部署门槛也拉满。
- **决策二：注意力走稀疏化而非稠密化**（MLA + DSA，再到 IndexShare、混合线性）。每一代都在降"每 token 成本"，而非单纯提指标。
- **决策三：上下文分阶段扩展**（32K over 1T tokens → 128K over 500B → 200K over 50B，再叠加 160B 软件工程数据）。一次性拉到长上下文会稀释质量，分阶段是工程共识。
- **决策四（争议）：GLM-5.3 换用自定义 License**。5.2 及之前是 MIT，5.3 本体改为自定义 GLM-5.3 License（5.3-Flash 仍 FLOSS），社区已在仓库开 issue 质疑"为什么突然专有化"（[morphllm](https://morphllm.com/glm-5)）。选型时务必逐版本核对许可，别默认"GLM 系列都 MIT"。
- **负面结果也公开**：技术报告坦承稀疏注意力在 RL 中需要"确定性 top-k 操作"才稳定——这类诚实披露在厂商报告里很罕见（[beri 报告解读](https://www.beri.net/learning/glm-5-technical-report)）。

---

## 🌐 全网口碑画像

### 好评共识

- **Vercel CEO Guillermo Rauch** 在 X 上公开表示对 GLM-5.2 的编码表现 "impressed"；前 Meta / Google DeepMind / Microsoft 高管 **Matt Velloso** 用它工作一整天后称其达到"日常可用"门槛（[neomanex](https://neomanex.com/news/z-ai-glm-5-2-coding-model)）——这是开源模型难得的"业内一号位"背书。
- **orcarouter 编辑评分 ~8.5/10**：成本效率 10/10、编码 9/10、上下文 9/10，评价其为"第一个接近前沿到可以当默认、而非妥协方案的开源权重模型"（[orcarouter](https://cms.orcarouter.ai/posts/glm-5-2-review)）。
- **中文实测（极客日志）** 对比 MiniMax M2.5：GLM-5 在复杂 3D 场景生成"完成度高、空间推理明显更优"，在财务分析 Agent 的 PPT"图文并茂、结论有洞察"，被总结为"走大而全路线的开源六边形战士"（[zeeklog](https://v1.zeeklog.com/guo-chan-aishuang-xiong-dui-jue-zhi-pu-glm-5yu-minimax-m2-5-5)）。

### 差评共识 & 踩坑高发区

- **benchmark 全是厂商自报**：benchr 明确标注所有分数来自 Z.ai 自己的运行，"是带具名基准的厂商声明，比无名营销数字强，但仍是一家之言，不构成独立验证"（[benchr](https://benchr.org/ar/articles/glm-5-2-review)）。Eden AI 更尖锐：Z.ai 发布时没给分数，数字主要来自 BenchLM / llm-stats 等第三方 tracker（[Eden AI](https://edenai.co/post/glm-5-2-benchmark-vs-gpt-5-5-claude-opus-4-8-and-gemini-3-1-pro)）。**复现前别把 81.0 当金标准。**
- **体量劝退个人**：benchr 直言 753B "不是游戏显卡能跑的，MIT 也救不了"，多卡服务器或 API 才是现实路径。
- **速度是短板**：orcarouter 给速度/首 token 延迟仅 7/10，称其是"thinking-first 模型"，快速任务要手动调低 effort——与"默认 max"形成隐性成本陷阱。
- **纯文本**：无图像输入，截图驱动 / 文档视觉工作流需另配模型。

### 争议焦点

- **许可转向**：5.3 从 MIT 改自定义 License，与"全系自由软件"的社区预期冲突（morphllm 记录的 open request）。
- **"最强开源编码模型"名号**：BenchLeader 数据显示 GLM-5 与 GLM-5.2 在误差带内互有胜负（60.2 vs 58.9），GLM-5 在推理/数学/知识领先，5.2 在编码/Agent/长上下文领先——**"哪代最强"取决于用例，不是一句话能定的**（[BenchLeader](https://www.benchleader.com/compare/glm-5-vs-glm-5-2)）。

### 维护者响应风格

Issue 模板结构化（bug-report / feature-request 分列），社区活跃于微信 + Discord。技术报告以 270 作者署名、v2 修订（2 月 17 日提交、2 月 24 日修订），体现"论文级严谨 + 快速迭代"的双轨风格。

---

## ⚔️ 竞品对比

| 维度 | GLM-5.2/5.3 | DeepSeek-V3.2/R1 | Qwen3-Max | Kimi K2.5 | Claude Opus 4.8 |
|---|---|---|---|---|---|
| 权重/许可 | 开源 MIT（5.3 例外） | 开源 MIT | 部分开源 | 开源 | 闭源 |
| 总参/激活 | 744B/40B | 671B/37B | — | — | 未公开 |
| 上下文 | 1M（5.2 起） | 128K/256K | 256K | 200K+ | 200K |
| Terminal-Bench 2.1 | **81.0** | ~39–50 | ~54 | ~50.8 | **85.0** |
| 长程经营(Vending Bench 2) | **$4,432（开源第一）** | $1,034 | — | $1,198 | $4,967（4.5） |
| 输出价/1M | $4.40 | 低 | 低 | 低 | $25 |
| 自部署 | 难（744B）/ Flash 更易 | 难 | 中 | 中 | 不可 |
| 国产芯片适配 | **7 平台 + W4A8** | 有 | 有 | 有 | 无 |

### 选择建议

- **自托管 + 长上下文 + 编码 Agent** → GLM-5.2/5.3，尤其需要国产芯片适配时几乎无替代。
- **极致成本 + 数学/推理** → DeepSeek 系或 GLM-5 基础版（BenchLeader 显示 GLM-5 在 reasoning 68、math 63 上领先 5.2）。
- **可靠性优先 / 多模态 / 企业 SLA** → Claude Opus 4.8 / GPT-5.5 / Gemini 3.1 Pro，最难的 agentic 编排与工具调用仍是闭源更强。
- **快速原型 / 高频短任务** → MiniMax M2.5（中文实测开发速度约 30 分钟 vs GLM-5 的 2.5 小时），GLM-5 更适合需长期维护的生产级项目。

---

## 🎯 核心研判

### 项目优势（不可替代的价值点）

- **长周期 Agent 能力 + 开源权重 + 极低推理成本**三者同时成立的模型极少；IndexShare 让 1M 上下文从"能跑"变"跑得起"，这是结构性优势。
- **国产芯片全栈适配**是地缘不确定性下的稀缺确定性，对国内政企落地价值极高。
- **月更节奏 + 论文级技术报告 + 负面结果公开**，工程可信度高于同规模闭源黑盒。

### 项目风险（潜在隐患和局限性）

- **厂商自报基准缺独立验证**，81.0 / 62.1 等数字需自行复现；GLM-5.3 分数甚至有第三方 tracker 与官方口径不一致的情况。
- **许可转向**（5.3 自定义 License）打破"全系 MIT"预期，商业选型须逐版本审法务。
- **744B 体量 + thinking-first 延迟**，个人与小团队实际只能用 API 或等 Flash 版。
- **迭代过快导致文档滞后**：本仓 README 已到 5.3，但大量中文教程与第三方评测还停留在 5/5.2——信息半衰期极短。

### 适用场景 & 不适用场景

✅ 适合：仓库级编码 Agent、长周期自主任务、成本敏感的 Agent 集群、国产化自托管、安全研究。
❌ 不适合：个人单机尝鲜、需要图像输入的视觉工作流、要求 SLA 与合规背书的关键业务、追求首 token 低延迟的交互场景。

### 趋势判断（上升期）

GLM-5 家族处于**高速上升期**：5 → 5.3-Flash 半年五代，能力曲线陡峭，生态位从"开源替代"向"默认选项"迁移。但要警惕两点——许可碎片化与基准可信度，这两件事会决定它能否从"技术领先"转成"企业标配"。

---

## 📂 关键文件路径速查

| 路径 | 用途 |
|---|---|
| `README.md` / `README_zh.md` | 五代模型介绍、基准表、下载与部署总入口 |
| `skills/glm-master-skill/SKILL.md` | 官方技能导航（documentation-only，串 GLM-OCR/Image/V） |
| `example/ascend.md` | 昇腾等国产 NPU 部署专章（README 未展开） |
| `resources/bench_53_2.png` / `bench_53.png` | 5.3 / 5.3-Flash 官方基准可视化 |
| `resources/vending_bench.png` / `realworld_bench.png` | 长程经营与真实世界评测图 |
| `resources/bench_52.png` / `bench_51.png` | 5.2 / 5.1 基准图 |
| `requirements.txt` | 工具链依赖 |
| `.github/ISSUE_TEMPLATE/{bug_report,feature-request}.yaml` | 结构化反馈入口 |
| 外部：[arXiv 2602.15763](https://arxiv.org/abs/2602.15763) | GLM-5 技术报告（270 作者，2 月 v2） |
| 外部：[arXiv 2603.12201](https://arxiv.org/abs/2603.12201) | IndexShare 论文（1M 上下文 2.9× FLOPs 降） |
| 外部：[THUDM/slime](https://github.com/THUDM/slime) | 官方异步 RL 训练框架 |

---

## 📎 数据来源与可信度说明

本报告数据来自 2026-11-18 实时抓取：GitHub API（仓库元数据、文件树、README、SKILL.md）+ 8 个独立信息源（BenchLeader / benchr / orcarouter / neomanex / Eden AI / morphllm / aiwiki / 极客日志）。所有基准分数均标注为**厂商自报**或**第三方评测**，未做独立复现。GLM-5.3 具体基准数值以官方 `resources/bench_53_*.png` 为准，文字版 third-party 数据存在口径差异，已在上文标注。
