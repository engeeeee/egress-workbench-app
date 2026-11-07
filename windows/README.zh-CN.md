# Egress Workbench Windows 预览版 0.2.0

中文 Windows 客户端，提供代理导入、本机线路中转、出口核对、项目终端和持久化共享 Chromium。基于原项目的使用文档及 DMG 静态分析独立重建；未包含原版 macOS 程序和受保护模块。

## 下载与安装

在 [Windows 0.2.0 Release](https://github.com/engeeeee/egress-workbench-app/releases/tag/v0.2.0-windows) 下载：

- **推荐安装版**：`Egress-Workbench-Windows-x64-0.2.0-Setup.exe`，安装到当前用户目录，提供开始菜单和桌面快捷方式，无需管理员权限。
- **免安装版**：`Egress-Workbench-Windows-x64-0.2.0-Portable.zip`，完整解压后直接运行根目录的 `EgressWorkbench.exe`。同目录的 `_internal` 文件夹需要保留，命令行入口为 `ewb.exe`。

两个版本都无需另外安装 Python。使用现有 logo 的多尺寸图标，支持 Windows 任务栏图标、DPI 适配和同一数据目录的单实例启动。程序先显示界面，再在后台检测 Docker。

推荐 x64 Windows 11。先安装并启动 [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)，启用 WSL 2 后端并使用 Linux containers，需要 Docker Engine 28 或更新版本。客户端不会修改系统代理。

安装包尚未代码签名。升级时先停止环境并退出旧窗口；卸载只移除程序，不会主动删除项目、私有设置或 Docker 数据卷。免安装版在另一目录解压，仍使用同一默认数据目录。

## 本机线路 + SOCKS5 落地

适合已经运行线路客户端、只需要再套落地代理的场景：

```text
Claude Code / Codex / Chromium → 本机线路代理 → SOCKS5 落地 → 目标服务
```

1. 打开自己的线路客户端，确认它提供本机 HTTP 或 SOCKS5 监听，例如 `http://127.0.0.1:7890`。不需要启用“允许局域网”。
2. 在“连接与代理”中点击“添加代理”，选择 SOCKS5，填入远程落地地址、端口和可选的用户名、密码。
3. 勾选“通过本机代理连接落地”，填写线路客户端的本机监听地址。也可点击“读取系统代理”；此按钮只读取配置，不修改系统设置，不执行 PAC 脚本。
4. 保存设置并“检查连接”，核对测得的**落地出口 IP**、预计地区和时区，再“核对并确认”。

本机线路负责连接落地，最终出口由落地决定。速度取决于线路与落地之间的质量，不能保证任意线路都能加速。代理关闭或出口变化被检测后，环境停止，不会自动切回直连。纯 TUN、没有本机代理端口的客户端，无法使用此显式中转配置。

本机线路可填写 HTTP、HTTPS 或 SOCKS5 URI，只接受 loopback 地址。主机和容器通过 Docker 标准输入输出传输连接，不开放局域网监听端口。无需配置 `host.docker.internal` 或防火墙入站例外。

## 导入代理与节点

支持单条、批量文本、JSON、Clash `proxies` 和 Base64 列表，也可选择文件。常见代理格式：

```text
socks5://用户名:密码@落地服务器:1080#我的落地
http://用户名:密码@代理服务器:8080
https://用户名:密码@代理服务器:443
```

无认证时省略 `用户名:密码@`；用户名或密码含 `@`、`:` 等字符时，需要 URL 百分号编码。HTTPS 代理表示与代理服务器之间建立 TLS，要求有效证书；HTTP 代理也可以通过 CONNECT 访问 HTTPS 网站。

导入对话框提供明确的“代理链接 / JSON / Clash”和“HTTPS 订阅地址”两种模式，避免将 HTTPS 代理误当成订阅下载。订阅只在主动导入时获取，不保存订阅地址，不会后台定时刷新。

还支持 Trojan TCP/TLS、VLESS TCP/TLS、VMess AEAD TCP（可选 TLS）、Shadowsocks AEAD / 2022 TCP。节点域名在主机解析为 IPv4，保留 TLS SNI；只支持 IPv4 出口。不支持 WS、gRPC、Reality、XTLS、插件、自定义证书、跳过证书校验、uTLS 或给 SOCKS5 额外套 TLS。不支持的配置会报告原因。

JSON 接受 `outbound` 对象、对象数组或单个节点对象。可选的 `data` URL 不访问；`udp` 标志不会启用 UDP。导入后选中新代理；修改选中节点、线路或时区后，需要保存、重新检查并确认。

## 首次运行环境安装

打开“下载与安装”，确认 Docker 正常，然后点击“下载并安装 / 继续下载”。客户端从本版本 Release 获取预构建的 Linux x64 环境包，显示下载大小、速度、预计剩余时间，完成后校验 SHA-256 并导入 Docker。导入阶段显示独立状态，不将下载完成当作安装完成。

下载可暂停、关闭窗口后续传；网络中断保留 `.part`。服务器不支持续传时会重新下载，损坏文件会清除并提示重试。“下载运行环境时也使用本机线路”可让下载直接经过前置线路代理；首次安装无需先连通落地。先在“连接与代理”保存线路配置。

预构建包只导入指定镜像 ID，不覆盖现有镜像标签。已安装且配方匹配的镜像会继续保留。0.1.0 升级到 0.2.0 时更新网关，项目文件、工具账号、会话和浏览器数据保留；更新会停止环境，之后重新核对连接。

高级选项“从源码构建（较慢）”适合开发者或无预构建包的架构。会在线下载基础镜像和工具，详细输出位于数据目录 `build.log`。本机线路的下载开关仅用于预构建环境包；Docker 自己拉取基础镜像时使用 Docker Desktop 的网络配置。

## 开始工作

1. 导入并选择落地，配置可选本机线路。在“偏好设置”确认 IANA 时区。已有环境固定时区，其他时区请使用新的专用数据目录。
2. “检查连接”会停止本环境已有工作，测量两个来源的出口 IPv4，并测试直接访问公网是否被阻断。
3. 核对 IP、预计地区、时区后“核对并确认”。确认时再次测量，检查结果 5 分钟后过期。
4. 在“项目工作区”选择真实项目文件夹，启动 Claude Code、Codex 或 Linux 终端。工具直接修改项目，请使用版本管理。
5. 需要登录时点击“登录 Claude Code”或“登录 Codex”，在共享 Chromium 的远程画面内完成授权。工具与浏览器共享网络空间，支持 localhost OAuth 回调。

关闭远程显示网页会保留 Chromium。关闭主窗口后，已确认环境和独立监测进程继续运行；结束工作请点击“停止环境”或运行 `ewb stop`。停止会保留数据。

## 数据与网络

默认私有目录 `%LOCALAPPDATA%/EgressWorkbenchWindows` 保存节点密码、线路密码、设置、测量结果和日志；下载缓存位于其 `cache` 子目录。数据未使用系统凭据库加密，请仅在自己的账号下使用。CLI `--data` 可指定另一专用目录，路径暂不支持逗号和换行。

工具 home、授权与会话，以及单独的浏览器 profile 和下载目录保存在 Docker 数据卷。各项目绑定不同 `/workspace/<项目标识>`，工具账号在项目间共享。浏览器下载位于本实例的 `-downloads` 命名卷，可通过 Docker Desktop 的 Volumes 导出。真实项目保持在原目录。备份需同时保留私有目录、Docker 数据和项目文件。

工作区和浏览器位于仅有内部网络的 session 网络空间，经独立网关的 HTTP 代理访问所选落地。没有 TUN 驱动、主机 Docker socket 挂载或直连兜底；不支持 HTTP 代理的第三方工具可能无法联网。

独立进程周期性核对出口，发现连接失败、策略变化或出口改变会停止环境。网关许可失效后最多约 180 秒自行关闭代理；存在检测周期和网络超时，不能瞬间发现变化。地区是外部数据库估计，查询失败显示“未知”。

Chromium 为兼容 Docker Desktop 使用 `--no-sandbox`，没有启用浏览器自身沙箱；浏览器容器不挂载主机项目和工具账号卷。这是实验性环境，不代表原版全部安全机制，不保证匿名、隐藏容器特征或账号被服务商接受。没有原版 macOS 数据迁移、跨时区身份迁移、订阅定时刷新、闲置回收或完整中英文切换。

## 命令行与源码运行

打包版在程序目录使用 `ewb.exe`；源码版使用 `ewb.cmd`：

```powershell
C:\EgressWorkbench\ewb.exe doctor
C:\EgressWorkbench\ewb.exe install
C:\EgressWorkbench\ewb.exe import-node C:\private\nodes.txt
C:\EgressWorkbench\ewb.exe check
C:\EgressWorkbench\ewb.exe confirm
cd C:\Projects\MyProject
C:\EgressWorkbench\ewb.exe claude
C:\EgressWorkbench\ewb.exe codex exec "分析这个项目"
C:\EgressWorkbench\ewb.exe shell
C:\EgressWorkbench\ewb.exe browser
C:\EgressWorkbench\ewb.exe status
C:\EgressWorkbench\ewb.exe stop
```

动作前增加 `--data C:\EwbData\AnotherEnvironment` 可使用另一套环境。从源码安装镜像使用 `install --from-source`。

源码运行需要 Python 3.12 或更高版本，包含 Tcl/Tk 和 Python Launcher；双击 `windows/Start-Windows.cmd`，首次建立虚拟环境并安装依赖。原生 Linux x64 / ARM64 支持从源码构建容器，Windows 发布包目标为 x64。

在 x64 Windows 上安装 Inno Setup 6，然后运行 `windows/Build-Windows.ps1`，生成上述 Setup、Portable 和对应 SHA-256 文件。构建脚本使用 PyInstaller 共享运行库，GUI 和 CLI 共用 `_internal`。

```powershell
$env:PYTHONPATH = 'windows'
python -m unittest discover -s tests -v
python windows/smoke_gui.py
```

自动化覆盖 Windows / Linux 单元检查、真实 Windows GUI 与打包程序启动、安装卸载、原生 Linux x64 容器、双层代理和线路失效。尚未在真实 Windows 11 + Docker Desktop 桌面完成整套交互验收，也未使用真实 Anthropic / OpenAI 账号登录或请求模型。详见 [验证记录](../docs/windows-0.2-validation.zh-CN.md)。许可证见仓库 `LICENSE`；第三方说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
