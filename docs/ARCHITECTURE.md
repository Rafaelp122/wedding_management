# 🏗️ Arquitetura Técnica - Wedding Management System

## Versão 1.1 - Arquitetura de Software e Infraestrutura

> **Última atualização:** 1 de março de 2026

---

## 1. Visão Geral

### Arquitetura Headless (API-First)

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND LAYER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React 19 + Vite 7 + TypeScript 5                    │   │
│  │  - Tailwind CSS v4 (styling)                         │   │
│  │  - Zustand 5 (state management)                      │   │
│  │  - TanStack Query 5 (data fetching)                  │   │
│  │  - Axios (HTTP client)                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↕ HTTPS (JWT)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Vercel Edge Network (CDN Global)                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                ↕
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND LAYER                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Django 5.2 + Django Ninja 1.6                       │   │
│  │  - django-ninja-jwt (Auth)                           │   │
│  │  - django-filter (query filtering)                   │   │
│  │  - django-zeal (N+1 detection)                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Google Cloud Run (Serverless)                       │   │
│  │  - Auto-scaling: 0 → 100 instances                   │   │
│  │  - CPU: 1 vCPU, RAM: 512MB                          │   │
│  │  - Request timeout: 60s                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                    ↕                      ↕
┌───────────────────────────┐  ┌──────────────────────────────┐
│   DATABASE LAYER          │  │   STORAGE LAYER              │
│  ┌────────────────────┐   │  │  ┌───────────────────────┐  │
│  │  Neon PostgreSQL   │   │  │  │  Cloudflare R2        │  │
│  │  - 3GB storage     │   │  │  │  - 10GB storage       │  │
│  │  - 191h compute/mês│   │  │  │  - Zero egress cost   │  │
│  │  - Branching       │   │  │  │  - S3-compatible API  │  │
│  └────────────────────┘   │  │  └───────────────────────┘  │
└───────────────────────────┘  └──────────────────────────────┘
                    ↕
┌───────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                        │
│  ┌───────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Resend Email  │  │ Sentry       │  │ Cloud Scheduler│ │
│  │ 3k emails/mês │  │ 5k events/mês│  │ 3 jobs grátis  │ │
│  └───────────────┘  └──────────────┘  └────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

**Características:**

- ✅ Frontend e Backend evoluem independentemente
- ✅ Múltiplos clientes possíveis (Web, Mobile, API pública)
- ✅ Deploy separado com zero acoplamento
- ✅ Escalabilidade independente por camada

---

## 2. Stack Técnico Detalhado

### 2.1 Backend (Django Ninja)

**Framework Core:**

```python
Django>=5.2.9,<6.0
django-ninja>=1.6.2
```

**Extensões:**

```python
django-ninja-jwt>=5.4.4         # JWT auth
django-cors-headers>=4.6.0,<4.7 # CORS handling
```

**Utilitários:**

```python
django-extensions>=4.1,<4.2     # Shell plus, etc.
django-zeal>=2.0.4,<3.0         # N+1 query detection
gunicorn>=23.0.0,<24.0          # WSGI server
```

**Estrutura de Apps:**

```
backend/apps/
├── core/           # BaseModel, Mixins, Managers, Schemas Base
├── tenants/        # Company entity, TenantModel, TenantManager
├── users/          # Authentication, JWT, User model
├── weddings/       # Wedding entity (raiz do domínio)
├── finances/       # Budget, BudgetCategory, Expense, Installment
├── logistics/      # Supplier, Item, Contract
└── scheduler/      # Event, Task
```

---

### 2.2 Frontend (React + Vite)

**Framework Core:**

```json
{
  "react": "^19.2.0",
  "react-dom": "^19.2.0",
  "vite": "^7.2.4",
  "typescript": "~5.9.3"
}
```

**UI e Styling:**

```json
{
  "tailwindcss": "^4.1.18",
  "shadcn/ui": "latest",
  "lucide-react": "^0.563.0"
}
```

**State Management:**

```json
{
  "zustand": "^5.0.11",
  "@tanstack/react-query": "^5.90.21",
  "axios": "^1.13.5"
}
```

**Estrutura de Pastas:**

