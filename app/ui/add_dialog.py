"""
app/ui/add_dialog.py — Add / Edit task dialog
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
        self._task     = task
        self._is_edit  = task is not None
        self.setObjectName("addDialog")
        self.setWindowTitle("แก้ไขงาน" if self._is_edit else "เพิ่มงานใหม่")
        self.setFixedWidth(320)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog
        )
        self._build()
        if self._is_edit:
            self._populate()

    def _build(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(12)

        # Dialog title
        heading = QLabel("แก้ไขงาน" if self._is_edit else "เพิ่มงานใหม่")
        heading.setObjectName("dialogHeading")
        v.addWidget(heading)

        # Title field
        v.addWidget(self._lbl("หัวข้อ *"))
        self.inp_title = QLineEdit()
        self.inp_title.setObjectName("dialogInput")
        self.inp_title.setPlaceholderText("ชื่องาน...")
        v.addWidget(self.inp_title)

        # Description field
        v.addWidget(self._lbl("รายละเอียด"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setObjectName("dialogTextArea")
        self.inp_desc.setPlaceholderText("รายละเอียดเพิ่มเติม...")
        self.inp_desc.setFixedHeight(72)
        v.addWidget(self.inp_desc)

        # Priority + Status row
        row = QHBoxLayout()
        row.setSpacing(10)

        col_pri = QVBoxLayout()
        col_pri.addWidget(self._lbl("Priority"))
        self.sel_priority = QComboBox()
        self.sel_priority.setObjectName("dialogSelect")
        for p in Priority:
            self.sel_priority.addItem(p.value, p)
        self.sel_priority.setCurrentIndex(1)  # medium default
        col_pri.addWidget(self.sel_priority)
        row.addLayout(col_pri)

        col_status = QVBoxLayout()
        col_status.addWidget(self._lbl("สถานะ"))
        self.sel_status = QComboBox()
        self.sel_status.setObjectName("dialogSelect")
        for s in Status:
            self.sel_status.addItem(s.value, s)
        col_status.addWidget(self.sel_status)
        row.addLayout(col_status)
        v.addLayout(row)

        # Deadline field
        v.addWidget(self._lbl("กำหนดส่ง (YYYY-MM-DD)"))
        self.inp_due = QLineEdit()
        self.inp_due.setObjectName("dialogInput")
        self.inp_due.setPlaceholderText("เช่น 2026-12-31")
        v.addWidget(self.inp_due)

        # Error label
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("dialogError")
        v.addWidget(self.lbl_error)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("ยกเลิก")
        btn_cancel.setObjectName("btnCancel")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("บันทึก" if self._is_edit else "เพิ่มงาน")
        btn_save.setObjectName("btnSave")
        btn_save.clicked.connect(self._save)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        v.addLayout(btn_row)

    def _lbl(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("dialogLabel")
        return lbl

    def _populate(self):
        """Pre-fill fields when editing an existing task."""
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
            self.lbl_error.setText("กรุณาใส่หัวข้องาน")
            return

        description = self.inp_desc.toPlainText().strip()
        priority    = self.sel_priority.currentData()
        status      = self.sel_status.currentData()
        due_at      = self.inp_due.text().strip() or None

        if self._is_edit:
            edit_task(
                self._task.id,
                title=title,
                description=description,
                priority=priority,
                status=status,
                due_at=due_at,
            )
        else:
            add_task(
                title=title,
                description=description,
                priority=priority,
                due_at=due_at,
            )

        self.accept()