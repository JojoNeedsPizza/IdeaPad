import sys
import json
import time
import ctypes
import ctypes.wintypes
from datetime import datetime
from pathlib import Path
import win32gui
import win32con

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

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

IDEAS_FILE = Path(__file__).parent / "ideas.json"


# ═══════════════════════════════════════════════════════════════════════════════
# Hilfsfunktionen für Fenster & JSON-Struktur
# ═══════════════════════════════════════════════════════════════════════════════
def get_work_area() -> tuple[int, int, int, int]:
    """Gibt (x, y, w, h) der primären Arbeitsfläche ohne Taskleiste zurück."""

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


def load_ideas() -> list[dict]:
    """Lädt die bestehende Struktur (Liste von Dictionaries)."""
    if IDEAS_FILE.exists():
        try:
            data = json.loads(IDEAS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def save_ideas(ideas: list[dict]):
    IDEAS_FILE.write_text(json.dumps(ideas, ensure_ascii=False, indent=2), encoding="utf-8")


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
# AddIdeaWindow (An Haupt-Dock Design angepasst)
# ═══════════════════════════════════════════════════════════════════════════════
class AddIdeaWindow(QWidget):
    def __init__(self, dock_x: int, dock_y: int, dock_w: int):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.win_w, self.win_h = 280, 90
        # Exakt rechtsbündig über dem Haupt-Dock ausrichten
        px = dock_x + dock_w - self.win_w
        py = dock_y - self.win_h - 6
        self.setGeometry(px, py, self.win_w, self.win_h)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        lbl = QLabel("NEW IDEA")
        lbl.setStyleSheet(
            "color: #666666; font-family: 'Segoe UI'; font-size: 9px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(lbl)

        self.field = QLineEdit()
        self.field.setPlaceholderText("Type your idea...")
        self.field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                color: #EEEEEE;
                border: none;
                border-bottom: 1px solid #333333;
                padding: 4px 0px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QLineEdit:focus { border-bottom: 1px solid #666666; }
        """)
        self.field.returnPressed.connect(self._save_and_close)
        layout.addWidget(self.field)
        self.field.setFocus()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(10, 10, 10, 210)))  # Identisch zum Dock
        p.setPen(QPen(QColor(55, 55, 55, 160), 1))  # Identisch zum Dock
        p.drawRoundedRect(0, 0, self.win_w - 1, self.win_h - 1, 9, 9)  # Gleicher Radius (9px)

        # Integrierter Hardware-Punkt oben rechts
        p.setBrush(QBrush(QColor(229, 43, 31)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(self.win_w - 8, 8), 2.5, 2.5)

    def _save_and_close(self):
        text = self.field.text().strip()
        if text:
            ideas = load_ideas()
            # Struktur-Mapping auf deine bestehende JSON-Architektur
            new_entry = {
                "key": str(int(time.time())),
                "name": text,
                "description": "",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            ideas.insert(0, new_entry)
            save_ideas(ideas)
        self.close()


# ═══════════════════════════════════════════════════════════════════════════════
# ShowIdeasWindow (An Haupt-Dock Design angepasst)
# ═══════════════════════════════════════════════════════════════════════════════
class ShowIdeasWindow(QWidget):
    def __init__(self, dock_x: int, dock_y: int, dock_w: int):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.win_w, self.win_h = 280, 220
        px = dock_x + dock_w - self.win_w
        py = dock_y - self.win_h - 6
        self.setGeometry(px, py, self.win_w, self.win_h)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        lbl = QLabel("SAVED IDEAS")
        lbl.setStyleSheet(
            "color: #666666; font-family: 'Segoe UI'; font-size: 9px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(lbl)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFrameStyle(QFrame.Shape.NoFrame)
        self.text.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: #CCCCCC;
                border: none;
                font-family: 'Segoe UI';
            }
            QScrollBar:vertical { background: transparent; width: 4px; margin: 0; }
            QScrollBar::handle:vertical { background: #333333; border-radius: 2px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        ideas = load_ideas()
        if ideas:
            # HTML-Formatierung für saubere Darstellung von Name & Datum im Nothing-Stil
            html_content = ""
            for item in ideas:
                name = item.get("name", "Untitled")
                date = item.get("date", "")
                html_content += (
                    f"<div style='margin-bottom: 8px;'>"
                    f"<span style='color: #EEEEEE; font-size: 12px;'>• {name}</span><br/>"
                    f"<span style='color: #555555; font-size: 10px; font-family: \"Courier New\"; margin-left: 10px;'>{date}</span>"
                    f"</div>"
                )
            self.text.setHtml(html_content)
        else:
            self.text.setHtml(
                "<span style='color: #444444; font-style: italic; font-size: 12px;'>No ideas yet.<br>Press the + button to add one.</span>")

        layout.addWidget(self.text)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(10, 10, 10, 210)))  # Identisch zum Dock
        p.setPen(QPen(QColor(55, 55, 55, 160), 1))  # Identisch zum Dock
        p.drawRoundedRect(0, 0, self.win_w - 1, self.win_h - 1, 9, 9)  # Gleicher Radius (9px)

        # Integrierter Hardware-Punkt
        p.setBrush(QBrush(QColor(229, 43, 31)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(self.win_w - 8, 8), 2.5, 2.5)


# ═══════════════════════════════════════════════════════════════════════════════
# NothingDock — Haupt-Overlay
# ═══════════════════════════════════════════════════════════════════════════════
class NothingDock(QWidget):
    DOCK_W = 170
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

        sw = self.DOCK_W // 2
        self._buttons = [
            GlyphButton(0, sw, self._draw_add_idea, "Add Idea"),
            GlyphButton(sw, sw, self._draw_show_ideas, "Show Ideas"),
        ]

        self._hwnd = None
        self._was_fullscreen = False
        self.active_popup = None
        self._hover_x = -1
        self.setMouseTracking(True)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_state)
        self._timer.start(500)

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_win32_styles()

    def _apply_win32_styles(self):
        self._hwnd = int(self.winId())
        # Sichere pywin32 API-Aufrufe zur Vermeidung von x64-Speicherabshchnitten
        ex = win32gui.GetWindowLong(self._hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(self._hwnd, win32con.GWL_EXSTYLE, ex | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
        win32gui.SetWindowPos(self._hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, SWP_ZORDER_ONLY)

    def _update_state(self):
        if self._hwnd is None:
            return
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

    def _close_popup(self):
        if self.active_popup:
            try:
                self.active_popup.close()
            except Exception:
                pass
            self.active_popup = None

    def trigger_add_idea(self):
        self._close_popup()
        self.active_popup = AddIdeaWindow(self.dock_x, self.dock_y, self.DOCK_W)
        self.active_popup.show()
        self.active_popup.raise_()
        self.active_popup.activateWindow()

    def trigger_show_ideas(self):
        self._close_popup()
        self.active_popup = ShowIdeasWindow(self.dock_x, self.dock_y, self.DOCK_W)
        self.active_popup.show()
        self.active_popup.raise_()
        self.active_popup.activateWindow()

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

    def _draw_add_idea(self, p: QPainter, cx: float, cy: float, color: QColor):
        s = self.SCALE
        draw_notepad(p, cx - 5 * s, cy, s, color)
        draw_plus(p, cx + 7 * s, cy + 4 * s, s, color)

    def _draw_show_ideas(self, p: QPainter, cx: float, cy: float, color: QColor):
        s = self.SCALE
        draw_notepad(p, cx - 5 * s, cy, s, color)
        draw_eye(p, cx + 7 * s, cy + 5 * s, s, color)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.setBrush(QBrush(QColor(10, 10, 10, 210)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.DOCK_W, self.DOCK_H, 9, 9)

        p.setPen(QPen(QColor(55, 55, 55, 160), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(0, 0, self.DOCK_W - 1, self.DOCK_H - 1, 9, 9)

        mid = self.DOCK_W // 2
        p.setPen(QPen(QColor(50, 50, 50, 140), 1))
        p.drawLine(mid, 7, mid, self.DOCK_H - 7)

        for btn in self._buttons:
            if btn.hovered:
                p.setBrush(QBrush(QColor(255, 255, 255, 12)))
                p.setPen(Qt.PenStyle.NoPen)
                if btn is self._buttons[0]:
                    p.drawRoundedRect(1, 1, mid - 1, self.DOCK_H - 2, 9, 9)
                else:
                    p.drawRoundedRect(mid, 1, mid - 1, self.DOCK_H - 2, 9, 9)

        cy = self.DOCK_H / 2
        for btn in self._buttons:
            cx = btn.x + btn.w / 2
            btn.draw(p, cx, cy, btn.color())

        p.setBrush(QBrush(QColor(229, 43, 31)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(self.DOCK_W - 8, 8), 2.5, 2.5)
        p.end()


# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    dock = NothingDock()
    dock.show()
    sys.exit(app.exec())