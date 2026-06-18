# sybil-solutions-codex-shim - 全方位深度调研

## 项目全景
- **仓库**：`sybil-solutions/codex-shim`
- **一句话定位**：Local Responses-API shim that exposes Factory BYOK models (and optional ChatGPT GPT-5.5 passthrough) to Codex Desktop.
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=868 / Forks=83 / 默认分支=`main`
- **Topics**：数据不可用
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 
- **顶层目录分布（递归树抽样汇总）**：codex_shim(10), tests(8), .github(3), bin(3), .gitignore(1), CHANGELOG.md(1), 
- `CONTRIBUTING.md`(1), LICENSE(1), Launch Codex-Shim.bat(1), 
- `README.md`(1)
- 
- **关键文件候选**：
- `pyproject.toml`, 
- `README.md`, 
- `CONTRIBUTING.md`, 
- `tests/conftest.py,` 
- `tests/test_cursor_passthrough.py,` 
- `tests/test_hostguard.py,` 
- `tests/test_router.py,` 
- `tests/test_router_integration.py,` 
- `tests/test_server.py,` 
- `tests/test_settings_catalog.py,` 
- `tests/test_translate.py`

### 设计亮点研判
- 
- 存在 Python 入口，通常意味着 CLI、服务端或研究型流水线由 Python 主导。
- 
- 项目显式提供测试目录，说明作者至少为关键行为建立了可回归验证。
- 
- 仓库包含 .github 自动化配置，通常代表 CI 或 issue 模板已被纳入工程流程。

## 源码深度解读
### README / 说明文档要点
# codex-shim

Run **Codex Desktop** against any BYOK model you can describe in
`~/.codex-shim/models.json`, plus an optional passthrough to your **ChatGPT
subscription's Codex model** — without rebuilding Codex.

The shim is a local Python/aiohttp server that exposes an OpenAI
Responses-compatible endpoint on loopback. Codex points at the shim; the shim
routes each request to the matching upstream (OpenAI chat completions,
Anthropic Messages, a generic OpenAI-shaped chat endpoint, or ChatGPT Codex
passthrough), then translates streaming responses back into the shape Codex
expects.

> Tested on Codex Desktop **0.133.0-alpha.1** for macOS arm64. The shim server
> and routing layer are plain Python/aiohttp and work on Windows, macOS, Linux,
> WSL, and Git Bash. The only macOS-specific piece is the optional Desktop picker
> ASAR patch, needed when Codex hides custom catalog entries.

---

## What this gives you

Codex Desktop only shows models allowed by its server-side config. If you have
OpenAI / Anthropic / Z.ai / DeepSeek / Gemini / OpenRouter / local proxy models
you want as first-class picker entries, this wires them in locally.

The practical win is that Codex keeps its native UX while model routing moves
local:

- **BYOK models in the normal Codex picker.** No Codex rebuild, no request
  replay workflow.
- **Native Codex agent loops stay intact.** Function calls, tool outputs,
  reasoning blocks, image-capable models, shell-command metadata, and streaming
  SSE are translated instead of flattened into plain text.
- **ChatGPT/Codex passthrough.** If `~/.codex/auth.json` has a valid Codex
  access token, the shim can route Codex's native `/v1/responses` traffic to
  ChatGPT's Codex backend under the `gpt-5.5` slug used by current Codex builds.
- **Cursor/Composer passthrough.** If `cursor-agent login` is active, the shim
  exposes `composer-2-5` and routes through your Cursor subscription — no
  Dashboard API key (`crsr_…`) required. See
  [`docs/subscription-integration.md`](docs/subscription-integration.md).
- **Auto Router (optional).** Add an `Auto (smart routing)` picker entry that
  uses a cheap classifier model to route each task to the cheapest configu
...[truncated]

### 

### 关键文件精读

### `pyproject.toml`
```
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "codex-shim"
version = "0.1.0"
description = "Local all-model BYOK shim for Codex Desktop and CLI."
readme = "
- `README.md`"
requires-python = ">=3.11"
license = { file = "LICENSE" }
authors = [{ name = "0xSero" }]
keywords = ["codex", "byok", "openai", "anthropic", "responses-api", "model-routing"]
classifiers = [
  "Development Status :: 3 - Alpha",
  "Environment :: Console",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
]
dependencies = [
  "aiohttp>=3.9",
]

[project.optional-dependencies]
dev = [
  "pytest>=8",
  "pytest-asyncio>=0.23",
]

[project.urls]
Homepage = "https://github.com/0xSero/codex-shim"
Repository = "https:
...[truncated]
```

