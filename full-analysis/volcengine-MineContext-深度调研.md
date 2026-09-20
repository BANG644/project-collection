# volcengine/MineContext 深度调研

> 调研日期：2026-09-21 | 星标：5,518⭐ | 语言：Python（后端 opencontext）+ TypeScript（Electron 前端）| 许可：Apache-2.0 | 默认分支：main | 最近提交：活跃（v0.1.8）

## 一句话定位
字节火山引擎开源的主动式「上下文感知 AI 伙伴」：通过截图 + 多源理解「看见」你的数字世界，基于上下文工程框架主动推送摘要 / 待办 / 活动记录；本地优先、可接本地模型。

## 项目亮点
- **Local-First 隐私**：数据默认存本地（`~/Library/Application Support/MineContext/Data`），可用兼容 OpenAI 协议的本地 / 自建模型，数据不出本机。
- **上下文工程分层架构**：`capture → processing → storage → consumption` 全生命周期，生成六类智能上下文。
- **多源采集路线图**：P0 屏幕截图+笔记+链接 → P1 文件 → P2 MCP/会议 → P3 DeepResearch/RSS → P4 微信/QQ/手机截图 → P5 可穿戴，开放贡献。
- **主动投递**：每日 / 周摘要、可执行待办、活动记录，直接推到首页，而非被动问答。
- **与 OpenViking 联动**：同组织 `volcengine/OpenViking` 上下文数据库（文件范式统一记忆 / 资源 / 技能）作基础设施层。

## 核心架构
- 前端 `frontend/`：Electron + React + TS，main / preload / renderer 三层分离，Vite 构建。
- 后端 `opencontext/`：FastAPI 服务 + `managers/`（Capture / Processor / Consumption / Event Manager）+ `context_capture/`（截图 / 文件 / 链接）+ `context_processing/`（chunker / merger / processor）+ `storage/`（SQLite / ChromaDB 多后端）+ `llm/`（多 provider + VLM + embedding）。
- 处理管线：截图 → pHash 去重 → VLM 抽取 → embedding 入库 → 后台线程队列异步消费。

## 应用场景与启发
- 「个人上下文中枢」：把屏幕 / 文件 / 会议统一沉淀为可检索上下文，给「第二大脑 / 主动记忆」需求参考。
- Manager + 组件注册模式（可插拔采集源）值得借鉴到任何「多源数据接入」系统。
- 本地优先 + 开源是相对于 ChatGPT Pulse 的硬差异化，适合隐私敏感的知识工作者 / 学生。

## 源码解读
**采集管理器（`opencontext/managers/capture_manager.py`）**

```python
class ContextCaptureManager:
    def __init__(self):
        self._components: Dict[str, ICaptureComponent] = {}
        self._running_components: Set[str] = set()
        self._callback = None  # 新数据捕获时回调
    def register_component(self, name, component): ...
    def start_component(self, name):
        component.set_callback(self._on_component_capture)
        component.start(); self._running_components.add(name)
```

**截图处理（`opencontext/context_processing/processor/screenshot_processor.py`）**

```python
class ScreenshotProcessor(BaseContextProcessor):
    def __init__(self):
        self._input_queue = queue.Queue(maxsize=self._batch_size*3)
        self._processing_task = threading.Thread(
            target=self._run_processing_loop, daemon=True)  # 后台线程消费
        self._processing_task.start()
    def _is_duplicate(self, new_context):
        new_phash = calculate_phash(new_context.content_path)  # pHash 实时去重
```

## 全网口碑
GitHub 5.5k⭐、Trendshift 收录、Discord / 微信 / Lark 社区；字节火山引擎背书。README 与 ChatGPT Pulse / Dayflow 正面对比，强调本地优先 + 开源 + 主动投递。

## 竞品对比 + 核心研判
- 竞品：ChatGPT Pulse（闭源、云端、需 $200/月）、Dayflow（被动记录）、Rewind / Mem。
- 研判：MineContext 以「本地优先 + 开源 + 主动上下文工程」切入，架构清晰（Manager 模式 + 多后端存储 + VLM/embedding 管线），适合隐私敏感的个人知识场景；默认推荐豆包模型，需注意 API 依赖与国内 PyPI 镜像限制（文档已注明）。

## 关键文件路径速查
- `opencontext/managers/capture_manager.py` — 采集管理器
- `opencontext/context_capture/screenshot.py` — 截图采集（mss + 去重）
- `opencontext/context_processing/processor/screenshot_processor.py` — 截图处理（pHash + VLM + 后台队列）
- `frontend/src/{main,preload,renderer}/` — Electron 三层
- `config/config.yaml` — 服务配置（embedding / vlm / capture）
- 关联仓库：`volcengine/OpenViking`
