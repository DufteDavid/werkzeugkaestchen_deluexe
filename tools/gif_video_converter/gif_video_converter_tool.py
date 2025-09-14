import os
import uuid
import tempfile
from datetime import datetime, timedelta
from flask_babel import lazy_gettext as _
import ffmpeg
from tool_interface import MiniTool, OutputType


class GifVideoConverterTool(MiniTool):
    def __init__(self):
        super().__init__(_("GIF/Video Konverter"), "GifVideoConverterTool", OutputType.TEXT)
        self.description = _("Konvertiert Videos in GIFs und umgekehrt")
        self.input_params = {
            "file": "file"
        }

        # Extract translatable strings for HTML
        self.started_header = _("Konvertierung gestartet!")
        self.gif_to_video = _("GIF zu Video")
        self.video_to_gif = _("Video zu GIF")
        self.conversion_started_text = _("Ihre {0} Konvertierung wurde erfolgreich gestartet. Bitte klicken Sie auf den Button unten, um die Datei herunterzuladen.")
        self.download_button = _("Konvertierte Datei herunterladen")
        self.new_conversion_button = _("Neue Konvertierung starten")

        # Dictionary für die Verwaltung der Konvertierungen
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

            # Prüfe Dateigröße (max 1GB)
            if os.path.getsize(file_path) > 1024 * 1024 * 1024:  # 1GB in Bytes
                self.error_message = _("Die Datei ist zu groß. Maximale Größe ist 1GB.")
                return False

            # Bestimme Dateityp (GIF oder Video)
            is_gif = filename.lower().endswith('.gif')

            # Konvertierungsparameter aus den Eingaben
            quality = input_params.get("quality", "medium")
            fps = input_params.get("fps", "10")
            # Loop-Count nur für Video -> GIF (0 = unendlich)
            loop = input_params.get("loop", "0")

            # Initialisiere Variablen
            resize = None
            format = None

            if not is_gif:
                # Für Video zu GIF
                resize = input_params.get("resize", "none")
            else:
                # Für GIF zu Video
                format = input_params.get("format", "mp4")

            # Erstelle ein eindeutiges Token für diese Konvertierung
            token = str(uuid.uuid4())

            # Speichere die Konvertierungsinformationen
            self.pending_conversions[token] = {
                "file_path": file_path,
                "is_gif": is_gif,
                "filename": filename,
                "quality": quality,
                "fps": fps,
                "resize": resize if not is_gif else None,
                "format": format if is_gif else None,
                "loop": loop if not is_gif else None,
                "timestamp": datetime.now(),
                "downloaded": False
            }

            # HTML-Ausgabe mit Download-Link
            self.output = self._create_output_html(token, is_gif)
            return True

        except Exception as e:
            self.error_message = _("Fehler bei der Verarbeitung:") + f" {str(e)}"
            return False

    def _create_output_html(self, token, is_gif):
        """Erstellt das HTML für die Erfolgsanzeige"""
        conversion_type = self.gif_to_video if is_gif else self.video_to_gif
        return f"""
        <div class="alert alert-success">
            <h4 class="alert-heading">{self.started_header}</h4>
            <p>{self.conversion_started_text.format(conversion_type)}</p>
            <hr>
            <div class="d-flex justify-content-between">
                <a href="/download_converted_media/{token}" class="btn btn-primary" download>
                    <i class="fas fa-download"></i> {self.download_button}
                </a>
                <a href="/tool/GifVideoConverterTool" class="btn btn-secondary">
                    <i class="fas fa-redo"></i> {self.new_conversion_button}
                </a>
            </div>
        </div>
        """

    def convert_and_save(self, token):
        """Führt die eigentliche Konvertierung durch und gibt den Pfad zur konvertierten Datei zurück"""
        if token not in self.pending_conversions:
            return None

        conversion = self.pending_conversions[token]
        if conversion["downloaded"]:
            return None

        try:
            input_path = conversion["file_path"]
            is_gif = conversion["is_gif"]

            # Bestimme Ausgabedateipfad und -format
            if is_gif:
                # GIF zu Video
                format = conversion.get("format", "mp4")
                output_path = os.path.join(self.temp_dir, f"converted_{token}.{format}")
                output_path = output_path.replace('\\', '/')  # Normalize path for tests

                # Qualitätseinstellungen
                quality_settings = {
                    "low": {"crf": "28", "preset": "ultrafast"},
                    "medium": {"crf": "23", "preset": "medium"},
                    "high": {"crf": "18", "preset": "slow"}
                }
                quality = conversion.get("quality", "medium")
                settings = quality_settings[quality]

                # FFmpeg-Befehl für GIF zu Video
                stream = ffmpeg.input(input_path)
                stream = ffmpeg.output(
                    stream,
                    output_path,
                    vcodec='libx264',
                    pix_fmt='yuv420p',
                    crf=settings["crf"],
                    preset=settings["preset"]
                )
                ffmpeg.run(stream, overwrite_output=True, quiet=True)

            else:
                # Video zu GIF
                output_path = os.path.join(self.temp_dir, f"converted_{token}.gif")
                output_path = output_path.replace('\\', '/')  # Normalize path for tests

                # Qualitäts- und FPS-Einstellungen
                fps = int(conversion.get("fps", 10))

                # Größenanpassung
                resize_options = {
                    "none": "iw:-1",
                    "small": "320:-1",
                    "medium": "480:-1",
                    "large": "640:-1"
                }
                resize = conversion.get("resize", "none")
                scale = resize_options[resize]

                # Qualitätseinstellungen für GIF
                quality_dither = {
                    "low": "0",
                    "medium": "2",
                    "high": "4"
                }
                quality = conversion.get("quality", "medium")
                dither = quality_dither[quality]

                # Loop-Parameter für GIF (0 = unendlich)
                loop = int(conversion.get("loop", 0))

                # FFmpeg-Befehl für Video zu GIF
                stream = ffmpeg.input(input_path)
                stream = ffmpeg.output(
                    stream,
                    output_path,
                    vf=f"fps={fps},scale={scale}:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=diff[p];[s1][p]paletteuse=dither={dither}",
                    loop=loop
                )
                ffmpeg.run(stream, overwrite_output=True, quiet=True)

            return output_path

        except Exception as e:
            print(f"Fehler bei der Konvertierung: {str(e)}")
            return None

    def cleanup_old_files(self):
        """Entfernt alte Konvertierungen und Dateien"""
        now = datetime.now()
        tokens_to_remove = []

        for token, conversion in self.pending_conversions.items():
            # Entferne Konvertierungen, die älter als 1 Stunde sind oder bereits heruntergeladen wurden
            if (now - conversion["timestamp"] > timedelta(hours=1) or
                    conversion["downloaded"]):
                # Versuche, die temporären Dateien zu entfernen
                try:
                    if os.path.exists(conversion["file_path"]):
                        os.remove(conversion["file_path"])

                    # Bestimme den Pfad der konvertierten Datei
                    if conversion["is_gif"]:
                        format = conversion.get("format", "mp4")
                        converted_path = os.path.join(
                            self.temp_dir,
                            f"converted_{token}.{format}"
                        )
                    else:
                        converted_path = os.path.join(
                            self.temp_dir,
                            f"converted_{token}.gif"
                        )
                    converted_path = converted_path.replace('\\', '/')  # Normalize path for tests

                    if os.path.exists(converted_path):
                        os.remove(converted_path)
                except Exception as e:
                    print(f"Fehler beim Aufräumen von Dateien: {str(e)}")

                tokens_to_remove.append(token)

        # Entferne die verarbeiteten Tokens
        for token in tokens_to_remove:
            self.pending_conversions.pop(token, None)
