# Third-party components

This Windows implementation was written from the public product documentation and the static interface/configuration analysis recorded in `docs/windows-port-analysis.zh-CN.md`. It does not include the original application's Nuitka binaries, Swift executable, DMG, or offline images.

The repository's LICENSE and AUTHORS.md are preserved. The following independently distributed components retain their respective licenses and terms:

- Python / Tcl / Tk: https://www.python.org/psf/license/ and https://www.tcl.tk/software/tcltk/license.html
- PyYAML (MIT): https://github.com/yaml/pyyaml/blob/main/LICENSE
- tzdata (Apache-2.0, IANA time-zone data public-domain notices): https://github.com/python/tzdata
- PyInstaller bootloader (GPL with distribution exception): https://pyinstaller.org/en/stable/license.html
- sing-box (GPL-3.0 and its project notices): https://github.com/SagerNet/sing-box
- Node.js and npm: https://github.com/nodejs/node/blob/main/LICENSE and https://github.com/npm/cli/blob/latest/LICENSE
- Codex CLI (Apache-2.0 and bundled notices): https://github.com/openai/codex
- Claude Code: https://code.claude.com/docs/en/legal-and-compliance
- Chromium, TigerVNC, noVNC, websockify, Openbox, Debian/Alpine packages and fonts: their upstream and installed package copyright notices apply; Linux package notices are retained in the images.

The initial ZIP contains the Windows host application and container recipes. Tool/browser dependencies are downloaded during environment installation. The application does not redistribute the original macOS release package or claim affiliation with its author or the third-party providers.
