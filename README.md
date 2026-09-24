# 🕹️ Retro Neon Tetris — Cloud Run Arcade (Microservices Saga, Anti-Cheat, Observability & DevSecOps Edition)

Uma versão moderna, estilosa e extremamente sofisticada do clássico jogo **Tetris**, projetada com visual retro-wave/neon (Synthwave) e **Sintetizador de Áudio Procedural** nativo no navegador (usando a Web Audio API).

Esta versão (**Checkpoint 05**) consolida a **Automação DevSecOps** com uma pipeline completa de CI/CD via GitHub Actions e portões robustos de segurança e qualidade. O projeto herda e aprimora a **Arquitetura baseada em Microserviços e Orquestração Avançada (Saga Pattern & Decision Trees - Checkpoint 03)** e a **Instrumentação e Observabilidade Nativa no GCP (Cloud Logging & Cloud Monitoring - Checkpoint 04)**, agregando ferramentas automáticas de SAST (Bandit), SCA (Trivy), detecção de segredos (Gitleaks), conformidade sintática (ESLint, Ruff, Hadolint), testes unitários contínuos e implantação contínua segura via WIF no Google Cloud Run.

## 🎨 Interface do Jogo

![Tela do Jogo Tetris Neon](tetris-app.jpg)

*Visualização da interface com estilo neon synthwave, exibindo o canvas do jogo (centro), controles (esquerda), próximas peças e estatísticas (direita) com sistema de ranking integrado.*

O projeto é estruturado com um backend assíncrono em **Python (FastAPI)** que gerencia a API de pontuações de recorde persistida no Firestore. O frontend é servido de forma estática, construído em **HTML5 Canvas, CSS moderno e JavaScript Vanilla** com **UI Otimista** para respostas instantâneas e **Feedback Visual de Conquistas**.

Este aplicativo foi planejado e otimizado especificamente para rodar localmente e ser facilmente implantado de forma escalável no **Google Cloud Run (GCP)**.

---

## 🚀 Funcionalidades e Diferenciais
*   **Sintetizador de Áudio Procedural (Web Audio API):** Som clássico de arcade gerado por código diretamente na placa de som do seu computador, dispensando carregamento de arquivos externos `.wav` ou `.mp3`.
*   **Interface Assíncrona Otimista (Novo):** O frontend não trava esperando o banco de dados. Os placares são inseridos na tela instantaneamente enquanto o Pub/Sub garante a gravação no fundo.
*   **Telemetria em Tempo Real e Conquistas (Novo):** O jogo captura eventos de "Level Up", "Tetris" e "Linhas Limpas" em tempo real, desbloqueando **Badges (Troféus)** que aparecem brilhando no meio da tela e ficam gravados ao lado do seu nome no Ranking mundial.
*   **Algoritmo Bag-of-7 (Mecânica Justa):** Geração de peças igual à do Tetris oficial de campeonato, garantindo que o jogador não sofra com sequências de azar sem peças fundamentais.
*   **Sistema de Níveis Progressivo:** O nível de dificuldade aumenta a cada 10 linhas removidas, acelerando a queda das peças de forma fluida e aplicando multiplicadores à pontuação.

---

## 🏛️ Evolução Arquitetural (Fases 1 a 6)

O projeto original usava armazenamento local em disco, o que é incompatível com a natureza Serverless Efêmera do Cloud Run. O sistema foi refatorado nas seguintes fases:

### Fase 1: Persistência Robusta
*   **Google Cloud Firestore:** O backend foi integrado ao banco de dados NoSQL gerenciado do Google. Todos os scores recebidos são gravados de forma permanente, resolvendo o problema de perda de dados.

