# TurixAI/TuriX-CUA — 深度调研

> 调研日期：2026-09-28 ｜ 星标：3,166 ｜ 许可：MIT ｜ 语言：Python 3.12（agent）+ OpenClaw/Clawdbot Skill ｜ 平台：macOS 15+ 主（Win/Linux 在分支）｜ 形态：开源 Computer-Use Agent

## 1. 项目定位（一句话）
开源的**计算机使用智能体（CUA）**："对你的电脑说话，看它干活"——用多模型架构驱动桌面 GUI 自动化，OSWorld 榜单 64.2%（第 3），macOS 自测 80%+。

## 2. 项目亮点
- **SOTA 桌面自动化**：OSWorld 64.2%（358 分里 229.88，第 3），零 Linux 训练数据却进前三；macOS 自测 80%+ 成功率。
- **多模型架构**：Brain（理解+规划）/ Actor（执行 UI 动作）/ Planner（高层分解，`use_plan` 时）/ Memory（跨步上下文）四角色；"脑"可热插拔 VLM（`config.json` 换 provider，支持 turix/ollama/openai/google/anthropic）。
- **Skills 剧本系统**：`skills/` 下 markdown playbook（YAML frontmatter 的 name+description），Planner 只看 name+description 选技能、Brain 读全文执行。
- **MCP-ready**：可经 Model Context Protocol 接 Claude for Desktop 或任意 agent；自带 OpenClaw 技能包（macOS/Windows 分支）。
- **完全开源免费**：MIT，个人与研究用途零成本；支持本地 Ollama（`llama3.2-vision`）。

## 3. 核心架构
- **入口与配置**：`examples/main.py` 启动；`examples/config.json` 配置 task / 四个 LLM 角色 / `use_plan` `use_skills` `max_steps` `max_actions_per_step` 等。
- **分层代码**：`src/agent/service.py`（约 75KB，agent 主服务）、`src/agent/planner_service.py`（Planner 类）、`src/agent/message_manager/`、`src/agent/prompts.py`、`src/controller/service.py`（控制器桥接桌面）。
- **Skills 工具**：`src/utils/skills.py`（`SkillMetadata` / `load_skill_contents` / `format_skill_context`）加载剧本；内置 `skills/github-web-actions.md`。
- **OpenClaw 集成**：`OpenCLaw_TuriX_skill/SKILL.md` + `scripts/run_turix.sh`；Windows 在 `multi-agent-windows` 分支（含 `.ps1` + `agents/openai.yaml`）。

## 4. 应用场景与启发
- **桌面自动化基线**：用户做 agent/工作流研究，TuriX 是"Brain/Actor/Planner/Memory + Skills + MCP"架构的现成开源实现，可直接当 CUA 基线或二次开发。
- **借鉴多角色 + 剧本架构**：其 Planner 的"预规划决定要不要联网搜索 + 选哪些 skill"、Brain/Actor 职责分离，可映射到用户**错题归因 agent** 的"规划-执行-复核"链路。
- **注意**：默认 brain/actor 是 TuriX 自家模型需 API key；真正离线要换本地 Ollama 多模态；macOS 优先，Windows 在单独分支、Linux 在 `multi-agent-linux`。

## 5. 源码深度解读
`src/agent/planner_service.py` 的 `class Planner` 用 `PreplanDecision` 冻结结构体做"预规划决策"：
```python
@dataclass(frozen=True)
class PreplanDecision:
    use_search: bool
    queries: List[str]
    selected_skills: List[str]
    raw_text: str = ""
# Planner.__init__: max_input_tokens=32000, use_search, skill_catalog,
#                    preplan_llm, available_skills, skills_max_chars=4000
```
即先判断"要不要联网搜索、搜什么、加载哪些 skill"，再进入逐步执行——把"是否检索/选技能"显式化为决策，避免每步都盲目调用工具。

Skills 系统的关键在 `src/utils/skills.py`：`SkillMetadata` 解析 frontmatter，`format_skill_context` 把选中剧本拼进 Brain 提示词；Planner 仅用 name+description 做匹配，Brain 用全文——**检索与执行解耦**，是 playbook 规模化的关键。配置热插拔则通过 `examples/main.py` 的 `build_llm(provider, model_name, base_url)` 工厂实现，新增模型只要加一个分支。

## 6. 社区口碑
- 3.2k⭐、2026 持续更新（v3.0.0-alpha、Linux/Windows 分支、ClawHub 技能）；有 Discord、OSWorld 公开榜单成绩、技术报告（turix.ai/technical-report）。
- 局限：macOS 主战场，Windows/Linux 在分支成熟度不一；默认模型需商业 API，纯本地体验依赖 Ollama 多模态能力；GUI agent 本身慢且非确定性（SKILL.md 也提醒"能用 Clawdbot 就别让 TuriX 慢慢手搓文档"）。

## 7. 竞品对比 + 核心研判
| 项目 | 形态 | 差异 |
|---|---|---|
| TuriX-CUA | 开源 CUA + 多模型 + Skills + MCP | 开源、可本地、Mac SOTA |
| UI-TARS (字节) | 闭源商业 CUA | 不开源 |
| OpenAI Operator / Claude CUA | 闭源托管 | 不开放权重/代码 |
| Cua / OpenInterpreter | 开源桌面自动化 | 架构/打分类不同 |

**研判**：在"可自托管、可换模型、带 Skills 剧本、OSWorld 有公开成绩"的 CUA 里综合性价比最高，是用户做桌面自动化/agent 研究的优质开源基线；建议先 macOS/Ollama 试跑，再评估移植到 Windows 工作流的成本。

## 8. 关键文件路径速查
- `examples/main.py` — 启动入口（含 `build_llm` 模型工厂）
- `examples/config.json` — 任务/四角色 LLM/规划与技能开关
- `src/agent/service.py` — Agent 主服务（~75KB）
- `src/agent/planner_service.py` — Planner 与 `PreplanDecision`
- `src/agent/message_manager/` + `src/agent/prompts.py` — 消息管理与提示词
- `src/controller/service.py` — 桌面控制桥
- `src/utils/skills.py` — Skills 加载与格式化
- `skills/github-web-actions.md` — 内置剧本样例
- `OpenCLaw_TuriX_skill/SKILL.md` + `scripts/run_turix.sh` — OpenClaw 集成
