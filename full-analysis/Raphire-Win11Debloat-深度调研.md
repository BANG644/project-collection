Raphire/Win11Debloat 全方位深度调研报告调研日期：2026-06-13 | 数据来源：GitHub API + README📦 项目概览属性值仓库Raphire/Win11DebloatStars⭐ 47,488Forks1,908语言PowerShell许可证MIT创建时间2020-10-27最后更新2026-06-12最新版本2026.06.11一句话定位：轻量级 PowerShell 脚本，一键去除 Windows 预装应用、禁用遥测、优化系统体验的开源工具。📖 核心功能详解1. 应用移除（App Removal）移除大量预装应用（支持完整列表详见 Wiki）支持保留特定应用移除的应用可通过 Microsoft Store 恢复2. 隐私与建议内容（Privacy & Suggested Content）禁用遥测、诊断数据、活动历史、应用启动跟踪和定向广告禁用 Windows 中的提示、技巧、建议和广告禁用 Windows 定位服务和应用定位权限禁用"查找我的设备"位置追踪禁用锁屏"Windows 聚焦"和提示禁用桌面背景"Windows 聚焦"选项禁用 Microsoft Edge 中的广告、建议和 MSN 新闻源隐藏设置"主页"中的 Microsoft 365 广告3. AI 功能控制（AI Features）禁用并移除 Microsoft Copilot禁用 Windows Recall（时间线回滚）禁用 Click to Do（AI 文本和图像分析工具）防止 AI 服务（WSAIFabricSvc）自动启动禁用 Edge 中的 AI 功能禁用画图中的 AI 功能禁用记事本中的 AI 功能4. 系统优化（System）禁用文件拖拽共享托盘恢复 Windows 10 经典右键菜单关闭鼠标加速（增强指针精确度）禁用粘滞键快捷键禁用存储感知自动磁盘清理禁用快速启动（确保完全关机）禁用 BitLocker 自动设备加密禁用现代待机（Modern Standby）网络连接以降低耗电5. Windows 更新控制阻止 Windows 立即获取更新登录后禁止自动重启禁用更新共享（传递优化）6. 外观定制（Appearance）开启深色模式禁用透明效果禁用动画和视觉效果7. 开始菜单和搜索移除或替换开始菜单固定应用隐藏推荐部分隐藏"所有应用"部分禁用手机链接集成禁用 Bing 网页搜索和 Copilot 搜索集成禁用 Microsoft Store 应用建议禁用搜索高亮8. 任务栏优化图标左对齐隐藏或更改搜索图标隐藏任务视图按钮禁用小部件隐藏聊天图标启用"结束任务"右键选项启用"上次活动点击"行为多显示器任务栏图标控制9. 文件资源管理器优化更改默认打开位置显示已知文件类型扩展名显示隐藏文件隐藏主页或图库导航移除重复的可移动驱动器10. 高级功能（Advanced）支持应用到其他用户（非当前登录用户）Sysprep 模式：应用到 Windows 默认用户配置文件，使新用户自动继承更改🏗️ 架构分析核心架构Win11Debloat/├── Win11Debloat.ps1    # 主脚本（核心逻辑）├── Run.bat             # 便捷启动批处理├── Assets/             # 资源文件│   └── Images/         # 截图├── .github/            # GitHub 配置├── LICENSE             # MIT 许可证└── 
- `README.md`           # 完整文档执行流程启动方式：支持 PowerShell 一行命令、双击 Run.bat、手动执行三种方式管理员权限：需要以管理员身份运行交互式菜单：提供 GUI 风格菜单，用户可勾选需要执行的操作命令行参数：支持参数化执行（静默模式、自定义配置）完全可逆：所有更改均可还原，应用可通过 Microsoft Store 恢复技术特点纯 PowerShell 实现：无外部依赖，Windows 自带即可运行模块化设计：每个功能独立可开关可逆操作：执行前备份注册表和应用列表错误处理：完善的异常捕获和恢复机制📈 社区口碑积极评价简单易用：一行命令即可完成，无需技术背景功能全面：覆盖从预装应用到系统设置的 100+ 优化项持续更新：紧跟 Windows 更新，及时适配新版本开源透明：MIT 许可证，所有代码可审计安全可靠：所有更改均可还原，不会损坏系统负面反馈功能过多：部分用户认为选项过多，初次使用不知所措过于激进：某些优化（如禁用 Copilot）可能影响后续 Windows 功能更新兼容性问题：少数情况下导致 Windows 更新失败🔄 竞品对比特性Win11DebloatChrisTitusTech/winutilO&O ShutUp10++PrivateWin10开源✅ MIT✅ 开源❌ 闭源✅ 部分开源Stars47.4K50K+N/AN/A平台Windows 10/11Windows 10/11Windows 10/11Windows 10/11技术栈PowerShellPowerShell原生应用原生应用功能数量100+200+300+150+一键执行✅✅✅✅交互菜单✅✅✅✅可逆操作✅✅✅✅命令行支持✅✅❌❌更新频率月更新月更新季度更新不定期中文支持❌❌✅❌

## 🎯 核心研判

项目价值Windows 生态刚需：随着 Windows 11 预装应用和 AI 功能增多，去臃肿需求持续增长隐私保护工具：系统级的遥测和广告禁用功能，满足隐私敏感用户需求企业部署辅助：Sysprep 模式和命令行参数使其适合企业批量部署竞争力分析Stars 增长迅速：2020-2026 年间从 0 增长到 47.4K，增速持续社区活跃度高：Discussions 和 Issues 活跃，贡献者众多与 Windows 版本高度绑定：每次 Windows 大版本更新都需要适配潜在

### 风险

Windows 更新兼容性：微软可能通过更新破坏脚本功能Copilot 等 AI 功能的深度绑定：微软可能将 Copilot 与系统核心功能耦合法律

### 风险

：部分地区对禁用遥测有法律限制使用建议普通用户：使用交互式菜单，按需选择优化项高级用户：使用命令行参数实现自动化部署企业 IT：利用 Sysprep 模式实现批量部署优化🔑 关键文件路径路径说明Win11Debloat.ps1主脚本（核心逻辑）Run.bat便捷启动入口Wiki/在线文档（GitHub Wiki）Assets/Images/界面截图📌 总结Win11Debloat 是 Windows 去臃肿领域的标杆级开源项目（47.4K Stars），以纯 PowerShell 脚本实现 100+ 系统优化功能，覆盖应用移除、隐私保护、AI 功能禁用、系统性能优化等全场景。其最大

### 优势

在于简单易用（一行命令即可）和完全可逆（所有更改可还原）。随着 Windows 11 预装应用和 AI 功能不断增加，该项目在可预见的未来仍将保持强劲需求。
