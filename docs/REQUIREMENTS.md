# Levantamento de Requisitos - Wedding Management System

## Versão 4.1

---

## 1. Requisitos Funcionais (RF)

### Módulo de Casamentos e Multitenancy

**RF01 (Isolamento de Dados):** O sistema deve implementar multitenancy rigoroso. Um Planner (Usuário) só pode visualizar e manipular dados de seus próprios casamentos e fornecedores.

**RF02 (Gestão de Permissões):** O sistema deve implementar 2 níveis de acesso iniciais:

- **Owner** (Planner): CRUD total sobre seus casamentos, itens e fornecedores
- **Viewer** (Noivos): Read-Only em cronograma, financeiro e contratos de seu casamento

> **Nota:** Níveis adicionais (Editor/Auditor) serão implementados em versões futuras conforme demanda real de usuários.

---

### Módulo Financeiro e Orçamentário

**RF03 (Categorias Dinâmicas):** O sistema deve permitir que planners criem suas próprias categorias de orçamento. Categorias com itens ativos vinculados não podem ser deletadas, apenas arquivadas (soft delete).

**RF04 (Integridade de Fluxo Financeiro):** O sistema deve validar que a soma das parcelas (Installments) seja igual ao `actual_cost` do item, com tolerância de arredondamento de até R$ 0,02 (dois centavos) para lidar com divisões não exatas.

```python
# Exemplo de validação usando Decimal (obrigatório para operações monetárias)
from decimal import Decimal

tolerance = Decimal('0.02')
total_installments = sum(Decimal(str(i['amount'])) for i in installments)
diff = abs(actual_cost - total_installments)

if diff > tolerance:
    raise ValidationError(
        f"Diferença de R$ {diff} excede tolerância permitida de R$ 0.02"
    )
```

> **Regra de Ouro:** Toda operação monetária deve usar `DecimalField` no Django, nunca `FloatField`, para evitar erros de precisão binária (0.1 + 0.2 ≠ 0.3 em float).

**RF05 (Automação de Status):** O sistema deve executar diariamente (via Django management command + cron job) a atualização de parcelas vencidas para o status `OVERDUE`. A task deve:

- Rodar às 00:00 UTC via Cloud Run Scheduler
- Usar autenticação OIDC (OpenID Connect) para validar que apenas o Cloud Scheduler pode invocar o endpoint
- Registrar execuções (sucesso/falha) em log estruturado
- Enviar alerta por email ao administrador em caso de falha persistente

```bash
# Configuração com OIDC Token (segurança nível sênior)
gcloud scheduler jobs create http update-overdue-installments \
  --schedule="0 0 * * *" \
  --uri="https://wedding-api-xxx.a.run.app/api/tasks/update-overdue/" \
  --http-method=POST \
  --oidc-service-account-email="scheduler@project-id.iam.gserviceaccount.com" \
  --oidc-token-audience="https://wedding-api-xxx.a.run.app"
```

```python
# Validação OIDC no backend
from google.auth.transport import requests
from google.oauth2 import id_token

def validate_scheduler_request(request):
    """Valida que requisição veio do Cloud Scheduler via OIDC"""
    token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    claim = id_token.verify_oauth2_token(token, requests.Request(), settings.CLOUD_RUN_SERVICE_URL)
    if claim['email'] != settings.SCHEDULER_SERVICE_ACCOUNT:
        raise PermissionDenied('Unauthorized service account')
```

> **Justificativa técnica:** OIDC elimina necessidade de gerenciar secrets manualmente e demonstra conhecimento de Service-to-Service authentication no GCP.

**RF06 (Saúde Financeira):** O sistema deve calcular em tempo real a saúde financeira do evento (Gasto Real vs. Estimado) por categoria e exibir em dashboard visual.

---

### Módulo de Logística e Fornecedores

**RF07 (Normalização de Itens):** Itens de logística devem ser vinculados a uma categoria de orçamento, herdando a relação com o casamento via cadeia: `Item → BudgetCategory → Budget → Wedding`.

**RF07.1 (Validação de Integridade):** O sistema deve validar que a `BudgetCategory` pertence ao mesmo `Wedding` do `Budget` ao qual o `Item` está sendo vinculado, prevenindo cross-contamination entre eventos.

**RF08 (Gestão de Status de Itens):** Atualização de status de aquisição independente por item com estados: `Orçado`, `Contratado`, `Entregue`, `Cancelado`.

**RF09 (Notas de Fornecedores):** O sistema deve permitir que planners mantenham notas internas sobre fornecedores, incluindo estatísticas simples de entregas:

