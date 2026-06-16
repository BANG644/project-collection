# 🔬 OthmanAdi/planning-with-files - 全方位深度调研

## 项目全景
- **仓库**：`OthmanAdi/planning-with-files`
- **一句话定位**：Claude Code skill implementing Manus-style persistent markdown planning — the workflow pattern behind the $2B acquisition.
- **基础指标**：Stars=22959 / Forks=2029 / 默认分支=`master`
- **Topics**：claude, claude-code, claude-skills, manus, agent-skills, antigravity, kilocode, adal, hermes, hermes-agent, hermes-skill, openclaw, openclaw-skills, planning, copilot, copilot-skills, mastra, pi, pi-agent
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：skills(62), .codex(29), docs(27), .pi(25), .gemini(23), .hermes(23), tests(22), .codebuddy(17), .factory(17), .cursor(16)
- 关键文件候选：README.md, AGENTS.md, CONTRIBUTING.md, tests/test_canonical_script_sync.py, tests/test_check_complete_resolver.py, tests/test_codex_hooks.py, tests/test_codex_session_isolation.py, tests/test_hermes_adapter.py, tests/test_hook_body_v240.py, tests/test_hook_resolver_integration.py, tests/test_init_session_slug.py, tests/test_path_fix.py

### 设计亮点研判
- 仓库包含测试代码，说明作者至少为关键行为建立了回归验证。
- 仓库包含 .github 目录，通常意味着 CI、issue 模板或自动发布流程已被工程化。

## 源码深度解读
### README / 说明文档要点
<div align="center">
<img src="media/banner.png" alt="planning-with-files" width="100%">
</div>

# Planning with Files

> **Work like Manus** — the AI agent company Meta acquired for **$2 billion**.

