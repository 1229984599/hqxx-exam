# 🎓 红旗小学考试管理系统 (HQXX Exam Management System)

一个功能完整的企业级考试管理解决方案，基于 FastAPI + Vue 3 构建。

## ✨ **系统特色**

- 🎯 **完整的试题管理** - 富文本编辑、批量操作、搜索筛选
- 🔐 **企业级权限控制** - 5角色22权限细粒度管理
- 📊 **实时系统监控** - CPU、内存、磁盘、网络监控
- 💾 **多重数据备份** - 本地+WebDAV远程备份
- ⚡ **高性能优化** - 数据库索引、虚拟滚动、懒加载
- 🎨 **现代化界面** - 响应式设计、Element Plus组件

## 🚀 **快速启动**

### Windows用户
```bash
start_system.bat
```

### Linux/Mac用户
```bash
chmod +x start_system.sh
./start_system.sh
```

### 访问地址
- **管理后台**: http://localhost:3001
- **API文档**: http://localhost:8000/docs
- **默认账号**: admin / admin123

## 📖 **详细文档**
- [快速启动指南](QUICK_START_GUIDE.md)
- [项目完成报告](PROJECT_FINAL_COMPLETION_REPORT.md)
- [性能优化报告](PERFORMANCE_PERMISSION_OPTIMIZATION_REPORT.md)

## 项目结构

```
hqxx-exam/
├── api/                    # 后端API服务 (FastAPI + Tortoise ORM)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPI应用入口
│   │   ├── config.py      # 配置文件
│   │   ├── models/        # 数据模型
│   │   ├── routers/       # API路由
│   │   ├── services/      # 业务逻辑
│   │   ├── utils/         # 工具函数
│   │   └── dependencies/  # 依赖注入
│   ├── pyproject.toml     # PDM项目配置
│   ├── requirements.txt   # 依赖列表
│   └── .env              # 环境变量
├── admin/                 # 后台管理前端 (Vue3)
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── router/        # 路由
│   │   ├── stores/        # 状态管理
│   │   ├── utils/         # 工具函数
│   │   └── main.js        # 应用入口
│   ├── package.json
│   └── vite.config.js
├── home/                  # 前台用户前端 (Vue3)
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── router/        # 路由
│   │   ├── stores/        # 状态管理
│   │   ├── utils/         # 工具函数
│   │   └── main.js        # 应用入口
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 功能特性

### 前台功能
- 🎯 **题目选择**: 根据学期、年级、学科、题目分类筛选试题
- 🎲 **随机出题**: 点击按钮随机显示当前分类的试题
- 🎨 **响应式设计**: 适配不同设备屏幕
- ⚙️ **快速切换**: 通过header设置按钮快速切换分类
- 🏫 **学校品牌**: 左上角显示学校logo

### 后台功能
- 🔐 **安全登录**: 管理员登录验证
- 📝 **富文本编辑**: 支持富文本编辑器添加和编辑题目
- 🔤 **拼音支持**: 内置拼音功能，方便语文题目编辑
- 📊 **分类管理**: 管理学期、年级、学科、题目分类
- 🗂️ **题目管理**: 增删改查试题

## 技术栈

### 后端
- **框架**: FastAPI
- **ORM**: Tortoise ORM
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **缓存**: Redis (可选)
- **包管理**: PDM
- **认证**: JWT

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **包管理**: pnpm
- **富文本编辑器**: Quill.js / TinyMCE

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- PDM
- pnpm

### 后端启动

```bash
# 进入API目录
cd api

# 安装PDM (如果未安装)
pip install pdm

# 安装依赖
pdm install

# 配置环境变量
cp .env.example .env

# 运行数据库迁移
pdm run python -m app.migrations

# 启动开发服务器
pdm run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前台启动

```bash
# 进入前台目录
cd home

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

### 后台启动

```bash
# 进入后台目录
cd admin

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库模型

### 核心实体
- **学期 (Semester)**: 管理学期信息
- **年级 (Grade)**: 管理年级信息
- **学科 (Subject)**: 管理学科信息
- **题目分类 (Category)**: 管理题目分类
- **试题 (Question)**: 存储具体试题内容
- **管理员 (Admin)**: 后台管理员账户

## 开发指南

### 代码规范
- 后端遵循 PEP 8 规范
- 前端使用 ESLint + Prettier
- 提交信息遵循 Conventional Commits

### 测试
```bash
# 后端测试
cd api && pdm run pytest

# 前端测试
cd home && pnpm test
cd admin && pnpm test
```

## 部署

### Docker部署
```bash
# 构建并启动所有服务
docker-compose up -d
```

### 手动部署
详见 `docs/deployment.md`

## 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。
