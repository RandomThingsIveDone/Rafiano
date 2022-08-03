# Rafiano
---
## Notesheet's
The script reads the Notsheet file and let's you play the songs that are in that file saved.

This is a Notesheet example: 

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

the nex lines are the notes, here are some examples how they can be used

to play the piano key "0" for 0.1 sekunden and wait for 0.5 sekund to play the next note it would look like this:

```0  0.1 0.5```

to play the piano key "0" and "5" simutanisly for 0.2 sekunden and wait for 0.3 sekund to play the next note it would look like this:

`0|5  0.2 0.3`

to play the piano key "3" and "6" simutanisly while holding shift for 0.3 sekunden and wait for 0.3 sekund to play the next note it would look like this:

`3|6 SH 0.3 0.3`

to play the piano key "9"  while holding Space for 0.2 sekunden and wait for 0.2 sekund to play the next note it would look like this:

`9 SP 0.2 0.2`
