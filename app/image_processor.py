import os

from PIL import Image


class ImageProcessor:
    def __init__(self):
        self.selected_files = []
        self.output_folder = ""
        self.width = None
        self.height = None
        self.output_format = "JPG"
        self.keep_aspect_ratio = False
        self.quality = 95

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

    def set_keep_aspect_ratio(self, keep_aspect_ratio):
        self.keep_aspect_ratio = bool(keep_aspect_ratio)

    def get_keep_aspect_ratio(self):
        return self.keep_aspect_ratio

    def set_quality(self, quality):
        self.quality = int(quality)

    def get_quality(self):
        return self.quality

    def resize_image(self, image_path):
        tmp_path = None

        try:
            if not self.output_folder:
                return False

            if not self.width or not self.height:
                return False

            # Fully load the source image into memory, then detach the
            # resized result from it with .copy() before closing the file.
            # This guarantees the image we save no longer shares any
            # reference (pixel buffer, palette, file handle) with the
            # source file, so saving to a path that overlaps the source
            # (e.g. same input/output folder) can no longer corrupt it.
            image = Image.open(image_path)
            try:
                image.load()

                if self.keep_aspect_ratio:
                    # Fit the image within the requested width/height box
                    # without distorting it: scale by the smaller of the
                    # two ratios so neither dimension exceeds the target.
                    original_width, original_height = image.size
                    ratio = min(
                        self.width / original_width,
                        self.height / original_height
                    )
                    target_size = (
                        max(1, round(original_width * ratio)),
                        max(1, round(original_height * ratio))
                    )
                else:
                    target_size = (self.width, self.height)

                resized_image = image.resize(target_size).copy()
            finally:
                image.close()

            filename = os.path.splitext(
                os.path.basename(image_path)
            )[0]

            extension = self.output_format.lower()

            output_path = os.path.join(
                self.output_folder,
                f"{filename}.{extension}"
            )

            # Avoid overwriting an existing file in the output folder:
            # if the target name is already taken, append " (1)", " (2)",
            # etc. until an unused name is found.
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(
                    self.output_folder,
                    f"{filename} ({counter}).{extension}"
                )
                counter += 1

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

            # Write to a temporary file first, then atomically move it
            # into place. If saving fails or is interrupted partway
            # through, the half-written data lands only in tmp_path and
            # output_path is never touched with bad bytes - so a failed
            # save can never leave a corrupted file where the finished
            # image is expected. os.replace() is atomic on both Windows
            # and POSIX, so output_path always contains either the old
            # file or a fully-written new one, never a partial one.
            save_format = (
                "JPEG" if self.output_format == "JPG"
                else self.output_format
            )

            tmp_path = output_path + ".tmp"

            save_kwargs = {"format": save_format}

            # Quality only applies to JPEG and WEBP; PNG is lossless and
            # has no "quality" concept, so the setting is ignored for it.
            if save_format in ("JPEG", "WEBP"):
                save_kwargs["quality"] = self.quality

            resized_image.save(tmp_path, **save_kwargs)
            resized_image.close()

            os.replace(tmp_path, output_path)
            tmp_path = None

            return output_path

        except Exception:
            return False

        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
