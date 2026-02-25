# ==============================================================================
# MULTI-STAGE BUILD - React + Vite Frontend
# ==============================================================================

# Definição de versão para evitar repetição e erro de tag flutuante
ARG NODE_VERSION=22.14.0
FROM node:${NODE_VERSION}-slim AS base

# ------------------------------------------------------------------------------
# Stage 1: Dependencies
# ------------------------------------------------------------------------------
FROM base AS dependencies
WORKDIR /app
COPY package.json package-lock.json ./
# npm ci é obrigatório em CI/Docker
RUN npm ci --quiet

# ------------------------------------------------------------------------------
# Stage 2: Development (Para uso com Docker Compose + Volumes)
# ------------------------------------------------------------------------------
FROM base AS development
WORKDIR /app
# Copiamos as dependências do estágio anterior
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .

EXPOSE 5173
# Vite precisa do --host para aceitar conexões de fora do container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ------------------------------------------------------------------------------
# Stage 3: Builder (Onde a mágica da produção acontece)
# ------------------------------------------------------------------------------
FROM base AS builder
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
# Build otimizado
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 4: Production (Nginx servindo estáticos)
# ------------------------------------------------------------------------------
FROM nginx:1.27-alpine AS production

WORKDIR /usr/share/nginx/html

# Limpeza e cópia do build
RUN rm -rf ./*
COPY --from=builder /app/dist .

# Configuração do Nginx via HEREDOC para legibilidade
RUN printf 'server { \n\
    listen 80; \n\
    root /usr/share/nginx/html; \n\
    index index.html; \n\
    gzip on; \n\
    gzip_types text/plain text/css application/json application/javascript text/xml; \n\
    location / { \n\
        try_files $uri $uri/ /index.html; \n\
    } \n\
    # Cache para assets estáticos \n\
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ { \n\
        expires 1y; \n\
        add_header Cache-Control "public, immutable"; \n\
    } \n\
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
