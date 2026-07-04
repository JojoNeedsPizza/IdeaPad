import sys
import json
import datetime
import ctypes
import ctypes.wintypes
import subprocess
from pathlib import Path
import win32gui
import win32con

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFrame, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

# --- GLOBAL DAEMON KEYBINDS EXTENSION ---
try:
    from pynput import keyboard as pynput_keyboard
except ImportError:
    print("pynput dynamic dependency missing. Run: pip install pynput")
    pynput_keyboard = None

# ═══════════════════════════════════════════════════════════════════════════════
# DPI AWARENESS
# ═══════════════════════════════════════════════════════════════════════════════
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except OSError:
    ctypes.windll.user32.SetProcessDPIAware()

# ═══════════════════════════════════════════════════════════════════════════════
# Win32 Konstanten & Flags
# ═══════════════════════════════════════════════════════════════════════════════
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
SWP_ZORDER_ONLY = (
        win32con.SWP_NOMOVE |
        win32con.SWP_NOSIZE |
        win32con.SWP_NOACTIVATE
)

DATABASE_FILE = Path(__file__).parent / "database.json"
SETTINGS_FILE = Path(__file__).parent / "settings.json"


# ═══════════════════════════════════════════════════════════════════════════════
# Hilfsfunktionen & Standalone JSON-Loader
# ═══════════════════════════════════════════════════════════════════════════════
def get_work_area() -> tuple[int, int, int, int]:
    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_ulong),
                    ("rcMonitor", ctypes.wintypes.RECT),
                    ("rcWork", ctypes.wintypes.RECT),
                    ("dwFlags", ctypes.c_ulong)]

    pt = ctypes.wintypes.POINT(0, 0)
    hmon = ctypes.windll.user32.MonitorFromPoint(pt, 1)
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(info))
    r = info.rcWork
    return r.left, r.top, r.right - r.left, r.bottom - r.top


def is_real_fullscreen() -> bool:
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False
    if win32gui.GetClassName(hwnd) in ("Progman", "WorkerW", "Shell_TrayWnd"):
        return False
    try:
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        rect = ctypes.wintypes.RECT()
        ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd, DWMWA_EXTENDED_FRAME_BOUNDS,
            ctypes.byref(rect), ctypes.sizeof(rect))
        fx, fy = rect.left, rect.top
        fw, fh = rect.right - fx, rect.bottom - fy
    except Exception:
        r = win32gui.GetWindowRect(hwnd)
        fx, fy, fw, fh = r[0], r[1], r[2] - r[0], r[3] - r[1]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_ulong),
                    ("rcMonitor", ctypes.wintypes.RECT),
                    ("rcWork", ctypes.wintypes.RECT),
                    ("dwFlags", ctypes.c_ulong)]

    pt = ctypes.wintypes.POINT(fx + fw // 2, fy + fh // 2)
    hmon = ctypes.windll.user32.MonitorFromPoint(pt, 2)
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(info))
    mr = info.rcMonitor
    mw, mh = mr.right - mr.left, mr.bottom - mr.top
    return (abs(fw - mw) <= 2 and abs(fh - mh) <= 2 and
            abs(fx - mr.left) <= 2 and abs(fy - mr.top) <= 2)


def load_ideas() -> dict:
    if DATABASE_FILE.exists():
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as file:
                databasetemp = json.load(file)
                if isinstance(databasetemp, dict):
                    return databasetemp
        except (json.JSONDecodeError, Exception):
            pass
    return {}


def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            pass
    return {}


# ═══════════════════════════════════════════════════════════════════════════════
# Nothing-Glyph Zeichenfunktionen
# ═══════════════════════════════════════════════════════════════════════════════
def _nothing_pen(painter: QPainter, color: QColor, width: float = 1.5):
    pen = QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)


