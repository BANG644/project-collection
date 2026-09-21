# EmergenceAI/Agent-E 深度调研

> 调研日期：2026-09-22 ｜ 定位：基于 AG2(AutoGen) 的浏览器自动化 agent，用"分层规划 + DOM 蒸馏 + 技能化"让 LLM 安全操作网页 ｜ Stars：1,251 ｜ 语言：Python ｜ 许可：MIT ｜ 默认分支：master ｜ 最近活跃：2026-05

## 一、项目定位（一句话）

Agent-E 是 Emergence AI 开源的**网页自动化 agent 系统**：构建在 AG2（原 AutoGen）之上，用"高层规划 agent + 浏览器导航 agent + 一组预定义的网页操作技能"在真实网站完成填表、搜商品、播视频、管 JIRA 等任务，并配套一篇 arXiv 论文（2407.13032）阐述 agentic 系统设计原则。

## 二、项目亮点（差异化）

- **技能化而非自由代码生成**：刻意让 LLM 调用"人类视角的网页技能"（click/enter_text/openurl…），而非随手写代码——更安全、结果更可预测（"至少不会执行未知恶意代码"）。
- **DOM 蒸馏（DOM Distillation）**：向每个 DOM 元素注入 `mmid` 属性，用**无障碍树**而非原始 HTML，返回 `text_only / input_fields / all_fields` 三种紧凑 JSON，大幅降低喂给 LLM 的噪声。
- **分层规划架构**：User Proxy + Browser Navigation 两个 agent 协作；高层 planner 拆任务，导航 agent 执行技能并回自然语言结果（便于纠错）。
- **企业版 + 论文双轨**：开源版即研究原型，企业版（Emergence Orchestrator）加日志、RBAC、云托管；论文被后续 browser-use 类项目广泛引用。

## 三、核心架构

```
用户自然语言指令
   └─ ae/core/system_orchestrator.py  编排
        ├─ high_level_planner_agent.py   拆解任务（规划）
        └─ browser_nav_agent.py          执行网页技能
             └─ ae/core/skills/    Sensing + Action 技能
                  ├─ geturl / get_dom_with_content_type   （感知）
                  ├─ click / enter_text / enter_text_and_click
                  ├─ open_url / bulk_enter_text / press_key_combination
                  └─ get_user_input / pdf_text_extractor / pause_flow
   └─ ae/core/playwright_manager.py   驱动浏览器
   └─ ae/core/memory/static_ltm.py     长期记忆（用户偏好）
   └─ ae/server/api_routes.py          FastAPI（/execute_task 流式）
```

- **技能库 `ae/core/skills/`**：每个技能是一个返回自然语言结果的函数（如 `click_using_selector.py` 接收 DOM query selector 点击）；`skill_registry.py` 注册管理。
- **DOM 蒸馏**：`get_dom_with_content_type.py` 调 Playwright 取无障碍树 → 注入 `mmid` → 按 content type 输出紧凑 JSON；`post_process_responses.py` 做后处理。
- **可接入本地模型**：经 LiteLLM + Ollama 可换非 OpenAI 模型（官方标注"未充分测试"）。

## 四、应用场景与启发

- **自建网页 agent 的架构范本**：想做"帮用户下单/填表/查资料"的 agent，Agent-E 的"规划 agent + 导航 agent + 技能注册表 + DOM 蒸馏"是可直接照抄的分层模板。
- **安全优先的 agent 设计**：它用"配置好的技能"替代"LLM 自由写代码"，对金融/医疗等高风险自动化场景尤其有借鉴——用白名单技能约束 LLM 行为边界。
- **DOM 蒸馏思路**：给 DOM 打 `mmid`、用无障碍树降噪，是降低网页 agent token 成本与误触的通用技巧。

## 五、源码深度解读（关键片段）

技能返回自然语言而非布尔值，便于 LLM 纠错（来自 README 设计说明）：

```python
# ae/core/skills/click_using_selector.py（示意）
def click_using_selector(selector: str) -> str:
    # 用 Playwright 按 selector 点击，返回发生了什么的自然语言描述
    return f"[Success] Clicked element matching '{selector}'."
```

DOM 蒸馏核心在 `get_dom_with_content_type.py`：取无障碍树 → 给元素注入 `mmid` → 按 `text_only / input_fields / all_fields` 三种粒度输出 JSON，让 LLM 只拿到与任务相关的结构。`system_orchestrator.py` 把 planner 与 nav agent 串起来，nav agent 每步把技能结果回灌给 planner 做下一步决策。

## 六、全网口碑

- **正面**：arXiv 2407.13032 是网页 agent 方向的**奠基性参考**之一，DOM 蒸馏与"技能化安全"被 browser-use/Stagehand 等多项目沿用；MIT 许可、文档详尽（含测试 harness、FastAPI 接口、本地模型接入）。
- **注意**：基于 AG2/AutoGen（框架本身演进快、API 易变）；仓库近期提交放缓（2026-05）；单标签限制、Google 全家桶(canvas)不支持、PDF 大文本需分块——仍属研究原型。

## 七、竞品对比与核心研判

| 维度 | Agent-E | browser-use | Stagehand | UI-TARS / computer-use |
|------|---------|-------------|-----------|------------------------|
| 规划 | 分层 planner+nav | 单 agent | 自顶向下 API | 视觉端到端 |
| DOM 处理 | 无障碍树+mmid 蒸馏 | 可访问性快照 | 声明式抽取 | 视觉 |
| 安全 | 技能白名单 | 中 | 高 | 低 |

**核心研判**：⭐⭐⭐⭐ — 作为**网页 agent 的架构教科书**价值很高（论文 + 分层 + DOM 蒸馏 + 技能安全），适合想自研浏览器自动化的团队研读其 `ae/core/` 设计与论文；但作为可直接上生产的成品已偏旧（AG2 依赖、单标签、维护放缓）。若只要"开箱即用"，browser-use/Stagehand 更省心；要"学怎么造"，Agent-E 更值得读源码。

## 八、关键文件路径速查

- `ae/core/system_orchestrator.py` — 总编排
- `ae/core/agents/`（`high_level_planner_agent.py` `browser_nav_agent.py`）— 双 agent
- `ae/core/skills/`（`click_using_selector.py` `get_dom_with_content_type.py` `skill_registry.py` …）— 技能库
- `ae/core/playwright_manager.py` / `memory/static_ltm.py` — 浏览器驱动与长期记忆
- `ae/server/api_routes.py` — FastAPI `/execute_task`
- 论文：[arXiv 2407.13032](https://arxiv.org/abs/2407.13032) ｜ 框架：[AG2/AutoGen](https://docs.ag2.ai/docs/Home)
