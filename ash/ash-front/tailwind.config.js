// tailwind.config.js
const { nextui } = require("@nextui-org/react");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // ...
    "./node_modules/@nextui-org/theme/dist/**/*.{js,ts,jsx,tsx}",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#0e1625",
        foreground: "#E8E8FC",
        lightblue: '#45EDF2',
        transparent: 'transparent',
      }
    },
  },
  darkMode: "class",
  plugins: [nextui()],
};