import sqlite3
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from .models import Task
from .utils import ToDoError

DB_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DB_DIR / "todo.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    done INTEGER NOT NULL DEFAULT 0
);
"""

class DB:
    def __init__(self, db_path: Optional[str] = None):
        DB_DIR.mkdir(parents=True, exist_ok=True)
        self.path = db_path or str(DB_PATH)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        try:
            self.conn.executescript(SCHEMA)
            self.conn.commit()
        except Exception as e:
            raise ToDoError(f"DB schema creation failed: {e}")

    def add_task(self, task: Task) -> Task:
        if not task.title.strip():
            raise ToDoError("Task must have a title.")
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, description, created_at, completed_at, done) VALUES (?, ?, ?, ?, ?)",
            (task.title, task.description, task.created_at.isoformat(), 
             task.completed_at.isoformat() if task.completed_at else None, int(task.done))
        )
        self.conn.commit()
        task.id = cur.lastrowid
        return task

    def update_task(self, task: Task) -> Task:
        if not task.id:
            raise ToDoError("Task must have id to update.")
        self.conn.execute(
            "UPDATE tasks SET title=?, description=?, created_at=?, completed_at=?, done=? WHERE id=?",
            (task.title, task.description, task.created_at.isoformat(),
             task.completed_at.isoformat() if task.completed_at else None, int(task.done), task.id)
        )
        self.conn.commit()
        return task

    def delete_task(self, task_id: int):
        self.conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()

    def get_task(self, task_id: int) -> Optional[Task]:
        cur = self.conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = cur.fetchone()
        return self._row_to_task(row) if row else None

    def list_tasks(self) -> List[Task]:
        cur = self.conn.execute("SELECT * FROM tasks ORDER BY id DESC")
        rows = cur.fetchall()
        return [self._row_to_task(r) for r in rows]

    def tasks_done_by_day(self):
        cur = self.conn.execute(
            "SELECT date(coalesce(completed_at, '1970-01-01')) as day, count(*) as cnt FROM tasks WHERE done=1 GROUP BY day ORDER BY day"
        )
        return [(r["day"], r["cnt"]) for r in cur.fetchall()]

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        if not row:
            return None
        created_at = datetime.fromisoformat(row["created_at"])
        completed_at = datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            created_at=created_at,
            completed_at=completed_at,
            done=bool(row["done"])
        )

    def close(self):
        self.conn.close()
