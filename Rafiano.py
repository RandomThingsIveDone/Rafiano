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
        print(
            "\nIf you are using the executable version of this program and this ERROR ocurs, open a GitHub issue with details.")
        print("GitHub: https://github.com/RandomThingsIveDone/Rafiano/issues")
        print("\nYou can continue to use the program, but MIDI conversion will not be available.")
        print("#" * 60 + "\n")
        print(
            "Big Thanks to Przemekkk for the MIDI conversion code, dont forget to look at his repo:\n    https://github.com/PrzemekkkYT/RaftMIDI \n")
        print("#" * 60 + "\n")
        input("Press Enter to continue...")

    elif module_name == 'pynput':
        print("\n" + "#" * 60)
        print("CRITICAL ERROR: Unable to import 'pynput' module.")
        print("This module is essential for the program to run.")
        print("\nPlease install it by running the following command:")
        print("    pip install pynput")
        print(
            "\nIf you are using the executable version of this program and this ERROR ocurs, open a GitHub issue with details.")
        print("GitHub: https://github.com/RandomThingsIveDone/Rafiano/issues")
        print("#" * 60 + "\n")
        input("Press Enter to continue...")
        exit(1)

CONFIG_FILE_PATH = "config.ini"


class Utils:
    """
    Utility class for handling configuration and other common tasks.
    """

    def __init__(self):
        pass

    @staticmethod
    def create_default_config(reset_config=False):
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
            config['DEFAULT'] = {'notesheet_path': 'Notesheets', 'master_notesheet': 'Master.notesheet'}

            # Write configuration to file
            with open(CONFIG_FILE_PATH, 'w') as configfile:
                config.write(configfile)

        # Read configuration values
        notesheet_path = config.get('DEFAULT', 'notesheet_path')
        master_notesheet = config.get('DEFAULT', 'master_notesheet')

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
            notesheet_filepath (str): The file path to the notesheet.
            song_name (str): The name of the song to be removed.

        Returns:
            None
        """
        notesheet_data = self.parse_notesheet_file(notesheet_folder_path)

        start_line = None
        end_line = None

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
      Parses a MIDI file in CSV format and extracts MIDI channels and rows of MIDI events.

    - filter_csv(rows, channels, selected):
      Filters MIDI CSV rows based on selected channels.

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
    def parse_midi(file_path):
        """
        Parses a MIDI file in CSV format and extracts MIDI channels and rows of MIDI events.

        Args:
        - file_path (str): The path to the MIDI file in CSV format.

        Returns:
        - sorted_channels (list): Sorted list of unique MIDI channels found in the file.
        - rows (list): List of rows representing MIDI events in CSV format.
        """
        midi_data = midi_to_csv(file_path)
        channels = set()
        rows = []

        for line in midi_data:
            parts = line.strip().split(", ")
            if parts[2] == "Note_on_c" or parts[2] == "Note_off_c":
                channels.add(int(parts[3]))

            rows.append(parts)

        return sorted(channels), rows

    @staticmethod
    def filter_csv(rows, channels, selected):
        """
        Filter MIDI CSV rows based on selected channels.

        Args:
        - rows (list): A list of MIDI CSV rows where each row is a list of strings.
        - channels (list): A list of MIDI channels corresponding to each row.
        - selected (list): A list of boolean values indicating whether each channel
          should be included in the filtered output.

        Returns:
        - list: A filtered list of MIDI CSV rows (strings) that match the selected
          channels. Each row is formatted as a comma-separated string.

        Notes:
        - The function iterates through each row in the 'rows' list and checks if
          the MIDI event type is 'Note_on_c' or 'Note_off_c'. If the MIDI channel
          of the event matches a channel marked as selected (True in 'selected'),
          the row is included in the filtered output.
        - Rows that do not match 'Note_on_c' or 'Note_off_c' or whose channel is
          not selected are also included in the filtered output.
        """
        selected_channels = {ch for ch, sel in zip(channels, selected) if sel}
        filtered_rows = []

        for row in rows:
            if len(row) >= 4 and row[2] in {"Note_on_c", "Note_off_c"}:
                channel = int(row[3])
                if channel in selected_channels:
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
        timestamps = {}
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
                            timestamps[record[1]] = []
                        else:
                            note = record[4]
                            index = self.find_unclosed_note_index(notes, note)
                            if index is not None and record[1] > notes[index][1]:
                                notes[index] = notes[index] + (record[1],)
                            timestamps[record[1]] = []
                    if record[2] == "note_off_c":
                        note = record[4]
                        index = self.find_unclosed_note_index(notes, note)
                        if index is not None and record[1] > notes[index][1]:
                            notes[index] = notes[index] + (record[1],)
                        timestamps[record[1]] = []
            except Exception as exc:
                self.handle_error(exc)

        timestamps = {ts: [] for ts in sorted(timestamps)}

        notes = [note for note in notes if len(note) == 3]
        notes = [(min(self.notes_to_keys, key=lambda x: abs(x - note[0])), *note[1:]) for note in notes]
        notes = sorted(notes, key=lambda x: x[1])

        for timestamp in timestamps:
            for note in notes:
                if note[1] == timestamp:
                    timestamps[timestamp].append((note[0], "start"))
                elif note[2] == timestamp:
                    timestamps[timestamp].append((note[0], "end"))

        timestamps = {key: sorted(value, key=lambda x: (x[1] == "start", x[1])) for key, value in timestamps.items()}

        return tpms, timestamps, notes

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

    def notesheet_v1(self, file_path, file_name, tpms, notes):
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
        with open(f"{file_path}/{file_name.split('/')[-1]}.notesheet", "w+") as notesheet:
            notesheet.write(
                f"|{file_name.split('/')[-1]}|RaftMIDI|1.0\n"
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


class NotesheetPlayer:
    """
    Class for playing notesheets based on different player versions.
    """

    def __init__(self):
        pass

    @staticmethod
    def _player_v1(song_notes: List[Dict]) -> bool:
        """
        Plays the notes of a given song by simulating key presses based on relative timings.

        Args:
            song_notes (List[Dict]): A list of dictionaries containing information about the song to be played.

        Returns:
            bool: True, if the song was played successfully.
        """
        keyboard = Controller()

        for note_dic in song_notes:
            keyboard.press(note_dic["modifier"])
            for note in note_dic["notes"]:
                keyboard.press(note)
            time.sleep(note_dic["press_time"])
            for note in note_dic["notes"]:
                keyboard.release(note)
            keyboard.release(note_dic["modifier"])
            time.sleep(note_dic["release_time"])

        return True

    @staticmethod
    def _player_v2(song_notes: List[Dict]) -> bool:
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

        songNotes = NotesheetUtils.notesheet_easy_convert(song_notes)

        start_time = time.time()
        for notes in songNotes:
            while time.time() - start_time < notes[0]:
                time.sleep(0.001)

            for note in notes[1:]:
                if _PressRelease[note]:
                    keyboard.release(note)
                    _PressRelease[note] = False
                else:
                    keyboard.press(note)
                    _PressRelease[note] = True

        return True

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

    @staticmethod
    def _play_songs_menu(stdscr, notesheet_data):
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
                    stdscr.addstr(10, 1,
                                  f"Playing : {notesheet_data[current_option]['name']} by: {notesheet_data[current_option]['creator']}")
                    stdscr.refresh()
                    for i in range(5, 0, -1):
                        stdscr.addstr(11, 1, str(i))
                        stdscr.refresh()
                        time.sleep(1)
                    NotesheetPlayer().play(notesheet_data[current_option]["notes"],
                                           notesheet_data[current_option]['version'])

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
        folder_path = config.get('DEFAULT', 'notesheet_path')  # Get the notesheet path from the configuration
        master_path = config.get('DEFAULT', 'master_notesheet')  # Get the notesheet path from the configuration

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
                    # TODO: remove Notesheet works now but its not pretty yet rework shoudld be done
                    # Remove Song
                    notesheet_data = NotesheetUtils().parse_notesheet_file(folder_path)
                    self._delete_song_menu(stdscr, notesheet_data, folder_path)
                elif current_option == 2:

                    self._export_notesheet_menu(stdscr, folder_path)

                elif current_option == 3:
                    # Add MIDI File
                    notesheet_path = config.get('DEFAULT', 'notesheet_path')
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
        output_path = f"{stdscr.getstr(4, 1).decode(encoding="utf-8").strip()}.notesheet"
        curses.noecho()  # Disable text input

        if not output_path:
            stdscr.addstr(5, 1, "Invalid output path. Please provide a valid path.")
            stdscr.refresh()
            stdscr.getch()  # Wait for user input to continue
            return

        notesheets = NotesheetUtils().list_notesheets(folder_path)

        #code to check if the ourput already exist if yes error lese create
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

            stdscr.addstr(1, 1, "Enter MIDI file name (e.g., Sandstorm.mid): ")
            stdscr.refresh()

            curses.echo()  # Enable text input
            input_file = stdscr.getstr(2, 1).decode(encoding="utf-8").strip()
            curses.noecho()  # Disable text input

            input_file_name = input_file.split(".")[0]  # Extract file name without extension

            try:
                channels, rows = MidiProcessor().parse_midi(input_file)
                midi_csv = midi_to_csv(input_file)

                # Further processing logic based on parsed MIDI data or CSV

                stdscr.addstr(3, 1, "MIDI file processed successfully!")
            except Exception as e:
                stdscr.addstr(3, 1, f"Error processing MIDI file: {str(e)}")
                stdscr.getch()
                return None

            curses.curs_set(0)  # Hide the cursor

            current_option = 0
            selected = [True] * len(channels)
            title = 'MIDI Channel Selection | Use up/down arrows to navigate, Enter to select channels and continue'

            while True:
                stdscr.clear()
                stdscr.addstr(1, 1, title, curses.A_BOLD)

                for i, channel in enumerate(channels):
                    option_text = f"Channel {channel} {'[x]' if selected[i] else '[ ]'}"
                    if i == current_option:
                        stdscr.addstr(i + 3, 1, "> " + option_text, curses.A_REVERSE)
                    else:
                        stdscr.addstr(i + 3, 1, "  " + option_text)

                # Option for continuing
                continue_text = "Continue"
                if current_option == len(channels):
                    stdscr.addstr(len(channels) + 3, 1, "> " + continue_text, curses.A_REVERSE)
                else:
                    stdscr.addstr(len(channels) + 3, 1, "  " + continue_text)

                stdscr.refresh()

                key = stdscr.getch()

                if key == curses.KEY_UP:
                    current_option = (current_option - 1) % (len(channels) + 1)
                elif key == curses.KEY_DOWN:
                    current_option = (current_option + 1) % (len(channels) + 1)
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    if current_option < len(channels):
                        selected[current_option] = not selected[current_option]
                    else:
                        break  # Break out of the loop to continue

            # filtered_rows = MidiProcessor().filter_csv(rows, channels, selected) not in use

            tpms, timestamps, notes = MidiProcessor().get_timestamps(midi_csv, selected)

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
                        # TODO: read title from MIDI and give this as the name of the notesheet

                        MidiProcessor().notesheet_v1(notesheet_path, input_file_name, tpms,
                                                     notes)  # Call function for Notesheet V1
                    elif current_option == 1:
                        # TODO: add function for Notesheet V2
                        # MidiProcessor().notesheet_v2()
                        stdscr.addstr(10, 1, "V2 not implemented yet.")
                        stdscr.getch()
                        break
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
                    notesheet_path = config.get('DEFAULT', 'notesheet_path')
                    notesheet_data = NotesheetUtils().parse_notesheet_file(notesheet_path)
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

    @staticmethod
    def _settings_menu(stdscr):
        config = Utils().load_config()
        options = ["Change Notesheet Path", "Change Notesheet Master", "Reset", "Go Back"]
        current_option = 0

        while True:
            stdscr.clear()
            for i, option in enumerate(options):
                if i == current_option:
                    stdscr.addstr(i + 1, 1, option, curses.A_REVERSE)
                    # Display current notesheet path to the right of "Change Notesheet Path" option
                    config = Utils().load_config()
                    if i == 0:
                        notesheet_path = config.get('DEFAULT', 'notesheet_path')
                        stdscr.addstr(1, 30, f"Notesheet Path: {notesheet_path}")

                    elif i == 1:
                        notesheet_master = config.get('DEFAULT', 'master_notesheet')
                        stdscr.addstr(1, 30, f"Notesheet Master: {notesheet_master}")

                    elif i == 2:
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
                    # Change Notesheet Path
                    stdscr.addstr(3, 1, "Enter new notesheet path:")
                    stdscr.refresh()
                    curses.echo()  # Enable text input
                    new_path = stdscr.getstr(4, 1).decode(encoding="utf-8")
                    curses.noecho()  # Disable text input
                    config.set('DEFAULT', 'notesheet_path', new_path)
                    with open(CONFIG_FILE_PATH, 'w') as configfile:
                        config.write(configfile)
                    stdscr.addstr(5, 1, "Notesheet path changed!")
                    stdscr.refresh()
                    stdscr.getch()  # Wait for user input to continue
                elif current_option == 1:
                    # Change Notesheet Path
                    stdscr.addstr(3, 1, "Enter new notesheet master path:")
                    stdscr.refresh()
                    curses.echo()  # Enable text input
                    new_path = stdscr.getstr(4, 1).decode(encoding="utf-8")
                    curses.noecho()  # Disable text input
                    config.set('DEFAULT', 'master_notesheet', new_path)
                    with open(CONFIG_FILE_PATH, 'w') as configfile:
                        config.write(configfile)
                    stdscr.addstr(5, 1, "Notesheet master path changed!")
                    stdscr.refresh()
                    stdscr.getch()  # Wait for user input to continue
                elif current_option == 2:
                    # Reset settings with confirmation
                    stdscr.addstr(3, 1, "Are you sure you want to reset? Type 'Yes!' to confirm: ")
                    stdscr.refresh()
                    curses.echo()  # Enable text input
                    confirmation = stdscr.getstr(4, 1).decode(encoding="utf-8")
                    curses.noecho()  # Disable text input
                    if confirmation.strip() == "Yes!":
                        Utils().create_default_config(True)
                        stdscr.addstr(5, 1, "Settings reset!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                    else:
                        stdscr.addstr(5, 1, "Reset canceled!")
                        stdscr.refresh()
                        stdscr.getch()  # Wait for user input to continue
                elif current_option == 3:
                    # Go Back
                    return

    def start(self):
        curses.wrapper(self._main_menu)


def main():
    Utils.create_default_config()
    menu_manager = MenuManager()
    menu_manager.start()


if __name__ == "__main__":
    main()
