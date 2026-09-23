/**
 * Retro Neon Tetris - Core Game Engine & Audio Synthesizer
 */

// ============================================================================
// 1. GERENCIADOR DE ÁUDIO SINTETIZADO (Web Audio API)
// ============================================================================
class SoundManager {
    constructor() {
        this.ctx = null;
        this.musicEnabled = false;
        this.soundEnabled = true;
        this.musicInterval = null;
        this.musicStep = 0;
        
        // Sequência de notas da melodia clássica do Tetris (Korobeiniki) em A menor
        // Formato: [nota, duração em ms] - 0 representa pausa
this.melodies = {
            'classic': [
                ['E5', 400], ['B4', 200], ['C5', 200], ['D5', 400], ['C5', 200], ['B4', 200],
                ['A4', 400], ['A4', 200], ['C5', 200], ['E5', 400], ['D5', 200], ['C5', 200],
                ['B4', 600], ['C5', 200], ['D5', 400], ['E5', 400], ['C5', 400], ['A4', 400],
                ['A4', 800], [0, 400], ['D5', 600], ['F5', 200], ['A5', 400], ['G5', 200],
                ['F5', 200], ['E5', 600], ['C5', 200], ['E5', 400], ['D5', 200], ['C5', 200],
                ['B4', 400], ['B4', 200], ['C5', 200], ['D5', 400], ['E5', 400], ['C5', 400],
                ['A4', 400], ['A4', 800], [0, 400], ['E5', 400], ['B4', 200], ['C5', 200],
                ['D5', 400], ['C5', 200], ['B4', 200], ['A4', 400], ['A4', 200], ['C5', 200],
                ['E5', 400], ['D5', 200], ['C5', 200], ['B4', 600], ['C5', 200], ['D5', 400],
                ['E5', 400], ['C5', 400], ['A4', 400], ['A4', 800], [0, 400], ['D5', 600],
                ['F5', 200], ['A5', 400], ['G5', 200], ['F5', 200], ['E5', 600], ['C5', 200],
                ['E5', 400], ['D5', 200], ['C5', 200], ['B4', 400], ['B4', 200], ['C5', 200],
                ['D5', 400], ['E5', 400], ['C5', 400], ['A4', 400], ['A4', 800], [0, 400],
                ['E4', 800], ['C4', 800], ['D4', 800], ['B3', 800], ['C4', 800], ['A3', 800],
                ['G#3', 800], ['B3', 800], ['E4', 800], ['C4', 800], ['D4', 800], ['B3', 800],
                ['C4', 400], ['E4', 400], ['A4', 800], ['G#4', 800], [0, 800]
            ],
            'lord_of_the_rings': [
                ['D4', 333], ['E4', 333], ['G4', 666], ['E4', 333], ['D4', 333], ['B3', 666],
                ['D4', 1333], [0, 333], ['D4', 333], ['E4', 333], ['G4', 666], ['A4', 333],
                ['B4', 333], ['A4', 333], ['G4', 333], ['E4', 666], ['G4', 1000], [0, 333],
                ['D4', 333], ['E4', 333], ['G4', 666], ['E4', 333], ['D4', 333], ['B3', 666],
                ['D4', 1333], [0, 333], ['G4', 333], ['A4', 333], ['B4', 666], ['D5', 333],
                ['B4', 333], ['A4', 333], ['G4', 333], ['A4', 1333], [0, 666], ['D4', 333],
                ['E4', 333], ['G4', 666], ['E4', 333], ['D4', 333], ['B3', 666], ['D4', 1333],
                [0, 333], ['D4', 333], ['E4', 333], ['G4', 666], ['A4', 333], ['B4', 333],
                ['A4', 333], ['G4', 333], ['E4', 666], ['G4', 1000], [0, 333], ['D4', 333],
                ['E4', 333], ['G4', 666], ['E4', 333], ['D4', 333], ['B3', 666], ['D4', 1333],
                [0, 333], ['G4', 333], ['A4', 333], ['B4', 666], ['D5', 333], ['B4', 333],
                ['A4', 333], ['G4', 333], ['A4', 1333], [0, 666], ['G4', 333], ['A4', 333],
                ['B4', 1000], ['B4', 333], ['B4', 666], ['C5', 666], ['B4', 666], ['A4', 666],
                ['G4', 666], ['F#4', 666], ['E4', 1333], ['G4', 1333], ['D4', 2666], ['B4', 1000],
                ['B4', 333], ['B4', 666], ['C5', 666], ['B4', 666], ['A4', 666], ['G4', 666],
                ['A4', 666], ['B4', 666], ['D5', 666], ['E5', 1333], ['D5', 2666]
            ],
            'star_wars': [
                ['G4', 370], ['G4', 370], ['G4', 370], ['C5', 1111], ['G5', 1111], ['F5', 370],
                ['E5', 370], ['D5', 370], ['C6', 1111], ['G5', 555], ['F5', 370], ['E5', 370],
                ['D5', 370], ['C6', 1111], ['G5', 555], ['F5', 370], ['E5', 370], ['F5', 370],
                ['D5', 1111], [0, 555], ['G4', 370], ['G4', 370], ['G4', 370], ['C5', 1111],
                ['G5', 1111], ['F5', 370], ['E5', 370], ['D5', 370], ['C6', 1111], ['G5', 555],
                ['F5', 370], ['E5', 370], ['D5', 370], ['C6', 1111], ['G5', 555], ['F5', 370],
                ['E5', 370], ['F5', 370], ['D5', 1111]
            ],
            'harry_potter': [
                ['B4', 375], ['E5', 562], ['G5', 187], ['F#5', 375], ['E5', 750], ['B5', 375],
                ['A5', 1125], ['F#5', 1125], ['E5', 562], ['G5', 187], ['F#5', 375], ['D#5', 750],
                ['F5', 375], ['B4', 1125], [0, 750], ['B4', 375], ['E5', 562], ['G5', 187],
                ['F#5', 375], ['E5', 750], ['B5', 375], ['D6', 750], ['C#6', 375], ['C6', 750],
                ['G#5', 375], ['C6', 562], ['B5', 187], ['A#5', 375], ['A#4', 750], ['G5', 375],
                ['E5', 1125], [0, 750], ['G5', 375], ['B5', 562], ['G5', 187], ['B5', 375],
                ['B5', 562], ['G5', 187], ['B5', 375], ['D6', 750], ['C#6', 375], ['C6', 750],
                ['G#5', 375], ['C6', 562], ['B5', 187], ['A#5', 375], ['A#4', 750], ['G5', 375],
                ['B5', 1125], [0, 750], ['G5', 375], ['B5', 562], ['G5', 187], ['B5', 375],
                ['B5', 562], ['G5', 187], ['B5', 375], ['D6', 750], ['C#6', 375], ['C6', 750],
                ['G#5', 375], ['C6', 562], ['B5', 187], ['A#5', 375], ['A#4', 750], ['G5', 375],
                ['E5', 1125]
            ],
            'pink_panther': [
                ['C#4', 272], ['D4', 272], [0, 545], ['D#4', 272], ['E4', 272], [0, 545],
                ['C#4', 272], ['D4', 272], ['D#4', 272], ['E4', 272], ['G4', 272], ['F#4', 272],
                ['D4', 272], ['E4', 818], [0, 272], ['C#4', 136], ['D4', 136], ['D#4', 136],
                ['E4', 136], ['G4', 272], ['F#4', 272], ['D4', 272], ['E4', 272], ['B4', 272],
                ['G4', 272], ['B4', 272], ['E5', 818], [0, 1090], ['C#4', 272], ['D4', 272],
                [0, 545], ['D#4', 272], ['E4', 272], [0, 545], ['C#4', 272], ['D4', 272],
                ['D#4', 272], ['E4', 272], ['G4', 272], ['F#4', 272], ['D4', 272], ['E4', 818],
                [0, 272], ['C#4', 136], ['D4', 136], ['D#4', 136], ['E4', 136], ['G4', 272],
                ['F#4', 272], ['D4', 272], ['E4', 272], ['B4', 272], ['G4', 272], ['B4', 272],
                ['E5', 818], [0, 1090]
            ],
            'gameboy': [
                ['E5', 150], ['E5', 150], [0, 150], ['E5', 150], [0, 150], ['C5', 150],
                ['E5', 300], ['G5', 300], [0, 300], ['G4', 300], [0, 300], ['C5', 450],
                ['G4', 450], ['E4', 300], [0, 150], ['A4', 300], ['B4', 300], ['A#4', 150],
                ['A4', 300], ['G4', 199], ['E5', 199], ['G5', 199], ['A5', 300], ['F5', 150],
                ['G5', 150], [0, 150], ['E5', 300], ['C5', 150], ['D5', 150], ['B4', 450],
                ['C5', 450], ['G4', 450], ['E4', 300], [0, 150], ['A4', 300], ['B4', 300],
                ['A#4', 150], ['A4', 300], ['G4', 199], ['E5', 199], ['G5', 199], ['A5', 300],
                ['F5', 150], ['G5', 150], [0, 150], ['E5', 300], ['C5', 150], ['D5', 150],
                ['B4', 450]
            ],
            'cyberpunk': [
                ['A3', 115], ['E4', 115], ['A4', 115], ['E4', 115], ['C4', 115], ['E4', 115],
                ['A4', 115], ['E4', 115], ['A3', 115], ['E4', 115], ['A4', 115], ['E4', 115],
                ['C4', 115], ['E4', 115], ['A4', 115], ['E4', 115], ['F3', 115], ['C4', 115],
                ['F4', 115], ['C4', 115], ['A3', 115], ['C4', 115], ['F4', 115], ['C4', 115],
                ['G3', 115], ['D4', 115], ['G4', 115], ['D4', 115], ['B3', 115], ['D4', 115],
                ['G4', 115], ['D4', 115], ['A3', 115], ['E4', 115], ['A4', 115], ['E4', 115],
                ['C4', 115], ['E4', 115], ['A4', 115], ['E4', 115], ['A3', 115], ['E4', 115],
                ['A4', 115], ['E4', 115], ['C4', 115], ['E4', 115], ['A4', 115], ['E4', 115],
                ['F3', 115], ['C4', 115], ['F4', 115], ['C4', 115], ['A3', 115], ['C4', 115],
                ['F4', 115], ['C4', 115], ['G3', 115], ['D4', 115], ['G4', 115], ['D4', 115],
                ['B3', 115], ['D4', 115], ['G4', 115], ['D4', 115]
            ],
            'retro_future': [
                ['C3', 187], ['E3', 187], ['G3', 187], ['B3', 187], ['C4', 187], ['B3', 187],
                ['G3', 187], ['E3', 187], ['C3', 187], ['E3', 187], ['G3', 187], ['B3', 187],
                ['C4', 187], ['B3', 187], ['G3', 187], ['E3', 187], ['A2', 187], ['C3', 187],
                ['E3', 187], ['G3', 187], ['A3', 187], ['G3', 187], ['E3', 187], ['C3', 187],
                ['F2', 187], ['A2', 187], ['C3', 187], ['E3', 187], ['F3', 187], ['E3', 187],
                ['C3', 187], ['A2', 187], ['C3', 187], ['E3', 187], ['G3', 187], ['B3', 187],
                ['C4', 187], ['B3', 187], ['G3', 187], ['E3', 187], ['C3', 187], ['E3', 187],
                ['G3', 187], ['B3', 187], ['C4', 187], ['B3', 187], ['G3', 187], ['E3', 187],
                ['A2', 187], ['C3', 187], ['E3', 187], ['G3', 187], ['A3', 187], ['G3', 187],
                ['E3', 187], ['C3', 187], ['F2', 187], ['A2', 187], ['C3', 187], ['E3', 187],
                ['F3', 187], ['E3', 187], ['C3', 187], ['A2', 187]
            ]
        };

        this.currentMelody = this.melodies['classic'];

        // Mapeamento de Frequências Completo (Oitavas 2 a 7)
        this.frequencies = {
            'C2': 65.41, 'C#2': 69.3, 'D2': 73.42, 'D#2': 77.78, 'E2': 82.41,
            'F2': 87.31, 'F#2': 92.5, 'G2': 98.0, 'G#2': 103.83, 'A2': 110.0,
            'A#2': 116.54, 'B2': 123.47, 'C3': 130.81, 'C#3': 138.59, 'D3': 146.83,
            'D#3': 155.56, 'E3': 164.81, 'F3': 174.61, 'F#3': 185.0, 'G3': 196.0,
            'G#3': 207.65, 'A3': 220.0, 'A#3': 233.08, 'B3': 246.94, 'C4': 261.63,
            'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23,
            'F#4': 369.99, 'G4': 392.0, 'G#4': 415.3, 'A4': 440.0, 'A#4': 466.16,
            'B4': 493.88, 'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25,
            'E5': 659.26, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61,
            'A5': 880.0, 'A#5': 932.33, 'B5': 987.77, 'C6': 1046.5, 'C#6': 1108.73,
            'D6': 1174.66, 'D#6': 1244.51, 'E6': 1318.51, 'F6': 1396.91, 'F#6': 1479.98,
            'G6': 1567.98, 'G#6': 1661.22, 'A6': 1760.0, 'A#6': 1864.66, 'B6': 1975.53,
            'C7': 2093.0, 'C#7': 2217.46, 'D7': 2349.32, 'D#7': 2489.02, 'E7': 2637.02,
            'F7': 2793.83, 'F#7': 2959.96, 'G7': 3135.96, 'G#7': 3322.44, 'A7': 3520.0,
            'A#7': 3729.31, 'B7': 3951.07
        };
    }

