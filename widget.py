import tkinter as tk
from tkinter import messagebox
import json
import os
import datetime

# --- NOTHING DESIGN GUIDELINES (Widget Edition) ---
COLOR_BG = "#000000"
COLOR_CARD = "#121212"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_MUTED = "#666666"
COLOR_DOT = "#FF0033"

FONT_LABEL = ("Courier", 10, "bold")
FONT_BODY = ("Courier", 11)
FONT_TIMESTAMP = ("Courier", 9)


# --- DATABASE LOGIC ---
def load_database():
    if os.path.exists("database.json"):
        with open("database.json", "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
            except json.JSONDecodeError:
                return {}
    return {}


def save_to_json(data):
    with open("database.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# --- INTERACTIVE LINKS ---
class ActionLabel(tk.Label):
    def __init__(self, master, text, command, active_color=COLOR_TEXT_MAIN, **kwargs):
        super().__init__(master, text=text, font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_BG, cursor="hand2", **kwargs)
        self.command = command
        self.active_color = active_color
        self.bind("<Enter>", lambda e: self.config(fg=self.active_color))
        self.bind("<Leave>", lambda e: self.config(fg=COLOR_TEXT_MUTED))
        self.bind("<Button-1>", lambda e: self.command())


# --- POPUP WIDGET WINDOW ---
class IdeaPadWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("IdeaPad Widget")
        self.root.configure(bg=COLOR_BG)

        # 1. Fensterränder entfernen für Widget-Look
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)  # Immer im Vordergrund beim Öffnen

        # 2. Fenstergröße definieren (Schmal & kompakt wie in deiner Skizze)
        self.width = 320
        self.height = 420
        self.position_above_taskbar()

        # Container für den Inhalt
        self.container = tk.Frame(self.root, bg=COLOR_BG, padx=20, pady=20)
        self.container.pack(fill="both", expand=True)

        # Starte standardmäßig mit der "Add Idea" Ansicht aus deiner Skizze
        self.show_add_view()

        # 3. VERSTECKEN WENN FOKUS VERLOREN GEHT (Wie Windows Taskbar Menüs)
        self.root.bind("<FocusOut>", lambda e: self.root.destroy())

        # Workaround: Manchmal verliert Tkinter den Fokus beim raustappen nicht sofort
        self.root.after(100, lambda: self.root.focus_force())

    def position_above_taskbar(self):
        """Berechnet die Position unten rechts, knapp über der Windows-Taskleiste"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Abstände (X = rechts, Y = Platz für die Windows Taskleiste unten, ca. 50-60 Pixel)
        x_pos = screen_width - self.width - 40
        y_pos = screen_height - self.height - 60

        self.root.geometry(f"{self.width}x{self.height}+{x_pos}+{y_pos}")

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- ANSICHT 1: ADD IDEA (Deine obere Zeichnung) ---
    def show_add_view(self):
        self.clear_container()

        # Header mit flachem Schließen [X]
        header = tk.Frame(self.container, bg=COLOR_BG)
        header.pack(fill="x", pady=(0, 15))
        tk.Label(header, text="Add Idea.", font=("Courier", 16, "bold"), fg=COLOR_TEXT_MAIN, bg=COLOR_BG).pack(
            side="left")
        close_lbl = tk.Label(header, text="✕", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_BG, cursor="hand2")
        close_lbl.pack(side="right")
        close_lbl.bind("<Button-1>", lambda e: self.root.destroy())

        # Inputs
        tk.Label(self.container, text="NAME OF IDEA...", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_BG,
                 anchor="w").pack(fill="x", pady=(5, 2))
        self.entry_name = tk.Entry(self.container, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG,
                                   insertbackground=COLOR_TEXT_MAIN, bd=0, highlightthickness=1,
                                   highlightbackground="#222222", highlightcolor=COLOR_TEXT_MAIN)
        self.entry_name.pack(fill="x", pady=(0, 15), ipady=6)

        tk.Label(self.container, text="DESCRIPTION...", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_BG,
                 anchor="w").pack(fill="x", pady=(5, 2))
        self.text_desc = tk.Text(self.container, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD,
                                 insertbackground=COLOR_TEXT_MAIN, bd=0, highlightthickness=0, height=8)
        self.text_desc.pack(fill="both", expand=True, pady=(0, 20))

        # Footer Actions
        footer = tk.Frame(self.container, bg=COLOR_BG)
        footer.pack(fill="x", side="bottom")

        ActionLabel(footer, text="Cancel", command=self.root.destroy, active_color=COLOR_DOT).pack(side="left")
        ActionLabel(footer, text="Save", command=self.save_widget_idea, active_color=COLOR_TEXT_MAIN).pack(side="right")

        # Shortcut: Shift + Enter speichert auch hier
        self.text_desc.bind("<Shift-Return>", lambda event: self.save_widget_idea())

    def save_widget_idea(self):
        name = self.entry_name.get()
        desc = self.text_desc.get("1.0", "end-1c")

        if name.strip() == "":
            return

        db = load_database()
        coid = len(db) + 1
        cdnt = datetime.datetime.now().strftime("%d %b %Y // %H:%M")

        db[f"Idea{coid}"] = {
            "Name of Idea": name,
            "Description": desc,
            "Date and Time": cdnt
        }
        save_to_json(db)

        # Schließt das Widget nach dem Speichern automatisch im Hintergrund
        self.root.destroy()


# --- START SCRIPT ---
if __name__ == "__main__":
    root = tk.Tk()
    app = IdeaPadWidget(root)
    root.mainloop()