### Fase 2: Event-Driven Architecture e CQRS
O sistema agora separa completamente as responsabilidades de leitura (Query) e escrita (Command).
1.  **Ingestão e Escrita (Pub/Sub):** Quando um jogador envia um placar, a API principal do FastAPI apenas publica a mensagem no tópico do **Google Cloud Pub/Sub** e responde "Sucesso" na mesma hora (absorvendo picos de tráfego).
2.  **Processamento Assíncrono (Webhook):** A fila do Pub/Sub envia a mensagem em background (via protocolo Push) para a rota interna `/api/internal/scores-worker`.
3.  **Geração do Cache Materializado (CQRS):** Após o worker gravar o score cru no Firestore, ele próprio processa o novo ranking ("Top 10") e salva um documento consolidado em `/cache/leaderboard`.
4.  **Leitura Otimizada:** Quando milhares de jogadores abrem o jogo simultaneamente, a rota `GET /api/scores` lê **apenas 1 documento estático** do Firestore (o cache), reduzindo a latência a milissegundos e eliminando o custo em nuvem de queries de ordenação massivas.

### Fase 3: Telemetria e Padrão Fan-out (Coreografia)
A arquitetura foi expandida para suportar monitoramento de eventos ao vivo durante a partida.
1.  **Emissão de Eventos (Frontend):** O `game.js` dispara pacotes silenciosos para a API sempre que o jogador sobe de nível ou faz um Tetris.
2.  **Barramento de Mensageria:** A API despacha esses eventos para um segundo tópico do Pub/Sub (`telemetry-topic`).
3.  **Coreografia Autônoma:** Um Webhook secundário (`/api/internal/telemetry-worker`) ouve a fila, atualiza os contadores globais do jogador e roda o "Motor de Regras" para conceder medalhas na coleção `achievements`, de forma totalmente desacoplada do salvamento principal de scores.

### Fase 4: Microserviços, Orquestração e Anti-Cheat com IA
O sistema monolítico foi refatorado e expandido adotando padrões modernos de orquestração distribuída (simulando capacidades do Google Cloud Workflows):
1. **APIs Atômicas (Desacoplamento):** Lógicas separadas em microserviços virtuais: Carteira Virtual (Moedas), Inventário de Temas, Gestão de Contas (Banimentos) e Validação de Segurança.
2. **Loja de Skins (Padrão Saga):** Novo fluxo orquestrado `buy_skin_workflow`. Ao comprar um tema, o serviço debita a carteira e desbloqueia no inventário. Se houver falha, ele executa uma **transação compensatória (rollback)** para reembolsar o saldo, garantindo consistência atômica.
3. **Validação de Scores (Árvore de Decisão e Anti-Cheat):** O envio de placar passa pelo fluxo `submit_score_workflow`. Um Motor Heurístico analisa a cadência dos toques do teclado: Se detectar bot, bane permanentemente. Se for humano, recompensa o usuário com moedas virtuais além de registrar o placar.
4. **Terminal Maestro e UI Didática:** Introdução de um console interativo estilo hacker no front-end para visualizar a orquestração em tempo real.
5. **Engine de Áudio Expandida:** Sintetizador turbinado de 1 para 6 oitavas de cobertura (C2 a B7), com script matemático para compilar clássicos (Senhor dos Anéis em BPM perfeito, Star Wars, Pink Panther) renderizados no Web Audio API nativo.

### Fase 5: Observabilidade e Instrumentação no GCP (Checkpoint 04)
A arquitetura evoluiu para contemplar governança e confiabilidade corporativas completas, introduzindo instrumentação nativa do Google Cloud de ponta a ponta (Logs, Métricas e Traces):
1. **Logs Estruturados em JSON (Cloud Logging):** O logger padrão do backend em Python foi modificado para utilizar uma classe customizada `GCPJsonFormatter`. Todos os registros de log agora são impressos em streams de saída estruturados em JSON no formato esperado pelo GCP, injetando automaticamente campos como `severity`, `session_id`, `saga_step`, `transaction_id` e metadados de execução.
2. **Métricas Personalizadas (Cloud Monitoring):** Integração segura com o SDK do Google Cloud Monitoring para emitir métricas personalizadas de negócio e infraestrutura de forma assíncrona, incluindo:
   - `tetris/store/skins_sold`: Contagem de transações de skins (sucesso, rollback e DLQ).
   - `tetris/db/cache_hits`: Taxa de acerto e uso de cache materializado no Firestore.
   - `tetris/anticheat/detections`: Quantidade de detecções de robôs vs humanos efetuadas pela IA.
   - `tetris/game/scores_submitted`: Volume de submissões de pontuação ao ranking.
