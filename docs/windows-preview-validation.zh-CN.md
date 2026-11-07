# Windows 预览版 0.1.0 交付与验证

日期：2026-11-07。应用代码提交：`305fda6e4be3fd972c4200124313bcef6a103a65`。

已经生成真正的 x64 Windows 可执行文件。代码保存在 `windows-preview` 分支，未合并到原文档仓库的 main 分支。

## 下载与启动

- [Windows x64 发布包所在的 GitHub Actions Artifact](https://github.com/engeeeee/egress-workbench-app/actions/runs/42378568840/artifacts/13575884547)
- [完整构建和检查记录](https://github.com/engeeeee/egress-workbench-app/actions/runs/42378568840)
- [使用、源码启动与自行打包说明](../windows/README.zh-CN.md)

GitHub Artifact 下载后包含一个 `Egress-Workbench-Windows-x64-0.1.0.zip`。将里面的发布 ZIP 完整解压，运行 `EgressWorkbench/EgressWorkbench.exe`；旁边的 `_internal` 文件夹需要保留。打包版本不需要另外安装 Python。命令行入口为 `ewb/ewb.exe`。

需要已运行的 Docker Desktop，使用 WSL 2 / Linux containers，Docker Engine 28 或更新版本。建议 x64 Windows 11。首次点击“安装运行环境”会在线下载并构建工具与浏览器镜像。之后依次导入节点、检查、核对并确认，再选择项目。

发布 ZIP 大小为 32,331,704 字节，SHA-256 为：

```text
f54f77987f24976c3087aab35b545873416402869f72fff70fcdb4929f586ffd
```

已经解开并校验发布 ZIP，确认图形程序和命令行程序均为 PE x64（machine `0x8664`），运行资源、许可证和说明文件均存在。

## 已完成的验证

上述构建的四个任务全部成功：

| 任务 | 实际检查 |
| --- | --- |
| Windows 自动检查 | Python 3.12 下 26 项检查；真实 Tk 界面启动与未应用设置的确认状态检查 |
| Linux 自动检查 | 同一组 26 项检查 |
| Windows 打包 | 在 x64 Windows runner 上生成 GUI / CLI；运行打包 CLI 的版本入口和 relay 导入入口；启动打包 GUI 并确认其持续运行 |
| 原生 x64 容器集成 | 在 x64 Linux runner 上实际构建三个镜像并通过下列完整流程 |

独立的本地 Linux ARM64 / Docker Engine 29.9.3 环境也完成了相同容器流程。测试使用临时自建 Shadowsocks 节点，未使用用户订阅或第三方工具账号。

容器集成实际通过了 12 组检查：

1. gateway / work / browser 镜像原生构建。
2. 两个外部来源的出口 IPv4 一致，工作容器到公网的直接 TCP 连接被阻断。
3. 检查、复核和连接确认流程。
4. Chromium / noVNC 显示服务启动，仅在主机 loopback 监听。
5. 通过 WebSocket 收到真实 VNC 协议数据；错误令牌和外部 Origin 被拒绝。
6. 容器内 Codex 可执行，版本为 0.167.0。
7. 容器内 Claude Code 可执行，版本为 2.1.319。
8. 工具发起的网址在共享 Chromium 内打开。
9. 浏览器容器能够访问工具容器监听的 localhost OAuth 回调端口。
10. 主机连接许可过期后，网关自行退出。
11. 网关退出后，工作容器仍无法直连公网。
12. 停止并重新检查、确认后，真实项目文件、工具 home、项目容器可写层和浏览器 home 均保留。

可复现的容器测试脚本为 [integration_runtime.py](../tests/integration_runtime.py)。它使用独立实例标识，清理自身创建的临时容器、网络和数据卷。退出 IP 等测量值未写入此公开交付记录。

## 验证边界

Windows runner 上的程序构建与启动、原生 x64 Linux 容器集成已分别验证；尚未在真实 Windows 11 + Docker Desktop 桌面上完成整套交互验收。特别是主机文件共享、休眠唤醒、杀毒软件兼容性及各版本 WSL 2 的行为，仍需在实际电脑上确认。

没有使用真实 Anthropic / OpenAI 账号执行登录或模型请求；已验证的是工具可执行、授权网址转交和共享 localhost 回调能力。实际订阅兼容性、账号授权和后续请求是否被服务商接受仍需用户自行完成。其他节点协议的导入有自动检查，实际网络集成目前使用 Shadowsocks。

此版本是独立实现的功能预览，不等同于原版全部安全和功能行为。Chromium 的 `--no-sandbox`、共享工具 home、在线首次安装，以及尚未实现的原版功能，已在使用说明中明确列出。没有将未验证项目视为通过。
