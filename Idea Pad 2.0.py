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

SETTINGS_FILE = "settings.json"


# --- DATABASE & SETTINGS LOGIC ---
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


def load_settings():
    default_settings = {
        "autostart_bar": False,
        "keybinds_enabled": False,
        "keybind_new_idea": "<Control-n>",
        "keybind_show_ideas": "<Control-s>"
    }
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                for key, val in default_settings.items():
                    data.setdefault(key, val)
                return data
            except json.JSONDecodeError:
                return default_settings
    return default_settings


def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
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


# --- CUSTOM UI TOGGLE SWITCH ---
class TextToggleSwitch(tk.Button):
    def __init__(self, master, current_state=False, command=None, **kwargs):
        self.state = current_state
        self.user_command = command
        super().__init__(
            master, text="", font=FONT_LABEL, bd=0, highlightthickness=0,
            padx=10, pady=5, cursor="hand2", bg=COLOR_BG, activebackground=COLOR_BG, **kwargs
        )
        self.update_visuals()
        self.config(command=self.toggle)

    def toggle(self):
        self.state = not self.state
        self.update_visuals()
        if self.user_command:
            self.user_command(self.state)

    def update_visuals(self):
        if self.state:
            self.config(text="[ ON ]", fg=COLOR_TEXT_MAIN)
        else:
            self.config(text="[ OFF ]", fg=COLOR_TEXT_MUTED)

    def set_state(self, state):
        self.state = state
        self.update_visuals()


# --- APPLICATION CORE ---
class IdeaPadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IdeaPad // OS")
        self.root.geometry("600x650")
        self.root.minsize(450, 500)
        self.root.configure(bg=COLOR_BG)

        self.settings = load_settings()

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.container = tk.Frame(self.root, bg=COLOR_BG)
        self.container.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)

        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenu, AddIdeaPage, ShowIdeasPage, SettingsPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")
        self.apply_global_keybinds()

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "ShowIdeasPage":
            frame.refresh_list()
        elif page_name == "SettingsPage":
            frame.load_current_settings_to_ui()
        frame.tkraise()
        frame.animate_fade_in()

    def apply_global_keybinds(self):
        """Deaktiviert: Keybinds funktionieren in dieser Anwendung nicht mehr."""
        pass


# --- MIXIN FOR ANIMATIONS ---
class AnimatedFrame(tk.Frame):
    def animate_fade_in(self):
        widgets = self.winfo_children()
        for w in widgets:
            try:
                info = w.pack_info()
                w.pack_configure(pady=(info.get('pady', 0)))
            except tk.TclError:
                pass


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
            fill="x", pady=6)
        EssentialButton(self, text="📂 Open Idea Archive", command=lambda: controller.show_frame("ShowIdeasPage")).pack(
            fill="x", pady=6)
        EssentialButton(self, text="⚙ System Settings", command=lambda: controller.show_frame("SettingsPage")).pack(
            fill="x", pady=6)

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


# --- 3. THE ARCHIVE FEED ---
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
        if self.winfo_containing(event.x_root, event.y_root):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def safe_wrap(self, event, label_widget):
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

            lbl_title = tk.Label(card, text=data["Name of Idea"], font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_CARD,
                                 anchor="w")
            lbl_title.pack(fill="x", pady=(0, 4))

            if data["Description"].strip():
                desc_label = tk.Label(card, text=data["Description"], font=FONT_BODY, fg=COLOR_TEXT_MUTED,
                                      bg=COLOR_CARD, justify="left", anchor="w")
                desc_label.pack(fill="x", pady=(6, 0))
                card.bind("<Configure>", lambda event, lbl=desc_label: self.safe_wrap(event, lbl))

    def start_inline_edit(self, card_frame, idea_id, old_data):
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

        cancel_lbl = tk.Label(control_frame, text="[ Cancel ]", font=FONT_LABEL, fg=COLOR_TEXT_MUTED, bg=COLOR_CARD,
                              cursor="hand2")
        cancel_lbl.pack(side="left", pady=5)
        cancel_lbl.bind("<Enter>", lambda e: cancel_lbl.config(fg=COLOR_TEXT_MAIN))
        cancel_lbl.bind("<Leave>", lambda e: cancel_lbl.config(fg=COLOR_TEXT_MUTED))
        cancel_lbl.bind("<Button-1>", lambda e: self.refresh_list())

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


