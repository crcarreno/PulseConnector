"use client"

import { ThemeProvider } from "next-themes"
import { AppToastProvider } from "@/components/Toast"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AppToastProvider>
      <ThemeProvider defaultTheme="system" attribute="class">
        {children}
      </ThemeProvider>
    </AppToastProvider>
  )
}
