import os
import tempfile
import secrets
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash, jsonify, send_file, session
from flask_babel import Babel, gettext as _
from markupsafe import Markup
from pytz import all_timezones
from tool_descriptions import get_description, get_use_cases
from tools.base64_encode.base64_encode_tool import Base64EncodeTool
from tools.base64_decode.base64_decode_tool import Base64DecodeTool
from tools.qr_code_generator.qr_code_generator_tool import QrCodeGeneratorTool
from tools.number_converter.number_converter_tool import NumberConverterTool
from tools.image_converter.image_converter_tool import ImageConverterTool
from tools.word_counter.word_counter_tool import WordCounterTool
from tools.password_generator.password_generator_tool import PasswordGeneratorTool
from tools.calendar_week.calendar_week_tool import CalendarWeekTool
from tools.image_cropper.image_cropper_tool import ImageCropperTool
from tools.random_number_generator.random_number_generator_tool import RandomNumberGeneratorTool
from tools.audio_converter.audio_converter_tool import AudioConverterTool
from tools.text_to_speech.text_to_speech_tool import TextToSpeechTool
from tools.unix_timestamp.unix_timestamp_tool import UnixTimestampTool
from tools.texte_vergleichen.texte_vergleichen_tool import TexteVergleichenTool
from tools.json_validieren.json_validieren_tool import JSONValidierungTool
from tools.json_formatieren.json_formatieren_tool import JSONFormatierungTool
from tools.unit_converter.unit_converter_tool import UnitConverterTool
from tools.date_calculator.date_calculator_tool import DateCalculatorTool
from tools.placeholder_text.placeholder_text_tool import PlaceholderTextTool
from tools.color_converter.color_converter_tool import ColorConverterTool
from tools.timezone_converter.timezone_converter_tool import TimezoneConverterTool
from tools.gif_video_converter.gif_video_converter_tool import GifVideoConverterTool
from tools.whisper_subtitle.whisper_subtitle_tool import WhisperSubtitleTool
from tools.pdf_split.pdf_split_tool import PdfSplitTool
from tools.text_summary.text_summary_tool import TextSummaryTool
from tools.pdf_merge.pdf_merge_tool import PdfMergeTool
from tools.file_size_converter.file_size_converter_tool import FileSizeConverterTool
from tools.ocr_scanner.ocr_scanner_tool import OcrScannerTool
from tools.video_image_converter.video_image_converter_tool import VideoImageConverterTool


# Erstellen einer Flask-Anwendung
app = Flask(__name__)

# Festlegen eines geheimen Schlüssels für die Anwendung.
# Dieser Schlüssel wird für die Sitzungsverwaltung und andere sicherheitsrelevante Funktionen verwendet.
# Verwendet Umgebungsvariable oder generiert sicheren zufälligen Schlüssel
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# Sicherheitseinstellungen für File-Uploads
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB Default-Limit für große Dateien
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Erlaubte Dateierweiterungen für verschiedene Tool-Typen
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
    'audio': {'mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'},
    'pdf': {'pdf'},
    'text': {'txt', 'json', 'csv', 'xml'}
}

# Spezifische Upload-Limits für verschiedene Tools (in MB)
TOOL_UPLOAD_LIMITS = {
    'WhisperSubtitleTool': 2048,        # 2GB für Audio/Video
    'GifVideoConverterTool': 1024,      # 1GB für Video zu GIF
    'AudioConverterTool': 512,          # 512MB für Audio
    'VideoConverterTool': 2048,         # 2GB für Video
    'ImageConverterTool': 50,           # 50MB für Bilder
    'ImageCropperTool': 50,             # 50MB für Bilder
    'PdfMergeTool': 200,                # 200MB für PDFs
    'PdfSplitTool': 200,                # 200MB für PDFs
    'OcrScannerTool': 100,              # 100MB für OCR
    'default': 100                      # 100MB Standard
}

def allowed_file(filename, file_type='all'):
    """Überprüft, ob eine Datei einen erlaubten Dateityp hat."""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'all':
        all_extensions = set()
        for exts in ALLOWED_EXTENSIONS.values():
            all_extensions.update(exts)
        return extension in all_extensions
    
    return extension in ALLOWED_EXTENSIONS.get(file_type, set())