```
frontend/src/
├── api/              # Clients gerados (Orval) e configuração Axios
├── components/
│   └── ui/           # Componentes shadcn/ui
├── features/         # Funcionalidades por domínio
├── hooks/            # Custom React hooks
├── lib/              # Utilitários e helpers
├── pages/            # Páginas da aplicação
├── router/           # Configuração de rotas (React Router v7)
├── stores/           # Zustand stores
└── types/            # TypeScript definitions
```

---

### 2.3 Banco de Dados (Neon PostgreSQL)

**Configuração:**

```python
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
# Em testes, sempre SQLite in-memory para velocidade
```

**Índices Estratégicos:**

```sql
-- Multitenancy (Vertical Isolation - Usado em 100% das queries)
CREATE INDEX idx_company_id ON finances_expense(company_id);
CREATE INDEX idx_company_id ON logistics_item(company_id);
CREATE INDEX idx_company_uuid_composite ON weddings_wedding(company_id, uuid);

-- Contextual Isolation (Horizontal - Wedding Context)
CREATE INDEX idx_wedding_id ON finances_expense(wedding_id);
CREATE INDEX idx_wedding_id ON logistics_item(wedding_id);

-- Filtragem de status
CREATE INDEX idx_installment_status ON finances_installment(status);
CREATE INDEX idx_contract_status ON logistics_contract(status);

-- Busca por data
CREATE INDEX idx_installment_due_date ON finances_installment(due_date);
CREATE INDEX idx_event_start_time ON scheduler_event(start_time);

-- UUID lookup (API pública)
CREATE UNIQUE INDEX idx_expense_uuid ON finances_expense(uuid);
```

**Limites do Free Tier:**

- Storage: 3GB (vs Railway 1GB)
- Compute: 191 horas/mês
- Branching: Ilimitado (dev/staging/prod)
- Backups: 7 dias de retenção

Ver [ADR-002](ADR/002-why-neon.md) para justificativa da escolha.

---

### 2.4 Storage (Cloudflare R2)

**Configuração boto3 (S3-compatible):**

```python
import boto3
from django.conf import settings

s3_client = boto3.client(
    's3',
    endpoint_url=settings.R2_ENDPOINT_URL,
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    region_name='auto'
)
```

**Estrutura de Buckets:**

```
wedding-contracts/
├── {wedding_uuid}/
│   ├── {contract_uuid}/
│   │   └── contract_signed.pdf
```

**Presigned URLs (Upload):**

```python
def generate_upload_url(wedding_id: str, filename: str) -> dict:
    object_key = f'contracts/{wedding_id}/{uuid.uuid4()}/{filename}'

    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.R2_BUCKET,
            'Key': object_key,
            'ContentType': 'application/pdf'
        },
        ExpiresIn=900  # 15 minutos
    )

    return {
        'upload_url': presigned_url,
        'object_key': object_key
    }
```

Ver [ADR-003](ADR/003-why-r2.md) e [ADR-004](ADR/004-presigned-urls.md).

---

## 3. Padrões de Código e Arquitetura

### 3.1 Service Layer Pattern

**Separação de responsabilidades:**

```python
# ❌ ERRADO: Lógica no endpoint / router diretamente
@router.post("/expenses")
def create_expense(request, payload: ExpenseIn):
    expense = Expense.objects.create(**payload.dict())
    # Lógica de negócio aqui é ANTI-PATTERN
    for i in range(expense.installments_count):
        Installment.objects.create(...)
    return expense

# ✅ CORRETO: Lógica no service
@router.post("/expenses")
def create_expense(request, payload: ExpenseIn):
    return ExpenseService.create_with_installments(payload.dict())

# apps/finances/services.py
class ExpenseService:
    @staticmethod
    @transaction.atomic
    def create_with_installments(data: dict) -> Expense:
        """
        Cria expense e gera installments com tolerância zero.

        Validações:
        - Soma de parcelas = valor total
        - Contract amount = Expense amount (se vinculado)
        - Categoria pertence ao mesmo wedding
        """
        expense = Expense.objects.create(**data)

        # Cálculo com tolerância zero (BR-F01)
        amounts = calculate_installments(
            expense.actual_amount,
            expense.installments_count
        )

        for idx, amount in enumerate(amounts, start=1):
            Installment.objects.create(
                expense=expense,
                amount=amount,
                due_date=expense.created_at.date() + timedelta(days=30 * idx)
            )

        return expense
```

**Vantagens:**

