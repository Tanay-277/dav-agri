/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dav: {
          bg: "#e8e5df",
          card: "#ffffff",
          pill: "#dcd7cf",
          dark: "#1c1917",
          soil: {
            light: "#7c3726",
            DEFAULT: "#542419",
            dark: "#33150e",
          },
          accent: {
            orange: "#f97316",
            teal: "#14b8a6",
            purple: "#8b5cf6",
            yellow: "#eab308",
            green: "#16a34a",
            red: "#dc2626"
          }
        }
      },
      borderRadius: {
        '3xl': '1.75rem',
        '4xl': '2.25rem',
        '5xl': '3rem',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 8px 30px rgba(0, 0, 0, 0.06)',
        'float': '0 12px 40px rgba(0, 0, 0, 0.12)',
      }
    },
  },
  plugins: [],
}
