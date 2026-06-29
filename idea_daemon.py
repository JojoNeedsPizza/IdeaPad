"""
Nothing-Style System Dock — Robuste Windows-Overlay-Implementierung
====================================================================
Behebt:
  - False-Positive Vollbild-Detection (Schatten, maximierte Fenster)
  - Z-Order Race Condition zwischen Qt und win32
  - Fokus-Diebstahl durch fehlendes WS_EX_NOACTIVATE
  - DPI-Awareness-Konflikte zwischen Qt und ctypes
"""

import sys
import ctypes
import ctypes.wintypes
import win32gui
import win32con
import win32api

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

# ─── DPI: VOR QApplication setzen, Qt soll NICHT selbst skalieren ───────────
# PROCESS_PER_MONITOR_DPI_AWARE (2) ist stabiler als SYSTEM_AWARE (1)
# bei Multi-Monitor-Setups mit unterschiedlichen DPIs.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except OSError:
    # Fallback für ältere Windows-Versionen
    ctypes.windll.user32.SetProcessDPIAware()

# ─── Win32 Konstanten ────────────────────────────────────────────────────────
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000  # Fenster stiehlt NIE den Fokus
WS_EX_TOOLWINDOW = 0x00000080  # Kein Alt+Tab Eintrag
WS_EX_TOPMOST = 0x00000008  # Immer vorne (redundant zu HWND_TOPMOST, aber sicher)
WS_EX_LAYERED = 0x00080000  # Für TranslucentBackground nötig

SWP_FLAGS = (
        win32con.SWP_NOACTIVATE |  # Dieser Aufruf stiehlt keinen Fokus
        win32con.SWP_NOMOVE |  # Position NICHT via SetWindowPos setzen
        win32con.SWP_NOSIZE |  # Größe NICHT via SetWindowPos setzen
        win32con.SWP_SHOWWINDOW  # Sicherstellen dass es sichtbar ist
)


# WICHTIG: SWP_NOMOVE + SWP_NOSIZE → SetWindowPos nur für Z-Order benutzen.
# Qt ist für Position/Größe zuständig. So gibt es KEINEN Race Condition.


def get_screen_geometry() -> tuple[int, int, int, int]:
    """
    Gibt (x, y, width, height) des primären Monitors zurück.
    Nutzt MonitorFromPoint + GetMonitorInfo für korrekte DPI-unabhängige Werte.
    """
    pt = ctypes.wintypes.POINT(0, 0)
    hmon = ctypes.windll.user32.MonitorFromPoint(pt, 1)  # MONITOR_DEFAULTTOPRIMARY

    class MONITORINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("rcMonitor", ctypes.wintypes.RECT),
            ("rcWork", ctypes.wintypes.RECT),  # Arbeitsfläche (ohne Taskleiste!)
            ("dwFlags", ctypes.c_ulong),
        ]

    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)
    ctypes.windll.user32.GetMonitorInfoW(hmon, ctypes.byref(info))

    # rcWork = Desktop ohne Taskleiste. Perfekt für "an der Taskleiste kleben".
    r = info.rcWork
    return r.left, r.top, r.right - r.left, r.bottom - r.top


