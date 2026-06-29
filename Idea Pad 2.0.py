import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
import os
import datetime


# --- LOGIK (Dein alter Code, angepasst an GUI) ---

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


# --- GUI KLASSE ---

class IdeaPadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IdeaPad - Alpha")
        self.root.geometry("600x500")

        # Container für die verschiedenen Seiten
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        # Erstelle alle Seiten aus deiner Skizze
        for F in (MainMenu, AddIdeaPage, ShowIdeasPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "ShowIdeasPage":
            frame.refresh_list()  # Liste jedes Mal neu laden
        frame.tkraise()


# --- 1. SEITE: MAIN MENU (Oben Links in deiner Skizze) ---

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="IdeaPad", font=("Arial", 30, "bold"))
        label.pack(pady=40)

        btn_add = tk.Button(self, text="Add Idea", width=20, height=2,
                            command=lambda: controller.show_frame("AddIdeaPage"))
        btn_add.pack(pady=10)

        btn_show = tk.Button(self, text="Show Ideas", width=20, height=2,
                             command=lambda: controller.show_frame("ShowIdeasPage"))
        btn_show.pack(pady=10)

        btn_exit = tk.Button(self, text="Exit", width=20, height=2, command=parent.quit)
        btn_exit.pack(pady=10)


# --- 2. SEITE: ADD IDEA (Oben Rechts in deiner Skizze) ---

class AddIdeaPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="IdeaPad - Add Idea", font=("Arial", 14)).pack(pady=10)

        tk.Label(self, text="Enter Idea Name:").pack()
        self.entry_name = tk.Entry(self, width=50)
        self.entry_name.pack(pady=5)

        tk.Label(self, text="Describe the Idea:").pack()
        self.text_desc = tk.Text(self, width=50, height=10)
        self.text_desc.pack(pady=5)

        # Buttons unten
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", side="bottom", pady=20)

        tk.Button(btn_frame, text="Back", command=lambda: controller.show_frame("MainMenu")).pack(side="left", padx=20)
        tk.Button(btn_frame, text="Save Idea", command=self.save_idea).pack(side="right", padx=20)

        # DEIN SHORTCUT: Shift + Enter zum Speichern
        self.text_desc.bind("<Shift-Return>", lambda event: self.save_idea())

    def save_idea(self):
        name = self.entry_name.get()
        desc = self.text_desc.get("1.0", "end-1c")

        if name.strip() == "":
            messagebox.showwarning("Fehler", "Bitte gib einen Namen ein!")
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
        messagebox.showinfo("Erfolg", "Idee gespeichert!")

        # Felder leeren und zurück
        self.entry_name.delete(0, "end")
        self.text_desc.delete("1.0", "end")
        self.controller.show_frame("MainMenu")


# --- 3. SEITE: SHOW IDEAS (Unten Links in deiner Skizze) ---

class ShowIdeasPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        header = tk.Frame(self)
        header.pack(fill="x")
        tk.Button(header, text="< Go Back", command=lambda: controller.show_frame("MainMenu")).pack(side="left", padx=10)
        tk.Label(header, text="Your Ideas", font=("Arial", 12, "bold")).pack(side="left", padx=50)

        # Scrollbarer Bereich für Ideen
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def refresh_list(self):
        # Bestehende Liste löschen
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        db = load_database()
        if not db:
            tk.Label(self.scrollable_frame, text="Keine Ideen vorhanden.").pack(pady=20)
            return

        for idea_id, data in db.items():
            # Ein Rahmen pro Idee (wie in deiner Skizze)
            frame = tk.Frame(self.scrollable_frame, bd=1, relief="solid", padx=10, pady=10)
            frame.pack(fill="x", padx=10, pady=5)

            tk.Label(frame, text=data["Name of Idea"], font=("Arial", 10, "bold")).pack(anchor="w")
            tk.Label(frame, text=data["Description"], wraplength=400, justify="left").pack(anchor="w")

            # Buttons Edit/Delete
            btn_f = tk.Frame(frame)
            btn_f.pack(anchor="e")
            tk.Button(btn_f, text="Delete", fg="red", command=lambda i=idea_id: self.delete_idea(i)).pack(side="right")

    def delete_idea(self, idea_id):
        if messagebox.askyesno("Löschen", "Idee wirklich entfernen?"):
            db = load_database()
            if idea_id in db:
                del db[idea_id]
                save_to_json(db)
                self.refresh_list()


# --- START ---
if __name__ == "__main__":
    root = tk.Tk()
    app = IdeaPadApp(root)
    root.mainloop()