3. **Rastreamento Distribuído (Cloud Trace):** Ativação e propagação automática de cabeçalhos de contexto de trace (`X-Cloud-Trace-Context`) entre o navegador, o balanceador de carga do Cloud Run e os orquestradores de GCP Workflows, gerando gráficos de Gantt detalhados na console do Cloud Trace para aferição de latências e caminhos de rede.
4. **Logs Nativos de Workflows:** Configuração de nível `TRACE_ALL_CALLS` nos orquestradores serverless (`buy_skin_workflow.yaml` e `submit_score_workflow.yaml`) para visibilidade total de etapas e compensações SAGA no Log Explorer.
5. **Agregação de Erros de Frontend:** Implementação de um monitor global de erros em JS (`window.addEventListener('error')`) que reporta automaticamente exceções ocorridas no navegador do jogador para o endpoint `/api/logs` do backend, centralizando os erros de frontend no GCP Error Reporting.
6. **Resiliência e Fallback Local:** O código foi projetado de forma defensiva para auto-detectar o ambiente. Se as bibliotecas do GCP não puderem se conectar ao barramento na nuvem (como no desenvolvimento local), o sistema chaveia automaticamente para impressão local formatada, garantindo testes locais perfeitamente offline.

### Fase 6: Automação DevSecOps e Pipeline Integrada (Checkpoint 05 - Atual)
A arquitetura atingiu maturidade de nível corporativo ao introduzir uma esteira automatizada de Integração, Qualidade, Segurança e Entrega Contínuas (CI/CD) via GitHub Actions, garantindo que nenhum código seja implantado sem passar por rigorosos portões de qualidade (Quality Gates):
1. **Varredura Estática de Segredos (Gitleaks):** Análise automatizada de todo o histórico de commits para detecção preventiva de chaves de API, senhas ou tokens expostos.
2. **Qualidade e Estilo de Código (Ruff & ESLint):** Linting automatizado de Python com Ruff (ultrarrápido) e de JavaScript (Flat Config `eslint.config.mjs`) para manter os padrões e a legibilidade do código.
3. **Análise de Segurança do Código (Bandit SAST):** Análise estática focada em vulnerabilidades de segurança específicas do ecossistema Python (FastAPI).
4. **Análise de Segurança de Dependências e Infraestrutura (Trivy SCA):** Varredura de segurança de pacotes (filesystem) e da imagem Docker gerada para identificação de CVEs (vulnerabilidades e exposições comuns) de níveis crítico/alto, garantindo a imunidade do ambiente de execução.
5. **Linting de Infraestrutura como Código (Hadolint):** Validação estática das instruções do `Dockerfile` visando otimização de camadas, redução de tamanho e eliminação de privilégios elevados.
6. **Testes Unitários Automatizados (CI):** Execução automática de testes unitários para garantir a estabilidade do backend a cada alteração.
7. **Autenticação sem Segredos (Workload Identity Federation):** Conexão direta e segura com o GCP eliminando chaves estáticas JSON no repositório.
8. **Implantação Contínua Automatizada (CD):** Publicação automatizada da imagem segura no Artifact Registry, deploy automático para o Cloud Run e deploy imediato dos workflows de orquestração do GCP Workflows.
9. **Varredura Dinâmica Ativa Sob Demanda (DAST - OWASP ZAP):** Pipeline isolada (`dast.yml`) executável de forma manual e segura que realiza simulações de ataques de injeção em um ambiente efêmero local, gerando relatórios dinâmicos completos.

---

## 🛠️ Arquitetura do Projeto

