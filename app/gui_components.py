import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
from .models import Task
from .utils import ToDoError
import logging
from pathlib import Path

logger = logging.getLogger("app.gui")
LOG_PATH = Path(__file__).resolve().parent / "activity.log"

# Настройка логгирования для GUI модуля
handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class TaskTable(ttk.Treeview):
    def __init__(self, master, **kwargs):
        columns = ("id", "title", "description", "done", "created_at", "completed_at")
        super().__init__(master, columns=columns, show="headings", **kwargs)
        self.heading("id", text="ID")
        self.heading("title", text="Title")
        self.heading("description", text="Description")
        self.heading("done", text="Done")
        self.heading("created_at", text="Created")
        self.heading("completed_at", text="Completed")
        self.column("id", width=40, anchor="center")
        self.column("title", width=150)
        self.column("description", width=250)
        self.column("done", width=60, anchor="center")
        self.column("created_at", width=140)
        self.column("completed_at", width=140)

    def load_tasks(self, tasks):
        self.delete(*self.get_children())
        for t in tasks:
            self.insert("", "end", values=(
                t.id, t.title, t.description, "✓" if t.done else "", 
                t.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                t.completed_at.strftime("%Y-%m-%d %H:%M:%S") if t.completed_at else ""
            ))

class ActivityPlot(ttk.Frame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db
        self.fig, self.ax = plt.subplots(figsize=(4,2.5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.draw()

    def draw(self):
        self.ax.clear()
        data = self.db.tasks_done_by_day()
        if data:
            days = [d for d,c in data]
            counts = [c for d,c in data]
            # matplotlib default colors used (we do not override per rules)
            self.ax.bar(days, counts)
            self.ax.set_title("Completed tasks by day")
            self.ax.set_xlabel("Day")
            self.ax.set_ylabel("Count")
            self.ax.tick_params(axis="x", rotation=45)
        else:
            self.ax.text(0.5, 0.5, "No completed tasks", ha="center", va="center")
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        self.fig.tight_layout()
        self.canvas.draw()
