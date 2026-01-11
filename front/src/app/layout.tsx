import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { siteConfig } from "./siteConfig"
import { Providers } from "./providers"
import { Sidebar } from "@/components/ui/navigation/Sidebar"

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
})

export const metadata: Metadata = {
  metadataBase: new URL("https://localhost:3000"),
  title: siteConfig.name,
  description: siteConfig.description,
  keywords: [],
  authors: [
    {
      name: "yourname",
      url: "",
    },
  ],
  creator: "yourname",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteConfig.url,
    title: siteConfig.name,
    description: siteConfig.description,
    siteName: siteConfig.name,
  },
    icons: {
        icon: "/favicon.ico",
      },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.className} overflow-y-scroll scroll-auto antialiased dark:bg-gray-950`}
      >
        <Providers>
          <Sidebar />
          <main className="lg:pl-72">{children}</main>
        </Providers>
      </body>
    </html>
  )
}
