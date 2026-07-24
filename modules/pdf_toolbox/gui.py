import os
import tkinter as tk
from tkinter import filedialog, ttk

APP_TITLE = "PDF Toolbox — AI Toolbox Suite"


class PDFToolboxGUI:
    def __init__(self, root):
        self.root = root

        # Full paths of every selected PDF, in selection order. This is
        # the single source of truth for "what's selected" — the listbox
        # only displays it.
        self.selected_files = []

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
            selectmode="extended",
            yscrollcommand=file_list_scroll.set
        )
        file_list_scroll.config(command=self.file_listbox.yview)

        self.file_listbox.pack(side="left", fill="both", expand=True)
        file_list_scroll.pack(side="right", fill="y")

        # --- Output section ---------------------------------------------------
        self.output_frame = ttk.LabelFrame(container, text="Output", padding=15)
        self.output_frame.pack(fill="x", pady=(0, 15))

        # --- Processing Options section ---------------------------------------
        self.processing_options_frame = ttk.LabelFrame(
            container, text="Processing Options", padding=15
        )
        self.processing_options_frame.pack(fill="x", pady=(0, 15))

        # --- Progress section ---------------------------------------------------
        self.progress_frame = ttk.LabelFrame(container, text="Progress", padding=15)
        self.progress_frame.pack(fill="both", expand=True, pady=(0, 15))

        # --- Status bar ---------------------------------------------------------
        self.status_label = ttk.Label(
            container,
            text="Status: Ready",
            anchor="w"
        )
        self.status_label.pack(fill="x")

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

    def clear_files(self):
        self.file_listbox.delete(0, tk.END)
        self.selected_files.clear()

        self._update_status()
