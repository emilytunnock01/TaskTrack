import sqlite3
from tkinter import messagebox

global window, day_frames, task_buttons

################################################## DATABASE FUNCTIONS ##################################################
# Establishes a connection to the SQLite database
def initialize_database():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    # Creates the table for tasks if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            day TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

# Ensures that all required columns are present in the tasks table
def ensure_schema(): 
    cursor = db_connection.cursor()
    try:
        # Checks if the 'day' column exists
        cursor.execute("SELECT day FROM tasks LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE tasks ADD COLUMN day TEXT DEFAULT 'Monday'")
        db_connection.commit()

    try:
        # Checks if the 'status' column exists
        cursor.execute("SELECT status FROM tasks LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'not-completed'")
        db_connection.commit()

db_connection = initialize_database()
ensure_schema()

# Clears all tasks from the database (for debugging purposes)
def clear_database():
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM tasks")  # Deletes all rows from the 'tasks' table
    db_connection.commit()
    messagebox.showinfo("Database Cleared", "All tasks have been removed!")

# Saves the task content to the database (initial creation of a task)
def save_task_to_db(task_title, task_content, day):
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO tasks (title, content, day) VALUES (?, ?, ?)", (task_title, task_content, day))
    db_connection.commit()

# Deletes a task from the database
def delete_task_from_db(task_title):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE title = ?", (task_title,))
    db_connection.commit()

# Updates the task content in the database (save function)
def update_task_in_db(task_id, task_content):
    cursor = db_connection.cursor()
    cursor.execute("UPDATE tasks SET content = ? WHERE id = ?", (task_content, task_id))
    db_connection.commit()

# Moves a task to a different day
def change_task_day(task_id, new_day):
    cursor = db_connection.cursor()
    cursor.execute("UPDATE tasks SET day = ? WHERE id = ?", (new_day, task_id))
    db_connection.commit()
    messagebox.showinfo("Task Updated", f"Task has been moved to {new_day}.")

# Marks a task as completed and removes the corresponding button
def completed_task(task_id, task_title, task_day):
    # Marks the task as completed in the database
    cursor = db_connection.cursor()
    cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
    db_connection.commit()

    # Removes the task button from the weekly view
    if task_title in task_buttons[task_day]:
        task_buttons[task_day][task_title].destroy()  # Destroys the button
        del task_buttons[task_day][task_title]  # Removes from the dictionary

    messagebox.showinfo("Task Marked as Completed", f"Task '{task_title}' has been marked as completed!")

# Loads all non-completed tasks for a specific day from the database
def load_tasks_for_day(day):
    cursor = db_connection.cursor()
    # Queries and retrieves all non-completed tasks for the specified day
    cursor.execute("SELECT id, title FROM tasks WHERE day = ? AND status != 'completed'", (day,))
    return cursor.fetchall()

# Fetches all completed tasks from the database
def load_completed_tasks():
    cursor = db_connection.cursor()
    cursor.execute("SELECT id, title, content, day FROM tasks WHERE status = 'completed'")
    return cursor.fetchall()