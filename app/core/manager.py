from datetime import datetime
from app.core.task import Task, Priority, Status
from app.core.storage import load_tasks, save_tasks


def _next_id(tasks: list[Task]) -> int:
    """Return the next available ID using a persistent counter.
    The counter only increments, so IDs never repeat even after deletions.
    """
    from pathlib import Path
    counter_file = Path(__file__).parent / "_id_counter.txt"
    current = int(counter_file.read_text()) if counter_file.exists() else 0
    next_id = current + 1
    counter_file.write_text(str(next_id))
    return next_id


def _find(tasks: list[Task], task_id: int) -> Task | None:
    """Return the task matching task_id, or None if not found."""
    return next((t for t in tasks if t.id == task_id), None)


def _parse_dt(value: str) -> datetime:
    """Parse ISO date string to datetime object."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: '{value}'")


# ─── Create ───────────────────────────────────────────────────────────────────

def add_task(
    title: str,
    description: str = "",
    priority: Priority = Priority.MEDIUM,
    due_at: str | None = None,
) -> Task:
    """Create a new task and persist it.
    Status defaults to NOT_STARTED.
    Returns the newly created Task.
    """
    tasks = load_tasks()
    task = Task(
        id=_next_id(tasks),
        title=title,
        description=description,
        priority=priority,
        due_at=due_at,
    )
    tasks.append(task)
    save_tasks(tasks)
    return task


# ─── Read ─────────────────────────────────────────────────────────────────────

def get_all_tasks() -> list[Task]:
    """Return every task sorted by ID."""
    return sorted(load_tasks(), key=lambda t: t.id)


def get_by_status(status: Status) -> list[Task]:
    """Return tasks that match the given status."""
    return [t for t in load_tasks() if t.status == status]


def get_by_priority(priority: Priority) -> list[Task]:
    """Return tasks that match the given priority."""
    return [t for t in load_tasks() if t.priority == priority]


def get_by_date(year: int, month: int | None = None, day: int | None = None) -> list[Task]:
    """Return tasks filtered by created_at date.

    - get_by_date(2026)          → รายปี
    - get_by_date(2026, 6)       → รายเดือน
    - get_by_date(2026, 6, 15)   → รายวัน
    """
    result = []
    for t in load_tasks():
        try:
            dt = _parse_dt(t.created_at)
        except ValueError:
            continue
        if dt.year != year:
            continue
        if month is not None and dt.month != month:
            continue
        if day is not None and dt.day != day:
            continue
        result.append(t)
    return sorted(result, key=lambda t: t.created_at)


def get_today() -> list[Task]:
    """Return tasks created today."""
    now = datetime.now()
    return get_by_date(now.year, now.month, now.day)


def get_this_month() -> list[Task]:
    """Return tasks created this month."""
    now = datetime.now()
    return get_by_date(now.year, now.month)


def get_this_year() -> list[Task]:
    """Return tasks created this year."""
    return get_by_date(datetime.now().year)


def search(keyword: str) -> list[Task]:
    """Return tasks whose title or description contains the keyword (case-insensitive)."""
    kw = keyword.lower()
    return [
        t for t in load_tasks()
        if kw in t.title.lower() or kw in t.description.lower()
    ]


# ─── Update ───────────────────────────────────────────────────────────────────

def update_status(task_id: int, status: Status) -> Task:
    """Change the status of a task.
    Raises ValueError if the task is not found.
    """
    tasks = load_tasks()
    task = _find(tasks, task_id)
    if task is None:
        raise ValueError(f"Task #{task_id} not found")
    task.status = status
    save_tasks(tasks)
    return task


def update_priority(task_id: int, priority: Priority) -> Task:
    """Change the priority of a task.
    Raises ValueError if the task is not found.
    """
    tasks = load_tasks()
    task = _find(tasks, task_id)
    if task is None:
        raise ValueError(f"Task #{task_id} not found")
    task.priority = priority
    save_tasks(tasks)
    return task


def edit_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: Priority | None = None,
    status: Status | None = None,
    due_at: str | None = None,
) -> Task:
    """Update one or more fields of an existing task.
    Only fields that are explicitly passed will be changed.
    Raises ValueError if the task is not found.
    """
    tasks = load_tasks()
    task = _find(tasks, task_id)
    if task is None:
        raise ValueError(f"Task #{task_id} not found")

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if priority is not None:
        task.priority = priority
    if status is not None:
        task.status = status
    if due_at is not None:
        task.due_at = due_at

    save_tasks(tasks)
    return task


# ─── Delete ───────────────────────────────────────────────────────────────────

def delete_task(task_id: int) -> None:
    """Permanently remove a single task by ID.
    Raises ValueError if the task is not found.
    """
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t.id != task_id]
    if len(new_tasks) == len(tasks):
        raise ValueError(f"Task #{task_id} not found")
    save_tasks(new_tasks)


def delete_all_tasks() -> int:
    """Remove every task.
    Returns the number of tasks deleted.
    """
    tasks = load_tasks()
    count = len(tasks)
    save_tasks([])
    return count


def clear_done() -> int:
    """Remove all tasks with status DONE.
    Returns the number of tasks removed.
    """
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t.status != Status.DONE]
    removed = len(tasks) - len(new_tasks)
    save_tasks(new_tasks)
    return removed