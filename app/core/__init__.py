# Expose the most-used symbols so callers can write:
#   from app.core import Task, Priority, Status
#   from app.core import add_task, get_all_tasks

from .task import Task, Priority, Status
from .storage import load_tasks, save_tasks
from .manager import (
    add_task,
    get_all_tasks,
    get_by_status,
    get_by_priority,
    get_by_date,
    get_today,
    get_this_month,
    get_this_year,
    search,
    update_status,
    update_priority,
    edit_task,
    delete_task,
    delete_all_tasks,
    clear_done,
)