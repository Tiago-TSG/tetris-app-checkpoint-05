// Integração com a API de Recordes do Backend FastAPI

/**
 * Busca a lista de recordes do backend e renderiza na interface
 */
async function fetchScores() {
    const scoresListElement = document.getElementById('scores-list');
    if (!scoresListElement) return;

    try {
        const response = await fetch('/api/scores');
        if (!response.ok) {
            throw new Error('Falha ao obter pontuações.');
        }
        const scores = await response.json();
        renderScores(scores);
        return scores;
    } catch (error) {
        console.error('Erro ao buscar placar:', error);
        scoresListElement.innerHTML = `<li class="loading" style="color: var(--neon-red)">Erro ao carregar recordes.</li>`;
        return [];
    }
}

/**
 * Renderiza os recordes na listagem da página
 * @param {Array} scores Lista de objetos contendo {name, score, level, lines}
 */
function renderScores(scores) {
    const scoresListElement = document.getElementById('scores-list');
    if (!scoresListElement) return;

    if (scores.length === 0) {
        scoresListElement.innerHTML = `<li class="loading">Nenhum recorde ainda.</li>`;
        return;
    }

    // Limpa a lista
    scoresListElement.innerHTML = '';

    scores.forEach((entry, index) => {
        const li = document.createElement('li');
        
        const rankSpan = document.createElement('span');
        rankSpan.className = 'score-rank';
        rankSpan.textContent = `#${index + 1}`;
        
        const nameSpan = document.createElement('span');
        nameSpan.className = 'score-name';
        nameSpan.textContent = entry.name.toUpperCase();
        
        const badgeContainer = document.createElement('span');
        badgeContainer.className = 'achievement-badge-container';
        badgeContainer.id = `badge-container-${index}`;
        nameSpan.appendChild(badgeContainer);
        
        // Fetch assíncrono das badges do jogador para exibir no ranking
        fetch(`/api/achievements/${entry.name.toUpperCase()}`)
            .then(res => res.json())
            .then(data => {
                const badges = data.badges || [];
                badges.forEach(b => {
                    const info = BADGES_MAP[b];
                    if (info) {
                        const iconSpan = document.createElement('span');
                        iconSpan.className = 'achievement-badge-icon';
                        iconSpan.textContent = info.icon;
                        iconSpan.title = info.label;
                        badgeContainer.appendChild(iconSpan);
                    }
                });
            })
            .catch(() => {});
        
        const valSpan = document.createElement('span');
        valSpan.className = 'score-val';
        valSpan.textContent = entry.score.toLocaleString();

        li.appendChild(rankSpan);
        li.appendChild(nameSpan);
        li.appendChild(valSpan);
        
        // Efeito sutil neon verde para scores enviados de forma otimista que estão salvando em background
        if (entry.isOptimistic) {
            li.classList.add('syncing-score');
            
            // Cria um badge piscando "[SALVANDO]"
            const badgeSpan = document.createElement('span');
            badgeSpan.className = 'score-badge';
            badgeSpan.textContent = ' [SALVANDO]';
            badgeSpan.style.color = 'var(--neon-green)';
            badgeSpan.style.fontSize = '8px';
            badgeSpan.style.fontStyle = 'italic';
            badgeSpan.style.fontWeight = 'bold';
            nameSpan.appendChild(badgeSpan);
            
            li.style.textShadow = "0 0 10px #39ff14";
            li.style.color = "#39ff14";
            li.title = "Sincronizando recorde com a nuvem...";
        }
        
        scoresListElement.appendChild(li);
    });
}

/**
 * Atualiza a mensagem de status do Pub/Sub dentro do formulário do modal
 * @param {string} message Mensagem a ser exibida
 * @param {string} type Tipo: 'success' (verde) ou 'info' (ciano) ou 'hidden' (esconder)
 */
function updatePubSubStatus(message, type = 'success') {
    const statusEl = document.getElementById('pubsub-status');
    if (!statusEl) return;
    
    if (type === 'hidden') {
        statusEl.classList.add('hidden');
        return;
    }
    
    statusEl.classList.remove('hidden', 'info', 'success');
    statusEl.classList.add(type);
    
    const icon = type === 'info' ? '🕹️ ' : '✓ ';
    statusEl.innerHTML = `<span>${icon}</span>${message}`;
}

