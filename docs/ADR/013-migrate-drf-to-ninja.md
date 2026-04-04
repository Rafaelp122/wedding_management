# ADR 013: Migração de Django REST Framework para Django Ninja

## Status
Aceito

## Contexto
O ecossistema inicial de APIs no backend dependia integralmente do **Django REST Framework (DRF)**. Utilizávamos pacotes satélites para funcionalidades como documentação (`drf-spectacular`) e autenticação (`djangorestframework-simplejwt`).

Apesar do DRF ter fornecido um robusto mecanismo inicial de ViewSets, Serializers e Roteamentos, com o tempo nossa camada de visualização começou a acumular gargalos:
1. **Desacoplamento Front e Back:** Com a adoção do **Orval** no frontend, nossa principal fonte da verdade virou o *OpenAPI schema*. O DRF exige extenso boilerplate do drf-spectacular via `@extend_schema` para exportar tipos complexos perfeitamente.
2. **Tipagem Estática:** Queríamos validações mais consistentes em tempo de compilação/digitação no IDE. Os serializers do DRF baseiam-se numa implementação dinâmica baseada em dicionários para expor seus `validated_data`.

## Decisão
Substituir o Django REST Framework pelo **Django Ninja**.
A migração consistiu em substituir:
* `serializers.py` -> `schemas.py` (Baseados nativamente em Pydantic).
* `viewsets.py` / `views.py` -> `api.py` (Funções baseadas em tipagem Python 3).
* `drf-spectacular` -> Exposição automática e nativa da API pelo Django Ninja.

## Consequências
* **Aumento de Performance:** Pydantic provê velocidade de validação consideravelmente superior, baseada na reescrita interna em Rust da própria lib.
* **Garantia de Tipagem:** `request` e as funções utilitárias agora validam fortemente tanto requisições de entrada quanto saída.
* **Menor complexidade de arquivos:** Não possuímos mais `urls.py` dentro de cada aplicação. As rotas agora são todas concentradas via instâncias do Ninja `Router()`.
* O Front end permanece estagnado e imutável quanto às requisições, pois o `.yaml` e `.json` gerados pelo OpenAPI são isomórficos.
