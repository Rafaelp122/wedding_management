# ADR-006: Service Layer Pattern

> **Categoria:** Decisões de Arquitetura (ADR)
> **Status:** 🟡 Superada pela [ADR-030](030-rich-domain-model-service-layer.md)
> **Data:** Janeiro 2025
> **Decisor:** Rafael
> **Relacionados:** [ADR-013: Migração para Django Ninja](013-migrate-drf-to-ninja.md) · [ADR-030: Rich Domain Model e Service Layer como Casos de Uso](030-rich-domain-model-service-layer.md)

> [!WARNING]
> **Decisão Histórica / Superada pela [ADR-030: Rich Domain Model e Service Layer como Casos de Uso](030-rich-domain-model-service-layer.md)**:
> Esta decisão originalmente adotou o padrão de **Modelos Anêmicos** com toda regra de negócio concentrada exclusivamente em `services.py` (para combater os *Fat Serializers* do DRF). Em setembro de 2026, a [ADR-030](030-rich-domain-model-service-layer.md) superou este modelo anêmico, evoluindo a arquitetura para **Rich Domain Model (Rich Active Record)** onde invariantes intrínsecas e máquinas de estado residem nos Models (`clean()` e métodos de ciclo de vida), enquanto a Service Layer atua estritamente na orquestração de casos de uso e limites transacionais.

---

## 1. Contexto e Problema

Nos primórdios do projeto com Django REST Framework (DRF), a lógica de negócio estava dispersa entre Views, Serializers e Models, gerando os seguintes problemas arquiteturais:

1. **Testabilidade Comprometida:** Dificuldade em testar regras de negócio sem simular instâncias HTTP `request` completas.
2. **Reusabilidade Baixa:** Validações de negócio acopladas aos serializadores não podiam ser reutilizadas por tarefas assíncronas, rotinas CLI ou outros endpoints.
3. **Complexidade Excessiva (*Fat Serializers*):** Classes de serializadores acumulando centenas de linhas de métodos `.validate()` e lógicas de mutação secundárias.
4. **Acoplamento Elevado:** Alterações em contratos de apresentação quebravam fluxos de persistência e validações de negócio não relacionadas.

---

## 2. Decisão

Introduzir a **Service Layer (Camada de Serviços)** no monólito Django para isolar regras de negócio e orquestrações de caso de uso, separando-as da camada de apresentação HTTP.

### Comparativo de Abordagens de Camadas

| Aspecto | Service Layer (Escolha Original) | Fat Serializer (DRF Legado) | Fat Model (Django Tradicional) | Rich Active Record ([ADR-030](030-rich-domain-model-service-layer.md) - Vigente) |
| :--- | :--- | :--- | :--- | :--- |
| **Testabilidade** | :material-check-circle: Testes unitários puros | :material-close-circle: Exige mock de HTTP `request` | :material-alert: Exige conexão ao banco | :material-check-circle: Testes unitários puros em memória |
| **Reusabilidade** | :material-check-circle: Isolado de HTTP | :material-close-circle: Acoplado ao framework web | :material-alert: Acoplado ao ORM | :material-check-circle: Reutilizável em qualquer camada |
| **Encapsulamento** | :material-alert: Model anêmico (regras fora da entidade) | :material-close-circle: Objeto monolítico HTTP | :material-close-circle: Mistura I/O com domínio | :material-check-circle: Entidade protege suas próprias invariantes |
| **Orquestração** | :material-check-circle: Casos de uso atômicos | :material-close-circle: Procedural no `.save()` | :material-close-circle: Efeitos colaterais em signals | :material-check-circle: Transações atômicas e múltiplos agregados |

### Fluxo Arquitetural

```
Requisição HTTP (JSON)
       ↓
API / View (Autenticação, Autorização, Tipagem)
       ↓
Service Layer (Orquestração de Casos de Uso, Transações @transaction.atomic)
       ↓
Domain Models (Invariantes, Ciclo de Vida, Validação clean())
       ↓
Persistência (PostgreSQL)
```

---

## 3. Consequências

### Positivas :material-check-circle:
- **Testabilidade:** Regras de negócio passaram a ser testáveis de forma direta e independente do ciclo de vida de requisições HTTP.
- **Reusabilidade:** Serviços podem ser invocados uniformemente por endpoints de API, comandos do Django e tarefas em background.
- **Separação de Responsabilidades (SRP):** Limite nítido entre a borda de rede/validação de sintaxe e as regras operacionais da aplicação.

### Negativas / Trade-offs :material-close-circle:
- **Risco de Modelos Anêmicos:** A decisão original esvaziou os models de domínio, transformando-os em meras tabelas de dados sem comportamento intrínseco — problema posteriormente sanado pela [ADR-030](030-rich-domain-model-service-layer.md).
- **Sobrecarga em CRUDs Simples:** Criar classes de serviço para operações elementares sem lógica de negócio adiciona arquivos desnecessários.

---

## 4. Referências

- [ADR-013: Migração de Django REST Framework para Django Ninja](013-migrate-drf-to-ninja.md)
- [ADR-030: Rich Domain Model e Service Layer como Casos de Uso](030-rich-domain-model-service-layer.md)
- [Padrão Service Layer](../concepts/service-layer-pattern.md)
