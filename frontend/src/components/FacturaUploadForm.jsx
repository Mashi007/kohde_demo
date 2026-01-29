import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import { Upload } from 'lucide-react'

export default function FacturaUploadForm({ onClose, onSuccess }) {
  const [file, setFile] = useState(null)
  const [tipo, setTipo] = useState('proveedor')
  const [preview, setPreview] = useState(null)

  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: (formData) => api.post('/contabilidad/facturas/ingresar-imagen', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess: () => {
      toast.success('Factura procesada correctamente')
      queryClient.invalidateQueries(['facturas'])
      onSuccess?.()
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al procesar factura')
    },
  })

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      // Crear preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(selectedFile)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!file) {
      toast.error('Selecciona una imagen')
      return
    }

    const formData = new FormData()
    formData.append('imagen', file)
    formData.append('tipo', tipo)

    uploadMutation.mutate(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">Tipo de Factura *</label>
        <select
          required
          value={tipo}
          onChange={(e) => setTipo(e.target.value)}
          className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:border-purple-500"
        >
          <option value="proveedor">Proveedor</option>
          <option value="cliente">Cliente</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">Imagen de Factura *</label>
        <div className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center">
          <input
            type="file"
            accept="image/*,.pdf"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
            required
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer flex flex-col items-center gap-2"
          >
            <Upload className="text-purple-500" size={32} />
            <span className="text-slate-400">
              {file ? file.name : 'Haz clic para seleccionar imagen'}
            </span>
          </label>
        </div>
        {preview && (
          <div className="mt-4">
            <img
              src={preview}
              alt="Preview"
              className="max-w-full h-auto rounded-lg border border-slate-700"
            />
          </div>
        )}
      </div>

      <div className="bg-blue-500/10 border border-blue-500/50 rounded-lg p-4 text-sm text-blue-400">
        <p>💡 La factura será procesada automáticamente con OCR para extraer los datos.</p>
      </div>

      <div className="flex gap-4 pt-4">
        <button
          type="submit"
          disabled={uploadMutation.isPending || !file}
          className="flex-1 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {uploadMutation.isPending ? (
            'Procesando...'
          ) : (
            <>
              <Upload size={20} />
              Subir y Procesar
            </>
          )}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="flex-1 bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}
