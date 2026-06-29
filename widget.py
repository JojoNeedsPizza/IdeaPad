import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, QPoint
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


# --- DETACHED POPUP WIDGET (The Menu from your Drawing) ---
class IdeaPadWidgetMenu(QWidget):
    def __init__(self, mode="add", launch_x=0):
        super().__init__()
        # Frameless, Stays on Top, Tool-Window (verhindert Taskleisten-Eintrag für das Popup)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setStyleSheet(f"background-color: {COLOR_BG}; border: 1px solid #222222; color: {COLOR_TEXT_MAIN};")

        self.width = 320
        self.height = 420

        # Positioniert das Menü exakt über dem geklickten Icon
        screen = QApplication.primaryScreen().availableGeometry()
        y_pos = screen.height() - self.height - 50  # Direkt über der Taskleiste
        self.setGeometry(launch_x - (self.width // 2) + 20, y_pos, self.width, self.height)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        if mode == "add":
            self.init_add_view()
        else:
            self.init_archive_view()

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

        # Name Input
        lbl_name = QLabel("ENTER IDEA NAME...")
        lbl_name.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px; font-family: Courier;")
        self.main_layout.addWidget(lbl_name)
        self.entry_name = QLineEdit()
        self.entry_name.setStyleSheet(
            "background: transparent; border: 1px solid #333333; padding: 6px; font-family: Courier;")
        self.main_layout.addWidget(self.entry_name)

        # Description Input
        lbl_desc = QLabel("DESCRIBE THE IDEA...")
        lbl_desc.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px; font-family: Courier;")
        self.main_layout.addWidget(lbl_desc)
        self.text_desc = QTextEdit()
        self.text_desc.setStyleSheet(f"background-color: {COLOR_CARD}; border: none; font-family: Courier;")
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

        # ScrollArea für die Kacheln
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
            self.main_layout.addWidget(empty_lbl)
            return

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

    def leaveEvent(self, event):
        """Automatisches Schließen, wenn man die Maus wegbewegt (Vanish)"""
        self.close()


# --- NATIVE-LOOKING TASKBAR ICON OVERLAYS ---
class NativeTaskbarIconOverlay(QWidget):
    def __init__(self, mode="add", offset_x=0, symbol="+"):
        super().__init__()
        self.mode = mode
        self.symbol = symbol

        # Komplett rahmenlos, transparent und überlagert alles, taucht NICHT in der Taskleiste als Fenster auf
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Fest definierte Größe für das Icon auf der Taskleiste
        self.resize(36, 36)

        # Dynamische Positionierung unten rechts NEBEN der Wetteranzeige
        screen = QApplication.primaryScreen().geometry()
        # Platziert das Icon exakt auf Höhe der Windows-Taskleiste
        self.x_pos = screen.width() - 280 + offset_x
        self.y_pos = screen.height() - 42
        self.move(self.x_pos, self.y_pos)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.active_widget = None

    def paintEvent(self, event):
        """Zeichnet das wunderschöne, kreisrunde Nothing OS Icon direkt auf die Taskleiste"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Transparenter, weicher Hintergrund für Hover-Look (simuliert natives Windows-Verhalten)
        painter.setPen(Qt.GlobalColor.transparent)
        painter.setBrush(QColor(255, 255, 255, 15))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 6, 6)

        # Der weiße Nothing-Kreisring
        painter.setPen(QColor("#FFFFFF"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(4, 4, 28, 28)

        # Der ikonische rote Nothing-Punkt im inneren des Symbols
        painter.setBrush(QColor(COLOR_DOT))
        painter.setPen(Qt.GlobalColor.transparent)
        painter.drawEllipse(22, 22, 6, 6)

        # Das Textsymbol im Zentrum (+ oder ☰)
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.symbol)
        painter.end()

    def mousePressEvent(self, event):
        """Bei Klick ploppt das gezeichnete Widget direkt nach oben auf"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.active_widget = IdeaPadWidgetMenu(mode=self.mode, launch_x=self.x_pos)
            self.active_widget.show()


# --- CORE APPLICATION ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Erzeugt die zwei runden Taskleisten-Icons
    # Icon 1: Add Idea (+) Platziert links neben der Wetteranzeige
    icon_add = NativeTaskbarIconOverlay(mode="add", offset_x=-50, symbol="+")
    icon_add.show()

    # Icon 2: Show Archive (☰) Direkt daneben platziert
    icon_show = NativeTaskbarIconOverlay(mode="show", offset_x=-10, symbol="=")
    icon_show.show()

    sys.exit(app.exec())