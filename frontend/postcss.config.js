const removeTextSizeAdjust = () => {
  return {
    postcssPlugin: 'postcss-remove-text-size-adjust',
    Declaration(decl) {
      // Eliminar todas las propiedades relacionadas con text-size-adjust
      if (
        decl.prop === '-webkit-text-size-adjust' ||
        decl.prop === '-moz-text-size-adjust' ||
        decl.prop === 'text-size-adjust'
      ) {
        decl.remove()
      }
    },
  }
}

removeTextSizeAdjust.postcss = true

export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    [removeTextSizeAdjust]: {},
  },
}
