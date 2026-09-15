# ADR-005: OIDC para Cloud Scheduler

> **Categoria:** Decisões de Arquitetura (ADR)
> **Status:** 🟢 Vigente
> **Data:** Janeiro 2025
> **Decisor:** Rafael
> **Relacionados:** [ADR-001: Cloud Run](001-why-cloud-run.md) · [ADR-017: Async Task Infrastructure](017-async-task-infrastructure.md) · [ADR-025: Terraform & GitOps](025-terraform-iac-architecture.md)

---

## 1. Contexto e Problema

Cloud Scheduler precisa chamar endpoint `/api/tasks/check-overdue/` diariamente para atualizar parcelas vencidas.

**Requisitos:**

- Endpoint protegido (não público)
- Zero secrets no código (sem API keys)
- Auditável (identificar qual service fez request)
- Sem rotação manual de credenciais

**Alternativas:**

1. **OIDC (OpenID Connect)** (escolhido)
2. API Key no header (Authorization: Bearer <secret>)
3. IP Whitelist (permitir apenas IPs do GCP)
4. Sem autenticação (público)

---

## 2. Decisão

Escolhemos **OIDC (OpenID Connect)** para autenticar Cloud Scheduler.

---

## 3. Justificativa

### Comparação de Métodos

| Aspecto          | OIDC                | API Key      | IP Whitelist |
| ---------------- | ------------------- | ------------ | ------------ |
| **Zero secrets** | :material-check-circle: Sim              | :material-close-circle: Não (key) | :material-alert: Parcial   |
| **Auditável**    | :material-check-circle: Email do SA      | :material-close-circle: Não       | :material-close-circle: Apenas IP |
| **Rotação**      | :material-check-circle: Automática (GCP) | :material-close-circle: Manual    | N/A          |
| **Vendor lock**  | :material-alert: GCP-specific     | :material-check-circle: Portável  | :material-check-circle: Portável  |

---

### Como Funciona OIDC?

**1. Cloud Scheduler gera token:**

```
Cloud Scheduler (Service Account: scheduler@project.iam)
   ↓ GCP assina JWT token criptograficamente
   ↓ Token contém: email, audience, exp
POST /api/tasks/check-overdue/
Authorization: Bearer <OIDC_TOKEN>
```

**2. Backend valida token:**

```python
from google.oauth2 import id_token
from google.auth.transport import requests

def require_oidc_auth(view_func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = auth_header.replace('Bearer ', '')

        # Valida assinatura criptográfica do GCP
        claim = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.CLOUD_RUN_SERVICE_URL  # Audience esperado
        )

        # Valida service account específico
        if claim['email'] != 'scheduler@project.iam.gserviceaccount.com':
            raise PermissionDenied('Unauthorized service account')

        return view_func(request, *args, **kwargs)

    return wrapper
```

**3. Token contém:**

```json
{
  "iss": "https://accounts.google.com",
  "aud": "https://wedding-api.run.app",
  "email": "scheduler@project.iam.gserviceaccount.com",
  "exp": 1706810400,
  "iat": 1706806800
}
```

---

### Vantagens do OIDC

**1. Zero Secrets:**

```python
# API Key (precisa guardar secret)
API_KEY = os.getenv('SCHEDULER_API_KEY')  # Onde guardar? .env? Secret Manager?

# OIDC (zero secrets no código)
# GCP assina token automaticamente
```

**2. Auditável:**

```python
# Logs mostram QUAL service account fez request
logger.info(
    "overdue_task_executed",
    service_account=claim['email'],
    updated_count=42
)
```

**3. Rotação Automática:**

- GCP rotaciona chaves criptográficas automaticamente
- Sem intervenção manual
- Zero downtime

**4. Validação Criptográfica:**

- Token assinado com chave privada do GCP
- Backend valida com chave pública (Google JWKS)
- Impossível falsificar

---

### Configuração de Integração

**1. Criar Service Account:**

```bash
gcloud iam service-accounts create scheduler-sa \
  --display-name="Cloud Scheduler Service Account"
```

**2. Configurar Cloud Scheduler:**

```bash
gcloud scheduler jobs create http check-overdue \
  --schedule="0 0 * * *" \
  --uri="https://wedding-api.run.app/api/tasks/check-overdue/" \
  --http-method=POST \
  --oidc-service-account-email="scheduler-sa@project.iam.gserviceaccount.com" \
  --oidc-token-audience="https://wedding-api.run.app"
```

**3. Backend (Django):**

```python
# apps/core/authentication.py
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.exceptions import AuthenticationFailed

def authenticate_scheduler_oidc(request):
    """
    Valida token OIDC do Cloud Scheduler.

    Raises:
        AuthenticationFailed: Token inválido ou expirado
    """
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        raise AuthenticationFailed('Missing Bearer token')

    token = auth_header.split(' ')[1]

    try:
        # Valida token com chaves públicas do Google
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=settings.CLOUD_RUN_URL
        )

        # Valida service account email
        expected_email = settings.SCHEDULER_SERVICE_ACCOUNT_EMAIL
        if id_info.get('email') != expected_email:
            raise AuthenticationFailed(f'Invalid service account: {id_info.get("email")}')

        return id_info

    except ValueError as e:
        raise AuthenticationFailed(f'Invalid token: {str(e)}')

# apps/tasks/views.py
@api_view(['POST'])
def check_overdue_tasks(request):
    """Endpoint chamado pelo Cloud Scheduler para atualizar parcelas."""
    # Valida OIDC
    authenticate_scheduler_oidc(request)

    # Executa task
    overdue_count = InstallmentService.update_overdue_installments()

    return Response({'overdue_count': overdue_count})
```

---

### Trade-offs Aceitos

**:material-close-circle: Vendor Lock-in (GCP):**

- OIDC específico do GCP
- Migrar para AWS/Azure requer reescrever autenticação
- **Mitigação:** Lógica isolada em decorator (fácil substituir)

**:material-close-circle: Complexidade Setup:**

- Requer criar Service Account
- Configurar IAM roles
- **Mitigação:** Setup único (não recorrente)

---

## 4. Consequências

### Positivas :material-check-circle:

- **Zero secrets** no código
- **Auditável:** Logs mostram email do service account
- **Rotação automática:** GCP gerencia chaves
- **Segurança:** Validação criptográfica

### Negativas :material-close-circle:

- **Vendor lock-in:** GCP-specific
- **Complexidade:** Setup IAM/Service Accounts

### Neutras :material-alert:

- Alternativas (API key) são mais simples, mas menos seguras

---

### Monitoramento e Alertas

**Métricas:**

- Taxa de sucesso OIDC validation (meta: 100%)
- Tentativas não autorizadas (meta: 0)

**Alertas:**

- Falha na validação OIDC → Slack
- Service account não autorizado → Sentry

**Gatilhos de revisão:**

- Taxa de falha > 1%
- Necessidade de migrar para AWS/Azure

---

## 5. Referências

- [Google OIDC Documentation](https://cloud.google.com/run/docs/authenticating/service-to-service)
- [Cloud Scheduler Authentication](https://cloud.google.com/scheduler/docs/http-target-auth)
- [BUSINESS_RULES.md (BR-FUT05)](../domains/core-domain.md)
- [ARCHITECTURE.md](../concepts/system-overview.md)

---

**Última atualização:** 8 de fevereiro de 2026
