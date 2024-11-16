'use client'
import type { FC } from 'react'
import classNames from '@/utils/classnames'
import { useSelector } from '@/context/app-context'

type LogoSiteCProps = {
  className?: string
}

const LogoSiteC: FC<LogoSiteCProps> = ({
  className,
}) => {
  const { theme } = useSelector((s) => {
    return {
      theme: s.theme,
    }
  })

  const src = theme === 'light' ? '/logo/logo-site-c.png' : `/logo/logo-site-c-${theme}.png`
  return (
    <img
      src={src}
      className={classNames('block w-auto h-10', className)}
      alt='logo'
    />
  )
}

export default LogoSiteC
