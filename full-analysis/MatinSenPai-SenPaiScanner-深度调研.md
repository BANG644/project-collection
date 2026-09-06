# 🔬 MatinSenPai/SenPaiScanner - 全方位深度调研

> 调研日期：2026-09-07 ｜ 重写自模板化旧报告（原"四层组成"通用 boilerplate，无真实源码/架构/外链）
> 数据来源：GitHub 仓库 `MatinSenPai/SenPaiScanner` 真实 README / 目录树抓取（stars 2,365，pushed 2026-08-03，MIT，Go 1.26.1）

## 📌 一句话定位

`MatinSenPai/SenPaiScanner` 是**跨平台 Cloudflare 端点扫描器**，面向不稳定 / 被过滤 / 高延迟网络：先做快速边缘探测，再用**内嵌 Xray core** 通过真实代理配置做端到端验证，最后导出客户端就绪配置（Clash / Sing-box / 订阅）。

> 核心判断：它解决的是"在受限网络里找到低延迟、可用的 Cloudflare 优选端点"这一具体需求。工程亮点在**两阶段验证 + 三界面统一 + 停止后速度测试 + 多格式导出**。⚠️ 属网络探测工具，仅可在**你授权测试的网络 / 地址范围**内使用。

## 🏆 项目亮点（差异化）

1. **两阶段验证**：快速 Cloudflare 可达性检查 → 可选端到端 Xray 测试（对真实代理配置生效）。
2. **实时结果**：扫描进行中即可搜索 / 排序 / 复制健康端点；停止后才对短名单做聚焦速度测试。
3. **代理感知探测**：SNI / host / path / transport / TLS / port 全部从 `vless://` `trojan://` `vmess://` 分享链接自动推导。
4. **可移植导出**：原始端点、rewrite 后的分享 URL、Base64 订阅、Sing-box JSON、Clash YAML 一键生成。
5. **弹性元数据**：ISP / ASN 检测合并 Cloudflare + IPWhois + IPinfo，并以 Team Cymru DNS 作为回退。
6. **安全邻居发现**：邻近 Cloudflare 地址探索**默认关闭**，需显式开启。

## 🏗️ 核心架构

单一 Go 代码库，三界面共用同一扫描引擎：

```
SenPaiScanner/
├── cmd/senpaiscanner/main.go      # CLI 入口
├── desktop/                       # Wails 桌面后端 + Signal Desk 前端（frontend/dist）
├── android/                       # 原生 Kotlin + Jetpack Compose
├── mobile/                        # Go mobile 桥接（与 Android 共享）
├── internal/
│   ├── engine/engine.go           # 扫描引擎：Cloudflare IPv4 ranges 加权随机采样
│   ├── prober/prober.go          # 多端口探测（worker/timeout/WebSocket 检查）
│   ├── xraytest/                 # 内嵌 Xray 验证（解析 vless/trojan/vmess，transport-aware）
│   ├── ipsrc/                    # IP 源 + 邻居发现（ranges_v4/v6.txt，默认关）
│   ├── output/  export/          # 端点 / 订阅 / Sing-box / Clash 导出
│   ├── result/                   # 结果模型
│   └── ui/                       # TUI 命令、live_results、ir_isps（ISP/ASN 检测）
└── .github/workflows/            # ci / build-cli / build-gui / build-android / release
```

**Signal Desk 工作流**：Configure scan → Discover → Inspect/copy live → Stop → Speed test green → Rank → Export。桌面与 Android 各自把"Scan / Results / Export"放在独立 workspace，导出不中断结果查看。

## 🧠 源码深度解读

### 1. `internal/engine/engine.go` —— 扫描引擎

核心是对内嵌 Cloudflare IPv4 地址段做**加权随机采样**，配合文件输入（IP / CSV / CIDR），多 worker、可配置超时与 WebSocket 检查。取消操作会**保留已发现结果**——这是"长扫描可中断"的关键。

### 2. `internal/prober/prober.go` —— 探测与多端口

负责实际连通性探测，产出实时 health / latency / loss / throughput / colo / port / status。支持 TCP / WebSocket / gRPC / XHTTP(SplitHTTP) 的 transport-aware 解析。

