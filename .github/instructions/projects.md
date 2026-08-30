---
name: project-microservices
description: >
  CATÁLOGO DE MICROSSERVIÇOS — Lista dos microserviços ativos do workspace
  com descrição, stack, porta, scripts disponíveis e configuração PM2.
  Use quando: precisar consultar um microserviço, seus comandos, ou função.
applyTo: "**/*"
---

# Catálogo de Microserviços

## Visão Geral

O workspace contém **7 microserviços ativos** divididos em categorias. Cada um tem
scripts padronizados para desenvolvimento, build, teste e produção.

---

## 📦 AI/ML Microservices (Python FastAPI)

### `gen_text` — LLM Server Gateway
- **Função:** Gateway para modelos de linguagem (LLM). Proxy para llama.cpp, controle de contexto, streaming.
- **Stack:** Python FastAPI + Uvicorn
- **Porta:** `8081`
- **Acesso local:** `http://localhost:8081`
- **PM2:** `gen-text`
- **Scripts:**
  ```bash
  cd projetos/gen_text
  ./start.sh          # Produção
  python server.py    # Dev direto
  ```

### `gen_video` — Video Generation API
- **Função:** Geração de vídeos via HuggingFace Cloud (primary) + ComfyUI local (fallback).
- **Stack:** Python FastAPI + Uvicorn
- **Porta:** `8095`
- **Acesso local:** `http://localhost:8095`
- **PM2:** `gen-video`
- **Scripts:**
  ```bash
  cd projetos/gen_video
  ./start.sh           # Produção
  python api/main.py   # Dev direto
  ```

### `gen_audio` — Audio Generation API
- **Função:** Geração de áudio — Music/TTS/SFX. API para criação de conteúdo sonoro por IA.
- **Stack:** Python FastAPI + Uvicorn
- **Porta:** `8099`
- **Acesso local:** `http://localhost:8099`
- **PM2:** `gen-audio`
- **Scripts:**
  ```bash
  cd projetos/gen_audio
  ./start.sh           # Produção
  python api/main.py   # Dev direto
  ```

### `stable` — Stable Diffusion Web UI
- **Função:** Interface web para geração de imagens com Stable Diffusion (AUTOMATIC1111).
- **Stack:** Python + Gradio + PyTorch (GPU)
- **Porta:** `8080` (interna)
- **Acesso local:** `http://localhost:8080`
- **PM2:** `stable-diffusion`
- **Scripts:**
  ```bash
  cd projetos/stable
  ./start_native.sh    # Iniciar com GPU affinity
  ```

---

## 📦 API Microservices (Node.js)

### `payment-manager` — Stripe Payment Microservice
- **Função:** Microserviço de pagamentos Stripe para múltiplos aplicativos.
- **Stack:** Node.js/Express + Sequelize (PostgreSQL)
- **Porta:** `8035`
- **Acesso local:** `http://localhost:8035`
- **PM2:** `payment-manager`
- **Scripts:**
  ```bash
  cd projetos/payment-manager
  npm run dev          # Desenvolvimento
  npm start            # Produção
  npm run build        # Build TypeScript
  ```

### `whatsapp-api` — WhatsApp Automation
- **Função:** API de automação WhatsApp para notificações dos monitores.
- **Stack:** Node.js/Express + better-sqlite3
- **Porta:** `9110`
- **Acesso local:** `http://localhost:9110`
- **PM2:** `whatsapp-api`
- **Scripts:**
  ```bash
  cd projetos/whatsapp-api
  npm run dev          # Desenvolvimento
  npm run build        # Build TypeScript
  npm start            # Produção
  npm test             # Testes (jest)
  ```

---

## 📦 Aplicações Web (FastAPI + React)

### `3d_model` — Conversor 2D (Grayscale) → 3D Mesh
- **Função:** Converte imagens em escala de cinza em malhas 3D (OBJ/STL) via Shape-from-Shading clássico (Frankot-Chellappa / Poisson) — sem IA/ML. Autenticação por telefone com código enviado via WhatsApp (allowlist `ALLOWED_PHONES` auto-aprova; demais telefones dependem de aprovação do admin).
- **Stack:** Python FastAPI + Uvicorn (backend) + React 19/Vite/TypeScript/Tailwind (frontend)
- **Porta:** backend `8094`, frontend `8100`
- **Acesso local:** backend `http://localhost:8094`, frontend `http://localhost:8100`
- **PM2:** `3d-model` (backend), `3d-model-frontend` (frontend)
- **Scripts:**
  ```bash
  # Backend (porta 8094 — env PORT sobrepõe)
  cd projetos/3d_model/backend
  pip install -r requirements.txt
  ./start.sh

  # Frontend (build + servidor estático, porta 8100 — env PORT sobrepõe)
  cd projetos/3d_model/frontend
  npm install
  npm run build
  node server.cjs
  ```

---

## 📦 Go Microservices

<!-- snake-game removed from PM2 -->

---

## 📦 Infraestrutura/Deploy

### Docker

