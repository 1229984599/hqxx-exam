<template>
  <PageLayout
    title="权限管理指南"
    subtitle="详细了解如何在后台进行权限控制和菜单分配"
  >
    <div class="permission-guide">
      <!-- 权限管理流程 -->
      <el-card class="guide-card">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>权限管理流程</span>
          </div>
        </template>
        
        <el-steps :active="4" align-center>
          <el-step title="创建角色" description="定义系统角色" />
          <el-step title="分配权限" description="为角色分配权限" />
          <el-step title="创建用户" description="创建管理员账户" />
          <el-step title="分配角色" description="为用户分配角色" />
          <el-step title="权限生效" description="用户获得权限" />
        </el-steps>
      </el-card>

      <!-- 角色管理 -->
      <el-card class="guide-card">
        <template #header>
          <div class="card-header">
            <el-icon><UserFilled /></el-icon>
            <span>1. 角色管理</span>
          </div>
        </template>
        
        <div class="guide-content">
          <h4>如何创建和管理角色：</h4>
          <ol>
            <li>
              <strong>访问角色管理页面</strong>
              <p>导航到 "用户管理" → "角色权限" 页面</p>
            </li>
            <li>
              <strong>创建新角色</strong>
              <p>点击 "新增角色" 按钮，填写角色信息：</p>
              <ul>
                <li><strong>角色名称</strong>：如 "教师"、"学科管理员"</li>
                <li><strong>角色代码</strong>：如 "teacher"、"subject_admin"</li>
                <li><strong>描述</strong>：角色的详细说明</li>
              </ul>
            </li>
            <li>
              <strong>编辑角色</strong>
              <p>点击角色列表中的 "编辑" 按钮修改角色信息</p>
            </li>
          </ol>

          <el-alert
            title="注意事项"
            type="warning"
            :closable="false"
          >
            <ul>
              <li>角色代码创建后不能修改</li>
              <li>系统预设角色不能删除</li>
              <li>删除角色前请确保没有用户使用该角色</li>
            </ul>
          </el-alert>
        </div>
      </el-card>

      <!-- 权限分配 -->
      <el-card class="guide-card">
        <template #header>
          <div class="card-header">
            <el-icon><Lock /></el-icon>
            <span>2. 权限分配</span>
          </div>
        </template>
        
        <div class="guide-content">
          <h4>如何为角色分配权限：</h4>
          <ol>
            <li>
              <strong>打开权限管理</strong>
              <p>在角色列表中点击 "权限" 按钮</p>
            </li>
            <li>
              <strong>选择权限</strong>
              <p>在权限树中勾选需要的权限：</p>
              <div class="permission-tree-demo">
                <el-tree
                  :data="demoPermissionTree"
                  :props="{ children: 'children', label: 'label' }"
                  show-checkbox
                  node-key="id"
                  :default-checked-keys="[1, 2]"
                  class="demo-tree"
                />
              </div>
            </li>
            <li>
              <strong>保存权限</strong>
              <p>点击 "保存权限" 按钮确认分配</p>
            </li>
          </ol>

          <h4>权限分类说明：</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="试题管理">
              包含试题的查看、创建、编辑、删除、导出、批量操作权限
            </el-descriptions-item>
            <el-descriptions-item label="模板管理">
              包含模板的查看、创建、编辑、删除权限
            </el-descriptions-item>
            <el-descriptions-item label="基础数据">
              包含学期、年级、学科、分类的查看和编辑权限
            </el-descriptions-item>
            <el-descriptions-item label="用户管理">
              包含管理员的查看、创建、编辑、删除权限
            </el-descriptions-item>
            <el-descriptions-item label="系统管理">
              包含系统监控、配置、备份、日志权限
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>

      <!-- 用户管理 -->
      <el-card class="guide-card">
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>3. 用户管理</span>
          </div>
        </template>
        
        <div class="guide-content">
          <h4>如何创建和管理用户：</h4>
          <ol>
            <li>
              <strong>访问用户管理页面</strong>
              <p>导航到 "用户管理" → "管理员管理" 页面</p>
            </li>
            <li>
              <strong>创建新用户</strong>
              <p>点击 "添加管理员" 按钮，填写用户信息：</p>
              <ul>
                <li><strong>用户名</strong>：登录用户名</li>
                <li><strong>邮箱</strong>：用户邮箱地址</li>
                <li><strong>姓名</strong>：用户真实姓名</li>
                <li><strong>密码</strong>：登录密码</li>
                <li><strong>状态</strong>：是否激活</li>
                <li><strong>分配角色</strong>：选择用户角色</li>
              </ul>
            </li>
            <li>
              <strong>编辑用户</strong>
              <p>点击用户列表中的 "编辑" 按钮修改用户信息和角色</p>
            </li>
          </ol>

          <el-alert
            title="角色分配说明"
            type="info"
            :closable="false"
          >
            <ul>
              <li>一个用户可以分配多个角色</li>
              <li>用户将获得所有分配角色的权限</li>
              <li>超级管理员拥有所有权限，无需分配角色</li>
            </ul>
          </el-alert>
        </div>
      </el-card>

      <!-- 菜单控制 -->
      <el-card class="guide-card">
        <template #header>
          <div class="card-header">
            <el-icon><Menu /></el-icon>
            <span>4. 菜单控制</span>
          </div>
        </template>
        
        <div class="guide-content">
          <h4>菜单如何根据权限显示：</h4>
          <p>系统采用基于角色的菜单控制，用户只能看到自己有权限访问的菜单项。</p>
          
          <h4>菜单权限映射：</h4>
          <el-table :data="menuPermissionData" border style="width: 100%">
            <el-table-column prop="menu" label="菜单项" width="150" />
            <el-table-column prop="roles" label="所需角色" />
            <el-table-column prop="description" label="说明" />
          </el-table>
        </div>
      </el-card>

      <!-- 权限测试 -->
      <el-card class="guide-card">
        <template #header>
          <div class="card-header">
            <el-icon><View /></el-icon>
            <span>5. 权限测试</span>
          </div>
        </template>
        
        <div class="guide-content">
          <h4>如何测试权限配置：</h4>
          <ol>
            <li>
              <strong>创建测试用户</strong>
              <p>创建不同角色的测试用户</p>
            </li>
            <li>
              <strong>登录测试</strong>
              <p>使用测试用户登录系统，检查菜单显示</p>
            </li>
            <li>
              <strong>功能测试</strong>
              <p>测试各功能页面的访问权限</p>
            </li>
            <li>
              <strong>权限调试</strong>
              <p>使用开发工具检查权限状态</p>
            </li>
          </ol>

          <div class="debug-tools">
            <h4>权限调试工具：</h4>
            <el-button @click="checkCurrentPermissions">检查当前权限</el-button>
            <el-button @click="checkMenuPermissions">检查菜单权限</el-button>
            <el-button @click="generatePermissionReport">生成权限报告</el-button>
          </div>
        </div>
      </el-card>

      <!-- 常见问题 -->
      <el-card class="guide-card">
        <template #header>
          <div class="card-header">
            <el-icon><QuestionFilled /></el-icon>
            <span>常见问题</span>
          </div>
        </template>
        
        <div class="guide-content">
          <el-collapse v-model="activeCollapse">
            <el-collapse-item title="用户看不到某个菜单怎么办？" name="1">
              <p>检查以下几点：</p>
              <ol>
                <li>确认用户已分配相应角色</li>
                <li>确认角色已分配相应权限</li>
                <li>确认用户账户状态为激活</li>
                <li>重新登录系统</li>
              </ol>
            </el-collapse-item>
            
            <el-collapse-item title="如何批量分配权限？" name="2">
              <p>可以通过以下方式：</p>
              <ol>
                <li>创建标准角色模板</li>
                <li>为角色批量分配权限</li>
                <li>为用户批量分配角色</li>
              </ol>
            </el-collapse-item>
            
            <el-collapse-item title="权限修改后何时生效？" name="3">
              <p>权限修改的生效时间：</p>
              <ul>
                <li>角色权限修改：立即生效</li>
                <li>用户角色修改：需要重新登录</li>
                <li>菜单权限：实时更新</li>
              </ul>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref } from 'vue'
