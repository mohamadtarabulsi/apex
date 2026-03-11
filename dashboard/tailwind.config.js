/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        apex: {
          bg: '#0a0a0f',
          panel: '#12121a',
          border: '#1e1e2e',
          green: '#00ff88',
          blue: '#0088ff',
          red: '#ff3366',
          amber: '#ffaa00',
          text: '#e0e0e0',
          muted: '#666680',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
    },
  },
  plugins: [],
}
