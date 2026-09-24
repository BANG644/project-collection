# 🔬 PleasePrompto/notebooklm-skill - 全方位深度调研

## 📌 一句话定位
`PleasePrompto/notebooklm-skill` 是一个让 **Claude Code 直接查询你的 Google NotebookLM 笔记本** 的 agent skill——每次提问都开新浏览器会话、仅从你上传的文档检索，用 Gemini 产出"有来源、带引用、降幻觉"的答案，适合把私人知识库当 agent 的检索后端。

## ⭐ 项目亮点
- **源 grounding 降幻觉**：强制"只答自有文档"，每个回答末尾追问「Is that ALL you need to know?」并自动追问补齐，再综合作答——把 RAG 的"检索-追问-综合"固化进 skill 工作流。
- **统一 run.py 包装器**：所有脚本必须经 `python scripts/run.py <script>` 调用；首次运行自动建 `.venv`、装依赖、装 Chromium，规避"直接跑脚本缺环境"的常见坑。
- **智能 Add（Smart Discovery）**：新增笔记本时先 `ask_question` 探其内容再登记元数据（`--name`/`--description`/`--topics` 必填且禁止瞎猜），保证库索引质量。
- **本地库管理 + 持久化鉴权**：`notebook_manager.py` 管 `library.json`（增删查激活）、`auth_manager.py` 管 Google 登录（`data/auth_info.json` + `browser_state/`），且全部 `.gitignore` 保护不入库。
- **跨平台 + 反检测可选**：`run.py` 的 `get_venv_python()` 区分 Windows `Scripts/` 与 Unix `bin/`；`.env` 可开 `STEALTH_ENABLED` 拟人化输入。

## 🏗️ 项目架构全景
### 仓库结构（master 树）
- `SKILL.md` — 路由 + 决策流（何时用、必走 run.py、追问机制、脚本参考、排错表）。
- `scripts/`：`run.py`（统一 runner）、`auth_manager.py`（OAuth 状态/setup/reauth/clear）、`notebook_manager.py`（add/list/search/activate/remove/stats）、`ask_question.py`（提问）、`browser_session.py`/`browser_utils.py`（patchright 浏览器封装）、`cleanup_manager.py`、`config.py`、`setup_environment.py`。
- `references/`：`api_reference.md` / `troubleshooting.md` / `usage_patterns.md`（扩展文档）。
- `requirements.txt`、`.gitignore`、数据存 `~/.claude/skills/notebooklm/data/`。

### 运行模型
用户提及 NotebookLM → 查 auth → 未登录则 `auth_manager setup`（**浏览器可见手动 Google 登录**）→ 列/加/激活笔记本 → `ask_question` 提问 → 触发追问直到信息完整 → 综合回复。每次提问新建浏览器会话（**无会话持久化**）。

## 💡 应用场景与启发
- **私人知识库的 agent 检索后端**：把论文/教材/内部资料传 NotebookLM，再让 Claude Code 引用作答——和 paper-companion（论文伴读）的"分层记忆 + 引用链"思路互补：NotebookLM 管"已上传文档的 grounding"，agent 管"对话与综合"。
- **「run.py 统一环境」范式**：对含 Python 依赖的 skill，用 runner 自动建 venv、装依赖、调度子脚本，彻底解决"agent 直接跑脚本环境错配"，值得任何本地 Python skill 借鉴。
- **「追问-综合」机制**：强制在多轮检索后才给用户综合答案，是缓解一次性问答遗漏的有效设计，可复用到问答类 agent。

## 🧠 核心源码解读
### 1. run.py 的 venv 自举（跨平台）
```python
def get_venv_python():
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"
    if os.name == 'nt':                       # Windows
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"        # Unix/Mac

def ensure_venv():
    if not venv_dir.exists():
        subprocess.run([sys.executable, str(setup_script)])
    return get_venv_python()
```
子脚本调度：`cmd = [venv_python, script_path] + script_args`，并容错 `KeyboardInterrupt`/异常退出码。

### 2. SKILL.md 强制「永远经 run.py」
```text
NEVER call scripts directly. ALWAYS use `python scripts/run.py [script]`:
python scripts/run.py auth_manager.py status   # ✅
python scripts/auth_manager.py status          # ❌ Fails without venv!
```
这是把"环境契约"写进 skill 指令，避免 agent 用系统 Python 直接跑导致缺包。

### 3. 追问机制（Follow-Up）
每个答案末尾固定提示「EXTREMELY IMPORTANT: Is that ALL you need to know?」→ agent 比对原始请求找缺口 → 有则立即再 `ask_question` → 循环至完整 → 综合回复。配合"每次提问新浏览器会话"，以"多次独立检索"换"答案完整性"。

## 🌐 全网口碑画像
- **社区信号**：7.8k⭐ / 886 fork（2025-10 创建，2026-09 仍有更新），属于"知识库 grounding"热点下的热门 skill。
- **定位共识**：被视为"Claude Code 连 NotebookLM 的桥"，核心价值在"只用自有文档、降幻觉"。
- **明确限制（作者在 README 直说）**：免费 Google 账号 50 次/天限额、文档需手动上传、每次提问有浏览器开销（数秒）、无会话持久化。`.gitignore` 明确保护 auth 数据，安全意识到位。

## ⚔️ 竞品对比
| 维度 | notebooklm-skill | 直接用 NotebookLM Web/API | 通用 RAG skill |
|------|----------------|--------------------------|---------------|
| agent 原生 | Claude Code 内 | 需切网页 | 视实现 |
| 数据源 | 仅自有 NotebookLM 文档 | 同 | 任意 |
| 降幻觉 | 源 grounding + 追问 | 同 | 取决于检索 |
| 依赖 | 浏览器自动化（patchright） | 无 | 向量库 |

## 🎯 核心研判
- **优势**：把"私人文档 grounding + 多轮追问 + 综合"做成开箱即用的 Claude Code skill；run.py 环境自举与 `.gitignore` 保护是可复用的最佳实践。
- **风险**：依赖 Google 账号与 NotebookLM 可用性；免费 50 次/天限额偏低；浏览器自动化（patchright）较脆、每次有开销；非会话持久化。
- **趋势**：与"agent + 私人知识库"浪潮同频，对已有 NotebookLM 资料库的用户是低成本增强；也可作为 paper-companion 之外"文档检索后端"的候选方案。

## 📂 关键文件路径速查
- `SKILL.md` — 路由、决策流、追问机制、排错表
- `scripts/run.py` — 统一 venv runner（环境自举）
- `scripts/ask_question.py` — 提问接口
- `scripts/notebook_manager.py` — 笔记本库管理
- `scripts/auth_manager.py` — Google OAuth 状态/setup
- `references/api_reference.md` / `troubleshooting.md` / `usage_patterns.md`
- 仓库：`https://github.com/PleasePrompto/notebooklm-skill`