    // Configura a melodia baseada na skin
    setTheme(themeId) {
        this.currentMelody = this.melodies[themeId] || this.melodies['classic'];
        this.musicStep = 0;
    }

    init() {
        if (!this.ctx) {
            // Cria o contexto de áudio apenas na primeira interação do usuário
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    // Toca um sintetizador rápido para efeitos sonoros
    playSynth(freq, type, duration, gainStart, gainEnd) {
        if (!this.soundEnabled || !this.ctx) return;
        
        try {
            const osc = this.ctx.createOscillator();
            const gainNode = this.ctx.createGain();
            
            osc.type = type;
            osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
            
            gainNode.gain.setValueAtTime(gainStart, this.ctx.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(gainEnd, this.ctx.currentTime + duration);
            
            osc.connect(gainNode);
            gainNode.connect(this.ctx.destination);
            
            osc.start();
            osc.stop(this.ctx.currentTime + duration);
        } catch (e) {
            console.warn('Erro ao tocar efeito de som:', e);
        }
    }

    playMove() {
        this.init();
        this.playSynth(150, 'triangle', 0.08, 0.2, 0.01);
    }

    playRotate() {
        this.init();
        this.playSynth(300, 'square', 0.1, 0.15, 0.01);
    }

    playLineClear(linesCount) {
        this.init();
        if (!this.soundEnabled || !this.ctx) return;
        
        // Multi-tons para comemorar linhas limpas (arpejo mais complexo quanto mais linhas)
        const delayBetween = 80; // ms
        const baseFreq = 523.25; // C5
        const scale = [1, 1.25, 1.5, 1.875]; // C5, E5, G5, B5
        
        for (let i = 0; i < linesCount; i++) {
            setTimeout(() => {
                const freq = baseFreq * (scale[i % scale.length]);
                this.playSynth(freq, 'sawtooth', 0.25, 0.25, 0.01);
            }, i * delayBetween);
        }
    }

    playLevelUp() {
        this.init();
        if (!this.soundEnabled || !this.ctx) return;
        
        const now = this.ctx.currentTime;
        const notes = [440, 554, 659, 880]; // Arpejo Maior Triunfante
        notes.forEach((freq, idx) => {
            setTimeout(() => {
                this.playSynth(freq, 'sine', 0.3, 0.3, 0.01);
            }, idx * 120);
        });
    }

    playGameOver() {
        this.init();
        if (!this.soundEnabled || !this.ctx) return;
        
        const now = this.ctx.currentTime;
        const notes = [392, 349, 311, 261]; // Escala melancólica descendente
        notes.forEach((freq, idx) => {
            setTimeout(() => {
                this.playSynth(freq, 'sawtooth', 0.4, 0.2, 0.01);
            }, idx * 180);
        });
    }

    // Toca uma nota musical com agendamento preciso
    playMusicNote(freq, type, duration, startTime) {
        if (!this.musicEnabled || !this.ctx) return;
        
        try {
            const osc = this.ctx.createOscillator();
            const gainNode = this.ctx.createGain();
            
            osc.type = type;
            osc.frequency.setValueAtTime(freq, startTime);
            
            // Envelope simples para suavizar a nota
            gainNode.gain.setValueAtTime(0, startTime);
            gainNode.gain.linearRampToValueAtTime(0.08, startTime + 0.02);
            gainNode.gain.setValueAtTime(0.08, startTime + duration - 0.05);
            gainNode.gain.linearRampToValueAtTime(0, startTime + duration);
            
            osc.connect(gainNode);
            gainNode.connect(this.ctx.destination);
            
            osc.start(startTime);
            osc.stop(startTime + duration);
        } catch (e) {
            console.warn('Erro ao tocar nota musical:', e);
        }
    }

    // Inicia e agenda o loop da melodia com tempo preciso do AudioContext
    startMusic() {
        this.init();
        if (this.musicEnabled) return;
        
        this.musicEnabled = true;
        let nextNoteTime = this.ctx.currentTime;
        let index = 0;
        
        const scheduler = () => {
            if (!this.musicEnabled) return;
            
            while (nextNoteTime < this.ctx.currentTime + 0.1) {
                const current = this.currentMelody[index];
                const note = current[0];
                const duration = current[1] / 1000;
                
                if (note !== 0 && this.frequencies[note]) {
                    this.playMusicNote(this.frequencies[note], 'triangle', duration, nextNoteTime);
                }
                
                nextNoteTime += duration;
                index = (index + 1) % this.currentMelody.length;
            }
            requestAnimationFrame(scheduler);
        };
        
        scheduler();
    }

    stopMusic() {
        this.musicEnabled = false;
        if (this.musicInterval) {
            clearTimeout(this.musicInterval);
            this.musicInterval = null;
        }
    }
}

const audio = new SoundManager();


// ============================================================================
// 2. CONFIGURAÇÕES E ESTADOS DO JOGO
// ============================================================================
const canvas = document.getElementById('tetris-canvas');
const ctx = canvas.getContext('2d');
const nextCanvas = document.getElementById('next-canvas');
const nextCtx = nextCanvas.getContext('2d');

const COLS = 10;
const ROWS = 20;
let BLOCK_SIZE = 30; // 30px por bloco (dinâmico baseado no resize)

// Cores Modernas com Efeito Neon (Mutável via Temas da Loja)
let COLORS = {
    0: '#000000',
    1: '#00f0ff', // I - Cyan
    2: '#ffff00', // O - Yellow
    3: '#9d4edd', // T - Purple
    4: '#39ff14', // S - Green
    5: '#ff3131', // Z - Red
    6: '#0055ff', // J - Blue
    7: '#ff5f1f'  // L - Orange
};

// Cores de Sombra Glow para as Peças (Mutável via Temas da Loja)
let GLOW_COLORS = {
    1: 'rgba(0, 240, 255, 0.75)',
    2: 'rgba(255, 255, 0, 0.75)',
    3: 'rgba(157, 78, 221, 0.75)',
    4: 'rgba(57, 255, 20, 0.75)',
    5: 'rgba(255, 49, 49, 0.75)',
    6: 'rgba(0, 85, 255, 0.75)',
    7: 'rgba(255, 95, 31, 0.75)'
};

// Matrizes de Formatos de Tetrominós
const SHAPES = [
    [], // Índice 0 vazio
    // I
    [[0,0,0,0],
     [1,1,1,1],
     [0,0,0,0],
     [0,0,0,0]],
    // O
    [[2,2],
     [2,2]],
    // T
    [[0,3,0],
     [3,3,3],
     [0,0,0]],
    // S
    [[0,4,4],
     [4,4,0],
     [0,0,0]],
    // Z
    [[5,5,0],
     [0,5,5],
     [0,0,0]],
    // J
    [[6,0,0],
     [6,6,6],
     [0,0,0]],
    // L
    [[0,0,7],
     [7,7,7],
     [0,0,0]]
];


// ============================================================================
// 3. ENGENHARIA DE PARTÍCULAS (Glow Sparks)
// ============================================================================
class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.size = Math.random() * 3 + 1;
        this.speedX = Math.random() * 6 - 3;
        this.speedY = Math.random() * -4 - 1;
        this.color = color;
        this.alpha = 1;
        this.decay = Math.random() * 0.03 + 0.015;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        this.alpha -= this.decay;
    }

    draw(context) {
        context.save();
        context.globalAlpha = this.alpha;
        context.shadowBlur = 8;
        context.shadowColor = this.color;
        context.fillStyle = this.color;
        context.beginPath();
        context.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        context.fill();
        context.restore();
    }
}


// ============================================================================
// 4. CLASSE PRINCIPAL DO JOGO (TETRIS ENGINE)
// ============================================================================
class GameEngine {
    constructor() {
        this.board = this.createBoard();
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.isGameOver = false;
        this.isPaused = false;
        this.isPlaying = false;
        this.highScores = [];
        
        this.currentPiece = null;
        this.nextPiece = null;
        this.bag = [];
        
        // Loop de tempo (Delta Time para velocidade de queda constante)
        this.dropCounter = 0;
        this.dropInterval = 1000; // Começa com 1 segundo por queda (Level 1)
        this.lastTime = 0;
        
        // Partículas e animações
        this.particles = [];
        
        this.initEvents();
        
        // Inicializa o tamanho responsivo do canvas
        this.resizeCanvas();
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.draw();
        });
        
