/**
 * 权限系统最终验证脚本
 * 用于确保权限系统的完整性和正确性
 */

import { useAuthStore } from '../stores/auth'
import api from './api'

export class FinalPermissionValidation {
  constructor() {
    this.authStore = useAuthStore()
    this.validationResults = []
    this.errors = []
  }

  /**
   * 运行完整的权限验证
   */
  async runFullValidation() {
    console.clear()
    console.log('🔍 权限系统最终验证开始...')
    console.log('=' .repeat(60))
    
    this.validationResults = []
    this.errors = []
    
    try {
      await this.validateUserState()
      await this.validatePermissionCoverage()
      await this.validateAPIPermissions()
      await this.validateFrontendPermissions()
      await this.validateMenuPermissions()
      await this.validatePermissionConsistency()
      
      this.generateValidationReport()
    } catch (error) {
      console.error('❌ 验证过程中发生错误:', error)
      this.errors.push(error.message)
    }
    
    console.log('=' .repeat(60))
    console.log('✅ 权限系统验证完成')
    
    return this.getValidationSummary()
  }

  /**
   * 验证用户状态
   */
  async validateUserState() {
    console.group('👤 用户状态验证')
    
    const user = this.authStore.user
    const isAuthenticated = this.authStore.isAuthenticated
    const permissions = this.authStore.permissions
    const roles = this.authStore.roles
    
    this.addValidation('用户认证', isAuthenticated, '用户必须已登录')
    this.addValidation('用户信息', !!user, '用户信息必须存在')
    this.addValidation('权限列表', permissions.length > 0, '用户必须有权限')
    this.addValidation('角色列表', roles.length > 0, '用户必须有角色')
    
    console.log(`用户: ${user?.username || '未登录'}`)
    console.log(`权限数量: ${permissions.length}`)
    console.log(`角色数量: ${roles.length}`)
    
    console.groupEnd()
  }

  /**
   * 验证权限覆盖率
   */
  async validatePermissionCoverage() {
    console.group('📋 权限覆盖率验证')
    
    const requiredPermissions = [
      'questions:view', 'questions:create', 'questions:edit', 'questions:delete',
      'templates:view', 'templates:create', 'templates:edit', 'templates:delete',
      'basic_data:view', 'basic_data:edit',
      'admins:view', 'admins:create', 'admins:edit', 'admins:delete',
      'system:view', 'system:config'
    ]
    
    const userPermissions = this.authStore.permissions
    const missingPermissions = []
    const availablePermissions = []
    
    requiredPermissions.forEach(permission => {
      if (userPermissions.includes(permission)) {
        availablePermissions.push(permission)
      } else {
        missingPermissions.push(permission)
      }
    })
    
    this.addValidation(
      '权限覆盖率',
      availablePermissions.length > 0,
      `可用权限: ${availablePermissions.length}/${requiredPermissions.length}`
    )
    
    console.log(`可用权限: ${availablePermissions.length}`)
    console.log(`缺失权限: ${missingPermissions.length}`)
    
    if (missingPermissions.length > 0) {
      console.log('缺失的权限:', missingPermissions)
    }
    
    console.groupEnd()
  }

  /**
   * 验证API权限
   */
  async validateAPIPermissions() {
    console.group('🔒 API权限验证')
    
    const apiTests = [
      { endpoint: '/questions', method: 'GET', permission: 'questions:view' },
      { endpoint: '/questions', method: 'POST', permission: 'questions:create' },
      { endpoint: '/templates', method: 'GET', permission: 'templates:view' },
      { endpoint: '/templates', method: 'POST', permission: 'templates:create' },
      { endpoint: '/semesters', method: 'POST', permission: 'basic_data:edit' },
      { endpoint: '/grades', method: 'POST', permission: 'basic_data:edit' },
      { endpoint: '/subjects', method: 'POST', permission: 'basic_data:edit' },
      { endpoint: '/categories', method: 'POST', permission: 'basic_data:edit' },
      { endpoint: '/system/admins', method: 'GET', permission: 'admins:view' }
    ]
    
    let passedTests = 0
    let totalTests = apiTests.length
    
    for (const test of apiTests) {
      const hasPermission = this.authStore.hasPermission(test.permission)
      const shouldPass = hasPermission
      
      this.addValidation(
        `API权限: ${test.method} ${test.endpoint}`,
        shouldPass,
        `需要权限: ${test.permission}`
      )
      
      if (shouldPass) {
        passedTests++
        console.log(`✅ ${test.method} ${test.endpoint}`)
      } else {
        console.log(`❌ ${test.method} ${test.endpoint} (缺少权限: ${test.permission})`)
      }
    }
    
    console.log(`API权限测试: ${passedTests}/${totalTests} 通过`)
    
    console.groupEnd()
  }

