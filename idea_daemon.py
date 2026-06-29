import sys
import ctypes
import ctypes.wintypes
import win32gui
import win32con

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen

# ─── DPI AWARENESS ──────────────────────────────────────────────────────────
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except OSError:
    ctypes.windll.user32.SetProcessDPIAware()

# ─── WIN32 KONSTANTEN ────────────────────────────────────────────────────────
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008

SWP_FLAGS = (
        win32con.SWP_NOACTIVATE |
        win32con.SWP_NOMOVE |
        win32con.SWP_NOSIZE |
        win32con.SWP_SHOWWINDOW
)


# ─── HELPER FUNKTIONEN ───────────────────────────────────────────────────────
def get_screen_geometry() -> tuple[int, int, int, int]:
    pt = ctypes.wintypes.POINT(0, 0)
    hmon = ctypes.windll.user32.MonitorFromPoint(pt, 1)

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("rcMonitor", ctypes.wintypes.RECT),
            ("rcWork", ctypes.wintypes.RECT),
            ("dwFlags", ctypes.c_ulong),
        ]

    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(info))

    r = info.rcWork
    return r.left, r.top, r.right - r.left, r.bottom - r.top


def is_real_fullscreen() -> bool:
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False

    class_name = win32gui.GetClassName(hwnd)
    if class_name in ("Progman", "WorkerW", "Shell_TrayWnd"):
        return False

    try:
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        rect = ctypes.wintypes.RECT()
        ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rect), ctypes.sizeof(rect)
        )
        fw, fh = rect.right - rect.left, rect.bottom - rect.top
        fx, fy = rect.left, rect.top
    except Exception:
        r = win32gui.GetWindowRect(hwnd)
        fx, fy, fw, fh = r[0], r[1], r[2] - r[0], r[3] - r[1]

    pt = ctypes.wintypes.POINT(fx + fw // 2, fy + fh // 2)
    hmon = ctypes.windll.user32.MonitorFromPoint(pt, 2)

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("rcMonitor", ctypes.wintypes.RECT),
            ("rcWork", ctypes.wintypes.RECT),
            ("dwFlags", ctypes.c_ulong),
        ]

    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(info))

    mr = info.rcMonitor
    mw = mr.right - mr.left
    mh = mr.bottom - mr.top

    return (abs(fw - mw) <= 2 and abs(fh - mh) <= 2 and
            abs(fx - mr.left) <= 2 and abs(fy - mr.top) <= 2)


# ─── HAUPT-DOCK KLASSE ───────────────────────────────────────────────────────
class NothingDock(QWidget):
    def __init__(self):
        super().__init__()

        # Qt Flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Geometrie
        wx, wy, ww, wh = get_screen_geometry()
        self.dock_w = 140
        self.dock_h = 36
        self.dock_x = wx + ww - self.dock_w - 20
        self.dock_y = wy + wh - self.dock_h - 10

        self.setGeometry(self.dock_x, self.dock_y, self.dock_w, self.dock_h)

        # State
        self._was_fullscreen = False
        self._hwnd = None

        # Timer (500ms ist Ressourcen-schonend und verhindert Flackern)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_state)
        self.timer.start(500)

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_win32_styles()

    def _apply_win32_styles(self):
        self._hwnd = int(self.winId())
        ex_style = ctypes.windll.user32.GetWindowLongW(self._hwnd, GWL_EXSTYLE)
        new_style = ex_style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
        ctypes.windll.user32.SetWindowLongW(self._hwnd, GWL_EXSTYLE, new_style)

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

    # ─── UI UND GLYPHEN ──────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Hintergrund: Nothing-Style Dunkelgrau/Transparent
        painter.setBrush(QColor(15, 15, 15, 210))
        painter.setPen(QPen(QColor(50, 50, 50, 200), 1))
        painter.drawRoundedRect(0, 0, self.dock_w, self.dock_h, 18, 18)

        # Glyphen zeichnen
        self._draw_glyph(painter, 25, "add")
        self._draw_glyph(painter, 95, "show")

    def _draw_glyph(self, painter, x, mode):
        # Basis-Kreis
        painter.setPen(QPen(QColor(255, 255, 255, 220), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(x, 8, 20, 20)

        # Details
        painter.setPen(QColor(255, 255, 255, 255))
        if mode == "add":
            # Das Plus
            painter.drawLine(x + 10, 12, x + 10, 24)
            painter.drawLine(x + 4, 18, x + 16, 18)
        else:
            # Das Auge
            painter.drawEllipse(x + 6, 13, 8, 8)
            painter.setBrush(QColor(255, 255, 255, 255))
            painter.drawEllipse(x + 9, 16, 2, 2)

    # ─── KLICK-LOGIK ─────────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x_pos = event.position().x()
            if x_pos < self.dock_w / 2:
                print("ACTION: Add Idea clicked! -> Öffne Input-Fenster")
                # Hier kannst du dein Add-Idea Skript aufrufen
            else:
                print("ACTION: Show Ideas clicked! -> Öffne Liste")
                # Hier kannst du dein Show-Ideas Skript aufrufen


# ─── START ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    dock = NothingDock()
    dock.show()

    sys.exit(app.exec())