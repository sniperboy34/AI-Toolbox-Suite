import os
import json
import tkinter as tk
import threading
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import DND_FILES

from app.image_processor import ImageProcessor

APP_TITLE = "Image Toolbox"
SETTINGS_FILENAME = "settings.json"
DROPPABLE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


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
            # "clam" isn't guaranteed to be available on every Tk install;
            # fall back to whatever the platform default theme is.
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

        # Common target sizes offered in the "Resize Preset" dropdown.
        # "Custom" (appended below) lets the user type their own width/height.
        self.resize_presets = {
            "64x64": (64, 64),
            "128x128": (128, 128),
            "256x256": (256, 256),
            "512x512": (512, 512),
            "800x600": (800, 600),
            "1024x768": (1024, 768),
            "1280x720 (HD)": (1280, 720),
            "1920x1080 (Full HD)": (1920, 1080),
            "2048x2048": (2048, 2048),
            "3840x2160 (4K)": (3840, 2160),
        }

        ttk.Label(resize_frame, text="Resize Preset:").grid(row=0, column=0, sticky="w")

        self.preset_var = tk.StringVar(value="Custom")

        self.preset_combo = ttk.Combobox(
            resize_frame,
            textvariable=self.preset_var,
            values=list(self.resize_presets.keys()) + ["Custom"],
            state="readonly",
            width=20
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

        # --- Persistent settings --------------------------------------------
        # Auto-save whenever a persisted setting changes.
        self.format_var.trace_add("write", lambda *_: self.save_settings())
        self.keep_aspect_var.trace_add("write", lambda *_: self.save_settings())
        self.width_entry.bind("<FocusOut>", self.save_settings)
        self.height_entry.bind("<FocusOut>", self.save_settings)

        # Also save on close, so any in-progress edits aren't lost.
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # --- Drag & drop ------------------------------------------------------
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

        # Restore settings saved from a previous run, if any.
        self.load_settings()

    def _settings_path(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(project_root, SETTINGS_FILENAME)

    def save_settings(self, event=None):
        settings = {
            "output_folder": self.processor.get_output_folder(),
            "width": self.width_entry.get(),
            "height": self.height_entry.get(),
            "output_format": self.format_var.get(),
            "resize_preset": self.preset_var.get(),
            "keep_aspect_ratio": self.keep_aspect_var.get(),
        }

        try:
            with open(self._settings_path(), "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except OSError:
            # Persisting settings is a convenience, not critical —
            # ignore failures (e.g. read-only folder) silently.
            pass

    def load_settings(self):
        path = self._settings_path()

        if not os.path.exists(path):
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except (OSError, ValueError):
            return

        output_folder = settings.get("output_folder") or ""
        if output_folder:
            self.processor.set_output_folder(output_folder)
            self.output_label.config(text=f"Output Folder: {output_folder}")

        # Restore the preset first: if it's a real preset, on_preset_selected
        # fills and locks Width/Height itself. Only fall back to the saved
        # raw width/height below if the preset turned out to be "Custom".
        preset = settings.get("resize_preset", "Custom")
        if preset in self.resize_presets or preset == "Custom":
            self.preset_var.set(preset)
            self.on_preset_selected(save=False)

        if self.preset_var.get() == "Custom":
            self._set_entry_value(self.width_entry, settings.get("width", ""))
            self._set_entry_value(self.height_entry, settings.get("height", ""))

        output_format = settings.get("output_format", "JPG")
        if output_format in ("JPG", "PNG", "WEBP"):
            self.format_var.set(output_format)

        self.keep_aspect_var.set(bool(settings.get("keep_aspect_ratio", False)))

    def _on_close(self):
        self.save_settings()
        self.root.destroy()

    def _set_entry_value(self, entry, value, disable=False):
        """Replace an Entry's contents with `value`. Used for both
        preset-filled fields (disable=True, so the user can't edit a
        preset's numbers) and restoring a saved Custom width/height."""
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
        if disable:
            entry.config(state="disabled")

    def _populate_file_list(self, paths):
        """Insert each path's basename into the listbox, then refresh the
        status label with the current total selection count. Shared by
        select_images() (which lists everything) and on_drop() (which
        only passes the newly-added paths, since the listbox already
        holds whatever was selected before)."""
        for path in paths:
            self.file_listbox.insert(tk.END, os.path.basename(path))

        self.status_label.config(
            text=f"Status: {self.file_listbox.size()} image(s) selected"
        )

    def on_preset_selected(self, event=None, save=True):
        # save=False is used by load_settings(): it restores the preset
        # before the rest of the saved state (format, keep-aspect, etc.)
        # is applied, so saving here would write a half-restored settings
        # file. The combobox binding and manual calls elsewhere all want
        # the normal save=True behavior.
        preset = self.preset_var.get()

        if preset == "Custom":
            self.width_entry.config(state="normal")
            self.height_entry.config(state="normal")
        else:
            width, height = self.resize_presets[preset]
            self._set_entry_value(self.width_entry, width, disable=True)
            self._set_entry_value(self.height_entry, height, disable=True)

        if save:
            self.save_settings()

    def on_drop(self, event):
        dropped_paths = self.root.tk.splitlist(event.data)

        new_files = [
            path for path in dropped_paths
            if os.path.isfile(path)
            and path.lower().endswith(DROPPABLE_EXTENSIONS)
        ]

        if not new_files:
            return

        existing_files = list(self.processor.get_selected_files())

        # Skip anything already selected, checking progressively so a
        # duplicate path within this same drop is also only added once.
        added = []
        for path in new_files:
            if path not in existing_files:
                existing_files.append(path)
                added.append(path)

        if not added:
            return

        self.processor.set_selected_files(existing_files)
        self._populate_file_list(added)

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
            self._populate_file_list(files)

    def select_output_folder(self):
        folder = filedialog.askdirectory()

        if folder:
            self.processor.set_output_folder(folder)
            self.output_label.config(
                text=f"Output Folder: {folder}"
            )
            self.save_settings()

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
            failures = []

            for index, file in enumerate(files, start=1):
                try:
                    self.processor.resize_image(file)
                    success_count += 1
                except Exception as error:
                    failures.append((os.path.basename(file), str(error)))

                self.progress["value"] = index

                self.status_label.config(
                    text=f"Status: Processing {index}/{len(files)}"
                )

                self.root.update_idletasks()

            self.progress["value"] = len(files)

            self.status_label.config(
                text=f"Status: {success_count} succeeded, {len(failures)} failed"
            )

            messagebox.showinfo(
                "Done",
                f"Successful: {success_count}\nFailed: {len(failures)}"
            )

            if failures:
                self.show_failures_dialog(failures)
        finally:
            self.resize_button.config(state="normal")

    def show_failures_dialog(self, failures):
        dialog = tk.Toplevel(self.root)
        dialog.title("Failed Images")
        dialog.geometry("520x320")
        dialog.transient(self.root)

        container = ttk.Frame(dialog, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text=f"{len(failures)} image(s) failed to process:"
        ).pack(anchor="w", pady=(0, 10))

        list_frame = ttk.Frame(container)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")

        failures_text = tk.Text(
            list_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            height=12
        )
        scrollbar.config(command=failures_text.yview)

        for filename, error_message in failures:
            failures_text.insert(tk.END, f"{filename}\n    {error_message}\n\n")

        failures_text.config(state="disabled")

        failures_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(
            container,
            text="Close",
            command=dialog.destroy
        ).pack(pady=(10, 0))
