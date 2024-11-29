import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile


# Counter for button creation
button_count = 0

# Function to open the text editor when a task button is clicked
def text_editor_function(task_title):
    editor_window = tk.Tk()
    editor_window.title(f"Text Editor - {task_title}")
   
    # Where text is typed: the paper
    text_edit = tk.Text(editor_window, font="Helvetica 12") 
    text_edit.grid(row=1, column=0)

    # Fits in window
    editor_window.rowconfigure(1, weight=1)
    editor_window.columnconfigure(0, weight=1)

    # Functions frame
    frame = tk.Frame(editor_window, relief=tk.RAISED, bd=2)
    frame.grid(row=0, column=0, columnspan=2, sticky="ew") 

    # Buttons (e.g., Save button)
    button_save = tk.Button(frame, text="Save", command=lambda: save_file(editor_window, text_edit))

    button_save.grid(row=0, column=0)
    frame.grid(row=0, column=0)

    editor_window.mainloop()


# Function to save the text in the editor to a file
def save_file(editor_window, text_edit):
    filepath = asksaveasfile(filetypes=[("Text Files", "*.txt")])
    
    if not filepath:
        return
    
    with open(filepath, "w") as f:
        content = text_edit.get(1.0, tk.END)  # Gets text from start to end of file
        f.write(content)
    editor_window.title(f"Opened file: {filepath}")


# Function to create a new task button
def task_buttons(task_title):
    global button_count
    button_count += 1
    new_button = tk.Button(window, text=task_title, width=20,
                           command=lambda: text_editor_function(task_title))
    new_button.pack(pady=5)


# Form submission handler
def submission_form():
    task_title = entry_title.get()

    if not task_title:
        messagebox.showwarning("Error", "Title required!")
        return

    task_buttons(task_title)  # Adds the task button with title to the main window
    task_window.destroy()  # Closes the form window


# Form window (for task title input)
def open_task_window():
    global task_window, entry_title
    task_window = tk.Toplevel(window)  # Create a new window
    task_window.title("Create New Task")
    task_window.geometry("300x150")

    # Entry fields
    label_title = tk.Label(task_window, text="Enter Task Title:")
    label_title.pack(pady=10)
    
    entry_title = tk.Entry(task_window, width=30)
    entry_title.pack(pady=5)

    # Submit title button
    submit_button = tk.Button(task_window, text="Submit", command=submission_form)
    submit_button.pack(pady=10)


# Main window
def open_main_window():
    global window
    window = tk.Tk()
    window.title("Task Management")
    window.geometry("300x200")

    create_task_button = tk.Button(window, text="Create Task", command=open_task_window)
    create_task_button.pack(pady=20)

    window.mainloop()


# Start the main window
open_main_window()
