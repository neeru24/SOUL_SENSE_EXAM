import sqlite3
import tkinter as tk
from tkinter import messagebox
from journal_feature import JournalFeature
from analytics_dashboard import AnalyticsDashboard

#DATABASE SETUP
conn = sqlite3.connect("soulsense_db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    age INTEGER,
    total_score INTEGER,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# Add age column if it doesn't exist
try:
    cursor.execute("ALTER TABLE scores ADD COLUMN age INTEGER")
except sqlite3.OperationalError:
    pass  # Column already exists

conn.commit()

#QUESTIONS
#QUESTIONS - Keep your original 5 questions, but we'll show them to everyone
questions = [
    {"text": "You can recognize your emotions as they happen.", "age_min": 12, "age_max": 25},
    {"text": "You find it easy to understand why you feel a certain way.", "age_min": 14, "age_max": 30},
    {"text": "You can control your emotions even in stressful situations.", "age_min": 15, "age_max": 35},
    {"text": "You reflect on your emotional reactions to situations.", "age_min": 13, "age_max": 28},
    {"text": "You are aware of how your emotions affect others.", "age_min": 16, "age_max": 40}
]

#USER DETAILS WINDOW
root = tk.Tk()
root.title("SoulSense - User Details")
root.geometry("450x380")
root.resizable(False, False)

username = tk.StringVar()
age = tk.StringVar()

tk.Label(
    root,
    text="SoulSense Assessment",
    font=("Arial", 20, "bold")
).pack(pady=20)

tk.Label(root, text="Enter your name:", font=("Arial", 15)).pack()
tk.Entry(root, textvariable=username, font=("Arial", 15), width=25).pack(pady=8)

tk.Label(root, text="Enter your age:", font=("Arial", 15)).pack()
tk.Entry(root, textvariable=age, font=("Arial", 15), width=25).pack(pady=8)

def submit_details():
    if not username.get():
        messagebox.showerror("Error", "Please enter your name")
        return
    
    if not age.get().isdigit():
        messagebox.showerror("Error", "Please enter a valid age (numbers only)")
        return
    
    user_age = int(age.get())
    if user_age < 12:
        messagebox.showerror("Error", "Age must be at least 12")
        return

    root.destroy()
    start_quiz(username.get(), user_age)

tk.Button(
    root,
    text="Start Assessment",
    command=submit_details,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 14, "bold"),
    width=20
).pack(pady=15)

# Initialize features
journal_feature = JournalFeature(root)

tk.Button(
    root,
    text="📝 Open Journal",
    command=lambda: journal_feature.open_journal_window(username.get() or "Guest"),
    bg="#2196F3",
    fg="white",
    font=("Arial", 12),
    width=20
).pack(pady=5)

tk.Button(
    root,
    text="📊 View Dashboard",
    command=lambda: AnalyticsDashboard(root, username.get() or "Guest").open_dashboard(),
    bg="#FF9800",
    fg="white",
    font=("Arial", 12),
    width=20
).pack(pady=5)

