#!/bin/sh

# 数据库初始化脚本

set -e

echo "🗄️ 开始数据库初始化..."

cd /app/api

# 设置环境变量
export PYTHONPATH="/app/api"
export DATABASE_URL="sqlite:///app/data/app.db"
export REDIS_URL="redis://localhost:6379"

# 等待Redis启动（可选）
echo "⏳ 等待Redis启动..."
REDIS_AVAILABLE=false
for i in $(seq 1 10); do
    if redis-cli -h 127.0.0.1 -p 6379 ping > /dev/null 2>&1; then
        echo "✅ Redis已启动"
        REDIS_AVAILABLE=true
        break
    fi
    sleep 1
done

if [ "$REDIS_AVAILABLE" = false ]; then
    echo "⚠️ Redis未启动，将使用内存缓存"
fi

# 检查数据库是否已初始化
if [ -f "/app/data/.db_initialized" ] && [ -f "/app/data/app.db" ]; then
    echo "📊 数据库已初始化，跳过初始化"
else
    echo "📊 使用现有数据库文件初始化..."

    # 删除可能存在的空数据库文件
    rm -f /app/data/app.db*

    # 检查是否存在现有的数据库文件
    if [ -f "/app/api/db.sqlite3" ]; then
        echo "📋 复制现有数据库文件..."
        cp /app/api/db.sqlite3 /app/data/app.db

        # 复制相关的SQLite文件（如果存在）
        if [ -f "/app/api/db.sqlite3-shm" ]; then
            cp /app/api/db.sqlite3-shm /app/data/app.db-shm
        fi
        if [ -f "/app/api/db.sqlite3-wal" ]; then
            cp /app/api/db.sqlite3-wal /app/data/app.db-wal
        fi

        echo "✅ 现有数据库文件复制完成"
    else
        echo "📊 未找到现有数据库，创建新的数据库..."
        # 运行完整的数据库初始化
        /app/.venv/bin/python /app/api/app/init_db.py || {
            echo "❌ 数据库初始化失败"
            exit 1
        }
        echo "✅ 新数据库创建完成"
    fi
fi

echo "✅ 数据库初始化完成"

# 标记初始化完成
touch /app/data/.db_initialized

exit 0
