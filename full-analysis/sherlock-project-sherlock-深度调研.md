# Sherlock 深度调研报告

> 调研时间：2026-11-08 ｜ 编号：#576 ｜ 来源：GitHub Trending（daily）净新增
> GitHub：https://github.com/sherlock-project/sherlock ｜ 许可：MIT
> 语言：Python ｜ ⭐ 100,128 ｜ Fork 11,844 ｜ Open Issues 362 ｜ 末次推送 2026-11-07

---

## 一、项目全景

Sherlock 是 OSINT（开源情报）领域**用户名校验利器**：给定一个用户名，跨 **400+ 社交网络**查询该账号是否存在，输出命中的站点清单（txt / csv / xlsx / json）。它是最受欢迎的「用户名足迹追溯」工具之一，100k+ ⭐、11.8k fork，支持 `pipx` / `docker` / 各发行版包安装，提供丰富的 CLI 选项（代理、NSFW 过滤、站点限定、本地数据、忽略排除表等）。

---

## 二、项目亮点（差异化）

1. **400+ 站点覆盖**：社区持续维护的站点清单，是同类最广之一。
2. **数据驱动、易扩展**：站点信息全部放在 `data.json`，新增站点无需改代码。
3. **并发高效**：基于 `requests-futures` 的异步请求，对大量站点并行探测。
4. **多检出策略**：支持 `message` / `status_code` / `response_url` 等多种「账号存在」判定。
5. **分发友好**：pipx / Docker / 系统包 / `--json` 脚本化，便于集成到工作流。

---

## 三、核心架构

Python 包 `sherlock_project/`，结构清晰：

| 文件 | 职责 |
|------|------|
| `sherlock.py` | 主逻辑：参数解析、异步请求（`SherlockFuturesSession`）、结果判定与输出 |
| `sites.py` | `SiteInformation` / `SitesInformation`：加载并解析站点清单（本地或远程） |
| `resources/data.json` | 站点数据库（`$schema` + 每站点 `url` / `urlMain` / `errorType` / `errorMsg` / `regexCheck` / `isNSFW` / `username_claimed`） |
| `resources/data.schema.json` | data.json 的 JSON Schema 校验 |
| `result.py` | `QueryStatus` / `QueryResult` 状态与结果建模 |
| `notify.py` | 结果通知（终端打印等） |

数据流：`用户名 → 加载 data.json（默认取远程最新）→ 为每个站点构造 URL → 并发请求 → 按 errorType 判定存在与否 → 聚合输出`。

---

## 四、源码深度解读

### 1. 站点清单加载——默认取远程最新（`sites.py`）

```python
if not data_file_path:
    # 默认用 GitHub 仓里的实时 data.json，保证用户拿到最新数据，避免报告已修复的误报/过期数据
    data_file_path = MANIFEST_URL   # https://data.sherlockproject.xyz
if data_file_path.lower().startswith("http"):
    response = requests.get(url=data_file_path, timeout=30)
    ...
    site_data = response.json()
```

要点：`SitesInformation` 默认从 `MANIFEST_URL` 拉取**实时** data.json，而非本地文件——目的是让用户始终用最新站点数据，减少「已修复的误报」被反复提 issue。`honor_exclusions` 还会从 `exclusions/false_positive_exclusions.txt` 拉取排除表，剔除已知误报站点。每个站点被建模为 `SiteInformation`，含 `url_username_format`（`{}` 占位用户名）、`username_claimed`、`is_nsfw` 等。

### 2. 异步请求与耗时度量（`sherlock.py`）

```python
class SherlockFuturesSession(FuturesSession):
    def request(self, method, url, hooks=None, *args, **kwargs):
        start = monotonic()
        def response_time(resp, *args, **kwargs):
            resp.elapsed = monotonic() - start
        # 把耗时 hook 插到最前，避免计入后续 hook 的执行时间
        hooks["response"].insert(0, response_time)
        return super().request(method, url, hooks=hooks, *args, **kwargs)
```

要点：继承 `FuturesSession`，通过 response hook 在**最前**插入耗时测量（不把后续 hook 的执行时间算进去），从而对每个站点的请求做准确度量；`get_response` 再对 `request_future.result()` 做 HTTPError / ProxyError / ConnectionError 等异常归类。判定逻辑由 data.json 的 `errorType`（`message` 比错误文案、`status_code` 比状态码、`response_url` 比跳转后 URL）驱动。

---

## 五、应用场景与启发

- **OSINT / 安全研究 / 用户名抢注排查**：人肉一个用户名的各平台足迹、确认自己账号是否被盗用克隆，是 Sherlock 的主场。
- **「数据驱动的检测规则」架构可借鉴**：把「怎么判存在」完全外置到 JSON，代码只负责执行与并发——任何「按站点/按规则批量探测」的工具（如本工作区可能涉及的链接存活巡检）都可套用这套「规则数据化 + 异步执行」骨架。

---

## 六、社区口碑

- 正面：100k+ ⭐、长期活跃、站点覆盖最广之一，是 OSINT 入门与实战的标配工具；Docker / pipx / 系统包分发齐全。
- 注意点：误报/漏报依赖社区维护 data.json 的质量；README 明确警告 **ParrotOS 与 Ubuntu 24.04 的第三方包疑似损坏**，建议用 `uv` / `pipx` / `pip` / Docker；NSFW 站点默认排除、可用 `--nsfw` 开启。

---

## 七、竞品对比

| 项目 | 定位 | 与 Sherlock 差异 |
|------|------|------------------|
| maigret | 用户名跨站搜索 | 站点数相近，偏账号聚合画像 |
| socialscan | 用户名/邮箱存在性校验 | 站点较少、更偏验证码绕过 |
| whatsmyname | 用户名足迹清单 | 偏 Web 查、非 CLI 并发引擎 |
| **Sherlock** | 400+ 站点 + 并发 + 数据驱动 | 覆盖广、异步高效、社区维护活跃 |

---

## 八、核心研判

Sherlock 是「数据驱动的批量探测」范式的最易读范本：核心复杂度（怎么判存在、覆盖哪些站点）全部外置到 `data.json` + `data.schema.json`，代码只做并发执行与结果聚合。其长盛不衰靠的是**社区持续维护的站点库**。短板是完全依赖清单质量、误报需人工治理。对「需要按规则批量探活/查证」的工程需求，它是值得拆解借鉴的轻量架构样本。

---

## 九、关键文件路径速查

- `sherlock_project/sherlock.py`：主逻辑、`SherlockFuturesSession`、请求 hook
- `sherlock_project/sites.py`：`SiteInformation` / `SitesInformation`、远程/本地数据加载、排除表
- `sherlock_project/resources/data.json`：400+ 站点数据库（`errorType` / `errorMsg` / `regexCheck` / `isNSFW`）
- `sherlock_project/resources/data.schema.json`：数据校验 Schema
- `sherlock_project/result.py` / `notify.py`：状态建模与结果通知
- `.github/workflows/`：`update-site-list` / `regression` / `validate_modified_targets` 等站点维护流水线
