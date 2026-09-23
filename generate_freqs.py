notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
A4 = 440.0
A4_index = 4 * 12 + 9 # 57

freqs = {}
for octave in range(2, 8):
    for i, note in enumerate(notes):
        note_index = octave * 12 + i
        distance = note_index - A4_index
        freq = A4 * (2 ** (distance / 12.0))
        freqs[f"{note}{octave}"] = round(freq, 2)

import json
print(json.dumps(freqs, indent=4))