```text
├── backend/
│   ├── main.py                # Servidor FastAPI com APIs atômicas, CQRS, Maestro Simulador e Webhooks
│   ├── requirements.txt       # Dependências de bibliotecas Python
│   └── test_main.py           # Suíte de testes automatizados do backend
├── static/                    # Pasta com os ativos de frontend servidos pelo FastAPI
│   ├── css/
│   │   └── style.css          # Estilos modernos neon, grade e animações
│   ├── js/
│   │   ├── api.js             # Funções de chamadas HTTP (Wallet, Inventory, Anti-Cheat, Orquestrador)
│   │   └── game.js            # Lógica do jogo, telemetria e sintetizador matemático Web Audio
│   └── index.html             # Esqueleto da página e modais (Loja, Placar, Terminal Maestro)
├── buy_skin_workflow.yaml     # Definição do fluxo orquestrado da loja (Saga, Retries, Rollback)
├── submit_score_workflow.yaml # Definição da Árvore de Decisão do Anti-Cheat e gravação
├── Dockerfile                 # Instruções de montagem da imagem Docker (Cloud Run)
├── .dockerignore              # Exclusão de arquivos desnecessários na imagem Docker
├── .gitignore                 # Exclusão de arquivos de versionamento e venv
└── README.md                  # Esta documentação completa do projeto
```

---

## 🛡️ DevSecOps & Pipeline de CI/CD (GitHub Actions)

O projeto adota uma abordagem de **DevSecOps robusta**, automatizada e integrada através do **GitHub Actions** (configurado em `.github/workflows/pipeline.yml`). O pipeline garante que toda alteração de código passe por um rigoroso processo de validação de qualidade, testes automatizados e varreduras de segurança estática e de dependências antes de ser promovida para produção no **Google Cloud**.

Abaixo está o detalhamento completo de cada etapa, sua justificativa técnica e as ferramentas empregadas:

### 📊 Estrutura Geral do Pipeline (Confiança Progressiva Encadeada)
O fluxo de trabalho (workflow) adota uma arquitetura em **cascata linear de portões estritos**, desenhando uma esteira de confiança progressiva e extremamente organizada. Ele é composto por **cinco jobs encadeados**, onde cada etapa funciona como um portão de segurança que só libera a execução da seguinte se estiver perfeitamente homologada:

```text
┌───────────┐       ┌───────────┐       ┌────────────┐       ┌────────────────────┐       ┌──────────────────────┐
│  1. LINT  │ ───►  │  2. SAST  │ ───►  │  3. TEST   │ ───►  │ 4. BUILD & SCAN    │ ───►  │ 5. DEPLOY (CD)       │
│  (Ruff,   │       │ (Gitleaks,│       │ (Unit Tests│       │ (Docker Build,     │       │ (Cloud Run Deploy,   │
│  ESLint,  │       │  Bandit)  │       │    - CI)   │       │  Trivy Image Scan, │       │  Cloud Workflows)    │
│ Hadolint) │       │           │       │            │       │  Push to GAR)      │       │                      │
└───────────┘       └───────────┘       └────────────┘       └────────────────────┘       └──────────────────────┘
```

Esta arquitetura linear traz grandes benefícios de governança de software:
1. **Confiança Incremental:** O código só é escaneado em segurança se estiver bem formatado; só é testado logicamente se estiver livre de falhas de segurança conhecidas; só é buildado e implantado se passar em todos os testes funcionais.
2. **Separação de Artefato e Orquestração (Melhor Prática de CD):** O job **`4. Secure Artifact Build (SCA)`** é focado puramente em empacotar, escanear as camadas do container (Trivy Image Scan) e "promover" o artefato seguro para o registro oficial do GCP (**Google Artifact Registry - GAR**). O job **`5. Continuous Deployment (CD)`** é totalmente desacoplado e assume apenas o papel de orquestração do ambiente, puxando a imagem já aprovada do GAR para atualizar o **Cloud Run** e aplicando em seguida os orquestradores SAGA do **Google Cloud Workflows**.
3. **Eficiência Financeira e de Logs (Fail-Fast):** Se houver um erro de lint (5s), a esteira é abortada imediatamente. Não há desperdício de tempo e recursos executando testes unitários, scans complexos ou gerando builds de container sobre códigos com erros de sintaxe ou vazamento de credenciais.
4. **Filtro Inteligente de Gatilhos (paths-ignore):** Para otimizar o tempo e os custos de execução de runners, o pipeline principal utiliza filtros inteligentes que ignoram alterações puramente de documentação (como arquivos `.md`) ou modificações nas receitas de infraestrutura do próprio GitHub Actions (pasta `.github/workflows/**`). O build e o deploy só acontecem quando há modificações de código lógico na aplicação (backend ou frontend).

