/**
 * 权限调试工具
 * 用于开发环境下调试权限问题
 */

import { useAuthStore } from '../stores/auth'
import { PERMISSIONS, MENU_CONFIG } from './menuConfig'

/**
 * 权限调试器类
 */
export class PermissionDebugger {
  constructor() {
    this.authStore = useAuthStore()
    this.isDebugMode = import.meta.env.DEV
  }

  /**
   * 打印当前用户的权限信息
   */
  printUserPermissions() {
    if (!this.isDebugMode) return

    console.group('🔐 用户权限信息')
    console.log('用户信息:', this.authStore.user)
    console.log('是否超级管理员:', this.authStore.isSuperuser)
    console.log('用户权限:', this.authStore.permissions)
    console.log('用户角色:', this.authStore.roles)
    console.groupEnd()
  }

  /**
   * 检查特定权限并打印结果
   * @param {string} permission 权限代码
   */
  checkPermission(permission) {
    if (!this.isDebugMode) return

    const hasPermission = this.authStore.hasPermission(permission)
    console.log(`🔍 权限检查: ${permission} = ${hasPermission ? '✅ 有权限' : '❌ 无权限'}`)
    
    if (!hasPermission && !this.authStore.isSuperuser) {
      console.log(`💡 提示: 用户缺少权限 "${permission}"`)
      this.suggestSolution(permission)
    }
    
    return hasPermission
  }

  /**
   * 批量检查权限
   * @param {Array} permissions 权限代码数组
   */
  checkPermissions(permissions) {
    if (!this.isDebugMode) return

    console.group('🔍 批量权限检查')
    const results = {}
    
    permissions.forEach(permission => {
      const hasPermission = this.authStore.hasPermission(permission)
      results[permission] = hasPermission
      console.log(`${permission}: ${hasPermission ? '✅' : '❌'}`)
    })
    
    console.groupEnd()
    return results
  }

  /**
   * 检查菜单权限并打印结果
   */
  checkMenuPermissions() {
    if (!this.isDebugMode) return

    console.group('📋 菜单权限检查')
    
    const checkMenuItem = (item, level = 0) => {
      const indent = '  '.repeat(level)
      const hasPermission = this.hasMenuPermission(item)
      const status = hasPermission ? '✅' : '❌'
      
      console.log(`${indent}${status} ${item.title} (${item.id})`)
      
      if (item.permissions) {
        console.log(`${indent}  权限要求:`, item.permissions)
      }
      
      if (!hasPermission && item.permissions) {
        console.log(`${indent}  💡 缺少权限:`, item.permissions)
      }
      
      if (item.children) {
        item.children.forEach(child => checkMenuItem(child, level + 1))
      }
    }
    
    MENU_CONFIG.forEach(item => checkMenuItem(item))
    console.groupEnd()
  }

  /**
   * 检查菜单项权限
   * @param {Object} menuItem 菜单项
   */
  hasMenuPermission(menuItem) {
    if (!menuItem.permissions) return true
    
    if (Array.isArray(menuItem.permissions)) {
      return this.authStore.hasAnyPermission(menuItem.permissions)
    }
    
    return this.authStore.hasPermission(menuItem.permissions)
  }

  /**
   * 提供权限解决方案建议
   * @param {string} permission 权限代码
   */
  suggestSolution(permission) {
    const suggestions = {
      [PERMISSIONS.QUESTIONS_VIEW]: '需要试题查看权限，请联系管理员分配"试题管理"角色',
      [PERMISSIONS.QUESTIONS_CREATE]: '需要试题创建权限，请联系管理员分配"试题管理"角色',
      [PERMISSIONS.QUESTIONS_EDIT]: '需要试题编辑权限，请联系管理员分配"试题管理"角色',
      [PERMISSIONS.QUESTIONS_DELETE]: '需要试题删除权限，请联系管理员分配"试题管理"角色',
      [PERMISSIONS.TEMPLATES_VIEW]: '需要模板查看权限，请联系管理员分配"模板管理"角色',
      [PERMISSIONS.TEMPLATES_CREATE]: '需要模板创建权限，请联系管理员分配"模板管理"角色',
      [PERMISSIONS.BASIC_DATA_VIEW]: '需要基础数据查看权限，请联系管理员分配相应角色',
      [PERMISSIONS.BASIC_DATA_EDIT]: '需要基础数据编辑权限，请联系管理员分配相应角色',
      [PERMISSIONS.ADMINS_VIEW]: '需要管理员查看权限，请联系超级管理员分配"用户管理"角色',
      [PERMISSIONS.SYSTEM_VIEW]: '需要系统查看权限，请联系超级管理员分配"系统管理"角色'
    }
    
    const suggestion = suggestions[permission]
    if (suggestion) {
      console.log(`💡 解决方案: ${suggestion}`)
    }
  }

