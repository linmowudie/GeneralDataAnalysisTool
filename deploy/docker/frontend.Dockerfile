# 前端镜像：Vite 构建 + nginx 托管（含 /api 反向代理）
# 构建上下文：仓库根目录
#   minikube image build -t gdat/frontend:1.0.0 -f deploy/docker/frontend.Dockerfile .
FROM node:22-alpine AS build

WORKDIR /app

# 先复制依赖清单，利用层缓存
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---------- 运行镜像 ----------
FROM nginx:alpine

# nginx 官方镜像会在启动时对该目录下 *.template 做 envsubst 并输出到去掉 .template 的路径
COPY deploy/docker/nginx.conf.template /etc/nginx/templates/default.conf.template

COPY --from=build /app/dist /usr/share/nginx/html

# 后端服务地址（k8s Service 名），可被 Deployment env 覆盖
ENV BACKEND_HOST=backend-svc \
    BACKEND_PORT=8000

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1