# --- 4. THE SYSTEM SETTINGS INTERFACE (With Interactive Key-Recorder) ---
class SettingsPage(AnimatedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)
        self.controller = controller

        # Header Block
        tk.Label(self, text="Settings.", font=FONT_DOTMATRIX, fg=COLOR_TEXT_MAIN, bg=COLOR_BG, anchor="w").pack(
            fill="x", pady=(10, 25))

        # --- Setting Row 1: Autostart Bar ---
        row_auto = tk.Frame(self, bg=COLOR_BG)
        row_auto.pack(fill="x", pady=12)
        tk.Label(row_auto, text="AUTOSTART DOCK BAR", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG).pack(side="left")
        self.toggle_autostart = TextToggleSwitch(row_auto, command=self.handle_toggle_change)
        self.toggle_autostart.pack(side="right")

        # --- Setting Row 2: Close Bar (Button Only) ---
        row_close = tk.Frame(self, bg=COLOR_BG)
        row_close.pack(fill="x", pady=12)
        tk.Label(row_close, text="DOCK OVERLAY CONTROL", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG).pack(
            side="left")

        btn_close_bar = tk.Button(
            row_close, text="[ Close Bar ]", font=FONT_LABEL, bd=0, highlightthickness=0,
            fg=COLOR_DOT, bg=COLOR_BG, activebackground=COLOR_BG, activeforeground=COLOR_TEXT_MAIN,
            cursor="hand2", command=self.close_dock_bar_signal
        )
        btn_close_bar.pack(side="right")

        # --- Setting Row 3: Keybind Master Switch ---
        row_keys = tk.Frame(self, bg=COLOR_BG)
        row_keys.pack(fill="x", pady=12)
        tk.Label(row_keys, text="GLOBAL SYSTEM KEYBINDS", font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG).pack(
            side="left")
        self.toggle_keybinds = TextToggleSwitch(row_keys, command=self.toggle_keybind_section)
        self.toggle_keybinds.pack(side="right")

        # --- Sub-Section: Keybind Configuration Fields ---
        self.sub_keybind_frame = tk.Frame(self, bg=COLOR_CARD, padx=15, pady=15)

        tk.Label(self.sub_keybind_frame, text="CAPTURE NEW IDEA BIND (CLICK TO RECORD)", font=FONT_LABEL,
                 fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, anchor="w").pack(fill="x")
        self.entry_kb_new = tk.Entry(self.sub_keybind_frame, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG,
                                     insertbackground=COLOR_TEXT_MAIN, bd=0, highlightthickness=1,
                                     highlightbackground="#222222", highlightcolor=COLOR_TEXT_MAIN)
        self.entry_kb_new.pack(fill="x", pady=(4, 12), ipady=6)

        tk.Label(self.sub_keybind_frame, text="OPEN ARCHIVE BIND (CLICK TO RECORD)", font=FONT_LABEL,
                 fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, anchor="w").pack(fill="x")
        self.entry_kb_show = tk.Entry(self.sub_keybind_frame, font=FONT_BODY, fg=COLOR_TEXT_MAIN, bg=COLOR_BG,
                                      insertbackground=COLOR_TEXT_MAIN, bd=0, highlightthickness=1,
                                      highlightbackground="#222222", highlightcolor=COLOR_TEXT_MAIN)
        self.entry_kb_show.pack(fill="x", pady=(4, 4), ipady=6)

        # Event-Bindings für interaktive Tastenaufnahme anheften
        self.entry_kb_new.bind("<FocusIn>", lambda e: self.start_recording(self.entry_kb_new))
        self.entry_kb_new.bind("<KeyPress>", lambda e: self.record_key(e, self.entry_kb_new))
        self.entry_kb_new.bind("<KeyRelease>", lambda e: self.stop_recording(e, self.entry_kb_new))

        self.entry_kb_show.bind("<FocusIn>", lambda e: self.start_recording(self.entry_kb_show))
        self.entry_kb_show.bind("<KeyPress>", lambda e: self.record_key(e, self.entry_kb_show))
        self.entry_kb_show.bind("<KeyRelease>", lambda e: self.stop_recording(e, self.entry_kb_show))

        # Footer Actions
        footer = tk.Frame(self, bg=COLOR_BG)
        footer.pack(fill="x", side="bottom", pady=10)

        tk.Button(footer, text="✕ Cancel", font=FONT_BODY, fg=COLOR_TEXT_MUTED, bg=COLOR_BG, bd=0,
                  activebackground=COLOR_BG, activeforeground=COLOR_TEXT_MAIN,
                  command=lambda: controller.show_frame("MainMenu")).pack(side="left")
        EssentialButton(footer, text="Apply Changes", command=self.save_current_settings).pack(side="right")

    # --- INTERACTIVE SHORTCUT RECORDER CORE ---
    def start_recording(self, entry_widget):
        entry_widget.delete(0, "end")
        entry_widget.insert(0, "[ Listening... ]")
        entry_widget.config(fg=COLOR_DOT, highlightcolor=COLOR_DOT, highlightbackground=COLOR_DOT)

    def record_key(self, event, entry_widget):
        modifiers = []
        # Bitmask-Checks für Modifikatoren
        if event.state & 4: modifiers.append("Control")
        if event.state & 1: modifiers.append("Shift")
        if event.state & 8: modifiers.append("Alt")

        key = event.keysym

        # Falls die gedrückte Taste selbst nur ein Modifikator ist, fangen wir sie ab
        if key in ("Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R", "Win_L", "Win_R"):
            display_str = "-".join(modifiers) if modifiers else key.split('_')[0]
            entry_widget.delete(0, "end")
            entry_widget.insert(0, f"<{display_str}>")
            return "break"

        # Tkinter bevorzugt Kleinbuchstaben bei standardmäßigen Buchstaben-Binds
        if len(key) == 1 and key.isalpha():
            key = key.lower()

        # Sauberes Zusammenbauen des Tkinter-kompatiblen Bind-Strings
        if modifiers:
            final_str = f"<{'-'.join(modifiers)}-{key}>"
        else:
            final_str = f"<{key}>"

        entry_widget.delete(0, "end")
        entry_widget.insert(0, final_str)
        return "break"  # Verhindert, dass normaler Text parallel reingeschrieben wird

    def stop_recording(self, event, entry_widget):
        current_text = entry_widget.get()

        # Abfangen falls abgebrochen wurde oder unvollständige Modifikatoren herumstehen
        if current_text in ("", "[ Listening... ]") or "_" in current_text:
            s = self.controller.settings
            entry_widget.delete(0, "end")
            if entry_widget == self.entry_kb_new:
                entry_widget.insert(0, s.get("keybind_new_idea", "<Control-n>"))
            else:
                entry_widget.insert(0, s.get("keybind_show_ideas", "<Control-s>"))

        # Design zurücksetzen und Focus abziehen -> Sichert das "Let go"-Event
        entry_widget.config(fg=COLOR_TEXT_MAIN, highlightcolor=COLOR_TEXT_MAIN, highlightbackground="#222222")
        self.focus_set()
        return "break"

    # --- END RECORDER CORE ---

    def load_current_settings_to_ui(self):
        s = self.controller.settings
        self.toggle_autostart.set_state(s.get("autostart_bar", False))
        self.toggle_keybinds.set_state(s.get("keybinds_enabled", False))

        self.entry_kb_new.delete(0, "end")
        self.entry_kb_new.insert(0, s.get("keybind_new_idea", "<Control-n>"))

        self.entry_kb_show.delete(0, "end")
        self.entry_kb_show.insert(0, s.get("keybind_show_ideas", "<Control-s>"))

        self.toggle_keybind_section(s.get("keybinds_enabled", False))

    def toggle_keybind_section(self, is_enabled):
        if is_enabled:
            self.sub_keybind_frame.pack(fill="x", pady=(5, 15),
                                        before=self.sub_keybind_frame.master.winfo_children()[-1])
        else:
            self.sub_keybind_frame.pack_forget()

    def handle_toggle_change(self, state):
        pass

    def close_dock_bar_signal(self):
        messagebox.showinfo("System Core", "Close command sent to overlay bar interface.")

    def save_current_settings(self):
        updated_settings = {
            "autostart_bar": self.toggle_autostart.state,
            "keybinds_enabled": self.toggle_keybinds.state,
            "keybind_new_idea": self.entry_kb_new.get().strip(),
            "keybind_show_ideas": self.entry_kb_show.get().strip()
        }

        if updated_settings["keybind_new_idea"] in ("", "[ Listening... ]") or updated_settings[
            "keybind_show_ideas"] in ("", "[ Listening... ]"):
            messagebox.showwarning("System Configuration", "Keybind fields cannot be left empty.")
            return

        save_settings(updated_settings)
        self.controller.settings = updated_settings
        self.controller.apply_global_keybinds()
        self.controller.show_frame("MainMenu")


# --- RUN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = IdeaPadApp(root)
    root.mainloop()