  /**
   * 生成权限报告
   */
  generatePermissionReport() {
    if (!this.isDebugMode) return

    const report = {
      user: this.authStore.user,
      isSuperuser: this.authStore.isSuperuser,
      permissions: this.authStore.permissions,
      roles: this.authStore.roles,
      permissionChecks: {},
      menuAccess: {}
    }

    // 检查所有权限
    Object.values(PERMISSIONS).forEach(permission => {
      report.permissionChecks[permission] = this.authStore.hasPermission(permission)
    })

    // 检查菜单访问
    const checkMenuAccess = (item) => {
      report.menuAccess[item.id] = this.hasMenuPermission(item)
      if (item.children) {
        item.children.forEach(checkMenuAccess)
      }
    }
    
    MENU_CONFIG.forEach(checkMenuAccess)

    console.group('📊 权限报告')
    console.log(report)
    console.groupEnd()

    return report
  }

  /**
   * 模拟权限变更（仅开发环境）
   * @param {Array} permissions 新的权限列表
   */
  simulatePermissions(permissions) {
    if (!this.isDebugMode) {
      console.warn('权限模拟仅在开发环境可用')
      return
    }

    console.warn('🚨 模拟权限变更（仅开发环境）')
    console.log('原权限:', this.authStore.permissions)
    console.log('新权限:', permissions)
    
    // 临时修改权限（仅用于调试）
    const originalPermissions = [...this.authStore.permissions]
    this.authStore.permissions = permissions
    
    console.log('✅ 权限已临时变更，请刷新页面恢复')
    
    // 5秒后自动恢复
    setTimeout(() => {
      this.authStore.permissions = originalPermissions
      console.log('🔄 权限已自动恢复')
    }, 5000)
  }
}

// 创建全局调试器实例
export const permissionDebugger = new PermissionDebugger()

// 在开发环境下将调试器挂载到全局
if (import.meta.env.DEV) {
  window.permissionDebugger = permissionDebugger
  
  // 提供快捷方法
  window.checkPermission = (permission) => permissionDebugger.checkPermission(permission)
  window.checkMenuPermissions = () => permissionDebugger.checkMenuPermissions()
  window.printUserPermissions = () => permissionDebugger.printUserPermissions()
  window.generatePermissionReport = () => permissionDebugger.generatePermissionReport()
  
  console.log('🔧 权限调试工具已加载，可使用以下方法:')
  console.log('- window.checkPermission(permission)')
  console.log('- window.checkMenuPermissions()')
  console.log('- window.printUserPermissions()')
  console.log('- window.generatePermissionReport()')
}

/**
 * 权限检查装饰器（用于组件方法）
 * @param {string} permission 权限代码
 */
export function requirePermission(permission) {
  return function(target, propertyKey, descriptor) {
    const originalMethod = descriptor.value
    
    descriptor.value = function(...args) {
      const authStore = useAuthStore()
      
      if (!authStore.hasPermission(permission)) {
        console.error(`权限不足: 需要权限 "${permission}"`)
        
        if (import.meta.env.DEV) {
          permissionDebugger.suggestSolution(permission)
        }
        
        throw new Error(`Permission denied: ${permission}`)
      }
      
      return originalMethod.apply(this, args)
    }
    
    return descriptor
  }
}

export default permissionDebugger