### 3. `internal/xraytest/` —— 内嵌 Xray 验证（最有价值的部分）

把 Xray core 进程内嵌进工具，用用户的真实代理配置做端到端验证，而非只测裸连通性。解析 `vless/trojan/vmess` 分享链接、推导 SNI/host/path/transport，验证后才标记为"绿色可用"。这是它区别于"只 ping IP"类扫描器的核心。

### 4. `internal/ipsrc/` 与 `internal/ui/ir_isps.go` —— 源与元数据

`ipsrc` 管理 Cloudflare IPv4/IPv6 段与可选的邻居发现（默认关）；`ir_isps` 做 ISP/ASN 检测，合并多源并 Team Cymru DNS 回退，让导出结果带"这是哪家 ISP"的弹性元数据。

## 🌐 全网口碑画像

- GitHub：2,365⭐、MIT、43 open issues、活跃（pushed 2026-08-03）。v1.0.0 引入 Signal Desk 工作流 + SHA256SUMS 校验。
- 技术栈：Go 1.26.1 + Wails 2.11.0（桌面）+ JDK 17 / Android SDK 36（Android）。CI 矩阵完善（ci 含 race test/lint，三套 build + release）。
- 社区定位：受限网络用户的"Cloudflare 优选端点"工具，分发形态完整（Windows/Linux/macOS/Android/Termux 全覆盖）。

## ⚔️ 竞品对比

| 方案 | 优势 | 风险 |
|---|---|---|
| `SenPaiScanner` | 三界面统一、内嵌 Xray 真实验证、停止后速度测试、多格式导出 | 仅限授权网络使用；功能聚焦 CF，非通用端口扫描 |
| CloudflareSpeedTest（11HKM 等） | 轻量、纯测速、用户基数大 | 通常无内嵌代理验证、导出格式较少 |
| 纯 ping/tcping 脚本 | 极简 | 无代理验证、无 UI、无批量导出 |

## 🎯 核心研判

**优势**：① 工程完成度高（跨平台 + 内嵌验证 + 多格式导出 + 完整 CI）；② "两阶段验证 + 停止后速度测试"精准命中"要的是能用的端点，不是能 ping 通的 IP"这一痛点；③ 安全设计到位（邻居发现默认关、凭证不入库）。

**风险**：① 属网络探测工具，**务必仅在授权网络/地址范围使用**，勿在 issue 截图里泄露代理凭证；② 功能聚焦 Cloudflare，泛用性有限；③ 依赖 Xray 生态版本演进。

**适用场景**：在受限 / 高延迟网络下，为 Cloudflare 反代 / 优选 IP 寻找低延迟可用端点，并直接产出 Clash/Sing-box 配置的用户。

**不适用场景**：未经授权对任意网络扫描（合规红线）；需要通用全端口服务发现的场景。

## 📂 关键文件路径速查

- `README.md` / `README.fa.md`：功能、Signal Desk 工作流、三界面下载、构建。
- `cmd/senpaiscanner/main.go`：CLI 入口。
- `internal/engine/engine.go`：扫描引擎（加权随机采样 Cloudflare 段）。
- `internal/prober/prober.go`：多端口探测。
- `internal/xraytest/`：内嵌 Xray 端到端验证。
- `internal/ipsrc/` + `internal/ui/ir_isps.go`：IP 源 / 邻居发现 / ISP·ASN 检测。
- `internal/export/export.go`：多格式客户端配置导出。
- `.github/workflows/`：ci / build-cli / build-gui / build-android / release（含 SHA256SUMS）。

## ⭐ 三条关键发现

1. 真正的技术护城河是**内嵌 Xray 的端到端验证**——它验证的是"你的代理配置真能跑通"，而非裸 IP 连通性。
2. **"扫描中可复制 + 停止后才测速"** 的工作流设计，比"扫完再筛"高效得多，是受限网络用户的实际刚需。
3. 合规是硬约束：仓库明确"仅扫描你授权测试的网络"，任何使用都必须在授权边界内。
