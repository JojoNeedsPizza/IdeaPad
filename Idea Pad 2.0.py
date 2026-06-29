import tkinter as tk
from tkinter import messagebox
import json
import os
import datetime

# --- NOTHING ESSENTIAL SPACE DESIGN GUIDELINES ---
COLOR_BG = "#000000"  # Reines Schwarz
COLOR_CARD = "#121212"  # Essential Space Karten-Hintergrund
COLOR_TEXT_MAIN = "#FFFFFF"  # Hochkontrast-Weiß
COLOR_TEXT_MUTED = "#666666"  # Gedimmtes Grau für Systemdaten
COLOR_DOT = "#FF0033"  # Nothing-Signalrot (Der ikonische Punkt)

FONT_DOTMATRIX = ("Courier", 24, "bold")
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


# --- INTERACTIVE HOVER ELEMENTS ---
class EssentialButton(tk.Button):
    """Minimalistische Kapsel-Buttons wie im Nothing OS"""

    def __init__(self, master, text, command, **kwargs):
        super().__init__(
            master, text=text, command=command, font=FONT_BODY,
            fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, activebackground=COLOR_TEXT_MAIN, activeforeground=COLOR_BG,
            bd=0, highlightthickness=0, padx=20, pady=10, cursor="hand2", **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg="#1A1A1A"))
        self.bind("<Leave>", lambda e: self.config(bg=COLOR_CARD))


# --- APPLICATION CORE ---
class IdeaPadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Essential Space // IdeaPad")
        self.root.geometry("600x650")
        self.root.configure(bg=COLOR_BG)

        self.container = tk.Frame(self.root, bg=COLOR_BG)
        self.container.pack(fill="both", expand=True, padx=25, pady=25)

        self.frames = {}
        for F in (MainMenu, AddIdeaPage, ShowIdeasPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "ShowIdeasPage":
            frame.refresh_list()
        frame.tkraise()


# --- 1. THE MAIN DASHBOARD ---
class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)

        # Oben links platziertes Logo im typischen "Punkt-Stil"
        header_frame = tk.Frame(self, bg=COLOR_BG)
        header_frame.pack(fill="x", pady=(40, 60))

        tk.Label(header_frame, text="Space.", font=FONT_DOTMATRIX, fg=COLOR_TEXT_MAIN, bg=COLOR_BG, anchor="w").pack(
            side="left")
        tk.Label(header_frame, text="●", font=("Arial", 10), fg=COLOR_DOT, bg=COLOR_BG).pack(side="left", padx=5,
                                                                                             pady=(15, 0))
        tk.Label(header_frame, text="// IDEAPAD CORE", font=FONT_TIMESTAMP, fg=COLOR_TEXT_MUTED, bg=COLOR_BG).pack(
            side="left", padx=5, pady=(12, 0))
        # Zwei große Kacheln als Interface-Elemente
        EssentialButton(self, text="⚡ Capture Idea", command=lambda: controller.show_frame("AddIdeaPage")).pack(
            fill="x", pady=8)
        EssentialButton(self, text="📂 Open Memories", command=lambda: controller.show_frame("ShowIdeasPage")).pack(
            fill="x", pady=8)

        # Ein dezenter Exit-Link ganz unten
        exit_lbl = tk.Label(self, text="[ Power Off ]", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_BG,
                            cursor="hand2")
        exit_lbl.pack(side="bottom", pady=20)
        exit_lbl.bind("<Button-1>", lambda e: parent.quit())
        exit_lbl.bind("<Enter>", lambda e: exit_lbl.config(fg=COLOR_DOT))
        exit_lbl.bind("<Leave>", lambda e: exit_lbl.config(fg=COLOR_TEXT_MUTED))

        # --- 2. THE CAPTURE INTERFACE ---


class AddIdeaPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller

        tk.Label(self, text="New Memory.", font=FONT_DOTMATRIX, fg=COLOR_TEXT_MAIN, bg=COLOR_BG, anchor="w").pack(
            fill="x", pady=(10, 40))

        # Minimalistisches Eingabefeld (Keine Box, nur eine feine graue Linie unten drunter)
        tk.Label(self, text="CONCEPT IDENTIFIER", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_BG, anchor="w").pack(
            fill="x")
        self.entry_name = tk.Entry(self, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG,
                                   insertbackground=COLOR_TEXT_MAIN, bd=0, highlightthickness=1,
                                   highlightbackground="#222222", highlightcolor=COLOR_TEXT_MAIN)
        self.entry_name.pack(fill="x", pady=(5, 30), ipady=10)

        tk.Label(self, text="THOUGHT DATA // NOTES", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_BG,
                 anchor="w").pack(fill="x")
        self.text_desc = tk.Text(self, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD,
                                 insertbackground=COLOR_TEXT_MAIN, bd=0, highlightthickness=0, height=8)
        self.text_desc.pack(fill="x", pady=(5, 20))

        # Navigation Bar am unteren Rand
        footer = tk.Frame(self, bg=COLOR_BG)
        footer.pack(fill="x", side="bottom", pady=10)

        tk.Button(footer, text="✕ Cancel", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_BG, bd=0,
                  activebackground=COLOR_BG, activeforeground=COLOR_TEXT_MAIN,
                  command=lambda: controller.show_frame("MainMenu")).pack(side="left")
        EssentialButton(footer, text="Save to Space", command=self.save_idea).pack(side="right")

        self.text_desc.bind("<Shift-Return>", lambda event: self.save_idea())

    def save_idea(self):
        name = self.entry_name.get()
        desc = self.text_desc.get("1.0", "end-1c")

        if name.strip() == "":
            messagebox.showwarning("System", "Identification title required.")
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

        self.entry_name.delete(0, "end")
        self.text_desc.delete("1.0", "end")
        self.controller.show_frame("MainMenu")


# --- 3. THE MEMORIES FEED (Essential Space View) ---
class ShowIdeasPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_BG)
        header.pack(fill="x", pady=(0, 25))

        tk.Button(header, text="← Space", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG, bd=0,
                  activebackground=COLOR_BG, activeforeground=COLOR_TEXT_MUTED,
                  command=lambda: controller.show_frame("MainMenu")).pack(side="left")
        tk.Label(header, text="All Memories", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_BG).pack(side="right",
                                                                                                      pady=5)

        # Der unauffällige Scroll-Bereich
        self.canvas = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, bg=COLOR_BG)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def refresh_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        db = load_database()
        if not db:
            tk.Label(self.scrollable_frame, text="SPACE_EMPTY // NO_MEMORIES", font=FONT_BODY, fg=COLOR_DOT,
                     bg=COLOR_BG).pack(pady=80)
            return

        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Genau wie im echten Space: Timeline-Karten
        for idea_id, data in reversed(list(db.items())):
            card = tk.Frame(self.scrollable_frame, bg=COLOR_CARD, padx=18, pady=18)
            card.pack(fill="x", pady=6)

            # Obere Meta-Zeile
            meta_row = tk.Frame(card, bg=COLOR_CARD)
            meta_row.pack(fill="x", pady=(0, 10))
            tk.Label(meta_row, text=data.get('Date and Time', '-'), font=FONT_TIMESTAMP, fg=COLOR_TEXT_MUTED,
                     bg=COLOR_CARD).pack(side="left")

            # Subtiler Wipe-Link (Mülleimer) oben rechts in der Ecke
            lbl_del = tk.Label(meta_row, text="✕ Wipe", font=FONT_TIMESTAMP, fg=COLOR_TEXT_MUTED, bg=COLOR_CARD,
                               cursor="hand2")
            lbl_del.pack(side="right")
            lbl_del.bind("<Enter>", lambda e, l=lbl_del: l.config(fg=COLOR_DOT))
            lbl_del.bind("<Leave>", lambda e, l=lbl_del: l.config(fg=COLOR_TEXT_MUTED))
            lbl_del.bind("<Button-1>", lambda e, i=idea_id: self.delete_idea(i))

            # Inhalt
            tk.Label(card, text=data["Name of Idea"], font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, anchor="w",
                     wraplength=500).pack(fill="x", pady=(0, 4))

            # Wenn eine Beschreibung existiert, kriegt sie eine feine optische Trennung
            if data["Description"].strip():
                desc_label = tk.Label(card, text=data["Description"], font=FONT_BODY, fg=COLOR_TEXT_MUTED,
                                      bg=COLOR_CARD, wraplength=500, justify="left", anchor="w")
                desc_label.pack(fill="x", pady=(6, 0))

    def delete_idea(self, idea_id):
        if messagebox.askyesno("Essential Space", "Wipe this memory permanent?"):
            db = load_database()
            if idea_id in db:
                del db[idea_id]
                save_to_json(db)
                self.refresh_list()


# --- INITIALIZATION ---
if __name__ == "__main__":
    root = tk.Tk()
    app = IdeaPadApp(root)
    root.mainloop()