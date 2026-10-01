# Sophomoresty/gemini-web2api 深度调研

> 调研时间：2026-10-02 ｜ 数据来源：gh API 真实抓取 README / gemini.py / server.py / 语言统计
> 定位：把 Google Gemini 网页端"反编译"成 OpenAI 兼容 API 的零成本代理——纯 Python 单文件，支持流式 / 工具调用 / 多模型 / @think 调节

## 一、项目亮点（差异化）

1. **零 API Key 即用**：`api_keys` 留空时免鉴权，把浏览器能访问的 Gemini 网页能力直接暴露成 `/v1/chat/completions` 与 `/v1/models`。
2. **真实逆向而非套壳**：直接逆向 Gemini Web 的 `StreamGenerate` 私有协议，在 `inner[79]` 字段映射模型、`inner[17]=[think_mode]` 控制思考深度，把前端 JS 的 `MODE_CATEGORY` 枚举翻译成请求体。
3. **协议双向翻译**：OpenAI 格式入、Gemini protobuf-like 格式出；工具调用（function calling）与多模态图片输入均做双向转换。
4. **轻量可部署**：纯 Python + 唯一可选依赖 `httpx`（仅流式），一行 `python gemini_web2api.py` 起服务；支持 Docker / Cloudflare Worker（`cloudflare/` 目录）。
5. **工程细节到位**：代理自动检测（`HTTPS_PROXY`）、XSRF token（`SNlM0e`）与 `SAPISIDHASH` 鉴权、cookie 缓存按 mtime、429 自动重试、`@think=N` 后缀调思考深度。

## 二、核心架构

```
Client (OpenAI SDK / Cherry Studio / Codex / Gemini CLI)
   │  POST /v1/chat/completions  (OpenAI 格式)
   ▼
server.py  (BaseHTTPRequestHandler + ThreadingMixIn)
   │  _parse_body / _authorized / _start_sse
   ▼
tools.py    messages→prompt / parse_tool_calls / google_contents↔prompt
gemini.py   _build_payload → StreamGenerate 协议 → 流式解析 wrb.fr 行
   │  urllib + httpx(流式), Origin/Referer/Cookie/SAPISIDHASH
   ▼
https://gemini.google.com/_/BardChatUi/data/.../StreamGenerate?bl=...
```
模块职责清晰：`config.py`（配置）× `models.py`（模型注册表 `resolve_model`）× `multimodal.py`（图片上传 fetch/upload）× `gemini.py`（协议核心）× `server.py`（HTTP 层）× `tools.py`（格式转换）。

## 三、应用场景与启发

- **给本地 Agent 喂免费算力**：Codex CLI、OpenCode、Cline 等本要配付费 key 的工具，可把 base_url 指到 `localhost:8081/v1` 白嫖 Gemini 网页额度（匿名 Flash 或付费账号 cookie 解锁 Pro）。
- **逆向私有协议的范式**：本项目是把"网页端内部 API 当作免费后端"的典型做法——`inner[79]` 这类魔数索引字段的破译方式，是爬虫/协议逆向的通用思路（先抓前端 JS 的枚举，再映射到请求数组下标）。
- **协议翻译器设计**：OpenAI↔厂商私有格式的双射转换，与 LiteLLM、OneAPI 思路一致但更轻——适合学习"最小可用 API 网关"怎么写。

## 四、源码深度解读

**① 协议载荷构造**（`gemini_web2api/gemini.py`）
```python
def _build_payload(prompt, model_id, think_mode, ...):
    inner = [None] * 102                       # 102 长度的位置数组
    inner[0]  = [prompt, 0, None, refs, None, None, 0]
    inner[17] = [[think_mode]]                # 思考深度
    inner[79] = model_id                      # 模型选择 (MODE_CATEGORY 枚举)
    inner[59] = str(uuid.uuid4())             # 请求指纹
    outer = [None, json.dumps(inner)]
    return urllib.parse.urlencode({"f.req": json.dumps(outer), "at": xsrf})
```
关键点：Gemini Web 的请求体是一个**定长位置数组**，模型与思考深度都是"数组下标"而非命名字段——逆向者必须从前端 JS 还原 `MODE_CATEGORY` 枚举到 `inner[79]` 的映射。

**② 鉴权头构造**（`gemini.py`）
```python
def make_sapisidhash(sapisid):
    ts = int(time.time())
    h = hashlib.sha1(f"{ts} {sapisid} https://gemini.google.com".encode()).hexdigest()
    return f"SAPISIDHASH {ts}_{h}"
# _build_headers 注入 Cookie + Authorization: SAPISIDHASH ...
```
这是 Google 网页端标准的 `SAPISIDHASH` 校验，配合从 `gemini.google.com` 抓的 `__Secure-1PSID` 等 cookie，复现"已登录网页"的身份。

**③ OpenAI 兼容服务端**（`server.py`）
```python
class GeminiHandler(BaseHTTPRequestHandler):
    def _authorized(self):
        keys = CONFIG.get("api_keys") or []
        if not keys: return True                     # 留空=免鉴权
        auth = self.headers.get("Authorization","")
        return auth.startswith("Bearer ") and auth[7:] in keys
    def do_POST(self): ... # /v1/chat/completions → generate_stream → SSE
```
用标准库 `http.server` + `ThreadingMixIn` 即可，无需 Flask；还手动解析 chunked 请求体，体现了对"最小依赖"的执着。

## 五、全网口碑

- 星标 3,361⭐，长期活跃（最后提交 2026-08），中文文档 `README_CN.md` 完善；被 LinuxDo 社区与 GenericAgent 项目引用致谢。
- 在"免费 Gemini 代理"细分里属于**维护较好、协议真实逆向**的一档，区别于纯套壳或依赖第三方中转的方案。

## 六、竞品对比

| 方案 | 依赖 | 协议真实性 | 多模型 |
|---|---|---|---|
| **gemini-web2api** | 纯 Python + httpx | ✅ 逆向 StreamGenerate | Flash/Pro/think 全支持 |
| gemini-api-free (社区) | 常需中转 | ⚠️ 依赖第三方 | 有限 |
| LiteLLM / OneAPI | 多依赖、需 key | ❌ 走官方 API | 全模型统一网关 |
| gpt-academic 类 | 重 | 混合 | 混合 |

**研判**：它是"用网页额度当免费后端"的轻量标杆，适合个人开发/实验；**合规与稳定性是硬约束**——Google 随时改 `bl=` 版本号或协议字段就会失效（README 明确要求 `gemini_bl` 随前端更新），且匿名额度有速率限制。生产环境不建议依赖。

## 七、核心研判

对个人 Agent 玩家是"零成本接 Gemini"的利器，也是学习**私有协议逆向 + 协议翻译网关**的好样本。需清醒认知：这是游走在 Google ToS 边缘的"灰色便利"，脆弱且不可用于生产；把它当学习材料比当基础设施更合适。

## 八、关键文件路径速查

- `gemini_web2api/gemini.py` — 协议核心（`_build_payload` / `make_sapisidhash` / `StreamGenerate` 解析）
- `gemini_web2api/server.py` — OpenAI 兼容 HTTP 服务（`GeminiHandler`）
- `gemini_web2api/tools.py` — messages↔prompt、tool_calls 转换
- `gemini_web2api/multimodal.py` — 图片上传（`upload_image`）
- `gemini_web2api/config.py` / `models.py` — 配置与模型注册表
- `cloudflare/` — Cloudflare Worker 部署变体
- `config.example.json` — 端口/cookie/proxy/xsrf 等配置样例