/**
 * Gerencia a sessão única do jogador
 */
function getSessionId() {
    let sid = sessionStorage.getItem('tetris_session_id');
    if (!sid) {
        sid = 'PLAYER-' + Math.random().toString(36).substring(2, 9).toUpperCase();
        sessionStorage.setItem('tetris_session_id', sid);
    }
    return sid;
}

/**
 * Envia eventos de telemetria em tempo real
 */
function sendTelemetry(eventType, value) {
    fetch('/api/telemetry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: getSessionId(),
            event_type: eventType,
            value: value
        })
    }).catch(e => console.warn('Falha na telemetria:', e));
}

const BADGES_MAP = {
    "level_3": { icon: "🥉", label: "Novato Neon" },
    "level_7": { icon: "🥈", label: "Piloto de Fuga" },
    "level_10": { icon: "🥇", label: "Deus do Arcade" },
    "lines_50": { icon: "🥉", label: "Operador da Grade" },
    "lines_200": { icon: "🥈", label: "Hacker de Sistemas" },
    "lines_500": { icon: "🥇", label: "Lenda Synthwave" },
    "tetris_1": { icon: "🥉", label: "Golpe Perfeito" },
    "tetris_10": { icon: "🥈", label: "Combo Matrix" },
    "tetris_50": { icon: "🥇", label: "Arquiteto de Blocos" }
};

let knownBadges = [];

async function fetchAndShowAchievements() {
    try {
        const response = await fetch(`/api/achievements/${getSessionId()}`);
        if (response.ok) {
            const data = await response.json();
            const badges = data.badges || [];
            
            const newBadges = badges.filter(b => !knownBadges.includes(b));
            if (newBadges.length > 0) {
                knownBadges = badges;
                showAchievementToast(newBadges);
            }
        }
    } catch (e) {
        console.warn('Erro ao buscar conquistas', e);
    }
}

function showAchievementToast(newBadgeIds) {
    const container = document.getElementById('game-events-container');
    if (!container) return;
    
    // Mostra o último desbloqueado
    const latestBadgeId = newBadgeIds[newBadgeIds.length - 1];
    const badgeInfo = BADGES_MAP[latestBadgeId];
    
    if (badgeInfo) {
        const el = document.createElement('div');
        el.className = 'floating-event achievement';
        el.innerHTML = `
            <span class="achievement-title">CONQUISTA!</span>
            <strong>${badgeInfo.icon} ${badgeInfo.label}</strong>
        `;
        container.appendChild(el);
        
        // Remove após a animação (4s)
        setTimeout(() => {
            if (container.contains(el)) {
                container.removeChild(el);
            }
        }, 4000);
    }
}

/**
 * Envia uma nova pontuação de recorde para o backend
 * @param {string} name Nome do jogador
 * @param {number} score Pontuação total
 * @param {number} level Nível atingido
 * @param {number} lines Quantidade de linhas completadas
 */
/**
 * Envia uma nova pontuação de recorde para o backend de forma orquestrada (Anti-Cheat)
 * @param {string} name Nome do jogador
 * @param {number} score Pontuação total
 * @param {number} level Nível atingido
 * @param {number} lines Quantidade de linhas completadas
 * @param {Array} keystrokes Gravação de toques de teclas coletados durante a partida
 * @param {boolean} isBotSimulated Flag para simular um Bot (Cheat) e disparar o anti-cheat
 */
