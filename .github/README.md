# GitHub Actions 工作流说明

本项目包含两个主要的GitHub Actions工作流，用于自动化Docker镜像构建和版本发布。

## 📋 工作流概览

### 1. Docker镜像构建 (`docker-build.yml`)

**触发条件：**
- 🔧 手动触发（支持强制构建选项）
- 📝 当以下文件发生变化时自动触发：
  - `api/pyproject.toml`（版本号变化）
  - `Dockerfile`
  - `api/**`、`admin/**`、`home/**`、`docker/**` 目录下的文件
- 🔀 Pull Request时构建（但不推送镜像）

**功能特性：**
- ✅ 自动检测版本号变化
- 🏗️ 多平台构建（linux/amd64, linux/arm64）
- 🏷️ 智能标签管理
- 🗑️ 自动清理旧镜像
- 📊 构建缓存优化

### 2. 版本发布 (`release.yml`)

**触发条件：**
- 🚀 GitHub Release发布时自动触发
- 🔧 手动触发（可创建新的Release）

**功能特性：**
- 📦 自动创建GitHub Release
- 🏷️ 版本标签验证
- 📝 自动生成更新日志
- 🐳 构建发布专用Docker镜像

## 🚀 使用方法

### 自动构建（推荐）

1. **版本更新触发：**
   ```bash
   # 修改版本号
   vim api/pyproject.toml
   # 将 version = "0.1.0" 改为 version = "0.1.1"
   
   # 提交更改
   git add api/pyproject.toml
   git commit -m "bump version to 0.1.1"
   git push
   ```

2. **文件变化触发：**
   - 修改任何相关文件（API代码、前端代码、Docker配置等）
   - 提交并推送到主分支
   - 工作流将自动运行

### 手动构建

1. **访问GitHub Actions页面：**
   ```
   https://github.com/你的用户名/你的仓库名/actions
   ```

2. **选择"构建Docker镜像"工作流**

3. **点击"Run workflow"按钮**

4. **选择构建选项：**
   - ☑️ 强制构建镜像：忽略版本检查，强制构建

### 版本发布

#### 方法一：手动创建Release

1. **使用GitHub Actions：**
   - 访问Actions页面
   - 选择"发布版本"工作流
   - 点击"Run workflow"
   - 填写发布信息：
     - 标签名称：`v1.0.0`
     - 发布名称：`版本 1.0.0`
     - 是否为草稿/预发布

#### 方法二：GitHub界面创建Release

1. **访问Releases页面：**
   ```
   https://github.com/你的用户名/你的仓库名/releases
   ```

2. **点击"Create a new release"**

3. **填写Release信息并发布**

4. **工作流将自动构建发布镜像**

## 🏷️ 镜像标签说明

### 开发构建标签
- `latest` - 最新的主分支构建
- `v0.1.0` - 具体版本号
- `main-abc1234` - 分支名+commit SHA
- `pr-123` - Pull Request编号

### 发布构建标签
- `latest` - 最新发布版本
- `stable` - 最新稳定版本（非预发布）
- `v1.0.0` - 发布标签
- `1.0.0` - 版本号

## 📦 使用Docker镜像

### 拉取镜像
```bash
# 拉取最新版本
docker pull ghcr.io/你的用户名/你的仓库名:latest

# 拉取指定版本
docker pull ghcr.io/你的用户名/你的仓库名:v1.0.0
```

### 运行容器
```bash
# 使用docker-compose（推荐）
docker-compose up -d

# 直接运行
docker run -d \
  --name hqxx-exam \
  -p 80:80 \
  ghcr.io/你的用户名/你的仓库名:latest
```

## ⚙️ 配置说明

### 环境变量
- `REGISTRY`: 容器注册表地址（默认：ghcr.io）
- `IMAGE_NAME`: 镜像名称（自动使用仓库名）

### 权限要求
工作流需要以下权限：
- `contents: read` - 读取代码
- `packages: write` - 推送镜像到GHCR
- `contents: write` - 创建Release（仅发布工作流）

### 缓存优化
- 使用GitHub Actions缓存加速构建
- 多阶段构建减少镜像大小
- 自动清理旧的未标记镜像

## 🔧 自定义配置

### 修改触发条件
编辑 `.github/workflows/docker-build.yml`：
```yaml
on:
  push:
    paths:
      - 'api/pyproject.toml'
      # 添加或移除监控路径
    branches:
      - main
      # 添加或移除监控分支
```

### 修改镜像标签
编辑工作流中的 `docker/metadata-action` 配置：
```yaml
tags: |
  type=raw,value=${{ needs.check-version.outputs.version }}
  # 添加自定义标签规则
```

### 修改构建平台
```yaml
platforms: linux/amd64,linux/arm64
# 添加或移除目标平台
```

## 📝 注意事项

1. **首次使用需要启用GitHub Packages**
2. **确保仓库设置中启用了Actions**
3. **私有仓库需要配置适当的访问权限**
4. **版本号格式应遵循语义化版本规范**
5. **大型项目建议调整缓存策略**

## 🐛 故障排除

### 常见问题

1. **权限错误：**
   - 检查仓库设置中的Actions权限
   - 确认GITHUB_TOKEN有足够权限

2. **构建失败：**
   - 检查Dockerfile语法
   - 查看构建日志中的错误信息

3. **版本检测失败：**
   - 确认pyproject.toml格式正确
   - 检查版本号格式是否符合要求

4. **镜像推送失败：**
   - 检查网络连接
   - 确认容器注册表权限

### 获取帮助
- 查看GitHub Actions运行日志
- 检查工作流文件语法
- 参考GitHub Actions官方文档
