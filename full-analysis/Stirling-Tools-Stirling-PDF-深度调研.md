# 📄 Stirling-PDF — #1 PDF Application on GitHub

> **仓库**: [Stirling-Tools/Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF)
> **Stars**: 82,799⭐ | **今日新增**: 691⭐
> **语言**: TypeScript | **许可证**: AGPL-3.0 (Open Core)
> **官网**: [stirling.com](https://stirling.com) | **文档**: [docs.stirlingpdf.com](https://docs.stirlingpdf.com)

## 项目概述

Stirling PDF 是 GitHub 上 **排名第一的 PDF 应用程序**，同时也是**排名第一的 Docker 化 PDF 工具**。它是一款功能强大、开源的 PDF 编辑平台，定位是"PDF 领域的超级工具箱"——50+ 种 PDF 操作工具集成于一身，支持个人桌面客户端、浏览器 Web UI 和企业级服务器部署。

核心卖点：**不把文档发送给外部服务**，所有处理在本地或自托管服务器完成，数据零泄露。

## 核心能力

### 50+ PDF 工具矩阵

| 类别 | 工具 |
|------|------|
| **合并/拆分** | PDF 合并、拆分页面、提取页面 |
| **编辑** | 添加文本/图像、擦除内容、裁剪 |
| **转换** | 多种格式互转（PDF↔Word/Excel/PPT/图片） |
| **OCR** | 扫描件文字识别（多语言） |
| **签名 & 安全** | 电子签名、添加水印、密码加密/解密、Redact 脱敏 |
| **压缩优化** | 文件压缩、图像优化 |
| **元数据** | 编辑/清理元数据 |
| **自动化** | 无代码管线 + REST API |

### 部署形态

| 形态 | 适用场景 | 命令 |
|------|---------|------|
| Docker（推荐） | 最快上手 | `docker run -p 8080:8080 docker.stirlingpdf.com/stirlingtools/stirling-pdf` |
| 桌面客户端 | 个人日常 | 原生安装包 |
| 浏览器 Web UI | 临时使用 | 浏览器打开即可 |
| 自托管服务器 | 企业级 | Docker/K8s/手动部署 + 私有 API |

## 技术架构

```
┌─────────────────────────────────────┐
│          Web UI (React)              │
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
- **后端**: Java (Spring Boot)
- **核心引擎**: Apache PDFBox（免费版）/ iText（增强版）
- **OCR**: Tesseract + OCRmyPDF（多语言）
- **部署**: Docker 优先，支持 Kubernetes
- **安全**: SSO（OAuth2/OIDC/LDAP）、审计日志、细粒度权限

## 企业级特性

- **SSO 集成**: OAuth2、OIDC、LDAP、SAML
- **审计日志**: 全操作记录追踪
- **API 优先**: REST API 覆盖几乎全部工具，支持百万级文档处理
- **自动化管线**: 可视化无代码工作流编辑器
- **扩展性**: 水平扩展，Redis 缓存，对象存储后端
- **多区域部署**: 灵活 on-premises 方案

## 竞品对比

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

## 关键统计数据

- **Docker Pulls**: 4000万+（Docker Hub 排名前 200）
- **GitHub Stars**: 82K+（PDF 类别 #1）
- **贡献者**: 500+ 社区贡献者
- **语言**: 40+ 界面语言
- **更新频率**: 月均 4-6 个版本

## 使用场景

1. **个人文档处理**: 合并 PDF、格式转换、签名
2. **企业文档系统**: 自托管 API 集成到 OA/ERP
3. **DevOps 自动管线**: CI/CD 中批量 PDF 生成和处理
4. **政府/金融机构**: 文档脱敏处理（Redact）、审计追踪
5. **法律行业**: 电子签名、文档加密、批量水印

## 定价模式 (Open Core)

| 版本 | 费用 | 功能 |
|------|------|------|
| **Community** | 免费 | 核心 50+ 工具，Web UI |
| **Server Plan** | 订阅 | SSO + 审计 + API 增强 + 技术支持 |
| **Enterprise** | 定制 | 专属部署 + 定制功能 + SLA |

## 结论

Stirling-PDF 的成功（82K Stars, #1 PDF App on GitHub）证明了一个经典策略：**将简单需求做到极致**。它不是 PDF 领域的技术突破，而是对"自托管 PDF 工具箱"这个被忽略需求的完美满足。对于需要 PDF 处理能力的团队/个人，这是目前成本最低、隐私最好的方案。
