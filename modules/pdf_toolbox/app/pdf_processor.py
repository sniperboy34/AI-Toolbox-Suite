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
        document = fitz.open(input_pdf)

        try:
            page_texts = [page.get_text() for page in document]
        finally:
            document.close()

        full_text = "\n".join(page_texts)

        base_name = os.path.splitext(os.path.basename(input_pdf))[0]
        extension = ".txt" if output_format == "TXT" else ".md"
        output_file_path = os.path.join(output_folder, base_name + extension)

        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        return output_file_path
