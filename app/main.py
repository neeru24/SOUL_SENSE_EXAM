# import tkinter as tk
# from tkinter import messagebox
# from datetime import datetime
# import logging

# from app.db import get_connection
# from app.questions import load_questions
# from app.utils import compute_age_group
# from app.models import (
#     ensure_scores_schema,
#     ensure_responses_schema,
#     ensure_question_bank_schema
# )

# # --------------------------------------------------
# # Logging
# # --------------------------------------------------
# logging.basicConfig(
#     filename="logs/soulsense.log",
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(message)s"
# )

# # --------------------------------------------------
# # DB setup (run once on startup)
# # --------------------------------------------------
# def initialize_db():
#     conn = get_connection()
#     cursor = conn.cursor()

#     ensure_question_bank_schema(cursor)
#     ensure_scores_schema(cursor)
#     ensure_responses_schema(cursor)

#     conn.commit()
#     conn.close()


# # --------------------------------------------------
# # Tkinter App
# # --------------------------------------------------
# class SoulSenseApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Soul Sense Exam")
#         self.root.geometry("600x400")

#         self.username = ""
#         self.age = None
#         self.age_group = "unknown"

#         self.questions = load_questions()  # [(id, text), ...]
#         self.current_index = 0
#         self.responses = []

#         self.build_user_info_screen()

#     # -------------------------
#     # Screen 1: User Info
#     # -------------------------
#     def build_user_info_screen(self):
#         self.clear_screen()

#         tk.Label(self.root, text="Soul Sense Exam", font=("Arial", 18)).pack(pady=20)

#         tk.Label(self.root, text="Username").pack()
#         self.username_entry = tk.Entry(self.root)
#         self.username_entry.pack()

#         tk.Label(self.root, text="Age").pack()
#         self.age_entry = tk.Entry(self.root)
#         self.age_entry.pack()

#         tk.Button(self.root, text="Start Exam", command=self.start_exam).pack(pady=20)

#     def start_exam(self):
#         self.username = self.username_entry.get().strip()
#         age_raw = self.age_entry.get().strip()

#         if not self.username:
#             messagebox.showerror("Error", "Username required")
#             return

#         try:
#             self.age = int(age_raw)
#         except Exception:
#             self.age = None

#         self.age_group = compute_age_group(self.age)
#         logging.info(f"User started exam: {self.username}, age_group={self.age_group}")

#         self.build_question_screen()

#     # -------------------------
#     # Screen 2: Questions
#     # -------------------------
#     def build_question_screen(self):
#         self.clear_screen()

#         q_id, q_text = self.questions[self.current_index]

#         tk.Label(
#             self.root,
#             text=f"Question {self.current_index + 1} of {len(self.questions)}",
#             font=("Arial", 12)
#         ).pack(pady=10)

#         tk.Label(
#             self.root,
#             text=q_text,
#             wraplength=500,
#             font=("Arial", 14)
#         ).pack(pady=20)

#         self.answer_var = tk.IntVar(value=0)

#         for i in range(1, 6):
#             tk.Radiobutton(
#                 self.root,
#                 text=str(i),
#                 variable=self.answer_var,
#                 value=i
#             ).pack(anchor="w", padx=200)

#         tk.Button(self.root, text="Next", command=self.save_and_next).pack(pady=20)

#     def save_and_next(self):
#         value = self.answer_var.get()

#         if value == 0:
#             messagebox.showerror("Error", "Please select an answer")
#             return

#         q_id, _ = self.questions[self.current_index]

#         self.responses.append({
#             "question_id": q_id,
#             "value": value
#         })

#         self.current_index += 1

#         if self.current_index >= len(self.questions):
#             self.finish_exam()
#         else:
#             self.build_question_screen()

#     # -------------------------
#     # Finish + Save to DB
#     # -------------------------
#     def finish_exam(self):
#         conn = get_connection()
#         cursor = conn.cursor()

