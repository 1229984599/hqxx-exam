/**
 * 拼音工具 - 使用 pinyin-pro 库生成分类代码
 */

import { pinyin } from 'pinyin-pro'

/**
 * 将中文字符串转换为拼音首字母
 * @param {string} text - 中文字符串
 * @returns {string} 拼音首字母组合
 */
export function toPinyinInitials(text) {
  if (!text) return ''

  try {
    // 使用 pinyin-pro 获取拼音首字母
    return pinyin(text, {
      pattern: 'first', // 只获取首字母
      toneType: 'none', // 不要声调
      type: 'string'    // 返回字符串
    }).toLowerCase()
  } catch (error) {
    console.warn('拼音转换失败:', error)
    // 降级处理：只保留字母和数字
    return text.replace(/[^\w]/g, '').toLowerCase()
  }
}



/**
 * 生成分类代码
 * @param {string} name - 分类名称
 * @param {string} subjectCode - 学科代码（可选）
 * @returns {string} 生成的分类代码
 */
export function generateCategoryCode(name, subjectCode = '') {
  if (!name) return ''

  // 获取拼音首字母
  const pinyinCode = toPinyinInitials(name)

  // 清理代码
  const cleanedCode = cleanCode(pinyinCode)

  // 如果有学科代码，添加前缀
  if (subjectCode) {
    return `${subjectCode.toLowerCase()}_${cleanedCode}`
  }

  return cleanedCode
}

/**
 * 验证代码格式
 * @param {string} code - 代码
 * @returns {boolean} 是否有效
 */
export function isValidCode(code) {
  // 只允许字母、数字、下划线和连字符
  return /^[a-zA-Z0-9_-]+$/.test(code)
}

/**
 * 清理和格式化代码
 * @param {string} code - 原始代码
 * @returns {string} 清理后的代码
 */
export function cleanCode(code) {
  if (!code) return ''

  return code
    .toLowerCase()
    .replace(/[^a-zA-Z0-9_-]/g, '') // 移除非法字符
    .replace(/^[^a-zA-Z]+/, '') // 确保以字母开头
    .replace(/_{2,}/g, '_') // 合并多个下划线
    .replace(/-{2,}/g, '-') // 合并多个连字符
    .substring(0, 50) // 限制长度
    .replace(/[_-]$/, '') // 移除末尾的下划线或连字符
}

/**
 * 获取完整拼音（用于显示）
 * @param {string} text - 中文字符串
 * @returns {string} 完整拼音
 */
export function getFullPinyin(text) {
  if (!text) return ''

  try {
    return pinyin(text, {
      toneType: 'none',
      type: 'string',
      separator: ''
    }).toLowerCase()
  } catch (error) {
    console.warn('拼音转换失败:', error)
    return text.replace(/[^\w]/g, '').toLowerCase()
  }
}

export default {
  toPinyinInitials,
  generateCategoryCode,
  isValidCode,
  cleanCode,
  getFullPinyin
}