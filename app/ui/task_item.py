"""
app/ui/task_item.py — Individual task row widget
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
    Priority.HIGH:   ("▲ high",   "badge-high"),
    Priority.MEDIUM: ("● medium", "badge-medium"),
    Priority.LOW:    ("▽ low",    "badge-low"),
}

STATUS_NEXT = {
    Status.NOT_STARTED: Status.IN_PROGRESS,
    Status.IN_PROGRESS: Status.DONE,
    Status.PENDING:     Status.IN_PROGRESS,
    Status.DONE:        Status.NOT_STARTED,
}


def _deadline_label(due_at: str | None) -> tuple[str, str]:
    """Return (text, css_class) for deadline display."""
    if not due_at:
        return "", ""
    try:
        dl   = date.fromisoformat(due_at[:10])
        diff = (dl - date.today()).days
        if diff < 0:
            return f"! เกินกำหนด {abs(diff)}วัน", "due-overdue"
        elif diff == 0:
            return "◷ วันนี้!", "due-today"
        elif diff <= 3:
            return f"◷ อีก {diff}วัน", "due-soon"
        else:
            return f"◷ {due_at[:10]}", "due-normal"
    except ValueError:
        return "", ""


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
        outer.setContentsMargins(14, 10, 14, 10)
        outer.setSpacing(10)

        # ── Check button ──────────────────────────────────────────────────
        check = QPushButton("✓" if done else "○")
        check.setObjectName("checkDone" if done else "checkPending")
        check.setFixedSize(20, 20)
        check.setToolTip("คลิกเพื่อเปลี่ยนสถานะ")
        check.clicked.connect(lambda: self._on_status(t, STATUS_NEXT[t.status]))
        outer.addWidget(check, alignment=Qt.AlignmentFlag.AlignTop)

        # ── Task body ─────────────────────────────────────────────────────
        body = QVBoxLayout()
        body.setSpacing(4)

        title = QLabel(t.title)
        title.setObjectName("taskTitleDone" if done else "taskTitle")
        title.setWordWrap(True)
        body.addWidget(title)

        # Description (if any)
        if t.description:
            desc = QLabel(t.description)
            desc.setObjectName("taskDesc")
            desc.setWordWrap(True)
            body.addWidget(desc)

        # Meta row: priority badge + status badge + deadline
        meta = QHBoxLayout()
        meta.setSpacing(6)
        meta.setContentsMargins(0, 0, 0, 0)

        pri_text, pri_class = PRIORITY_BADGE[t.priority]
        pri_lbl = QLabel(pri_text)
        pri_lbl.setObjectName(pri_class)
        meta.addWidget(pri_lbl)

        status_lbl = QLabel(t.status.value)
        status_lbl.setObjectName("badgeStatus")
        meta.addWidget(status_lbl)

        dl_text, dl_class = _deadline_label(t.due_at)
        if dl_text:
            dl_lbl = QLabel(dl_text)
            dl_lbl.setObjectName(dl_class)
            meta.addWidget(dl_lbl)

        meta.addStretch()
        body.addLayout(meta)
        outer.addLayout(body, stretch=1)

        # ── Right side: ID + action menu ──────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(4)
        right.setAlignment(Qt.AlignmentFlag.AlignTop)

        id_lbl = QLabel(f"#{t.id}")
        id_lbl.setObjectName("taskId")

        btn_menu = QPushButton("···")
        btn_menu.setObjectName("btnMenu")
        btn_menu.setFixedSize(24, 24)
        btn_menu.clicked.connect(self._show_menu)

        right.addWidget(id_lbl)
        right.addWidget(btn_menu)
        outer.addLayout(right)

    def _show_menu(self):
        """Context menu for task actions."""
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