"""
app/ui/task_item.py — Task row widget v2
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from app.core.task import Task, Priority, Status
from datetime import date


# Map priority to (badge text, QSS object name)
PRIORITY_BADGE = {
    Priority.HIGH:   ("↑ High",   "badgeHigh"),
    Priority.MEDIUM: ("● Medium", "badgeMedium"),
    Priority.LOW:    ("↓ Low",    "badgeLow"),
}

# Map status to QSS object name
STATUS_BADGE = {
    Status.NOT_STARTED: "badgeNoStatus",
    Status.IN_PROGRESS: "badgeInProgress",
    Status.PENDING:     "badgePending",
    Status.DONE:        "badgeDone",
}

# Clicking check cycles to the next logical status
STATUS_NEXT = {
    Status.NOT_STARTED: Status.IN_PROGRESS,
    Status.IN_PROGRESS: Status.DONE,
    Status.PENDING:     Status.IN_PROGRESS,
    Status.DONE:        Status.NOT_STARTED,
}


def _due_text(due_at: str | None) -> str:
    if not due_at:
        return "DD-MM-YYYY"
    try:
        dl   = date.fromisoformat(due_at[:10])
        diff = (dl - date.today()).days
        if diff < 0:
            return f"Overdue {abs(diff)}d"
        return dl.strftime("%d-%m-%Y")
    except ValueError:
        return due_at[:10]


class TaskItem(QWidget):
    def __init__(self, task: Task, on_status, on_edit, on_delete):
        super().__init__()
        self._task      = task
        self._on_status = on_status
        self._on_edit   = on_edit
        self._on_delete = on_delete
        self.setObjectName("taskItem")
        self._build()

    def _build(self):
        t    = self._task
        done = t.status == Status.DONE

        outer = QHBoxLayout(self)
        outer.setContentsMargins(20, 14, 20, 14)
        outer.setSpacing(12)

        # ── Check circle ──────────────────────────────────────────────────
        check = QPushButton("✓" if done else "")
        check.setObjectName("checkDone" if done else "checkPending")
        check.setFixedSize(20, 20)
        check.setToolTip("เปลี่ยนสถานะ")
        check.clicked.connect(
            lambda: self._on_status(t, STATUS_NEXT[t.status])
        )
        outer.addWidget(check, alignment=Qt.AlignmentFlag.AlignTop)

        # ── Body ──────────────────────────────────────────────────────────
        body = QVBoxLayout()
        body.setSpacing(3)

        title = QLabel(t.title)
        title.setObjectName("taskTitleDone" if done else "taskTitle")
        body.addWidget(title)

        if t.description:
            desc = QLabel(t.description)
            desc.setObjectName("taskDesc")
            desc.setMaximumWidth(240)
            body.addWidget(desc)

        # Meta row
        meta = QHBoxLayout()
        meta.setSpacing(6)
        meta.setContentsMargins(0, 4, 0, 0)

        pri_text, pri_class = PRIORITY_BADGE[t.priority]
        pri_lbl = QLabel(pri_text)
        pri_lbl.setObjectName(pri_class)
        meta.addWidget(pri_lbl)

        status_lbl = QLabel(t.status.value)
        status_lbl.setObjectName(STATUS_BADGE.get(t.status, "badgeNoStatus"))
        meta.addWidget(status_lbl)

        due_lbl = QLabel(_due_text(t.due_at))
        due_lbl.setObjectName("dueLabel")
        meta.addWidget(due_lbl)

        meta.addStretch()
        body.addLayout(meta)
        outer.addLayout(body, stretch=1)

        # ── Menu button ───────────────────────────────────────────────────
        btn_menu = QPushButton("···")
        btn_menu.setObjectName("btnDots")
        btn_menu.setFixedSize(28, 28)
        btn_menu.clicked.connect(self._show_menu)
        outer.addWidget(btn_menu, alignment=Qt.AlignmentFlag.AlignTop)

    def _show_menu(self):
        menu = QMenu(self)
        menu.setObjectName("taskMenu")

        act_edit   = QAction("✏  แก้ไข", self)
        act_delete = QAction("×  ลบ",    self)

        act_edit.triggered.connect(lambda: self._on_edit(self._task))
        act_delete.triggered.connect(lambda: self._on_delete(self._task))

        menu.addAction(act_edit)
        menu.addSeparator()
        menu.addAction(act_delete)
        menu.exec(self.cursor().pos())