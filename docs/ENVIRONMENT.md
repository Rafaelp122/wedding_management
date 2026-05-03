# 🔐 Guia de Configuração de Ambiente

Este guia detalha como configurar seu ambiente de desenvolvimento local e as variáveis necessárias para produção. Para um início rápido, consulte o **[Quick Start no README.md](../../README.md#quick-start-resumo)**.

---

## ⚙️ Configuração Inicial

1. **Clonar e Configurar Variáveis:**
   ```bash
   cp .env.example .env  # Crie o arquivo de ambiente
   make secret-key       # Gere uma SECRET_KEY segura
   ```

2. **Gerenciamento de Login:**
   O sistema utiliza **email** como identificador único (login), não username.

---

## 📄 Variáveis de Ambiente (.env)

### Obrigatórias
| Variável | Descrição |
| :--- | :--- |
| `SECRET_KEY` | Chave criptográfica do Django. Gere com `make secret-key`. |
| `DB_HOST` | Host do banco (`db` para Docker, `localhost` para local). |

### Opcionais (Desenvolvimento)
| Variável | Padrão | Descrição |
| :--- | :--- | :--- |
| `DEBUG` | `True` | Ativa modo debug. **NUNCA use True em produção.** |
| `DB_NAME` | `wedding_db` | Nome do banco de dados. |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Origens permitidas para o frontend. |

### Produção (Exemplos)
| Variável | Descrição |
| :--- | :--- |
| `ALLOWED_HOSTS` | Domínios permitidos (ex: `app.meusistema.com`). |
| `SENTRY_DSN` | URL para monitoramento de erros. |
| `R2_BUCKET` | Nome do bucket no Cloudflare R2 para uploads. |

---

## 🛠 Comandos de Gestão (Makefile)

O projeto utiliza um `Makefile` para automatizar tarefas comuns.

### Docker (Fluxo Recomendado)
```bash
make up              # Inicia containers em background
make down            # Para e remove containers
make migrate         # Aplica migrações no banco
make superuser       # Cria um administrador
make logs            # Ver logs em tempo real
```

### Desenvolvimento Local (sem Docker)
Se preferir rodar sem containers, você precisará do **[UV](https://docs.astral.sh/uv/)** instalado:
```bash
# Backend
cd backend && uv sync --group dev
uv run python manage.py runserver

# Frontend
cd frontend && npm ci && npm run dev
```

### Qualidade e Testes
```bash
make lint            # Verifica erros de estilo (Ruff)
make format          # Corrige formatação automaticamente
make mypy            # Verifica tipagem estática
make test            # Executa a suíte de testes (Pytest)
make check-ci        # Executa todos os checks locais (espelha o CI)
```

---

## 🛡️ Segurança: Checklist Pré-Deploy

- [ ] `DEBUG=False` configurado.
- [ ] `SECRET_KEY` com pelo menos 64 caracteres.
- [ ] `ALLOWED_HOSTS` restrito aos domínios oficiais.
- [ ] Banco de dados utiliza senha forte e não a padrão.
- [ ] Monitoramento (Sentry) configurado.
- [ ] **Checklist completo em [docs/ARCHITECTURE.md](ARCHITECTURE.md#segurança)**.

---

**Última atualização:** 1 de março de 2026
**Responsável:** Rafael
**Versão:** 2.0 (Foco em How-to/Referência)
