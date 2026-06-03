"""
app/ui/main_window.py
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QDate

from app.ui.task_item import TaskItem
from app.ui.add_dialog import AddDialog
from app.core import (
    get_all_tasks, delete_task, clear_done, update_status,
    Task, Status
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._drag_pos  = QPoint()
        self._main_tab  = "today"
        self._filter    = "all"
        self._week_day  = QDate.currentDate()
        self._setup_window()
        self._build_ui()
        self._start_clock()
        self._set_main_tab("today")

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

        v.addWidget(self._build_main_tab_bar())
        v.addWidget(self._build_header())
        v.addWidget(self._build_week_strip())
        v.addWidget(self._build_search())
        v.addWidget(self._build_filter_tabs())
        v.addWidget(self._build_task_area())
        v.addWidget(self._build_footer())

    # ── Main tab bar (All | Today's Task | Week's Task) ───────────────────────

    def _build_main_tab_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("mainTabBar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        self._main_tabs: dict = {}
        for key, label in [("all", "All"), ("today", "Today's Task"), ("week", "Week's Task")]:
            btn = QPushButton(label)
            btn.setObjectName("mainTab")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, k=key: self._set_main_tab(k))
            self._main_tabs[key] = btn
            h.addWidget(btn)

        return bar

    # ── Today's Task header ───────────────────────────────────────────────────

    def _build_header(self) -> QWidget:
        self._header = QWidget()
        self._header.setObjectName("header")
        v = QVBoxLayout(self._header)
        v.setContentsMargins(20, 20, 20, 16)
        v.setSpacing(0)

        row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)

        self.lbl_title = QLabel("Today's Task")
        self.lbl_title.setObjectName("heading")

        self.lbl_date = QLabel()
        self.lbl_date.setObjectName("subheading")

        col.addWidget(self.lbl_title)
        col.addWidget(self.lbl_date)

        self._btn_new = QPushButton("+ New")
        self._btn_new.setObjectName("btnNew")
        self._btn_new.setFixedHeight(36)
        self._btn_new.clicked.connect(self._open_add)

        row.addLayout(col)
        row.addStretch()
        row.addWidget(self._btn_new, alignment=Qt.AlignmentFlag.AlignTop)
        v.addLayout(row)
        return self._header

    # ── Week calendar strip ───────────────────────────────────────────────────

    def _build_week_strip(self) -> QWidget:
        self._week_strip = QWidget()
        self._week_strip.setObjectName("weekStrip")
        h = QHBoxLayout(self._week_strip)
        h.setContentsMargins(12, 16, 12, 8)
        h.setSpacing(0)

        self._day_btns: dict[str, QPushButton] = {}
        today = QDate.currentDate()
        dow = today.dayOfWeek()          # 1=Mon … 7=Sun
        sun_offset = dow % 7             # steps back to Sunday
        week_sun = today.addDays(-sun_offset)

        for i, abbr in enumerate(["S", "M", "T", "W", "T", "F", "S"]):
            d = week_sun.addDays(i)
            key = d.toString("yyyy-MM-dd")

            col_w = QWidget()
            col_l = QVBoxLayout(col_w)
            col_l.setContentsMargins(0, 0, 0, 0)
            col_l.setSpacing(2)
            col_l.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            dot = QLabel("•" if d == today else " ")
            dot.setObjectName("todayDot" if d == today else "noDot")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setFixedHeight(10)
            col_l.addWidget(dot)

            btn = QPushButton(f"{abbr}\n{d.day()}")
            btn.setCheckable(True)
            btn.setFixedSize(44, 46)
            btn.clicked.connect(lambda _, dd=d: self._set_week_day(dd))
            self._day_btns[key] = btn
            col_l.addWidget(btn)

            h.addWidget(col_w, stretch=1)

        self._week_strip.setVisible(False)
        return self._week_strip

    def _refresh_day_btn_styles(self):
        today = QDate.currentDate()
        for key, btn in self._day_btns.items():
            d = QDate.fromString(key, "yyyy-MM-dd")
            is_today    = (d == today)
            is_selected = (d == self._week_day)

            if is_selected:
                name = "dayBtnSelected"
            elif is_today:
                name = "dayBtnToday"
            else:
                name = "dayBtn"

            btn.setChecked(is_selected)
            if btn.objectName() != name:
                btn.setObjectName(name)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    # ── Search bar ────────────────────────────────────────────────────────────

    def _build_search(self) -> QWidget:
        self._search_w = QWidget()
        self._search_w.setObjectName("searchWidget")
        lay = QVBoxLayout(self._search_w)
        lay.setContentsMargins(20, 0, 20, 12)
        lay.setSpacing(0)

        box = QWidget()
        box.setObjectName("searchBox")
        box.setFixedHeight(40)
        sb = QHBoxLayout(box)
        sb.setContentsMargins(14, 0, 14, 0)
        sb.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("search...")
        self.search_input.textChanged.connect(self.refresh)

        icon = QLabel("🔍")
        icon.setObjectName("searchIcon")

        sb.addWidget(self.search_input)
        sb.addWidget(icon)
        lay.addWidget(box)
        return self._search_w

    # ── Filter sub-tabs ───────────────────────────────────────────────────────

    def _build_filter_tabs(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("filterBar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(20, 10, 20, 0)
        h.setSpacing(0)

        self._tabs: dict = {}
        items = [
            ("all",              "All"),
            (Status.IN_PROGRESS, "In Progress"),
            (Status.PENDING,     "Pending"),
            (Status.NOT_STARTED, "No Status"),
            (Status.DONE,        "Done"),
        ]
        for i, (key, label) in enumerate(items):
            if i > 0:
                sep = QLabel("|")
                sep.setObjectName("filterSep")
                h.addWidget(sep)
            btn = QPushButton(label)
            btn.setObjectName("filterTab")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, k=key: self._set_filter(k))
            self._tabs[key] = btn
            h.addWidget(btn)

        h.addStretch()
        return bar

    # ── Task list ─────────────────────────────────────────────────────────────

    def _build_task_area(self) -> QScrollArea:
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
        scroll.setMinimumHeight(180)
        scroll.setMaximumHeight(400)
        return scroll

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self) -> QWidget:
        footer = QWidget()
        footer.setObjectName("footer")
        h = QHBoxLayout(footer)
        h.setContentsMargins(20, 10, 20, 10)

        self.lbl_stats = QLabel()
        self.lbl_stats.setObjectName("footerStats")

        btn_trash = QPushButton("🗑")
        btn_trash.setObjectName("btnTrash")
        btn_trash.setFixedSize(30, 30)
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
        t.start(60_000)

    def _tick(self):
        from datetime import datetime
        now = datetime.now()
        days   = ["Monday", "Tuesday", "Wednesday", "Thursday",
                  "Friday", "Saturday", "Sunday"]
        months = ["", "January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.lbl_date.setText(f"{days[now.weekday()]}, {now.day} {months[now.month]}")

    # ── Tab / filter switching ────────────────────────────────────────────────

    def _set_main_tab(self, key: str):
        self._main_tab = key
        for k, btn in self._main_tabs.items():
            btn.setChecked(k == key)

        self._header.setVisible(key == "today")
        self._week_strip.setVisible(key == "week")
        self._search_w.setVisible(key == "today")

        if key == "week":
            self._refresh_day_btn_styles()

        self._set_filter("all", refresh=False)
        self.refresh()

    def _set_filter(self, key, refresh=True):
        self._filter = key
        for k, btn in self._tabs.items():
            btn.setChecked(k == key)
        if refresh:
            self.refresh()

    def _set_week_day(self, day: QDate):
        self._week_day = day
        self._refresh_day_btn_styles()
        self.refresh()

    # ── Data helpers ──────────────────────────────────────────────────────────

    def _base_tasks(self) -> list:
        all_tasks = get_all_tasks()
        if self._main_tab == "week":
            date_str = self._week_day.toString("yyyy-MM-dd")
            return [t for t in all_tasks if t.due_at and t.due_at[:10] == date_str]
        # "all" and "today" both show all tasks
        return all_tasks

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh(self):
        keyword = self.search_input.text().strip() if hasattr(self, "search_input") else ""
        base = self._base_tasks()

        if keyword:
            kw = keyword.lower()
            tasks = [t for t in base if kw in t.title.lower() or kw in t.description.lower()]
        elif self._filter == "all":
            tasks = base
        else:
            tasks = [t for t in base if t.status == self._filter]

        while self.task_layout.count() > 1:
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for task in tasks:
            w = TaskItem(task, self._on_status, self._on_edit, self._on_delete)
            self.task_layout.insertWidget(self.task_layout.count() - 1, w)

        all_tasks = get_all_tasks()
        total = len(all_tasks)
        done  = sum(1 for t in all_tasks if t.status == Status.DONE)
        self.lbl_stats.setText(f"{total} All   {done} Done")

    # ── Handlers ──────────────────────────────────────────────────────────────

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
