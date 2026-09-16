# 🔬 pot-app/pot-desktop - 全方位深度调研

> 调研日期：2026-09-17 ｜ 来源：GitHub 仓库 `pot-app/pot-desktop` 真实 README / 目录树抓取（stars 19,433，forks 1,004，pushed 2026-07-04，GPL-3.0，JS+Rust/Tauri）

## 一、项目定位（一句话）

**Pot（派了个萌的翻译器）** 是一款跨平台「划词翻译 + OCR + TTS」桌面软件：用 Tauri 把 20+ 翻译引擎、10+ OCR 引擎、多路语音合成统一进一个轻量本地客户端，并通过本地 HTTP 控制面与划词工具（SnipDo / PopClip / Starry）组合，是 macOS 上 Bob 的跨平台开源替代品。

## 二、项目亮点（差异化）

1. **全本地优先的轻量架构**：后端 Rust（Tauri）、前端 WebView，而非 Electron。安装包小、常驻内存低，三端（Windows / macOS / Linux）均以原生托盘运行，且官方提供了 Wayland（KDE/GNOME/Hyprland）适配说明。
2. **能力矩阵化 + 并行翻译**：翻译 / 文字识别 / 语音合成 / 生词本四类能力各自抽象成 `src/services` 下的独立子模块，单类可挂 20+ 内置引擎，并支持「多接口并行翻译」取最优结果。
3. **本地 HTTP 控制面（核心设计）**：在 `127.0.0.1:port`（默认 `60828`）暴露一套 REST 式接口，任意外部软件都能驱动 Pot 做划词 / 截图 OCR / 截图翻译——这是它能无缝嵌入划词生态的根本。
4. **开放插件系统（`.potext`）**：内置引擎有限，但官方提供 translate/recognize/tts/collection 四类插件模板，社区可扩展新服务而无需改主程序。
5. **离线能力完整**：系统 OCR（Windows.Media.OCR / Apple Vision / Tesseract）+ Tesseract.js / Rapid / Paddle 离线插件，断网也能完成识别与翻译。

## 三、核心架构

采用经典 Tauri 双层结构，前端负责 UI 与编排，后端 Rust 负责系统能力与本地服务：

- **前端（React + Vite）**：`src/App.jsx` 入口，`src/services/{translate,recognize,tts,collection}` 是四类引擎的抽象层，`src/components/WindowControl` 处理无边框窗口，`jotai` 管状态、`react-router-dom` 管路由、`i18next` 管多语言、`react-markdown` 渲染译文。
- **后端（Rust，`src-tauri/src/`）**：以 Tauri Command 暴露能力，关键模块：
  - `server.rs` —— 本地 HTTP 控制面（对应下方接口契约）
  - `cmd.rs` —— 暴露给前端的 Tauri 命令聚合
  - `hotkey.rs` / `screenshot.rs` / `clipboard.rs` —— 全局快捷键、截图、剪贴板监听
  - `system_ocr.rs` —— 调用各平台系统级 OCR
  - `lang_detect.rs` —— 源语言识别
  - `tray.rs` / `window.rs` / `config.rs` / `backup.rs` / `updater.rs` —— 托盘、窗口、配置、备份、自更新
- **配置**：`src-tauri/tauri.conf.json` 及分平台 `tauri.windows/macos/linux.conf.json`，`webview.*.json` 内嵌 WebView2 runtime 信息。

> 关键洞察：Pot 把「翻译器」做成了一个**本地微服务**——UI 只是它的一个客户端，真正的能力都通过 `server.rs` 的 HTTP 接口对外暴露，因此才能被划词工具、快捷指令、自动化脚本任意调用。

## 四、应用场景与启发

- **划词翻译工作流**：搭配 SnipDo（Win）/ PopClip（Mac）/ Starry（Linux），选中即译；也可在 Hyprland 下用 `grim+slurp` 截图后 `curl` 调接口，绕开 Tauri 在 Wayland 下取不到鼠标坐标的限制。
- **截图 OCR / 截图翻译**：`/ocr_recognize`、`/ocr_translate` 端点支持 `?screenshot=false` 复用外部截图工具的图，解决部分平台内置截图不可用问题。
- **生词本闭环**：`src/services/collection` 直接对接 Anki / 欧路 / 有道 / 扇贝，翻译即收藏。
- **给同类需求的思路**：① 想把「桌面小工具」做成可组合能力，优先暴露**本地 HTTP 接口**而非只做 GUI；② 多引擎能力用「services 子目录 + 统一接口」做插件化，比 if-else 堆厂商 SDK 更易扩展；③ Tauri 是 Electron 之外做轻量跨端桌面的成熟选择，尤其是需要系统级 OCR/快捷键时。

## 五、源码深度解读

### 5.1 本地 HTTP 控制面（来自 README 的真实接口契约，对应 `src-tauri/src/server.rs`）

