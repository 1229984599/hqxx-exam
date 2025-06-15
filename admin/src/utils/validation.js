/**
 * 表单验证工具
 */

/**
 * 通用验证规则
 */
export const validationRules = {
  // 必填验证
  required: (message = '此字段为必填项') => ({
    required: true,
    message,
    trigger: 'blur'
  }),

  // 邮箱验证
  email: (message = '请输入有效的邮箱地址') => ({
    type: 'email',
    message,
    trigger: 'blur'
  }),

  // 手机号验证
  phone: (message = '请输入有效的手机号') => ({
    pattern: /^1[3-9]\d{9}$/,
    message,
    trigger: 'blur'
  }),

  // 长度验证
  length: (min, max, message) => ({
    min,
    max,
    message: message || `长度应在 ${min} 到 ${max} 个字符之间`,
    trigger: 'blur'
  }),

  // 最小长度验证
  minLength: (min, message) => ({
    min,
    message: message || `最少需要 ${min} 个字符`,
    trigger: 'blur'
  }),

  // 最大长度验证
  maxLength: (max, message) => ({
    max,
    message: message || `最多允许 ${max} 个字符`,
    trigger: 'blur'
  }),

  // 数字验证
  number: (message = '请输入有效的数字') => ({
    type: 'number',
    message,
    trigger: 'blur'
  }),

  // 整数验证
  integer: (message = '请输入有效的整数') => ({
    type: 'integer',
    message,
    trigger: 'blur'
  }),

  // 正数验证
  positive: (message = '请输入正数') => ({
    validator: (rule, value, callback) => {
      if (value && value <= 0) {
        callback(new Error(message))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }),

  // 非负数验证
  nonNegative: (message = '请输入非负数') => ({
    validator: (rule, value, callback) => {
      if (value && value < 0) {
        callback(new Error(message))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }),

  // 范围验证
  range: (min, max, message) => ({
    validator: (rule, value, callback) => {
      if (value && (value < min || value > max)) {
        callback(new Error(message || `值应在 ${min} 到 ${max} 之间`))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }),

  // URL验证
  url: (message = '请输入有效的URL') => ({
    type: 'url',
    message,
    trigger: 'blur'
  }),

  // 密码强度验证
  password: (message = '密码至少8位，包含字母和数字') => ({
    pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/,
    message,
    trigger: 'blur'
  }),

  // 确认密码验证
  confirmPassword: (passwordField, message = '两次输入的密码不一致') => ({
    validator: (rule, value, callback) => {
      if (value && value !== passwordField) {
        callback(new Error(message))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }),

  // 身份证验证
  idCard: (message = '请输入有效的身份证号') => ({
    pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/,
    message,
    trigger: 'blur'
  }),

  // 中文验证
  chinese: (message = '请输入中文') => ({
    pattern: /^[\u4e00-\u9fa5]+$/,
    message,
    trigger: 'blur'
  }),

  // 英文验证
  english: (message = '请输入英文') => ({
    pattern: /^[A-Za-z]+$/,
    message,
    trigger: 'blur'
  }),

  // 字母数字验证
  alphanumeric: (message = '只能包含字母和数字') => ({
    pattern: /^[A-Za-z0-9]+$/,
    message,
    trigger: 'blur'
  }),

  // 代码格式验证（字母、数字、下划线、连字符）
  code: (message = '只能包含字母、数字、下划线和连字符') => ({
    pattern: /^[A-Za-z0-9_-]+$/,
    message,
    trigger: 'blur'
  }),

  // IP地址验证
  ip: (message = '请输入有效的IP地址') => ({
    pattern: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
    message,
    trigger: 'blur'
  }),

  // 端口号验证
  port: (message = '请输入有效的端口号(1-65535)') => ({
    validator: (rule, value, callback) => {
      if (value && (value < 1 || value > 65535)) {
        callback(new Error(message))
      } else {
        callback()
      }
    },
    trigger: 'blur'
  }),

  // 自定义正则验证
  pattern: (regex, message) => ({
    pattern: regex,
    message,
    trigger: 'blur'
  }),

  // 自定义验证函数
  custom: (validator, message) => ({
    validator: (rule, value, callback) => {
      if (validator(value)) {
        callback()
      } else {
        callback(new Error(message))
      }
    },
    trigger: 'blur'
  })
}

/**
 * 常用表单验证规则组合
 */
export const commonValidationRules = {
  // 用户名
  username: [
    validationRules.required('请输入用户名'),
    validationRules.length(3, 20),
    validationRules.alphanumeric('用户名只能包含字母和数字')
  ],

  // 邮箱
  email: [
    validationRules.required('请输入邮箱'),
    validationRules.email()
  ],

  // 手机号
  phone: [
    validationRules.required('请输入手机号'),
    validationRules.phone()
  ],

  // 密码
  password: [
    validationRules.required('请输入密码'),
    validationRules.password()
  ],

  // 姓名
  name: [
    validationRules.required('请输入姓名'),
    validationRules.length(2, 20),
    validationRules.chinese('姓名只能包含中文')
  ],

  // 标题
  title: [
    validationRules.required('请输入标题'),
    validationRules.length(1, 100)
  ],

  // 内容
  content: [
    validationRules.required('请输入内容'),
    validationRules.minLength(1)
  ],

  // 代码
  code: [
    validationRules.required('请输入代码'),
    validationRules.length(1, 50),
    validationRules.code()
  ],

  // 排序
  sortOrder: [
    validationRules.required('请输入排序'),
    validationRules.integer('排序必须是整数'),
    validationRules.nonNegative('排序不能为负数')
  ],

  // URL
  url: [
    validationRules.url()
  ],

  // 描述
  description: [
    validationRules.maxLength(500, '描述不能超过500个字符')
  ]
}

/**
 * 验证工具函数
 */
export const validators = {
  /**
   * 验证邮箱
   */
  isEmail: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  },

  /**
   * 验证手机号
   */
  isPhone: (phone) => {
    const phoneRegex = /^1[3-9]\d{9}$/
    return phoneRegex.test(phone)
  },

  /**
   * 验证身份证
   */
  isIdCard: (idCard) => {
    const idCardRegex = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
    return idCardRegex.test(idCard)
  },

  /**
   * 验证URL
   */
  isUrl: (url) => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  },

  /**
   * 验证IP地址
   */
  isIp: (ip) => {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
    return ipRegex.test(ip)
  },

  /**
   * 验证密码强度
   */
  isStrongPassword: (password) => {
    // 至少8位，包含大小写字母、数字和特殊字符
    const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
    return strongPasswordRegex.test(password)
  },

  /**
   * 验证中文
   */
  isChinese: (text) => {
    const chineseRegex = /^[\u4e00-\u9fa5]+$/
    return chineseRegex.test(text)
  },

  /**
   * 验证英文
   */
  isEnglish: (text) => {
    const englishRegex = /^[A-Za-z]+$/
    return englishRegex.test(text)
  },

  /**
   * 验证字母数字
   */
  isAlphanumeric: (text) => {
    const alphanumericRegex = /^[A-Za-z0-9]+$/
    return alphanumericRegex.test(text)
  }
}

/**
 * 表单验证辅助函数
 */
export const formHelpers = {
  /**
   * 创建动态验证规则
   */
  createDynamicRules: (config) => {
    const rules = {}
    
    for (const [field, ruleConfig] of Object.entries(config)) {
      rules[field] = []
      
      if (ruleConfig.required) {
        rules[field].push(validationRules.required(ruleConfig.requiredMessage))
      }
      
      if (ruleConfig.type) {
        switch (ruleConfig.type) {
          case 'email':
            rules[field].push(validationRules.email(ruleConfig.message))
            break
          case 'phone':
            rules[field].push(validationRules.phone(ruleConfig.message))
            break
          case 'number':
            rules[field].push(validationRules.number(ruleConfig.message))
            break
          case 'url':
            rules[field].push(validationRules.url(ruleConfig.message))
            break
        }
      }
      
      if (ruleConfig.min || ruleConfig.max) {
        rules[field].push(validationRules.length(ruleConfig.min, ruleConfig.max, ruleConfig.lengthMessage))
      }
      
      if (ruleConfig.pattern) {
        rules[field].push(validationRules.pattern(ruleConfig.pattern, ruleConfig.patternMessage))
      }
      
      if (ruleConfig.custom) {
        rules[field].push(validationRules.custom(ruleConfig.custom, ruleConfig.customMessage))
      }
    }
    
    return rules
  },

  /**
   * 验证表单数据
   */
  validateFormData: (data, rules) => {
    const errors = {}
    
    for (const [field, fieldRules] of Object.entries(rules)) {
      const value = data[field]
      
      for (const rule of fieldRules) {
        if (rule.required && (!value || value === '')) {
          errors[field] = rule.message
          break
        }
        
        if (rule.pattern && value && !rule.pattern.test(value)) {
          errors[field] = rule.message
          break
        }
        
        if (rule.validator) {
          try {
            rule.validator(rule, value, (error) => {
              if (error) {
                errors[field] = error.message
              }
            })
          } catch (error) {
            errors[field] = error.message
          }
          if (errors[field]) break
        }
      }
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }
}

/**
 * 智能表单验证系统
 */
export class SmartValidator {
  constructor() {
    this.state = reactive({
      fields: new Map(),
      errors: new Map(),
      touched: new Map(),
      validating: new Map(),
      rules: new Map()
    })

    this.debounceTimers = new Map()
    this.asyncValidators = new Map()
  }

  /**
   * 注册字段
   */
  registerField(name, rules = [], options = {}) {
    this.state.rules.set(name, rules)
    this.state.fields.set(name, options.defaultValue || '')
    this.state.errors.delete(name)
    this.state.touched.set(name, false)
    this.state.validating.set(name, false)

    // 如果有异步验证器，注册它
    if (options.asyncValidator) {
      this.asyncValidators.set(name, options.asyncValidator)
    }
  }

  /**
   * 设置字段值
   */
  setValue(name, value) {
    this.state.fields.set(name, value)
    this.state.touched.set(name, true)

    // 实时验证（防抖）
    this.debounceValidate(name, value)
  }

  /**
   * 防抖验证
   */
  debounceValidate(name, value, delay = 300) {
    if (this.debounceTimers.has(name)) {
      clearTimeout(this.debounceTimers.get(name))
    }

    const timer = setTimeout(() => {
      this.validateField(name, value)
    }, delay)

    this.debounceTimers.set(name, timer)
  }

  /**
   * 验证单个字段
   */
  async validateField(name, value = null) {
    const fieldValue = value !== null ? value : this.state.fields.get(name)
    const rules = this.state.rules.get(name) || []

    this.state.validating.set(name, true)
    this.state.errors.delete(name)

    try {
      // 同步验证
      for (const rule of rules) {
        const result = await this.executeRule(rule, fieldValue, name)
        if (!result.valid) {
          this.state.errors.set(name, result.message)
          break
        }
      }

      // 异步验证
      if (this.asyncValidators.has(name) && !this.state.errors.has(name)) {
        const asyncValidator = this.asyncValidators.get(name)
        try {
          const result = await asyncValidator(fieldValue)
          if (!result.valid) {
            this.state.errors.set(name, result.message)
          }
        } catch (error) {
          this.state.errors.set(name, error.message || '验证失败')
        }
      }
    } catch (error) {
      this.state.errors.set(name, error.message || '验证出错')
    } finally {
      this.state.validating.set(name, false)
    }

    return !this.state.errors.has(name)
  }

  /**
   * 执行验证规则
   */
  async executeRule(rule, value, fieldName) {
    return new Promise((resolve) => {
      if (rule.required && (!value || value === '')) {
        resolve({ valid: false, message: rule.message })
        return
      }

      if (!value && !rule.required) {
        resolve({ valid: true })
        return
      }

      if (rule.pattern && !rule.pattern.test(value)) {
        resolve({ valid: false, message: rule.message })
        return
      }

      if (rule.validator) {
        rule.validator(rule, value, (error) => {
          if (error) {
            resolve({ valid: false, message: error.message })
          } else {
            resolve({ valid: true })
          }
        })
        return
      }

      if (rule.min !== undefined && value.length < rule.min) {
        resolve({ valid: false, message: rule.message })
        return
      }

      if (rule.max !== undefined && value.length > rule.max) {
        resolve({ valid: false, message: rule.message })
        return
      }

      resolve({ valid: true })
    })
  }

  /**
   * 验证所有字段
   */
  async validateAll() {
    const promises = Array.from(this.state.fields.keys()).map(name =>
      this.validateField(name)
    )

    const results = await Promise.all(promises)
    return results.every(result => result)
  }

  /**
   * 获取字段值
   */
  getValue(name) {
    return this.state.fields.get(name)
  }

  /**
   * 获取字段错误
   */
  getError(name) {
    return this.state.errors.get(name)
  }

  /**
   * 检查字段是否有错误
   */
  hasError(name) {
    return this.state.errors.has(name)
  }

  /**
   * 检查字段是否被触摸
   */
  isTouched(name) {
    return this.state.touched.get(name) || false
  }

  /**
   * 检查字段是否正在验证
   */
  isValidating(name) {
    return this.state.validating.get(name) || false
  }

  /**
   * 检查表单是否有效
   */
  isValid() {
    return this.state.errors.size === 0
  }

  /**
   * 获取所有错误
   */
  getAllErrors() {
    return Object.fromEntries(this.state.errors)
  }

  /**
   * 清除字段错误
   */
  clearError(name) {
    this.state.errors.delete(name)
  }

  /**
   * 清除所有错误
   */
  clearAllErrors() {
    this.state.errors.clear()
  }

  /**
   * 重置表单
   */
  reset() {
    this.state.fields.clear()
    this.state.errors.clear()
    this.state.touched.clear()
    this.state.validating.clear()

    // 清除防抖定时器
    this.debounceTimers.forEach(timer => clearTimeout(timer))
    this.debounceTimers.clear()
  }

  /**
   * 获取表单数据
   */
  getFormData() {
    return Object.fromEntries(this.state.fields)
  }

  /**
   * 设置表单数据
   */
  setFormData(data) {
    for (const [name, value] of Object.entries(data)) {
      this.setValue(name, value)
    }
  }
}

/**
 * 创建智能验证器实例
 */
export function useSmartValidator() {
  return new SmartValidator()
}

/**
 * 异步验证器示例
 */
export const asyncValidators = {
  // 检查用户名是否已存在
  checkUsernameExists: async (username) => {
    if (!username) return { valid: true }

    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500))

      // 模拟检查结果
      const exists = ['admin', 'test', 'user'].includes((username || '').toLowerCase())

      return {
        valid: !exists,
        message: exists ? '用户名已存在' : ''
      }
    } catch (error) {
      return {
        valid: false,
        message: '检查用户名时出错'
      }
    }
  },

  // 检查邮箱是否已注册
  checkEmailExists: async (email) => {
    if (!email || !validators.isEmail(email)) return { valid: true }

    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 300))

      // 模拟检查结果
      const exists = ['admin@example.com', 'test@example.com'].includes((email || '').toLowerCase())

      return {
        valid: !exists,
        message: exists ? '邮箱已被注册' : ''
      }
    } catch (error) {
      return {
        valid: false,
        message: '检查邮箱时出错'
      }
    }
  }
}
