import tkinter as tk
from tkinter import messagebox
import json
import os
import datetime

# --- NOTHING DESIGN GUIDELINES ---
COLOR_BG = "#000000"
COLOR_CARD = "#121212"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_MUTED = "#666666"
COLOR_DOT = "#FF0033"

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


# --- HOVER & ANIMATION ELEMENTS ---
class EssentialButton(tk.Button):
    def __init__(self, master, text, command, **kwargs):
        super().__init__(
            master, text=text, command=command, font=FONT_BODY,
            fg=COLOR_TEXT_MAIN, bg=COLOR_CARD, activebackground=COLOR_TEXT_MAIN, activeforeground=COLOR_BG,
            bd=0, highlightthickness=0, padx=20, pady=15, cursor="hand2", **kwargs
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.config(bg="#1A1A1A")

    def on_leave(self, e):
        self.config(bg=COLOR_CARD)


# --- APPLICATION CORE ---
class IdeaPadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IdeaPad // OS")
        self.root.geometry("600x650")
        self.root.minsize(450, 500)
        self.root.configure(bg=COLOR_BG)

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.container = tk.Frame(self.root, bg=COLOR_BG)
        self.container.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

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
        frame.animate_fade_in()


# --- MIXIN FOR ANIMATIONS ---
class AnimatedFrame(tk.Frame):
    def animate_fade_in(self):
        widgets = self.winfo_children()
        for w in widgets:
            if hasattr(w, 'pack_info'):
                w.pack_configure(pady=(w.pack_info().get('pady', 0)))


# --- 1. THE MAIN DASHBOARD ---
class MainMenu(AnimatedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)

        header_frame = tk.Frame(self, bg=COLOR_BG)
        header_frame.pack(fill="x", pady=(40, 60))

        tk.Label(header_frame, text="IdeaPad.", font=FONT_DOTMATRIX, fg=COLOR_TEXT_MAIN, bg=COLOR_BG, anchor="w").pack(
            side="left")
        tk.Label(header_frame, text="●", font=("Arial", 10), fg=COLOR_DOT, bg=COLOR_BG).pack(side="left", padx=5,
                                                                                             pady=(15, 0))
        tk.Label(header_frame, text="// SYSTEM CORE", font=FONT_TIMESTAMP, fg=COLOR_TEXT_MUTED, bg=COLOR_BG).pack(
            side="left", padx=5, pady=(12, 0))

        EssentialButton(self, text="⚡ Capture New Idea", command=lambda: controller.show_frame("AddIdeaPage")).pack(
            fill="x", pady=8)
        EssentialButton(self, text="📂 Open Idea Archive", command=lambda: controller.show_frame("ShowIdeasPage")).pack(
            fill="x", pady=8)

        exit_lbl = tk.Label(self, text="[ Power Off ]", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_BG,
                            cursor="hand2")
        exit_lbl.pack(side="bottom", pady=20)
        exit_lbl.bind("<Button-1>", lambda e: parent.quit())
        exit_lbl.bind("<Enter>", lambda e: exit_lbl.config(fg=COLOR_DOT))
        exit_lbl.bind("<Leave>", lambda e: exit_lbl.config(fg=COLOR_TEXT_MUTED))


# --- 2. THE CAPTURE INTERFACE ---
class AddIdeaPage(AnimatedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller

        tk.Label(self, text="New Idea.", font=FONT_DOTMATRIX, fg=COLOR_TEXT_MAIN, bg=COLOR_BG, anchor="w").pack(
            fill="x", pady=(10, 30))

        tk.Label(self, text="CONCEPT IDENTIFIER", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_BG, anchor="w").pack(
            fill="x")
        self.entry_name = tk.Entry(self, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG,
                                   insertbackground=COLOR_TEXT_MAIN, bd=0, highlightthickness=1,
                                   highlightbackground="#222222", highlightcolor=COLOR_TEXT_MAIN)
        self.entry_name.pack(fill="x", pady=(5, 25), ipady=10)

        tk.Label(self, text="THOUGHT DATA // NOTES", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_BG,
                 anchor="w").pack(fill="x")
        self.text_desc = tk.Text(self, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD,
                                 insertbackground=COLOR_TEXT_MAIN, bd=0, highlightthickness=0, height=8)
        self.text_desc.pack(fill="both", expand=True, pady=(5, 20))

        footer = tk.Frame(self, bg=COLOR_BG)
        footer.pack(fill="x", side="bottom", pady=10)

        tk.Button(footer, text="✕ Cancel", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_BG, bd=0,
                  activebackground=COLOR_BG, activeforeground=COLOR_TEXT_MAIN,
                  command=lambda: controller.show_frame("MainMenu")).pack(side="left")
        EssentialButton(footer, text="Save to Archive", command=self.save_idea).pack(side="right")

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


# --- 3. THE ARCHIVE FEED (Safe Configure & Inline Editing) ---
class ShowIdeasPage(AnimatedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller

        header = tk.Frame(self, bg=COLOR_BG)
        header.pack(fill="x", pady=(0, 25))

        tk.Button(header, text="← Menu", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG, bd=0,
                  activebackground=COLOR_BG, activeforeground=COLOR_TEXT_MUTED,
                  command=lambda: controller.show_frame("MainMenu")).pack(side="left")
        tk.Label(header, text="Idea Archive", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_BG).pack(side="right",
                                                                                                      pady=5)

        self.canvas = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfig(self.canvas_window, width=event.width))

        self.canvas.pack(fill="both", expand=True)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.winfo_containing(event.x_root, event.y_root):  # Scrollt nur, wenn die Maus im App-Fenster ist
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def safe_wrap(self, event, label_widget):
        """Verhindert Terminal-Fehler beim Löschen/Schließen, indem die Existenz des Widgets geprüft wird"""
        if label_widget.winfo_exists():
            label_widget.config(wraplength=event.width - 40)

    def refresh_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        db = load_database()
        if not db:
            tk.Label(self.scrollable_frame, text="ARCHIVE_EMPTY // NO_DATA", font=FONT_BODY, fg=COLOR_DOT,
                     bg=COLOR_BG).pack(pady=80)
            return

        for idea_id, data in reversed(list(db.items())):
            card = tk.Frame(self.scrollable_frame, bg=COLOR_CARD, padx=18, pady=18)
            card.pack(fill="x", pady=6, expand=True)

            # Meta Row
            meta_row = tk.Frame(card, bg=COLOR_CARD)
            meta_row.pack(fill="x", pady=(0, 10))
            tk.Label(meta_row, text=data.get('Date and Time', '-'), font=FONT_TIMESTAMP, fg=COLOR_TEXT_MUTED,
                     bg=COLOR_CARD).pack(side="left")

            action_frame = tk.Frame(meta_row, bg=COLOR_CARD)
            action_frame.pack(side="right")

            lbl_edit = tk.Label(action_frame, text="[ Edit ]", font=FONT_TIMESTAMP, fg=COLOR_TEXT_MUTED, bg=COLOR_CARD,
                                cursor="hand2")
            lbl_edit.pack(side="left", padx=5)
            lbl_edit.bind("<Enter>", lambda e, l=lbl_edit: l.config(fg=COLOR_TEXT_MAIN))
            lbl_edit.bind("<Leave>", lambda e, l=lbl_edit: l.config(fg=COLOR_TEXT_MUTED))
            lbl_edit.bind("<Button-1>", lambda e, c=card, i=idea_id, d=data: self.start_inline_edit(c, i, d))

            lbl_del = tk.Label(action_frame, text="✕ Wipe", font=FONT_TIMESTAMP, fg=COLOR_TEXT_MUTED, bg=COLOR_CARD,
                               cursor="hand2")
            lbl_del.pack(side="left", padx=5)
            lbl_del.bind("<Enter>", lambda e, l=lbl_del: l.config(fg=COLOR_DOT))
            lbl_del.bind("<Leave>", lambda e, l=lbl_del: l.config(fg=COLOR_TEXT_MUTED))
            lbl_del.bind("<Button-1>", lambda e, i=idea_id: self.delete_idea(i))

            # Display Content
            lbl_title = tk.Label(card, text=data["Name of Idea"], font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD,
                                 anchor="w")
            lbl_title.pack(fill="x", pady=(0, 4))

            if data["Description"].strip():
                desc_label = tk.Label(card, text=data["Description"], font=FONT_BODY, fg=COLOR_TEXT_MUTED,
                                      bg=COLOR_CARD, justify="left", anchor="w")
                desc_label.pack(fill="x", pady=(6, 0))
                # Nutzt jetzt die geschützte safe_wrap-Funktion
                card.bind("<Configure>", lambda event, lbl=desc_label: self.safe_wrap(event, lbl))

    def start_inline_edit(self, card_frame, idea_id, old_data):
        # Löscht alle Elemente außer der ersten Meta-Leiste für den Editier-Modus
        for w in card_frame.winfo_children()[1:]:
            w.destroy()

        edit_name = tk.Entry(card_frame, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG, bd=0, highlightthickness=1,
                             highlightbackground="#333333", highlightcolor=COLOR_TEXT_MAIN)
        edit_name.insert(0, old_data["Name of Idea"])
        edit_name.pack(fill="x", pady=5, ipady=4)

        edit_desc = tk.Text(card_frame, font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_BG, bd=0, highlightthickness=1,
                            highlightbackground="#333333", highlightcolor=COLOR_TEXT_MAIN, height=4)
        edit_desc.insert("1.0", old_data["Description"])
        edit_desc.pack(fill="x", pady=5)

        control_frame = tk.Frame(card_frame, bg=COLOR_CARD)
        control_frame.pack(fill="x", pady=(5, 0))

        # Cancel Option hinzugefügt
        cancel_lbl = tk.Label(control_frame, text="[ Cancel ]", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_CARD,
                              cursor="hand2")
        cancel_lbl.pack(side="left", pady=5)
        cancel_lbl.bind("<Enter>", lambda e: cancel_lbl.config(fg=COLOR_TEXT_MAIN))
        cancel_lbl.bind("<Leave>", lambda e: cancel_lbl.config(fg=COLOR_TEXT_MUTED))
        cancel_lbl.bind("<Button-1>", lambda
            e: self.refresh_list())  # Lädt die Liste einfach neu (bricht ungespeicherte Änderungen ab)

        save_lbl = tk.Label(control_frame, text="[ Save Changes ]", font=FONT_LABEL, fg=COLOR_DOT, bg=COLOR_CARD,
                            cursor="hand2")
        save_lbl.pack(side="right", pady=5)
        save_lbl.bind("<Button-1>",
                      lambda e: self.commit_inline_edit(idea_id, edit_name.get(), edit_desc.get("1.0", "end-1c")))

    def commit_inline_edit(self, idea_id, new_name, new_desc):
        if new_name.strip() == "":
            messagebox.showwarning("System", "Idea name cannot be blank.")
            return

        db = load_database()
        if idea_id in db:
            db[idea_id]["Name of Idea"] = new_name
            db[idea_id]["Description"] = new_desc
            db[idea_id]["Date and Time"] = datetime.datetime.now().strftime("%d %b %Y // %H:%M") + " (Edited)"
            save_to_json(db)
            self.refresh_list()

    def delete_idea(self, idea_id):
        if messagebox.askyesno("IdeaPad", "Wipe this memory permanent?"):
            db = load_database()
            if idea_id in db:
                del db[idea_id]
                save_to_json(db)
                self.refresh_list()


# --- RUN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = IdeaPadApp(root)
    root.mainloop()