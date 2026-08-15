# Agent-S 深度调研

> 调研日期：2026-08-16 ｜ 星标：12,159 ⭐ ｜ 协议：Apache-2.0 ｜ 语言：Python
> 仓库：`simular-ai/Agent-S` ｜ 默认分支：`main` ｜ 官网：simular.ai ｜ 最近活跃：2026-08-01
> 定位：用「像人一样操作电脑」的开源 GUI Agent 框架（Computer-Use Interface Agent）

## 一、项目定位（一句话）

**让 LLM/VLM「像人一样用电脑」的开源 Agent 框架**——给定一句自然语言指令，Agent 自主观察屏幕、规划、调用鼠标键盘完成跨应用任务；其标志性的 **bBoN（behavior bounding，行为边界）** 机制用「执行前后截图对比」校验动作是否达成预期，把不可控的 computer-use 行为「框定」在安全可验证范围内。

## 二、项目亮点（差异化）

1. **多代演进的清晰谱系**：从 S1（认知/操作/执行三层 hierarchy）→ S2 → S2.5 → **S3（无层级扁平架构）**，每一代都在削减推理开销。S3 直接去掉层级化简，换来更低的单步延迟。
2. **bBoN 行为边界机制（核心创新）**：不盲目信任模型输出的每一步，而是**对比动作执行前后的屏幕差异**来「判定」行为是否如预期发生——把 computer-use 的「幻觉动作」关进可验证的笼子。
3. **多平台 grounding**：`gui_agents/s3/agents/grounding` 的 `ACI`（Agent-Computer Interface）抽象屏蔽 macOS/Linux/Windows 差异，上层 Agent 只面对统一observation/action。
4. **事实叙述 + 轨迹评估双裁判**：`BehaviorNarrator` 把「截图+动作」转成自然语言事实，`ComparativeJudge` 在多条轨迹间择优，形成可审计的决策闭环。
5. **开源友好**：Apache-2.0，模块化 `gui_agents/s3/`（agents / worker / memory / mllm / utils），便于二次开发。

## 三、核心架构

Agent-S 运行时由三层角色构成：

- **UIAgent / AgentS3（`agents/agent_s.py`）**：Agent 主体。`UIAgent` 是基类，持有 `worker_engine`（决策 LLM）与 `grounding_agent`（ACI）。`AgentS3` 是最简版——**无层级**，直接把预测委托给 `Worker`。
- **Worker（`agents/worker.py`）**：真正调用 LLM 生成 next action 的执行器，支持 `max_trajectory_length`（轨迹窗口）与 `enable_reflection`（反思 Agent 协助）。
- **ACI（Grounding，`agents/grounding`）**：把高层动作（click/moveTo/dragTo/type）翻译为 `pyautogui` 等平台原语，并负责截图 observation。
- **记忆与裁判（`memory/procedural_memory.py` + `core/mllm.py`）**：
  - `BehaviorNarrator`：用 VLM 把「前后截图 + action」叙述为事实。
  - `ComparativeJudge`：多条轨迹间择优。
  - 系统提示词 `BEHAVIOR_NARRATOR_SYSTEM_PROMPT` / `VLM_EVALUATOR_PROMPT_COMPARATIVE_BASELINE` 沉淀在 `procedural_memory`。

数据流：`instruction + observation → Worker.generate_next_action → actions → ACI 执行 → 截图 → BehaviorNarrator 判定 → （多轨迹时）ComparativeJudge 择优`。

## 四、应用场景与启发

**典型场景**：自动化桌面操作（填表、跨软件搬运数据）、UI 自动化测试、无障碍辅助、RPA 替代、作为「计算机使用」能力的可验证底座供上层 Agent 调用。

**架构启发（可复用）**：
- **「动作后截图校验」是 computer-use 的必备安全网**：模型说「我点了按钮」不等于「按钮真被点了」。Agent-S 用前后截图 diff 做事实判定（bBoN），任何 GUI Agent 都应内置「执行—验证」回环，而非开环执行。
- **扁平 vs 层级是推理时延/质量的可调旋钮**：S3 砍掉层级换取速度，说明「并非越复杂的 Agent 架构越好」，应按任务时延预算选代数。
- **事实叙述（caption）+ 轨迹择优（judge）** 把不可解释的像素操作转成可审计的自然语言，是 GUI Agent 可观测性的关键。

