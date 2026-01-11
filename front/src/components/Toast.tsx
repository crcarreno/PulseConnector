"use client"

import * as Toast from "@radix-ui/react-toast"
import { createContext, useContext, useState, ReactNode } from "react"

type ToastData = {
  title: string
  description?: string
}

type ToastContextType = {
  showToast: (data: ToastData) => void
}

const ToastContext = createContext<ToastContextType | null>(null)

export function useAppToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error("useAppToast must be used inside AppToastProvider")
  return ctx
}

export function AppToastProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const [toast, setToast] = useState<ToastData | null>(null)

  const showToast = (data: ToastData) => {
    setToast(data)
    setOpen(true)
  }

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      <Toast.Provider>
        <Toast.Root
          open={open}
          onOpenChange={setOpen}
          className="rounded-md border bg-background p-4 shadow-lg"
        >
          <Toast.Title className="font-medium">
            {toast?.title}
          </Toast.Title>

          {toast?.description && (
            <Toast.Description className="text-sm text-muted-foreground">
              {toast.description}
            </Toast.Description>
          )}
        </Toast.Root>

        <Toast.Viewport className="fixed top-4 right-4 z-50 w-96 max-w-[90vw]" />
      </Toast.Provider>
    </ToastContext.Provider>
  )
}
