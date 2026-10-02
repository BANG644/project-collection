# pyfuze 深度调研

> 数据来源：GitHub API 抓取（stars / README / 目录树 / pyproject.toml / src/pyfuze/cli.py），抓取日期 2026-10-03。许可：MIT。版本：2.7.2（已上 PyPI）。

## 一、项目定位（一句话）
把 Python 项目打包成**单个可执行文件**的 CLI 工具，基于 **cosmopolitan（APE）+ uv**，提供 bundle / online / portable 三种打包模式。

## 二、项目亮点（差异化）
1. **三模式权衡**：bundle（内置 Python+依赖，同平台最高兼容）、online（小体积跨平台，运行期下载依赖）、portable（纯 Python 跨平台 `.com`，无需解压/联网，基于 APE）。
2. **复用现代工具链**：uv 做依赖解析与锁文件（`pyproject.toml` / `uv.lock`），cosmopolitan 提供真·跨平台单文件。
3. **丰富 CLI**：`--entry / --reqs / --include / --exclude / --win-gui / --env(镜像) / --uv-install-script-*`，覆盖生产分发细节。
4. **跨平台目标**：macOS（ARM64/AMD64）、Linux（AMD64）、Windows（AMD64）。

## 三、核心架构
- **语言**：纯 Python（click CLI）+ C 扩展（`csrc/`，cosmo 相关）+ 外部依赖 cosmopolitan / uv。
- **入口**：`pyproject.toml` → `[project.scripts] pyfuze = "pyfuze.cli:cli"`；仅依赖 `click>=8.1.8`；构建后端 `uv_build`。
- **逻辑**：`src/pyfuze/cli.py`（click 命令定义）+ `src/pyfuze/utils.py`（打包实现）+ `src/pyfuze/__main__.py`。
- **portable 模式**：使用 `python.com`（APE，固定 Python 3.12.3）把脚本固化为跨平台 `.com`。

## 四、应用场景与启发
- 给「Python 分发」提供了不依赖 PyInstaller / Nuitka 的新选择——尤其 **portable（APE）单文件跨平台**对工具分发极其友好。
- **online 模式**用 uv 运行期拉依赖 + 可配镜像（`UV_DEFAULT_INDEX` / `UV_PYTHON_INSTALL_MIRROR`），适合受限网络环境分发。
- 可借鉴其「三模式权衡」设计：在「体积 / 跨平台 / 兼容性」三角中让用户按需选择。

## 五、源码深度解读
`pyproject.toml` 的入口与依赖：
```toml
[project]
name = "pyfuze"
requires-python = ">=3.8"
dependencies = ["click>=8.1.8"]
[project.scripts]
pyfuze = "pyfuze.cli:cli"
[build-system]
requires = ["uv_build>=0.7.3,<0.8"]
build-backend = "uv_build"
```
`src/pyfuze/cli.py` 用 click 定义命令骨架：
```python
@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("python_project", type=click.Path(exists=True, dir_okay=True, path_type=Path))
@click.option("--mode", "mode", default="bundle", help="bundle/online/portable ...")
@click.option("--entry", "entry", default="main.py", show_default=True, ...)
@click.option("--win-gui", is_flag=True, help="Hide the console window on Windows")
@click.option("--env", "env", multiple=True, help="INSTALLER_DOWNLOAD_URL/UV_PYTHON_INSTALL_MIRROR/UV_DEFAULT_INDEX ...")
@click.version_option(__version__, "-v", "--version", prog_name="pyfuze")
def cli(...): ...
```
要点：① 参数化打包全流程（入口/依赖/包含排除/镜像），用 `multiple=True` 支持重复 `--include/--env`；② 默认 `bundle` 模式，portable 仅支持纯 Python（兼容性低但零依赖）；③ 明确声明「不做代码加密/混淆」——定位是打包而非保护。

## 六、全网口碑
约 **889 ⭐**，已发布 PyPI（`pip install pyfuze` / `uvx pyfuze`），版本 2.7.2，有 Discord 与 QQ 群。⚠️ 本次无人值守巡检未单独爬取深度舆情；PyPI 上架与社区群反映项目可用度良好。

## 七、竞品对比
| 维度 | pyfuze | PyInstaller | Nuitka | shiv/pex | Briefcase |
|------|--------|-------------|--------|----------|-----------|
| 原理 | cosmo+uv | 打包引导 | 编译为 C | zipapp | 各平台安装包 |
| 单文件跨平台 | portable ✅ | ❌（按平台） | ❌ | ❌ | ❌ |
| 体积 | 可选小(online) | 大 | 中 | 中 | 大 |
| 加密 | ❌（明确不做） | 弱 | ✅(编译) | ❌ | ❌ |

差异化：基于 cosmo+uv、portable 真跨平台 `.com`、online 轻量。
- **风险**：portable 仅支持纯 Python（API 兼容性低）；bundle 体积大；跨平台受 uv / APE 平台支持限制。

## 八、核心研判
小众但思路新颖的打包工具，**portable（APE）模式是真亮点**——真正单文件跨平台，对非技术用户分发 exe/sh/com 很实用。
- **适合**：需要「给非技术用户发一个可执行文件」的脚本/小工具分发场景。
- **注意**：不做代码加密/混淆（README 明确），敏感代码需用其他方案；选型前先评估 portable 对纯 Python 的适用面与 bundle 体积成本。

## 关键文件路径速查
- `src/pyfuze/cli.py` — click 命令定义（参数全景）
- `src/pyfuze/utils.py` — 打包核心逻辑
- `src/pyfuze/__main__.py` — 模块入口
- `csrc/` — C 扩展（cosmopolitan 相关）
- `pyproject.toml` — 入口与依赖
- `examples/` — simple.py / complex/（含 windows_part / unix_part 分平台示例）
