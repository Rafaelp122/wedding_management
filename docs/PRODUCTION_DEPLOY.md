# 🚀 Guia de Deploy para Produção

## 📋 Checklist Pré-Deploy

### 1. ✅ Otimizações Docker Concluídas
- [x] Dockerfile multi-stage (411MB vs 816MB)
- [x] docker-compose.prod.yml configurado
- [x] Portas internas protegidas (DB e Redis não expostos)
- [x] Nginx como proxy reverso

### 2. ⚠️ Configurações Necessárias

#### 2.1 Variáveis de Ambiente

```bash
# No servidor de produção, crie o arquivo .env
cp .env.production.example .env
nano .env  # ou vim, ou seu editor favorito
```

**Variáveis OBRIGATÓRIAS:**
- `SECRET_KEY` - Gere uma chave única e aleatória
- `POSTGRES_PASSWORD` - Senha forte para o banco
- `ALLOWED_HOSTS` - Seu domínio real

**Gerar SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 2.2 Nginx e SSL

**Com domínio e SSL (Recomendado):**

1. Crie `nginx/conf.d/production.conf`:
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    # Configurações SSL recomendadas
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Resto da configuração igual ao default.conf
    location /static/ { ... }
    location /media/ { ... }
    location / { proxy_pass http://django; }
}
```

2. Obter certificado SSL:
```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

**Sem domínio (Apenas HTTP):**
- Pode usar a configuração atual `default.conf`
- ⚠️ Não recomendado para produção real

### 3. 🖥️ Servidor de Produção

#### Requisitos Mínimos:
- **RAM:** 2GB (recomendado 4GB)
- **CPU:** 2 cores
- **Disco:** 20GB
- **OS:** Ubuntu 22.04 LTS ou similar

#### Instalar Docker:
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Verificar instalação
docker --version
docker compose version
```

## 🚀 Deploy Passo a Passo

### Opção A: Deploy com Build no Servidor

```bash
# 1. Clonar repositório
git clone https://github.com/Rafaelp122/wedding_management.git
cd wedding_management

# 2. Configurar variáveis de ambiente
cp .env.production.example .env
nano .env  # Preencher com valores reais

# 3. Build e subir containers
docker compose -f docker/docker-compose.prod.yml up -d --build

# 4. Verificar logs
docker compose -f docker/docker-compose.prod.yml logs -f

# 5. Criar superusuário
docker compose -f docker/docker-compose.prod.yml exec web python manage.py createsuperuser

# 6. Testar
curl -I http://localhost
```

### Opção B: Deploy com Imagens do Registry

```bash
# 1. Na máquina local, fazer push das imagens
docker compose -f docker/docker-compose.prod.yml build
docker compose -f docker/docker-compose.prod.yml push

# 2. No servidor, pull e deploy
git clone https://github.com/Rafaelp122/wedding_management.git
cd wedding_management
cp .env.production.example .env
nano .env  # Configurar

docker compose -f docker/docker-compose.prod.yml pull
docker compose -f docker/docker-compose.prod.yml up -d

# 3. Verificar
docker compose -f docker/docker-compose.prod.yml ps
```

## 🔄 Atualização da Aplicação

```bash
# 1. Fazer backup do banco
docker compose -f docker/docker-compose.prod.yml exec db pg_dump -U postgres wedding_management > backup_$(date +%Y%m%d).sql

# 2. Atualizar código
git pull origin main

# 3. Rebuild e restart
docker compose -f docker/docker-compose.prod.yml up -d --build

# 4. Executar migrações
docker compose -f docker/docker-compose.prod.yml exec web python manage.py migrate

# 5. Coletar estáticos
docker compose -f docker/docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 📊 Monitoramento

### Logs em Tempo Real
```bash
# Todos os serviços
docker compose -f docker/docker-compose.prod.yml logs -f

# Apenas web
docker compose -f docker/docker-compose.prod.yml logs -f web

# Apenas nginx
docker compose -f docker/docker-compose.prod.yml logs -f nginx
```

### Status dos Containers
```bash
docker compose -f docker/docker-compose.prod.yml ps
```

### Uso de Recursos
```bash
docker stats
```

## 🔐 Backup e Restore

### Backup do Banco de Dados
```bash
# Backup manual
docker compose -f docker/docker-compose.prod.yml exec db pg_dump -U postgres wedding_management > backup.sql

# Backup automático (cron)
# Adicionar no crontab: crontab -e
0 2 * * * cd /path/to/wedding_management && docker compose -f docker/docker-compose.prod.yml exec db pg_dump -U postgres wedding_management > /backups/backup_$(date +\%Y\%m\%d).sql
```

### Restore do Banco
```bash
# 1. Copiar backup para o container
docker cp backup.sql wedding_db_prod:/tmp/backup.sql

# 2. Restore
docker compose -f docker/docker-compose.prod.yml exec db psql -U postgres wedding_management < /tmp/backup.sql
```

## 🛡️ Segurança

### Checklist de Segurança:
- [ ] `DEBUG=False` em produção
- [ ] `SECRET_KEY` única e secreta
- [ ] Senha forte no PostgreSQL
- [ ] SSL/HTTPS configurado (se tiver domínio)
- [ ] Portas internas não expostas (apenas 80/443)
- [ ] Firewall configurado no servidor
- [ ] Backups regulares configurados
- [ ] Monitoramento de erros (Sentry)
- [ ] Logs sendo coletados

### Configurar Firewall (UFW)
```bash
# Permitir apenas SSH, HTTP e HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## 🚨 Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker compose -f docker/docker-compose.prod.yml logs web

# Ver status
docker compose -f docker/docker-compose.prod.yml ps
```

### Erro de conexão com banco
```bash
# Verificar se DB está rodando
docker compose -f docker/docker-compose.prod.yml exec db psql -U postgres -c "SELECT 1"

# Verificar variáveis de ambiente
docker compose -f docker/docker-compose.prod.yml exec web env | grep POSTGRES
```

### Nginx mostrando página padrão
```bash
# Verificar configuração
docker compose -f docker/docker-compose.prod.yml exec nginx cat /etc/nginx/conf.d/default.conf

# Recarregar nginx
docker compose -f docker/docker-compose.prod.yml restart nginx
```

## 📈 Otimizações Avançadas

### 1. Usar Volume Driver para Backups
```yaml
volumes:
  postgres_data_prod:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/postgres
```

### 2. Limitar Recursos
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 3. Health Checks Avançados
```yaml
web:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

## 📚 Referências

- [Docker Compose Production Guide](https://docs.docker.com/compose/production/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Let's Encrypt Certbot](https://certbot.eff.org/)
