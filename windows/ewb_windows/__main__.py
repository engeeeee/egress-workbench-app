import argparse
import json
from pathlib import Path
import subprocess
import sys

from . import __version__
from .engine import Engine
from .nodes import fetch_subscription, parse_nodes
from .state import Store, WorkbenchError


def main():
    parser = argparse.ArgumentParser(description="Egress Workbench Windows — 本机项目、共享工具与受控代理出口")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--data", type=Path, help="专用数据目录，默认位于 LocalAppData")
    parser.add_argument("--project", default=str(Path.cwd()), help="项目目录")
    sub = parser.add_subparsers(dest="action")
    for action in ("gui", "doctor", "install", "check", "confirm", "browser", "stop", "status", "guard", "shell"):
        sub.add_parser(action)
    importer = sub.add_parser("import-node")
    importer.add_argument("file", type=Path, help="本地订阅/节点文件（不保存订阅地址）")
    selector = sub.add_parser("select")
    selector.add_argument("index", type=int, help="节点序号，从 1 开始")
    for action in ("claude", "codex", "exec"):
        item = sub.add_parser(action, add_help=False)
        item.add_argument("arguments", nargs=argparse.REMAINDER)
    args, forwarded = parser.parse_known_args()
    if forwarded and args.action not in ("claude", "codex", "exec"):
        parser.error("unrecognized arguments: " + " ".join(forwarded))
    try:
        store = Store(args.data)
        if args.action in (None, "gui"):
            from .gui import launch
            launch(store)
            return 0
        engine = Engine(store, lambda text: print(text, file=sys.stderr, flush=True))
        if args.action == "import-node":
            nodes, warnings = parse_nodes(args.file.read_text(encoding="utf-8-sig"))
            engine.save_nodes(nodes)
            result = {"nodes": [{"index": i + 1, "name": n["label"]} for i, n in enumerate(nodes)], "warnings": warnings}
        elif args.action == "select":
            nodes = store.read("nodes.json", [])
            if not 1 <= args.index <= len(nodes):
                raise WorkbenchError("节点序号不存在。")
            settings = store.settings()
            engine.save_settings(nodes[args.index - 1]["id"], settings["timezone"], settings["context"])
            result = {"selected": nodes[args.index - 1]["label"]}
        elif args.action in ("claude", "codex", "exec", "shell"):
            tail = [*forwarded, *getattr(args, "arguments", [])]
            if tail[:1] == ["--"]:
                tail = tail[1:]
            command = [args.action, *tail] if args.action in ("claude", "codex") else ["bash", "-l"] if args.action == "shell" else tail
            if not command:
                raise WorkbenchError("请在 exec 后填写 Linux 命令。")
            attached = bool(sys.stdin and sys.stdin.isatty())
            cmd = engine.tool_command(args.project, command, interactive=attached)
            return subprocess.call(cmd, env=engine.docker.environment())
        else:
            result = getattr(engine, args.action)()
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (WorkbenchError, OSError) as error:
        if sys.stderr:
            print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
