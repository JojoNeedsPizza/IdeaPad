import tkinter as tk
from tkinter import messagebox
import json
import os
import datetime

# --- CONFIGURATION (Nothing OS 2.0 / 3.0 Look) ---
BG_COLOR = "#0B0B0B"  # Nahezu reines, edles Schwarz
CARD_BG = "#161616"  # Subtiles Dunkelgrau für Eingaben & Karten
FG_MAIN = "#FFFFFF"  # Haupttext in Weiß
FG_MUTED = "#888888"  # Gedimmter Text für Sekundenär-Infos
ACCENT = "#FF0033"  # Das unverkennbare Nothing-Signalrot

FONT_DISPLAY = ("Courier", 26, "bold")
FONT_HEADER = ("Courier", 16, "bold")
FONT_TEXT = ("Courier", 11)
FONT_SUB = ("Courier", 9, "italic")


# --- CORE LOGIC ---

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


# --- APP CONTROLLER ---

class IdeaPadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IdeaPad // NTHG_OS")
        self.root.geometry("650x600")
        self.root.configure(bg=BG_COLOR)

        self.container = tk.Frame(self.root, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True, padx=30, pady=30)

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


# --- STYLISH HOVER BUTTON WIDGET ---

class NothingButton(tk.Button):
    """Ein wiederverwendbarer Button im puren Nothing-Look mit Hover-Effekt"""

    def __init__(self, master, text, command, is_accent=False, **kwargs):
        fg = ACCENT if is_accent else FG_MAIN
        active_bg = ACCENT if is_accent else FG_MAIN
        active_fg = FG_MAIN if is_accent else BG_COLOR

        super().__init__(
            master, text=text, command=command, font=FONT_TEXT,
            fg=fg, bg=BG_COLOR, activebackground=active_bg, activeforeground=active_fg,
            bd=1, relief="solid", highlightthickness=0, padx=15, pady=8, cursor="hand2", **kwargs
        )
        # Invertierungseffekt beim Drüberfahren mit der Maus
        self.bind("<Enter>", lambda e: self.config(bg=active_bg, fg=active_fg))
        self.bind("<Leave>", lambda e: self.config(bg=BG_COLOR, fg=fg))


# --- 1. PAGE: MAIN MENU ---

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)

        # Header Element
        title_frame = tk.Frame(self, bg=BG_COLOR)
        title_frame.pack(pady=(60, 50), fill="x")

        tk.Label(title_frame, text="IdeaPad.", font=FONT_DISPLAY, fg=FG_MAIN, bg=BG_COLOR, anchor="w").pack(fill="x")
        tk.Label(title_frame, text="// OS.3_PRE_ALPHA", font=FONT_SUB, fg=FG_MUTED, anchor="w").pack(fill="x")

        # Intuitive Button-Anordnung
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill="x", pady=20)

        NothingButton(btn_frame, text="Add New Idea", command=lambda: controller.show_frame("AddIdeaPage")).pack(
            fill="x", pady=8)
        NothingButton(btn_frame, text="View Saved Ideas", command=lambda: controller.show_frame("ShowIdeasPage")).pack(
            fill="x", pady=8)
        NothingButton(btn_frame, text="Disconnect / Exit", command=parent.quit, is_accent=True).pack(fill="x", pady=30)


# --- 2. PAGE: ADD IDEA ---

class AddIdeaPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Page Title
        tk.Label(self, text="New Idea.", font=FONT_HEADER, fg=FG_MAIN, bg=BG_COLOR, anchor="w").pack(fill="x",
                                                                                                     pady=(10, 30))

        # Input Name
        tk.Label(self, text="CONCEPT NAME", font=FONT_SUB, fg=FG_MUTED, bg=BG_COLOR, anchor="w").pack(fill="x")
        self.entry_name = tk.Entry(self, font=FONT_TEXT, fg=FG_MAIN, bg=CARD_BG, insertbackground=FG_MAIN, bd=0,
                                   highlightthickness=1, highlightbackground="#333333", highlightcolor=FG_MAIN)
        self.entry_name.pack(fill="x", pady=(5, 25), ipady=8, padx=1)

        # Input Description
        tk.Label(self, text="DESCRIPTION // CORE DETAILS", font=FONT_SUB, fg=FG_MUTED, bg=BG_COLOR, anchor="w").pack(
            fill="x")
        self.text_desc = tk.Text(self, font=FONT_TEXT, fg=FG_MAIN, bg=CARD_BG, insertbackground=FG_MAIN, bd=0,
                                 highlightthickness=1, highlightbackground="#333333", highlightcolor=FG_MAIN, height=8)
        self.text_desc.pack(fill="x", pady=(5, 20), padx=1)

        # Navigation Footer
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill="x", side="bottom", pady=10)

        NothingButton(btn_frame, text="< Back", command=lambda: controller.show_frame("MainMenu")).pack(side="left")
        NothingButton(btn_frame, text="Commit Idea", command=self.save_idea, is_accent=True).pack(side="right")

        self.text_desc.bind("<Shift-Return>", lambda event: self.save_idea())

    def save_idea(self):
        name = self.entry_name.get()
        desc = self.text_desc.get("1.0", "end-1c")

        if name.strip() == "":
            messagebox.showwarning("System Notification", "Concept requires a valid identification name.")
            return

        db = load_database()
        coid = len(db) + 1
        cdnt = datetime.datetime.now().strftime("%Y/%m/%d @ %H:%M")

        db[f"Idea{coid}"] = {
            "Name of Idea": name,
            "Description": desc,
            "Date and Time": cdnt
        }

        save_to_json(db)

        self.entry_name.delete(0, "end")
        self.text_desc.delete("1.0", "end")
        self.controller.show_frame("MainMenu")


# --- 3. PAGE: SHOW IDEAS ---

class ShowIdeasPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Clean Header Row
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", pady=(0, 20))

        NothingButton(header, text="< Back", command=lambda: controller.show_frame("MainMenu")).pack(side="left")
        tk.Label(header, text="Storage.", font=FONT_HEADER, fg=FG_MAIN, bg=BG_COLOR).pack(side="right", pady=5)

        # Scrollable Minimalist Feed
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, bg=BG_COLOR)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y", padx=(10, 0))

    def refresh_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        db = load_database()
        if not db:
            tk.Label(self.scrollable_frame, text="NO_DATA_FOUND // ARCHIVE_EMPTY", font=FONT_TEXT, fg=ACCENT,
                     bg=BG_COLOR).pack(pady=60)
            return

        # Trick, um die Breite an das Fenster anzupassen
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        for idea_id, data in reversed(list(db.items())):  # Die neuesten Ideen stehen jetzt intuitiv ganz oben!
            # Cleane Karte ohne harte Ränder, sondern durch Farbflächen getrennt
            card = tk.Frame(self.scrollable_frame, bg=CARD_BG, padx=20, pady=20)
            card.pack(fill="x", pady=6)

            # Header-Zeile innerhalb der Karte (ID & Zeit)
            top_row = tk.Frame(card, bg=CARD_BG)
            top_row.pack(fill="x", pady=(0, 8))
            tk.Label(top_row, text=f"// ID: {idea_id}", font=FONT_SUB, fg=ACCENT, bg=CARD_BG).pack(side="left")
            tk.Label(top_row, text=data.get('Date and Time', '-'), font=FONT_SUB, fg=FG_MUTED, bg=CARD_BG).pack(
                side="right")

            # Content
            tk.Label(card, text=data["Name of Idea"].upper(), font=FONT_HEADER, fg=FG_MAIN, bg=CARD_BG,
                     anchor="w").pack(fill="x", pady=(0, 6))
            tk.Label(card, text=data["Description"], font=FONT_TEXT, fg=FG_MAIN, bg=CARD_BG, wraplength=520,
                     justify="left", anchor="w").pack(fill="x")

            # Subtiler Delete-Link statt klobigem Button
            lbl_del = tk.Label(card, text="[ WIPE_ENTRY ]", font=FONT_SUB, fg=FG_MUTED, bg=CARD_BG, cursor="hand2")
            lbl_del.pack(anchor="e", pady=(15, 0))
            lbl_del.bind("<Enter>", lambda e, l=lbl_del: l.config(fg=ACCENT))
            lbl_del.bind("<Leave>", lambda e, l=lbl_del: l.config(fg=FG_MUTED))
            lbl_del.bind("<Button-1>", lambda e, i=idea_id: self.delete_idea(i))

    def delete_idea(self, idea_id):
        if messagebox.askyesno("ARCHIVE SYSTEM", "CONFIRM TOTAL DELETION?"):
            db = load_database()
            if idea_id in db:
                del db[idea_id]
                save_to_json(db)
                self.refresh_list()


# --- APPLICATION EXECUTION ---
if __name__ == "__main__":
    root = tk.Tk()
    app = IdeaPadApp(root)
    root.mainloop()