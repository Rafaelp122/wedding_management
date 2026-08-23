# Visão de Arquitetura: Fluxo de Upload de Contrato PDF (Cloudflare R2)

> **Módulo:** [logistics-domain](../domains/logistics-domain.md) | [finances-domain](../domains/finances-domain.md)
> **Código:** `frontend/src/features/logistics/components/contracts/ContractUploadDialog.tsx`, `frontend/src/features/logistics/hooks/useContractUploadForm.ts`, `backend/apps/logistics/services/contract_service.py`

---

## Visão Geral do Fluxo

O upload de contratos em PDF utiliza o armazenamento de objetos no **Cloudflare R2** via URLs pré-assinadas (*Presigned URLs*), evitando o tráfego pesado de arquivos binários no servidor de aplicação Python Cloud Run (ADR-004 / ADR-020).

Ao enviar um contrato, a plataforma orquestra automaticamente:
1. Geração de URL segura de upload (`PUT`).
2. Envio direto do arquivo do navegador para o Cloudflare R2.
3. Criação da entidade `Contract` no banco de dados.
4. Criação da despesa vinculada (`Expense` + `Installment`) no módulo financeiro.
5. Cadastro inicial dos itens/serviços contratados (`Item`).

---

## Sequência de Execução (Diagrama de Fluxo)

```text
[Navegador / React]              [Backend Django Ninja]           [Cloudflare R2 Storage]
        |                                   |                                |
        | 1. Solicita Presigned Upload URL  |                                |
        |---------------------------------->|                                |
        |                                   | Generates S3 Presigned PUT URL |
        | 2. Retorna upload_url + key       |                                |
        |<----------------------------------|                                |
        |                                                                    |
        | 3. HTTP PUT (Binary Upload Direct)                                 |
        |------------------------------------------------------------------->|
        | 4. HTTP 200 OK (Upload Concluído)                                  |
        |<-------------------------------------------------------------------|
        |                                                                    |
        | 5. Criação Completa (POST /contracts/full com key do R2 + dados)   |
        |---------------------------------->|                                |
        |                                   | Valida integridade e inicia    |
        |                                   | transação atômica DB (DB TX):   |
        |                                   |  - Salva Contract (com R2 key) |
        |                                   |  - Salva Expense + Installment |
        |                                   |  - Salva Itens contratados     |
        | 6. HTTP 201 Created               |                                |
        |<----------------------------------|                                |
```

---

## Injeção de Dependência de Storage (`set_storage_service`)

Na camada de serviço (`ContractService`), o cliente de storage é gerenciado via injeção de dependência (`_storage_service` / `get_storage_client()`).

- **Utilidade para Testes:** Permite que os testes unitários injetem instâncias customizadas ou mocks via `ContractService.set_storage_service(mock_storage)` sem disparar chamadas de rede reais para a API do Cloudflare R2 nem exigir credenciais no ambiente de testes.

---

## Tratamento de Erros e Resiliência

- **Expiração da URL:** A URL pré-assinada possui validade de 15 minutos (900 segundos).
- **Validação no Frontend:** O formulário valida o tipo de arquivo (`application/pdf`, `image/png`, `image/jpeg`) e o tamanho máximo de 10 MB antes de solicitar a URL.
- **Atomicidade no Backend:** A rota `/contracts/full` executa em transação atômica (`transaction.atomic()`). Se a criação das parcelas ou itens falhar, o contrato não é mantido inconsistente.
