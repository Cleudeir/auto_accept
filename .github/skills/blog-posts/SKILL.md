---
name: blog-posts
user-invocable: true
description: 'Atualizar os posts do Blog & Insights do portfólio. Cada post HTML em server/data/posts/ é comparado com o código fonte real dos projetos (whatsapp-api, caixa_escolar, Insta_post, py_text_insert_image, eixo_x_projetos, beNext, advp-python) usando subagentes para verificar tópico por tópico. Corrige afirmações desatualizadas sobre DB schema, autenticação, endpoints, LLM, scraping, YAML profiles, ORM, zoom 3D, estados de fila, LGPD, stubs, CLI e deploy. Remove seções "Evolução Recente" integrando o conteúdo na narrativa principal e exclui informações sensíveis (portas, IPs, domínios internos, tokens).'
---

# Atualização de Posts do Blog

## Arquivos dos Posts
Os posts do blog estão em arquivos HTML em:
```
/home/user/server/projetos/github-portifolio/server/data/posts/
```

Cada arquivo `.html` contém um `<article>` completo com:
- `<header>`: título, resumo, data, tempo de leitura, categoria, imagem
- Corpo do artigo com seções `<h2>` e `<h3>`
- Diagramas Mermaid dentro de `<div class="mermaid">`
- FAQ (`<div class="faq-section">`)
- Conclusão

## Projetos Relacionados

### whatsapp-api
- Caminho: `/home/user/server/projetos/whatsapp-api/`
- Stack: Node.js + TypeScript + Express + whatsapp-web.js (Puppeteer) + better-sqlite3
- Arquivos principais: `src/index.ts`, `src/whatsapp.ts`, `src/db.ts`, `src/queue.ts`, `src/config.ts`, `src/middleware/auth.ts`
- DB schema (`asks` table): `id`, `chatId`, `lid`, `question`, `options`, `callbackUrl`, `status` (default 'pending'), `createdAt` — SEM `messageId` ou `updatedAt`

### caixa_escolar
- Caminho: `/home/user/server/projetos/caixa_escolar/`
- Stack: Python + Playwright + Flask + curl_cffi + BeautifulSoup + Geopy + LLM (API compatível com OpenAI)
- Pipeline: Playwright autentica no portal Caixa Escolar MG → coleta editais (grupos 2896, 3491) → filtra por distância (Geopy) → NLP via LLM → scraping de preços no Buscapé → estatísticas de preços → relatório Markdown → alertas WhatsApp
- Autenticação: CNPJ + senha (decriptada via Fernet) no portal `caixaescolar.educacao.mg.gov.br`
- LLM: API compatível com OpenAI (`/v1/chat/completions`) configurável via `LLM_BASE_URL`
- Cache: `cache/api_cache.json` (TTL 12h) para escolas, itens, resultados Buscapé e coordenadas; `cache/data.json` para coordenadas geográficas
- Painel Flask: `webserver.py` com autenticação WhatsApp (código de **5 dígitos**) e agendador dinâmico (lê `cfg.md` a cada 60s)

### Insta_post
- Caminho: `/home/user/server/projetos/Insta_post/`
- Stack: Python + Flask + Flask-SocketIO + APScheduler + React/TS + Pillow + Ollama + gen_provider
- Geração de imagens via gen_provider (`/api/image/generate`, diffusers, realisticVisionV60B1)
- Perfis YAML: `person.yaml`, `post.yaml`, `stories.yaml`, `meta.yaml`, `image.yaml`, `pack.yaml`, `user.yaml`, `.env`
- Autenticação WhatsApp: código de **5 dígitos**, token JWT com 10 dias de validade
- VLM quality check: usa `think=False` para inferência rápida

### py_text_insert_image
- Caminho: `/home/user/server/projetos/py_text_insert_image/`
- Stack: Flask + Pillow + ReportLab
- Pipeline: upload imagem → Pillow lê dimensões → cadastra fontes TTF → parse inputs ";" → itertools.product → ReportLab canvas → PDF
- Deploy: PM2 (processo `image2pdf`)

### eixo_x_projetos (360View)
- Caminho: `/home/user/server/projetos/eixo_x_projetos/`
- Stack: Node.js + Express + **Sequelize** (NÃO Prisma) + SQLite + React + Three.js + React Three Fiber
- Esfera: `scale={[-1, 1, 1]}`, `side={THREE.BackSide}`, raio 500, segmentos 128×64
- Zoom: FOV dinâmico (NÃO translação da câmera)
- MediaHistory: registra URL e título, NÃO tem userId nem replacedFile
- Arquivos: servidos via middleware estático Express em `/media/files` e `/media/uploads`

### beNext
- Caminho: `/home/user/server/projetos/beNext/`
- Stack: Node.js + Express + Sequelize + PostgreSQL + WebSockets + Stripe + whatsapp-web.js
- Estados da fila: `inLine`, `priority`, `inService`, `served`, `removed`, `canceled`
- LGPD: AES-256-GCM, audit log (sem diff antes/depois), data retention (apenas DELETEs)
- Observabilidade: logger JSON, métricas Prometheus-style

### advp-python
- Caminho: `/home/user/server/projetos/advp-python/`
- Stack: Python + FastAPI + Uvicorn + React/TS + Vite 5 + Tailwind CSS
- Lexer: **45 regras** de regex
- Stubs: `ui.py`, `db.py`, `string.py`, `math.py`, `array.py`, `date.py`, `types.py`, `xml_json.py`, `protheus.py` (NÃO existem `rest.py` ou `ui_extra.py`)

