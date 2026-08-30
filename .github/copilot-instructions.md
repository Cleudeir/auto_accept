# Project Guidelines

## Code Style & Conventions

- **Never add fallback code** (try/catch fallbacks, default values, optional chaining fallbacks, conditional fallbacks, or any other form of defensive fallback logic) unless the user explicitly orders you to. If a value may not exist, let it fail naturally instead of silently falling back to a default.
- **Sempre pergunte ao usuário em caso de dúvida** — Ao tomar decisões de projeto (arquitetura, padrões, abordagens, escolhas de bibliotecas, estrutura de diretórios, nomes de variáveis/funções, etc.), se houver qualquer ambiguidade ou dúvida, pergunte ao usuário antes de decidir. Nunca assuma ou faça escolhas arbitrárias por conta própria.

## Blog & Insights Posts

Posts do blog estão em `/home/user/server/projetos/github-portifolio/server/data/posts/*.html`. 
Para atualizar, use a skill **blog-posts** (`.github/skills/blog-posts/SKILL.md`).