---

### 🔍 Detalhamento das Ferramentas e Portões de Segurança (Quality Gates)

#### 1. Gitleaks (Prevenção de Vazamento de Segredos)
* **Objetivo:** Analisar de forma estática todo o histórico de commits do repositório procurando por segredos, credenciais expostas, chaves de API, senhas ou certificados privados em texto claro.
* **Por que é crucial?** Impede o comprometimento da infraestrutura em nuvem, garantindo que credenciais sensíveis (como chaves de contas de serviço) nunca entrem na árvore do Git.

#### 2. Ruff (Linting e Estilo de Código Python)
* **Objetivo:** Executar a validação sintática e de boas práticas de codificação no código Python do backend de forma extremamente rápida.
* **Por que é crucial?** Mantém a consistência estilística (PEP 8) e identifica bugs em potencial (variáveis não utilizadas, importações incorretas) de forma ágil. No pipeline, ignoramos erros de manipulação genérica de exceções (`BLE001`) específicos para o fluxo local de fallback.

#### 3. ESLint (Qualidade e Conformidade do JavaScript)
* **Objetivo:** Linting das regras de código JavaScript do frontend (`static/js/`), utilizando uma estrutura de arquivo moderna de **Flat Config** (`eslint.config.mjs`).
* **Por que é crucial?** Valida a ausência de variáveis e funções não declaradas (`no-undef`) e mantém o frontend livre de bugs comuns de escopo ou sintaxe Javascript. O arquivo de configuração mapeia explicitamente as funções globais compartilhadas entre `api.js` e `game.js`.

#### 4. Hadolint (Linter de Dockerfile)
* **Objetivo:** Analisar estaticamente o arquivo `Dockerfile` em busca de desvios das melhores práticas recomendadas pela comunidade e pela Docker.
* **Por que é crucial?** Garante imagens menores (evitando pacotes supérfluos), builds mais rápidos (aproveitamento inteligente do cache de camadas) e maior segurança (desencorajando a execução de containers como usuário root sem necessidade).

#### 5. Bandit (Análise Estática de Segurança / SAST em Python)
* **Objetivo:** Executar análises de segurança estática no código Python, sinalizando possíveis brechas comuns de segurança, como injeção de comandos, uso de geradores de números pseudo-aleatórios fracos para fins criptográficos, etc.
* **Por que é crucial?** Ajuda a identificar vulnerabilidades antes que o código entre em execução (análise do tipo "White-Box"). O comando é configurado para sinalizar falhas de nível médio ou alto (`-ll`).

#### 6. Trivy FS (Análise de Vulnerabilidade de Dependências / SCA)
* **Objetivo:** Analisar as dependências do repositório (declaradas em `backend/requirements.txt`) à procura de vulnerabilidades conhecidas (CVEs).
* **Por que é crucial?** Evita o uso de bibliotecas de terceiros com falhas de segurança conhecidas e públicas. O pipeline é configurado para falhar imediatamente (`exit-code 1`) se encontrar vulnerabilidades com severidade `HIGH` ou `CRITICAL`.
* **Mecanismo de Exceção (`.trivyignore`):** Para evitar falsos positivos ou falhas causadas por pacotes utilitários de sistema upstream empacotados internamente pelo Python (`pip` e `setuptools`), criamos o arquivo `.trivyignore` para documentar e ignorar com segurança essas exceções que não afetam a segurança da nossa aplicação.

---

### 🧪 Testes Unitários Automatizados (CI)
Superado o portão de segurança e qualidade, o pipeline avança para a fase funcional:
* **Testes Unitários:** Executa a suíte de testes do backend (`backend/test_main.py`) usando o módulo nativo do Python `unittest`.
* **Garantia de Regressão:** Garante que novas funcionalidades ou alterações no backend (APIs de transação SAGA, anti-cheat, endpoints de score) não quebraram o comportamento funcional esperado pela aplicação.

