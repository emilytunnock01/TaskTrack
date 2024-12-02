import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from database import (
  save_task_to_db, 
  update_task_in_db, 
  delete_task_from_db, 
  completed_task, 
  load_completed_tasks, 
  load_tasks_for_day, 
  initialize_database
)

##################################################  UI  ##################################################
def center_window(window, width, height):
    # Get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate the position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set the geometry of the window
    window.geometry(f"{width}x{height}+{x}+{y}")

################################################## TEXT EDITOR WINDOW ##################################################
def open_text_editor(task_title, task_id=None, day=None, status="not-complete"):
    editor_window = tk.Toplevel()
    editor_window.title(f"Editing Task - {task_title}")
    center_window(editor_window, 400, 450)

    frame = tk.Frame(editor_window, relief=tk.RAISED, bd=1, bg="white")
    frame.pack(side="top", fill="x")

    title_var = tk.StringVar(value=task_title)  # For managing title changes
    day_var = tk.StringVar(value=day)  # For managing the day of the week

    # Title section
    title_frame = tk.Frame(frame, bg="white")
    title_frame.pack(side="top", fill="x", pady=5)

    tk.Label(title_frame, text="Title:", bg="white", fg="#6A7F8C", font=("Montserrat", 12, "bold")).pack(side="left", padx=5)
    title_entry = tk.Entry(title_frame, textvariable=title_var, font=("Montserrat", 12))
    title_entry.pack(side="left", padx=5, fill="x", expand=True)

    # "Move to Day" section, centered
    day_frame = tk.Frame(frame, bg="white")
    day_frame.pack(side="top", fill="x", pady=5)

    day_label = tk.Label(day_frame, text="Move to Day:", bg="white", fg="#6A7F8C", font=("Montserrat", 10, "bold"))
    day_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    day_dropdown = tk.OptionMenu(day_frame, day_var, "Monday", "Tuesday", "Wednesday", 
                                  "Thursday", "Friday", "Saturday", "Sunday")
    day_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Center the "Move to Day" section
    day_frame.grid_columnconfigure(0, weight=1)
    day_frame.grid_columnconfigure(1, weight=1)

    # Text editor for task content
    text_edit = tk.Text(editor_window, font="Roboto 12")
    text_edit.pack(expand=True, fill="both", padx=10, pady=10)

    # Action buttons, centered
    button_frame = tk.Frame(frame, bg="white")
    button_frame.pack(side="top", fill="x", pady=5)

    button_save = tk.Button(button_frame, text="Save", command=lambda: save_content())
    button_save.grid(row=0, column=0, padx=5)

    button_delete = tk.Button(button_frame, text="Delete", command=lambda: delete_content())
    button_delete.grid(row=0, column=1, padx=5)

    button_complete = tk.Button(button_frame, text="Mark as Completed", command=lambda: mark_as_completed())
    button_complete.grid(row=0, column=2, padx=5)

    # Center the buttons
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)

    def save_content():
        nonlocal task_id
        new_title = title_var.get().strip()
        new_day = day_var.get()
        content = text_edit.get("1.0", tk.END).strip()

        if not new_title:
            messagebox.showwarning("Missing Title", "Please provide a task title.")
            return

        if task_id is None:  # New task
            save_task_to_db(new_title, content, new_day)
            cursor = db_connection.cursor()
            cursor.execute("SELECT id FROM tasks WHERE title = ?", (new_title,))
            new_task_id = cursor.fetchone()
            if new_task_id:
                task_id = new_task_id[0]
        else:  # Update existing task
            if new_title != task_title or new_day != day:  # Update if title or day changes
                cursor = db_connection.cursor()
                cursor.execute(
                    "UPDATE tasks SET title = ?, day = ? WHERE id = ?",
                    (new_title, new_day, task_id),
                )
                db_connection.commit()

                # Handle UI changes for moving the task
                if task_title in task_buttons[day]:
                    task_buttons[day][task_title].destroy()
                    del task_buttons[day][task_title]

                create_task_button(new_title, task_id, new_day)

            update_task_in_db(task_id, content)

        messagebox.showinfo("Saved", f"Task '{new_title}' saved!")
        editor_window.destroy()

    def delete_content():
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the task '{task_title}'?"):
            delete_task_from_db(task_title)
            if task_title in task_buttons[day]:
                task_buttons[day][task_title].destroy()
                del task_buttons[day][task_title]
            messagebox.showinfo("Deleted", f"Task '{task_title}' deleted!")
            editor_window.destroy()

    def mark_as_completed():
        if messagebox.askyesno("Mark as Completed", f"Mark task '{task_title}' as completed?"):
            completed_task(task_id, task_title, day)
            editor_window.destroy()

    # Pre-fill the content if the task exists
    if task_id is not None:
        cursor = db_connection.cursor()
        cursor.execute("SELECT content FROM tasks WHERE id = ?", (task_id,))
        content = cursor.fetchone()
        if content and content[0]:
            text_edit.insert("1.0", content[0])

