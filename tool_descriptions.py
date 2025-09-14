# tool_descriptions.py
# This file contains descriptions for all tools in the application
from flask_babel import lazy_gettext as _

TOOL_DESCRIPTIONS = {
    "FileSizeConverterTool": {
        "description": _("Konvertiert Dateigrößen zwischen verschiedenen Einheiten wie Bytes, KB, MB, GB und TB. Unterstützt sowohl dezimale (SI) als auch binäre (IEC) Einheiten."),
        "use_cases": [_("Umrechnung von Speicherkapazitäten"), _("Vergleich von Dateigrößen in verschiedenen Formaten"), _("Berechnung von Speicheranforderungen")]
    },
    "Base64EncodeTool": {
        "description": _("Konvertiert Text oder Dateien in das Base64-Format. Ideal für die sichere Übertragung von Binärdaten in textbasierten Systemen wie E-Mail oder HTTP."),
        "use_cases": [_("Einbettung von Bildern in HTML/CSS"), _("Codierung binärer Daten für API-Übertragungen"), _("Sichere Übermittlung von Zeichen, die in URLs problematisch sein können")]
    },    "Base64DecodeTool": {
        "description": _("Decodiert Base64-kodierte Daten zurück in ihre ursprüngliche Form (Text oder Binärdaten). Nützlich zum Entschlüsseln von Base64-Inhalten."),
        "use_cases": [_("Extraktion von Daten aus API-Antworten"), _("Wiederherstellen von Binärdateien aus Base64-Text"), _("Analyse kodierter Inhalte")]
    },
    "QrCodeGeneratorTool": {
        "description": _("Erstellt QR-Codes aus Text, URLs oder anderen Daten. Ideal für kontaktlose Informationsübermittlung und schnellen Datenzugriff über mobile Geräte."),
        "use_cases": [_("Erstellung von Kontaktinformationen zum Scannen"), _("Generierung von Website-Links für Print-Materialien"), _("Entwicklung von kontaktlosen Zahlungslösungen")]
    },
    "NumberConverterTool": {
        "description": _("Konvertiert Zahlen zwischen verschiedenen Zahlensystemen (Dezimal, Binär, Hexadezimal, Oktal). Unverzichtbar für Programmierer und IT-Spezialisten."),
        "use_cases": [_("Umrechnung für Programmieraufgaben"), _("Analyse von Speicheradressen"), _("Arbeit mit Farbcodes und anderen hexadezimalen Werten")]
    },
    "ImageConverterTool": {
        "description": _("Wandelt Bilder zwischen verschiedenen Formaten um (JPG, PNG, WebP, etc.) und ermöglicht die Anpassung von Qualität und Größe."),
        "use_cases": [_("Optimierung von Bildern für Websites"), _("Anpassung an spezifische Formatanforderungen"), _("Konvertierung für bessere Kompatibilität")]
    },
    "WordCounterTool": {
        "description": _("Zählt die Anzahl der Wörter in einem Text. Einfaches und schnelles Wortzählwerkzeug."),
        "use_cases": [_("Überprüfung der Wortanzahl für Schreibaufgaben"), _("Einhaltung von Wortbegrenzungen für Aufsätze oder Artikel"), _("Schnelle Wortzahl-Überprüfung")]
    },
    "PasswordGeneratorTool": {
        "description": _("Erstellt sichere, zufällige Passwörter mit anpassbarer Länge und Zeichensatz-Optionen. Erhöht die Sicherheit Ihrer Online-Konten."),
        "use_cases": [_("Generierung sicherer Zugangsdaten"), _("Erstellung von API-Schlüsseln"), _("Verbesserung der Kontosicherheit")]
    },
    "CalendarWeekTool": {
        "description": _("Berechnet Kalenderwochen für beliebige Daten nach ISO-8601 Standard. Hilfreich für Projektplanung und Terminkoordination."),
        "use_cases": [_("Planung nach Kalenderwochen"), _("Berechnung von Projektzeitleisten"), _("Analyse von saisonalen Trends")]
    },
    "ImageCropperTool": {
        "description": _("Ermöglicht präzises Zuschneiden von Bildern durch Auswahl des gewünschten Bereichs. Ideal für Profilbilder oder fokussierte Bildausschnitte."),
        "use_cases": [_("Anpassung von Bildern für soziale Medien"), _("Erstellung einheitlicher Produktbilder"), _("Fokussierung auf relevante Bildbereiche")]
    },
    "RandomNumberGeneratorTool": {
        "description": _("Erzeugt Zufallszahlen in einem definierbaren Bereich mit Optionen für Duplikate und Sortierung. Perfekt für Auslosungen und statistische Zwecke."),
        "use_cases": [_("Durchführung von Verlosungen"), _("Erstellung von Test-Datensätzen"), _("Simulation von Zufallsprozessen")]
    },
    "AudioConverterTool": {
        "description": _("Konvertiert Audiodateien zwischen verschiedenen Formaten (MP3, WAV, AAC, FLAC) unter Beibehaltung der Audioqualität."),
        "use_cases": [_("Anpassung an Gerätekompatibilität"), _("Optimierung der Dateigröße"), _("Vorbereitung von Audio für verschiedene Plattformen")]
    },
    "TextToSpeechTool": {
        "description": _("Wandelt geschriebenen Text in natürlich klingende Sprache um. Unterstützt verschiedene Sprachen und Stimmoptionen."),
        "use_cases": [_("Erstellung von Audio-Content"), _("Barrierefreiheit für sehbehinderte Nutzer"), _("Entwicklung von Sprachassistenten")]
    },
    "UnixTimestampTool": {
        "description": _("Konvertiert zwischen menschenlesbaren Datumsformaten und Unix-Zeitstempeln. Essentiell für Entwickler und Systemadministratoren."),
        "use_cases": [_("Fehlersuche in Logs"), _("Zeitberechnung in Anwendungen"), _("Planung von zeitgesteuerten Aufgaben")]
    },
    "TexteVergleichenTool": {
        "description": _("Vergleicht zwei Texte und hebt Unterschiede hervor. Ideal für die Überprüfung von Änderungen in Dokumenten oder Code."),
        "use_cases": [_("Vergleich von Vertragsentwürfen"), _("Identifikation von Änderungen in Texten"), _("Code-Review und Dokumentenprüfung")]
    },
    "JSONValidierungTool": {
        "description": _("Überprüft JSON-Daten auf syntaktische Korrektheit und Validität. Hilfreich für Entwickler bei der Arbeit mit APIs und Datenaustausch."),
        "use_cases": [_("Validierung von API-Antworten"), _("Fehlersuche in JSON-Daten"), _("Test von Datenstrukturen")]
    },
    "JSONFormatierungTool": {
        "description": _("Formatiert JSON-Daten für bessere Lesbarkeit mit Einrückungen und strukturierter Darstellung. Erleichtert die Analyse komplexer Datenstrukturen."),
        "use_cases": [_("Übersichtliche Darstellung von API-Antworten"), _("Vorbereitung von JSON für Dokumentation"), _("Verbesserung der Lesbarkeit von Konfigurationsdateien")]
    },
    "UnitConverterTool": {
        "description": _("Wandelt Werte zwischen verschiedenen Maßeinheiten um (Länge, Gewicht, Temperatur, etc.). Präzise und zuverlässige Konvertierungen für alltägliche und technische Anwendungen."),
        "use_cases": [_("Umrechnung für internationale Projekte"), _("Wissenschaftliche Berechnungen"), _("Anpassung von Rezepten und Anleitungen")]
    },
    "DateCalculatorTool": {
        "description": _("Berechnet Zeiträume zwischen Daten oder addiert/subtrahiert Tage zu einem Datum. Perfekt für Projekt- und Eventplanung."),
        "use_cases": [_("Berechnung von Projektlaufzeiten"), _("Planung von Terminen und Fristen"), _("Analyse von Zeiträumen")]
    },
    "PlaceholderTextTool": {
        "description": _("Generiert Platzhaltertext (Lorem Ipsum) für Design- und Layoutzwecke. Ideal für die Gestaltung von Webseiten, Dokumenten und Präsentationen."),
        "use_cases": [_("Vorschau von Webseitenlayouts"), _("Gestaltung von Druckmaterialien"), _("Erstellung von Design-Mockups")]
    },
    "ColorConverterTool": {
        "description": _("Konvertiert Farben zwischen verschiedenen Formaten wie HEX, RGB, HSL und HSV mit interaktiver Vorschau. Ideal für Web-Entwicklung und Design."),
        "use_cases": [_("Anpassung von Farbwerten für CSS"), _("Erstellung konsistenter Farbpaletten"), _("Umwandlung zwischen verschiedenen Farbnotationen")]
    },
    "GifVideoConverterTool": {
        "description": _("Konvertiert zwischen GIF-Animationen und Videoformaten. Ermöglicht die Optimierung von animierten Inhalten für verschiedene Plattformen."),
        "use_cases": [_("Erstellung von GIFs aus Videos für soziale Medien"), _("Umwandlung von GIFs in Videos für bessere Qualität"), _("Optimierung von Animationen für Web")]
    },
    "WhisperSubtitleTool": {
        "description": _("Generiert automatisch Untertitel für Videos mithilfe von KI-basierter Spracherkennung. Verbessert die Zugänglichkeit und Nutzererfahrung von Videocontent."),
        "use_cases": [_("Erstellung barrierefreier Videos"), _("Übersetzung von Videoinhalten"), _("Verbesserung der SEO für Videokanäle")]
    },
    "PdfSplitTool": {
        "description": _("Teilt PDF-Dokumente in einzelne Seiten oder Abschnitte. Ideal für die Extraktion spezifischer Informationen aus umfangreichen Dokumenten."),
        "use_cases": [_("Aufteilung von großen Berichten"), _("Extraktion relevanter Seiten"), _("Organisation von Dokumenten nach Themen")]
    },
    "PdfMergeTool": {
        "description": _("Kombiniert mehrere PDF-Dateien zu einem einzigen Dokument. Perfekt für die Erstellung umfassender Berichte oder die Zusammenführung verwandter Dokumente."),
        "use_cases": [_("Zusammenstellung von Unterlagen"), _("Erstellung von Handbüchern aus Einzeldokumenten"), _("Organisation von digitalem Papierkram")]
    },
    "OcrScannerTool": {
        "description": _("Analysiert und verbessert Bilder, um Text zu erkennen. Die optimierte Bildverarbeitung identifiziert Textbereiche und extrahiert Inhalte, ohne zusätzliche Software zu benötigen. Unterstützt Formate wie PNG, JPG, BMP und TIFF."),
        "use_cases": [_("Digitalisierung von gedruckten Dokumenten"), _("Identifizierung von Textbereichen in Bildern"), _("Bildoptimierung für bessere Lesbarkeit von Texten")]
    },    "TextSummaryTool": {
        "description": _("Fasst Text mithilfe von Sprachmodellen (LLMs) zusammen"),
        "use_cases": [_("Zusammenfassung von Text"), _("Verstehen von komplexen Texten")]
    },
    "TimezoneConverterTool": {
        "description": _("Konvertiert Datum und Uhrzeit zwischen verschiedenen Zeitzonen weltweit. Berücksichtigt automatisch Sommerzeit und andere zeitzonespezifische Regeln für präzise Umrechnungen."),
        "use_cases": [_("Planung internationaler Meetings und Anrufe"), _("Koordination globaler Projekte"), _("Umrechnung für Reiseplanung und Flugzeiten"), _("Synchronisation weltweiter Events")]
    },
    "VideoImageConverterTool": {
        "description": _("Konvertiert Videos in Bildsequenzen (ZIP-Archiv) und Bildsequenzen zurück in Videos. Ideal für die Bearbeitung von Video-Frames und die Erstellung von Videos aus Bildserien."),
        "use_cases": [_("Extraktion von Video-Frames für Bildbearbeitung"), _("Erstellung von Stop-Motion-Videos aus Bildern"), _("Analyse von Videoinhalten Frame für Frame"), _("Umwandlung von Bildserien in Videos")]
    }
}


def get_description(tool_name):
    """Returns the description for a given tool name"""
    tool_info = TOOL_DESCRIPTIONS.get(tool_name, {})
    return tool_info.get("description", _("Keine Beschreibung verfügbar."))


def get_use_cases(tool_name):
    """Returns the use cases for a given tool name"""
    tool_info = TOOL_DESCRIPTIONS.get(tool_name, {})
    return tool_info.get("use_cases", [])