## 五、源码深度解读

### 1. 无层级 Agent 主体：`agent_s.py`

`UIAgent` 定义统一接口，`AgentS3` 是最简实现——**明确为「减少推理时间」而去掉层级**：

```python
class UIAgent:
    """Base class for UI automation agents"""
    def __init__(self, worker_engine_params, grounding_agent, platform=...):
        self.worker_engine_params = worker_engine_params
        self.grounding_agent = grounding_agent
        self.platform = platform

    def predict(self, instruction, observation) -> Tuple[Dict, List[str]]:
        pass


class AgentS3(UIAgent):
    """Agent that uses no hierarchy for less inference time"""
    def __init__(self, worker_engine_params, grounding_agent, platform=...,
                 max_trajectory_length=8, enable_reflection=True):
        super().__init__(worker_engine_params, grounding_agent, platform)
        self.max_trajectory_length = max_trajectory_length
        self.enable_reflection = enable_reflection
        self.reset()

    def predict(self, instruction, observation):
        executor_info, actions = self.executor.generate_next_action(   # 直接委托 Worker
            instruction=instruction, obs=observation
        )
        info = {**{k: v for d in [executor_info or {}] for k, v in d.items()}}
        return info, actions
```

`AgentS3` 把「预测下一步动作」完全交给 `Worker.generate_next_action`，自身不做任何规划分层——这是 S3 相对早期 S1 三层 hierarchy 的最大简化。

### 2. bBoN 的事实叙述器：`behavior_narrator.py`

`BehaviorNarrator.judge()`（line 170）是行为边界机制的核心：它**先把动作标记到「执行前截图」上**（红色圆=Click、蓝色圆=MoveTo、绿线=DragTo），再围绕动作坐标对「执行后截图」做 4× 放大（denoise + 标注 bounding box），最后把 BEFORE / AFTER / ZOOMED 三图 + 动作喂给 VLM 判定：

```python
def judge(self, screenshot_num, before_img_bytes, after_img_bytes, pyautogui_action):
    mouse_actions = BehaviorNarrator.extract_mouse_action(pyautogui_action)
    before_img = Image.open(BytesIO(before_img_bytes))
    BehaviorNarrator.mark_action(mouse_actions, before_img)        # 标记红/蓝/绿圈
    ...
    if mouse_actions:
        x, y = int(coords[0]), int(coords[1])
        zoomed_after_img_bytes, marked_after_img_bytes = (
            BehaviorNarrator.get_zoomed_image(
                image_bytes=after_img_bytes, x=x, y=y,
                width=300, height=300, scale=4, upscaling=True,
                add_bounding_box=True)
        )
    fact_message = [{"role": "system",
                     "content": PROCEDURAL_MEMORY.BEHAVIOR_NARRATOR_SYSTEM_PROMPT}]
    fact_message_content = [{"type": "text", "text": "BEFORE:"},
                            marked_before_img_message,
                            {"type": "text", "text": f"Agent Action: {pyautogui_action}"},
                            {"type": "text", "text": "AFTER:"}, after_img_message]
    ...
    fact_response = call_llm_formatted(self.judge_agent,
                                       [THOUGHTS_ANSWER_TAG_FORMATTER],
                                       messages=fact_message, temperature=0.0)
    fact_answer, fact_thoughts = split_thinking_response(fact_response)
    return {"fact_thoughts": fact_thoughts,
            "fact_answer": f"Fact Caption from Screenshot {screenshot_num}: {fact_answer}"}
```

`mark_action` 对 `pyautogui.click/moveTo/dragTo` 分别画红/蓝/绿标记，`get_zoomed_image` 用 `cv2` 做 4× 放大 + 非局部去噪提升小控件可读性。**这个「动作坐标定位 + 局部放大 + VLM 判定」的闭环，就是 bBoN「行为边界」的可验证核心**——它回答的不是「模型说它做了什么」，而是「屏幕实际发生了什么」。

### 3. 多轨迹择优裁判：`comparative_judge.py`

当同任务生成多条轨迹时，`ComparativeJudge.judge()`（line 66）用每条轨迹的 initial/final 截图 + 各步 fact caption 做横向比较，输出所选轨迹：