def draw_notepad(p: QPainter, cx: float, cy: float, s: float, color: QColor):
    _nothing_pen(p, color, 1.4 * s)
    bw, bh, ear = 11 * s, 14 * s, 3.5 * s
    x0, y0 = cx - bw / 2, cy - bh / 2
    path = QPainterPath()
    path.moveTo(x0, y0)
    path.lineTo(x0 + bw - ear, y0)
    path.lineTo(x0 + bw, y0 + ear)
    path.lineTo(x0 + bw, y0 + bh)
    path.lineTo(x0, y0 + bh)
    path.closeSubpath()
    p.drawPath(path)
    _nothing_pen(p, color, 1.0 * s)
    p.drawLine(QPointF(x0 + bw - ear, y0), QPointF(x0 + bw - ear, y0 + ear))
    p.drawLine(QPointF(x0 + bw - ear, y0 + ear), QPointF(x0 + bw, y0 + ear))
    lx0, lx1 = x0 + 2.5 * s, x0 + bw - 3.5 * s
    for i in range(3):
        ly = y0 + 4.5 * s + i * 3.2 * s
        p.drawLine(QPointF(lx0, ly), QPointF(lx1, ly))


def draw_plus(p: QPainter, cx: float, cy: float, s: float, color: QColor):
    _nothing_pen(p, color, 1.6 * s)
    r = 3.5 * s
    p.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))
    p.drawLine(QPointF(cx, cy - r), QPointF(cx, cy + r))


def draw_eye(p: QPainter, cx: float, cy: float, s: float, color: QColor):
    _nothing_pen(p, color, 1.4 * s)
    ew, eh = 9.0 * s, 4.5 * s
    eye_path = QPainterPath()
    eye_path.moveTo(cx - ew, cy)
    eye_path.cubicTo(cx - ew * 0.4, cy - eh * 1.6, cx + ew * 0.4, cy - eh * 1.6, cx + ew, cy)
    eye_path.cubicTo(cx + ew * 0.4, cy + eh * 1.6, cx - ew * 0.4, cy + eh * 1.6, cx - ew, cy)
    p.drawPath(eye_path)
    p.drawEllipse(QPointF(cx, cy), 2.8 * s, 2.8 * s)
    p.setBrush(QBrush(color))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(cx + 1.2 * s, cy - 1.2 * s), 0.7 * s, 0.7 * s)
    p.setBrush(Qt.BrushStyle.NoBrush)


def draw_launch(p: QPainter, cx: float, cy: float, s: float, color: QColor):
    _nothing_pen(p, color, 1.4 * s)
    r = 3.0 * s
    p.drawLine(QPointF(cx - r, cy + r), QPointF(cx + r, cy - r))
    p.drawLine(QPointF(cx - 0.5 * r, cy - r), QPointF(cx + r, cy - r))
    p.drawLine(QPointF(cx + r, cy - r), QPointF(cx + r, cy + 0.5 * r))


# ═══════════════════════════════════════════════════════════════════════════════
# Dock-Button Logik
# ═══════════════════════════════════════════════════════════════════════════════
class GlyphButton:
    def __init__(self, x: int, w: int, draw_fn, label: str):
        self.x = x
        self.w = w
        self.draw = draw_fn
        self.label = label
        self.hovered = False

    def contains(self, px: int) -> bool:
        return self.x <= px < self.x + self.w

    def color(self) -> QColor:
        return QColor(220, 220, 220) if self.hovered else QColor(150, 150, 150)