---

### 🚀 Implantação Contínua Segura (CD)
O job de Deploy é acionado apenas quando há uma inserção (push) direta na branch principal (`main`), sob as seguintes condições de segurança de ponta:

1. **Autenticação Baseada em Identidade (Workload Identity Federation - WIF):** 
   Não armazenamos nenhuma chave JSON estática ou de longa duração no GitHub para nos conectar ao GCP. O pipeline utiliza o WIF para trocar de forma dinâmica e efêmera o token JWT do GitHub Actions por credenciais temporárias do Google Cloud Platform, reduzindo drasticamente o risco de vazamento de credenciais.
   
2. **Build de Imagem e Varredura de Imagem (Trivy Image Scan):**
   * A imagem Docker é gerada localmente no runner.
   * Antes de enviá-la para o GCP, o **Trivy realiza uma segunda análise profunda (SCA)**, agora diretamente nas camadas da imagem Docker final compilada (incluindo o sistema operacional de base da imagem).
   * Se alguma vulnerabilidade crítica/alta for detectada na imagem compilada, o pipeline é abortado e a imagem **não** é enviada ao repositório, mitigando o risco de "Contâineres Envenenados".
   
3. **Artifact Registry e Cloud Run:**
   * Aprovada na análise, a imagem é enviada com tag contendo o SHA do commit para o **Google Artifact Registry (GAR)**.
   * O deploy automático é efetuado no **Google Cloud Run** apontando de forma segura para a nova tag do container.
   
4. **Deploy Automático dos Orquestradores de Workflows:**
   * O pipeline executa de forma automática o deploy dos fluxos do Google Cloud Workflows:
     * `buy_skin_workflow.yaml` (Orquestração SAGA da Loja)
     * `submit_score_workflow.yaml` (Árvore de Decisão do Anti-Cheat)
   * Garante a sincronia imediata entre o código da aplicação FastAPI e as definições dos fluxos orquestrados no GCP.

---

### 🛡️ Testes de Invasão Ativos e Dinâmicos (DAST com OWASP ZAP)
Como as melhores práticas de mercado desaconselham rodar testes dinâmicos pesados e invasivos de DAST em cada pequeno push diário (para economizar recursos e evitar poluição de dados no banco com payloads de teste), o projeto introduz uma **pipeline de DAST separada e sob demanda** configurada em `.github/workflows/dast.yml`.

* **Como Funciona:**
  1. O pipeline é ativado manualmente pelo painel **Actions** do GitHub (**Workflow Dispatch**).
  2. Ele clona o repositório e compila a imagem Docker do jogo localmente no Runner temporário do GitHub.
  3. Inicializa o container da aplicação em background.
  4. Extrai dinamicamente o IP interno do container na rede interna do Docker para garantir conexões de rede 100% resilientes e isoladas.
  5. Sobe o container oficial do **OWASP ZAP** e dispara um **Baseline Scan** contra o endereço IP interno do app, simulando ataques de injeção e testando a segurança da porta `8080` (como cabeçalhos ausentes ou cookies inseguros).
  6. Gera e anexa um relatório completo de vulnerabilidades dinâmicas em formato HTML diretamente no painel do GitHub Actions.
  7. Finaliza e destrói o container de testes, sem nunca expor ou poluir a infraestrutura de produção no GCP.

---

## 🖥️ Como Executar Localmente (Ambiente Virtual)

Siga os passos abaixo para preparar seu ambiente Python, instalar as dependências necessárias e inicializar o jogo em seu navegador.

### Passo 1: Clonar o Repositório
Primeiro, clone o repositório para a sua máquina local e acesse a pasta do projeto:

```bash
git clone https://github.com/Tiago-TSG/tetris-app-checkpoint-05.git
cd tetris-app-checkpoint-05
```

### Passo 2: Criar o Ambiente Virtual (`venv`)
No diretório raiz do projeto, execute o comando correspondente ao seu sistema operacional para criar o ambiente virtual:

