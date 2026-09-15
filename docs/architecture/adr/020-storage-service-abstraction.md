# ADR-020: Abstração do Serviço de Storage e Injeção de Dependências

> **Categoria:** Decisões de Arquitetura (ADR)
> **Status:** 🟢 Vigente
> **Data:** Julho 2026
> **Decisor:** Rafael
> **Relacionados:** [ADR-003: Armazenamento de Arquivos no Cloudflare R2](003-why-r2.md) · [ADR-004: Upload Direto via URLs Pré-Assinadas](004-presigned-urls.md) · [ADR-006: Service Layer Pattern](006-service-layer.md) · [ADR-030: Rich Domain Model e Service Layer](030-rich-domain-model-service-layer.md)

---

## 1. Contexto e Problema

Anteriormente, o `ContractService` (no app `logistics`) continha lógica de negócios de gestão de contratos acoplada diretamente à criação de clientes `boto3` e geração de URLs pré-assinadas para o Cloudflare R2. Esse acoplamento gerava:

1. **Violação do SRP (Princípio de Responsabilidade Única):** O serviço do domínio de contratos precisava conhecer detalhes de baixo nível da infraestrutura de storage.
2. **Dificuldade de Testabilidade:** Os testes do serviço e da API de logística precisavam realizar mocks diretos do pacote de baixo nível `boto3.client`.
3. **Rigidez Arquitetural:** Alterar o provedor de nuvem (ex: do Cloudflare R2 para AWS S3 ou Google Cloud Storage) exigiria reescrever lógica interna do domínio de logística.

---

## 2. Decisão

1. **Abstração Base (`StorageService`):** Criar um protocolo estrutural `StorageService` no módulo `apps/core/services/storage_service.py` que define a interface de interação com o storage de arquivos.
2. **Implementação Concreta (`CloudflareR2StorageService`):** Encapsular a lógica de baixo nível do `boto3` e a leitura de credenciais dentro da implementação concreta.
3. **Injeção de Dependência:**
   - Fornecer suporte para injeção via parâmetro de método nos serviços do domínio.
   - Fornecer suporte para configuração de injeção global de classe via setter (`ContractService.set_storage_service()`).
4. **Resolução de Configurações Dinâmicas (Lazy Resolution):**
   - A leitura das chaves de settings de storage deve ocorrer sob demanda por propriedades dinâmicas (`@property`), permitindo que modificações feitas em tempo de execução pelos testes tenham efeito imediato.
   - O serviço de storage global ativo deve ser instanciado sob demanda via factory baseada em configurações (`settings.STORAGE_PROVIDER`), evitando a dependência precoce no import time do módulo.

---

## 3. Consequências

### Positivas
- **Desacoplamento do Domínio:** `ContractService` lida apenas com contratos; não tem conhecimento de `boto3`, S3 ou endpoints de rede do R2.
- **Substituição Transparente:** Para migrar de provedor, basta implementar um novo serviço que atenda ao protocolo e alterar a variável `STORAGE_PROVIDER` no `.env`.
- **Testes Limpos:** A suíte de testes de logística agora injeta um `DummyStorageService` simples nas chamadas, acelerando os testes e eliminando a fragilidade de mockar bibliotecas de terceiros.

### Negativas e mitigações
- Pequeno aumento no número de classes e interfaces de infraestrutura do sistema (compensado amplamente pela testabilidade e isolamento do domínio).

---

## 4. Referências

1. [ADR-003: Armazenamento de Arquivos no Cloudflare R2](003-why-r2.md)
2. [ADR-004: Upload Direto via URLs Pré-Assinadas](004-presigned-urls.md)
3. [ADR-006: Service Layer Pattern](006-service-layer.md)
4. [ADR-030: Rich Domain Model e Service Layer](030-rich-domain-model-service-layer.md)
