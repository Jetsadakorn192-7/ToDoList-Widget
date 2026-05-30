# Todo Widget

A minimal floating desktop Todo app for macOS built with Python and PyQt6.

---

## Preview

> Floating window that stays on top of your desktop — manage tasks without switching apps.

**Design Reference:** [View on Figma](https://www.figma.com/proto/4XZfHcKiGM4JE0I8Na9X6e/ToDoList-Wedget?page-id=0%3A1&node-id=41-4&viewport=214%2C190%2C1.57&t=nj58Z2jxw6AhDki7-1&scaling=min-zoom&content-scaling=fixed&starting-point-node-id=41%3A4)
---

## Features

- Floating window that stays on top of all windows
- Real-time clock with day and date
- Add / edit / delete tasks
- Priority levels — High, Medium, Low
- Status tracking — No Status, In Progress, Pending, Done
- Deadline support
- Filter by status via tab bar
- Search by title or description
- One-click status cycling
- Clean minimal UI

---

## Requirements

- macOS
- Python 3.10+
- PyQt6

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/Jetsadakorn192-7/todo-widget.git
cd todo-widget

# 2. Install dependencies
pip install PyQt6

# 3. Run
python3 main.py
```

---

## Project Structure

```
todo-widget/
├── main.py                  ← entry point
│
├── app/
│   ├── core/
│   │   ├── __init__.py      ← exports all core functions
│   │   ├── task.py          ← Task model, Priority, Status enums
│   │   ├── storage.py       ← load / save JSON
│   │   └── manager.py       ← all business logic
│   │
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py   ← main floating window
│       ├── task_item.py     ← individual task row widget
│       └── add_dialog.py    ← add / edit task dialog
│
├── assets/
│   └── style.qss            ← stylesheet
│
├── tests/
│   └── test_backend.py      ← unit tests for core logic
│
├── todo_data.json            ← auto-generated, not tracked by git
├── requirements.txt
└── README.md
```

---

## Data Model

Each task stores:

| Field | Type | Description |
|---|---|---|
| `id` | int | Auto-incremented, never reused |
| `title` | str | Task title |
| `description` | str | Optional details |
| `priority` | Priority | `high` / `medium` / `low` |
| `status` | Status | `Not Started` / `In Progress` / `Pending` / `Completed` |
| `created_at` | str | ISO 8601 timestamp |
| `due_at` | str | Deadline date (optional) |

Data is stored locally in `todo_data.json` — no server, no internet required.

---

## Running Tests

```bash
python3 -m unittest tests/test_backend.py -v
```

---

## Tech Stack

- [Python 3](https://www.python.org/)
- [PyQt6](https://pypi.org/project/PyQt6/) — desktop UI framework
