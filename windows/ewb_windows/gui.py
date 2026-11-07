from __future__ import annotations

from datetime import datetime
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from . import __version__
from .engine import Engine
from .nodes import fetch_subscription, parse_nodes
from .state import Store


class App:
    def __init__(self, root: tk.Tk, store: Store):
        self.root, self.store = root, store
        self.events = queue.Queue()
        self.busy = False
        self.buttons = []
        self.nodes = []
        root.title("Egress Workbench · Windows")
        root.geometry("1020x760")
        root.minsize(820, 650)
        root.configure(background="#f3f5f8")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f3f5f8")
        style.configure("Card.TFrame", background="white")
        style.configure("TLabel", background="#f3f5f8", foreground="#182436", font=("Segoe UI", 10))
        style.configure("Card.TLabel", background="white")
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"))
        style.configure("Subtitle.TLabel", foreground="#64748b")
        style.configure("TButton", font=("Segoe UI", 10), padding=(14, 9))
        style.configure("Accent.TButton", background="#2563eb", foreground="white")
        style.map("Accent.TButton", background=[("active", "#1d4ed8"), ("disabled", "#93a4bf")])
        outer = ttk.Frame(root, padding=26)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Egress Workbench", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text=f"Windows 预览版 {__version__}   ·   Claude Code / Codex / Chromium", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 20))
        self.phase = tk.StringVar(value="等待配置")
        self.detail = tk.StringVar(value="先安装运行环境，再导入并核对连接。")
        card = ttk.Frame(outer, style="Card.TFrame", padding=18)
        card.pack(fill="x")
        ttk.Label(card, textvariable=self.phase, font=("Segoe UI", 15, "bold"), style="Card.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=self.detail, style="Card.TLabel", wraplength=870).pack(anchor="w", pady=(8, 0))
        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True, pady=(18, 0))
        connection, workspace, logs, settings = [ttk.Frame(notebook, padding=20) for _ in range(4)]
        for tab, text in zip((connection, workspace, logs, settings), ("  连接  ", "  工作区  ", "  运行日志  ", "  设置  ")):
            notebook.add(tab, text=text)
        ttk.Label(connection, text="1  安装 Linux 运行环境", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(connection, text="首次安装会下载工具和浏览器。Docker Desktop 需要保持运行。", style="Subtitle.TLabel").pack(anchor="w", pady=(5, 9))
        row = ttk.Frame(connection)
        row.pack(fill="x")
        self.button(row, "检查 Docker", lambda: self.run(lambda e: e.doctor(), self.show_doctor)).pack(side="left")
        self.button(row, "安装运行环境", lambda: self.run(lambda e: e.install())).pack(side="left", padx=8)
        ttk.Label(connection, text="2  导入并选择连接节点", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(20, 10))
        row = ttk.Frame(connection)
        row.pack(fill="x")
        self.selected = tk.StringVar()
        self.node_box = ttk.Combobox(row, textvariable=self.selected, state="readonly")
        self.node_box.pack(side="left", fill="x", expand=True)
        self.button(row, "导入节点 / 订阅", self.import_dialog).pack(side="left", padx=(8, 0))
        self.evidence = tk.StringVar(value="出口 IP：—       地区：—\n配置时区：—")
        ttk.Label(connection, text="3  检查出口，再确认启用", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(20, 10))
        ttk.Label(connection, textvariable=self.evidence, font=("Segoe UI", 11), justify="left").pack(anchor="w", pady=(0, 14))
        row = ttk.Frame(connection)
        row.pack(fill="x")
        self.button(row, "检查所选连接", self.check).pack(side="left")
        self.confirm_button = self.button(row, "核对并确认", self.confirm, accent=True)
        self.confirm_button.pack(side="left", padx=8)
        self.button(row, "停止整个环境", lambda: self.run(lambda e: e.stop())).pack(side="left")
        ttk.Label(connection, text="节点不可用时不会退回直连。地区信息为估计值；本应用不保证账号接受或匿名。", style="Subtitle.TLabel", wraplength=850).pack(anchor="w", pady=16)
        ttk.Label(workspace, text="选择你的项目文件夹", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        row = ttk.Frame(workspace)
        row.pack(fill="x")
        self.project = tk.StringVar(value=(store.settings()["projects"] or [""])[-1])
        self.project_box = ttk.Combobox(row, textvariable=self.project, values=store.settings()["projects"])
        self.project_box.pack(side="left", fill="x", expand=True)
        self.button(row, "浏览…", self.choose_project).pack(side="left", padx=(8, 0))
        ttk.Label(workspace, text="工具直接读写所选文件夹。账号与会话保存在 Docker 数据卷中。", style="Subtitle.TLabel").pack(anchor="w", pady=(8, 20))
        for label, tools in [("开始工作", [("Claude Code", "claude"), ("Codex", "codex"), ("Linux Shell", "shell")]), ("账号登录", [("登录 Claude Code", "login-claude"), ("登录 Codex", "login-codex")])]:
            ttk.Label(workspace, text=label, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(6, 10))
            row = ttk.Frame(workspace)
            row.pack(fill="x", pady=(0, 14))
            for name, tool in tools:
                self.button(row, name, lambda t=tool: self.open_terminal(t)).pack(side="left", padx=(0, 8))
        row = ttk.Frame(workspace)
        row.pack(fill="x", pady=(10, 0))
        self.button(row, "打开共享 Chromium", lambda: self.run(lambda e: e.browser()), accent=True).pack(side="left")
        ttk.Label(workspace, text="登录授权请在共享 Chromium 的远程画面内完成。\n关闭显示网页会保留浏览器；“停止整个环境”会停止工具和浏览器。", style="Subtitle.TLabel", wraplength=840).pack(anchor="w", pady=16)
        self.log_view = scrolledtext.ScrolledText(logs, font=("Consolas", 10), background="#111c2d", foreground="#dce7f5", relief="flat", state="disabled")
        self.log_view.pack(fill="both", expand=True)
        ttk.Label(logs, text="完整安装输出保存在数据目录的 build.log。", style="Subtitle.TLabel").pack(anchor="w", pady=(10, 0))
        self.timezone = tk.StringVar(value=store.settings()["timezone"])
        self.context = tk.StringVar(value=store.settings()["context"])
        for text, value in [("环境时区（IANA）", self.timezone), ("本机 Docker 上下文", self.context)]:
            ttk.Label(settings, text=text).pack(anchor="w", pady=(8, 5))
            ttk.Entry(settings, textvariable=value, width=45).pack(anchor="w")
        self.button(settings, "保存设置", self.save_settings).pack(anchor="w", pady=16)
        ttk.Label(settings, text="已建立环境后固定时区；需要其他时区时，请用 --data 指定新的数据目录。", style="Subtitle.TLabel", wraplength=840).pack(anchor="w")
        ttk.Label(settings, text="数据目录", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(24, 6))
        ttk.Label(settings, text=str(store.home), wraplength=830).pack(anchor="w")
        ttk.Label(settings, text="此目录保存节点密码与运行记录，请妥善保管。\n工具账号、会话和浏览器配置位于 Docker 数据卷。", style="Subtitle.TLabel").pack(anchor="w", pady=8)
        self.operation = tk.StringVar(value="就绪。首次构建可能需要数分钟。")
        ttk.Label(outer, textvariable=self.operation, style="Subtitle.TLabel", wraplength=900).pack(anchor="w", pady=(14, 0))
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh_nodes()
        root.after(100, self.poll)

    def button(self, parent, text, command, accent=False):
        button = ttk.Button(parent, text=text, command=command, style="Accent.TButton" if accent else "TButton")
        self.buttons.append(button)
        return button

    def add_log(self, text):
        self.log_view.configure(state="normal")
        self.log_view.insert("end", datetime.now().strftime("%H:%M:%S  ") + str(text) + "\n")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def run(self, action, done=None):
        if self.busy:
            return
        self.busy = True
        self.operation.set("正在执行，请等待…")
        def worker():
            try:
                engine = Engine(self.store, lambda text: self.events.put(("log", text)))
                result = action(engine)
                self.events.put(("done", (result, done)))
            except Exception as error:
                self.events.put(("error", str(error)))
        threading.Thread(target=worker, daemon=True).start()

    def refresh_nodes(self):
        self.nodes = self.store.read("nodes.json", [])
        self.node_box["values"] = [f"{i+1}. {n['label']}" for i, n in enumerate(self.nodes)]
        index = next((i for i, n in enumerate(self.nodes) if n["id"] == self.store.settings()["selected"]), 0)
        if self.nodes:
            self.node_box.current(index)

    def node_id(self):
        index = self.node_box.current()
        return self.nodes[index]["id"] if 0 <= index < len(self.nodes) else ""

    def save_settings(self):
        selected, timezone, context = self.node_id(), self.timezone.get().strip(), self.context.get().strip()
        self.run(lambda e: e.save_settings(selected, timezone, context))

    def check(self):
        state = Engine(self.store).status()
        if state["phase"] == "ready" and not messagebox.askyesno("检查连接", "检查连接会停止本环境正在运行的工具和浏览器。请先保存工作。继续检查？", parent=self.root):
            return
        selected, timezone, context = self.node_id(), self.timezone.get().strip(), self.context.get().strip()
        def action(e):
            e.save_settings(selected, timezone, context)
            return Engine(self.store, e.log).check()
        self.run(action)

    def confirm(self):
        if not messagebox.askyesno("核对连接", self.evidence.get() + "\n\n确认以上出口与配置时区后启用环境？", parent=self.root):
            return
        self.run(lambda e: e.confirm())

    def show_doctor(self, result):
        messagebox.showinfo("Docker 已就绪", f"Docker {result['docker']}\n架构：{result['architecture']}\n上下文：{result['context']}", parent=self.root)

    def choose_project(self):
        path = filedialog.askdirectory(title="选择项目目录", parent=self.root)
        if path:
            self.project.set(path)

    def open_terminal(self, tool):
        path = self.project.get().strip()
        if not path:
            messagebox.showinfo("选择项目", "请先选择一个具体项目文件夹。", parent=self.root)
            return
        self.run(lambda e: e.terminal(path, tool))

    def import_dialog(self):
        if Engine(self.store).status()["phase"] == "ready" and not messagebox.askyesno("导入节点", "导入节点会停止当前环境并要求重新核对。已保存的账号和项目数据会保留。继续？", parent=self.root):
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("导入连接节点")
        dialog.geometry("700x450")
        dialog.transient(self.root)
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="粘贴 HTTPS 订阅地址、节点 URI、JSON 或 Clash 配置").pack(anchor="w", pady=(0, 10))
        entry = scrolledtext.ScrolledText(frame, height=12, font=("Consolas", 10))
        entry.pack(fill="both", expand=True)
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(12, 0))
        def file():
            path = filedialog.askopenfilename(parent=dialog)
            if path:
                try:
                    if Path(path).stat().st_size > 2 * 1024 * 1024:
                        raise ValueError("配置文件不能超过 2 MiB。")
                    entry.delete("1.0", "end")
                    entry.insert("1.0", Path(path).read_text(encoding="utf-8-sig"))
                except Exception:
                    messagebox.showerror("文件读取失败", "请选择小于 2 MiB 的 UTF-8 配置文件。", parent=dialog)
        def accept():
            text = entry.get("1.0", "end").strip()
            dialog.destroy()
            def action(engine):
                content = fetch_subscription(text) if text.startswith("https://") and "\n" not in text else text
                nodes, warnings = parse_nodes(content)
                engine.save_nodes(nodes)
                return {"count": len(nodes), "warnings": warnings}
            def done(result):
                self.refresh_nodes()
                messagebox.showinfo("导入完成", f"已导入 {result['count']} 个节点。" + ("\n跳过的节点：\n" + "\n".join(result["warnings"][:8]) if result["warnings"] else ""), parent=self.root)
            self.run(action, done)
        ttk.Button(row, text="选择配置文件", command=file).pack(side="left")
        ttk.Button(row, text="导入", command=accept, style="Accent.TButton").pack(side="right")

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.add_log(value)
                    self.operation.set(value)
                else:
                    self.busy = False
                    if kind == "error":
                        self.add_log(value)
                        self.operation.set("操作未完成，请查看运行日志。")
                        messagebox.showerror("操作未完成", value, parent=self.root)
                    else:
                        result, callback = value
                        self.operation.set("操作完成。")
                        self.add_log("操作完成。")
                        if callback:
                            callback(result)
        except queue.Empty:
            pass
        try:
            state = Engine(self.store).status()
            labels = {"stopped": "环境已停止", "review": "请核对出口并确认", "ready": "连接已确认"}
            self.phase.set(labels.get(state["phase"], "状态未知"))
            self.detail.set(state.get("reason") or ("后台正在监测连接；检测失败或出口变化后会停止本环境。" if state["phase"] == "ready" else "核对下方测量结果，确认后再开始工作。"))
            evidence = state.get("evidence")
            if evidence:
                self.evidence.set(f"出口 IP：{evidence['ip']}     地区：{evidence['country']} / {evidence['city']}\n配置时区：{state['timezone']}     估计地区时区：{evidence['timezone']}     直连：已阻断")
            else:
                self.evidence.set("出口 IP：—       地区：—\n配置时区：" + state["timezone"])
            if state["phase"] == "ready" and state["guard_age"] > 100:
                self.phase.set("连接监测未响应，请重新检查")
            for button in self.buttons:
                button.configure(state="disabled" if self.busy else "normal")
            self.confirm_button.configure(state="normal" if not self.busy and state["phase"] == "review" else "disabled")
        except Exception:
            self.phase.set("状态读取失败")
        self.root.after(250, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo("操作进行中", "请等待当前操作完成后再退出。", parent=self.root)
            return
        # The independent guard and gateway lease continue after closing the UI.
        self.root.destroy()


def launch(store):
    root = tk.Tk()
    App(root, store)
    root.mainloop()