async function submitScore(name, score, level, lines, keystrokes = [], isBotSimulated = false) {
    try {
        const trimmedName = name.trim().toUpperCase() || 'ANÔNIMO';
        
        // Exibe o status de progresso direto no modal, entre o input e o botão
        updatePubSubStatus("ORQUESTRANDO ENTREGA DO SCORE (ANTI-CHEAT)...", "info");
        
        // Dispara a requisição assíncrona POST para o backend orquestrado
        const responsePromise = fetch('/api/orchestrate/submit-score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: trimmedName,
                score: score,
                level: level,
                lines: lines,
                session_id: getSessionId(),
                keystrokes: keystrokes,
                is_bot_simulated: isBotSimulated
            })
        });

        // --- ATUALIZAÇÃO OTIMISTA (UX EVENT-DRIVEN) ---
        // Pegamos a lista que já está renderizada em tela, adicionamos o novo score do jogador
        // localmente de forma imediata, ordenamos de forma decrescente e redesenhamos a tabela.
        const scoresListElement = document.getElementById('scores-list');
        const currentScores = [];
        
        if (scoresListElement && !isBotSimulated) {
            const listItems = scoresListElement.querySelectorAll('li:not(.loading)');
            listItems.forEach(li => {
                const nameSpan = li.querySelector('.score-name');
                const valSpan = li.querySelector('.score-val');
                if (nameSpan && valSpan) {
                    // Limpa badges ou textos extras ao obter os scores anteriores da tela
                    let cleanName = nameSpan.textContent;
                    if (cleanName.includes('[SALVANDO]')) {
                        cleanName = cleanName.replace('[SALVANDO]', '').trim();
                    }
                    const parsedScore = parseInt(valSpan.textContent.replace(/[.,\s]/g, ''), 10);
                    currentScores.push({
                        name: cleanName,
                        score: isNaN(parsedScore) ? 0 : parsedScore
                    });
                }
            });
        }
        
        if (!isBotSimulated) {
            // Adiciona o novo recorde otimista
            currentScores.push({
                name: trimmedName,
                score: score,
                level: level,
                lines: lines,
                isOptimistic: true // Ativa o efeito visual neon verde de sincronização
            });
            
            // Ordena por maior pontuação e limita aos top 10
            const sortedScores = currentScores
                .sort((a, b) => b.score - a.score)
                .slice(0, 10);
                
            // Renderiza instantaneamente em menos de 5ms na tela do jogador
            renderScores(sortedScores);
        }

        // Aguarda a resposta do backend (que executa a orquestração de anti-cheat)
        const response = await responsePromise;
        const resultData = await response.json();

        // Renderiza os logs do orquestrador no modal para fins didáticos!
        if (resultData.logs) {
            renderOrchestratorLogs(resultData.logs);
        }

        if (!response.ok) {
            if (response.status === 403) {
                updatePubSubStatus("SESSÃO BANIDA POR TRAPAÇA!", "info");
                alert("Trapaça detectada! Sua sessão foi banida permanentemente e seu score descartado.");
                location.reload(); // Recarrega para aplicar o bloqueio
                return false;
            }
            throw new Error(resultData.detail || 'Erro ao processar pontuação.');
        }

        if (resultData.status === "banned") {
            updatePubSubStatus("DETECTOR DE CHEATS: BANIDO!", "info");
            alert("AUTO-BOT DETECTADO! Sua sessão foi permanentemente banida da infraestrutura.");
            location.reload();
            return false;
        }

        // Exibe o status informando que foi recebido pela fila de mensageria com sucesso
        updatePubSubStatus("VALIDADO! SALVANDO NO FIRESTORE...", "success");

        // Retorna uma Promise que resolve após a sincronização, mantendo o modal aberto
        // para o jogador conseguir ler as etapas ocorrendo em tempo real!
        return new Promise((resolve) => {
            setTimeout(() => {
                fetchScores();
                updatePubSubStatus("GRAVAÇÃO CONCLUÍDA!", "success");
                
                // Espera mais 1 segundo com a mensagem de sucesso na tela e depois fecha o form
                setTimeout(() => {
                    updatePubSubStatus("", "hidden");
                    resolve(true); // Resolve o submit, o que fechará o form e resetará o input no game.js
                }, 1000);
                
            }, 2000); // 2 segundos para o processamento assíncrono na nuvem
        });
        
    } catch (error) {
        console.error('Erro ao registrar pontuação:', error);
        // Desfaz a alteração otimista e exibe erro
        fetchScores();
        updatePubSubStatus("FALHA AO SALVAR NA NUVEM!", "info");
        setTimeout(() => {
            updatePubSubStatus("", "hidden");
        }, 3000);
        alert('Não foi possível salvar sua pontuação no ranking da nuvem, mas parabéns pela partida!');
        return false;
    }
}

