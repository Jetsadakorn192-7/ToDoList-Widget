import json
from pathlib import Path
from app.core.task import Task, Priority, Status

# Data file lives in the project root (same level as main.py)
DATA_FILE = Path(__file__).parent.parent.parent / "todo_data.json"


def load_tasks() -> list[Task]:
    if not DATA_FILE.exists():
        return []
    content = DATA_FILE.read_text(encoding="utf-8").strip()
    if not content:          # ไฟล์ว่างเปล่า
        return []
    raw: list[dict] = json.loads(content)

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