import tkinter as tk
from tkinter import messagebox
import json
import os
import datetime

# --- SYSTEM FARBEN & FONTS (Nothing Style) ---
BG_COLOR = "#000000"  # Tiefschwarz
FG_COLOR = "#FFFFFF"  # Reinweiß
ACCENT_COLOR = "#FF0044"  # Nothing-Signalrot
CARD_BG = "#111111"  # Dunkelgrau für die Ideen-Boxen

FONT_TITLE = ("Courier", 24, "bold")
FONT_SUBTITLE = ("Courier", 12, "italic")
FONT_REGULAR = ("Courier", 10)
FONT_BOLD = ("Courier", 10, "bold")


# --- LOGIK ---

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


# --- GUI MAIN APPLICATION ---

class IdeaPadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IdeaPad // OS.1")
        self.root.geometry("600x550")
        self.root.configure(bg=BG_COLOR)

        self.container = tk.Frame(self.root, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True)

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


# --- 1. MAIN MENU (Nothing Redesign) ---

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)

        # Titel im Pixel/Coding-Look
        label = tk.Label(self, text="IdeaPad_.", font=FONT_TITLE, fg=FG_COLOR, bg=BG_COLOR)
        label.pack(pady=(60, 5))

        subtitle = tk.Label(self, text="v2.0 // BY JOJO", font=FONT_SUBTITLE, fg=ACCENT_COLOR, bg=BG_COLOR)
        subtitle.pack(pady=(0, 40))

        # Stylische, flache Buttons mit weißem Rahmen
        btn_style = {
            "font": FONT_REGULAR, "fg": FG_COLOR, "bg": BG_COLOR,
            "activebackground": FG_COLOR, "activeforeground": BG_COLOR,
            "bd": 1, "relief": "solid", "width": 25, "height": 2
        }

        tk.Button(self, text="[+ Add a new Idea ]", command=lambda: controller.show_frame("AddIdeaPage"),
                  **btn_style).pack(pady=10)
        tk.Button(self, text="[= Show Ideas     ]", command=lambda: controller.show_frame("ShowIdeasPage"),
                  **btn_style).pack(pady=10)

        # Exit Button in Signalrot
        exit_style = btn_style.copy()
        exit_style.update({"fg": ACCENT_COLOR, "activebackground": ACCENT_COLOR, "activeforeground": FG_COLOR})
        tk.Button(self, text="[x Exit Program   ]", command=parent.quit, **exit_style).pack(pady=10)


# --- 2. ADD IDEA PAGE (Nothing Redesign) ---

class AddIdeaPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        tk.Label(self, text="// ADD_NEW_IDEA", font=FONT_TITLE, fg=FG_COLOR, bg=BG_COLOR).pack(pady=20)

        # Name Input
        tk.Label(self, text="ENTER IDEA NAME:", font=FONT_BOLD, fg=ACCENT_COLOR, bg=BG_COLOR).pack(anchor="w", padx=50)
        self.entry_name = tk.Entry(self, font=FONT_REGULAR, fg=FG_COLOR, bg=CARD_BG, insertbackground=FG_COLOR, bd=1,
                                   relief="solid", width=50)
        self.entry_name.pack(pady=(5, 20), ipady=5)

        # Description Input
        tk.Label(self, text="DESCRIBE THE IDEA:", font=FONT_BOLD, fg=ACCENT_COLOR, bg=BG_COLOR).pack(anchor="w",
                                                                                                     padx=50)
        self.text_desc = tk.Text(self, font=FONT_REGULAR, fg=FG_COLOR, bg=CARD_BG, insertbackground=FG_COLOR, bd=1,
                                 relief="solid", width=50, height=8)
        self.text_desc.pack(pady=5)

        # Nav-Buttons am unteren Rand
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(fill="x", side="bottom", pady=30, padx=50)

        nav_style = {"font": FONT_REGULAR, "bg": BG_COLOR, "bd": 1, "relief": "solid", "height": 2,
                     "activebackground": FG_COLOR, "activeforeground": BG_COLOR}

        tk.Button(btn_frame, text="< BACK", fg=FG_COLOR, width=12, command=lambda: controller.show_frame("MainMenu"),
                  **nav_style).pack(side="left")
        tk.Button(btn_frame, text="[ SAVE_IDEA ]", fg=ACCENT_COLOR, width=15, command=self.save_idea, **nav_style).pack(
            side="right")

        self.text_desc.bind("<Shift-Return>", lambda event: self.save_idea())

    def save_idea(self):
        name = self.entry_name.get()
        desc = self.text_desc.get("1.0", "end-1c")

        if name.strip() == "":
            messagebox.showwarning("System Error", "Idea name cannot be empty.")
            return

        db = load_database()
        coid = len(db) + 1
        cdnt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db[f"Idea{coid}"] = {
            "Name of Idea": name,
            "Description": desc,
            "Date and Time": cdnt
        }

        save_to_json(db)

        self.entry_name.delete(0, "end")
        self.text_desc.delete("1.0", "end")
        self.controller.show_frame("MainMenu")


