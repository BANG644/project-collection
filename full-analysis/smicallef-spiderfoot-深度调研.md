# SpiderFoot 深度调研

> 调研日期：2026-08-13 | 星标：20,287（2026-08-12）| 协议：MIT | 语言：Python 3.7+ | 定位：开源情报（OSINT）自动化

## 一、项目定位

SpiderFoot 是**开源情报（OSINT）自动化工具**，集成几乎所有可用数据源，用多种分析方法让数据易于导航。Python 3 编写、MIT 许可，提供嵌入式 Web UI 与 CLI。自 2012 年持续开发，是 OSINT 领域的开源标杆（Maltego 的开源替代）。

## 二、项目亮点

1. **200+ 模块**，多数无需 API key，含免费层。
2. **模块间 publisher/subscriber 模型**：一个模块产出喂给下一个，最大化数据抽取。
3. **YAML 可配置关联引擎（correlation engine）**，37 条预置规则。
4. **多目标类型**：IP/域名/主机/子网/ASN/邮箱/电话/用户名/人名/BTC。
5. 导出 CSV/JSON/GEXF；SQLite 后端自定义查询；可视化。
6. TOR 集成；可调用 DNSTwist/Whatweb/Nmap/CMSeeK；Docker 部署；商业版 HX（云托管、攻击面监控、多用户）。

## 三、核心架构

- **入口**：`sf.py`（Web `-l 127.0.0.1:5001`）/ `sfcli/`（CLI）/ `sfwebui/`（Web）/ `bin/`。
- **核心 `sflib/`**：`SpiderFootEvent` / `SpiderFootPlugin` / `SpiderFootHelpers` 等基础设施。
- **模块 `modules/sfp_*.py`**：每个模块继承 `SpiderFootPlugin`，声明 `meta`/`opts`/`optdescs`，消费/生产事件。
- **扫描编排 `sfscan.py`**：驱动模块按依赖图执行。
- **关联引擎 `correlations/*.yaml`**：声明式规则把低层事件升级为高层结论。
- **数据流**：模块通过事件总线（Queue）发布/订阅，形成 feed-each-other 的 DAG。

## 四、应用场景与启发

- **场景**：红队侦察、渗透测试前信息收集；蓝队/防御方自查暴露面；攻击面监控。
- **启发 1**：OSINT 的本质是"**数据源联邦 + 事件驱动的模块图**"，SpiderFoot 用 publish/subscribe + 可插拔模块把 200+ 异构源编织成一张情报网。
- **启发 2**：YAML 关联规则把"原始观测"提升为"威胁结论"（如 `cloud_bucket_open`、`vulnerability_critical`），这种"**模块即插件 + 规则即策略**"架构对任何威胁情报/数据融合平台都适用。
- **启发 3**：十年积累的模块网络是真正的护城河，远非单点爬虫可比。

## 五、源码深度解读

### 1. `modules/sfp_accounts.py` — 典型模块实现
```python
class sfp_accounts(SpiderFootPlugin):
    meta = {
        'name': "Account Finder",
        'summary': "Look for possible associated accounts on over 500 social...",
        'useCases': ["Footprint", "Passive"],
        'categories': ["Social Media"]
    }
    opts = { "ignorenamedict": True, "permutate": False, "usernamesize": 4, "_maxthreads": 20 }
    # 多线程 Queue 处理，跨 500+ 站点查找关联账号
```
印证"**每个模块 = 一个独立情报源，统一插件接口**"。

### 2. `sflib/` — SpiderFootEvent / SpiderFootPlugin 基类
定义事件类型、模块生命周期（`handleEvent`）、与核心的事件总线契约。所有 `sfp_*` 模块遵循此契约，是 SpiderFoot **可扩展性**的根基。

### 3. `correlations/template.yaml` + 37 条规则
关联引擎用声明式 YAML 把低层事件（证书过期、开放端口、bucket 公开）组合成高层结论（`outlier_*` / `cloud_bucket_open` / `vulnerability_*`），实现"从数据到洞察"的可配置升级。

## 六、社区口碑

- 20k⭐，自 2012 年持续开发（10+ 年），有 HX 商业版、Codecov、Discord。
- 口碑：模块覆盖极广、开箱即用；被视为 OSINT 开源首选。
- 不足：部分模块依赖第三方 API key、部分数据源失效需维护；Python 3.7+ 基线较老。

## 七、竞品对比 + 核心研判

| 维度 | SpiderFoot | Maltego（商业） | theHarvester / Recon-ng |
|------|-----------|----------------|------------------------|
| 授权 | 开源 MIT | 商业 | 开源（单点） |
| 模块/数据源 | 200+ 集成平台 | 图形化强、商业生态 | 单点工具 |
| 自动化 | CLI/Web 全自动化 | 交互式图 | 脚本式 |

- **核心护城河**："200+ 模块的情报源网络 + 关联规则引擎"，且 10 年积累难以短时间复制。
- **风险**：维护负担重（数据源易失效）；商业 HX 分流部分高级能力（攻击面监控、多用户）。
- **研判**：适合安全研究员、渗透测试者、攻击面自查；与图形化 Maltego 互补，自动化场景更优。

## 八、关键文件速查

- `sf.py` — 主入口/Web 服务
- `sflib/` — SpiderFootEvent / SpiderFootPlugin 基础设施
- `modules/sfp_*.py` — 200+ 情报模块
- `sfscan.py` — 扫描编排
- `correlations/*.yaml` — 关联规则
- `sfwebui/` + `sfcli/` — Web / CLI 界面
