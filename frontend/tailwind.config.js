/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Geist Variable", "Geist", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["Bricolage Grotesque Variable", "Bricolage Grotesque", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        // Status colours re-mapped onto the NutriSense palette so every
        // existing emerald/amber usage picks up leaf/turmeric automatically.
        emerald: {
          50: "#EEF7F1", 100: "#D5ECDD", 200: "#ADD8BD", 300: "#7EBF97",
          400: "#4FA474", 500: "#2A8A58", 600: "#1E7A4C", 700: "#17603C",
          800: "#124A2F", 900: "#0D3522",
        },
        amber: {
          50: "#FDF6E5", 100: "#FAEAC0", 200: "#F5D68A", 300: "#EFC055",
          400: "#E9AF31", 500: "#E3A21A", 600: "#C08512", 700: "#9A6810",
          800: "#7A5212", 900: "#5F4012",
        },
        turmeric: "hsl(var(--turmeric))",
        chili: "hsl(var(--chili))",
        steel: "hsl(var(--steel))",
        sidebar: {
          DEFAULT: "hsl(var(--sidebar))",
          foreground: "hsl(var(--sidebar-foreground))",
          muted: "hsl(var(--sidebar-muted))",
          active: "hsl(var(--sidebar-active))",
        },
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
