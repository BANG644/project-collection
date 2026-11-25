# 🔬 ace-trump-tech/DeltaForce-OBS-Locker - 全方位深度调研（安全风险视角）

- GitHub: https://github.com/ace-trump-tech/DeltaForce-OBS-Locker
- 调研日期: 2026-11-26 | Stars: 1,798 | 语言: Python | 许可: **无（license=null）**
- 仓库创建: 2026-06-14 | 最后推送: 2026-11-04 | 默认分支: main | 仓库体积: ~20MB

> ⚠️ **本报告为安全风险研判，不构成任何使用/传播建议。** 调研全程只做静态代码与元数据阅读，**未执行仓库内任何二进制文件、未运行任何脚本**。项目自称游戏作弊工具，本报告仅把它当作「可疑仓库样本」分析其真实实现与社工话术，帮助读者识别同类风险。

## 📌 一句话定位

这是一个**打着「三角洲行动 OBS 锁头/自瞄/稳定过检」旗号、实则为诱导 Star→Fork→Download 并引导安装某款游戏客户端的社工/引流仓库**——README 用 YOLO、骨骼识别、反作弊对抗等高热词包装，但源码核心全是「教学占位」空壳，作者本人在描述里用 base64 藏了一句自白：**「但其实以上全是骗你的，这只是个帮你安装暗区突围的反作弊项目罢了」**。

## ⭐ 项目亮点（作为「风险样本」的研判价值）

- **亮点 1 — 宣传与实现脱节的教科书级样本**：README 宣称「锁头/自瞄/压枪抑制/稳定过检」，实际 `fake_plugin.py` 类名就叫 `FakeLockhead`，`get_target_position()` 永远返回 `None`，注释明写 "does nothing except print a warning"。
- **亮点 2 — 作者自白藏在一行 base64 里**：仓库 description 尾部与 README 教程中反复出现的 `5L2G5YW25...` 串，解码后是作者承认「全是骗你的，只是帮你安装暗区突围的反作弊项目」——这是识别钓鱼仓库的决定性证据。
- **亮点 3 — 完整的「Star→Fork→Download」社工漏斗**：README 把「点 Star 申请使用权限」「Fork 才能修改」「下载 ZIP」写成三步硬性流程，配合「Star 解锁权限」的稀缺性话术，是典型的 GitHub 涨星诱导模式。
- **亮点 4 — 提权 + 不透明二进制组合**：`main.py` 启动即 `run_as_admin()` 请求 UAC 管理员权限，`data/bin/Lockhead.exe` 为无源码的 Windows 可执行文件，弹窗文案从 base64 编码的 `.bin` 文件读取，全程对使用者不透明。
- **亮点 5 — Issue 区「托儿」与质疑并存**：既有「真能用」「巅峰108星」等疑似刷量好评，也有 #31「这个项目是空壳吗」、#19 直接贴出 base64 解码命令的质疑，社区自身已分裂。

## 🏗️ 项目架构全景

### 目录结构与真实实现分布

```
Readme.md / README.md       宣传主文档（S11赛季、V5.0.0、钓鱼模块等话术）
Desktop/                    电脑端
  main.py                   入口：请求 UAC 管理员权限 → 读 YAML → 弹 Tk 对话框
  config.yaml               伪装配置（plugin_name / 弹窗文案 / 下载目录）
  core/
    fake_plugin.py          ⚠️ 空壳：FakeLockhead，get_target_position() 恒返回 None
    registry.py             ⚠️ 空壳：write_fake_registry() = pass
    downloader.py           实际行为：webbrowser.open() 打开游戏官网
    fish_anti_detect.py     自动钓鱼「反检测」类（人类化时序/指纹轮换，均为占位）
    fish_detector.py        YOLO 鱼种识别类（含随机/占位逻辑）
    fish_input.py           输入模拟类（activate 里仅 self._active=True，注释「教学占位实现」）
  data/
    bin/Lockhead.exe        ⚠️ 无源码二进制安装器（由 launcher.py 提权后 Popen 启动）
    bin/launcher.py         ctypes 提权 + 启动 exe
    crypto.py               从 msg_ok.bin / msg_warn.bin 读取 base64 文案
    msg_ok.bin/msg_warn.bin base64 编码的提示语（解码即「骗你的」）
  models/weights/           仅 .gitkeep，权重需外链下载（yolo-omni）
Mobile/                     手机端 APK 下载脚本 + 演示图/视频
third_party/yolo-omni       git submodule 外链
```

