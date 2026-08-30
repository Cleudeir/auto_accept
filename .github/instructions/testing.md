---
name: testing-quality-gates
description: >
  PADRÕES DE TESTE E QUALITY GATES — Cobertura mínima, estrutura de testes,
  git hooks, configuração de ferramentas. Aplica-se a TODO projeto no workspace.
applyTo: "**/*"
---

# Testes e Quality Gates

## Regra Obrigatória

> **Todo projeto DEVE ter testes com ampla cobertura. Nenhum commit ou push é permitido sem que os testes passem.**

## Cobertura Mínima

- **80%** em código de produção (excluindo migrations, configs e boilerplate)
- Estratégia: unitários + integração + (quando aplicável) E2E

## Stack de Testes por Tipo de Projeto

| Tipo | Ferramentas |
|------|-------------|
| Backend Python (FastAPI/Flask) | `pytest` + `pytest-cov` + `httpx` (AsyncHTTPClient) |
| Backend Node.js (Express) | `vitest` ou `jest` com cobertura |
| Frontend React | `vitest` + `@testing-library/react` + `jsdom` |
| Testes de API | Cobrir todos os endpoints (sucesso + erro + validação) |

## Estrutura de Diretórios

```
projeto/
├── tests/
│   ├── unit/                  # Testes unitários
│   ├── integration/           # Testes de integração (API, DB)
│   └── fixtures/              # Dados de teste / mocks
├── conftest.py                # Fixtures compartilhadas (Python)
├── vitest.config.ts           # Config vitest (Node/React)
└── jest.config.js             # Config jest (alternativa)
```

## Quality Gates — Git Hooks

### Node.js/TypeScript — Husky + lint-staged

```bash
# .husky/pre-commit
npm run lint && npm test

# .husky/pre-push
npm run test:coverage
```

```json
// package.json
{
  "scripts": {
    "prepare": "husky",
    "test": "vitest run",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src/"
  }
}
```

### Python — pre-commit ou git hooks manuais

```bash
#!/bin/bash
# .git/hooks/pre-commit
set -e
pytest tests/ --cov=. --cov-fail-under=80 -q

# .git/hooks/pre-push
set -e
pytest tests/ --cov=. --cov-fail-under=80 --tb=short
```

## Configuração de Cobertura

### Python (pytest)

```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
omit = ["tests/*", "migrations/*", "config/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### Node.js/TypeScript (vitest)

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      lines: 80,
      functions: 80,
      branches: 80,
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.d.ts', 'src/**/*.test.ts'],
    }
  }
});
```

## Regras para o Copilot

1. **Sempre gerar testes** junto com código novo (unitários no mínimo)
2. **Novos endpoints** devem ter testes de integração cobrindo sucesso e erro
3. **Novas funções** devem ter testes unitários com edge cases
4. **Ao modificar código**, atualizar os testes existentes relacionados
5. **Não remover testes** sem justificativa explícita do usuário
6. **Cobertura deve ser verificada** antes de sugerir que o código está pronto
