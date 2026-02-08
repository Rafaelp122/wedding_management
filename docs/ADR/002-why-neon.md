# ADR-002: Por que Neon PostgreSQL?

**Status:** Aceito
**Data:** Janeiro 2025
**Decisor:** Rafael
**Contexto:** Escolha de banco de dados PostgreSQL gerenciado

---

## Contexto e Problema

Precisamos de um banco de dados PostgreSQL que:

- Seja serverless (escale automaticamente)
- Tenha free tier generoso (MVP com baixo volume)
- Ofereça backups automáticos
- Permita branching para dev/staging/prod
- Tenha boa performance (< 100ms de latência)

**Alternativas consideradas:**

1. **Neon** (escolhido)
2. Railway PostgreSQL
3. AWS RDS Free Tier
4. Supabase PostgreSQL
5. Heroku PostgreSQL

---

## Decisão

Escolhemos **Neon PostgreSQL** como banco de dados gerenciado.

---

## Justificativa

### Vantagens do Neon

**1. Free Tier Superior:**

| Feature       | Neon         | Railway   | Supabase  | RDS Free |
| ------------- | ------------ | --------- | --------- | -------- |
| **Storage**   | **3GB**      | 1GB       | 500MB     | 20GB     |
| **Compute**   | 191h/mês     | Sempre-on | Ilimitado | 750h/mês |
| **Branching** | ✅ Ilimitado | ❌ Não    | ❌ Não    | ❌ Não   |
| **Backups**   | 7 dias       | 7 dias    | Ilimitado | Manual   |

**2. Serverless Verdadeiro:**

- **Hibernação automática:** Banco "dorme" após 5 minutos de inatividade
- **Cold start:** 1-2s (aceitável)
- **Zero custo quando inativo** (perfeito para MVP)

**3. Branching (Killer Feature):**

```bash
# Cria branch de desenvolvimento a partir da produção
neon branches create --name dev --parent main

# Testa migrations sem afetar produção
python manage.py migrate --database dev

# Merge branch após validação
neon branches merge dev --to main
```

**Casos de uso:**

- ✅ Testar migrations complexas sem risco
- ✅ Staging com dados reais (branch de prod)
- ✅ Desenvolvimento local sem contaminar prod

**4. Performance:**

```
Latência média (us-east-1 → Neon):
- Queries simples: ~50ms
- Queries complexas (JOIN): ~150ms
- Cold start: 1-2s (primeira query após sleep)
```

