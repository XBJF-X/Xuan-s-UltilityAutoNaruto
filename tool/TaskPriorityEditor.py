import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ScrollableFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width),
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_mousewheel(self, event):
        if self.winfo_exists():
            self.canvas.yview_scroll(int(-event.delta / 120), "units")


class PriorityTab:
    def __init__(self, parent, app, title, key_name):
        self.app = app
        self.title = title
        self.key_name = key_name
        self.vars = {}
        self.task_labels = []
        self._is_rebuilding = False
        self._refresh_job = None

        self.frame = ttk.Frame(parent)

        control = ttk.Frame(self.frame)
        control.pack(fill="x", padx=10, pady=(10, 4))

        self.sort_mode = tk.StringVar(value="name")
        ttk.Label(control, text="编辑列表排序：").pack(side="left")
        ttk.Radiobutton(
            control,
            text="按任务名",
            variable=self.sort_mode,
            value="name",
            command=self.on_sort_mode_changed,
        ).pack(side="left", padx=(0, 8))
        ttk.Radiobutton(
            control,
            text="按优先级",
            variable=self.sort_mode,
            value="priority",
            command=self.on_sort_mode_changed,
        ).pack(side="left")

        body = ttk.PanedWindow(self.frame, orient="horizontal")
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left_card = ttk.LabelFrame(body, text=f"{title}编辑")
        right_card = ttk.LabelFrame(body, text=f"{title}执行顺序预览（值越小越先执行）")
        body.add(left_card, weight=3)
        body.add(right_card, weight=2)

        self.edit_scroll = ScrollableFrame(left_card)
        self.edit_scroll.pack(fill="both", expand=True, padx=8, pady=8)

        header = ttk.Frame(self.edit_scroll.inner)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(header, text="任务", width=26).grid(row=0, column=0, sticky="w")
        ttk.Label(header, text="优先级", width=12).grid(row=0, column=1, sticky="w")
        ttk.Label(header, text="说明", width=12).grid(row=0, column=2, sticky="w")

        self.rows_container = ttk.Frame(self.edit_scroll.inner)
        self.rows_container.grid(row=1, column=0, sticky="nsew")

        preview_cols = ("rank", "task", "priority")
        self.preview_tree = ttk.Treeview(right_card, columns=preview_cols, show="headings", height=22)
        self.preview_tree.heading("rank", text="顺位")
        self.preview_tree.heading("task", text="任务")
        self.preview_tree.heading("priority", text="优先级")
        self.preview_tree.column("rank", width=60, anchor="center")
        self.preview_tree.column("task", width=200, anchor="w")
        self.preview_tree.column("priority", width=90, anchor="center")
        self.preview_tree.pack(fill="both", expand=True, padx=8, pady=8)

        tips = ttk.Label(
            right_card,
            text="同优先级任务会并列；可直接在左侧输入负数或正数。",
            foreground="#666666",
        )
        tips.pack(anchor="w", padx=8, pady=(0, 8))

    def rebuild_editor_list(self):
        self._is_rebuilding = True
        for widget in self.rows_container.winfo_children():
            widget.destroy()
        self.task_labels.clear()

        tasks = list(self.app.tasks.keys())
        if self.sort_mode.get() == "priority":
            tasks.sort(key=lambda name: (self.get_priority_value(name), name))
        else:
            tasks.sort()

        for idx, task_name in enumerate(tasks, start=1):
            row = ttk.Frame(self.rows_container)
            row.grid(row=idx, column=0, sticky="ew", pady=2)

            ttk.Label(row, text=task_name, width=26).grid(row=0, column=0, sticky="w")
            var = self.vars[task_name]

            spin = tk.Spinbox(
                row,
                textvariable=var,
                from_=-999,
                to=999,
                width=10,
                increment=1,
                justify="center",
            )
            spin.grid(row=0, column=1, sticky="w", padx=(0, 8))

            label = ttk.Label(row, text="", width=12, foreground="#2f6f31")
            label.grid(row=0, column=2, sticky="w")
            self.task_labels.append((task_name, label))

        self._is_rebuilding = False

    def get_priority_value(self, task_name):
        value = self.vars[task_name].get().strip()
        try:
            return int(value)
        except ValueError:
            return 0

    def load_values_from_tasks(self):
        self.vars = {}
        for task_name, info in self.app.tasks.items():
            value = info.get(self.key_name, 0)
            self.vars[task_name] = tk.StringVar(value=str(value))
            self.vars[task_name].trace_add("write", lambda *_: self.on_priority_changed())

        self.rebuild_editor_list()
        self.refresh_preview()

    def on_sort_mode_changed(self):
        self.rebuild_editor_list()
        self.refresh_preview()

    def refresh_preview(self):
        for row in self.preview_tree.get_children():
            self.preview_tree.delete(row)

        ordered = sorted(
            self.app.tasks.keys(),
            key=lambda name: (self.get_priority_value(name), name),
        )

        previous = None
        rank = 0
        for task_name in ordered:
            priority = self.get_priority_value(task_name)
            if priority != previous:
                rank += 1
                previous = priority
            self.preview_tree.insert("", "end", values=(rank, task_name, priority))

        rank_map = {}
        previous = None
        rank = 0
        for task_name in ordered:
            priority = self.get_priority_value(task_name)
            if priority != previous:
                rank += 1
                previous = priority
            rank_map[task_name] = rank

        for task_name, label in self.task_labels:
            label.config(text=f"第 {rank_map[task_name]} 顺位")

    def on_priority_changed(self):
        if self._is_rebuilding:
            return

        if self._refresh_job is not None:
            try:
                self.frame.after_cancel(self._refresh_job)
            except tk.TclError:
                pass
            self._refresh_job = None

        self._refresh_job = self.frame.after(30, self._flush_priority_change)

    def _flush_priority_change(self):
        self._refresh_job = None
        if self._is_rebuilding or not self.frame.winfo_exists():
            return

        self.refresh_preview()
        if self.sort_mode.get() == "priority":
            self.rebuild_editor_list()
            self.refresh_preview()

    def write_back(self):
        for task_name, info in self.app.tasks.items():
            info[self.key_name] = self.get_priority_value(task_name)


class TaskPriorityEditorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DefaultConfig 任务优先级编辑器")
        self.geometry("1300x760")
        self.minsize(1100, 680)

        self.config_path = self.default_config_path()
        self.data = {}
        self.tasks = {}

        self.create_widgets()
        self.load_config()

    @staticmethod
    def default_config_path():
        project_root = Path(__file__).resolve().parents[1]
        return project_root / "src" / "DefaultConfig.json"

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="配置文件：").pack(side="left")
        self.path_var = tk.StringVar(value=str(self.config_path))
        path_entry = ttk.Entry(top, textvariable=self.path_var)
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ttk.Button(top, text="浏览", command=self.browse_file).pack(side="left", padx=(0, 6))
        ttk.Button(top, text="重新加载", command=self.load_config).pack(side="left", padx=(0, 6))
        ttk.Button(top, text="保存", command=self.save_config).pack(side="left")

        self.info_var = tk.StringVar(value="")
        info = ttk.Label(self, textvariable=self.info_var, foreground="#444444")
        info.pack(anchor="w", padx=10, pady=(0, 6))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.click_tab = PriorityTab(notebook, self, "连点优先级", "连点优先级")
        self.base_tab = PriorityTab(notebook, self, "基础优先级", "基础优先级")

        notebook.add(self.click_tab.frame, text="连点优先级")
        notebook.add(self.base_tab.frame, text="基础优先级")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择 DefaultConfig.json",
            filetypes=[("JSON", "*.json"), ("All Files", "*.*")],
        )
        if file_path:
            self.path_var.set(file_path)
            self.load_config()

    def load_config(self):
        path = Path(self.path_var.get()).expanduser()
        if not path.exists():
            messagebox.showerror("错误", f"文件不存在：\n{path}")
            return

        try:
            with path.open("r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception as exc:
            messagebox.showerror("读取失败", f"无法读取配置文件：\n{exc}")
            return

        tasks = self.data.get("任务")
        if not isinstance(tasks, dict) or not tasks:
            messagebox.showerror("格式错误", "配置中未找到“任务”字典。")
            return

        self.config_path = path
        self.tasks = tasks
        self.click_tab.load_values_from_tasks()
        self.base_tab.load_values_from_tasks()

        self.info_var.set(
            f"已加载：{self.config_path}    任务数：{len(self.tasks)}    规则：优先级值越小，执行越靠前"
        )

    def save_config(self):
        if not self.tasks:
            return

        self.click_tab.write_back()
        self.base_tab.write_back()

        backup_path = self.config_path.with_suffix(".json.bak")
        try:
            if self.config_path.exists():
                backup_path.write_text(self.config_path.read_text(encoding="utf-8"), encoding="utf-8")

            with self.config_path.open("w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)

            self.info_var.set(
                f"已保存：{self.config_path}（已自动备份到 {backup_path.name}）"
            )
            messagebox.showinfo("保存成功", f"配置已保存。\n备份文件：{backup_path.name}")
        except Exception as exc:
            messagebox.showerror("保存失败", f"写入文件失败：\n{exc}")


def main():
    app = TaskPriorityEditorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
