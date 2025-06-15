/**
 * RBAC菜单权限配置
 * 基于角色的访问控制 - 菜单项基于角色显示
 */

// 角色常量 - 与后端保持一致
export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  ADMIN: 'admin',
  TEACHER: 'teacher',
  SUBJECT_ADMIN: 'subject_admin',
  VIEWER: 'viewer'
}

// 权限常量 - 与后端保持一致（用于细粒度权限检查）
export const PERMISSIONS = {
  // 试题管理权限
  QUESTIONS_VIEW: 'questions:view',
  QUESTIONS_CREATE: 'questions:create',
  QUESTIONS_EDIT: 'questions:edit',
  QUESTIONS_DELETE: 'questions:delete',
  QUESTIONS_EXPORT: 'questions:export',
  QUESTIONS_BATCH: 'questions:batch',

  // 用户管理权限
  ADMINS_VIEW: 'admins:view',
  ADMINS_CREATE: 'admins:create',
  ADMINS_EDIT: 'admins:edit',
  ADMINS_DELETE: 'admins:delete',

  // 基础数据权限
  BASIC_DATA_VIEW: 'basic_data:view',
  BASIC_DATA_EDIT: 'basic_data:edit',

  // 模板管理权限
  TEMPLATES_VIEW: 'templates:view',
  TEMPLATES_CREATE: 'templates:create',
  TEMPLATES_EDIT: 'templates:edit',
  TEMPLATES_DELETE: 'templates:delete',

  // 系统管理权限
  SYSTEM_VIEW: 'system:view',
  SYSTEM_CONFIG: 'system:config',
  SYSTEM_BACKUP: 'system:backup',
  SYSTEM_LOGS: 'system:logs'
}

// 基于角色的菜单配置
export const MENU_CONFIG = [
  {
    id: 'dashboard',
    name: 'dashboard',
    title: '仪表板',
    icon: 'Odometer',
    path: '/',
    roles: null, // 所有登录用户都可以访问
    visible: true
  },

  // 基础管理组 - 需要管理员角色或学科管理员角色
  {
    id: 'basic-management',
    title: '基础管理',
    type: 'group',
    roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.SUBJECT_ADMIN],
    children: [
      {
        id: 'semesters',
        name: 'semesters',
        title: '学期管理',
        icon: 'Calendar',
        path: '/semesters',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.SUBJECT_ADMIN],
        permissions: [PERMISSIONS.BASIC_DATA_VIEW]
      },
      {
        id: 'grades',
        name: 'grades',
        title: '年级管理',
        icon: 'School',
        path: '/grades',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.SUBJECT_ADMIN],
        permissions: [PERMISSIONS.BASIC_DATA_VIEW]
      },
      {
        id: 'subjects',
        name: 'subjects',
        title: '学科管理',
        icon: 'Reading',
        path: '/subjects',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.SUBJECT_ADMIN],
        permissions: [PERMISSIONS.BASIC_DATA_VIEW]
      },
      {
        id: 'categories',
        name: 'categories',
        title: '分类管理',
        icon: 'Collection',
        path: '/categories',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.SUBJECT_ADMIN],
        permissions: [PERMISSIONS.BASIC_DATA_VIEW]
      }
    ]
  },
  
  // 内容管理组 - 教师及以上角色可访问
  {
    id: 'content-management',
    title: '内容管理',
    type: 'group',
    roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.TEACHER, ROLES.SUBJECT_ADMIN],
    children: [
      {
        id: 'questions',
        name: 'questions',
        title: '试题管理',
        icon: 'Document',
        path: '/questions',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.TEACHER, ROLES.SUBJECT_ADMIN],
        permissions: [PERMISSIONS.QUESTIONS_VIEW],
        activeNames: ['questions', 'question-add', 'question-edit']
      },
      {
        id: 'templates',
        name: 'templates',
        title: '模板管理',
        icon: 'DocumentCopy',
        path: '/templates',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.TEACHER, ROLES.SUBJECT_ADMIN],
        permissions: [PERMISSIONS.TEMPLATES_VIEW],
        activeNames: ['templates', 'template-add', 'template-edit']
      }
    ]
  },
  
  // 用户管理组 - 仅超级管理员和管理员可访问
  {
    id: 'user-management',
    title: '用户管理',
    type: 'group',
    roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN],
    children: [
      {
        id: 'admin-management',
        name: 'admin-management',
        title: '管理员管理',
        icon: 'User',
        path: '/users/admins',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN],
        permissions: [PERMISSIONS.ADMINS_VIEW]
      },
      {
        id: 'role-management',
        name: 'role-management',
        title: '角色权限',
        icon: 'UserFilled',
        path: '/users/roles',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN],
        permissions: [PERMISSIONS.ADMINS_VIEW]
      }
    ]
  },

  // 系统管理组 - 仅超级管理员和管理员可访问
  {
    id: 'system-management',
    title: '系统管理',
    type: 'group',
    roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN],
    children: [
      {
        id: 'system-monitor',
        name: 'system-monitor',
        title: '系统监控',
        icon: 'Monitor',
        path: '/system/monitor',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN],
        permissions: [PERMISSIONS.SYSTEM_VIEW]
      },
      {
        id: 'system-logs',
        name: 'system-logs',
        title: '系统日志',
        icon: 'Document',
        path: '/system/logs',
        roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN],
        permissions: [PERMISSIONS.SYSTEM_LOGS]
      },
      {
        id: 'backup-management',
        name: 'backup-management',
        title: '备份管理',
        icon: 'FolderOpened',
        path: '/system/backup',
        roles: [ROLES.SUPER_ADMIN],  // 仅超级管理员
        permissions: [PERMISSIONS.SYSTEM_BACKUP]
      },
      {
        id: 'system-settings',
        name: 'system-settings',
        title: '系统设置',
        icon: 'Tools',
        path: '/system/settings',
        roles: [ROLES.SUPER_ADMIN],  // 仅超级管理员
        permissions: [PERMISSIONS.SYSTEM_CONFIG]
      }
    ]
  },
  
  // 开发工具组（仅开发环境显示）
  {
    id: 'dev-tools',
    title: '开发工具',
    type: 'group',
    roles: null, // 开发环境下所有人可见
    visible: import.meta.env.DEV, // 仅开发环境显示
    children: [
      {
        id: 'tinymce-test',
        name: 'tinymce-test',
        title: '编辑器测试',
        icon: 'Edit',
        path: '/tinymce-test',
        roles: null
      },
      {
        id: 'permission-help',
        name: 'permission-help',
        title: '权限说明',
        icon: 'QuestionFilled',
        path: '/permission-help',
        roles: null
      },
      {
        id: 'permission-guide',
        name: 'permission-guide',
        title: '权限管理指南',
        icon: 'Setting',
        path: '/permission-guide',
        roles: ['super_admin', 'admin']
      }
    ]
  }
]

