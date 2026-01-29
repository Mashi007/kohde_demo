import { ChevronLeft, ChevronRight } from 'lucide-react'

/**
 * Componente de paginación reutilizable.
 * Usa los headers del backend: X-Total-Count, X-Page-Size, X-Page-Offset
 */
export default function Pagination({
  total,
  pageSize,
  currentPage,
  onPageChange,
  className = '',
  showInfo = true,
  showPageSizeSelector = true,
  pageSizeOptions = [10, 25, 50, 100]
}) {
  const totalPages = Math.ceil(total / pageSize)
  const startItem = (currentPage - 1) * pageSize + 1
  const endItem = Math.min(currentPage * pageSize, total)

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      onPageChange(newPage)
    }
  }

  const handlePageSizeChange = (e) => {
    const newPageSize = parseInt(e.target.value)
    const newTotalPages = Math.ceil(total / newPageSize)
    const newPage = Math.min(currentPage, newTotalPages)
    onPageChange(newPage, newPageSize)
  }

  if (total === 0) {
    return null
  }

  // Generar números de página a mostrar
  const getPageNumbers = () => {
    const pages = []
    const maxVisible = 5
    
    if (totalPages <= maxVisible) {
      // Mostrar todas las páginas si son pocas
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Mostrar páginas con elipsis
      if (currentPage <= 3) {
        // Al inicio
        for (let i = 1; i <= 4; i++) {
          pages.push(i)
        }
        pages.push('ellipsis')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 2) {
        // Al final
        pages.push(1)
        pages.push('ellipsis')
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i)
        }
      } else {
        // En el medio
        pages.push(1)
        pages.push('ellipsis')
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i)
        }
        pages.push('ellipsis')
        pages.push(totalPages)
      }
    }
    
    return pages
  }

  return (
    <div className={`flex flex-col sm:flex-row items-center justify-between gap-4 ${className}`}>
      {showInfo && (
        <div className="text-sm text-slate-400">
          Mostrando {startItem} - {endItem} de {total} resultados
        </div>
      )}

      <div className="flex items-center gap-2">
        {/* Selector de tamaño de página */}
        {showPageSizeSelector && (
          <select
            value={pageSize}
            onChange={handlePageSizeChange}
            className="px-3 py-1.5 bg-slate-700 border border-slate-600 rounded-lg text-sm focus:outline-none focus:border-purple-500"
          >
            {pageSizeOptions.map(size => (
              <option key={size} value={size}>
                {size} por página
              </option>
            ))}
          </select>
        )}

        {/* Botones de navegación */}
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Página anterior"
        >
          <ChevronLeft size={18} />
        </button>

        {/* Números de página */}
        <div className="flex gap-1">
          {getPageNumbers().map((page, index) => {
            if (page === 'ellipsis') {
              return (
                <span key={`ellipsis-${index}`} className="px-2 text-slate-400">
                  ...
                </span>
              )
            }
            return (
              <button
                key={page}
                onClick={() => handlePageChange(page)}
                className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                  currentPage === page
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                }`}
                aria-label={`Ir a página ${page}`}
                aria-current={currentPage === page ? 'page' : undefined}
              >
                {page}
              </button>
            )
          })}
        </div>

        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="p-2 bg-slate-700 hover:bg-slate-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Página siguiente"
        >
          <ChevronRight size={18} />
        </button>
      </div>
    </div>
  )
}
