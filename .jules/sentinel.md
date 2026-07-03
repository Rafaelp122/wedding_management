## 2026-04-04 - Ninja Extra Throttling Rate Format
**Vulnerability:** N/A (Security Enhancement)
**Learning:** Ao implementar throttling com `django-ninja-extra`, descobri que o parser de `RateThrottle` espera abreviações de uma única letra para unidades de tempo ('s', 'm', 'h', 'd'). O uso de palavras completas como 'minute' ou 'day' resulta em um `ValueError` durante a inicialização da API, impedindo que o servidor suba.
**Prevention:** Sempre utilizar o formato abreviado nas configurações de `THROTTLE_RATES` (ex: '10/m' em vez de '10/minute').