- Quantidade de entregas no prazo
- Quantidade de entregas atrasadas
- Campo de texto livre para observações

> **Nota:** Sistema de rating público (estrelas) será implementado apenas em V2.0 após acúmulo de volume estatístico significativo.

---

### Módulo Jurídico (Gestão de Contratos)

**RF10 (Contratos Externos N:M):** O sistema deve permitir upload de PDFs de contratos externos para Cloudflare R2 via **presigned URLs**, onde um único documento pode reger múltiplos itens de um mesmo fornecedor (Relação N:M).

**Fluxo de Upload Otimizado:**

1. Frontend solicita presigned URL ao backend
2. Backend gera URL assinada válida por 15 minutos (sem processar o arquivo)
3. Frontend faz upload DIRETO ao R2 via PUT request
4. Frontend confirma ao backend que upload foi concluído

```python
# Exemplo de geração de presigned URL
import boto3

def generate_upload_url(filename: str, user_id: int):
    s3_client = boto3.client('s3', endpoint_url=settings.R2_ENDPOINT_URL)
    object_key = f'contracts/{user_id}/{uuid.uuid4()}/{filename}'

    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': settings.R2_BUCKET, 'Key': object_key},
        ExpiresIn=900  # 15 minutos
    )
    return {'upload_url': presigned_url, 'object_key': object_key}
```

> **Vantagem:** Backend gasta ~50ms gerando URL ao invés de 5s processando upload de 50MB, economizando compute time do Cloud Run e permitindo uploads simultâneos escaláveis.

**RF11 (Metadados Contratuais):** Contratos devem armazenar:

- Data de validade
- Partes envolvidas (Planner, Fornecedor, Noivos)
- Status simples: `Pendente` ou `Assinado`
- URL do arquivo no Cloudflare R2
- Referência aos itens cobertos

**RF12 (Controle de Assinatura Simplificado):** O sistema deve permitir marcar manualmente o status de assinatura do contrato como `Assinado` após upload do PDF final assinado.

> **Nota:** Assinatura digital via DocuSign/Adobe Sign será implementada apenas em V2.0 devido à complexidade e custo de integração.

**RF13 (Alertas de Vencimento):** O sistema deve disparar alertas automáticos via email para:

- Contratos com vencimento em até 30 dias
- Contratos pendentes de assinatura por mais de 15 dias

---

### Módulo de Cronograma e Notificações

**RF14 (Exportação de Calendário):** O sistema deve gerar um link de exportação `.ics` (iCal) por casamento, permitindo sincronização unidirecional com Google Calendar, Outlook e Apple Calendar.

**RF15 (Notificações Básicas):** Alertas críticos (parcelas atrasadas, prazos contratuais, marcos do cronograma) devem ser enviados via:

- **Email (Resend):** Notificações imediatas (obrigatório)
- **In-App:** Badge de notificações atualizado ao:
  - Fazer login
  - Navegar entre páginas
  - Clicar manualmente em "Atualizar notificações"
- **WhatsApp:** Módulo Premium futuro (V2.0), custo repassado ao usuário

> **Justificativa técnica:** Polling a cada 30s geraria 144k requests/dia inúteis. Refresh manual + email cobre 95% dos casos sem overhead de infraestrutura.

---

## 2. Requisitos Não Funcionais (RNF)

**RNF01 (Arquitetura Headless):** Backend API REST (Django REST Framework) deployado no Google Cloud Run e Frontend SPA (React) deployado no Vercel, com desacoplamento total.

**RNF02 (Segurança):**

- Autenticação JWT Stateless com tokens expirando em 24h
- Refresh tokens válidos por 7 dias
- Rate limiting: 100 requests/minuto por IP via `django-ratelimit`
- HTTPS obrigatório (fornecido automaticamente por Cloud Run e Vercel)

**RNF03 (Arquitetura de Código - Service Layer):**

- Views/Serializers: validação de entrada/saída HTTP apenas
- Services: lógica de negócio (ex: `ItemService.create_with_installments()`)
- Models: validações de integridade e propriedades calculadas
- **Toda lógica financeira deve usar `Decimal`, nunca `float`**

**RNF04 (Soft Delete Seletivo):**
Implementar soft delete apenas nos modelos críticos:

- `Wedding`, `BudgetCategory`, `Item`, `Contract`, `Vendor`
- Dados deletados movem para `is_deleted=True` e mantidos por 30 dias
- **EXCLUSÕES:** Parcelas pagas (`Installment` com status `PAID`) e logs de sistema (imutáveis)

**RNF05 (Chaves Primárias - Estratégia Híbrida):**

