# GitHub Actions Docker构建工作流设置指南

## 📁 已创建的文件

本次设置创建了以下文件：

```
.github/
├── workflows/
│   ├── docker-build.yml    # 主要的Docker构建工作流
│   └── release.yml         # 版本发布工作流
├── scripts/
│   └── check-version.sh    # 本地版本检测脚本
├── README.md               # 工作流使用说明
└── SETUP.md               # 本文件
```

## 🚀 快速开始

### 1. 启用GitHub Actions

1. 访问你的GitHub仓库
2. 点击 **Settings** 标签
3. 在左侧菜单中选择 **Actions** > **General**
4. 确保选择了 **Allow all actions and reusable workflows**

### 2. 启用GitHub Container Registry

1. 在仓库设置中，选择 **Actions** > **General**
2. 向下滚动到 **Workflow permissions**
3. 选择 **Read and write permissions**
4. 勾选 **Allow GitHub Actions to create and approve pull requests**

### 3. 测试工作流

#### 方法一：修改版本号触发
```bash
# 编辑版本号
vim api/pyproject.toml
# 将 version = "0.1.0" 改为 version = "0.1.1"

# 提交更改
git add api/pyproject.toml
git commit -m "bump version to 0.1.1"
git push origin main
```

#### 方法二：手动触发
1. 访问 `https://github.com/你的用户名/你的仓库名/actions`
2. 选择 **构建Docker镜像** 工作流
3. 点击 **Run workflow** 按钮
4. 选择分支并点击 **Run workflow**

## 🔧 配置说明

### 工作流触发条件

**自动触发：**
- `api/pyproject.toml` 文件变化（版本号更新）
- `Dockerfile` 文件变化
- `api/`、`admin/`、`home/`、`docker/` 目录下文件变化
- 推送到 `main`、`master`、`develop` 分支

**手动触发：**
- 支持强制构建选项
- 可以在任何分支上运行

### 镜像标签策略

| 触发方式 | 标签 | 说明 |
|---------|------|------|
| 版本更新 | `v0.1.0`, `latest` | 使用pyproject.toml中的版本号 |
| 分支推送 | `main`, `develop` | 使用分支名 |
| PR构建 | `pr-123` | 使用PR编号 |
| 手动构建 | `main-abc1234` | 分支名+commit SHA |

### 版本发布流程

1. **更新版本号：**
   ```bash
   # 编辑 api/pyproject.toml
   version = "1.0.0"
   ```

2. **提交并推送：**
   ```bash
   git add api/pyproject.toml
   git commit -m "release: version 1.0.0"
   git push origin main
   ```

3. **创建Release：**
   - 方式一：使用GitHub界面创建Release
   - 方式二：使用Actions手动触发发布工作流

## 🏷️ 使用构建的镜像

### 拉取镜像
```bash
# 拉取最新版本
docker pull ghcr.io/你的用户名/hqxx-exam:latest

# 拉取指定版本
docker pull ghcr.io/你的用户名/hqxx-exam:0.1.0
```

### 更新docker-compose.yml
```yaml
version: '3.8'
services:
  app:
    image: ghcr.io/你的用户名/hqxx-exam:latest
    # 或指定版本
    # image: ghcr.io/你的用户名/hqxx-exam:0.1.0
    ports:
      - "80:80"
```

## 🛠️ 本地测试

### 使用版本检测脚本
```bash
# 在Linux/macOS上
chmod +x .github/scripts/check-version.sh
./.github/scripts/check-version.sh

# 在Windows上（使用Git Bash）
bash .github/scripts/check-version.sh
```

### 本地构建测试
```bash
# 构建镜像
docker build -t hqxx-exam:local .

# 运行测试
docker run -d --name test-app -p 8080:80 hqxx-exam:local

# 测试健康检查
curl http://localhost:8080/api/health

# 清理
docker stop test-app && docker rm test-app
```

## 📊 监控和维护

### 查看构建状态
- 访问 Actions 页面查看构建历史
- 检查构建日志排查问题
- 监控镜像大小和构建时间

### 清理旧镜像
工作流会自动清理：
- 保留最近10个版本
- 删除未标记的镜像
- 可在工作流中调整清理策略

### 性能优化建议
1. **启用构建缓存** - 已在工作流中配置
2. **多阶段构建** - 已在Dockerfile中实现
3. **并行构建** - 支持多平台并行构建
4. **依赖缓存** - 前端和后端依赖分别缓存

## 🔒 安全考虑

### 权限最小化
- 工作流只请求必要的权限
- 使用GitHub提供的GITHUB_TOKEN
- 不需要额外的secrets配置

### 镜像安全
- 使用非root用户运行
- 定期更新基础镜像
- 启用健康检查

## 🐛 故障排除

### 常见问题

1. **权限错误：**
   ```
   Error: denied: permission_denied
   ```
   **解决方案：** 检查仓库Actions权限设置

2. **版本检测失败：**
   ```
   Error: Cannot find version in pyproject.toml
   ```
   **解决方案：** 确认pyproject.toml格式正确

3. **构建超时：**
   ```
   Error: The operation was canceled
   ```
   **解决方案：** 检查网络连接，考虑增加超时时间

4. **镜像推送失败：**
   ```
   Error: failed to push to registry
   ```
   **解决方案：** 检查GHCR权限和网络连接

### 获取支持
- 查看GitHub Actions文档
- 检查工作流运行日志
- 参考项目的Issues页面

## 📝 下一步

1. **测试工作流** - 提交一个版本更新测试自动构建
2. **配置通知** - 设置构建状态通知
3. **集成部署** - 连接到生产环境自动部署
4. **监控设置** - 配置镜像使用监控

## 🎉 完成

GitHub Actions Docker构建工作流已经设置完成！现在你可以：

- ✅ 自动构建Docker镜像
- ✅ 智能版本检测
- ✅ 多平台支持
- ✅ 自动标签管理
- ✅ 版本发布流程
- ✅ 镜像清理维护

享受自动化的开发体验吧！🚀
