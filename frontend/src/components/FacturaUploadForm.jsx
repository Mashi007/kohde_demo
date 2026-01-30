import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../config/api'
import toast from 'react-hot-toast'
import { validateFile, ALLOWED_FILE_TYPES } from '../utils/validation'
import { Upload, Sparkles } from 'lucide-react'

export default function FacturaUploadForm({ onClose, onSuccess }) {
  const [file, setFile] = useState(null)
  const [tipo, setTipo] = useState('proveedor')
  const [preview, setPreview] = useState(null)

  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: (formData) => api.post('/logistica/facturas/ingresar-imagen', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    onSuccess: (response) => {
      toast.success('Factura procesada correctamente')
      queryClient.invalidateQueries(['facturas'])
      queryClient.invalidateQueries(['factura-ultima'])
      queryClient.invalidateQueries(['facturas-pendientes'])
      onSuccess?.(response.data)
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al procesar factura')
    },
  })

  const ejemploOCRMutation = useMutation({
    mutationFn: () => api.post('/logistica/facturas/ejemplo-ocr'),
    onSuccess: (response) => {
      toast.success('Factura ejemplo OCR creada correctamente')
      queryClient.invalidateQueries(['facturas'])
      queryClient.invalidateQueries(['factura-ultima'])
      queryClient.invalidateQueries(['facturas-pendientes'])
      // Pasar la factura creada al callback para abrir el modal de confirmación
      if (onSuccess) {
        onSuccess(response.data)
      }
      onClose()
    },
    onError: (error) => {
      toast.error(error.response?.data?.error || 'Error al crear factura ejemplo')
    },
  })

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (!selectedFile) {
      return
    }

    // Validar archivo antes de procesarlo
    const validation = validateFile(selectedFile, {
      allowedTypes: [...ALLOWED_FILE_TYPES.image, ...ALLOWED_FILE_TYPES.pdf],
      maxSizeMB: 16
    })

    if (!validation.valid) {
      toast.error(validation.error)
      e.target.value = '' // Limpiar input
      setFile(null)
      setPreview(null)
      return
    }

    setFile(selectedFile)
    // Crear preview solo para imágenes
    if (selectedFile.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(selectedFile)
    } else {
      setPreview(null)
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

      <div className="bg-purple-500/10 border border-purple-500/50 rounded-lg p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h4 className="font-semibold text-purple-300 mb-1 flex items-center gap-2">
              <Sparkles size={16} />
              Ejemplo de Factura OCR
            </h4>
            <p className="text-xs text-purple-400">
              Crea una factura de ejemplo realista con datos OCR simulados que cumple todas las reglas de negocio.
              Incluye items identificables, cálculos correctos de IVA y estructura completa.
            </p>
          </div>
          <button
            type="button"
            onClick={() => ejemploOCRMutation.mutate()}
            disabled={ejemploOCRMutation.isPending}
            className="ml-4 bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm flex items-center gap-2 disabled:opacity-50 whitespace-nowrap"
          >
            <Sparkles size={16} />
            {ejemploOCRMutation.isPending ? 'Creando...' : 'Crear Ejemplo'}
          </button>
        </div>
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