/**
 * 检查菜单项是否可见（基于权限和角色）
 * @param {Object} menuItem 菜单项配置
 * @param {Function} hasPermission 权限检查函数
 * @param {Function} hasAnyPermission 任意权限检查函数
 * @param {Function} hasRole 角色检查函数
 * @param {Function} hasAnyRole 任意角色检查函数
 * @param {boolean} isSuperuser 是否超级管理员
 * @returns {boolean} 是否可见
 */
export function isMenuVisible(menuItem, hasPermission, hasAnyPermission, hasRole, hasAnyRole, isSuperuser = false) {
  // 超级管理员可以看到所有菜单
  if (isSuperuser) {
    return true
  }

  // 检查基本可见性
  if (menuItem.visible === false) {
    return false
  }

  // 优先检查权限，如果没有权限配置则检查角色
  if (menuItem.permissions) {
    if (Array.isArray(menuItem.permissions)) {
      return hasAnyPermission(menuItem.permissions)
    } else {
      return hasPermission(menuItem.permissions)
    }
  } else if (menuItem.roles) {
    // 兼容旧的角色配置
    if (Array.isArray(menuItem.roles)) {
      return hasAnyRole(menuItem.roles)
    } else {
      return hasRole(menuItem.roles)
    }
  }

  // 如果没有权限和角色要求，则可见
  return true
}

/**
 * 过滤菜单配置，只返回用户有权限访问的菜单
 * @param {Array} menuConfig 菜单配置
 * @param {Function} hasPermission 权限检查函数
 * @param {Function} hasAnyPermission 任意权限检查函数
 * @param {Function} hasRole 角色检查函数
 * @param {Function} hasAnyRole 任意角色检查函数
 * @param {boolean} isSuperuser 是否超级管理员
 * @returns {Array} 过滤后的菜单配置
 */
export function filterMenuByPermissions(menuConfig, hasPermission, hasAnyPermission, hasRole, hasAnyRole, isSuperuser = false) {
  return menuConfig.filter(item => {
    // 检查菜单项本身是否可见
    if (!isMenuVisible(item, hasPermission, hasAnyPermission, hasRole, hasAnyRole, isSuperuser)) {
      return false
    }

    // 如果有子菜单，递归过滤
    if (item.children) {
      item.children = filterMenuByPermissions(item.children, hasPermission, hasAnyPermission, hasRole, hasAnyRole, isSuperuser)
      // 如果所有子菜单都被过滤掉了，则隐藏父菜单
      return item.children.length > 0
    }

    return true
  })
}

// 兼容旧的函数名
export const filterMenuByRoles = filterMenuByPermissions

/**
 * 根据路由名称查找菜单项
 * @param {string} routeName 路由名称
 * @param {Array} menuConfig 菜单配置
 * @returns {Object|null} 找到的菜单项
 */
export function findMenuByRoute(routeName, menuConfig = MENU_CONFIG) {
  for (const item of menuConfig) {
    if (item.name === routeName) {
      return item
    }
    
    if (item.activeNames && item.activeNames.includes(routeName)) {
      return item
    }
    
    if (item.children) {
      const found = findMenuByRoute(routeName, item.children)
      if (found) return found
    }
  }
  
  return null
}
