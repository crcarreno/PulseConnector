"use client"

import { Button } from "@/components/Button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/Dialog"
import { Input } from "@/components/Input"
import { Label } from "@/components/Label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/Select"
import { useEffect, useState } from "react"
import { useAppToast } from "@/components/Toast"


// -------------------- TYPES --------------------
type Dialect = {
  id: string
  name: string
}

// -------------------- HOOK --------------------
export function useDialects() {
  const [dialects, setDialects] = useState<Dialect[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("https://localhost:5000/admin/dialects")
      .then(res => res.json())
      .then(data => setDialects(data.items ?? []))
      .catch(err => console.error("Fetch error:", err))
      .finally(() => setLoading(false))
  }, [])

  return { dialects, loading }
}

type ModalAddConnectionProps = {
  children: React.ReactNode
  onSuccess?: () => void
}

// -------------------- COMPONENT --------------------
export function ModalAddConnection({children, onSuccess,}: ModalAddConnectionProps) {
  const { dialects, loading: dialectsLoading } = useDialects()

  const [submitting, setSubmitting] = useState(false)
  const [open, setOpen] = useState(false)

  const [name, setName] = useState("")
  const [host, setHost] = useState("")
  const [port, setPort] = useState("")
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [databaseName, setDatabaseName] = useState("")
  const [dialectId, setDialectId] = useState<string | null>(null)

  const { showToast } = useAppToast()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!dialectId) return alert("Select a database engine")

    setSubmitting(true)

    const payload = {
      name,
      host,
      port: Number(port),
      username,
      password,
      database_name: databaseName,
      dialect_id: dialectId,
      is_active: true,
    }

    console.log(payload)

    try {
      const res = await fetch("https://localhost:5000/admin/data-sources", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!res.ok) throw new Error(await res.text())

        showToast({
          title: "Connection created",
          description: "Saved successfully",
        })

      onSuccess?.()
      setOpen(false)
    } catch (err) {
      console.error("Create error", err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>

      <DialogContent className="sm:max-w-lg">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Add different database engine connections</DialogTitle>
            <DialogDescription>Add database connections</DialogDescription>

            <div className="mt-4">
              <Label>Name connection</Label>
              <Input value={name} onChange={e => setName(e.target.value)} />
            </div>

            <div className="mt-4">
              <Label>Select database</Label>
              <Select value={dialectId} onValueChange={setDialectId}>
                <SelectTrigger className="mt-2">
                  <SelectValue placeholder="Select database..." />
                </SelectTrigger>
                <SelectContent>
                  {dialectsLoading && (
                    <SelectItem value="loading" disabled>
                      Loading...
                    </SelectItem>
                  )}
                  {dialects.map(d => (
                    <SelectItem key={d.id} value={d.id}>
                      {d.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="mt-4">
              <Label>Host</Label>
              <Input value={host} onChange={e => setHost(e.target.value)} />
            </div>

            <div className="mt-4">
              <Label>Port</Label>
              <Input value={port} onChange={e => setPort(e.target.value)} />
            </div>

            <div className="mt-4">
              <Label>User</Label>
              <Input value={username} onChange={e => setUsername(e.target.value)} />
            </div>

            <div className="mt-4">
              <Label>Password</Label>
              <Input type="password" value={password} onChange={e => setPassword(e.target.value)} />
            </div>

            <div className="mt-4">
              <Label>Database</Label>
              <Input value={databaseName} onChange={e => setDatabaseName(e.target.value)} />
            </div>
          </DialogHeader>

          <DialogFooter className="mt-6">
            <DialogClose asChild>
              <Button type="button" variant="secondary">
                Go back
              </Button>
            </DialogClose>

            <Button type="submit" disabled={submitting} variant="warning">
              {submitting ? "Creating..." : "Add connection"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
