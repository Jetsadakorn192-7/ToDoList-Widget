from dataclasses import dataclass, field
from datetime import datetime 
from enum import Enum

class Priority(str, Enum):
    "Priority levels for tasks."
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class Status(str, Enum):
    "workflow status for tasks."
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"
    DONE = "Completed"

@dataclass
class Task:
    id: int                         # Unique identifier for the task
    title: str                      # Title of the task
    description: str = ""           # Optional description of the task
    priority: Priority = Priority.MEDIUM
    status: Status = Status.NOT_STARTED


    #Timestamps stored as ISO 8601 strings (YYYY-MM-DDTHH:MM:SS)
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
    due_at: str | None = None       # Deadline — None if not set



