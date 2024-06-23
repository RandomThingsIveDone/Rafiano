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
import curses
import os
import re
import shutil
import time
import random
import sys

from typing import Dict, List
from collections import defaultdict

try:
    from pynput.keyboard import Controller, Key
    from py_midicsv import midi_to_csv
    from py_midicsv.midi.fileio import ValidationError
except ImportError as e:
    module_name = str(e).split("'")[-2]
    if module_name in ['py_midicsv', 'py_midicsv.midi.fileio']:
        print("\n" + "#" * 60)
        print("WARNING: Unable to import 'py_midicsv' module.")
        print("This module is required for MIDI conversion functionality.")
        print("\nPlease install it by running the following command:")
        print("    pip install py_midicsv")
        print("\nIf you are using the executable version of this program and this ERROR ocurs, open a GitHub issue with details.")
        print("GitHub: https://github.com/RandomThingsIveDone/Rafiano/issues")
        print("\nYou can continue to use the program, but MIDI conversion will not be available.")
        print("#" * 60 + "\n")
        print("Big Thanks to Przemekkk for the MIDI conversion code, dont forget to look at his repo:\n    https://github.com/PrzemekkkYT/RaftMIDI \n")
        print("#" * 60 + "\n")
        input("Press Enter to continue...")


    elif module_name == 'pynput':
        print("\n" + "#" * 60)
        print("CRITICAL ERROR: Unable to import 'pynput' module.")
        print("This module is essential for the program to run.")
        print("\nPlease install it by running the following command:")
        print("    pip install pynput")
        print("\nIf you are using the executable version of this program and this ERROR ocurs, open a GitHub issue with details.")
        print("GitHub: https://github.com/RandomThingsIveDone/Rafiano/issues")
        print("#" * 60 + "\n")
        input("Press Enter to continue...")
        exit(1)

CONFIG_FILE_PATH = "config.ini"


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def create_default_config():
        """
        Creates a default configuration file with default values.
        """
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'notesheet_paths': 'Notesheet'}
        with open(CONFIG_FILE_PATH, 'w') as configfile:
            config.write(configfile)

    def load_config(self):
        """
        Loads configuration from the config file.
        """
        if not os.path.exists(CONFIG_FILE_PATH):
            self.create_default_config()

        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        return config



