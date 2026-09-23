export default [
    {
        files: ["static/js/**/*.js"],
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: "module",
            globals: {
                window: "readonly",
                document: "readonly",
                console: "readonly",
                fetch: "readonly",
                setTimeout: "readonly",
                setInterval: "readonly",
                clearTimeout: "readonly",
                clearInterval: "readonly",
                AudioContext: "readonly",
                alert: "readonly",
                localStorage: "readonly",
                location: "readonly",
                history: "readonly",
                navigator: "readonly",
                CustomEvent: "readonly",
                HTMLElement: "readonly",
                WebSocket: "readonly",
                Event: "readonly"
            }
        },
        rules: {
            "no-unused-vars": "warn",
            "no-undef": "error"
        }
    }
];
