# 📄 Stirling-PDF — #1 PDF Application on GitHub

> **仓库**: [Stirling-Tools/Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF)
> **Stars**: 82,799⭐ | **今日新增**: 691⭐
> **语言**: Java (Spring Boot) + TypeScript/React 前端 | **许可证**: AGPL-3.0 (Open Core)
> **官网**: [stirling.com](https://stirling.com) | **文档**: [docs.stirlingpdf.com](https://docs.stirlingpdf.com)

## 一、项目全景

Stirling PDF 是 GitHub 上 **排名第一的 PDF 应用程序**，同时也是**排名第一的 Docker 化 PDF 工具**。它是一款功能强大、开源的 PDF 编辑平台，定位是"PDF 领域的超级工具箱"——50+ 种 PDF 操作工具集成于一身，支持个人桌面客户端、浏览器 Web UI 和企业级服务器部署。

核心卖点：**不把文档发送给外部服务**，所有处理在本地或自托管服务器完成，数据零泄露。

**项目亮点**：
- 🥇 PDF 类目 GitHub Stars 第一（82K+），Docker Hub 4000万+ pulls（前 200）
- 🔒 隐私优先：自托管、本地处理、SSO + 审计日志，企业合规友好
- 🧩 50+ 工具矩阵 + 可视化无代码自动化管线 + REST API
- 💡 Open Core 商业模型：社区版永久免费，企业订阅提供 SSO/审计/技术支持

## 二、核心架构

```
┌─────────────────────────────────────┐
│          Web UI (React/TS)           │
├─────────────────────────────────────┤
│          REST API Gateway             │
├──────────┬──────────┬────────────────┤
│ Core PDF │ OCR      │ Automation     │
│ Engine   │ Engine   │ Pipeline       │
│(PDFBox/  │(Tesseract│ (No-Code       │
│ iText)   │/OCRmyPDF)│  Workflow)     │
├──────────┴──────────┴────────────────┤
│  Storage: Local FS / S3 / Object Store│
└─────────────────────────────────────┘
```

### 技术栈
- **前端**: React + TypeScript（响应式，40+ 语言支持）
- **后端**: Java (Spring Boot)，多模块 Maven 工程
- **核心引擎**: Apache PDFBox（免费版）/ iText（增强版，proprietary 模块）
- **OCR**: Tesseract + OCRmyPDF（多语言）
- **部署**: Docker 优先，支持 Kubernetes
- **安全**: SSO（OAuth2/OIDC/LDAP/SAML）、审计日志、细粒度权限

### 多模块工程结构
仓库采用 Maven 多模块划分，将开源核心与商业功能物理隔离：
- `app/common` — 跨模块共享库（配置模型、工具类）
- `app/core` — 开源核心（启动类、50+ REST 控制器、转换/签名逻辑）
- `app/proprietary` — 商业增强功能（企业特性）
- `app/saas` — SaaS 部署配置（dev/saas profile）

## 三、源码深度解读

Stirling-PDF 的 Spring Boot 代码高度「声明式」——每个 PDF 操作为一个独立 `@RestController`，这是理解它「50+ 工具」扩展方式的关键。

**1. 控制器即工具（每个功能一个 Controller）**
控制器集中在 `app/core/.../SPDF/controller/api/` 下，命名即功能：
- `MergeController.java` / `SplitPDFController.java` / `SplitPdfByChaptersController.java` — 合并与按章节/尺寸拆分
- `CropController.java` / `RotationController.java` / `ScalePagesController.java` / `RearrangePagesPDFController.java` — 页面编辑
- `controller/api/converters/` — 格式互转簇：`ConvertPDFToOffice.java`、`ConvertPDFToHtml.java`、`ConvertOfficeController.java`、`ConvertHtmlToPDF.java`、`ConvertPdfToVideoController.java` 等

这种「一功能一 Controller」的扁平结构，使新增工具等价于新增一个带 `@PostMapping` 的类，是它能在社区贡献下快速堆出 50+ 工具的设计原因。

**2. 签名/安全基于 Apache PDFBox 示例体系**
签名相关逻辑直接复用并封装 PDFBox 官方示例：`app/core/.../org/apache/pdfbox/examples/signature/` 下可见：
- `CreateSignatureBase.java` — 数字签名基类
- `TSAClient.java` / `ValidationTimeStamp.java` — 时间戳权威（TSA）接入
- `CMSProcessableInputStream.java` — CMS 签名数据处理

这说明其安全能力并非自研加密，而是 **PDFBox 标准签名流程的 Spring 封装**，降低了安全实现出错面。

**3. 配置驱动（Open Core 的开关机制）**
`app/common/.../model/ApplicationProperties.java` 是整个系统的配置中枢，企业特性（SSO、审计、API 增强）通过 `app/proprietary/src/main/resources/application-proprietary.properties` 与 `app/saas/.../application-saas.properties` 的分 profile 配置开启——这是典型 Open Core「同一代码库、配置门控商业功能」的实现。

## 四、社区口碑

- **规模**：82K+ Stars、500+ 社区贡献者、Docker Hub 4000万+ pulls（Docker 官方排名前 200），月均 4-6 个版本的高频迭代。
- **定位口碑**：长期被视为「自托管 PDF 工具箱」事实标准，在 r/selfhosted、Hacker News、少数派等社区被反复推荐为 SmallPDF/Adobe 的隐私替代。
- **企业信号**：提供 SSO（OAuth2/OIDC/LDAP/SAML）、审计日志、水平扩展（Redis 缓存 + 对象存储），已被政府/金融/法律等强合规行业采用。
- **争议点**：AGPL-3.0 对闭源集成不友好；部分高级能力（如某些格式转换精度、企业支持）仅在订阅版，社区偶有「开源版够用但边界模糊」的讨论。

## 五、竞品对比

| 特性 | Stirling-PDF | Adobe Acrobat | PDF24 | Sejda | SmallPDF |
|------|-------------|--------------|-------|-------|----------|
| 开源 | ✅ Open Core | ❌ 商业 | ❌ | ❌ | ❌ |
| 数据隐私 | ✅ 本地 | ❌ 云 | ❌ 云 | ❌ 云 | ❌ 云 |
| 自托管 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 50+ 工具 | ✅ | ~30 | ~20 | ~15 | ~20 |
| 自动化管线 | ✅ | ❌ | ❌ | ❌ | ❌ |
| API | ✅ | ✅ (昂贵) | ❌ | ✅ | ✅ (收费) |
| OCR | ✅ | ✅ | ✅ | ❌ | ✅ |
| SSO | ✅ | ✅ (企业) | ❌ | ❌ | ❌ |
| Docker | ✅ | ❌ | ❌ | ❌ | ❌ |
| 价格 | 免费+企业订阅 | $25/月+ | 免费 | 免费 | 免费+付费 |

## 六、核心研判

**优势**
- 「将简单需求做到极致」的典范：自托管 PDF 工具箱是被大厂长期忽略的刚需，Stirling-PDF 用开源 + 隐私 + Docker 一键部署精准占位。
- 架构支撑规模化：一功能一 Controller 的扁平结构 + 配置门控 Open Core，使社区贡献与企业商业化并行不悖。

**风险**
- AGPL-3.0 对闭源 SaaS 集成构成合规门槛；核心引擎依赖 PDFBox/iText，转换精度天花板受上游约束。
- 功能 breadth 优先于单点深度，重度排版/复杂表单场景仍弱于 Adobe。

**趋势**
- 企业订阅（Server/Enterprise）是其商业化主路径，SSO/审计/API 增强持续加码；AI 文档处理（如 LLM 摘要/提取）是下一明显扩展方向。

**启发**
- 对同类「工具箱型」需求（如图像、音视频、OCR），Stirling-PDF 验证了「开源占位 + 隐私卖点 + Docker 分发 + Open Core 变现」的可复制范式。

## 七、关键文件速查

| 路径 | 作用 |
|------|------|
| `app/core/src/main/java/stirling/software/SPDF/SPDFApplication.java` | Spring Boot 启动类 |
| `app/core/src/main/java/stirling/software/SPDF/controller/api/` | 50+ REST 控制器（每功能一个） |
| `app/core/src/main/java/stirling/software/SPDF/controller/api/converters/` | 格式互转控制器簇 |
| `app/core/src/main/java/org/apache/pdfbox/examples/signature/` | 数字签名/时间戳封装（PDFBox 示例体系） |
| `app/common/src/main/java/stirling/software/common/model/ApplicationProperties.java` | 全局配置模型（商业功能开关） |
| `app/proprietary/src/main/resources/application-proprietary.properties` | 企业特性 profile 配置 |
| `app/core/src/main/resources/application.properties` | 核心应用配置 |

## 八、使用场景与定价

**使用场景**：个人文档处理（合并/转换/签名）、企业文档系统（自托管 API 集成 OA/ERP）、DevOps 自动管线（CI/CD 批量 PDF 处理）、政府/金融机构文档脱敏（Redact）+ 审计追踪、法律行业电子签名与批量水印。

**定价模式（Open Core）**：

| 版本 | 费用 | 功能 |
|------|------|------|
| **Community** | 免费 | 核心 50+ 工具，Web UI |
| **Server Plan** | 订阅 | SSO + 审计 + API 增强 + 技术支持 |
| **Enterprise** | 定制 | 专属部署 + 定制功能 + SLA |
