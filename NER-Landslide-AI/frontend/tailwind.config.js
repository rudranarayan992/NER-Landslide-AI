/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f2f9f4',
          100: '#dfeee0',
          500: '#2f6f46',
          700: '#214f34',
          900: '#133325',
        },
      },
    },
  },
  plugins: [],
};
