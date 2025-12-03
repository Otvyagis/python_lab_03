import tempfile
from app.db import DB
from app.models import Task
import os

def test_db_add_get_delete():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = tmp.name
    tmp.close()
    db = DB(db_path=path)
    t = Task(title="db test", description="desc")
    t = db.add_task(t)
    assert t.id is not None
    fetched = db.get_task(t.id)
    assert fetched.title == "db test"
    db.delete_task(t.id)
    assert db.get_task(t.id) is None
    db.close()
    os.remove(path)

def test_db_update():
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = tmp.name
    tmp.close()
    db = DB(db_path=path)
    t = Task(title="to update")
    t = db.add_task(t)
    t.title = "updated"
    db.update_task(t)
    new = db.get_task(t.id)
    assert new.title == "updated"
    db.close()
    os.remove(path)
