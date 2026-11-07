# Egress Workbench 0.3.3：DMG 静态分析与 Windows 适配评估

分析日期：2026-11-07。

已完成 DMG 解包、文件完整性核对、原生模块常量解析及镜像历史层检查。已恢复模块清单、函数元数据、配置常量和部分前端/构建文件；尚未恢复原生函数实现，也尚未产出可运行的 Windows 版本。

## 分析对象与完整性

对象为上游 [v0.3.3 Release](https://github.com/bbfp/egress-workbench-app/releases/tag/v0.3.3) 的 `Egress-Workbench-0.3.3-arm64.dmg`，大小为 1,149,144,881 字节。

DMG 的 SHA-256 与公开校验值一致：

```text
0e2efab0f7110aa71032c5b27e741b755da897328267ff57f3a19a91a6a9598d
```

包内 `Contents/Info.plist` 标记应用版本为 0.3.3、构建号 20，最低系统为 macOS 14。离线环境清单标记运行环境版本为 0.1.12。

校验结果：

- `build-manifest.json` 中的 254 个 Source 文件哈希全部匹配。
- 各模块清单中 34 个原生编译文件的哈希全部匹配。
- 离线清单中 89 个容器构建输入文件的哈希全部匹配。
- `images.tar.gz` 的 SHA-256 为 `97be84fd50d5ec52067baeb94ac6001f01d87ff762fe4e38582349aaaca10e83`，与清单一致。

本次没有运行应用、导入 Docker 镜像、连接订阅节点或执行账号登录。

## 安装包实际包含什么

| 部分 | 观察到的实现 | 对 Windows 的影响 |
| --- | --- | --- |
| 桌面界面 | `MacOS/EgressWorkbench`，ARM64 Mach-O，链接 SwiftUI / AppKit | 需要实现 Windows 界面 |
| 主机控制层 | `_ewb_host.cpython-312-darwin.so`，一个文件包含 54 个业务模块 | 核心实现为 macOS 原生机器码，需要恢复行为并重写主机层 |
| 桌面控制器 | `desktop/Controller/ewb-controller`，Nuitka standalone Mach-O，附带 `libpython3.12.dylib` | 需要 Windows 控制器或跨平台后端 |
| 闲置回收 | 3 个 macOS CPython 3.12 原生扩展，使用 launchd | 需要替换后台任务、进程和锁机制 |
| 工作区与浏览器组件 | 18 个 Linux ARM64、glibc、CPython 3.11 原生扩展 | 可研究 ARM64 容器内复用；原生 x64 需要重新实现或获得源码重编译 |
| 网关组件 | 12 个 Linux ARM64、musl、CPython 3.12 原生扩展 | 同时受 CPU 架构和 Python ABI 约束 |
| 离线镜像 | gateway / work / browser 三张镜像，全部为 `linux/arm64` | 普通 x64 Windows 需要评估仿真，或准备 amd64 实现 |
| 浏览器显示页面 | HTML、JavaScript、noVNC、WebSocket 中继 | 文本资源可提取；中继中的进程管理与环境变量需要 Windows 适配 |
| 构建与配置资料 | Dockerfile、依赖锁、seccomp、示例节点配置、中文消息表 | 可作为重建依据 |

包内 `Source/protection.json` 声明编译器为 Nuitka 4.3.3、自有模块总数为 87。它们对应 54 个主机模块、18 个 guest 模块、12 个 gateway 模块和 3 个闲置回收模块。

`Source` 下有 87 个大小完全相同的 134 字节 Python 文件，内容是加载对应原生扩展后调用 `_ewb_entry()`。目录名为 Source，并不表示这些业务实现以 Python 源码形式保留。

## 已恢复的接口资料

新增 [静态解析工具](../tools/inspect_nuitka.py)，按 Nuitka 4.3.3 的公开常量格式解析二进制数据，不导入或执行目标模块。对 34 个清单列出的原生编译文件均已成功完成解析。

提取结果合计为 1,022 条代码元数据记录：799 条函数记录、22 条类记录、109 条生成器表达式记录，以及 92 条模块记录。这些数量包含加载入口和编译辅助代码，不等于 799 个独立产品功能。

输出可保留函数名、原始行号、参数数量、变量名、关键字参数信息、字符串和结构化常量。函数默认值和控制流不能仅靠这些元数据完整还原。

例如，主机模块中能够识别：

```text
runtime.ensure_gateway(verify)
runtime.ensure_project(path)
runtime.execute(project, args, interactive, user)
runtime.stop_all()

desktop.controller.import_nodes(request)
desktop.controller.probe_node(request)
desktop.controller.confirm_setup(request)
desktop.controller.launch_terminal(request)
desktop.controller.status()
desktop.controller.work(action, request)
```

桌面控制器的字符串常量中可见 `confirm-location`、`import`、`probe`、`confirm-setup`、`environment-check`、`terminal`、`accounts`、`browser`、`browser-stop`、`update-runtime` 等操作名。它们为恢复操作协议提供线索；完整请求字段、状态转换和错误行为仍需逐项确认。

同时可见 `installation.json`、`config/node.json`、`config/egress.json`、`state/images.json`、`state/projects.json`、`desktop/setup-candidate.json` 等路径。字符串常量能证明名称存在，不能单独证明文件的全部结构或调用顺序。

所有这 34 个原生文件的 `.bytecode` 常量块均为空。当前没有从这些块提取到应用业务逻辑的 Python 字节码；恢复函数实现仍需要机器码反编译和行为验证。

## 镜像历史层检查

使用流式读取检查了离线归档中的 18 个镜像层，没有启动容器。检查范围为历史层中 `/opt` 下小于 2 MB 的 `.py` 和 `.so` 常规文件，共找到 35 个相关文件。

在该范围内，网关的 Python 文件仍是 134 字节加载入口；浏览器的三个 Python 入口转交给挂载的 `/opt/ewb` 组件。没有在这些文件中发现完整的自有 Python 业务源码。这是针对上述路径和文件类型的检查结果，不是对镜像内任意形式隐藏内容的穷尽证明。

## Windows 实现路径

可先保留 Linux 容器结构，重建 Windows 主机控制层和界面。Windows Docker Desktop 的 WSL 2 后端可承载 Linux 容器；安装条件应以 [Docker 的 Windows 文档](https://docs.docker.com/desktop/setup/install/windows-install/) 为准。

架构存在两种实现方向，以下属于基于提取结果的工程判断，均未完成 Windows 实测：

1. **ARM64 容器兼容验证。** 研究复用现有镜像及 Linux 原生扩展，在 x64 主机上通过 Docker Desktop 的跨架构仿真验证功能。Docker 文档说明支持仿真运行与构建，并提示仿真可能明显慢于原生执行；性能和全部系统调用兼容性仍需实测。[依据](https://docs.docker.com/build/building/multi-platform/)
2. **原生 x64 Windows 版本。** 重建主机层，并为 Linux guest/gateway 准备 amd64 实现。已有 Dockerfile 能保留部分依赖安装流程，但只修改镜像的 `--platform` 无法转换包内 ARM64 原生扩展。

已发现的主机适配点包括：

- Docker 可执行文件查找依赖 `/Applications/Docker.app`、Homebrew 路径和固定的 `desktop-linux` 上下文。
- 终端启动依赖 `/usr/bin/open -a Terminal` 和 `.command` 文件。
- 进程管理使用 POSIX 进程组、`killpg`、`pass_fds`、`fcntl.flock`；闲置检查使用 launchd。
- Python、Node 和控制器分发的是 macOS ARM64 二进制。
- 数据目录与挂载需支持 Windows 盘符、空格、中文路径、文件权限和文件锁差异。
- 浏览器中继依赖主机 Python 路径、`HOME` 和 POSIX 进程组终止方式，不能只修改页面中的 Mac 文案。

连接确认、节点切换、出口变化后的阻断、容器归属和账号/项目持久化都需要行为验证。目前尚未确认这些逻辑的完整机器码实现，不能将常量提取结果当作功能等价或安全等价的实现证明。

## 复现常量提取

在已解包的目录上使用 Python 3.10 或更高版本运行：

```sh
python tools/inspect_nuitka.py \
  "/path/to/Egress Workbench.app/Contents/Resources/Source/app/_ewb_host.cpython-312-darwin.so" \
  --output /path/to/analysis/host
```

Windows PowerShell 中使用 Windows Python 和实际解包路径即可；无需执行包内 macOS Python：

```powershell
py -3 tools/inspect_nuitka.py 'C:\ewb-analysis\extracted\Egress Workbench.app\Contents\Resources\Source\app\_ewb_host.cpython-312-darwin.so' --output 'C:\ewb-analysis\decoded\host'
```

工具生成 `summary.json` 和按模块划分的常量 JSON，明确标记 `recovered_function_bodies: false`。它仅支持本次观察到的未压缩、小端 Nuitka 常量格式；不支持的文件会报告失败。

解析格式参考：[Nuitka 4.3.3 常量格式定义](https://github.com/Nuitka/Nuitka/blob/4.3.3/nuitka/build/include/nuitka/constants_blob_spec.h)、[对应加载器实现](https://github.com/Nuitka/Nuitka/blob/4.3.3/nuitka/build/static_src/HelpersConstantsBlob.c)。

DMG、提取的原始资源和完整解码 JSON 保留在本地分析目录，没有加入仓库。本次结果为后续 Windows 重建提供了可核对的接口资料；完成可用版本仍需恢复关键行为、实现 Windows 主机层并在 Windows 上验收。
