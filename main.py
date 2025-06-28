"""
TT Tool

Author: xqi

Requirements:
pip install colorama pyttsx3

sudo pacman -S espeak-ng festival festival-de  # Backend for pyttsx3
# festival-de provides high-quality German voices
# Optional: sudo pacman -S festival-english for English voices
"""
import shutil
import os
import threading
from random import randint
from typing import Dict, List
import pyttsx3
import colorama


# Initialize colorama
colorama.init()


# -----------------------------------------------------------------------------
# PYTTSX3 TTS SYSTEM
# -----------------------------------------------------------------------------
class ArchTTS:
    """TTS System using pyttsx3"""

    def __init__(self):
        self.tts_engine = None
        self.available_voices = []
        self.current_voice_id = None
        self.is_initialized = False
        self.settings = {
            "rate": 160,  # words per minute
            "volume": 0.8,  # 0.0 to 1.0
            "voice": "auto"  # set first available voice
        }
        self.initialize_engine()

    def initialize_engine(self):
        """Initialize pyttsx3 TTS engine"""
        try:
            self.tts_engine = pyttsx3.init()
            self.is_initialized = True

            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.available_voices = voices

                selected_voice = self._select_best_voice(voices)
                if selected_voice:
                    self.current_voice_id = selected_voice.id
                    self.settings["voice"] = selected_voice.name
                else:
                    self.current_voice_id = voices[0].id
                    self.settings["voice"] = voices[0].name

                self.tts_engine.setProperty('voice', self.current_voice_id)

            # Set initial properties
            self.tts_engine.setProperty('rate', self.settings["rate"])
            self.tts_engine.setProperty('volume', self.settings["volume"])

            #print("pyttsx3 TTS Engine initialisiert")
            if self.current_voice_id:
                voice_info = self.settings["voice"]
                if "festival" in self.current_voice_id.lower() and "de" in self.current_voice_id.lower():
                    voice_info += " (festival-de)"
                #print(f"Stimme: {voice_info}")

        except Exception as e:
            print(f"Fehler beim Initialisieren der TTS Engine: {e}")
            print("Stelle sicher, dass TTS Backends installiert sind: sudo pacman -S espeak-ng festival festival-de")
            self.is_initialized = False

    def speak_text(self, text: str) -> bool:
        """Main TTS function using pyttsx3"""
        if not self.is_initialized or not self.tts_engine:
            print("TTS Engine nicht verfügbar!")

            return False

        try:
            # Ensure engine is properly configured
            self.tts_engine.setProperty('rate', self.settings["rate"])
            self.tts_engine.setProperty('volume', self.settings["volume"])
            if self.current_voice_id:
                self.tts_engine.setProperty('voice', self.current_voice_id)

            # Speak the text
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

            return True

        except Exception as e:
            print(f"TTS Fehler: {e}")
            return False

    def list_voices(self):
        """Lists all available voices"""
        if not self.available_voices:
            print("Keine Stimmen verfügbar")
            return

        print("Verfügbare Stimmen:")
        print("=" * 50)

        for i, voice in enumerate(self.available_voices):
            is_current = "Aktiv" if voice.id == self.current_voice_id else " "
            voice_type = self._get_voice_type(voice.id.lower())
            # Extract language info if available
            lang_info = ""

            if hasattr(voice, 'languages') and voice.languages:
                lang_info = f" [{', '.join(voice.languages)}]"

            print(f"  {is_current} {i}: {voice.name}{voice_type}{lang_info}")
            print(f"      ID: {voice.id}")

            # Show additional info if available
            if hasattr(voice, 'age'):
                print(f"      Age: {voice.age}")

            if hasattr(voice, 'gender'):
                print(f"      Gender: {voice.gender}")
            print()

    def change_voice(self, voice_index: int) -> bool:
        """Change to a specific voice by index"""
        if not self.available_voices or voice_index < 0 or voice_index >= len(self.available_voices):
            return False

        try:
            selected_voice = self.available_voices[voice_index]
            self.current_voice_id = selected_voice.id
            self.settings["voice"] = selected_voice.name

            if self.tts_engine:
                self.tts_engine.setProperty('voice', self.current_voice_id)

            print(f"Stimme geändert zu: {selected_voice.name}")
            return True

        except Exception as e:
            print(f"Fehler beim Ändern der Stimme: {e}")
            return False

    def change_settings(self, rate=None, volume=None):
        """Change TTS settings"""
        if not self.is_initialized:
            return False

        try:
            if rate is not None:
                # Validate rate (typically 50-400 WPM)
                rate = max(50, min(400, rate))
                self.settings["rate"] = rate
                self.tts_engine.setProperty('rate', rate)
                print(f"Geschwindigkeit auf {rate} WPM gesetzt")

            if volume is not None:
                # Validate volume (0.0 to 1.0)
                volume = max(0.0, min(1.0, volume))
                self.settings["volume"] = volume
                self.tts_engine.setProperty('volume', volume)
                print(f"Lautstärke auf {int(volume * 100)}% gesetzt")
            return True

        except Exception as e:
            print(f"Fehler beim Ändern der Einstellungen: {e}")
            return False

    def test_voice(self, text="Test deutschen Stimme mit festival-de."):
        """Test the current voice with sample text"""
        return self.speak_text(text)

    def get_status(self) -> str:
        """Returns current TTS status"""
        if not self.is_initialized:
            return "TTS Engine nicht initialisiert"

        status = f"pyttsx3 TTS Engine aktiv\n"
        status += f"Aktuelle Stimme: {self.settings['voice']}\n"
        status += f"Geschwindigkeit: {self.settings['rate']} WPM\n"
        status += f"Lautstärke: {int(self.settings['volume'] * 100)}%\n"
        status += f"Verfügbare Stimmen: {len(self.available_voices)}"

        return status

    def reinitialize(self):
        """Reinitialize the TTS engine"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        self.initialize_engine()

    @staticmethod
    def _select_best_voice(voices):
        german_keywords = ['german', 'deutsch', 'de-de', 'de_de', 'de', 'festival_de']
        english_keywords = ['english', 'en-us', 'en_us', 'en-gb']
        
        for voice in voices:
            voice_name = voice.name.lower() if voice.name else ""
            voice_id = voice.id.lower() if voice.id else ""
            
            if any(keyword in voice_name or keyword in voice_id for keyword in german_keywords):
                if 'festival' in voice_id and 'de' in voice_id:
                    return voice
                    
        for voice in voices:
            voice_name = voice.name.lower() if voice.name else ""
            voice_id = voice.id.lower() if voice.id else ""
            
            if any(keyword in voice_name or keyword in voice_id for keyword in german_keywords):
                return voice
                
        for voice in voices:
            voice_name = voice.name.lower() if voice.name else ""
            voice_id = voice.id.lower() if voice.id else ""
            
            if any(keyword in voice_name or keyword in voice_id for keyword in english_keywords):
                return voice
                
        return None

    @staticmethod
    def _get_voice_type(voice_id):
        if "festival" in voice_id and "de" in voice_id:
            return " [festival-de - DEUTSCH]"
        elif "festival" in voice_id:
            return " [festival]"
        elif "espeak" in voice_id:
            return " [espeak]"
        return ""



# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
class UI:
    """Terminal UI class for displaying menus and formatted output."""

    def __init__(self) -> None:
        self.banner: str = r'''
                                       ______
                    |\_______________ (_____\\______________
            HH======#H###############H#######################  
                    ' ~""""""""""""""`##(_))#H\"""""Y########    
                                      ))    \#H\       `"Y###
                                      "      }#H)
                                      
                                powered by xqi
        '''
        self.colors: Dict[str, str] = {
            "reset": colorama.Fore.RESET,
            "main": colorama.Fore.LIGHTCYAN_EX,
            "accent": colorama.Fore.MAGENTA,
            "success": colorama.Fore.LIGHTGREEN_EX,
            "error": colorama.Fore.LIGHTRED_EX,
            "warning": colorama.Fore.LIGHTYELLOW_EX,
            "tts": colorama.Fore.LIGHTBLUE_EX
        }

        # Borders with accent color
        border_line: str = "─" * 70
        self.top_border: str = (
            f"{self.colors['accent']}┌{border_line}┐{self.colors['reset']}"
        )
        self.bottom_border: str = (
            f"{self.colors['accent']}└{border_line}┘{self.colors['reset']}"
        )

        # TTS System
        self.tts = ArchTTS()

    def _speak_text_async(self, text):
        def speak_async():
            self.tts.speak_text(text)

        thread = threading.Thread(target=speak_async)
        thread.start()
        thread.join()

    @staticmethod
    def clear() -> None:
        os.system("clear")

    def print_banner(self) -> None:
        self.clear()
        print(f"{self.colors['main']}{self.banner}{self.colors['reset']}")

        # TTS Status
        if self.tts.is_initialized:
            print(f"{self.colors['tts']}[TTS] pyttsx3 geladen - {self.tts.settings['voice']}{self.colors['reset']}")
        else:
            print(
                f"{self.colors['error']}[TTS] Nicht verfügbar - installiere: sudo pacman -S espeak-ng festival festival-de{self.colors['reset']}")

    def print_centered(self, text: str, color: str = "main") -> None:
        terminal_width: int = shutil.get_terminal_size().columns
        print(f"{self.colors[color]}{text.center(terminal_width)}{self.colors['reset']}")

    def input_prompt(self, prompt: str) -> str:
        return input(f"{self.colors['accent']}[?] {prompt}{self.colors['reset']} > ")

    def menu_option(self, key: str, text: str) -> None:
        print(f" {self.colors['accent']}{key}{self.colors['reset']} > {self.colors['main']}{text}")

    def message(self, msg_type: str, text: str) -> None:
        print(f"{self.colors[msg_type]}[{msg_type[0].upper()}] {text}{self.colors['reset']}")

    def display_menu(self) -> None:
        self.print_banner()
        self.print_centered(self.top_border)
        self.menu_option("0", "Beenden")
        self.menu_option("1", "Zufälligen Text vorlesen")
        self.menu_option("2", "TTS Einstellungen ändern")
        self.menu_option("3", "TTS Status anzeigen")
        self.menu_option("4", "Verfügbare Stimmen anzeigen")
        self.menu_option("5", "Stimme ändern")
        self.menu_option("6", "Text eingeben und vorlesen")
        self.menu_option("7", "TTS Engine neu initialisieren")
        self.print_centered(self.bottom_border)

    def task_header(self) -> None:
        self.print_banner()
        self.print_centered(self.top_border)


# -----------------------------------------------------------------------------
# TASKS
# -----------------------------------------------------------------------------
def task_1(ui: UI) -> None:
    ui.task_header()

    filename: str = "text.txt"

    try:
        # Check if the file exists and create it if not
        if not os.path.exists(filename):
            default_lines = [
                "Hallo!",
                "I use Arch btw"
            ]
            with open(filename, "w", encoding="utf-8") as file:
                file.write('\n'.join(default_lines))
            ui.message("warning", f"Datei {filename} wurde mit Beispieltext erstellt.")

        # Read the text file
        with open(filename, "r", encoding="utf-8") as file:
            lines: List[str] = file.readlines()

        # Clean lines
        lines = [line.strip() for line in lines if line.strip()]

        if lines:
            random_line: str = lines[randint(0, len(lines) - 1)]
            ui.print_centered(f'"{random_line}"', "success")

            if ui.tts.is_initialized:

                # TTS in separatem Thread für bessere UI-Responsivität
                ui._speak_text_async(random_line)
            else:
                ui.message("error",
                           "TTS nicht verfügbar! Installiere: pip install pyttsx3 && sudo pacman -S espeak-ng festival festival-de")

        else:
            ui.message("error", "Die Textdatei enthält keine Zeilen.")

    except (FileNotFoundError, IOError, OSError) as e:
        ui.message("error", f"Fehler beim Verarbeiten der Datei: {e}")

    ui.print_centered(ui.bottom_border)
    #ui.message("success", "Aufgabe abgeschlossen")
    ui.input_prompt("Enter drücken um zum Menü zurückzukehren")


def task_2(ui: UI) -> None:
    ui.task_header()
    ui.print_centered("TTS Einstellungen", "accent")

    if not ui.tts.is_initialized:
        ui.message("error", "TTS Engine nicht verfügbar!")
        ui.print_centered(ui.bottom_border)
        ui.input_prompt("Enter drücken um zum Menü zurückzukehren")
        return

    settings = ui.tts.settings

    print(f"Aktuelle Einstellungen:")
    print(f"  Geschwindigkeit: {settings['rate']} WPM")
    print(f"  Lautstärke: {int(settings['volume'] * 100)}%")
    print(f"  Stimme: {settings['voice']}")
    print()

    try:
        new_speed = ui.input_prompt(f"Neue Geschwindigkeit (50-400, aktuell {settings['rate']})")
        if new_speed.strip():
            speed = int(new_speed)
            ui.tts.change_settings(rate=speed)

        new_volume = ui.input_prompt(f"Neue Lautstärke (0-100%, aktuell {int(settings['volume'] * 100)}%)")
        if new_volume.strip():
            volume = int(new_volume) / 100.0
            ui.tts.change_settings(volume=volume)

        # Test the new settings
        test = ui.input_prompt("Einstellungen testen? (y/n)")
        if test.lower() == 'y':
            ui.tts.test_voice("Test wird gestartet...")

    except ValueError:
        ui.message("error", "Ungültige Eingabe!")

    ui.print_centered(ui.bottom_border)
    ui.input_prompt("Enter drücken um zum Menü zurückzukehren")


def task_3(ui: UI) -> None:
    ui.task_header()
    ui.print_centered("TTS Status", "accent")

    print(ui.tts.get_status())
    print()

    if ui.tts.is_initialized:
        ui.print_centered(ui.bottom_border)
        test = ui.input_prompt("Status-Test durchführen? (y/n)")
        if test.lower() == 'y':
            ui.tts.test_voice("Test für TTS Engine wird gestartet...")

    ui.input_prompt("Enter drücken um zum Menü zurückzukehren")


def task_4(ui: UI) -> None:
    ui.task_header()
    ui.print_centered("Verfügbare Stimmen", "accent")

    ui.tts.list_voices()

    ui.print_centered(ui.bottom_border)
    ui.input_prompt("Enter drücken um zum Menü zurückzukehren")


def task_5(ui: UI) -> None:
    ui.task_header()
    ui.print_centered("Stimme ändern", "accent")

    if not ui.tts.is_initialized:
        ui.message("error", "TTS Engine nicht verfügbar!")
        ui.print_centered(ui.bottom_border)
        ui.input_prompt("Enter drücken um zum Menü zurückzukehren")
        return

    ui.tts.list_voices()

    try:
        ui.print_centered(ui.bottom_border)
        voice_input = ui.input_prompt("Stimmen-Nummer eingeben")
        if voice_input.strip():
            voice_index = int(voice_input)

            if ui.tts.change_voice(voice_index):
                test = ui.input_prompt("Neue Stimme testen? (y/n)")
                if test.lower() == 'y':
                    ui.tts.test_voice("Hallo! Dies ist die neue Stimme.")
            else:
                ui.message("error", "Ungültige Stimmen-Nummer!")

    except ValueError:
        ui.message("error", "Ungültige Eingabe!")

    #ui.print_centered(ui.bottom_border)
    ui.input_prompt("Enter drücken um zum Menü zurückzukehren")


def task_6(ui: UI) -> None:
    ui.task_header()
    ui.print_centered("Eigenen Text vorlesen", "accent")

    if not ui.tts.is_initialized:
        ui.message("error", "TTS nicht verfügbar!")
        ui.print_centered(ui.bottom_border)
        ui.input_prompt("Enter drücken um zum Menü zurückzukehren")
        return

    ui.print_centered(ui.bottom_border)
    custom_text = ui.input_prompt("Text eingeben")

    if custom_text.strip():
        ui._speak_text_async(custom_text.strip())
    else:
        ui.message("warning", "Kein Text eingegeben!")

    # ui.print_centered(ui.bottom_border)
    ui.task_header()
    ui.print_centered("Eigenen Text vorlesen", "accent")
    ui.print_centered(f"{custom_text}", "accent")
    ui.print_centered(ui.bottom_border)
    ui.input_prompt("Enter drücken um zum Menü zurückzukehren")


def task_7(ui: UI) -> None:
    ui.task_header()
    ui.print_centered("TTS Engine neu initialisieren", "accent")

    ui.message("warning", "TTS Engine wird neu initialisiert...")
    ui.tts.reinitialize()

    if ui.tts.is_initialized:
        ui.message("success", "TTS Engine erfolgreich neu initialisiert!")
        # ui.message("tts", f"Aktuelle Stimme: {ui.tts.settings['voice']}")
    else:
        ui.message("error", "Neuinitialisierung fehlgeschlagen!")

    ui.print_centered(ui.bottom_border)
    ui.input_prompt("Enter drücken um zum Menü zurückzukehren")


def error(ui: UI) -> None:
    ui.task_header()
    ui.message("error", "Ungültige Eingabe! Bitte erneut versuchen.")
    ui.print_centered(ui.bottom_border)
    ui.input_prompt("Enter drücken um zum Menü zurückzukehren")


# -----------------------------------------------------------------------------
# MAIN PROGRAM
# -----------------------------------------------------------------------------
def main() -> None:

    print("pyttsx3 gefunden")
    
    # Check for festival-de backend
    if not shutil.which("espeak") and not shutil.which("espeak-ng"):
        print("TTS Backend nicht gefunden!")
        print("Installiere mit: sudo pacman -S espeak-ng festival festival-de")
        print("Empfohlen: festival-de für hochwertige deutsche Stimmen")
        print("Optional: sudo pacman -S festival-english für englische Stimmen")
        print()

    ui: UI = UI()

    try:
        while True:
            ui.display_menu()
            command: str = ui.input_prompt("AUSWAHL")

            match command:
                case "0":
                    print("UwU")
                    return
                case "1":
                    task_1(ui)
                case "2":
                    task_2(ui)
                case "3":
                    task_3(ui)
                case "4":
                    task_4(ui)
                case "5":
                    task_5(ui)
                case "6":
                    task_6(ui)
                case "7":
                    task_7(ui)
                case _:
                    error(ui)

    except KeyboardInterrupt:
        print("\nProgramm wird beendet...")
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")


if __name__ == "__main__":
    main()
