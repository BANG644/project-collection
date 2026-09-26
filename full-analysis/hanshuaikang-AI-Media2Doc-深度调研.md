# AI-Media2Doc — 音视频一键转风格化文档

> 调研日期：2026-09-27 ｜ 定位：本地部署的 Web 工具，把视频/音频转成小红书/公众号/笔记/思维导图等风格文档
> 数据源：gh api 真实抓取 README.md / backend/app.py / backend/routers/llm.py / backend 目录树

## 一、项目全景

| 项 | 值 |
|---|---|
| 仓库 | `hanshuaikang/AI-Media2Doc`（默认分支 `main`） |
| 星标 | 4,031 ⭐ |
| 语言 | Vue（前端）+ Python（FastAPI 后端） |
| 许可 | MIT（完全开源、可本地/Docker 部署） |
| 最后提交 | 2026-02-05（后端架构稳定，作者以"辣条"人设持续运营） |

**一句话**：一个"前后端本地部署、无需登录"的 Web 工具——上传音视频，用大模型一键生成多种风格的文档（小红书/公众号/知识笔记/思维导图/内容总结），并支持 AI 二次问答、字幕导出、智能截图插图。

## 二、项目亮点

1. **完全本地、隐私优先**：无需注册，任务记录留本地；前端用 **ffmpeg wasm** 处理音视频，连 ffmpeg 都不用本机装。
2. **多风格输出**：小红书/公众号/知识笔记/思维导图/总结等多种模板，前端可自定义 Prompt。
3. **0 成本智能截图**：基于字幕信息智能截图并插入文章对应位置，**无需视觉大模型**（不烧多模态 token）。
4. **AI 二次问答**：针对视频内容做对话式追问。
5. **一键部署**：Docker Compose + 访问密码保护（`WEB_ACCESS_PASSWORD`）。

## 三、核心架构

```
backend/                     ← FastAPI
  app.py                     ← 应用装配（CORS + 异常处理器 + 密码校验 + 路由注册）
  routers/  llm.py(对话/Markdown生成) files.py(上传/处理) audio.py(音频) secrets.py
  core/    exceptions.py, response.py（统一返回）
  utils/   env.py, s3.py
  models.py, constants.py, config/, env.py
frontend/                     ← Vue（docs 展示 ffmpeg wasm 前端处理）
docker-compose.yaml + variables.env（配置项：火山引擎等 LLM 环境变量）
```
**处理流（README 图）**：音视频 → 转写/理解 → 按风格 Prompt 生成文档 → 智能截图插图 → 导出（含字幕文件）。

## 四、源码深度解读

**① 应用装配（`backend/app.py`）**——密码校验以 Header 依赖注入到所有 `/api/v1` 路由：
```python
async def verify_web_access_password(
    request_web_access_password: str | None = Header(None, alias="request-web-access-password")):
    if env.WEB_ACCESS_PASSWORD and request_web_access_password != env.WEB_ACCESS_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized ...")
    return True

app.include_router(llm.router,    prefix="/api/v1", dependencies=[Depends(verify_web_access_password)])
app.include_router(files.router,  prefix="/api/v1", dependencies=[Depends(verify_web_access_password)])
app.include_router(audio.router,  prefix="/api/v1", dependencies=[Depends(verify_web_access_password)])
```
设计干净：鉴权是"可选开关"（设了密码才校验），且统一挂在 router 依赖上，不侵入业务。

**② LLM 路由（`routers/llm.py`）**——OpenAI 兼容客户端，环境驱动：
```python
client = OpenAI(base_url=env.LLM_BASE_URL, api_key=env.LLM_API_KEY)
response = client.chat.completions.create(model=env.LLM_MODEL_ID, messages=messages, timeout=120)
```
模型/密钥/BaseURL 全走环境变量（`variables.env`），**任意 OpenAI 兼容端点**皆可（火山引擎等），不绑定厂商。
> 注：转写与"风格化生成"的具体 pipeline 在 `routers/files.py`/`audio.py` 与 `utils/`，本次未展开具体实现，标注"核心处理细节数据不可用"。

## 五、社区口碑

- HelloGitHub 推荐、被阮一峰周刊等自媒体转发；作者"韩数同学"用公众号/小红书强势运营，Star 增长快。
- 定位"个人低成本体验音视频转文档"，直击"不想注册/不想上传第三方"的痛点，口碑偏正面。
- **局限**：后端最后提交停在 2026-02，更新节奏放缓；核心依赖外部 LLM（无内置模型）；"智能截图"质量受字幕准确度影响。

## 六、竞品对比

| 项目 | 定位 | 差异 |
|---|---|---|
| `linyqh/NarratoAI`（已入库） | AI 影视解说 + 自动剪辑 | 偏视频剪辑/带货；本工具偏"音视频→图文笔记" |
| `Anionex/banana-slides`（已入库） | 原生 AI PPT 生成 | 垂直 PPT；本工具通用文档 |
| NoteGPT / 飞书妙记 等 | 音视频转笔记（SaaS） | 商业 SaaS、需登录；本工具本地开源、隐私优先 |
| `hanshuaikang/AI-Media2Doc` | 本地开源、多风格、0 成本截图 | 差异化在"隐私 + 免费 + 智能截图不烧多模态" |

## 七、核心研判

- **范式价值**："ffmpeg wasm 前端处理 + 智能截图基于字幕（不调视觉模型）"是**极致降本的本地化范式**——把贵的多模态步骤用便宜的信号（字幕时间戳）替代。
- **对用户启发**：做"媒体→笔记"类个人工具时，优先本地 + 开源 + 隐私牌，比卷 SaaS 更易获早期口碑；截图用字幕对齐是低成本实现"图文并茂"的好技巧。
- **风险**：强依赖外部 LLM（无离线模型兜底，虽 README 提未来接 fast-whisper 本地 ASR）；后端更新慢，部署前自测。

## 八、关键文件路径速查

| 路径 | 作用 |
|---|---|
| `backend/app.py` | FastAPI 装配、CORS、密码依赖、路由注册 |
| `backend/routers/llm.py` | OpenAI 兼容对话 / Markdown 生成 |
| `backend/routers/files.py` | 文件上传与处理流水线 |
| `backend/routers/audio.py` | 音频处理 |
| `backend/core/response.py` | 统一返回结构 |
| `variables_template.env` | LLM 环境变量配置模板（火山引擎等） |
| `docker-compose.yaml` | 一键部署 |