[![Benchmark](https://img.shields.io/badge/Benchmark-96.7%25_pass_rate-brightgreen)](docs/evals.md)
[![A/B Verified](https://img.shields.io/badge/A%2FB_Blind-3%2F3_wins-brightgreen)](docs/evals.md)
[![SkillCheck Validated](https://img.shields.io/badge/SkillCheck-Validated-4c1)](https://getskillcheck.com)
[![Security Verified](https://img.shields.io/badge/Security-Audited_%26_Fixed_v2.21.0-blue)](docs/evals.md)

[![Skills Playground](https://skillsplayground.com/badges/installs/othmanadi-planning-with-files-planning-with-files.svg)](https://skillsplayground.com/skills/othmanadi-planning-with-files-planning-with-files/)
[![Downloads](https://skill-history.com/badge/othmanadi/planning-with-files.svg)](https://skill-history.com/othmanadi/planning-with-files)
[![Version](https://img.shields.io/badge/version-2.43.0-brightgreen)](https://github.com/OthmanAdi/planning-with-files/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Closed Issues](https://img.shields.io/github/issues-closed/OthmanAdi/planning-with-files?color=success)](https://github.com/OthmanAdi/planning-with-files/issues?q=is%3Aissue+is%3Aclosed)
[![Closed PRs](https://img.shields.io/github/issues-pr-closed/OthmanAdi/planning-with-files?color=success)](https://github.com/OthmanAdi/planning-with-files/pulls?q=is%3Apr+is%3Aclosed)

<details>
<summary><strong>💬 A Note from the Author</strong></summary>

To everyone who starred, forked, and shared this skill — thank you. This project blew up in less than 24 hours, and the support from the community has been incredible.

If this skill helps you work smarter, that's all I wanted.

</details>

<details>
<summary><strong>🌍 What the community shipped</strong></summary>

### Forks & Extensions

| Fork | Author | What They Built |
|------|--------|-----------------|
| [devis](https://github.com/st01cs/devis) | [@st01cs](https://github.com/st01cs) | Interview-first workflow, `/devis:intv` and `/devis:impl` commands, guaranteed activation |
| [multi-manus-planning](https://github.com/kmichels/multi-manus-planning) | [@kmichels](https://github.com/kmichels) | Multi-project support, SessionStart git sync |
| [plan-cascade](https://github.com/Taoidle/plan-cascade) | [@Taoidle](https://github.com/Tao
...[truncated]

### 关键文件精读
### `README.md`
```
<div align="center">
<img src="media/banner.png" alt="planning-with-files" width="100%">
</div>

# Planning with Files

> **Work like Manus** — the AI agent company Meta acquired for **$2 billion**.

[![Benchmark](https://img.shields.io/badge/Benchmark-96.7%25_pass_rate-brightgreen)](docs/evals.md)
[![A/B Verified](https://img.shields.io/badge/A%2FB_Blind-3%2F3_wins-brightgreen)](docs/evals.md)
[![SkillCheck Validated](https://img.shields.io/badge/SkillCheck-Validated-4c1)](https://getskillcheck.com)
[![Security Verified](https://img.shields.io/badge/Security-Audited_%26_Fixed_v2.21.0-blue)](docs/evals.md)

[![Skills Playground](https://skillsplayground.com/badges/installs/othmanadi-planning-with-files-planning-with-files.svg)](https://skillsplayground.com/skills/othmanadi-planning-with-files-planning-with-files/)
[![Downloads](https://skill-history.com/badge/othmanadi/planning-with-files.svg)](https://skill-history.com/othmanadi/planning-with-files)
[![Version](https://img.shields.io/
...[truncated]
```

### `AGENTS.md`
```
# AGENTS.md — planning-with-files agent reference card

This file is the canonical, session-portable reference for how every agent working in this repo must handle commits, releases, version bumps, CHANGELOG entries, and issue/PR communication.

---

## Commit rules

- **Author**: OthmanAdi only. NEVER add `Co-Authored-By:` trailers.
- **Format**: Conventional Commits — `fix:`, `feat:`, `release:`, `docs:` prefixes.
- **One squashed commit per release or PR merge.**
- No `--no-verify`. No force push to master except tag ref updates.
- Contributors are credited in CHANGELOG `### Thanks` and `CONTRIBUTORS.md`, never in commit trailers.

---

## Release checklist (12 steps)

1. `gh issue view N` and `gh pr view N` — read both in full.
2. Verify the bug is real: find the exact file/line, grep for the pattern, confirm reporter is correct.
3. `python -m pytest tests/ -q` — all tests pass before touching anything.
4. Squash merge: `git fetch origin branch && git merge --squash origin/branch`,
...[truncated]
```

### `CONTRIBUTING.md`
```
# Contributing

Thank you for considering a contribution to planning-with-files.

This project keeps contribution work small, traceable, and reviewable. Please make one logical change per pull request and keep the tone concise and concrete.

## How to set up locally

Fork the repository, then clone your fork:

```bash
git clone https://github.com/YOUR-USERNAME/planning-with-files.git
cd planning-with-files
```

Add the upstream repository so you can sync your fork with the original project:

```bash
git remote add upstream https://github.com/OthmanAdi/planning-with-files.git
git fetch upstream
```

The canonical skill lives here:

```text
skills/planning-with-files/SKILL.md
```

Before opening a pull request, run the test suite:

```bash
python -m pytest tests/ -q
```

Two pre-existing Windows exec-bit test failures may appear on Windows. If those are the only failures, note that in your pull request description.

## Project layout

The canonical skill source is:

```text
skills/planni
...[truncated]
```

### `tests/test_canonical_script_sync.py`
```
"""Regression test: keep top-level scripts/ in sync with canonical skills/.../scripts/.

Background — the repo ships two parallel copies of the helper scripts:

  * `scripts/...`                              — top-level (used by tests, CI, dev)
  * `skills/planning-with-files/scripts/...`   — canonical for the shipped skill;
                                                 sync-ide-folders.py copies this one
                                                 into all `.<ide>/skills/.../scripts/`.

Past PRs (analytics template in v2.29.0, slug-mode in v2.36.0) edited only the
top-level copy and forgot the canonical, so users installing the skill via any IDE
folder ended up with the previous-version script. This test catches that class of
drift up front.

It also exercises sync-ide-folders.py --verify so the IDE-folder mirrors stay
honest after every commit.
"""
from __future__ import annotations

import filecmp
import subprocess
import sys
import unittest
from pathlib import Path


REPO_R
...[truncated]
```

### `tests/test_check_complete_resolver.py`
```
"""Tests for scripts/check-complete.sh resolver integration (v2.40).

Before v2.40, check-complete.sh defaulted to `./task_plan.md` when invoked
without arguments. Any caller running in pure-slug-mode (no root plan, only
`.planning/<slug>/task_plan.md` + `.active_plan`) would receive the
"No task_plan.md found" message even though an active plan existed.

The Stop hook in SKILL.md frontmatter passes the resolved plan path
explicitly, so this was silent: only user-driven invocations or third-party
tooling that called check-complete with no args hit the bug.

v2.40 wires check-complete.sh into resolve-plan-dir.sh when no explicit path is
passed, restoring slug-mode parity.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_COMPLETE = REPO_ROOT / "scripts" / "check-complete.sh"


PLAN_WITH_FIVE_PHASES = """# Task Plan: Smoke

## Phases

### Phase 1
- **Status:*
...[truncated]
```

### `tests/test_codex_hooks.py`
```
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CODEX_ROOT = REPO_ROOT / ".codex"
HOOKS_JSON = CODEX_ROOT / "hooks.json"
HOOKS_DIR = CODEX_ROOT / "hooks"


class CodexHooksTests(unittest.TestCase):
    def run_python_hook(self, script_name: str, payload: dict, cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HOOKS_DIR / script_name)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=str(cwd),
            check=False,
        )

    def run_shell_hook(self, script_name: str, cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["sh", str(HOOKS_DIR / script_name)],
            text=True,
            capture_output=True,
            cwd=str(cwd),
            env=env,
            c
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #179 [OPEN] ive built the strongest CEO agent..（comments=[] labels=无）
- #178 [OPEN] Codex Stop hook blocks normal stopping and causes the agent to continue unfinished plans automatically（comments=[{'id': 'IC_kwDOQy5Vl88AAAABEIgOjQ', 'author': {'login': 'instinct6819-oss'}, 'authorAssociation': 'NONE', 'body': 'Is this for me?', 'createdAt': '2026-05-29T07:58:53Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/OthmanAdi/planning-with-files/issues/178#issuecomment-4572319373', 'viewerDidAuthor': False}, {'id': 'IC_kwDOQy5Vl88AAAABELB1NA', 'author': {'login': 'instinct6819-oss'}, 'authorAssociation': 'NONE', 'body': 'Helppp', 'createdAt': '2026-05-29T12:26:24Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/OthmanAdi/planning-with-files/issues/178#issuecomment-4574967092', 'viewerDidAuthor': False}, {'id': 'IC_kwDOQy5Vl88AAAABEMPQEQ', 'author': {'login': 'instinct6819-oss'}, 'authorAssociation': 'NONE', 'body': '![20260529_222126.jpg](https://github.com/user-attachments/assets/2a92b9ed-a18c-49cb-9045-bdd8a641088a)\n\n![20260529_222023.jpg](https://github.com/user-attachments/assets/d8c160ba-65a4-489b-b7a6-7c1ee280b3cf)\n\n![20260529_222151.jpg](https://github.com/user-attachments/assets/07f6a19b-3a0d-4c4f-a295-a9c83fec2d9a)\n\n![20260529_222212.jpg](https://github.com/user-attachments/assets/f75c4dbe-494d-4c98-a93c-9a1ff7e1a441)\nub.com/user-attachments/assets/c591c308-f17c-4ff1-aaae-417da828d966\n\n\nIve done it check jpgs\n', 'createdAt': '2026-05-29T14:24:39Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/OthmanAdi/planning-with-files/issues/178#issuecomment-4576235537', 'viewerDidAuthor': False}, {'id': 'IC_kwDOQy5Vl88AAAABEMPqFA', 'author': {'login': 'instinct6819-oss'}, 'authorAssociation': 'NONE', 'body': 'Partner ship?', 'createdAt': '2026-05-29T14:25:12Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/OthmanAdi/planning-with-files/issues/178#issuecomment-4576242196', 'viewerDidAuthor': False}] labels=无）
- #177 [CLOSED] npx skills add xxx not supported opencode?（comments=[{'id': 'IC_kwDOQy5Vl88AAAABEIoXhg', 'author': {'login': 'instinct6819-oss'}, 'authorAssociation': 'NONE', 'body': 'Whos this for me???', 'createdAt': '2026-05-29T08:11:55Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/OthmanAdi/planning-with-files/issues/177#issuecomment-4572452742', 'viewerDidAuthor': False}] labels=无）
- #176 [OPEN] Partnership inquiry from MyClaw.ai（comments=[{'id': 'IC_kwDOQy5Vl88AAAABEIkrGA', 'author': {'login': 'instinct6819-oss'}, 'authorAssociation': 'NONE', 'body': 'Yes bro contact me on instinctsecurity@gmail.com \nJC.instinct@protonmail.com', 'createdAt': '2026-05-29T08:05:51Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/OthmanAdi/planning-with-files/issues/176#issuecomment-4572392216', 'viewerDidAuthor': False}, {'id': 'IC_kwDOQy5Vl88AAAABELDMBA', 'author': {'login': 'instinct6819-oss'}, 'authorAssociation': 'NONE', 'body': 'New project ceo file i have is elite tech ', 'createdAt': '2026-05-29T12:29:30Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/OthmanAdi/planning-with-files/issues/176#issuecomment-4574989316', 'viewerDidAuthor': False}] labels=无）
- #173 [OPEN] クラウド（comments=[] labels=无）
- #172 [CLOSED] opencode setup error（comments=[{'id': 'IC_kwDOQy5Vl88AAAABDr26FA', 'author': {'login': 'OthmanAdi'}, 'authorAssociation': 'OWNER', 'body': '@luyanfeng the path in \\docs/opencode.md\\ lines 40, 101, 106 was doubled: it read \\planning-with-files/planning-with-files/SKILL.md\\. This happened because the manual-install instructions assumed a \\git clone\\ of the whole repo into \\~/.config/opencode/skills/\\ and then referenced the SKILL.md at \\planning-with-files/planning-with-files/SKILL.md\\ inside that clone — but the clone lands one level deeper than the \\cat\\ and \\ls\\ commands expected.\n\nRoot cause: the Quick Install section should have used \\\npx skills add\\ like every other IDE doc, which produces the correct single-level path. The manual-install and verification paths now reflect that.\n\nFix ships in v2.43.0.', 'createdAt': '2026-05-26T08:43:15Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/OthmanAdi/planning-with-files/issues/172#issuecomment-4542282260', 'viewerDidAuthor': False}, {'id': 'IC_kwDOQy5Vl88AAAABDr6hFQ', 'author': {'login': 'OthmanAdi'}, 'authorAssociation': 'OWNER', 'body': '@luyanfeng fix confirmed in v2.43.0. The Quick Install block in \\docs/opencode.md\\ now uses \\\npx skills add\\ (matching every other IDE doc). The manual-install and verification paths no longer carry the doubled \\planning-with-files/planning-with-files/\\ folder segment. You are credited in CONTRIBUTORS.md and in the v2.43.0 release notes.', 'createdAt': '2026-05-26T08:48:17Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/OthmanAdi/planning-with-files/issues/172#issuecomment-4542341397', 'viewerDidAuthor': False}] labels=无）

### Pull Requests 抽样
- PR #181 [OPEN] fix: add Codex PreCompact hook
- PR #180 [OPEN] fix: make Codex stop hook non-blocking for incomplete plans
- PR #175 [OPEN] test: add Pi extension integration tests
- PR #174 [OPEN] docs: document SHA cache transient directory and keying
- PR #171 [MERGED] docs: add contributing guide

### Releases 抽样
- v2.43.0（published=2026-05-26T08:48:08Z latest=True）
- v2.42.0（published=2026-05-25T09:51:39Z latest=False）
- v2.41.0（published=2026-05-24T11:56:57Z latest=False）
- v2.40.1（published=2026-05-22T15:17:38Z latest=False）
- v2.40.0（published=2026-05-21T21:08:28Z latest=False）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 4/4，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 2 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者具备版本化交付意识。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | planning-with-files | 竞品/替代 |
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
- `README.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `tests/test_canonical_script_sync.py`
- `tests/test_check_complete_resolver.py`
- `tests/test_codex_hooks.py`
- `tests/test_codex_session_isolation.py`
- `tests/test_hermes_adapter.py`
- `tests/test_hook_body_v240.py`
- `tests/test_hook_resolver_integration.py`
- `tests/test_init_session_slug.py`
- `tests/test_path_fix.py`

## 3 条关键发现
- 代码入口/骨架集中在：README.md, AGENTS.md, CONTRIBUTING.md, tests/test_canonical_script_sync.py, tests/test_check_complete_resolver.py
- Issue 抽样显示近期关注点包括：ive built the strongest CEO agent..；Codex Stop hook blocks normal stopping and causes the agent to continue unfinished plans automatically
- 版本交付可从最新 release 观察：v2.43.0

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
