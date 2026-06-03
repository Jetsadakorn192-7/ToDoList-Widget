"""
app/ui/task_item.py
"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from app.core.task import Task, Priority, Status
from datetime import date


PRIORITY_BADGE = {
    Priority.HIGH:   ("↑ High",   "badgeHigh"),
    Priority.MEDIUM: ("● Medium", "badgeMedium"),
    Priority.LOW:    ("↓ Low",    "badgeLow"),
}

STATUS_BADGE = {
    Status.NOT_STARTED: ("No Status",   "badgeNoStatus"),
    Status.IN_PROGRESS: ("In Progress", "badgeInProgress"),
    Status.PENDING:     ("Pending",     "badgePending"),
    Status.DONE:        ("Done",        "badgeDone"),
}

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
        outer.setContentsMargins(20, 14, 16, 14)
        outer.setSpacing(10)

        # ── Body (left, stretchy) ─────────────────────────────────────────
        body = QVBoxLayout()
        body.setSpacing(3)

        title = QLabel(t.title)
        title.setObjectName("taskTitleDone" if done else "taskTitle")
        body.addWidget(title)

        if t.description:
            desc = QLabel(t.description)
            desc.setObjectName("taskDesc")
            desc.setWordWrap(True)
            desc.setMaximumWidth(220)
            body.addWidget(desc)

        # Meta row: [priority] [status] [date] stretch [···]
        meta = QHBoxLayout()
        meta.setSpacing(6)
        meta.setContentsMargins(0, 4, 0, 0)

        pri_text, pri_cls = PRIORITY_BADGE[t.priority]
        pri_lbl = QLabel(pri_text)
        pri_lbl.setObjectName(pri_cls)
        meta.addWidget(pri_lbl)

        st_text, st_cls = STATUS_BADGE.get(t.status, ("No Status", "badgeNoStatus"))
        st_lbl = QLabel(st_text)
        st_lbl.setObjectName(st_cls)
        meta.addWidget(st_lbl)

        due_lbl = QLabel(_due_text(t.due_at))
        due_lbl.setObjectName("dueLabel")
        meta.addWidget(due_lbl)

        meta.addStretch()

        btn_menu = QPushButton("···")
        btn_menu.setObjectName("btnDots")
        btn_menu.setFixedSize(24, 20)
        btn_menu.clicked.connect(self._show_menu)
        meta.addWidget(btn_menu)

        body.addLayout(meta)
        outer.addLayout(body, stretch=1)

        # ── Circle check (right, top-aligned) ────────────────────────────
        check = QPushButton()
        check.setObjectName("checkDone" if done else "checkPending")
        check.setFixedSize(20, 20)
        check.setToolTip("เปลี่ยนสถานะ")
        check.clicked.connect(lambda: self._on_status(t, STATUS_NEXT[t.status]))
        outer.addWidget(check, alignment=Qt.AlignmentFlag.AlignTop)

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
