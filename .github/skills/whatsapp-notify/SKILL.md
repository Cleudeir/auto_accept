---
name: whatsapp-notify
user-invocable: false
description: 'Enviar notificações via WhatsApp usando o serviço whatsapp-api do workspace. Usado para avisar o usuário (número padrão 553193281399) quando um agente precisa de atenção — por exemplo, quando o Task Orchestrator vai fazer uma pergunta ao usuário. Cobre endpoint, autenticação, formato da mensagem e tratamento de falhas.'
---

# Notificação via WhatsApp

## Serviço
O envio usa o serviço **whatsapp-api** (projeto `/home/user/server/projetos/whatsapp-api`), que roda via PM2.
- Nome PM2: `whatsapp-api`
- Porta: `9110` (definida no `ecosystem.config.js`)
- Base URL local: `http://localhost:9110`

## Destinatário padrão
- Número: `553193281399` (com código do país, sem `@c.us` — a API adiciona `@c.us` automaticamente)
- Para outro número, use o mesmo formato: `55` + DDD + número.

## Autenticação
- Header: `Authorization: Bearer <API_TOKEN>`
- O `API_TOKEN` **nunca** deve ser hardcoded em código, skill ou documento.
- **NUNCA** imprima, logue ou reporte o valor do token em outputs, relatórios ou mensagens.

### Como ler o token do `.env` do projeto
O token está no arquivo `.env` do projeto whatsapp-api:
```
/home/user/server/projetos/whatsapp-api/.env
```
Linha relevante: `API_TOKEN=<valor>`

Passos obrigatórios antes de qualquer envio:
1. **Verifique se o arquivo existe** — se não existir, não invente o token; reporte o erro ao chamador.
2. **Leia o token SEMPRE em tempo de execução** via comando, nunca copie o valor manualmente:
   ```bash
   TOKEN=$(grep '^API_TOKEN=' /home/user/server/projetos/whatsapp-api/.env | cut -d= -f2 | tr -d '"' | tr -d "'" | tr -d '\r')
   ```
   - O `tr -d` remove aspas e `\r` (quebras de linha do Windows) caso existam.
3. **Confirme que o token não está vazio** antes de usar:
   ```bash
   [ -n "$TOKEN" ] || echo "ERRO: API_TOKEN vazio ou não encontrado no .env"
   ```
4. **NUNCA** exiba `$TOKEN` em logs, reports ou mensagens — só use no header da requisição.

## Enviar mensagem de texto
Endpoint: `POST /whatsapp_api/send-text`

```bash
TOKEN=$(grep '^API_TOKEN=' /home/user/server/projetos/whatsapp-api/.env | cut -d= -f2 | tr -d '"' | tr -d "'" | tr -d '\r')
[ -n "$TOKEN" ] || { echo "ERRO: API_TOKEN vazio"; exit 1; }
curl -sS -X POST http://localhost:9110/whatsapp_api/send-text \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to": "553193281399", "message": "SEU TEXTO AQUI"}'
```

Resposta de sucesso esperada:
```json
{"success": true, "message": "Text message queued and sent", "messageId": "..."}
```

### Mensagem
- Use texto simples, direto e objetivo (ex.: `Copilot precisa de você: abra o VS Code para responder uma pergunta.`).
- Markdown do WhatsApp é aceito: `*negrito*`, `_itálico_`, `~tachado~`, ``` `código` ```.

## Verificar saúde do serviço
Endpoint público: `GET /health`

```bash
curl -sS http://localhost:9110/health
```
- Se não responder, verifique se o serviço está online:
  ```bash
  pm2 status whatsapp-api
  pm2 logs whatsapp-api --lines 20 --nostream
  ```
- Se estiver offline, tente iniciar:
  ```bash
  pm2 start /home/user/server/projetos/whatsapp-api/ecosystem.config.js
  ```
  Depois aguarde o cliente WhatsApp conectar (a conexão pode levar alguns segundos).

## Tratamento de falhas
- **401 Unauthorized** → token inválido ou `.env` não lido; confira se o `API_TOKEN` está definido no `.env`.
- **400 Missing "to" or "message"** → confira os campos do body.
- **500 / erro do cliente WhatsApp** → o cliente pode estar desconectado; confira `pm2 logs whatsapp-api`.
- Se o envio falhar após 1 tentativa, reporte a falha ao chamador (não fique repetindo) — o agente que pediu a notificação decide se o aviso é crítico.

## Regras
- NUNCA exponha o token, nem em logs, reports ou mensagens.
- NUNCA envie mensagens sem que o chamador tenha pedido.
- NUNCA use este serviço para spam — apenas notificações solicitadas.
