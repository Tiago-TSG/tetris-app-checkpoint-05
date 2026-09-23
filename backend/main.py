import base64
import json
import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


# Safely import firestore to avoid NameError when real client is disabled or missing
class MockQuery:
    DESCENDING = "DESCENDING"
    ASCENDING = "ASCENDING"

class MockFirestore:
    Query = MockQuery

try:
    from google.cloud import firestore
except Exception:
    firestore = MockFirestore

# Custom formatter to produce structured JSON logs for GCP Cloud Logging
class GCPJsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "message": record.getMessage(),
            "severity": record.levelname,
            "timestamp": self.formatTime(record, self.datefmt),
            "logger": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
        }
        # Standard GCP Cloud Logging severity mapping
        severity_map = {
            "DEBUG": "DEBUG",
            "INFO": "INFO",
            "WARNING": "WARNING",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL"
        }
        log_entry["severity"] = severity_map.get(record.levelname, "INFO")
        
        # Include extra fields (e.g. session_id, transaction_id, etc.)
        standard_attrs = {
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName'
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                log_entry[key] = value
                
        return json.dumps(log_entry, ensure_ascii=False)

# Configuração do Logger Estruturado JSON
logger = logging.getLogger(__name__)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(GCPJsonFormatter())
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)
logger.propagate = False

# Inicialização segura do cliente GCP Cloud Monitoring (Métricas Personalizadas)
monitoring_client = None
project_name = None
try:
    import google.auth
    from google.cloud import monitoring_v3
    
    # Auto-detecta o ID do projeto no GCP (funciona local com ADC ou no Cloud Run)
    try:
        _, monitoring_project_id = google.auth.default()
    except Exception:
        monitoring_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        
    if monitoring_project_id:
        monitoring_client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/{monitoring_project_id}"
        logger.info(f"Cloud Monitoring client successfully initialized for project: {monitoring_project_id}")
    else:
        logger.warning("Could not auto-detect GCP project ID for Cloud Monitoring.")
except Exception as e:
    logger.warning(f"Could not initialize Cloud Monitoring Client: {e}. Metrics will be logged locally only.")

def report_custom_metric(metric_type: str, value: float, labels: dict[str, str] | None = None) -> None:
    """Envia uma métrica customizada para o Google Cloud Monitoring ou loga localmente como fallback."""
    metric_path = f"custom.googleapis.com/{metric_type}"
    if monitoring_client is None or project_name is None:
        logger.info(f"[Metric Fallback] {metric_path} -> value: {value}, labels: {labels}")
        return
    try:
        import time

        from google.cloud import monitoring_v3
        
        series = monitoring_v3.TimeSeries()
        series.metric.type = metric_path
        if labels:
            for k, v in labels.items():
                series.metric.labels[k] = str(v)
                
        series.resource.type = "global"
        
        point = monitoring_v3.Point()
        if isinstance(value, int):
            point.value.int64_value = value
        else:
            point.value.double_value = float(value)
            
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        interval = monitoring_v3.TimeInterval(
            end_time={"seconds": seconds, "nanos": nanos}
        )
        point.interval = interval
        series.points = [point]
        
        monitoring_client.create_time_series(name=project_name, time_series=[series])
        logger.info(f"Metric {metric_path} successfully reported to Cloud Monitoring.")
    except Exception as e:
        logger.warning(f"Failed to write metric {metric_type} to Cloud Monitoring: {e}")

app = FastAPI(title="Sophisticated Tetris Backend")

# Caminho para arquivo de scores (usado como fallback local)
SCORES_FILE = os.getenv("SCORES_FILE_PATH", "scores.json")
COLLECTION_NAME = "scores"
TOPIC_NAME = "scores-topic"
TELEMETRY_TOPIC_NAME = "telemetry-topic"

class ScoreEntry(BaseModel):
    name: str = Field(..., min_length=1, max_length=15)
    score: int = Field(..., ge=0)
    level: int = Field(..., ge=1)
    lines: int = Field(..., ge=0)
    session_id: str | None = Field(default=None)

class TelemetryEvent(BaseModel):
    session_id: str = Field(..., min_length=1)
    event_type: str = Field(..., pattern="^(line_clear|level_up|tetris_clear)$")
    value: int = Field(..., ge=1)

class PubSubPushPayload(BaseModel):
    message: dict
    subscription: str

# Scores padrão para inicializar o placar com estilo arcade retro
DEFAULT_SCORES = [
    {"name": "NEON_MASTER", "score": 100000, "level": 10, "lines": 100},
    {"name": "ARCADE_PRO", "score": 75000, "level": 8, "lines": 80},
    {"name": "RETRO_CHAMP", "score": 50000, "level": 5, "lines": 50},
    {"name": "TETRIS_FAN", "score": 25000, "level": 3, "lines": 30},
    {"name": "NEWBIE", "score": 5000, "level": 1, "lines": 10}
]

# Inicializa o Firestore de forma segura
db = None
if os.getenv("SCORES_FILE_PATH") == "test_scores.json":
    logger.info("Test environment detected. Disabling real Firestore client for unit tests.")
else:
    try:
        # Se houver um emulador rodando ou se estiver na nuvem (Cloud Run/GCP),
        # o SDK do Google Cloud lida com as credenciais nativamente.
        # Usamos None como padrão para que o SDK autodetecte o ID do projeto atual na nuvem.
        from google.cloud import firestore
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        db = firestore.Client(project=project_id)
        logger.info(f"Firestore client successfully initialized with project: {db.project}")
    except Exception as e:
        logger.warning(f"Could not initialize Firestore Client: {e}. Falling back to local JSON storage.")
        db = None

# Inicializa o Pub/Sub de forma segura (Publisher)
publisher = None
topic_path = None
telemetry_topic_path = None
if os.getenv("SCORES_FILE_PATH") == "test_scores.json":
    logger.info("Test environment detected. Disabling real Pub/Sub client for unit tests.")
else:
    try:
        from google.cloud import pubsub_v1
        pub_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        publisher = pubsub_v1.PublisherClient()
        
        # Se conseguirmos obter o projeto (seja da env ou resolvido pelo cliente)
        if pub_project_id or getattr(publisher, "project", None):
            resolved_project = pub_project_id or publisher.project
            topic_path = publisher.topic_path(resolved_project, TOPIC_NAME)
            telemetry_topic_path = publisher.topic_path(resolved_project, TELEMETRY_TOPIC_NAME)
            logger.info(f"Pub/Sub Publisher client successfully initialized. Topic path: {topic_path}")
            logger.info(f"Pub/Sub Telemetry Topic path initialized: {telemetry_topic_path}")
        else:
            logger.warning("Could not auto-detect GCP project for Pub/Sub. Falling back to direct database writes.")
            publisher = None
    except Exception as e:
        logger.warning(f"Could not initialize Pub/Sub Publisher Client: {e}. Falling back to direct database writes.")
        publisher = None

