# Troubleshooting: Falhas em Presigned URLs e Upload no Cloudflare R2

> **Sintoma:** Upload de arquivos de contrato falha com HTTP `403 SignatureDoesNotMatch` ou `CORS Error`.

---

## Soluções

1. **Verificar Configuração de CORS no Bucket Cloudflare R2:**
   Assegure-se de que a origem do frontend (`http://localhost:5173`) está cadastrada nas regras CORS do bucket:
   ```json
   [
     {
       "AllowedOrigins": ["http://localhost:5173"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
       "AllowedHeaders": ["*"]
     }
   ]
   ```
2. **Verificar Relógio do Servidor:**
   Presigned URLs expiram rapidamente (ADR-004). Garanta que a hora do sistema esteja sincronizada via NTP (`ntpdate -u pool.ntp.org`).
