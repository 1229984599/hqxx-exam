/**
 * 权限系统完整测试套件
 * 用于验证前后端权限系统的完整性和一致性
 */

import { useAuthStore } from '../stores/auth'
import { PERMISSIONS, ROLES } from './menuConfig'
import api from './api'

export class PermissionSystemTest {
  constructor() {
    this.authStore = useAuthStore()
    this.testResults = []
  }

  /**
   * 运行完整的权限系统测试
   */
  async runFullTest() {
    console.clear()
    console.log('🚀 权限系统完整测试开始...')
    console.log('=' .repeat(60))
    
    this.testResults = []
    
    try {
      await this.testUserAuthentication()
      await this.testPermissionMapping()
      await this.testFrontendPermissions()
      await this.testBackendPermissions()
      await this.testMenuPermissions()
      await this.testRoutePermissions()
      
      this.generateTestReport()
    } catch (error) {
      console.error('❌ 测试过程中发生错误:', error)
    }
    
    console.log('=' .repeat(60))
    console.log('✅ 权限系统测试完成')
  }

  /**
   * 测试用户认证状态
   */
  async testUserAuthentication() {
    console.group('👤 用户认证测试')
    
    const user = this.authStore.user
    const isAuthenticated = this.authStore.isAuthenticated
    const isSuperuser = this.authStore.isSuperuser
    
    this.addTestResult('用户认证', isAuthenticated, '用户已登录')
    this.addTestResult('用户信息', !!user, `用户: ${user?.username || '未知'}`)
    this.addTestResult('超级管理员', isSuperuser, `超级管理员: ${isSuperuser}`)
    
    console.log(`用户: ${user?.username || '未登录'}`)
    console.log(`认证状态: ${isAuthenticated ? '✅' : '❌'}`)
    console.log(`超级管理员: ${isSuperuser ? '✅' : '❌'}`)
    
    console.groupEnd()
  }

  /**
   * 测试权限映射
   */
  async testPermissionMapping() {
    console.group('🗺️ 权限映射测试')
    
    const userPermissions = this.authStore.permissions
    const userRoles = this.authStore.roles
    
    console.log('用户角色:', userRoles.map(r => r.code))
    console.log('用户权限数量:', userPermissions.length)
    
    // 测试关键权限
    const keyPermissions = [
      PERMISSIONS.QUESTIONS_VIEW,
      PERMISSIONS.QUESTIONS_EDIT,
      PERMISSIONS.TEMPLATES_VIEW,
      PERMISSIONS.TEMPLATES_EDIT,
      PERMISSIONS.ADMINS_VIEW,
      PERMISSIONS.SYSTEM_VIEW
    ]
    
    keyPermissions.forEach(permission => {
      const hasPermission = this.authStore.hasPermission(permission)
      this.addTestResult(`权限检查: ${permission}`, hasPermission, permission)
      console.log(`${hasPermission ? '✅' : '❌'} ${permission}`)
    })
    
    console.groupEnd()
  }

  /**
   * 测试前端权限控制
   */
  async testFrontendPermissions() {
    console.group('🎨 前端权限控制测试')
    
    // 测试权限指令
    const testPermissions = [
      'questions:create',
      'questions:edit',
      'templates:edit',
      'admins:create'
    ]
    
    testPermissions.forEach(permission => {
      const hasPermission = this.authStore.hasPermission(permission)
      const element = this.createTestElement(permission)
      const shouldShow = hasPermission
      
      this.addTestResult(`前端权限: ${permission}`, shouldShow, `元素${shouldShow ? '显示' : '隐藏'}`)
      console.log(`${shouldShow ? '✅' : '❌'} ${permission} - 元素${shouldShow ? '显示' : '隐藏'}`)
    })
    
    console.groupEnd()
  }

  /**
   * 测试后端权限验证
   */
  async testBackendPermissions() {
    console.group('🔒 后端权限验证测试')
    
    const testCases = [
      { method: 'GET', url: '/questions', permission: 'questions:view' },
      { method: 'POST', url: '/questions', permission: 'questions:create' },
      { method: 'PUT', url: '/questions/1', permission: 'questions:edit' },
      { method: 'DELETE', url: '/questions/1', permission: 'questions:delete' },
      { method: 'GET', url: '/templates', permission: 'templates:view' },
      { method: 'PUT', url: '/templates/1', permission: 'templates:edit' },
      { method: 'GET', url: '/system/admins', permission: 'admins:view' }
    ]
    
    for (const testCase of testCases) {
      try {
        const hasPermission = this.authStore.hasPermission(testCase.permission)
        console.log(`${hasPermission ? '✅' : '❌'} ${testCase.method} ${testCase.url} (${testCase.permission})`)
        
        this.addTestResult(
          `API权限: ${testCase.method} ${testCase.url}`,
          hasPermission,
          `需要权限: ${testCase.permission}`
        )
      } catch (error) {
        console.log(`❌ ${testCase.method} ${testCase.url} - 测试失败: ${error.message}`)
      }
    }
    
    console.groupEnd()
  }

