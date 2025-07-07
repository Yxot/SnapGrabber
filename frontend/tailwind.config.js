module.exports = {
  purge: ['./index.html', './script.js'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: '#18181b',
        accent: {
          DEFAULT: '#a78bfa',
          dark: '#7c3aed',
        },
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}; 