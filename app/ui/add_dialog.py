"""
app/ui/add_dialog.py — Add / Edit dialog v2
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit,
    QComboBox, QPushButton
)
from PyQt6.QtCore import Qt

from app.core.task import Priority, Status, Task
from app.core.manager import add_task, edit_task


class AddDialog(QDialog):
    def __init__(self, parent=None, task: Task | None = None):
        super().__init__(parent)
        self._task    = task
        self._is_edit = task is not None
        self.setObjectName("addDialog")
        self.setWindowTitle("Edit Task" if self._is_edit else "New Task")
        self.setFixedWidth(340)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )
        self._build()
        if self._is_edit:
            self._populate()

    def _build(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 24, 24, 24)
        v.setSpacing(14)

        heading = QLabel("Edit Task" if self._is_edit else "New Task")
        heading.setObjectName("dialogHeading")
        v.addWidget(heading)

        # Title
        v.addWidget(self._lbl("Title *"))
        self.inp_title = QLineEdit()
        self.inp_title.setObjectName("dialogInput")
        self.inp_title.setPlaceholderText("Task title...")
        self.inp_title.setFixedHeight(36)
        v.addWidget(self.inp_title)

        # Description
        v.addWidget(self._lbl("Description"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setObjectName("dialogTextArea")
        self.inp_desc.setPlaceholderText("Details...")
        self.inp_desc.setFixedHeight(72)
        v.addWidget(self.inp_desc)

        # Priority + Status
        row = QHBoxLayout()
        row.setSpacing(12)

        col_p = QVBoxLayout()
        col_p.addWidget(self._lbl("Priority"))
        self.sel_priority = QComboBox()
        self.sel_priority.setObjectName("dialogSelect")
        self.sel_priority.setFixedHeight(36)
        for p in Priority:
            self.sel_priority.addItem(p.value.capitalize(), p)
        self.sel_priority.setCurrentIndex(1)
        col_p.addWidget(self.sel_priority)

        col_s = QVBoxLayout()
        col_s.addWidget(self._lbl("Status"))
        self.sel_status = QComboBox()
        self.sel_status.setObjectName("dialogSelect")
        self.sel_status.setFixedHeight(36)
        for s in Status:
            self.sel_status.addItem(s.value, s)
        col_s.addWidget(self.sel_status)

        row.addLayout(col_p)
        row.addLayout(col_s)
        v.addLayout(row)

        # Deadline
        v.addWidget(self._lbl("Deadline (YYYY-MM-DD)"))
        self.inp_due = QLineEdit()
        self.inp_due.setObjectName("dialogInput")
        self.inp_due.setPlaceholderText("e.g. 2026-12-31")
        self.inp_due.setFixedHeight(36)
        v.addWidget(self.inp_due)

        # Error
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("dialogError")
        v.addWidget(self.lbl_error)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btnCancel")
        btn_cancel.setFixedHeight(36)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save" if self._is_edit else "Add Task")
        btn_save.setObjectName("btnSave")
        btn_save.setFixedHeight(36)
        btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        v.addLayout(btn_row)

    def _lbl(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("dialogLabel")
        return lbl

    def _populate(self):
        t = self._task
        self.inp_title.setText(t.title)
        self.inp_desc.setPlainText(t.description)

        idx = self.sel_priority.findData(t.priority)
        if idx >= 0:
            self.sel_priority.setCurrentIndex(idx)

        idx = self.sel_status.findData(t.status)
        if idx >= 0:
            self.sel_status.setCurrentIndex(idx)

        if t.due_at:
            self.inp_due.setText(t.due_at[:10])

    def _save(self):
        title = self.inp_title.text().strip()
        if not title:
            self.lbl_error.setText("Please enter a title.")
            return

        description = self.inp_desc.toPlainText().strip()
        priority    = self.sel_priority.currentData()
        status      = self.sel_status.currentData()
        due_at      = self.inp_due.text().strip() or None

        if self._is_edit:
            edit_task(
                self._task.id,
                title=title, description=description,
                priority=priority, status=status, due_at=due_at,
            )
        else:
            add_task(
                title=title, description=description,
                priority=priority, due_at=due_at,
            )
        self.accept()