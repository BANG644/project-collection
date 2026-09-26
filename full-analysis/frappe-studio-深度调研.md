# Frappe Studio — Frappe 框架的可视化应用构建器

> 调研日期：2026-09-27 ｜ 定位：拖拽式低代码 App Builder，产物即 Frappe 框架原生源码
> 数据源：gh api 真实抓取 README.md / studio/sync.py / studio/ 目录树 / frontend/src 目录树 / frontend/package.json

## 一、项目全景

| 项 | 值 |
|---|---|
| 仓库 | `frappe/studio`（默认分支 `develop`，注意非 `main`） |
| 星标 | 285 ⭐（早期项目，增长中） |
| 语言 | Vue（前端）+ Python（Frappe 后端） |
| 许可 | MIT |
| 阶段 | ⚠️ 极早期（breaking changes、功能不全、不建议生产） |
| 最后提交 | 2026-09-24 |

**一句话**：Frappe Studio 是 Frappe 生态的"可视化 App 构建器"——拖拽 frappe-ui 组件排版、连线 Frappe 数据源、写类 Vue `<script setup>` 页面脚本，还能用内置 AI 助手生成/修改页面；**导出的 app 就是框架原生源码，可 bench 部署生产**。

## 二、项目亮点

1. **产物即源码（核心价值）**：编辑器里的页面/组件以 JSON（结构）+ `.ts`（脚本）存盘，导出的 app 是标准 Frappe app，不锁死在私有格式。
2. **文件 ↔ 数据库双向同步**：`watch-studio` 监听磁盘上的 `studio/` 文件夹，把变更的 app/page/component JSON 导入 DB，AI/手写/CLI 改盘即所见即所得。
3. **原生接入 Frappe 数据层**：拖拽即可连线 DocType 数据源，复用 Frappe 全套权限/ORM，而非另起炉灶。
4. **内置 AI 助手**：OpenRouter API Key 驱动，生成并修改页面（设 Studio Settings 即可）。
5. **生产可构建**：`bench build-studio-app <app>` 产出由 Studio 自路由托管的标准 app。

## 三、核心架构

```
frappe/studio/
  frontend/            ← Vue3 + Vite + frappe-ui（App.vue / pages / components / stores / router）
    src/setupFrappeUIResource.ts, socket.js, main.ts
  studio/              ← Python 包（跑在 bench 内）
    api.py             ← REST/API 端点
    sync.py            ← 磁盘 JSON ↔ DB 同步（after_migrate 钩子）
    build.py           ← build_custom_apps（重建已发布 app）
    export.py          ← 导出标准 Frappe app
    watch.py           ← watch-studio 长驻监听
    ai/                ← AI 助手
    hooks.py, realtime.py, config/, templates/, www/
  pyproject.toml, package.json（前端 37 依赖：vue/frappe-ui/pinia/vue-router…）
```
**数据流**：编辑器(前端 Vite) ↔ `studio/` API ↔ Frappe DB；`watch-studio` 把磁盘 `<app>/studio_page/*.json+.ts` 经 `import_file_by_path` 灌入 DB。

## 四、源码深度解读

`studio/sync.py` 体现了"文件即真相源"的设计（节选）：
```python
def sync_studio_apps(app_name=None):
    apps = [app_name] if app_name else frappe.get_installed_apps()
    for app in apps:
        studio_folder = frappe.get_app_source_path(app, "studio")
        for studio_app in os.listdir(studio_folder):
            import_file_by_path(get_app_file_path(app_folder))  # app JSON → DB Doc
            sync_pages(app_folder)        # 每页 = <stem>.json + <stem>.ts
            sync_components(app_folder)   # studio_components/*.json

def after_migrate():          # bench migrate 后自动
    sync_studio_apps()
    remove_orphaned_apps_and_pages()   # 磁盘已删的 DB 记录清理
    build_custom_apps()
```
两个值得借鉴的点：
- **页面脚本活在 `.ts` 而非 DB**：`sync_pages` 把 `<stem>.ts` 直接存盘、运行时由 Vite 热加载，DB 的 `script` 字段留空——既保留"版本可控的源码"，又避免把可执行脚本塞进数据库。
- **孤儿清理对称**：`remove_orphaned_apps_and_pages` 类比 Frappe 的孤儿 DocType 清理，保证"文件删了 DB 也删"，避免漂移。

## 五、社区口碑

- 背靠 Frappe/ERPNext 成熟生态，定位"降低 Frappe 应用开发门槛"，目标用户是 Frappe 开发者。
- README 明确**早期警告**，demo 靠 YouTube 直播；社区期待高但生产可用性尚早。
- 与 Frappe 官博、ERPNext 用户群重叠，增长靠生态内口碑。

## 六、竞品对比

| 项目 | 定位 | 差异 |
|---|---|---|
| Appsmith / Budibase | 通用低代码内部工具 | 独立运行时、私有格式；Frappe Studio 产物是 Frappe 原生 app |
| Refly（已入库） | AI 原生应用构建 | 偏 AI 代理；Studio 偏表单/CRUD 可视化 |
| 其他 Frappe 低代码 | — | Studio 是官方首推可视化方案，深度集成 DocType |

## 七、核心研判

- **范式价值**："可视化编辑器产物 = 框架原生源码（JSON+TS），可导出、可 bench 部署、文件↔DB 双向同步"是 low-code 的正确方向——不绑架用户。比"黑盒运行时"更可持续。
- **对用户启发**：若你将来做"可视化搭东西又不想被平台锁死"的需求，Studio 的 `watch + import_file_by_path + 孤儿清理` 三件套是可复用的同步模式。
- **风险**：极早期、breaking changes 频繁、仅 Frappe 生态内可用；生产前等稳定版。

## 八、关键文件路径速查

| 路径 | 作用 |
|---|---|
| `studio/sync.py` | 磁盘 studio/ JSON ↔ DB 同步 + 孤儿清理 |
| `studio/build.py` | `build_custom_apps` 重建已发布 app |
| `studio/export.py` | 导出标准 Frappe app 源码 |
| `studio/watch.py` | `watch-studio` 长驻监听 |
| `studio/api.py` | REST 端点 |
| `frontend/src/App.vue` | 编辑器主壳 |
| `frontend/src/setupFrappeUIResource.ts` | frappe-ui 资源注入 |