def check_file_size(file, tool_name):
    """Überprüft, ob eine Datei das spezifische Limit für das Tool überschreitet."""
    if not file:
        return True, ""
    
    # Aktuelle Position speichern
    file.seek(0, 2)  # Zum Ende der Datei
    file_size = file.tell()
    file.seek(0)  # Zurück zum Anfang
    
    # Limit für das spezifische Tool holen
    limit_mb = TOOL_UPLOAD_LIMITS.get(tool_name, TOOL_UPLOAD_LIMITS['default'])
    limit_bytes = limit_mb * 1024 * 1024
    
    if file_size > limit_bytes:
        return False, _("Datei ist zu groß. Maximum für {0}: {1}MB").format(tool_name, limit_mb)
    
    return True, ""


# Sprachauswahl-Funktion
def get_locale():
    # Versuche Sprache aus der Session zu holen (wenn Benutzer manuell gewählt hat)
    if 'language' in request.args:
        session['language'] = request.args.get('language')
    if 'language' in session:
        return session['language']
    # Ansonsten Browser-Einstellungen verwenden
    return request.accept_languages.best_match(['de', 'en'])

# Babel konfigurieren mit neuerer API
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'de'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
babel.init_app(app, locale_selector=get_locale)


# Hier müssen wir nur unsere Tools registrieren
tools = {
    "Base64EncodeTool": Base64EncodeTool(),
    "Base64DecodeTool": Base64DecodeTool(),
    "FileSizeConverterTool": FileSizeConverterTool(),
    "QrCodeGeneratorTool": QrCodeGeneratorTool(),
    "NumberConverterTool": NumberConverterTool(),
    "ImageConverterTool": ImageConverterTool(),
    "WordCounterTool": WordCounterTool(),
    "CalendarWeekTool": CalendarWeekTool(),
    "RandomNumberGeneratorTool": RandomNumberGeneratorTool(),
    "PasswordGeneratorTool": PasswordGeneratorTool(),
    "ImageCropperTool": ImageCropperTool(),
    "AudioConverterTool": AudioConverterTool(),
    "TextToSpeechTool": TextToSpeechTool(),
    "UnixTimestampTool": UnixTimestampTool(),
    "TexteVergleichenTool": TexteVergleichenTool(),
    "JSONValidierungTool": JSONValidierungTool(),
    "JSONFormatierungTool": JSONFormatierungTool(),
    "UnitConverterTool": UnitConverterTool(),
    "DateCalculatorTool": DateCalculatorTool(),
    "PlaceholderTextTool": PlaceholderTextTool(),
    "ColorConverterTool": ColorConverterTool(),
    "WhisperSubtitleTool": WhisperSubtitleTool(),
    "PdfSplitTool": PdfSplitTool(),
    "GifVideoConverterTool": GifVideoConverterTool(),
    "TextSummaryTool": TextSummaryTool(),
    "PdfMergeTool": PdfMergeTool(),
    "TimezoneConverterTool": TimezoneConverterTool(),
    "OcrScannerTool": OcrScannerTool(),
    "VideoImageConverterTool": VideoImageConverterTool(),
}


@app.route('/')
def index():
    tools_classes = []
    for name, tool in tools.items():
        tool.description = get_description(name)
        tool.use_cases = get_use_cases(name)
        tools_classes.append(tool)

        cookie_consent = request.cookies.get('cookie_consent')
        show_ads = cookie_consent == 'accepted'
    return render_template('index.jinja', toolsToRender=tools_classes, show_ads=show_ads)


@app.route("/search_tools", methods=["GET"])
def search_tools():
    query = request.args.get("q", "").lower()
    filtered_tools = []

    for tool_id, tool in tools.items():
        if query in tool.name.lower() or query in tool.description.lower():
            filtered_tools.append({
                "name": tool.name,
                "description": tool.description,
                "identifier": tool.identifier
            })

    return jsonify(filtered_tools)

# /contact


@app.route('/contact')
def contact():
    return render_template('contact.jinja')

#/privacy
@app.route('/privacy')
def privacy():
    return render_template('legal/privacy.jinja')

#/impressum
@app.route('/impressum')
def impressum():
    return render_template('legal/impressum.jinja')

#/agb
@app.route('/agb')
def agb():
    return render_template('legal/agb.jinja')

# Input


