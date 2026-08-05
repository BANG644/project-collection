# firecrawl/anydoc 深度调研

> 一句话：**Firecrawl 出品的 Rust 文档转 Markdown 库——把 Word/PPT/Excel/ODF/RTF/EPUB/CSV/PDF 统一解析进同一个 document model，再用单一序列化器输出一致的 GitHub-Flavored Markdown**，号称单毫秒级、Rust/Node/Python/WASM 四端同构。

🔗 https://github.com/firecrawl/anydoc ｜ 许可 MIT ｜ 语言 Rust（edition 2024，rust-version 1.88）｜ ⭐ 4,343（2026-08-03 创建）｜ 主页 https://firecrawl.github.io/anydoc/

## 一、项目亮点（差异化）

1. **统一模型 + 单序列化器**：每个格式各写 parser，但都汇入同一个 `model`（block/inline/list/link/asset），最后走**唯一** Markdown 渲染器。结果：转义、表格、标题锚点、脚注——无论输入是 2003 的 `.doc` 还是昨天的 `.pptx`，行为完全一致（README 称之为 "one consistent output"）。
2. **内容签名检测，而非扩展名 heuristic**：`Format::from_bytes` 按容器规范指定的身份识别（PDF `%PDF-` 头、RTF `{\rtf` 起手、OLE 流名、ZIP 包 mimetype/OPC content-type），绝不靠猜内容。CSV 无签名，显式要求"命名而非检测"。
3. **四端同构 + Agent Skill 一等公民**：Rust crate / npm `@firecrawl/anydoc` / PyPI `firecrawl-anydoc` / WASM `@firecrawl/anydoc-wasm`，以及 `npx skills add firecrawl/anydoc` 直接给 Claude Code/Codex/Cursor/OpenCode 装成 agent 技能。
4. **浏览器本地跑**：demo 页用 WASM 在本地转换，文件不出机器——隐私友好。
5. **为生产而生**：自带 `fuzz/`（cargo-fuzz，覆盖 csv/doc/docx/epub/odf/pdf/ppt/rtf/xlsx 八类）、`bench/`（mammoth 对比 + LLM-as-judge 评分）、单测用 `insta` 快照。它实际驱动 Firecrawl Parse，扫不出能 OCR 的页才走托管 API。

## 二、核心架构

Cargo workspace：`anydoc` 核心 crate + `node` / `python` / `wasm` 三个 binding members（`fuzz` 被 exclude，独立 nightly 依赖）。

```
src/
├── lib.rs            # 公开 API: to_markdown / to_markdown_bytes / to_document / Format 枚举
├── model/           # 共享文档模型: block.rs inline.rs list.rs link.rs asset.rs
├── formats/         # 每格式一个 parser，全部汇入 model
│   ├── detect.rs    # 内容签名检测（magic byte / OLE / ZIP 包）
│   ├── doc/  docx/  odf/  rtf/  epub/  pdf.rs  ppt/  pptx/  sheet/
├── render/markdown.rs  # 唯一 Markdown 序列化器
├── package/         # OLE(CFB) / ZIP(OPC) 容器解析
└── error.rs  shared.rs
```

**关键依赖**：`calamine`（Excel 多容器）、`cfb`（OLE 二进制 Office）、`pdf-inspector`（PDF→MD，直接产出，故 `to_document` 对 PDF 不支持）、`quick-xml`、`zip`、`csv`、`encoding_rs`、`flate2`。`release` profile 开 `lto="thin"` + `strip="symbols"`。

## 三、源码深度解读

### 1. 公开 API 形态（`src/lib.rs`）
```rust
pub enum Format { Doc, Docx, Odt, Pdf, Ppt, Pptx, Rtf, Epub, Excel, Ods, Odp, Csv }
pub fn to_markdown(path)            // 从路径
pub fn to_markdown_bytes(&bytes, Option<Format>)  // 从字节，格式可省（自动检测）
pub fn to_document(&bytes, ...)     // 停在文档模型（带内嵌 asset）
```
`Format::from_bytes` 自动检测；`from_extension` 按扩展名映射；容器变体（docm/xlsm…）都归并到基础枚举。PDF 特殊：`to_document` 不支持（pdf-inspector 直接出 MD），扫描件（需 OCR）报 unsupported。

