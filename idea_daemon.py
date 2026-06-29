import sys
import ctypes
import win32gui
import win32con
import win32api

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

# ─── DPI AWARENESS (Abgesichert gegen Stack-Crashes) ─────────────────────────
try:
    shcore = ctypes.windll.shcore
    shcore.SetProcessDpiAwareness.argtypes = [ctypes.c_int]
    shcore.SetProcessDpiAwareness.restype = ctypes.c_long
    shcore.SetProcessDpiAwareness(2)
except (OSError, AttributeError):
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass

# ─── WIN32 KONSTANTEN ────────────────────────────────────────────────────────
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080

SWP_FLAGS = (
        win32con.SWP_NOACTIVATE |
        win32con.SWP_NOMOVE |
        win32con.SWP_NOSIZE |
        win32con.SWP_SHOWWINDOW
)


# ─── STABILE API HELPER ───────────────────────────────────────────────────────
def get_screen_geometry() -> tuple[int, int, int, int]:
    """Holt die Geometrie der primären Arbeitsfläche ohne ctypes-Risiko."""
    hmon = win32api.MonitorFromPoint((0, 0), win32con.MONITOR_DEFAULTTOPRIMARY)
    info = win32api.GetMonitorInfo(hmon)
    r = info['Work']  # [left, top, right, bottom]
    return r[0], r[1], r[2] - r[0], r[3] - r[1]


def is_real_fullscreen() -> bool:
    """Erkennt echtes Vollbild über saubere pywin32-Abfragen."""
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False

    class_name = win32gui.GetClassName(hwnd)
    if class_name in ("Progman", "WorkerW", "Shell_TrayWnd"):
        return False

    try:
        r = win32gui.GetWindowRect(hwnd)
        fx, fy, fw, fh = r[0], r[1], r[2] - r[0], r[3] - r[1]

        hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        info = win32api.GetMonitorInfo(hmon)
        mr = info['Monitor']
        mw = mr[2] - mr[0]
        mh = mr[3] - mr[1]

        return (abs(fw - mw) <= 2 and abs(fh - mh) <= 2 and
                abs(fx - mr[0]) <= 2 and abs(fy - mr[1]) <= 2)
    except Exception:
        return False


# ─── HAUPT-DOCK KLASSE ───────────────────────────────────────────────────────
class NothingDock(QWidget):
    def __init__(self):
        super().__init__()

        # Qt Fensterkonfiguration
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Geometrie berechnen
        wx, wy, ww, wh = get_screen_geometry()
        self.dock_w = 130
        self.dock_h = 38
        self.dock_x = wx + ww - self.dock_w - 15
        self.dock_y = wy + wh - self.dock_h - 4

        self.setGeometry(self.dock_x, self.dock_y, self.dock_w, self.dock_h)

        self._was_fullscreen = False
        self._hwnd = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_state)
        self.timer.start(500)

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_win32_styles()

    def _apply_win32_styles(self):
        self._hwnd = int(self.winId())

        # PURE WIN32GUI: Verhindert die x64-Bit Memory Truncation (Crash-Ursache)
        ex_style = win32gui.GetWindowLong(self._hwnd, win32con.GWL_EXSTYLE)
        new_style = ex_style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
        win32gui.SetWindowLong(self._hwnd, win32con.GWL_EXSTYLE, new_style)

        win32gui.SetWindowPos(
            self._hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
        )

    def _update_state(self):
        if self._hwnd is None:
            return

        fullscreen = is_real_fullscreen()

        if fullscreen and not self._was_fullscreen:
            self._was_fullscreen = True
            self.hide()
            return

        if not fullscreen and self._was_fullscreen:
            self._was_fullscreen = False
            self.show()
            return

        if not fullscreen and self.isVisible():
            win32gui.SetWindowPos(
                self._hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS
            )

    # ─── DESIGN & PAINTING (NOTHING OS GLYPH STYLE) ──────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Kapsel-Hintergrund
        painter.setBrush(QBrush(QColor(14, 14, 14, 225)))
        painter.setPen(QPen(QColor(60, 60, 60, 150), 1))
        painter.drawRoundedRect(0, 0, self.dock_w, self.dock_h, 19, 19)

        center_y = self.dock_h // 2
        add_center_x = 32
        show_center_x = 82

        # 1. ADD-ICON (Plus im Kreis)
        painter.setPen(QPen(QColor(255, 255, 255, 230), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(add_center_x, center_y), 11, 11)

        painter.setPen(QPen(QColor(255, 255, 255, 255), 1.5))
        painter.drawLine(add_center_x, center_y - 5, add_center_x, center_y + 5)
        painter.drawLine(add_center_x - 5, center_y, add_center_x + 5, center_y)

        # 2. SHOW-ICON (Mandelauge im Kreis)
        painter.setPen(QPen(QColor(255, 255, 255, 230), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(show_center_x, center_y), 11, 11)

        eye_path = QPainterPath()
        left_corner = QPoint(show_center_x - 6, center_y)
        right_corner = QPoint(show_center_x + 6, center_y)

        eye_path.moveTo(left_corner)
        eye_path.quadTo(QPoint(show_center_x, center_y - 5), right_corner)
        eye_path.quadTo(QPoint(show_center_x, center_y + 5), left_corner)
        painter.drawPath(eye_path)

        # Pupille
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPoint(show_center_x, center_y), 2, 2)

        # 3. NOTHING RED DOT
        painter.setBrush(QBrush(QColor(229, 43, 31)))
        painter.drawEllipse(QPoint(self.dock_w - 20, center_y), 2, 2)

        painter.end()

    # ─── INTERACTION & INTERFACE ─────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x_click = event.position().x()

            if x_click < (self.dock_w / 2):
                self.trigger_add_idea()
            else:
                self.trigger_show_ideas()

    def trigger_add_idea(self):
        print("[Daemon] Trigger: Add Idea Function")

    def trigger_show_ideas(self):
        print("[Daemon] Trigger: Show Ideas Function")


# ─── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    dock = NothingDock()
    dock.show()

    sys.exit(app.exec())