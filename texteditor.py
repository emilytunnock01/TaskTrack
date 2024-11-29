import tkinter as tkinter
from tkinter.filedialog import asksaveasfile

def save_file(window, text_edit):
    filepath = asksaveasfile(filetypes=[("Text Files", "*.txt")])
    
    if not filepath:
        return
    
    with open(filepath, "w") as f:
        content = text_edit.get(1.0, tkinter.END) #gets text from start to end of file
        f.write(content)
    window.title(f"Open file: {filepath}")


def main():
    window = tkinter.Tk()
    window.title("text Editor")
   
    #where text is typed: the paper
    text_edit = tkinter.Text(window, font = "Helvetica 12") 
    text_edit.grid(row = 1, column = 0)

    #fits in window
    window.rowconfigure(1, weight=1)
    window.columnconfigure(0, weight=1)

    #functions frame
    frame = tkinter.Frame(window, relief=tkinter.RAISED, bd=2)
    frame.grid(row=0, column=0, columnspan=2, sticky="ew") 

   
    #buttons
    button_save = tkinter.Button(frame, text="Save", command=lambda:save_file(window, text_edit))

    button_save.grid(row=0, column=0)
    frame.grid(row=0, column=0)

    window.mainloop()

main()