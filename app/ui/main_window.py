"""
app/ui/main_window.py — Main window v2
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer, QPoint

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
        self._filter   = "all"
        self._setup_window()
        self._build_ui()
        self._start_clock()
        self.refresh()

    # ── Window ────────────────────────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowTitle("Todo")
        self.setFixedWidth(364)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        v = QVBoxLayout(root)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        v.addWidget(self._build_top())
        v.addWidget(self._build_tabs())
        v.addWidget(self._build_task_area())
        v.addWidget(self._build_footer())

    def _build_top(self) -> QWidget:
        """Header: title, date, search bar, + New button."""
        top = QWidget()
        top.setObjectName("top")
        v = QVBoxLayout(top)
        v.setContentsMargins(20, 20, 20, 14)
        v.setSpacing(0)

        # Title + New button row
        title_row = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        self.lbl_title = QLabel("Today's Task")
        self.lbl_title.setObjectName("heading")

        self.lbl_date = QLabel()
        self.lbl_date.setObjectName("subheading")

        title_col.addWidget(self.lbl_title)
        title_col.addWidget(self.lbl_date)

        btn_new = QPushButton("+ New")
        btn_new.setObjectName("btnNew")
        btn_new.setFixedHeight(36)
        btn_new.clicked.connect(self._open_add)

        title_row.addLayout(title_col)
        title_row.addStretch()
        title_row.addWidget(btn_new, alignment=Qt.AlignmentFlag.AlignTop)

        # Search box
        search_box = QWidget()
        search_box.setObjectName("searchBox")
        search_box.setFixedHeight(40)
        sb = QHBoxLayout(search_box)
        sb.setContentsMargins(12, 0, 12, 0)
        sb.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setObjectName("searchIcon")

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("search...")
        self.search_input.textChanged.connect(self.refresh)

        sb.addWidget(search_icon)
        sb.addWidget(self.search_input)

        v.addLayout(title_row)
        v.addSpacing(14)
        v.addWidget(search_box)
        return top

    def _build_tabs(self) -> QWidget:
        """Filter tab bar."""
        bar = QWidget()
        bar.setObjectName("tabBar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(20, 0, 20, 0)
        h.setSpacing(0)

        self._tabs: dict = {}
        items = [
            ("all",              "All"),
            (Status.IN_PROGRESS, "In Progress"),
            (Status.PENDING,     "Pending"),
            (Status.NOT_STARTED, "No Status"),
            (Status.DONE,        "Done"),
        ]
        for key, label in items:
            btn = QPushButton(label)
            btn.setObjectName("tab")
            btn.setCheckable(True)
            btn.setChecked(key == "all")
            btn.clicked.connect(lambda _, k=key: self._set_filter(k))
            self._tabs[key] = btn
            h.addWidget(btn)

        h.addStretch()
        return bar

    def _build_task_area(self) -> QScrollArea:
        """Scrollable task list."""
        scroll = QScrollArea()
        scroll.setObjectName("taskScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.task_container = QWidget()
        self.task_container.setObjectName("taskContainer")
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setContentsMargins(0, 0, 0, 0)
        self.task_layout.setSpacing(0)
        self.task_layout.addStretch()

        scroll.setWidget(self.task_container)
        scroll.setMinimumHeight(200)
        scroll.setMaximumHeight(420)
        return scroll

    def _build_footer(self) -> QWidget:
        """Footer: stats + trash."""
        footer = QWidget()
        footer.setObjectName("footer")
        h = QHBoxLayout(footer)
        h.setContentsMargins(20, 10, 20, 10)

        self.lbl_stats = QLabel()
        self.lbl_stats.setObjectName("footerStats")

        btn_trash = QPushButton("🗑")
        btn_trash.setObjectName("btnTrash")
        btn_trash.setFixedSize(32, 32)
        btn_trash.setToolTip("ลบที่เสร็จแล้ว")
        btn_trash.clicked.connect(self._clear_done)

        h.addWidget(self.lbl_stats)
        h.addStretch()
        h.addWidget(btn_trash)
        return footer

    # ── Clock ─────────────────────────────────────────────────────────────────

    def _start_clock(self):
        self._tick()
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(60000)

    def _tick(self):
        from datetime import datetime
        now = datetime.now()
        days   = ["Monday","Tuesday","Wednesday","Thursday",
                  "Friday","Saturday","Sunday"]
        months = ["","January","February","March","April","May","June",
                  "July","August","September","October","November","December"]
        self.lbl_date.setText(
            f"{days[now.weekday()]}, {now.day} {months[now.month]}"
        )

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh(self):
        keyword = self.search_input.text().strip() if hasattr(self, "search_input") else ""

        if keyword:
            tasks = search(keyword)
        elif self._filter == "all":
            tasks = get_all_tasks()
        else:
            tasks = get_by_status(self._filter)

        # Clear old task widgets (keep trailing stretch)
        while self.task_layout.count() > 1:
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for task in tasks:
            w = TaskItem(task, self._on_status, self._on_edit, self._on_delete)
            self.task_layout.insertWidget(self.task_layout.count() - 1, w)

        # Update footer
        all_tasks = get_all_tasks()
        total = len(all_tasks)
        done  = sum(1 for t in all_tasks if t.status == Status.DONE)
        self.lbl_stats.setText(f"{total} All  ·  {done} Done")

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _set_filter(self, key):
        self._filter = key
        for k, btn in self._tabs.items():
            btn.setChecked(k == key)
        self.refresh()

    def _open_add(self):
        dlg = AddDialog(self)
        if dlg.exec():
            self.refresh()

    def _on_status(self, task: Task, new_status: Status):
        update_status(task.id, new_status)
        self.refresh()

    def _on_edit(self, task: Task):
        dlg = AddDialog(self, task)
        if dlg.exec():
            self.refresh()

    def _on_delete(self, task: Task):
        delete_task(task.id)
        self.refresh()

    def _clear_done(self):
        clear_done()
        self.refresh()

    # ── Drag to move ──────────────────────────────────────────────────────────

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)