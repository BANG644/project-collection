# KsanaDock/Microverse 深度调研

> 调研日期：2026-09-30 ｜ 数据源：gh API（README / 目录树 / 源码 MemoryManager.gd / DialogManager.gd / AIAgent.gd）｜ 定位：Godot 4 多智能体 AI 社交模拟沙盒游戏

## 一、项目定位（一句话）

**Microverse** 是一个基于 Godot 4 的「模拟上帝」沙盒游戏 + 多智能体 AI 社交模拟系统：AI 角色拥有独立思维与记忆，在办公室等开放场景中自主社交、执行任务、发展社会关系（类斯坦福 AI 小镇，但可 DIY 且可玩）。

## 二、项目亮点（差异化）

1. **类斯坦福 AI 小镇 + 游戏化**：8 个预设 AI 角色（PM/数据分析/设计师/技术/市场/HR/财务/开发），WASD 移动、T 对话、L 结束、ESC 设置——既是研究原型，又是能玩的沙盒。
2. **多智能体生态**：角色自主 LLM 对话、记忆持久化、任务自主管理、环境/角色状态感知，能发展出复杂社会关系。
3. **多 AI 服务集成**：OpenAI / Claude / Gemini / DeepSeek / 豆包 / Kimi / Ollama 等可切换。
4. **数据本地化 + 商业演进**：JSON 本地存档；开源的是 2025-06 初版 Demo，完整版上 Steam（`Microverse In Box`，App 3902630）。

## 三、核心架构

- **技术栈**：Godot 4.3+ / GDScript / REST 调 LLM / JSON 本地存储 / Godot 内置 UI。
- `script/ai/`：`AIAgent.gd`（角色 AI 决策核心：感知半径 `PERCEPTION_RADIUS=200`、状态机 IDLE/MOVING/TALKING、每 60s 决策定时器、`generate_scene_description` 场景描述生成、接入 `/root/APIManager`）、`APIManager.gd`（LLM 调用管理）、`DialogManager.gd` / `DialogService.gd`（对话）、`ConversationManager.gd`、`memory/MemoryManager.gd`（记忆）、`background_story/BackgroundStoryManager.gd`（角色背景生成）。
- `script/`：`CharacterManager.gd`、`CharacterPersonality.gd`（8 角色配置）、`CharacterStatusManager.gd`、`TaskManager.gd`、`GameSaveManager.gd`、`RoomManager.gd`、`CameraController.gd` 等。
- 场景：`scene/characters/*.tscn`、`scene/ui/DialogBubble.tscn`；资源：`asset/`（角色立绘/地图/字体）。

## 四、应用场景与启发

- **场景**：想动手做一个「多智能体社会模拟 / AI 小镇」的开发者与研究者；教学演示 LLM Agent 的感知-决策-记忆-社交闭环；游戏化叙事原型。
- **启发**：
  - 它把「斯坦福 Generative Agents」的研究范式落地成**可玩的游戏**：用游戏世界状态（房间/物品/邻近角色）驱动 LLM 决策，比纯网页原型更易演示与扩展。
  - 记忆系统用「类型 + 重要性 + 时间戳」三元组 + 上限裁剪，是轻量、可解释的角色记忆实现，可直接借鉴到任何 agent 模拟。

## 五、源码深度解读（核心模块）

**1. `script/ai/memory/MemoryManager.gd`：轻量可解释的角色记忆**

```gdscript
# script/ai/memory/MemoryManager.gd (节选)
enum MemoryType { PERSONAL, INTERACTION, TASK, EMOTION, EVENT }
enum MemoryImportance { LOW = 1, NORMAL = 3, HIGH = 5, CRITICAL = 10 }
func add_memory(character, memory_content, memory_type = PERSONAL, importance = NORMAL):
    var memory_obj = { "content": memory_content, "timestamp": time_str,
                       "type": memory_type, "importance": importance,
                       "created_at": Time.get_unix_time_from_system() }
    character_data["memories"].append(memory_obj); character.set_meta(...)
    _cleanup_old_memories(character)            # 限 50 条，按重要性+时间裁剪
func get_formatted_memories_for_prompt(character, max_count = -1):
    # 按"重要性优先、时间次之"排序注入 prompt
    formatted_memories.sort_custom(func(a, b):
        if a.importance != b.importance: return a.importance > b.importance
        return a.timestamp > b.timestamp)
```

