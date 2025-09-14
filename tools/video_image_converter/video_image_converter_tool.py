import os
import uuid
import tempfile
import zipfile
from datetime import datetime, timedelta
from flask_babel import lazy_gettext as _
import ffmpeg
from PIL import Image
from tool_interface import MiniTool, OutputType


class VideoImageConverterTool(MiniTool):
    def __init__(self):
        super().__init__(_("Video/Bild Konverter"), "VideoImageConverterTool", OutputType.TEXT)
        self.description = _("Konvertiert Videos in Bildsequenzen (ZIP) und Bildsequenzen in Videos")
        self.input_params = {
            "file": "file",
            "conversion_type": "string"
        }
        
        self.started_header = _("Konvertierung gestartet!")
        self.video_to_images = _("Video zu Bildern")
        self.images_to_video = _("Bilder zu Video")
        self.conversion_started_text = _("Ihre {0} Konvertierung wurde erfolgreich gestartet. Bitte klicken Sie auf den Button unten, um die Datei herunterzuladen.")
        self.download_button = _("Konvertierte Datei herunterladen")
        self.new_conversion_button = _("Neue Konvertierung starten")
        
        self.pending_conversions = {}
        self.temp_dir = tempfile.gettempdir()

    def execute_tool(self, input_params: dict) -> bool:
        try:
            if "file" not in input_params:
                self.error_message = _("Bitte wählen Sie eine Datei aus.")
                return False

            file_info = input_params["file"]
            file_path = file_info["file_path"]
            filename = file_info["filename"]
            conversion_type = input_params.get("conversion_type", "video_to_images")

            if os.path.getsize(file_path) > 2 * 1024 * 1024 * 1024:  # 2GB limit
                self.error_message = _("Die Datei ist zu groß. Maximale Größe ist 2GB.")
                return False

            if conversion_type == "video_to_images":
                if not self._is_video_file(filename):
                    self.error_message = _("Bitte wählen Sie eine Videodatei aus.")
                    return False
            elif conversion_type == "images_to_video":
                if not self._is_zip_file(filename):
                    self.error_message = _("Bitte wählen Sie eine ZIP-Datei mit Bildern aus.")
                    return False

            token = str(uuid.uuid4())
            
            fps = input_params.get("fps", "10")
            quality = input_params.get("quality", "medium")
            image_format = input_params.get("image_format", "png")
            video_format = input_params.get("video_format", "mp4")

            self.pending_conversions[token] = {
                "file_path": file_path,
                "filename": filename,
                "conversion_type": conversion_type,
                "fps": fps,
                "quality": quality,
                "image_format": image_format,
                "video_format": video_format,
                "timestamp": datetime.now(),
                "downloaded": False
            }

            conversion_type_display = self.video_to_images if conversion_type == "video_to_images" else self.images_to_video
            self.output = self._create_output_html(token, conversion_type_display)
            return True

        except Exception as e:
            self.error_message = _("Fehler bei der Verarbeitung:") + f" {str(e)}"
            return False

    def _is_video_file(self, filename):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
        return any(filename.lower().endswith(ext) for ext in video_extensions)

    def _is_zip_file(self, filename):
        return filename.lower().endswith('.zip')

    def _create_output_html(self, token, conversion_type):
        return f"""
        <div class="alert alert-success">
            <h4 class="alert-heading">{self.started_header}</h4>
            <p>{self.conversion_started_text.format(conversion_type)}</p>
            <hr>
            <div class="d-flex justify-content-between">
                <a href="/download_video_image_conversion/{token}" class="btn btn-primary" download>
                    <i class="fas fa-download"></i> {self.download_button}
                </a>
                <a href="/tool/VideoImageConverterTool" class="btn btn-secondary">
                    <i class="fas fa-redo"></i> {self.new_conversion_button}
                </a>
            </div>
        </div>
        """

    def convert_and_save(self, token):
        if token not in self.pending_conversions:
            return None

        conversion = self.pending_conversions[token]
        if conversion["downloaded"]:
            return None

        try:
            if conversion["conversion_type"] == "video_to_images":
                return self._video_to_images(token, conversion)
            else:
                return self._images_to_video(token, conversion)

        except Exception as e:
            print(f"Fehler bei der Konvertierung: {str(e)}")
            return None

    def _video_to_images(self, token, conversion):
        input_path = conversion["file_path"]
        fps = int(conversion.get("fps", 10))
        image_format = conversion.get("image_format", "png")
        
        temp_image_dir = os.path.join(self.temp_dir, f"images_{token}")
        os.makedirs(temp_image_dir, exist_ok=True)
        
        image_pattern = os.path.join(temp_image_dir, f"frame_%04d.{image_format}")
        
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(
            stream,
            image_pattern,
            vf=f"fps={fps}",
            format="image2"
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        zip_path = os.path.join(self.temp_dir, f"images_{token}.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image_file in os.listdir(temp_image_dir):
                if image_file.endswith(f".{image_format}"):
                    image_path = os.path.join(temp_image_dir, image_file)
                    zipf.write(image_path, image_file)
        
        for image_file in os.listdir(temp_image_dir):
            os.remove(os.path.join(temp_image_dir, image_file))
        os.rmdir(temp_image_dir)
        
        return zip_path

    def _images_to_video(self, token, conversion):
        input_path = conversion["file_path"]
        fps = int(conversion.get("fps", 10))
        video_format = conversion.get("video_format", "mp4")
        quality = conversion.get("quality", "medium")
        
        temp_image_dir = os.path.join(self.temp_dir, f"extracted_{token}")
        os.makedirs(temp_image_dir, exist_ok=True)
        
        with zipfile.ZipFile(input_path, 'r') as zipf:
            image_files = []
            for file_info in zipf.filelist:
                if self._is_image_file(file_info.filename):
                    zipf.extract(file_info, temp_image_dir)
                    image_files.append(file_info.filename)
        
        if not image_files:
            raise Exception("Keine Bilddateien in der ZIP-Datei gefunden")
        
        image_files.sort()
        
        first_image_path = os.path.join(temp_image_dir, image_files[0])
        with Image.open(first_image_path) as img:
            width, height = img.size
        
        for i, image_file in enumerate(image_files):
            old_path = os.path.join(temp_image_dir, image_file)
            new_path = os.path.join(temp_image_dir, f"frame_{i:04d}.png")
            
            with Image.open(old_path) as img:
                if img.size != (width, height):
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                img = img.convert("RGB")
                img.save(new_path, "PNG")
            
            if old_path != new_path:
                os.remove(old_path)
        
        output_path = os.path.join(self.temp_dir, f"video_{token}.{video_format}")
        
        quality_settings = {
            "low": {"crf": "28", "preset": "ultrafast"},
            "medium": {"crf": "23", "preset": "medium"},
            "high": {"crf": "18", "preset": "slow"}
        }
        settings = quality_settings[quality]
        
        pattern = os.path.join(temp_image_dir, "frame_%04d.png")
        stream = ffmpeg.input(pattern, framerate=fps)
        stream = ffmpeg.output(
            stream,
            output_path,
            vcodec='libx264',
            pix_fmt='yuv420p',
            crf=settings["crf"],
            preset=settings["preset"]
        )
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        for file in os.listdir(temp_image_dir):
            os.remove(os.path.join(temp_image_dir, file))
        os.rmdir(temp_image_dir)
        
        return output_path

    def _is_image_file(self, filename):
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff']
        return any(filename.lower().endswith(ext) for ext in image_extensions)

    def cleanup_old_files(self):
        now = datetime.now()
        tokens_to_remove = []

        for token, conversion in self.pending_conversions.items():
            if (now - conversion["timestamp"] > timedelta(hours=1) or
                    conversion["downloaded"]):
                try:
                    if os.path.exists(conversion["file_path"]):
                        os.remove(conversion["file_path"])

                    if conversion["conversion_type"] == "video_to_images":
                        zip_path = os.path.join(self.temp_dir, f"images_{token}.zip")
                        if os.path.exists(zip_path):
                            os.remove(zip_path)
                    else:
                        video_format = conversion.get("video_format", "mp4")
                        output_path = os.path.join(self.temp_dir, f"video_{token}.{video_format}")
                        if os.path.exists(output_path):
                            os.remove(output_path)

                except Exception as e:
                    print(f"Fehler beim Aufräumen von Dateien: {str(e)}")

                tokens_to_remove.append(token)

        for token in tokens_to_remove:
            self.pending_conversions.pop(token, None)