### `README.md`
```
# codex-shim

Run **Codex Desktop** against any BYOK model you can describe in
`~/.codex-shim/models.json`, plus an optional passthrough to your **ChatGPT
subscription's Codex model** — without rebuilding Codex.

The shim is a local Python/aiohttp server that exposes an OpenAI
Responses-compatible endpoint on loopback. Codex points at the shim; the shim
routes each request to the matching upstream (OpenAI chat completions,
Anthropic Messages, a generic OpenAI-shaped chat endpoint, or ChatGPT Codex
passthrough), then translates streaming responses back into the shape Codex
expects.

> Tested on Codex Desktop **0.133.0-alpha.1** for macOS arm64. The shim server
> and routing layer are plain Python/aiohttp and work on Windows, macOS, Linux,
> WSL, and Git Bash. The only macOS-specific piece is the optional Desktop picker
> ASAR patch, needed when Codex hides custom catalog entries.

---

##
...[truncated]
```

### `CONTRIBUTING.md`
```
# Contributing to codex-shim

Thanks for hacking on the shim. Issues and PRs welcome.

## Dev loop

```bash
git clone https://github.com/0xSero/codex-shim
cd codex-shim
python3 -m pip install -e ".[dev]"

python3 -m pytest tests/ -q
python3 -m compileall codex_shim/ -q
```

CI runs the same commands on Python 3.11 and 3.12 via
`.github/workflows/ci.yml`. Match it locally before opening a PR.

## What kinds of changes are useful

- Translation fixes for tricky tool-call / reasoning streams, with a
  captured fixture under `tests/` proving the bug and the fix.
- New provider translations (e.g. a new chat-completions or
  Anthropic-shaped upstream). Add a test that exercises the new shape end
  to end through `ShimServer`, the way `test_server.py` does.
- Compatibility notes / safer detection for new Codex Desktop builds,
  especially around the ASAR picker patch needle in
  `codex_shim/cli
...[truncated]
```

### `tests/conftest.py`
```
from __future__ import annotations

import pytest

@pytest.fixture(autouse=True)
def _disable_cursor_passthrough_by_default(monkeypatch, request):
    if "cursor_present" in request.fixturenames:
        return

    def _off(**_kwargs):
        return False

    for target in (
        "codex_shim.cursor_passthrough.cursor_passthrough_available",
        "codex_shim.server.cursor_passthrough_available",
        "codex_shim.catalog.cursor_passthrough_available",
        "codex_shim.cli.cursor_passthrough_available",
    ):
        monkeypatch.setattr(target, _off, raising=False)
```

### `tests/test_cursor_passthrough.py`
```
from __future__ import annotations

import json

from codex_shim.cursor_passthrough import (
    CursorStreamParser,
    build_cursor_prompt,
    is_cursor_passthrough_slug,
    iter_cursor_agent_events,
)

def test_is_cursor_passthrough_slug():
    assert is_cursor_passthrough_slug("composer-2-5")
    assert is_cursor_passthrough_slug("composer-2.5")
    assert not is_cursor_passthrough_slug("gpt-5.5")

def test_build_cursor_prompt_from_responses_body():
    body = {
        "model": "composer-2-5",
        "instructions": "You are Codex.",
        "input": [{"role": "user", "content": "Hello"}],
    }
    prompt = build_cursor_prompt(body)
    assert "You are Codex." in prompt
    assert "Hello" in prompt

