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

# Importing required libraries
from typing import List, Dict, Union
import re
import time
from pick import pick
from pynput.keyboard import Key, Controller


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


def parse_notesheet(notesheet: str) -> List[Dict[str, Union[str, List[Dict[str, Union[List[str], Key, float, float]]]]]]:
    """
    Parses the notesheet and returns a list of dictionaries, where each dictionary represents a song with its name, creator and notes.

    Args:
        notesheet (str): The notesheet to be parsed.

    Returns:
        list: A list of dictionaries, where each dictionary represents a song with its name, creator and notes.

    Raises:
        Exception: If the notesheet contains invalid modifier, release/press time values or invalid characters.
    """
    # Initialize variables to store song information
    read_notesheet = False
    current_song = {}
    all_songs = []
    current_song_notes = []

    # Validate the notesheet before parsing
    if not validate_notesheet(notesheet):
        raise Exception("Notesheet uses invalid characters")

    # Split the notesheet string into individual lines
    notesheet = notesheet.split("\n")

    # Loop through each line of the notesheet
    for notesheet_line in notesheet:

        # Ignore comment lines and empty lines
        if notesheet_line == "" or notesheet_line.startswith("#"):
            continue

        # If a song header line is found, start a new song
        elif notesheet_line.startswith("|"):

            # If already read song information, append to list
            if read_notesheet:
                current_song["notes"] = current_song_notes
                all_songs.append(current_song)

            # Set variables for new song
            read_notesheet = True
            song_info = notesheet_line.split("|")
            current_song = {"name": song_info[1], "creator": song_info[2]}
            current_song_notes = []

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
    # Add last song to list
    current_song["notes"] = current_song_notes
    all_songs.append(current_song)
    return all_songs


def player(song_notes: Dict[str, Union[str, List[Dict[str, Union[List[str], Key, float, float]]]]]) -> bool:
    """
    Plays the notes of a given song by simulating key presses.

    Args:
        song_notes (Dict[str, Union[str, List[Dict[str, Union[List[str], Key, float, float]]]]]): A dictionary containing information about the song to be played.

    Returns:
        bool: True, if the song was played successfully.

    Raises:
        None: This function does not raise any exceptions.
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


def main():
    """
    The main function that runs the program.

    Args:
        None

    Returns:
        None

    Raises:
        None: This function does not raise any exceptions.
    """
    with open("Notesheet", 'r', encoding='utf-8') as f:
        notesheet_data = parse_notesheet(f.read())

    menu_indicator = ">>>"
    while True:
        # TODO add Settings
        title: str = 'Rafiano | use up and down arrows for controlling'

        main_menu_options = [x["name"] + " by " + x["creator"] for x in notesheet_data]
        main_index = pick(main_menu_options, title, menu_indicator)
        print(main_index)
        print(f"Playing : {notesheet_data[main_index[1]]['name']} by: {notesheet_data[main_index[1]]['creator']}")
        for i in range(5, 0, -1):
            print(i)
            time.sleep(1)
        player(notesheet_data[main_index[1]]["notes"])


if __name__ == "__main__":
    main()
