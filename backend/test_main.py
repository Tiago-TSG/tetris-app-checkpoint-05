import base64
import json
import os
import unittest
from unittest.mock import MagicMock, patch

# Configura variáveis de ambiente de teste antes de importar o main
os.environ["SCORES_FILE_PATH"] = "test_scores.json"

from backend import main


class TestTetrisBackend(unittest.TestCase):
    def setUp(self):
        # Limpar arquivos de teste locais se existirem
        files_to_remove = ["test_scores.json", "wallets.json", "inventories.json", "bans.json", "transactions.json"]
        for f in files_to_remove:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass
        # Resetar mocks globais do módulo
        main.db = None
        main.publisher = None
        main.topic_path = None

    def tearDown(self):
        # Limpar arquivos de teste locais se existirem
        files_to_remove = ["test_scores.json", "wallets.json", "inventories.json", "bans.json", "transactions.json"]
        for f in files_to_remove:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

    def test_local_fallback_load_default(self):
        """Testa se carrega os scores padrão se o arquivo não existir."""
        scores = main.load_scores_local()
        self.assertEqual(len(scores), 5)
        self.assertEqual(scores[0]["name"], "NEON_MASTER")

    def test_local_fallback_save_and_load(self):
        """Testa se salva e carrega corretamente localmente."""
        test_data = [{"name": "TEST_PLAYER", "score": 999999, "level": 10, "lines": 100}]
        main.save_scores_local(test_data)
        scores = main.load_scores_local()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["name"], "TEST_PLAYER")

    @patch("backend.main.db")
    def test_firestore_load_empty_populates_defaults(self, mock_db):
        """Testa se popula valores padrão no Firestore se a coleção estiver vazia."""
        main.db = mock_db
        
        # Mocar coleções e consultas do Firestore
        mock_col = MagicMock()
        mock_query = MagicMock()
        mock_db.collection.return_value = mock_col
        mock_col.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Primeira chamada de stream() retorna lista vazia (coleção sem nada)
        # Segunda chamada (após popular) retorna o documento mocado
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {"name": "MOCK_CHAMP", "score": 120000}
        
        mock_query.stream.side_effect = [[], [mock_doc]]
        
        # Chamar a função de carregamento do Firestore
        scores = main.load_scores_from_firestore()
        
        # Verificar se o batch foi criado para popular os dados padrões
        mock_db.batch.assert_called_once()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["name"], "MOCK_CHAMP")

    @patch("backend.main.db")
    def test_firestore_save_score(self, mock_db):
        """Testa o salvamento de um score no Firestore."""
        main.db = mock_db
        mock_col = MagicMock()
        mock_db.collection.return_value = mock_col
        
        test_entry = {"name": "NEW_HERO", "score": 150000, "level": 12, "lines": 120}
        main.save_score_to_firestore(test_entry)
        
        # Verifica se o documento foi adicionado na coleção do Firestore
        mock_col.add.assert_called_once_with(test_entry)

    @patch("backend.main.publisher")
    def test_pubsub_publish_success(self, mock_publisher):
        """Testa a publicação bem-sucedida de um score no Pub/Sub."""
        main.publisher = mock_publisher
        main.topic_path = "projects/test-project/topics/scores-topic"
        
        # Moca o retorno do publish (Future)
        mock_future = MagicMock()
        mock_future.result.return_value = "msg_123456"
        mock_publisher.publish.return_value = mock_future
        
        test_entry = {"name": "PUBSUB_PRO", "score": 300000, "level": 15, "lines": 150}
        success = main.publish_score_to_pubsub(test_entry)
        
        self.assertTrue(success)
        mock_publisher.publish.assert_called_once()
        
        # Verifica se o payload em bytes foi enviado corretamente
        args, _ = mock_publisher.publish.call_args
        self.assertEqual(args[0], "projects/test-project/topics/scores-topic")
        sent_bytes = args[1]
        decoded_sent_data = json.loads(sent_bytes.decode("utf-8"))
        self.assertEqual(decoded_sent_data["name"], "PUBSUB_PRO")

    @patch("backend.main.db")
    def test_pubsub_push_receiver_success(self, mock_db):
        """Testa se a rota Push do Pub/Sub decodifica a mensagem e salva no Firestore."""
        main.db = mock_db
        mock_col = MagicMock()
        mock_db.collection.return_value = mock_col
        
        # Constrói dados da partida mocado
        score_data = {"name": "PUBSUB_HERO", "score": 250000, "level": 15, "lines": 150}
        # Codifica o JSON da partida em Base64
        encoded_data = base64.b64encode(json.dumps(score_data).encode("utf-8")).decode("utf-8")
        
        # Constrói o payload estruturado como o Pub/Sub envia via Push
        payload = main.PubSubPushPayload(
            message={"data": encoded_data, "messageId": "12345"},
            subscription="projects/test-project/subscriptions/scores-topic-sub"
        )
        
        # Aciona o receiver diretamente no módulo
        response = main.pubsub_push_receiver(payload)
        
        self.assertEqual(response["status"], "success")
        # Garante que o método add() do Firestore foi chamado com o score decodificado
        mock_col.add.assert_called_once_with(score_data)

    # --- NOVO: TESTES DA ARQUITETURA ORQUESTRADA ---

    def test_wallet_idempotency(self):
        """Testa se as operações de débito e crédito na carteira respeitam as chaves de idempotência."""
        session_id = "TEST_IDEMPOTENCY"
        
        # Saldo inicial é 1000
        balance = main.get_wallet_balance(session_id)
        self.assertEqual(balance, 1000)
        
        # Primeiro débito: Sucesso
        debit_req = main.WalletDebitRequest(session_id=session_id, amount=200, transaction_id="TX-123")
        res1 = main.api_wallet_debit(debit_req)
        self.assertEqual(res1["status"], "success")
        self.assertEqual(res1["coins"], 800)
        
        # Segundo débito idêntico (idempotente): Deve retornar o mesmo saldo de 800 sem cobrar de novo
        res2 = main.api_wallet_debit(debit_req)
        self.assertEqual(res2["coins"], 800)
        self.assertTrue("Idempotent" in res2["message"])
        
        # Primeiro reembolso (crédito): Sucesso
        credit_req = main.WalletCreditRequest(session_id=session_id, amount=200, transaction_id="TX-123-COMP")
        res3 = main.api_wallet_credit(credit_req)
        self.assertEqual(res3["coins"], 1000)
        
        # Segundo crédito idêntico (idempotente): Deve ignorar sem adicionar moedas extras
        res4 = main.api_wallet_credit(credit_req)
        self.assertEqual(res4["coins"], 1000)

    def test_saga_buy_skin_success(self):
        """Testa a orquestração bem-sucedida de compra de skin."""
        session_id = "TEST_SAGA_OK"
        # Inicializa carteira com saldo suficiente de 15000 moedas (gameboy custa 10000)
        main.update_wallet_balance(session_id, 14000) # 1000 + 14000 = 15000
        
        req = main.BuySkinOrchestratedRequest(session_id=session_id, skin_id="gameboy")
        res = main.orchestrator_buy_skin(req)
        
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["new_balance"], 5000) # De 15000 cobrou 10000
        
        # Verifica se o inventário tem a skin
        skins = main.get_unlocked_skins(session_id)
        self.assertIn("gameboy", skins)

    def test_saga_buy_skin_compensatory_rollback(self):
        """Testa a transação compensatória (SAGA rollback) quando a entrega de skin falha."""
        session_id = "TEST_SAGA_FAIL"
        # Inicializa carteira com saldo suficiente de 1000 moedas (corrupt_skin custa 1000)
        main.update_wallet_balance(session_id, 0) # Força saldo 1000
        
        # corrupt_skin força erro no serviço de inventário
        req = main.BuySkinOrchestratedRequest(session_id=session_id, skin_id="corrupt_skin")
        res = main.orchestrator_buy_skin(req)
        
        # O Maestro detecta o erro e reembolsa
        self.assertEqual(res["status"], "rolled_back")
        self.assertIn("compra foi abortada e o saldo foi compensado", res["message"])
        
        # Garante que o saldo do jogador foi restaurado para 1000 moedas
        balance = main.get_wallet_balance(session_id)
        self.assertEqual(balance, 1000)
        
        # Garante que a skin NÃO foi liberada
        skins = main.get_unlocked_skins(session_id)
        self.assertNotIn("corrupt_skin", skins)

    def test_orchestrate_submit_score_human(self):
        """Testa se a orquestração de placar valida partidas humanas e as envia para gravação."""
        session_id = "TEST_HUMAN"
        
        # Mock de keystrokes humanos (tempo variável)
        keystrokes = [
            {"key": "ArrowLeft", "t": 100.0},
            {"key": "ArrowUp", "t": 250.0},
            {"key": "ArrowRight", "t": 480.0},
            {"key": "ArrowDown", "t": 690.0},
            {"key": "Space", "t": 950.0}
        ]
        
        req = main.ScoreOrchestratedRequest(
            name="HUMAN_PRO",
            score=5000,
            level=3,
            lines=15,
            session_id=session_id,
            keystrokes=keystrokes
        )
        
        res = main.orchestrator_submit_score(req)
        self.assertEqual(res["status"], "success")
        self.assertIn("Partida humana validada", res["message"])
        
        # Verifica se ganhou moedas de recompensa (100% do score = 5000 moedas)
        balance = main.get_wallet_balance(session_id)
        self.assertEqual(balance, 6000) # 1000 inicial + 5000 recompensa

    def test_orchestrate_submit_score_robot_bans(self):
        """Testa se a orquestração detecta bot, bloqueia salvamento e bane a sessão."""
        session_id = "TEST_ROBOT"
        
        # Mock de keystrokes robóticos (perfeitamente espaçados de 50ms)
        keystrokes = [
            {"key": "ArrowLeft", "t": 50.0},
            {"key": "ArrowLeft", "t": 100.0},
            {"key": "ArrowLeft", "t": 150.0},
            {"key": "ArrowLeft", "t": 200.0},
            {"key": "ArrowLeft", "t": 250.0}
        ]
        
        req = main.ScoreOrchestratedRequest(
            name="BOT_CHEAT",
            score=900000,
            level=20,
            lines=200,
            session_id=session_id,
            keystrokes=keystrokes
        )
        
        res = main.orchestrator_submit_score(req)
        self.assertEqual(res["status"], "banned")
        self.assertIn("Uso de Auto-Bot/Cheat detectado", res["message"])
        
        # Verifica se a sessão foi incluída no Ban Service
        self.assertTrue(main.is_session_banned(session_id))
        
        # Tenta enviar de novo após banido: Deve ser barrado imediatamente
        with self.assertRaises(main.HTTPException) as context:
            main.orchestrator_submit_score(req)
        self.assertEqual(context.exception.status_code, 403)

if __name__ == "__main__":
    unittest.main()