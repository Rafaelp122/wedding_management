# ADR-004: Presigned URLs para Upload

**Status:** Aceito
**Data:** Janeiro 2025
**Decisor:** Rafael
**Contexto:** Método de upload de arquivos para R2/S3

---

## Contexto e Problema

Precisamos permitir upload de PDFs de contratos (2-5MB) com:

- **Performance:** Upload não deve travar o backend
- **Escalabilidade:** Suportar múltiplos uploads simultâneos
- **Segurança:** Apenas usuários autenticados podem fazer upload
- **Custo:** Minimizar uso de compute time no Cloud Run

**Alternativas:**

1. **Presigned URLs** (escolhido)
2. Upload via backend (multipart form)
3. Direct upload com API key no frontend

---

## Decisão

Escolhemos **Presigned URLs** para upload de arquivos.

---

## Justificativa

### Fluxo Presigned URL

```
┌──────────┐                          ┌─────────┐
│ Frontend │                          │ Backend │
└────┬─────┘                          └────┬────┘
     │                                     │
     │ 1. POST /api/contracts/upload-url  │
     │    {filename: "contrato.pdf"}      │
     ├────────────────────────────────────▶│
     │                                     │
     │                                     │ 2. Gera presigned URL
     │                                     │    - Validade: 15min
     │                                     │    - Permissão: PUT only
     │                                     │
     │◀────────────────────────────────────┤
     │ {upload_url, object_key}            │
     │                                     │
     │                                     │
     │ 3. PUT {upload_url}                 │
     │    Body: PDF file (2-5MB)           │
     ├──────────────────────────▶┌────────┴────────┐
     │                           │  Cloudflare R2  │
     │◀──────────────────────────│  (S3-compatible)│
     │ 200 OK                    └─────────────────┘
     │
     │ 4. POST /api/contracts/
     │    {object_key, ...metadata}
     ├────────────────────────────────────▶│
     │                                     │
     │                                     │ 5. Salva metadata no DB
     │                                     │    - object_key
     │                                     │    - status = PENDING
     │◀────────────────────────────────────┤
     │ {contract_id}                       │
```

---

### Comparação: Presigned URL vs Upload via Backend

| Aspecto            | Presigned URL         | Upload via Backend      |
| ------------------ | --------------------- | ----------------------- |
| **Tempo backend**  | ~50ms (gerar URL)     | ~5s (processar upload)  |
| **Compute cost**   | Mínimo                | Alto (5s × CPU)         |
| **Escalabilidade** | Ilimitado (R2)        | ~10 uploads simultâneos |
| **Complexidade**   | Média (2 requests)    | Baixa (1 request)       |
| **Segurança**      | Alta (URL temporária) | Alta (backend valida)   |

---

### Exemplo de Implementação

**Backend (gerar presigned URL):**

```python
# apps/logistics/views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_contract_upload_url(request):
    """
    Gera presigned URL para upload de contrato.

    Request: {"filename": "contrato.pdf"}
    Response: {"upload_url": "https://...", "object_key": "contracts/..."}
    """
    filename = request.data.get('filename')
    wedding_id = request.data.get('wedding_id')

    # Validar wedding pertence ao usuário
    if not Wedding.objects.filter(id=wedding_id, planner=request.user).exists():
        return Response({'error': 'Wedding not found'}, status=404)

    # Gerar presigned URL (15 minutos)
    result = ContractService.generate_upload_url(filename, wedding_id)

    return Response(result)
```

**Service layer:**

```python
# apps/logistics/services.py
import boto3
import uuid
from django.conf import settings

class ContractService:
    @staticmethod
    def generate_upload_url(filename: str, wedding_id: str) -> dict:
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY
        )

        # Gerar key único
        object_key = f'contracts/{wedding_id}/{uuid.uuid4()}/{filename}'

        # Gerar presigned URL para PUT
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

**Frontend (React):**

```typescript
// services/contractService.ts
async function uploadContract(file: File, weddingId: string) {
  // 1. Solicitar presigned URL
  const { upload_url, object_key } = await api.post("/contracts/upload-url", {
    filename: file.name,
    wedding_id: weddingId,
  });

  // 2. Upload direto para R2
  await axios.put(upload_url, file, {
    headers: {
      "Content-Type": "application/pdf",
    },
  });

  // 3. Criar registro de contrato
  const contract = await api.post("/contracts/", {
    object_key,
    wedding: weddingId,
    status: "PENDING",
  });

  return contract;
}
```

---

## Vantagens

### 1. Performance

**Backend:**

- Gera URL: ~50ms
- **NÃO** processa upload (economiza 5s)
- **NÃO** consome compute time do Cloud Run

**Frontend:**

- Upload direto para R2 (mais rápido)
- Progresso visual (XMLHttpRequest.upload.onprogress)

### 2. Escalabilidade

**Uploads simultâneos:**

- Presigned URL: Ilimitado (R2 escala automaticamente)
- Backend upload: ~10 simultâneos (limite de containers)

**Custo:**

```
100 uploads/dia × 5s cada = 500s compute/dia
Cloud Run: USD 0,0000024/vCPU-s × 500 = USD 0,0012/dia
Mês: USD 0,036 (~R$ 0,18)

Presigned URL: R$ 0 (R2 Class B operations grátis)
```

### 3. Segurança

**Presigned URL:**

- Expira em 15 minutos
- Permite **apenas** PUT (não GET/DELETE)
- Object key tem UUID (impossível adivinhar)

**Validação:**

```python
# Backend valida antes de gerar URL
if not Wedding.objects.filter(id=wedding_id, planner=request.user).exists():
    raise PermissionDenied()
```

---

## Trade-offs Aceitos

**❌ Complexidade (2 requests):**

- Frontend precisa fazer 2 chamadas:
  1. Backend: Gerar URL
  2. R2: Upload arquivo
- **Mitigação:** Abstrair em função `uploadContract()`

**❌ Validação de tipo no backend:**

- Backend não valida se arquivo é realmente PDF
- **Mitigação:**
  - ContentType='application/pdf' no presigned URL
  - Validação frontend (file.type === 'application/pdf')
  - Webhook R2 (futuro) para scan de vírus

---

## Consequências

### Positivas ✅

- **Performance:** Backend gasta 50ms (não 5s)
- **Escalabilidade:** Uploads ilimitados (R2 escala)
- **Custo:** R$ 0 em compute time
- **Segurança:** URL temporária (15min)

### Negativas ❌

- **Complexidade:** 2 requests (vs 1)
- **Validação limitada:** Backend não vê o arquivo

### Neutras ⚠️

- Requer configuração de CORS no R2

---

## Monitoramento

**Métricas:**

- Tempo médio de upload (meta: < 3s para 2MB)
- Taxa de falha (meta: < 1%)
- URLs expiradas (meta: < 0,5%)

**Gatilhos de revisão:**

- Upload time P95 > 10s
- Taxa de falha > 5%
- Complexidade frontend inaceitável

---

## Referências

- [AWS S3 Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
- [boto3 generate_presigned_url](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_url.html)
- [ADR-003: Cloudflare R2](003-why-r2.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)

---

**Última atualização:** 8 de fevereiro de 2026
