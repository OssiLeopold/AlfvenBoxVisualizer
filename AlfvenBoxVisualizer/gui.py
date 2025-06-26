import tkinter
import customtkinter

def choose_directory():
    directory = tkinter.filedialog.askdirectory()
    if directory:
        print("Selected directory:", directory)
        bulkfile_dir.set(directory)

# System settings
customtkinter.set_appearance_mode("System")

# App frame
app = customtkinter.CTk()
app.geometry("720x480")
app.title("AlfvenBoxVisualizer")

# Add bulkfile directory chooser
# Generate frame for label, directory and button
bulkfile_dir_frame = customtkinter.CTkFrame(app)
bulkfile_dir_frame.pack(pady = 10)

bulkfile_dir_label = customtkinter.CTkLabel(bulkfile_dir_frame, text = "Bulkfile directory: ")
bulkfile_dir_label.pack(side="left", padx = (0,5))

bulkfile_dir = customtkinter.StringVar()

bulkfile_dir_entry = customtkinter.CTkEntry(bulkfile_dir_frame, textvariable = bulkfile_dir, width = 400)
bulkfile_dir_entry.pack(padx = (5,5), side = "left")

button = customtkinter.CTkButton(bulkfile_dir_frame, text = "Choose bulkfile dir", command = choose_directory)
button.pack(padx = (5,5), side = "right")

# Generate output directory chooser
output_dir_frame = customtkinter.CTkFrame(app)
output_dir_frame.pack(pady = 10)

output_dir_label = customtkinter.CTkLabel(output_dir_frame, text = "Output directory: ")
output_dir_label.pack(side="left", padx = (0,5))

output_dir = customtkinter.StringVar()

output_dir_entry = customtkinter.CTkEntry(output_dir_frame, textvariable = output_dir, width = 400)
output_dir_entry.pack(padx = (5,5), side = "left")

button = customtkinter.CTkButton(output_dir_frame, text = "Choose output dir", command = choose_directory)
button.pack(padx = (5,5), side = "right")

# Run app
app.mainloop()