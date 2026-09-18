import { createTheme, type MantineColorsTuple } from "@mantine/core"

const brandGreen: MantineColorsTuple = [
  "#e6f2ed",
  "#d0e6dd",
  "#a3ccbc",
  "#74b199",
  "#4f9b7c",
  "#398e6a",
  "#2b8861",
  "#196b55",
  "#10503f",
  "#003d2c",
]

export const theme = createTheme({
  colors: {
    brand: brandGreen,
  },
  defaultRadius: "md",
  fontFamily:
    'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  headings: {
    fontFamily: 'Georgia, "Times New Roman", serif',
  },
  primaryColor: "brand",
})