**No Linux / macOS:**
```bash
python3 -m venv venv
```

**No Windows (CMD ou PowerShell):**
```bash
python -m venv venv
```

### Passo 3: Ativar o Ambiente Virtual
Ative o ambiente virtual para que os pacotes sejam instalados isoladamente:

**No Linux / macOS:**
```bash
source venv/bin/activate
```

**No Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**No Windows (CMD):**
```bash
.\venv\Scripts\activate.bat
```

### Passo 4: Instalar as Dependências
Com o ambiente virtual ativado (indicado pelo prefixo `(venv)` no seu terminal), instale as dependências listadas:

```bash
pip install -r backend/requirements.txt
```

### Passo 5: Executar o Servidor FastAPI
Execute o servidor de desenvolvimento utilizando o `uvicorn`:

```bash
uvicorn backend.main:app --reload --port 8080
```
> **Nota de Fallback:** O código é resiliente. Se você rodar localmente sem as credenciais do Google Cloud ativadas, o sistema entrará no "Modo de Segurança" (Fallback), voltando a salvar e ler os placares em um arquivo JSON local, permitindo testes offline perfeitos.

### Passo 6: Jogar!
Abra seu navegador e acesse:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🐳 Como Executar Localmente via Docker

Este projeto possui suporte a contêineres Docker, o que permite rodar toda a aplicação sem precisar instalar o Python ou pacotes de dependências na sua máquina local.

### Passo 1: Clonar o Repositório
Primeiro, clone o repositório para a sua máquina local e acesse a pasta do projeto:

```bash
git clone https://github.com/Tiago-TSG/tetris-app-checkpoint-05.git
cd tetris-app-checkpoint-05
```

### Passo 2: Construir a Imagem Docker
No diretório raiz (onde está o arquivo `Dockerfile`), construa a imagem executando:

```bash
docker build -t tetris-app-checkpoint-05 .
```

### Passo 3: Executar o Contêiner Localmente
Inicialize o contêiner mapeando a porta interna `8080` para a porta `8080` do seu computador local:

```bash
docker run -p 8080:8080 tetris-app-checkpoint-05
```

Acesse o jogo no navegador através do endereço local **`http://localhost:8080`**.

---

## ☁️ Como Fazer o Deploy no Google Cloud Run

O **Google Cloud Run** é um serviço totalmente gerenciado do GCP que executa contêineres de forma altamente escalável e cobra apenas pelo tempo de processamento utilizado.

