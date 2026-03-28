import { useEffect, useRef } from 'react'
import type { Notification } from '../../types'

interface NotificationPanelProps {
  notifications: Notification[]
  onMarkAsRead: (id: string) => void
  onMarkAllAsRead: () => void
  onClose: () => void
}

export function NotificationPanel({ notifications, onMarkAsRead, onMarkAllAsRead, onClose }: NotificationPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [onClose])

  const hasUnread = notifications.some((n) => !n.isRead)

  return (
    <div
      ref={panelRef}
      className="absolute top-full right-0 mt-2 w-80 bg-surface-container border-2 border-black shadow-hard z-50"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b-2 border-black">
        <span className="font-headline font-black text-sm uppercase tracking-tight">Notifications</span>
        {hasUnread && (
          <button
            onClick={onMarkAllAsRead}
            className="text-[10px] font-black uppercase text-primary-container hover:underline"
          >
            Mark all read
          </button>
        )}
      </div>

      {/* List */}
      {notifications.length === 0 ? (
        <div className="px-4 py-6 text-center text-on-surface-variant text-sm font-label">
          No notifications yet
        </div>
      ) : (
        <ul
            className="divide-y-2 divide-black overflow-y-auto"
            style={{ maxHeight: 'calc(3 * 4.5rem)' }}
          >
            {notifications.map((n) => (
              <li
                key={n.id}
                onClick={() => { if (!n.isRead) onMarkAsRead(n.id) }}
                className={`flex gap-3 px-4 py-3 cursor-pointer hover:bg-surface-container-high transition-none ${!n.isRead ? 'bg-surface-container-low' : ''}`}
              >
                {/* Unread dot */}
                <div className="pt-1 flex-shrink-0">
                  <div className={`w-2 h-2 rounded-full border border-black ${!n.isRead ? 'bg-primary-container' : 'bg-transparent'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm leading-tight ${!n.isRead ? 'font-black text-on-surface' : 'font-medium text-on-surface-variant'}`}>
                    {n.title}
                  </p>
                  {n.body && (
                    <p className="text-xs text-on-surface-variant mt-0.5 line-clamp-2">{n.body}</p>
                  )}
                  <p className="text-[10px] text-on-surface-variant mt-1 font-label uppercase">
                    {relativeTime(n.createdAt)}
                  </p>
                </div>
              </li>
            ))}
          </ul>
      )}
    </div>
  )
}

function relativeTime(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 60) return `${diff}s ago`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}