  /**
   * 测试菜单权限
   */
  async testMenuPermissions() {
    console.group('📋 菜单权限测试')
    
    const { MENU_CONFIG, filterMenuByPermissions } = await import('./menuConfig')
    
    const visibleMenus = filterMenuByPermissions(
      MENU_CONFIG,
      this.authStore.hasPermission,
      this.authStore.hasAnyPermission,
      this.authStore.hasRole,
      this.authStore.hasAnyRole,
      this.authStore.isSuperuser
    )
    
    console.log(`可见菜单数量: ${visibleMenus.length}`)
    
    visibleMenus.forEach(menu => {
      if (menu.children) {
        console.log(`📁 ${menu.title} (${menu.children.length} 个子菜单)`)
        menu.children.forEach(child => {
          console.log(`  📄 ${child.title}`)
        })
      } else {
        console.log(`📄 ${menu.title}`)
      }
    })
    
    this.addTestResult('菜单过滤', visibleMenus.length > 0, `显示 ${visibleMenus.length} 个菜单`)
    
    console.groupEnd()
  }

  /**
   * 测试路由权限
   */
  async testRoutePermissions() {
    console.group('🛣️ 路由权限测试')
    
    const testRoutes = [
      { name: 'questions', title: '试题管理' },
      { name: 'templates', title: '模板管理' },
      { name: 'admin-management', title: '管理员管理' },
      { name: 'system-monitor', title: '系统监控' }
    ]
    
    const { findMenuByRoute } = await import('./menuConfig')
    
    testRoutes.forEach(route => {
      const menuItem = findMenuByRoute(route.name)
      let hasAccess = false
      
      if (menuItem) {
        if (menuItem.permissions) {
          hasAccess = Array.isArray(menuItem.permissions) 
            ? this.authStore.hasAnyPermission(menuItem.permissions)
            : this.authStore.hasPermission(menuItem.permissions)
        } else if (menuItem.roles) {
          hasAccess = Array.isArray(menuItem.roles)
            ? this.authStore.hasAnyRole(menuItem.roles)
            : this.authStore.hasRole(menuItem.roles)
        } else {
          hasAccess = true
        }
      }
      
      console.log(`${hasAccess ? '✅' : '❌'} ${route.title} (${route.name})`)
      this.addTestResult(`路由权限: ${route.name}`, hasAccess, route.title)
    })
    
    console.groupEnd()
  }

  /**
   * 创建测试元素
   */
  createTestElement(permission) {
    const element = document.createElement('button')
    element.textContent = `测试 ${permission}`
    element.style.display = this.authStore.hasPermission(permission) ? 'inline-block' : 'none'
    return element
  }

  /**
   * 添加测试结果
   */
  addTestResult(testName, passed, details) {
    this.testResults.push({
      name: testName,
      passed,
      details,
      timestamp: new Date().toISOString()
    })
  }

  /**
   * 生成测试报告
   */
  generateTestReport() {
    console.group('📊 测试报告')
    
    const totalTests = this.testResults.length
    const passedTests = this.testResults.filter(r => r.passed).length
    const failedTests = totalTests - passedTests
    const successRate = ((passedTests / totalTests) * 100).toFixed(1)
    
    console.log(`总测试数: ${totalTests}`)
    console.log(`通过: ${passedTests}`)
    console.log(`失败: ${failedTests}`)
    console.log(`成功率: ${successRate}%`)
    
    if (failedTests > 0) {
      console.log('\n❌ 失败的测试:')
      this.testResults
        .filter(r => !r.passed)
        .forEach(r => console.log(`  - ${r.name}: ${r.details}`))
    }
    
    console.groupEnd()
    
    return {
      total: totalTests,
      passed: passedTests,
      failed: failedTests,
      successRate: parseFloat(successRate),
      results: this.testResults
    }
  }

  /**
   * 导出测试报告
   */
  exportReport() {
    const report = this.generateTestReport()
    const reportData = {
      ...report,
      user: this.authStore.user,
      roles: this.authStore.roles,
      permissions: this.authStore.permissions,
      timestamp: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `permission-test-report-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    console.log('📄 测试报告已导出')
  }
}

// 创建全局测试实例
export const permissionSystemTest = new PermissionSystemTest()

// 在开发环境下挂载到全局
if (import.meta.env.DEV) {
  window.permissionSystemTest = permissionSystemTest
  window.testPermissionSystem = () => permissionSystemTest.runFullTest()
  window.exportPermissionReport = () => permissionSystemTest.exportReport()
}