################################################## TASK CREATION ##################################################
# Create a task button
def create_task_button(task_title, task_id=None, day=None, status="not-completed"):
    # Dynamically set width based on task title length
    max_title_length = 30  # Maximum number of characters that will fit within the button
    title_length = len(task_title) + 5
    button_width = min(max_title_length, title_length) + 5  # Add extra space for padding

    task_button = tk.Button(day_frames[day], text=task_title, width=button_width,
                            command=lambda: open_text_editor(task_title, task_id, day, status)) #open the text-editor for that task
    task_button.pack(pady=5)
    task_buttons[day][task_title] = task_button  # Track the button in the global dictionary


#function for creating task form
def add_task():
    # Create a pop-up window
    task_window = tk.Toplevel(window)
    task_window.title("Creating a Task")
    center_window(task_window, 300, 200)
    
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


#pop up window to view and access completed tasks
def completed_task_menu():
    completed_tasks = load_completed_tasks()

    # Create a new popup window to display completed tasks
    completed_window = tk.Toplevel()
    completed_window.title("Completed Tasks")
    center_window(completed_window, 400, 400)

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


################################################## MAIN MENU ##################################################
from datetime import datetime, timedelta

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

def initialize_weekly_view():
    global window, day_frames, task_buttons
    window = tk.Tk()
    window.title("TaskTrack")
    center_window(window, 1150, 900)

    # Header frame for the title and subtitle
    header_frame = tk.Frame(window, bg="#6A7F8C", pady=10)
    header_frame.grid(row=0, column=0, columnspan=7, sticky="nsew")

    # Title label
    title_label = tk.Label(
        header_frame,
        text="Welcome to TaskTrack!",
        font=("Montserrat", 25, "bold"),
        bg="#6A7F8C",
        fg="white"
    )
    title_label.pack()

    # Subtitle label
    subtitle_label = tk.Label(
        header_frame,
        text="FastTrack with TaskTrack and manage all your tasks with ease.",
        font=("Roboto", 10, "italic"),
        bg="#6A7F8C",
        fg="white"
    )
    subtitle_label.pack()

    # Ensure header row resizes proportionally
    window.grid_rowconfigure(0, weight=0)

    # Frames for each day of the week
    days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    day_frames = {}
    task_buttons = {day: {} for day in days_of_week}

    # Get the current date and calculate the week
    today = datetime.now()
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)  # Get the start of the week (Sunday)
    day_colors = {
        "Sunday": "#F94144",
        "Monday": "#F3722C",
        "Tuesday": "#F8961E",
        "Wednesday": "#F9C74F",
        "Thursday": "#90BE6D",
        "Friday": "#43AA8B",
        "Saturday": "#577590"
    }


    for i, day in enumerate(days_of_week):
        frame = tk.Frame(window, borderwidth=2, relief="raised", padx=10, pady=10)
        frame.grid(row=1, column=i, sticky="nsew", padx=5, pady=5)
        day_frames[day] = frame

        # Set background color
        frame.configure(bg=day_colors[day])

        # Calculate the date for the day
        current_date = start_of_week + timedelta(days=i)
        date_str = current_date.strftime("%m/%d/%Y")

        # Label for the day
        tk.Label(frame, text=day, font=("Montserrat", 15, "bold"), fg="white", bg=day_colors[day]).pack()
        tk.Label(frame, text=date_str, font=("Roboto", 10), fg="white", bg=day_colors[day]).pack()


        # Load existing tasks for the day and add the task-buttons into view
        tasks = load_tasks_for_day(day)
        for task_id, task_title in tasks:
            create_task_button(task_title, task_id, day)

        # setup the "Create New Task" button and "View Completed Tasks" button on the same row
        add_task_button = tk.Button(window, text="Create New Task", command=add_task, width=20)
        add_task_button.grid(row=2, column=1, columnspan=2, pady=10, padx=10)

        completed_button = tk.Button(window, text="View Completed Tasks", command=completed_task_menu, width=20)
        completed_button.grid(row=2, column=4, columnspan=2, pady=10, padx=10)

    # Ensure columns resize proportionally
    for i in range(7):
        window.grid_columnconfigure(i, weight=1, uniform="equal")
    window.grid_rowconfigure(1, weight=1)
    
    # All Rights Reserved Footer
    footer_label_frame = tk.Frame(window, bg="#6A7F8C", pady=5)
    footer_label_frame.grid(row=4, column=0, columnspan=7, sticky="nsew")  # Use grid instead of pack

    footer_label = tk.Label(
        footer_label_frame,
        text="TaskTrack © 2024 | All Rights Reserved to Michelle Palatty and Emily Tunnock",
        font=("Roboto", 10, "bold"),
        bg="#6A7F8C",
        fg="white"
    )
    footer_label.pack()  # You can still use pack for the label inside the frame

    window.mainloop()

################################################## START'ER UP ##################################################
# Initialize database and start program
db_connection = initialize_database()
initialize_weekly_view()