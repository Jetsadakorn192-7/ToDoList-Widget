"""
app/ui/main_window.py — Main floating window
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor

from app.ui.task_item import TaskItem
from app.ui.add_dialog import AddDialog
from app.core import (
    get_all_tasks, get_by_status, search,
    delete_task, clear_done, update_status,
    Task, Status
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._drag_pos = QPoint()
        self._current_filter = "all"
        self._setup_window()
        self._build_ui()
        self._start_clock()
        self.refresh()

    # ─── Window setup ─────────────────────────────────────────────────────────

    def _setup_window(self):
        """Configure frameless floating window."""
        self.setWindowTitle("Todo-everyday")
        self.setFixedWidth(364)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    # ─── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        """Build the full widget layout."""
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_titlebar())
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_filter_bar())
        layout.addWidget(self._build_task_list())
        layout.addWidget(self._build_footer())

    def _build_titlebar(self) -> QWidget:
        """macOS-style titlebar with traffic light dots."""
        bar = QWidget()
        bar.setObjectName("titlebar")
        bar.setFixedHeight(38)
        h = QHBoxLayout(bar)
        h.setContentsMargins(12, 0, 12, 0)

        # Traffic light dots
        dots = QWidget()
        dots_h = QHBoxLayout(dots)
        dots_h.setContentsMargins(0, 0, 0, 0)
        dots_h.setSpacing(6)
        for color in ["#ff5f57", "#febc2e", "#27c840"]:
            dot = QLabel()
            dot.setFixedSize(11, 11)
            dot.setStyleSheet(
                f"background:{color}; border-radius:5px;"
            )
            dots_h.addWidget(dot)

        title = QLabel("Todo")
        title.setObjectName("winTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        h.addWidget(dots)
        h.addStretch()
        h.addWidget(title)
        h.addStretch()
        h.addSpacing(40)
        return bar

    def _build_header(self) -> QWidget:
        """Clock + search bar + add button."""
        header = QWidget()
        header.setObjectName("header")
        v = QVBoxLayout(header)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(8)

        # Clock row
        clock_row = QHBoxLayout()
        self.lbl_time = QLabel()
        self.lbl_time.setObjectName("clock")
        self.lbl_date = QLabel()
        self.lbl_date.setObjectName("clockDate")
        clock_row.addWidget(self.lbl_time)
        clock_row.addWidget(self.lbl_date)
        clock_row.addStretch()

        # Search + add row
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("ค้นหางาน...")
        self.search_input.textChanged.connect(self._on_search)

        btn_add = QPushButton("+ เพิ่ม")
        btn_add.setObjectName("btnAdd")
        btn_add.clicked.connect(self._open_add_dialog)

        search_row.addWidget(self.search_input)
        search_row.addWidget(btn_add)

        v.addLayout(clock_row)
        v.addLayout(search_row)
        return header

    def _build_filter_bar(self) -> QWidget:
        """Status filter chips."""
        bar = QWidget()
        bar.setObjectName("filterBar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(14, 6, 14, 6)
        h.setSpacing(6)

        self._filter_btns = {}
        filters = [
            ("all",                  "ทั้งหมด"),
            (Status.NOT_STARTED,     "ยังไม่เริ่ม"),
            (Status.IN_PROGRESS,     "กำลังทำ"),
            (Status.PENDING,         "รอทำ"),
            (Status.DONE,            "เสร็จสิ้น"),
        ]

        for key, label in filters:
            btn = QPushButton(label)
            btn.setObjectName("filterChip")
            btn.setCheckable(True)
            btn.setChecked(key == "all")
            btn.clicked.connect(lambda _, k=key: self._set_filter(k))
            self._filter_btns[key] = btn
            h.addWidget(btn)

        h.addStretch()
        return bar

    def _build_task_list(self) -> QScrollArea:
        """Scrollable task list area."""
        scroll = QScrollArea()
        scroll.setObjectName("taskScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.task_container = QWidget()
        self.task_container.setObjectName("taskContainer")
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setContentsMargins(0, 4, 0, 4)
        self.task_layout.setSpacing(0)
        self.task_layout.addStretch()

        scroll.setWidget(self.task_container)
        scroll.setMinimumHeight(200)
        scroll.setMaximumHeight(380)
        return scroll

    def _build_footer(self) -> QWidget:
        """Summary stats + action buttons."""
        footer = QWidget()
        footer.setObjectName("footer")
        h = QHBoxLayout(footer)
        h.setContentsMargins(14, 8, 14, 8)

        self.lbl_stats = QLabel()
        self.lbl_stats.setObjectName("footerStats")

        btn_clear = QPushButton()
        btn_clear.setObjectName("btnIcon")
        btn_clear.setToolTip("ลบที่เสร็จแล้ว")
        btn_clear.setText("🗑")
        btn_clear.clicked.connect(self._clear_done)

        h.addWidget(self.lbl_stats)
        h.addStretch()
        h.addWidget(btn_clear)
        return footer

    # ─── Clock ────────────────────────────────────────────────────────────────

    def _start_clock(self):
        """Update clock every second."""
        self._tick()
        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(1000)

    def _tick(self):
        from datetime import datetime
        now = datetime.now()
        thai_days   = ["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"]
        thai_months = ["","มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม",
                       "มิถุนายน","กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม",
                       "พฤศจิกายน","ธันวาคม"]
        self.lbl_time.setText(now.strftime("%H:%M:%S"))
        self.lbl_date.setText(
            f"วัน{thai_days[now.weekday()]}ที่ {now.day} "
            f"{thai_months[now.month]} พ.ศ. {now.year + 543}"
        )

    # ─── Task list rendering ──────────────────────────────────────────────────

    def refresh(self):
        """Reload and re-render the task list."""
        keyword = self.search_input.text().strip() if hasattr(self, "search_input") else ""

        if keyword:
            tasks = search(keyword)
        elif self._current_filter == "all":
            tasks = get_all_tasks()
        else:
            tasks = get_by_status(self._current_filter)

        # Clear existing items (keep the trailing stretch)
        while self.task_layout.count() > 1:
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Insert fresh task items
        for task in tasks:
            item = TaskItem(task, self._on_status_change, self._on_edit, self._on_delete)
            self.task_layout.insertWidget(self.task_layout.count() - 1, item)

        # Update footer stats
        all_tasks = get_all_tasks()
        pending = sum(1 for t in all_tasks if t.status != Status.DONE)
        done    = sum(1 for t in all_tasks if t.status == Status.DONE)
        self.lbl_stats.setText(f"{pending} รอทำ · {done} เสร็จแล้ว")

    # ─── Event handlers ───────────────────────────────────────────────────────

    def _set_filter(self, key):
        self._current_filter = key
        for k, btn in self._filter_btns.items():
            btn.setChecked(k == key)
        self.refresh()

    def _on_search(self):
        self.refresh()

    def _open_add_dialog(self):
        dialog = AddDialog(self)
        if dialog.exec():
            self.refresh()

    def _on_status_change(self, task: Task, new_status: Status):
        update_status(task.id, new_status)
        self.refresh()

    def _on_edit(self, task: Task):
        dialog = AddDialog(self, task)
        if dialog.exec():
            self.refresh()

    def _on_delete(self, task: Task):
        delete_task(task.id)
        self.refresh()

    def _clear_done(self):
        clear_done()
        self.refresh()

    # ─── Drag to move (frameless window) ──────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)