# ---- Build stage — compile the React SPA ----
FROM node:20-alpine AS builder

WORKDIR /app
COPY front/package.json front/package-lock.json ./
RUN npm ci
COPY front/ .
RUN npm run build

# ---- Serve stage — nginx handles SPA, API proxy and video streaming ----
FROM nginx:alpine

COPY --from=builder /app/dist        /usr/share/nginx/html
COPY nginx/nginx.conf                /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
