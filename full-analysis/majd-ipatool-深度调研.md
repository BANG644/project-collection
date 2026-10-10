# majd/ipatool 深度调研

> 调研日期：2026-10-11 | 星标：11,579⭐ | 语言：Go | 许可：MIT | 默认分支：main | 最近提交：活跃（pushed 2026-10-10）| 趋势：GitHub Trending（当日新增）

## 一句话定位

ipatool 是一个命令行工具，用来在 App Store 搜索 iOS / iPadOS / tvOS / watchOS / visionOS / macOS 应用，并下载 `.ipa`（或 macOS `.pkg`）安装包——支持 macOS / Linux / Windows / iOS，可经 MCP 把 App Store 能力暴露给 agent。

## 项目亮点

- **全 Apple 平台覆盖**：一套命令搜/下 iOS、iPadOS、tvOS、watchOS、visionOS、macOS 的 app 包（`.ipa` / `.pkg`）。
- **多平台 CLI**：macOS（Homebrew `brew install ipatool`）、Linux、Windows、甚至 iOS 都能跑。
- **内置 MCP 服务器**：`ipatool mcp` 以 stdio 暴露 App Store 工具，可被任意 MCP 客户端接入。
- **工程化良好**：cobra 子命令（auth / search / download / purchase / list-purchases / list-versions / get-version-metadata / mcp），`--non-interactive` 适配自动化，`--format json` 便于管道。
- **认证清晰**：需已配置的 Apple Account，交互登录或 keychain 口令，明确「下载你拥有/已购的 app」。

## 核心架构

- **cmd/（cobra 命令层）**：`download.go` / `search.go` / `auth.go` / `purchase.go` / `purchases.go` / `mcp.go` / `mcp_tools.go` 等，命令解耦、可单测。
- **internal/sap/（StoreKit Auth Protocol 实现）**：`protocol.go`（SAP 握手：certificate / exchange，plist XML）、`signer.go`（请求签名）、`machine/kbsync.go`（设备标识/同步）、`unicorn/`（本地模拟与缓存/归档）、`machimage/`（mach-o 镜像）、`cpio/`（cpio 读写）。
- **依赖注入**：`dependencies.AppStore` 抽象，命令通过 `downloadCmdWithAppStore(func() appstore.AppStore)` 注入，便于测试替换。
- **下载链路**：`store.AccountInfo()` → 解析 platform → 走 SAP 协议取授权 → 拉包 + `retry-go` 重试 + `progressbar` 进度。

## 应用场景与启发

- 安全研究者 / 逆向工程师抓取指定版本 `.ipa` 做静态分析、版本比对、漏洞复现；普通用户做「已购应用归档 / 降级备份」。
- **「把封闭平台能力封装成 CLI + MCP」的范式**：ipatool 把 Apple 私有 StoreKit 协议逆向成可脚本化的命令行，再叠 MCP 层给 agent——与「把 GUI/私有 API 变成 agent 工具」的通用思路一致。
- 对做 App Store 生态工具 / 应用分发审计的启发：plist 协议 + 设备标识模拟是这类抓取器的关键模块，可借鉴其 `internal/sap/` 分层。

## 源码深度解读

**下载命令（`cmd/download.go`）——cobra + 依赖注入 + 重试**

```go
func downloadCmdWithAppStore(appStore func() appstore.AppStore) *cobra.Command {
    cmd := &cobra.Command{
        Use: "download",
        RunE: func(cmd *cobra.Command, args []string) error {
            if appID == 0 && bundleID == "" {
                return errors.New("either the app ID or the bundle identifier must be specified")
            }
            platform, err := appstore.ParsePlatform(platformValue)
            ...
            store := appStore()
            infoResult, err := store.AccountInfo()
            ...
        },
    }
}
```

**SAP 握手（`internal/sap/protocol.go`）——plist 协议**

```go
func (p setupProtocol) certificate(ctx context.Context, endpoint string) ([]byte, error) {
    request, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
    request.Header.Set("User-Agent", apphttp.DefaultUserAgent)
    body, err := p.send(request)
    return plistBytes(body, setupCertificateKey)
}
func (p setupProtocol) exchange(ctx context.Context, endpoint string, input []byte) ([]byte, error) {
    envelope, err := plist.Marshal(map[string]any{setupBufferKey: input}, plist.XMLFormat)
    ...
}
```

两个要点：① 下载命令把 `appstore.AppStore` 通过闭包注入，测试可传入 fake 实现（依赖倒置），且 `RunE` 先校验入参再发请求；② SAP 协议全程用 `howett.net/plist` 的 XML 格式做证书拉取与信封交换（`maxSetupBody = 1<<20` 限流），是逆向 Apple 私有协议的标准手法。

## 全网口碑

- 长期维护的经典工具，此次因新增 MCP 支持 + 多平台重新登趋势榜；Go 单二进制、跨平台、MIT，社区口碑稳。
- **合规提示**：工具需你自己的 Apple Account，定位「下载你拥有/已购的 app」；经非官方认证拉 `.ipa` 可能触及 Apple ToS，研究/备份用途为主，勿用于侵权分发。

## 竞品对比 + 核心研判

- **竞品**：商业版 App 管理器（如 Apple Configurator 仅限 macOS）、各类闭源抓包脚本；OSS 同类极少。
- **差异化**：MIT 开源、Go 单二进制跨平台、覆盖全部 Apple OS、并原生带 MCP 服务器。
- **研判**：实用且工程扎实的 App Store CLI，MCP 化使其可嵌入 agent 工作流。两点提醒——① 依赖 Apple 私有协议，Apple 改协议即需跟进（维护风险）；② ToS 边界需用户自觉遵守。适合安全研究、应用归档与 agent 化 App Store 操作场景。

## 关键文件路径速查

- `cmd/download.go` — 下载命令（cobra + 依赖注入 + retry-go + progressbar）
- `internal/sap/protocol.go` — StoreKit Auth Protocol 握手（plist certificate / exchange）
- `internal/sap/machine/kbsync.go` — 设备标识 / 同步
- `internal/sap/signer.go` — 请求签名
- `cmd/mcp_tools.go` · `cmd/mcp.go` — MCP 工具暴露与 stdio 服务
- `internal/sap/unicorn/` — 本地模拟 / 缓存 / 归档
- `internal/sap/machimage/` · `internal/sap/cpio/` — mach-o 镜像与 cpio 处理
