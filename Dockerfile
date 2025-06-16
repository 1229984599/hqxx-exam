# 多阶段构建 - 前端构建阶段
FROM --platform=$BUILDPLATFORM node:18-alpine AS frontend-builder

# 设置工作目录
WORKDIR /build

# 安装pnpm（使用国内镜像加速）
RUN npm config set registry https://registry.npmmirror.com && \
    npm install -g pnpm && \
    pnpm config set registry https://registry.npmmirror.com

# 构建前端项目
WORKDIR /build/home
COPY home/package*.json home/pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile
COPY home/ .
RUN pnpm build

# 构建管理后台
WORKDIR /build/admin
COPY admin/package*.json admin/pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile
COPY admin/ .
RUN pnpm build

# Python依赖构建阶段
FROM --platform=$BUILDPLATFORM python:3.11.6-alpine AS python-builder

# 安装构建依赖（合并到一个RUN层减少镜像大小）
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust \
    && pip install --no-cache-dir pdm

# 设置工作目录
WORKDIR /build

# 复制Python项目文件（先复制依赖文件利用缓存）
COPY api/pyproject.toml api/pdm.lock* ./

# 安装Python依赖到指定目录
RUN pdm install --prod --no-editable --no-self

# 最终运行阶段
FROM python:3.11.6-alpine AS runtime

# 安装运行时依赖（合并命令减少层数）
RUN apk add --no-cache \
    nginx \
    redis \
    supervisor \
    sqlite \
    curl \
    tzdata \
    && rm -rf /var/cache/apk/* \
    && addgroup -g 1000 appuser \
    && adduser -D -s /bin/sh -u 1000 -G appuser appuser

# 创建应用目录和必要的目录结构
WORKDIR /app
RUN mkdir -p \
    /app/api \
    /app/static/home \
    /app/static/admin \
    /app/config \
    /app/scripts \
    /app/data \
    /app/logs/nginx \
    /app/logs/nginx/client_temp \
    /app/logs/nginx/proxy_temp \
    /app/logs/nginx/fastcgi_temp \
    /app/logs/nginx/uwsgi_temp \
    /app/logs/nginx/scgi_temp \
    /app/logs/supervisor \
    /app/logs/redis \
    /run/nginx

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/api" \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 复制Python依赖
COPY --from=python-builder /build/.venv /app/.venv

# 复制前端构建文件
COPY --from=frontend-builder /build/home/dist /app/static/home
COPY --from=frontend-builder /build/admin/dist /app/static/admin

# 复制后端代码和配置文件
COPY api/ /app/api/
COPY docker/nginx.conf /app/config/
COPY docker/supervisord.conf /app/config/
COPY docker/redis.conf /app/config/
COPY docker/start.sh /app/scripts/
COPY docker/init_db.sh /app/scripts/

# 设置权限（合并到一个RUN层）
RUN chmod +x /app/scripts/start.sh /app/scripts/init_db.sh \
    && chown -R appuser:appuser /app /run/nginx

# 暴露端口
EXPOSE 80

# 健康检查（优化）
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/api/health || curl -f http://localhost/ || exit 1

# 切换到非root用户运行
USER appuser

# 设置启动命令
CMD ["/app/scripts/start.sh"]
