# 🔬 larksuite/cli - 全方位深度调研

## 项目全景
- **仓库**：`larksuite/cli`
- **一句话定位**：The official Lark/Feishu CLI tool, maintained by the larksuite team — built for humans and AI Agents. Covers core business domains including Messenger, Docs, Base, Sheets, Calendar, Mail, Tasks, Meetings, and more, with 200+ commands and 20+ AI Agent Skills.
- **基础指标**：Stars=13792 / Forks=941 / 默认分支=`main`
- **Topics**：数据不可用
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：shortcuts(693), internal(380), skills(338), cmd(131), tests(115), extension(52), lint(26), scripts(26), events(22), sidecar(18)
- 关键文件候选：package.json, go.mod, README.md, AGENTS.md, cmd/api/api.go, cmd/api/api_test.go, cmd/auth/auth.go, cmd/auth/auth_test.go, cmd/auth/check.go, cmd/auth/check_test.go, cmd/auth/list.go, cmd/auth/list_test.go

### 设计亮点研判
- 存在 Node/前端工具链入口，说明项目的运行、构建或 CLI 能力围绕 package.json 脚本组织。
- 仓库包含 .github 目录，通常意味着 CI、issue 模板或自动发布流程已被工程化。

## 源码深度解读
### README / 说明文档要点
# lark-cli

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/go-%3E%3D1.23-blue.svg)](https://go.dev/)
[![npm version](https://img.shields.io/npm/v/@larksuite/cli.svg)](https://www.npmjs.com/package/@larksuite/cli)

[中文版](./README.zh.md) | [English](./README.md)

The official [Lark/Feishu](https://www.larksuite.com/) CLI tool, maintained by the [larksuite](https://github.com/larksuite) team — built for humans and AI Agents. Covers core business domains including Messenger, Docs, Base, Sheets, Slides, Calendar, Mail, Tasks, Meetings, Markdown, and more, with 200+ commands and 26 AI Agent [Skills](./skills/).

[Install](#installation--quick-start) · [AI Agent Skills](#agent-skills) · [Auth](#authentication) · [Commands](#three-layer-command-system) · [Advanced](#advanced-usage) · [Security](#security--risk-warnings-read-before-use) · [Contributing](#contributing)

## Why lark-cli?

- **Agent-Native Design** — 24 structured [Skills](./skills/) out of the box, compatible with popular AI tools — Agents can operate Lark with zero extra setup
- **Wide Coverage** — 18 business domains, 200+ curated commands, 26 AI Agent [Skills](./skills/)
- **AI-Friendly & Optimized** — Every command is tested with real Agents, featuring concise parameters, smart defaults, and structured output to maximize Agent call success rates
- **Open Source, Zero Barriers** — MIT license, ready to use, just `npm install`
- **Up and Running in 3 Minutes** — One-click app creation, interactive login, from install to first API call in just 3 steps
- **Secure & Controllable** — Input injection protection, terminal output sanitization, OS-native keychain credential storage
- **Three-Layer Architecture** — Shortcuts (human & AI friendly) → API Commands (platform-synced) → Raw API (full coverage), choose the right granularity

## Features

| Category      | Capabilities                                                                                                                      |
| ------------- |-----------------------------------------------------------------------------------------------------------------------------------|
| 📅 Calendar   | View, create and update events, invite attendees, find meeting rooms, RSVP to invitations, check free/busy & time suggestions     |
| 💬 Messenger  | Send/reply messages, create and manage group chats, view chat history & threads, search messages, dow
...[truncated]

### 关键文件精读
### `package.json`
```
{
  "name": "@larksuite/cli",
  "version": "1.0.50",
  "description": "The official CLI for Lark/Feishu open platform",
  "bin": {
    "lark-cli": "scripts/run.js"
  },
  "scripts": {
    "postinstall": "node scripts/install.js"
  },
  "os": [
    "darwin",
    "linux",
    "win32"
  ],
  "cpu": [
    "x64",
    "arm64"
  ],
  "engines": {
    "node": ">=16"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/larksuite/cli.git"
  },
  "license": "MIT",
  "files": [
    "scripts/install.js",
    "scripts/install-wizard.js",
    "scripts/run.js",
    "checksums.txt",
    "CHANGELOG.md"
  ],
  "dependencies": {
    "@clack/prompts": "^1.2.0"
  }
}
```

### `go.mod`
```
module github.com/larksuite/cli

go 1.23.0

require (
	github.com/Microsoft/go-winio v0.6.2
	github.com/bmatcuk/doublestar/v4 v4.10.0
	github.com/charmbracelet/huh v1.0.0
	github.com/charmbracelet/lipgloss v1.1.0
	github.com/gofrs/flock v0.8.1
	github.com/google/uuid v1.6.0
	github.com/itchyny/gojq v0.12.17
	github.com/larksuite/oapi-sdk-go/v3 v3.5.4
	github.com/sergi/go-diff v1.4.0
	github.com/skip2/go-qrcode v0.0.0-20200617195104-da1b6568686e
	github.com/smartystreets/goconvey v1.8.1
	github.com/spf13/cobra v1.10.2 // flag-error-text contract: see cmd/root.go unknownFlagName
	github.com/spf13/pflag v1.0.9
	github.com/stretchr/testify v1.11.1
	github.com/tidwall/gjson v1.18.0
	github.com/zalando/go-keyring v0.2.8
	golang.org/x/net v0.33.0
	golang.org/x/sync v0.15.0
	golang.org/x/sys v0.33.0
	golang.org/x/term v0.27.0
	golang.org/x/text v0.23.0
	gopkg.in/yaml.v3 v3.0.1
)

require (
	github.com/atotto/clipboard v0.1.4 // indirect
	github.com/aymanbagabas/go-osc52/v2 v2.0.1 // indirect
	
...[truncated]
```

### `README.md`
```
# lark-cli

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/go-%3E%3D1.23-blue.svg)](https://go.dev/)
[![npm version](https://img.shields.io/npm/v/@larksuite/cli.svg)](https://www.npmjs.com/package/@larksuite/cli)

[中文版](./README.zh.md) | [English](./README.md)

The official [Lark/Feishu](https://www.larksuite.com/) CLI tool, maintained by the [larksuite](https://github.com/larksuite) team — built for humans and AI Agents. Covers core business domains including Messenger, Docs, Base, Sheets, Slides, Calendar, Mail, Tasks, Meetings, Markdown, and more, with 200+ commands and 26 AI Agent [Skills](./skills/).

[Install](#installation--quick-start) · [AI Agent Skills](#agent-skills) · [Auth](#authentication) · [Commands](#three-layer-command-system) · [Advanced](#advanced-usage) · [Security](#security--risk-warnings-read-before-use) · [Contributing](#contributing)

## Why lark-cli?

- **
...[truncated]
```

### `AGENTS.md`
```
# AGENTS.md

## Goal (pick one per PR)

- Make CLI better: improve UX, error messages, help text, flags, and output clarity.
- Improve reliability: fix bugs, edge cases, and regressions with tests.
- Improve developer velocity: simplify code paths, reduce complexity, keep behavior explicit.
- Improve quality gates: strengthen tests/lint/checks without adding heavy process.

## Build & Test

```bash
make build          # Build (runs fetch_meta first)
make unit-test      # Required before PR (runs with -race)
make test           # Full: vet + unit + integration
```

## Notification Opt-Outs

`lark-cli` emits two notice types into JSON envelope `_notice` to nudge AI agents toward fixes:

- `_notice.update` — a newer binary is available on npm
- `_notice.skills` — locally installed skills are out of sync with the running binary

To suppress them in non-CI scripts (CI envs are auto-skipped):

| Env var | Effect |
|---------|--------|
| `LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1` | Suppress `_notic
...[truncated]
```

### `cmd/api/api.go`
```
// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package api

import (
	"context"
	"fmt"
	"io"
	"regexp"
	"strings"

	"github.com/larksuite/cli/internal/client"
	"github.com/larksuite/cli/internal/cmdutil"
	"github.com/larksuite/cli/internal/core"
	"github.com/larksuite/cli/internal/output"
	"github.com/larksuite/cli/internal/validate"
	larkcore "github.com/larksuite/oapi-sdk-go/v3/core"
	"github.com/spf13/cobra"
)

// APIOptions holds all inputs for the api command.
type APIOptions struct {
	Factory *cmdutil.Factory
	Cmd     *cobra.Command
	Ctx     context.Context

	// Positional args
	Method string
	Path   string

	// Flags
	Params    string
	Data      string
	As        core.Identity
	Output    string
	PageAll   bool
	PageSize  int
	PageLimit int
	PageDelay int
	Format    string
	JqExpr    string
	DryRun    bool
	File      string
}

var urlPrefixRe = regexp.MustCompile(`https?://[^/]+(/open-apis/.+)`)

func normalisePath(raw string) string {
	if matc
...[truncated]
```

### `cmd/api/api_test.go`
```
// Copyright (c) 2026 Lark Technologies Pte. Ltd.
// SPDX-License-Identifier: MIT

package api

import (
	"errors"
	"os"
	"sort"
	"strings"
	"testing"

	"github.com/larksuite/cli/errs"
	"github.com/larksuite/cli/internal/cmdutil"
	"github.com/larksuite/cli/internal/core"
	"github.com/larksuite/cli/internal/httpmock"
	"github.com/spf13/cobra"
)

func TestApiCmd_FlagParsing(t *testing.T) {
	f, _, _, _ := cmdutil.TestFactory(t, &core.CliConfig{
		AppID: "test-app", AppSecret: "test-secret", Brand: core.BrandFeishu,
	})

	var gotOpts *APIOptions
	cmd := NewCmdApi(f, func(opts *APIOptions) error {
		gotOpts = opts
		return nil
	})
	cmd.SetArgs([]string{"GET", "/open-apis/test", "--as", "bot", "--dry-run"})
	err := cmd.Execute()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if gotOpts.Method != "GET" {
		t.Errorf("expected method GET, got %s", gotOpts.Method)
	}
	if gotOpts.Path != "/open-apis/test" {
		t.Errorf("expected path /open-apis/test, got %s", gotOpts.Path)
	}
	if got
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #1360 [OPEN] Mermaid pie chart legend text truncated in whiteboard rendering（comments=[] labels=domain/doc,domain/whiteboard）
- #1356 [OPEN] Bug: sheets +cells-set rich_text segment styles are not applied（comments=[] labels=bug,domain/sheets）
- #1354 [OPEN] Feature Request: 希望对于表格新增查看历史版本内容的功能（comments=[] labels=enhancement）
- #1333 [OPEN] 服务台token（comments=[] labels=bug）
- #1314 [OPEN] Add +form-public-link command to generate or read form share links（comments=[] labels=无）
- #1309 [OPEN] Feature request: expose Feishu Docs revision suggestions / track changes for AI agents（comments=[] labels=enhancement,domain/doc）

### Pull Requests 抽样
- PR #1367 [OPEN] feat(sidecar): auto-discover app scopes via API, remove offline_access fallback
- PR #1366 [OPEN] fix(im): return partial mget results in messages search instead of all-or-nothing
- PR #1365 [OPEN] test(im): add dry-run E2E tests for message scanning shortcuts
- PR #1364 [OPEN] fix(im): continue contact batch resolution on transient API failures
- PR #1363 [OPEN] feat: add attendance +records shortcut with --detail projection

### Releases 抽样
- v1.0.50（published=2026-06-09T14:48:44Z latest=True）
- v1.0.49（published=2026-06-08T13:44:58Z latest=False）
- v1.0.48（published=2026-06-04T13:15:09Z latest=False）
- v1.0.47（published=2026-06-03T14:31:45Z latest=False）
- v1.0.46（published=2026-06-02T14:09:31Z latest=False）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 8/0，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 0 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者具备版本化交付意识。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | cli | 竞品/替代 |
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
- `package.json`
- `go.mod`
- `README.md`
- `AGENTS.md`
- `cmd/api/api.go`
- `cmd/api/api_test.go`
- `cmd/auth/auth.go`
- `cmd/auth/auth_test.go`
- `cmd/auth/check.go`
- `cmd/auth/check_test.go`
- `cmd/auth/list.go`
- `cmd/auth/list_test.go`

## 3 条关键发现
- 代码入口/骨架集中在：package.json, go.mod, README.md, AGENTS.md, cmd/api/api.go
- Issue 抽样显示近期关注点包括：Mermaid pie chart legend text truncated in whiteboard rendering；Bug: sheets +cells-set rich_text segment styles are not applied
- 版本交付可从最新 release 观察：v1.0.50

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
