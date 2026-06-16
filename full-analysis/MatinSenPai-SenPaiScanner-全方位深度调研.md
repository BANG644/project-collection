# MatinSenPai-SenPaiScanner - 全方位深度调研

## 项目全景
- **仓库**：`MatinSenPai/SenPaiScanner`
- **一句话定位**：A light-weight scanner for Cloudflare IPs, written in Golang
- **解决的问题**：该项目试图把 README 中描述的能力产品化/脚本化，降低特定任务的搭建或执行门槛。
- **基础指标**：Stars=1405 / Forks=79 / 默认分支=`main`
- **Topics**：数据不可用
- **Homepage**：数据不可用

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：android(46), internal(30), .github(2), mobile(2), .gitignore(1), .goreleaser.yaml(1), CONTRIBUTING.md(1), LICENSE(1), Makefile(1), README.fa.md(1)
- 关键文件候选：go.mod, README.md, CONTRIBUTING.md, cmd/senpaiscanner/main.go

### 设计亮点研判
- 仓库包含 .github 自动化配置，通常代表 CI 或 issue 模板已被纳入工程流程。

## 源码深度解读
### README / 说明文档要点
# SenPai Scanner

> **Persian / فارسی:** [README.fa.md](README.fa.md)

[![CI](https://github.com/matinsenpai/senpaiscanner/actions/workflows/ci.yml/badge.svg)](https://github.com/matinsenpai/senpaiscanner/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/matinsenpai/senpaiscanner?style=flat-square)](https://github.com/matinsenpai/senpaiscanner/releases/latest)
[![Go Version](https://img.shields.io/github/go-mod/go-version/matinsenpai/senpaiscanner?style=flat-square)](go.mod)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Platforms](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows%20%7C%20android%20%7C%20termux-informational?style=flat-square)](#installation)

A Cloudflare IP finder with a terminal UI and an Android app, built for networks where latency is unpredictable and connections drop without warning. Probe Cloudflare edge IPs, optionally validate them through your VLESS or Trojan config with embedded xray — no commands to memorize.

---

## How it works

Run `senpaiscanner` and you land in a short menu. Navigate with arrow keys and Enter — no scan-related CLI flags.

```
┌────────────────────────────────────────────────────────────┐
│  ▶  Find Working IPs   scan Cloudflare IPs — config optional │
│     Retry Last Scan    retry last scan with previous config  │
│     About                                                │
│     Quit                                                 │
└────────────────────────────────────────────────────────────┘
```

**Find Working IPs** can run in one or two phases:

1. **Phase 1 — Connectivity scan** probes candidate Cloudflare IPs. Without a config URL it uses a standard HTTP probe; with a URL it derives SNI, host, WebSocket path, and port from your link. In **Random** mode, healthy hits also trigger a **neighbor scan** — nearby addresses in the same Cloudflare block are explored automatically.
2. **Phase 2 — xray validation** (optional) launches an embedded xray instance and tests the best Phase 1 hits end-to-end through your actual VLESS/Trojan config. Results show endpoint, transport type, download speed, latency (TTFB), 
...[truncated]

### 关键文件精读
### `go.mod`
```
module github.com/matinsenpai/senpaiscanner

go 1.26.1

require (
	github.com/atotto/clipboard v0.1.4
	github.com/charmbracelet/bubbles v1.0.0
	github.com/charmbracelet/bubbletea v1.3.10
	github.com/charmbracelet/lipgloss v1.1.0
	github.com/xtls/xray-core v1.260327.0
	golang.org/x/time v0.15.0
)

require (
	github.com/andybalholm/brotli v1.0.6 // indirect
	github.com/apernet/quic-go v0.59.1-0.20260217092621-db4786c77a22 // indirect
	github.com/aymanbagabas/go-osc52/v2 v2.0.1 // indirect
	github.com/charmbracelet/colorprofile v0.4.1 // indirect
	github.com/charmbracelet/x/ansi v0.11.6 // indirect
	github.com/charmbracelet/x/cellbuf v0.0.15 // indirect
	github.com/charmbracelet/x/term v0.2.2 // indirect
	github.com/clipperhouse/displaywidth v0.9.0 // indirect
	github.com/clipperhouse/stringish v0.1.1 // indirect
	github.com/clipperhouse/uax29/v2 v2.5.0 // indirect
	github.com/cloudflare/ci
...[truncated]
```

### `README.md`
```
# SenPai Scanner

> **Persian / فارسی:** [README.fa.md](README.fa.md)

[![CI](https://github.com/matinsenpai/senpaiscanner/actions/workflows/ci.yml/badge.svg)](https://github.com/matinsenpai/senpaiscanner/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/matinsenpai/senpaiscanner?style=flat-square)](https://github.com/matinsenpai/senpaiscanner/releases/latest)
[![Go Version](https://img.shields.io/github/go-mod/go-version/matinsenpai/senpaiscanner?style=flat-square)](go.mod)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Platforms](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows%20%7C%20android%20%7C%20termux-informational?style=flat-square)](#installation)

A Cloudflare IP finder with a terminal UI and an Android app, built for networks where latency is unpredictable and connections dro
...[truncated]
```

### `CONTRIBUTING.md`
```
# Contributing to SenPai Scanner

Thank you for taking the time to improve SenPai Scanner. This project exists so that people on slow or restricted networks can find Cloudflare IPs that **actually work with their own config** — without reading docs, memorizing flags, or babysitting a terminal.

Every contribution should move us closer to that goal.

---

## What we optimize for

These priorities are ordered on purpose. When they conflict, resolve them from top to bottom.

| Priority | What it means in practice |
|---|---|
| **Simplicity for users** | Fewer menu items, fewer decisions, sensible defaults. If a feature needs a paragraph of explanation, simplify the feature first. |
| **Low complexity** | Prefer one clear code path over pluggable frameworks. Avoid new abstractions until the same logic appears at least twice. |
| **Clean code** | Small functions, honest names, minimal scope. 
...[truncated]
```

### `cmd/senpaiscanner/main.go`
```
package main

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/matinsenpai/senpaiscanner/internal/ui"
	"github.com/matinsenpai/senpaiscanner/pkg/version"
)

func main() {
	// --version flag without launching TUI
	if len(os.Args) > 1 && (os.Args[1] == "--version" || os.Args[1] == "-v" || os.Args[1] == "version") {
		fmt.Println("SenPai Scanner", version.String())
		return
	}

	model := ui.NewApp(version.Version)

	p := tea.NewProgram(
		model,
		tea.WithAltScreen(),
		tea.WithMouseCellMotion(),
	)

	// Give the UI package a reference so background goroutines can send messages.
	ui.SetProgram(p)

	if _, err := p.Run(); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
}
```

### 关键逻辑总结
- 从关键文件组合看，项目更像是**围绕单一目标组织的任务流水线/工具链**，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件则暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #91 [OPEN] مشکل با کانفیگ vless روی پروتکل xhttp（comments=[] labels=无）
- #90 [OPEN] آموزش ذخیره کردن ایپی ها بعداز پایان اسکن در ترموکس اندروید（comments=[] labels=无）
- #89 [OPEN] invalid URL error（comments=[] labels=无）
- #85 [OPEN] شدوساکس (ss)（comments=[] labels=无）
- #83 [OPEN] کار نکردن توییتر（comments=[] labels=无）
- #82 [OPEN] تست دانلود آی پی ها（comments=[] labels=无）

### Pull Requests 抽样
- PR #88 [MERGED] افزودن پشتیبانی از VMess، خروجی‌های Clash و Sing-Box، نمایش مشخصات شبکه و تنظیمات پیشرفته سرعت
- PR #87 [OPEN] feat(mobile): sync validate.go with runner.go changes
- PR #86 [OPEN]  add Shadowsocks (ss://) support
- PR #84 [MERGED] feat(android): Add complete Android application support
- PR #81 [MERGED] Add fallback trace target

### Releases 抽样
- v0.5.0（published=2026-05-30T15:26:13Z latest=True）
- v0.4.0（published=2026-05-30T05:25:54Z latest=False）
- v0.3.0（published=2026-05-29T15:56:00Z latest=False）
- v0.2.0（published=2026-05-29T00:17:18Z latest=False）
- v0.1.0（published=2026-05-28T17:27:07Z latest=False）

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 8/0，可作为维护者响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 4 个，说明项目并非完全冻结。
- 存在 release 记录，说明作者有版本化交付意识。
- 由于本批处理以 GitHub 官方数据为主，若外部搜索结果缺失，应把 GitHub issue/PR 视为最可信的一手社区反馈源。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。

## 竞品对比
| 维度 | SenPaiScanner | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | LangGraph / AutoGen / CrewAI 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 风险
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
- `go.mod`
- `README.md`
- `CONTRIBUTING.md`
- `cmd/senpaiscanner/main.go`

## 3 条关键发现
- 代码入口/骨架集中在：go.mod, README.md, CONTRIBUTING.md, cmd/senpaiscanner/main.go
- 近期开源反馈以 issue 为主，典型议题包括：مشکل با کانفیگ vless روی پروتکل xhttp；آموزش ذخیره کردن ایپی ها بعداز پایان اسکن در ترموکس اندروید
- 发布节奏可从最新 release 观察：v0.5.0

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