- ✅ Testável: Service pode ser testado isoladamente
- ✅ Reutilizável: Chamado de views, tasks, management commands
- ✅ Manutenível: Lógica de negócio em um único lugar

Ver [ADR-006](ADR/006-service-layer.md).

---

### 3.2 Modelagem Base e Multi-tenancy

O sistema utiliza uma hierarquia de classes abstratas para garantir consistência técnica e segurança de dados.

**BaseModel (Técnico):**

```python
# apps/core/models.py
class BaseModel(models.Model):
    """Base abstrata com chave híbrida (BigInt + UUID4) e timestamps."""
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

**TenantModel (Segurança SaaS):**

```python
# apps/tenants/models.py
class TenantModel(BaseModel):
    """
    Garante o isolamento vertical (entre empresas).
    Todo dado de domínio deve herdar desta classe.
    """
    company = models.ForeignKey('tenants.Company', on_delete=models.CASCADE)
    objects = TenantManager() # Filtro automático .for_tenant()

    class Meta:
        abstract = True
```

**WeddingOwnedMixin (Contexto de Negócio):**

```python
class WeddingOwnedMixin(models.Model):
    """
    Denormalização para isolamento horizontal (dentro da mesma empresa).
    Garante que itens do Casamento A não apareçam no Casamento B.
    """
    wedding = models.ForeignKey('weddings.Wedding', on_delete=models.CASCADE)

    class Meta:
        abstract = True
```

---

### 3.3 Validações em Cascata

**Ordem de validação:**

```python
class Expense(WeddingOwnedMixin):
    def clean(self):
        """
        Validações executadas nesta ordem:
        1. Validações de campo (required, max_length)
        2. Validações de negócio (custom)
        3. Validações de integridade (cross-model)
        """
        super().clean()

        # BR-F01: Tolerância zero
        total_installments = self.installments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')

        if total_installments != self.actual_amount:
            raise ValidationError(
                f"Soma das parcelas (R${total_installments}) != "
                f"valor total (R${self.actual_amount})"
            )

        # BR-F02: Âncora Jurídica
        if self.contract and self.actual_amount != self.contract.total_amount:
            raise ValidationError(
                f"Valor da despesa != valor do contrato"
            )

        # BR-SEC03: Cross-wedding validation
        if self.category and self.category.wedding != self.wedding:
            raise ValidationError(
                f"Categoria não pertence ao mesmo casamento"
            )
```

Ver [BUSINESS_RULES.md](BUSINESS_RULES.md) para todas as regras.

---

## 4. Infraestrutura e Deploy

### 4.1 Google Cloud Run (Backend)

**Configuração:**

```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: wedding-api
spec:
  template:
    spec:
      containers:
        - image: gcr.io/PROJECT_ID/wedding-api:latest
          resources:
            limits:
              cpu: "1"
              memory: "512Mi"
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: neon-database
                  key: url
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: django-secret
                  key: value
      timeoutSeconds: 60
      containerConcurrency: 80

  traffic:
    - percent: 100
      latestRevision: true
```

**Dockerfile:**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD exec gunicorn config.wsgi:application \
    --bind :$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
```

**Custos do Free Tier:**

- 2 milhões de requisições/mês
- 360 mil GB-segundos de memória
- 180 mil vCPU-segundos
- **Estimativa MVP:** 25% do limite (R$ 0/mês)

Ver [ADR-001](ADR/001-why-cloud-run.md).

---

### 4.2 Vercel (Frontend)

**Configuração:**

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_URL": "https://wedding-api.run.app"
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [{ "key": "Access-Control-Allow-Origin", "value": "*" }]
    }
  ],
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

**Build otimizado:**

```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          "react-vendor": ["react", "react-dom"],
          "ui-vendor": [
            "@radix-ui/react-dialog",
            "@radix-ui/react-dropdown-menu",
          ],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
});
```

**Custos do Hobby Tier:**

- Build time: Ilimitado
- Bandwidth: 100GB/mês
- **Estimativa MVP:** 10GB/mês (R$ 0/mês)

---

### 4.3 CI/CD Pipeline

**GitHub Actions:**

