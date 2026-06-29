import sys
import win32gui
import win32con
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class NothingOverlay(QWidget):
    def __init__(self, mode, icon_type):
        super().__init__()
        self.mode = mode
        self.icon_type = icon_type
        # Tool window prevents it from showing in Alt-Tab and Taskbar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(40, 40)

        # Timer to sync position with taskbar and check for fullscreen
        self.timer = QTimer()
        self.timer.timeout.connect(self.sync_position)
        self.timer.start(500)

    def is_fullscreen(self):
        hwnd = win32gui.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hwnd)
        screen_w = win32gui.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_h = win32gui.GetSystemMetrics(win32con.SM_CYSCREEN)
        return (rect[2] - rect[0] >= screen_w and rect[3] - rect[1] >= screen_h)

    def sync_position(self):
        if self.is_fullscreen():
            self.hide()
            return

        # Logic to stick to the bottom right, next to system tray
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - 220 + (45 if self.mode == "show" else 0), screen.height() - 40)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Glyph Style Background
        painter.setBrush(QBrush(QColor("#FF0000")))  # Red Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 40, 40)

        # White Glyph Drawing Logic
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        # Draw base paper/pen
        painter.drawRect(8, 8, 15, 20)
        painter.drawLine(25, 8, 25, 28)

        if self.icon_type == "plus":
            painter.drawText(20, 35, "+")
        else:
            painter.drawEllipse(20, 20, 10, 8)  # Simple Eye shape

    def mousePressEvent(self, event):
        # Open your main Widget here
        print(f"Opening {self.mode}...")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create the two icons
    add_icon = NothingOverlay("add", "plus")
    show_icon = NothingOverlay("show", "eye")

    add_icon.show()
    show_icon.show()

    sys.exit(app.exec())