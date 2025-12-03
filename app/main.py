import tkinter as tk
from tkinter import ttk, messagebox
from .db import DB
from .models import Task
from .gui_components import TaskTable, ActivityPlot, logger
from .utils import ToDoError
from datetime import datetime
import logging
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "activity.log"
app_logger = logging.getLogger("app.main")
if not app_logger.handlers:
    fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s"))
    app_logger.addHandler(fh)
app_logger.setLevel(logging.INFO)

class ToDoApp(tk.Tk):
    def __init__(self, db_path: str = None):
        super().__init__()
        self.title("ToDo GUI")
        self.geometry("1000x600")
        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.on_exit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

        self.db = DB(db_path)

        left = ttk.Frame(self)
        left.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        right = ttk.Frame(self, width=320)
        right.pack(side="right", fill="y", padx=5, pady=5)

        self.table = TaskTable(left)
        self.table.pack(fill="both", expand=True)
        self.table.bind("<Double-1>", self.on_edit_selected)

        ttk.Label(right, text="New / Edit Task").pack(anchor="w")
        ttk.Label(right, text="Title:").pack(anchor="w", pady=(6,0))
        self.title_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.title_var).pack(fill="x")

        ttk.Label(right, text="Description:").pack(anchor="w", pady=(6,0))
        self.desc_text = tk.Text(right, height=6, wrap="word")
        self.desc_text.pack(fill="x")

        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill="x", pady=6)
        ttk.Button(btn_frame, text="Add Task", command=self.add_task).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Edit Selected", command=self.on_edit_selected).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=2)

        ttk.Button(right, text="Mark Done/Undone", command=self.toggle_done).pack(fill="x", pady=4)

        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=6)

        ttk.Label(right, text="Activity:").pack(anchor="w")
        self.plot = ActivityPlot(right, self.db)
        self.plot.pack(fill="both", expand=False)

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(side="bottom", fill="x")

        self.refresh_tasks()

    def set_status(self, text):
        self.status.set(text)
        app_logger.info(text)

    def refresh_tasks(self):
        tasks = self.db.list_tasks()
        self.table.load_tasks(tasks)
        self.plot.draw()
        self.set_status(f"Loaded {len(tasks)} tasks")

    def add_task(self):
        title = self.title_var.get().strip()
        desc = self.desc_text.get("1.0", "end").strip()
        try:
            t = Task(title=title, description=desc)
            self.db.add_task(t)
            self.set_status(f"Task added: {title}")
            self.title_var.set("")
            self.desc_text.delete("1.0", "end")
            self.refresh_tasks()
        except ToDoError as e:
            messagebox.showerror("Error", str(e))
            app_logger.exception("Error adding task")

    def get_selected_task_id(self):
        sel = self.table.selection()
        if not sel:
            return None
        item = self.table.item(sel[0])
        return item["values"][0]

    def on_edit_selected(self, event=None):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showinfo("Info", "Select a task to edit.")
            return
        task = self.db.get_task(tid)
        if not task:
            messagebox.showerror("Error", "Task not found.")
            return
        def save_changes():
            new_title = title_var.get().strip()
            new_desc = desc_box.get("1.0", "end").strip()
            if not new_title:
                messagebox.showerror("Error", "Title required.")
                return
            task.title = new_title
            task.description = new_desc
            self.db.update_task(task)
            top.destroy()
            self.set_status(f"Task updated: {task.title}")
            self.refresh_tasks()

        top = tk.Toplevel(self)
        top.title(f"Edit Task #{task.id}")
        ttk.Label(top, text="Title:").pack(anchor="w")
        title_var = tk.StringVar(value=task.title)
        ttk.Entry(top, textvariable=title_var).pack(fill="x")

        ttk.Label(top, text="Description:").pack(anchor="w")
        desc_box = tk.Text(top, height=6)
        desc_box.insert("1.0", task.description)
        desc_box.pack(fill="both", expand=True)

        ttk.Button(top, text="Save", command=save_changes).pack(pady=4)

    def delete_selected(self):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showinfo("Info", "Select a task to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete selected task?"):
            return
        self.db.delete_task(tid)
        self.set_status(f"Task deleted: id={tid}")
        self.refresh_tasks()

    def toggle_done(self):
        tid = self.get_selected_task_id()
        if not tid:
            messagebox.showinfo("Info", "Select a task.")
            return
        task = self.db.get_task(tid)
        if not task:
            messagebox.showerror("Error", "Task not found.")
            return
        if task.done:
            task.mark_undone()
            self.set_status(f"Marked undone: {task.title}")
        else:
            task.mark_done()
            self.set_status(f"Marked done: {task.title}")
        self.db.update_task(task)
        self.refresh_tasks()

    def on_exit(self):
        try:
            self.db.close()
        except Exception:
            app_logger.exception("Error closing DB")
        self.destroy()

if __name__ == "__main__":
    app = ToDoApp()
    app.mainloop()
