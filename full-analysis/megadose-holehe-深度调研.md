# Holehe 深度调研（megadose/holehe）

> 调研日期：2026-08-14 ｜ 星标：12,332 ⭐ ｜ 语言：Python ｜ 协议：GPL-3.0 ｜ 默认分支：master ｜ 创建：2020-06-25

## 一、项目定位（一句话）

Holehe 是一个 **OSINT（开源情报）工具**：通过网站「忘记密码 / 注册 / 登录」接口的差异化响应，**被动侦查某个邮箱是否在 120+ 主流站点注册了账号**，且**不触发目标通知**。

## 二、项目亮点（差异化，开篇呈现）

- 🕵️ **被动侦查、不告警**：仅用公开接口的响应差异判断账号存在，**不会向目标邮箱发送任何通知**（见 issue #12），隐蔽性强。
- 🌐 **120+ 站点模块覆盖**：Twitter、Instagram、eBay、GitHub、Google、Discord、Patreon 等，是邮箱类 OSINT 覆盖最广的工具之一。
- ⚡ **Trio 异步并发**：基于 `trio` + `httpx`，百级站点数秒扫完（实测 121 站 ~10s）。
- 🔌 **多形态部署**：`pip3 install holehe`、Docker、或直接 `import` 为 Python 模块嵌入自有流水线。
- 📦 **标准输出结构**：每个模块返回统一字典 `{name, rateLimit, exists, emailrecovery, phoneNumber, others}`，便于程序化消费。

## 三、核心架构

仓库结构极薄：`holehe/core.py`（请求模板与判定辅助）+ `holehe/modules/`（每站点一个异步函数）+ `holehe/instruments.py`（进度条）+ `holehe/localuseragent.py`（随机 UA）。主流程用 `trio` 并发调度所有模块，结果收集进 `out` 列表。每个模块遵循统一签名 `async def <site>(email, client, out)`，根据站点支持的方式（`register` / `login` / `password recovery` / `other`）发送请求并解析 `exists`。

## 四、应用场景与启发

- **授权渗透测试 / 红队侦察**：枚举目标的数字身份攻击面（在哪些平台有账号）。
- **账号归集与欺诈检测**：验证某邮箱是否被滥用在未经授权的平台；社工防护自查。
- **持续监控流水线**：作为模块 `import` 进更大的安全框架或 OSINT 管线（已集成 Maltego 的 `holehe-maltego`）。
- 💡 **架构启发**：① 网站「注册 / 找回密码」接口对「已注册 / 未注册」的差异化响应，本身就是**信息泄露面**，应被产品侧收敛（统一返回）；② 「被动不告警 + 标准输出」是 OSINT 工具的良好设计范式，便于自动化编排。

## 五、源码深度解读

### 1. `holehe/core.py` —— 请求与判定核心
提供构造请求头、发送请求、根据响应判断 `exists` 的辅助函数。各模块复用它，只需关注「如何分辨该站点的已/未注册信号」。
```python
# 概念骨架
async def <site>(email, client, out):
    r = await client.get(url, headers=headers, data=payload)
    exists = parse(r)            # 站点特有：注册接口对已存在邮箱返回特定错误
    out.append({"name":"<site>","exists":exists, ...})
```

### 2. `holehe/modules/social_media/snapchat.py` —— 模块范例
用 `register` 接口探测：若邮箱已注册，响应会给出不同信号（如「该邮箱已存在」），模块据此置 `exists=True`。这是 120+ 模块的统一写法。

### 3. 主流程并发
`holehe` CLI 用 `trio` 把全部模块并发跑完，`instruments.py` 渲染进度条与彩色结果（`[+]` 已用 / `[-]` 未用 / `[x]` 限流 / `[!]` 错误）。

## 六、全网口碑

- OSINT 社区**经典常青工具**，10k+⭐，被 Sherlock 作者推荐、Maltego 官方集成（holehe-maltego）、多篇博客与教学视频引用。
- ⚠️ **维护状态**：最后一次 push 为 **2024-09**（维护放缓），部分站点因反爬/风控升级出现 rate-limit 或失效，作者 README 也提示「Rate limit? Change your IP」。
- 协议 GPL-3.0，明确「Built for educational purposes only」；属安全/渗透测试教育范畴。

## 七、竞品对比 + 核心研判

| 维度 | Holehe | Sherlock | Mosint | socialscan | SpiderFoot |
|---|---|---|---|---|---|
| 输入 | 邮箱 | 用户名 | 邮箱 | 邮箱(主动) | 域名/IP/邮箱 |
| 不告警 | ✅ | ✅ | ✅ | ❌(可能告警) | ✅ |
| 范围 | 账号注册 | 用户名占用 | 社交/泄露 | 多平台验证 | 广谱 OSINT |
| 维护 | 放缓 | 活跃 | 活跃 | 活跃 | 活跃 |

- **核心研判**：
  - ✅ 优势：被动不告警、覆盖广、易嵌入自有管线、GPL 自由。
  - ⚠️ 风险：**维护停滞**（2024 后基本冻结）、反爬导致漏报、处于**伦理/法律灰区**（必须用于授权场景）。
  - 🔮 趋势：OSINT 自动化已成熟，但「被动邮箱侦查」类工具依赖各站接口行为，长期需持续适配。
  - 💡 启发：仅限**授权渗透 / 自卫自查**使用；产品侧应统一「已/未注册」响应以消除此类泄露面。

## 八、关键文件路径速查

- `holehe/core.py`（请求与判定核心）
- `holehe/modules/`（120+ 站点模块，按 social_media / professional 等分类）
- `holehe/localuseragent.py` · `holehe/instruments.py`
- `setup.py` · `Dockerfile` · `LICENSE.md`（GPL-3.0）
