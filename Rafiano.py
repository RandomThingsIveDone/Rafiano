"""
8888888b.            .d888 d8b
888   Y88b          d88P"  Y8P
888    888          888
888   d88P  8888b.  888888 888  8888b.  88888b.   .d88b.
8888888P"      "88b 888    888     "88b 888 "88b d88""88b
888 T88b   .d888888 888    888 .d888888 888  888 888  888
888  T88b  888  888 888    888 888  888 888  888 Y88..88P
888   T88b "Y888888 888    888 "Y888888 888  888  "Y88P"
"""

import configparser
import os
import shutil
import re
import time
import random
import sys
import ctypes
from ctypes import wintypes

from typing import Dict, List
from collections import defaultdict

CONFIG_FILE_PATH = "config.ini"
installed_apis = ["pyautogui", "keyboard", "pynput"]


def handle_import_error(module_name: str, is_critical: bool, message: str, module_pip: str = None,
                        continuation_message: str = None):
    """
    Handles the ImportError for a specified module by printing an appropriate message,
    suggesting installation commands, and optionally exiting the program.

    Parameters:
    module_name (str): The name of the module that failed to import.
    is_critical (bool): Whether the missing module is critical for the program's execution.
    message (str): The main error message to display.
    continuation_message (str, optional): An additional message to display if the program can continue without the module.

    Behavior:
    - Prints a formatted error message with installation instructions.
    - If a continuation_message is provided, prints it and waits for user input to continue.
    - If is_critical is True, exits the program after displaying the message.
    """

    if module_pip is None:
        module_pip = module_name
    print(message)
    print("\nPlease install it by running the following command:")
    print(f"    pip install {module_pip}")
    print(
        "\nIf you are using the executable version of this program and this ERROR occurs, open a GitHub issue with details.")
    print("GitHub: https://github.com/RandomThingsIveDone/Rafiano/issues")
    print("\n" + "#" * 60 + "\n")
    if continuation_message:
        print(continuation_message)
        print("#" * 60 + "\n")
    input("Press Enter to continue...")
    if is_critical:
        exit(1)


try:
    import curses
    from pynput.keyboard import Controller, Key
    from py_midicsv import midi_to_csv
    from py_midicsv.midi.fileio import ValidationError
    import keyboard as keyboard_controller
except ImportError as e:
    module_name = str(e).split("'")[-2]
    print(module_name)

    error_messages = {
        '_curses': {
            "module_pip": "windows-curses",
            'is_critical': True,
            'message': "CRITICAL ERROR: Unable to import 'windows-curses' module.\nThis module is essential for Windows console input handling in curses applications."
        },
        'py_midicsv': {
            'is_critical': False,
            'message': "WARNING: Unable to import 'py_midicsv' module.\nThis module is required for MIDI conversion functionality.",
            'continuation_message': "You can continue to use the program, but MIDI conversion will not be available.\nBig Thanks to Przemekkk for the MIDI conversion code, don't forget to look at his repo:\n    https://github.com/PrzemekkkYT/RaftMIDI \n"
        },
        'pynput': {
            'is_critical': False,
            'message': "WARNING: Unable to import 'pynput' module.\nThis module is required to use the libary 'pynput' as a controller/API method.",
            'continuation_message': "You can continue to use the program, but the library/api 'pynput' will not be available.\n"
        },
        'keyboard': {
            'is_critical': False,
            'message': "Warning: Unable to import 'keyboard' module.\nThis module is required to use the libary 'keyboard' as a controller/API method.",
            'continuation_message': "You can continue to use the program, but the library/api 'keyboard' will not be available.\n"
        },
    }

    if module_name in error_messages:

        # Remove the module from the list of installed modules
        if module_name in installed_apis:
            lst.remove(item)

        error_info = error_messages[module_name]
        handle_import_error(
            module_name,
            error_info['is_critical'],
            error_info['message'],
            error_info.get('module_pip'),
            error_info.get('continuation_message')
        )


