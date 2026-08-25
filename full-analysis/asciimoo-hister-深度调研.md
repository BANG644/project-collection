# asciimoo/hister 深度调研

> 调研日期：2026-08-26 ｜ 星标：2,692 ⭐ ｜ 语言：Go ｜ 协议：AGPL-3.0 ｜ 默认分支：master
> 定位：你自己的私人搜索引擎 —— 索引你访问过的网页与你保存的文件全文，可从网页 / 终端 / 通过 MCP 连接的 AI 助手检索

## 一、项目亮点（差异化）

1. **searxng 作者出品， pedigree 过硬**：`asciimoo` 正是知名开源元搜索引擎 searx / searxng 的作者，做「搜索」是老本行。
2. **全文索引（而非仅标题/URL）**：真正索引页面与文件的**实际内容**，所以能搜到「正文里的一句话」，而非只匹配标题。
3. **隐私优先、可自托管**：默认无遥测、无强制云服务；浏览器扩展只把索引内容发往你配置的 Hister 服务器。
4. **多端 + MCP 桥接 AI**：网页界面、终端 TUI、命令行、以及通过 **MCP server** 让 AI 助手直接检索你的个人内容 —— 是天然的个人 AI 记忆层。
5. **生态导入极广**：原生支持 Karakeep、Linkding、Linkwarden、Readeck、Shaarli、Wallabag 等书签/稍后读管理器，外加浏览器历史与爬虫导入。

## 二、核心架构

Go 单二进制后端 + 浏览器扩展 + Web UI（Svelte，见 `webui/`）。`hister.go` 极简，仅把执行交给 `cmd` 包：

```go
package main
import "github.com/asciimoo/hister/cmd"
func main() {
    if err := cmd.Execute(); err != nil { os.Exit(1) }
}
```

`cmd/` 以 Cobra 组织大量子命令，体现能力面：

```
cmd/
├── root.go            # cobra 根
├── browser.go companion.go   # 浏览器扩展 / 伴侣进程
├── crawl.go index.go search.go  # 爬虫 / 索引 / 搜索
├── documents.go import_export.go service_import.go  # 文档与多服务导入
├── karakeep.go linkding.go linkwarden.go readeck.go shaarli.go wallabag.go  # 书签生态导入
├── users.go scope.go prompt.go maintenance.go update.go version.go tui/
```

`server/` 是真正的核心服务层：

```
server/
├── api.go endpoints.go        # HTTP API 与端点
├── indexer/                  # 全文索引引擎
├── extractor/ document/      # 内容抽取与文档模型
├── crawler/                  # 网页爬取
└── errors/
```

`client/` 提供 search / history / document 等客户端逻辑（含 TUI）。

整体数据流：**浏览器扩展/爬虫/导入器 → extractor 抽取正文 → indexer 建全文索引 → server 提供 API → web/tui/cli/mcp 多端检索**；可选语义搜索通过你自建的 embeddings endpoint 实现（文档文本发往你选的端点）。

## 三、应用场景与启发

- **个人知识检索层**：把微信文章、GitHub、论文、本地文件全部索引，用一句自然语言/关键词找回「上周看过的那段话」。
- **AI 助手的私有记忆**：通过 MCP server，让 Claude Code / Cursor 等 Agent 在回答时检索你的私人浏览与文件内容，是「本地优先 AI 记忆」的轻量实现。
- **书签/稍后读统一管理**：把 Karakeep/Linkding 等多处收藏归一为一个可全文搜索的库。
- **对同类需求的启发**：「个人内容搜索」与「公共 web 搜索」是两类问题——Hister 选了前者并补齐 MCP 桥接，证明「给 AI 一个可检索的私人知识库」不一定需要重训练，一个全文索引 + MCP 就够了。

## 四、源码深度解读

**1. 命令面即能力面（`cmd/` 的 Cobra 子命令群）**
`search` / `index` / `crawl` / `import_export` / 六大书签服务导入命令，把「能搜什么、从哪来」直接映射为 CLI 动词，扩展性强（新增一个导入源=加一个子命令）。

**2. 服务分层（`server/` 的 indexer + extractor + crawler 分离）**
抽取（extractor）、索引（indexer）、爬取（crawler）三者解耦，使「索引本地文件」与「爬取网页」可独立演进；`api.go`/`endpoints.go` 统一对外。

**3. MCP 桥接（topics 含 `mcp` / `mcp-server`）**
把个人索引暴露为 MCP server，是让 AI 助手「只读你的私人内容」的关键一环，也是 Hister 区别于传统书签管理器的分水岭。

## 五、社区口碑

- 作者 searxng 背景带来天然信任；demo（demo.hister.org）与文档（hister.org/docs）较完善，上手曲线平缓（下载二进制即可 `listen`）。
- 隐私定位清晰，AGPL-3.0 开源；IRCNet `#hister` + Discord 双社区。
- ⚠️ 仍属 2026-08 新晋项目（2.7K⭐），语义搜索需自备 embeddings endpoint，成熟度与大规模索引性能尚待社区验证。

## 六、竞品对比与核心研判

| 维度 | hister | Karakeep/Hoarder | Readeck | SearXNG | Memex |
|------|--------|------------------|---------|---------|-------|
| 定位 | 个人内容**搜索** | 书签/稍后读 | 文章归档阅读 | 公共 web 搜索 | 浏览器标注搜索 |
| 全文索引 | ✅ | 部分 | ✅ | ✅(web) | ✅ |
| 浏览器历史 | ✅ | ❌ | ❌ | ❌ | ✅ |
| MCP 桥接 AI | ✅ | 部分 | ❌ | ❌ | ❌ |
| 隐私/自托管 | ✅ AGPL | ✅ | ✅ | ✅ | 部分 |

**核心研判**：
- ✅ **找准了缝隙市场**：公共搜索引擎（SearXNG）不算「你的内容」，书签管理器（Karakeep）不算「全文搜索」，Hister 用「私人全文索引 + MCP」卡在两者中间，且由 searxng 作者操刀，质量可期。
- ⚠️ **风险**：项目年轻，语义搜索依赖外部 embeddings；若索引规模/性能跟不上，体验会塌；AGPL 对商用不友好但利于个人。
- 🔭 **最适合**：注重隐私、想把「浏览+文件+书签」统一成可检索私人知识库、并希望 AI 助手能就地检索的个人用户与研究型团队。可作为轻量「本地优先 AI 记忆层」直接复用其 MCP 设计。

## 七、关键文件速查

| 文件 | 作用 |
|------|------|
| `hister.go` | 入口，转交 `cmd.Execute()` |
| `cmd/` | Cobra 子命令（search/index/crawl/import + 6 大书签导入） |
| `server/api.go` `server/endpoints.go` | HTTP API 与端点 |
| `server/indexer/` `server/extractor/` `server/crawler/` | 全文索引 / 内容抽取 / 爬取 |
| `client/` | search/history/document 客户端 + TUI |
| `webui/` | Svelte Web 界面 |
| `compose.yml` `Dockerfile` `flake.nix` | 部署与 Nix 支持 |