```yaml
# .github/workflows/backend.yml
name: Backend CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - "backend/**"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-django pytest-cov nplusone

      - name: Run tests
        run: |
          cd backend
          pytest \
            --cov=apps \
            --cov-report=xml \
            --cov-fail-under=75 \
            --nplusone --nplusone-raise

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: wedding-api
          image: gcr.io/${{ secrets.GCP_PROJECT_ID }}/wedding-api:${{ github.sha }}
```

---

## 5. Segurança

### 5.1 Autenticação JWT

**Configuração:**

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Configurável via env
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}
```

**Fluxo de autenticação:**

```
┌─────────┐                                      ┌─────────┐
│ Cliente │                                      │ Backend │
└────┬────┘                                      └────┬────┘
     │                                                │
     │ POST /api/token/                              │
     │ {email, password}                             │
     ├──────────────────────────────────────────────▶│
     │                                                │
     │                    ┌──────────────────────┐   │
     │                    │ Valida credenciais   │   │
     │                    │ Gera access + refresh│   │
     │                    └──────────────────────┘   │
     │                                                │
     │◀──────────────────────────────────────────────┤
     │ {access, refresh}                             │
     │                                                │
     │ GET /api/expenses/                            │
     │ Authorization: Bearer {access}                │
     ├──────────────────────────────────────────────▶│
     │                                                │
     │◀──────────────────────────────────────────────┤
     │ [expenses...]                                 │
```

---

### 5.2 OIDC para Service-to-Service

**Cloud Scheduler → Cloud Run:**

```python
# apps/core/decorators.py
from google.auth.transport import requests
from google.oauth2 import id_token

def require_oidc_auth(view_func):
    """
    Valida token OIDC do Cloud Scheduler.
    Rejeita qualquer outro token (incluindo JWT de usuários).
    """
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            raise PermissionDenied('Missing OIDC token')

        token = auth_header.replace('Bearer ', '')

        try:
            claim = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.CLOUD_RUN_SERVICE_URL
            )

            # Validar service account específico
            if claim['email'] != settings.SCHEDULER_SERVICE_ACCOUNT:
                raise PermissionDenied('Unauthorized service account')

        except Exception as e:
            raise PermissionDenied(f'Invalid OIDC token: {e}')

        return view_func(request, *args, **kwargs)

    return wrapper

# Usage
@api_view(['POST'])
@require_oidc_auth
def check_overdue(request):
    """Endpoint chamado APENAS pelo Cloud Scheduler"""
    # ...
```

Ver [ADR-005](ADR/005-oidc-scheduler.md).

---

### 5.3 Rate Limiting

> 📋 **Planejado** — `django-ratelimit` não está nas dependências atuais.
> Será adicionado antes do deploy em produção.

---

## 6. Performance e Otimizações

### 6.1 Database Query Optimization

**Paginação obrigatória:**

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

**Eager loading:**

```python
# ❌ N+1 Problem
expenses = Expense.objects.all()
for expense in expenses:
    print(expense.category.name)  # Nova query a cada iteração

# ✅ Select Related (1 query)
expenses = Expense.objects.select_related('category', 'contract')

# ✅ Prefetch Related (2 queries)
expenses = Expense.objects.prefetch_related('installments')
```

**Detector N+1 no CI:**

```python
# pytest.ini
[tool:pytest]
addopts = --nplusone --nplusone-raise

# Se detectar N+1, CI falha
```

---

### 6.2 Caching Strategy

**Django cache framework:**

```python
from django.core.cache import cache

def get_financial_health(wedding_id: str):
    cache_key = f'financial_health:{wedding_id}'

    # Tenta cache (TTL: 5 minutos)
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Calcula se não houver cache
    data = calculate_financial_health(wedding_id)

    # Armazena no cache
    cache.set(cache_key, data, timeout=300)

    return data
```

**Invalidação ao modificar dados:**

```python
@receiver(post_save, sender=Expense)
def invalidate_financial_health_cache(sender, instance, **kwargs):
    cache_key = f'financial_health:{instance.wedding_id}'
    cache.delete(cache_key)
