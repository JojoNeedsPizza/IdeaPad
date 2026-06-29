import sys
import ctypes
import ctypes.wintypes
import win32gui
import win32con

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

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

        # Qt Fensterkonfiguration
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Perfekt proportionierte Geometrie für 2 runde System-Buttons + Status-Dot
        wx, wy, ww, wh = get_screen_geometry()
        self.dock_w = 130
        self.dock_h = 38
        self.dock_x = wx + ww - self.dock_w - 15  # Rechter Rand Abstand
        self.dock_y = wy + wh - self.dock_h - 4  # Exakt bündig über der Taskleiste

        self.setGeometry(self.dock_x, self.dock_y, self.dock_w, self.dock_h)

        self._was_fullscreen = False
        self._hwnd = None

        # Loop für Z-Order und Fullscreen-Wächter (500ms flackert nicht)
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

    # ─── DESIGN & PAINTING (NOTHING OS GLYPH STYLE) ──────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Matte, translucent schwarze Widget-Kapsel
        painter.setBrush(QBrush(QColor(14, 14, 14, 225)))
        painter.setPen(QPen(QColor(60, 60, 60, 150), 1))
        painter.drawRoundedRect(0, 0, self.dock_w, self.dock_h, 19, 19)

        # Center-Points für die mathematisch exakte Ausrichtung
        center_y = self.dock_h // 2
        add_center_x = 32
        show_center_x = 82

        # 1. ADD-ICON (Circle + Minimalist Plus)
        painter.setPen(QPen(QColor(255, 255, 255, 230), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(add_center_x, center_y), 11, 11)

        painter.setPen(QPen(QColor(255, 255, 255, 255), 1.5))
        painter.drawLine(add_center_x, center_y - 5, add_center_x, center_y + 5)
        painter.drawLine(add_center_x - 5, center_y, add_center_x + 5, center_y)

        # 2. SHOW-ICON (Circle + Geometric Almond Eye)
        painter.setPen(QPen(QColor(255, 255, 255, 230), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(show_center_x, center_y), 11, 11)

        # Auge über zwei symmetrische Bezier-Kurven (Almond-Shape)
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

        # 3. SIGNATURE NOTHING RED DOT (Hardware Accent)
        painter.setBrush(QBrush(QColor(229, 43, 31)))  # Das originale Nothing-Rot
        painter.drawEllipse(QPoint(self.dock_w - 20, center_y), 2, 2)

        painter.end()

    # ─── INTERACTION & INTERFACE ─────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x_click = event.position().x()

            # Trennung der Klick-Zonen anhand der mathematischen Mitte
            if x_click < (self.dock_w / 2):
                self.trigger_add_idea()
            else:
                self.trigger_show_ideas()

    def trigger_add_idea(self):
        """Hier die Logik zum Öffnen deines Erstellungs-Fensters einbinden."""
        print("[Daemon] Trigger: Add Idea Function")
        # BEISPIEL:
        # self.add_window = AddIdeaWindow()
        # self.add_window.show()

    def trigger_show_ideas(self):
        """Hier die Logik zum Öffnen deiner Ideen-Übersicht einbinden."""
        print("[Daemon] Trigger: Show Ideas Function")
        # BEISPIEL:
        # self.show_window = ShowIdeasWindow()
        # self.show_window.show()


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