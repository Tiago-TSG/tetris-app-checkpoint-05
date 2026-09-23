import json

def parse_melody(melody_str, bpm):
    beat_ms = 60000 / bpm
    notes_list = []
    
    tokens = melody_str.replace('|', '').split()
    for token in tokens:
        if ':' not in token:
            continue
        pitch, length = token.split(':')
        
        # Calculate duration
        is_dotted = '.' in length
        is_triplet = 't' in length
        
        base_len_str = length.replace('.', '').replace('t', '')
        if not base_len_str:
            continue
            
        base_len = int(base_len_str)
        # 4 means 1 beat. duration in beats = 4 / base_len
        beats = 4.0 / base_len
        
        if is_dotted:
            beats *= 1.5
        if is_triplet:
            beats *= 0.666666666
            
        duration_ms = int(beats * beat_ms)
        
        if pitch == 'r':
            notes_list.append([0, duration_ms])
        else:
            notes_list.append([pitch, duration_ms])
            
    return notes_list

melodies = {}

# 1. Tetris (Korobeiniki) - BPM 150
tetris_str = """
E5:4 B4:8 C5:8 D5:4 C5:8 B4:8 | A4:4 A4:8 C5:8 E5:4 D5:8 C5:8 |
B4:4. C5:8 D5:4 E5:4 | C5:4 A4:4 A4:2 | r:4
D5:4. F5:8 A5:4 G5:8 F5:8 | E5:4. C5:8 E5:4 D5:8 C5:8 |
B4:4 B4:8 C5:8 D5:4 E5:4 | C5:4 A4:4 A4:2 | r:4

E5:4 B4:8 C5:8 D5:4 C5:8 B4:8 | A4:4 A4:8 C5:8 E5:4 D5:8 C5:8 |
B4:4. C5:8 D5:4 E5:4 | C5:4 A4:4 A4:2 | r:4
D5:4. F5:8 A5:4 G5:8 F5:8 | E5:4. C5:8 E5:4 D5:8 C5:8 |
B4:4 B4:8 C5:8 D5:4 E5:4 | C5:4 A4:4 A4:2 | r:4

E4:2 C4:2 | D4:2 B3:2 | C4:2 A3:2 | G#3:2 B3:2 |
E4:2 C4:2 | D4:2 B3:2 | C4:4 E4:4 A4:2 | G#4:2 r:2
"""
melodies['classic'] = parse_melody(tetris_str, 150)

# 2. Lord of the Rings (Concerning Hobbits) - BPM 90
lotr_str = """
D4:8 E4:8 |
G4:4 E4:8 D4:8 B3:4 | D4:2 r:8 D4:8 E4:8 |
G4:4 A4:8 B4:8 A4:8 G4:8 | E4:4 G4:4. r:8 D4:8 E4:8 |
G4:4 E4:8 D4:8 B3:4 | D4:2 r:8 G4:8 A4:8 |
B4:4 D5:8 B4:8 A4:8 G4:8 | A4:2 r:4 D4:8 E4:8 |

G4:4 E4:8 D4:8 B3:4 | D4:2 r:8 D4:8 E4:8 |
G4:4 A4:8 B4:8 A4:8 G4:8 | E4:4 G4:4. r:8 D4:8 E4:8 |
G4:4 E4:8 D4:8 B3:4 | D4:2 r:8 G4:8 A4:8 |
B4:4 D5:8 B4:8 A4:8 G4:8 | A4:2 r:4 G4:8 A4:8 |

B4:4. B4:8 B4:4 C5:4 | B4:4 A4:4 G4:4 F#4:4 |
E4:2 G4:2 | D4:1 |
B4:4. B4:8 B4:4 C5:4 | B4:4 A4:4 G4:4 A4:4 |
B4:4 D5:4 E5:2 | D5:1
"""
melodies['lord_of_the_rings'] = parse_melody(lotr_str, 90)

# 3. Star Wars (Main Theme) - BPM 108
sw_str = """
G4:4t G4:4t G4:4t | C5:2 G5:2 |
F5:4t E5:4t D5:4t C6:2 G5:4 |
F5:4t E5:4t D5:4t C6:2 G5:4 |
F5:4t E5:4t F5:4t D5:2 r:4 G4:4t G4:4t G4:4t |

C5:2 G5:2 |
F5:4t E5:4t D5:4t C6:2 G5:4 |
F5:4t E5:4t D5:4t C6:2 G5:4 |
F5:4t E5:4t F5:4t D5:2
"""
melodies['star_wars'] = parse_melody(sw_str, 108)

# 4. Harry Potter (Hedwig's Theme) - BPM 160 (3/4 time)
hp_str = """
B4:4 |
E5:4. G5:8 F#5:4 | E5:2 B5:4 | A5:2. | F#5:2. |
E5:4. G5:8 F#5:4 | D#5:2 F5:4 | B4:2. | r:2 B4:4 |
E5:4. G5:8 F#5:4 | E5:2 B5:4 | D6:2 C#6:4 | C6:2 G#5:4 |
C6:4. B5:8 A#5:4 | A#4:2 G5:4 | E5:2. | r:2 G5:4 |

B5:4. G5:8 B5:4 | B5:4. G5:8 B5:4 | D6:2 C#6:4 | C6:2 G#5:4 |
C6:4. B5:8 A#5:4 | A#4:2 G5:4 | B5:2. | r:2 G5:4 |
B5:4. G5:8 B5:4 | B5:4. G5:8 B5:4 | D6:2 C#6:4 | C6:2 G#5:4 |
C6:4. B5:8 A#5:4 | A#4:2 G5:4 | E5:2.
"""
melodies['harry_potter'] = parse_melody(hp_str, 160)

