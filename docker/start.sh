#!/bin/sh

# 启动脚本 - 初始化并启动所有服务

set -e

echo "🚀 启动红旗小学无纸化测评系统..."

# 创建必要的目录（使用应用目录避免权限问题）
mkdir -p /app/logs/nginx/client_temp
mkdir -p /app/logs/nginx/proxy_temp
mkdir -p /app/logs/nginx/fastcgi_temp
mkdir -p /app/logs/nginx/uwsgi_temp
mkdir -p /app/logs/nginx/scgi_temp
mkdir -p /app/logs/supervisor
mkdir -p /app/logs/redis
mkdir -p /app/data
mkdir -p /run/nginx

# 设置权限（以当前用户身份）
chmod -R 755 /app/data /app/logs /run/nginx

# 创建空的日志文件
touch /app/logs/nginx/error.log /app/logs/nginx/access.log
chmod 644 /app/logs/nginx/error.log /app/logs/nginx/access.log

# 等待一下确保目录创建完成
sleep 1

echo "📁 目录结构创建完成"

# 检查Python环境
echo "🐍 检查Python环境..."
if [ ! -f "/app/.venv/bin/python" ]; then
    echo "❌ Python虚拟环境未找到"
    exit 1
fi

# 检查前端文件
echo "🌐 检查前端文件..."
if [ ! -f "/app/static/home/index.html" ]; then
    echo "❌ 前端文件未找到"
    exit 1
fi

if [ ! -f "/app/static/admin/index.html" ]; then
    echo "❌ 管理后台文件未找到"
    exit 1
fi

echo "✅ 文件检查完成"

# 初始化数据库（如果需要）
echo "🗄️ 初始化数据库..."
cd /app/api

# 设置环境变量
export PYTHONPATH="/app/api"
export DATABASE_URL="sqlite:///app/data/app.db"

# 检查是否已经初始化过
if [ ! -f "/app/data/app.db" ]; then
    echo "📊 首次运行，创建数据库..."

    # 尝试创建数据库目录
    mkdir -p /app/data

    # 运行数据库初始化
    /app/.venv/bin/python -c "
import asyncio
import sys
sys.path.insert(0, '/app/api')

try:
    from tortoise import Tortoise
    from app.config import TORTOISE_ORM

    async def init_db():
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        await Tortoise.close_connections()
        print('✅ 数据库初始化完成')

    asyncio.run(init_db())
except Exception as e:
    print(f'⚠️ 数据库初始化失败: {e}')
    print('将在运行时自动创建')
"

else
    echo "📊 数据库已存在，跳过初始化"
fi

# 测试Redis配置
echo "🔴 测试Redis配置..."
echo "⚠️ 跳过Redis配置测试"

# 测试Nginx配置
echo "🌐 测试Nginx配置..."
nginx -t -c /app/config/nginx.conf || {
    echo "❌ Nginx配置测试失败"
    exit 1
}

echo "✅ 配置测试完成"

# 启动supervisord
echo "🎯 启动服务管理器..."
exec /usr/bin/supervisord -c /app/config/supervisord.conf
