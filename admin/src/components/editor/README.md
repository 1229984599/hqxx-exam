# TinyMCE 富文本编辑器组件

## 📁 目录结构

```
admin/src/components/editor/
├── TinyMCEEditor.vue          # 主编辑器组件
├── README.md                  # 说明文档
├── config/
│   └── editorConfig.js        # 编辑器配置
├── composables/
│   └── useEditor.js           # 编辑器核心逻辑
├── dialogs/
│   ├── PreviewDialog.vue      # 响应式预览对话框
│   ├── StatsDialog.vue        # 内容统计对话框
│   ├── SymbolDialog.vue       # 符号插入对话框
│   └── TemplateDialog.vue     # 模板插入对话框
└── utils/
    ├── contentUtils.js        # 内容处理工具
    └── pinyinUtils.js         # 拼音处理工具
```

## 🚀 主要功能

### ✅ 已实现功能

#### 基础编辑功能
- 📝 富文本编辑（字体、颜色、对齐等）
- 🖼️ 图片上传和自动样式应用
- 📊 表格编辑和样式
- 🔗 链接插入和管理
- 📋 复制粘贴和格式处理

#### 拼音注音功能
- ➕ 为选中文字添加拼音注音
- ➖ 移除拼音注音
- 🧠 智能拼音（为所有中文字符自动添加拼音）
- ✏️ 双击编辑拼音（支持多音字）
- 🖱️ 右键快速切换拼音
- ⌨️ 键盘导航（方向键、Delete键）

#### 内容处理功能
- 📄 粘贴为纯文本（去除格式）
- 🧹 清理Word等外部格式
- 📏 字体大小快速调整（A+/A-按钮 + 快捷键）
- 📐 行间距调整
- 📊 内容统计（字数、段落、阅读时间等）

#### 用户体验功能
- 👁️ 响应式预览（多设备尺寸）
- 🔣 符号快速插入
- 📋 模板插入
- ⌨️ 快捷键支持
- 📈 实时字数统计
- 💾 自动保存

### 🔧 技术特性

#### 组件化设计
- 🧩 模块化拆分，便于维护
- 🔄 Composition API，逻辑复用
- 📦 独立的工具函数
- 🎨 统一的样式设计

#### 性能优化
- ⚡ 懒加载插件
- 🖼️ 图片自动优化
- 💾 智能缓存
- 📱 响应式设计

## 📖 使用方法

### 基本用法

```vue
<template>
  <TinyMCEEditor
    v-model="content"
    :height="400"
    :show-status-bar="true"
    :show-shortcuts="false"
    :auto-style-images="true"
    placeholder="请输入内容..."
  />
</template>

<script setup>
import { ref } from 'vue'
import TinyMCEEditor from '@/components/editor/TinyMCEEditor.vue'

const content = ref('')
</script>
```

### 属性配置

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `modelValue` | String | `''` | 编辑器内容 |
| `placeholder` | String | `'请输入内容...'` | 占位符文本 |
| `height` | Number/String | `400` | 编辑器高度 |
| `showStatusBar` | Boolean | `true` | 显示状态栏 |
| `showShortcuts` | Boolean | `false` | 显示快捷键提示 |
| `autoStyleImages` | Boolean | `true` | 自动应用图片样式 |
| `toolbarMode` | String | `'sliding'` | 工具栏模式 |
| `apiKey` | String | `'gpl'` | TinyMCE API密钥 |

## ⌨️ 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl/Cmd + +` | 增大字体 |
| `Ctrl/Cmd + -` | 减小字体 |
| `Shift + Enter` | 插入换行符 |
| `Ctrl/Cmd + Shift + V` | 粘贴纯文本 |
| `Ctrl/Cmd + Shift + X` | 清除格式 |

## 🎨 自定义样式

编辑器支持自定义CSS样式，可以通过修改 `config/editorConfig.js` 中的 `content_style` 来调整编辑器内容的样式。

## 🔌 扩展功能

### 添加新的工具栏按钮

在 `composables/useEditor.js` 的 `setupEditorButtons` 函数中添加：

```javascript
editor.ui.registry.addButton('custombutton', {
  text: '自定义',
  tooltip: '自定义功能',
  onAction: () => customFunction()
})
```

### 添加新的对话框

1. 在 `dialogs/` 目录下创建新的Vue组件
2. 在主组件中引入并使用
3. 在composable中添加对应的状态管理

## 🐛 问题排查

### 常见问题

1. **编辑器无法加载**
   - 检查TinyMCE资源文件是否正确加载
   - 确认API密钥配置正确

2. **拼音功能异常**
   - 检查pinyin-pro库是否正确安装
   - 确认中文字符编码正确

3. **图片上传失败**
   - 检查上传接口配置
   - 确认认证token有效

## 📝 更新日志

### v2.0.0 (2024-01-XX)
- ✅ 完成组件拆分重构
- ✅ 修复粘贴为文本功能
- ✅ 添加实时状态栏
- ✅ 优化拼音注音体验
- ✅ 改进响应式设计

### v1.0.0 (2024-01-XX)
- ✅ 基础富文本编辑功能
- ✅ 拼音注音功能
- ✅ 图片处理功能
- ✅ 内容统计功能

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License