```text
POST "/"            => 翻译指定文本（body 为待译文本）
GET  "/config"      => 打开设置
POST "/translate"   => 翻译指定文本（同 "/"）
GET  "/selection_translate" => 划词翻译
GET  "/input_translate"     => 输入翻译
GET  "/ocr_recognize"       => 截图 OCR
GET  "/ocr_translate"       => 截图翻译
# ?screenshot=false 复用外部截图；?screenshot=true 使用内置截图
```

默认监听 `127.0.0.1:60828`，端口可在设置中更改。划词工具只需 `curl "127.0.0.1:60828/selection_translate"` 即可触发。

### 5.2 引擎抽象层（`src/services/`）

```text
src/services/
├── translate/    # 翻译引擎（OpenAI/智谱/Gemini/Ollama/百度/腾讯/DeepL/有道/Google/Bing…）
├── recognize/    # OCR 引擎（系统 OCR / Tesseract.js / 百度 / 腾讯 / 火山 / 讯飞 / Rapid / Paddle）
├── tts/          # 语音合成引擎
└── collection/   # 生词本（Anki / 欧路 / 有道 / 扇贝）
```

每个引擎实现统一接口，前端按「服务列表」动态加载，新增厂商只需在对应子目录加一个实现 + 在插件模板注册。

### 5.3 系统能力后端（`src-tauri/src/`）

系统 OCR 在不同平台走不同实现（`system_ocr.rs` 分发到 Windows.Media.OCR / Apple Vision / Tesseract），快捷键与截图由 `hotkey.rs` / `screenshot.rs` 通过 Tauri 插件与平台 API 桥接；`lang_detect.rs` 在调用翻译前先判源语言，支撑「自动识别→译目标语」。

## 六、社区口碑

- GitHub 19.4k⭐、1.0k fork、449 open issues（pushed 2026-07-04，活跃维护中）；中文翻译工具赛道中人气最高的开源项目之一，常被称作「Bob 的跨平台平替」。
- 多语言文档（中/英/韩）+ Weblate 众包翻译，社区本地化完善；提供 Winget / Homebrew / apt / AUR / Flatpak 全渠道分发。
- 外部评测数据「数据不可用」；口碑主要体现为星标增长与划词工具生态（SnipDo/PopClip 官方扩展）的主动适配。

## 七、竞品对比

| 维度 | Pot | Bob(mac) | DeepL / 有道客户端 | CopyTranslator | TTime |
|------|-----|----------|-------------------|----------------|-------|
| 平台 | Win/Mac/Linux | 仅 macOS | 各端独立 | Win/Mac | Win/Mac |
| 引擎数 | 20+ 翻译 / 10+ OCR | 较少 | 单厂商 | 少 | 中等 |
| 本地 HTTP 接口 | ✅ 完整 | ❌ | ❌ | 部分 | 部分 |
| 插件扩展 | ✅ `.potext` | ❌ | ❌ | ❌ | ❌ |
| 离线 OCR | ✅ 系统+OCR | ✅ | 部分 | 部分 | ✅ |

**结论**：Pot 的差异化不在「翻译质量」（取决于所挂引擎），而在**跨端一致性 + 可组合的控制面 + 插件生态**。

## 八、核心研判

- **定位清晰**：它卖的不是「翻译算法」，而是「翻译能力的统一入口与本地自动化总线」。这个定位让它不依赖任何单一厂商，也天然适配 LLM 翻译（已内置 OpenAI/Ollama）。
- **架构可借鉴**：把 GUI 工具做成「本地 HTTP 服务 + 轻量前端」的模式，极大提升了可组合性，值得任何桌面小工具参考。
- **风险点**：GPL-3.0 对闭源分发不友好；部分云引擎需用户自备 Key；Wayland 下快捷键/坐标仍需系统级 workaround（非 Pot 自身能解）。
- **适合复用**：需要「划词/截图→调用某能力→回写」的桌面自动化场景，可直接复用其 HTTP 控制面设计。

## 九、关键文件路径速查

```text
pot-app/pot-desktop
├── src/App.jsx                  # 前端入口
├── src/services/
│   ├── translate/  recognize/  tts/  collection/   # 四类引擎抽象
├── src-tauri/src/
│   ├── server.rs     # 本地 HTTP 控制面（127.0.0.1:60828）
│   ├── cmd.rs        # Tauri 命令聚合
│   ├── hotkey.rs  screenshot.rs  clipboard.rs  system_ocr.rs  lang_detect.rs
│   ├── tray.rs  window.rs  config.rs  backup.rs  updater.rs
├── src-tauri/tauri.conf.json    # Tauri 配置（分平台 *.conf.json）
├── package.json      # deps: @nextui-org/react, jotai, tesseract.js, ollama, tauri-plugin-*
└── README.md         # 安装/外部调用/插件开发文档
```

🔗 仓库：https://github.com/pot-app/pot-desktop ｜ 官网：https://pot-app.com ｜ 插件市场：https://pot-app.com/plugin.html
