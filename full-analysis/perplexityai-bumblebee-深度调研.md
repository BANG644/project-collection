# perplexityai/bumblebee 深度调研

> 调研日期：2026-09-29 ｜ 数据源：gh API（README / 目录树 / threat_intel 目录）｜ 定位：开发者终端供应链暴露只读扫描器

## 一、项目定位（一句话）

**bumblebee**（Perplexity 出品）是一个用 Go 写的**只读**终端资产清点器：扫描开发者机器上散落的包/扩展/开发工具元数据，把杂乱的本地状态转成结构化 NDJSON 记录，配合暴露目录可秒级标记"哪些机器上出现了已知供应链投毒的包/扩展"。

## 二、项目亮点（差异化）

1. **极简零依赖二进制**：Go 1.25+，零非标准库依赖，单静态二进制，`go install` 即可，便于在大规模终端批量下发。
2. **只读、不执行**：明确**不**跑 `npm ls`/`pip show`/`go list`，**不**读源码文件，只解析锁文件、包管理器元数据、扩展 manifest、MCP 配置——安全响应场景最看重的"不引入新风险"。
3. **三档扫描画像**：`baseline`(全局/user 常见根) / `project`(指定代码目录) / `deep`(显式根，含 `$HOME`)，把扫描频率与覆盖范围解耦，由外部 runner(cron/MDM) 决定节奏。
4. **MCP/agent-skill 也纳入清点**：不仅包，连 `claude_desktop_config.json`、`~/.claude.json`、`~/.gemini/settings.json`、skills-lock 等 AI 工具链配置都解析进 `mcp` / `agent-skill` 生态——直击 2026 年 AI 供应链新攻击面。
5. **内置自检与可溯源**：`bumblebee selftest` 用二进制内嵌假数据做端到端冒烟测试；版本经 `ldflags` 写入，每条记录可回溯到具体构建。

## 三、核心架构

- **命令层 `cmd/bumblebee/`**：`main.go`(入口)、`roots.go`(根解析)、`sink.go`(NDJSON 输出汇)、`selftest.go`(内置夹具)、`version.go`(可溯源版本)。
- **内部包 `internal/`**：
  - `walk` — 文件系统遍历与根解析（baseline/project/deep 不同准入规则）
  - `ecosystem` — 各生态解析器（npm/pnpm/yarn/bun/PyPI/Go/RubyGems/Composer/MCP/agent-skill/editor/browser/Homebrew）
  - `scanner` — 编排扫描、并发读取各类源
  - `model` — 组件记录数据结构（含 `profile`、`root_kind`、`ecosystem`）
  - `exposure` — 暴露目录匹配引擎
  - `normalize` — 版本/名称归一化
  - `osv` / `output` — OSV 对接预留与 NDJSON 输出
- **威胁情报 `threat_intel/`**：一批真实供应链战役 JSON 目录（`glassworm.json`、`mini-shai-hulud*.json`、`antv-mini-shai-hulud.json`、`gemstuffer.json`、`laravel-lang-2026-05-23.json`、`mastra-2026-06-17.json`、`memtensor-2026-09-23.json` 等），作为 `--exposure-catalog` 的输入样例，说明它是为真实事件响应而建。
- **文档 `docs/inventory-sources.md`**：逐生态列出被读取的具体文件路径。

## 四、应用场景与启发

- **场景**：安全团队的供应链事件响应（CVE/投毒通报后，快速回答"哪些开发机装了问题包"）、常态化终端资产清点、AI 工具链(扩展/MCP server)暴露面盘查。
- **启发（对同类需求）**：
  - "只读 + 不执行外部命令 + 不 emit 凭据值"是写**安全响应工具**的黄金准则，bumblebee 把它落到代码层（解析 MCP 配置只为取 server 清单，丢弃 `env` 里的密钥）。任何终端扫描器都应照此设计。
  - 把"AI 工具链(MCP/agent-skill)"当成一等公民生态来清点，是 2026 年才出现的新视角，做 DevSecOps 可参考它的生态清单。
  - `selftest` 内嵌夹具 + 版本溯源，是"给 fleet 下发的二进制要可验证"的最佳实践。

## 五、源码深度解读（核心模块）

**1. 生态解析器 `internal/ecosystem`**
每个包管理器/扩展体系一个解析器，统一产出 `model` 里的组件记录。覆盖到 Bun 的 `bun.lockb` 仅作"存在性诊断"、Yarn Berry 的 `yarn.lock`、Composer 的 `installed.json`——细节颗粒度很高，是实用性的来源。

**2. 暴露匹配 `internal/exposure` + `threat_intel`**
`--exposure-catalog` 接受单文件或目录（非递归合并，要求同 `schema_version`）。匹配逻辑只保留精确命中并支持 `--findings-only` 抑制正常包记录——响应人员已有明确目标时极省噪声。

**3. 根准入 `cmd/bumblebee/roots.go` + `internal/walk`**
`baseline`/`project` 拒绝裸 `$HOME` 根，仅 `deep` 允许走 `$HOME`；`bumblebee roots --profile` 可预演解析出的根而不扫描。这种"按画像分级放宽权限"的设计兼顾安全与灵活。

## 六、社区口碑

- Perplexity 官方出品，Apache-2.0，5k⭐、454 fork，安全/Go 圈认可度高（topics: golang / package-inventory / supply-chain-security）。
- 文档专业度远超一般个人项目：README 讲清"为什么不用 SBOM/EDR 替代"、Scope/ Coverage/ Profiles 分层清晰、`SECURITY.md` 与 `CONTRIBUTING.md` 齐全。
- 更新活跃（pushed 2026-09-23），威胁情报目录随真实战役持续补充。

## 七、竞品对比 + 核心研判

| 维度 | bumblebee | Syft/Grype( SBOM+扫描) | OSV-Scanner | EDR |
|---|---|---|---|---|
| 定位 | 终端本地状态清点 | 镜像/项目 SBOM | 依赖漏洞 | 运行时行为 |
| 只读不执行 | ✅ | 部分 | ✅ | N/A |
| AI 工具链清点 | ✅ MCP/skills | ❌ | ❌ | ❌ |
| 单二进制零依赖 | ✅ | ❌ | ❌ | N/A |

**研判**：bumblebee 不是要取代 SBOM/EDR，而是补上"开发终端散落本地状态"这一被忽略的视图，尤其把 MCP/agent-skill 纳入清点极具前瞻性。作为事件响应的"快问快答"工具价值明确。注意 v0.1 阶段：Codex `config.toml`、Continue YAML 等非 JSON MCP 配置暂未解析，覆盖仍在扩展中；生产部署建议结合自身威胁情报目录持续更新。

## 八、关键文件路径速查

- 仓库根：`https://github.com/perplexityai/bumblebee`
- 命令入口：`cmd/bumblebee/main.go`、`roots.go`、`selftest.go`、`sink.go`
- 核心包：`internal/ecosystem/`、`internal/scanner/`、`internal/walk/`、`internal/exposure/`、`internal/model/`、`internal/normalize/`
- 威胁情报样例：`threat_intel/*.json`（glassworm / mini-shai-hulud / memtensor 等真实战役）
- 覆盖说明：`docs/inventory-sources.md`
- 安装：`go install github.com/perplexityai/bumblebee/cmd/bumblebee@latest`
