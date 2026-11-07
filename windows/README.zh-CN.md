# Egress Workbench Windows 预览版 0.1.0

面向 Windows 的独立主机实现，提供中文桌面界面、节点导入、出口核对、项目终端和持久化共享 Chromium。基于原项目的使用文档及 DMG 静态分析重建；原版 macOS 程序和受保护 Python 模块未包含在此版本中。

## 启动

推荐使用 x64 Windows 11。安装并启动 [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)，启用 WSL 2 后端并使用 Linux containers，需要 Docker Engine 28 或更新版本。

如果使用已打包的 Windows ZIP：解压整个 ZIP，运行 `EgressWorkbench/EgressWorkbench.exe`。请保留旁边的 `_internal` 文件夹。命令行入口为 `ewb/ewb.exe`。

如果使用源码 ZIP：安装 [Python 3.12 或更高版本](https://www.python.org/downloads/windows/)，保留安装器默认的 Tcl/Tk 和 Python Launcher 组件。双击 `Start-Windows.cmd`；首次启动会建立 Python 虚拟环境并安装 PyYAML、tzdata。之后也可直接运行 `.venv/Scripts/pythonw.exe entry.py`。

## 首次使用

1. 在“连接”页点击“检查 Docker”，然后“安装运行环境”。首次构建下载 Linux 镜像、Claude Code、Codex 和 Chromium，需要网络与磁盘空间。详细输出写入数据目录的 `build.log`。
2. 点击“导入节点 / 订阅”，粘贴 HTTPS 订阅地址、URI、JSON 或 Clash `proxies`，也可选择文件。订阅只在主动导入时下载，不保存订阅地址，也不会后台自动刷新。
3. 选择节点，并在“设置”中确认 IANA 时区。已有环境的时区固定，其他时区请使用新的专用数据目录。
4. 点击“检查所选连接”。这会停止本环境已有工作，测量两个来源的出口 IP，并测试直连是否被阻断。
5. 核对 IP、估计地区和配置时区，再点击“核对并确认”。确认前会再次测量出口；检查结果在 5 分钟后过期。
6. 在“工作区”选择具体项目文件夹，打开 Claude Code、Codex 或 Linux Shell。工具直接修改真实项目文件，请使用正常版本管理。
7. 首次使用可点击“登录 Claude Code”或“登录 Codex”。授权链接交给共享 Chromium；在打开的远程画面内完成登录。工具与浏览器共享 Linux 网络空间，支持 localhost OAuth 回调。

关闭远程显示网页不会关闭 Chromium。关闭桌面界面后，独立连接监测进程继续运行；要停止工具、浏览器与网关，请先点击“停止整个环境”，或运行 `ewb stop`。停止会保留项目文件、账号、会话与浏览器配置。

## 支持范围

支持原生 x64 或 ARM64 Linux 容器；Windows 可执行文件的自动构建目标为 x64。主机应用不需要 macOS 安装包。

节点支持范围：Trojan TCP/TLS、VLESS TCP/TLS、VMess AEAD TCP（可选 TLS）、Shadowsocks AEAD / 2022 TCP。节点域名在主机上解析为 IPv4，保留 TLS SNI；只支持 IPv4 出口。不支持 WS、gRPC、Reality、XTLS、插件、自定义证书、证书跳过校验和 uTLS 指纹配置。无法支持的节点会被跳过并报告原因，不会转换为其他传输。

JSON 可使用原节点的 `outbound` 对象、节点对象数组，或单个 `{type, host, port, password}` Trojan 客户端对象。可选的 `data` URL 不会访问；`udp` 标志不会启用 UDP。

## 网络和数据

工作区与浏览器加入仅有内部网络的 session 容器网络空间，通过双网络网关的 HTTP 代理访问所选节点。没有系统代理修改、TUN 驱动或主机 Docker socket 挂载。未配置代理的第三方工具可能无法联网，需要其自身支持 HTTP 代理。

确认连接后，独立进程周期性核对出口；发现失败、配置变化或 IP 改变会停止本环境。网关还检查短期许可，主机不再续期时最多约 180 秒后自行关闭代理。检测存在周期及网络超时，不能瞬间发现出口变化。IP 地区是外部数据库估计值；地区查询失败时显示“未知”，不会伪造成功。

默认私有数据目录为 `%LOCALAPPDATA%/EgressWorkbenchWindows`，保存节点密码、设置、测量结果和日志。CLI 的 `--data` 可指定其他专用目录；路径暂不支持逗号和换行。各安装实例使用独立 Docker 资源标识。

Docker 数据卷保存工具的共享 home、账号与按项目路径组织的会话，以及单独的浏览器 profile 和下载目录。每个项目绑定到不同的 `/workspace/<项目标识>`。此版工具 home 由项目共享，不提供项目之间的账号隔离。下载保存在本实例的 `-downloads` 命名卷中；可通过 Docker Desktop 的 Volumes 页面导出。

停止或重新检查连接不会删除卷或项目容器，保留容器可写层。Docker 数据盘与上述私有目录需要分别备份。本预览版不提供原版 macOS 数据迁移、跨版本容器升级、订阅定时刷新、30 分钟闲置回收或原版完整中英文切换。

Chromium 在受限的独立容器中以普通用户运行；为兼容 Docker Desktop，本预览版使用 `--no-sandbox`，没有启用 Chromium 自身的沙箱。浏览器不挂载主机项目目录或工具账号卷。请将它视为实验性环境，不代表与原版安全机制等价，也不保证匿名、隐藏全部容器特征或账号被服务商接受。

## 命令行

在源码目录外可以使用 `ewb.cmd` 的完整路径；打包版本将其替换为 `ewb.exe`：

```powershell
C:\ewb\ewb.cmd doctor
C:\ewb\ewb.cmd install
C:\ewb\ewb.cmd import-node C:\private\nodes.txt
C:\ewb\ewb.cmd check
C:\ewb\ewb.cmd confirm

cd C:\Projects\MyProject
C:\ewb\ewb.cmd claude
C:\ewb\ewb.cmd codex exec "分析这个项目"
C:\ewb\ewb.cmd shell
C:\ewb\ewb.cmd exec python3 --version
C:\ewb\ewb.cmd browser
C:\ewb\ewb.cmd status
C:\ewb\ewb.cmd stop
```

需要另一套环境时，在动作前增加 `--data C:\EwbData\AnotherEnvironment`。使用源代码也可运行 `python entry.py --data ...`。

## 生成 Windows 可执行文件

在 Windows PowerShell 中运行：

```powershell
Set-Location C:\path\to\repository\windows
.\Build-Windows.ps1
```

输出为 `dist/Egress-Workbench-Windows-x64-0.1.0.zip`，包括图形程序和命令行程序。构建脚本需要在 x64 Python / Windows 中执行；没有代码签名。GitHub Actions 的 `Windows preview` 工作流自动运行 Windows / Linux 单元检查、Windows 界面启动检查，并在 Windows runner 上打包。

首次容器安装是在线构建，ZIP 不含约 1 GB 的 macOS 离线镜像，不会导入或覆盖原版资源。源代码测试命令：

```powershell
$env:PYTHONPATH = 'windows'
python -m unittest discover -s tests -v
python windows/smoke_gui.py
```

## 验证边界

发布前需要分别核对：Windows 宿主检查与打包、真实 Docker 容器构建/启动、无直连与网关许可失效、浏览器显示、真实账号交互登录。自动构建和静态测试不能替代全部实际账号或各订阅提供商的兼容性测试。具体验证结果见本分支交付记录，不将尚未完成的检查视为通过。

许可证见仓库 `LICENSE`；第三方组件说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
