'use client'

import type { ChatConfig } from '@/app/components/base/chat/types'
import Loading from '@/app/components/base/loading'
import { checkOrSetAccessToken } from '@/app/components/share/utils'
import { AccessMode } from '@/models/access-control'
import type { AppData, AppMeta } from '@/models/share'
import { useGetWebAppAccessModeByCode } from '@/service/use-share'
import { usePathname, useSearchParams } from 'next/navigation'
import type { FC, PropsWithChildren } from 'react'
import { useEffect } from 'react'
import { useState } from 'react'
import { create } from 'zustand'
import { useGlobalPublicStore } from './global-public-context'
import { getAccessTypeFromStorage, setAccessTypeInStorage } from '@/utils/access-type'

type WebAppStore = {
  shareCode: string | null
  updateShareCode: (shareCode: string | null) => void
  appInfo: AppData | null
  updateAppInfo: (appInfo: AppData | null) => void
  appParams: ChatConfig | null
  updateAppParams: (appParams: ChatConfig | null) => void
  webAppAccessMode: AccessMode
  updateWebAppAccessMode: (accessMode: AccessMode) => void
  appMeta: AppMeta | null
  updateWebAppMeta: (appMeta: AppMeta | null) => void
  userCanAccessApp: boolean
  updateUserCanAccessApp: (canAccess: boolean) => void
  // 新增：记录访问类型
  accessType: 'normal_login' | 'token_url_access' | null
  updateAccessType: (accessType: 'normal_login' | 'token_url_access' | null) => void
}

export const useWebAppStore = create<WebAppStore>(set => ({
  shareCode: null,
  updateShareCode: (shareCode: string | null) => set(() => ({ shareCode })),
  appInfo: null,
  updateAppInfo: (appInfo: AppData | null) => set(() => ({ appInfo })),
  appParams: null,
  updateAppParams: (appParams: ChatConfig | null) => set(() => ({ appParams })),
  webAppAccessMode: AccessMode.SPECIFIC_GROUPS_MEMBERS,
  updateWebAppAccessMode: (accessMode: AccessMode) => set(() => ({ webAppAccessMode: accessMode })),
  appMeta: null,
  updateWebAppMeta: (appMeta: AppMeta | null) => set(() => ({ appMeta })),
  userCanAccessApp: false,
  updateUserCanAccessApp: (canAccess: boolean) => set(() => ({ userCanAccessApp: canAccess })),
  // 新增：记录访问类型
  accessType: null,
  updateAccessType: (accessType: 'normal_login' | 'token_url_access' | null) => set(() => ({ accessType })),
}))

const getShareCodeFromRedirectUrl = (redirectUrl: string | null): string | null => {
  if (!redirectUrl || redirectUrl.length === 0)
    return null
  const url = new URL(`${window.location.origin}${decodeURIComponent(redirectUrl)}`)
  return url.pathname.split('/').pop() || null
}
const getShareCodeFromPathname = (pathname: string): string | null => {
  const code = pathname.split('/').pop() || null
  if (code === 'webapp-signin')
    return null
  return code
}

const WebAppStoreProvider: FC<PropsWithChildren> = ({ children }) => {
  const isGlobalPending = useGlobalPublicStore(s => s.isGlobalPending)
  const updateWebAppAccessMode = useWebAppStore(state => state.updateWebAppAccessMode)
  const updateShareCode = useWebAppStore(state => state.updateShareCode)
  const updateAccessType = useWebAppStore(state => state.updateAccessType)
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const redirectUrlParam = searchParams.get('redirect_url')

  // Compute shareCode directly
  const shareCode = getShareCodeFromRedirectUrl(redirectUrlParam) || getShareCodeFromPathname(pathname)
  useEffect(() => {
    updateShareCode(shareCode)
  }, [shareCode, updateShareCode])

  const { isFetching, data: accessModeResult } = useGetWebAppAccessModeByCode(shareCode)
  const [isFetchingAccessToken, setIsFetchingAccessToken] = useState(true)

  useEffect(() => {
    if (accessModeResult?.accessMode) {
      updateWebAppAccessMode(accessModeResult.accessMode)
      if (accessModeResult.accessMode === AccessMode.PUBLIC) {
        setIsFetchingAccessToken(true)
        checkOrSetAccessToken(shareCode).finally(() => {
          setIsFetchingAccessToken(false)
        })
      }
      else {
        setIsFetchingAccessToken(false)
      }
    }
  }, [accessModeResult, updateWebAppAccessMode, shareCode])

   // 根据URL参数设置访问类型
  useEffect(() => {
    // 检查URL中是否有access_token或refresh_token参数
    const hasTokenParams = searchParams.has('access_token') || searchParams.has('refresh_token')

    if (hasTokenParams) {
      // 如果有token参数，设置为token_url_access并保存到localStorage
      updateAccessType('token_url_access')
      setAccessTypeInStorage('token_url_access')
    }
    else {
      // 如果没有token参数，尝试从localStorage读取访问类型
      const storedAccessType = getAccessTypeFromStorage()
      if (storedAccessType) {
        updateAccessType(storedAccessType)
      }
      else {
        // 如果localStorage中也没有，设置为正常登录并保存到localStorage
        updateAccessType('normal_login')
        setAccessTypeInStorage('normal_login')
      }
    }
  }, [searchParams, updateAccessType])

  if (isGlobalPending || isFetching || isFetchingAccessToken) {
    return <div className='flex h-full w-full items-center justify-center'>
      <Loading />
    </div>
  }
  return (
    <>
      {children}
    </>
  )
}
export default WebAppStoreProvider
