import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3

##########################  UI  ###################################################################################
def center_window(window, width, height):
    # Get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate the position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set the geometry of the window
    window.geometry(f"{width}x{height}+{x}+{y}")

################################## DATABASE FUNCTIONS ###########################################################
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
            day TEXT NOT NULL,
            status TEXT NOT NULL
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

#CLEARING
def clear_database():
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM tasks")  # Deletes all rows from the 'tasks' table
    db_connection.commit()
    messagebox.showinfo("Database Cleared", "All tasks have been removed!")


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

#move task to a different day
def change_task_day(task_id, new_day):
    cursor = db_connection.cursor()
    cursor.execute("UPDATE tasks SET day = ? WHERE id = ?", (new_day, task_id))
    db_connection.commit()
    messagebox.showinfo("Task Updated", f"Task has been moved to {new_day}.")

#move task to completed
def completed_task(task_id, task_title, task_day):
    # Mark the task as completed in the database
    cursor = db_connection.cursor()
    cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
    db_connection.commit()

    # Remove the task button from the weekly view
    if task_title in task_buttons[task_day]:
        task_buttons[task_day][task_title].destroy()  # Destroy the button
        del task_buttons[task_day][task_title]  # Remove from the dictionary

    messagebox.showinfo("Task Marked as Completed", f"Task '{task_title}' has been marked as completed!")

# Load all tasks for a specific day from the database
def load_tasks_for_day(day):
    cursor = db_connection.cursor()
    cursor.execute("SELECT id, title FROM tasks WHERE day = ? AND status != 'completed'", (day,))
    return cursor.fetchall()

#fetch all completed task
def load_completed_tasks():
    cursor = db_connection.cursor()
    cursor.execute("SELECT id, title, content, day FROM tasks WHERE status = 'completed'")
    return cursor.fetchall()


def refresh_weekly_view():
    # Clear the task buttons for each day
    for day in day_frames:
        for task_button in task_buttons[day].values():
            task_button.destroy()
        task_buttons[day].clear()

    # Load tasks again for each day
    for day in day_frames:
        tasks = load_tasks_for_day(day)
        for task_id, task_title in tasks:
            create_task_button(task_title, task_id, day)



####################### TEXT EDITOR WINDOW #######################################################################
# Open text editor window for a task
def open_text_editor(task_title, task_id=None, day=None, status="not-complete"):
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

    def edit_content(task_id, task_title, current_day, status):
        # Create a new popup window
        edit_window = tk.Toplevel()
        edit_window.title(f"Edit Task - {task_title}")
        edit_window.geometry("300x200")

        # Dropdown for selecting the new day
        tk.Label(edit_window, text="Select new day:", font=("Helvetica", 12)).pack(pady=5)
        days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        day_var = tk.StringVar(value=current_day)
        day_selector = ttk.Combobox(edit_window, textvariable=day_var, values=days_of_week, state="readonly")
        day_selector.pack(pady=5)

        # Checkbox for marking as completed
        completed_var = tk.BooleanVar(value=(status == "completed"))
        tk.Checkbutton(edit_window, text="Mark as Completed", variable=completed_var).pack(pady=5)

        # Function to save edits
        def save_edits():
            new_day = day_var.get()
            completed = "completed" if completed_var.get() else "not-complete"

            # Check if the new day is different from the current day
            if new_day != current_day:
                # Update the task's day in the database if the day has changed
                change_task_day(task_id, new_day)
                
                # Update UI for the new day (remove from old day and add to new day)
                if task_title in task_buttons[current_day]:
                    task_buttons[current_day][task_title].destroy()
                    del task_buttons[current_day][task_title]
                
                create_task_button(task_title, task_id, new_day)



            # Update the status (whether completed or not)
            cursor = db_connection.cursor()
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (completed, task_id))
            db_connection.commit()

            messagebox.showinfo("Task Updated", f"Task '{task_title}' updated!")
            edit_window.destroy()

        tk.Button(edit_window, text="Save Changes", command=save_edits).pack(pady=10)



            
            
        
            



    button_save = tk.Button(frame, text="Save", command=save_content)
    button_save.pack(side="left", padx=5, pady=5)

    button_delete = tk.Button(frame, text="Delete", command=delete_content)
    button_delete.pack(side="left", padx=5, pady=5)

    button_edit = tk.Button(frame, text="Edit", 
                             command=lambda: edit_content(task_id, task_title, day, status))
    button_edit.pack(side="left", padx=5, pady=5)



    # Pre-fill with existing content if editing
    if task_id is not None:
        cursor = db_connection.cursor()
        cursor.execute("SELECT content FROM tasks WHERE id = ?", (task_id,))
        content = cursor.fetchone()
        if content and content[0]:
            text_edit.insert("1.0", content[0])

############################### TASK CREATION ###################################################################
# Create a task button
def create_task_button(task_title, task_id=None, day=None, status="not-completed"):
    task_button = tk.Button(day_frames[day], text=task_title, width=20,
                            command=lambda: open_text_editor(task_title, task_id, day, status))
    task_button.pack(pady=5)
    task_buttons[day][task_title] = task_button  # Track the button in the global dictionary