import { 
  Setting, UserFilled, Lock, User, Menu, View, QuestionFilled 
} from '@element-plus/icons-vue'
import { permissionDebugger } from '../utils/permissionDebug'
import PageLayout from '../components/PageLayout.vue'

const activeCollapse = ref(['1'])

// 演示权限树数据
const demoPermissionTree = [
  {
    id: 'questions',
    label: '试题管理',
    children: [
      { id: 1, label: '查看试题' },
      { id: 2, label: '创建试题' },
      { id: 3, label: '编辑试题' },
      { id: 4, label: '删除试题' }
    ]
  },
  {
    id: 'templates',
    label: '模板管理',
    children: [
      { id: 5, label: '查看模板' },
      { id: 6, label: '创建模板' }
    ]
  }
]

// 菜单权限映射数据
const menuPermissionData = [
  { menu: '仪表板', roles: '所有用户', description: '系统首页，所有登录用户可访问' },
  { menu: '基础管理', roles: 'admin, subject_admin', description: '学期、年级、学科、分类管理' },
  { menu: '试题管理', roles: 'admin, teacher, subject_admin', description: '试题查看和管理' },
  { menu: '模板管理', roles: 'admin, teacher, subject_admin', description: '模板查看和管理' },
  { menu: '用户管理', roles: 'super_admin, admin', description: '管理员和角色管理' },
  { menu: '系统管理', roles: 'super_admin, admin', description: '系统监控和配置' }
]

// 调试方法
function checkCurrentPermissions() {
  permissionDebugger.printUserPermissions()
}

function checkMenuPermissions() {
  permissionDebugger.checkMenuPermissions()
}

function generatePermissionReport() {
  permissionDebugger.generatePermissionReport()
}
</script>

<style scoped>
.permission-guide {
  padding: 20px;
}

.guide-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.guide-content {
  line-height: 1.6;
}

.guide-content h4 {
  margin: 16px 0 8px 0;
  color: #303133;
}

.guide-content ol, .guide-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.guide-content li {
  margin: 4px 0;
}

.permission-tree-demo {
  margin: 16px 0;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 4px;
}

.demo-tree {
  background: white;
  border-radius: 4px;
  padding: 10px;
}

.debug-tools {
  margin-top: 16px;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 4px;
}

.debug-tools h4 {
  margin: 0 0 12px 0;
}

.debug-tools .el-button {
  margin-right: 8px;
}
</style>
