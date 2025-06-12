# 搜索筛选功能修复

## 🐛 问题描述

用户发现搜索和筛选时，发送的API请求根本没有筛选的字段。通过curl请求可以看到：

```bash
curl 'http://localhost:3000/api/v1/categories/' \
  -H 'Authorization: Bearer xxx'
```

请求中没有任何查询参数，如 `?search=xxx&subject_id=1&is_active=true` 等。

## 🔍 问题分析

### 根本原因
1. **useCrud.js 筛选字段限制**：原来的 `loadData` 函数只处理固定的 `search` 和 `is_active` 字段
2. **客户端筛选覆盖**：CategoryView.vue 和 GradeView.vue 重写了 `filteredData`，使用客户端筛选而不是服务端筛选
3. **筛选器参数传递问题**：CrudTable 组件的自动监听没有正确传递筛选器参数

### 具体问题
```javascript
// 原来的代码只处理固定字段
if (!clientFilter) {
  if (filters.search) queryParams.search = filters.search
  if (filters.is_active !== null) queryParams.is_active = filters.is_active
}
// 缺少 subject_id, level 等扩展字段
```

## ✅ 解决方案

### 1. 修改 useCrud.js - 支持动态筛选字段

**修改前**：
```javascript
if (!clientFilter) {
  // 服务端筛选
  if (filters.search) queryParams.search = filters.search
  if (filters.is_active !== null) queryParams.is_active = filters.is_active
}
```

**修改后**：
```javascript
if (!clientFilter) {
  // 服务端筛选 - 动态添加所有非空筛选字段
  Object.keys(filters).forEach(key => {
    const value = filters[key]
    if (value !== null && value !== undefined && value !== '') {
      queryParams[key] = value
    }
  })
}
```

### 2. 修改管理页面 - 使用服务端筛选

**CategoryView.vue 修改**：
```javascript
// 添加 clientFilter: false 配置
const crud = useCrud('/categories/', {
  // ... 其他配置
  clientFilter: false // 使用服务端筛选
})

// 移除客户端筛选逻辑
// 删除了重写 filteredData 的代码
```

**GradeView.vue 修改**：
```javascript
// 同样添加 clientFilter: false 配置
const crud = useCrud('/grades/', {
  // ... 其他配置
  clientFilter: false // 使用服务端筛选
})
```

### 3. 修改 CrudTable.vue - 正确传递筛选器

**修改前**：
```javascript
searchTimeout = setTimeout(() => {
  emit('search')
}, 300)
```

**修改后**：
```javascript
searchTimeout = setTimeout(() => {
  emit('search', { ...filters })
}, 300)
```

### 4. 增强 handleSearch 方法

**修改前**：
```javascript
function handleSearch() {
  if (pagination) {
    paginationData.page = 1
  }
  loadData()
}
```

**修改后**：
```javascript
function handleSearch(searchFilters = null) {
  // 如果传入了筛选器参数，更新本地筛选器
  if (searchFilters) {
    Object.assign(filters, searchFilters)
  }
  
  if (pagination) {
    paginationData.page = 1
  }
  loadData()
}
```

## 🔧 修改的文件

### 1. useCrud.js
- ✅ 修改 `loadData` 函数，支持动态筛选字段
- ✅ 增强 `handleSearch` 方法，支持接收筛选器参数

### 2. CategoryView.vue
- ✅ 添加 `clientFilter: false` 配置
- ✅ 移除客户端筛选逻辑
- ✅ 保留扩展筛选字段（subject_id）

### 3. GradeView.vue
- ✅ 添加 `clientFilter: false` 配置
- ✅ 移除客户端筛选逻辑
- ✅ 保留扩展筛选字段（level）

### 4. CrudTable.vue
- ✅ 修复自动监听时的筛选器参数传递

## 📋 预期效果

### 修复后的API请求示例

**分类管理页面**：
```bash
# 搜索 "数学"
GET /api/v1/categories/?search=数学

# 筛选数学学科
GET /api/v1/categories/?subject_id=1

# 组合筛选
GET /api/v1/categories/?search=基础&subject_id=1&is_active=true
```

**年级管理页面**：
```bash
# 搜索 "一年级"
GET /api/v1/grades/?search=一年级

# 筛选第1级
GET /api/v1/grades/?level=1

# 组合筛选
GET /api/v1/grades/?search=年级&level=1&is_active=true
```

**学期管理页面**：
```bash
# 搜索 "春季"
GET /api/v1/semesters/?search=春季

# 筛选启用状态
GET /api/v1/semesters/?is_active=true
```

## 🧪 测试验证

### 1. 功能测试
- [ ] 在分类管理页面输入搜索关键词，检查API请求是否包含 `search` 参数
- [ ] 选择学科筛选，检查API请求是否包含 `subject_id` 参数
- [ ] 在年级管理页面选择级别筛选，检查API请求是否包含 `level` 参数
- [ ] 组合多个筛选条件，检查API请求是否包含所有参数

### 2. 性能测试
- [ ] 验证防抖功能是否正常工作（300ms延迟）
- [ ] 检查是否有重复的API请求
- [ ] 验证筛选器变化时的响应速度

### 3. 兼容性测试
- [ ] 测试学期管理和学科管理页面是否正常工作
- [ ] 验证现有功能是否受到影响
- [ ] 检查分页功能是否正常

## 🎯 优化效果

### 1. 性能提升
- ✅ **服务端筛选**：减少数据传输量，提升响应速度
- ✅ **精确查询**：后端可以使用数据库索引优化查询
- ✅ **减少内存占用**：前端不需要加载所有数据进行筛选

### 2. 用户体验提升
- ✅ **实时筛选**：筛选器变化立即生效
- ✅ **快速响应**：300ms防抖优化
- ✅ **准确结果**：服务端筛选更准确

### 3. 代码质量提升
- ✅ **统一架构**：所有管理页面使用相同的筛选机制
- ✅ **可扩展性**：支持任意筛选字段，无需修改核心代码
- ✅ **维护性**：减少重复的客户端筛选逻辑

## 🔄 后续优化建议

1. **后端优化**：
   - 添加数据库索引优化查询性能
   - 实现更复杂的搜索功能（模糊匹配、多字段搜索）
   - 添加搜索结果高亮

2. **前端优化**：
   - 添加搜索历史记录
   - 实现高级搜索功能
   - 添加搜索建议/自动完成

3. **监控优化**：
   - 添加搜索性能监控
   - 统计常用搜索关键词
   - 优化热门搜索的缓存策略