### 技术栈与工程判断

- **表层技术栈**：Python + Tkinter（弹窗）+ PyYAML（配置）+ NumPy/YOLO（占位模块）+ ctypes（Windows 提权）。
- **真实技术含量**：几乎为零。核心"作弊逻辑"全部是 stub；唯一有实际行为的代码路径是「提权 → 弹窗 → 打开游戏官网 / 启动 Lockhead.exe」。
- **许可证缺失**：`license=null`，既无授权声明也无免责边界，传播与使用都存在法律不确定性。

## 💡 应用场景与启发（重点章节）

### 这个仓库能用在哪

**结论：除了作为「安全风险识别的教学样本」，没有任何正当使用场景。** 它不适合：
- 生产/个人使用（无真实功能，且要求管理员权限 + 执行不透明二进制）；
- 二次开发学习（占位代码无架构价值，README 教程指向站外引流博客）；
- 安全研究之外的技术参考（无 LICENSE、无测试、无 CI）。

### 给同类需求带来的解决思路（如何识别这类钓鱼仓库）

1. **基数解码体检**：遇到 README/description 里成串的 base64、hex、长串"教程链接"，先解码再看——本项目作者的自白就藏在 description 尾部一行里。
2. **宣传-实现对照表**：把 README 的每个能力声明（锁头/过检/压枪）映射到具体源码函数；映射不上或命中 `Fake*`、`pass`、`return None`、`占位实现` 的，判定为空壳。
3. **Star/Fork 门槛红旗**：正常开源项目不会把「Star 申请权限」「Fork 才能使用」写成硬性步骤——这是涨星/引流的强信号。
4. **提权 + 二进制 + 外链下载三件套**：`run_as_admin()` + 无源码 `.exe` + "去外站下载权重/客户端"同时出现时，默认按恶意软件处理，绝不实机运行。
5. **Issue 区信号挖掘**：刷量好评（"真能用""感谢开源"，标 `good first issue`）与质疑（"空壳吗"）并存、且维护者用标签戏谑回应时，可信度极低。

### 可复用片段（安全分析视角）

- 一条可直接复用的仓库体检命令：`gh api repos/{owner}/{repo} --jq '.description, .license, .size'` + 对可疑串 `echo <串> | base64 -d`；再看 `contents/` 树里是否存在 `Fake*`、`pass`、占位注释。

## 🧠 核心源码解读（克制代码量）

### 入口与主流程（`Desktop/main.py`）

整个程序真实只有一条可执行链路，且第一步就是提权：

```python
from data.bin.launcher import run_as_admin, run_installer
from data.crypto import get_ok_message, get_warn_message

def main():
    run_as_admin()                       # ← 启动即请求 UAC 管理员权限
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)       # ← 读取伪装弹窗文案
    root = tk.Tk(); root.withdraw()      # ← 隐藏主窗口，只留对话框
    # 随后弹出 base64 编码的确认框，点击后走 run_installer() → 启动 Lockhead.exe
```

**判断**：一个"锁头辅助"没有任何理由在启动瞬间索要管理员权限；这一步暴露其真实目标是安装/执行本机程序，而非游戏内视觉处理。

### 假作弊模块（`Desktop/core/fake_plugin.py`）

```python
class FakeLockhead:
    def __init__(self):
        self.enabled = False
        print("[DeltaForce Plugin] 警告：外挂插件已被安全模块拦截，请勿使用非法软件。")
    def get_target_position(self):
        return None                      # ← 永远没有"锁头坐标"
```

