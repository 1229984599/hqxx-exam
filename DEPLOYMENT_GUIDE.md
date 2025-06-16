# 红旗小学考试系统 - 部署指南

## 🎯 快速部署

### 1. 构建Docker镜像
```bash
docker build -t hqxx-exam:latest .
```

### 2. 启动容器
```bash
docker run -d \
  --name hqxx-exam-container \
  --restart unless-stopped \
  -p 8080:80 \
  -v hqxx-exam-data:/app/data \
  hqxx-exam:latest
```

### 3. 访问系统
- **前台页面**: http://localhost:8080/
- **管理后台**: http://localhost:8080/admin/
- **API文档**: http://localhost:8080/api/docs

### 4. 默认登录信息
- **用户名**: admin
- **密码**: admin123

## 🔧 系统架构

### 服务组件
- **Nginx**: 反向代理和静态文件服务
- **FastAPI**: 后端API服务
- **SQLite**: 数据库
- **Redis**: 缓存服务（可选）

### 端口配置
- **80**: Nginx（容器内部）
- **8000**: FastAPI（容器内部）
- **6379**: Redis（容器内部）
- **8080**: 外部访问端口（可修改）

## 📊 数据持久化

### 数据卷
- **hqxx-exam-data**: 存储数据库文件和上传文件
- **路径**: `/app/data`

### 备份数据
```bash
# 备份数据卷
docker run --rm -v hqxx-exam-data:/data -v $(pwd):/backup alpine tar czf /backup/hqxx-exam-backup.tar.gz -C /data .

# 恢复数据
docker run --rm -v hqxx-exam-data:/data -v $(pwd):/backup alpine tar xzf /backup/hqxx-exam-backup.tar.gz -C /data
```

## 🚀 生产环境部署

### 1. 使用自定义端口
```bash
docker run -d \
  --name hqxx-exam \
  --restart unless-stopped \
  -p 80:80 \
  -v hqxx-exam-data:/app/data \
  hqxx-exam:latest
```

### 2. 使用Docker Compose
创建 `docker-compose.yml`:
```yaml
version: '3.8'
services:
  hqxx-exam:
    image: hqxx-exam:latest
    container_name: hqxx-exam
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - hqxx-exam-data:/app/data
    environment:
      - TZ=Asia/Shanghai

volumes:
  hqxx-exam-data:
```

启动：
```bash
docker-compose up -d
```

### 3. 环境变量配置
```bash
docker run -d \
  --name hqxx-exam \
  --restart unless-stopped \
  -p 8080:80 \
  -v hqxx-exam-data:/app/data \
  -e DATABASE_URL="sqlite:///app/data/app.db" \
  -e REDIS_URL="redis://localhost:6379" \
  -e TZ="Asia/Shanghai" \
  hqxx-exam:latest
```

## 🔍 故障排除

### 检查容器状态
```bash
docker ps
docker logs hqxx-exam-container
```

### 检查服务状态
```bash
# 进入容器
docker exec -it hqxx-exam-container sh

# 检查进程
ps aux

# 检查端口
netstat -tlnp

# 检查nginx配置
nginx -t -c /app/config/nginx.conf
```

### 常见问题

#### 1. 无法访问管理后台
- 确保访问 `http://localhost:8080/admin/`（注意末尾的斜杠）
- 检查nginx配置是否正确

#### 2. API请求404错误
- 检查nginx代理配置
- 确认FastAPI服务正在运行

#### 3. 数据库初始化失败
- 删除数据卷重新初始化：`docker volume rm hqxx-exam-data`
- 检查初始化日志：`docker exec hqxx-exam-container cat /var/log/supervisor/db_init.log`

#### 4. Redis连接失败
- 系统会自动降级到内存缓存
- 不影响基本功能

## 📝 维护操作

### 更新系统
```bash
# 停止容器
docker stop hqxx-exam-container

# 删除容器（保留数据）
docker rm hqxx-exam-container

# 重新构建镜像
docker build -t hqxx-exam:latest .

# 启动新容器
docker run -d \
  --name hqxx-exam-container \
  --restart unless-stopped \
  -p 8080:80 \
  -v hqxx-exam-data:/app/data \
  hqxx-exam:latest
```

### 重置数据库
```bash
# 删除数据卷
docker volume rm hqxx-exam-data

# 重新启动容器（会自动初始化）
docker restart hqxx-exam-container
```

### 查看日志
```bash
# 容器日志
docker logs -f hqxx-exam-container

# 服务日志
docker exec hqxx-exam-container tail -f /var/log/supervisor/supervisord.log
docker exec hqxx-exam-container tail -f /var/log/nginx/access.log
docker exec hqxx-exam-container tail -f /var/log/nginx/error.log
```

## 🎉 部署完成

系统部署完成后，你可以：

1. **访问前台页面**查看考试界面
2. **登录管理后台**管理题目和用户
3. **查看API文档**了解接口详情
4. **备份数据**确保数据安全

默认管理员账号：**admin / admin123**

请及时修改默认密码以确保系统安全！
