<template>
  <div class="permission-help">
    <div class="page-header">
      <h1>权限说明</h1>
      <p class="subtitle">了解系统权限体系和使用方法</p>
    </div>

    <el-row :gutter="20">
      <!-- 当前用户权限 -->
      <el-col :span="8">
        <el-card class="permission-card">
          <template #header>
            <div class="card-header">
              <el-icon><UserFilled /></el-icon>
              <span>当前权限</span>
            </div>
          </template>
          
          <div class="user-info">
            <div class="info-item">
              <label>用户名:</label>
              <span>{{ authStore.user?.username }}</span>
            </div>
            <div class="info-item">
              <label>角色:</label>
              <el-tag 
                v-for="role in authStore.roles" 
                :key="role.id" 
                type="primary" 
                size="small"
                style="margin-right: 8px;"
              >
                {{ role.name }}
              </el-tag>
            </div>
            <div class="info-item">
              <label>超级管理员:</label>
              <el-tag :type="authStore.isSuperuser ? 'success' : 'info'" size="small">
                {{ authStore.isSuperuser ? '是' : '否' }}
              </el-tag>
            </div>
          </div>

          <el-divider />

          <div class="permission-list">
            <h4>拥有的权限 ({{ authStore.permissions.length }})</h4>
            <div class="permission-tags">
              <el-tag 
                v-for="permission in authStore.permissions" 
                :key="permission"
                size="small"
                class="permission-tag"
              >
                {{ getPermissionName(permission) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 权限说明 -->
      <el-col :span="16">
        <el-card class="permission-card">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>权限说明</span>
            </div>
          </template>

          <el-collapse v-model="activeCollapse">
            <el-collapse-item 
              v-for="category in permissionCategories" 
              :key="category.key"
              :title="category.title" 
              :name="category.key"
            >
              <div class="permission-category">
                <p class="category-description">{{ category.description }}</p>
                
                <div class="permission-items">
                  <div 
                    v-for="permission in category.permissions" 
                    :key="permission.code"
                    class="permission-item"
                    :class="{ 'has-permission': hasPermission(permission.code) }"
                  >
                    <div class="permission-header">
                      <el-icon v-if="hasPermission(permission.code)" class="permission-icon success">
                        <Check />
                      </el-icon>
                      <el-icon v-else class="permission-icon disabled">
                        <Close />
                      </el-icon>
                      <span class="permission-name">{{ permission.name }}</span>
                      <el-tag size="small" class="permission-code">{{ permission.code }}</el-tag>
                    </div>
                    <p class="permission-description">{{ permission.description }}</p>
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-col>
    </el-row>

    <!-- 权限申请说明 -->
    <el-card class="permission-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <el-icon><QuestionFilled /></el-icon>
          <span>如何获取权限</span>
        </div>
      </template>

      <el-steps :active="2" align-center>
        <el-step title="联系管理员" description="联系系统管理员或超级管理员" />
        <el-step title="说明需求" description="说明需要访问的功能模块" />
        <el-step title="分配角色" description="管理员为您分配相应角色" />
        <el-step title="重新登录" description="重新登录系统生效" />
      </el-steps>

      <el-alert
        title="权限申请提示"
        type="info"
        style="margin-top: 20px;"
        :closable="false"
      >
        <template #default>
          <p>如果您需要更多权限，请联系系统管理员。在申请时，请说明：</p>
          <ul>
            <li>您的工作职责和需要访问的功能</li>
            <li>具体需要的权限模块（如试题管理、模板管理等）</li>
            <li>使用权限的时间范围</li>
          </ul>
        </template>
      </el-alert>
    </el-card>

    <!-- 开发调试工具 -->
    <el-card v-if="isDev" class="permission-card debug-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <el-icon><Tools /></el-icon>
          <span>开发调试工具</span>
        </div>
      </template>

      <div class="debug-tools">
        <el-button @click="printUserPermissions">打印用户权限</el-button>
        <el-button @click="checkMenuPermissions">检查菜单权限</el-button>
        <el-button @click="generateReport">生成权限报告</el-button>
      </div>

      <el-alert
        title="开发环境专用"
        type="warning"
        style="margin-top: 10px;"
        :closable="false"
      >
        这些工具仅在开发环境可用，可以帮助调试权限问题。请打开浏览器控制台查看输出。
      </el-alert>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  UserFilled, Document, QuestionFilled, Tools, Check, Close 
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { usePermissions } from '../composables/usePermissions'
import { PERMISSIONS } from '../utils/menuConfig'
import { permissionDebugger } from '../utils/permissionDebug'

const authStore = useAuthStore()
const { hasPermission } = usePermissions()

const activeCollapse = ref(['questions', 'templates'])
const isDev = import.meta.env.DEV

// 权限分类
const permissionCategories = [
  {
    key: 'questions',
    title: '试题管理权限',
    description: '管理试题的创建、编辑、删除和导出等操作',
    permissions: [
      { code: PERMISSIONS.QUESTIONS_VIEW, name: '查看试题', description: '可以浏览和搜索试题列表' },
      { code: PERMISSIONS.QUESTIONS_CREATE, name: '创建试题', description: '可以添加新的试题' },
      { code: PERMISSIONS.QUESTIONS_EDIT, name: '编辑试题', description: '可以修改现有试题内容' },
      { code: PERMISSIONS.QUESTIONS_DELETE, name: '删除试题', description: '可以删除试题' },
      { code: PERMISSIONS.QUESTIONS_EXPORT, name: '导出试题', description: '可以导出试题数据' },
      { code: PERMISSIONS.QUESTIONS_BATCH, name: '批量操作', description: '可以批量处理试题' }
    ]
  },
  {
    key: 'templates',
    title: '模板管理权限',
    description: '管理试题模板和教学模板',
    permissions: [
      { code: PERMISSIONS.TEMPLATES_VIEW, name: '查看模板', description: '可以浏览模板列表' },
      { code: PERMISSIONS.TEMPLATES_CREATE, name: '创建模板', description: '可以创建新模板' },
      { code: PERMISSIONS.TEMPLATES_EDIT, name: '编辑模板', description: '可以修改模板内容' },
      { code: PERMISSIONS.TEMPLATES_DELETE, name: '删除模板', description: '可以删除模板' }
    ]
  },
  {
    key: 'basic_data',
    title: '基础数据权限',
    description: '管理学期、年级、学科、分类等基础数据',
    permissions: [
      { code: PERMISSIONS.BASIC_DATA_VIEW, name: '查看基础数据', description: '可以查看学期、年级、学科等信息' },
      { code: PERMISSIONS.BASIC_DATA_EDIT, name: '编辑基础数据', description: '可以修改基础数据设置' }
    ]
  },
  {
    key: 'admins',
    title: '用户管理权限',
    description: '管理系统用户和角色权限',
    permissions: [
      { code: PERMISSIONS.ADMINS_VIEW, name: '查看用户', description: '可以查看管理员列表' },
      { code: PERMISSIONS.ADMINS_CREATE, name: '创建用户', description: '可以创建新的管理员账户' },
      { code: PERMISSIONS.ADMINS_EDIT, name: '编辑用户', description: '可以修改用户信息' },
      { code: PERMISSIONS.ADMINS_DELETE, name: '删除用户', description: '可以删除用户账户' }
    ]
  },
  {
    key: 'system',
    title: '系统管理权限',
    description: '系统配置、监控、备份等高级功能',
    permissions: [
      { code: PERMISSIONS.SYSTEM_VIEW, name: '系统监控', description: '可以查看系统状态和统计信息' },
      { code: PERMISSIONS.SYSTEM_CONFIG, name: '系统配置', description: '可以修改系统设置' },
      { code: PERMISSIONS.SYSTEM_BACKUP, name: '数据备份', description: '可以创建和管理数据备份' },
      { code: PERMISSIONS.SYSTEM_LOGS, name: '系统日志', description: '可以查看系统操作日志' }
    ]
  }
]

// 获取权限名称
function getPermissionName(permissionCode) {
  for (const category of permissionCategories) {
    const permission = category.permissions.find(p => p.code === permissionCode)
    if (permission) {
      return permission.name
    }
  }
  return permissionCode
}

// 调试工具方法
function printUserPermissions() {
  permissionDebugger.printUserPermissions()
}

function checkMenuPermissions() {
  permissionDebugger.checkMenuPermissions()
}

function generateReport() {
  permissionDebugger.generatePermissionReport()
}
</script>

<style scoped>
.permission-help {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.permission-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.user-info .info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.user-info .info-item label {
  width: 100px;
  font-weight: 500;
  color: #606266;
}

.permission-list h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.permission-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.permission-tag {
  margin: 0;
}

.permission-category {
  padding: 16px 0;
}

.category-description {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 14px;
}

.permission-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.permission-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  transition: all 0.3s;
}

.permission-item.has-permission {
  border-color: #67c23a;
  background-color: #f0f9ff;
}

.permission-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.permission-icon.success {
  color: #67c23a;
}

.permission-icon.disabled {
  color: #c0c4cc;
}

.permission-name {
  font-weight: 500;
  color: #303133;
}

.permission-code {
  margin-left: auto;
  font-family: monospace;
}

.permission-description {
  margin: 0;
  color: #606266;
  font-size: 13px;
}

.debug-card {
  border: 2px dashed #e6a23c;
}

.debug-tools {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
</style>
