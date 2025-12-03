from app.models import Task
from datetime import datetime, timedelta

def test_task_mark_done_and_undone():
    t = Task(title="Test")
    assert not t.done
    t.mark_done()
    assert t.done
    assert t.completed_at is not None
    saved_time = t.completed_at
    t.mark_undone()
    assert not t.done
    assert t.completed_at is None
    t.mark_done(when=datetime.now() - timedelta(days=1))
    assert t.completed_at < datetime.now()
