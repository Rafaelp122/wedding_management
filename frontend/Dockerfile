# ==============================================================================
# MULTI-STAGE BUILD - React + Vite Frontend
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Dependencies - Instala node_modules
# ------------------------------------------------------------------------------
FROM node:22-alpine AS dependencies

WORKDIR /app

# Copia apenas arquivos de dependências para cache otimizado
COPY package.json package-lock.json ./

# Instala dependências (usa cache quando package.json não muda)
RUN npm ci --quiet

# ------------------------------------------------------------------------------
# Stage 2: Development - Ambiente de desenvolvimento com hot reload
# ------------------------------------------------------------------------------
FROM node:22-alpine AS development

WORKDIR /app

# Copia node_modules do stage de dependencies
COPY --from=dependencies /app/node_modules ./node_modules

# Copia código da aplicação
COPY . .

EXPOSE 5173

# Vite dev server com HMR
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ------------------------------------------------------------------------------
# Stage 3: Builder - Build otimizado para produção
# ------------------------------------------------------------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# Copia node_modules do stage de dependencies
COPY --from=dependencies /app/node_modules ./node_modules

# Copia código fonte
COPY . .

# Build de produção (minificado, tree-shaking, etc)
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 4: Production - Nginx servindo arquivos estáticos
# ------------------------------------------------------------------------------
FROM nginx:alpine AS production

# Remove configuração default do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia build otimizado do stage builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia configuração customizada do Nginx (se existir)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Cria configuração otimizada do Nginx
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Compressão Gzip \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json; \
    \
    # Logs \
    access_log /var/log/nginx/access.log; \
    error_log /var/log/nginx/error.log warn; \
    \
    # Cache de assets estáticos \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
    \
    # HTML não deve ser cacheado \
    location ~* \.html$ { \
        expires -1; \
        add_header Cache-Control "no-store, no-cache, must-revalidate"; \
    } \
    \
    # SPA fallback - todas as rotas retornam index.html \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Security headers \
    add_header X-Frame-Options "SAMEORIGIN" always; \
    add_header X-Content-Type-Options "nosniff" always; \
    add_header X-XSS-Protection "1; mode=block" always; \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
