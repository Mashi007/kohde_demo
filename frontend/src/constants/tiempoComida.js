/**
 * Constantes para tiempo de comida / tipo de receta
 * Asegura consistencia en todos los formularios
 */

// Valores en minúsculas (para formularios y backend)
export const TIEMPO_COMIDA_VALUES = {
  DESAYUNO: 'desayuno',
  ALMUERZO: 'almuerzo',
  CENA: 'cena',
}

// Etiquetas para mostrar (primera letra mayúscula)
export const TIEMPO_COMIDA_LABELS = {
  [TIEMPO_COMIDA_VALUES.DESAYUNO]: 'Desayuno',
  [TIEMPO_COMIDA_VALUES.ALMUERZO]: 'Almuerzo',
  [TIEMPO_COMIDA_VALUES.CENA]: 'Cena',
}

// Valores para selects (array de objetos {value, label})
export const TIEMPO_COMIDA_OPTIONS = [
  { value: TIEMPO_COMIDA_VALUES.DESAYUNO, label: TIEMPO_COMIDA_LABELS[TIEMPO_COMIDA_VALUES.DESAYUNO] },
  { value: TIEMPO_COMIDA_VALUES.ALMUERZO, label: TIEMPO_COMIDA_LABELS[TIEMPO_COMIDA_VALUES.ALMUERZO] },
  { value: TIEMPO_COMIDA_VALUES.CENA, label: TIEMPO_COMIDA_LABELS[TIEMPO_COMIDA_VALUES.CENA] },
]

// Colores para badges (consistentes en toda la app)
export const TIEMPO_COMIDA_COLORS = {
  [TIEMPO_COMIDA_VALUES.DESAYUNO]: 'bg-yellow-600/20 text-yellow-300 border-yellow-500/50',
  [TIEMPO_COMIDA_VALUES.ALMUERZO]: 'bg-orange-600/20 text-orange-300 border-orange-500/50',
  [TIEMPO_COMIDA_VALUES.CENA]: 'bg-blue-600/20 text-blue-300 border-blue-500/50',
}

// Función helper para obtener la etiqueta
export const getTiempoComidaLabel = (value) => {
  return TIEMPO_COMIDA_LABELS[value] || value
}

// Función helper para obtener el color del badge
export const getTiempoComidaColor = (value) => {
  return TIEMPO_COMIDA_COLORS[value] || 'bg-slate-600/20 text-slate-300 border-slate-500/50'
}

// Valor por defecto
export const TIEMPO_COMIDA_DEFAULT = TIEMPO_COMIDA_VALUES.ALMUERZO
