# 华侨小学考试系统 Docker 部署指南

## 🎯 概述

本项目提供了一个完整的单容器解决方案，包含：
- **前端**: Vue3 + Vite (用户界面)
- **管理后台**: Vue3 + Element Plus (管理界面)
- **后端API**: FastAPI + Tortoise ORM (Python)
- **Web服务器**: Nginx (反向代理和静态文件服务)
- **缓存**: Redis (API缓存)
- **进程管理**: Supervisord (多进程管理)
- **数据库**: SQLite (轻量级数据库)

## 🚀 快速开始

### 方法一：使用构建脚本（推荐）

```bash
# 给脚本执行权限
chmod +x docker/build.sh

# 运行构建脚本
./docker/build.sh
```

### 方法二：手动构建

```bash
# 构建镜像
docker build -t hqxx-exam:latest .

# 运行容器
docker run -d \
  --name hqxx-exam-container \
  --restart unless-stopped \
  -p 80:80 \
  -v hqxx-exam-data:/app/data \
  hqxx-exam:latest
```

### 方法三：使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📁 目录结构

```
/app/
├── api/                 # 后端API代码
├── static/              # 静态文件
│   ├── home/           # 前端构建文件
│   └── admin/          # 管理后台构建文件
├── config/             # 配置文件
│   ├── nginx.conf      # Nginx配置
│   ├── supervisord.conf # 进程管理配置
│   └── redis.conf      # Redis配置
├── scripts/            # 启动脚本
├── data/               # 数据目录（持久化）
└── .venv/              # Python虚拟环境
```

## 🔧 配置说明

### 端口配置
- **80**: Nginx (对外访问)
- **8000**: FastAPI (内部)
- **6379**: Redis (内部)

### 访问地址
- **前台页面**: http://localhost/
- **管理后台**: http://localhost/admin/
- **API文档**: http://localhost/api/docs
- **健康检查**: http://localhost/health

### 环境变量

可以通过环境变量自定义配置：

```bash
docker run -d \
  --name hqxx-exam-container \
  -p 80:80 \
  -e DATABASE_URL="sqlite:///app/data/app.db" \
  -e REDIS_URL="redis://localhost:6379" \
  -e SECRET_KEY="your-secret-key" \
  -v hqxx-exam-data:/app/data \
  hqxx-exam:latest
```

## 📊 监控和日志

### 查看容器状态
```bash
docker ps | grep hqxx-exam
```

### 查看日志
```bash
# 查看所有日志
docker logs hqxx-exam-container

# 实时查看日志
docker logs -f hqxx-exam-container

# 查看特定服务日志
docker exec hqxx-exam-container tail -f /var/log/supervisor/fastapi.log
docker exec hqxx-exam-container tail -f /var/log/supervisor/nginx.log
docker exec hqxx-exam-container tail -f /var/log/supervisor/redis.log
```

### 进入容器
```bash
docker exec -it hqxx-exam-container sh
```

### 健康检查
```bash
curl http://localhost/health
```

## 🔄 数据备份和恢复

### 备份数据
```bash
# 备份数据卷
docker run --rm -v hqxx-exam-data:/data -v $(pwd):/backup alpine tar czf /backup/hqxx-exam-backup.tar.gz -C /data .

# 或者直接复制数据库文件
docker cp hqxx-exam-container:/app/data/app.db ./app.db.backup
```

### 恢复数据
```bash
# 恢复数据卷
docker run --rm -v hqxx-exam-data:/data -v $(pwd):/backup alpine tar xzf /backup/hqxx-exam-backup.tar.gz -C /data

# 或者直接复制数据库文件
docker cp ./app.db.backup hqxx-exam-container:/app/data/app.db
docker restart hqxx-exam-container
```

## 🛠️ 故障排除

### 常见问题

1. **容器启动失败**
   ```bash
   # 查看详细错误信息
   docker logs hqxx-exam-container
   
   # 检查端口是否被占用
   netstat -tulpn | grep :80
   ```

2. **前端页面无法访问**
   ```bash
   # 检查Nginx状态
   docker exec hqxx-exam-container supervisorctl status nginx
   
   # 重启Nginx
   docker exec hqxx-exam-container supervisorctl restart nginx
   ```

3. **API接口报错**
   ```bash
   # 检查FastAPI状态
   docker exec hqxx-exam-container supervisorctl status fastapi
   
   # 查看API日志
   docker exec hqxx-exam-container tail -f /var/log/supervisor/fastapi.log
   ```

4. **Redis连接失败**
   ```bash
   # 检查Redis状态
   docker exec hqxx-exam-container supervisorctl status redis
   
   # 测试Redis连接
   docker exec hqxx-exam-container redis-cli ping
   ```

### 重启服务
```bash
# 重启所有服务
docker restart hqxx-exam-container

# 重启特定服务
docker exec hqxx-exam-container supervisorctl restart fastapi
docker exec hqxx-exam-container supervisorctl restart nginx
docker exec hqxx-exam-container supervisorctl restart redis
```

## 🔒 安全建议

1. **修改默认密钥**
   ```bash
   -e SECRET_KEY="your-very-secure-secret-key"
   ```

2. **使用HTTPS**
   - 在生产环境中配置SSL证书
   - 可以使用Nginx反向代理配置HTTPS

3. **限制访问**
   - 配置防火墙规则
   - 使用VPN或内网访问

4. **定期备份**
   - 设置自动备份计划
   - 定期测试恢复流程

## 📈 性能优化

1. **资源限制**
   ```bash
   docker run -d \
     --name hqxx-exam-container \
     --memory="1g" \
     --cpus="1.0" \
     -p 80:80 \
     hqxx-exam:latest
   ```

2. **缓存配置**
   - Redis内存限制已设置为128MB
   - 可根据需要调整缓存策略

3. **数据库优化**
   - 定期清理日志文件
   - 监控数据库大小

## 📞 技术支持

如果遇到问题，请：
1. 查看日志文件获取详细错误信息
2. 检查系统资源使用情况
3. 确认网络连接正常
4. 联系技术支持团队

---

**版本**: v1.0.0  
**更新时间**: 2024-12-XX  
**维护者**: 开发团队
