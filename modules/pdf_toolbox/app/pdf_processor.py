import os

import fitz


class PDFProcessor:
    """Placeholder for PDF Toolbox's processing engine.

    No processing logic is implemented yet. This class will eventually
    house PDF loading, text extraction, cleaning, structural analysis,
    and export logic, following the approved PDF Toolbox architecture.
    """

    def __init__(self):
        pass

    def process_file(self, input_pdf, output_folder, output_format, options):
        """Extract plain text from a single PDF and save it to output_folder.

        Parameters
        ----------
        input_pdf : str
            Full path of one PDF file.
        output_folder : str
            Destination directory.
        output_format : str
            Either "TXT" or "Markdown".
        options : dict
            Processing option flags from the GUI. Accepted only for API
            compatibility — none of them are applied yet.

        Returns
        -------
        str
            Full path of the saved output file.
        """
        if not os.path.exists(output_folder):
            raise ValueError(f"Output folder does not exist: {output_folder}")

        if not os.path.isdir(output_folder):
            raise ValueError(f"Output path is not a directory: {output_folder}")

        if not os.access(output_folder, os.W_OK):
            raise ValueError(f"Output folder is not writable: {output_folder}")

        try:
            document = fitz.open(input_pdf)
        except Exception:
            raise ValueError("PDF is corrupted or unreadable.")

        try:
            if document.needs_pass:
                raise ValueError("PDF is password-protected and cannot be processed.")

            if document.page_count == 0:
                raise ValueError("PDF contains 0 pages (empty file).")

            try:
                page_texts = [page.get_text() for page in document]
            except Exception:
                raise ValueError("PDF is corrupted or unreadable.")
        finally:
            document.close()

        full_text = "\n".join(page_texts)

        base_name = os.path.splitext(os.path.basename(input_pdf))[0]
        extension = ".txt" if output_format == "TXT" else ".md"
        output_file_path = os.path.join(output_folder, base_name + extension)

        if os.path.exists(output_file_path):
            raise ValueError(f"Output file already exists: {output_file_path}")

        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        return output_file_path
