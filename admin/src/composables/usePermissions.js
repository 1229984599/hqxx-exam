import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { PERMISSIONS, ROLES } from '../utils/menuConfig'

/**
 * 权限检查组合式函数
 * 提供便捷的权限检查方法
 */
export function usePermissions() {
  const authStore = useAuthStore()

  // 常量
  const permissions = PERMISSIONS
  const roles = ROLES

  // 基于角色的权限检查方法（RBAC核心）
  const hasRole = (roleCode) => {
    return authStore.hasRole(roleCode)
  }

  const hasAnyRole = (roleCodes) => {
    return authStore.hasAnyRole(roleCodes)
  }

  const hasAllRoles = (roleCodes) => {
    return authStore.hasAllRoles(roleCodes)
  }

  // 基于权限的检查方法（细粒度控制）
  const hasPermission = (permission) => {
    return authStore.hasPermission(permission)
  }

  const hasAnyPermission = (permissionList) => {
    return authStore.hasAnyPermission(permissionList)
  }

  const hasAllPermissions = (permissionList) => {
    return authStore.hasAllPermissions(permissionList)
  }

  // 计算属性 - 基于角色的权限检查
  const isAdmin = computed(() => hasAnyRole([roles.SUPER_ADMIN, roles.ADMIN]))
  const isTeacher = computed(() => hasRole(roles.TEACHER))
  const isSubjectAdmin = computed(() => hasRole(roles.SUBJECT_ADMIN))
  const isViewer = computed(() => hasRole(roles.VIEWER))

  // 计算属性 - 常用权限检查（基于权限的细粒度控制）
  const canViewQuestions = computed(() => hasPermission(permissions.QUESTIONS_VIEW))
  const canCreateQuestions = computed(() => hasPermission(permissions.QUESTIONS_CREATE))
  const canEditQuestions = computed(() => hasPermission(permissions.QUESTIONS_EDIT))
  const canDeleteQuestions = computed(() => hasPermission(permissions.QUESTIONS_DELETE))
  const canExportQuestions = computed(() => hasPermission(permissions.QUESTIONS_EXPORT))
  const canBatchQuestions = computed(() => hasPermission(permissions.QUESTIONS_BATCH))

  const canViewTemplates = computed(() => hasPermission(permissions.TEMPLATES_VIEW))
  const canCreateTemplates = computed(() => hasPermission(permissions.TEMPLATES_CREATE))
  const canEditTemplates = computed(() => hasPermission(permissions.TEMPLATES_EDIT))
  const canDeleteTemplates = computed(() => hasPermission(permissions.TEMPLATES_DELETE))

  const canViewBasicData = computed(() => hasPermission(permissions.BASIC_DATA_VIEW))
  const canEditBasicData = computed(() => hasPermission(permissions.BASIC_DATA_EDIT))

  const canViewAdmins = computed(() => hasPermission(permissions.ADMINS_VIEW))
  const canCreateAdmins = computed(() => hasPermission(permissions.ADMINS_CREATE))
  const canEditAdmins = computed(() => hasPermission(permissions.ADMINS_EDIT))
  const canDeleteAdmins = computed(() => hasPermission(permissions.ADMINS_DELETE))

  const canViewSystem = computed(() => hasPermission(permissions.SYSTEM_VIEW))
  const canConfigSystem = computed(() => hasPermission(permissions.SYSTEM_CONFIG))
  const canBackupSystem = computed(() => hasPermission(permissions.SYSTEM_BACKUP))
  const canViewLogs = computed(() => hasPermission(permissions.SYSTEM_LOGS))

  // 组合权限检查
  const canManageQuestions = computed(() => 
    hasAnyPermission([
      permissions.QUESTIONS_CREATE,
      permissions.QUESTIONS_EDIT,
      permissions.QUESTIONS_DELETE
    ])
  )

  const canManageTemplates = computed(() => 
    hasAnyPermission([
      permissions.TEMPLATES_CREATE,
      permissions.TEMPLATES_EDIT,
      permissions.TEMPLATES_DELETE
    ])
  )

  const canManageSystem = computed(() => 
    hasAnyPermission([
      permissions.SYSTEM_CONFIG,
      permissions.SYSTEM_BACKUP,
      permissions.SYSTEM_LOGS
    ])
  )

  const canManageUsers = computed(() => 
    hasAnyPermission([
      permissions.ADMINS_CREATE,
      permissions.ADMINS_EDIT,
      permissions.ADMINS_DELETE
    ])
  )

  // 用户信息
  const isSuperuser = computed(() => authStore.isSuperuser)
  const userPermissions = computed(() => authStore.permissions)
  const userRoles = computed(() => authStore.roles)

  return {
    // 常量
    permissions,
    roles,

    // 基于角色的权限检查方法（RBAC核心）
    hasRole,
    hasAnyRole,
    hasAllRoles,

    // 基于权限的检查方法（细粒度控制）
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,

    // 角色判断
    isAdmin,
    isTeacher,
    isSubjectAdmin,
    isViewer,
    
    // 试题管理权限
    canViewQuestions,
    canCreateQuestions,
    canEditQuestions,
    canDeleteQuestions,
    canExportQuestions,
    canBatchQuestions,
    canManageQuestions,
    
    // 模板管理权限
    canViewTemplates,
    canCreateTemplates,
    canEditTemplates,
    canDeleteTemplates,
    canManageTemplates,
    
    // 基础数据权限
    canViewBasicData,
    canEditBasicData,
    
    // 用户管理权限
    canViewAdmins,
    canCreateAdmins,
    canEditAdmins,
    canDeleteAdmins,
    canManageUsers,
    
    // 系统管理权限
    canViewSystem,
    canConfigSystem,
    canBackupSystem,
    canViewLogs,
    canManageSystem,
    
    // 用户信息
    isSuperuser,
    userPermissions,
    userRoles
  }
}

