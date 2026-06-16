# 🔬 dreammis/social-auto-upload - 全方位深度调研

## 项目全景
- **仓库**：`dreammis/social-auto-upload`
- **一句话定位**：自动化上传视频到社交媒体：抖音、小红书、视频号、tiktok、youtube、bilibili
- **基础指标**：Stars=12435 / Forks=2176 / 默认分支=`main`
- **Topics**：bilibili, douyin, tiktok, xiaohongshu, youtube
- **Homepage**：https://sap-doc.nasdaddy.com/

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：sau_frontend(28), skills(28), uploader(22), examples(16), docs(11), media(11), utils(9), tests(5), videos(5), myUtils(4)
- 关键文件候选：pyproject.toml, requirements.txt, README.md, CLAUDE.md, tests/__init__.py, tests/test_bilibili_runtime.py, tests/test_sau_bilibili_cli.py, tests/test_sau_browser_cli.py, tests/test_xiaohongshu_uploader.py

### 设计亮点研判
- 存在 Python 工程入口，通常意味着自动化流水线、服务端或研究脚本由 Python 主导。
- 仓库包含测试代码，说明作者至少为关键行为建立了回归验证。

## 源码深度解读
### README / 说明文档要点
# social-auto-upload

`social-auto-upload` 是一个强大的自动化工具，旨在帮助内容创作者和运营者高效地将视频内容一键发布到多个国内外主流社交媒体平台。
项目实现了对 `抖音`、`Bilibili`、`小红书`、`快手`、`视频号`、`百家号` 以及 `TikTok` 等平台的视频上传、定时发布等功能。
结合各平台 `uploader` 模块，您可以轻松配置和扩展支持的平台，并通过示例脚本快速上手。

<img src="media/show/tkupload.gif" alt="tiktok show" width="800"/>

## 💎 赞助商

<table width="100%">
  <tr>
    <td width="25%" align="center" valign="middle">
      <a href="https://chilltion.com/?ref=1y5k5k">
        <img src="static/chilltion.png" alt="chilltion Sponsor" width="180">
      </a>
    </td>
    <td width="75%" align="left" valign="middle">
      轻视AI：一句话生产MG动画，适合知识，科普，讲解，教程，介绍等类型视频的低成本制作，视频矩阵，养号等，成本只有seedance等1%。现在<a href="https://chilltion.com/?ref=1y5k5k">注册</a>送1500积分
    </td>
  </tr>
    <tr>
        <td width="25%" align="center" valign="middle">
          <a href="http://t.clawpower.vip/1005">
            <img src="static/clawpower.png" alt="ClawPower Sponsor" width="180">
          </a>
        </td>
        <td width="75%" align="left" valign="middle">
          ClawPower 是一家稳定可靠 AI 大模型中转服务商，提供 Claude、GPT、Gemini 60+ 大模型接入。无论是 OpenClaw、Hermes 智能体自动化场景，Claude Code、Codex 编程工具接入，还是公众号、小红书内容创作；都能获得稳定、顺滑、可长期使用的模型服务体验。低至官方价格的 30%，点击<a href="http://t.clawpower.vip/1005">免费领取 5 刀现金</a>体验券
        </td>
      </tr>
  <tr>
    <td width="25%" align="center" valign="middle">
      <img src="static/wechat.png" alt="Sponsor Contact" width="150">
    </td>
    <td width="75%" align="left" valign="middle">
      <strong>成为赞助商</strong><br>
      如果您有意赞助本项目，请扫描左侧微信二维码（添加时请注明来意：<strong>赞助</strong>）。
    </td>
  </tr>
</table>

---


## 目录

