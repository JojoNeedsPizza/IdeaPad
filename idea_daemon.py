import sys
import json
import ctypes
import ctypes.wintypes
from pathlib import Path

import win32gui
import win32con

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPainterPath, QFont, QFontMetrics
)


# ═══════════════════════════════════════════════════════════════════════════════
# DPI  (VOR QApplication)
# ═══════════════════════════════════════════════════════════════════════════════
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)   # PER_MONITOR_AWARE
except OSError:
    ctypes.windll.user32.SetProcessDPIAware()


# ═══════════════════════════════════════════════════════════════════════════════
# Win32 Konstanten & Flags
# ═══════════════════════════════════════════════════════════════════════════════
GWL_EXSTYLE      = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080

SWP_ZORDER_ONLY = (
    win32con.SWP_NOMOVE |
    win32con.SWP_NOSIZE |
    win32con.SWP_NOACTIVATE
)

# Ideenspeicher (JSON neben dem Skript)
IDEAS_FILE = Path(__file__).parent / "ideas.json"


# ═══════════════════════════════════════════════════════════════════════════════
# Hilfsfunktionen
# ═══════════════════════════════════════════════════════════════════════════════

def get_work_area() -> tuple[int, int, int, int]:
    """Gibt (x, y, w, h) der primären Arbeitsfläche zurück (ohne Taskleiste)."""
    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_ulong),
                    ("rcMonitor", ctypes.wintypes.RECT),
                    ("rcWork",    ctypes.wintypes.RECT),
                    ("dwFlags",   ctypes.c_ulong)]
    pt   = ctypes.wintypes.POINT(0, 0)
    hmon = ctypes.windll.user32.MonitorFromPoint(pt, 1)
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(info))
    r = info.rcWork
    return r.left, r.top, r.right - r.left, r.bottom - r.top


def is_real_fullscreen() -> bool:
    """Erkennt echtes Exklusiv-Vollbild. Ignoriert maximierte Fenster."""
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
        fx, fy, fw, fh = r[0], r[1], r[2]-r[0], r[3]-r[1]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_ulong),
                    ("rcMonitor", ctypes.wintypes.RECT),
                    ("rcWork",    ctypes.wintypes.RECT),
                    ("dwFlags",   ctypes.c_ulong)]
    pt   = ctypes.wintypes.POINT(fx + fw//2, fy + fh//2)
    hmon = ctypes.windll.user32.MonitorFromPoint(pt, 2)
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(info))
    mr   = info.rcMonitor
    mw, mh = mr.right - mr.left, mr.bottom - mr.top
    return (abs(fw-mw) <= 2 and abs(fh-mh) <= 2 and
            abs(fx-mr.left) <= 2 and abs(fy-mr.top) <= 2)


