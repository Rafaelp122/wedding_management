# App: Weddings

Núcleo do sistema, responsável pelo gerenciamento de casamentos e eventos.

## Descrição

O app `weddings` gerencia a entidade principal do sistema: o **Casamento** (`Wedding`). Possui **arquitetura híbrida** com duas interfaces distintas:

- **Interface Web** (Django + HTMX): Uso tradicional via navegador
- **Interface API** (Django REST Framework): Integrações programáticas e apps mobile

**Principais recursos:**
- CRUD completo de casamentos
- Painel central de cada evento
- Filtros, busca e ordenação
- Relacionamento com todos os outros módulos (itens, contratos, orçamento, agenda)

**Status:** ✅ 60 testes passando (53 web + 7 API) | Versão 3.0

---

## 📚 Documentação Completa

Para informações detalhadas sobre arquitetura, QuerySets, Mixins, ViewSets, Serializers, exemplos de uso e guia de testes, consulte:

👉 **[Documentação Técnica Completa](../../docs/apps/weddings.md)**
