import { X } from 'lucide-react'

/**
 * Componente de diálogo de confirmación reutilizable.
 * Reemplaza window.confirm con una solución accesible y personalizable.
 */
export default function ConfirmDialog({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title = 'Confirmar acción',
  message = '¿Estás seguro de realizar esta acción?',
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  variant = 'danger', // 'danger', 'warning', 'info'
  isLoading = false
}) {
  if (!isOpen) return null

  const variantStyles = {
    danger: {
      button: 'bg-red-600 hover:bg-red-700',
      icon: 'text-red-500'
    },
    warning: {
      button: 'bg-yellow-600 hover:bg-yellow-700',
      icon: 'text-yellow-500'
    },
    info: {
      button: 'bg-blue-600 hover:bg-blue-700',
      icon: 'text-blue-500'
    }
  }

  const styles = variantStyles[variant] || variantStyles.danger

  const handleConfirm = () => {
    if (!isLoading) {
      onConfirm()
    }
  }

  const handleCancel = () => {
    if (!isLoading) {
      onClose()
    }
  }

  // Manejar tecla Escape
  const handleKeyDown = (e) => {
    if (e.key === 'Escape' && !isLoading) {
      onClose()
    }
  }

  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={handleCancel}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-message"
    >
      <div 
        className="bg-slate-800 rounded-lg border border-slate-700 w-full max-w-md mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-6 border-b border-slate-700">
          <h2 id="confirm-dialog-title" className="text-xl font-bold">{title}</h2>
          <button
            onClick={handleCancel}
            disabled={isLoading}
            className="text-slate-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Cerrar diálogo"
          >
            <X size={24} />
          </button>
        </div>
        
        <div className="p-6">
          <p id="confirm-dialog-message" className="text-slate-300 mb-6">
            {message}
          </p>
          
          <div className="flex gap-3 justify-end">
            <button
              onClick={handleCancel}
              disabled={isLoading}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {cancelText}
            </button>
            <button
              onClick={handleConfirm}
              disabled={isLoading}
              className={`px-4 py-2 ${styles.button} rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2`}
            >
              {isLoading && (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              )}
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