/**
 * Exibe os logs do orquestrador em um console visual didático
 * @param {Array} logs Lista de strings contendo os logs do Maestro
 */
function renderOrchestratorLogs(logs) {
    const terminalEl = document.getElementById('maestro-terminal');
    if (!terminalEl) return;
    
    terminalEl.classList.remove('hidden');
    terminalEl.innerHTML = '<div class="terminal-header">Maestro Console (GCP Workflows Engine)</div>';
    
    logs.forEach((log, index) => {
        setTimeout(() => {
            const line = document.createElement('div');
            line.className = 'terminal-line';
            
            if (log.includes('[WalletService]') || log.includes('debit') || log.includes('credit')) {
                line.classList.add('log-wallet');
            } else if (log.includes('[InventoryService]') || log.includes('unlock')) {
                line.classList.add('log-inventory');
            } else if (log.includes('[AntiCheat') || log.includes('IA')) {
                line.classList.add('log-anticheat');
            } else if (log.includes('Erro') || log.includes('FAIL') || log.includes('TRANSAÇÃO COMPENSATÓRIA')) {
                line.classList.add('log-error');
            } else {
                line.classList.add('log-maestro');
            }
            
            line.textContent = log;
            terminalEl.appendChild(line);
            terminalEl.scrollTop = terminalEl.scrollHeight;
        }, index * 250); // Efeito máquina de escrever / digitação
    });
}

// --- APIS DE INTEGRAÇÃO DA LOJA (ORQUESTRADA) ---

async function fetchStoreCatalog() {
    try {
        const response = await fetch(`/api/store/catalog/${getSessionId()}`);
        if (!response.ok) {
            if (response.status === 403) {
                return { isBanned: true };
            }
            throw new Error("Erro ao obter catálogo.");
        }
        return await response.json();
    } catch (error) {
        console.error("Erro no catálogo:", error);
        return null;
    }
}

async function buySkinOrchestrated(skinId) {
    try {
        const response = await fetch('/api/orchestrate/buy-skin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: getSessionId(),
                skin_id: skinId
            })
        });
        
        const data = await response.json();
        
        if (data.logs) {
            renderOrchestratorLogs(data.logs);
        }
        
        return data;
    } catch (error) {
        console.error("Erro na compra orquestrada:", error);
        return { status: "error", message: "Erro de rede ao conectar ao orquestrador." };
    }
}

async function equipSkin(skinId) {
    try {
        const response = await fetch('/api/inventory/select', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: getSessionId(),
                skin_id: skinId
            })
        });
        return await response.json();
    } catch (error) {
        console.error("Erro ao equipar skin:", error);
        return { status: "error" };
    }
}

/**
 * Verifica se a pontuação se qualifica para o Top 10 atual
 * @param {number} score Pontuação final do jogador
 * @param {Array} scoresList Lista atual de recordes
 * @returns {boolean} True se for um novo recorde
 */
function isHighScore(score, scoresList) {
    if (score <= 0) return false;
    // Se a lista tiver menos de 10 entradas, qualquer pontuação maior que 0 se qualifica
    if (scoresList.length < 10) return true;
    // Se não, verifica se é maior que o menor score do top 10
    const lowestHighScore = scoresList[scoresList.length - 1].score;
    return score > lowestHighScore;
}

// Executar busca de placar ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    fetchScores();
});

// Monitor de Erros Globais no Frontend integrado ao Cloud Logging via API do Backend
window.addEventListener('error', (event) => {
    // Evita loop se o próprio fetch de log falhar
    if (event.filename && event.filename.includes('api.js') && event.message.includes('api/logs')) {
        return;
    }
    fetch('/api/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message: event.message || 'Erro desconhecido no frontend',
            source: event.filename || 'unknown',
            line: event.lineno || 0,
            column: event.colno || 0,
            stack: event.error ? event.error.stack : null,
            session_id: typeof getSessionId === 'function' ? getSessionId() : null
        })
    }).catch(err => console.error('Erro ao enviar log para o backend:', err));
});