def load_scores_local() -> list[dict[str, Any]]:
    if not os.path.exists(SCORES_FILE):
        logger.info("Scores file not found. Pre-populating with default scores.")
        save_scores_local(DEFAULT_SCORES)
        return DEFAULT_SCORES
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading scores file: {e}. Returning default scores.")
        return DEFAULT_SCORES

def save_scores_local(scores: list[dict[str, Any]]) -> None:
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving scores file: {e}")

def populate_default_scores_firestore() -> None:
    if not db:
        return
    try:
        col_ref = db.collection(COLLECTION_NAME)
        batch = db.batch()
        for entry in DEFAULT_SCORES:
            doc_ref = col_ref.document()
            batch.set(doc_ref, entry)
        batch.commit()
        logger.info("Successfully populated Firestore with default retro scores.")
    except Exception as e:
        logger.error(f"Failed to populate default scores in Firestore: {e}")

def load_scores_from_firestore() -> list[dict[str, Any]]:
    if db is None:
        return load_scores_local()
    try:
        col_ref = db.collection(COLLECTION_NAME)
        # Buscar os top 10 ordenados por pontuação decrescente
        query = col_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(10)
        docs = list(query.stream())
        
        if not docs:
            logger.info("Firestore collection empty. Pre-populating with default scores.")
            populate_default_scores_firestore()
            docs = list(query.stream())
            
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        logger.error(f"Error loading scores from Firestore: {e}. Falling back to local file.")
        return load_scores_local()

def update_leaderboard_cache_sync():
    """Atualiza o cache materializado do Top 10 diretamente do backend."""
    if db is None:
        return
    try:
        logger.info("Atualizando cache do leaderboard (CQRS interno)...")
        scores_ref = db.collection(COLLECTION_NAME)
        query = scores_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(10)
        
        top_scores = [doc.to_dict() for doc in query.stream()]
        
        cache_ref = db.collection("cache").document("leaderboard")
        cache_ref.set({"top_10": top_scores})
        logger.info(f"Cache atualizado com sucesso! Total: {len(top_scores)}")
    except Exception as e:
        logger.error(f"Erro ao atualizar o cache internamente: {e}")

ACHIEVEMENTS_FILE = "achievements.json"

