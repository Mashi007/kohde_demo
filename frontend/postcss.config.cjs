module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {
      // Evitar agregar propiedades webkit-text-size-adjust que causan errores
      overrideBrowserslist: ['> 1%', 'last 2 versions'],
      // Deshabilitar propiedades específicas problemáticas
      grid: false,
    },
  },
}