同类还有 `utils/registry.py` 的 `write_fake_registry(): pass`。**这些不是"被安全模块拦截"，而是作者从未实现作弊能力。** README 把 stub 包装成"教学与原理验证"，是典型的责任规避话术。

### 安装器启动逻辑（`Desktop/data/bin/launcher.py`）

```python
def run_as_admin():
    if is_admin(): return
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()                           # ← 用 runas 动词静默重启自身提权

def run_installer():
    run_as_admin()
    exe_path = os.path.join(os.path.dirname(__file__), "Lockhead.exe")
    subprocess.Popen([exe_path], shell=True)   # ← 启动无源码二进制
```

`Lockhead.exe` 无哈希、无签名说明、无源码，配合提权与 `shell=True`，构成完整的高危执行链。**本报告未执行该文件。**

## 📐 架构决策与设计哲学

- **不是"技术取舍"，而是"欺骗设计"**：所有看似架构的选择（占位模块 / 外链权重 / base64 文案 / 提权安装器）都服务于一个目标——让用户完成 Star-Fork-Download 漏斗并在本机运行不明程序。
- **责任规避**：README 反复用"技术教学与原理验证为目的"，配合无 LICENSE，一旦出事可推诿。
- **版本演进**：commit 历史几乎全是 `Update Readme.md`（2026-08 至 11 月反复更新文案与赛季热词），**几乎没有功能性代码提交**——进一步佐证这是文案运营而非软件项目。

## 🌐 全网口碑画像

> 说明：本项目无可靠第三方长评（一个作弊引流仓库不会有正规评测）。以下均为可核验的一手/社区信号，附来源。

- **作者自白（决定性）**：仓库 description 与 README 内 base64 串 `5L2G5YW25...` 解码为「但其实以上全是骗你的，这只是个帮你安装暗区突围的反作弊项目罢了」（来源：GitHub repo description，Issue #19 亦贴出解码命令）。
- **弹窗文案解码**：`msg_ok.bin` 解码为「恭喜你学会了配置 python 环境，但是很抱歉，我骗你的，想玩暗区突围吧」（来源：`Desktop/data/crypto.py` + `.bin` 文件静态读取）。
- **社区质疑**：Issue #31 标题即「这个项目是空壳吗，具体代码要自己去实现？」；#19 直接给出 base64 解码命令（来源：GitHub Issues）。
- **疑似刷量好评**：#40「我靠 真能用 大佬牛逼」、#28「三角洲巅峰108星了」、#36「好用，这宝藏我咋才发现」等，多被标记为 `good first issue`；#42「一群乐子人」（来源：GitHub Issues）。
- **维护者态度**：多个 issue 被以 `invalid`/`duplicate` 或戏谑标签关闭，无实质技术答疑（来源：GitHub Issues 标签分布）。

**口碑结论**：真实用户评价两极且高度可疑，缺乏任何可信第三方背书；所有"能用"的声称与源码 stub 直接矛盾。

## ⚔️ 竞品对比（同类"可疑仓库" vs 正常项目）

| 维度 | 本仓库 | 正常游戏辅助/视觉开源项目 | 正常 YOLO 视觉项目（如 ultralytics） |
|---|---|---|---|
| 核心实现 | stub（`Fake*`/`pass`/`None`） | 有可运行逻辑与测试 | 完整源码 + 测试 + benchmark |
| 许可证 | 无 | 通常 MIT/Apache/GPL | AGPL 等明确 |
| 安装方式 | 提权 + 无源码 exe + 外链 | 常规安装/构建 | pip/conda 标准分发 |
| 获取门槛 | Star+Fork+Download 三步 | 直接 clone | 直接 clone |
| 文案风格 | 赛季热词+base64 隐藏自白 | 技术描述 | 技术文档 |
| 可信度 | 极低 | 中—高 | 高 |