### Pré-requisitos
1. Ter uma conta ativa no **Google Cloud Platform (GCP)**.
2. Instalar a ferramenta de linha de comando [Google Cloud CLI (gcloud)](https://cloud.google.com/sdk/gcloud).
3. Ter um projeto criado no GCP e habilitar o faturamento (Billing) e as APIs do Cloud Build e Cloud Run.
4. Clonar este repositório Git em sua máquina local e acessar o diretório do projeto:
   ```bash
   git clone https://github.com/Tiago-TSG/tetris-app-checkpoint-05.git
   cd tetris-app-checkpoint-05
   ```

### 1. Criar os Tópicos do Pub/Sub
Para a arquitetura de Mensageria e Telemetria funcionar, crie os tópicos necessários:
```bash
gcloud pubsub topics create scores-topic
gcloud pubsub topics create telemetry-topic
```

---

### Opção 1: Deploy Direto via gcloud (Recomendado)
A forma mais rápida e simples de fazer o deploy no Cloud Run é usando o build automático do GCP a partir do seu código-fonte local. O Google Cloud enviará o código, construirá o container na nuvem e fará o deploy em uma única etapa.

1.  Abra seu terminal na raiz do projeto e faça login no Google Cloud:
    ```bash
    gcloud auth login
    ```

2.  Defina o seu projeto padrão do GCP (substitua `NOME-DO-SEU-PROJETO` pelo ID correto do console):
    ```bash
    gcloud config set project NOME-DO-SEU-PROJETO
    ```

3.  Execute o comando de deploy. Ele criará a imagem e a colocará em execução:
    ```bash
    gcloud run deploy tetris-app-checkpoint-05 \
      --source . \
      --region us-central1 \
      --allow-unauthenticated
    ```
    
    > **📝 Nota:** Por padrão, o gcloud criará automaticamente um repositório no **Artifact Registry** com o nome `cloud-run-source-deploy` para armazenar a imagem Docker construída. Você pode visualizá-lo no console do GCP em **Artifact Registry > Repositories**.
    
    *(Você pode alterar a região se desejar, como `southamerica-east1` para o Brasil).*

4.  Ao final do processo, a CLI do gcloud exibirá a **URL pública do jogo** (ex: `https://tetris-app-checkpoint-05-xxxxx-us-central1.run.app`) no serviço "Cloud Run".

### 2. Configurar as Assinaturas de Push (Webhooks)
Para fechar o ciclo do Pub/Sub, vincule os tópicos criados aos Webhooks da sua aplicação, substituindo a URL abaixo pela URL gerada no passo anterior:

**Assinatura de Scores e Cache:**
```bash
gcloud pubsub subscriptions create scores-topic-sub \
  --topic=scores-topic \
  --push-endpoint=https://SUA_URL_DO_CLOUD_RUN.a.run.app/api/internal/scores-worker \
  --ack-deadline=10
```

**Assinatura de Telemetria e Badges:**
```bash
gcloud pubsub subscriptions create telemetry-topic-sub \
  --topic=telemetry-topic \
  --push-endpoint=https://SUA_URL_DO_CLOUD_RUN.a.run.app/api/internal/telemetry-worker \
  --ack-deadline=10
```

---

### Opção 2: Deploy em Duas Etapas (Via Artifact Registry)
Se você preferir construir a imagem manualmente e enviá-la para um repositório de contêineres próprio do GCP antes de realizar o deploy:

1.  **Criar um repositório no Artifact Registry (caso não possua):**
    ```bash
    gcloud artifacts repositories create neon-arcade-repo \
      --repository-format=docker \
      --location=us-central1 \
      --description="Repositorio para o jogo Tetris"
    ```

2.  **Construir a imagem e enviá-la para o GCP via Cloud Build:**
    Substitua `PROJECT_ID` pelo ID real do seu projeto.
    ```bash
    gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/neon-arcade-repo/tetris-app-checkpoint-05:latest .
    ```

3.  **Realizar o deploy do container armazenado no registro para o Cloud Run:**
    ```bash
    gcloud run deploy retro-neon-tetris \
      --image us-central1-docker.pkg.dev/PROJECT_ID/neon-arcade-repo/tetris-app-checkpoint-05:latest \
      --region us-central1 \
      --allow-unauthenticated
    ```

*(Lembre-se de configurar as Assinaturas de Push descritas acima após este tipo de deploy também).*

---

## 🎮 Controles do Jogo
*   **Seta para Esquerda (`←`) ou `A`:** Move a peça para a esquerda.
*   **Seta para Direita (`→`) ou `D`:** Move a peça para a direita.
*   **Seta para Baixo (`↓`) ou `S`:** Acelera a descida normal da peça (Descida Rápida).
*   **Seta para Cima (`↑`) ou `W`:** Rotaciona a peça em sentido horário.
*   **Barra de Espaço:** Queda instantânea (Dropa o bloco ao fundo e soma pontos bônus).
*   **Letra `P`:** Pausa e despausa o jogo a qualquer momento.

---

## 🔒 Persistência de Dados (Scores e Conquistas)
Nesta nova arquitetura (Fases 1, 2 e 3), a persistência de dados efêmera baseada em arquivo local foi completamente substituída em ambiente de produção pelo banco de dados **Google Cloud Firestore**. 

- **Scores (Leaderboard):** As pontuações são armazenadas permanentemente na coleção `scores` e servidas via Cache Materializado, garantindo alta disponibilidade e durabilidade sem impacto na escalabilidade do Cloud Run.
- **Conquistas (Badges):** A telemetria de jogo em tempo real alimenta a coleção `achievements`, que consolida métricas globais e troféus desbloqueados de forma individual para cada jogador de forma totalmente assíncrona.