#QUIZ WINDOW
def start_quiz(username, age):
    # Show ALL questions to EVERYONE, regardless of age
    # We ignore the age_min and age_max filters
    filtered_questions = questions  # All 5 questions for everyone
    
    # If you want MORE questions, add them to the questions list above
    # For example, add these additional questions:
    # questions.append({"text": "You can easily put yourself in someone else's shoes.", "age_min": 12, "age_max": 100})
    # questions.append({"text": "You stay calm under pressure.", "age_min": 12, "age_max": 100})
    # etc.

    quiz = tk.Tk()
    quiz.title("SoulSense Assessment")
    quiz.geometry("750x550")

    # Store quiz state in a dictionary to avoid nonlocal issues
    quiz_state = {
        "current_q": 0,
        "score": 0,
        "responses": [],  # Store all responses
        "username": username,
        "age": age
    }

    var = tk.IntVar()

    question_label = tk.Label(
        quiz,
        text="",
        wraplength=700,
        font=("Arial", 16)
    )
    question_label.pack(pady=25)

    options = [
        ("Strongly Disagree", 1),
        ("Disagree", 2),
        ("Neutral", 3),
        ("Agree", 4),
        ("Strongly Agree", 5)
    ]

    for text, val in options:
        tk.Radiobutton(
            quiz,
            text=text,
            variable=var,
            value=val,
            font=("Arial", 14)
        ).pack(anchor="w", padx=60, pady=2)

    # Question counter
    counter_label = tk.Label(
        quiz,
        text=f"Question 1 of {len(filtered_questions)}",
        font=("Arial", 12, "bold"),
        fg="gray"
    )
    counter_label.pack(pady=5)

    def load_question():
        """Load the current question"""
        current_q = quiz_state["current_q"]
        question_label.config(text=filtered_questions[current_q]["text"])
        counter_label.config(text=f"Question {current_q + 1} of {len(filtered_questions)}")
        
        # Set the radio button to previous response if available
        if current_q < len(quiz_state["responses"]):
            var.set(quiz_state["responses"][current_q])
        else:
            var.set(0)

    def update_navigation_buttons():
        """Update button states based on current question"""
        current_q = quiz_state["current_q"]
        if current_q == 0:
            prev_btn.config(state="disabled")
        else:
            prev_btn.config(state="normal")
        
        if current_q == len(filtered_questions) - 1:
            next_btn.config(text="Finish ✓")
        else:
            next_btn.config(text="Next →")

    def save_current_answer():
        """Save the current answer before navigating"""
        current_answer = var.get()
        if current_answer > 0:  # Only save if an answer was selected
            current_q = quiz_state["current_q"]
            if current_q < len(quiz_state["responses"]):
                quiz_state["responses"][current_q] = current_answer
            else:
                quiz_state["responses"].append(current_answer)

    def previous_question():
        """Go to previous question"""
        # Save current answer before moving back
        save_current_answer()
        
        # Move to previous question
        if quiz_state["current_q"] > 0:
            quiz_state["current_q"] -= 1
            load_question()
            update_navigation_buttons()

    def next_question():
        """Go to next question or finish"""
        current_q = quiz_state["current_q"]

        if var.get() == 0:
            messagebox.showwarning("Warning", "Please select an option")
            return

        # Save current answer
        save_current_answer()
        
        # Clear radio button for next question
        var.set(0)
        
        # Move to next question or finish
        if current_q < len(filtered_questions) - 1:
            quiz_state["current_q"] += 1
            load_question()
            update_navigation_buttons()
        else:
            # Calculate final score from all responses
            quiz_state["score"] = sum(quiz_state["responses"])
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO scores (username, age, total_score, timestamp) VALUES (?, ?, ?, ?)",
                (quiz_state["username"], quiz_state["age"], quiz_state["score"], timestamp)
            )
            conn.commit()

            # Show completion message with options
            result = messagebox.askyesno(
                "Completed",
                f"Thank you {quiz_state['username']}!\n"
                f"Your EQ Score: {quiz_state['score']} out of {len(filtered_questions) * 5}\n"
                f"Average: {quiz_state['score']/len(filtered_questions):.1f} per question\n\n"
                f"View your dashboard?"
            )
            
            if result:
                quiz.destroy()
                dashboard = AnalyticsDashboard(None, quiz_state["username"])
                dashboard.open_dashboard()
            else:
                quiz.destroy()
            conn.close()

    # Navigation buttons frame
    nav_frame = tk.Frame(quiz)
    nav_frame.pack(pady=20)

    # Previous button (initially disabled)
    prev_btn = tk.Button(
        nav_frame,
        text="← Previous",
        command=previous_question,
        bg="#70CFFF",
        fg="white",
        font=("Arial", 12),
        width=12,
        state="disabled"  # Disabled on first question
    )
    prev_btn.pack(side="left", padx=10)

    # Next/Finish button
    next_btn = tk.Button(
        nav_frame,
        text="Next →",
        command=next_question,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        width=12
    )
    next_btn.pack(side="left", padx=10)

    # Initialize first question
    load_question()
    update_navigation_buttons()

    quiz.mainloop()

root.mainloop()