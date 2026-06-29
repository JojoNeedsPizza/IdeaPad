import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont, QPainter, QColor

# --- NOTHING DESIGN GUIDELINES ---
COLOR_BG = "#000000"
COLOR_CARD = "#121212"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_MUTED = "#666666"
COLOR_DOT = "#FF0033"


def load_database():
    if os.path.exists("database.json"):
        with open("database.json", "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                return {}
            return data if isinstance(data, dict) else {}
    return {}


def save_to_json(data):
    with open("database.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# --- DETACHED POPUP WIDGET ---
class IdeaPadWidgetMenu(QWidget):
    def __init__(self, mode="add", launch_x=0):
        super().__init__()
        # Frameless, Stays on Top, Tool-Window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setStyleSheet(f"background-color: {COLOR_BG}; border: 1px solid #222222; color: {COLOR_TEXT_MAIN};")

        self.width = 320
        self.height = 420

        # Positioniert das Menü exakt über dem geklickten Icon
        screen = QApplication.primaryScreen().geometry()
        y_pos = screen.height() - self.height - 55
        self.setGeometry(launch_x - (self.width // 2) + 18, y_pos, self.width, self.height)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        if mode == "add":
            self.init_add_view()
        else:
            self.init_archive_view()

        # Fokus erzwingen für das Vanish-Event
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.activateWindow()

    def init_add_view(self):
        header = QHBoxLayout()
        lbl_title = QLabel("Add Idea.")
        lbl_title.setFont(QFont("Courier", 14, QFont.Weight.Bold))
        close_btn = QLabel("✕")
        close_btn.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 14px;")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.mousePressEvent = lambda e: self.close()

        header.addWidget(lbl_title)
        header.addStretch()
        header.addWidget(close_btn)
        self.main_layout.addLayout(header)

        # Name
        lbl_name = QLabel("ENTER IDEA NAME...")
        lbl_name.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px; font-family: Courier;")
        self.main_layout.addWidget(lbl_name)
        self.entry_name = QLineEdit()
        self.entry_name.setStyleSheet(
            "background: transparent; border: 1px solid #333333; padding: 6px; font-family: Courier; color: white;")
        self.main_layout.addWidget(self.entry_name)

        # Description
        lbl_desc = QLabel("DESCRIBE THE IDEA...")
        lbl_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px; font-family: Courier;")
        self.main_layout.addWidget(lbl_desc)
        self.text_desc = QTextEdit()
        self.text_desc.setStyleSheet(
            f"background-color: {COLOR_CARD}; border: none; font-family: Courier; color: white;")
        self.main_layout.addWidget(self.text_desc)

        # Footer Actions
        footer = QHBoxLayout()
        btn_cancel = QLabel("Cancel")
        btn_cancel.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-family: Courier;")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.mousePressEvent = lambda e: self.close()

        btn_save = QLabel("Save Idea")
        btn_save.setStyleSheet("color: #FFFFFF; font-family: Courier; font-weight: bold;")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.mousePressEvent = lambda e: self.save_idea()

        footer.addWidget(btn_cancel)
        footer.addStretch()
        footer.addWidget(btn_save)
        self.main_layout.addLayout(footer)

    def init_archive_view(self):
        header = QHBoxLayout()
        lbl_title = QLabel("Idea Archive.")
        lbl_title.setFont(QFont("Courier", 14, QFont.Weight.Bold))
        header.addWidget(lbl_title)
        self.main_layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        db = load_database()
        if not db:
            empty_lbl = QLabel("ARCHIVE EMPTY")
            empty_lbl.setStyleSheet(f"color: {COLOR_DOT}; font-family: Courier;")
            scroll_layout.addWidget(empty_lbl)
        else:
            for idea_id, data in reversed(list(db.items())):
                card = QWidget()
                card.setStyleSheet(f"background-color: {COLOR_CARD}; border-radius: 4px;")
                card_layout = QVBoxLayout(card)

                title = QLabel(data["Name of Idea"])
                title.setStyleSheet("color: #FFFFFF; font-family: Courier; font-weight: bold;")
                card_layout.addWidget(title)

                if data["Description"].strip():
                    desc = QLabel(data["Description"])
                    desc.setWordWrap(True)
                    desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-family: Courier; font-size: 11px;")
                    card_layout.addWidget(desc)
                scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        self.main_layout.addWidget(scroll)

    def save_idea(self):
        name = self.entry_name.text()
        desc = self.text_desc.toPlainText()
        if not name.strip(): return

        db = load_database()
        coid = len(db) + 1
        db[f"Idea{coid}"] = {
            "Name of Idea": name,
            "Description": desc,
            "Date and Time": datetime.now().strftime("%d %b %Y // %H:%M")
        }
        save_to_json(db)
        self.close()

    def changeEvent(self, event):
        """Vanish-Effekt: Schließt das Fenster sofort, wenn es den Fokus verliert"""
        if event.type() == QEvent.Type.ActivationChange and not self.isActiveWindow():
            self.close()


# --- NATIVE TASKBAR OVERLAYS (Position Fixed) ---
class NativeTaskbarIconOverlay(QWidget):
    def __init__(self, mode="add", offset_x=0, symbol="+"):
        super().__init__()
        self.mode = mode
        self.symbol = symbol

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.resize(36, 36)

        # Positionierung korrigiert: Sitzt jetzt perfekt im freien Bereich vor der System-Tray-Leiste
        screen = QApplication.primaryScreen().geometry()
        self.x_pos = screen.width() - 250 + offset_x
        self.y_pos = screen.height() - 42
        self.move(self.x_pos, self.y_pos)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Subtiler Hintergrund bei Hover-Simulation
        painter.setPen(Qt.GlobalColor.transparent)
        painter.setBrush(QColor(255, 255, 255, 12))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 18, 18)

        # Weißer Nothing-Ring
        painter.setPen(QColor("#FFFFFF"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(4, 4, 28, 28)

        # Roter Punkt
        painter.setBrush(QColor(COLOR_DOT))
        painter.setPen(Qt.GlobalColor.transparent)
        painter.drawEllipse(22, 22, 6, 6)

        # Symbol (+ oder =)
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.symbol)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.menu = IdeaPadWidgetMenu(mode=self.mode, launch_x=self.x_pos)
            self.menu.show()


# --- LAUNCHER ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Erstellt die beiden sauberen Icons nebeneinander im nun freien Bereich
    icon_add = NativeTaskbarIconOverlay(mode="add", offset_x=-45, symbol="+")
    icon_add.show()

    icon_show = NativeTaskbarIconOverlay(mode="show", offset_x=0, symbol="=")
    icon_show.show()

    sys.exit(app.exec())