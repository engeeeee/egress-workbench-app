<p align="center"><img src="assets/logo.svg" width="88" alt="Egress Workbench logo"></p>
<h1 align="center">Egress Workbench | Fingerprint Runtime Environment</h1>
<p align="center">One working environment for Claude Code, Codex and Chromium.</p>
<p align="center"><strong>English</strong> · <a href="README.zh-CN.md">简体中文</a></p>

> **Windows preview implementation:** this branch adds a rebuilt Windows host and native-architecture Linux container recipes. See [Windows setup and build instructions](windows/README.zh-CN.md). The original macOS release described below is maintained separately.

Egress Workbench is a **fingerprint runtime environment** for macOS, providing Claude Code, Codex and shared Chromium with a common network exit, configured time zone and persistent workspaces.

Tools run in Linux and can read and edit the project folder you select on your Mac. Software, sign-ins and conversation state survive ordinary environment stops and restarts, so you can continue working on existing projects.

The current implementation checks the exit IP and estimated region, applies the configured time zone, and preserves tool and browser state. Linux, container and hardware characteristics may remain detectable; this is not a physical-machine emulator or an anonymity, anti-ban or account-acceptance guarantee. Other tools need their own compatibility checks.

**Set up once, then work from Terminal.** Different projects have separate workspace directories; the supported tools share their account authorization.