**选择建议**：任何以"锁头/过检/免费外挂"为卖点、要求 Star 解锁、要求提权运行不明二进制的仓库，都不要下载、不要运行、不要传播。真正的视觉/自动化学习请选有 LICENSE、有源码、有测试的正规项目。

## 🎯 核心研判

### 项目优势（作为风险样本）
1. 罕见地完整保留了"钓鱼仓库"的全套证据链（base64 自白 + stub 源码 + 提权器 + 社工 README），是安全教育的优质反面教材。

### 项目风险（对使用者）
1. **功能欺诈**：宣传的作弊能力全部不存在，下载者只会得到一个空壳。
2. **本机安全**：要求管理员权限并执行无源码 `Lockhead.exe`，存在恶意软件/后门风险（本报告未验证二进制内容，属"未验证高风险"）。
3. **社工操纵**：Star→Fork 门槛利用用户行为获利，base64 隐藏文案规避审查。
4. **法律与合规**：无 LICENSE、涉游戏作弊与反作弊对抗话题，传播和使用均有风险。

### 适用场景 & 不适用场景
- ✅ 适用：安全意识教育、"如何识别钓鱼仓库"的培训样本、GitHub 内容治理研究。
- ❌ 不适用：任何实际使用、二次开发、当作 YOLO/视觉技术参考。

### 趋势判断
仓库创建于 2026-06，靠"赛季更新"文案反复激活（commit 多为改 README），Issue 区仍有人被引流。属**长期运营的社工/引流项目**，非技术项目；随时间只会持续换赛季话术，无技术演进价值。

## 📂 关键文件路径速查

| 路径 | 研判价值 |
|---|---|
| `description` / `Readme.md` 尾部 base64 串 | 作者"全是骗你的"自白（决定性证据） |
| `Desktop/core/fake_plugin.py` | FakeLockhead，`get_target_position()` 恒返回 None |
| `Desktop/utils/registry.py` | `write_fake_registry(): pass` 空壳 |
| `Desktop/core/downloader.py` | 实际行为是 `webbrowser.open()` 打开游戏官网 |
| `Desktop/main.py` | 启动即 `run_as_admin()` 请求 UAC |
| `Desktop/data/bin/launcher.py` | `runas` 提权 + `Popen(Lockhead.exe, shell=True)` |
| `Desktop/data/msg_{ok,warn}.bin` + `crypto.py` | base64 隐藏文案（解码即"骗你的"） |
| `Desktop/core/fish_*.py` | 自动钓鱼模块，注释"教学占位实现" |
| `Desktop/models/weights/` | 仅 `.gitkeep`，权重需外链（引流的一环） |
| Issue #31 / #19 | 社区"空壳吗"质疑 / base64 解码命令 |

## ⭐ 三条关键发现

1. **这是钓鱼/引流仓库，不是作弊工具**：作者 description 里的 base64 自白与 `msg_ok.bin` 解码文案双重确认"全是骗你的，只想让你装暗区突围"。
2. **源码与宣传零对应**：核心"作弊"模块全是 `Fake*`/`pass`/`None` stub，唯一真实行为是提权 + 打开游戏官网 / 启动不明 exe。
3. **识别方法可复用**：base64 解码 + 宣传-实现对照 + Star/Fork 门槛 + 提权二进制三件套，是一套可迁移到任意可疑仓库的体检流程。

## 🧪 研究方法与数据来源

- 静态阅读 GitHub 仓库元数据、文件树、`Readme.md`、`Desktop/` 下 7 个源码文件（本报告全程未执行任何代码/二进制）。
- 解码 description base64 串与 `msg_ok.bin`/`msg_warn.bin` 内容。
- GitHub Issues（#19/#31/#40 等）标签与标题分布。
- commit 历史（`gh api repos/.../commits`）验证"只改 README 不改代码"。
- 无可靠第三方长评时明确标注，不编造口碑。
