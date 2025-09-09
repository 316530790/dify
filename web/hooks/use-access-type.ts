import { useWebAppStore } from '@/context/web-app-context'
import { getAccessTypeFromStorage, getCurrentAccessType, isNormalLogin, isTokenUrlAccess } from '@/utils/access-type'

/**
 * 自定义hook：获取当前访问类型信息
 * @returns 访问类型相关的状态和方法
 */
export const useAccessType = () => {
  const { accessType, updateAccessType } = useWebAppStore()

  return {
    // 当前访问类型
    accessType,
    // 更新访问类型
    updateAccessType,
    // 是否为通过URL参数访问
    isTokenUrlAccess: isTokenUrlAccess(),
    // 是否为正常前端登录
    isNormalLogin: isNormalLogin(),
    // 从localStorage获取访问类型
    getAccessTypeFromStorage,
    // 获取当前访问类型（基于URL参数）
    getCurrentAccessType,
    // 是否为首次访问（accessType为null）
    isFirstAccess: accessType === null,
  }
}