### 2. 内容签名检测（`src/formats/detect.rs`）
```rust
pub fn from_bytes(bytes: &[u8]) -> Option<Format> {
    if bytes[..bytes.len().min(1024)].windows(5).any(|w| w == b"%PDF-") { return Some(Pdf); }
    if bytes.starts_with(b"{\\rtf") { return Some(Rtf); }
    if bytes.starts_with(&OLE_MAGIC) { return detect_ole(bytes); }   // 0xD0CF11E0...
    if bytes.starts_with(b"PK\x03\x04") { return detect_zip(bytes); } // OPC/ODF/EPUB
    None
}
```
- OLE：`cfb::CompoundFile` 打开后按规范强制流名判定（`WordDocument`→Doc，`PowerPoint Document`→Ppt，`Workbook`/`Book`→Excel，大小写不敏感）。
- ZIP：先读 OCF `mimetype`（ODF/EPUB），否则走 OPC 的 `officeDocument` 关系所指主部件 content-type（content-type 过期/通用时回退主部件强制根元素）。
- **加密 OOXML（`EncryptedPackage`）返回 None**——内部格式不可知，前端精确报 "Encrypted"。**检测永不报错**，未识别一律 `None`，交给"扩展名→前端错误"兜底。

### 3. 单一渲染路径（`render/markdown.rs`）
所有 parser 产出 `model::*` 结构，`document_to_markdown` 统一渲染。这是"一致输出"的真正支点——新增格式只需写 parser，不用碰渲染。

## 四、应用场景与启发

- **RAG / Agent 文档摄入**：任何需要"把各种 Office 文档变成干净 MD 喂给 LLM"的管道，直接 `npx @firecrawl/anydoc file.docx` 或 agent skill 调用，比临时写 python-docx/openpyxl 脚本稳得多。
- **"统一模型 + 单渲染"的解析器架构**：做多格式导入器（设计稿/笔记/邮件）时，把"格式差异"收敛进 parser 层，模型层和渲染层各只有一份，避免 N 种格式 × M 种输出爆炸。
- **签名检测优于扩展名**：处理用户上传文件时，用 magic byte + 容器规范身份判定，防 `.exe` 改名 `.pdf` 类绕过。
- **多语言 binding 同构**：核心 Rust + napi/pyo3/wasm 三套绑定共享一份逻辑，性能与行为跨语言一致——比各自实现维护成本低。

## 五、社区口碑

- 2026-08-03 创建即破 4.3k⭐，依托 Firecrawl 品牌与"Parse 同款引擎"背书，发布当日即上 GitHub Trending。
- 卖点"单毫秒级 + 一致输出 + 本地 WASM"在 X/开发者圈反响正面；主要期待是"PDF 扫描件 OCR 是否补进开源版"（目前 OCR 仅在托管 API）。
- 成熟度信号强：自带 fuzz（8 类格式）、bench（mammoth 对比 + LLM judge）、insta 快照测试——不是 demo 级。

## 六、竞品对比 + 核心研判

| 维度 | anydoc | mammoth (docx→html) | markitdown (MS) | pandoc |
| --- | --- | --- | --- | --- |
| 输出 | GFM Markdown | HTML（主） | Markdown | 多格式互转 |
| 格式覆盖 | 9 类 Office+PDF | 仅 docx | 广（含 pptx/xlsx/pdf） | 极广 |
| 实现 | Rust，单序列化器 | JS | Python | Haskell |
| 性能 | 单毫秒级（Rust） | 中 | 中 | 中 |
| Agent 友好 | 一等 skill + WASM | 否 | 否 | 否 |
| 一致输出 | ✅ 模型统一 | ⚠️ 每格式各异 | ⚠️ | ⚠️ |

**研判**：
- ✅ 做"文档→LLM-ready MD"的**最佳单点工具**之一：覆盖够用、输出一致、Rust 性能、四端可用、agent 原生。RAG/知识库摄入管线首选。
- ⚠️ PDF 仅支持文本层（pdf-inspector），**扫描件 OCR 在开源版缺失**，重度 PDF 场景仍需托管 API 或另接 OCR。
- ⚠️ 定位是"转换库"非"排版保真编辑器"——往返编辑（改完写回 docx 且样式不崩）不是它的目标，别拿它当文档协作内核。
- 结论：入库为"文档摄入基础设施"标杆；与 `unclecode/crawl4ai`（网页→MD）形成"网页+文档"双轨摄入组合。

## 七、关键文件路径速查

- `src/lib.rs` — 公开 API 与 `Format` 枚举（`from_bytes`/`from_extension`）
- `src/formats/detect.rs` — 内容签名检测（OLE_MAGIC / ZIP/OPC 判定）
- `src/model/` — 共享文档模型（block/inline/list/link/asset）
- `src/render/markdown.rs` — 唯一 Markdown 序列化器 `document_to_markdown`
- `src/formats/{doc,docx,odf,rtf,epub,ppt,pptx,sheet,pdf.rs}` — 各格式 parser
- `node/` `python/` `wasm/` — 三套 binding（napi / pyo3 / wasm-bindgen）
- `fuzz/fuzz_targets/` — 8 类格式 cargo-fuzz 目标
- `bench/` — mammoth 对比 + `judge.py` LLM 评分
- `Cargo.toml` — workspace + `rust-version = "1.88"` + `calamine`/`cfb`/`pdf-inspector` 依赖
