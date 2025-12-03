from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    done: bool = False

    def mark_done(self, when: Optional[datetime] = None):
        if self.done:
            return
        self.done = True
        self.completed_at = when or datetime.now()

    def mark_undone(self):
        self.done = False
        self.completed_at = None
