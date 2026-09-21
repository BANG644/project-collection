# HKUDS/ClawWork 深度调研

> 调研日期：2026-09-22 ｜ 定位：把 AI 助手变成"会赚钱的 AI 同事"的经济 accountability 基准与运行时 ｜ Stars：8,550 ｜ 语言：Python ｜ 许可：MIT ｜ 默认分支：main ｜ 最近活跃：2026-03

## 一、项目定位（一句话）

ClawWork 是 HKUDS（香港大学数据科学实验室）开源的一个**经济生存基准 + 运行时封装**：把通用 AI 助手（基于 nanobot）包装成"AI Coworker"，让它在真实专业任务（GDPVal 220 题 / 44 个职业）中靠产出赚钱、为每次 token 付费，用"能否活下来"衡量 agent 的真实生产力。

## 二、项目亮点（差异化）

- **经济 accountability 范式**：agent 起步只有 $10，每产生一个 token 就扣费，收入只来自"高质量完成专业任务"——把"agent 到底有没有用"翻译成可量化的盈亏表，而非跑分榜。
- **真实经济基准 GDPVal**：直接复用 OpenAI 的 GDPVal 数据集（220 个真实职业任务、44 个行业），付款 = `质量分 × (估算工时 × BLS 时薪)`，单任务价值 $82–$5004。
- **ClawMode 即插即用**：`clawmode_integration` 把任意在运行的 nanobot 网关包成"会算账的同事"，自带 `/clawwork` 命令与成本脚注（`Cost: $0.0075 | Balance: $999.99 | Status: thriving`）。
- **多层评估维度**：存活天数、最终余额、利润率、token 效率、工作质量、活动配比（work vs learn），而非单点准确率。
- **领英式榜单叙事**：README 主打"$19K in 8 Hours"，ATIC+Qwen3.5-Plus 榜首余额 $19,915——传播力强、争议也大（自报数据）。

## 三、核心架构

```
ClawWork Agent（每日循环）
  ├─ decide_activity(work|learn)    # 战略取舍：立即赚钱 or 投资学习
  ├─ submit_work(产出, 附件)        # LLM 评估 → 按质量付款
  ├─ learn(topic)                   # 持久化知识到记忆
  ├─ get_status()                   # 余额/成本/生存档位
  ├─ search_web / create_file / execute_code_sandbox / create_video
  └─ Economic Tracker（每轮 LLM 调用后扣费）
        │
   FastAPI + WebSocket ──→ React Dashboard (localhost:3000 实时看板)
        │
   ClawMode 包装 nanobot gateway ──→ TrackedProvider 拦截每次 LLM 调用扣费
```

- **基准内核 `livebench/`**：`agent/live_agent.py`（编排器）、`agent/economic_tracker.py`（余额/成本/收入）、`work/task_manager.py`（GDPVal 任务加载与派发）、`work/evaluator.py`（GPT-5.2 按 44 行业 rubric 评分）。
- **工具层 `livebench/tools/`**：`direct_tools.py`（decide/submit/learn/status）+ `productivity/`（search_web、create_file 生成 docx/xlsx/pdf、execute_code_sandbox 用 E2B/BoxLite 沙箱、create_video）。
- **集成层 `clawmode_integration/`**：`agent_loop.py`（ClawWorkAgentLoop + `/clawwork` 命令）、`task_classifier.py`（40 类职业分类器）、`provider_wrapper.py`（TrackedProvider 成本拦截）、`cli.py`（`python -m clawmode_integration.cli agent|gateway`）。
- **看板 `frontend/`**：React + WebSocket 实时推送余额曲线、活动分布、任务与学习时间线。

## 四、应用场景与启发

