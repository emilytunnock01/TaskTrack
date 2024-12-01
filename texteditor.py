import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

# Create SQLite database connection
def initialize_database():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    # Create table for tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            day TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

def ensure_schema():
    cursor = db_connection.cursor()
    try:
        cursor.execute("SELECT day FROM tasks LIMIT 1")  # Check if 'day' column exists
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE tasks ADD COLUMN day TEXT DEFAULT 'Monday'")  # Add column if missing
        db_connection.commit()

db_connection = initialize_database()
ensure_schema()

# Save task content to the database
def save_task_to_db(task_title, task_content, day):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO tasks (title, content, day) VALUES (?, ?, ?)", (task_title, task_content, day))
    db_connection.commit()

# Delete task from the database
def delete_task_from_db(task_title):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE title = ?", (task_title,))
    db_connection.commit()

# Update task content in the database
def update_task_in_db(task_id, task_content):
    cursor = db_connection.cursor()
    cursor.execute("UPDATE tasks SET content = ? WHERE id = ?", (task_content, task_id))
    db_connection.commit()

# Load all tasks for a specific day from the database
def load_tasks_for_day(day):
    cursor = db_connection.cursor()
    cursor.execute("SELECT id, title FROM tasks WHERE day = ?", (day,))
    return cursor.fetchall()

# Open text editor window for a task
def open_text_editor(task_title, task_id=None, day=None):
    editor_window = tk.Toplevel()
    editor_window.title(f"Text Editor - {task_title}")
    editor_window.geometry("400x300")

    frame = tk.Frame(editor_window, relief=tk.RAISED, bd=2, bg="lightgray")
    frame.pack(side="top", fill="x")

    text_edit = tk.Text(editor_window, font="Helvetica 12")
    text_edit.pack(expand=True, fill="both", padx=10, pady=10)

    def save_content():
        nonlocal task_id
        content = text_edit.get("1.0", tk.END).strip()
        if task_id is None:  # If it's a new task
            save_task_to_db(task_title, content, day)
            # Retrieve the task ID from the database
            cursor = db_connection.cursor()
            cursor.execute("SELECT id FROM tasks WHERE title = ?", (task_title,))
            new_task_id = cursor.fetchone()
            if new_task_id:
                task_id = new_task_id[0]
        else:  # If it's an existing task
            update_task_in_db(task_id, content)

        messagebox.showinfo("Saved", f"Task '{task_title}' saved!")
        editor_window.destroy()

    def delete_content():
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the task '{task_title}'?"):
            delete_task_from_db(task_title)
            if task_title in task_buttons[day]:  # Check if button exists
                task_buttons[day][task_title].destroy()  # Destroy the button
                del task_buttons[day][task_title]  # Remove from the dictionary
            messagebox.showinfo("Deleted", f"Task '{task_title}' deleted!")
            editor_window.destroy()

    button_save = tk.Button(frame, text="Save", command=save_content)
    button_save.pack(side="left", padx=5, pady=5)

    button_delete = tk.Button(frame, text="Delete", command=delete_content)
    button_delete.pack(side="left", padx=5, pady=5)

    # Pre-fill with existing content if editing
    if task_id is not None:
        cursor = db_connection.cursor()
        cursor.execute("SELECT content FROM tasks WHERE id = ?", (task_id,))
        content = cursor.fetchone()
        if content and content[0]:
            text_edit.insert("1.0", content[0])

# Create a task button
def create_task_button(task_title, task_id=None, day=None):
    task_button = tk.Button(day_frames[day], text=task_title, width=20,
                            command=lambda: open_text_editor(task_title, task_id, day))
    task_button.pack(pady=5)
    task_buttons[day][task_title] = task_button  # Track the button in the global dictionary

# Handle task submission
def add_task(day):
    task_title = simpledialog.askstring("Create Task", f"Enter task title for {day}:")
    if not task_title:
        return
    save_task_to_db(task_title, "", day)
    cursor = db_connection.cursor()
    cursor.execute("SELECT id FROM tasks WHERE title = ?", (task_title,))
    new_task_id = cursor.fetchone()
    if new_task_id:
        create_task_button(task_title, new_task_id[0], day)  # Create the button within the appropriate frame

# Initialize the main weekly view
def initialize_weekly_view():
    global window, day_frames, task_buttons
    window = tk.Tk()
    window.title("Weekly Task Manager")
    window.geometry("900x600")

    # Frames for each day of the week
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_frames = {}
    task_buttons = {day: {} for day in days_of_week}

    for day in days_of_week:
        frame = tk.Frame(window, borderwidth=2, relief="groove", padx=10, pady=10)
        frame.pack(side="left", expand=True, fill="both")
        day_frames[day] = frame

        # Label for the day
        tk.Label(frame, text=day, font=("Helvetica", 14, "bold")).pack()

        # Button to add tasks
        tk.Button(frame, text="Add Task", command=lambda d=day: add_task(d)).pack(pady=5)

        # Load existing tasks for the day
        tasks = load_tasks_for_day(day)
        for task_id, task_title in tasks:
            create_task_button(task_title, task_id, day)

    window.mainloop()

# Initialize database and start program
db_connection = initialize_database()
initialize_weekly_view()
