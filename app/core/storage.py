import json
from pathlib import Path
from app.core.task import Task, Priority, Status

# Data file lives in the project root (same level as main.py)
DATA_FILE = Path(__file__).parent.parent.parent / "todo_data.json"


def load_tasks() -> list[Task]:
    """Load all tasks from the JSON file.
    Returns an empty list if the file does not exist yet.
    Converts raw dicts back into typed Task objects.
    """
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw: list[dict] = json.load(f)

    tasks = []
    for item in raw:
        # Convert string values back into Enum types
        item["priority"] = Priority(item["priority"])
        item["status"]   = Status(item["status"])
        tasks.append(Task(**item))
    return tasks


def save_tasks(tasks: list[Task]) -> None:
    """Persist the task list to the JSON file.
    Enum values are stored as their string value for readability.
    """
    data = []
    for t in tasks:
        record = {
            "id":          t.id,
            "title":       t.title,
            "description": t.description,
            "priority":    t.priority.value,   # e.g. "high"
            "status":      t.status.value,     # e.g. "กำลังทำ"
            "created_at":  t.created_at,
            "due_at":      t.due_at,
        }
        data.append(record)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)