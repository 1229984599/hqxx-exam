# 多阶段构建 - 前端构建阶段
FROM node:18-alpine AS frontend-builder

# 设置工作目录
WORKDIR /build

# 复制前端项目文件
COPY home/package*.json home/pnpm-lock.yaml* ./home/
COPY admin/package*.json admin/pnpm-lock.yaml* ./admin/

# 安装pnpm
RUN npm config set registry https://registry.npmmirror.com && npm install -g pnpm

# 安装依赖并构建前端
WORKDIR /build/home
COPY home/ .
RUN pnpm install && pnpm build

# 构建管理后台
WORKDIR /build/admin
COPY admin/ .
RUN pnpm install && pnpm build

# Python依赖构建阶段
FROM python:3.11.6-alpine AS python-builder

# 安装构建依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust

# 安装PDM
RUN pip install --no-cache-dir pdm

# 设置工作目录
WORKDIR /build

# 复制Python项目文件
COPY api/pyproject.toml api/pdm.lock* ./

# 安装Python依赖到指定目录
RUN pdm install --prod --no-editable --no-self

# 最终运行阶段
FROM python:3.11.6-alpine AS runtime

# 安装运行时依赖
RUN apk add --no-cache \
    nginx \
    redis \
    supervisor \
    sqlite \
    curl \
    && rm -rf /var/cache/apk/*

# 创建应用目录
WORKDIR /app

# 创建必要的目录
RUN mkdir -p \
    /app/api \
    /app/static/home \
    /app/static/admin \
    /app/config \
    /app/scripts \
    /app/data \
    /var/log/supervisor \
    /run/nginx

# 复制Python依赖
COPY --from=python-builder /build/.venv /app/.venv

# 复制前端构建文件
COPY --from=frontend-builder /build/home/dist /app/static/home
COPY --from=frontend-builder /build/admin/dist /app/static/admin

# 复制后端代码
COPY api/ /app/api/

# 设置Python路径
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/api:$PYTHONPATH"

# 复制配置文件
COPY docker/nginx.conf /app/config/
COPY docker/supervisord.conf /app/config/
COPY docker/redis.conf /app/config/
COPY docker/start.sh /app/scripts/
COPY docker/init_db.sh /app/scripts/

# 设置权限
RUN chmod +x /app/scripts/start.sh /app/scripts/init_db.sh && \
    chown -R nginx:nginx /var/lib/nginx && \
    chown -R nginx:nginx /var/log/nginx

# 创建非root用户
RUN addgroup -g 1000 appuser && \
    adduser -D -s /bin/sh -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /app

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/api/health || exit 1

# 设置启动命令
CMD ["/app/scripts/start.sh"]
