/**
 * Componente de spinner de carga reutilizable.
 */
export default function LoadingSpinner({ 
  size = 'md', 
  className = '',
  text = 'Cargando...',
  fullScreen = false 
}) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  }

  const spinner = (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div
        className={`${sizeClasses[size]} border-4 border-slate-600 border-t-purple-600 rounded-full animate-spin`}
        role="status"
        aria-label="Cargando"
      />
      {text && (
        <p className="mt-2 text-sm text-slate-400">{text}</p>
      )}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50">
        {spinner}
      </div>
    )
  }

  return spinner
}
