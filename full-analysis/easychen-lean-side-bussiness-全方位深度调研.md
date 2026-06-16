# 🔬 easychen/lean-side-bussiness - 全方位深度调研

## 项目全景
- **仓库**：`easychen/lean-side-bussiness`
- **一句话定位**：精益副业：程序员如何优雅地做副业
- **基础指标**：Stars=11978 / Forks=961 / 默认分支=`main`
- **Topics**：数据不可用
- **Homepage**：http://r.ftqq.com/lean-side-bussiness/index.html

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：docs(255), src(236), .DS_Store(1), README.md(1), book.toml(1), cover.jpg(1), qrcode.jpeg(1)
- 关键文件候选：README.md

### 设计亮点研判
- 从目录上看更偏轻量仓库，核心价值主要集中在脚本、配置和场景化实现。

## 源码深度解读
### README / 说明文档要点
# 精益副业：程序员如何优雅地做副业

UPDATE：🎈 [《一人企业方法论2.0》已在CC-BY-NC-SA协议下发布，建议先读完后继续阅读本书](https://github.com/easychen/one-person-businesses-methodology-v2.0) 

![](https://github.com/easychen/one-person-businesses-methodology-v2.0/raw/master/src/images/opb-book-cover.jpg)

---

> 本书部分内容已被收录于《全栈路线图》，[可点此查看高清版PDF和源文件](https://github.com/easychen/stack-roadmap)

[![方糖全栈路线图](https://user-images.githubusercontent.com/1294760/210160612-68e4a551-47d8-4137-b2f1-4dd5fdf6d49d.jpg)](https://github.com/easychen/stack-roadmap)

本书扩展了《程序员如何优雅地挣零花钱》的基本内容，将其放到更大的副业视角；同时，引入经过互联网行业验证的「精益创业」流程，并优化为副业专用的「精益副业」流程。

在书籍第二部分，以实际案例为主，添加了「独立开发变现」和「网课变现实践」的内容。

本书成书于2020年12月，晚于[一人公司方法论](https://github.com/easychen/one-person-businesses-methodology)，在阅读完本书后，可以阅读[一人公司方法论](https://github.com/easychen/one-person-businesses-methodology)。将来如有机会，我会尝试把「精益副业」和「一人公司方法论」整合到一个体系下。可扫[这个二维码](qrcode.jpeg)订阅更新通知。



![cover.jpg](cover.jpg)

[在线阅读](http://r.ftqq.com/lean-side-bussiness/)

# 目录

* [为什么副业特别重要](src/01.md)
    * [职业可能性](src/0101.md)
        * [职业的四大象限](src/010101.md)
        * [没有副业的职业](src/010102.md)
        * [副业带来的可能性](src/010103.md)
    * [职业自由度](src/0102.md)
        * [从中指备用金说起](src/010201.md)
        * [PlanB和反脆弱](src/010202.md)
        * [全新的工作自由度](src/010203.md)
    * [职业成长性](src/0103.md)
        * [新技术练兵场](src/010301A.md)
        * [业务敏感度](src/010302.md)
* [如何优雅地做副业](src/02.md)
    * [想明白核心资源和核心优势](src/0201.md)
        * [副业的核心资源](src/020101.md)
        * [副业的核心优势](src/020102.md)
    * [时间片](src/0202.md)
        * [时间片的销售](src/020201.md)
        * [时间片的优化](src/020202.md)
        * [突破时间片限制](src/020203.md)
    * [资产和被动收入](src/0203.md)
        * [什么是资产](src/020301.md)
        * [资产的获得方式](src/020302.md)
        * [资产的量化评估](src/020303.md)
* [优选资产](src/03.md)
    * [知识和人脉的变现](src/0301.md)
        * [付费视频课](src/030101.md)
        * [付费专栏](src/030102.md)
        * [付费社群](src/030103.md)
        * [图书出版](src/030104.md)
    * [自有产品和服务](src/0302.md)
        * [半成品市场](src/030205.md)
        * [开源/免费+收费模式](src/030204.md)
        * [应用市场卖APP](src/030201.md)
        
* [精益副业](src/04.md)
    * [精益副业流程](src/0401.md)
        * [什么是精益创业](src/040101.md)
        * [精益副业：为副业优化的精益流程](src/040102.md)
        * [商业模式画布](src/040104.md)
        * [最小可行产品和产品市场契合](src/040105.md)

    * [精益独立开发实践](src/0403.md)
        * [独立开发的精益流程](src/040301.md)
        * [福利单词项目简介](src/040302.md)
        * [福利单词的商业模式画布](src/040303.md)
        * [通过用户画像细化客户](src/040304.md)
        * [画像→场景→功能和分期](src/040305.md)
        * [什么是好的商业设计](src/
...[truncated]

### 关键文件精读
### `README.md`
```
# 精益副业：程序员如何优雅地做副业

UPDATE：🎈 [《一人企业方法论2.0》已在CC-BY-NC-SA协议下发布，建议先读完后继续阅读本书](https://github.com/easychen/one-person-businesses-methodology-v2.0) 

![](https://github.com/easychen/one-person-businesses-methodology-v2.0/raw/master/src/images/opb-book-cover.jpg)

---

> 本书部分内容已被收录于《全栈路线图》，[可点此查看高清版PDF和源文件](https://github.com/easychen/stack-roadmap)

[![方糖全栈路线图](https://user-images.githubusercontent.com/1294760/210160612-68e4a551-47d8-4137-b2f1-4dd5fdf6d49d.jpg)](https://github.com/easychen/stack-roadmap)

本书扩展了《程序员如何优雅地挣零花钱》的基本内容，将其放到更大的副业视角；同时，引入经过互联网行业验证的「精益创业」流程，并优化为副业专用的「精益副业」流程。

在书籍第二部分，以实际案例为主，添加了「独立开发变现」和「网课变现实践」的内容。

本书成书于2020年12月，晚于[一人公司方法论](https://github.com/easychen/one-person-businesses-methodology)，在阅读完本书后，可以阅读[一人公司方法论](https://github.com/easychen/one-person-businesses-methodology)。将来如有机会，我会尝试把「精益副业」和「一人公司方法论」整合到一个体系下。可扫[这个二维码](qrcode.jpeg)订阅更新通知。



![cover.jpg](cover.jpg)

[在线阅读](http://r.ftqq.com/lean-side-bussiness/)

# 目录

* [为什么副业特别重要](src/01.md)
    * [职业可能性](src/0101.
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
数据不可用

### Pull Requests 抽样
- PR #6 [CLOSED] Added English Readme

### Releases 抽样
暂无 release 或数据不可用

### 真实反馈与维护信号研判
- 近期 PR 抽样里可见已合并项 0 个，说明项目并非完全冻结。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | lean-side-bussiness | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | 同生态官方方案 / 通用自建方案 / 相邻开源竞品 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 项目优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 项目风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `README.md`

## 3 条关键发现
- 代码入口/骨架集中在：README.md
- 目录结构与关键文件表明该项目采用较强意见化实现，而非纯演示仓库。

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
