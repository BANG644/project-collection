# koala73/worldmonitor — 实时全球情报仪表盘深度调研

## 项目全景

- **仓库**: [koala73/worldmonitor](https://github.com/koala73/worldmonitor)
- **Stars**: ~58,000⭐ (Trending, +253 today)
- **语言**: TypeScript
- **许可**: AGPL-3.0
- **作者**: Elie Habib (koala73)
- **官网**: https://worldmonitor.app
- **核心定位**: AI 驱动的实时全球情报仪表盘 — 新闻聚合、地缘政治监控、基础设施追踪的统一态势感知界面

## 核心架构

### 技术栈
| 层 | 技术 |
|---|------|
| 前端 | Vanilla TypeScript + Vite |
| 3D 地图 | globe.gl + Three.js |
| 2D 地图 | deck.gl + MapLibre GL |
| 桌面端 | Tauri 2 (Rust + Node.js sidecar) |
| AI/ML | Ollama / Groq / OpenRouter, Transformers.js |
| 部署 | Vercel Edge Functions (60+), Railway, PWA |
| 缓存 | Redis (Upstash), 3-tier cache, CDN, Service Worker |
| API 契约 | Protocol Buffers (276 protos, 34 services) |

### 核心功能
- **500+ 精选新闻源**，15 个分类，AI 合成简报
- **双地图引擎**：3D 地球 (globe.gl) + WebGL 平面地图 (deck.gl)，56 种地图图层
- **跨流关联**：军事、经济、灾害、升级信号汇聚分析
- **国家不稳定指数 (CII)**：31 个 Tier-1 国家压力评分 v8
- **金融雷达**：29 个股票交易所 + 商品 + 加密货币，7 信号市场复合指标
- **本地 AI**：完全支持 Ollama，无需任何 API Key
- **6 站点变体**：同一代码库构建 world/tech/finance/commodity/happy/energy 六个站点
- **24 种语言**：原生语种新闻源 + RTL 支持

## 竞品对比

| 维度 | WorldMonitor | Dataminr | EventRegistry | GDELT |
|------|-------------|----------|--------------|-------|
| 开源 | ✅ AGPL-3.0 | ❌ 商业 | ❌ 商业 | ✅ |
| 本地 AI | ✅ Ollama | ❌ | ❌ | ❌ |
| 桌面端 | ✅ Tauri 2 | ❌ | ❌ | ❌ |
| 地缘政治评分 | ✅ CII v8 | ✅ | ❌ | ⚠️ |
| 多交易所金融 | ✅ 29个 | ⚠️ 部分 | ❌ | ❌ |
| 自部署 | ✅ 支持 | ❌ | ⚠️ | ✅ |

## 核心研判

**优势**：
1. **唯一开源的全栈全球情报平台** — 同类产品（Dataminr、NewsWhip）均为商业闭源
2. **单体代码库产生 6 个站点变体**，架构设计极为精良
3. **本地 AI 优先** — Ollama 支持使敏感机构可完全脱离外网运行
4. **276 个 Protobuf + 34 个服务**的 API 契约表明是严肃工程而非原型
5. CII v8 国家不稳定指数有独立方法论，非简单聚合

**风险/局限**：
1. AGPL-3.0 对商业 SaaS 有强 copyleft 约束
2. 高度依赖第三方数据源（65+ 外部提供商），任一源断供影响面大
3. 单个维护者（Elie Habib）驱动，长期可持续性存疑
4. 58K 星但 Issue 列表活跃度不详，需观察社区健康度

## 关键文件路径速查

```
/koala73/worldmonitor
├── src/                    # 前端主代码 (TypeScript)
├── tauri/                  # Tauri 2 桌面端
├── protos/                 # Protocol Buffers 定义
├── docs/                   # 文档 (MDX)
│   ├── architecture.md     # 架构文档
│   ├── data-sources.md     # 数据源目录
│   └── license.mdx         # 许可说明
├── .env.example            # 环境变量模板
└── LICENSE                 # AGPL-3.0
```

## 关键数据
- Stars: ~58,000 (Trending)
- 外部数据源: 65+ 合作伙伴
- 新闻源: 500+ 精选
- 地图图层: 56 种
- Protobuf: 276 个定义, 34 个服务
- 支持语言: 24 种
- 站点变体: 6 个
- 桌面端: Windows / macOS / Linux

## 总结

WorldMonitor 是目前最全面的开源全球情报仪表盘，在开源领域无直接竞品。其「单体代码库多站点变体」架构设计值得深入学习。对于需要实时地缘政治/金融市场监控的团队，这是不可多得的选择。但 AGPL 许可和对单一维护者的依赖是需要评估的风险点。
