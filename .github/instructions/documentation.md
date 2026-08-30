---
name: documentation-standards
description: >
  PADRÕES DE DOCUMENTAÇÃO — Guia completo de como documentar projetos,
  microserviços, APIs, scripts e infraestrutura. Define estrutura, templates,
  nomenclatura e workflow para toda a organização.
applyTo: "**/*"
---

# Padrões de Documentação

## Índice

1. [Onde Salvar](#1-onde-salvar)
2. [Estrutura de Diretórios](#2-estrutura-de-diretórios)
3. [Nomenclatura de Arquivos](#3-nomenclatura-de-arquivos)
4. [Template por Tipo de Projeto](#4-template-por-tipo-de-projeto)
5. [Documentação de API](#5-documentação-de-api)
6. [Documentação de Scripts e Infra](#6-documentação-de-scripts-e-infra)
7. [CHANGELOG e Versionamento](#7-changelog-e-versionamento)
8. [Workflow de Documentação](#8-workflow-de-documentação)
9. [Checklist de Qualidade](#9-checklist-de-qualidade)

---

## 1. Onde Salvar

### Regra Geral

Cada projeto documenta **dentro de si mesmo** (pasta `docs/` na raiz do projeto)
**E** também possui uma pasta com seu nome em `/home/user/server/documentation/`
para documentação complementar, explicações de arquitetura e visuais.

```
/home/user/server/
├── .github/instructions/         ← Instruções globais (infra, projetos, docs)
├── documentation/                ← Documentação geral + 1 pasta por projeto
│   ├── README.md                 ← Índice completo
│   ├── documentation-standards.html
│   ├── guides/                   ← Tutoriais e guias
│   ├── diagrams/                 ← Diagramas de arquitetura geral
│   ├── manuals/                  ← Manuais de operação
│   ├── opencode-orchestrator/    ← Pasta por projeto
│   │   ├── README.md
│   │   └── analyser.html
│   ├── payment-manager/
│   │   └── README.md
│   └── <cada-projeto>/           ← Uma pasta para cada projeto
│       └── README.md
└── projetos/
    └── <nome-do-projeto>/
        ├── README.md            ← ESSENCIAL: visão geral do projeto
        ├── docs/                ← Documentação técnica específica
        │   ├── index.md         ← Índice da documentação
        │   ├── architecture.md  ← Arquitetura
        │   ├── api.md           ← API endpoints (se aplicável)
        │   ├── setup.md         ← Setup e instalação
        │   ├── deploy.md        ← Deploy e produção
        │   ├── CHANGELOG.md     ← Histórico de versões
        │   └── assets/          ← Imagens, diagramas, etc.
        └── ...
```

### Onde cada tipo de documentação deve ficar

| Tipo de Documento | Local Padrão | Formato |
|---|---|---|
| README do projeto | `projetos/<projeto>/README.md` | Markdown |
| Documentação técnica do projeto | `projetos/<projeto>/docs/` | Markdown |
| Documentação complementar/visual | `documentation/<projeto>/` | Markdown ou HTML |
| API Reference | `projetos/<projeto>/docs/api.md` | Markdown |
| Arquitetura | `projetos/<projeto>/docs/architecture.md` | Markdown |
| Setup/Instalação | `projetos/<projeto>/docs/setup.md` | Markdown |
| Deploy/Produção | `projetos/<projeto>/docs/deploy.md` | Markdown |
| CHANGELOG | `projetos/<projeto>/docs/CHANGELOG.md` | Markdown |
| Guias visuais/diagramas | `projetos/<projeto>/docs/assets/` | PNG, SVG, Mermaid |
| Instruções globais | `.github/instructions/` | Markdown (YAML frontmatter) |
| Documentação geral compartilhada | `documentation/` | Markdown ou HTML |
| Diagramas de arquitetura geral | `documentation/diagrams/` | Mermaid, PNG, draw.io |
| Manuais de operação | `documentation/manuals/` | Markdown ou HTML |
| Tutoriais e guias | `documentation/guides/` | Markdown ou HTML |

---

## 2. Estrutura de Diretórios

### Para projetos novos

```
projetos/<nome-do-projeto>/
├── README.md
├── docs/
│   ├── index.md
│   ├── architecture.md
│   ├── setup.md
│   ├── api.md              (se tiver API)
│   ├── deploy.md           (se tiver deploy)
│   ├── CHANGELOG.md
│   └── assets/
│       ├── diagram.png
│       └── ...
├── src/                    (ou backend/, frontend/, etc.)
├── tests/
├── package.json            (ou pyproject.toml, etc.)
├── ecosystem.config.js     (PM2, se aplicável)
└── ...
```

### Para projetos existentes (mínimo aceitável)

```
projetos/<nome-do-projeto>/
├── README.md               ← OBRIGATÓRIO
└── docs/
    └── CHANGELOG.md        ← OBRIGATÓRIO
```

---

## 3. Nomenclatura de Arquivos

### Regras

- **Arquivos**: `kebab-case` (ex: `architecture-overview.md`)
- **Pastas**: `snake_case` ou `kebab-case` (ex: `docs/assets/`)
- **Imagens/diagramas**: `kebab-case` (ex: `system-architecture.png`)
- **CHANGELOG**: Sempre `CHANGELOG.md` (maiúsculo)
- **README**: Sempre `README.md` (maiúsculo)

### Prefixos recomendados

| Prefixo | Uso | Exemplo |
|---|---|---|
| `guide-` | Tutoriais e guias | `guide-deployment.md` |
| `ref-` | Material de referência | `ref-endpoints.md` |
| `howto-` | Passo-a-passo | `howto-add-new-service.md` |
| `troubleshoot-` | Solução de problemas | `troubleshoot-database.md` |
| `report-` | Relatórios automáticos | `report-2026-07-24-health.md` |

---

## 4. Template por Tipo de Projeto

### 4.1 Template para README.md (TODO projeto)

```markdown
# <Nome do Projeto>

> <Descrição de uma linha sobre o que o projeto faz.>

## Stack

| Categoria | Tecnologia |
|---|---|
| Backend | Node.js / Express / TypeScript |
| Frontend | React / Vite / TailwindCSS |
| Banco | PostgreSQL / SQLite |
| Cache | Redis |
| Container | Docker |

## Rápido Início

```bash
git clone ...
cd projetos/<projeto>
cp .env.example .env
npm install
npm run dev
```

Acesse: `http://localhost:<porta>`

## Scripts

| Comando | Descrição |
|---|---|
| `npm run dev` | Desenvolvimento com hot-reload |
| `npm run build` | Build de produção |
| `npm start` | Iniciar produção |
| `npm test` | Executar testes |
| `./start.sh` | Iniciar via PM2 |

## PM2

- **Nome do processo:** `<nome-pm2>`
- **Gerenciar:** `pm2 start <nome-pm2>`, `pm2 stop <nome-pm2>`
- **Logs:** `pm2 logs <nome-pm2>`

## Documentação

Documentação completa em [`docs/index.md`](docs/index.md).

## Ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `PORT` | Porta do servidor | `3000` |
| `NODE_ENV` | Ambiente | `development` |
```

### 4.2 Python FastAPI (AI/ML)

```markdown
# <Nome do Projeto>

> <Descrição: gateway LLM, geração de vídeo, áudio, etc.>

## Stack

- **Runtime:** Python 3.11+
- **Framework:** FastAPI + Uvicorn
- **Gerenciamento:** PM2
- **GPU:** CUDA / PyTorch

## Setup

```bash
cd projetos/<projeto>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executar

### Desenvolvimento
```bash
python server.py
# ou
uvicorn api.main:app --reload --port 8081
```

### Produção (PM2)
```bash
./start.sh
pm2 start <nome-pm2>
```

## API

Documentação interativa: `http://localhost:<porta>/docs`

Endpoints principais:

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/generate` | Gerar conteúdo |
| GET | `/api/health` | Health check |
| GET | `/api/models` | Listar modelos disponíveis |

## PM2

- **Nome do processo:** `<nome-pm2>`
- **Script PM2:** `ecosystem.config.js`
```

### 4.3 Node.js/Express (API)

```markdown
# <Nome do Projeto>

> <Descrição do microserviço.>

## Stack

- **Runtime:** Node.js 20+
- **Framework:** Express + TypeScript
- **Banco:** MySQL/PostgreSQL + Sequelize
- **Gerenciamento:** PM2

## Setup

```bash
cd projetos/<projeto>
cp .env.example .env
npm install
npm run build
```

## Scripts

| Comando | Descrição |
|---|---|
| `npm run dev` | Desenvolvimento com tsx watch |
| `npm run build` | Compilar TypeScript |
| `npm start` | Produção |
| `npm test` | Testes |

## Ambiente

| Variável | Descrição |
|---|---|
| `PORT` | Porta |
| `DATABASE_URL` | Conexão banco |
| `JWT_SECRET` | Chave JWT |
```

### 4.4 Frontend React/Vite

```markdown
# <Nome do Projeto>

> <Descrição do frontend.>

## Stack

- **Framework:** React 19 + TypeScript
- **Build:** Vite 6
- **Estilos:** TailwindCSS
- **Roteamento:** React Router

## Setup

```bash
cd projetos/<projeto>
npm install
npm run dev
```

## Scripts

| Comando | Descrição |
|---|---|
| `npm run dev` | Dev server (`:5173`) |
| `npm run build` | Build produção |
| `npm run preview` | Preview do build |

## Deploy

Build produzido em `dist/`. Servir via Nginx.
```

### 4.5 Script/Bash

```markdown
# <Nome do Script>

> <Descrição do que o script faz.>

## Uso

```bash
./<script>.sh [opções]
```

## Opções

| Flag | Descrição |
|---|---|
| `-h` | Ajuda |
| `--full` | Execução completa |

## Comportamento

<Explicação do que o script faz, em que contexto executar, etc.>

## PM2 (se aplicável)

Gerenciado como processo `<nome>` no PM2.
```

### 4.6 Docker/Infraestrutura

```markdown
# <Nome do Serviço Docker>

> <Descrição do container/serviço.>

## Iniciar

```bash
docker compose -f ngnix/docker-compose.yml up -d
```

## Parar

```bash
docker compose -f ngnix/docker-compose.yml down
```

## Logs

```bash
docker compose -f ngnix/docker-compose.yml logs --tail 50 -f
```

## Portas

| Serviço | Porta Host | Porta Container |
|---|---|---|
| nginx | 80/443 | 80/443 |
```

---

## 5. Documentação de API

Sempre que um projeto expõe uma API HTTP (REST), incluir `docs/api.md`:

### Template `docs/api.md`

```markdown
# API Reference — <Nome do Projeto>

**Base URL:** `http://localhost:<porta>/api`

## Autenticação

| Método | Rota | Descrição |
|---|---|---|
| POST | `/auth/login` | Login, retorna JWT |

## Endpoints

### `<Método> <Rota>`

**Descrição:** <do que o endpoint faz>

**Headers:**

| Header | Valor |
|---|---|
| `Authorization` | `Bearer <token>` |

**Request Body:**

```json
{
    "campo": "valor"
}
```

**Response `200`:**

```json
{
    "status": "ok",
    "data": {}
}
```

**Response `4xx/5xx`:**

```json
{
    "error": "mensagem de erro"
}
```
```

---

## 6. Documentação de Scripts e Infra

### `.github/instructions/` — Instruções Globais

Os arquivos em `.github/instructions/` seguem o formato:

```markdown
---
name: <identificador-único>
description: >
  <Descrição de duas a três linhas sobre o escopo deste documento.
  Deve ser específica o suficiente para o Copilot entender quando aplicar.>
applyTo: "**/*"
---

# Título

<Conteúdo da instrução>
```

**Arquivos existentes:**

| Arquivo | Escopo |
|---|---|
| `infrastructure.md` | Nginx, PM2, Docker Compose, Dockerfile, GPU, monitoramento |
| `projects.md` | Catálogo de microserviços ativos (portas, scripts, PM2) |
| `testing.md` | Padrões e comandos de teste |
| `documentation.md` | **(este arquivo)** Padrões de documentação |

### Scripts de infraestrutura na raiz

Scripts como `start-all-pm2.sh`, `git-commit-all.sh`, etc. devem ter cabeçalho:

```bash
#!/bin/bash
# ============================================================
# <nome> — <descrição de uma linha>
# ============================================================
# Uso: ./<script>.sh
# Dependências: <lista>
# ============================================================
```

---

## 7. CHANGELOG e Versionamento

### Template `docs/CHANGELOG.md`

```markdown
# CHANGELOG — <Nome do Projeto>

## [1.0.0] — 2026-07-24

### Adicionado
- Funcionalidade X implementada

### Corrigido
- Bug Y resolvido

### Alterado
- Comportamento de Z modificado

### Removido
- Recurso W removido
```

### Convenção de versionamento

- **Major** (1.0.0): Mudanças que quebram compatibilidade
- **Minor** (0.1.0): Novas funcionalidades (backward-compatible)
- **Patch** (0.0.1): Correções de bugs

---

## 8. Workflow de Documentação

### Ao criar um novo projeto

1. Use o template correspondente ao tipo de projeto (seção 4)
2. Crie `README.md` obrigatoriamente
3. Crie `docs/` com `index.md`, `architecture.md`, `setup.md`
4. Se expõe API → crie `docs/api.md`
5. Adicione ao catálogo em `.github/instructions/projects.md`

### Ao modificar um projeto existente

- Se adicionou novo endpoint → atualize `docs/api.md`
- Se mudou setup/ambiente → atualize `docs/setup.md`
- Se mudou arquitetura → atualize `docs/architecture.md`
- Qualquer mudança significativa → atualize `docs/CHANGELOG.md`

### Ao documentar algo novo

1. Identifique o tipo de documentação necessária
2. Escolha o local correto (seção 1)
3. Use o template adequado (seção 4)
4. Salve com nomenclatura correta (seção 3)
5. Revise com o checklist (seção 9)

### Documentação automática (Analyser)

Para projetos com o **Analyser** ativo (ex: opencode-orchestrator), relatórios
automáticos são salvos em `Analyser/reports/` e seguem o formato:

```
Analyser/reports/<data>/report-<timestamp>-<tipo>.md
```

---

## 9. Checklist de Qualidade

### ✅ Checklist para README.md

- [ ] Nome do projeto e descrição clara
- [ ] Stack tecnológica listada
- [ ] Comandos de setup e execução
- [ ] Porta e URL de acesso
- [ ] Link para documentação detalhada
- [ ] PM2: nome do processo (se aplicável)
- [ ] Variáveis de ambiente principais

### ✅ Checklist para docs/

- [ ] `index.md` com índice de toda a documentação
- [ ] `architecture.md` com diagrama ou descrição
- [ ] `setup.md` com passo-a-passo do ambiente
- [ ] `deploy.md` com instruções de produção
- [ ] `api.md` (se aplicável) com todos os endpoints
- [ ] `CHANGELOG.md` com histórico de versões
- [ ] Imagens/diagramas em `assets/` quando necessário

### ✅ Checklist geral

- [ ] Markdown válido e bem formatado
- [ ] Links funcionam (relativos ou absolutos)
- [ ] Código nos blocos ``` tem linguagem especificada
- [ ] Tabelas são usadas para dados estruturados
- [ ] Sem informações sensíveis (senhas, tokens, API keys)
- [ ] Datas no formato ISO (YYYY-MM-DD)
- [ ] Português claro e consistente