记忆以 `character_data` meta 形式存在角色节点上；`_cleanup_old_memories` 限制 50 条并按重要性裁剪——清晰、可解释。

**2. `script/ai/AIAgent.gd`：以游戏世界状态驱动 LLM 决策**

```gdscript
# script/ai/AIAgent.gd (节选)
const PERCEPTION_RADIUS = 200
enum State { IDLE, MOVING, TALKING }
func _ready():
    decision_timer = Timer.new(); decision_timer.wait_time = 60   # 每 60s 决策一次
    decision_timer.timeout.connect(_on_decision_timer_timeout); decision_timer.start()
func generate_scene_description() -> String:
    # 综合"当前房间 + 环境 + 房间内物品 + 房间内角色"生成世界状态文本喂给 LLM
    var current_room = room_manager.get_current_room(...)
    description += "你现在在" + current_room.name + "。" + current_room.description
    # + 环境信息 + 房间内物品 + 角色
```

每个角色挂一个 AIAgent 节点，`decision_timer` 每 60s 触发 `make_decision()`；`PERCEPTION_RADIUS` 限定可交互对象——体现「游戏世界状态 → LLM 决策」的范式。

**3. `script/ai/DialogManager.gd`：对话生命周期与记忆累积**

`_add_conversation_memory_to_participants` 在对话开始/结束时为**双方**写记忆（`你与X开始了对话`/`结束了对话`），使社会关系可跨会话累积——是多 agent 社会涌现的关键闭环。

## 六、社区口碑

- 2.4k⭐、402 fork，MIT；Steam 即将上线（App 3902630），有官方站点 `ksanadock.com` + 中文社媒（小红书/B站）；开源的是早期 Demo，完整能力在 Steam 闭源版。

## 七、竞品对比 + 核心研判

| 维度 | Microverse | Stanford Generative Agents | AI Town (web) | 商业 Sims 类 |
|---|---|---|---|---|
| 游戏化/可玩 | ✅ Godot 沙盒 | ❌ 研究原型 | ⚠️ 网页演示 | ✅ |
| 多 LLM 可切换 | ✅ 7+ | ⚠️ | ⚠️ | ❌ |
| 开源可 DIY | ✅（Demo） | ✅（研究代码） | ✅ | ❌ |
| 维护/完整度 | ⚠️ 早期 Demo | 停滞 | 社区 | 商业 |

**研判**：对「想动手做多智能体社会模拟/AI 小镇」的开发者，是比 Stanford 原型更可玩、比 web demo 更接近游戏的参考实现；GDScript + Godot 上手成本低，记忆/对话/任务系统模块清晰。风险：开源版为 2025-06 早期 Demo，活跃度与持续维护存疑；完整能力在 Steam 闭源版；LLM 调用成本随角色数与频率上升。与用户的「多 Agent / 社会模拟」兴趣高度契合，可作为 agent 协作范式的中文可玩样例。

## 八、关键文件路径速查

- 仓库根：`https://github.com/KsanaDock/Microverse`；官网：`https://www.ksanadock.com`
- AI 决策：`script/ai/AIAgent.gd`、`script/ai/APIManager.gd`
- 记忆系统：`script/ai/memory/MemoryManager.gd`
- 对话：`script/ai/DialogManager.gd`、`script/ai/DialogService.gd`、`script/ai/ConversationManager.gd`
- 角色/任务/场景：`script/CharacterManager.gd`、`script/CharacterPersonality.gd`、`script/TaskManager.gd`、`script/RoomManager.gd`
- 场景与资源：`scene/characters/*.tscn`、`scene/ui/DialogBubble.tscn`、`asset/`
- 文档：`README_EN.md`、`script/ai/background_story/README.md`、`project.godot`
