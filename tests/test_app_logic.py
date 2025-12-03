from app.db import DB
from app.models import Task
import tempfile, os

def test_tasks_done_by_day_empty_then_done():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = tmp.name
    tmp.close()
    db = DB(db_path=path)
    assert db.list_tasks() == []
    t = Task(title="a")
    db.add_task(t)
    assert db.tasks_done_by_day() == []
    t.mark_done()
    db.update_task(t)
    data = db.tasks_done_by_day()
    assert len(data) >= 1
    db.close()
    os.remove(path)