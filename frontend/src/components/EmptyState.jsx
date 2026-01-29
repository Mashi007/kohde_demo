/**
 * Componente para estados vacíos reutilizable.
 */
export default function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  actionLabel,
  className = ''
}) {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center ${className}`}>
      {Icon && (
        <div className="mb-4 p-4 bg-slate-700/50 rounded-full">
          <Icon size={48} className="text-slate-400" />
        </div>
      )}
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      {description && (
        <p className="text-slate-400 mb-6 max-w-md">{description}</p>
      )}
      {action && actionLabel && (
        <button
          onClick={action}
          className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  )
}