| Projeto | Função | Porta | Como iniciar |
|---------|--------|-------|-------------|
| `ngnix/` | Reverse proxy Nginx + Cloudflare SSL | `80`/`443` (host) | `docker compose -f ngnix/docker-compose.yml up -d` |

### PM2

Todos os microserviços são gerenciados via PM2 com `ecosystem.config.js` próprio:

| Microserviço | Nome PM2 | Iniciar |
|-------------|----------|---------|
| `gen_text` | `gen-text` | `pm2 start gen-text` |
| `gen_video` | `gen-video` | `pm2 start gen-video` |
| `gen_audio` | `gen-audio` | `pm2 start gen-audio` |
| `stable` | `stable-diffusion` | `pm2 start stable-diffusion` |
| `payment-manager` | `payment-manager` | `pm2 start payment-manager` |
| `whatsapp-api` | `whatsapp-api` | `pm2 start whatsapp-api` |
| `3d_model` (backend) | `3d-model` | `pm2 start 3d-model` |
| `3d_model` (frontend) | `3d-model-frontend` | `pm2 start 3d-model-frontend` |

> ⚠️ O projeto `3d_model` ainda **não possui** `ecosystem.config.js` — os nomes PM2 acima são os planejados (o nome do pacote do frontend já é `3d-model-frontend`).

> Comandos úteis: `pm2 list`, `pm2 logs <nome>`, `pm2 restart <nome>`, `pm2 stop <nome>`
> Para iniciar todos de uma vez: `./start-all-pm2.sh`

> Para detalhes completos de configuração de deploy (PM2, Docker Compose, Dockerfile, GPU VRAM Manager), consulte `.github/instructions/infrastructure.md`.

## Comandos Rápidos

### AI/ML (Python FastAPI)
```bash
# Desenvolvimento direto
python projetos/gen_text/server.py
python projetos/gen_video/api/main.py
python projetos/gen_audio/api/main.py

# Testes
pytest projetos/gen_text/tests/
pytest projetos/gen_video/tests/
```

### Node.js (Express)
```bash
# Desenvolvimento
cd projetos/payment-manager && npm run dev
cd projetos/whatsapp-api && npm run dev

# Build produção
cd projetos/payment-manager && npm run build
cd projetos/whatsapp-api && npm run build
```

### Aplicações Web (FastAPI + React)
```bash
# Backend 3d_model (porta 8094)
cd projetos/3d_model/backend && ./start.sh

# Frontend 3d_model (build + servidor estático, porta 8100)
cd projetos/3d_model/frontend && npm install && npm run build && node server.cjs
```

### Gerenciamento PM2
```bash
# Listar todos os serviços
pm2 list

# Logs de um serviço
pm2 logs <nome-servico>

# Reiniciar serviço
pm2 restart <nome-servico>

# Iniciar todos (via script raiz)
./start-all-pm2.sh
```

### Git
```bash
# Commitar todos os projetos (pergunta antes)
./git-commit-all.sh
```

---

## 📦 Test Gallery — `test-gallery`

### `test-gallery` — Test Gallery Server
- **Função:** Galeria de testes com login e dashboard dinâmico. Projetos em `pages/` são automaticamente detectados e exibidos em iframes.
- **Stack:** Node.js/Express + chokidar (auto-scan)
- **Porta:** `8082`
- **Acesso local:** `http://localhost:8082`
- **PM2:** `test-gallery`
- **Scripts:**
  ```bash
  cd projetos/test-gallery
  node server.js        # Desenvolvimento
  pm2 start ecosystem.config.js --update-env  # Produção
  ```
- **Acesso público:** `https://test.apps.tec.br`
- **Credenciais:** configuradas via `.env` (`ADMIN_USER`/`ADMIN_PASS`)

### Estrutura
```
projetos/test-gallery/
├── server.js              ← Servidor Express
├── ecosystem.config.js    ← PM2
├── index.html             ← Login (obrigatório)
├── dashboard.html         ← Galeria com iframes
├── style.css              ← Estilo
├── .env                   ← Credenciais (ADMIN_USER / ADMIN_PASS)
└── pages/                 ← Projetos de teste
    └── <projeto>/
        ├── index.html
        └── .manifest.json (opcional)
```

### URLs
| Tipo | URL |
|------|-----|
| Login | `https://test.apps.tec.br/` |
| Dashboard | `https://test.apps.tec.br/dashboard.html` |
| Projeto | `https://test.apps.tec.br/pages/<projeto>/` |
| API | `https://test.apps.tec.br/api/projects` |

### Endpoints da API
- `GET /api/projects` — Lista projetos em `pages/`
- `POST /api/auth/login` — Autenticação (`{ user, pass }`)
- `GET /api/auth/check` — Verifica se token é válido

### Como adicionar um teste
1. Criar pasta: `projetos/test-gallery/pages/<nome>/`
2. Adicionar `index.html`
3. (Opcional) `.manifest.json` com `{ "title", "description" }`
4. O servidor detecta automaticamente