@app.route("/tool/<tool_name>")
def tool_form(tool_name):
    tool = tools.get(tool_name)
    if not tool:
        return "Tool not found", 404
    
    # Add description and use cases
    tool.description = get_description(tool_name)
    tool.use_cases = get_use_cases(tool_name)    # Spezielle Behandlung für bestimmte Tools
    if tool_name == "ColorConverterTool":
        return render_template('color_converter.html',
                            tool=tool,
                            description=tool.description,
                            use_cases=tool.use_cases)
    elif tool_name == "GifVideoConverterTool":
        return render_template('gif_video_converter.jinja',
                              tool=tool,
                              description=tool.description,
                              use_cases=tool.use_cases)
    elif tool_name == "ImageCropperTool":
        return render_template('image_cropper.jinja',
                              tool=tool,
                              description=tool.description,
                              use_cases=tool.use_cases)
    elif tool_name == "FileSizeConverterTool":
        return render_template('file_size_converter.jinja',
                              tool=tool,
                              description=tool.description,
                              use_cases=tool.use_cases)

    # Regulärer Ablauf für andere Tools
    return render_template('variable_input_mask.jinja',
                          tool=tool,
                          toolName=tool.name,
                          input_params=tool.input_params,
                          identifier=tool.identifier,
                          description=tool.description,
                          use_cases=tool.use_cases, 
                          pytz_zones=all_timezones)


@app.route("/handle_tool", methods=["POST"])
def handle_tool():
    tool_name = request.form.get('tool_name')
    tool = tools.get(tool_name)

    if not tool:
        return "Tool not found", 404

    input_params = {}

    # Handle file uploads with security validation
    temp_dir = tempfile.gettempdir()

    if request.form.get("tool_name") == "PdfMergeTool":
        uploaded_files = request.files.getlist("pdf_files")
        files_info = []

        for file in uploaded_files:
            if file and file.filename:
                # Sicherheitsvalidierung
                if not allowed_file(file.filename, 'pdf'):
                    return render_template('output.html',
                                           toolName=tool.name,
                                           output_text=_("Nur PDF-Dateien sind erlaubt."),
                                           has_error=True)
                
                # Dateigröße-Überprüfung
                size_ok, size_error = check_file_size(file, tool_name)
                if not size_ok:
                    return render_template('output.html',
                                           toolName=tool.name,
                                           output_text=size_error,
                                           has_error=True)
                
                file_path = os.path.join(temp_dir, file.filename)
                file.save(file_path)
                files_info.append({
                    "file_obj": file,
                    "file_path": file_path,
                    "filename": file.filename
                })

        input_params["pdf_files"] = files_info
        input_params["pdf_order"] = request.form.get("pdf_order", "")

    else:
        for key, file in request.files.items():
            if file and file.filename != '':
                # Dateitypvalidierung basierend auf Tool
                file_type = 'all'  # Standard: alle Dateitypen erlaubt
                
                if 'image' in tool_name.lower():
                    file_type = 'image'
                elif 'audio' in tool_name.lower() or 'whisper' in tool_name.lower():
                    file_type = 'audio'
                elif 'video' in tool_name.lower():
                    file_type = 'video'
                elif 'pdf' in tool_name.lower():
                    file_type = 'pdf'
                
                # Sicherheitsvalidierung
                if not allowed_file(file.filename, file_type):
                    allowed_exts = ', '.join(ALLOWED_EXTENSIONS.get(file_type, ['alle']))
                    return render_template('output.html',
                                           toolName=tool.name,
                                           output_text=_("Dateityp nicht erlaubt. Erlaubte Formate: {0}").format(allowed_exts),
                                           has_error=True)
                
                # Dateigröße-Überprüfung
                size_ok, size_error = check_file_size(file, tool_name)
                if not size_ok:
                    return render_template('output.html',
                                           toolName=tool.name,
                                           output_text=size_error,
                                           has_error=True)
                
                file_path = os.path.join(temp_dir, file.filename)
                file.save(file_path)
                input_params[key] = {
                    "file_obj": file,
                    "file_path": file_path,
                    "filename": file.filename
                }


    # Handle form inputs
    for key, value in request.form.items():
        if key != 'tool_name':
            if value == 'on':
                input_params[key] = True
            else:
                input_params[key] = value

    success = tool.execute_tool(input_params)

    if not success:
        return render_template('output.html',
                               toolName=tool.name,
                               output_text=tool.error_message,
                               has_error=True)

    return render_template('output.html',
                           toolName=tool.name,
                           output_text=tool.output)