# 5. Pink Panther - BPM 120
pp_str = """
C#4:8 D4:8 r:4 D#4:8 E4:8 r:4 |
C#4:8 D4:8 D#4:8 E4:8 G4:8 F#4:8 D4:8 E4:4. r:8 |
C#4:16 D4:16 D#4:16 E4:16 G4:8 F#4:8 D4:8 E4:8 B4:8 G4:8 | B4:8 E5:4. r:2 |

C#4:8 D4:8 r:4 D#4:8 E4:8 r:4 |
C#4:8 D4:8 D#4:8 E4:8 G4:8 F#4:8 D4:8 E4:4. r:8 |
C#4:16 D4:16 D#4:16 E4:16 G4:8 F#4:8 D4:8 E4:8 B4:8 G4:8 | B4:8 E5:4. r:2
"""
melodies['pink_panther'] = parse_melody(pp_str, 110)

# 6. Gameboy (Super Mario Bros Overworld Theme intro + part A) - BPM 200
gb_str = """
E5:8 E5:8 r:8 E5:8 r:8 C5:8 E5:4 | G5:4 r:4 G4:4 r:4 |
C5:4. G4:4. E4:4 | r:8 A4:4 B4:4 A#4:8 A4:4 |
G4:4t E5:4t G5:4t A5:4 F5:8 G5:8 | r:8 E5:4 C5:8 D5:8 B4:4. |
C5:4. G4:4. E4:4 | r:8 A4:4 B4:4 A#4:8 A4:4 |
G4:4t E5:4t G5:4t A5:4 F5:8 G5:8 | r:8 E5:4 C5:8 D5:8 B4:4.
"""
melodies['gameboy'] = parse_melody(gb_str, 200)

# 7. Cyberpunk (Synthwave fast loop) - BPM 130
cp_str = """
A3:16 E4:16 A4:16 E4:16 C4:16 E4:16 A4:16 E4:16 |
A3:16 E4:16 A4:16 E4:16 C4:16 E4:16 A4:16 E4:16 |
F3:16 C4:16 F4:16 C4:16 A3:16 C4:16 F4:16 C4:16 |
G3:16 D4:16 G4:16 D4:16 B3:16 D4:16 G4:16 D4:16 |
A3:16 E4:16 A4:16 E4:16 C4:16 E4:16 A4:16 E4:16 |
A3:16 E4:16 A4:16 E4:16 C4:16 E4:16 A4:16 E4:16 |
F3:16 C4:16 F4:16 C4:16 A3:16 C4:16 F4:16 C4:16 |
G3:16 D4:16 G4:16 D4:16 B3:16 D4:16 G4:16 D4:16
"""
melodies['cyberpunk'] = parse_melody(cp_str, 130)

# 8. Retro Future (Stranger Things style arpeggio) - BPM 160
rf_str = """
C3:8 E3:8 G3:8 B3:8 C4:8 B3:8 G3:8 E3:8 |
C3:8 E3:8 G3:8 B3:8 C4:8 B3:8 G3:8 E3:8 |
A2:8 C3:8 E3:8 G3:8 A3:8 G3:8 E3:8 C3:8 |
F2:8 A2:8 C3:8 E3:8 F3:8 E3:8 C3:8 A2:8 |
C3:8 E3:8 G3:8 B3:8 C4:8 B3:8 G3:8 E3:8 |
C3:8 E3:8 G3:8 B3:8 C4:8 B3:8 G3:8 E3:8 |
A2:8 C3:8 E3:8 G3:8 A3:8 G3:8 E3:8 C3:8 |
F2:8 A2:8 C3:8 E3:8 F3:8 E3:8 C3:8 A2:8
"""
melodies['retro_future'] = parse_melody(rf_str, 160)


def fmt_melody(m):
    lines = []
    for i in range(0, len(m), 6):
        chunk = m[i:i+6]
        str_chunk = ", ".join(f"['{n}', {d}]" if n != 0 else f"[0, {d}]" for n, d in chunk)
        lines.append("                " + str_chunk)
    return "[\n" + ",\n".join(lines) + "\n            ]"

out = "this.melodies = {\n"
for k, v in melodies.items():
    out += f"            '{k}': " + fmt_melody(v) + ",\n"
out = out.rstrip(",\n") + "\n        };"


import os
filepath = "/home/tiago/estudos/puc-minas/serverless-computing-and-arquiteturas-event-driven/checkpoint-03/static/js/game.js"
with open(filepath, "r") as f:
    content = f.read()

import re
# Find the this.melodies block
pattern = re.compile(r"this\.melodies = \{.*?\n        \};", re.DOTALL)
if pattern.search(content):
    new_content = pattern.sub(out, content)
    with open(filepath, "w") as f:
        f.write(new_content)
    print("Replaced successfully!")
else:
    print("Block not found!")

