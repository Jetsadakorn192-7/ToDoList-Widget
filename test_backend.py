import unittest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from app.core.task import Task, Priority, Status

# ─── In-memory fake storage (no file I/O) ────────────────────────────────────

_fake_db: list[dict] = []
_counter: int = 0


def _reset():
    global _fake_db, _counter
    _fake_db = []
    _counter = 0


def _mock_load() -> list[Task]:
    tasks = []
    for item in _fake_db:
        d = dict(item)
        d["priority"] = Priority(d["priority"])
        d["status"]   = Status(d["status"])
        tasks.append(Task(**d))
    return tasks


def _mock_save(tasks: list[Task]) -> None:
    global _fake_db
    _fake_db = [{
        "id": t.id, "title": t.title, "description": t.description,
        "priority": t.priority.value, "status": t.status.value,
        "created_at": t.created_at, "due_at": t.due_at,
    } for t in tasks]


def _next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def _find(tasks, task_id):
    return next((t for t in tasks if t.id == task_id), None)


# ─── Manager functions (in-memory) ───────────────────────────────────────────

def add_task(title, description="", priority=Priority.MEDIUM, due_at=None):
    tasks = _mock_load()
    task = Task(id=_next_id(), title=title, description=description,
                priority=priority, due_at=due_at)
    tasks.append(task)
    _mock_save(tasks)
    return task

def get_all_tasks():
    return sorted(_mock_load(), key=lambda t: t.id)

def get_by_status(status):
    return [t for t in _mock_load() if t.status == status]

def get_by_priority(priority):
    return [t for t in _mock_load() if t.priority == priority]

def search(keyword):
    kw = keyword.lower()
    return [t for t in _mock_load()
            if kw in t.title.lower() or kw in t.description.lower()]

def update_status(task_id, status):
    tasks = _mock_load()
    task = _find(tasks, task_id)
    if not task: raise ValueError(f"Task #{task_id} not found")
    task.status = status
    _mock_save(tasks)
    return task

def update_priority(task_id, priority):
    tasks = _mock_load()
    task = _find(tasks, task_id)
    if not task: raise ValueError(f"Task #{task_id} not found")
    task.priority = priority
    _mock_save(tasks)
    return task

def edit_task(task_id, title=None, description=None,
              priority=None, status=None, due_at=None):
    tasks = _mock_load()
    task = _find(tasks, task_id)
    if not task: raise ValueError(f"Task #{task_id} not found")
    if title       is not None: task.title       = title
    if description is not None: task.description = description
    if priority    is not None: task.priority    = priority
    if status      is not None: task.status      = status
    if due_at      is not None: task.due_at      = due_at
    _mock_save(tasks)
    return task

def delete_task(task_id):
    tasks = _mock_load()
    new = [t for t in tasks if t.id != task_id]
    if len(new) == len(tasks): raise ValueError(f"Task #{task_id} not found")
    _mock_save(new)

def delete_all_tasks():
    count = len(_mock_load())
    _mock_save([])
    return count

def clear_done():
    tasks = _mock_load()
    new = [t for t in tasks if t.status != Status.DONE]
    removed = len(tasks) - len(new)
    _mock_save(new)
    return removed


# ═══════════════════════════════════════════════════════════════════════════════
# Test cases
# ═══════════════════════════════════════════════════════════════════════════════

class Base(unittest.TestCase):
    def setUp(self):
        _reset()


class TestTaskModel(Base):

    def test_default_values(self):
        t = Task(id=1, title="test")
        self.assertEqual(t.priority, Priority.MEDIUM)
        self.assertEqual(t.status,   Status.NOT_STARTED)
        self.assertEqual(t.description, "")
        self.assertIsNone(t.due_at)

    def test_created_at_auto(self):
        t = Task(id=1, title="test")
        self.assertTrue(len(t.created_at) > 0)

    def test_priority_values(self):
        self.assertEqual(Priority.HIGH.value,   "High")
        self.assertEqual(Priority.MEDIUM.value, "Medium")
        self.assertEqual(Priority.LOW.value,    "Low")

    def test_status_values(self):
        self.assertEqual(Status.NOT_STARTED.value, "Not Started")
        self.assertEqual(Status.IN_PROGRESS.value, "In Progress")
        self.assertEqual(Status.PENDING.value,     "Pending")
        self.assertEqual(Status.DONE.value,        "Completed")

    def test_can_update_priority(self):
        t = Task(id=1, title="test")
        t.priority = Priority.HIGH
        self.assertEqual(t.priority, Priority.HIGH)

    def test_can_update_status(self):
        t = Task(id=1, title="test")
        t.status = Status.IN_PROGRESS
        self.assertEqual(t.status, Status.IN_PROGRESS)


