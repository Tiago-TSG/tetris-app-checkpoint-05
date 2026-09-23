import os

filepath = "/home/tiago/estudos/puc-minas/serverless-computing-and-arquiteturas-event-driven/checkpoint-03/static/js/game.js"
with open(filepath, "r") as f:
    content = f.read()

old_str = """        this.melodies = {
            'classic': [
                ['E5', 400], ['B4', 200], ['C5', 200], ['D5', 400], ['C5', 200], ['B4', 200],
                ['A4', 400], ['A4', 200], ['C5', 200], ['E5', 400], ['D5', 200], ['C5', 200],
                ['B4', 600], ['C5', 200], ['D5', 400], ['E5', 400],
                ['C5', 400], ['A4', 400], ['A4', 400], [0, 200],
                ['D5', 600], ['F5', 200], ['A5', 400], ['G5', 200], ['F5', 200],
                ['E5', 600], ['C5', 200], ['E5', 400], ['D5', 200], ['C5', 200],
                ['B4', 400], ['B4', 200], ['C5', 200], ['D5', 400], ['E5', 400],
                ['C5', 400], ['A4', 400], ['A4', 400], [0, 200]
            ],
            'star_wars': [
                ['A4', 500], ['A4', 500], ['A4', 500], ['F4', 350], ['C5', 150], ['A4', 500], ['F4', 350], ['C5', 150], ['A4', 650],
                ['E5', 500], ['E5', 500], ['E5', 500], ['F5', 350], ['C5', 150], ['G4', 500], ['F4', 350], ['C5', 150], ['A4', 650]
            ],
            'harry_potter': [
                ['B4', 400], ['E5', 600], ['G5', 200], ['F#5', 400], ['E5', 800], ['B5', 400], ['A5', 800], ['F#5', 1200],
                ['E5', 600], ['G5', 200], ['F#5', 400], ['D#5', 800], ['B4', 1200]
            ],
            'pink_panther': [
                ['C#5', 200], ['D5', 200], [0, 200], ['D#5', 200], ['E5', 400], [0, 200], ['C#5', 200], ['D5', 200], [0, 200], ['D#5', 200], ['E5', 400],
                ['G5', 200], ['F#5', 200], ['D5', 200], ['E5', 200], ['C#5', 400]
            ],
            'lord_of_the_rings': [
                ['D5', 400], ['A4', 200], ['B4', 200], ['A4', 400], ['G4', 200], ['A4', 200], ['D5', 800],
                ['D5', 400], ['A4', 200], ['B4', 200], ['A4', 400], ['E5', 400], ['D5', 400]
            ],
            'gameboy': [
                ['C4', 200], ['E4', 200], ['G4', 200], ['C5', 400], [0, 200], ['C5', 200], ['G4', 200], ['E4', 200], ['C4', 400],
                ['G4', 200], ['E4', 200], ['C4', 200], ['G3', 400]
            ],
            'cyberpunk': [
                ['A4', 100], ['A4', 100], ['C5', 100], ['A4', 100], ['G4', 100], ['A4', 100], ['C5', 100], ['A4', 100],
                ['A4', 100], ['A4', 100], ['C5', 100], ['A4', 100], ['F4', 100], ['A4', 100], ['C5', 100], ['A4', 100]
            ],
            'retro_future': [
                ['C5', 150], ['E5', 150], ['G5', 150], ['C6', 300], ['G5', 150], ['E5', 150], ['C5', 300],
                ['C5', 150], ['E5', 150], ['G5', 150], ['B5', 300], ['G5', 150], ['E5', 150], ['C5', 300]
            ]
        };
        this.currentMelody = this.melodies['classic'];

        // Mapeamento de Frequências (Hz) para Notas Musicais (Oitavas 4 e 5)
        this.frequencies = {
            'A4': 440.00, 'A#4': 466.16, 'B4': 493.88, 'C5': 523.25, 'C#5': 554.37,
            'D5': 587.33, 'D#5': 622.25, 'E5': 659.25, 'F5': 698.46, 'F#5': 739.99,
            'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'B5': 987.77, 'F4': 349.23, 'C4': 261.63
        };"""

with open('new_melodies.js', 'r') as mf:
    new_m = mf.read()
with open('freqs.json', 'r') as ff:
    new_f = ff.read()

# reformat new_f to be JS object string with matching indent
import json
f_dict = json.loads(new_f)
f_str = "        this.frequencies = {\n            "
items = []
for k, v in f_dict.items():
    items.append(f"'{k}': {v}")
# group by 5
grouped = []
for i in range(0, len(items), 5):
    grouped.append(", ".join(items[i:i+5]))
f_str += ",\n            ".join(grouped) + "\n        };"

new_str = new_m + "\n        this.currentMelody = this.melodies['classic'];\n\n        // Mapeamento de Frequências Completo (Oitavas 2 a 7)\n" + f_str

if old_str in content:
    with open(filepath, "w") as f:
        f.write(content.replace(old_str, new_str))
    print("Replaced successfully!")
else:
    print("Old string not found!")

