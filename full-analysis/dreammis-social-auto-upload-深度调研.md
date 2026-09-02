# dreammis/social-auto-upload 深度调研

> 调研日期：2026-09-03 ｜ 星标：14,735 ⭐ ｜ 语言：Python ｜ 协议：MIT ｜ 默认分支：main ｜ 最后推送：2026-09-02
> 定位：把视频/图文一键分发到国内外 11+ 主流社交平台的自动化上传工具（抖音/Bilibili/小红书/快手/视频号/TikTok/YouTube 等）

## 一、项目亮点（差异化）

1. **统一多平台分发**：单仓库覆盖抖音、Bilibili、小红书、快手、视频号、百家号、支付宝生活号、微博、虎扑、TikTok、YouTube 的上传与定时发布，创作者矩阵运营一处配置。
2. **双集成范式**：有开放 API 的平台（抖音/Bilibili）走原生接口；无 API 的平台（小红书/快手/视频号等）走浏览器自动化（Playwright/undetected-chromedriver + 反检测 JS）。
3. **三种入口**：`sau_cli.py`（命令行）、`sau_backend`+`sau_frontend`（Web 服务）、`skills/`（OpenClaw/Claude Code Skill），并配 `docs/agent-bootstrap.md` 把仓库直接交给 Agent 安装使用。
4. **活跃维护**：2026-09-02 仍在推送，主线重构（抖音最完整，bilibili/xhs/ks/douyin 优先验证），文档收敛到 `docs/install.md`/`update.md`。
5. **平台能力矩阵可追溯**：README 用表格标注每个平台的登录/上传/图文/定时/CLI/Skill 支持度，便于按需扩展。

## 二、核心架构

`uploader/` 下每个平台一个独立包，共享 `base_video.py` 基类与 `utils/` 公共能力：

- **uploader/base_video.py** — 视频上传器抽象基类（登录→上传→定时发布通用骨架）。
- **utils/base_social_media.py** — 更底层的社交平台抽象；`utils/browser_hook.py` + `utils/stealth.min.js` — 浏览器自动化的 hook 与反检测脚本。
- **myUtils/postVideo.py / login.py / auth.py** — 跨平台共享的发布/登录/鉴权逻辑。
- **双路径**：
  - 原生 API 路径：`douyin_uploader/main.py`、`bilibili_uploader/runtime.py`（运行时自动准备 `biliup`）、`youtube_uploader/main.py`（Studio，支持播放列表/可见性）。
  - 浏览器自动化路径：`xhs_uploader/`（含 `xhs_login_qrcode.py` 二维码登录）、`ks_uploader/`、`tencent_uploader/`（视频号）、`tk_uploader/main_chrome.py`（TikTok Chrome 版）等。
- **服务层**：`sau_backend.py`（FastAPI 后端）、`sau_frontend/`（前端）、`sau_cli.py`（CLI 入口）。

## 三、应用场景与启发

- **场景**：内容矩阵运营者、多平台分发、AI 自动化运营（把「高频重复无聊」的上传交给脚本，Agent 只做决策）。
- **启发 1**：「有 API 走 API、无 API 走浏览器自动化」的**分层适配器**是打通多封闭平台的可行范式，比等官方开放更实际。
- **启发 2**：把上传这一高频重复动作从 Agent 的「每次截图理解网页」中剥离为确定性脚本，是 Agent 工程里「把稳定动作脚本化」的典型实践。
- **启发 3**：`skills/` + `agent-bootstrap.md` 让仓库本身成为可被 Agent 消费的工具，契合「仓库即技能」趋势。

## 四、源码深度解读

### 1. 平台适配器模式（`uploader/base_video.py` + 各 `main.py`）
```python
# 每个平台 uploader 继承基类，实现 login/upload/schedule
class DouyinUploader(BaseVideo):
    def login(self): ...        # 扫码/ Cookie 登录
    def upload(self, video, ...): ...   # 调原生 API 或浏览器流程
    def schedule(self, time): ...       # 定时发布
```
统一接口让新增平台只需在 `uploader/<platform>_uploader/main.py` 实现三件事，README 能力矩阵即由这些实现回填。

