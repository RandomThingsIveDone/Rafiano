# Rafiano

---
# I TAKE NO RESPONSIBILITY FOR ANYTHING DONE WITH/FROM THE SCRIPT 
---

## How it work's

After you selected a song to play, the script gives you 5 seconds to maximize RAFT.
After the 5-seconds pass, it emulates you pressing the right keys.

Right now, there is no way to stop the script except for closing it.

## Notesheet's
The script reads the Notsheet file and lets you play the songs that are in that file saved.

This is a Notesheet song example: 

(A Wiki song from https://raft.fandom.com/wiki/Raft_Piano_Sheet_Music that I converted to a Notesheet)

```
|Bella Ciao|wiki|1.0
0  0.1 0.1
9  0.1 0.1
0  0.1 0.1
4 SH 0.1 0.1
4 SH 0.6 0.1
#
4 SH 0.1 0.1
0  0.1 0.1
9  0.1 0.1
4 SH 0.1 0.1
0  0.6 0.1
#
0  0.1 0.1
9  0.1 0.1
8  0.1 0.1
7  0.1 0.1
0  0.1 0.1
8  0.1 0.1
7  0.1 0.1
6  0.6 0.1
#
3  0.1 0.1
6  0.1 0.1
7  0.1 0.1
8  0.1 0.1
6  0.6 0.1
#
3  0.1 0.1
6  0.1 0.1
7  0.1 0.1
8  0.1 0.1
6  0.6 0.1
#
3  0.1 0.1
6  0.1 0.1
7  0.1 0.1
8  0.3 0.1
7  0.1 0.1
6  0.1 0.1
8  0.3 0.1
7  0.1 0.1
6  0.1 0.1
0  0.1 0.1
0  0.1 0.1
0  0.1 0.1
#
0  0.1 0.1
9  0.1 0.1
0  0.1 0.1
4 SH 0.1 0.1
4 SH 0.6 0.1
#
4 SH 0.1 0.1
0  0.1 0.1
9  0.1 0.1
4 SH 0.1 0.1
0  0.6 0.1
#
0  0.1 0.1
9  0.1 0.1
8  0.1 0.1
7  0.1 0.1
0  0.1 0.1
8  0.1 0.1
7  0.1 0.1
6  0.6 0.1
#
3  0.1 0.1
6  0.1 0.1
7  0.1 0.1
8  0.1 0.1
6  0.6 0.1
#
3  0.1 0.1
6  0.1 0.1
7  0.1 0.1
8  0.1 0.1
6  0.6 0.1
#
3  0.1 0.1
6  0.1 0.1
7  0.1 0.1
8  0.3 0.1
7  0.1 0.1
6  0.1 0.1
8  0.3 0.1
7  0.1 0.1
6  0.1 0.1
0  0.1 0.1
0  0.1 0.1
0  0.1 0.1
```
The first Line is the:

`Songname|creator|which version of Notesheet is used (not in use right now)`

the next lines are the notes, here are some examples how they can be used:

to play the piano key "0" for 0.1 seconds and wait for 0.5 seconds to play the next note, it would look like this:                                           
```0  0.1 0.5```

to play the piano key "0" and "5" simultaneously for 0.2 seconds and wait for 0.3 seconds to play the next note, it would look like this:                    
`0|5  0.2 0.3`

to play the piano key "3" and "6" simultaneously while holding shift for 0.3 seconds and wait for 0.3 seconds to play the next note, it would look like this: 
`3|6 SH 0.3 0.3`

to play the piano key "9"  while holding Space for 0.2 seconds and wait for 0.2 seconds to play the next note, it would look like this:  
`9 SP 0.2 0.2`

A "#" is a comment.
`# everything after "#" is ignored`

A Notesheet can contain multiple Songs see Notesheet
[example](https://github.com/RandomThingsIveDone/Rafiano/blob/main/Notesheet).
