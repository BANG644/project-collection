# 🔬 Automattic/harper — 本地优先、隐私安全的 Rust 英语语法检查器

> **调研日期**：2026-07-26 | **数据来源**：GitHub API + README + Cargo.toml + 源码树走读
> **实时数据**：⭐ 12,923（Trending +877/日）| 协议 Apache-2.0 | 语言 Rust | 官网 writewithharper.com

## 一、项目定位（一句话）

一款 **完全本地运行、隐私优先的英语语法/拼写检查器**，用 Rust 实现，毫秒级 lint、内存占用不到 LanguageTool 的 1/50，还能编译进 WebAssembly 直接在浏览器跑。

## 二、项目亮点（3-5 条差异化，开篇呈现）

- ⚡ **极致性能**：lint 文档只需毫秒级，内存 < LanguageTool 1/50，长文档 lint 慢即视为 bug。
- 🔒 **隐私优先**：全部本地运行，文本不出本机——直击 Grammarly（上云）与 LanguageTool（16GB n-gram 数据集）的痛点。
- 🕸️ **WASM 可嵌入**：核心可编译为 WebAssembly，直接在前端/浏览器内做实时检查（writewithharper.com 即证）。
- 🧱 **20 crate 高度模块化 workspace**：核心引擎与各类文件解析器（tex/py/html/comments/git-commit…）彻底解耦，易扩展。
- 🏢 **Automattic 背书**：已归入 WordPress.com 母公司 Automattic 旗下，维护与生态确定性高。

## 三、核心架构

Cargo workspace，成员 crate 覆盖「核心引擎 + 各类接入/解析器」：

```
harper/  (workspace)
├── harper-core        # 语法检查引擎（规则 + 词法 + lint）
├── harper-ls          # Language Server Protocol 适配（编辑器集成）
├── harper-cli         # 命令行入口
├── harper-wasm        # WebAssembly 构建（浏览器/Web）
├── harper-tree-sitter # 基于 tree-sitter 的解析
├── harper-html / -comments / -python / -tex / -typst / -asciidoc
├── harper-ink / -jjdescription / -git-commit / -literate-haskell
├── harper-stats / -pos-utils / -brill / -thesaurus
└── harper-desktop/src-tauri  # 桌面端（Tauri）
```

## 四、应用场景与启发

- **隐私写作助手底座**：要把 grammar check 嵌入本地笔记/编辑器/IM，Harper 是可自托管的最佳开源选择。
- **WASM 端侧 NLP 范式**：证明「规则引擎 + WASM」能在浏览器内做实时语言处理，无需云端大模型。
- **可扩展架构样板**：`harper-core` 只管引擎，文件类型（tex/py/comment…）各自成 crate，新增格式只需加一个解析 crate——插件化思路清晰。

## 五、源码解读（核心模块精读）

`harper-core/src/lib.rs` 揭示它是 **手写规则引擎，而非统计/ML 模型**——这是与 LanguageTool 的根本差异：

```rust
// harper-core/src/lib.rs（模块声明节选）
pub mod expr;          // 可组合语法模式 DSL
mod linting;           // Lint 结构 + 规则注册
mod document;          // Document：被检查文本的单位
pub mod parsers;       // 文本 → token 流
pub mod patterns;      // 高层规则组合
pub mod spell;         // 拼写
pub mod weir;          // WASM/嵌入相关
```

`expr/` 是整个引擎的「秘密武器」：用一组可组合的组合子描述语法结构——`anchor_start` / `anchor_end` / `fixed_phrase` / `pronoun_be` / `reflexive_pronoun` / `sequence_expr` / `step` 等。即把「这里该用反身代词」「这里缺冠词」等语法知识，建模成 **在 token 流上匹配的小型模式**，而非训练语言模型。这正是它快且省内存的原因。

## 六、全网口碑

- 星标 12.9K+，Trending 日增 ~877，增长迅猛；编辑器生态（VS Code / Neovim / Helix / Emacs / Zed / Obsidian 插件）快速铺开。
- 用户盛赞「快、私、准」，对 Grammarly 隐私问题的替代诉求强烈。
- 已知限制：**目前仅支持英语**，其他语言靠社区贡献 core 的扩展性来补齐。

## 七、竞品对比 + 核心研判

| 维度 | harper | LanguageTool | Grammarly | Vale / write-good |
|------|--------|--------------|-----------|-------------------|
| 运行 | 本地/Rust/WASM | 本地/Java(重) | 云端 | 本地(lint) |
| 隐私 | ✅ 全本地 | 中 | ❌ 上云 | ✅ |
| 性能 | 毫秒/省内存 | 秒级/GB 内存 | 依赖网络 | 快 |
| 语言 | 仅英语 | 多 | 多 | 样式/职业写作 |

**核心研判**：
- ✅ **优势**：性能与隐私双杀，WASM 可嵌入任意前端，模块化架构易扩展，且有 Automattic 背书。
- ⚠️ **风险**：仅英语；规则引擎靠人写，长尾语法/风格覆盖度不及训练模型；生态成熟度仍上升期。
- 🎯 **启发**：做「本地优先 + 端侧 NLP」产品时，Harper 证明「规则/模式 DSL + WASM」是绕开云端大模型、保隐私保性能的可靠路线；其 `expr` 组合子设计值得借鉴。

## 八、关键文件速查

- `Cargo.toml` — workspace 成员（20 crate）一览
- `harper-core/src/lib.rs` — 引擎模块声明与公开 API
- `harper-core/src/expr/` — 语法模式 DSL（anchor/fixed_phrase/pronoun_be…）
- `harper-ls/` — LSP 适配（编辑器集成入口）
- `harper-wasm/` — WebAssembly 构建
- GitHub：`https://github.com/Automattic/harper`