class TestAddTask(Base):

    def test_basic(self):
        t = add_task("ทำรายงาน")
        self.assertEqual(t.title, "ทำรายงาน")
        self.assertEqual(t.id, 1)

    def test_all_fields(self):
        t = add_task("deploy", description="push to prod",
                     priority=Priority.HIGH, due_at="2026-06-01")
        self.assertEqual(t.description, "push to prod")
        self.assertEqual(t.priority, Priority.HIGH)
        self.assertEqual(t.due_at, "2026-06-01")

    def test_id_increments(self):
        ids = [add_task(f"task {i}").id for i in range(3)]
        self.assertEqual(ids, [1, 2, 3])

    def test_id_no_repeat_after_delete(self):
        add_task("task 1")
        add_task("task 2")
        delete_task(2)
        t3 = add_task("task 3")
        self.assertEqual(t3.id, 3)  # must NOT reuse id=2


class TestGetFilter(Base):

    def setUp(self):
        super().setUp()
        add_task("งาน A", priority=Priority.HIGH)
        add_task("งาน B", priority=Priority.LOW)
        add_task("งาน C", priority=Priority.HIGH)

    def test_get_all(self):
        self.assertEqual(len(get_all_tasks()), 3)

    def test_filter_priority(self):
        high = get_by_priority(Priority.HIGH)
        self.assertEqual(len(high), 2)
        self.assertTrue(all(t.priority == Priority.HIGH for t in high))

    def test_filter_status_default(self):
        result = get_by_status(Status.NOT_STARTED)
        self.assertEqual(len(result), 3)

    def test_filter_status_after_update(self):
        tasks = get_all_tasks()
        update_status(tasks[0].id, Status.IN_PROGRESS)
        self.assertEqual(len(get_by_status(Status.IN_PROGRESS)), 1)


class TestSearch(Base):

    def setUp(self):
        super().setUp()
        add_task("ทำรายงาน Q2", description="รวบรวมข้อมูลยอดขาย")
        add_task("ประชุมทีม")
        add_task("deploy production", description="push to prod server")

    def test_by_title(self):
        self.assertEqual(len(search("รายงาน")), 1)

    def test_by_description(self):
        self.assertEqual(len(search("prod server")), 1)

    def test_case_insensitive(self):
        self.assertEqual(len(search("DEPLOY")), 1)
        self.assertEqual(len(search("deploy")), 1)

    def test_no_result(self):
        self.assertEqual(search("xyz_notexist"), [])


class TestEditTask(Base):

    def setUp(self):
        super().setUp()
        self.task = add_task("งานเดิม", priority=Priority.LOW)

    def test_edit_title_only(self):
        updated = edit_task(self.task.id, title="งานใหม่")
        self.assertEqual(updated.title, "งานใหม่")
        self.assertEqual(updated.priority, Priority.LOW)  # unchanged

    def test_edit_multiple_fields(self):
        updated = edit_task(self.task.id, title="updated",
                            priority=Priority.HIGH, status=Status.IN_PROGRESS)
        self.assertEqual(updated.title,    "updated")
        self.assertEqual(updated.priority, Priority.HIGH)
        self.assertEqual(updated.status,   Status.IN_PROGRESS)

    def test_not_found(self):
        with self.assertRaises(ValueError):
            edit_task(999, title="x")


class TestUpdateFields(Base):

    def setUp(self):
        super().setUp()
        self.task = add_task("งานทดสอบ")

    def test_status_workflow(self):
        update_status(self.task.id, Status.IN_PROGRESS)
        self.assertEqual(get_all_tasks()[0].status, Status.IN_PROGRESS)
        update_status(self.task.id, Status.DONE)
        self.assertEqual(get_all_tasks()[0].status, Status.DONE)

    def test_priority_persisted(self):
        update_priority(self.task.id, Priority.HIGH)
        self.assertEqual(get_all_tasks()[0].priority, Priority.HIGH)

    def test_status_not_found(self):
        with self.assertRaises(ValueError):
            update_status(999, Status.DONE)

    def test_priority_not_found(self):
        with self.assertRaises(ValueError):
            update_priority(999, Priority.HIGH)


class TestDelete(Base):

    def setUp(self):
        super().setUp()
        add_task("งาน 1")
        add_task("งาน 2")
        add_task("งาน 3")

    def test_delete_single(self):
        delete_task(2)
        ids = [t.id for t in get_all_tasks()]
        self.assertNotIn(2, ids)
        self.assertEqual(len(ids), 2)

    def test_delete_not_found(self):
        with self.assertRaises(ValueError):
            delete_task(999)

    def test_delete_all(self):
        count = delete_all_tasks()
        self.assertEqual(count, 3)
        self.assertEqual(get_all_tasks(), [])

    def test_clear_done(self):
        update_status(1, Status.DONE)
        update_status(3, Status.DONE)
        removed = clear_done()
        self.assertEqual(removed, 2)
        remaining = get_all_tasks()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].id, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)