```

---

### 6.3 Metas de Performance

| Métrica          | Alvo P50 | Alvo P95 | Estratégia                        |
| ---------------- | -------- | -------- | --------------------------------- |
| **GET simples**  | < 200ms  | < 500ms  | Índices, select_related           |
| **POST/PUT**     | < 300ms  | < 800ms  | Validações otimizadas             |
| **Dashboard**    | < 500ms  | < 1s     | Cache (5min TTL)                  |
| **Batch import** | < 5s     | < 10s    | Bulk insert, transaction.atomic   |
| **Cold start**   | < 2s     | < 3s     | Gunicorn pre-fork, image size opt |

---

## 7. Monitoramento e Observabilidade

### 7.1 Sentry (Error Tracking)

> 📋 **Planejado** — `sentry-sdk` não está nas dependências atuais.
> Será adicionado antes do deploy em produção.

---

### 7.2 Structured Logging

**Configuração atual:** O projeto usa logging JSON em produção e `pretty` em DEBUG, com `RequestIDMiddleware` para rastreamento.

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}
```

**Uso:**

```python
import logging

logger = logging.getLogger(__name__)

logger.info(
    "expense_created",
    extra={
        "wedding_id": expense.wedding_id,
        "amount": float(expense.actual_amount),
    }
)
```

---

## 8. Custos Estimados

### Free Tier Utilization (MVP)

| Serviço             | Free Tier Limite | Uso Estimado    | Utilização | Custo    |
| ------------------- | ---------------- | --------------- | ---------- | -------- |
| **Cloud Run**       | 2M req/mês       | 500k req/mês    | 25%        | R$ 0     |
| **Neon PostgreSQL** | 3GB + 191h       | 1GB + 50h       | 30%        | R$ 0     |
| **Vercel**          | 100GB bandwidth  | 10GB/mês        | 10%        | R$ 0     |
| **Resend**          | 3k emails/mês    | 500 emails/mês  | 16%        | R$ 0     |
| **Cloudflare R2**   | 10GB storage     | 2GB (V1.1)      | 20%        | R$ 0     |
| **Sentry**          | 5k events/mês    | 1k events/mês   | 20%        | R$ 0     |
| **Cloud Scheduler** | 3 jobs grátis    | 1 job (OVERDUE) | 33%        | R$ 0     |
| **TOTAL**           | -                | -               | -          | **R$ 0** |

### Escala Futura (500 usuários)

| Serviço       | Custo Mensal | Notas                            |
| ------------- | ------------ | -------------------------------- |
| **Cloud Run** | USD 15       | Min instances: 1, auto-scale     |
| **Neon**      | USD 0        | Ainda dentro do free tier        |
| **Vercel**    | USD 0        | Ainda dentro do hobby tier       |
| **Resend**    | USD 20       | Pro plan (50k emails/mês)        |
| **R2**        | USD 1        | ~20GB storage                    |
| **Sentry**    | USD 26       | Team plan (50k events/mês)       |
| **TOTAL**     | **USD 62**   | **~R$ 330/mês** (com margem 30%) |

---

## 9. Referências

- [REQUIREMENTS.md](REQUIREMENTS.md) - Requisitos funcionais e não-funcionais
- [BUSINESS_RULES.md](BUSINESS_RULES.md) - Regras de negócio consolidadas
- [ADR/](ADR/) - Architecture Decision Records (decisões técnicas)

### ADRs Relacionadas

1. [ADR-001: Por que Cloud Run?](ADR/001-why-cloud-run.md)
2. [ADR-002: Por que Neon PostgreSQL?](ADR/002-why-neon.md)
3. [ADR-003: Por que Cloudflare R2?](ADR/003-why-r2.md)
4. [ADR-004: Presigned URLs para Upload](ADR/004-presigned-urls.md)
5. [ADR-005: OIDC para Cloud Scheduler](ADR/005-oidc-scheduler.md)
6. [ADR-006: Service Layer Pattern](ADR/006-service-layer.md)
7. [ADR-007: Chaves Híbridas (BigInt + UUID)](ADR/007-hybrid-keys.md)
8. [ADR-008: Soft Delete Seletivo](ADR/008-soft-delete.md)
9. [ADR-009: Multitenancy Denormalizado](ADR/009-multitenancy.md)
10. [ADR-010: Tolerância Zero em Cálculos](ADR/010-tolerance-zero.md)
11. [ADR-016: Multi-tenancy Pragmático](ADR/016-pragmatic-multi-tenancy.md)

---

**Última atualização:** 1 de março de 2026
**Responsável:** Rafael
**Versão:** 1.1 - Atualizada para refletir estado real do código
**Próxima revisão:** Após deploy do MVP
