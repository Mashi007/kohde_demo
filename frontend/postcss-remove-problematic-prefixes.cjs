/**
 * Plugin de PostCSS para eliminar prefijos y pseudo-clases problemáticas
 * que causan errores en algunos navegadores modernos
 */
module.exports = () => {
  return {
    postcssPlugin: 'postcss-remove-problematic-prefixes',
    Rule(rule) {
      // Eliminar reglas con pseudo-clases problemáticas
      if (rule.selector) {
        // Eliminar selectores con -ms-backdrop
        if (rule.selector.includes('-ms-backdrop')) {
          rule.remove();
          return;
        }
        // Eliminar selectores con -ms-input-placeholder
        if (rule.selector.includes('-ms-input-placeholder')) {
          rule.remove();
          return;
        }
      }
    },
    Declaration(decl) {
      // Eliminar propiedades problemáticas
      if (decl.prop === '-webkit-text-size-adjust') {
        decl.remove();
        return;
      }
    },
  };
};

module.exports.postcss = true;
