# Especificação Técnica: Guard-Rail de Segurança e Permissões

> **Módulo:** [guard-rails](index.md) | [auth-jwt-flow](../../../architecture/concepts/auth-jwt-flow.md)
> **Testes:** `backend/apps/core/tests/test_security_audit.py` e `test_sensitive_data_leak.py`

---

## 1. Visão Geral

Os guard-rails de segurança em `test_security_audit.py` e `test_sensitive_data_leak.py` auditam a API REST e os schemas DTO buscando por vazamentos de dados sensíveis e acessos não autenticados.

---

## 2. Garantias do Teste

1. **Prevenção de Exposição de Senhas/Hashes**: Inspeciona todos os schemas de resposta Ninja/Pydantic garantindo que campos sensíveis (`password`, `hash`, `secret_key`) jamais sejam expostos nos payloads JSON da API.
2. **Auditoria de Parâmetro `company`**: Garante que serviços públicos tratem isolamento de tenant declarando `company` (ou `company: Company | None = None` em serviços do sistema).
