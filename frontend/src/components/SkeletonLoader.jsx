/**
 * Componente de skeleton loader para estados de carga.
 */
export default function SkeletonLoader({ 
  type = 'text',
  lines = 3,
  className = '',
  width = 'full'
}) {
  const widthClasses = {
    full: 'w-full',
    '3/4': 'w-3/4',
    '1/2': 'w-1/2',
    '1/4': 'w-1/4',
  }

  if (type === 'text') {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={`h-4 bg-slate-700 rounded animate-pulse ${
              widthClasses[width] || widthClasses.full
            } ${i === lines - 1 ? 'w-3/4' : ''}`}
          />
        ))}
      </div>
    )
  }

  if (type === 'table') {
    return (
      <div className={`space-y-3 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="h-4 bg-slate-700 rounded animate-pulse flex-1" />
            <div className="h-4 bg-slate-700 rounded animate-pulse w-1/4" />
            <div className="h-4 bg-slate-700 rounded animate-pulse w-1/4" />
          </div>
        ))}
      </div>
    )
  }

  if (type === 'card') {
    return (
      <div className={`bg-slate-800 p-6 rounded-lg border border-slate-700 ${className}`}>
        <div className="h-6 bg-slate-700 rounded animate-pulse w-1/3 mb-4" />
        <div className="space-y-2">
          <div className="h-4 bg-slate-700 rounded animate-pulse w-full" />
          <div className="h-4 bg-slate-700 rounded animate-pulse w-5/6" />
          <div className="h-4 bg-slate-700 rounded animate-pulse w-4/6" />
        </div>
      </div>
    )
  }

  return null
}
