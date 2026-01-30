const removeProblematicPrefixes = require('./postcss-remove-problematic-prefixes.cjs');

module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {
      // Configurar browserslist para evitar prefijos problemáticos
      overrideBrowserslist: [
        '> 1%',
        'last 2 versions',
        'not dead',
        'not ie <= 11', // Excluir IE que requiere prefijos problemáticos
      ],
      // Deshabilitar propiedades específicas problemáticas
      grid: false,
      // Evitar agregar prefijos para propiedades problemáticas
      flexbox: 'no-2009', // Solo prefijos necesarios, no los antiguos
    },
    // Eliminar prefijos y pseudo-clases problemáticas después de autoprefixer
    'postcss-remove-problematic-prefixes': removeProblematicPrefixes,
  },
}