@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    privacy_policy = request.form.get('privacy_policy')

    if not name or not email or not message or privacy_policy is None:
        flash("Bitte füllen Sie alle Pflichtfelder aus und stimmen Sie der Datenschutzerklärung zu.", "error")
        return redirect(url_for('contact'))

    print(f"Neue Kontaktanfrage von {name} ({email}, {phone}): {message}")

    flash("Vielen Dank für Ihre Nachricht! Wir werden uns so schnell wie möglich bei Ihnen melden.", "success")
    return redirect(url_for('contact_success'))


@app.route('/contact_success')
def contact_success():
    return render_template('contact_success.jinja')

@app.route('/about')
def about():
    team_members = [
        {
            "name": "Elias Vincent Simon",
            "role": _("Fullstack Entwickler"),
            "specialty": "Python | Flask | UI/UX",
            "image": "img/dummy-user.png"
        },
        {
            "name": "David Thomfohrde",
            "role": _("Fullstack Entwickler"),
            "specialty": "Python | Flask | UI/UX",
            "image": "img/dummy-user.png"
        },
        {
            "name": "Dumitrita Gorgan",
            "role": _("Fullstack Entwickler"),
            "specialty": "Python | Flask | UI/UX",
            "image": "img/dummy-user.png"
        },  
        {
            "name": "Abdullah Diab",
            "role": _("Fullstack Entwickler"),
            "specialty": "Python | Flask | UI/UX",
            "image": "img/dummy-user.png"
        }, 
         {
            "name": "Soufiane Hammagi",
            "role": _("Fullstack Entwickler"),
            "specialty": "Python | Flask | UI/UX",
            "image": "img/dummy-user.png"
        },
        {
            "name": "Ayoub Aalaou",
            "role": _("Fullstack Entwickler"),
            "specialty": "Python | Flask | UI/UX",
            "image": "img/dummy-user.png"
        }
    ]
    return render_template('about.jinja', team_members=team_members)


@app.route('/download/<token>')
def download_converted_image(token):
    image_tool = tools.get("ImageConverterTool")
    if not image_tool:
        return "Tool nicht gefunden", 404

    temp_path = image_tool.convert_and_save(token)
    if not temp_path:
        return "Konvertierung fehlgeschlagen oder Token ungültig", 404

    # Get the original filename from pending_conversions
    filename = image_tool.pending_conversions[token]['filename']

    # Send the file with the original filename
    response = send_file(temp_path, as_attachment=True, download_name=filename)

    # Schedule cleanup after response is sent
    @response.call_on_close
    def cleanup():
        # Mark as downloaded and cleanup
        image_tool.pending_conversions[token]['downloaded'] = True
        image_tool.cleanup_old_files()

    return response


@app.route('/download_crop/<token>')
def download_cropped_image(token):
    image_tool = tools.get("ImageCropperTool")
    if not image_tool:
        return "Tool nicht gefunden", 404

    temp_path = image_tool.crop_and_save(token)
    if not temp_path:
        return "Zuschneiden fehlgeschlagen oder Token ungültig", 404

    # Get the original filename from pending_crops
    filename = image_tool.pending_crops[token]['filename']

    # Send the file with the original filename
    response = send_file(temp_path, as_attachment=True,
                         download_name=f"cropped_{filename}")

    # Schedule cleanup after response is sent
    @response.call_on_close
    def cleanup():
        # Mark as downloaded and cleanup
        image_tool.pending_crops[token]['downloaded'] = True
        image_tool.cleanup_old_files()

    return response