## Processo de Atualização

Ao receber um pedido de atualização dos posts do blog:

### 1. Leia o post atual
Leia o arquivo HTML completo do post em `/home/user/server/projetos/github-portifolio/server/data/posts/`.

### 2. Verifique cada tópico contra o código real
Use subagentes para verificar cada seção/tópico do post. Cada subagente deve:
- Ler o post (forneça o trecho relevante)
- Explorar o código fonte do projeto correspondente
- Comparar cada afirmação com a implementação real
- Reportar como ✅ CORRETO ou ❌ INCORRETO

### 3. Tópicos a verificar em cada post (checklist):

**whatsapp-api:**
- [ ] DB schema (colunas reais da tabela `asks` em `db.ts`)
- [ ] Autenticação (Bearer Token em `auth.ts`)
- [ ] Endpoints existentes (send-text, send-media, send-ask, edit-message, help, health)
- [ ] Fila de mensagens (intervalo de 1s em `queue.ts`)
- [ ] Normalização LID/WID (`normalizeToPhoneId()` em `whatsapp.ts`)
- [ ] Deduplicação (Set em `whatsapp.ts`)
- [ ] beNext forwarding (payload com whatsappPhone, messageBody, etc.)
- [ ] Configuração (PORT, API_TOKEN, BENEXT_WEBHOOK_URL em `config.ts`)

**caixa_escolar:**
- [ ] Portal correto (Caixa Escolar MG, NÃO SEE/MG)
- [ ] Fluxo de login (perfil Fornecedor + CNPJ + senha + extração de token)
- [ ] LLM (API compatível com OpenAI, NÃO necessariamente Ollama local; modelo NÃO especificado no código)
- [ ] Etapas do NLP (build_product_description_from_description + build_search_query_from_description)
- [ ] Busca de preços (Buscapé via curl_cffi + BeautifulSoup, NÃO Playwright)
- [ ] Cache (api_cache.json TTL 12h; data.json só para coordenadas)
- [ ] Algoritmo de preços (estatísticas min/max/média/mediana, NÃO filtro por orçamento)
- [ ] WhatsApp auth (código de **5 dígitos**)
- [ ] Agendador (polling a cada 60s no cfg.md)

**Insta_post:**
- [ ] Gen provider (URL `/api/image/generate` via `stable_diffusion.py`)
- [ ] Perfis YAML (arquivos reais: person.yaml, post.yaml, stories.yaml, meta.yaml, image.yaml, pack.yaml, user.yaml)
- [ ] WhatsApp auth (código de **5 dígitos**, token 10 dias)
- [ ] VLM quality check (think=False para imagem, think=True disponível para texto)
- [ ] VRAM (GenerationQueue, OLLAMA_KEEP_ALIVE padrão 10m)
- [ ] State persistence (generation_queue.json, pending_approvals.yaml)

**py_text_insert_image:**
- [ ] Flask pipeline (upload → Pillow → TTF → ";" → itertools.product → ReportLab)
- [ ] Pillow para dimensões
- [ ] ReportLab com showPage() e drawString()
- [ ] Fontes em static/fonts/
- [ ] Alinhamento via stringWidth()
- [ ] PM2 (processo image2pdf)

**eixo_x_projetos (360View):**
- [ ] ORM correto (Sequelize, NÃO Prisma)
- [ ] Esfera (scale[-1,1,1], BackSide, 500, 128, 64)
- [ ] Zoom via FOV
- [ ] Mipmapping desabilitado
- [ ] MediaHistory (campos reais: sem userId, sem replacedFile)
- [ ] Servidor de arquivos (middleware estático, NÃO controller dedicado)

**beNext:**
- [ ] Estados da fila (todos os 6)
- [ ] WebSocket trigger
- [ ] Pagamentos Stripe com cancelAtPeriodEnd
- [ ] LGPD encryption (AES-256-GCM)
- [ ] Data retention (apenas DELETEs, sem anonimização automática)
- [ ] Audit log (sem diff antes/depois)
- [ ] Logger estruturado JSON
- [ ] Métricas (latência WebSocket, erro webhook, memória, filas ativas)
- [ ] WhatsApp auth service
- [ ] Testes (encryption.test.ts, hashPassword.test.ts, phoneUtils.test.ts)

**advp-python:**
- [ ] Lexer (**45 regras**, NÃO 50+)
- [ ] CLI (subcomandos reais em `cli.py`)
- [ ] Stubs (conferir cada módulo individualmente no código)
- [ ] Round-trip testing (SequenceMatcher, threshold 80%)
- [ ] Deploy (PM2, localhost binding, Vite 5)

### 4. Aplique as correções
Use `multi_replace_string_in_file` para aplicar todas as correções de uma vez.

### 5. Informações sensíveis a NÃO incluir
- Portas numéricas (ex: 8098, 4001, 8040, 3000, 9110, 10020)
- IPs internos (127.0.0.1, 192.168.*)
- Domínios internos (apps.tec.br, ai.apps.tec.br, api.apps.tec.br)
- Caminhos absolutos do servidor (ex: /home/user/server/.venv/bin/python)
- Nomes de variáveis de ambiente sensíveis (BENEXT_WEBHOOK_URL, API_TOKEN, etc.)
- Senhas, tokens, chaves de API