#form for creating task
def add_task():
    # Create a pop-up window
    task_window = tk.Toplevel(window)
    task_window.title("Create Task")
    task_window.geometry("300x200")
    
    # Task Title Label and Entry
    tk.Label(task_window, text="Task Title:").pack(pady=5)
    task_title_entry = tk.Entry(task_window, width=25)
    task_title_entry.pack(pady=5)
    
    # Day Selection Label and Combobox
    tk.Label(task_window, text="Select Day:").pack(pady=5)
    day_selector = ttk.Combobox(task_window, values=list(day_frames.keys()), state="readonly")
    day_selector.pack(pady=5)
    
    # Function to handle task creation
    def submit_task():
        task_title = task_title_entry.get().strip()
        day = day_selector.get().strip()
        
        if not task_title:
            messagebox.showwarning("Missing Title", "Please enter a task title.")
            return
        
        if not day:
            messagebox.showwarning("Missing Day", "Please select a day.")
            return
        
        # Save the task to the database
        save_task_to_db(task_title, "", day,)
        
        # Retrieve the task ID from the database
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM tasks WHERE title = ? AND day = ?", (task_title, day))
        new_task_id = cursor.fetchone()
        
        if new_task_id:
            create_task_button(task_title, new_task_id[0], day)  # Create a task button in the selected day's frame
            
        messagebox.showinfo("Task Created", f"Task '{task_title}' added to {day}!")
        task_window.destroy()  # Close the pop-up form

    # Submit Button
    tk.Button(task_window, text="Create Task", command=submit_task).pack(pady=15)

def completed_task_menu():
    completed_tasks = load_completed_tasks()

    # Create a new popup window to display completed tasks
    completed_window = tk.Toplevel()
    completed_window.title("Completed Tasks")
    completed_window.geometry("400x300")

    # Create a scrollbar and a frame to hold the tasks
    scroll_frame = tk.Frame(completed_window)
    scroll_frame.pack(expand=True, fill="both")

    canvas = tk.Canvas(scroll_frame)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    task_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=task_frame, anchor="nw")

    # Add each completed task as a button
    for task in completed_tasks:
        task_id, task_title, task_content, task_day = task

        # Create a button for each completed task
        task_button = tk.Button(task_frame, text=f"{task_title} - {task_day}",
                                command=lambda task_id=task_id, task_title=task_title, task_day=task_day: open_text_editor(task_title, task_id, task_day, "completed"))
        task_button.pack(fill="x", padx=10, pady=5)

    # Update scrollable region
    task_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))



################################# MAIN MENU ##################################################################################
def initialize_weekly_view():
    global window, day_frames, task_buttons
    window = tk.Tk()
    window.title("TaskTrack")
    center_window(window, 1000, 900)  # Center the main window

    # Header frame for the title and subtitle
    header_frame = tk.Frame(window, bg="#4C9EEB", pady=10)  # Add padding for better spacing
    header_frame.grid(row=0, column=0, columnspan=7, sticky="nsew")  # Span all columns

    # Title label
    title_label = tk.Label(
        header_frame,
        text="Welcome to TaskTrack!",
        font=("League Spartan", 25, "bold"),
        bg="#4C9EEB",
        fg="white"
    )
    title_label.pack()

    # Subtitle label
    subtitle_label = tk.Label(
        header_frame,
        text="FastTrack with TaskTrack and manage all your tasks with ease.",
        font=("League Spartan", 15, "italic"),
        bg="#4C9EEB",
        fg="white"
    )
    subtitle_label.pack()

    # Ensure header row resizes proportionally
    window.grid_rowconfigure(0, weight=0)

    # Frames for each day of the week
    days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    day_frames = {}
    task_buttons = {day: {} for day in days_of_week}

    # Colors for each day of the week
    day_colors = {
        "Sunday": "#F94144",  # Red
        "Monday": "#F3722C",  # Orange
        "Tuesday": "#F8961E",  # Yellow
        "Wednesday": "#F9C74F",  # Light Yellow
        "Thursday": "#90BE6D",  # Green
        "Friday": "#43AA8B",  # Teal
        "Saturday": "#577590"  # Blue
    }

    for i, day in enumerate(days_of_week):
        frame = tk.Frame(window, borderwidth=2, relief="groove", padx=10, pady=10)
        frame.grid(row=1, column=i, sticky="nsew", padx=5, pady=5)  # Adjust row index to 1
        day_frames[day] = frame

        # Set background color for each day
        frame.configure(bg=day_colors[day])

        # Label for the day
        tk.Label(frame, text=day, font=("League Spartan", 15, "bold"), bg=day_colors[day]).pack()

        # Load existing tasks for the day
        tasks = load_tasks_for_day(day)
        for task_id, task_title in tasks:
            create_task_button(task_title, task_id, day)




    # Create the "Create Task" button at the bottom
    add_task_button = tk.Button(window, text="Create Task", command=add_task, width=20)
    add_task_button.grid(row=2, column=0, columnspan=7, pady=10)

    ##clear_button = tk.Button(window, text="Clear All Tasks", command=clear_database)
    ##clear_button.grid(row=3, column=0, columnspan=7, pady=10)

    completed_button = tk.Button(window, text="Completed Tasks", command=completed_task_menu)
    completed_button.grid(row=3, column=0, columnspan=7, pady=10)


    # Ensure columns resize proportionally
    for i in range(7):
        window.grid_columnconfigure(i, weight=1, uniform="equal")
    window.grid_rowconfigure(1, weight=1)  # Make day frames stretchable

    window.mainloop()





############################# START'ER UP #########################################################################3
# Initialize database and start program
db_connection = initialize_database()
initialize_weekly_view()