- **评估你的 agent 真值不值钱**：当你想比较"GPT vs Claude vs Qwen 当打工人谁更划算"，ClawWork 提供了一套可直接复用的经济记账骨架（TrackedProvider + Economic Tracker）——可迁移到任何 agent 框架做成本/质量联合评估。
- **"会算账的 agent"产品化思路**：ClawMode 的 `/clawwork` + 成本脚注模式，是给客服/运营 agent 加"经济约束"的现成参考（做多少活收多少钱、亏了就停）。
- **学习-工作权衡建模**：`decide_activity` 把"短期收益 vs 长期能力投资"显式化为决策工具，对搭"自主学习 agent"有借鉴。

## 五、源码深度解读（关键片段）

`clawmode_integration/provider_wrapper.py` 的 TrackedProvider 是"经济 accountability"的核心——它包裹 nanobot 的 LLM provider，在每次 chat completion 返回后从 agent 余额扣除真实成本：

```python
# 伪代码示意（来自 README 描述 + provider_wrapper 命名）
class TrackedProvider:
    def create_completion(self, *args, **kwargs):
        resp = self.inner.create_completion(*args, **kwargs)
        cost = price_of(resp.usage)          # 含 thinking token
        self.economic_tracker.deduct(cost)   # 余额不足 → Status: struggling/bankrupt
        return resp
```

`livebench/work/evaluator.py` 用 `meta_prompts/` 下按行业分类的 rubric 做 LLM-as-judge，评分写入 `task_completions.jsonl`；付款公式在 `scripts/calculate_task_values.py`：`BLS_hourly_wage × estimate_task_hours.py 估算工时 × 质量分`。

## 六、全网口碑

- **正面**：HKUDS 实验室出品、叙事抓人（"AI 同事 8 小时赚 $19K"），把"agent 经济可行性"做成可复现实验，社区有飞书/微信/Discord 群；被多家 agent 评测文章引用为"经济生存基准"范本。
- **争议/风险**：榜单为自报、无可独立复现的第三方审计；强依赖 OpenAI（GPT-4o agent + GPT-5.2 评估）与 E2B 沙箱（默认），本地化/国产模型接入需改 `TrackedProvider`；仓库最近一次提交在 2026-03，迭代放缓。

## 七、竞品对比与核心研判

| 维度 | ClawWork | WebArena / τ-bench / AgentBench | 通用 agent 框架 |
|------|----------|--------------------------------|----------------|
| 评价对象 | 经济存活（钱） | 任务成功率 | 能力/跑分 |
| 环境 | 真实专业任务(GDPVal) | 受控 Web/工具环境 | 自定义 |
| 可复现成本 | ✅ 真实扣费 | ❌ | ❌ |

**竞品**：AgentBench、WebArena、τ-bench、OpenAI GDPVal（仅数据集）均不做"经济存活"维度；ClawWork 的独特价值是把会计账本塞进 agent 循环。

**核心研判**：⭐⭐⭐⭐ — 作为"agent 经济价值"的研究基准与叙事样本非常出色，其 **TrackedProvider + Economic Tracker 的算账范式**值得任何做"付费 agent / 自主打工 agent"的团队抄作业；但作为生产系统偏重（OpenAI+E2B 硬依赖、维护放缓），更适合当方法论参考而非直接部署。关注其 roadmap 的"多 agent 竞争榜"与"语义记忆检索"是否补齐。

## 八、关键文件路径速查

- `livebench/agent/live_agent.py` — 主 agent 编排器
- `livebench/agent/economic_tracker.py` — 余额/成本/收入记账
- `livebench/work/task_manager.py` / `evaluator.py` — GDPVal 任务派发与 LLM 评估
- `livebench/tools/direct_tools.py` — decide/submit/learn/status 核心工具
- `clawmode_integration/agent_loop.py` / `provider_wrapper.py` / `cli.py` — ClawMode 集成与成本拦截
- `livebench/configs/` — agent 与经济学配置（initial_balance / token_pricing）
- 上游依赖：[HKUDS/nanobot](https://github.com/HKUDS/nanobot) ｜ 基准数据集：[OpenAI GDPVal](https://openai.com/index/gdpval/)
