"""
Terminal UI application for displaying random text from a file.

Author: xqi
"""
import colorama
import shutil
import sys
import os

from random import randint
from typing import Dict, List

# Initialize colorama
colorama.init()

# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
class UI:
    """Terminal UI class for displaying menus and formatted output."""
    def __init__(self) -> None:
        """Creating the class UI"""
        self.banner: str = r'''
                                       ______
                    |\_______________ (_____\\______________
            HH======#H###############H#######################  
                    ' ~""""""""""""""`##(_))#H\"""""Y########    
                                      ))    \#H\       `"Y###
                                      "      }#H)
        '''
        self.colors: Dict[str, str] = {
            "reset": colorama.Fore.RESET,
            "main": colorama.Fore.LIGHTCYAN_EX,
            "accent": colorama.Fore.MAGENTA,
            "success": colorama.Fore.LIGHTGREEN_EX,
            "error": colorama.Fore.LIGHTRED_EX,
            "warning": colorama.Fore.LIGHTYELLOW_EX
        }

        # Borders with accent color
        border_line: str = "─" * 85
        self.top_border: str = (
            f"{self.colors['accent']}┌{border_line}┐{self.colors['reset']}"
        )
        self.bottom_border: str = (
            f"{self.colors['accent']}└{border_line}┘{self.colors['reset']}"
        )

    @staticmethod
    def clear() -> None:
        """Clears the console screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def print_banner(self) -> None:
        """Prints the main banner with colors"""
        self.clear()
        print(f"{self.colors['main']}{self.banner}{self.colors['reset']}")

    def print_centered(self, text: str, color: str = "main") -> None:
        """Prints centered text with specified color"""
        terminal_width: int = shutil.get_terminal_size().columns
        print(f"{self.colors[color]}{text.center(terminal_width)}{self.colors['reset']}")

    def input_prompt(self, prompt: str) -> str:
        """Displays a colored input prompt"""
        return input(f"{self.colors['accent']}[?] {prompt}{self.colors['reset']} > ")

    def menu_option(self, key: str, text: str) -> None:
        """Displays a menu option with colored formatting"""
        print(f" {self.colors['accent']}{key}{self.colors['reset']} > {self.colors['main']}{text}")

    def message(self, msg_type: str, text: str) -> None:
        """Displays a colored message (success, error, warning, etc.)"""
        print(f"{self.colors[msg_type]}[{msg_type[0].upper()}] {text}{self.colors['reset']}")

    def display_menu(self) -> None:
        """Displays the main menu"""
        self.print_banner()
        self.print_centered(self.top_border)
        self.menu_option("0", "Exit")
        self.menu_option("1", "TASK 1")
        self.menu_option("2", "TASK 2")
        self.menu_option("3", "TASK 3")
        self.print_centered(self.bottom_border)

    def task_header(self) -> None:
        """Displays the task header format"""
        self.print_banner()
        self.print_centered(self.top_border)


# -----------------------------------------------------------------------------
# SUBPROGRAMS
# -----------------------------------------------------------------------------
def task_1(ui: UI) -> None:
    """Task 1: Displays tt from a text file"""
    ui.task_header()

    path: str = './'
    filename: str = "text.txt"

    try:
        # Check if the file exists and create it if not
        if not os.path.exists(os.path.join(path, filename)):
            with open(os.path.join(path, filename), "w", encoding="utf-8") as file:
                file.write("Es müssen in text.txt Wörter eingetragen werden.")
                ui.message("warning", f"Datei {filename} wurde erstellt, da sie nicht existierte.")

        # Read the text file
        with open(os.path.join(path, filename), "r", encoding="utf-8") as file:
            lines: List[str] = file.readlines()

        # Split text in words
        lines = [line.strip() for line in lines if line.strip() != ""]

        if lines:
            random_line: str = lines[randint(0, len(lines) - 1)]
            # for i in range(0, len(lines)):
                # ui.print_centered(f"{random_line[i]}")
            ui.print_centered(f"{random_line}")
            # Display the random word
            # ui.message("success", "Task completed successfully")
        else:
            ui.message("error", "Die Textdatei enthält keine Wörter.")

    except (FileNotFoundError, IOError, OSError) as e:
        ui.message("error", f"Fehler beim Verarbeiten der Datei: {e}")

    ui.print_centered(ui.bottom_border)
    ui.message("success", "Task completed successfully")
    ui.input_prompt("Press Enter to return to menu")


def task_2(ui: UI) -> None:
    """Task 2: Placeholder function"""
    ui.task_header()
    ui.print_centered("Task 2 functionality not yet implemented")
    ui.print_centered(ui.bottom_border)
    ui.input_prompt("Press Enter to return to menu")


def task_3(ui: UI) -> None:
    """Task 3: Placeholder function"""
    ui.task_header()
    ui.print_centered("Task 3 functionality not yet implemented")
    ui.print_centered(ui.bottom_border)
    ui.input_prompt("Press Enter to return to menu")

def error(ui: UI) -> None:
    """Error: Displays function Errors"""
    ui.task_header()
    ui.message("error", "Ungültige Eingabe! Bitte erneut versuchen.")
    ui.print_centered(ui.bottom_border)
    ui.input_prompt("Press Enter to return to menu")

# -----------------------------------------------------------------------------
# MAIN PROGRAM
# -----------------------------------------------------------------------------
def main() -> None:
    """Main program entry point."""
    ui: UI = UI()

    while True:
        ui.display_menu()
        command: str = ui.input_prompt("MENU")

        match command:
            case "0":
                sys.exit()
            case "1":
                task_1(ui)
            case "2":
                task_2(ui)
            case "3":
                task_3(ui)
            case _:
                error(ui)


if __name__ == "__main__":
    main()
