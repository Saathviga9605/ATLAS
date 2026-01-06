/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#FFFFFF',
        'bg-card': '#FAFBFC',
        'bg-secondary': '#F8F9FA',
        'border-color': '#E9ECEF',
        'text-primary': '#1A1D29',
        'text-secondary': '#6C757D',
        'visa-blue': '#003D82',
        'visa-blue-light': '#1A5BA8',
        'visa-orange': '#FF8200',
        'visa-orange-light': '#FFA640',
        'risk-green': '#28A745',
        'risk-amber': '#FFC107',
        'risk-red': '#DC3545',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'bounce-gentle': 'bounce-gentle 2s infinite',
        'slide-up': 'slide-up 0.6s ease-out',
        'slide-right': 'slide-right 0.5s ease-out',
        'fade-in': 'fade-in 0.8s ease-out',
        'scale-in': 'scale-in 0.4s ease-out',
        'rotate-slow': 'rotate-slow 20s linear infinite',
        'pulse-soft': 'pulse-soft 3s ease-in-out infinite',
        'shimmer-wave': 'shimmer-wave 3s ease-in-out infinite',
        'card-hover': 'card-hover 0.3s ease-out',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'morph-shape': 'morph-shape 4s ease-in-out infinite',
        'text-gradient': 'text-gradient 3s ease-in-out infinite',
        'border-dance': 'border-dance 2s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '33%': { transform: 'translateY(-20px) rotate(1deg)' },
          '66%': { transform: 'translateY(-10px) rotate(-0.5deg)' },
        },
        'bounce-gentle': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-right': {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'rotate-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.05)' },
        },
        'shimmer-wave': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        'card-hover': {
          '0%': { transform: 'translateY(0) scale(1)' },
          '100%': { transform: 'translateY(-8px) scale(1.02)' },
        },
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 61, 130, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(255, 130, 0, 0.6), 0 0 60px rgba(0, 61, 130, 0.4)' },
        },
        'morph-shape': {
          '0%, 100%': { borderRadius: '1rem' },
          '25%': { borderRadius: '2rem 1rem 1rem 2rem' },
          '50%': { borderRadius: '50%' },
          '75%': { borderRadius: '1rem 2rem 2rem 1rem' },
        },
        'text-gradient': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        'border-dance': {
          '0%': { borderColor: '#003D82' },
          '25%': { borderColor: '#FF8200' },
          '50%': { borderColor: '#1A5BA8' },
          '75%': { borderColor: '#FFA640' },
          '100%': { borderColor: '#003D82' },
        },
      },
      boxShadow: {
        'visa': '0 4px 20px rgba(0, 61, 130, 0.15)',
        'visa-hover': '0 8px 40px rgba(0, 61, 130, 0.25)',
        'orange': '0 4px 20px rgba(255, 130, 0, 0.15)',
        'orange-hover': '0 8px 40px rgba(255, 130, 0, 0.25)',
        'card': '0 2px 10px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 8px 30px rgba(0, 61, 130, 0.2)',
        'glow': '0 0 30px rgba(255, 130, 0, 0.3)',
        'rainbow': '0 0 20px rgba(0, 61, 130, 0.3), 0 0 40px rgba(255, 130, 0, 0.2)',
      },
    },
  },
  plugins: [],
}