  /**
   * 验证前端权限
   */
  async validateFrontendPermissions() {
    console.group('🎨 前端权限验证')
    
    const frontendTests = [
      { component: '试题创建按钮', permission: 'questions:create' },
      { component: '试题编辑按钮', permission: 'questions:edit' },
      { component: '试题删除按钮', permission: 'questions:delete' },
      { component: '模板创建按钮', permission: 'templates:create' },
      { component: '模板编辑按钮', permission: 'templates:edit' },
      { component: '模板删除按钮', permission: 'templates:delete' },
      { component: '管理员创建按钮', permission: 'admins:create' },
      { component: '管理员编辑按钮', permission: 'admins:edit' }
    ]
    
    let visibleComponents = 0
    let totalComponents = frontendTests.length
    
    frontendTests.forEach(test => {
      const hasPermission = this.authStore.hasPermission(test.permission)
      const shouldShow = hasPermission
      
      this.addValidation(
        `前端组件: ${test.component}`,
        shouldShow,
        `权限: ${test.permission}`
      )
      
      if (shouldShow) {
        visibleComponents++
        console.log(`✅ ${test.component} (显示)`)
      } else {
        console.log(`❌ ${test.component} (隐藏)`)
      }
    })
    
    console.log(`前端组件: ${visibleComponents}/${totalComponents} 可见`)
    
    console.groupEnd()
  }

  /**
   * 验证菜单权限
   */
  async validateMenuPermissions() {
    console.group('📋 菜单权限验证')
    
    try {
      const { MENU_CONFIG, filterMenuByPermissions } = await import('./menuConfig')
      
      const visibleMenus = filterMenuByPermissions(
        MENU_CONFIG,
        this.authStore.hasPermission,
        this.authStore.hasAnyPermission,
        this.authStore.hasRole,
        this.authStore.hasAnyRole,
        this.authStore.isSuperuser
      )
      
      const totalMenus = MENU_CONFIG.reduce((count, menu) => {
        return count + 1 + (menu.children ? menu.children.length : 0)
      }, 0)
      
      const visibleMenuCount = visibleMenus.reduce((count, menu) => {
        return count + 1 + (menu.children ? menu.children.length : 0)
      }, 0)
      
      this.addValidation(
        '菜单过滤',
        visibleMenuCount > 0,
        `可见菜单: ${visibleMenuCount}/${totalMenus}`
      )
      
      console.log(`总菜单数: ${totalMenus}`)
      console.log(`可见菜单数: ${visibleMenuCount}`)
      
      visibleMenus.forEach(menu => {
        console.log(`📁 ${menu.title}`)
        if (menu.children) {
          menu.children.forEach(child => {
            console.log(`  📄 ${child.title}`)
          })
        }
      })
      
    } catch (error) {
      console.error('菜单权限验证失败:', error)
      this.errors.push(`菜单权限验证失败: ${error.message}`)
    }
    
    console.groupEnd()
  }

  /**
   * 验证权限一致性
   */
  async validatePermissionConsistency() {
    console.group('🔄 权限一致性验证')
    
    const permissionMethods = [
      'hasPermission',
      'hasAnyPermission',
      'hasRole',
      'hasAnyRole'
    ]
    
    let methodsAvailable = 0
    
    permissionMethods.forEach(method => {
      const isAvailable = typeof this.authStore[method] === 'function'
      
      this.addValidation(
        `权限方法: ${method}`,
        isAvailable,
        `方法必须可用`
      )
      
      if (isAvailable) {
        methodsAvailable++
        console.log(`✅ ${method}`)
      } else {
        console.log(`❌ ${method}`)
      }
    })
    
    console.log(`权限方法: ${methodsAvailable}/${permissionMethods.length} 可用`)
    
    console.groupEnd()
  }

  /**
   * 添加验证结果
   */
  addValidation(name, passed, details) {
    this.validationResults.push({
      name,
      passed,
      details,
      timestamp: new Date().toISOString()
    })
  }

  /**
   * 生成验证报告
   */
  generateValidationReport() {
    console.group('📊 验证报告')
    
    const totalValidations = this.validationResults.length
    const passedValidations = this.validationResults.filter(v => v.passed).length
    const failedValidations = totalValidations - passedValidations
    const successRate = ((passedValidations / totalValidations) * 100).toFixed(1)
    
    console.log(`总验证项: ${totalValidations}`)
    console.log(`通过: ${passedValidations}`)
    console.log(`失败: ${failedValidations}`)
    console.log(`成功率: ${successRate}%`)
    console.log(`错误数: ${this.errors.length}`)
    
    if (failedValidations > 0) {
      console.log('\n❌ 失败的验证:')
      this.validationResults
        .filter(v => !v.passed)
        .forEach(v => console.log(`  - ${v.name}: ${v.details}`))
    }
    
    if (this.errors.length > 0) {
      console.log('\n🚨 错误信息:')
      this.errors.forEach(error => console.log(`  - ${error}`))
    }
    
    console.groupEnd()
  }

  /**
   * 获取验证摘要
   */
  getValidationSummary() {
    const totalValidations = this.validationResults.length
    const passedValidations = this.validationResults.filter(v => v.passed).length
    const successRate = ((passedValidations / totalValidations) * 100).toFixed(1)
    
    return {
      total: totalValidations,
      passed: passedValidations,
      failed: totalValidations - passedValidations,
      successRate: parseFloat(successRate),
      errors: this.errors.length,
      isValid: this.errors.length === 0 && passedValidations === totalValidations
    }
  }
}

// 创建全局验证实例
export const finalPermissionValidation = new FinalPermissionValidation()

// 在开发环境下挂载到全局
if (import.meta.env.DEV) {
  window.finalPermissionValidation = finalPermissionValidation
  window.validatePermissionSystem = () => finalPermissionValidation.runFullValidation()
}
