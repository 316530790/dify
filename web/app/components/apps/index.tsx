'use client'
import { useEducationInit } from '@/app/education-apply/hooks'
import List from './list'
import useDocumentTitle from '@/hooks/use-document-title'
import { useTranslation } from 'react-i18next'
import { useAccessType } from '@/hooks/use-access-type'
import { clearAllTokenAccessCache } from '@/utils/access-type'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

const Apps = () => {
  const { t } = useTranslation()
  const { isTokenUrlAccess } = useAccessType()
  const router = useRouter()

  useDocumentTitle(t('common.menus.apps'))
  useEducationInit()

  // 如果之前是通过token访问的，清除缓存并跳转到登录页
  useEffect(() => {
    if (isTokenUrlAccess) {
      // 清除所有token访问相关的缓存
      clearAllTokenAccessCache()
      // 强制跳转到登录页面
      router.replace('/signin')
    }
  }, [isTokenUrlAccess, router])

  return (
    <div className='relative flex h-0 shrink-0 grow flex-col overflow-y-auto bg-background-body'>
      <List />
    </div >
  )
}

export default Apps
