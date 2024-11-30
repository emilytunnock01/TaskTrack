import tkinter as tk
from tkinter import messagebox
import sqlite3

# Global dictionary to keep track of task buttons in the main menu
task_buttons = {}

# Create SQLite database connection
def initialize_database():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    # Create table for tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT
        )
    ''')
    conn.commit()
    return conn

#FOR EMILYS DEBUGGING - we could keep lowkey
def clear_database():
    if messagebox.askyesno("Confirm Clear", "Are you sure you want to delete all tasks? This action cannot be undone!"):
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM tasks")  # Delete all rows from the tasks table
        db_connection.commit()

        # Remove all task buttons from the GUI
        for task_button in task_buttons.values():
            task_button.destroy()
        task_buttons.clear()  # Clear the dictionary

        messagebox.showinfo("Cleared", "All tasks have been deleted!")


# Save task content to the database
def save_task_to_db(task_title, task_content):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO tasks (title, content) VALUES (?, ?)", (task_title, task_content))
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

# Load all tasks from the database
def load_tasks_from_db():
    cursor = db_connection.cursor()
    cursor.execute("SELECT id, title FROM tasks")
    return cursor.fetchall()

# Open text editor window for a task
def open_text_editor(task_title, task_id=None):
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
            save_task_to_db(task_title, content)
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
            if task_title in task_buttons:  # Check if button exists
                task_buttons[task_title].destroy()  # Destroy the button
                del task_buttons[task_title]  # Remove from the dictionary
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
def create_task_button(task_title, task_id=None):
    task_button = tk.Button(window, text=task_title, width=20,
                            command=lambda: open_text_editor(task_title, task_id))
    task_button.pack(pady=5)
    task_buttons[task_title] = task_button  # Track the button in the global dictionary

# Handle task submission
def submit_task():
    task_title = entry_title.get()
    if not task_title:
        messagebox.showwarning("Error", "Task title is required!")
        return
    save_task_to_db(task_title, "")
    cursor = db_connection.cursor()
    cursor.execute("SELECT id FROM tasks WHERE title = ?", (task_title,))
    new_task_id = cursor.fetchone()
    if new_task_id:
        create_task_button(task_title, new_task_id[0])  # Create the button with the correct task ID
    task_window.destroy()

# Open the task creation window
def open_task_window():
    global task_window, entry_title
    task_window = tk.Toplevel(window)
    task_window.title("Create New Task")
    task_window.geometry("300x150")

    tk.Label(task_window, text="Enter Task Title:").pack(pady=10)
    entry_title = tk.Entry(task_window, width=30)
    entry_title.pack(pady=5)

    tk.Button(task_window, text="Submit", command=submit_task).pack(pady=10)

# Initialize main window
def initialize_main_window():
    global window
    window = tk.Tk()
    window.title("Task Management")
    window.geometry("300x400")

    tk.Button(window, text="Create Task", command=open_task_window).pack(pady=20)
    
    # Load existing tasks from the database and create buttons
    tasks = load_tasks_from_db()
    for task_id, task_title in tasks:
        create_task_button(task_title, task_id)


    #EMILYS DEBUGGING - we can leave
    delete_button = tk.Button(window, text="Clear All Tasks", command=clear_database, bg="red", fg="white").pack(pady=10)



    window.mainloop()

# Initialize database and start program
db_connection = initialize_database()
initialize_main_window()