class NotesheetUtils:
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
        # Split the notesheet string into individual lines
        notesheet = notesheet.split("\n")

        # Loop through each line of the notesheet
        for notesheet_line in notesheet:

            # Ignore comment lines, empty lines and song header lines
            if notesheet_line.startswith("#") or notesheet_line == "" or notesheet_line.startswith("|"):
                continue

            # If the line contains invalid characters, return False
            if not bool(re.match(r'([0-9.\s|]|SH|SP)*$', notesheet_line.upper())):
                return False

        # If all lines contain valid characters, return True
        return True

    def parse_file(self, file_path: str) -> List[Dict]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                notesheet_data = f.read()
        except:
            return []

        all_songs = []
        read_notesheet = False
        current_song = {}
        current_song_notes = []
        start_line = 0

        # Validate the notesheet before parsing
        if not self.validate_notesheet(notesheet_data):
            print(f"Skipping invalid notesheet: {file_path}")
            return []

        # Split the notesheet string into individual lines
        notesheet_lines = notesheet_data.split("\n")

        # Loop through each line of the notesheet
        for i, notesheet_line in enumerate(notesheet_lines):
            # Ignore comment lines and empty lines
            if notesheet_line == "" or notesheet_line.startswith("#"):
                continue

            # If a song header line is found, start a new song
            elif notesheet_line.startswith("|"):
                # If already read song information, append to list
                if read_notesheet:
                    current_song["notes"] = current_song_notes
                    current_song["Lines"] = [start_line, i]
                    all_songs.append(current_song)

                # Set variables for new song
                read_notesheet = True
                song_info = notesheet_line.split("|")
                current_song = {"name": song_info[1], "creator": song_info[2], "version": song_info[3]}
                current_song_notes = []
                start_line = i

            # If reading notes, add note information to current song
            elif read_notesheet:
                # Parse note information
                split_notes = notesheet_line.split(" ")
                if split_notes[1].upper() == "":
                    modifier_key = Key.up
                elif split_notes[1].upper() == "SH":
                    modifier_key = Key.shift
                elif split_notes[1].upper() == "SP":
                    modifier_key = Key.space
                else:
                    raise Exception("Invalid modifier value")

                try:
                    press_time = float(split_notes[2])
                    release_time = float(split_notes[3])
                except ValueError:
                    raise Exception("Invalid press/release time value")

                # Add note information to song
                current_song_notes.append({"notes": split_notes[0].split("|"),
                                           "modifier": modifier_key,
                                           "press_time": press_time,
                                           "release_time": release_time
                                           })

        # Add the last song to the list if one was being read
        if read_notesheet:
            current_song["notes"] = current_song_notes
            current_song["Lines"] = [start_line, len(notesheet_lines)]
            all_songs.append(current_song)

        return all_songs

    def parse_notesheet_file(self, filepath: str) -> List[Dict]:
        """
        Parses a notesheet file or files in a folder and returns a list of dictionaries, where each dictionary represents a song with its name, creator, and notes.

        Args:
            filepath (str): The path to the notesheet file or folder to be parsed.

        Returns:
            list: A list of dictionaries, where each dictionary represents a song with its name, creator, notes, and line numbers.

        Raises:
            Exception: If the notesheet contains invalid modifier, release/press time values, or invalid characters.
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
    def notesheet_easy_convert(data):
        """
        Process the input data to extract actions with their corresponding times,
        combining actions for press and release times if applicable, and outputting
        a list of lists where each sublist contains a time followed by the actions
        performed at that time.

        Args:
        - data (list of dicts): A list of dictionaries where each dictionary contains
          keys 'Note', 'press_time', and 'release_time'.

        Returns:
        - list of lists: A list where each sublist contains a time followed by the
          actions performed at that time, sorted by time.
        """

        result = []

        # Process each entry in the data
        for entry in data:
            press_time = entry["press_time"]
            release_time = entry["release_time"]
            notes = entry["notes"]

            # Add notes with press time
            for note in notes:
                result.append((press_time, note))

            # Add notes with release time if different from press time
            if press_time != release_time:
                for note in notes:
                    result.append((release_time, note))

        # Sort the result based on time (first element of each tuple)
        result.sort()

        # Initialize output list
        output_list = []

        # Use defaultdict to collect notes by time
        notes_by_time = defaultdict(list)

        for time, note in result:
            notes_by_time[time].append(note)

        # Convert defaultdict to the final output format
        output_list = [[time] + notes_by_time[time] for time in sorted(notes_by_time)]

        return output_list

    def remove_song_from_notesheet(self, notesheet_filepath: str, song_name: str):
        """
        Removes a song from the notesheet by its name.

        Args:
            notesheet_filepath (str): The file path to the notesheet.
            song_name (str): The name of the song to be removed.

        Returns:
            None
        """
        # Parse the notesheet file to get song metadata
        notesheet_data = self.parse_notesheet_file(notesheet_filepath)

        # Initialize variables to track the lines corresponding to the song to be removed
        start_line = None
        end_line = None

        # Find the start and end lines of the song to be removed
        for song in notesheet_data:
            if song["name"] == song_name:
                start_line, end_line = song["Lines"]
                break

        # If the song was found, remove its lines from the notesheet file
        if start_line is not None and end_line is not None:
            # Read the contents of the notesheet file
            with open(notesheet_filepath, 'r', encoding='utf-8') as f:
                notesheet_contents = f.readlines()

            # Remove the lines corresponding to the song to be deleted
            del notesheet_contents[start_line:end_line]

            # Rewrite the notesheet file with the updated contents
            with open(notesheet_filepath, 'w', encoding='utf-8') as f:
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
        # Read raw lines from master and secondary notesheets
        with open(master_filepath, 'r', encoding='utf-8') as f:
            master_lines = f.readlines()

        with open(secondary_filepath, 'r', encoding='utf-8') as f:
            secondary_lines = f.readlines()

        # Parse the notesheets to get song metadata
        master_data = self.parse_notesheet_file(master_filepath)
        secondary_data = self.parse_notesheet_file(secondary_filepath)

        # Dictionary to track song names in the master notesheet
        master_songs = {song["name"]: song for song in master_data}

        # Combine the master notesheet lines with non-duplicate songs from the secondary notesheet
        combined_lines = master_lines.copy()

        for song in secondary_data:
            if song["name"] not in master_songs:
                start_line, end_line = song["Lines"]
                if combined_lines[-1].strip() != "":  # Add a newline if the last line is not empty
                    combined_lines.append('\n')
                combined_lines.extend(secondary_lines[start_line:end_line])

        # Write combined notesheet lines to the output file
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.writelines(combined_lines)


class NotesheetPlayer:
    def __init__(self):
        pass

    def _player_v1(self, song_notes: List[Dict]) -> bool:
        """
        Plays the notes of a given song by simulating key presses based on relative timings.

        Args:
            song_notes (List[Dict]): A list of dictionaries containing information about the song to be played.

        Returns:
            bool: True, if the song was played successfully.
        """
        # Create a keyboard controller object to simulate key presses
        keyboard = Controller()

        # Iterate through each note in the song notes dictionary
        for note_dic in song_notes:
            # Press the modifier key for the current note
            keyboard.press(note_dic["modifier"])
            # Press each note in the current note's list of notes
            for note in note_dic["notes"]:
                keyboard.press(note)
            # Wait for the specified press time
            time.sleep(note_dic["press_time"])
            # Release each note in the current note's list of notes
            for note in note_dic["notes"]:
                keyboard.release(note)
            # Release the modifier key for the current note
            keyboard.release(note_dic["modifier"])
            # Wait for the specified release time
            time.sleep(note_dic["release_time"])

        # Return True to indicate that the song was played successfully
        return True

    def _player_v2(self, song_notes: List[Dict]) -> bool:
        """
        Plays the notes of a given song by simulating key presses based on absolute timings.

        Args:
            song_notes (List[Dict]): A list of dictionaries containing information about the song to be played.

        Returns:
            bool: True, if the song was played successfully.
        """
        keyboard = Controller()
        _PressRelease = {Key.shift: False, Key.space: False, "1": False, "2": False, "3": False,
                         "4": False, "5": False, "6": False, "7": False, "8": False,
                         "9": False, "0": False}

        songNotes = NotesheetUtils().notesheet_easy_convert(
            song_notes)  # Assuming you have a function to convert song_notes

        start_time = time.time()
        for notes in songNotes:
            while time.time() - start_time < notes[0]:
                time.sleep(0.001)  # Adjust sleep time to avoid excessive CPU usage

            for note in notes[1:]:
                if _PressRelease[note]:
                    keyboard.release(note)
                    _PressRelease[note] = False
                else:
                    keyboard.press(note)
                    _PressRelease[note] = True

        return True  # Return True if the song was played successfully

    def play(self, song_notes: List[Dict], version: str) -> bool:
        """
        Plays the notes of a given song by simulating key presses.

        Args:
            song_notes (List[Dict]): A list of dictionaries containing information about the song to be played.
            version (str): The version of the player to use ("1.0" for relative timing, "2.0" for absolute timing).

        Returns:
            bool: True, if the song was played successfully.
        """
        if version == "1.0":
            return self._player_v1(song_notes)
        elif version == "2.0":
            return self._player_v2(song_notes)
        else:
            raise ValueError("Unsupported version")


class MenuManager:
    def __init__(self):
        pass

    def _play_songs_menu(self, stdscr, notesheet_data):
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
                    stdscr.addstr(i + 3, 1, "   " + option)

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
                    stdscr.addstr(10, 1,
                                  f"Playing : {notesheet_data[current_option]['name']} by: {notesheet_data[current_option]['creator']}")
                    stdscr.refresh()
                    for i in range(5, 0, -1):
                        stdscr.addstr(11, 1, str(i))
                        stdscr.refresh()
                        time.sleep(1)
                    NotesheetPlayer().play(notesheet_data[current_option]["notes"],
                                           notesheet_data[current_option]['version'])

    def _edit_notesheet_menu(self, stdscr):
        options = ["Combine Notesheets", "Remove Song", "Export Notesheet", "Add MIDI File", "Go Back"]
        current_option = 0
        config = Utils().load_config()  # Load the configuration
        master_path = config.get('DEFAULT', 'notesheet_paths')  # Get the notesheet path from the configuration

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
                    stdscr.addstr(len(options) + 3, 1, f"Master notesheet: {master_path}")
                    stdscr.addstr(len(options) + 4, 1, "Enter path to secondary notesheet:")
                    stdscr.refresh()
                    curses.echo()  # Enable text input
                    secondary_path = stdscr.getstr(len(options) + 5, 1).decode(encoding="utf-8")
                    curses.noecho()  # Disable text input

                    try:
                        NotesheetUtils().combine_notesheets(master_path, secondary_path, master_path)
                        stdscr.addstr(len(options) + 8, 1, "Notesheets combined successfully!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                    except Exception as e:
                        stdscr.addstr(len(options) + 8, 1, f"Error combining notesheets: {str(e)}")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                elif current_option == 1:
                    # Remove Song
                    notesheet_data = NotesheetUtils().parse_notesheet_file(master_path)
                    self._delete_song_menu(stdscr, notesheet_data, master_path)
                elif current_option == 2:
                    # Export Notesheet
                    stdscr.addstr(len(options) + 3, 1, "Enter output path for the exported notesheet:")
                    stdscr.refresh()
                    curses.echo()  # Enable text input
                    output_path = stdscr.getstr(len(options) + 4, 1).decode(encoding="utf-8")
                    curses.noecho()  # Disable text input
                    try:
                        shutil.copyfile(master_path, output_path)
                        stdscr.addstr(len(options) + 5, 1, "Notesheet exported successfully!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                    except Exception as e:
                        stdscr.addstr(len(options) + 5, 1, f"Error exporting notesheet: {str(e)}")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                elif current_option == 3:
                    # Add MIDI File
                    self._run_midi_conversion_menu(stdscr)
                elif current_option == 4:
                    # Go Back
                    return

    def _run_midi_conversion_menu(self, stdscr):

        stdscr.clear()  # Clear the screen
        if "py_midicsv" in sys.modules:
            stdscr.addstr(1, 1, "MIDI conversion is under development.")
            stdscr.refresh()
            stdscr.getch()  # Wait for user input to continue
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

    def _delete_song_menu(self, stdscr, notesheet_data, master_path):
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
                        NotesheetUtils().remove_song_from_notesheet(master_path, song_name)
                        stdscr.addstr(len(song_options) + 5, 1, f"Song '{song_name}' deleted successfully!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                        return True  # Deletion confirmed
                    else:
                        stdscr.addstr(len(song_options) + 5, 1, "Deletion canceled!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                        return False  # Deletion canceled

    def _credits_menu(self, stdscr):
        curses.curs_set(0)  # Hide the cursor
        stdscr.clear()
        stdscr.nodelay(1)

        # Credits art and text (unchanged from your original function)
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
        snake = [(5, 20), (5, 19), (5, 18)]  # Example initial snake body
        direction = None

        # Wait for arrow key press to set initial direction
        while direction is None:
            key = stdscr.getch()
            if key in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN]:
                direction = key

        count = 0
        # Game loop for snake movement and credits display
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

                    # Wait a short time before switching again (optional)
                    time.sleep(random.uniform(0.02, 0.4))

        curses.endwin()

    def _main_menu(self, stdscr):
        curses.curs_set(0)  # Hide the cursor
        stdscr.clear()
        stdscr.refresh()

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
                    notesheet_paths = config.get('DEFAULT', 'notesheet_paths')
                    notesheet_data = NotesheetUtils().parse_notesheet_file(notesheet_paths)
                    self._play_songs_menu(stdscr, notesheet_data)
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
        options = ["Change Notesheet Path", "Reset", "Go Back"]
        current_option = 0

        while True:
            stdscr.clear()
            for i, option in enumerate(options):
                if i == current_option:
                    stdscr.addstr(i + 1, 1, option, curses.A_REVERSE)
                    # Display current notesheet path to the right of "Change Notesheet Path" option
                    if i == 0:
                        config = Utils().load_config()
                        notesheet_path = config.get('DEFAULT', 'notesheet_paths')
                        stdscr.addstr(i + 1, len(option) + 3, f"Notesheet Path: {notesheet_path}")
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
                    # Change Notesheet Path
                    stdscr.addstr(3, 1, "Enter new notesheet path:")
                    stdscr.refresh()
                    curses.echo()  # Enable text input
                    new_path = stdscr.getstr(4, 1).decode(encoding="utf-8")
                    curses.noecho()  # Disable text input
                    config.set('DEFAULT', 'notesheet_paths', new_path)
                    with open(CONFIG_FILE_PATH, 'w') as configfile:
                        config.write(configfile)
                    stdscr.addstr(5, 1, "Notesheet path changed!")
                    stdscr.refresh()
                    stdscr.getch()  # Wait for user input to continue
                elif current_option == 1:
                    # Reset settings with confirmation
                    stdscr.addstr(3, 1, "Are you sure you want to reset? Type 'Yes!' to confirm: ")
                    stdscr.refresh()
                    curses.echo()  # Enable text input
                    confirmation = stdscr.getstr(4, 1).decode(encoding="utf-8")
                    curses.noecho()  # Disable text input
                    if confirmation.strip() == "Yes!":
                        Utils().create_default_config()
                        stdscr.addstr(5, 1, "Settings reset!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                    else:
                        stdscr.addstr(5, 1, "Reset canceled!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                elif current_option == 2:
                    # Go Back
                    return

    def start(self):
        curses.wrapper(self._main_menu)


def main():
    menu_manager = MenuManager()
    menu_manager.start()


if __name__ == "__main__":
    main()
