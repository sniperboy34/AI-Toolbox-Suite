import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "PDF Toolbox — AI Toolbox Suite"
SETTINGS_FILENAME = "settings.json"
VALID_OUTPUT_FORMATS = ("TXT", "Markdown")


class PDFToolboxGUI:
    def __init__(self, root):
        self.root = root

        # Full paths of every selected PDF, in selection order. This is
        # the single source of truth for "what's selected" — the listbox
        # only displays it.
        self.selected_files = []

        # Output destination and format. None/"" means "not chosen yet";
        # the Output section widgets below keep these in sync.
        self.output_folder = None
        self.output_format = tk.StringVar(value="TXT")

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

        container = ttk.Frame(self.root, padding=20)
        container.pack(fill="both", expand=True)

        # --- Files section ---------------------------------------------------
        self.files_frame = ttk.LabelFrame(container, text="Files", padding=15)
        self.files_frame.pack(fill="both", expand=True, pady=(0, 15))

        files_buttons = ttk.Frame(self.files_frame)
        files_buttons.pack(fill="x", pady=(0, 10))

        self.add_pdf_button = ttk.Button(
            files_buttons,
            text="Add PDF",
            command=self.add_pdf
        )
        self.add_pdf_button.pack(side="left")

        self.remove_button = ttk.Button(
            files_buttons,
            text="Remove",
            command=self.remove_selected
        )
        self.remove_button.pack(side="left", padx=(10, 0))

        self.clear_button = ttk.Button(
            files_buttons,
            text="Clear",
            command=self.clear_files
        )
        self.clear_button.pack(side="left", padx=(10, 0))

        file_list_frame = ttk.Frame(self.files_frame)
        file_list_frame.pack(fill="both", expand=True)

        file_list_scroll = ttk.Scrollbar(file_list_frame, orient="vertical")

        self.file_listbox = tk.Listbox(
            file_list_frame,
            height=4,
            selectmode="extended",
            yscrollcommand=file_list_scroll.set
        )
        file_list_scroll.config(command=self.file_listbox.yview)

        self.file_listbox.pack(side="left", fill="both", expand=True)
        file_list_scroll.pack(side="right", fill="y")

        # --- Output + Processing Options row (side-by-side) -------------------
        output_and_options_row = ttk.Frame(container)
        output_and_options_row.pack(fill="x", pady=(0, 15))
        output_and_options_row.columnconfigure(0, weight=1)
        output_and_options_row.columnconfigure(1, weight=1)

        self.output_frame = ttk.LabelFrame(output_and_options_row, text="Output", padding=15)
        self.output_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.select_output_button = ttk.Button(
            self.output_frame,
            text="Select Output Folder",
            command=self.select_output_folder
        )
        self.select_output_button.pack(anchor="w")

        self.output_folder_label = ttk.Label(
            self.output_frame,
            text="No output folder selected",
            anchor="w"
        )
        self.output_folder_label.pack(fill="x", pady=(8, 15))

        output_format_frame = ttk.Frame(self.output_frame)
        output_format_frame.pack(fill="x")

        ttk.Label(output_format_frame, text="Output Format:").pack(side="left")

        self.txt_format_radio = ttk.Radiobutton(
            output_format_frame,
            text="TXT",
            variable=self.output_format,
            value="TXT"
        )
        self.txt_format_radio.pack(side="left", padx=(10, 0))

        self.markdown_format_radio = ttk.Radiobutton(
            output_format_frame,
            text="Markdown",
            variable=self.output_format,
            value="Markdown"
        )
        self.markdown_format_radio.pack(side="left", padx=(10, 0))

        # --- Processing Options section (second column of the row above) ------
        self.processing_options_frame = ttk.LabelFrame(
            output_and_options_row, text="Processing Options", padding=15
        )
        self.processing_options_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.smart_paragraph_reconstruction_var = tk.BooleanVar(value=True)
        self.remove_page_numbers_var = tk.BooleanVar(value=True)
        self.remove_header_footer_var = tk.BooleanVar(value=True)
        self.detect_titles_headings_var = tk.BooleanVar(value=True)
        self.detect_lists_var = tk.BooleanVar(value=True)

        self.smart_paragraph_reconstruction_checkbox = ttk.Checkbutton(
            self.processing_options_frame,
            text="Smart Paragraph Reconstruction",
            variable=self.smart_paragraph_reconstruction_var
        )
        self.smart_paragraph_reconstruction_checkbox.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=(0, 8))

        self.remove_page_numbers_checkbox = ttk.Checkbutton(
            self.processing_options_frame,
            text="Remove Page Numbers",
            variable=self.remove_page_numbers_var
        )
        self.remove_page_numbers_checkbox.grid(row=0, column=1, sticky="w", pady=(0, 8))

        self.remove_header_footer_checkbox = ttk.Checkbutton(
            self.processing_options_frame,
            text="Remove Header/Footer",
            variable=self.remove_header_footer_var
        )
        self.remove_header_footer_checkbox.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=(0, 8))

        self.detect_titles_headings_checkbox = ttk.Checkbutton(
            self.processing_options_frame,
            text="Detect Titles / Headings",
            variable=self.detect_titles_headings_var
        )
        self.detect_titles_headings_checkbox.grid(row=1, column=1, sticky="w", pady=(0, 8))

        self.detect_lists_checkbox = ttk.Checkbutton(
            self.processing_options_frame,
            text="Detect Lists",
            variable=self.detect_lists_var
        )
        self.detect_lists_checkbox.grid(row=2, column=0, sticky="w")

        # --- Progress section ---------------------------------------------------
        self.progress_frame = ttk.LabelFrame(container, text="Progress", padding=15)
        self.progress_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Bound to the progress bar so future processing code can just call
        # self.progress_value.set(n) instead of reaching into the widget.
        self.progress_value = tk.DoubleVar(value=0)

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            mode="determinate",
            variable=self.progress_value,
            maximum=100
        )
        self.progress_bar.pack(fill="x", pady=(0, 15))

        progress_info_row = ttk.Frame(self.progress_frame)
        progress_info_row.pack(fill="x")
        progress_info_row.columnconfigure(0, weight=1)
        progress_info_row.columnconfigure(1, weight=1)
        progress_info_row.columnconfigure(2, weight=1)

        self.current_file_label = ttk.Label(
            progress_info_row,
            text="Current file:\n—",
            anchor="w",
            justify="left"
        )
        self.current_file_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.page_progress_label = ttk.Label(
            progress_info_row,
            text="Processed pages:\n0 / 0",
            anchor="w",
            justify="left"
        )
        self.page_progress_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        # Reserved for a future version — time estimation itself is not
        # implemented yet, this widget only holds the placeholder text.
        self.estimated_time_label = ttk.Label(
            progress_info_row,
            text="Estimated remaining:\n—",
            anchor="w",
            justify="left"
        )
        self.estimated_time_label.grid(row=0, column=2, sticky="w")

        # --- Action buttons (bottom of window, above the status bar) --------
        action_buttons_frame = ttk.Frame(container)
        action_buttons_frame.pack(fill="x", pady=(0, 15))

        self.process_button = ttk.Button(
            action_buttons_frame,
            text="Process",
            width=20,
            command=self.process_files,
            state="disabled"
        )
        self.process_button.pack(side="left")

        self.cancel_button = ttk.Button(
            action_buttons_frame,
            text="Cancel",
            command=self.cancel_processing,
            state="disabled"
        )
        self.cancel_button.pack(side="left", padx=(10, 0))

        # --- Status bar ---------------------------------------------------------
        self.status_label = ttk.Label(
            container,
            text="Status: Ready",
            anchor="w"
        )
        self.status_label.pack(fill="x")

        # --- Output Format persistence ---------------------------------------
        # Auto-save whenever the format changes; restore whatever was saved
        # (if anything) last, now that the widget exists to receive it.
        self.output_format.trace_add("write", lambda *_: self.save_settings())
        self.smart_paragraph_reconstruction_var.trace_add("write", lambda *_: self.save_settings())
        self.remove_page_numbers_var.trace_add("write", lambda *_: self.save_settings())
        self.remove_header_footer_var.trace_add("write", lambda *_: self.save_settings())
        self.detect_titles_headings_var.trace_add("write", lambda *_: self.save_settings())
        self.detect_lists_var.trace_add("write", lambda *_: self.save_settings())
        self.load_settings()
        self._update_process_button_state()

    def _settings_path(self):
        module_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(module_root, SETTINGS_FILENAME)

    def save_settings(self, event=None):
        settings = {
            "output_format": self.output_format.get(),
            "output_folder": self.output_folder,
            "smart_paragraph_reconstruction": self.smart_paragraph_reconstruction_var.get(),
            "remove_page_numbers": self.remove_page_numbers_var.get(),
            "remove_header_footer": self.remove_header_footer_var.get(),
            "detect_titles_headings": self.detect_titles_headings_var.get(),
            "detect_lists": self.detect_lists_var.get(),
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

        saved_format = settings.get("output_format")
        if saved_format in VALID_OUTPUT_FORMATS:
            self.output_format.set(saved_format)
        # An invalid or missing value is left as-is, keeping the default
        # ("TXT") that self.output_format was already initialized with.

        saved_folder = settings.get("output_folder")
        if saved_folder and os.path.isdir(saved_folder):
            self.output_folder = saved_folder
            self.output_folder_label.config(text=saved_folder)
        # A missing, empty, or no-longer-existing folder is ignored,
        # keeping the current default (None / "No output folder selected").

        option_vars = (
            ("smart_paragraph_reconstruction", self.smart_paragraph_reconstruction_var),
            ("remove_page_numbers", self.remove_page_numbers_var),
            ("remove_header_footer", self.remove_header_footer_var),
            ("detect_titles_headings", self.detect_titles_headings_var),
            ("detect_lists", self.detect_lists_var),
        )
        for key, var in option_vars:
            saved_value = settings.get(key)
            if isinstance(saved_value, bool):
                var.set(saved_value)
            # A missing or non-boolean value is left as-is, keeping the
            # existing default (True) that the variable was initialized with.

    def _update_process_button_state(self):
        """Process is only enabled once both prerequisites are met: at
        least one PDF selected, and a valid (existing) output folder.
        Called after anything that could change either condition."""
        has_files = bool(self.selected_files)
        has_valid_folder = bool(self.output_folder) and os.path.isdir(self.output_folder)

        if has_files and has_valid_folder:
            self.process_button.config(state="normal")
        else:
            self.process_button.config(state="disabled")

    def _update_status(self):
        """Refresh the status bar to reflect the current selection count.
        Shared by every operation that changes self.selected_files, so the
        status text stays consistent no matter which action triggered it."""
        count = len(self.selected_files)

        if count == 0:
            text = "Status: No PDF selected"
        else:
            text = f"Status: {count} PDF(s) selected"

        self.status_label.config(text=text)

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")

        if not folder:
            return

        self.output_folder = folder
        self.output_folder_label.config(text=folder)
        self.save_settings()
        self._update_process_button_state()

    def add_pdf(self):
        new_paths = filedialog.askopenfilenames(
            title="Add PDF",
            filetypes=[
                ("PDF files", "*.pdf")
            ]
        )

        if not new_paths:
            return

        for path in new_paths:
            if path not in self.selected_files:
                self.selected_files.append(path)
                self.file_listbox.insert(tk.END, os.path.basename(path))

        self._update_status()
        self._update_process_button_state()

    def remove_selected(self):
        selected_indices = self.file_listbox.curselection()

        if not selected_indices:
            return

        # Delete from the end backward so earlier indices stay valid as
        # later ones are removed.
        for index in reversed(selected_indices):
            self.file_listbox.delete(index)
            del self.selected_files[index]

        self._update_status()
        self._update_process_button_state()

    def clear_files(self):
        self.file_listbox.delete(0, tk.END)
        self.selected_files.clear()

        self._update_status()
        self._update_process_button_state()

    def process_files(self):
        if not self.selected_files:
            messagebox.showerror(
                "Error",
                "Please select at least one PDF file."
            )
            return

        if not self.output_folder:
            messagebox.showerror(
                "Error",
                "Please select an output folder."
            )
            return

        self.process_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.status_label.config(text="Status: Preparing...")

    def cancel_processing(self):
        self.process_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.status_label.config(text="Status: Ready")
