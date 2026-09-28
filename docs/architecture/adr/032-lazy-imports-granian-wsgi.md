# ADR-032: Lazy Imports e Granian WSGI para Cold Start

> **Categoria:** Decisões de Arquitetura (ADR)
> **Status:** 🟢 Vigente
> **Data:** Setembro 2026
> **Decisor:** Rafael
> **Relacionados:** [ADR-001: Cloud Run](001-why-cloud-run.md) · [ADR-017: Async Tasks](017-async-task-infrastructure.md) · [ADR-020: StorageService](020-storage-service-abstraction.md) · [ADR-030: Rich Domain Model](030-rich-domain-model-service-layer.md)

---

## 1. Contexto e Problema

Backend Django Ninja sync no Cloud Run (`min 0`, 1vCPU/512Mi, `max_concurrency 15`) com cold start dominado por imports pesados (`reportlab`, `openpyxl`, `boto3/botocore`, `google-auth`) puxados no boot via `config/api.py` mesmo em requests que nunca geram arquivo. Servidor atual `gunicorn gthread 1x4` subutiliza a concorrência contratada.

Alternativas consideradas:

1. **Lazy imports manuais + Granian WSGI (escolhido)**
2. Manter Gunicorn e subir `min instances = 1`
3. Aguardar Python 3.15 (PEP 810 `lazy import`) sem fazer nada agora
4. Migrar para ASGI puro agora

---

## 2. Decisão

Trilha A: mover `reportlab`, `openpyxl`, `boto3` e `google-auth` para imports locais sob demanda nos services que realmente usam. Trilha B: trocar runtime de produção para Granian em modo WSGI com 15 blocking threads (casando 1:1 com a concorrência de 15 do Cloud Run), ativar `PYTHONOPTIMIZE=1` no build e congelar objetos permanentes de boot via `gc.freeze()` em `config/wsgi.py`, mantendo `config/wsgi.py` sem adotar ASGI (codebase sem `async def`).

---

## 3. Justificativa

Lazy ataca `1.2-1.4s` do boot; Granian ataca `0.2-0.4s` + p99 sob concorrência (parser Rust, threads eficientes em 512Mi com 15 threads atendendo a concorrência sem head-of-line blocking). `gc.freeze()` congela mais de 150 mil objetos de metadados do Django no boot, eliminando varreduras desnecessárias de GC em todas as requisições subsequentes. Python 3.15 ajuda no futuro mas exige upgrade de runtime + validação Django e não dispensa a auditoria feita aqui — o trabalho manual vira `lazy import` no topo quando migrarmos. ASGI descartado agora: sem views async, ganho marginal e risco de `CONN_MAX_AGE` + threadpool.

---

## 4. Consequências

Positivas: cold start menor sem custo recorrente, mesma instância atende mais concorrência, um servidor só para WSGI/ASGI futuro.

Negativas: imports locais exigem disciplina (novos SDKs pesados devem nascer lazy); Granian tem ecossistema menor que Gunicorn (rollback preservado por 1 release).

Monitoramento: p95 `/api/v1/*`, frequência de cold start, memória max, `instance_count`, `5xx`. Gatilho de revisão: p95 acima do baseline por 7 dias ou qualquer OOM.

---

## 5. Referências

- [ADR-001: Cloud Run](001-why-cloud-run.md)
- [Granian benchmarks](https://github.com/emmett-framework/granian/blob/master/benchmarks/vs.md)
- [PEP 810 — lazy imports](https://peps.python.org/pep-0810/)
- Plano de implementação: `docs/superpowers/plans/2026-09-26-lazy-imports-granian.md` (excluído do site)