        // Carrega o tema selecionado ativamente na nuvem
        this.loadActiveTheme();
    }

    resizeCanvas() {
        let maxH, maxW;
        if (window.innerWidth > 950) {
            // No desktop, desconta menos espaço do cabeçalho (~110px) para maximizar a área de jogo
            maxH = window.innerHeight - 110;
            // Para a largura, desconta o espaço ocupado pelos painéis laterais (250px * 2) mais folgas e gaps (30px * 2)
            maxW = window.innerWidth - 560;
        } else {
            // No mobile/telas colapsadas
            maxH = window.innerHeight - 340;
            maxW = window.innerWidth - 40;
        }
        
        // Mantém limites elegantes mais generosos para telas grandes
        maxH = Math.max(300, Math.min(maxH, 1400));
        maxW = Math.max(150, Math.min(maxW, 850));
        
        let width = maxH / 2;
        let height = maxH;
        
        if (width > maxW) {
            width = maxW;
            height = width * 2;
        }
        
        // Garante que BLOCK_SIZE seja inteiro para o grid desenhar com precisão pixel-perfect
        BLOCK_SIZE = Math.floor(width / 10);
        
        if (BLOCK_SIZE < 15) {
            BLOCK_SIZE = 15;
        }
        
        canvas.width = BLOCK_SIZE * 10;
        canvas.height = BLOCK_SIZE * 20;
    }

    createBoard() {
        return Array.from({ length: ROWS }, () => Array(COLS).fill(0));
    }

    initEvents() {
        // Inputs do teclado
        document.addEventListener('keydown', (e) => this.handleInput(e));
        
        // Botão de Start
        document.getElementById('btn-start').addEventListener('click', () => {
            this.start();
        });
        
        // Botão de Reinício no Game Over
        document.getElementById('btn-restart').addEventListener('click', () => {
            this.restart();
        });
        
        // Botão de Áudio - Música
        const btnMusic = document.getElementById('btn-music');
        btnMusic.addEventListener('click', () => {
            audio.init();
            if (audio.musicEnabled) {
                audio.stopMusic();
                document.getElementById('music-status').textContent = 'OFF';
                btnMusic.classList.remove('active');
            } else {
                audio.startMusic();
                document.getElementById('music-status').textContent = 'ON';
                btnMusic.classList.add('active');
            }
        });
        
        // Botão de Áudio - Efeitos Sonoros
        const btnSound = document.getElementById('btn-sound');
        btnSound.addEventListener('click', () => {
            audio.init();
            audio.soundEnabled = !audio.soundEnabled;
            document.getElementById('sound-status').textContent = audio.soundEnabled ? 'ON' : 'OFF';
            btnSound.classList.toggle('active');
        });

        // Envio de Score do Placar
        document.getElementById('btn-submit-score').addEventListener('click', () => {
            this.submitHighScore();
        });
        
        // Trata fechamento/reabertura de input de texto para o placar
        document.getElementById('player-name').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.submitHighScore();
            }
        });

        // Botão de Abrir Loja
        const btnOpenStore = document.getElementById('btn-open-store');
        if (btnOpenStore) {
            btnOpenStore.addEventListener('click', () => {
                this.openStore();
            });
        }

        // Botão de Fechar Loja
        const btnCloseStore = document.getElementById('btn-close-store');
        if (btnCloseStore) {
            btnCloseStore.addEventListener('click', () => {
                this.closeStore();
            });
        }
    }

    start() {
        audio.init();
        document.getElementById('start-overlay').classList.add('hidden');
        this.isPlaying = true;
        this.isGameOver = false;
        this.isPaused = false;
        
        // Reseta atributos e inicializa gravação de telemetria
        this.score = 0;
        this.level = 1;
        this.lines = 0;
        this.board = this.createBoard();
        this.particles = [];
        this.bag = [];
        
        this.keystrokes = [];
        this.gameStartTime = performance.now();
        
        // Atributos de Estratégias de Bonificações
        this.comboCount = 0;
        this.lastWasTetris = false;
        
        this.updateStatsDisplay();
        
        // Gera as primeiras peças
        this.currentPiece = this.generatePiece();
        this.nextPiece = this.generatePiece();
        
        this.updateInterval();
        
        // Inicia música se ativada
        if (document.getElementById('btn-music').classList.contains('active')) {
            audio.startMusic();
        }
        
        this.lastTime = performance.now();
        requestAnimationFrame((time) => this.update(time));
    }

    restart() {
        document.getElementById('gameover-modal').classList.add('hidden');
        this.start();
    }

    // Algoritmo Randomizer de Bolsa Completa (Bag of 7)
    // Evita repetição exaustiva e garante peças justas
    generatePiece() {
        if (this.bag.length === 0) {
            this.bag = [1, 2, 3, 4, 5, 6, 7];
            // Embaralha
            for (let i = this.bag.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [this.bag[i], this.bag[j]] = [this.bag[j], this.bag[i]];
            }
        }
        
        const type = this.bag.pop();
        return {
            matrix: JSON.parse(JSON.stringify(SHAPES[type])),
            type: type,
            pos: { x: Math.floor(COLS / 2) - Math.floor(SHAPES[type][0].length / 2), y: type === 1 ? -1 : 0 }
        };
    }

    // Loop do Jogo principal baseado em Tempo (Independente do FPS)
    update(time) {
        if (!this.isPlaying || this.isPaused || this.isGameOver) return;
        
        const deltaTime = time - this.lastTime;
        this.lastTime = time;
        
        this.dropCounter += deltaTime;
        if (this.dropCounter > this.dropInterval) {
            this.moveDown();
        }
        
        // Atualiza as partículas de faíscas
        this.particles.forEach((p, idx) => {
            p.update();
            if (p.alpha <= 0) {
                this.particles.splice(idx, 1);
            }
        });
        
        this.draw();
        
        requestAnimationFrame((t) => this.update(t));
    }

    moveLeft() {
        this.currentPiece.pos.x--;
        if (this.collide()) {
            this.currentPiece.pos.x++;
        } else {
            audio.playMove();
        }
    }

    moveRight() {
        this.currentPiece.pos.x++;
        if (this.collide()) {
            this.currentPiece.pos.x--;
        } else {
            audio.playMove();
        }
    }

    moveDown() {
        this.currentPiece.pos.y++;
        if (this.collide()) {
            this.currentPiece.pos.y--;
            this.merge();
            this.clearLines();
            this.spawnNext();
        } else {
            this.dropCounter = 0;
        }
    }

    hardDrop() {
        let dropDistance = 0;
        while (!this.collide()) {
            this.currentPiece.pos.y++;
            dropDistance++;
        }
        this.currentPiece.pos.y--;
        this.score += dropDistance * 2; // Pontos extras por descida total instantânea
        
        this.merge();
        this.clearLines();
        this.spawnNext();
        
        audio.playMove();
        this.updateStatsDisplay();
    }

    rotate() {
        const matrix = this.currentPiece.matrix;
        const n = matrix.length;
        
        // Cria nova matriz rotacionada (90 graus sentido horário)
        const rotated = Array.from({ length: n }, () => Array(n).fill(0));
        for (let r = 0; r < n; r++) {
            for (let c = 0; c < n; c++) {
                rotated[c][n - 1 - r] = matrix[r][c];
            }
        }
        
        const originalMatrix = this.currentPiece.matrix;
        this.currentPiece.matrix = rotated;
        
        // Mecanismo simples de "Wall Kick" (Empurra se bater na parede ou em outra peça)
        const pos = this.currentPiece.pos;
        let offset = 1;
        while (this.collide()) {
            pos.x += offset;
            offset = -(offset + (offset > 0 ? 1 : -1));
            if (Math.abs(offset) > n) {
                // Reverte se não couber de forma alguma
                this.currentPiece.matrix = originalMatrix;
                pos.x = pos.x;
                return;
            }
        }
        audio.playRotate();
    }

    // Detecção de Colisão Matemática
    collide() {
        const matrix = this.currentPiece.matrix;
        const pos = this.currentPiece.pos;
        
        for (let r = 0; r < matrix.length; r++) {
            for (let c = 0; c < matrix[r].length; c++) {
                if (matrix[r][c] !== 0) {
                    const boardX = pos.x + c;
                    const boardY = pos.y + r;
                    
                    // Verifica limites das paredes laterais e do fundo
                    if (boardX < 0 || boardX >= COLS || boardY >= ROWS) {
                        return true;
                    }
                    
                    // Verifica se já existe uma peça fixa no local (ignora se estiver acima do topo da grade)
                    if (boardY >= 0 && this.board[boardY][boardX] !== 0) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    // Fixa a peça atual no tabuleiro
    merge() {
        const matrix = this.currentPiece.matrix;
        const pos = this.currentPiece.pos;
        
        matrix.forEach((row, r) => {
            row.forEach((value, c) => {
                if (value !== 0) {
                    const boardY = pos.y + r;
                    const boardX = pos.x + c;
                    
                    // Permite fixar peças mesmo que ultrapassem o topo da grade
                    if (boardY >= 0) {
                        this.board[boardY][boardX] = value;
                    }
                }
            });
        });
    }

    // Limpeza de Linhas e Geração de Partículas
    clearLines() {
        let clearedCount = 0;
        
        // Varre de baixo para cima
        for (let r = ROWS - 1; r >= 0; r--) {
            if (this.board[r].every(val => val !== 0)) {
                // Cria efeito visual de explosão de fagulhas coloridas
                this.createSparksEffect(r);
                
                // Remove a linha e adiciona uma linha vazia no topo
                this.board.splice(r, 1);
                this.board.unshift(Array(COLS).fill(0));
                clearedCount++;
                r++; // Reajusta índice para reavaliar a mesma linha que desceu
            }
        }
        
        if (clearedCount > 0) {
            this.lines += clearedCount;
            
            // Incrementa o Combo de limpezas sequenciais!
            this.comboCount++;
            
            // Fase 3: Telemetria de Linhas Limpas
            sendTelemetry('line_clear', clearedCount);
            
            let pointsGained = 0;
            const scoreMultiplier = [0, 100, 300, 500, 800];
            
            if (clearedCount === 4) {
                sendTelemetry('tetris_clear', 1);
                
                // 1. Super Bônus de Tetris Progressivo por Nível
                const baseTetrisPoints = 800 * this.level;
                const progressiveBonus = Math.round(1000 * Math.pow(this.level, 1.5));
                pointsGained = baseTetrisPoints + progressiveBonus;
                
                // 2. Bônus de Back-to-Back Tetris (+50%)
                if (this.lastWasTetris) {
                    pointsGained = Math.round(pointsGained * 1.5);
                    this.showFloatingEvent('⚡ BACK-TO-BACK TETRIS! ⚡', 'b2b');
                } else {
                    this.showFloatingEvent('TETRIS!', 'tetris');
                }
                
                this.lastWasTetris = true;
            } else {
                pointsGained = scoreMultiplier[clearedCount] * this.level;
                this.lastWasTetris = false; // Quebrou a sequência de Back-to-Back Tetris
            }
            
            // 3. Multiplicador de Combo Sequencial
            if (this.comboCount > 1) {
                const comboMultiplier = 1 + ((this.comboCount - 1) * 0.5);
                pointsGained = Math.round(pointsGained * comboMultiplier);
                
                // Mostra evento flutuante de combo
                setTimeout(() => {
                    this.showFloatingEvent(`🔥 COMBO x${this.comboCount}! +${(this.comboCount - 1) * 50}% BONUS! 🔥`, 'combo');
                }, 300);
            }
            
            // 4. Bônus de Perfect Clear (Tabuleiro totalmente vazio após a limpa!)
            const isBoardEmpty = this.board.every(row => row.every(val => val === 0));
            if (isBoardEmpty) {
                pointsGained += 20000;
                setTimeout(() => {
                    this.showFloatingEvent('⭐ PERFECT CLEAR! +20.000 PTS ⭐', 'perfect');
                }, 600);
            }
            
            // Soma os pontos finais calculados
            this.score += pointsGained;
            
            // Aumenta nível a cada 10 linhas limpas
            const newLevel = Math.floor(this.lines / 10) + 1;
            if (newLevel > this.level) {
                this.level = newLevel;
                audio.playLevelUp();
                this.updateInterval();
                // Fase 3: Telemetria de Nível
                sendTelemetry('level_up', this.level);
                this.showFloatingEvent(`LEVEL UP!`, 'levelup');
            } else {
                audio.playLineClear(clearedCount);
            }
            
            // Fase 3: Verifica se desbloqueou conquistas
            setTimeout(() => fetchAndShowAchievements(), 500);
            
            this.updateStatsDisplay();
        } else {
            // Se nenhuma linha foi limpa nessa peça que fixou, o Combo sequencial é quebrado!
            this.comboCount = 0;
        }
    }

    showFloatingEvent(text, cssClass) {
        const container = document.getElementById('game-events-container');
        if (!container) return;
        
        const el = document.createElement('div');
        el.className = `floating-event ${cssClass}`;
        el.textContent = text;
        
        container.appendChild(el);
        
        // Remove após a animação (2.5s)
        setTimeout(() => {
            if (container.contains(el)) {
                container.removeChild(el);
            }
        }, 3000);
    }

    createSparksEffect(rowY) {
        // Gera partículas brilhantes na altura da linha limpa
        const canvasY = rowY * BLOCK_SIZE + (BLOCK_SIZE / 2);
        for (let x = 0; x < COLS * BLOCK_SIZE; x += 10) {
            // Usa cor neon de fagulha rosa ou amarela aleatória
            const color = Math.random() > 0.5 ? COLORS[1] : COLORS[3];
            this.particles.push(new Particle(x, canvasY, color));
        }
    }

    spawnNext() {
        this.currentPiece = this.nextPiece;
        this.nextPiece = this.generatePiece();
        this.dropCounter = 0;
        
        // Verifica se a nova peça nasce colidindo (GAME OVER)
        if (this.collide()) {
            this.gameOver();
        }
    }

    updateInterval() {
        // Reduz progressivamente o tempo entre quedas conforme o nível aumenta (mais rápido)
        // Mínimo de 60ms por queda
        this.dropInterval = Math.max(60, 1000 - (this.level - 1) * 90);
    }

    togglePause() {
        if (!this.isPlaying || this.isGameOver) return;
        
        this.isPaused = !this.isPaused;
        const overlay = document.getElementById('pause-overlay');
        
        if (this.isPaused) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
            this.lastTime = performance.now();
            requestAnimationFrame((time) => this.update(time));
        }
    }

    gameOver() {
        this.isPlaying = false;
        this.isGameOver = true;
        audio.playGameOver();
        
        // Exibe resultados no modal
        document.getElementById('final-score').textContent = this.score.toLocaleString();
        document.getElementById('final-level').textContent = this.level;
        document.getElementById('final-lines').textContent = this.lines;
        
        // Verifica se é recorde (High Score) de forma assíncrona
        this.checkIfHighScore();
        
        document.getElementById('gameover-modal').classList.remove('hidden');
    }

    async checkIfHighScore() {
        const form = document.getElementById('new-high-score-form');
        form.classList.add('hidden');
        
        try {
            const currentScores = await fetchScores();
            if (isHighScore(this.score, currentScores)) {
                form.classList.remove('hidden');
                document.getElementById('player-name').focus();
            }
        } catch (e) {
            console.warn('Não foi possível verificar recorde com o backend.', e);
        }
    }

    async submitHighScore() {
        const nameInput = document.getElementById('player-name');
        const name = nameInput.value.trim();
        
        if (!name) {
            alert('Por favor, digite seu nome ou iniciais para o placar.');
            return;
        }
        
        const btn = document.getElementById('btn-submit-score');
        btn.disabled = true;
        btn.textContent = 'Orquestrando...';
        
        const chkBot = document.getElementById('chk-simulate-bot');
        const isBotSimulated = chkBot ? chkBot.checked : false;
        
        // Envia o placar de forma orquestrada com gravação das teclas para o Anti-Cheat
        const success = await submitScore(name, this.score, this.level, this.lines, this.keystrokes, isBotSimulated);
        
        if (success) {
            document.getElementById('new-high-score-form').classList.add('hidden');
            nameInput.value = '';
        }
        
        btn.disabled = false;
        btn.textContent = 'Salvar Placar';
    }

    updateStatsDisplay() {
        document.getElementById('stat-score').textContent = this.score;
        document.getElementById('stat-level').textContent = this.level;
        document.getElementById('stat-lines').textContent = this.lines;
    }

    // Inputs de Teclado
    handleInput(e) {
        if (!this.isPlaying) return;
        
        if (e.key.toLowerCase() === 'p') {
            this.togglePause();
            return;
        }
        
        if (this.isPaused || this.isGameOver) return;
        
        // Captura a telemetria de toques para análise de anti-cheat com IA
        if (this.keystrokes) {
            this.keystrokes.push({
                key: e.key,
                t: performance.now() - this.gameStartTime
            });
        }
        
        switch (e.key) {
            case 'ArrowLeft':
            case 'a':
            case 'A':
                this.moveLeft();
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                this.moveRight();
                break;
            case 'ArrowDown':
            case 's':
            case 'S':
                this.moveDown();
                break;
            case 'ArrowUp':
            case 'w':
            case 'W':
                this.rotate();
                break;
            case ' ': // Barra de espaço
                e.preventDefault(); // Evita scroll da página
                this.hardDrop();
                break;
        }
    }


    // ============================================================================
    // 5. SISTEMA DE RENDERIZAÇÃO NO CANVAS (DRAW ENGINE)
    // ============================================================================
    draw() {
        // 1. Limpa o Canvas Principal com fundo preto semi-transparente para rastro glow
        ctx.fillStyle = 'rgba(8, 6, 15, 0.35)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Desenha uma leve grade de fundo futurista
        this.drawGrid(ctx, canvas.width, canvas.height);
        
        // 2. Desenha os blocos fixos no tabuleiro
        this.board.forEach((row, y) => {
            row.forEach((value, x) => {
                if (value !== 0) {
                    this.drawBlock(ctx, x, y, value);
                }
            });
        });
        
        // 3. Desenha a peça atual caindo
        if (this.currentPiece) {
            // Desenha uma projeção de sombra (Ghost Piece) onde a peça vai cair
            this.drawGhostPiece();
            
            // Desenha a peça real
            this.currentPiece.matrix.forEach((row, y) => {
                row.forEach((value, x) => {
                    if (value !== 0) {
                        this.drawBlock(ctx, this.currentPiece.pos.x + x, this.currentPiece.pos.y + y, value);
                    }
                });
            });
        }
        
        // 4. Desenha as faíscas de partículas
        this.particles.forEach(p => p.draw(ctx));
        
        // 5. Desenha o painel da Próxima Peça
        this.drawNextPiece();
    }

    drawGrid(context, width, height) {
        context.strokeStyle = 'rgba(61, 28, 92, 0.15)';
        context.lineWidth = 1;
        
        // Linhas verticais
        for (let x = 0; x < width; x += BLOCK_SIZE) {
            context.beginPath();
            context.moveTo(x, 0);
            context.lineTo(x, height);
            context.stroke();
        }
        // Linhas horizontais
        for (let y = 0; y < height; y += BLOCK_SIZE) {
            context.beginPath();
            context.moveTo(0, y);
            context.lineTo(width, y);
            context.stroke();
        }
    }

    // Desenha um bloco com visual neon sofisticado
    drawBlock(context, x, y, value, isGhost = false) {
        // Impede desenhar blocos acima da tela visível
        if (y < 0) return;
        
        const posX = x * BLOCK_SIZE;
        const posY = y * BLOCK_SIZE;
        
        context.save();
        
        if (isGhost) {
            // Peça fantasma (vazada, apenas contorno neon suave)
            context.strokeStyle = GLOW_COLORS[value];
            context.lineWidth = 2;
            context.strokeRect(posX + 2, posY + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4);
        } else {
            // Bloco normal com efeito gradiente interno e brilho glow
            context.shadowBlur = 10;
            context.shadowColor = GLOW_COLORS[value];
            
            const grad = context.createLinearGradient(posX, posY, posX + BLOCK_SIZE, posY + BLOCK_SIZE);
            grad.addColorStop(0, '#fff'); // Brilho de reflexo interno
            grad.addColorStop(0.15, COLORS[value]);
            grad.addColorStop(1, '#000'); // Sombra de profundidade 3D
            
            context.fillStyle = grad;
            context.fillRect(posX + 1, posY + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2);
            
            // Adiciona borda brilhante
            context.strokeStyle = GLOW_COLORS[value];
            context.lineWidth = 1.5;
            context.strokeRect(posX + 1, posY + 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2);
        }
        
        context.restore();
    }

    // Desenha a sombra de projeção onde a peça vai tocar o fundo
    drawGhostPiece() {
        const ghost = {
            pos: { x: this.currentPiece.pos.x, y: this.currentPiece.pos.y },
            matrix: this.currentPiece.matrix,
            type: this.currentPiece.type
        };
        
        // Avança até bater em colisão
        while (!this.collideGhost(ghost)) {
            ghost.pos.y++;
        }
        ghost.pos.y--; // Volta uma célula para ficar em cima da colisão
        
        // Renderiza apenas se estiver abaixo da peça atual
        if (ghost.pos.y > this.currentPiece.pos.y) {
            ghost.matrix.forEach((row, y) => {
                row.forEach((value, x) => {
                    if (value !== 0) {
                        this.drawBlock(ctx, ghost.pos.x + x, ghost.pos.y + y, value, true);
                    }
                });
            });
        }
    }

    // Colisão exclusiva para a simulação da peça fantasma
    collideGhost(ghost) {
        const matrix = ghost.matrix;
        const pos = ghost.pos;
        
        for (let r = 0; r < matrix.length; r++) {
            for (let c = 0; c < matrix[r].length; c++) {
                if (matrix[r][c] !== 0) {
                    const boardX = pos.x + c;
                    const boardY = pos.y + r;
                    
                    if (boardX < 0 || boardX >= COLS || boardY >= ROWS) {
                        return true;
                    }
                    if (boardY >= 0 && this.board[boardY][boardX] !== 0) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    // Renderiza a próxima peça no Canvas menor lateral
    drawNextPiece() {
        // Limpa o canvas lateral
        nextCtx.fillStyle = 'rgba(0, 0, 0, 0.9)';
        nextCtx.fillRect(0, 0, nextCanvas.width, nextCanvas.height);
        
        if (!this.nextPiece) return;
        
        const matrix = this.nextPiece.matrix;
        const type = this.nextPiece.type;
        
        // Encontra os limites da peça para centralizá-la perfeitamente no Canvas de 120x120px
        const n = matrix.length;
        const size = BLOCK_SIZE; // Usaremos blocos de 20px ou 24px no painel lateral
        const miniBlockSize = 22;
        
        // Calcula offset para centralização
        let minX = n, maxX = -1, minY = n, maxY = -1;
        matrix.forEach((row, r) => {
            row.forEach((value, c) => {
                if (value !== 0) {
                    if (c < minX) minX = c;
                    if (c > maxX) maxX = c;
                    if (r < minY) minY = r;
                    if (r > maxY) maxY = r;
                }
            });
        });
        
        const pieceW = (maxX - minX + 1) * miniBlockSize;
        const pieceH = (maxY - minY + 1) * miniBlockSize;
        const offsetX = (nextCanvas.width - pieceW) / 2 - minX * miniBlockSize;
        const offsetY = (nextCanvas.height - pieceH) / 2 - minY * miniBlockSize;
        
        matrix.forEach((row, r) => {
            row.forEach((value, c) => {
                if (value !== 0) {
                    const posX = offsetX + c * miniBlockSize;
                    const posY = offsetY + r * miniBlockSize;
                    
                    nextCtx.save();
                    nextCtx.shadowBlur = 8;
                    nextCtx.shadowColor = GLOW_COLORS[value];
                    
                    const grad = nextCtx.createLinearGradient(posX, posY, posX + miniBlockSize, posY + miniBlockSize);
                    grad.addColorStop(0, '#fff');
                    grad.addColorStop(0.2, COLORS[value]);
                    grad.addColorStop(1, '#000');
                    
                    nextCtx.fillStyle = grad;
                    nextCtx.fillRect(posX + 1, posY + 1, miniBlockSize - 2, miniBlockSize - 2);
                    nextCtx.restore();
                }
            });
        });
    }

    // --- MÉTODOS ADICIONADOS DE TEMAS, LOJA & ORQUESTRADO SAGA ---

    async loadActiveTheme() {
        try {
            const data = await fetchStoreCatalog();
            if (data && data.active_skin) {
                this.applyThemePalette(data.active_skin);
            }
        } catch (e) {
            console.warn("Falha ao carregar tema inicial do servidor.", e);
        }
    }

    async openStore() {
        if (this.isPlaying && !this.isPaused) {
            this.togglePause();
        }
        
        document.getElementById('store-modal').classList.remove('hidden');
        
        // Mostra o terminal do Maestro da Loja e limpa-o
        const terminalEl = document.getElementById('store-maestro-terminal');
        if (terminalEl) {
            terminalEl.classList.add('hidden');
            terminalEl.innerHTML = '';
        }
        
        this.updateStoreView();
    }

    closeStore() {
        document.getElementById('store-modal').classList.add('hidden');
    }

    async updateStoreView() {
        const catalogListEl = document.getElementById('store-catalog-list');
        const balanceEl = document.getElementById('store-coin-balance');
        
        if (!catalogListEl || !balanceEl) return;
        
        catalogListEl.innerHTML = '<p class="loading">Sincronizando catálogo com a nuvem...</p>';
        
        const data = await fetchStoreCatalog();
        if (!data) {
            catalogListEl.innerHTML = '<p class="loading" style="color: var(--neon-red)">Falha de rede ao conectar à Nuvem.</p>';
            return;
        }
        
        // Se a sessão do usuário estiver banida, exibe tela de bloqueio dedicada
        if (data.isBanned) {
            catalogListEl.innerHTML = `
                <div style="text-align: center; padding: 20px; border: 2px dashed var(--neon-red); background: rgba(255, 49, 49, 0.08); border-radius: 4px; margin-top: 10px;">
                    <p class="blink" style="color: var(--neon-red); font-size: 14px; font-weight: bold; margin-bottom: 8px; letter-spacing: 1px;">🚫 CONTA BLOQUEADA POR TRAPAÇA</p>
                    <p style="color: #bbb; font-size: 10px; line-height: 1.5; font-family: 'Share Tech Mono', monospace;">Seu ID de sessão foi permanentemente banido da nossa infraestrutura serverless por uso de Bots/Cheats detectado pelo classificador de IA de telemetria.<br><br>O acesso à carteira, catálogo de skins e o envio de pontuações de recordes foram revogados para este ID.</p>
                </div>
            `;
            balanceEl.textContent = "0";
            return;
        }
        
        balanceEl.textContent = data.balance.toLocaleString();
        catalogListEl.innerHTML = ''; // Limpa catálogo
        
        data.catalog.forEach(item => {
            const card = document.createElement('div');
            card.className = `skin-card ${item.is_active ? 'equipped' : ''}`;
            
            // Informações
            const info = document.createElement('div');
            info.className = 'skin-info';
            
            const name = document.createElement('div');
            name.className = 'skin-name';
            name.textContent = item.name.toUpperCase();
            
            const desc = document.createElement('div');
            desc.className = 'skin-desc';
            desc.textContent = item.description;
            
            info.appendChild(name);
            info.appendChild(desc);
            
            // Preço (se não desbloqueado)
            if (!item.is_unlocked) {
                const price = document.createElement('div');
                price.className = 'skin-price';
                price.innerHTML = `${item.price.toLocaleString()} <span>🪙</span>`;
                info.appendChild(price);
            }
            
            // Ações
            const action = document.createElement('div');
            action.className = 'skin-action';
            
            const btn = document.createElement('button');
            btn.className = 'arcade-btn skin-btn';
            
            if (item.is_active) {
                btn.className += ' active';
                btn.textContent = 'EQUIPADO';
                btn.disabled = true;
            } else if (item.is_unlocked) {
                btn.className += ' equip';
                btn.textContent = 'EQUIPAR';
                btn.addEventListener('click', async () => {
                    btn.disabled = true;
                    btn.textContent = 'Carregando...';
                    const res = await equipSkin(item.skin_id);
                    if (res && res.status === 'success') {
                        this.applyThemePalette(item.skin_id);
                        this.updateStoreView();
                        this.draw();
                    } else {
                        alert('Falha ao selecionar tema.');
                        btn.disabled = false;
                        btn.textContent = 'EQUIPAR';
                    }
                });
            } else {
                btn.className += ' buy';
                btn.textContent = 'COMPRAR';
                
                // Se o saldo for menor, desativa botão de compra
                if (data.balance < item.price) {
                    btn.disabled = true;
                    btn.style.opacity = '0.4';
                    btn.style.cursor = 'not-allowed';
                }
                
                btn.addEventListener('click', async () => {
                    // Desativa todos os botões de compra para focar na orquestração
                    const allButtons = catalogListEl.querySelectorAll('.skin-btn');
                    allButtons.forEach(b => b.disabled = true);
                    
                    btn.textContent = 'Processando...';
                    
                    // Redireciona os logs do terminal de orquestração da compra
                    const storeTerminal = document.getElementById('store-maestro-terminal');
                    if (storeTerminal) {
                        storeTerminal.classList.remove('hidden');
                        storeTerminal.innerHTML = '<div class="terminal-header">Maestro Console (GCP Workflows Engine)</div>';
                        
                        // Criamos um elemento de log global para a função renderOrchestratorLogs usar
                        const originalTerminal = document.getElementById('maestro-terminal');
                        
                        // Temporariamente faz com que o id maestro-terminal aponte para o terminal da loja!
                        storeTerminal.id = 'maestro-terminal';
                        if (originalTerminal) originalTerminal.id = 'temp-maestro-terminal';
                        
                        // Dispara a SAGA orquestrada!
                        const res = await buySkinOrchestrated(item.skin_id);
                        
                        // Restaura os IDs originais após a animação de logs começar
                        setTimeout(() => {
                            storeTerminal.id = 'store-maestro-terminal';
                            if (originalTerminal) originalTerminal.id = 'maestro-terminal';
                        }, 2500);
                        
                        if (res && res.status === 'success') {
                            setTimeout(() => alert(`Sucesso! Tema '${item.name}' adquirido via orquestrador SAGA!`), 2200);
                        } else if (res && res.status === 'rolled_back') {
                            setTimeout(() => alert(`SAGA ROLLBACK DETECTADO!\nA entrega do item falhou no Inventário, então o Maestro (orquestrador) executou uma transação compensatória de reembolso na sua carteira!`), 2200);
                        } else if (res && res.status === 'dlq_error') {
                            setTimeout(() => alert(`ERRO CRÍTICO DUPLO!\nA entrega da skin falhou E a transação compensatória também falhou. O incidente foi encaminhado para a Dead-Letter Queue (DLQ) no Pub/Sub.`), 2200);
                        } else {
                            setTimeout(() => alert(`Erro na orquestração: ${res ? res.message : 'Falha desconhecida'}`), 2200);
                        }
                    } else {
                        // Sem terminal: apenas dispara compra
                        const res = await buySkinOrchestrated(item.skin_id);
                        if (res && res.status === 'success') {
                            alert(`Sucesso! Tema '${item.name}' adquirido via orquestrador SAGA!`);
                        }
                    }
                    
                    setTimeout(() => {
                        this.updateStoreView();
                        this.draw();
                    }, 2500); // Aguarda a animação dos logs terminar
                });
            }
            
            action.appendChild(btn);
            card.appendChild(info);
            card.appendChild(action);
            catalogListEl.appendChild(card);
        });
    }

    applyThemePalette(themeId) {
        // Atualiza a melodia no SoundManager
        audio.setTheme(themeId);
        
        const THEME_PALETTES = {
            "classic": {
                COLORS: {
                    0: '#000000', 1: '#00f0ff', 2: '#ffff00', 3: '#9d4edd', 4: '#39ff14', 5: '#ff3131', 6: '#0055ff', 7: '#ff5f1f'
                },
                GLOW_COLORS: {
                    1: 'rgba(0, 240, 255, 0.75)', 2: 'rgba(255, 255, 0, 0.75)', 3: 'rgba(157, 78, 221, 0.75)', 4: 'rgba(57, 255, 20, 0.75)', 5: 'rgba(255, 49, 49, 0.75)', 6: 'rgba(0, 85, 255, 0.75)', 7: 'rgba(255, 95, 31, 0.75)'
                }
            },
            "star_wars": {
                COLORS: {
                    0: '#03030c', 1: '#0066ff', 2: '#00ff33', 3: '#b000ff', 4: '#ff0000', 5: '#00ffff', 6: '#ffcc00', 7: '#e0e0e0'
                },
                GLOW_COLORS: {
                    1: 'rgba(0, 102, 255, 0.85)', 2: 'rgba(0, 255, 51, 0.85)', 3: 'rgba(176, 0, 255, 0.85)', 4: 'rgba(255, 0, 0, 0.85)', 5: 'rgba(0, 255, 255, 0.85)', 6: 'rgba(255, 204, 0, 0.85)', 7: 'rgba(224, 224, 224, 0.85)'
                }
            },
            "harry_potter": {
                COLORS: {
                    0: '#0d001a', 1: '#9e0000', 2: '#ffcc00', 3: '#00703c', 4: '#cccccc', 5: '#003da5', 6: '#cd7f32', 7: '#f0c300'
                },
                GLOW_COLORS: {
                    1: 'rgba(158, 0, 0, 0.85)', 2: 'rgba(255, 204, 0, 0.85)', 3: 'rgba(0, 112, 60, 0.85)', 4: 'rgba(204, 204, 204, 0.85)', 5: 'rgba(0, 61, 165, 0.85)', 6: 'rgba(205, 127, 50, 0.85)', 7: 'rgba(240, 195, 0, 0.85)'
                }
            },
            "lord_of_the_rings": {
                COLORS: {
                    0: '#120d03', 1: '#ffaa00', 2: '#007f30', 3: '#f0f0f0', 4: '#ff3300', 5: '#151522', 6: '#ff7700', 7: '#ee99ff'
                },
                GLOW_COLORS: {
                    1: 'rgba(255, 170, 0, 0.85)', 2: 'rgba(0, 127, 48, 0.85)', 3: 'rgba(240, 240, 240, 0.85)', 4: 'rgba(255, 51, 0, 0.85)', 5: 'rgba(21, 21, 34, 0.85)', 6: 'rgba(255, 119, 0, 0.85)', 7: 'rgba(238, 153, 255, 0.85)'
                }
            },
            "pink_panther": {
                COLORS: {
                    0: '#300020', 1: '#ff66b2', 2: '#ff007f', 3: '#e0b0ff', 4: '#da70d6', 5: '#ffb3ba', 6: '#fadadd', 7: '#3a005c'
                },
                GLOW_COLORS: {
                    1: 'rgba(255, 102, 178, 0.85)', 2: 'rgba(255, 0, 127, 0.85)', 3: 'rgba(224, 176, 255, 0.85)', 4: 'rgba(218, 112, 214, 0.85)', 5: 'rgba(255, 179, 186, 0.85)', 6: 'rgba(250, 218, 221, 0.85)', 7: 'rgba(58, 0, 92, 0.85)'
                }
            },
            "gameboy": {
                COLORS: {
                    0: '#0f380f', 1: '#306230', 2: '#8bac0f', 3: '#9bbc0f', 4: '#306230', 5: '#8bac0f', 6: '#9bbc0f', 7: '#306230'
                },
                GLOW_COLORS: {
                    1: 'rgba(48, 98, 48, 0.75)', 2: 'rgba(139, 172, 15, 0.75)', 3: 'rgba(155, 188, 15, 0.75)', 4: 'rgba(48, 98, 48, 0.75)', 5: 'rgba(139, 172, 15, 0.75)', 6: 'rgba(155, 188, 15, 0.75)', 7: 'rgba(48, 98, 48, 0.75)'
                }
            },
            "cyberpunk": {
                COLORS: {
                    0: '#0d0211', 1: '#ff007f', 2: '#ff5e00', 3: '#ffb700', 4: '#8b00ff', 5: '#ee82ee', 6: '#4b0082', 7: '#00ffff'
                },
                GLOW_COLORS: {
                    1: 'rgba(255, 0, 127, 0.75)', 2: 'rgba(255, 94, 0, 0.75)', 3: 'rgba(255, 183, 0, 0.75)', 4: 'rgba(139, 0, 255, 0.75)', 5: 'rgba(238, 130, 238, 0.75)', 6: 'rgba(75, 0, 130, 0.75)', 7: 'rgba(0, 255, 255, 0.75)'
                }
            },
            "retro_future": {
                COLORS: {
                    0: '#00001a', 1: '#00f0ff', 2: '#00d0ff', 3: '#00aaff', 4: '#0088ff', 5: '#0055ff', 6: '#0022ff', 7: '#0099ff'
                },
                GLOW_COLORS: {
                    1: 'rgba(0, 240, 255, 0.75)', 2: 'rgba(0, 208, 255, 0.75)', 3: 'rgba(0, 170, 255, 0.75)', 4: 'rgba(0, 136, 255, 0.75)', 5: 'rgba(0, 85, 255, 0.75)', 6: 'rgba(0, 34, 255, 0.75)', 7: 'rgba(0, 153, 255, 0.75)'
                }
            }
        };

        const palette = THEME_PALETTES[themeId] || THEME_PALETTES["classic"];
        COLORS = { ...palette.COLORS };
        GLOW_COLORS = { ...palette.GLOW_COLORS };
        
        // Aplica cores de fundo do canvas principal
        const canvasEl = document.getElementById('tetris-canvas');
        if (canvasEl) {
            if (themeId === 'gameboy') {
                canvasEl.style.backgroundColor = '#8bac0f';
            } else if (themeId === 'cyberpunk') {
                canvasEl.style.backgroundColor = '#0d0211';
            } else if (themeId === 'retro_future') {
                canvasEl.style.backgroundColor = '#00001a';
            } else if (themeId === 'star_wars') {
                canvasEl.style.backgroundColor = '#03030c';
            } else if (themeId === 'harry_potter') {
                canvasEl.style.backgroundColor = '#0d001a';
            } else if (themeId === 'lord_of_the_rings') {
                canvasEl.style.backgroundColor = '#120d03';
            } else if (themeId === 'pink_panther') {
                canvasEl.style.backgroundColor = '#300020';
            } else {
                canvasEl.style.backgroundColor = '#000000';
            }
        }
    }
}

// Inicializa o Engine de Jogo ao carregar a página
window.addEventListener('load', () => {
    window.game = new GameEngine();
});