> **0.3.3 release:** this repository contains the public documentation and screenshots. Download the Apple Silicon DMG from the [v0.3.3 release](https://github.com/bbfp/egress-workbench-app/releases/tag/v0.3.3). The app is ad-hoc signed and has not been Apple-notarized.

## 0.3.3 release

[Download the full DMG, about 1.149 GB](https://github.com/bbfp/egress-workbench-app/releases/download/v0.3.3/Egress-Workbench-0.3.3-arm64.dmg) · [SHA-256](https://github.com/bbfp/egress-workbench-app/releases/download/v0.3.3/Egress-Workbench-0.3.3-arm64.dmg.sha256) · [Release notes](https://github.com/bbfp/egress-workbench-app/releases/tag/v0.3.3)

This release targets Apple Silicon Macs running macOS 14 or later. The DMG contains the offline environment and has this SHA-256 digest:

```text
0e2efab0f7110aa71032c5b27e741b755da897328267ff57f3a19a91a6a9598d
```

The public repository contains guides and screenshots. The application source is not published here.

0.3.3 improves setup-step transitions, visible operation feedback, connection-evidence handling and first browser startup feedback. It keeps existing account, project and browser data, and retains the source-protection and telemetry defaults. Claude Code remains the primary command entry while Codex stays available with the same commands. See the release notes for the complete list of fixes.

**This is a test release.** It began as a tool for personal use; bugs and compatibility gaps may remain. The repository publishes the App, documentation and screenshots, without the application's own source code.

![Native connection screen with explicitly labeled demonstration data](assets/connection-en.png)

*Screenshots show the native app using labeled demonstration data. The IP, region and project paths shown are examples, not user data or live connection measurements.*

## What it does

- **Persistent tools:** Claude Code, Codex and Chromium are included in the full installer. You bring your own accounts and connection subscription.
- **A controlled network route:** the environment connects to the chosen node itself. It does not fall back to an ordinary direct connection when the node is unavailable.
- **Explicit connection approval:** inspect the measured exit IP, estimated region and time zone before enabling the environment. A detected node or exit change requires a new check and confirmation.
- **Real project files:** run a command from your Mac project directory to share it with that project's Linux workspace. Multiple projects can run concurrently.
- **One shared browser:** cookies, bookmarks and history persist across projects. Sign-in uses this browser; the Mac browser displays its remote screen.
- **English and Chinese UI:** the app initially follows macOS. Change its language and appearance in Settings. App and Mac-side messages are localized; some Linux startup diagnostics and third-party tool output remain in English.

## Before you begin

You need an **Apple Silicon Mac with macOS 14 or later**, a running **Docker Desktop** installation, enough storage for the included Linux environment, and a supported connection node. The app uses Docker Desktop's `desktop-linux` environment. OrbStack and Colima are detected but are not supported as runtime engines.

Version 0.3.3 supports fixed public IPv4 nodes: **Trojan TCP/TLS, VMess AEAD TCP with optional TLS, VLESS TCP/TLS, and Shadowsocks AEAD/2022 TCP without plugins**. Existing subscription URLs, URI/Base64 lists, Clash `proxies`, and EWB profiles remain compatible. Unsupported transports and options are reported with a reason; the app does not silently convert them to a weaker connection mode.

A single-object Trojan client JSON can also be pasted or imported when it contains fields such as `type`, `host`, `port` and `password`. The optional `data` URL is not fetched or retained, and an `udp` flag does not enable UDP. Other raw client JSON exports are not supported yet.

**Do I need to run another VPN app?** Egress Workbench establishes its own connection to the selected node. Your Mac's VPN does not need to use that same node or TUN mode. Your Mac still needs to be able to reach the selected node's server. Egress Workbench controls its own environment's traffic, not all traffic from your Mac.

**Choose a stable node you trust and can keep using.** Frequent network or location changes may prompt additional account checks; [OpenAI lists unexpected sign-in locations as one possible alert cause](https://help.openai.com/en/articles/10471992-why-am-i-receiving-a-suspicious-activity-alert). A node name does not guarantee a fixed exit IP, and no node choice guarantees account acceptance. Egress Workbench requires another check and confirmation when it detects an exit change.

## First setup

1. **Install the app.** Open the DMG, drag Egress Workbench to Applications, and launch Docker Desktop. Open Egress Workbench. Follow macOS's normal security approval process for a preview build; do not disable system protection globally.
2. **Confirm a data folder.** Keep the default, or choose a dedicated folder on an external drive. Confirm this location before importing the environment.
3. **Import the included environment.** The app verifies and imports the bundled components locally. It does not download Claude Code, Codex or Chromium one by one. Wait for installation to finish; a failed attempt retains existing data and can be retried in the same directory.
4. **Import and select a node.** Paste your subscription or node link, or choose a file. Pick a supported node and click **Check**. The app asks before stopping any running work in this environment to check a node. Subscriptions are parsed locally. A provider's certificate-compatibility setting may require a trust confirmation; no certificate file or fingerprint needs to be entered by hand.
5. **Review the exit.** Check the exit IP, estimated region and time zone. Click **Review and confirm**. Continue only when the connection reads **Confirmed and ready**.
6. **Sign in when needed.** Open **Accounts**, then choose Claude Code or Codex. Terminal shows progress. Complete authorization on the official page **inside the shared browser's remote screen**. Do not copy its authorization URL into the Mac browser's address bar.
   You can skip the account step and return later. Finishing the setup guide does not certify an account login.
7. **Open your project in Terminal.** Use the command examples on the Connection page. They target the selected data folder, even if your Mac already has another Egress Workbench installation.

### Where is my data?

There are three distinct locations:

| Location | What it contains |
|---|---|
| Applications | The macOS app |
| Your chosen data folder | Private connection settings, host runtime files, logs and browser downloads |
| Docker Desktop's data disk | Linux images, containers, persistent tool homes, sign-ins, conversations and browser profile |

Your project files stay in their original Mac folders. **Choosing an external data folder does not move Docker's data disk.** Set its location separately in Docker Desktop if needed. Moving an existing environment to another Mac requires a separate backup and restore of both the chosen folder and Docker-backed data. The first-use steps above create a new environment; copying the app or chosen folder alone is not a full environment backup. Don't unplug a drive while the app or Docker is using it.

Keep both storage locations when backing up or moving an environment. This desktop preview does not include a migration assistant.

### Docker image-store compatibility

Since 0.2.8, the installer includes the complete offline image set for both containerd and classic image stores and recognizes their different image identifiers. **You do not need to switch image stores to install this version.** The installer does not change Docker's storage settings, overwrite existing image tags or delete existing containers and volumes. After import, it verifies all three required images; a failed check stops installation instead of silently downloading replacements.

The 0.2.8 validation completed native offline installation, repeat installation and data-preservation checks on Docker Desktop Engine 29.4.3 with the classic store and an isolated ARM64 Engine 29.9.2 with containerd. The containerd tests retained an existing test container, its writable layer, image tag and volume data. This is not a claim of coverage for every Docker version; a fresh-Mac installation through Docker Desktop 4.97's graphical interface has not been retested with 0.2.8.

## Daily use

Settings > Environment check reads local configuration and the isolation and mounts of existing containers on demand. It does not start workloads or probe the public network; unverified items are labeled.

The app shows a full command path when it cannot verify the short `ewb` entry. **Use that displayed path in place of `ewb` below.** Settings can add the entry under `~/.local/bin`; the app does not edit your shell configuration. If your shell cannot find `ewb`, the full path still works.

```sh
cd /path/to/your-project

# Interactive tools
ewb claude
ewb codex

# Send one request
ewb claude -p "Summarize this project"
ewb codex exec "Summarize this project"

# Continue an earlier conversation
ewb claude --continue
ewb codex resume

# Enter the project's Linux shell
ewb shell
```

Replace the example project path with your own. Tools edit the real shared files, so normal version control and backups still matter. Project contents can reveal information about you or your work; the app does not sanitize them automatically.

### Refresh a subscription or change node

When a provider publishes a monthly update, open **Connection > Connection settings**, paste the new subscription URL or choose the downloaded file, and select **Import**. Choose a node, run **Check**, review the exit details, and confirm it before starting work again. This is a manual refresh; it keeps the installed software, projects, accounts, sessions and browser profile. Changing a node does not require reinstalling the DMG.

Save your work before checking a node: the check stops this environment's workloads. Once a browser or project exists, a node requiring a different country, city or time zone directs you to a new dedicated directory while preserving the old environment; existing identity data is not migrated automatically.

### Update an existing environment

**From 0.3.0–0.3.2 to 0.3.3:** replace the app. If Settings offers a runtime-component update, run it before checking and confirming the connection. Existing data remains in its data folder; macOS may ask you to approve opening the updated app.

After replacing the app, check the runtime component status in Settings and use the offered update entry. The 0.2.7 → 0.2.9 update was tested with existing authorization, configuration, project records, writable container data and persistent volumes preserved, and the previous runtime backed up. Replacing the app alone does not update installed runtime components. Initialized 0.2.6 protected environments also retain the backup-and-upgrade path. End active sessions before updating. A successful update leaves the environment stopped until you check and confirm the connection again. An old directory that has not been initialized directs you to finish connection setup. Older or incompatible layouts require a new dedicated directory and retain the original data. If recovery is pending, keep Docker running and choose Continue recovery.

### Accounts

```sh
ewb claude auth login     # Claude Code
ewb login                 # Codex
```

These commands use the shared internal browser. A failed internal browser flow stops rather than opening an account page in the Mac browser. The browser keeps its cookies, but providers can expire sessions or require new verification. **An unknown account status is not the same as being signed out.** Ordinary environment restarts do not deliberately erase authorization.

Use **Accounts > Refresh account status** to check the saved local authorization with the official CLI interfaces. The app does not send a model request or return credentials as part of this check.

| Appearance | Meaning |
|---|---|
| Green, Signed in · local authorization | The tool recognizes its local authorization. |
| Yellow, Not signed in | No local authorization was found. |
| Blue, Checking | The check is still running. |
| Gray, Unable to check / Previous result · refresh to check | Read the reason and refresh. This is not a sign-out result. |

Local authorization does not guarantee that a provider will accept the next request; expired or revoked sessions may still require another sign-in. Updating this environment normally preserves authorization.

### Browser and clipboard

```sh
ewb browser
ewb browser stop
```

One browser serves all projects, regardless of the directory you start it from. Use **Paste in** to send text from your Mac. To copy text back, select it inside Chromium, press **Ctrl+C**, then click **Copy out**. Clipboard writes happen only when you click; there is no automatic synchronization. Chinese, English and multiline text are supported. Downloads appear under `browser-files/Downloads` in your chosen data folder.

Closing the remote viewer does not stop Chromium. `ewb browser stop` releases browser resources while retaining its profile and downloads.

### Network-check websites

Open the shared browser, then choose **Net.Coffee** or **fuck-claude.app** on the app's Browser page or under **Network checks · 网络检测** above the remote display. These fixed shortcuts open [ip.net.coffee/claude](https://ip.net.coffee/claude/) and [fuck-claude.app](https://fuck-claude.app/) in a new tab inside Chromium, using the environment's confirmed connection.

The first-open suggestion can be skipped. Neither site is opened automatically, and Egress Workbench does not read or interpret the results. The websites display their own assessments; those assessments do not guarantee account acceptance.

### Resources and stopping

```sh
ewb ps             # Show running containers and resource usage
ewb stop           # Stop the current project
ewb stop-all       # Stop this environment, including shared services
```

Project containers stop automatically after **30 idle minutes**, once every session, shell and background job has exited. A tool waiting for input still counts as active. The browser and shared services are excluded. Stopping preserves software, authorization and conversation files.

## Connection states

| State | What to do |
|---|---|
| Not set up yet | Complete the steps in Get started. |
| Checking the connection | Wait for the result before starting work. |
| Confirmed and ready | Start your tools or browser. |
| Review and confirm | Review the checked node and exit before approving. |
| Networking blocked | Check the node and connection again; don't bypass the gate. |
| Status unavailable | Refresh and inspect the app's private logs. The app cannot currently confirm the state; it does not show stale success. |

Connection checks are periodic, so detecting an upstream exit change takes time. IP location is an estimate from external databases. This app does **not** prove physical location, conceal every container or proxy characteristic, or guarantee account acceptance by a service. Its network controls govern the environment's route to the selected node; they cannot control how the provider forwards traffic beyond that node. Provider rules and account verification still apply.

## Getting help

Keep subscription links, node passwords, cookies, authorization codes and private logs out of GitHub issues. Describe the step that failed, your macOS/app version and a redacted error message. Installer failures can be retried in the same data folder; do not delete persistent data as a first troubleshooting step.

---
Created by [MOYU](https://github.com/bbfp).

## License and scope

Licensor: MOYU. The [PolyForm Noncommercial License 1.0.0](LICENSE) covers MOYU's original documentation, images and descriptions in this repository, and the 0.3.0, 0.3.1 and 0.3.3 Release Apps published on GitHub Releases, to the extent MOYU holds the relevant rights. Those Release Apps are offered for the noncommercial purposes stated in the license, subject to its scope and notices. Third-party components remain under their own licenses. If you copy or redistribute material covered by this license, include the LICENSE text or its official URL and any notices that LICENSE requires. The license includes its stated permissions for charitable, educational, public research, public safety or health, environmental protection and government institutions. If this summary conflicts with the [LICENSE](LICENSE) text, the LICENSE text controls.

PolyForm Noncommercial is a noncommercial license. It is not an OSI-approved open-source license, and it does not permit commercial use. This repository only publishes documentation, images and the Release App; it does not publish Egress Workbench's own source code. Adding LICENSE does not mean that the source code has been published or grant additional rights to unpublished source. Third-party components and services remain subject to their own licenses, terms and policies.

## Commercial authorization and collaboration

Commercial use outside the permissions in LICENSE, as well as enterprise use, resale, product integration or hosted services, requires prior contact at [alphaevolve.com@gmail.com](mailto:alphaevolve.com@gmail.com). You can use “Egress Workbench commercial authorization” as the email subject. Contacting us does not itself grant a commercial license; terms, pricing and applicable versions must be agreed separately.

## Account, service and affiliation disclaimer

Egress Workbench is an independent project by MOYU. It is not affiliated with, sponsored by, endorsed by or officially partnered with Anthropic, OpenAI, Google, Docker or any other service provider named in this repository. The project does not provide third-party accounts, subscription nodes or third-party services, and does not guarantee that a network, account or third-party service will remain available.

Using this environment, including Codex, Claude Code, Chromium or another tool, may lead a provider to require verification, restrict, suspend, terminate or ban an account. To the extent allowed by applicable law, the user accepts the risk and consequences of any account loss, service interruption or related loss. Follow applicable law, node-provider rules and each service's terms, and back up project data before use. Except where applicable law requires otherwise, the author and maintainers are not responsible for third-party service decisions or resulting losses.
