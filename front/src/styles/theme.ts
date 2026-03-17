// Thème Netflix pour styled-components

export const theme = {
  colors: {
    background: "#141414",
    surface: "#1f1f1f",
    surfaceHover: "#2a2a2a",
    primary: "#E50914",
    primaryHover: "#b81d24",
    text: "#ffffff",
    textSecondary: "#b3b3b3",
    textMuted: "#666666",
    border: "#333333",
    error: "#e87c03",
    success: "#46d369",
    inputBg: "#333333",
    inputFocus: "#ffffff",
  },
  fonts: {
    base: "'Helvetica Neue', Helvetica, Arial, sans-serif",
  },
  fontSizes: {
    sm: "13px",
    md: "16px",
    lg: "20px",
    xl: "32px",
  },
  radii: {
    sm: "3px",
    md: "6px",
  },
  spacing: {
    xs: "4px",
    sm: "8px",
    md: "16px",
    lg: "24px",
    xl: "40px",
  },
}

export type Theme = typeof theme