def is_real_fullscreen() -> bool:
    """
    Erkennt ECHTES Vollbild (Spiele, Video-Player im Exklusiv-Modus).
    Unterscheidet von maximierten normalen Fenstern.

    Methode: Vergleich des Foreground-Fenster-Rects mit dem MONITOR-Rect
             (nicht mit GetSystemMetrics, das gibt DPI-skalierte Werte zurück).
    """
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False

    # Desktop-Fenster und eigene Fenster ignorieren
    class_name = win32gui.GetClassName(hwnd)
    if class_name in ("Progman", "WorkerW", "Shell_TrayWnd"):
        return False

    # Fenster-Rect (OHNE Schatten, via DwmGetWindowAttribute)
    try:
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        rect = ctypes.wintypes.RECT()
        ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd,
            DWMWA_EXTENDED_FRAME_BOUNDS,
            ctypes.byref(rect),
            ctypes.sizeof(rect)
        )
        fw, fh = rect.right - rect.left, rect.bottom - rect.top
        fx, fy = rect.left, rect.top
    except Exception:
        # Fallback: klassisches GetWindowRect
        r = win32gui.GetWindowRect(hwnd)
        fx, fy, fw, fh = r[0], r[1], r[2] - r[0], r[3] - r[1]

    # Monitor-Rect für das Fenster ermitteln (NICHT GetSystemMetrics!)
    pt = ctypes.wintypes.POINT(fx + fw // 2, fy + fh // 2)
    hmon = ctypes.windll.user32.MonitorFromPoint(pt, 2)  # MONITOR_DEFAULTTONEAREST

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

    mr = info.rcMonitor  # Vollständiges Monitor-Rect inkl. Taskleiste
    mw = mr.right - mr.left
    mh = mr.bottom - mr.top

    # Echtes Vollbild: Fenster deckt den kompletten Monitor ab (nicht nur rcWork)
    # Toleranz von 2px für Sub-Pixel-Rendering-Unterschiede
    return (abs(fw - mw) <= 2 and abs(fh - mh) <= 2 and
            abs(fx - mr.left) <= 2 and abs(fy - mr.top) <= 2)


class NothingDock(QWidget):
    # ── Glyphen-Definitionen ─────────────────────────────────────────────────
    GLYPHS = ["◆", "◈", "◇", "⬡"]  # Ersetze durch deine Nothing-Glyphen

    def __init__(self):
        super().__init__()

        # ── Qt Window Flags ──────────────────────────────────────────────────
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # = kein Taskleisten-Eintrag in Qt
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)  # Qt-seitig

        # ── Geometrie berechnen ──────────────────────────────────────────────
        wx, wy, ww, wh = get_screen_geometry()
        self.dock_w = 160
        self.dock_h = 36
        self.dock_x = wx + ww - self.dock_w - 8  # 8px Rand zur Kante
        self.dock_y = wy + wh - self.dock_h - 4  # 4px über Taskleiste

        self.setGeometry(self.dock_x, self.dock_y, self.dock_w, self.dock_h)

        # ── State ────────────────────────────────────────────────────────────
        self._was_fullscreen = False
        self._hwnd = None

        # Timer: Vollbild-Check + Z-Order-Refresh
        # 500ms reicht – muss nicht 10× pro Sekunde prüfen.
        # Zu kurze Intervalle verursachen das Flackern!
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_state)
        self.timer.start(500)

    def showEvent(self, event):
        """Nach show() die Win32 Extended Styles setzen."""
        super().showEvent(event)
        self._apply_win32_styles()

    def _apply_win32_styles(self):
        """
        Setzt WS_EX_NOACTIVATE und HWND_TOPMOST einmalig via SetWindowLong.
        Das ist stabiler als es jedes Mal in SetWindowPos zu wiederholen.
        """
        self._hwnd = int(self.winId())

        # Aktuellen Extended Style lesen und Flags hinzufügen
        ex_style = ctypes.windll.user32.GetWindowLongW(self._hwnd, GWL_EXSTYLE)
        new_style = ex_style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW

        ctypes.windll.user32.SetWindowLongW(self._hwnd, GWL_EXSTYLE, new_style)

        # Einmalig HWND_TOPMOST setzen (nur Z-Order, keine Position/Größe)
        win32gui.SetWindowPos(
            self._hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
        )

    def _update_state(self):
        """
        Wird alle 500ms aufgerufen.
        Nur zwei Aufgaben: Vollbild-Check + Z-Order-Refresh.
        KEINE Positionsänderung hier (kein Race Condition).
        """
        if self._hwnd is None:
            return

        fullscreen = is_real_fullscreen()

        if fullscreen and not self._was_fullscreen:
            # Vollbild hat begonnen → verstecken
            self._was_fullscreen = True
            self.hide()
            return

        if not fullscreen and self._was_fullscreen:
            # Vollbild beendet → wieder zeigen + Styles neu setzen
            self._was_fullscreen = False
            self.show()
            # show() triggert showEvent → _apply_win32_styles()
            return

        if not fullscreen and self.isVisible():
            # Normalbetrieb: Z-Order auffrischen ohne Fokus zu stehlen.
            # SWP_NOMOVE + SWP_NOSIZE → NUR Z-Order wird geändert.
            win32gui.SetWindowPos(
                self._hwnd,
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_FLAGS
            )

    # ── Painting ─────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Hintergrund: leicht transparentes Schwarz (Nothing-Style)
        painter.setBrush(QColor(10, 10, 10, 200))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.dock_w, self.dock_h, 8, 8)

        # Dünner Rahmen
        painter.setPen(QPen(QColor(60, 60, 60, 180), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(0, 0, self.dock_w - 1, self.dock_h - 1, 8, 8)

        # Glyphen zeichnen
        font = QFont("Segoe UI", 14)
        painter.setFont(font)

        slot_w = self.dock_w // len(self.GLYPHS)
        for i, glyph in enumerate(self.GLYPHS):
            # Aktive Glyphe = weiß, inaktive = grau
            active = (i == 0)  # Beispiel: erste Glyphe aktiv
            painter.setPen(QColor(255, 255, 255) if active else QColor(80, 80, 80))
            painter.drawText(
                slot_w * i, 0, slot_w, self.dock_h,
                Qt.AlignmentFlag.AlignCenter,
                glyph
            )

        painter.end()


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # High-DPI Qt-Attribute VOR QApplication setzen
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Dock soll laufen bis sys.exit

    dock = NothingDock()
    dock.show()

    sys.exit(app.exec())