class Utils:
    """
    Utility class for handling configuration and other common tasks.
    """

    def __init__(self):
        pass

    def create_default_config(self, reset_config=False):
        """
        Creates or resets a default configuration file with default values.
        Also ensures that the folder specified in 'notesheet_path' and the file 'master_notesheet' exist.

        Parameters:
        reset_config (bool): If True, reset the configuration file even if it already exists.
        """
        # Create ConfigParser object
        config = configparser.ConfigParser()

        # Check if config file exists
        if os.path.exists(CONFIG_FILE_PATH) and not reset_config:

            config.read(CONFIG_FILE_PATH)
        else:
            # Default configuration values

            config['DEFAULT'] = {'notesheet_path': 'Notesheets',
                                 'master_notesheet': 'Master.notesheet',
                                 'username': 'Anonymous',
                                 'api_type': 'pyautogui'}

            config['DO-NOT-EDIT'] = {'install_type': f'{self.get_install_type()}',
                                     'first_run': True}

            # Write configuration to file
            with open(CONFIG_FILE_PATH, 'w') as configfile:
                config.write(configfile)

        # Read configuration values
        notesheet_path = Utils().adjust_path(config.get('DEFAULT', 'notesheet_path'))
        master_notesheet = Utils().adjust_path(config.get('DEFAULT', 'master_notesheet'))

        # Ensure 'Notesheets' folder exists as per config
        if not os.path.exists(notesheet_path):
            os.makedirs(notesheet_path)

        # Ensure 'Master.notesheet' file exists inside 'Notesheets' folder as per config
        master_notesheet_path = os.path.join(notesheet_path, master_notesheet)
        if not os.path.exists(master_notesheet_path):
            with open(master_notesheet_path, 'w') as f:
                f.write('')  # Create an empty file

    def load_config(self):
        """
        Loads configuration from the config file.
        """
        if not os.path.exists(CONFIG_FILE_PATH):
            self.create_default_config()

        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        return config

    @staticmethod
    def nearest_lower(list_, num):
        """
        Find the nearest lower value in a list compared to a given number.

        Args:
        - list_: List of numbers.
        - num: Number to compare against.

        Returns:
        - The nearest lower value in the list.
        """
        return min(list_, key=lambda x: abs(x - num) if x <= num else float("inf"))

    @staticmethod
    def first_not_closed(list_, num):
        """
        Find the index of the first occurrence in a list where the first element of a tuple is equal to num.

        Args:
        - list_: List of tuples.
        - num: Number to compare against.

        Returns:
        - Index of the first occurrence where the first element of a tuple equals num, or None if not found.
        """
        return next(
            (
                index
                for index, item in enumerate(list_)
                if len(item) == 2 and item[0] == num
            ),
            None,
        )

    @staticmethod
    def sort_dicts_by_weights(groups, group_weights, reverse: bool = False):
        """
        Sort nested dictionary by group_weights from same key

        Args:
        - groups: Dictionary with dictionaries under special key.
        - group_weights: Dictionary with weights under special key.

        Returns:
        - Dictionary with sorted dictionaries based on group_weights
        """
        sorted_groups = {}
        for key in groups:
            inner_group = groups[key]
            inner_weights = group_weights[key]

            sorted_inner_keys = sorted(inner_group.keys(), key=lambda k: inner_weights[k], reverse=not reverse)

            sorted_inner_group = {k: inner_group[k] for k in sorted_inner_keys}

            sorted_groups[key] = sorted_inner_group
        return sorted_groups

    @staticmethod
    def is_pyinstaller_exe():
        try:
            frozen = getattr(sys, 'frozen', False)
            if frozen:
                # Running in a PyInstaller bundle
                return True
            else:
                return False
        except Exception:
            return False

    @staticmethod
    def find_all_programs_folder():
        try:
            # This is the default path for All Users Start Menu in English Windows versions
            start_menu_path = os.path.join(os.environ['ProgramData'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
            if os.path.exists(start_menu_path):
                return start_menu_path
            else:
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def get_exe_path():
        if getattr(sys, 'frozen', False):
            # When running in a PyInstaller bundle
            return sys.executable
        else:
            # When running in a normal Python environment
            return os.path.abspath(__file__)

    def get_install_type(self):
        # Check if running as a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            exe_path = self.get_exe_path()
            all_programs_path = self.find_all_programs_folder()
            if exe_path and all_programs_path and all_programs_path in exe_path:
                return "installed exe"
            else:
                return "exe"
        else:
            return "script"

    @staticmethod
    def clean_user_input(user_input: str, replace_character: str = ""):
        r"""
        Cleans the given user input string by removing or replacing invalid filename characters.

        Invalid characters include: < > : " / \ | ? * # and ASCII control characters (0-31).
        Leading and trailing whitespace and dots are also removed.

        Parameters:
        - user_input (str): The string to be cleaned.
        - replace_character (str): The character to replace invalid characters with. Default is an empty string.

        Returns:
        - str: The cleaned string with invalid characters removed or replaced.

        Raises:
        - ValueError: If the resulting cleaned filename is empty.
        """
        # Define a regex pattern for invalid filename characters including #
        invalid_chars_pattern = r'[<>:"/\\|?*#\x00-\x1F]'

        # Replace invalid characters with the specified replacement character
        cleaned_user_input = re.sub(invalid_chars_pattern, replace_character, user_input)

        # Remove leading or trailing whitespace and dots
        cleaned_user_input = cleaned_user_input.strip().strip('.')

        return cleaned_user_input

    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def run_as_admin():
        if os.name == 'nt':
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    @staticmethod
    def adjust_path(input_path):
        # todo: implement a way to when a relative path is in the config file it gets traced to the exe not where it started
        return input_path


class PyAutoGuiBareBones:
    # Barebones implementation of PyAutoGUI keyboard functions.
    # Based on https://github.com/asweigart/pyautogui/blob/master/pyautogui/_pyautogui_win.py
    # BSD license
    # Al Sweigart al@inventwithpython.com
    """A class for Windows-specific keyboard automation using Windows API."""

    # Key name constants
    KEY_NAMES = [
        "\t", "\n", "\r", " ", "!", '"', "#", "$", "%", "&", "'", "(", ")", "*",
        "+", ",", "-", ".", "/", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "^", "_", "",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
        "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "{", "|", "}", "~",
        "accept", "add", "alt", "altleft", "altright", "apps", "backspace",
        "browserback", "browserfavorites", "browserforward", "browserhome",
        "browserrefresh", "browsersearch", "browserstop", "capslock", "clear",
        "convert", "ctrl", "ctrlleft", "ctrlright", "decimal", "del", "delete",
        "divide", "down", "end", "enter", "esc", "escape", "execute",
        "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
        "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f20", "f21", "f22",
        "f23", "f24", "final", "fn", "hanguel", "hangul", "hanja", "help", "home",
        "insert", "junja", "kana", "kanji", "launchapp1", "launchapp2", "launchmail",
        "launchmediaselect", "left", "modechange", "multiply", "nexttrack",
        "nonconvert", "num0", "num1", "num2", "num3", "num4", "num5", "num6", "num7",
        "num8", "num9", "numlock", "pagedown", "pageup", "pause", "pgdn", "pgup",
        "playpause", "prevtrack", "print", "printscreen", "prntscrn", "prtsc",
        "prtscr", "return", "right", "scrolllock", "select", "separator", "shift",
        "shiftleft", "shiftright", "sleep", "space", "stop", "subtract", "tab", "up",
        "volumedown", "volumemute", "volumeup", "win", "winleft", "winright", "yen",
        "command", "option", "optionleft", "optionright"
    ]

    # Key event flags
    KEYEVENTF_KEYDOWN = 0x0000
    KEYEVENTF_KEYUP = 0x0002

    def __init__(self):
        """Initialize the Windows Keyboard Automation."""

        # Create keyboard mapping
        self.keyboard_mapping = self._create_keyboard_mapping()

    def _create_keyboard_mapping(self):
        """Create the keyboard mapping dictionary."""
        # Initialize mapping with None for all key names
        mapping = dict([(key, None) for key in self.KEY_NAMES])

        # Update with Windows-specific key mappings
        mapping.update({
            'backspace': 0x08,  # VK_BACK
            '\b': 0x08,  # VK_BACK
            'super': 0x5B,  #VK_LWIN
            'tab': 0x09,  # VK_TAB
            '\t': 0x09,  # VK_TAB
            'clear': 0x0c,  # VK_CLEAR
            'enter': 0x0d,  # VK_RETURN
            '\n': 0x0d,  # VK_RETURN
            'return': 0x0d,  # VK_RETURN
            'shift': 0x10,  # VK_SHIFT
            'ctrl': 0x11,  # VK_CONTROL
            'alt': 0x12,  # VK_MENU
            'pause': 0x13,  # VK_PAUSE
            'capslock': 0x14,  # VK_CAPITAL
            'kana': 0x15,  # VK_KANA
            'hanguel': 0x15,  # VK_HANGUEL
            'hangul': 0x15,  # VK_HANGUL
            'junja': 0x17,  # VK_JUNJA
            'final': 0x18,  # VK_FINAL
            'hanja': 0x19,  # VK_HANJA
            'kanji': 0x19,  # VK_KANJI
            'esc': 0x1b,  # VK_ESCAPE
            'escape': 0x1b,  # VK_ESCAPE
            'convert': 0x1c,  # VK_CONVERT
            'nonconvert': 0x1d,  # VK_NONCONVERT
            'accept': 0x1e,  # VK_ACCEPT
            'modechange': 0x1f,  # VK_MODECHANGE
            ' ': 0x20,  # VK_SPACE
            'space': 0x20,  # VK_SPACE
            'pgup': 0x21,  # VK_PRIOR
            'pgdn': 0x22,  # VK_NEXT
            'pageup': 0x21,  # VK_PRIOR
            'pagedown': 0x22,  # VK_NEXT
            'end': 0x23,  # VK_END
            'home': 0x24,  # VK_HOME
            'left': 0x25,  # VK_LEFT
            'up': 0x26,  # VK_UP
            'right': 0x27,  # VK_RIGHT
            'down': 0x28,  # VK_DOWN
            'select': 0x29,  # VK_SELECT
            'print': 0x2a,  # VK_PRINT
            'execute': 0x2b,  # VK_EXECUTE
            'prtsc': 0x2c,  # VK_SNAPSHOT
            'prtscr': 0x2c,  # VK_SNAPSHOT
            'prntscrn': 0x2c,  # VK_SNAPSHOT
            'printscreen': 0x2c,  # VK_SNAPSHOT
            'insert': 0x2d,  # VK_INSERT
            'del': 0x2e,  # VK_DELETE
            'delete': 0x2e,  # VK_DELETE
            'help': 0x2f,  # VK_HELP
            'win': 0x5b,  # VK_LWIN
            'winleft': 0x5b,  # VK_LWIN
            'winright': 0x5c,  # VK_RWIN
            'apps': 0x5d,  # VK_APPS
            'sleep': 0x5f,  # VK_SLEEP
            'num0': 0x60,  # VK_NUMPAD0
            'num1': 0x61,  # VK_NUMPAD1
            'num2': 0x62,  # VK_NUMPAD2
            'num3': 0x63,  # VK_NUMPAD3
            'num4': 0x64,  # VK_NUMPAD4
            'num5': 0x65,  # VK_NUMPAD5
            'num6': 0x66,  # VK_NUMPAD6
            'num7': 0x67,  # VK_NUMPAD7
            'num8': 0x68,  # VK_NUMPAD8
            'num9': 0x69,  # VK_NUMPAD9
            'multiply': 0x6a,  # VK_MULTIPLY  ??? Is this the numpad *?
            'add': 0x6b,  # VK_ADD  ??? Is this the numpad +?
            'separator': 0x6c,  # VK_SEPARATOR  ??? Is this the numpad enter?
            'subtract': 0x6d,  # VK_SUBTRACT  ??? Is this the numpad -?
            'decimal': 0x6e,  # VK_DECIMAL
            'divide': 0x6f,  # VK_DIVIDE
            'f1': 0x70,  # VK_F1
            'f2': 0x71,  # VK_F2
            'f3': 0x72,  # VK_F3
            'f4': 0x73,  # VK_F4
            'f5': 0x74,  # VK_F5
            'f6': 0x75,  # VK_F6
            'f7': 0x76,  # VK_F7
            'f8': 0x77,  # VK_F8
            'f9': 0x78,  # VK_F9
            'f10': 0x79,  # VK_F10
            'f11': 0x7a,  # VK_F11
            'f12': 0x7b,  # VK_F12
            'f13': 0x7c,  # VK_F13
            'f14': 0x7d,  # VK_F14
            'f15': 0x7e,  # VK_F15
            'f16': 0x7f,  # VK_F16
            'f17': 0x80,  # VK_F17
            'f18': 0x81,  # VK_F18
            'f19': 0x82,  # VK_F19
            'f20': 0x83,  # VK_F20
            'f21': 0x84,  # VK_F21
            'f22': 0x85,  # VK_F22
            'f23': 0x86,  # VK_F23
            'f24': 0x87,  # VK_F24
            'numlock': 0x90,  # VK_NUMLOCK
            'scrolllock': 0x91,  # VK_SCROLL
            'shiftleft': 0xa0,  # VK_LSHIFT
            'shiftright': 0xa1,  # VK_RSHIFT
            'ctrlleft': 0xa2,  # VK_LCONTROL
            'ctrlright': 0xa3,  # VK_RCONTROL
            'altleft': 0xa4,  # VK_LMENU
            'altright': 0xa5,  # VK_RMENU
            'browserback': 0xa6,  # VK_BROWSER_BACK
            'browserforward': 0xa7,  # VK_BROWSER_FORWARD
            'browserrefresh': 0xa8,  # VK_BROWSER_REFRESH
            'browserstop': 0xa9,  # VK_BROWSER_STOP
            'browsersearch': 0xaa,  # VK_BROWSER_SEARCH
            'browserfavorites': 0xab,  # VK_BROWSER_FAVORITES
            'browserhome': 0xac,  # VK_BROWSER_HOME
            'volumemute': 0xad,  # VK_VOLUME_MUTE
            'volumedown': 0xae,  # VK_VOLUME_DOWN
            'volumeup': 0xaf,  # VK_VOLUME_UP
            'nexttrack': 0xb0,  # VK_MEDIA_NEXT_TRACK
            'prevtrack': 0xb1,  # VK_MEDIA_PREV_TRACK
            'stop': 0xb2,  # VK_MEDIA_STOP
            'playpause': 0xb3,  # VK_MEDIA_PLAY_PAUSE
            'launchmail': 0xb4,  # VK_LAUNCH_MAIL
            'launchmediaselect': 0xb5,  # VK_LAUNCH_MEDIA_SELECT
            'launchapp1': 0xb6,  # VK_LAUNCH_APP1
            'launchapp2': 0xb7,  # VK_LAUNCH_APP2
        })

        # Populate basic printable ASCII characters
        for c in range(32, 128):
            mapping[chr(c)] = ctypes.windll.user32.VkKeyScanA(ctypes.wintypes.WCHAR(chr(c)))

        return mapping

    def press(self, key):
        """
        renamed from _keydown(self, key): to release(self, key) to simplify usage

        Perform a keyboard key press without release.

        Args:
            key (str): The key to be pressed down.
        """
        if key not in self.keyboard_mapping or self.keyboard_mapping[key] is None:
            return

        mods, vk_code = divmod(self.keyboard_mapping[key], 0x100)

        # Handle modifier keys
        modifier_keys = [
            (mods & 4, 0x12),  # Alt
            (mods & 2, 0x11),  # Ctrl
            (mods & 1, 0x10)  # Shift
        ]

        # Press down modifier keys if needed
        for apply_mod, vk_mod in modifier_keys:
            if apply_mod:
                ctypes.windll.user32.keybd_event(vk_mod, 0, self.KEYEVENTF_KEYDOWN, 0)

        # Press the main key
        ctypes.windll.user32.keybd_event(vk_code, 0, self.KEYEVENTF_KEYDOWN, 0)

    def release(self, key):
        """
        renamed from _keyup(self, key): to release(self, key) to simplify usage

        Args:
        Perform a keyboard key release.

        Args:
            key (str): The key to be released.
        """
        if key not in self.keyboard_mapping or self.keyboard_mapping[key] is None:
            return

        mods, vk_code = divmod(self.keyboard_mapping[key], 0x100)

        # Release the main key
        ctypes.windll.user32.keybd_event(vk_code, 0, self.KEYEVENTF_KEYUP, 0)

        # Release modifier keys if needed
        modifier_keys = [
            (mods & 1, 0x10),  # Shift
            (mods & 2, 0x11),  # Ctrl
            (mods & 4, 0x12)  # Alt
        ]

        for apply_mod, vk_mod in modifier_keys:
            if apply_mod:
                ctypes.windll.user32.keybd_event(vk_mod, 0, self.KEYEVENTF_KEYUP, 0)


class NotesheetUtils:
    """
    Utility class for parsing, validating, and manipulating notesheet files.
    """

    def __init__(self):
        pass

    @staticmethod
    def validate_notesheet(notesheet: str) -> bool:
        """
        Validates the notesheet by checking if it contains only valid characters.

        Args:
            notesheet (str): The notesheet to be validated.

        Returns:
            bool: True if the notesheet contains only valid characters, False otherwise.

        Raises:
            None: This function does not raise any exceptions.
        """
        notesheet = notesheet.split("\n")
        for notesheet_line in notesheet:
            if notesheet_line.startswith("#") or notesheet_line == "" or notesheet_line.startswith("|"):
                continue
            if not bool(re.match(r'([0-9.\s|]|SH|SP)*$', notesheet_line.upper())):
                return False
        return True

    def parse_file(self, file_path: str) -> List[Dict]:
        """
        Parse a notesheet file and extract song information.

        Args:
            file_path (str): Path to the notesheet file.

        Returns:
            List[Dict]: A list of dictionaries, each representing a song with its metadata and notes.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                notesheet_data = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return []

        all_songs = []
        read_notesheet = False
        current_song = {}
        current_song_notes = []
        start_line = 0

        if not self.validate_notesheet(notesheet_data):
            print(f"Skipping invalid notesheet: {file_path}")
            return []

        notesheet_lines = notesheet_data.split("\n")
        for i, notesheet_line in enumerate(notesheet_lines):
            if notesheet_line == "" or notesheet_line.startswith("#"):
                continue
            elif notesheet_line.startswith("|"):
                if read_notesheet:
                    current_song["notes"] = current_song_notes
                    current_song["Lines"] = [start_line, i]
                    current_song["file_path"] = file_path
                    all_songs.append(current_song)
                read_notesheet = True
                song_info = notesheet_line.split("|")
                current_song = {"name": song_info[1], "creator": song_info[2], "version": song_info[3]}
                current_song_notes = []
                start_line = i
            elif read_notesheet:
                split_notes = notesheet_line.split(" ")
                if split_notes[1].upper() == "":
                    modifier_key = "up"
                elif split_notes[1].upper() == "SH":
                    modifier_key = "shift"
                elif split_notes[1].upper() == "SP":
                    modifier_key = "space"
                else:
                    raise Exception("Invalid modifier value")
                try:
                    press_time = float(split_notes[2])
                    release_time = float(split_notes[3])
                except ValueError:
                    raise Exception("Invalid press/release time value")
                current_song_notes.append({"notes": split_notes[0].split("|"),
                                           "modifier": modifier_key,
                                           "press_time": press_time,
                                           "release_time": release_time
                                           })
        if read_notesheet:
            current_song["notes"] = current_song_notes
            current_song["Lines"] = [start_line, len(notesheet_lines)]
            current_song["file_path"] = file_path
            all_songs.append(current_song)

        return all_songs

    def parse_notesheet_file(self, filepath: str) -> List[Dict]:
        """
        Parses a notesheet file or files in a folder and returns a list of dictionaries,
        where each dictionary represents a song with its name, creator, and notes.

        Args:
            filepath (str): The path to the notesheet file or folder to be parsed.

        Returns:
            list: A list of dictionaries, where each dictionary represents a song with its
                  name, creator, notes, and line numbers.

        Raises:
            Exception: If the notesheet contains invalid modifier, release/press time values,
                       or invalid characters.
        """
        all_songs = []

        if os.path.isdir(filepath):
            for filename in os.listdir(filepath):
                file_path = os.path.join(filepath, filename)
                if os.path.isfile(file_path):
                    all_songs.extend(self.parse_file(file_path))
        elif os.path.isfile(filepath):
            all_songs.extend(self.parse_file(filepath))
        else:
            raise Exception("Provided path is neither a file nor a directory")

        return all_songs

    @staticmethod
    def notesheet_easy_convert(data: List[Dict]) -> List[List]:
        """
        Process the input data to extract actions with their corresponding times,
        combining actions for press and release times if applicable, and outputting
        a list of lists where each sublist contains a time followed by the actions
        performed at that time.

        Args:
            data (list of dicts): A list of dictionaries where each dictionary contains
                                  keys 'Note', 'press_time', and 'release_time'.

        Returns:
            list of lists: A list where each sublist contains a time followed by the
                           actions performed at that time, sorted by time.
        """
        result = []

        for entry in data:
            press_time = entry["press_time"]
            release_time = entry["release_time"]
            notes = entry["notes"]

            for note in notes:
                result.append((press_time, note))

            if press_time != release_time:
                for note in notes:
                    result.append((release_time, note))

        result.sort()

        output_list = []
        notes_by_time = defaultdict(list)

        for time, note in result:
            notes_by_time[time].append(note)

        output_list = [[time] + notes_by_time[time] for time in sorted(notes_by_time)]

        return output_list

    def remove_song_from_notesheet(self, notesheet_folder_path: str, song_name: str):
        """
        Removes a song from the notesheet by its name.

        Args:
            notesheet_folder_path (str): The file path to the notesheet.
            song_name (str): The name of the song to be removed.

        Returns:
            None
        """
        notesheet_data = self.parse_notesheet_file(notesheet_folder_path)

        start_line = None
        end_line = None
        notesheet_path = ""

        for song in notesheet_data:
            if song["name"] == song_name:
                start_line, end_line = song["Lines"]
                notesheet_path = song["file_path"]
                break

        if start_line is not None and end_line is not None:
            with open(notesheet_path, 'r', encoding='utf-8') as f:
                notesheet_contents = f.readlines()

            del notesheet_contents[start_line:end_line]

            with open(notesheet_path, 'w', encoding='utf-8') as f:
                f.writelines(notesheet_contents)

    def combine_notesheets(self, master_filepath: str, secondary_filepath: str, output_filepath: str):
        """
        Combines two notesheets into one, retaining the master notesheet's data
        in case of duplicate song names.

        Args:
            master_filepath (str): The file path to the master notesheet.
            secondary_filepath (str): The file path to the secondary notesheet.
            output_filepath (str): The file path to save the combined notesheet.

        Returns:
            None
        """
        with open(master_filepath, 'r', encoding='utf-8') as f:
            master_lines = f.readlines()

        with open(secondary_filepath, 'r', encoding='utf-8') as f:
            secondary_lines = f.readlines()

        master_data = self.parse_notesheet_file(master_filepath)
        secondary_data = self.parse_notesheet_file(secondary_filepath)

        master_songs = {song["name"]: song for song in master_data}

        combined_lines = master_lines.copy()

        for song in secondary_data:
            if song["name"] not in master_songs:
                start_line, end_line = song["Lines"]
                if combined_lines[-1].strip() != "":
                    combined_lines.append('\n')
                combined_lines.extend(secondary_lines[start_line:end_line])

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.writelines(combined_lines)

    def list_notesheets(self, folder_path):
        """
        Retrieve a list of notesheet filenames from the specified folder path.

        Args:
        - folder_path (str): The path to the folder containing notesheet files.

        Returns:
        - list: A list of filenames (strings) representing valid notesheet files found
          in the specified folder. Only files that can be parsed into songs are included.

        Notes:
        - This method checks each file in the folder_path directory. If the file is a
          valid notesheet (determined by the parse_file method), its filename is added
          to the returned list.

        - If folder_path does not exist or is not a valid directory, an empty list is returned.
        """
        notesheets = []
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    songs = self.parse_file(file_path)
                    if songs:  # Check if parse_file returned any songs
                        notesheets.append(filename)
        return notesheets


class MidiProcessor:
    """
    A class for processing MIDI files in CSV format.

    Attributes:
    - notes_to_keys (dict): Mapping of MIDI note values to corresponding key identifiers.
    - notes_with_shift (list): List of MIDI note values that trigger a 'shift' modifier.
    - notes_with_space (list): List of MIDI note values that trigger a 'space' modifier.

    Methods:
    - parse_midi(file_path):
      Parses a MIDI file in CSV format and extracts MIDI tracks and rows of MIDI events.

    - filter_csv(rows, tracks, selected):
      Filters MIDI CSV rows based on selected tracks.

    - get_timestamps(csv_string, track_num):
      Extracts timestamps, tempo information, and note events from a MIDI CSV string.

    - find_unclosed_note_index(notes, note):
      Finds the index of the last unclosed note of a specific pitch in the notes list.

    - handle_error(exc, message="An error occurred"):
      Handles an error by printing a formatted error message.

    - notesheet_v1(file_path, file_name, tpms, notes):
      Generates a notesheet file based on MIDI note events.
    """

    def __init__(self):
        self.notes_to_keys = {
            60: 1, 62: 2, 64: 3, 65: 4, 67: 5, 69: 6, 71: 7, 72: 8,
            74: 9, 76: 0, 77: 4, 79: 5, 81: 6, 83: 7, 84: 8, 86: 9, 88: 0,
            48: 1, 50: 2, 52: 3, 53: 4, 55: 5, 57: 6, 59: 7
        }
        self.notes_with_shift = [77, 79, 81, 83, 84, 86, 88]
        self.notes_with_space = [48, 50, 52, 53, 55, 57, 59]

    @staticmethod
    def find_title(file_path):
        titles = []

        for line in file_path:
            # Remove brackets and whitespace, then split by commas
            cleaned_line = line.strip()[1:-1].split(',')
            row = [elem.strip() for elem in cleaned_line]

            # Check if the third element is "Title_t"
            if len(row) > 2 and row[2] == "Title_t":
                titles.append(row[3])  # Assuming the title is in the fourth element

        return titles

    @staticmethod
    def parse_midi(file_path):
        """
        Parses a MIDI file in CSV format and extracts MIDI tracks and rows of MIDI events.

        Args:
        - file_path (str): The path to the MIDI file in CSV format.

        Returns:
        - sorted_tracks (list): Sorted list of unique MIDI tracks found in the file.
        - rows (list): List of rows representing MIDI events in CSV format.
        """
        midi_data = midi_to_csv(file_path)
        tracks = {}
        rows = []

        for line in midi_data:
            parts = line.strip().split(", ")
            if parts[2] == "Note_on_c" or parts[2] == "Note_off_c":
                tracks[int(parts[0])] = True

            rows.append(parts)

        return dict(sorted(tracks.items(), key=lambda x: x[1])), rows

    @staticmethod
    def filter_csv(rows, tracks, selected):
        """
        Filter MIDI CSV rows based on selected tracks.

        Args:
        - rows (list): A list of MIDI CSV rows where each row is a list of strings.
        - tracks (list): A list of MIDI tracks corresponding to each row.
        - selected (list): A list of boolean values indicating whether each track
          should be included in the filtered output.

        Returns:
        - list: A filtered list of MIDI CSV rows (strings) that match the selected
          tracks. Each row is formatted as a comma-separated string.

        Notes:
        - The function iterates through each row in the 'rows' list and checks if
          the MIDI event type is 'Note_on_c' or 'Note_off_c'. If the MIDI track
          of the event matches a track marked as selected (True in 'selected'),
          the row is included in the filtered output.
        - Rows that do not match 'Note_on_c' or 'Note_off_c' or whose track is
          not selected are also included in the filtered output.
        """
        selected_tracks = {ch for ch, sel in zip(tracks, selected) if sel}
        filtered_rows = []

        for row in rows:
            if len(row) >= 4 and row[2] in {"Note_on_c", "Note_off_c"}:
                track = int(row[3])
                if track in selected_tracks:
                    filtered_rows.append(",".join(row) + "\n")
            else:
                filtered_rows.append(",".join(row) + "\n")

        return filtered_rows

    def get_timestamps(self, csv_string, track_num):
        """
        Extract timestamps, tempo information, and note events from a MIDI CSV string.

        Args:
        - csv_string (str): MIDI CSV data represented as a string.
        - track_num (list): List of integers representing track numbers to process,
          or [-1] to process all tracks.

        Returns:
        - tuple: A tuple containing:
          - dict: Tempo map (tpms) where keys are timestamps and values are tempo values in BPM.
          - dict: Timestamps map where keys are timestamps and values are lists of tuples
            representing note events (note, event_type).
          - list: List of tuples representing note events sorted by their start timestamps.

        Notes:
        - This method parses MIDI CSV data (`csv_string`) to extract tempo information,
          note events, and their corresponding timestamps.
        - `track_num` specifies which tracks to process; [-1] indicates all tracks.
        - Tempo information is converted to BPM and stored in `tpms`.
        - Note events are categorized as 'start' and 'end' and stored in `timestamps`.
        - The `notes` list contains tuples of note events sorted by their start timestamps.
        """
        ppq = 0
        tpms = {}
        notes = []

        for line in csv_string:
            record = [int(v) if v.isdigit() else v for v in line.lower().replace("\n", "").split(", ")]
            if record[2] == "header":
                ppq = record[5]
            if record[2] == "tempo":
                try:
                    bpm = int(60_000_000 / int(record[3]))
                    tpms[record[1]] = bpm * ppq / 60_000
                except Exception as exc:
                    self.handle_error(exc)

            try:
                if record[0] in track_num or -1 in track_num:
                    if record[2] == "note_on_c":
                        if record[5]:
                            note = record[4]
                            notes.append((note, record[1]))
                        else:
                            note = record[4]
                            index = self.find_unclosed_note_index(notes, note)
                            if index is not None and record[1] > notes[index][1]:
                                notes[index] = notes[index] + (record[1],)
                    if record[2] == "note_off_c":
                        note = record[4]
                        index = self.find_unclosed_note_index(notes, note)
                        if index is not None and record[1] > notes[index][1]:
                            notes[index] = notes[index] + (record[1],)
            except Exception as exc:
                self.handle_error(exc)

        notes = [note for note in notes if len(note) == 3]
        notes = [(min(self.notes_to_keys, key=lambda x: abs(x - note[0])), *note[1:]) for note in notes]
        notes = sorted(notes, key=lambda x: x[1])

        return tpms, notes

    @staticmethod
    def find_unclosed_note_index(notes, note):
        """
        Find the index of the last unclosed note of a specific pitch in the notes list.

        Args:
        - notes (list): A list of tuples representing notes, where each tuple may have
          two or three elements (note, start_time, end_time).
        - note (int): The pitch value of the note to search for.

        Returns:
        - int or None: The index of the last unclosed note matching the given pitch `note`
          in the `notes` list. Returns None if no unclosed note is found.

        Notes:
        - This function searches through the `notes` list to find the last unclosed note
          with the specified pitch `note`. An unclosed note is defined as a tuple with
          two elements (note, start_time) indicating the note has been started but not yet
          ended with a third element (end_time).
        """
        for idx, n in enumerate(notes):
            if len(n) == 2 and n[0] == note:
                return idx
        return None

    @staticmethod
    def handle_error(exc, message="An error occurred"):
        """
        Handle an error by printing a formatted error message.

        Args:
        - exc (Exception): The exception object that was raised.
        - message (str): Optional. Custom error message to prepend to the exception details.
          Default is "An error occurred".

        Returns:
        - None: This function does not return any value.

        Notes:
        - This function is intended to handle errors in a generic way by printing an error
          message to standard output (usually the console).
        - It takes an exception object `exc` and an optional custom `message` to provide
          context or additional details about the error.
        """
        print(f"{message}: {exc}")

    def notesheet_v1(self, file_path, file_name, tpms, notes, title):
        """
        Generate a notesheet file based on MIDI note events.

        Args:
        - file_path (str): The directory path where the notesheet file will be created.
        - file_name (str): The name of the MIDI file or input source.
        - tpms (dict): Dictionary mapping timestamps to tempo values in BPM.
        - notes (list): List of tuples representing MIDI note events, where each tuple
          contains (note, start_time, end_time).

        Returns:
        - None: This function writes the notesheet file to disk but does not return any value.

        Notes:
        - This method generates a notesheet file (.notesheet) based on MIDI note events
          extracted from the input file.
        - The notesheet format is adapted from the RaftMIDI project, acknowledging the
          original code source and adapting it accordingly.
        - Notes are grouped by their start times, and for each group, the function calculates
          the key presses, modifiers (like 'SP' for space), durations, and times until the next note.
        - The `tpms` parameter is used to convert timestamps into seconds based on the nearest
          tempo map entry.
        """

        config = Utils().load_config()
        username = config.get('DEFAULT', 'username')

        with open(f"{file_path}/{file_name.split('/')[-1]}.notesheet", "w+") as notesheet:
            notesheet.write(
                f"|{title}|{username}|1.0\n"
                "###############################################################################\n"
                "# Notesheet generated using code from https://github.com/PrzemekkkYT/RaftMIDI #\n"
                "# Big Thanks to PrzemekkkYT for his work and help adapting his code to the    #\n"
                "# Notesheet format.                                                           #\n"
                "###############################################################################\n"
            )

            notes_per_start = {}
            for note in notes:
                start = note[1]
                if start not in notes_per_start:
                    notes_per_start[start] = [note]
                if start in notes_per_start and note not in notes_per_start[start]:
                    notes_per_start[start].append(note)

            for i, (start, _notes) in enumerate(notes_per_start.items()):
                ret_keys = ""
                ret_modifier = ""
                ret_howLong = 0.0
                ret_tillNext = 0.0

                for _note in _notes:
                    if len(_notes) > 1:
                        if _note[0] in self.notes_with_space:
                            notesheet.write(f"{self.notes_to_keys[_note[0]]} SP 0.001 0.0\n")
                            break
                        elif _note[0] in self.notes_with_shift:
                            notesheet.write(f"{self.notes_to_keys[_note[0]]} SH 0.001 0.0\n")
                            break
                    elif len(_notes) == 1:
                        if _note[0] in self.notes_with_space:
                            ret_modifier = "SP"
                        elif _note[0] in self.notes_with_shift:
                            ret_modifier = "SH"

                    if (x := f"{self.notes_to_keys[_note[0]]}") not in ret_keys:
                        ret_keys += f"{x}|"

                min_end = min(_notes, key=lambda x: x[2])[2]

                ret_howLong = ((min_end - start) / 1000 / tpms[Utils().nearest_lower(tpms.keys(), start)])

                ret_tillNext = ((list(notes_per_start.keys())[(
                    i + 1 if i < len(notes_per_start) - 1 else len(notes_per_start) - 1)] - min_end) / 1000 / tpms[
                                    Utils().nearest_lower(tpms.keys(), start)])

                if ret_howLong < 0:
                    ret_howLong = 0.0
                if ret_tillNext < 0:
                    ret_tillNext = 0.0

                if len(ret_keys) > 0:
                    if i != len(notes_per_start) - 1:
                        notesheet.write(
                            f"{ret_keys[:-1]} {ret_modifier} {ret_howLong:.4f} {ret_tillNext:.4f}\n"
                        )
                    else:
                        notesheet.write(f"{ret_keys[:-1]} {ret_modifier} {ret_howLong:.4f} {ret_tillNext:.4f}")

    def notesheet_v2(self, file_path, file_name, tpms, notes, title):
        """
        Generate a notesheet 2.0 file based on MIDI note events.

        Args:
        - file_path (str): The directory path where the notesheet file will be created.
        - file_name (str): The name of the MIDI file or input source.
        - tpms (dict): Dictionary mapping timestamps to tempo values in BPM.
        - notes (list): List of tuples representing MIDI note events, where each tuple
          contains (note, start_time, end_time).

        Returns:
        - None: This function writes the notesheet file to disk but does not return any value.

        Notes:
        - This method generates a notesheet file (.notesheet) based on MIDI note events
          extracted from the input file.
        - The notesheet format is adapted from the RaftMIDI project, acknowledging the
          original code source and adapting it accordingly.
        - Notes are grouped by their start times, and for each group, the function calculates
          the key presses, modifiers (like 'SP' for space), durations, and times until the next note.
        - The `tpms` parameter is used to convert timestamps into seconds based on the nearest
          tempo map entry.
        """

        config = Utils().load_config()
        username = config.get('DEFAULT', 'username')

        with open(f"{file_path}/{file_name.split('/')[-1]}.notesheet", "w+") as notesheet:
            notesheet.write(
                f"|{title}|{username}|2.0\n"
                "###############################################################################\n"
                "# Notesheet generated using code from https://github.com/PrzemekkkYT/RaftMIDI #\n"
                "# Big Thanks to PrzemekkkYT for his work and help adapting his code to the    #\n"
                "# Notesheet format.                                                           #\n"
                "###############################################################################\n"
            )

            notes_per_start = {}
            for note in notes:
                start = note[1]
                if start not in notes_per_start:
                    notes_per_start[start] = [note]
                if start in notes_per_start and note not in notes_per_start[start]:
                    notes_per_start[start].append(note)

            groups = {}
            for start, _notes in notes_per_start.items():
                groups[start] = {"SP": [], "SH": [], "": []}
                for _note in _notes:
                    if _note[0] in self.notes_with_shift:
                        groups[start]["SH"].append(_note)
                    elif _note[0] in self.notes_with_space:
                        groups[start]["SP"].append(_note)
                    else:
                        groups[start][""].append(_note)

            group_weights = {}
            for start, group in groups.items():
                group_weights[start] = {"SP": 0, "SH": 0, "": 0}
                for _modifier, _notes in group.items():
                    group_weights[start][_modifier] = len(_notes) * (
                            sum(_note[2] for _note in _notes) - sum(_note[1] for _note in _notes)) * (
                                                          1.01 if _modifier in ["SP", "SH"] else 1)

            sorted_groups = Utils().sort_dicts_by_weights(groups, group_weights, True)
            for start in groups:
                ret_keys = ""
                ret_modifier = ""
                ret_start = 0
                ret_end = 0
                for i, (_modifier, _notes) in enumerate(sorted_groups[start].items()):
                    for _note in _notes:
                        key = f"{self.notes_to_keys[_note[0]]}"
                        if key not in ret_keys:
                            ret_keys += f"{key}|"
                        ret_modifier = _modifier
                        cur_tpms = tpms[Utils().nearest_lower(tpms.keys(), _note[1])]
                        ret_start = _note[1] / 1000 / cur_tpms
                        ret_end = (_note[2] / 1000 / cur_tpms if i > 1 else ret_start + 0.1)
                    if len(ret_keys) > 0:
                        notesheet.write(
                            f"{ret_keys[:-1]} {ret_modifier} {ret_start:.4f} {ret_end:.4f}\n"
                        )


class NotesheetPlayer:
    """
    Class for playing notesheets based on different player versions.
    """

    class _Translate:
        """
        Class for translating special keys into any format.
        """

        # Dictionary for translating special keys into pynput format
        pynput_key_map = {
            "space": Key.space,
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "shift": Key.shift,
            "shift_r": Key.shift_r,  # Right Shift
            "ctrl": Key.ctrl,
            "ctrl_r": Key.ctrl_r,  # Right Control
            "alt": Key.alt,
            "alt_r": Key.alt_r,  # Right Alt
            "enter": Key.enter,
            "tab": Key.tab,
            "esc": Key.esc,
            "backspace": Key.backspace,
            "delete": Key.delete,
            "caps_lock": Key.caps_lock,
            "num_lock": Key.num_lock
        }

        pyautogui_key_map = {
            "shift": "shiftright",
        }

        keyboard_key_map = {}

        def __init__(self, translate_type="keyboard"):
            if translate_type == "pynput":
                self.special_key_map = self.pynput_key_map
            elif translate_type == "pyautogui":
                self.special_key_map = self.pyautogui_key_map
            elif translate_type == "keyboard":
                self.special_key_map = self.keyboard_key_map
            else:
                raise ValueError("Unsupported translation type.")

        def key(self, key):
            """ Helper function to translate string key names to pynput special keys. """
            if key in self.special_key_map:
                return self.special_key_map[key]
            else:
                return key  # If the key is not special, return it as is

    def __init__(self):
        pass

    class Keyboard:
        """ Class for handling keyboard events. """

        def __init__(self, api_type="pyautogui"):
            """
            Initialize the keyboard controller with the specified API type.

            :param api_type: The type of API to use. Options: 'pynput' or 'autopy'.
            """
            self.controller_type = api_type

            if self.controller_type == "pynput":
                self.keyboardC = Controller()
                self.translate = NotesheetPlayer._Translate(translate_type="pynput")

            elif self.controller_type == "keyboard":
                self.keyboardC = keyboard_controller
                self.translate = NotesheetPlayer._Translate(translate_type="keyboard")

            elif self.controller_type == "pyautogui":
                self.keyboardC = PyAutoGuiBareBones()
                self.translate = NotesheetPlayer._Translate(translate_type="pyautogui")
            else:
                raise ValueError("Unsupported controller type.")

        def release(self, key):
            """ Releases a key based on the controller type. """
            if key == "up":
                return

            self.keyboardC.release(self.translate.key(key))

        def press(self, key):
            """ Presses a key based on the controller type. """
            if key == "up":
                return

            self.keyboardC.press(self.translate.key(key))

    def _player_v1(self, stdscr, api_type, song_notes: List[Dict]) -> bool:
        """
        Plays the notes of a given song by simulating key presses based on relative timings.

        Args:
            song_notes (List[Dict]): A list of dictionaries containing information about the song to be played.

        Returns:
            bool: True, if the song was played successfully.
        """
        keyboard = self.Keyboard(api_type)
        stdscr.nodelay(True)

        for note_dic in song_notes:

            # Check for user input
            key = stdscr.getch()
            if key == ord('p') or key == ord('P'):  # Check for 'P' key press
                print("Playback stopped.")
                stdscr.nodelay(False)
                return False

            keyboard.press(note_dic["modifier"])
            for note in note_dic["notes"]:
                keyboard.press(note)
            time.sleep(note_dic["press_time"])
            for note in note_dic["notes"]:
                keyboard.release(note)
            keyboard.release(note_dic["modifier"])
            time.sleep(note_dic["release_time"])

        stdscr.nodelay(False)
        return True

    def _player_v2(self, stdscr, api_type, song_notes: List[Dict]) -> bool:
        """
        Plays the notes of a given song by simulating key presses based on absolute timings.

        Args:
            song_notes (List[Dict]): A list of dictionaries containing information about the song to be played.

        Returns:
            bool: True, if the song was played successfully.
        """
        keyboard = self.Keyboard(api_type)
        stdscr.nodelay(True)
        _PressRelease = {"shift": False, "space": False, "1": False, "2": False, "3": False,
                         "4": False, "5": False, "6": False, "7": False, "8": False,
                         "9": False, "0": False}

        songNotes = NotesheetUtils.notesheet_easy_convert(song_notes)

        start_time = time.time()
        for notes in songNotes:

            # Check for user input
            key = stdscr.getch()
            if key == ord('p') or key == ord('P'):  # Check for 'P' key press
                print("Playback stopped.")
                stdscr.nodelay(False)
                return False

            while time.time() - start_time < notes[0]:
                time.sleep(0.001)

            for note in notes[1:]:
                if _PressRelease[note]:
                    keyboard.release(note)
                    _PressRelease[note] = False
                else:
                    keyboard.press(note)
                    _PressRelease[note] = True

        stdscr.nodelay(False)
        return True

    def play(self, stdscr, api_type, song_notes: List[Dict], version: str) -> bool:
        """
        Plays the notes of a given song by simulating key presses.

        Args:
            song_notes (List[Dict]): A list of dictionaries containing information about the song to be played.
            version (str): The version of the player to use ("1.0" for relative timing, "2.0" for absolute timing).

        Returns:
            bool: True, if the song was played successfully.
        """
        if version == "1.0":
            return self._player_v1(stdscr, api_type, song_notes)
        elif version == "2.0":
            return self._player_v2(stdscr, api_type, song_notes)
        else:
            raise ValueError("Unsupported version")


class MenuManager:
    def __init__(self):
        pass

    #TODO: make whole Menu manger class more readable

    @staticmethod
    def _select_api(stdscr, installed_apis, last_line, config, CONFIG_FILE_PATH):
        """
        Allow the user to select an API type from a list using arrow keys.

        Args:
            stdscr: Curses screen object.
            installed_apis: List of available API types.
            last_line: Line number for displaying prompts.
            config: ConfigParser object.
            CONFIG_FILE_PATH: Path to the configuration file.
        """
        curses.curs_set(0)  # Hide the cursor
        current_selection = 0  # Start with the first item selected

        while True:
            # Clear the screen
            stdscr.clear()

            # Display the instruction
            stdscr.addstr(last_line, 1, "Use UP/DOWN to select your API type. Press ENTER to confirm.")

            # Display the list of APIs with the current selection highlighted
            for idx, api in enumerate(installed_apis):
                if idx == current_selection:
                    stdscr.attron(curses.A_REVERSE)  # Highlight the selected line
                    stdscr.addstr(last_line + 2 + idx, 1, f"> {api}")
                    stdscr.attroff(curses.A_REVERSE)
                else:
                    stdscr.addstr(last_line + 2 + idx, 1, f"  {api}")

            stdscr.refresh()

            # Get user input
            key = stdscr.getch()

            if key == curses.KEY_UP and current_selection > 0:
                current_selection -= 1
            elif key == curses.KEY_DOWN and current_selection < len(installed_apis) - 1:
                current_selection += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:  # ENTER key
                selected_api = installed_apis[current_selection]
                config.set('DEFAULT', 'api_type', selected_api)
                with open(CONFIG_FILE_PATH, 'w') as configfile:
                    config.write(configfile)
                stdscr.addstr(last_line + len(installed_apis) + 3, 1, f"API type set to '{selected_api}'!")
                stdscr.refresh()
                stdscr.getch()  # Wait for the user to acknowledge
                break

    @staticmethod
    def _play_songs_menu(stdscr, api_type, notesheet_data):
        curses.curs_set(0)  # Hide the cursor
        stdscr.clear()
        stdscr.refresh()

        menu_indicator = ">>>"
        current_option = 0

        while True:
            title: str = 'Rafiano | Song Selection | Use up and down arrows to navigate'

            song_options = [x["name"] + " by " + x["creator"] + " " + x["version"] for x in notesheet_data] + [
                "Go Back"]

            stdscr.addstr(1, 1, title, curses.A_BOLD)

            for i, option in enumerate(song_options):
                if i == current_option:
                    stdscr.addstr(i + 3, 1, menu_indicator + " " + option, curses.A_REVERSE)
                else:
                    stdscr.addstr(i + 3, 1, "   " + option + " ")

            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_option = (current_option - 1) % len(song_options)
            elif key == curses.KEY_DOWN:
                current_option = (current_option + 1) % len(song_options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_option == len(song_options) - 1:  # Exit option selected
                    break
                else:
                    stdscr.addstr(9, 1, " " * 100)
                    stdscr.addstr(10, 1, " " * 100)
                    stdscr.addstr(11, 1, " " * 100)
                    stdscr.addstr(12, 1, " " * 100)

                    stdscr.addstr(10, 1,
                                  f"Playing : {notesheet_data[current_option]['name']} by: {notesheet_data[current_option]['creator']}")
                    stdscr.refresh()
                    for i in range(5, 0, -1):
                        stdscr.addstr(11, 1, str(i))
                        stdscr.refresh()
                        time.sleep(1)

                    NotesheetPlayer().play(stdscr, api_type, notesheet_data[current_option]["notes"],
                                           notesheet_data[current_option]['version'])
                    stdscr.clear()

    @staticmethod
    def _combine_notesheets_menu(stdscr, folder_path):
        title = "Combine Notesheets | Use up/down arrows to navigate, Enter to select"
        subtitle_primary = "Select primary notesheet"
        subtitle_secondary = "Select secondary notesheet or enter custom path"

        options_primary = NotesheetUtils().list_notesheets(folder_path)
        if not options_primary:
            stdscr.addstr(1, 1, "No notesheets found in the specified folder.")
            stdscr.getch()  # Wait for user input to continue
            return

        options_primary.append("Custom path")  # Option to enter a custom path for primary notesheet
        current_option_primary = 0

        while True:
            stdscr.clear()
            stdscr.addstr(0, 1, title, curses.A_BOLD)
            stdscr.addstr(1, 1, subtitle_primary)
            for i, option in enumerate(options_primary):
                if i == current_option_primary:
                    stdscr.addstr(i + 3, 1, option, curses.A_REVERSE)
                else:
                    stdscr.addstr(i + 3, 1, option)

            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_option_primary = (current_option_primary - 1) % len(options_primary)
            elif key == curses.KEY_DOWN:
                current_option_primary = (current_option_primary + 1) % len(options_primary)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                selected_option_primary = options_primary[current_option_primary]
                if selected_option_primary == "Custom path":
                    stdscr.addstr(len(options_primary) + 4, 1, "Enter path to primary notesheet:")
                    stdscr.refresh()
                    curses.echo()  # Enable text input
                    primary_path = stdscr.getstr(len(options_primary) + 5, 1).decode(encoding="utf-8")
                    curses.noecho()  # Disable text input
                else:
                    primary_path = os.path.join(folder_path, selected_option_primary)

                # Secondary notesheet selection menu
                options_secondary = NotesheetUtils().list_notesheets(folder_path)
                if not options_secondary:
                    stdscr.addstr(len(options_primary) + 7, 1, "No notesheets found in the specified folder.")
                    stdscr.getch()  # Wait for user input to continue
                    return

                options_secondary.append("Custom path")  # Option to enter a custom path for secondary notesheet
                current_option_secondary = 0

                while True:
                    stdscr.clear()
                    stdscr.addstr(0, 1, title, curses.A_BOLD)
                    stdscr.addstr(1, 1, subtitle_secondary)
                    for i, option in enumerate(options_secondary):
                        if i == current_option_secondary:
                            stdscr.addstr(i + 3, 1, option, curses.A_REVERSE)
                        else:
                            stdscr.addstr(i + 3, 1, option)

                    stdscr.refresh()

                    key = stdscr.getch()

                    if key == curses.KEY_UP:
                        current_option_secondary = (current_option_secondary - 1) % len(options_secondary)
                    elif key == curses.KEY_DOWN:
                        current_option_secondary = (current_option_secondary + 1) % len(options_secondary)
                    elif key == curses.KEY_ENTER or key in [10, 13]:
                        selected_option_secondary = options_secondary[current_option_secondary]
                        if selected_option_secondary == "Custom path":
                            stdscr.addstr(len(options_secondary) + 4, 1, "Enter path to secondary notesheet:")
                            stdscr.refresh()
                            curses.echo()  # Enable text input
                            secondary_path = stdscr.getstr(len(options_secondary) + 5, 1).decode(encoding="utf-8")
                            curses.noecho()  # Disable text input
                        else:
                            secondary_path = os.path.join(folder_path, selected_option_secondary)

                        try:
                            NotesheetUtils().combine_notesheets(primary_path, secondary_path, primary_path)
                            stdscr.addstr(len(options_secondary) + 7, 1, "Notesheets combined successfully!")
                            stdscr.refresh()
                            stdscr.getch()  # Wait for user input to continue
                        except Exception as e:
                            stdscr.addstr(len(options_secondary) + 7, 1, f"Error combining notesheets: {str(e)}")
                            stdscr.refresh()
                            stdscr.getch()  # Wait for user input to continue
                        return

                    stdscr.clear()

    def _edit_notesheet_menu(self, stdscr):
        options = ["Combine Notesheets", "Remove Song", "One File Notesheet export", "Add MIDI File", "Go Back"]
        current_option = 0
        config = Utils().load_config()  # Load the configuration
        folder_path = Utils().adjust_path(
            config.get('DEFAULT', 'notesheet_path'))  # Get the notesheet path from the configuration

        while True:
            stdscr.clear()
            for i, option in enumerate(options):
                if i == current_option:
                    stdscr.addstr(i + 1, 1, option, curses.A_REVERSE)
                else:
                    stdscr.addstr(i + 1, 1, option)

            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_option = (current_option - 1) % len(options)
            elif key == curses.KEY_DOWN:
                current_option = (current_option + 1) % len(options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_option == 0:
                    # Combine Notesheets
                    self._combine_notesheets_menu(stdscr, folder_path)

                elif current_option == 1:
                    # TODO: "remove Notesheet" works now but its not pretty yet rework should be done display in
                    #  which Notesheet the song is Remove Song
                    notesheet_data = NotesheetUtils().parse_notesheet_file(folder_path)
                    self._delete_song_menu(stdscr, notesheet_data, folder_path)
                elif current_option == 2:

                    self._export_notesheet_menu(stdscr, folder_path)

                elif current_option == 3:
                    # Add MIDI File
                    notesheet_path = Utils().adjust_path(config.get('DEFAULT', 'notesheet_path'))
                    self._midi_conversion_menu(stdscr, notesheet_path)
                elif current_option == 4:
                    # Go Back
                    return

    @staticmethod
    def _export_notesheet_menu(stdscr, folder_path):
        # Export Notesheet
        stdscr.clear()
        stdscr.addstr(3, 1, "Enter output path for the exported notesheet:")
        stdscr.refresh()

        curses.echo()  # Enable text input
        output_path = f"{Utils.clean_user_input(stdscr.getstr(4, 1).decode(encoding='utf-8').strip())}.notesheet"
        curses.noecho()  # Disable text input

        if not output_path or output_path.endswith(".notesheet"):
            stdscr.addstr(5, 1, "Invalid output path. Please provide a valid path.")
            stdscr.refresh()
            stdscr.getch()  # Wait for user input to continue
            return

        notesheets = NotesheetUtils().list_notesheets(folder_path)

        #code to check if the output already exist if yes error lese create
        if os.path.exists(output_path):
            stdscr.addstr(5, 1, f"Notesheet already exists at {output_path}")
            stdscr.refresh()
            stdscr.getch()  # Wait for user input to continue
            return
        else:
            open(output_path, 'w').write("|If you are reading this|please contact us...|1.0")

        for notesheet in notesheets:
            try:
                NotesheetUtils().combine_notesheets(output_path, f"{folder_path}/{notesheet}", output_path)
            except Exception as e:
                stdscr.addstr(5, 1, f"Error exporting notesheet: {str(e)}")
                stdscr.refresh()
                stdscr.getch()  # Wait for user input to continue#

        with open(output_path, 'r') as f:
            lines = f.readlines()
        with open(output_path, 'w') as f:
            f.writelines(lines[1:])

        stdscr.addstr(5, 1, f"Notesheet exported successfully to {output_path}")
        stdscr.refresh()
        stdscr.getch()  # Wait for user input to continue

    @staticmethod
    def _midi_conversion_menu(stdscr, notesheet_path):
        stdscr.clear()  # Clear the screen
        if "py_midicsv" in sys.modules:
            curses.curs_set(1)  # Show the cursor
            stdscr.clear()
            stdscr.refresh()

            stdscr.addstr(1, 1, "Enter MIDI file path (e.g., Sandstorm.mid): ")
            stdscr.refresh()

            curses.echo()  # Enable text input
            input_file_path = stdscr.getstr(2, 1).decode(encoding="utf-8").strip().replace("\\", "/")
            curses.noecho()  # Disable text input

            input_file_name = input_file_path.split(".")[0]  # Extract file name without extension

            try:
                tracks, rows = MidiProcessor().parse_midi(input_file_path)
                midi_csv = midi_to_csv(input_file_path)

                # Further processing logic based on parsed MIDI data or CSV

                stdscr.addstr(3, 1, "MIDI file processed successfully!")
            except Exception as e:
                stdscr.addstr(3, 1, f"Error processing MIDI file: {str(e)}")
                stdscr.getch()
                return None

            curses.curs_set(0)  # Hide the cursor

            #using file name as Name for the Song
            # #try:
            #    title_t = "_".join(MidiProcessor.find_title(midi_csv))
            #except Exception as e:
            title_t = input_file_name.split('/')[-1]
            current_option = 0
            track_options = {i: tr for i, tr in enumerate(tracks.keys())}
            title = 'MIDI Track Selection | Use up/down arrows to navigate, Enter to select tracks and continue'

            while True:
                stdscr.clear()
                stdscr.addstr(1, 1, title, curses.A_BOLD)

                for i, track in enumerate(tracks.keys()):
                    option_text = f"Track {track} {'[x]' if tracks[track] else '[ ]'}"
                    if i == current_option:
                        stdscr.addstr(i + 3, 1, "> " + option_text, curses.A_REVERSE)
                    else:
                        stdscr.addstr(i + 3, 1, "  " + option_text)

                # Option for continuing
                continue_text = "Continue"
                if current_option == len(tracks):
                    stdscr.addstr(len(tracks) + 3, 1, "> " + continue_text, curses.A_REVERSE)
                else:
                    stdscr.addstr(len(tracks) + 3, 1, "  " + continue_text)

                stdscr.refresh()

                key = stdscr.getch()

                if key == curses.KEY_UP:
                    current_option = (current_option - 1) % (len(tracks) + 1)
                elif key == curses.KEY_DOWN:
                    current_option = (current_option + 1) % (len(tracks) + 1)
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    if current_option < len(tracks):
                        # selected[current_option] = not selected[current_option]
                        tracks[track_options[current_option]] = not tracks[track_options[current_option]]
                        ...
                    else:
                        break  # Break out of the loop to continue

            # filtered_rows = MidiProcessor().filter_csv(rows, tracks, selected)# not in use
            tpms, notes = MidiProcessor().get_timestamps(midi_csv, tracks.keys())

            options = ["Notesheet V1", "Notesheet V2"]

            while True:
                stdscr.clear()
                title = 'Select Notesheet Version: Use up and down arrows to navigate'

                stdscr.addstr(1, 1, title, curses.A_BOLD)

                for i, option in enumerate(options):
                    if i == current_option:
                        stdscr.addstr(i + 3, 1, "   " + option, curses.A_REVERSE)
                    else:
                        stdscr.addstr(i + 3, 1, "   " + option)

                stdscr.refresh()

                key = stdscr.getch()

                if key == curses.KEY_UP:
                    current_option = (current_option - 1) % len(options)
                elif key == curses.KEY_DOWN:
                    current_option = (current_option + 1) % len(options)
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    stdscr.clear()
                    stdscr.refresh()
                    if current_option == 0:

                        MidiProcessor().notesheet_v1(notesheet_path, input_file_name, tpms, notes,
                                                     title_t)  # Call function for Notesheet V1
                    elif current_option == 1:
                        MidiProcessor().notesheet_v2(notesheet_path, input_file_name, tpms, notes,
                                                     title_t)  # Call function for Notesheet V2
                    stdscr.addstr(10, 1, "Processing complete. Press any key to exit...")
                    stdscr.getch()
                    break

        else:
            stdscr.addstr(1, 1, "ERROR: py_midicsv is required for MIDI conversion functionality.")
            stdscr.addstr(3, 1, "Please install it by running the following command:")
            stdscr.addstr(4, 1, "    pip install py_midicsv")
            stdscr.addstr(6, 1, "If you're using the executable version and encounter issues,")
            stdscr.addstr(7, 1, "please report them on GitHub:")
            stdscr.addstr(9, 1, "GitHub: https://github.com/RandomThingsIveDone/Rafiano/issues")
            stdscr.addstr(11, 1, "#" * 60 + "\n")
            stdscr.addstr(12, 1, "Big Thanks to Przemekkk for the MIDI conversion code,")
            stdscr.addstr(13, 1, "don't forget to look at his repo:")
            stdscr.addstr(14, 1, "    https://github.com/PrzemekkkYT/RaftMIDI")
            stdscr.addstr(15, 1, "#" * 60 + "\n")
            stdscr.addstr(17, 1, "Press any key to go back...")
            stdscr.refresh()
            stdscr.getch()  # Wait for user input to continue
            stdscr.clear()  # Clear the screen after user input

    @staticmethod
    def _delete_song_menu(stdscr, notesheet_data, folder_path):
        curses.curs_set(0)  # Hide the cursor
        stdscr.clear()
        stdscr.addstr(1, 1, "Select song to delete:")

        song_options = [song["name"] + " by " + song["creator"] + " " + song["version"] for song in notesheet_data]
        song_options.append("Go Back")  # Add "Go Back" option
        current_option = 0

        while True:
            stdscr.clear()
            stdscr.addstr(1, 1, "Select song to delete:")

            for i, option in enumerate(song_options):
                if i == current_option:
                    stdscr.addstr(i + 3, 1, ">>>" + option, curses.A_REVERSE)
                else:
                    stdscr.addstr(i + 3, 1, "   " + option)
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_option = (current_option - 1) % len(song_options)
            elif key == curses.KEY_DOWN:
                current_option = (current_option + 1) % len(song_options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_option == len(song_options) - 1:  # Go Back option selected
                    return False  # Go back to the previous menu
                else:
                    confirmation_text = f"Are you sure you want to delete '{notesheet_data[current_option]['name']}'? Type 'Yes!' to confirm: "
                    stdscr.addstr(len(song_options) + 3, 1, confirmation_text)
                    stdscr.refresh()
                    curses.echo()  # Enable text input
                    confirmation = stdscr.getstr(len(song_options) + 4, 1).decode(encoding="utf-8")
                    curses.noecho()  # Disable text input

                    if confirmation.strip() == "Yes!":
                        song_name = notesheet_data[current_option]["name"]
                        NotesheetUtils().remove_song_from_notesheet(folder_path, song_name)
                        stdscr.addstr(len(song_options) + 5, 1, f"Song '{song_name}' deleted successfully!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                        return True  # Deletion confirmed
                    else:
                        stdscr.addstr(len(song_options) + 5, 1, "Deletion canceled!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                        return False  # Deletion canceled

    @staticmethod
    def _credits_menu(stdscr):
        curses.curs_set(0)  # Hide the cursor
        stdscr.clear()
        stdscr.nodelay(1)

        credits_art = r"""
        8888888b.            .d888 d8b
        888   Y88b          d88P"  Y8P
        888    888          888
        888   d88P  8888b.  888888 888  8888b.  88888b.   .d88b.
        8888888P"      "88b 888    888     "88b 888 "88b d88""88b
        888 T88b   .d888888 888    888 .d888888 888  888 888  888
        888  T88b  888  888 888    888 888  888 888  888 Y88..88P
        888   T88b "Y888888 888    888 "Y888888 888  888  "Y88P"
        """

        credits_text = """
        Credits:
    
        RandomThingsIveDone: Menu Coding and Notesheet format         https://github.com/RandomThingsIveDone/Rafiano
        PrzemekkkYT: MIDI conversion code and song added              https://github.com/PrzemekkkYT/RaftMIDI
        STALKER666YT: added new songs                                 https://github.com/STALKER666YT/Rafiano-UPDATED-
    
        Press any key to get back, EXCEPT FOR THE ARROW KEYS...
        """

        stdscr.addstr(1, 1, credits_art)
        stdscr.addstr(11, 1, credits_text)
        stdscr.refresh()

        # Initialize snake position and direction
        snake = [(5, 20), (5, 19), (5, 18)]
        direction = None

        # Wait for arrow key press to set initial direction
        while direction is None:
            key = stdscr.getch()
            if key in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN]:
                direction = key
            elif key != -1 and key not in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                stdscr.nodelay(0)
                return False  # return to get to main menu

        count = 0
        # loop for snake movement and credits display
        new_head = ()
        while True:
            try:
                # Display snake
                for y, x in snake:
                    stdscr.addch(y, x, curses.ACS_BLOCK)
                stdscr.refresh()

                key = stdscr.getch()

                if key in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN]:
                    direction = key

                # Check if any key is pressed to exit, but ignore arrow keys
                if key != -1 and key not in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                    stdscr.nodelay(0)
                    break

                time.sleep(0.1)
                count += 1
                if count < 5:
                    if direction == curses.KEY_RIGHT:
                        new_head = (snake[0][0], snake[0][1] + 1)
                    elif direction == curses.KEY_LEFT:
                        new_head = (snake[0][0], snake[0][1] - 1)
                    elif direction == curses.KEY_UP:
                        new_head = (snake[0][0] - 1, snake[0][1])
                    elif direction == curses.KEY_DOWN:
                        new_head = (snake[0][0] + 1, snake[0][1])
                    # Insert new head position at the beginning of the snake list
                    snake.insert(0, new_head)

                    # Erase tail (remove last element from snake)
                    stdscr.addch(snake[-1][0], snake[-1][1], ' ')
                    snake.pop()
                    count = 0

            except curses.error:
                art1 = """
                ██████╗  ██████╗     ███╗   ██╗ ██████╗ ████████╗    ██╗  ██╗██╗████████╗
                ██╔══██╗██╔═══██╗    ████╗  ██║██╔═══██╗╚══██╔══╝    ██║  ██║██║╚══██╔══╝
                ██║  ██║██║   ██║    ██╔██╗ ██║██║   ██║   ██║       ███████║██║   ██║   
                ██║  ██║██║   ██║    ██║╚██╗██║██║   ██║   ██║       ██╔══██║██║   ██║   
                ██████╔╝╚██████╔╝    ██║ ╚████║╚██████╔╝   ██║       ██║  ██║██║   ██║   
                ╚═════╝  ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝    ╚═╝       ╚═╝  ╚═╝╚═╝   ╚═╝    
                """

                art2 = """
                ████████╗██╗  ██╗███████╗    ██╗    ██╗ █████╗ ██╗     ██╗     ███████╗██╗
                ╚══██╔══╝██║  ██║██╔════╝    ██║    ██║██╔══██╗██║     ██║     ██╔════╝██║
                   ██║   ███████║█████╗      ██║ █╗ ██║███████║██║     ██║     ███████╗██║
                   ██║   ██╔══██║██╔══╝      ██║███╗██║██╔══██║██║     ██║     ╚════██║╚═╝
                   ██║   ██║  ██║███████╗    ╚███╔███╔╝██║  ██║███████╗███████╗███████║██╗
                   ╚═╝   ╚═╝  ╚═╝╚══════╝     ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝
                """
                art3 = """
                ▓█████▄  ▒█████      ███▄    █  ▒█████  ▄▄▄█████▓    ██░ ██  ██▓▄▄▄█████▓
                ▒██▀ ██▌▒██▒  ██▒    ██ ▀█   █ ▒██▒  ██▒▓  ██▒ ▓▒   ▓██░ ██▒▓██▒▓  ██▒ ▓▒
                ░██   █▌▒██░  ██▒   ▓██  ▀█ ██▒▒██░  ██▒▒ ▓██░ ▒░   ▒██▀▀██░▒██▒▒ ▓██░ ▒░
                ░▓█▄   ▌▒██   ██░   ▓██▒  ▐▌██▒▒██   ██░░ ▓██▓ ░    ░▓█ ░██ ░██░░ ▓██▓ ░ 
                ░▒████▓ ░ ████▓▒░   ▒██░   ▓██░░ ████▓▒░  ▒██▒ ░    ░▓█▒░██▓░██░  ▒██▒ ░ 
                 ▒▒▓  ▒ ░ ▒░▒░▒░    ░ ▒░   ▒ ▒ ░ ▒░▒░▒░   ▒ ░░       ▒ ░░▒░▒░▓    ▒ ░░   
                 ░ ▒  ▒   ░ ▒ ▒░    ░ ░░   ░ ▒░  ░ ▒ ▒░     ░        ▒ ░▒░ ░ ▒ ░    ░    
                 ░ ░  ░ ░ ░ ░ ▒        ░   ░ ░ ░ ░ ░ ▒    ░          ░  ░░ ░ ▒ ░  ░      
                   ░        ░ ░              ░     ░ ░               ░  ░  ░ ░           
                 ░                                                                       
                """
                art4 = """
                ▄▄▄█████▓ ██░ ██ ▓█████     █     █░ ▄▄▄       ██▓     ██▓      ██████  ▐██▌ 
                ▓  ██▒ ▓▒▓██░ ██▒▓█   ▀    ▓█░ █ ░█░▒████▄    ▓██▒    ▓██▒    ▒██    ▒  ▐██▌ 
                ▒ ▓██░ ▒░▒██▀▀██░▒███      ▒█░ █ ░█ ▒██  ▀█▄  ▒██░    ▒██░    ░ ▓██▄    ▐██▌ 
                ░ ▓██▓ ░ ░▓█ ░██ ▒▓█  ▄    ░█░ █ ░█ ░██▄▄▄▄██ ▒██░    ▒██░      ▒   ██▒ ▓██▒ 
                  ▒██▒ ░ ░▓█▒░██▓░▒████▒   ░░██▒██▓  ▓█   ▓██▒░██████▒░██████▒▒██████▒▒ ▒▄▄  
                  ▒ ░░    ▒ ░░▒░▒░░ ▒░ ░   ░ ▓░▒ ▒   ▒▒   ▓▒█░░ ▒░▓  ░░ ▒░▓  ░▒ ▒▓▒ ▒ ░ ░▀▀▒ 
                    ░     ▒ ░▒░ ░ ░ ░  ░     ▒ ░ ░    ▒   ▒▒ ░░ ░ ▒  ░░ ░ ▒  ░░ ░▒  ░ ░ ░  ░ 
                  ░       ░  ░░ ░   ░        ░   ░    ░   ▒     ░ ░     ░ ░   ░  ░  ░      ░ 
                     ░  ░  ░   ░  ░       ░          ░  ░    ░  ░    ░  ░      ░   ░    
                """

                while True:
                    # Check if a key is pressed
                    key = stdscr.getch()
                    if key != -1 and key not in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                        stdscr.nodelay(0)
                        curses.endwin()
                        return

                    # Randomly decide which art to change
                    if random.random() < 0.5:
                        current_art1 = art3  # Change art1
                    else:
                        current_art1 = art1  # Change art2

                    if random.random() < 0.5:
                        current_art2 = art4  # Change art1
                    else:
                        current_art2 = art2  # Change art2

                    # Display the current arts
                    stdscr.clear()
                    stdscr.addstr(1, 1, current_art1)
                    stdscr.addstr(9, 1, current_art2)
                    stdscr.refresh()

                    time.sleep(random.uniform(0.02, 0.4))

        curses.endwin()

    # TODO: Add a way to uninstall Rafiano
    # TODO: Add a way to import a notesheet

    @staticmethod
    def _perform_installation(stdscr):
        stdscr.addstr(5, 1, "Installing...", curses.A_BOLD)
        stdscr.refresh()

        try:
            # Get user's programs directory
            programs_folder = Utils.find_all_programs_folder()

            # Check if Rafiano folder already exists in programs directory
            rafiano_folder = os.path.join(programs_folder, "Rafiano")

            # Ensure the script is running with administrative privileges
            if not Utils.is_admin():
                stdscr.addstr(6, 1, "Restarting with administrative privileges...", curses.color_pair(1))
                stdscr.refresh()
                curses.napms(2000)  # Delay to show message

                sys.argv.append("--only-install")
                Utils.run_as_admin()
                sys.exit()

            # Create Rafiano folder in programs directory
            os.makedirs(rafiano_folder, exist_ok=True)

            # Get the path to the current executable or script
            current_path = Utils.get_exe_path()

            # Verify the current path is a valid executable
            if not current_path.endswith('.exe'):
                raise ValueError(f"The file {current_path} is not a valid executable")

            # Copy config.ini to Rafiano folder
            shutil.copy("config.ini", rafiano_folder)

            # Copy current executable or script to Rafiano folder
            shutil.copy(current_path, os.path.join(rafiano_folder, os.path.basename(current_path)))

            # Copy Notesheets folder to Rafiano folder
            shutil.copytree("Notesheets", os.path.join(rafiano_folder, "Notesheets"))

            # Create shortcuts
            Utils().create_programs_shortcut(rafiano_folder)
            Utils().create_desktop_shortcut(rafiano_folder)

            # Delete original config.ini and Notesheets folder
            os.remove("config.ini")
            shutil.rmtree("Notesheets")

            stdscr.addstr(6, 1,
                          "Installation completed successfully! \n search for Rafiano in the searchbar or use the desktop shortcut. \n Press any key to close the window.",
                          curses.A_BOLD)
            stdscr.refresh()
            stdscr.getch()

            # Close the current instance of the application
            sys.exit()

        except PermissionError:
            stdscr.addstr(7, 1, "Permission denied! Please run as administrator. Press any key to continue",
                          curses.color_pair(1))
            stdscr.refresh()
            stdscr.getch()
        except ValueError as e:
            stdscr.addstr(7, 1, f"Installation failed: {str(e)}. Press any key to continue", curses.color_pair(1))
            stdscr.refresh()
            stdscr.getch()
        except Exception as e:
            stdscr.addstr(7, 1, f"Installation failed: {str(e)}. Press any key to continue", curses.color_pair(1))
            stdscr.refresh()
            stdscr.getch()

    def _ask_to_install_menu(self, stdscr):
        stdscr.clear()
        stdscr.refresh()

        # Load configuration
        config = Utils().load_config()

        if "--only-install" in sys.argv:
            self._perform_installation(stdscr)
            return

        # Check if Rafiano is already installed
        programs_folder = Utils.find_all_programs_folder()
        rafiano_folder = os.path.join(programs_folder, "Rafiano")
        if os.path.exists(rafiano_folder):
            stdscr.addstr(6, 1,
                          "Rafiano is already installed! You should use the installed version instead. \n search for Rafiano in the searchbar. ",
                          curses.color_pair(1))
            stdscr.refresh()
            stdscr.getch()
            return

        # Define menu options
        options = ["Yes", "No, ask me later", "No, don't ask me again"]
        current_option = 0

        while True:
            stdscr.clear()
            stdscr.addstr(1, 1, f"Welcome! Would you like to install the application? {sys.argv[0]}", curses.A_BOLD)
            for i, option in enumerate(options):
                if i == current_option:
                    stdscr.addstr(3 + i, 1, f"{option}", curses.A_REVERSE)
                else:
                    stdscr.addstr(3 + i, 1, f"{option}")

            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_option = (current_option - 1) % len(options)
            elif key == curses.KEY_DOWN:
                current_option = (current_option + 1) % len(options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_option == 0:
                    # Handle "Yes" option - install the application
                    self._perform_installation(stdscr)
                    break
                elif current_option == 1:
                    # Handle "No, ask me later" option
                    break
                elif current_option == 2:
                    # Handle "No, don't ask me again" option
                    config.set('DO-NOT-EDIT', 'first_run', 'False')
                    with open(CONFIG_FILE_PATH, 'w') as configfile:
                        config.write(configfile)
                    break

    def _main_menu(self, stdscr):
        curses.curs_set(0)  # Hide the cursor
        stdscr.clear()
        stdscr.refresh()

        config = Utils().load_config()
        if Utils().get_exe_path() == os.path.join(Utils().find_all_programs_folder(), "Rafiano.exe"):
            config.set('DO-NOT-EDIT', 'first_run', 'False')
            with open(CONFIG_FILE_PATH, 'w') as configfile:
                config.write(configfile)

        elif config.getboolean('DO-NOT-EDIT', 'first_run', fallback=False) and config.get('DO-NOT-EDIT',
                                                                                          'install_type') == "exe":
            pass
            #TODO: ASK TO INSTALL DOSENT WORK PYWIN32 makes problems
            #self._ask_to_install_menu(stdscr)
        else:
            config.set('DO-NOT-EDIT', 'first_run', 'False')
            with open(CONFIG_FILE_PATH, 'w') as configfile:
                config.write(configfile)

        options = ["Play Music", "Edit Notesheet", "Settings", "Credits", "Exit"]
        current_option = 0

        while True:
            stdscr.clear()
            for i, option in enumerate(options):
                if i == current_option:
                    stdscr.addstr(i + 1, 1, option, curses.A_REVERSE)
                else:
                    stdscr.addstr(i + 1, 1, option)

            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_option = (current_option - 1) % len(options)
            elif key == curses.KEY_DOWN:
                current_option = (current_option + 1) % len(options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_option == 0:
                    # Play Music
                    config = Utils().load_config()
                    notesheet_path = Utils().adjust_path(config.get('DEFAULT', 'notesheet_path'))
                    api_type = config.get('DEFAULT', 'api_type')
                    notesheet_data = NotesheetUtils().parse_notesheet_file(notesheet_path)
                    self._play_songs_menu(stdscr, api_type, notesheet_data)
                elif current_option == 1:
                    # Edit Notesheet
                    self._edit_notesheet_menu(stdscr)
                elif current_option == 2:
                    # Settings
                    self._settings_menu(stdscr)
                elif current_option == 3:
                    # Credits
                    self._credits_menu(stdscr)
                elif current_option == 4:
                    # Exit
                    break

    def _settings_menu(self, stdscr):
        config = Utils().load_config()
        options = ["Change Notesheet Path", "Change Notesheet Master", "Set Username", "API type", "Reset",
                   "Open Rafiano Folder",
                   "Go Back"]
        current_option = 0
        last_line = len(options) + 2

        while True:
            stdscr.clear()
            stdscr.addstr(6, 30, f'program path: "{Utils().get_exe_path()}"')
            for i, option in enumerate(options):
                if i == current_option:
                    stdscr.addstr(i + 1, 1, option, curses.A_REVERSE)
                    config = Utils().load_config()
                    if i == 0:
                        notesheet_path = Utils().adjust_path(config.get('DEFAULT', 'notesheet_path'))
                        stdscr.addstr(1, 30, f"Notesheet Path: {notesheet_path}")
                    elif i == 1:
                        notesheet_master = Utils().adjust_path(config.get('DEFAULT', 'master_notesheet'))
                        stdscr.addstr(1, 30, f"Notesheet Master: {notesheet_master}")
                    elif i == 2:
                        current_username = config.get('DEFAULT', 'username', fallback='')
                        stdscr.addstr(1, 30, f"Current Username: {current_username}")
                    elif i == 3:
                        api_type = config.get('DEFAULT', 'api_type', fallback='')
                        stdscr.addstr(1, 30, f"API Type: {api_type}")
                    elif i == 4:
                        stdscr.addstr(1, 30, f"Config: set to default")
                else:
                    stdscr.addstr(i + 1, 1, option)

            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_option = (current_option - 1) % len(options)
            elif key == curses.KEY_DOWN:
                current_option = (current_option + 1) % len(options)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_option == 0:
                    stdscr.addstr(last_line, 1, "Enter new notesheet path:")
                    stdscr.refresh()
                    curses.curs_set(1)
                    curses.echo()
                    new_path = stdscr.getstr(8, 1).decode(encoding="utf-8")
                    curses.noecho()
                    config.set('DEFAULT', 'notesheet_path', new_path)
                    with open(CONFIG_FILE_PATH, 'w') as configfile:
                        config.write(configfile)
                    stdscr.addstr(last_line, 1, "Notesheet path changed!")
                    curses.curs_set(0)
                    stdscr.refresh()
                    stdscr.getch()
                elif current_option == 1:
                    stdscr.addstr(last_line, 1, "Enter new notesheet master path:")
                    curses.curs_set(1)
                    stdscr.refresh()
                    curses.echo()
                    new_path = stdscr.getstr(8, 1).decode(encoding="utf-8")
                    curses.noecho()
                    config.set('DEFAULT', 'master_notesheet', new_path)
                    with open(CONFIG_FILE_PATH, 'w') as configfile:
                        config.write(configfile)
                    stdscr.addstr(last_line, 1, "Notesheet master path changed!")
                    curses.curs_set(0)
                    stdscr.refresh()
                    stdscr.getch()
                elif current_option == 2:
                    stdscr.addstr(last_line, 1, "Enter your username:")
                    curses.curs_set(1)
                    stdscr.refresh()
                    curses.echo()
                    username = Utils().clean_user_input(stdscr.getstr(8, 1).decode(encoding="utf-8"))
                    curses.noecho()
                    config.set('DEFAULT', 'username', username)
                    with open(CONFIG_FILE_PATH, 'w') as configfile:
                        config.write(configfile)
                    stdscr.addstr(last_line, 1, "Username set!")
                    curses.curs_set(0)
                    stdscr.refresh()
                    stdscr.getch()
                elif current_option == 3:
                    self._select_api(stdscr, installed_apis, last_line, config, CONFIG_FILE_PATH)

                elif current_option == 4:
                    stdscr.addstr(last_line, 1, "Are you sure you want to reset? Type 'Yes!' to confirm: ")
                    stdscr.refresh()
                    curses.echo()
                    confirmation = stdscr.getstr(8, 1).decode(encoding="utf-8")
                    curses.noecho()
                    if confirmation.strip() == "Yes!":
                        Utils().create_default_config(True)
                        stdscr.addstr(last_line, 1, "Settings reset!" + "" * 50)
                        stdscr.refresh()
                        stdscr.getch()
                    else:
                        stdscr.addstr(last_line, 1, "Reset canceled!")
                        stdscr.refresh()
                        stdscr.getch()
                elif current_option == 5:
                    rafiano_folder = os.path.dirname(Utils().get_exe_path())
                    os.startfile(rafiano_folder)
                    return
                elif current_option == 6:
                    return

    def start(self):
        curses.wrapper(self._main_menu)


def main():
    Utils().create_default_config()
    menu_manager = MenuManager()
    menu_manager.start()


if __name__ == "__main__":
    main()

# TODO better wording for  "already installed Rafiano"
#  - when Rafiano is installed error displays the path to Rafiano
#  - Repair installation its really broken no time right now to fix, hot fix is to just dont allow people to install