```python
class ComparativeJudge:
    def judge(self, task_description, task, result_dirs, all_fact_captions):
        system_prompt = PROCEDURAL_MEMORY.VLM_EVALUATOR_PROMPT_COMPARATIVE_BASELINE
        system_prompt = system_prompt.replace("<TASK_DESCRIPTION_INPUT>", task_description)
        system_prompt = system_prompt.replace("<NUMBER OF TRAJECTORIES>", str(num_trajectories))
        for i, (result_dir, fact_captions) in enumerate(zip(result_dirs, all_fact_captions)):
            initial = image_to_openai_message_format(result_initial_screenshot, ...)
            final = image_to_openai_message_format(result_final_screenshot, ...)
            ...   # 把 initial/final 截图与 fact captions 拼进 messages
        response = call_llm_formatted(self.judge_agent, [], messages=messages)
        answer, thoughts = split_thinking_response(response)
        judge_choice = int(answer)   # 1..N 选一
        selected_trajectory = result_dirs[judge_choice - 1] if 1 <= judge_choice <= num_trajectories else None
        return answer, thoughts, selected_trajectory
```

## 六、全网口碑

- **学术/社区定位**：Agent-S 系列论文（S1→S3）在 GUI Agent / OSWorld 基准上有公开评测，是「computer-use」方向被频繁引用的开源实现之一。
- **近期活跃度信号**：GitHub Issue 中 `#181 "is this still alive?"`（社区对维护节奏的疑问）、`#186 代码执行工具损坏` 等说明项目有一定未决技术债，维护响应存在波动。
- **客观评价**：理念（bBoN 行为校验、多代扁平化）领先且可借鉴，但作为「直接生产用的桌面自动化」仍偏研究原型，跨应用鲁棒性与维护连续性是落地前需评估的风险点。

## 七、竞品对比与核心研判

| 维度 | Agent-S（simular-ai） | OpenAI Operator | Claude Computer Use | OmniParser | UI-TARS（库内已收录） |
|------|----------------------|----------------|--------------------|-----------|----------------------|
| 开源 | ✅ Apache-2.0 | ❌ | ✅（模型权重受限） | ✅ | ✅ |
| 行为校验(bBoN) | ✅ 前后截图判定 | 内部 | 内部 | 解析层 | 内部 |
| 架构代数 | S1→S3 多代可选 | 单一 | 单一 | 单一 | 单一 |
| 跨平台 grounding | ✅ macOS/Linux/Win | Web | 多 | 多 | 多 |
| 生产成熟度 | 研究原型 | 商用 | 商用 | 解析组件 | 商用 |

**核心研判**：
- **优势**：bBoN「执行—验证」闭环与多代扁平化架构是真实差异化，理念值得所有 GUI Agent 借鉴；完全开源便于研究二次开发。
- **风险**：维护节奏不稳定（社区已有「还活着吗」之问）、存在未修工具 bug；作为生产桌面自动化仍需加固。
- **启发**：「不信任模型自述、以屏幕实际变化为事实源」的验证范式，是任何 computer-use Agent 的必选项，而非可选项。

## 八、关键文件路径速查

| 关注点 | 路径（仓库根） |
|--------|---------------|
| Agent 主体（无层级） | `gui_agents/s3/agents/agent_s.py`（`UIAgent` L11 / `AgentS3` L48 / `predict` L85） |
| 执行器 | `gui_agents/s3/agents/worker.py`（`Worker.generate_next_action`） |
| Grounding / ACI | `gui_agents/s3/agents/grounding/`（ACI 跨平台抽象） |
| bBoN 事实叙述 | `gui_agents/s3/agents/behavior_narrator.py`（`judge` L170 / `mark_action` / `get_zoomed_image`） |
| 轨迹择优裁判 | `gui_agents/s3/agents/comparative_judge.py`（`ComparativeJudge.judge` L66） |
| 系统提示词沉淀 | `gui_agents/s3/memory/procedural_memory.py`（`BEHAVIOR_NARRATOR_SYSTEM_PROMPT` / `VLM_EVALUATOR_PROMPT_COMPARATIVE_BASELINE`） |
| VLM 封装 | `gui_agents/s3/core/mllm.py`（`LMMAgent`） |
| 历史问题线索 | Issues `#181`（维护活跃度）、`#186`（代码执行工具损坏） |
