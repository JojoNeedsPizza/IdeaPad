import sys
import ctypes
import win32gui
import win32con
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen

# WICHTIG: Erlaube DPI-Skalierung, damit es nicht "wegspringt"
ctypes.windll.shcore.SetProcessDpiAwareness(1)


class NothingDock(QWidget):
    def __init__(self):
        super().__init__()
        # FIXED: Flags für ein echtes System-Overlay
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint |
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(100, 40)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dock)
        self.timer.start(100)

    def update_dock(self):
        # 1. Vollbild-Check (Das VANISH bei Spielen)
        hwnd = win32gui.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hwnd)
        w, h = rect[2] - rect[0], rect[3] - rect[1]

        sw = ctypes.windll.user32.GetSystemMetrics(0)
        sh = ctypes.windll.user32.GetSystemMetrics(1)

        # Verschwinden bei Vollbild (Spiel/Video)
        if w >= sw and h >= sh:
            self.hide()
            return

        # 2. FIXED POSITION (An der Taskleiste kleben)
        self.show()
        x, y = sw - 280, sh - 45
        self.move(x, y)

        # 3. Z-ORDER ERSCHÜTTERLICH MACHEN
        # HWND_TOPMOST sorgt dafür, dass es immer VOR allem ist
        # SWP_NOACTIVATE sorgt dafür, dass du nicht beim Anklicken einer App den Fokus verlierst
        win32gui.SetWindowPos(
            int(self.winId()),
            win32con.HWND_TOPMOST,
            x, y, 100, 40,
            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
        )

    def paintEvent(self, event):
        # Zeichne deine Icons (wie gehabt)
        painter = QPainter(self)
        # ... (Dein Zeichencode hier)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dock = NothingDock()
    dock.show()
    sys.exit(app.exec())