@app.route('/download_audio/<token>')
def download_converted_audio(token):
    audio_tool = tools.get("AudioConverterTool")
    if not audio_tool:
        print("Error: AudioConverterTool not found")
        return "Tool nicht gefunden", 404

    # Check if the conversion exists
    if token not in audio_tool.pending_conversions:
        print(f"Error: Invalid or expired download token: {token}")
        return "Ungültiger oder abgelaufener Download-Token", 404

    try:
        # Convert the audio file
        temp_path = audio_tool.convert_and_save(token)
        if not temp_path:
            print(f"Error: Failed to convert audio file for token: {token}")
            return "Konvertierung fehlgeschlagen", 500

        if not os.path.exists(temp_path):
            print(f"Error: Converted file not found at: {temp_path}")
            return "Konvertierte Datei nicht gefunden", 404

        # Get file info
        conversion = audio_tool.pending_conversions[token]
        filename = conversion['filename']
        target_format = conversion['target_format']

        # Set the correct content type based on the target format
        content_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'aac': 'audio/mp4',  # Changed from audio/aac to audio/mp4 for .m4a files
            'flac': 'audio/flac'
        }
        content_type = content_types.get(
            target_format, 'application/octet-stream')

        # Verify file size
        file_size = os.path.getsize(temp_path)
        if file_size == 0:
            print(f"Error: Converted file is empty: {temp_path}")
            return "Konvertierte Datei ist leer", 500

        print(f"Sending file: {filename} ({content_type}, {file_size} bytes)")

        # Send the file with the correct content type and filename
        response = send_file(
            temp_path,
            as_attachment=True,
            download_name=filename,
            mimetype=content_type
        )

        # Schedule cleanup after response is sent
        @response.call_on_close
        def cleanup():
            try:
                # Mark as downloaded and cleanup
                audio_tool.pending_conversions[token]['downloaded'] = True
                audio_tool.cleanup_old_files()
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")

        return response

    except Exception as e:
        print(f"Error in download_converted_audio: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return "Fehler beim Senden der Datei", 500


@app.route('/download_converted_media/<token>', methods=['GET', 'POST'])
def download_converted_media(token):
    converter_tool = tools.get("GifVideoConverterTool")
    if not converter_tool:
        return "Tool nicht gefunden", 404

    temp_path = converter_tool.convert_and_save(token)
    if not temp_path:
        return "Konvertierung fehlgeschlagen oder Token ungültig", 404

    # Original-Dateiname aus pending_conversions abrufen
    conversion = converter_tool.pending_conversions[token]
    is_gif = conversion["is_gif"]

    # Ausgabenamen bestimmen
    if is_gif:
        # GIF zu Video
        format = conversion.get("format", "mp4")
        filename = os.path.splitext(conversion["filename"])[0] + f".{format}"
    else:
        # Video zu GIF
        filename = os.path.splitext(conversion["filename"])[0] + ".gif"

    # Datei mit dem Original-Dateinamen senden
    response = send_file(temp_path, as_attachment=True, download_name=filename)

    # Cleanup nach dem Senden der Antwort planen
    @response.call_on_close
    def cleanup():
        # Als heruntergeladen markieren und aufräumen
        converter_tool.pending_conversions[token]['downloaded'] = True
        converter_tool.cleanup_old_files()

    return response


@app.route('/download_video_image_conversion/<token>', methods=['GET', 'POST'])
def download_video_image_conversion(token):
    converter_tool = tools.get("VideoImageConverterTool")
    if not converter_tool:
        return "Tool nicht gefunden", 404

    temp_path = converter_tool.convert_and_save(token)
    if not temp_path:
        return "Konvertierung fehlgeschlagen oder Token ungültig", 404

    conversion = converter_tool.pending_conversions[token]
    conversion_type = conversion["conversion_type"]

    if conversion_type == "video_to_images":
        filename = os.path.splitext(conversion["filename"])[0] + "_frames.zip"
    else:
        video_format = conversion.get("video_format", "mp4")
        filename = os.path.splitext(conversion["filename"])[0] + f"_video.{video_format}"

    response = send_file(temp_path, as_attachment=True, download_name=filename)

    @response.call_on_close
    def cleanup():
        converter_tool.pending_conversions[token]['downloaded'] = True
        converter_tool.cleanup_old_files()

    return response


@app.route('/download_text/<token>')
def download_extracted_text(token):
    ocr_tool = tools.get("OcrScannerTool")
    if not ocr_tool:
        return "Tool nicht gefunden", 404

    extracted_text = ocr_tool.get_extracted_text(token)
    if not extracted_text:
        return "Text nicht gefunden oder Token ungültig", 404

    # Create a temporary file with the extracted text
    temp_file = os.path.join(ocr_tool.temp_dir, f"extracted_text_{token}.txt")
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(extracted_text)

    # Send the file
    response = send_file(temp_file, 
                         as_attachment=True, 
                         download_name="extracted_text.txt", 
                         mimetype="text/plain")

    # Schedule cleanup
    @response.call_on_close
    def cleanup():
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                ocr_tool.cleanup_old_files()
            except Exception as e:
                print(f"Error cleaning up files: {str(e)}")

    return response

# Error Handler für zu große Dateien
@app.errorhandler(413)
def too_large(e):
    return render_template('output.html',
                          toolName=_("Fehler"),
                          output_text=_("Die hochgeladene Datei ist zu groß. Maximum: 2GB"),
                          has_error=True), 413

# byebye
@app.route('/robots.txt')
def robots():
    return send_from_directory('.', 'robots.txt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Change the port if needed