#         timestamp = datetime.utcnow().isoformat()

#         for r in self.responses:
#             cursor.execute(
#                 """
#                 INSERT INTO responses
#                 (username, question_id, response_value, age_group, timestamp)
#                 VALUES (?, ?, ?, ?, ?)
#                 """,
#                 (
#                     self.username,
#                     r["question_id"],
#                     r["value"],
#                     self.age_group,
#                     timestamp
#                 )
#             )

#         conn.commit()
#         conn.close()

#         logging.info(f"Exam completed for {self.username}")

#         self.clear_screen()
#         tk.Label(
#             self.root,
#             text="Thank you for completing the exam!",
#             font=("Arial", 16)
#         ).pack(pady=50)

#         tk.Button(self.root, text="Exit", command=self.root.quit).pack()

#     # -------------------------
#     # Utility
#     # -------------------------
#     def clear_screen(self):
#         for widget in self.root.winfo_children():
#             widget.destroy()


# # --------------------------------------------------
# # Entry point
# # --------------------------------------------------
# if __name__ == "__main__":
#     initialize_db()

#     root = tk.Tk()
#     app = SoulSenseApp(root)
#     root.mainloop()





import tkinter as tk
from tkinter import messagebox
import logging
import sys
from datetime import datetime
import json
import os

from app.db import get_connection
from app.models import (
    ensure_scores_schema,
    ensure_responses_schema,
    ensure_question_bank_schema
)
from app.questions import load_questions
from app.utils import compute_age_group

# ---------------- SETTINGS ----------------
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "question_count": 10,
    "theme": "light",
    "sound_effects": True
}

def load_settings():
    """Load user settings from file or use defaults"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Ensure all default keys exist
                for key in DEFAULT_SETTINGS:
                    if key not in settings:
                        settings[key] = DEFAULT_SETTINGS[key]
                return settings
        except Exception:
            logging.error("Failed to load settings", exc_info=True)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save user settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception:
        logging.error("Failed to save settings", exc_info=True)
        return False

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="logs/soulsense.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

# ---------------- DB INIT ----------------
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    total_score INTEGER,
    age INTEGER
)
""")

ensure_scores_schema(cursor)
ensure_responses_schema(cursor)
ensure_question_bank_schema(cursor)

conn.commit()

# ---------------- LOAD QUESTIONS FROM DB ----------------
try:
    rows = load_questions()  # [(id, text)]
    all_questions = [q[1] for q in rows]   # preserve text only
    
    if not all_questions:
        raise RuntimeError("Question bank empty")

    logging.info("Loaded %s total questions from DB", len(all_questions))

except Exception:
    logging.critical("Failed to load questions from DB", exc_info=True)
    messagebox.showerror("Fatal Error", "Question bank could not be loaded.")
    sys.exit(1)

