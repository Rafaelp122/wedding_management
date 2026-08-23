# Troubleshooting: Resolução de Locks e Timeouts de Conexão no Neon PostgreSQL

> **Sintoma:** O backend congela ou lança `OperationalError: connection timeout` durante migrações ou picos de carga.

---

## Soluções

1. **Verificar Conexões Ativas via Neon Dashboard / psql:**
   ```sql
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
   FROM pg_stat_activity
   WHERE state != 'idle' AND now() - pg_stat_activity.query_start > interval '5 seconds';
   ```
2. **Encerrar Conexões Presas:**
   ```sql
   SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = <PID_CONGELADO>;
   ```
3. **Ajustar Connection Pooling (PgBouncer):**
   Garanta que a string `DATABASE_URL` no `.env` utiliza o endpoint pooler do Neon (`-pooler` no hostname).