- [💡 功能特性](#💡功能特性)
- [💾 安装指南](#💾安装指南)
- [🤖 AI Agent](#🤖ai-agent)
- [🏁 快速开始](#🏁快速开始)
- [🗂️ 重构计划](#🗂️重构计划)
- [📣 近况说明](#📣近况说明)
- [🐇 项目背景](#🐇项目背景)
- [📃 详细文档](#📃详细文档)
- [🐾 交流与支持](#🐾交流与支持)
- [🤝 贡献指南](#🤝贡献指南)
- [📜 许可证](#📜许可证)
- [⭐ Star History](#⭐Star-History)

## 💡功能特性

| 平台 | 登录/账号准备 | 视频上传 | 图文上传 | 定时发布 | CLI | Skill | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 抖音 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 当前主线重构最完整 |
| Bilibili | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | 运行时自动准备 `biliup` |
| 小红书（浏览器版） | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 浏览器自动化，CLI/Skill 已接入 |
| 快手 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 浏览器自动化，CLI/Skill 初版已接入 |
| 视频号 | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | 对应 `tencent_uploader` |
| 百家号 | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | 浏览器自动化 |
| TikTok | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | 当前示例走 Chrome 版实现 |

### AI这么强，为什么还需要这个项目
在你使用AI的能力，browser agent等等，每次都让 agent 重新解析网页、截图理解, 临场判断
该项目经过大量验证，上传这种 高频，重复，无聊的工作交给脚本和程序去执行


## 💾安装指南

### 自己上手使用
如果你只是普通用户，不准备借助 agent 客户端，直接看

安装、更
...[truncated]

### 关键文件精读
### `pyproject.toml`
```
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "social-auto-upload"
version = "0.1.0"
description = "Social media auto uploader"
readme = "README.md"
requires-python = ">=3.10,<3.13"
dependencies = [
  "loguru==0.7.3",
  "opencv-python>=4.13.0.92",
  "patchright==1.58.2",
  "qrcode==8.2",
  "requests==2.32.3",
  "segno>=1.6.6",
]

[project.scripts]
sau = "sau_cli:main"

[project.optional-dependencies]
web = [
  "Flask[async]==3.1.1",
  "flask-cors==6.0.0",
]

[tool.uv]
package = true

[tool.setuptools]
py-modules = ["cli_main", "conf", "sau_cli"]
include-package-data = true

[tool.setuptools.packages.find]
include = ["uploader*", "utils*", "myUtils*"]

[tool.setuptools.package-data]
utils = ["stealth.min.js"]
```

### `requirements.txt`
```
﻿aiofiles==24.1.0
aiohttp==3.9.5
aiohttp-cors==0.8.1
aiosignal==1.3.2
alembic==1.16.1
anyio==4.9.0
asgiref==3.8.1
async-lru==2.0.5
async-timeout==4.0.3
attrs==25.3.0
backports-datetime-fromisoformat==2.0.3
biliup==0.4.98
blinker==1.9.0
Brotli==1.1.0
certifi==2025.4.26
cf_clearance==0.31.0
cffi==1.17.1
charset-normalizer==3.4.2
click==8.2.1
colorama==0.4.6
dnspython==2.7.0
eventlet==0.40.0
exceptiongroup==1.3.0
Flask[async]==3.1.1
flask-cors==6.0.0
frozenlist==1.6.0
greenlet==3.2.2
h11==0.16.0
h2==4.2.0
hpack==4.1.0
httpcore==1.0.9
httpx==0.28.1
hyperframe==6.1.0
idna==3.10
isodate==0.7.2
itsdangerous==2.2.0
Jinja2==3.1.6
jsengine==1.0.7.post1
loguru==0.7.3
lxml==5.4.0
m3u8==6.0.0
Mako==1.3.10
MarkupSafe==3.0.2
multidict==6.4.4
outcome==1.3.0.post0
pillow==11.2.1
playwright==1.52.0
propcache==0.3.1
protobuf==6.31.1
psutil==7.0.0
pyasn1==0.6.1
pycountry==24.6.1
pycparser==2.22
pycryptodome==3.23.0
pyee==13.0.0
PySocks==1.7.1
PyYAML=
...[truncated]
```

### `README.md`
```
# social-auto-upload

`social-auto-upload` 是一个强大的自动化工具，旨在帮助内容创作者和运营者高效地将视频内容一键发布到多个国内外主流社交媒体平台。
项目实现了对 `抖音`、`Bilibili`、`小红书`、`快手`、`视频号`、`百家号` 以及 `TikTok` 等平台的视频上传、定时发布等功能。
结合各平台 `uploader` 模块，您可以轻松配置和扩展支持的平台，并通过示例脚本快速上手。

<img src="media/show/tkupload.gif" alt="tiktok show" width="800"/>

## 💎 赞助商

<table width="100%">
  <tr>
    <td width="25%" align="center" valign="middle">
      <a href="https://chilltion.com/?ref=1y5k5k">
        <img src="static/chilltion.png" alt="chilltion Sponsor" width="180">
      </a>
    </td>
    <td width="75%" align="left" valign="middle">
      轻视AI：一句话生产MG动画，适合知识，科普，讲解，教程，介绍等类型视频的低成本制作，视频矩阵，养号等，成本只有seedance等1%。现在<a href="https://chilltion.com/?ref=1y5k5k">注册</a>送1500积分
    </td>
  </tr>
    <tr>
        <td width="25%" align="center" valign="middle">
          <a href="http://t.clawpower.vip/1005">
            <img src="static/clawpower.png" alt="ClawPower Sponsor" width="180">
          </a>
        </td>
        <td width="75%" align="left" valign="
...[truncated]
```

### `CLAUDE.md`
```
## Project Overview

This project, `social-auto-upload`, is a powerful automation tool designed to help content creators and operators efficiently publish video content to multiple domestic and international mainstream social media platforms in one click. The project implements video upload, scheduled release and other functions for platforms such as `Douyin`, `Bilibili`, `Xiaohongshu`, `Kuaishou`, `WeChat Channel`, `Baijiahao` and `TikTok`.

The project consists of a Python backend and a Vue.js frontend.

**Backend:**

*   Framework: Flask
*   Core Functionality:
    *   Handles file uploads and management.
    *   Interacts with a SQLite database to store information about files and user accounts.
    *   Uses `playwright` for browser automation to interact with social media platforms.
    *   Provides a RESTful API for the frontend to consume.
    *   Uses Server-Sent Events (SSE) for real-time communication with the frontend during the login process.

**Frontend:**

*   Framework: 
...[truncated]
```

### `tests/__init__.py`
```

```

### `tests/test_bilibili_runtime.py`
```
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from uploader.bilibili_uploader.runtime import (
    build_biliup_runtime_path,
    ensure_biliup_binary,
    run_biliup_command,
)


class BiliupRuntimeTests(unittest.TestCase):
    def test_build_biliup_runtime_path_returns_platform_path(self):
        path = build_biliup_runtime_path("Windows")
        self.assertTrue(str(path).endswith("biliup.exe"))

    @patch("uploader.bilibili_uploader.runtime.fetch_latest_release")
    def test_ensure_biliup_binary_downloads_when_missing(self, mock_release):
        mock_release.return_value = {
            "tag_name": "v1.0.0",
            "asset_url": "https://example.invalid/biliup.exe",
            "asset_name": "biliup.exe",
        }
        with patch("uploader.bilibili_uploader.runtime.read_local_biliup_version", return_value=None):
            with patch("pathlib.Path.exists", return_value=False):
                with patch("uploader.bilibili_uploader.runt
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #222 [OPEN] zip下载的源码一堆报错 登录报错 上传文件报错 发布平台报错 啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊（comments=[{'id': 'IC_kwDOK1bNks8AAAABFCz2IQ', 'author': {'login': 'wap5259177'}, 'authorAssociation': 'NONE', 'body': 'bug开发么你', 'createdAt': '2026-06-05T16:19:58Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/dreammis/social-auto-upload/issues/222#issuecomment-4633458209', 'viewerDidAuthor': False}] labels=无）
- #220 [OPEN] 如果我要登录tiktok或者youtube，但是密码输入要么就是有风控，要就是提示浏览器不安全，不让登录google账号，这是有什么办法解决么（comments=[{'id': 'IC_kwDOK1bNks8AAAABFKJIDA', 'author': {'login': 'LF-DevJourney'}, 'authorAssociation': 'NONE', 'body': '了解下cdp方式解决google不能登录的问题\n', 'createdAt': '2026-06-07T02:17:52Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/dreammis/social-auto-upload/issues/220#issuecomment-4641146892', 'viewerDidAuthor': False}] labels=无）
- #215 [OPEN] 多账号场景下的浏览器环境隔离方案分享（comments=[] labels=无）
- #214 [OPEN] [Security Audit] Missing Authentication, Path Traversal, CSRF and Dependency Vulnerabilities（comments=[] labels=无）
- #210 [OPEN] B站 code 21566 投稿过于频繁，长时冷却及重新登录均无效（comments=[{'id': 'IC_kwDOK1bNks8AAAABEV4mfw', 'author': {'login': 'RePlayer2'}, 'authorAssociation': 'NONE', 'body': '解决了吗，知道多久能够重置吗，我今天中午之后一直出现这个问题更换cookie账号都试过了任然出现这个问题\n', 'createdAt': '2026-05-31T09:56:15Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/dreammis/social-auto-upload/issues/210#issuecomment-4586350207', 'viewerDidAuthor': False}, {'id': 'IC_kwDOK1bNks8AAAABEq6Ywg', 'author': {'login': 'Dannyliang200'}, 'authorAssociation': 'NONE', 'body': '> 解决了吗，知道多久能够重置吗，我今天中午之后一直出现这个问题更换cookie账号都试过了任然出现这个问题\n\n我切换成了有头模式去发布就可以了，无头发布容易被ban。但是标题简介上传的设置需要微调一下就好了', 'createdAt': '2026-06-03T01:48:54Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/dreammis/social-auto-upload/issues/210#issuecomment-4608399554', 'viewerDidAuthor': False}] labels=无）
- #206 [OPEN] 后端启动了 为什么扫码一直转圈不显示二维码（comments=[{'id': 'IC_kwDOK1bNks8AAAABEZfIEw', 'author': {'login': 'faust2510'}, 'authorAssociation': 'NONE', 'body': '我跟你一样，同一个情况\n显然是bug', 'createdAt': '2026-06-01T06:35:54Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/dreammis/social-auto-upload/issues/206#issuecomment-4590127123', 'viewerDidAuthor': False}] labels=无）

### Pull Requests 抽样
- PR #219 [MERGED] fix(xiaohongshu): limit tags to 10 and add original declaration
- PR #218 [MERGED] feat(douyin): 抖音手动获取cookie
- PR #217 [MERGED] fix: avoid f-string backslash syntax error in xiaohongshu uploader
- PR #216 [MERGED] feat(cli): 支持双比例封面参数
- PR #213 [MERGED] feat(douyin): 发布时自动选择「自主声明」；fix(xiaohongshu): 话题候选超时不再中断发布

### Releases 抽样
- baijiahao（published=2025-04-12T10:53:38Z latest=False）
- ks-support（published=2024-08-08T10:38:08Z latest=False）
- tk-chrome（published=2024-07-03T08:58:10Z latest=False）
- oh-v1.0（published=2024-04-10T05:27:16Z latest=True）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 8/0，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 6 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者具备版本化交付意识。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | social-auto-upload | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | LangGraph / AutoGen / CrewAI 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 项目优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 项目风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `pyproject.toml`
- `requirements.txt`
- `README.md`
- `CLAUDE.md`
- `tests/__init__.py`
- `tests/test_bilibili_runtime.py`
- `tests/test_sau_bilibili_cli.py`
- `tests/test_sau_browser_cli.py`
- `tests/test_xiaohongshu_uploader.py`

## 3 条关键发现
- 代码入口/骨架集中在：pyproject.toml, requirements.txt, README.md, CLAUDE.md, tests/__init__.py
- Issue 抽样显示近期关注点包括：zip下载的源码一堆报错 登录报错 上传文件报错 发布平台报错 啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊；如果我要登录tiktok或者youtube，但是密码输入要么就是有风控，要就是提示浏览器不安全，不让登录google账号，这是有什么办法解决么
- 版本交付可从最新 release 观察：baijiahao

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