def load_ideas() -> list[str]:
    if IDEAS_FILE.exists():
        try:
            return json.loads(IDEAS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_ideas(ideas: list[str]):
    IDEAS_FILE.write_text(json.dumps(ideas, ensure_ascii=False, indent=2),
                          encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# Nothing-Glyph Zeichenfunktionen (reines QPainter, kein SVG, kein Icon-File)
# ═══════════════════════════════════════════════════════════════════════════════

def _nothing_pen(painter: QPainter, color: QColor, width: float = 1.5):
    pen = QPen(color, width, Qt.PenStyle.SolidLine,
               Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)


def draw_notepad(p: QPainter, cx: float, cy: float, s: float, color: QColor):
    """
    Notizblock-Glyph im Nothing-Outline-Stil.
    cx/cy = Mittelpunkt, s = Skalierung (1.0 ≈ 20px Höhe)
    Zeichnet: Seiten-Rechteck + 3 Linien + kleines Eselsohr oben rechts.
    """
    _nothing_pen(p, color, 1.4 * s)

    bw = 11 * s   # Block-Breite
    bh = 14 * s   # Block-Höhe
    ear = 3.5 * s # Eselsohr-Größe

    x0 = cx - bw / 2
    y0 = cy - bh / 2

    # Körper (mit Eselsohr oben rechts ausgestanzt)
    path = QPainterPath()
    path.moveTo(x0, y0)
    path.lineTo(x0 + bw - ear, y0)          # Oberkante bis Eselsohr
    path.lineTo(x0 + bw, y0 + ear)          # Eselsohr diagonal
    path.lineTo(x0 + bw, y0 + bh)           # Rechte Seite runter
    path.lineTo(x0, y0 + bh)                # Unterkante
    path.closeSubpath()                      # Linke Seite hoch
    p.drawPath(path)

    # Eselsohr-Knick (kleine diagonale Linie im Eck)
    _nothing_pen(p, color, 1.0 * s)
    p.drawLine(QPointF(x0 + bw - ear, y0),
               QPointF(x0 + bw - ear, y0 + ear))
    p.drawLine(QPointF(x0 + bw - ear, y0 + ear),
               QPointF(x0 + bw, y0 + ear))

    # 3 Textlinien
    lx0 = x0 + 2.5 * s
    lx1 = x0 + bw - 3.5 * s
    for i in range(3):
        ly = y0 + 4.5 * s + i * 3.2 * s
        p.drawLine(QPointF(lx0, ly), QPointF(lx1, ly))


def draw_plus(p: QPainter, cx: float, cy: float, s: float, color: QColor):
    """
    Plus-Kreuz im Nothing-Stil: dicke runde Linien, kein Fill.
    Kleine Größe — sitzt rechts unten neben dem Notizblock.
    """
    _nothing_pen(p, color, 1.6 * s)
    r = 3.5 * s
    p.drawLine(QPointF(cx - r, cy), QPointF(cx + r, cy))   # horizontal
    p.drawLine(QPointF(cx, cy - r), QPointF(cx, cy + r))   # vertikal


def draw_eye(p: QPainter, cx: float, cy: float, s: float, color: QColor):
    """
    Auge im Nothing-Outline-Stil: Mandelform + Iris-Kreis + kleiner Glanzpunkt.
    """
    _nothing_pen(p, color, 1.4 * s)

    # Mandelform (zwei Bögen)
    ew = 9.0 * s   # halbe Breite
    eh = 4.5 * s   # halbe Höhe

    eye_path = QPainterPath()
    # Oberer Bogen
    eye_path.moveTo(cx - ew, cy)
    eye_path.cubicTo(cx - ew * 0.4, cy - eh * 1.6,
                     cx + ew * 0.4, cy - eh * 1.6,
                     cx + ew, cy)
    # Unterer Bogen
    eye_path.cubicTo(cx + ew * 0.4, cy + eh * 1.6,
                     cx - ew * 0.4, cy + eh * 1.6,
                     cx - ew, cy)
    p.drawPath(eye_path)

    # Iris-Kreis
    ir = 2.8 * s
    p.drawEllipse(QPointF(cx, cy), ir, ir)

    # Glanzpunkt (kleiner gefüllter Punkt)
    painter_brush = QBrush(color)
    p.setBrush(painter_brush)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(cx + ir * 0.45, cy - ir * 0.45),
                  0.7 * s, 0.7 * s)
    p.setBrush(Qt.BrushStyle.NoBrush)


# ═══════════════════════════════════════════════════════════════════════════════
# Dock-Button: Klickbarer Bereich mit Glyph
# ═══════════════════════════════════════════════════════════════════════════════

class GlyphButton:
    """Kein QWidget — reine Daten + Zeichenlogik für einen Slot im Dock."""
    def __init__(self, x: int, w: int, draw_fn, label: str):
        self.x     = x       # linker Rand im Dock
        self.w     = w       # Breite des Slots
        self.draw  = draw_fn # Callable: (painter, cx, cy, s, color)
        self.label = label
        self.hovered = False

    def contains(self, px: int) -> bool:
        return self.x <= px < self.x + self.w

    def color(self) -> QColor:
        return QColor(220, 220, 220) if self.hovered else QColor(150, 150, 150)


# ═══════════════════════════════════════════════════════════════════════════════
# AddIdeaWindow
# ═══════════════════════════════════════════════════════════════════════════════

class AddIdeaWindow(QWidget):
    """Popup-Eingabefenster. Benutzt Qt.Popup → bekommt normalen Fokus."""

    def __init__(self, dock_x: int, dock_y: int):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Popup
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.win_w, self.win_h = 280, 90
        # Positionierung: zentriert über dem Dock
        px = dock_x + 5
        py = dock_y - self.win_h - 8
        self.setGeometry(px, py, self.win_w, self.win_h)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header
        header_row = QHBoxLayout()
        lbl = QLabel("NEW IDEA")
        lbl.setStyleSheet(
            "color: #666666; font-family: 'Segoe UI'; "
            "font-size: 9px; font-weight: bold; letter-spacing: 2px;"
        )
        header_row.addWidget(lbl)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Eingabefeld
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
            QLineEdit:focus { border-bottom: 1px solid #888888; }
        """)
        self.field.returnPressed.connect(self._save_and_close)
        layout.addWidget(self.field)

        self.field.setFocus()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(12, 12, 12, 248)))
        p.setPen(QPen(QColor(45, 45, 45), 1))
        p.drawRoundedRect(0, 0, self.win_w, self.win_h, 12, 12)

        # Nothing-Akzentpunkt (rot, oben rechts)
        p.setBrush(QBrush(QColor(229, 43, 31)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(self.win_w - 14, 14), 3, 3)

    def _save_and_close(self):
        text = self.field.text().strip()
        if text:
            ideas = load_ideas()
            ideas.insert(0, text)   # Neueste zuerst
            save_ideas(ideas)
        self.close()


# ═══════════════════════════════════════════════════════════════════════════════
# ShowIdeasWindow
# ═══════════════════════════════════════════════════════════════════════════════

class ShowIdeasWindow(QWidget):
    """Popup-Liste aller gespeicherten Ideen."""

    def __init__(self, dock_x: int, dock_y: int):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Popup
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.win_w, self.win_h = 280, 220
        px = dock_x + 5
        py = dock_y - self.win_h - 8
        self.setGeometry(px, py, self.win_w, self.win_h)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        lbl = QLabel("SAVED IDEAS")
        lbl.setStyleSheet(
            "color: #666666; font-family: 'Segoe UI'; "
            "font-size: 9px; font-weight: bold; letter-spacing: 2px;"
        )
        layout.addWidget(lbl)

        # Scrollbereich für viele Ideen
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFrameStyle(QFrame.Shape.NoFrame)
        self.text.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: #CCCCCC;
                border: none;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QScrollBar:vertical {
                background: #1A1A1A; width: 4px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #444444; border-radius: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        ideas = load_ideas()
        if ideas:
            self.text.setPlainText("\n".join(f"– {idea}" for idea in ideas))
        else:
            self.text.setPlainText("No ideas yet.\nPress the + button to add one.")
            self.text.setStyleSheet(self.text.styleSheet() +
                                    "QTextEdit { color: #555555; font-style: italic; }")
        layout.addWidget(self.text)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor(12, 12, 12, 248)))
        p.setPen(QPen(QColor(45, 45, 45), 1))
        p.drawRoundedRect(0, 0, self.win_w, self.win_h, 12, 12)

        # Nothing-Akzentpunkt
        p.setBrush(QBrush(QColor(229, 43, 31)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(self.win_w - 14, 14), 3, 3)


# ═══════════════════════════════════════════════════════════════════════════════
# NothingDock — Haupt-Overlay
# ═══════════════════════════════════════════════════════════════════════════════

class NothingDock(QWidget):

    DOCK_W  = 170
    DOCK_H  = 38
    MARGIN  = 8   # Abstand zur Bildschirmkante
    SCALE   = 1.1 # Glyph-Skalierung

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # ── Position berechnen ────────────────────────────────────────────────
        wx, wy, ww, wh = get_work_area()
        self.dock_x = wx + ww - self.DOCK_W - self.MARGIN
        self.dock_y = wy + wh - self.DOCK_H - 4
        self.setGeometry(self.dock_x, self.dock_y, self.DOCK_W, self.DOCK_H)

        # ── Slot-Definitionen ─────────────────────────────────────────────────
        sw = self.DOCK_W // 2
        self._buttons = [
            GlyphButton(0,  sw, self._draw_add_idea,   "Add Idea"),
            GlyphButton(sw, sw, self._draw_show_ideas,  "Show Ideas"),
        ]

        # ── State ─────────────────────────────────────────────────────────────
        self._hwnd            = None
        self._was_fullscreen  = False
        self.active_popup     = None
        self._hover_x         = -1

        self.setMouseTracking(True)

        # ── Timer ─────────────────────────────────────────────────────────────
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_state)
        self._timer.start(500)

    # ── Win32 Style Setup ─────────────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_win32_styles()

    def _apply_win32_styles(self):
        self._hwnd = int(self.winId())
        ex = ctypes.windll.user32.GetWindowLongW(self._hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            self._hwnd, GWL_EXSTYLE,
            ex | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW
        )
        win32gui.SetWindowPos(
            self._hwnd, win32con.HWND_TOPMOST,
            0, 0, 0, 0, SWP_ZORDER_ONLY
        )

    # ── State-Update (Timer) ──────────────────────────────────────────────────

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
            self.show()   # → showEvent → _apply_win32_styles
            return
        if not full and self.isVisible():
            win32gui.SetWindowPos(
                self._hwnd, win32con.HWND_TOPMOST,
                0, 0, 0, 0, SWP_ZORDER_ONLY
            )

    # ── Popup-Trigger ─────────────────────────────────────────────────────────

    def _close_popup(self):
        if self.active_popup:
            try:
                self.active_popup.close()
            except Exception:
                pass
            self.active_popup = None

    def trigger_add_idea(self):
        self._close_popup()
        self.active_popup = AddIdeaWindow(self.dock_x, self.dock_y)
        self.active_popup.show()
        self.active_popup.raise_()
        self.active_popup.activateWindow()

    def trigger_show_ideas(self):
        self._close_popup()
        self.active_popup = ShowIdeasWindow(self.dock_x, self.dock_y)
        self.active_popup.show()
        self.active_popup.raise_()
        self.active_popup.activateWindow()

    # ── Maus-Events ───────────────────────────────────────────────────────────

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

    # ── Glyph-Zeichenfunktionen (Slot-spezifisch) ─────────────────────────────

    def _draw_add_idea(self, p: QPainter, cx: float, cy: float, color: QColor):
        """Notizblock + Plus-Kreuz (unten rechts)."""
        s = self.SCALE
        # Notizblock leicht nach links versetzt
        draw_notepad(p, cx - 5 * s, cy, s, color)
        # Plus rechts unten neben dem Block
        draw_plus(p, cx + 7 * s, cy + 4 * s, s, color)

    def _draw_show_ideas(self, p: QPainter, cx: float, cy: float, color: QColor):
        """Notizblock leicht schräg + Auge rechts unten."""
        s = self.SCALE
        # Notizblock leicht nach links
        draw_notepad(p, cx - 5 * s, cy, s, color)
        # Auge rechts unten
        draw_eye(p, cx + 7 * s, cy + 5 * s, s, color)

    # ── paintEvent ────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ── Hintergrund ───────────────────────────────────────────────────────
        p.setBrush(QBrush(QColor(10, 10, 10, 210)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.DOCK_W, self.DOCK_H, 9, 9)

        # Rahmen
        p.setPen(QPen(QColor(55, 55, 55, 160), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(0, 0, self.DOCK_W - 1, self.DOCK_H - 1, 9, 9)

        # ── Trennlinie zwischen den Slots ─────────────────────────────────────
        mid = self.DOCK_W // 2
        p.setPen(QPen(QColor(50, 50, 50, 140), 1))
        p.drawLine(mid, 7, mid, self.DOCK_H - 7)

        # ── Hover-Highlight ───────────────────────────────────────────────────
        for btn in self._buttons:
            if btn.hovered:
                p.setBrush(QBrush(QColor(255, 255, 255, 12)))
                p.setPen(Qt.PenStyle.NoPen)
                if btn is self._buttons[0]:
                    p.drawRoundedRect(1, 1, mid - 1, self.DOCK_H - 2, 9, 9)
                else:
                    p.drawRoundedRect(mid, 1, mid - 1, self.DOCK_H - 2, 9, 9)

        # ── Glyphen ───────────────────────────────────────────────────────────
        cy = self.DOCK_H / 2
        for btn in self._buttons:
            cx = btn.x + btn.w / 2
            btn.draw(p, cx, cy, btn.color())

        # ── Nothing-Akzentpunkt (oben rechts) ────────────────────────────────
        p.setBrush(QBrush(QColor(229, 43, 31)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(self.DOCK_W - 8, 8), 2.5, 2.5)

        p.end()


# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    dock = NothingDock()
    dock.show()

    sys.exit(app.exec())