# ---------------- GUI ----------------
class SoulSenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Soul Sense EQ Test")
        self.root.geometry("500x400")
        
        # Load settings
        self.settings = load_settings()
        
        # Define color schemes
        self.color_schemes = {
            "light": {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "button_bg": "#e0e0e0",
                "button_fg": "#000000",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "radiobutton_bg": "#f0f0f0",
                "radiobutton_fg": "#000000",
                "label_bg": "#f0f0f0",
                "label_fg": "#000000"
            },
            "dark": {
                "bg": "#2e2e2e",
                "fg": "#ffffff",
                "button_bg": "#4a4a4a",
                "button_fg": "#ffffff",
                "entry_bg": "#3a3a3a",
                "entry_fg": "#ffffff",
                "radiobutton_bg": "#2e2e2e",
                "radiobutton_fg": "#ffffff",
                "label_bg": "#2e2e2e",
                "label_fg": "#ffffff"
            }
        }
        
        # Apply theme
        self.apply_theme(self.settings.get("theme", "light"))
        
        # Test variables
        self.username = ""
        self.age = None
        self.age_group = None
        self.current_question = 0
        self.responses = []
        
        # Load questions based on settings
        question_count = self.settings.get("question_count", 10)
        self.questions = all_questions[:min(question_count, len(all_questions))]
        logging.info("Using %s questions based on settings", len(self.questions))
        
        self.create_welcome_screen()

    def apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        self.current_theme = theme_name
        self.colors = self.color_schemes.get(theme_name, self.color_schemes["light"])
        
        # Configure root window
        self.root.configure(bg=self.colors["bg"])
        
        # Configure default widget styles
        self.root.option_add("*Background", self.colors["bg"])
        self.root.option_add("*Foreground", self.colors["fg"])
        self.root.option_add("*Button.Background", self.colors["button_bg"])
        self.root.option_add("*Button.Foreground", self.colors["button_fg"])
        self.root.option_add("*Entry.Background", self.colors["entry_bg"])
        self.root.option_add("*Entry.Foreground", self.colors["entry_fg"])
        self.root.option_add("*Label.Background", self.colors["label_bg"])
        self.root.option_add("*Label.Foreground", self.colors["label_fg"])
        self.root.option_add("*Radiobutton.Background", self.colors["radiobutton_bg"])
        self.root.option_add("*Radiobutton.Foreground", self.colors["radiobutton_fg"])
        self.root.option_add("*Radiobutton.selectColor", self.colors["bg"])

    def create_widget(self, widget_type, *args, **kwargs):
        """Create a widget with current theme colors"""
        # Override colors if not specified
        if widget_type == tk.Label:
            kwargs.setdefault("bg", self.colors["label_bg"])
            kwargs.setdefault("fg", self.colors["label_fg"])
        elif widget_type == tk.Button:
            kwargs.setdefault("bg", self.colors["button_bg"])
            kwargs.setdefault("fg", self.colors["button_fg"])
            kwargs.setdefault("activebackground", self.darken_color(self.colors["button_bg"]))
            kwargs.setdefault("activeforeground", self.colors["button_fg"])
        elif widget_type == tk.Entry:
            kwargs.setdefault("bg", self.colors["entry_bg"])
            kwargs.setdefault("fg", self.colors["entry_fg"])
            kwargs.setdefault("insertbackground", self.colors["fg"])
        elif widget_type == tk.Radiobutton:
            kwargs.setdefault("bg", self.colors["radiobutton_bg"])
            kwargs.setdefault("fg", self.colors["radiobutton_fg"])
            kwargs.setdefault("selectcolor", self.colors["bg"])
        
        return widget_type(*args, **kwargs)

    def darken_color(self, color):
        """Darken a color for active button state"""
        if color.startswith("#"):
            # Convert hex to rgb, darken, then back to hex
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color

    def create_welcome_screen(self):
        """Create initial welcome screen with settings option"""
        self.clear_screen()
        
        # Title
        title = self.create_widget(
            tk.Label,
            self.root,
            text="Welcome to Soul Sense EQ Test",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=20)
        
        # Description
        desc = self.create_widget(
            tk.Label,
            self.root,
            text="Assess your Emotional Intelligence\nwith our comprehensive questionnaire",
            font=("Arial", 11)
        )
        desc.pack(pady=10)
        
        # Current settings display
        settings_frame = self.create_widget(tk.Frame, self.root)
        settings_frame.pack(pady=20)
        
        settings_label = self.create_widget(
            tk.Label,
            settings_frame,
            text="Current Settings:",
            font=("Arial", 11, "bold")
        )
        settings_label.pack()
        
        settings_text = self.create_widget(
            tk.Label,
            settings_frame,
            text=f"• Questions: {len(self.questions)}\n" +
                 f"• Theme: {self.settings.get('theme', 'light').title()}\n" +
                 f"• Sound: {'On' if self.settings.get('sound_effects', True) else 'Off'}",
            font=("Arial", 10),
            justify="left"
        )
        settings_text.pack(pady=5)
        
        # Buttons
        button_frame = self.create_widget(tk.Frame, self.root)
        button_frame.pack(pady=20)
        
        start_btn = self.create_widget(
            tk.Button,
            button_frame,
            text="Start Test",
            command=self.create_username_screen,
            font=("Arial", 12),
            width=15
        )
        start_btn.pack(pady=5)
        
        settings_btn = self.create_widget(
            tk.Button,
            button_frame,
            text="Settings",
            command=self.show_settings,
            font=("Arial", 12),
            width=15
        )
        settings_btn.pack(pady=5)
        
        exit_btn = self.create_widget(
            tk.Button,
            button_frame,
            text="Exit",
            command=self.force_exit,
            font=("Arial", 12),
            width=15
        )
        exit_btn.pack(pady=5)

    def show_settings(self):
        """Show settings configuration window"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x400")
        
        # Apply theme to settings window
        settings_win.configure(bg=self.colors["bg"])
        
        # Center window
        settings_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - settings_win.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - settings_win.winfo_height()) // 2
        settings_win.geometry(f"+{x}+{y}")
        
        # Title
        title = tk.Label(
            settings_win,
            text="Configure Test Settings",
            font=("Arial", 16, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title.pack(pady=15)
        
        # Question Count
        qcount_frame = tk.Frame(settings_win, bg=self.colors["bg"])
        qcount_frame.pack(pady=10, fill="x", padx=20)
        
        qcount_label = tk.Label(
            qcount_frame,
            text="Number of Questions:",
            font=("Arial", 11),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        qcount_label.pack(anchor="w")
        
        self.qcount_var = tk.IntVar(value=self.settings.get("question_count", 10))
        qcount_spin = tk.Spinbox(
            qcount_frame,
            from_=5,
            to=min(50, len(all_questions)),
            textvariable=self.qcount_var,
            font=("Arial", 11),
            width=10,
            bg=self.colors["entry_bg"],
            fg=self.colors["entry_fg"],
            buttonbackground=self.colors["button_bg"]
        )
        qcount_spin.pack(anchor="w", pady=5)
        
        # Theme Selection
        theme_frame = tk.Frame(settings_win, bg=self.colors["bg"])
        theme_frame.pack(pady=10, fill="x", padx=20)
        
        theme_label = tk.Label(
            theme_frame,
            text="Theme:",
            font=("Arial", 11),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        theme_label.pack(anchor="w")
        
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "light"))
        
        theme_light = tk.Radiobutton(
            theme_frame,
            text="Light Theme",
            variable=self.theme_var,
            value="light",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            activeforeground=self.colors["fg"]
        )
        theme_light.pack(anchor="w", pady=2)
        
        theme_dark = tk.Radiobutton(
            theme_frame,
            text="Dark Theme",
            variable=self.theme_var,
            value="dark",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            activeforeground=self.colors["fg"]
        )
        theme_dark.pack(anchor="w", pady=2)
        
        # Sound Effects
        sound_frame = tk.Frame(settings_win, bg=self.colors["bg"])
        sound_frame.pack(pady=10, fill="x", padx=20)
        
        self.sound_var = tk.BooleanVar(value=self.settings.get("sound_effects", True))
        sound_cb = tk.Checkbutton(
            sound_frame,
            text="Enable Sound Effects",
            variable=self.sound_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            activeforeground=self.colors["fg"]
        )
        sound_cb.pack(anchor="w")
        
        # Buttons
        btn_frame = tk.Frame(settings_win, bg=self.colors["bg"])
        btn_frame.pack(pady=20)
        
        def apply_settings():
            """Apply and save settings"""
            new_settings = {
                "question_count": self.qcount_var.get(),
                "theme": self.theme_var.get(),
                "sound_effects": self.sound_var.get()
            }
            
            # Update questions based on new count
            question_count = new_settings["question_count"]
            self.questions = all_questions[:min(question_count, len(all_questions))]
            
            # Save settings
            self.settings.update(new_settings)
            if save_settings(self.settings):
                # Apply theme immediately
                self.apply_theme(new_settings["theme"])
                messagebox.showinfo("Success", "Settings saved successfully!")
                settings_win.destroy()
                # Recreate welcome screen with updated settings
                self.create_welcome_screen()
        
        apply_btn = tk.Button(
            btn_frame,
            text="Apply",
            command=apply_settings,
            font=("Arial", 11),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            width=10,
            activebackground=self.darken_color(self.colors["button_bg"])
        )
        apply_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=settings_win.destroy,
            font=("Arial", 11),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            width=10,
            activebackground=self.darken_color(self.colors["button_bg"])
        )
        cancel_btn.pack(side="left", padx=5)
        
        def reset_defaults():
            """Reset to default settings"""
            self.qcount_var.set(DEFAULT_SETTINGS["question_count"])
            self.theme_var.set(DEFAULT_SETTINGS["theme"])
            self.sound_var.set(DEFAULT_SETTINGS["sound_effects"])
        
        reset_btn = tk.Button(
            settings_win,
            text="Reset to Defaults",
            command=reset_defaults,
            font=("Arial", 10),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            activebackground=self.darken_color(self.colors["button_bg"])
        )
        reset_btn.pack(pady=10)

    # ---------- ORIGINAL SCREENS (Modified) ----------
    def create_username_screen(self):
        self.clear_screen()
        
        self.create_widget(
            tk.Label,
            self.root,
            text="Enter Your Name:",
            font=("Arial", 14)
        ).pack(pady=10)
        
        self.name_entry = self.create_widget(
            tk.Entry,
            self.root,
            font=("Arial", 14)
        )
        self.name_entry.pack(pady=5)

        self.create_widget(
            tk.Label,
            self.root,
            text="Enter Your Age (optional):",
            font=("Arial", 14)
        ).pack(pady=5)
        
        self.age_entry = self.create_widget(
            tk.Entry,
            self.root,
            font=("Arial", 14)
        )
        self.age_entry.pack(pady=5)

        self.create_widget(
            tk.Button,
            self.root,
            text="Start Test",
            command=self.start_test
        ).pack(pady=15)
        
        # Back button
        self.create_widget(
            tk.Button,
            self.root,
            text="Back to Main",
            command=self.create_welcome_screen
        ).pack(pady=5)

    def validate_name_input(self, name):
        if not name:
            return False, "Please enter your name."
        if not all(c.isalpha() or c.isspace() for c in name):
            return False, "Name must contain only letters and spaces."
        return True, None

    def validate_age_input(self, age_str):
        if age_str == "":
            return True, None, None
        try:
            age = int(age_str)
            if not (1 <= age <= 120):
                return False, None, "Age must be between 1 and 120."
            return True, age, None
        except ValueError:
            return False, None, "Age must be numeric."

    def start_test(self):
        self.username = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()

        ok, err = self.validate_name_input(self.username)
        if not ok:
            messagebox.showwarning("Input Error", err)
            return

        ok, age, err = self.validate_age_input(age_str)
        if not ok:
            messagebox.showwarning("Input Error", err)
            return

        self.age = age
        self.age_group = compute_age_group(age)

        logging.info(
            "Session started | user=%s | age=%s | age_group=%s | questions=%s",
            self.username, self.age, self.age_group, len(self.questions)
        )

        self.show_question()

    def show_question(self):
        self.clear_screen()

        if self.current_question >= len(self.questions):
            self.finish_test()
            return

        q = self.questions[self.current_question]
        
        # Question counter
        self.create_widget(
            tk.Label,
            self.root,
            text=f"Question {self.current_question + 1} of {len(self.questions)}",
            font=("Arial", 10)
        ).pack(pady=5)
        
        self.create_widget(
            tk.Label,
            self.root,
            text=f"Q{self.current_question + 1}: {q}",
            wraplength=400,
            font=("Arial", 11)
        ).pack(pady=20)

        self.answer_var = tk.IntVar()

        for val, txt in enumerate(["Never", "Sometimes", "Often", "Always"], 1):
            self.create_widget(
                tk.Radiobutton,
                self.root,
                text=f"{txt} ({val})",
                variable=self.answer_var,
                value=val
            ).pack(anchor="w", padx=50)

        # Navigation buttons
        button_frame = self.create_widget(tk.Frame, self.root)
        button_frame.pack(pady=15)
        
        if self.current_question > 0:
            self.create_widget(
                tk.Button,
                button_frame,
                text="Previous",
                command=self.previous_question
            ).pack(side="left", padx=5)

        self.create_widget(
            tk.Button,
            button_frame,
            text="Next",
            command=self.save_answer
        ).pack(side="left", padx=5)

    def previous_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            if self.responses:
                self.responses.pop()
            self.show_question()

    def save_answer(self):
        ans = self.answer_var.get()
        if ans == 0:
            messagebox.showwarning("Input Error", "Please select an answer.")
            return

        self.responses.append(ans)

        qid = self.current_question + 1
        ts = datetime.utcnow().isoformat()

        try:
            cursor.execute(
                """
                INSERT INTO responses
                (username, question_id, response_value, age_group, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.username, qid, ans, self.age_group, ts)
            )
            conn.commit()
        except Exception:
            logging.error("Failed to store response", exc_info=True)

        self.current_question += 1
        self.show_question()

    def finish_test(self):
        total_score = sum(self.responses)
        max_score = len(self.responses) * 4

        try:
            cursor.execute(
                "INSERT INTO scores (username, age, total_score) VALUES (?, ?, ?)",
                (self.username, self.age, total_score)
            )
            conn.commit()
        except Exception:
            logging.error("Failed to store final score", exc_info=True)

        interpretation = (
            "Excellent Emotional Intelligence!" if total_score >= 65 else
            "Good Emotional Intelligence." if total_score >= 50 else
            "Average Emotional Intelligence." if total_score >= 35 else
            "You may want to work on your Emotional Intelligence."
        )

        self.clear_screen()
        
        self.create_widget(
            tk.Label,
            self.root,
            text=f"Thank you, {self.username}!",
            font=("Arial", 16)
        ).pack(pady=10)
        
        self.create_widget(
            tk.Label,
            self.root,
            text=f"Your total EQ score is: {total_score} / {max_score}",
            font=("Arial", 14)
        ).pack(pady=10)
        
        # Interpretation with blue color (works in both themes)
        interpretation_label = self.create_widget(
            tk.Label,
            self.root,
            text=interpretation,
            font=("Arial", 14)
        )
        interpretation_label.pack(pady=10)
        interpretation_label.config(fg="blue")  # Keep blue for emphasis

        # Test summary
        self.create_widget(
            tk.Label,
            self.root,
            text=f"Test completed with {len(self.questions)} questions",
            font=("Arial", 10)
        ).pack(pady=5)

        button_frame = self.create_widget(tk.Frame, self.root)
        button_frame.pack(pady=20)
        
        self.create_widget(
            tk.Button,
            button_frame,
            text="Take Another Test",
            command=self.reset_test,
            font=("Arial", 12)
        ).pack(side="left", padx=10)
        
        self.create_widget(
            tk.Button,
            button_frame,
            text="Main Menu",
            command=self.create_welcome_screen,
            font=("Arial", 12)
        ).pack(side="left", padx=10)

    def reset_test(self):
        """Reset test variables and start over"""
        self.username = ""
        self.age = None
        self.age_group = None
        self.current_question = 0
        self.responses = []
        self.create_username_screen()

    def force_exit(self):
        try:
            conn.close()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

# ---------------- MAIN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SoulSenseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.force_exit)
    root.mainloop()