- **Interno (JOINs):** `BigAutoField` sequencial (primary key)
- **Público (API):** `UUIDField` (UUID4) em campo separado com índice único
- **Vantagem:** Performance de inteiros em queries internas + segurança de UUIDs expostos

```python
# Implementação base
import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

**RNF06 (Performance):**

- API deve responder requisições GET em < 500ms (p95) com até 50 itens
- Paginação obrigatória: máximo 50 itens/página
- Queries N+1 detectadas via `nplusone` (modo strict em desenvolvimento) e corrigidas antes do merge
- Meta agressiva de < 200ms será perseguida via otimizações incrementais

**RNF07 (Documentação Automática):** API autodocumentada via `drf-spectacular` (OpenAPI 3.0) com exemplos de request/response e códigos de erro.

**RNF08 (Interface Mobile-First):** UI responsiva otimizada para smartphones (80% dos acessos esperados).

**RNF09 (Continuidade Básica):**

- Backups diários automáticos do Neon PostgreSQL (inclusos no free tier)
- Retenção: 7 dias
- Testes de restauração: a cada 3 meses
- RTO (Recovery Time Objective): < 8 horas

**RNF10 (Observabilidade Simplificada):**

- **Sentry** para captura de erros 5xx (free tier: 5k eventos/mês)
- Logs estruturados em JSON via `python-json-logger`
- Cloud Run Logs integrado nativamente
- **SEM Prometheus/Grafana** até 500+ usuários ativos

---

## 3. Premissas e Restrições

**P01 (Infraestrutura):** Hospedagem em stack serverless gratuita:

- **Backend:** Google Cloud Run (free tier: 2M requests/mês + 360k GB-s compute)
- **Frontend:** Vercel (Hobby plan + CDN global)
- **Database:** Neon PostgreSQL Serverless (3GB storage + 191h compute/mês)
- **Storage:** Cloudflare R2 (10GB + zero egress costs)
- **Email:** Resend (3k emails/mês)

**P02:** MVP em Português (pt-BR) apenas. Internacionalização em V2.0.

**P03:** Sem integração com gateways de pagamento no MVP.

**P04 (Cold Start):** Cloud Run pode ter cold start de 2-3s após inatividade. Aceitável para portfólio.

**R01:** Desenvolvimento: **6 meses com 1 desenvolvedor full-stack**.

**R02:** Custos de infraestrutura: **USD 0/mês** (stack gratuita dentro dos limites de free tier).

**R03 (Cobertura de Testes - Estratificada):**

- **Service Layer Financeira:** 100% de cobertura obrigatória
  - `ItemService`, `InstallmentService`, `BudgetService`
  - Inclui todos os edge cases de arredondamento e validação de parcelas
- **Lógica de Multitenancy:** 100% de cobertura obrigatória
  - Filtros de queryset, permissions, validações de ownership
- **Models:** 80% (validações, properties calculadas, métodos de negócio)
- **Serializers/Views:** 60% (apenas casos críticos e validações complexas)
- **Cobertura Global Mínima:** 75%

> **Justificativa:** Para um sistema financeiro, 100% de cobertura na lógica monetária é inegociável. Bugs em cálculos de parcelas podem causar perda de confiança e disputas legais.

---

## 4. Critérios de Aceitação (Definição de Pronto)

Uma funcionalidade só será considerada completa quando:

1. Possuir testes unitários conforme estratificação definida em R03
2. Estar documentada na OpenAPI com pelo menos 1 exemplo funcional
3. Passar por checklist de auto-revisão (qualidade de código, segurança básica)
4. Funcionar corretamente em dispositivo móvel real (teste manual obrigatório)
5. Estar deployada no Cloud Run (staging) + Vercel (preview deployment)

---

## 5. Roadmap de Priorização (MoSCoW Realista)

### Must Have (MVP - 4 meses)

**As 3 funcionalidades que fazem o Planner largar o Excel:**

1. **RF01, RF02** (Multitenancy + Permissões básicas: Owner/Viewer)
2. **RF03, RF04, RF06** (Orçamento com validação financeira + Dashboard de saúde)
3. **RF07, RF07.1, RF08** (Gestão de itens com status + vínculo a fornecedores)

**Infraestrutura mínima:**

- RNF01, RNF02, RNF03, RNF04, RNF05, RNF06, RNF07

**Total estimado:** 16 semanas de desenvolvimento

---

### Should Have (V1.1 - +2 meses após MVP)

4. **RF05** (Automação de status via Cloud Run Scheduler + OIDC)
5. **RF10, RF11, RF12** (Upload de contratos via presigned URLs + metadados)
6. **RF14** (Exportação .ics para calendário)
7. **RF09** (Notas internas de fornecedores + estatísticas)
8. **RNF09, RNF10** (Backups + Sentry)

**Total estimado:** 8 semanas adicionais

---

### Could Have (V2.0 - +3 meses após V1.1)

9. **RF13** (Alertas automáticos de vencimento)
10. **RF15** (WhatsApp Premium via API oficial)
11. **RF02** (Níveis adicionais: Editor/Auditor)
12. **RF09** (Rating público de fornecedores com estrelas)
13. **Assinatura digital via DocuSign**

---

### Won't Have (Fora de escopo)

- ❌ Auditoria imutável completa
- ❌ Geração automática de contratos via templates
- ❌ Marketplace de fornecedores
- ❌ Gateway de pagamento integrado
- ❌ Sincronização bidirecional com Google Calendar

---

## 6. Decisões Técnicas Documentadas

### Por que Cloud Run ao invés de Railway/Heroku?

- **Free tier generoso:** 2M requests/mês vs créditos limitados
- **Escala para zero:** Sem uso = custo zero
- **Docker nativo:** Aplicação já containerizada
- **Trade-off:** Cold start de 2-3s (aceitável para portfólio)

### Por que Neon ao invés de Railway PostgreSQL?

- **3GB de storage** vs 1GB
- **Hibernação automática:** Economiza compute time
- **Branching de banco:** Testa migrations sem afetar produção
- **Backups inclusos:** 7 dias de retenção

### Por que Cloudflare R2 ao invés de AWS S3?

- **10GB grátis** vs 5GB
- **Zero egress costs:** Downloads gratuitos (S3 cobra USD 0.09/GB)
- **S3-compatible API:** Usa boto3 normalmente

### Por que Resend ao invés de AWS SES?

- **3k emails/mês grátis** vs USD 0.10 por 1k
- **API ultra simples:** 5 linhas de código
- **SPF/DKIM automático:** Sem configuração DNS manual

### Por que BigInt + UUID4 ao invés de apenas UUID4?

- **Performance:** JOINs com inteiros são 3x mais rápidos
- **Segurança:** IDs sequenciais não vazam para API
- **Flexibilidade:** UUID facilita merges futuros
- **Trade-off:** Lookup por UUID adiciona ~1ms (negligível)

### Por que OIDC ao invés de simples Authorization header?

- **Segurança:** Tokens assinados pelo GCP e validáveis criptograficamente
- **Zero secrets:** Não precisa gerenciar/rotacionar senhas
- **Identity-Aware:** Valida service account específico
- **Auditável:** Logs mostram qual SA fez a requisição

### Por que Presigned URLs ao invés de upload via backend?

- **Performance:** Backend gasta 50ms ao invés de 5s por upload
- **Custo:** Não consome compute time do Cloud Run
- **Escalabilidade:** 100 uploads simultâneos não sobrecarregam backend
- **Segurança:** URL expira em 15min

### Por que refresh manual ao invés de polling/WebSocket?

- **Polling:** 50 usuários × 2 req/min = 144k requests/dia inúteis
- **WebSocket:** Requer servidor stateful (USD 50/mês)
- **Email + refresh:** Cobre 95% dos casos sem complexidade

---

## 7. Métricas de Sucesso do MVP

O MVP será considerado bem-sucedido se:

1. **5 planners reais** usarem o sistema por pelo menos 30 dias
2. **Redução de 50%** no tempo gasto com controle financeiro (vs Excel)
3. **Zero perda de dados** críticos (validado via testes de backup)
4. **< 5 bugs críticos** reportados no primeiro mês
5. **Pelo menos 1 planner** demonstrar interesse em pagar por features premium

---

## 8. Arquitetura de Deploy

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   GitHub    │────────▶│    Vercel    │────────▶│   CDN Edge  │
│(Repositório)│         │  (Frontend)  │         │  (Global)   │
└─────────────┘         └──────────────┘         └─────────────┘
       │                        │
       │                        │ API Calls (HTTPS)
       │                        ▼
       │                ┌──────────────┐
       │                │  Cloud Run   │
       └───────────────▶│  (Backend)   │
                        └──────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
            ┌─────────────┐ ┌─────────┐ ┌─────────┐
            │    Neon     │ │   R2    │ │ Resend  │
            │ PostgreSQL  │ │ (PDFs)  │ │ (Email) │
            └─────────────┘ └─────────┘ └─────────┘
```

---

**Última atualização:** 3 de fevereiro de 2026
**Responsável:** Rafael
**Versão:** 4.1
**Próxima revisão:** Após conclusão do MVP (4 meses)
