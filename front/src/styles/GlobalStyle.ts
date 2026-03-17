import { createGlobalStyle } from "styled-components"

// Le thème est injecté via ThemeProvider — DefaultTheme est augmenté dans styled.d.ts
const GlobalStyle = createGlobalStyle`
  *, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    background-color: ${({ theme }) => theme.colors.background};
    color: ${({ theme }) => theme.colors.text};
    font-family: ${({ theme }) => theme.fonts.base};
    font-size: ${({ theme }) => theme.fontSizes.md};
    -webkit-font-smoothing: antialiased;
  }

  a {
    color: inherit;
    text-decoration: none;
  }

  button {
    cursor: pointer;
    border: none;
    outline: none;
  }

  input, textarea {
    outline: none;
  }
`

export default GlobalStyle
