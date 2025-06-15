# 红旗小学考试系统 - 前台页面

这是红旗小学考试系统的前台页面，供学生进行试题练习使用。

## 功能特性

- 🎯 **智能配置**：支持学期、年级、学科、分类的灵活选择
- 📚 **丰富题库**：涵盖各个学科的精选试题
- 🔄 **随机出题**：智能推荐，避免重复练习
- 💡 **即时反馈**：实时查看答案，快速提升学习效果
- 📱 **响应式设计**：支持桌面端和移动端访问
- 🎨 **美观界面**：使用DaisyUI设计，界面简洁美观

## 技术栈

- **前端框架**：Vue 3 + Composition API
- **路由管理**：Vue Router 4
- **状态管理**：Pinia + pinia-plugin-persistedstate
- **UI组件库**：DaisyUI + Tailwind CSS
- **HTTP客户端**：Axios
- **构建工具**：Vite
- **包管理器**：pnpm

## 快速开始

### 方法一：一键启动（推荐）

```bash
# 在项目根目录运行
start_home.bat
```

这个脚本会自动：
- 检查环境依赖
- 启动后端API服务
- 启动前端开发服务器
- 配置代理连接

### 方法二：手动启动

#### 1. 启动后端服务

```bash
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. 启动前端服务

```bash
cd home
pnpm install
pnpm dev
```

### 访问地址

- 前台页面：http://localhost:3002
- 后端API：http://127.0.0.1:8000
- API文档：http://127.0.0.1:8000/docs
- API测试页面：test_api.html

### 构建生产版本

```bash
cd home
pnpm build
```

## 项目结构

```
home/
├── public/                 # 静态资源
│   └── logo.png           # 学校logo
├── src/
│   ├── components/        # 组件
│   │   ├── Header.vue     # 头部组件
│   │   └── ConfigDialog.vue # 配置对话框
│   ├── views/             # 页面
│   │   ├── Home.vue       # 首页配置
│   │   └── Questions.vue  # 试题页面
│   ├── stores/            # 状态管理
│   │   ├── config.js      # 配置状态
│   │   └── questions.js   # 试题状态
│   ├── utils/             # 工具函数
│   │   └── api.js         # API接口
│   ├── router/            # 路由配置
│   │   └── index.js
│   ├── App.vue            # 根组件
│   ├── main.js            # 入口文件
│   └── style.css          # 全局样式
├── package.json           # 项目配置
├── vite.config.js         # Vite配置
├── tailwind.config.js     # Tailwind配置
└── README.md              # 项目说明
```

## 使用说明

### 1. 首页配置

- 选择学期、年级、学科、分类
- 所有选项都是必选的
- 配置完成后点击"开始练习"

### 2. 试题练习

- 查看当前试题内容
- 点击"参考答案"查看答案
- 使用右下角的刷新按钮获取新题目
- 点击"换一题"按钮随机获取题目

### 3. 设置修改

- 点击右上角的设置按钮
- 在弹出的对话框中修改配置
- 保存后会自动重新加载试题

## API接口

前台页面通过以下API与后端通信：

- `GET /api/v1/semesters/` - 获取学期列表
- `GET /api/v1/grades/` - 获取年级列表  
- `GET /api/v1/subjects/` - 获取学科列表
- `GET /api/v1/categories/` - 获取分类列表
- `GET /api/v1/questions/` - 获取试题列表
- `GET /api/v1/questions/random` - 随机获取试题

## 开发说明

### 状态管理

使用Pinia进行状态管理，主要包含：

- **configStore**：管理用户配置（学期、年级、学科、分类）
- **questionsStore**：管理试题数据和当前显示的试题

### 数据持久化

使用pinia-plugin-persistedstate插件，用户的配置选择会自动保存到本地存储。

### 样式设计

- 使用Tailwind CSS + DaisyUI
- 响应式设计，支持移动端
- 自定义滚动条样式
- 平滑的动画效果

## 注意事项

1. 确保后端API服务正常运行（默认端口8000）
2. 前台页面默认运行在端口3002
3. 需要先完成配置选择才能进行试题练习
4. 试题内容支持富文本显示，包括图片、表格等

## 故障排除

### 1. API连接失败 (ECONNREFUSED)

**问题**：前端显示连接错误，无法获取数据

**解决方案**：
```bash
# 1. 检查后端服务是否启动
netstat -an | findstr :8000

# 2. 手动启动后端服务
cd api
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 3. 测试API连接
# 打开 test_api.html 文件进行连接测试
```

### 2. 前端依赖安装失败

```bash
# 清除缓存重新安装
cd home
rmdir /s node_modules
del pnpm-lock.yaml
pnpm install
```

### 3. 端口冲突

```bash
# 如果3002端口被占用，修改 home/vite.config.js 中的端口号
# 如果8000端口被占用，修改后端启动命令的端口号
```

### 4. 页面样式异常

- 检查浏览器控制台错误信息
- 确保Tailwind CSS和DaisyUI正确加载
- 清除浏览器缓存

### 5. 数据库连接问题

```bash
# 检查数据库服务状态
cd api
python -c "from app.database import engine; print('数据库连接正常')"
```

### 6. 使用API测试工具

打开项目根目录的 `test_api.html` 文件，可以：
- 测试后端服务连接
- 验证各个API接口
- 查看详细错误信息

## 联系方式

如有问题请联系系统管理员。
