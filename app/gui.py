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

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        self.title_label = ttk.Label(
            container,
            text=APP_TITLE,
            style="Title.TLabel"
        )
        self.title_label.pack(pady=(0, 20))

        # --- Files section -------------------------------------------------
        files_frame = ttk.LabelFrame(container, text="Files", padding=15)
        files_frame.pack(fill="x", pady=(0, 15))

        files_buttons = ttk.Frame(files_frame)
        files_buttons.pack(fill="x")

        self.select_button = ttk.Button(
            files_buttons,
            text="Select Images",
            command=self.select_images
        )
        self.select_button.pack(side="left")

        self.output_button = ttk.Button(
            files_buttons,
            text="Select Output Folder",
            command=self.select_output_folder
        )
        self.output_button.pack(side="left", padx=(10, 0))

        self.output_label = ttk.Label(
            files_frame,
            text="Output Folder: Not selected",
            anchor="w"
        )
        self.output_label.pack(fill="x", pady=(10, 0))

        # --- Resize options section -----------------------------------------
        resize_frame = ttk.LabelFrame(container, text="Resize Options", padding=15)
        resize_frame.pack(fill="x", pady=(0, 15))

        RESIZE_PRESETS = {
            "64x64": (64, 64),
            "128x128": (128, 128),
            "256x256": (256, 256),
            "512x512": (512, 512),
            "800x600": (800, 600),
            "1024x768": (1024, 768),
            "1280x720": (1280, 720),
            "1920x1080": (1920, 1080),
            "2048x2048": (2048, 2048),
            "3840x2160": (3840, 2160),
        }
        self.resize_presets = RESIZE_PRESETS

        ttk.Label(resize_frame, text="Resize Preset:").grid(row=0, column=0, sticky="w")

        self.preset_var = tk.StringVar(value="Custom")

        self.preset_combo = ttk.Combobox(
            resize_frame,
            textvariable=self.preset_var,
            values=list(RESIZE_PRESETS.keys()) + ["Custom"],
            state="readonly",
            width=12
        )
        self.preset_combo.grid(row=0, column=1, columnspan=2, padx=(8, 20), pady=(0, 10), sticky="w")
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_selected)

        ttk.Label(resize_frame, text="Width:").grid(row=1, column=0, sticky="w")

        self.width_entry = ttk.Entry(resize_frame, width=10)
        self.width_entry.grid(row=1, column=1, padx=(8, 20), sticky="w")

        ttk.Label(resize_frame, text="Height:").grid(row=1, column=2, sticky="w")

        self.height_entry = ttk.Entry(resize_frame, width=10)
        self.height_entry.grid(row=1, column=3, padx=(8, 20), sticky="w")

        self.keep_aspect_var = tk.BooleanVar(value=False)

        self.keep_aspect_checkbox = ttk.Checkbutton(
            resize_frame,
            text="Keep Aspect Ratio",
            variable=self.keep_aspect_var
        )
        self.keep_aspect_checkbox.grid(row=1, column=4, sticky="w")

        # --- Output options section -----------------------------------------
        format_frame = ttk.LabelFrame(container, text="Output Options", padding=15)
        format_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(format_frame, text="Output Format:").grid(row=0, column=0, sticky="w")

        self.format_var = tk.StringVar(value="JPG")

        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.format_var,
            values=["JPG", "PNG", "WEBP"],
            state="readonly",
            width=8
        )
        format_combo.grid(row=0, column=1, padx=(8, 30), sticky="w")

        ttk.Label(format_frame, text="Quality (JPEG/WEBP):").grid(row=0, column=2, sticky="w")

        self.quality_var = tk.IntVar(value=95)

        self.quality_slider = tk.Scale(
            format_frame,
            from_=1,
            to=100,
            orient="horizontal",
            variable=self.quality_var,
            length=180
        )
        self.quality_slider.grid(row=0, column=3, padx=(8, 10), sticky="w")

        # --- Process section -------------------------------------------------
        process_frame = ttk.Frame(container)
        process_frame.pack(fill="x", pady=(0, 15))

        self.resize_button = ttk.Button(
            process_frame,
            text="Process Images",
            width=20,
            command=self.start_processing
        )
        self.resize_button.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(
            process_frame,
            orient="horizontal",
            length=400,
            mode="determinate"
        )
        self.progress.pack(pady=(0, 10))

        self.status_label = ttk.Label(
            process_frame,
            text="Status: Ready",
            anchor="w"
        )
        self.status_label.pack(fill="x")

        # --- File list section -------------------------------------------------
        list_frame = ttk.LabelFrame(container, text="Selected Images", padding=10)
        list_frame.pack(fill="both", expand=True)

        list_scroll = ttk.Scrollbar(list_frame, orient="vertical")

        self.file_listbox = tk.Listbox(
            list_frame,
            width=100,
            height=20,
            yscrollcommand=list_scroll.set
        )
        list_scroll.config(command=self.file_listbox.yview)

        self.file_listbox.pack(side="left", fill="both", expand=True)
        list_scroll.pack(side="right", fill="y")

    def on_preset_selected(self, event=None):
        preset = self.preset_var.get()

        if preset == "Custom":
            self.width_entry.config(state="normal")
            self.height_entry.config(state="normal")
            return

        width, height = self.resize_presets[preset]

        self.width_entry.config(state="normal")
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(width))
        self.width_entry.config(state="disabled")

        self.height_entry.config(state="normal")
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(height))
        self.height_entry.config(state="disabled")

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

    def start_processing(self):
        self.resize_button.config(state="disabled")
        threading.Thread(target=self.resize_images, daemon=True).start()

    def resize_images(self):
        try:
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

            if not self.processor.set_resize_values(
                self.width_entry.get(),
                self.height_entry.get()
            ):
                messagebox.showerror(
                    "Error",
                    "Enter valid width and height."
                )
                return

            self.processor.set_output_format(
                self.format_var.get()
            )

            self.processor.set_keep_aspect_ratio(
                self.keep_aspect_var.get()
            )

            self.processor.set_quality(
                self.quality_var.get()
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
        finally:
            self.resize_button.config(state="normal")
