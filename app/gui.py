import os
import tkinter as tk
import threading
from tkinter import filedialog, messagebox, ttk

from app.image_processor import ImageProcessor

APP_TITLE = "Image Toolbox"


class ImageToolboxGUI:
    def __init__(self, root):
        self.root = root
        self.processor = ImageProcessor()

        self.root.title(APP_TITLE)
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        self.title_label = tk.Label(
            self.root,
            text=APP_TITLE,
            font=("Segoe UI", 20, "bold")
        )
        self.title_label.pack(pady=20)

        self.select_button = tk.Button(
            self.root,
            text="Select Images",
            command=self.select_images
        )
        self.select_button.pack(pady=10)

        self.output_button = tk.Button(
            self.root,
            text="Select Output Folder",
            command=self.select_output_folder
        )
        self.output_button.pack(pady=5)

        self.output_label = tk.Label(
            self.root,
            text="Output Folder: Not selected",
            anchor="w"
        )
        self.output_label.pack(fill="x", padx=20)

        resize_frame = tk.Frame(self.root)
        resize_frame.pack(pady=10)

        tk.Label(
            resize_frame,
            text="Width:"
        ).pack(side="left")

        self.width_entry = tk.Entry(
            resize_frame,
            width=8
        )
        self.width_entry.pack(side="left", padx=5)

        tk.Label(
            resize_frame,
            text="Height:"
        ).pack(side="left")

        self.height_entry = tk.Entry(
            resize_frame,
            width=8
        )
        self.height_entry.pack(side="left", padx=5)

        self.save_size_button = tk.Button(
            self.root,
            text="Save Resize Values",
            command=self.save_resize_values
        )
        self.save_size_button.pack(pady=5)

        format_frame = tk.Frame(self.root)
        format_frame.pack(pady=5)

        tk.Label(
            format_frame,
            text="Output Format:"
        ).pack(side="left")

        self.format_var = tk.StringVar(value="JPG")

        tk.OptionMenu(
            format_frame,
            self.format_var,
            "JPG",
            "PNG",
            "WEBP"
        ).pack(side="left")

        self.resize_button = tk.Button(
            self.root,
            text="Process Images",
            width=20,
            command=lambda: threading.Thread(target=self.resize_images, daemon=True).start()
        )
        self.resize_button.pack(pady=5)

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress.pack(pady=10)

        self.status_label = tk.Label(
            self.root,
            text="Status: Ready",
            anchor="w"
        )
        self.status_label.pack(
            fill="x",
            padx=20
        )

        self.file_listbox = tk.Listbox(
            self.root,
            width=100,
            height=20
        )
        self.file_listbox.pack(
            padx=20,
            pady=20,
            fill="both",
            expand=True
        )

    def select_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.webp")
            ]
        )

        self.file_listbox.delete(0, tk.END)

        if files:
            self.processor.set_selected_files(files)

            for file in files:
                self.file_listbox.insert(
                    tk.END,
                    os.path.basename(file)
                )

            self.status_label.config(
                text=f"Status: {len(files)} image(s) selected"
            )

    def select_output_folder(self):
        folder = filedialog.askdirectory()

        if folder:
            self.processor.set_output_folder(folder)
            self.output_label.config(
                text=f"Output Folder: {folder}"
            )

    def save_resize_values(self):
        if self.processor.set_resize_values(
            self.width_entry.get(),
            self.height_entry.get()
        ):
            messagebox.showinfo(
                "Success",
                "Resize values saved."
            )
        else:
            messagebox.showerror(
                "Error",
                "Enter valid width and height."
            )

    def resize_images(self):
        files = self.processor.get_selected_files()

        self.progress["value"] = 0
        self.progress["maximum"] = len(files)
        self.root.update_idletasks()

        if not files:
            messagebox.showerror(
                "Error",
                "No images selected."
            )
            return

        if not self.processor.get_output_folder():
            messagebox.showerror(
                "Error",
                "Please select output folder."
            )
            return

        width, height = self.processor.get_resize_values()

        if not width or not height:
            messagebox.showerror(
                "Error",
                "Please enter resize values."
            )
            return

        self.processor.set_output_format(
            self.format_var.get()
        )

        success_count = 0

        for index, file in enumerate(files, start=1):
            result = self.processor.resize_image(file)

            if result:
                success_count += 1

            self.progress["value"] = index

            self.status_label.config(
                text=f"Status: Processing {index}/{len(files)}"
            )

            self.root.update_idletasks()

        self.progress["value"] = len(files)

        self.status_label.config(
            text=f"Status: {success_count} image(s) processed"
        )

        messagebox.showinfo(
            "Done",
            f"{success_count} image(s) processed successfully."
        )