# --- 3. SHOW IDEAS PAGE (Nothing Redesign) ---

class ShowIdeasPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        # Header
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", pady=20, padx=20)

        tk.Button(header, text="< BACK", font=FONT_REGULAR, fg=FG_COLOR, bg=BG_COLOR,
                  activebackground=FG_COLOR, activeforeground=BG_COLOR, bd=1, relief="solid",
                  command=lambda: controller.show_frame("MainMenu")).pack(side="left", padx=10)

        tk.Label(header, text="// STORAGE_ALL", font=FONT_TITLE, fg=ACCENT_COLOR, bg=BG_COLOR).pack(side="right",
                                                                                                    padx=10)

        # Scrollbarer Bereich komplett in Schwarz gehalten
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, bg=BG_COLOR)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        self.scrollbar.pack(side="right", fill="y")

    def refresh_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        db = load_database()
        if not db:
            tk.Label(self.scrollable_frame, text="NO IDEAS SAVED_.", font=FONT_REGULAR, fg=ACCENT_COLOR,
                     bg=BG_COLOR).pack(pady=40)
            return

        for idea_id, data in db.items():
            # Karten im "Nothing Phone-Case" Look: Dunkles Grau, dünner weißer Rahmen
            frame = tk.Frame(self.scrollable_frame, bg=CARD_BG, bd=1, relief="solid", padx=15, pady=15)
            frame.pack(fill="x", padx=10, pady=8)

            # Details
            tk.Label(frame, text=f"ID: {idea_id} // {data.get('Date and Time', '-')}", font=FONT_SUBTITLE,
                     fg=ACCENT_COLOR, bg=CARD_BG).pack(anchor="w")
            tk.Label(frame, text=data["Name of Idea"].upper(), font=FONT_TITLE, fg=FG_COLOR, bg=CARD_BG).pack(
                anchor="w", pady=(5, 10))
            tk.Label(frame, text=data["Description"], font=FONT_REGULAR, fg=FG_COLOR, bg=CARD_BG, wraplength=450,
                     justify="left").pack(anchor="w")

            # Delete Knopf als minimalistisches [X]
            btn_f = tk.Frame(frame, bg=CARD_BG)
            btn_f.pack(anchor="e", pady=(10, 0))
            tk.Button(btn_f, text="[ DELETE ]", font=FONT_REGULAR, fg=ACCENT_COLOR, bg=CARD_BG,
                      activebackground=ACCENT_COLOR, activeforeground=FG_COLOR, bd=0, cursor="hand2",
                      command=lambda i=idea_id: self.delete_idea(i)).pack(side="right")

    def delete_idea(self, idea_id):
        if messagebox.askyesno("SYSTEM", "DELETE THIS ENTRY?"):
            db = load_database()
            if idea_id in db:
                del db[idea_id]
                save_to_json(db)
                self.refresh_list()


# --- RUN APPLICATION ---
if __name__ == "__main__":
    root = tk.Tk()
    app = IdeaPadApp(root)
    root.mainloop()