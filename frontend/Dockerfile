# Estágio Base
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm install

# Estágio de Desenvolvimento
FROM base AS development
COPY . .
EXPOSE 5173
# --host 0.0.0.0 é obrigatório para o Docker
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Estágio de Produção
FROM base AS build
COPY . .
RUN npm run build

FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]