# Anionex/banana-slides 深度调研

> 调研日期：2026-09-26 | 数据来源：GitHub API（README / 源码树 / 服务结构）| 许可：AGPL-3.0 | Stars：15,660 | Forks：1,789 | 语言：TypeScript | 默认分支：main

## 一、项目定位（一句话）

一站式**原生 AI PPT 生成应用**——基于 Google「nano banana pro」图像模型，上传模板/素材后，用一句话、大纲或页面描述生成幻灯片，支持口头改区域、一键导出**可编辑 PPTX 与视频**。

## 二、项目亮点（差异化）

1. **原生可编辑**：直接产出可编辑 PPTX（非图片拼贴），这是相对「截图式 AI PPT」的核心优势。
2. **模板+素材双驱动**：可上传任意模板图片、任意素材并智能解析，风格可控。
3. **多入口形态**：Web（frontend）、CLI（`cli/`）、桌面端（`desktop/`）、All-in-One Docker（`docker-compose.allinone.yml`）。
4. **视频导出**：`tts_video_service` 表明能把幻灯片转成带配音的视频，差异化明显。
5. **Agent Skill 化**：`skills/banana-cli` 把生成能力封装成 agent 技能，可嵌入 AI 工作流。

## 三、核心架构

典型「Python 后端 + TS 前端 + 容器化」全栈：

- 后端 `backend/`：FastAPI（`app.py` + `controllers/` + `models/` + `services/` + `utils/`），`pyproject.toml` + `uv` 管理，`alembic` 做迁移。
- 前端 `frontend/`：TypeScript 前端。
- `cli/`、`desktop/`：本地与桌面入口；`docker/` + 多份 compose（demo/prod/allinone）支持一键部署。

**后端服务拆解（`backend/services/`）**——按能力竖切：

```
ai_service.py / ai_service_manager.py   # 模型调用与多 provider 编排
export_service.py                       # 导出可编辑 PPTX
tts_video_service.py                    # 配音 + 视频合成
inpainting_service.py + image_editability/  # 图像修复/可编辑性处理
file_parser_service.py / pdf_service.py / pdf_image_service.py  # 文档与素材解析
material_import_service.py              # 素材导入
task_manager.py / task_watchdog.py      # 任务调度与看门狗
prompts.py / public_demo.py / update_check_service.py
```

## 四、应用场景与启发

- **课件/汇报速成**：用户输入大纲即可出可编辑幻灯片，适合学生/职场快速出稿。
- **营销物料**：模板+素材解析让品牌风格可复用。
- **借鉴点**：「后端服务按能力竖切 + 多入口（Web/CLI/桌面/Docker）+ Agent Skill 封装」是 AI 应用产品化的成熟范式；`task_watchdog` 体现长任务健壮性考量。

## 五、源码深度解读

**1. 服务化后端**：`backend/services/` 把「AI 调用 / 导出 / 配音视频 / 图像可编辑 / 文档解析 / 素材导入」拆成独立 service，由 `ai_service_manager` 统一编排——清晰、易扩展，避免了「一个大函数跑完全流程」的反模式。

**2. Agent Skill 入口**：`skills/banana-cli` 将生成能力做成 skill，意味着它可被 Claude Code / Codex 等 agent 调用，与用户「用 agent 做 PPT」的兴趣高度契合。

## 六、社区口碑

- 15.7k⭐ / 1.8k fork，中文社区「banana 系列」热度（同期有多个 nano-banana 相关高星仓库）。
- README 含 CLA.md、多份部署 compose、CONTRIBUTING，工程化较完整。
- 口碑以「出图快、可编辑」为主，但属社区个人/小团队项目。

## 七、竞品对比

| 维度 | banana-slides | PPTAgent | GordenSuperPPTSkills | 通义/ChatPPT |
|------|---------------|----------|----------------------|--------------|
| 产物 | 可编辑 PPTX | 可编辑 PPTX | 可编辑 PPTX | 平台内 |
| 模型依赖 | nano banana pro（图像） | LLM+微调 | GPT 生图+视觉 | 厂商私有 |
| 视频导出 | ✅ | ❌ | ❌ | 部分 |
| 许可 | AGPL-3.0 | MIT | MIT | 闭源 |

**差异点**：图像模型驱动 + 原生可编辑 + 视频导出三连；但 AGPL-3.0 对闭源商用不友好。

## 八、核心研判

- **强绑定 nano banana pro**：本质是 Google 图像模型的「套壳+工作流」，API 成本与合规（图像模型出口/条款）是主要风险点；模型迭代会直接冲击项目。
- **AGPL-3.0 是硬约束**：任何修改后的网络服务必须开源，商业集成需谨慎评估。
- **建议**：作为「快速出可编辑 PPT」的工具链备选很好；若要做私有化/商业化，应评估换模型后端 + 许可替换成本。可编辑导出与视频合成能力值得借鉴。

## 关键文件路径速查

- `backend/app.py` — FastAPI 入口
- `backend/services/export_service.py` — 可编辑 PPTX 导出
- `backend/services/tts_video_service.py` — 配音+视频合成
- `backend/services/inpainting_service.py` + `image_editability/` — 图像可编辑性
- `skills/banana-cli/` — Agent Skill 封装
- `docker-compose.allinone.yml` / `Dockerfile.allinone` — 一体部署
