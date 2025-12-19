# 🔒 Guia de Segurança - Wedding Management System

## 📋 Índice

1. [Checklist de Segurança](#-checklist-de-segurança)
2. [Configurações de Produção](#-configurações-de-produção)
3. [Variáveis Sensíveis](#-variáveis-sensíveis)
4. [Autenticação e Autorização](#-autenticação-e-autorização)
5. [Proteção contra Ataques](#-proteção-contra-ataques)
6. [HTTPS e SSL](#-https-e-ssl)
7. [Backup e Recuperação](#-backup-e-recuperação)
8. [Monitoramento](#-monitoramento)
9. [Atualizações](#-atualizações)
10. [Reporte de Vulnerabilidades](#-reporte-de-vulnerabilidades)

---

## ✅ Checklist de Segurança

### Antes de Deploy em Produção

- [ ] `DEBUG=False` no ambiente de produção
- [ ] `SECRET_KEY` única e forte (50+ caracteres)
- [ ] `ALLOWED_HOSTS` configurado com domínio real
- [ ] `CSRF_TRUSTED_ORIGINS` configurado
- [ ] HTTPS habilitado com certificado SSL válido
- [ ] Senhas de banco de dados fortes (20+ caracteres)
- [ ] Firewall configurado (apenas portas 80, 443, 22)
- [ ] Backup automático configurado
- [ ] Logs de erro configurados (Sentry ou similar)
- [ ] Dependências atualizadas (sem vulnerabilidades conhecidas)
- [ ] `.env` não commitado no Git
- [ ] Arquivos de mídia protegidos (uploads validados)
- [ ] Rate limiting configurado na API
- [ ] CORS configurado corretamente

---

## ⚙️ Configurações de Produção

### Django Settings

```python
# wedding_management/settings/production.py

# NUNCA use DEBUG=True em produção
DEBUG = False

# Hosts permitidos (substitua pelo seu domínio)
ALLOWED_HOSTS = ['seudominio.com', 'www.seudominio.com']
CSRF_TRUSTED_ORIGINS = ['https://seudominio.com', 'https://www.seudominio.com']

# Segurança HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
```

### Nginx Configuration

```nginx
# nginx/conf.d/production.conf

# Redirecionar HTTP para HTTPS
server {
    listen 80;
    server_name seudominio.com www.seudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seudominio.com www.seudominio.com;
    
    # SSL
    ssl_certificate /etc/letsencrypt/live/seudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com/privkey.pem;
    
    # Segurança SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Headers de segurança
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Tamanho máximo de upload
    client_max_body_size 10M;
    
    # ... resto da configuração
}
```

---

## 🔐 Variáveis Sensíveis

### Variáveis que NUNCA devem ser commitadas

```bash
# .env (NUNCA commitar este arquivo!)

# Django
SECRET_KEY=gere-uma-chave-aleatoria-com-50-caracteres-ou-mais
DEBUG=False

# Database
POSTGRES_PASSWORD=senha-super-segura-com-minimo-20-caracteres
POSTGRES_USER=usuario_producao_seguro
POSTGRES_DB=wedding_management_prod

# Email
EMAIL_HOST_USER=seu-email@dominio.com
EMAIL_HOST_PASSWORD=senha-de-aplicativo-do-email

# Sentry (opcional mas recomendado)
SENTRY_DSN=https://sua-chave-sentry@sentry.io/projeto

# AWS/S3 (se usar)
AWS_ACCESS_KEY_ID=sua-chave-aws
AWS_SECRET_ACCESS_KEY=sua-chave-secreta-aws
```

### Gerar SECRET_KEY Segura

```bash
# No servidor ou localmente
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Gerar Senha Forte

```bash
# Linux/Mac
openssl rand -base64 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 👤 Autenticação e Autorização

### Políticas de Senha

O sistema já implementa:
- ✅ Mínimo de 8 caracteres
- ✅ Validação de senhas comuns
- ✅ Hash seguro com PBKDF2 (padrão Django)

### Boas Práticas

```python
# Trocar senha padrão do admin imediatamente
python manage.py changepassword admin

# Criar usuários com senhas fortes
python manage.py createsuperuser
```

### Permissões

O sistema usa:
- **Mixins de autorização** em todas as views
- **Verificação de ownership** (usuários só acessam seus dados)
- **Permissões por grupo** (via Django Admin)

```python
# Exemplo de verificação automática
class WeddingDetailView(LoginRequiredMixin, UserOwnsWeddingMixin, DetailView):
    # Apenas o dono do casamento pode acessar
    pass
```

---

## 🛡️ Proteção contra Ataques

### SQL Injection

✅ **Já protegido:** Django ORM escapa automaticamente queries.

**❌ NUNCA faça:**
```python
# PERIGOSO - Não use!
User.objects.raw(f"SELECT * FROM users WHERE id = {user_id}")
```

**✅ SEMPRE faça:**
```python
# SEGURO
User.objects.filter(id=user_id)
```

### XSS (Cross-Site Scripting)

✅ **Já protegido:** Templates Django escapam HTML automaticamente.

**⚠️ Cuidado com:**
```django
{# Só use |safe se tiver CERTEZA que o conteúdo é seguro #}
{{ user_input|safe }}
```

### CSRF (Cross-Site Request Forgery)

✅ **Já protegido:** Django CSRF middleware ativo.

**Sempre use em forms:**
```django
<form method="post">
    {% csrf_token %}
    <!-- campos do formulário -->
</form>
```

### Clickjacking

✅ **Já protegido:** `X-Frame-Options: SAMEORIGIN` configurado.

### Rate Limiting (Recomendado implementar)

Proteger API contra abuso:

```bash
# Instalar
pip install django-ratelimit
```

```python
# apps/weddings/api/views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='GET')
def api_view(request):
    # Limita a 100 requests por hora por IP
    pass
```

---

## 🔒 HTTPS e SSL

### Obter Certificado SSL Gratuito (Let's Encrypt)

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seudominio.com -d www.seudominio.com

# Renovação automática (crontab)
sudo certbot renew --dry-run
```

### Verificar Configuração SSL

Teste em: https://www.ssllabs.com/ssltest/

**Meta:** Nota A ou A+

---

## 💾 Backup e Recuperação

### Backup Automático do Banco de Dados

```bash
# Script de backup (executar diariamente via cron)
#!/bin/bash
BACKUP_DIR="/backups/wedding_management"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="backup_${DATE}.sql.gz"

docker compose exec -T db pg_dump -U postgres wedding_management | gzip > "${BACKUP_DIR}/${FILENAME}"

# Manter apenas últimos 30 dias
find ${BACKUP_DIR} -name "backup_*.sql.gz" -mtime +30 -delete
```

### Crontab

```bash
# Adicionar ao crontab: crontab -e
0 2 * * * /path/to/backup_script.sh
```

### Restore do Backup

```bash
# Descompactar e restaurar
gunzip < backup_20251219.sql.gz | docker compose exec -T db psql -U postgres wedding_management
```

### Backup de Arquivos de Mídia

```bash
# Rsync para backup
rsync -avz /path/to/media/ backup_server:/backups/wedding_media/
```

---

## 📊 Monitoramento

### Sentry (Recomendado)

```python
# wedding_management/settings/production.py

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SENTRY_DSN = os.getenv("SENTRY_DSN")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,  # Não enviar dados pessoais
        environment="production",
    )
```

### Logs de Segurança

```python
# Monitorar tentativas de login falhadas
import logging

logger = logging.getLogger('security')

# Em views de login
if not user.is_authenticated:
    logger.warning(f"Failed login attempt for {username} from {request.META['REMOTE_ADDR']}")
```

### Health Checks

```python
# apps/core/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy"})
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=503)
```

---

## 🔄 Atualizações

### Verificar Vulnerabilidades

```bash
# Verificar dependências com vulnerabilidades conhecidas
pip install safety
safety check -r requirements/production.txt

# Ou usar pip-audit
pip install pip-audit
pip-audit
```

### Manter Dependências Atualizadas

```bash
# Verificar atualizações disponíveis
pip list --outdated

# Atualizar com cuidado (testar antes!)
pip install -U nome-do-pacote

# Sempre rodar testes após atualizar
pytest
```

### Política de Atualizações

- **Patches de segurança:** Aplicar imediatamente
- **Minor updates:** Mensalmente
- **Major updates:** Planejar e testar cuidadosamente

---

## 🚨 Reporte de Vulnerabilidades

### Como Reportar

Se você descobrir uma vulnerabilidade de segurança, por favor:

1. **NÃO abra uma issue pública**
2. Envie um email para: **rafaelpereiradearaujo5@gmail.com**
3. Inclua:
   - Descrição detalhada da vulnerabilidade
   - Passos para reproduzir
   - Impacto potencial
   - Sugestão de correção (se tiver)

### Resposta Esperada

- **Confirmação:** Até 48 horas
- **Correção:** Até 7 dias (para vulnerabilidades críticas)
- **Divulgação:** Após correção e deploy

---

## 📚 Recursos Adicionais

### Links Úteis

- [Django Security Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Mozilla Observatory](https://observatory.mozilla.org/)
- [Security Headers](https://securityheaders.com/)

### Ferramentas Recomendadas

- **Sentry:** Monitoramento de erros
- **Fail2ban:** Proteção contra brute force
- **ModSecurity:** WAF (Web Application Firewall)
- **Cloudflare:** DDoS protection

---

## 🔍 Auditoria de Segurança

### Checklist Trimestral

- [ ] Revisar usuários com acesso admin
- [ ] Verificar logs de acesso suspeitos
- [ ] Atualizar dependências
- [ ] Verificar certificados SSL (validade)
- [ ] Testar restore de backup
- [ ] Revisar permissões de arquivos no servidor
- [ ] Verificar configurações de firewall

### Ferramentas de Auditoria

```bash
# Verificar configuração Django
python manage.py check --deploy

# Scan de segurança
pip install bandit
bandit -r apps/

# Verificar headers HTTP
curl -I https://seudominio.com
```

---

**Última atualização:** 19 de dezembro de 2025

**Mantenha este documento atualizado** conforme novas medidas de segurança são implementadas.
