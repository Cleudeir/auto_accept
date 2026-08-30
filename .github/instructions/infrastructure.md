---
name: infrastructure-deploy-patterns
description: >
  INFRAESTRUTURA E DEPLOY — Nginx reverse proxy (Docker), PM2, Docker Compose,
  Dockerfile, GPU VRAM Manager, scripts raiz, variáveis de ambiente e monitoramento.
  Aplica-se à configuração de infraestrutura, deploy e diagnóstico.
applyTo: "**/*"
---

# Infraestrutura e Deploy

> Para a lista completa de todos os projetos com portas, scripts e funções,
> consulte `.github/instructions/projects.md`.

---

## Nginx Reverse Proxy

O Nginx roda em **Docker** (`ngnix/docker-compose.yml`) com `network_mode: host`.

- **Compose:** `ngnix/docker-compose.yml`
- **Config principal:** `ngnix/nginx/conf.d/apps.tec.br.conf`
- **SSL:** Cloudflare Origin CA (certificados em `/etc/nginx/snippets/`)
- **Iniciar:** `docker compose -f ngnix/docker-compose.yml up -d`

### Padrão de Proxy

```nginx
location / {
    proxy_pass http://localhost:PORTA/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $host;
}
```

### Configurações Especiais

- **Uploads:** `client_max_body_size 1G;`
- **Timeouts longos (AI):** 300s
- **Load balancing:** Upstream para llama.cpp (`localhost:8081` + `192.168.20.181:8081`)
- **Segurança:** IPs banidos via `banned-ips.conf` (auto-gerada pelo nginx-monitor)

---

## Deploy com PM2

### Single Service

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'meu-servico',
    cwd: '/home/user/server/projetos/meu-servico',
    script: './start.sh',
    interpreter: 'bash',
    autorestart: true,
    max_restarts: 5,
    min_uptime: 10000,
    restart_delay: 5000,
    env: {
      PORT: 8081,
      NODE_ENV: 'production'
    }
  }]
};
```

### Dual Service (backend + frontend)

```javascript
module.exports = {
  apps: [
    {
      name: 'projeto-backend',
      cwd: '/home/user/server/projetos/projeto/backend',
      script: 'npm',
      args: 'run start',
      autorestart: true,
      max_restarts: 5,
      min_uptime: 10000,
      restart_delay: 5000
    },
    {
      name: 'projeto-frontend',
      cwd: '/home/user/server/projetos/projeto/web',
      script: 'npm',
      args: 'run prod',
      autorestart: true,
      max_restarts: 5,
      min_uptime: 10000,
      restart_delay: 5000
    }
  ]
};
```

### Serviços GPU (AI/ML)

```javascript
env: {
  PYTORCH_CUDA_ALLOC_CONF: 'expandable_segments:True',
  PM2_SERVICE_NAME: 'meu-servico'
}
```

---

## Deploy com Docker

### Docker Compose

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready"]
  app:
    build: .
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "${PORT}:5000"
```

### Dockerfile — Node.js Alpine

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
RUN apk add --no-cache curl && adduser -D appuser
USER appuser
COPY --from=build /app/dist ./dist
EXPOSE 5000
CMD ["node", "dist/index.js"]
```
---

## Variáveis de Ambiente (Padrão)

```env
PORT=8035
NODE_ENV=production
DATABASE_URL=mysql://user:pass@host/db
JWT_SECRET_KEY=...
LLM_MODE=llamacpp
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
ALLOWED_ORIGINS=*
```

---

## Monitoramento

| Serviço | Função | Notificação |
|---------|--------|-------------|
| `nginx-monitor` | Detecta ataques no nginx, bane IPs | WhatsApp via whatsapp-api |
| `intrusion-monitor` | Monitora arquivos/portas | WhatsApp via whatsapp-api |

---

## Armazenamento Compartilhado

- Modelos AI/ML: `/mnt/data/`
- Virtual env Python: `/mnt/data/comfy/venv` (compartilhado entre serviços)
- Logs: `projetos/<projeto>/logs/`