### 2. 浏览器自动化反检测（`utils/stealth.min.js` + `utils/browser_hook.py`）
无开放 API 的平台靠 Playwright/undetected-chromedriver 驱动网页，`stealth.min.js` 注入抹除 `navigator.webdriver` 等自动化指纹，`browser_hook.py` 统一网页事件钩子。这是小红书/快手/视频号能稳定上传的技术底座，也是这类工具最易失效、需持续维护的部分。

### 3. 后端/CLI 双入口（`sau_backend.py` + `sau_cli.py`）
`sau_cli.py` 提供命令行批量发布；`sau_backend`（FastAPI）+ `sau_frontend` 提供可视化任务管理。二者最终都落到 `uploader/*` 与 `myUtils/postVideo.py`，保证「同一套上传逻辑，多入口调用」。

## 五、全网口碑

- 14.7k ⭐，中文内容运营圈高人气，长期活跃（几乎每日推送），被视作「国内多平台视频分发」最全的开源方案。
- 定位认知：口碑核心是「覆盖平台广 + 抖音主线成熟 + 给 Agent 用友好」；README 含赞助商与 Agent Bootstrap 提示词，社区运营强。
- 客观短板：① 浏览器自动化平台（小红书/快手/视频号等）随平台前端改版易失效，需持续跟版；② 涉及账号 Cookie/登录态，有封号与隐私风险；③ 各平台完成度不均（抖音最完整，部分仅初版）。
- 数据说明：平台矩阵/结构来自仓库一手元数据与 README；社区评价为公开普遍认知。

## 六、竞品对比 + 核心研判

| 维度 | social-auto-upload | biliup | youtuba/单平台脚本 | OpenClaw media skill | TubeBuddy(手动) |
|---|---|---|---|---|---|
| 覆盖平台 | 11+ 国内外 | 主要 Bilibili | 单平台 | 取决于 skill | 单平台手动 |
| 集成方式 | API+浏览器自动化 | API | API | Agent 驱动 | 网页手动 |
| 入口 | CLI/Web/Skill | CLI | CLI | 对话 | 网页 |
| 抗平台变更 | 中(浏览器易失效) | 高 | 中 | 中 | — |

**核心研判**：
- ✅ **价值确定**：在「多平台视频分发」这一强需求上，统一仓库 + 双集成范式显著降低运营心智负担，且对 Agent 友好，采用风险低、收益直接。
- ⚠️ **风险点**：浏览器自动化平台的前后端脆弱性、账号封禁/隐私合规、各平台完成度不均。
- 🔮 **趋势**：随 Agent 化运营兴起，「仓库即 skill + agent-bootstrap」会让这类工具成为自动化运营底座；平台收紧自动化会刺激更隐蔽的反检测演进。
- 💡 **启发迁移**：做跨封闭平台工具时，优先「API 优先、浏览器自动化兜底」的分层适配器，并把稳定动作脚本化、把决策留给 Agent。

## 七、关键文件路径速查

| 路径 | 作用 |
|---|---|
| `uploader/base_video.py` | 视频上传器抽象基类 |
| `uploader/douyin_uploader/main.py` | 抖音（主线最完整，原生 API） |
| `uploader/bilibili_uploader/runtime.py` | Bilibili（运行时准备 biliup） |
| `uploader/xhs_uploader/`（含 `xhs_login_qrcode.py`） | 小红书（浏览器+二维码登录） |
| `uploader/tencent_uploader/main.py` / `tk_uploader/main_chrome.py` | 视频号 / TikTok(Chrome) |
| `utils/base_social_media.py` / `utils/browser_hook.py` / `utils/stealth.min.js` | 平台抽象 + 浏览器钩子 + 反检测 |
| `myUtils/postVideo.py` / `login.py` / `auth.py` | 跨平台发布/登录/鉴权 |
| `sau_cli.py` / `sau_backend.py` / `sau_frontend/` | CLI / FastAPI 后端 / 前端 |
| `skills/` / `docs/agent-bootstrap.md` | Agent 技能与启动提示词 |
