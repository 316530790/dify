/**
 * 访问类型管理工具
 * 用于区分正常前端登录和通过URL参数访问的情况
 */

export type AccessType = 'normal_login' | 'token_url_access' | null

/**
 * 从localStorage中获取访问类型标记
 */
export const getAccessTypeFromStorage = (): AccessType => {
  if (typeof window === 'undefined') return null
  const accessType = localStorage.getItem('dify_access_type')
  return accessType as AccessType || null
}

/**
 * 检查当前是否为通过URL参数访问
 * 优先检查localStorage中保存的访问类型，然后检查当前URL参数
 */
export const isTokenUrlAccess = (): boolean => {
  if (typeof window === 'undefined') return false
  // 首先检查localStorage中保存的访问类型
  const storedAccessType = getAccessTypeFromStorage()
  if (storedAccessType === 'token_url_access')
    return true

  // 如果没有保存的访问类型，则检查当前URL参数
  const urlParams = new URLSearchParams(window.location.search)
  return urlParams.has('access_token') || urlParams.has('refresh_token')
}

/**
 * 检查当前是否为正常前端登录
 * 优先检查localStorage中保存的访问类型，然后检查当前URL参数
 */
export const isNormalLogin = (): boolean => {
  if (typeof window === 'undefined') return false

  // 首先检查localStorage中保存的访问类型
  const storedAccessType = getAccessTypeFromStorage()
  if (storedAccessType === 'normal_login')
    return true

  // 如果没有保存的访问类型，则检查当前URL参数
  const urlParams = new URLSearchParams(window.location.search)
  return !urlParams.has('access_token') && !urlParams.has('refresh_token')
}

/**
 * 获取当前访问类型
 */
export const getCurrentAccessType = (): AccessType => {
  if (isTokenUrlAccess())
    return 'token_url_access'

  return 'normal_login'
}

/**
 * 在localStorage中设置访问类型标记
 */
export const setAccessTypeInStorage = (accessType: AccessType): void => {
  if (typeof window === 'undefined') return
  localStorage.setItem('dify_access_type', accessType || '')
}

/**
 * 清除localStorage中的访问类型标记
 */
export const clearAccessTypeFromStorage = (): void => {
  if (typeof window === 'undefined') return
  localStorage.removeItem('dify_access_type')
}

/**
 * 清除所有token访问相关的缓存
 * 包括访问类型、console_token、refresh_token等
 */
export const clearAllTokenAccessCache = (): void => {
  if (typeof window === 'undefined') return
  // 清除访问类型
  clearAccessTypeFromStorage()
  // 清除token相关缓存
  localStorage.removeItem('console_token')
  localStorage.removeItem('refresh_token')
  // 清除其他相关缓存
  localStorage.removeItem('setup_status')
  // 清除webapp相关缓存
  localStorage.removeItem('token')
  localStorage.removeItem('webapp_access_token')
  // 清除对话相关缓存
  localStorage.removeItem('conversation_id_info')
}