def load_achievements_local() -> dict[str, Any]:
    if not os.path.exists(ACHIEVEMENTS_FILE):
        return {}
    try:
        with open(ACHIEVEMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading local achievements: {e}")
        return {}

def save_achievements_local(data: dict[str, Any]) -> None:
    try:
        with open(ACHIEVEMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving local achievements: {e}")

def calculate_badges(total_lines: int, total_tetris: int, max_level: int) -> list[str]:
    badges = []
    # 1. Sobrevivência (Níveis)
    if max_level >= 3:
        badges.append("level_3")
    if max_level >= 7:
        badges.append("level_7")
    if max_level >= 10:
        badges.append("level_10")
        
    # 2. Volume (Acúmulo de Linhas)
    if total_lines >= 50:
        badges.append("lines_50")
    if total_lines >= 200:
        badges.append("lines_200")
    if total_lines >= 500:
        badges.append("lines_500")
        
    # 3. Habilidade (Tetris)
    if total_tetris >= 1:
        badges.append("tetris_1")
    if total_tetris >= 10:
        badges.append("tetris_10")
    if total_tetris >= 50:
        badges.append("tetris_50")
        
    return badges

# ============================================================================
# MODERNIZAÇÃO: WALLET, INVENTORY, BANS & TRANSACTIONS STATE MANAGER
# ============================================================================
WALLETS_FILE = "wallets.json"
INVENTORIES_FILE = "inventories.json"
BANS_FILE = "bans.json"
TRANSACTIONS_FILE = "transactions.json"

SKINS_CATALOG = {
    "classic": {"name": "Classic Neon", "price": 0, "description": "O tema clássico com luzes neon vibrantes."},
    "pink_panther": {"name": "Pantera Cor de Rosa", "price": 100000, "description": "Visual retrô chic super elegante em tons rosa e magenta neon."},
    "star_wars": {"name": "Star Wars: Force Neon", "price": 250000, "description": "Sabres de luz azul Jedi e vermelho Sith no espaço sideral."},
    "harry_potter": {"name": "Harry Potter: Magic Neon", "price": 500000, "description": "Estilo místico baseado nas cores das quatro casas de Hogwarts."},
    "lord_of_the_rings": {"name": "LOTR: Middle-earth", "price": 1000000, "description": "Ouro do Um Anel, verde élfico e as chamas da Montanha da Perdição."},
    "gameboy": {"name": "Retro Gameboy", "price": 10000, "description": "Uma paleta de cores verde-oliva nostalgia pura."},
    "cyberpunk": {"name": "Cyberpunk Sunset", "price": 20000, "description": "Mistura quente de rosa neon, roxo e laranja do deserto."},
    "retro_future": {"name": "Neon Blue", "price": 30000, "description": "Eletrizante tema azul ciano e azul escuro."},
    "corrupt_skin": {"name": "Corrupt Skin (Erro SAGA)", "price": 1000, "description": "Tema experimental que falha na entrega para testar SAGA."}
}

# --- WALLET PERSISTENCE ---
def load_wallets_local() -> dict[str, Any]:
    if not os.path.exists(WALLETS_FILE):
        return {}
    try:
        with open(WALLETS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading local wallets: {e}")
        return {}

def save_wallets_local(data: dict[str, Any]) -> None:
    try:
        with open(WALLETS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving local wallets: {e}")

def get_wallet_balance(session_id: str) -> int:
    session_id = session_id.upper()
    if db is None:
        wallets = load_wallets_local()
        if session_id not in wallets:
            wallets[session_id] = {"coins": 1000}
            save_wallets_local(wallets)
            return 1000
        return wallets[session_id].get("coins", 1000)
    try:
        doc = db.collection("wallets").document(session_id).get()
        if doc.exists:
            return doc.to_dict().get("coins", 1000)
        db.collection("wallets").document(session_id).set({"coins": 1000})
        return 1000
    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        return 1000

def update_wallet_balance(session_id: str, amount: int) -> bool:
    session_id = session_id.upper()
    if db is None:
        wallets = load_wallets_local()
        user_wallet = wallets.get(session_id, {"coins": 1000})
        new_balance = user_wallet["coins"] + amount
        if new_balance < 0:
            return False
        user_wallet["coins"] = new_balance
        wallets[session_id] = user_wallet
        save_wallets_local(wallets)
        return True
    try:
        doc_ref = db.collection("wallets").document(session_id)
        doc = doc_ref.get()
        current_balance = doc.to_dict().get("coins", 1000) if doc.exists else 1000
        new_balance = current_balance + amount
        if new_balance < 0:
            return False
        doc_ref.set({"coins": new_balance})
        return True
    except Exception as e:
        logger.error(f"Error updating wallet: {e}")
        return False

# --- INVENTORY PERSISTENCE ---
def load_inventories_local() -> dict[str, Any]:
    if not os.path.exists(INVENTORIES_FILE):
        return {}
    try:
        with open(INVENTORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading local inventories: {e}")
        return {}

def save_inventories_local(data: dict[str, Any]) -> None:
    try:
        with open(INVENTORIES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving local inventories: {e}")

def get_unlocked_skins(session_id: str) -> list[str]:
    session_id = session_id.upper()
    if db is None:
        inv = load_inventories_local()
        if session_id not in inv:
            inv[session_id] = {"skins": ["classic"], "active_skin": "classic"}
            save_inventories_local(inv)
            return ["classic"]
        return inv[session_id].get("skins", ["classic"])
    try:
        doc = db.collection("inventories").document(session_id).get()
        if doc.exists:
            return doc.to_dict().get("skins", ["classic"])
        db.collection("inventories").document(session_id).set({"skins": ["classic"], "active_skin": "classic"})
        return ["classic"]
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        return ["classic"]

def unlock_skin(session_id: str, skin_id: str) -> bool:
    session_id = session_id.upper()
    if skin_id == "corrupt_skin":
        logger.warning("Simulating DB error on Inventory Service for corrupt_skin")
        return False
    if db is None:
        inv = load_inventories_local()
        user_inv = inv.get(session_id, {"skins": ["classic"], "active_skin": "classic"})
        if skin_id not in user_inv["skins"]:
            user_inv["skins"].append(skin_id)
        inv[session_id] = user_inv
        save_inventories_local(inv)
        return True
    try:
        doc_ref = db.collection("inventories").document(session_id)
        doc = doc_ref.get()
        if doc.exists:
            user_inv = doc.to_dict()
            skins = user_inv.get("skins", ["classic"])
            if skin_id not in skins:
                skins.append(skin_id)
            user_inv["skins"] = skins
        else:
            user_inv = {"skins": ["classic", skin_id], "active_skin": "classic"}
        doc_ref.set(user_inv)
        return True
    except Exception as e:
        logger.error(f"Error unlocking skin: {e}")
        return False

def get_active_skin(session_id: str) -> str:
    session_id = session_id.upper()
    if db is None:
        inv = load_inventories_local()
        return inv.get(session_id, {}).get("active_skin", "classic")
    try:
        doc = db.collection("inventories").document(session_id).get()
        if doc.exists:
            return doc.to_dict().get("active_skin", "classic")
        return "classic"
    except Exception as e:
        logger.error(f"Error getting active skin: {e}")
        return "classic"

def set_active_skin(session_id: str, skin_id: str) -> bool:
    session_id = session_id.upper()
    unlocked = get_unlocked_skins(session_id)
    if skin_id not in unlocked:
        return False
    if db is None:
        inv = load_inventories_local()
        user_inv = inv.get(session_id, {"skins": ["classic"], "active_skin": "classic"})
        user_inv["active_skin"] = skin_id
        inv[session_id] = user_inv
        save_inventories_local(inv)
        return True
    try:
        doc_ref = db.collection("inventories").document(session_id)
        doc_ref.update({"active_skin": skin_id})
        return True
    except Exception as e:
        logger.error(f"Error setting active skin: {e}")
        return False

# --- BAN SERVICE PERSISTENCE ---
def load_bans_local() -> list[str]:
    if not os.path.exists(BANS_FILE):
        return []
    try:
        with open(BANS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading local bans: {e}")
        return []

def save_bans_local(data: list[str]) -> None:
    try:
        with open(BANS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving local bans: {e}")

def is_session_banned(session_id: str) -> bool:
    session_id = session_id.upper()
    if db is None:
        bans = load_bans_local()
        return session_id in bans
    try:
        doc = db.collection("bans").document(session_id).get()
        return doc.exists
    except Exception as e:
        logger.error(f"Error checking ban status: {e}")
        return False

def ban_session(session_id: str) -> None:
    session_id = session_id.upper()
    if db is None:
        bans = load_bans_local()
        if session_id not in bans:
            bans.append(session_id)
            save_bans_local(bans)
        return
    try:
        from google.cloud import firestore
        db.collection("bans").document(session_id).set({"banned_at": firestore.SERVER_TIMESTAMP})
        logger.info(f"Session {session_id} successfully banned in Firestore.")
    except Exception as e:
        logger.error(f"Error banning session: {e}")

# --- IDEMPOTENCY KEY TRANSACTIONS PERSISTENCE ---
def load_transactions_local() -> dict[str, Any]:
    if not os.path.exists(TRANSACTIONS_FILE):
        return {}
    try:
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading local transactions: {e}")
        return {}

def save_transactions_local(data: dict[str, Any]) -> None:
    try:
        with open(TRANSACTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving local transactions: {e}")

def is_transaction_processed(transaction_id: str) -> bool:
    if not transaction_id:
        return False
    if db is None:
        txs = load_transactions_local()
        return transaction_id in txs
    try:
        doc = db.collection("transactions").document(transaction_id).get()
        return doc.exists
    except Exception as e:
        logger.error(f"Error checking transaction status: {e}")
        return False

def record_transaction(transaction_id: str, payload: dict[str, Any]) -> None:
    if not transaction_id:
        return
    if db is None:
        txs = load_transactions_local()
        txs[transaction_id] = {**payload, "timestamp": os.getpid()}
        save_transactions_local(txs)
        return
    try:
        from google.cloud import firestore
        payload["timestamp"] = firestore.SERVER_TIMESTAMP
        db.collection("transactions").document(transaction_id).set(payload)
    except Exception as e:
        logger.error(f"Error recording transaction: {e}")

# --- AI ML DETECTOR HEURISTIC ---
def analyze_keystrokes_with_ml(keystrokes: list[dict[str, Any]]) -> str:
    """
    Classificador Heurístico simulando IA/ML.
    Mede desvio padrão das cadências para detectar cliques robóticos ou falta de telemetria.
    """
    if not keystrokes or len(keystrokes) < 5:
        return "Robot"
    intervals = []
    for i in range(1, len(keystrokes)):
        dt = keystrokes[i]["t"] - keystrokes[i-1]["t"]
        intervals.append(dt)
    unique_intervals = set(intervals)
    if len(unique_intervals) == 1:
        return "Robot"
    avg = sum(intervals) / len(intervals)
    variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
    std_dev = variance ** 0.5
    # Humanos têm alta variabilidade no ritmo das teclas (> 8ms de desvio padrão)
    if std_dev < 8.0:
        return "Robot"
    # Humano normal não digita a mais de 25 teclas por segundo de média sustentada
    if avg < 40.0:
        return "Robot"
    return "Human"

# --- TELEMETRY PROCESSING REWARDS INTEGRATION ---
def process_telemetry_event(event: dict[str, Any]) -> dict[str, Any]:
    session_id = event["session_id"].upper()
    event_type = event["event_type"]
    value = event["value"]
    
    if db is None:
        data = load_achievements_local()
        user_data = data.get(session_id, {
            "name": session_id,
            "total_lines_cleared": 0,
            "tetris_count": 0,
            "max_level_reached": 1,
            "badges": []
        })
        
        if event_type == "line_clear":
            user_data["total_lines_cleared"] += value
            update_wallet_balance(session_id, value * 100)
        elif event_type == "level_up":
            user_data["max_level_reached"] = max(user_data["max_level_reached"], value)
            update_wallet_balance(session_id, 500)
        elif event_type == "tetris_clear":
            user_data["tetris_count"] += value
            update_wallet_balance(session_id, value * 1000)
            
        user_data["badges"] = calculate_badges(
            user_data["total_lines_cleared"],
            user_data["tetris_count"],
            user_data["max_level_reached"]
        )
        
        data[session_id] = user_data
        save_achievements_local(data)
        return user_data
        
    try:
        ach_ref = db.collection("achievements").document(session_id)
        doc = ach_ref.get()
        
        if doc.exists:
            user_data = doc.to_dict()
        else:
            user_data = {
                "name": session_id,
                "total_lines_cleared": 0,
                "tetris_count": 0,
                "max_level_reached": 1,
                "badges": []
            }
            
        if event_type == "line_clear":
            user_data["total_lines_cleared"] += value
            update_wallet_balance(session_id, value * 100)
        elif event_type == "level_up":
            user_data["max_level_reached"] = max(user_data["max_level_reached"], value)
            update_wallet_balance(session_id, 500)
        elif event_type == "tetris_clear":
            user_data["tetris_count"] += value
            update_wallet_balance(session_id, value * 1000)
            
        user_data["badges"] = calculate_badges(
            user_data["total_lines_cleared"],
            user_data["tetris_count"],
            user_data["max_level_reached"]
        )
        
        ach_ref.set(user_data)
        logger.info(f"Achievements for {session_id} updated in Firestore.")
        return user_data
    except Exception as e:
        logger.error(f"Error processing Firestore telemetry event: {e}")
        return {}

def merge_achievements(session_id: str, player_name: str) -> None:
    if not session_id:
        return
    session_id = session_id.upper()
    player_name = player_name.upper()
    logger.info(f"Merging achievements from session {session_id} to player {player_name}...")
    
    if db is None:
        data = load_achievements_local()
        sess_data = data.get(session_id)
        if not sess_data:
            logger.warning(f"No local achievements found for session {session_id}")
            return
            
        player_data = data.get(player_name, {
            "name": player_name,
            "total_lines_cleared": 0,
            "tetris_count": 0,
            "max_level_reached": 1,
            "badges": []
        })
        
        player_data["total_lines_cleared"] += sess_data["total_lines_cleared"]
        player_data["tetris_count"] += sess_data["tetris_count"]
        player_data["max_level_reached"] = max(player_data["max_level_reached"], sess_data["max_level_reached"])
        player_data["badges"] = calculate_badges(
            player_data["total_lines_cleared"],
            player_data["tetris_count"],
            player_data["max_level_reached"]
        )
        
        data[player_name] = player_data
        if session_id in data:
            del data[session_id]
        save_achievements_local(data)
        logger.info(f"Local achievements successfully merged into player {player_name}")
        return

    try:
        ach_col = db.collection("achievements")
        sess_doc = ach_col.document(session_id).get()
        if not sess_doc.exists:
            logger.warning(f"No Firestore achievements found for session {session_id}")
            return
            
        sess_data = sess_doc.to_dict()
        player_doc = ach_col.document(player_name).get()
        
        if player_doc.exists:
            player_data = player_doc.to_dict()
        else:
            player_data = {
                "name": player_name,
                "total_lines_cleared": 0,
                "tetris_count": 0,
                "max_level_reached": 1,
                "badges": []
            }
            
        player_data["total_lines_cleared"] += sess_data["total_lines_cleared"]
        player_data["tetris_count"] += sess_data["tetris_count"]
        player_data["max_level_reached"] = max(player_data["max_level_reached"], sess_data["max_level_reached"])
        player_data["badges"] = calculate_badges(
            player_data["total_lines_cleared"],
            player_data["tetris_count"],
            player_data["max_level_reached"]
        )
        
        ach_col.document(player_name).set(player_data)
        ach_col.document(session_id).delete()
        logger.info(f"Firestore achievements from session {session_id} successfully merged into {player_name}")
    except Exception as e:
        logger.error(f"Error merging achievements: {e}")

def save_score_to_firestore(entry: dict[str, Any]) -> None:
    session_id = entry.get("session_id")
    # Limpa o session_id antes de salvar o score cru no Firestore
    score_data = {k: v for k, v in entry.items() if k != "session_id"}
    
    if db is None:
        # Se estiver no modo local, adiciona o score na lista local e salva
        local_scores = load_scores_local()
        local_scores.append(score_data)
        local_scores = sorted(local_scores, key=lambda x: x["score"], reverse=True)[:10]
        save_scores_local(local_scores)
        if session_id:
            merge_achievements(session_id, entry["name"])
        return
    try:
        col_ref = db.collection(COLLECTION_NAME)
        col_ref.add(score_data)
        logger.info(f"Score for {entry['name']} successfully saved to Firestore.")
        if session_id:
            merge_achievements(session_id, entry["name"])
        # Atualiza o cache do ranking imediatamente após salvar o score
        update_leaderboard_cache_sync()
    except Exception as e:
        logger.error(f"Error saving score to Firestore: {e}. Saving to local fallback.")
        # Em caso de erro temporário no Firestore, salva local também
        try:
            local_scores = load_scores_local()
            local_scores.append(score_data)
            local_scores = sorted(local_scores, key=lambda x: x["score"], reverse=True)[:10]
            save_scores_local(local_scores)
            if session_id:
                merge_achievements(session_id, entry["name"])
        except Exception as local_err:
            logger.error(f"Failed to save to local fallback: {local_err}")

def publish_score_to_pubsub(entry: dict[str, Any]) -> bool:
    if publisher is None or topic_path is None:
        logger.info("Pub/Sub client not active. Fallback: direct write to Firestore/local.")
        save_score_to_firestore(entry)
        return False
    try:
        # Serializar dicionário para string JSON e codificar em bytes
        data_bytes = json.dumps(entry).encode("utf-8")
        # Publicar no Pub/Sub
        future = publisher.publish(topic_path, data_bytes)
        message_id = future.result()
        logger.info(f"Score for {entry['name']} successfully published to Pub/Sub. Message ID: {message_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish to Pub/Sub: {e}. Fallback: direct write.")
        save_score_to_firestore(entry)
        return False

def publish_telemetry_to_pubsub(event: dict[str, Any]) -> bool:
    if publisher is None or telemetry_topic_path is None:
        logger.info("Pub/Sub telemetry client not active. Fallback: direct processing.")
        process_telemetry_event(event)
        return False
    try:
        # Serializar dicionário para string JSON e codificar em bytes
        data_bytes = json.dumps(event).encode("utf-8")
        # Publicar no Pub/Sub
        future = publisher.publish(telemetry_topic_path, data_bytes)
        message_id = future.result()
        logger.info(f"Telemetry event successfully published to Pub/Sub. Message ID: {message_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish telemetry to Pub/Sub: {e}. Fallback: direct processing.")
        process_telemetry_event(event)
        return False

@app.post("/api/telemetry")
def add_telemetry_event(event: TelemetryEvent):
    """Recebe eventos de telemetria (linhas, níveis, tetris) e envia para processamento assíncrono."""
    event_dict = event.model_dump()
    publish_telemetry_to_pubsub(event_dict)
    return {"status": "ok"}

@app.get("/api/achievements/{session_id}")
def get_achievements(session_id: str):
    """Busca as conquistas de um jogador específico."""
    session_id = session_id.upper()
    if db is None:
        data = load_achievements_local()
        return data.get(session_id, {"badges": []})
        
    try:
        doc = db.collection("achievements").document(session_id).get()
        if doc.exists:
            return doc.to_dict()
        return {"badges": []}
    except Exception as e:
        logger.error(f"Error fetching achievements: {e}")
        return {"badges": []}

# --- ENDPOINT DE REGISTRO DE LOGS DO FRONTEND ---
class ClientLogPayload(BaseModel):
    message: str
    source: str | None = None
    line: int | None = None
    column: int | None = None
    stack: str | None = None
    session_id: str | None = None

@app.post("/api/logs")
def add_client_log(payload: ClientLogPayload):
    """Recebe logs de erro do frontend e os envia para o Cloud Logging de forma estruturada."""
    logger.error(
        f"Frontend Error: {payload.message}",
        extra={
            "session_id": payload.session_id,
            "source_file": payload.source,
            "line_number": payload.line,
            "column_number": payload.column,
            "stack_trace": payload.stack,
            "log_origin": "frontend"
        }
    )
    return {"status": "logged"}

# ============================================================================
# MODERNIZAÇÃO: MODELOS DE DADOS PARA MICROSERVIÇOS ATÔMICOS
# ============================================================================
class WalletDebitRequest(BaseModel):
    session_id: str
    amount: int
    transaction_id: str

class WalletCreditRequest(BaseModel):
    session_id: str
    amount: int
    transaction_id: str

class InventoryUnlockRequest(BaseModel):
    session_id: str
    skin_id: str
    transaction_id: str

class AccountBanRequest(BaseModel):
    session_id: str

class AntiCheatRequest(BaseModel):
    keystrokes: list[dict[str, Any]] = Field(default=[])
    is_bot_simulated: bool = False

class BuySkinOrchestratedRequest(BaseModel):
    session_id: str
    skin_id: str

class ScoreOrchestratedRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=15)
    score: int = Field(..., ge=0)
    level: int = Field(..., ge=1)
    lines: int = Field(..., ge=0)
    session_id: str
    keystrokes: list[dict[str, Any]] = Field(default=[])
    is_bot_simulated: bool = False

# ============================================================================
# MODERNIZAÇÃO: MICROSERVIÇOS INDIVIDUAIS (APIS ATÔMICAS PARA WORKFLOWS)
# ============================================================================

@app.get("/api/wallet/{session_id}")
def api_get_wallet(session_id: str):
    """Retorna o saldo da carteira do usuário."""
    if is_session_banned(session_id):
        raise HTTPException(status_code=403, detail="Sessão permanentemente banida por bots.")
    balance = get_wallet_balance(session_id)
    return {"session_id": session_id, "coins": balance}

@app.post("/api/wallet/debit")
def api_wallet_debit(req: WalletDebitRequest):
    """Efetua um débito de moedas (Atômico & Idempotente)."""
    session_id = req.session_id.upper()
    tx_id = f"debit:{req.transaction_id}"
    
    if is_session_banned(session_id):
        raise HTTPException(status_code=403, detail="Sessão banida.")
        
    # Idempotência: Se já processada, apenas retorna sucesso
    if is_transaction_processed(tx_id):
        return {
            "status": "success",
            "message": "Idempotent: Débito já processado anteriormente.",
            "coins": get_wallet_balance(session_id)
        }
        
    # Executa a regra de negócio
    success = update_wallet_balance(session_id, -abs(req.amount))
    if not success:
        raise HTTPException(status_code=402, detail="Saldo insuficiente na carteira.")
        
    # Grava transação
    record_transaction(tx_id, {
        "type": "debit",
        "session_id": session_id,
        "amount": req.amount
    })
    
    return {
        "status": "success",
        "coins": get_wallet_balance(session_id)
    }

@app.post("/api/wallet/credit")
def api_wallet_credit(req: WalletCreditRequest):
    """Efetua um crédito/reembolso de moedas (Atômico & Idempotente)."""
    session_id = req.session_id.upper()
    tx_id = f"credit:{req.transaction_id}"
    
    if is_transaction_processed(tx_id):
        return {
            "status": "success",
            "message": "Idempotent: Crédito já processado anteriormente.",
            "coins": get_wallet_balance(session_id)
        }
        
    # Executa crédito
    update_wallet_balance(session_id, abs(req.amount))
    
    # Grava transação
    record_transaction(tx_id, {
        "type": "credit",
        "session_id": session_id,
        "amount": req.amount
    })
    
    return {
        "status": "success",
        "coins": get_wallet_balance(session_id)
    }

@app.get("/api/inventory/{session_id}")
def api_get_inventory(session_id: str):
    """Consulta as skins desbloqueadas e o tema ativo do usuário."""
    if is_session_banned(session_id):
        raise HTTPException(status_code=403, detail="Sessão banida.")
    unlocked = get_unlocked_skins(session_id)
    active = get_active_skin(session_id)
    return {"skins": unlocked, "active_skin": active}

@app.post("/api/inventory/unlock")
def api_inventory_unlock(req: InventoryUnlockRequest):
    """Desbloqueia uma skin no inventário do usuário (Atômico & Idempotente)."""
    session_id = req.session_id.upper()
    tx_id = f"unlock:{req.transaction_id}"
    
    if is_session_banned(session_id):
        raise HTTPException(status_code=403, detail="Sessão banida.")
        
    if is_transaction_processed(tx_id):
        return {"status": "success", "message": "Idempotent: Desbloqueio já efetuado."}
        
    success = unlock_skin(session_id, req.skin_id)
    if not success:
        # Se falhar (ex: corrupt_skin), retorna 500 para acionar compensação no orquestrador
        raise HTTPException(status_code=500, detail="Erro interno ao liberar skin no banco de dados.")
        
    record_transaction(tx_id, {
        "type": "unlock",
        "session_id": session_id,
        "skin_id": req.skin_id
    })
    
    return {"status": "success", "unlocked": True}

@app.post("/api/inventory/select")
def api_inventory_select(req: BuySkinOrchestratedRequest):
    """Seleciona a skin ativa para o jogo."""
    session_id = req.session_id.upper()
    if is_session_banned(session_id):
        raise HTTPException(status_code=403, detail="Sessão banida.")
    success = set_active_skin(session_id, req.skin_id)
    if not success:
        raise HTTPException(status_code=400, detail="Skin não desbloqueada ou inválida.")
    return {"status": "success", "active_skin": req.skin_id}

@app.post("/api/accounts/ban")
def api_accounts_ban(req: AccountBanRequest):
    """Bane uma conta/sessão permanentemente."""
    session_id = req.session_id.upper()
    ban_session(session_id)
    return {"status": "success", "message": f"Sessão {session_id} banida por uso de bots."}

@app.post("/api/anti-cheat/analyze")
def api_anti_cheat_analyze(req: AntiCheatRequest):
    """Executa o motor de análise de digitação com IA."""
    if req.is_bot_simulated:
        classification = "Robot"
    else:
        classification = analyze_keystrokes_with_ml(req.keystrokes)
        
    logger.info(
        f"Anti-cheat analysis performed: {classification}",
        extra={
            "classification": classification,
            "keystroke_count": len(req.keystrokes),
            "is_bot_simulated": req.is_bot_simulated
        }
    )
    report_custom_metric("tetris/anticheat/detections", 1, {"classification": classification})
    
    return {"result": classification}

# ============================================================================
# MODERNIZAÇÃO: LOCAL MAESTROS (SIMULADORES DO GOOGLE CLOUD WORKFLOWS)
# ============================================================================

@app.get("/api/store/catalog/{session_id}")
def api_store_catalog(session_id: str):
    """Helper para consolidar catálogo, moedas e estado das skins no frontend."""
    session_id = session_id.upper()
    if is_session_banned(session_id):
        raise HTTPException(status_code=403, detail="Sessão banida.")
    unlocked = get_unlocked_skins(session_id)
    active = get_active_skin(session_id)
    balance = get_wallet_balance(session_id)
    
    catalog_list = []
    for skin_id, details in SKINS_CATALOG.items():
        catalog_list.append({
            "skin_id": skin_id,
            "name": details["name"],
            "price": details["price"],
            "description": details["description"],
            "is_unlocked": skin_id in unlocked,
            "is_active": skin_id == active
        })
        
    # Ordenar o catálogo do mais barato para o mais caro
    catalog_list.sort(key=lambda x: x["price"])
        
    return {
        "catalog": catalog_list,
        "balance": balance,
        "active_skin": active
    }

@app.post("/api/orchestrate/buy-skin")
def orchestrator_buy_skin(req: BuySkinOrchestratedRequest):
    """
    SIMULADOR LOCAL DO GCP WORKFLOWS (SAGA DESIGN PATTERN).
    Orquestra a compra da skin chamando as APIs atômicas com retries e compensação.
    """
    session_id = req.session_id.upper()
    skin_id = req.skin_id
    transaction_id = f"TX-BUY-{session_id}-{skin_id}"
    
    logs = []
    logs.append(f"[Workflows] Iniciando fluxo 'buy_skin_workflow' para a sessão {session_id}")
    
    logger.info(
        f"Starting SAGA buy skin workflow for session {session_id}, skin {skin_id}",
        extra={
            "session_id": session_id,
            "skin_id": skin_id,
            "transaction_id": transaction_id,
            "saga_step": "init"
        }
    )
    
    # Validações iniciais (Catálogo)
    if skin_id not in SKINS_CATALOG:
        logs.append(f"[Workflows] Erro: Skin '{skin_id}' não cadastrada no Catálogo.")
        logger.warning(
            f"SAGA buy skin failed: skin {skin_id} not in catalog",
            extra={
                "session_id": session_id,
                "skin_id": skin_id,
                "transaction_id": transaction_id,
                "saga_step": "invalid_skin"
            }
        )
        raise HTTPException(status_code=400, detail={"message": "Skin inválida", "logs": logs})
        
    details = SKINS_CATALOG[skin_id]
    price = details["price"]
    unlocked = get_unlocked_skins(session_id)
    
    if skin_id in unlocked:
        logs.append(f"[Workflows] Erro: Usuário já possui a skin '{skin_id}'.")
        logger.warning(
            f"SAGA buy skin failed: skin {skin_id} already unlocked",
            extra={
                "session_id": session_id,
                "skin_id": skin_id,
                "transaction_id": transaction_id,
                "saga_step": "already_owned"
            }
        )
        raise HTTPException(status_code=400, detail={"message": "Skin já adquirida", "logs": logs})
        
    # --- STEP 1: DEBITAR CARTEIRA ---
    logs.append(f"[Workflows] Executando chamada HTTP POST -> /api/wallet/debit (Preço: {price})")
    
    # Simulação de Retry do Workflow (Exemplo meramente visual de resiliência de rede)
    logs.append("[Workflows] (Tentativa 1/5) Conectando ao Wallet Service...")
    
    debit_payload = WalletDebitRequest(session_id=session_id, amount=price, transaction_id=transaction_id)
    try:
        api_wallet_debit(debit_payload)
        logs.append("[WalletService] Débito efetuado com sucesso! Saldo atualizado.")
        logger.info(
            f"SAGA Step 1: Wallet debit successful for {session_id}",
            extra={
                "session_id": session_id,
                "skin_id": skin_id,
                "transaction_id": transaction_id,
                "amount_debited": price,
                "saga_step": "debit_success"
            }
        )
    except HTTPException as e:
        logs.append(f"[WalletService] ERRO: Débito rejeitado (Código: {e.status_code}, Detalhe: {e.detail})")
        logs.append("[Workflows] Fluxo abortado antes de alterar inventário.")
        logger.warning(
            f"SAGA Step 1 Failed: Wallet debit rejected (code {e.status_code})",
            extra={
                "session_id": session_id,
                "skin_id": skin_id,
                "transaction_id": transaction_id,
                "error_detail": e.detail,
                "saga_step": "debit_failed"
            }
        )
        raise HTTPException(status_code=e.status_code, detail={"message": e.detail, "logs": logs})
        
    # --- STEP 2: ATIVAR INVENTÁRIO ---
    logs.append(f"[Workflows] Executando chamada HTTP POST -> /api/inventory/unlock (Skin: '{skin_id}')")
    logs.append("[Workflows] (Tentativa 1/5) Conectando ao Inventory Service...")
    
    unlock_payload = InventoryUnlockRequest(session_id=session_id, skin_id=skin_id, transaction_id=transaction_id)
    try:
        api_inventory_unlock(unlock_payload)
        logs.append(f"[InventoryService] Skin '{skin_id}' adicionada ao inventário do jogador!")
        logger.info(
            f"SAGA Step 2: Inventory unlock successful for {session_id}",
            extra={
                "session_id": session_id,
                "skin_id": skin_id,
                "transaction_id": transaction_id,
                "saga_step": "unlock_success"
            }
        )
    except HTTPException as e:
        logs.append(f"[InventoryService] ERRO CRÍTICO: Falha ao desbloquear skin no banco (Código: {e.status_code})")
        logger.error(
            f"SAGA Step 2 Failed: Inventory unlock failed (code {e.status_code}). Triggering rollback.",
            extra={
                "session_id": session_id,
                "skin_id": skin_id,
                "transaction_id": transaction_id,
                "saga_step": "unlock_failed"
            }
        )
        
        # --- TRANSAÇÃO COMPENSATÓRIA (SAGA ROLLBACK) ---
        logs.append("[Workflows] Falha detectada no passo 2! Iniciando rollback da transação (SAGA Compensatória)...")
        logs.append(f"[Workflows] Executando compensação HTTP POST -> /api/wallet/credit (Reembolso: {price})")
        
        try:
            credit_payload = WalletCreditRequest(session_id=session_id, amount=price, transaction_id=transaction_id + "-COMPENSATE")
            api_wallet_credit(credit_payload)
            logs.append(f"[WalletService] Reembolso de {price} moedas creditado com sucesso!")
            logs.append("[Workflows] SAGA compensação executada. Dinheiro devolvido. Transação desfeita de forma consistente.")
            logger.info(
                f"SAGA Rollback: Wallet successfully refunded for {session_id}",
                extra={
                    "session_id": session_id,
                    "skin_id": skin_id,
                    "transaction_id": transaction_id,
                    "saga_step": "rollback_success"
                }
            )
            report_custom_metric("tetris/store/skins_sold", 1, {"skin_id": skin_id, "status": "rolled_back"})
        except Exception as err:
            # DLQ (Dead Letter Queue) caso o rollback também falhe!
            logs.append("[WalletService] ERRO CRÍTICO COMPLEMENTAR: Falha catastrófica ao reembolsar jogador!")
            logs.append("[Workflows] !!! REDIRECIONANDO ERRO PARA SAGA-DLQ (Dead Letter Queue do Pub/Sub) !!!")
            logs.append(f"[Workflows] ID de rastreamento salvo na DLQ: {transaction_id}-DLQ-ERROR")
            logger.critical(
                "SAGA CRITICAL FAILURE: SAGA rollback failed! Routing to DLQ.",
                extra={
                    "session_id": session_id,
                    "skin_id": skin_id,
                    "transaction_id": transaction_id,
                    "error_detail": str(err),
                    "saga_step": "dlq_error"
                }
            )
            report_custom_metric("tetris/store/skins_sold", 1, {"skin_id": skin_id, "status": "dlq_error"})
            return {
                "status": "dlq_error",
                "message": "Erro gravíssimo! A transação de compensação falhou e o incidente foi salvo na DLQ.",
                "logs": logs
            }
            
        return {
            "status": "rolled_back",
            "message": "Falha no serviço de inventário. A compra foi abortada e o saldo foi compensado (reembolsado)!",
            "logs": logs
        }
        
    logs.append("[Workflows] Fluxo 'buy_skin_workflow' executado com 100% de sucesso!")
    report_custom_metric("tetris/store/skins_sold", 1, {"skin_id": skin_id, "status": "success"})
    return {
        "status": "success",
        "message": "Skin desbloqueada e comprada!",
        "logs": logs,
        "new_balance": get_wallet_balance(session_id)
    }

@app.post("/api/orchestrate/submit-score")
def orchestrator_submit_score(req: ScoreOrchestratedRequest):
    """
    SIMULADOR LOCAL DO GCP WORKFLOWS (DECISION TREE).
    Orquestra a triagem do placar via Anti-Cheat com IA, banimento ou gravação com moedas.
    """
    session_id = req.session_id.upper()
    logs = []
    
    logs.append(f"[Workflows] Iniciando fluxo 'submit_score_workflow' para o jogador '{req.name}'")
    
    logger.info(
        f"Starting submit score workflow for player {req.name}, session {session_id}",
        extra={
            "session_id": session_id,
            "player_name": req.name,
            "score": req.score,
            "level": req.level,
            "lines": req.lines
        }
    )
    
    # --- STEP 1: CONSULTAR BANIMENTO ---
    logs.append("[Workflows] Executando consulta HTTP GET -> /api/accounts/status")
    if is_session_banned(session_id):
        logs.append(f"[AccountService] REJEITADO: A sessão '{session_id}' foi identificada como BANIDA por fraude.")
        logs.append("[Workflows] Bloqueando fluxo. Scoreboard ignorado.")
        logger.warning(
            f"Score submission blocked: session {session_id} is already banned",
            extra={
                "session_id": session_id,
                "player_name": req.name,
                "score": req.score,
                "decision": "blocked"
            }
        )
        raise HTTPException(status_code=403, detail={"message": "Usuário banido permanentemente.", "logs": logs})
        
    # --- STEP 2: CLASSIFICAÇÃO DE IA ANTI-CHEAT ---
    logs.append(f"[Workflows] Executando chamada HTTP POST -> /api/anti-cheat/analyze ({len(req.keystrokes)} teclas coletadas)")
    
    cheat_req = AntiCheatRequest(keystrokes=req.keystrokes, is_bot_simulated=req.is_bot_simulated)
    cheat_res = api_anti_cheat_analyze(cheat_req)
    classification = cheat_res["result"]
    
    logs.append(f"[AntiCheatService] IA classificou o estilo de jogo como: '{classification.upper()}'")
    
    # --- STEP 3: CONDICIONAL (DECISION TREE) ---
    if classification == "Robot":
        logs.append("[Workflows] Decisão: ROTA BOT (Rígida). Acionando banimento de conta.")
        logs.append("[Workflows] Executando chamada HTTP POST -> /api/accounts/ban")
        
        ban_payload = AccountBanRequest(session_id=session_id)
        api_accounts_ban(ban_payload)
        
        logs.append("[Workflows] Placar de trapaça descartado. Conta banida da infraestrutura.")
        logger.warning(
            f"Score submission rejected for session {session_id}: Classified as Robot. Session banned.",
            extra={
                "session_id": session_id,
                "player_name": req.name,
                "score": req.score,
                "classification": "Robot",
                "decision": "ban"
            }
        )
        report_custom_metric("tetris/game/scores_submitted", 1, {"status": "banned"})
        return {
            "status": "banned",
            "message": "Uso de Auto-Bot/Cheat detectado pela IA! Sua sessão foi banida permanentemente.",
            "logs": logs
        }
    else:
        logs.append("[Workflows] Decisão: ROTA HUMANA (Segura). Salvando score na coreografia legada.")
        logs.append("[Workflows] Executando chamada HTTP POST -> /api/scores/publish (Score: " + str(req.score) + ")")
        
        score_entry = {
            "name": req.name.upper(),
            "score": req.score,
            "level": req.level,
            "lines": req.lines,
            "session_id": session_id
        }
        # Dispara no Pub/Sub legado sem alterar o comportamento existente
        publish_score_to_pubsub(score_entry)
        
        # --- RECOMPENSA DE MOEDAS ---
        # 100% do score vira moedas na carteira do jogador!
        coins_reward = max(1, int(req.score))
        logs.append(f"[Workflows] Gerando recompensa de score: {coins_reward} moedas adicionadas à carteira.")
        update_wallet_balance(session_id, coins_reward)
        
        logs.append("[Workflows] Fluxo 'submit_score_workflow' finalizado com sucesso!")
        logger.info(
            f"Score submission successful for human player {req.name}, session {session_id}",
            extra={
                "session_id": session_id,
                "player_name": req.name,
                "score": req.score,
                "classification": "Human",
                "decision": "publish"
            }
        )
        report_custom_metric("tetris/game/scores_submitted", 1, {"status": "success"})
        return {
            "status": "success",
            "message": "Partida humana validada! Pontuação gravada e moedas creditadas.",
            "logs": logs
        }

@app.post("/api/internal/telemetry-worker")
def telemetry_pubsub_push_receiver(payload: PubSubPushPayload):
    """Webhook para o Pub/Sub processar os eventos de telemetria assincronamente."""
    try:
        message_data = payload.message.get("data")
        if not message_data:
            raise HTTPException(status_code=400, detail="Invalid Pub/Sub message")
            
        decoded_str = base64.b64decode(message_data).decode("utf-8")
        event_dict = json.loads(decoded_str)
        validated_event = TelemetryEvent(**event_dict)
        
        process_telemetry_event(validated_event.model_dump())
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing telemetry Push message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process telemetry message: {e!s}")

@app.get("/api/scores", response_model=list[dict[str, Any]])
def get_scores():
    """
    Recupera os 10 melhores placares usando Cache Materializado.
    Lê apenas um documento estático gerado pela Cloud Function (Trigger).
    """
    if db:
        try:
            # Leitura Otimizada: 1 única leitura de documento em vez de query na coleção
            cache_doc = db.collection("cache").document("leaderboard").get()
            
            if cache_doc.exists:
                logger.info("Retornando scores do cache otimizado.")
                report_custom_metric("tetris/db/cache_hits", 1, {"source": "cache"})
                return cache_doc.to_dict().get("top_10", [])
            else:
                logger.warning("Cache não encontrado. Fazendo fallback para query pesada e leitura local.")
                report_custom_metric("tetris/db/cache_hits", 1, {"source": "query_fallback"})
                # Fallback caso a Cloud Function ainda não tenha criado o cache
                scores = load_scores_from_firestore()
                return sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
                
        except Exception as e:
            logger.error(f"Erro ao ler do cache do Firestore: {e}")
            report_custom_metric("tetris/db/cache_hits", 1, {"source": "query_fallback"})
            scores = load_scores_from_firestore()
            return sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    else:
        scores = load_scores_local()
        return sorted(scores, key=lambda x: x["score"], reverse=True)[:10]

@app.post("/api/scores", response_model=list[dict[str, Any]])
def add_score(entry: ScoreEntry):
    """Adiciona um novo placar. Publica no Pub/Sub de forma assíncrona se disponível."""
    logger.info(f"Adding score: {entry.name} - {entry.score}")
    entry_dict = entry.model_dump()
    publish_score_to_pubsub(entry_dict)
    return get_scores()

@app.post("/api/internal/scores-worker")
def pubsub_push_receiver(payload: PubSubPushPayload):
    """Gatilho Push do Pub/Sub que recebe mensagens assíncronas e grava no Firestore."""
    try:
        # Extrair dados da mensagem
        message_data = payload.message.get("data")
        if not message_data:
            raise HTTPException(status_code=400, detail="Invalid Pub/Sub message: missing 'data'")
            
        # Decodificar de base64 para string UTF-8
        decoded_bytes = base64.b64decode(message_data)
        decoded_str = decoded_bytes.decode("utf-8")
        
        # Converter a string em dicionário JSON
        entry_dict = json.loads(decoded_str)
        logger.info(f"Pub/Sub Push received message: {entry_dict}")
        
        # Validar dados usando o modelo de entrada
        validated_entry = ScoreEntry(**entry_dict)
        
        # Gravar no Firestore (ou fallback local se db for None)
        save_score_to_firestore(validated_entry.model_dump())
        
        return {"status": "success", "message": "Score successfully persisted via Pub/Sub"}
    except Exception as e:
        logger.error(f"Error processing Pub/Sub Push message: {e}")
        # Retorna erro 500 para o Pub/Sub saber que deve tentar novamente (retry)
        raise HTTPException(status_code=500, detail=f"Failed to process message: {e!s}")

# Montagem dos arquivos estáticos do frontend.
# Criamos a pasta estática se não existir para evitar erros ao iniciar o FastAPI
STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
