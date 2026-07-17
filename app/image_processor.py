import os

from PIL import Image


class ImageProcessor:
    def __init__(self):
        self.selected_files = []
        self.output_folder = ""
        self.width = None
        self.height = None
        self.output_format = "JPG"

    def set_selected_files(self, files):
        self.selected_files = list(files)

    def get_selected_files(self):
        return self.selected_files

    def set_output_folder(self, folder):
        self.output_folder = folder

    def get_output_folder(self):
        return self.output_folder

    def set_resize_values(self, width, height):
        width = width.strip()
        height = height.strip()

        if not width.isdigit() or not height.isdigit():
            return False

        self.width = int(width)
        self.height = int(height)
        return True

    def get_resize_values(self):
        return self.width, self.height

    def set_output_format(self, file_format):
        self.output_format = file_format.upper()

    def get_output_format(self):
        return self.output_format

    def resize_image(self, image_path):
        try:
            if not self.output_folder:
                return False

            if not self.width or not self.height:
                return False

            image = Image.open(image_path)

            resized_image = image.resize(
                (self.width, self.height)
            )

            filename = os.path.splitext(
                os.path.basename(image_path)
            )[0]

            output_path = os.path.join(
                self.output_folder,
                f"{filename}.{self.output_format.lower()}"
            )

            if self.output_format == "JPG":
                if resized_image.mode in ("RGBA", "LA"):
                    background = Image.new(
                        "RGB",
                        resized_image.size,
                        "white"
                    )
                    background.paste(
                        resized_image,
                        mask=resized_image.split()[-1]
                    )
                    resized_image = background
                else:
                    resized_image = resized_image.convert("RGB")

            resized_image.save(output_path)

            return output_path

        except Exception:
            return False