**5. Integração com Django:**

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('NEON_HOST'),
        'NAME': os.getenv('NEON_DATABASE'),
        'USER': os.getenv('NEON_USER'),
        'PASSWORD': os.getenv('NEON_PASSWORD'),
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',  # TLS obrigatório
        },
        'CONN_MAX_AGE': 600,  # Connection pooling (10min)
    }
}
```

---

### Comparação Detalhada

#### Neon vs Railway

| Aspecto           | Neon               | Railway              |
| ----------------- | ------------------ | -------------------- |
| **Storage**       | 3GB (3x maior)     | 1GB                  |
| **Compute**       | 191h/mês (hiberna) | Sempre-on (500h/mês) |
| **Cold start**    | 1-2s               | 0s (sempre ativo)    |
| **Branching**     | ✅ Nativo          | ❌ Não               |
| **Custo escala**  | USD 15/mês (prod)  | USD 5/mês            |
| **Portabilidade** | PostgreSQL puro    | PostgreSQL puro      |

**Por que Neon?**

- 3x mais storage (crítico para MVP crescer)
- Branching = segurança em migrations
- Hibernação = menor custo

**Trade-off:**

- Cold start de 1-2s (aceitável)

---

#### Neon vs AWS RDS

| Aspecto          | Neon          | RDS Free Tier        |
| ---------------- | ------------- | -------------------- |
| **Storage**      | 3GB           | 20GB                 |
| **Compute**      | 191h/mês      | 750h/mês (12 meses)  |
| **Hibernação**   | ✅ Automática | ❌ Manual            |
| **Branching**    | ✅ Nativo     | ❌ Não               |
| **Setup**        | 5 minutos     | 30 minutos (VPC, SG) |
| **Custo escala** | USD 15/mês    | USD 50-100/mês       |

**Por que Neon?**

- Setup mais simples (zero config de rede)
- Hibernação automática (RDS cobra sempre-on)
- Branching nativo
- **Após 12 meses:** RDS cobra, Neon continua free tier

---

### Trade-offs Aceitos

**❌ Cold Start (1-2s):**

- **Impacto:** Primeira query após inatividade é lenta
- **Mitigação:**
  - Keep-alive ping (opcional, USD 1/mês)
  - Aceitável para MVP (não é sistema crítico)

**❌ Storage Limitado (3GB):**

- **Estimativa MVP:** ~500MB (10% do limite)
- **Projeção 500 usuários:** ~2GB (60% do limite)
- **Mitigação:** Monitorar uso, upgrade para Pro (USD 15/mês)

**❌ Compute Limitado (191h):**

- **Cálculo:** 191h ÷ 30 dias = ~6.3h/dia ativo
- **Estimativa MVP:** ~50h/mês (26% do limite)
- **Mitigação:** Hibernação automática otimiza uso

---

## Configuração de Exemplo

**Variáveis de ambiente:**

```bash
# .env
NEON_HOST=ep-cool-darkness-123456.us-east-2.aws.neon.tech
NEON_DATABASE=wedding_db
NEON_USER=wedding_user
NEON_PASSWORD=secret_password_here
```

**Django settings.py:**

```python
import dj_database_url

# Configuração via DATABASE_URL (recomendado)
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True
    )
}
```

**Branching workflow:**

```bash
# Criar branch de dev
neon branches create \
  --project-id PROJECT_ID \
  --name dev \
  --parent main

# Conectar Django ao branch dev
export NEON_HOST=ep-dev-branch-123456.us-east-2.aws.neon.tech
python manage.py migrate

# Após validação, merge
neon branches merge dev --to main
```

---

## Consequências

### Positivas ✅

1. **Free tier generoso:** 3GB storage (3x Railway)
2. **Branching nativo:** Testa migrations sem risco
3. **Hibernação automática:** Zero custo quando inativo
4. **Backups automáticos:** 7 dias de retenção
5. **Portabilidade:** PostgreSQL puro (sem vendor lock-in)
6. **Setup simples:** 5 minutos vs 30 minutos (RDS)

### Negativas ❌

1. **Cold start:** 1-2s após hibernação
2. **Storage limitado:** 3GB (suficiente para MVP, mas requer monitoramento)
3. **Compute limitado:** 191h/mês (hibernação mitiga)
4. **Startup relativamente nova:** Menos maduro que RDS/Railway

### Neutras ⚠️

1. Requer monitoramento de usage (storage, compute)
2. Free tier permanente (sem prazo de 12 meses como RDS)

---

## Monitoramento

**Métricas a observar:**

```sql
-- Storage usado
SELECT pg_size_pretty(pg_database_size('wedding_db'));

-- Conexões ativas
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Queries lentas (> 1s)
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Gatilhos de revisão:**

- Storage > 2.5GB (83% do limite)
- Compute > 150h/mês (78% do limite)
- Cold start > 20% das requisições
- Latência P95 > 500ms

**Ações:**

- Storage alto: Implementar archive/purge de dados antigos
- Compute alto: Otimizar queries, considerar upgrade Pro
- Cold start frequente: Habilitar keep-alive ping (USD 1/mês)

---

## Referências

- [Neon Documentation](https://neon.tech/docs)
- [Neon Branching Guide](https://neon.tech/docs/guides/branching)
- [Django PostgreSQL Settings](https://docs.djangoproject.com/en/5.0/ref/databases/#postgresql-notes)
- [ARCHITECTURE.md](../ARCHITECTURE.md)

---

**Última atualização:** 8 de fevereiro de 2026
**Revisão:** Após 3 meses de MVP em produção
