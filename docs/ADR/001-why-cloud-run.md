# ADR-001: Por que Google Cloud Run?

**Status:** Aceito
**Data:** Janeiro 2025
**Decisor:** Rafael
**Contexto:** Escolha de plataforma de deploy para backend Django

---

## Contexto e Problema

Precisamos de uma plataforma serverless para hospedar o backend Django REST Framework que:

- Escale automaticamente de acordo com a demanda
- Tenha custo zero ou muito baixo no MVP (baixo tráfego)
- Suporte Python/Django nativamente
- Ofereça HTTPS automático
- Integre facilmente com outros serviços do GCP

**Alternativas consideradas:**

1. **Google Cloud Run** (escolhido)
2. AWS Lambda + API Gateway
3. Railway
4. Heroku
5. DigitalOcean App Platform

---

## Decisão

Escolhemos **Google Cloud Run** como plataforma de deploy do backend.

---

## Justificativa

### Vantagens do Cloud Run

**1. Free Tier Generoso:**

- 2 milhões de requisições/mês
- 360 mil GB-segundos de memória
- 180 mil vCPU-segundos
- **Estimativa MVP:** 500k req/mês = 25% do limite (R$ 0/mês)

**2. Serverless Verdadeiro:**

- Scale-to-zero: Nenhum custo quando não há tráfego
- Cold start ~2s (aceitável para MVP)
- Auto-scaling: 0 → 100 instâncias automaticamente

**3. Container-based:**

```dockerfile
FROM python:3.12-slim
# Dockerfile padrão, sem vendor lock-in
COPY . /app
CMD gunicorn config.wsgi:application
```

- Portabilidade: Mesmo Dockerfile roda em qualquer lugar
- Sem "magic config" proprietário (vs Heroku buildpacks)

**4. Integração Nativa GCP:**

- Cloud Scheduler (OIDC auth sem secrets)
- Cloud Logging (logs estruturados JSON)
- Secret Manager (variáveis de ambiente seguras)
- Cloud Build (CI/CD nativo)

**5. HTTPS Automático:**

- TLS gerenciado pelo Google
- Certificados automáticos
- Zero configuração

---

### Comparação com Alternativas

| Feature              | Cloud Run  | Lambda     | Railway     | Heroku      |
| -------------------- | ---------- | ---------- | ----------- | ----------- |
| **Free Tier**        | 2M req/mês | 1M req/mês | 500h/mês    | 1000h/mês   |
| **Cold Start**       | ~2s        | ~3s        | 0s (always) | 0s (always) |
| **Scale-to-zero**    | ✅ Sim     | ✅ Sim     | ❌ Não      | ❌ Não      |
| **Container native** | ✅ Sim     | ⚠️ Parcial | ✅ Sim      | ❌ Não      |
| **Vendor lock-in**   | ⚠️ Médio   | ❌ Alto    | ⚠️ Médio    | ❌ Alto     |
| **OIDC support**     | ✅ Nativo  | ⚠️ Manual  | ❌ Não      | ❌ Não      |
| **PostgreSQL**       | ⚠️ Externo | ⚠️ RDS     | ✅ Incluso  | ✅ Incluso  |

---

### Trade-offs Aceitos

**❌ Cold Start (2-3s):**

- **Impacto:** Primeira requisição após inatividade é lenta
- **Mitigação:** Aceitável para MVP (não é sistema crítico)
- **Solução futura:** Min instances = 1 (USD 5/mês)

**❌ PostgreSQL Separado:**

- Cloud Run não oferece database gerenciado
- **Solução:** Neon PostgreSQL (free tier 3GB)
- **Vantagem:** Banco independente = mais flexibilidade

**❌ Curva de Aprendizado GCP:**

- Ferramentas menos conhecidas que AWS
- **Mitigação:** Documentação excelente, comunidade ativa

---

## Configuração de Exemplo

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
      timeoutSeconds: 60
      containerConcurrency: 80
```

**Deploy:**

```bash
gcloud run deploy wedding-api \
  --image gcr.io/PROJECT_ID/wedding-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1
```

---

## Consequências

### Positivas ✅

1. **Custo zero no MVP** (dentro do free tier)
2. **Escalabilidade automática** (0 → 100 instâncias)
3. **Integração OIDC** para Cloud Scheduler (zero secrets)
4. **Logs estruturados** nativos (Cloud Logging)
5. **Portabilidade** (Dockerfile padrão)

### Negativas ❌

1. **Cold start** de 2-3s após inatividade
2. **Vendor lock-in médio** (OIDC, Cloud Scheduler)
3. **Requer setup externo** para PostgreSQL
4. **Complexidade inicial** (IAM, Service Accounts)

### Neutras ⚠️

1. Requer conhecimento de GCP (curva de aprendizado)
2. Free tier pode não ser suficiente em escala (previsível)

---

## Monitoramento

**Métricas a observar:**

- Requisições/mês (limite: 2M)
- Cold start frequency (meta: < 10% das requisições)
- Latência P95 (meta: < 500ms)
- Custo mensal (meta: R$ 0 no MVP)

**Gatilhos de revisão:**

- Custo mensal > R$ 50
- Cold start > 20% das requisições
- Latência P95 > 1s

---

## Referências

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Container runtime contract](https://cloud.google.com/run/docs/container-contract)
- [ARCHITECTURE.md](../ARCHITECTURE.md)

---

**Última atualização:** 8 de fevereiro de 2026
**Revisão:** Após 3 meses de MVP em produção