# ═══════════════════════════════════════════════════════════════════════════════
# AddIdeaWindow (Eingabe- & Edit-Menü)
# ═══════════════════════════════════════════════════════════════════════════════
class AddIdeaWindow(QWidget):
    def __init__(self, dock_x: int, dock_y: int, dock_w: int, dock_parent, edit_key=None, current_name="",
                 current_desc=""):
        super().__init__()
        self.dock_parent = dock_parent
        self.edit_key = edit_key

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.win_w, self.win_h = 320, 155
        self.target_px = (dock_x + dock_w) - self.win_w
        self.target_py = dock_y - self.win_h - 8

        self.setGeometry(self.target_px, self.target_py + 12, self.win_w, self.win_h)
        self.setWindowOpacity(0.0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 12)
        layout.setSpacing(6)

        header_row = QHBoxLayout()
        lbl = QLabel("EDIT IDEA" if self.edit_key else "NEW IDEA")
        lbl.setStyleSheet(
            "color: #666666; font-family: 'Segoe UI'; font-size: 9px; font-weight: bold; letter-spacing: 2px;")
        header_row.addWidget(lbl)
        header_row.addStretch()
        layout.addLayout(header_row)

        input_style = """
            QLineEdit {
                background: transparent;
                color: #EEEEEE;
                border: none;
                border-bottom: 1px solid #222222;
                padding: 4px 0px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QLineEdit:focus { border-bottom: 1px solid #666666; }
        """

        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Enter your Idea's Name...")
        self.name_field.setStyleSheet(input_style)
        self.name_field.setText(current_name)
        self.name_field.returnPressed.connect(self._save_and_close)
        layout.addWidget(self.name_field)

        self.desc_field = QLineEdit()
        self.desc_field.setPlaceholderText("Describe this Idea...")
        self.desc_field.setStyleSheet(input_style)
        self.desc_field.setText(current_desc)
        self.desc_field.returnPressed.connect(self._save_and_close)
        layout.addWidget(self.desc_field)

        layout.addStretch()

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        actions_layout.addStretch()

        button_style = """
            QPushButton {
                background: transparent;
                color: #555555;
                border: none;
                font-family: 'Segoe UI';
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1.5px;
                padding: 4px 2px;
            }
            QPushButton:hover { color: #EEEEEE; }
        """

        self.back_btn = QPushButton("BACK")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet(button_style)
        self.back_btn.clicked.connect(self._handle_back)
        actions_layout.addWidget(self.back_btn)

        self.save_btn = QPushButton("SAVE")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setStyleSheet(button_style)
        self.save_btn.clicked.connect(self._save_and_close)
        actions_layout.addWidget(self.save_btn)

        layout.addLayout(actions_layout)
        self.name_field.setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        self.anim_in_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_in_opacity.setDuration(250)
        self.anim_in_opacity.setStartValue(0.0)
        self.anim_in_opacity.setEndValue(1.0)
        self.anim_in_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_in_pos = QPropertyAnimation(self, b"pos")
        self.anim_in_pos.setDuration(250)
        self.anim_in_pos.setStartValue(QPoint(self.target_px, self.target_py + 12))
        self.anim_in_pos.setEndValue(QPoint(self.target_px, self.target_py))
        self.anim_in_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_in_opacity.start()
        self.anim_in_pos.start()

    def fade_out_and_close(self):
        self.anim_out_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out_opacity.setDuration(200)
        self.anim_out_opacity.setStartValue(self.windowOpacity())
        self.anim_out_opacity.setEndValue(0.0)
        self.anim_out_opacity.setEasingCurve(QEasingCurve.Type.InCubic)

        self.anim_out_pos = QPropertyAnimation(self, b"pos")
        self.anim_out_pos.setDuration(200)
        self.anim_out_pos.setStartValue(self.pos())
        self.anim_out_pos.setEndValue(QPoint(self.pos().x(), self.pos().y() + 10))
        self.anim_out_pos.setEasingCurve(QEasingCurve.Type.InCubic)

        self.anim_out_opacity.finished.connect(self.close)
        self.anim_out_opacity.start()
        self.anim_out_pos.start()

    def _handle_back(self):
        self.fade_out_and_close()
        if self.edit_key:
            QTimer.singleShot(220, self.dock_parent.trigger_show_ideas)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(12, 12, 12, 248)))
        p.setPen(QPen(QColor(45, 45, 45), 1))
        p.drawRoundedRect(0, 0, self.win_w - 1, self.win_h - 1, 12, 12)

        p.setBrush(QBrush(QColor(229, 43, 31)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(self.win_w - 14, 14), 3, 3)

    def _save_and_close(self):
        nid = self.name_field.text().strip()
        descriptionofidea = self.desc_field.text().strip()

        if nid == "":
            self._handle_back()
            return

        databasetemp = {}
        if DATABASE_FILE.exists():
            with open(DATABASE_FILE, "r", encoding="utf-8") as file:
                try:
                    databasetemp = json.load(file)
                except json.JSONDecodeError:
                    databasetemp = {}

        currentdateandtime = datetime.datetime.now()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        date_str = f"{currentdateandtime.day} {months[currentdateandtime.month - 1]} {currentdateandtime.year} // {currentdateandtime.strftime('%H:%M')}"

        if self.edit_key and self.edit_key in databasetemp:
            databasetemp[self.edit_key] = {
                "Name of Idea": f'{nid}',
                "Description": f'{descriptionofidea}',
                "Date and Time": date_str
            }
            with open(DATABASE_FILE, "w", encoding="utf-8") as file:
                json.dump(databasetemp, file, indent=4)
            self.fade_out_and_close()
            QTimer.singleShot(220, self.dock_parent.trigger_show_ideas)
        else:
            countofideas = len(databasetemp)
            coid = countofideas + 1
            databasetemp[f"Idea{coid}"] = {
                "Name of Idea": f'{nid}',
                "Description": f'{descriptionofidea}',
                "Date and Time": date_str
            }
            with open(DATABASE_FILE, "w", encoding="utf-8") as file:
                json.dump(databasetemp, file, indent=4)
            self.fade_out_and_close()


# ═══════════════════════════════════════════════════════════════════════════════
# Nativer Idea-Card Widget Block
# ═══════════════════════════════════════════════════════════════════════════════
class IdeaCard(QFrame):
    def __init__(self, key, name, desc, date, on_edit, on_delete):
        super().__init__()
        self.key = key
        self.name = name
        self.desc = desc
        self.date = date
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.setObjectName("IdeaCardFrame")
        self.set_normal_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        header = QHBoxLayout()
        date_lbl = QLabel(self.date)
        date_lbl.setStyleSheet("color: #555555; font-size: 10px; font-family: 'Courier New', monospace;")
        header.addWidget(date_lbl)
        header.addStretch()

        edit_btn = QPushButton("EDIT")
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #444444; border: none; font-family: 'Segoe UI'; font-size: 9px; font-weight: bold; padding: 0px 2px; }
            QPushButton:hover { color: #EEEEEE; }
        """)
        edit_btn.clicked.connect(lambda: self.on_edit(self.key, self.name, self.desc))
        header.addWidget(edit_btn)

        sep = QLabel("//")
        sep.setStyleSheet("color: #252525; font-size: 9px; font-family: 'Segoe UI'; font-weight: bold;")
        header.addWidget(sep)

        del_btn = QPushButton("DELETE")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet("""
            QPushButton { background: transparent; color: #444444; border: none; font-family: 'Segoe UI'; font-size: 9px; font-weight: bold; padding: 0px 2px; }
            QPushButton:hover { color: #E52B1F; }
        """)
        del_btn.clicked.connect(lambda: self.on_delete(self.key))
        header.addWidget(del_btn)

        layout.addLayout(header)

        name_lbl = QLabel(self.name)
        name_lbl.setWordWrap(True)
        name_lbl.setStyleSheet(
            "color: #FFFFFF; font-size: 13px; font-weight: bold; font-family: 'Segoe UI', Arial; padding-top: 2px;")
        layout.addWidget(name_lbl)

        if self.desc:
            desc_lbl = QLabel(self.desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("color: #888888; font-size: 11px; font-family: 'Segoe UI', Arial; padding-top: 2px;")
            layout.addWidget(desc_lbl)

    def set_normal_style(self):
        self.setStyleSheet("""
            QFrame#IdeaCardFrame {
                background-color: #151515;
                border: 1px solid #222222;
                border-radius: 4px;
            }
        """)

    def set_hover_style(self):
        self.setStyleSheet("""
            QFrame#IdeaCardFrame {
                background-color: #191919;
                border: 1px solid #333333;
                border-radius: 4px;
            }
        """)

    def enterEvent(self, event):
        self.set_hover_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.set_normal_style()
        super().leaveEvent(event)


# ═══════════════════════════════════════════════════════════════════════════════
# ShowIdeasWindow
# ═══════════════════════════════════════════════════════════════════════════════
class ShowIdeasWindow(QWidget):
    def __init__(self, dock_x: int, dock_y: int, dock_w: int, dock_parent):
        super().__init__()
        self.dock_parent = dock_parent

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.win_w, self.win_h = 320, 360
        self.target_px = (dock_x + dock_w) - self.win_w
        self.target_py = dock_y - self.win_h - 8

        self.setGeometry(self.target_px, self.target_py + 12, self.win_w, self.win_h)
        self.setWindowOpacity(0.0)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 14, 16, 14)
        self.main_layout.setSpacing(10)

        lbl = QLabel("SAVED IDEAS")
        lbl.setStyleSheet(
            "color: #666666; font-family: 'Segoe UI'; font-size: 9px; font-weight: bold; letter-spacing: 2px;")
        self.main_layout.addWidget(lbl)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: #111111; width: 4px; margin: 0; }
            QScrollBar::handle:vertical { background: #333333; border-radius: 2px; }
            QScrollBar::handle:vertical:hover { background: #555555; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 4, 0)
        self.scroll_layout.setSpacing(8)

        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.refresh_ideas()

    def refresh_ideas(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        ideas = load_ideas()
        if ideas:
            def get_key_num(k):
                if k.startswith("Idea") and k[4:].isdigit():
                    return int(k[4:])
                return 0

            sorted_keys = sorted(ideas.keys(), key=get_key_num, reverse=True)

            for key in sorted_keys:
                item = ideas[key]
                if isinstance(item, dict):
                    name = item.get("Name of Idea", "Untitled")
                    desc = item.get("Description", "")
                    date = item.get("Date and Time", "")
                else:
                    name = str(item)
                    desc, date = "", ""

                card = IdeaCard(key, name, desc, date, self.handle_edit, self.handle_delete)
                self.scroll_layout.addWidget(card)

            self.scroll_layout.addStretch()
        else:
            empty_lbl = QLabel("No ideas yet.\nPress the + button to add one.")
            empty_lbl.setStyleSheet("color: #555555; font-family: 'Segoe UI'; font-size: 12px; font-style: italic;")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self.scroll_layout.addWidget(empty_lbl)

    def handle_delete(self, key):
        ideas = load_ideas()
        if key in ideas:
            del ideas[key]
            with open(DATABASE_FILE, "w", encoding="utf-8") as file:
                json.dump(ideas, file, indent=4)
        self.refresh_ideas()

    def handle_edit(self, key, name, desc):
        self.dock_parent.trigger_edit_idea(key, name, desc)

    def showEvent(self, event):
        super().showEvent(event)
        self.anim_in_opacity = QPropertyAnimation(self, b"windowOpacity")
        self.anim_in_opacity.setDuration(250)
        self.anim_in_opacity.setStartValue(0.0)
        self.anim_in_opacity.setEndValue(1.0)
        self.anim_in_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_in_pos = QPropertyAnimation(self, b"pos")
        self.anim_in_pos.setDuration(250)
        self.anim_in_pos.setStartValue(QPoint(self.target_px, self.target_py + 12))
        self.anim_in_pos.setEndValue(QPoint(self.target_px, self.target_py))
        self.anim_in_pos.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.anim_in_opacity.start()
        self.anim_in_pos.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(12, 12, 12, 248)))
        p.setPen(QPen(QColor(45, 45, 45), 1))
        p.drawRoundedRect(0, 0, self.win_w - 1, self.win_h - 1, 12, 12)

        p.setBrush(QBrush(QColor(229, 43, 31)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(self.win_w - 14, 14), 3, 3)


# ═══════════════════════════════════════════════════════════════════════════════
# NothingDock — Haupt-Overlay (3 Buttons, Breite erhöht auf 240px)
# ═══════════════════════════════════════════════════════════════════════════════
class NothingDock(QWidget):
    DOCK_W = 240  # Breite vergrößert für 3 Buttons
    DOCK_H = 38
    MARGIN = 8
    SCALE = 1.1

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        wx, wy, ww, wh = get_work_area()
        self.dock_x = wx + ww - self.DOCK_W - self.MARGIN
        self.dock_y = wy + wh - self.DOCK_H - 4
        self.setGeometry(self.dock_x, self.dock_y, self.DOCK_W, self.DOCK_H)

        sw = self.DOCK_W // 3
        self._buttons = [
            GlyphButton(0, sw, self._draw_add_idea, "Add Idea"),
            GlyphButton(sw, sw, self._draw_show_ideas, "Show Ideas"),
            GlyphButton(sw * 2, sw, self._draw_open_main, "Open Main Program"),
        ]

        self._hwnd = None
        self._was_fullscreen = False
        self.active_popup = None
        self._hover_x = -1
        self.setMouseTracking(True)

        # Settings einlesen
        self.settings = load_settings()
        self._listener = None
        self._setup_global_keybinds()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_state)
        self._timer.start(500)

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_win32_styles()

    def _apply_win32_styles(self):
        self._hwnd = int(self.winId())
        ex = win32gui.GetWindowLong(self._hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(self._hwnd, win32con.GWL_EXSTYLE, ex | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
        win32gui.SetWindowPos(self._hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, SWP_ZORDER_ONLY)

    def _update_state(self):
        if self._hwnd is None:
            return

        # Einstellungen periodisch neu laden, falls sie im Hauptprogramm geändert wurden
        current_settings = load_settings()
        if current_settings != self.settings:
            self.settings = current_settings
            self._setup_global_keybinds()

        full = is_real_fullscreen()
        if full and not self._was_fullscreen:
            self._was_fullscreen = True
            self.hide()
            return
        if not full and self._was_fullscreen:
            self._was_fullscreen = False
            self.show()
            return
        if not full and self.isVisible():
            win32gui.SetWindowPos(self._hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, SWP_ZORDER_ONLY)

    # ═══════════════════════════════════════════════════════════════════════════
    # GLOBAL KEYBIND DEPLOYMENT (THREAD-SAFE WITH QTIMER)
    # ═══════════════════════════════════════════════════════════════════════════
    def _setup_global_keybinds(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

        if pynput_keyboard and self.settings.get("keybinds_enabled", False):
            kb_new = self.settings.get("keybind_new_idea", "<Control-n>")
            kb_show = self.settings.get("keybind_show_ideas", "<Control-s>")

            pynput_new = self._convert_tk_to_pynput(kb_new)
            pynput_show = self._convert_tk_to_pynput(kb_show)

            hotkeys = {
                pynput_new: lambda: QTimer.singleShot(0, self.trigger_add_idea),
                pynput_show: lambda: QTimer.singleShot(0, self.trigger_show_ideas)
            }

            try:
                self._listener = pynput_keyboard.GlobalHotKeys(hotkeys)
                self._listener.start()
            except Exception as e:
                print(f"Keybind Daemon Error: {e}")

    def _convert_tk_to_pynput(self, tk_bind):
        """
        Converts a Tkinter-style keybind string (e.g., '<Control-Shift-End>')
        into a pynput-compatible string format (e.g., '<ctrl>+<shift>+<end>').
        """
        cleaned = tk_bind.strip("<>")
        parts = cleaned.split("-")
        pynput_parts = []

        for p in parts:
            p_low = p.lower()

            # Modifiers
            if p_low in ("control", "ctrl"):
                pynput_parts.append("<ctrl>")
            elif p_low == "shift":
                pynput_parts.append("<shift>")
            elif p_low in ("alt", "option"):
                pynput_parts.append("<alt>")
            elif p_low in ("command", "cmd", "win", "meta"):
                pynput_parts.append("<cmd>")

            # Special individual keys (pynput specific mapping)
            elif p_low == "escape":
                pynput_parts.append("<esc>")
            elif p_low in ("pageup", "prior"):
                pynput_parts.append("<page_up>")
            elif p_low in ("pagedown", "next"):
                pynput_parts.append("<page_down>")

            # Standard special keys wrapped in brackets
            elif p_low in (
                    "space", "enter", "tab", "backspace",
                    "up", "down", "left", "right",
                    "end", "home", "insert", "delete"
            ):
                pynput_parts.append(f"<{p_low}>")

            # Function keys (F1 - F20)
            elif len(p_low) > 1 and p_low.startswith("f") and p_low[1:].isdigit():
                pynput_parts.append(f"<{p_low}>")

            # Regular alphanumeric characters
            else:
                pynput_parts.append(p_low)

        return "+".join(pynput_parts)

    def _close_popup(self):
        if self.active_popup:
            try:
                if hasattr(self.active_popup, 'fade_out_and_close'):
                    self.active_popup.fade_out_and_close()
                else:
                    self.active_popup.close()
            except Exception:
                pass
            self.active_popup = None

    def trigger_add_idea(self):
        self._close_popup()
        self.active_popup = AddIdeaWindow(self.dock_x, self.dock_y, self.DOCK_W, dock_parent=self)
        self.active_popup.show()
        self.active_popup.raise_()
        self.active_popup.activateWindow()

    def trigger_edit_idea(self, edit_key, current_name, current_desc):
        self._close_popup()
        self.active_popup = AddIdeaWindow(
            self.dock_x, self.dock_y, self.DOCK_W,
            dock_parent=self, edit_key=edit_key,
            current_name=current_name, current_desc=current_desc
        )
        self.active_popup.show()
        self.active_popup.raise_()
        self.active_popup.activateWindow()

    def trigger_show_ideas(self):
        self._close_popup()
        self.active_popup = ShowIdeasWindow(self.dock_x, self.dock_y, self.DOCK_W, dock_parent=self)
        self.active_popup.show()
        self.active_popup.raise_()
        self.active_popup.activateWindow()

    def trigger_open_main(self):
        self._close_popup()
        main_script = Path(__file__).parent / "Idea Pad 2.0.py"
        if main_script.exists():
            subprocess.Popen([sys.executable, str(main_script)])
        else:
            print(f"Error: {main_script.name} not found in path.")

    def mouseMoveEvent(self, event):
        self._hover_x = int(event.position().x())
        for btn in self._buttons:
            btn.hovered = btn.contains(self._hover_x)
        self.update()

    def leaveEvent(self, event):
        self._hover_x = -1
        for btn in self._buttons:
            btn.hovered = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            px = int(event.position().x())
            if self._buttons[0].contains(px):
                self.trigger_add_idea()
            elif self._buttons[1].contains(px):
                self.trigger_show_ideas()
            elif self._buttons[2].contains(px):
                self.trigger_open_main()

    def _draw_add_idea(self, p: QPainter, cx: float, cy: float, color: QColor):
        s = self.SCALE
        draw_notepad(p, cx - 5 * s, cy, s, color)
        draw_plus(p, cx + 7 * s, cy + 4 * s, s, color)

    def _draw_show_ideas(self, p: QPainter, cx: float, cy: float, color: QColor):
        s = self.SCALE
        draw_notepad(p, cx - 5 * s, cy, s, color)
        draw_eye(p, cx + 7 * s, cy + 5 * s, s, color)

    def _draw_open_main(self, p: QPainter, cx: float, cy: float, color: QColor):
        s = self.SCALE
        draw_notepad(p, cx - 5 * s, cy, s, color)
        draw_launch(p, cx + 7 * s, cy + 4 * s, s, color)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.setBrush(QBrush(QColor(10, 10, 10, 210)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.DOCK_W, self.DOCK_H, 9, 9)

        p.setPen(QPen(QColor(55, 55, 55, 160), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(0, 0, self.DOCK_W - 1, self.DOCK_H - 1, 9, 9)

        # Zwei Trennlinien zeichnen für 3 Buttons
        sw = self.DOCK_W // 3
        p.setPen(QPen(QColor(50, 50, 50, 140), 1))
        p.drawLine(sw, 7, sw, self.DOCK_H - 7)
        p.drawLine(sw * 2, 7, sw * 2, self.DOCK_H - 7)

        for btn in self._buttons:
            if btn.hovered:
                p.setBrush(QBrush(QColor(255, 255, 255, 12)))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawRoundedRect(btn.x, 1, btn.w, self.DOCK_H - 2, 9, 9)

        cy = self.DOCK_H / 2
        for btn in self._buttons:
            cx = btn.x + btn.w / 2
            btn.draw(p, cx, cy, btn.color())

        p.setBrush(QBrush(QColor(229, 43, 31)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(self.DOCK_W - 8, 8), 2.5, 2.5)
        p.end()

    def cleanup(self):
        if self._listener:
            self._listener.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    dock = NothingDock()
    dock.show()

    # Sicherstellen, dass der Keybind-Thread beim Schließen des Daemons gestoppt wird
    app.aboutToQuit.connect(dock.cleanup)

    sys.exit(app.exec())