def test_cursor_stream_parser_emits_deltas():
    parser = CursorStreamParser()
    line1 = json.dumps(
        {
            "type": "assistant",
            "message": {"role": 
...[truncated]
```

### `tests/test_hostguard.py`
```
from __future__ import annotations

import json

import pytest
from aiohttp.test_utils import TestClient, TestServer

from codex_shim.hostguard import build_allowed_hosts, host_only
from codex_shim.server import ShimServer

@pytest.mark.parametrize(
    "header,expected",
    [
        ("127.0.0.1:8765", "127.0.0.1"),
        ("localhost:8765", "localhost"),
        ("127.0.0.1", "127.0.0.1"),
        ("[::1]:8765", "::1"),
        ("[::1]", "::1"),
        ("attacker.example:8765", "attacker.example"),
        ("attacker.example", "attacker.example"),
        ("", ""),
        ("  127.0.0.1:8765  ", "127.0.0.1"),
    ],
)
def test_host_only_strips_port(header, expected):
    assert host_only(header) == expected

def test_build_allowed_hosts_defaults_to_loopback():
    assert build_allowed_hosts("127.0.0.1") == {"127.0.0.1", "localhost", "::1"}

def test_build_allowed_hosts_adds_bind_
...[truncated]
```

### 

### 关键逻辑总结

- 
- 从关键文件组合看，项目更像是**围绕单一目标组织的任务流水线/工具链**，而不是超重平台。
- 
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### 

### GitHub Issues 抽样

- 
- #28 [OPEN] `patch-app` fails on Codex Desktop ≥26.601.20914 — JS bundle refactor changed needle targets（comments=[] labels=无）
- 
- #10 [CLOSED] codex-shim Desktop install shows shim loaded, but custom models do not appear and chats disappear（comments=[{'id': 'IC_kwDOSkssts8AAAABD5Kz4w', 'author': {'login': 'OnlyTerp'}, 'authorAssociation': 'COLLABORATOR', 'body': "Closed by #13 (merged as 037e1a8). The chats disappearing in shim mode was the Codex Desktop sidebar's listRecentThreads narrowing to only the active provider when modelProviders was null; #13's patch sets it to [] so native openai threads stay visible alongside the codex_shim provider. Recomputing ElectronAsarIntegrity in Info.plist as part of the same patch is also what stops the EXC_BREAKPOINT crash on launch that some users were hitting. If you still see chats missing on a clean install + codex-shim patch-app after pulling main, please reopen with the new app.asar version string.", 'createdAt': '2026-05-27T15:56:08Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/sybil-solutions/codex-shim/issues/10#issuecomment-4556239843', 'viewerDidAuthor': False}, {'id': 'IC_kwDOSkssts8AAAABD7o1dA', 'author': {'login': 'atomtanstudio'}, 'authorAssociation': 'NONE', 'body': 'Thanks for #13. I can see the sidebar/chat visibility fix and the model-picker allowlist patch test. Can you confirm whether this also fixes the case where the shim overlay appears but the picker still only lists GPT-5.5? Or does #13 only address the disappearing chats/sidebar side of #10?', 'createdAt': '2026-05-27T21:30:33Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/sybil-solutions/codex-shim/issues/10#issuecomment-4558828916', 'viewerDidAuthor': False}, {'id': 'IC_kwDOSkssts8AAAABD-uQQA', 'author': {'login': 'tharuxpert'}, 'authorAssociation': 'CONTRIBUTOR', 'body': '@atomtanstudio yes, #13 covers the picker side too, not only the disappearing sidebar/chats side. It keeps the existing model-picker allowlist patch and adds the sidebar `modelProviders: []` patch, plus the `ElectronAsarIntegrity` update after repacking.\n\nIf the shim overlay appears but the picker still only lists GPT-5.5, I would first check the local setup rather than assume #13 missed that case:\n\n```bash\ncodex-shim generate\ncodex-shim list\ncodex-shim patch-app\ncodex-shim app .\n```\n\n`codex-shim list` should show the custom models from `~/.codex-shim/models.json`. Also, `patch-app` has to be rerun against the currently installed `/Applications/Codex.app`; a Codex Desktop update can replace `app.asar` and effectively undo the local picker/sidebar patch.\n\nOn my local current-main setup, custom picker entries are visible after regenerating the catalog and applying `patch-app`, so if it still only shows GPT-5.5 after those steps, please share the Codex app version/build and the relevant `codex-shim list` output.\n', 'createdAt': '2026-05-28T08:21:34Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/sybil-solutions/codex-shim/issues/10#issuecomment-4562063424', 'viewerDidAuthor': False}] labels=无）
- 
- #8 [CLOSED] codex-shim BYOK models silently overridden by Codex Desktop on Windows MSIX install（comments=[{'id': 'IC_kwDOSkssts8AAAABDlqivg', 'author': {'login': 'OnlyTerp'}, 'authorAssociation': 'COLLABORATOR', 'body': 'Fixed locally in `e3755d2`.\n\nWhat changed:\n- Documented the Windows Store/MSIX behavior: Desktop may treat custom local/BYOK slugs as unavailable and rewrite the active model back to `gpt-5.5`; the CLI/TUI/shim route still use the configured slug.\n- Documented that the macOS `patch-app` helper does not apply to Windows MSIX packages under `C:\\\\Program Files\\\\WindowsApps`.\n- Added explicit platform guards so `patch-app` / `restore-app` fail with a clear macOS-only message on Windows/Linux instead of stumbling over macOS paths/tools.\n- Added loopback `NO_PROXY` / `no_proxy` injection for `codex-shim app ...` and `codex-shim codex -- ...` child processes, covering Windows system proxy setups that send `127.0.0.1:8765` through Clash/V2Ray/etc.\n- Added README troubleshooting for the Windows proxy and MSIX model rewrite cases.\n\nValidation:\n- `python3 -m pytest 
- `tests/`` -> 29 passed\n- `python3 -m compileall codex_shim/ -q` -> passed\n\nLeaving open until the local commit is pushed/merged.', 'createdAt': '2026-05-25T16:43:53Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/sybil-solutions/codex-shim/issues/8#issuecomment-4535788222', 'viewerDidAuthor': False}, {'id': 'IC_kwDOSkssts8AAAABDlsMZQ', 'author': {'login': 'OnlyTerp'}, 'authorAssociation': 'COLLABORATOR', 'body': 'Merged to `main` in 496f04aa8dd82db857240b50a3d7b51022e6da74.\n\nSolution shipped:\n- README now documents the Windows Store/MSIX Desktop behavior: Desktop may mark custom local/BYOK slugs unavailable and rewrite active config back to `gpt-5.5`; CLI/TUI/shim routing still uses the configured slug.\n- README now states that the macOS ASAR `patch-app` helper does not apply to MSIX packages under `C:\\\\Program Files\\\\WindowsApps`.\n- `patch-app` and `restore-app` now fail explicitly off macOS with a clear message instead of trying macOS paths/tools.\n- `codex-shim app ...` and `codex-shim codex -- ...` now inject `NO_PROXY` and `no_proxy` entries for `127.0.0.1,localhost,::1`, covering Windows system proxy setups that were sending loopback traffic through Clash/V2Ray/etc.\n- README troubleshooting now includes the Windows proxy and MSIX model rewrite cases.\n\nValidation on the pushed tree:\n- `python3 -m pytest 
- `tests/`` -> 29 passed\n- `python3 -m compileall codex_shim/ -q` -> passed\n\nClosing as fixed/documented.', 'createdAt': '2026-05-25T16:49:15Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/sybil-solutions/codex-shim/issues/8#issuecomment-4535815269', 'viewerDidAuthor': False}] labels=bug）
- 
- #7 [CLOSED] Switching from BYOK/local model to gpt-5.5 fails with invalid_encrypted_content（comments=[{'id': 'IC_kwDOSkssts8AAAABDlqeZQ', 'author': {'login': 'OnlyTerp'}, 'authorAssociation': 'COLLABORATOR', 'body': 'Fixed locally in `e3755d2`.\n\nWhat changed:\n- ChatGPT passthrough now sanitizes request bodies before forwarding to `chatgpt.com/backend-api/codex/responses`.\n- Shim-local reasoning `encrypted_content` values with the `anthropic-thinking-v1:` prefix are stripped/dropped so OpenAI does not reject them as unverifiable when switching back to `gpt-5.5`.\n- Real/OpenAI encrypted content without that prefix is preserved.\n- Added regression tests for dropping shim-local reasoning items and preserving caller input immutability.\n\nValidation:\n- `python3 -m pytest 
- `tests/`` -> 29 passed\n- `python3 -m compileall codex_shim/ -q` -> passed\n\nLeaving open until the local commit is pushed/merged.', 'createdAt': '2026-05-25T16:43:38Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/sybil-solutions/codex-shim/issues/7#issuecomment-4535787109', 'viewerDidAuthor': False}, {'id': 'IC_kwDOSkssts8AAAABDlsGgg', 'author': {'login': 'OnlyTerp'}, 'authorAssociation': 'COLLABORATOR', 'body': 'Merged to `main` in 496f04aa8dd82db857240b50a3d7b51022e6da74.\n\nSolution shipped:\n- ChatGPT passthrough sanitizes request bodies before forwarding back to `gpt-5.5`.\n- Shim-local reasoning blobs with `anthropic-thinking-v1:` encrypted content are removed/dropped so OpenAI no longer rejects the conversation with `invalid_encrypted_content` after switching from a BYOK/local route back to GPT-5.5.\n- OpenAI/native encrypted content without that shim prefix is preserved.\n\nValidation on the pushed tree:\n- `python3 -m pytest 
- `tests/`` -> 29 passed\n- `python3 -m compileall codex_shim/ -q` -> passed\n\nClosing as fixed.', 'createdAt': '2026-05-25T16:48:57Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/sybil-solutions/codex-shim/issues/7#issuecomment-4535813762', 'viewerDidAuthor': False}] labels=bug）
- 
- #5 [CLOSED] issues I faced trying to connect it with ollama（comments=[{'id': 'IC_kwDOSkssts8AAAABDlqiag', 'author': {'login': 'OnlyTerp'}, 'authorAssociation': 'COLLABORATOR', 'body': 'Fixed locally in `e3755d2`.\n\nWhat changed:\n- Documented the Responses-vs-chat-completions trap for Ollama/local endpoints: Codex should stay on `wire_api = \\"responses\\"`, while the shim translates to OpenAI-shaped `/v1/chat/completions` upstreams.\n- Added support for launch-model style settings files via top-level `launchModels` / `launch_models`, including bare string model names.\n- Normalizes `provider: \\"ollama\\"` to `generic-chat-completion-api` and defaults the base URL to `http://127.0.0.1:11434/v1` when omitted.\n- Added a regression test proving repeated `codex-shim enable` / config install does not accumulate duplicate `model_provider`, `model_catalog_json`, or `[model_providers.codex_shim]` blocks.\n- Documented the macOS wrapper symlink gotcha and the expected `gpt-5.4-mini` background-call behavior.\n\nValidation:\n- `python3 -m pytest 
- `tests/`` -> 29 passed\n- `python3 -m compileall codex_shim/ -q` -> passed\n\nLeaving open until the local commit is pushed/merged.', 'createdAt': '2026-05-25T16:43:52Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/sybil-solutions/codex-shim/issues/5#issuecomment-4535788138', 'viewerDidAuthor': False}, {'id': 'IC_kwDOSkssts8AAAABDlsLyA', 'author': {'login': 'OnlyTerp'}, 'authorAssociation': 'COLLABORATOR', 'body': 'Merged to `main` in 496f04aa8dd82db857240b50a3d7b51022e6da74.\n\nSolution shipped:\n- README now documents the Ollama trap clearly: Codex must stay on `wire_api = \\"responses\\"`, while codex-shim bridges Responses to OpenAI-shaped `/v1/chat/completions` upstreams such as Ollama.\n- Settings loader now accepts launch-model style files with top-level `launchModels` / `launch_models`, including bare string model names.\n- `provider: \\"ollama\\"` is normalized to `generic-chat-completion-api`, defaulting to `http://127.0.0.1:11434/v1` when no base URL is supplied.\n- Added regression coverage that repeated config install does not accumulate duplicate `model_provider`, `model_catalog_json`, or `[model_providers.codex_shim]` entries.\n- README now calls out the macOS symlink gotcha and expected `gpt-5.4-mini` background calls.\n\nValidation on the pushed tree:\n- `python3 -m pytest 
- `tests/`` -> 29 passed\n- `python3 -m compileall codex_shim/ -q` -> passed\n\nClosing as fixed.', 'createdAt': '2026-05-25T16:49:13Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/sybil-solutions/codex-shim/issues/5#issuecomment-4535815112', 'viewerDidAuthor': False}] labels=无）

### 

### Pull Requests 抽样

- PR 
- #35 [OPEN] Add CSRF protection for picker model switching
- PR 
- #34 [OPEN] Add subscription passthrough integration docs
- PR 
- #33 [OPEN] Add doctor diagnostics command
- PR 
- #32 [OPEN] fix(translate): normalize image detail "original" to "high" for chat-completions
- PR 
- #31 [MERGED] fix(router): image-aware fallback_slug to never route image tasks to text-only models

### 

### Releases 抽样

暂无 release 或数据不可用

### 

### 真实反馈与维护信号研判

- 抽样 issue 中 open/closed 约为 1/4，可作为维护者响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 2 个，说明项目并非完全冻结。
- 由于本批处理以 GitHub 官方数据为主，若外部搜索结果缺失，应把 GitHub issue/PR 视为最可信的一手社区反馈源。
- 
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## 竞品对比
| 维度 | codex-shim | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | LangGraph / AutoGen / CrewAI 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 

### 风险

 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 

### 优势

- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 

### 风险

- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 

### 适用场景

- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不

### 适用场景

- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `pyproject.toml`
- `README.md`
- `CONTRIBUTING.md`
- `tests/conftest.py`
- `tests/test_cursor_passthrough.py`
- `tests/test_hostguard.py`
- `tests/test_router.py`
- `tests/test_router_integration.py`
- `tests/test_server.py`
- `tests/test_settings_catalog.py`
- `tests/test_translate.py`

## 3 条关键发现
- 代码入口/骨架集中在：
- `pyproject.toml`, 
- `README.md`, 
- `CONTRIBUTING.md`, 
- `tests/conftest.py,` 
- `tests/test_cursor_passthrough.py`
- 近期开源反馈以 issue 为主，典型议题包括：`patch-app` fails on Codex Desktop ≥26.601.20914 — JS bundle refactor changed needle targets；codex-shim Desktop install shows shim loaded, but custom models do not appear and chats disappear

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：
- 若外部搜索数据不可用，则明确标注并不伪造口碑结论
