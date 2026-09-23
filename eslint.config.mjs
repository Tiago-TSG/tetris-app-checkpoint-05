export default [
    {
        files: ["static/js/**/*.js"],
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: "module",
            globals: {
                // --- Navegador Padrão ---
                window: "readonly",
                document: "readonly",
                console: "readonly",
                fetch: "readonly",
                setTimeout: "readonly",
                setInterval: "readonly",
                clearTimeout: "readonly",
                clearInterval: "readonly",
                requestAnimationFrame: "readonly",
                cancelAnimationFrame: "readonly",
                performance: "readonly",
                sessionStorage: "readonly",
                localStorage: "readonly",
                location: "readonly",
                history: "readonly",
                navigator: "readonly",
                Image: "readonly",
                Audio: "readonly",
                AudioContext: "readonly",
                alert: "readonly",
                CustomEvent: "readonly",
                HTMLElement: "readonly",
                WebSocket: "readonly",
                Event: "readonly",

                // --- Funções Globais da API (Definidas em api.js e usadas em game.js) ---
                fetchScores: "readonly",
                renderScores: "readonly",
                updatePubSubStatus: "readonly",
                getSessionId: "readonly",
                sendTelemetry: "readonly",
                fetchAndShowAchievements: "readonly",
                showAchievementToast: "readonly",
                submitScore: "readonly",
                renderOrchestratorLogs: "readonly",
                fetchStoreCatalog: "readonly",
                buySkinOrchestrated: "readonly",
                equipSkin: "readonly",
                isHighScore: "readonly"
            }
        },
        rules: {
            "no-unused-vars": "warn",
            "no-undef": "error"
        }
    }
];
