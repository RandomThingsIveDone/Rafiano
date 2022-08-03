'''
8888888b.            .d888 d8b
888   Y88b          d88P"  Y8P
888    888          888
888   d88P  8888b.  888888 888  8888b.  88888b.   .d88b.
8888888P"      "88b 888    888     "88b 888 "88b d88""88b
888 T88b   .d888888 888    888 .d888888 888  888 888  888
888  T88b  888  888 888    888 888  888 888  888 Y88..88P
888   T88b "Y888888 888    888 "Y888888 888  888  "Y88P"
'''


import re
import sys
import time

from pick import pick
from pynput.keyboard import Key, Controller


def notesheet_security(notesheet):
    notesheet = notesheet.split("\n")

    for line in notesheet:

        if line[0] == "#" or line == "" or line[0] == "|":
            continue

        if not bool(re.match(r'([0-9.\s|]|SH|SP)*$', line.upper())):
            print("Notesheet uses invalid characters.")
            time.sleep(3)
            sys.exit()


def notesheet_reader(notesheet):
    read_notesheet = False
    song_dict = {}
    song_data = []
    song_notes = []

    notesheet_security(notesheet)

    notesheet = notesheet.split("\n")
    for line in notesheet:

        if line == "" or line[0] == "#":
            continue

        if line[0] == "|":

            if read_notesheet:
                song_dict["notes"] = song_notes
                song_data.append(song_dict)

            read_notesheet = True
            data = line.split("|")
            song_dict = {"name": data[1], "creator": data[2]}
            song_notes = []

        elif read_notesheet:
            split_notes = line.split(" ")
            if split_notes[1].upper() == "":
                modifier_note = Key.up
            elif split_notes[1].upper() == "SH":
                modifier_note = Key.shift
            elif split_notes[1].upper() == "SP":
                modifier_note = Key.space
            else:
                raise Exception("No valid modifier")

            song_notes.append({"notes": split_notes[0].split("|"),
                               "modifier": modifier_note,
                               "press_time": float(split_notes[2]),
                               "release_time": float(split_notes[3])
                               })

    song_dict["notes"] = song_notes
    song_data.append(song_dict)
    return song_data


def player(notepage):
    keyboard = Controller()
    for note_dic in notepage:
        keyboard.press(note_dic["modifier"])
        for note in note_dic["notes"]:
            keyboard.press(note)
        time.sleep(note_dic["press_time"])
        for note in note_dic["notes"]:
            keyboard.release(note)
        keyboard.release(note_dic["modifier"])
        time.sleep(note_dic["release_time"])


if __name__ == "__main__":
    with open("Notesheet", 'r', encoding='utf-8') as f:
        notesheet_data = notesheet_reader(f.read())
    indicator = ">>>"
    while True:
        # TODO add Settings
        title: str = 'Rafiano | use up and down arrows for controlling'

        main_menu_options = [x["name"] + " by " + x["creator"] for x in notesheet_data]
        main_index = pick(main_menu_options, title, indicator)
        print(main_index)
        print(f"Playing : {notesheet_data[main_index[1]]['name']} by: {notesheet_data[main_index[1]]['creator']}")
        for i in range(5, 0, -1):
            print(i)
            time.sleep(1)
        player(notesheet_data[main_index[1]]["notes"])
