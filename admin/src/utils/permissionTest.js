/**
 * 权限系统测试工具
 * 用于验证权限配置和功能是否正常工作
 */

import { useAuthStore } from '../stores/auth'

export class PermissionTester {
  constructor() {
    this.authStore = useAuthStore()
  }

  /**
   * 测试用户权限
   */
  testUserPermissions() {
    console.group('🔍 用户权限测试')
    
    const user = this.authStore.user
    const permissions = this.authStore.permissions
    const roles = this.authStore.roles
    
    console.log('👤 当前用户:', user?.username)
    console.log('🎭 用户角色:', roles.map(r => r.code))
    console.log('🔑 用户权限:', permissions)
    console.log('👑 超级管理员:', this.authStore.isSuperuser)
    
    console.groupEnd()
  }

  /**
   * 测试具体权限
   */
  testSpecificPermissions() {
    console.group('🎯 具体权限测试')
    
    const testPermissions = [
      'questions:view',
      'questions:create', 
      'questions:edit',
      'questions:delete',
      'templates:view',
      'templates:create',
      'templates:edit', 
      'templates:delete',
      'basic_data:view',
      'basic_data:edit',
      'admins:view',
      'admins:create',
      'admins:edit',
      'admins:delete',
      'system:view',
      'system:config'
    ]

    testPermissions.forEach(permission => {
      const hasPermission = this.authStore.hasPermission(permission)
      console.log(`${hasPermission ? '✅' : '❌'} ${permission}`)
    })
    
    console.groupEnd()
  }

  /**
   * 测试角色权限
   */
  testRolePermissions() {
    console.group('🎭 角色权限测试')
    
    const testRoles = [
      'super_admin',
      'admin', 
      'subject_admin',
      'teacher',
      'viewer'
    ]

    testRoles.forEach(role => {
      const hasRole = this.authStore.hasRole(role)
      console.log(`${hasRole ? '✅' : '❌'} ${role}`)
    })
    
    console.groupEnd()
  }

  /**
   * 测试页面权限
   */
  testPagePermissions() {
    console.group('📄 页面权限测试')
    
    const pagePermissions = {
      '试题管理': ['questions:view'],
      '试题创建': ['questions:create'],
      '试题编辑': ['questions:edit'],
      '模板管理': ['templates:view'],
      '模板创建': ['templates:create'],
      '模板编辑': ['templates:edit'],
      '基础数据管理': ['basic_data:edit'],
      '管理员管理': ['admins:view'],
      '角色管理': ['admins:view'],
      '系统监控': ['system:view'],
      '系统设置': ['system:config']
    }

    Object.entries(pagePermissions).forEach(([pageName, requiredPermissions]) => {
      const hasAccess = this.authStore.hasAnyPermission(requiredPermissions)
      console.log(`${hasAccess ? '✅' : '❌'} ${pageName} (需要: ${requiredPermissions.join(', ')})`)
    })
    
    console.groupEnd()
  }

  /**
   * 生成权限报告
   */
  generateReport() {
    console.group('📊 权限系统完整报告')
    
    this.testUserPermissions()
    this.testRolePermissions()
    this.testSpecificPermissions()
    this.testPagePermissions()
    
    console.groupEnd()
    
    // 返回报告数据
    return {
      user: this.authStore.user,
      roles: this.authStore.roles,
      permissions: this.authStore.permissions,
      isSuperuser: this.authStore.isSuperuser,
      timestamp: new Date().toISOString()
    }
  }

  /**
   * 模拟权限变更测试
   */
  async simulatePermissionChange() {
    console.group('🔄 权限变更测试')
    
    console.log('当前权限数量:', this.authStore.permissions.length)
    
    // 模拟权限刷新
    try {
      await this.authStore.fetchPermissions()
      console.log('✅ 权限刷新成功')
      console.log('刷新后权限数量:', this.authStore.permissions.length)
    } catch (error) {
      console.error('❌ 权限刷新失败:', error)
    }
    
    console.groupEnd()
  }

  /**
   * 测试权限指令
   */
  testPermissionDirectives() {
    console.group('🎨 权限指令测试')
    
    // 创建测试元素
    const testElement = document.createElement('div')
    testElement.textContent = '测试按钮'
    testElement.style.padding = '8px 16px'
    testElement.style.background = '#409eff'
    testElement.style.color = 'white'
    testElement.style.borderRadius = '4px'
    testElement.style.margin = '4px'
    testElement.style.display = 'inline-block'
    
    // 测试不同权限
    const testPermissions = [
      'questions:create',
      'templates:edit', 
      'admins:delete',
      'nonexistent:permission'
    ]
    
    testPermissions.forEach(permission => {
      const element = testElement.cloneNode(true)
      element.textContent = `测试 ${permission}`
      
      const hasPermission = this.authStore.hasPermission(permission)
      element.style.display = hasPermission ? 'inline-block' : 'none'
      
      console.log(`${hasPermission ? '✅' : '❌'} ${permission} - 元素${hasPermission ? '显示' : '隐藏'}`)
    })
    
    console.groupEnd()
  }

  /**
   * 完整测试套件
   */
  runFullTest() {
    console.clear()
    console.log('🚀 开始权限系统完整测试...')
    console.log('=' .repeat(50))
    
    this.generateReport()
    this.testPermissionDirectives()
    this.simulatePermissionChange()
    
    console.log('=' .repeat(50))
    console.log('✅ 权限系统测试完成')
  }
}

// 创建全局测试实例
export const permissionTester = new PermissionTester()

// 在开发环境下挂载到全局
if (import.meta.env.DEV) {
  window.permissionTester = permissionTester
  
  // 提供快捷方法
  window.testPermissions = () => permissionTester.runFullTest()
  window.checkPermission = (permission) => {
    const hasPermission = permissionTester.authStore.hasPermission(permission)
    console.log(`${hasPermission ? '✅' : '❌'} ${permission}`)
    return hasPermission
  }
  window.checkRole = (role) => {
    const hasRole = permissionTester.authStore.hasRole(role)
    console.log(`${hasRole ? '✅' : '❌'} ${role}`)
    return hasRole
  }
}