/**
 * 权限指令
 * 用于在模板中进行权限控制
 *
 * 使用方法：
 * v-permission="'questions:view'"  // 基于权限
 * v-permission="['questions:view', 'questions:edit']"  // 多个权限
 * v-role="'admin'"  // 基于角色
 * v-role="['admin', 'teacher']"  // 多个角色
 */
export const permissionDirective = {
  mounted(el, binding) {
    const authStore = useAuthStore()
    const value = binding.value

    let hasAccess = false

    if (Array.isArray(value)) {
      hasAccess = authStore.hasAnyPermission(value)
    } else if (typeof value === 'string') {
      hasAccess = authStore.hasPermission(value)
    } else {
      hasAccess = true
    }

    if (!hasAccess) {
      el.style.display = 'none'
    }
  },

  updated(el, binding) {
    const authStore = useAuthStore()
    const value = binding.value

    let hasAccess = false

    if (Array.isArray(value)) {
      hasAccess = authStore.hasAnyPermission(value)
    } else if (typeof value === 'string') {
      hasAccess = authStore.hasPermission(value)
    } else {
      hasAccess = true
    }

    el.style.display = hasAccess ? '' : 'none'
  }
}

/**
 * 角色指令
 * 用于在模板中进行角色控制
 *
 * 使用方法：
 * v-role="'admin'"
 * v-role="['admin', 'teacher']"
 */
export const roleDirective = {
  mounted(el, binding) {
    const authStore = useAuthStore()
    const role = binding.value

    let hasRole = false

    if (Array.isArray(role)) {
      hasRole = authStore.hasAnyRole(role)
    } else if (typeof role === 'string') {
      hasRole = authStore.hasRole(role)
    } else {
      hasRole = true
    }

    if (!hasRole) {
      el.style.display = 'none'
    }
  },

  updated(el, binding) {
    const authStore = useAuthStore()
    const role = binding.value

    let hasRole = false

    if (Array.isArray(role)) {
      hasRole = authStore.hasAnyRole(role)
    } else if (typeof role === 'string') {
      hasRole = authStore.hasRole(role)
    } else {
      hasRole = true
    }

    el.style.display = hasRole ? '' : 'none'
  }
}
