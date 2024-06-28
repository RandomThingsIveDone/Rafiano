
```css
8888888b.            .d888 d8b
888   Y88b          d88P"  Y8P
888    888          888
888   d88P  8888b.  888888 888  8888b.  88888b.   .d88b.
8888888P"      "88b 888    888     "88b 888 "88b d88""88b
888 T88b   .d888888 888    888 .d888888 888  888 888  888
888  T88b  888  888 888    888 888  888 888  888 Y88..88P
888   T88b "Y888888 888    888 "Y888888 888  888  "Y88P"
```
---


<div style="display: flex; align-items: center;">
  <img src="https://raw.githubusercontent.com/RandomThingsIveDone/Rafiano/main/ico/Rafiano-Circle.png" align="right"
     alt="Rafiano" width="200" height="200">
  
<br><br>**Rafiano** enhances the piano experience in the game RAFT,<br>
allowing you to play piano songs effortlessly using a predefined Notesheet file.<br>
Whether you're a music enthusiast or simply looking to prank a friend,<br>
Rafiano brings creativity and enjoyment to **RAFT**.
</div>

<br>


## How to Use

### Using the Executable (Windows)

1. **Download:**
   - Download the latest release from the [GitHub Releases](https://github.com/RandomThingsIveDone/Rafiano/releases) page.
   - Extract the contents of the ZIP file to a convenient location.

2. **Run:**
   - Double-click `rafiano.exe` to start the application.
   - Follow the on-screen instructions to select a song from your Notesheet file.

- - -
### Using the Python Script 

1. **Prerequisites:**
   - Ensure Python 3.x is installed on your system.
   - Install dependencies by running:
     ```
     pip install pynput py_midicsv windows-curses
     ```

2. **Download:**
   - Clone or download the Rafiano repository from [GitHub](https://github.com/RandomThingsIveDone/Rafiano).

3. **Setup:**
   - Navigate to the Rafiano directory.

4. **Run:**
   - Open a terminal or command prompt.
   - Navigate to the Rafiano directory.
   - Run the script using Python:
     ```
     python rafiano.py
     ```
   - Follow the console instructions to select a song from your Notesheet file.
- - -
### Compiling the .exe with PyInstaller

1. **Install PyInstaller:**
   Ensure you have PyInstaller installed. You can install it via pip if you haven't already:
   ```
   pip install pyinstaller
   ```

2. **Download:**
   - Clone or download the Rafiano repository from [GitHub](https://github.com/RandomThingsIveDone/Rafiano).
  
3. **Setup:**
   - Navigate to the Rafiano directory.

4. **Run:**
   - Open a terminal or command prompt.
   - Navigate to the Rafiano directory.
   - Run the script using Python:
     ```
     pyinstaller -F --icon=ico/Rafiano-Circle.ico Rafiano.py
     ```



## Notesheets

Rafiano reads a Notesheet file and allows you to play the songs saved within it. The Notesheet format supports both Version 1.0 and Version 2.0.

### Example Notesheet Song

*(A Wiki song from [Raft Piano Sheet Music](https://raft.fandom.com/wiki/Raft_Piano_Sheet_Music) converted to a Notesheet)*

```basic
|Bella Ciao|wiki|1.0
0  0.1 0.1
9  0.1 0.1
0  0.1 0.1
4 SH 0.1 0.1
4 SH 0.6 0.1
#
...
```

### Notesheet Format

1. **Header:** `Songname|creator|version`
2. **Notes:** Each line contains notes in the following format:
   - **Single Key:** `0  0.1 0.5` (Key "0" for 0.1 seconds, wait 0.5 seconds)
   - **Multiple Keys:** `0|5  0.2 0.3` (Keys "0" and "5" for 0.2 seconds, wait 0.3 seconds)
   - **With Shift:** `3|6 SH 0.3 0.3` (Keys "3" and "6" with Shift for 0.3 seconds, wait 0.3 seconds)
   - **With Space:** `9 SP 0.2 0.2` (Key "9" with Space for 0.2 seconds, wait 0.2 seconds)
3. **Comments:** Use `#` to add comments. Everything after "#" is ignored.

### Notesheet Versions

- **Version 1.0:** Uses individual timings for each note.
- **Version 2.0:** Uses global timing relative to the start of the song.

### Example Notesheet Song (Version 2.0)

```basic
|HappyBirthday|wiki|2.0
1  0.1 0.2
1  0.3 0.4
2  1.0 1.1
1  1.7 1.8
4  1.9 2.0
3  2.7 2.8
#
1  2.9 3.0
1  3.1 3.2
2  3.7 3.8
1  4.4 4.5
5  4.6 4.7
4  5.3 5.4
...
```

#### Explanation of Version 2.0:

- **Global Timing:** Each note's timing is calculated from the start of the song, ensuring consistent timing regardless of the previous notes' durations.
---

## Configuration (config.ini)

In `config.ini`, you can configure settings such as:
- Path to the Notesheet file or folder containing Notesheets.
- Other customizable settings to enhance your Rafiano experience.

---

## Usage

- Select a song from your Notesheet file within 5 seconds after starting Rafiano.
- Enjoy as Rafiano simulates the key presses to play the song in RAFT.

---

## Contributions

Contributions and feedback are welcome! If you have any improvements or suggestions, feel free to open an issue or a pull request on [GitHub](https://github.com/RandomThingsIveDone/Rafiano).


```python
Credits

RandomThingsIveDone: Menu Coding and Notesheet format         https://github.com/RandomThingsIveDone/Rafiano
PrzemekkkYT: MIDI conversion code and song added              https://github.com/PrzemekkkYT/RaftMIDI
STALKER666YT: added new songs                                 https://github.com/STALKER666YT/Rafiano-UPDATED-
```
---

By using Rafiano, you can easily play your favorite songs on RAFT with a simple Notesheet file. Happy playing!

For more information and updates, visit our [GitHub repository](https://github.com/RandomThingsIveDone/Rafiano).

---
