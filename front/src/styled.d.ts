/**
 * Augmente DefaultTheme de styled-components avec notre thème applicatif.
 * Cela permet à TypeScript de typer `theme.colors`, `theme.spacing`, etc.
 * dans tous les styled-components sans cast supplémentaire.
 */
import type { Theme } from "@/styles/theme"

declare module "styled-components" {
  // eslint-disable-next-line @typescript-eslint/no-empty-interface
  export interface DefaultTheme extends Theme {}
}
