"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/Button"
import { Card } from "@/components/Card"
import { Checkbox } from "@/components/Checkbox"
import { Divider } from "@/components/Divider"
import { Input } from "@/components/Input"
import { Label } from "@/components/Label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/Select"
import { Switch } from "@/components/Switch"
import { RiExternalLinkLine } from "@remixicon/react"
import { roles } from "@/data/data"
import { useAppToast } from "@/components/Toast"

export function useDataUsers() {

  const [users, setUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {

    setLoading(true)

    try {

      const res = await fetch("https://localhost:5000/admin/users")
      const data = await res.json()
      setUsers(data ?? [])
console.log(data)
    } catch (err) {
      console.error("Fetch error:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return {
    users,
    loading,
    refetch: fetchData
  }
}

export default function Users() {

  const { users, loading, refetch } = useDataUsers()
  const { showToast } = useAppToast()

  const [user, setUser] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [password, setPassword] = useState("")
  const [enabled, setEnabled] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!user || !password) return

    setSubmitting(true)

    const payload = {
      user,
      display_name: displayName,
      password_hash: password,
      is_active: enabled,
    }

    try {
      const res = await fetch("https://localhost:5000/admin/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!res.ok) throw new Error(await res.text())

      showToast({
        title: "User created",
        description: "Saved successfully",
      })

      // reset form
      setUser("")
      setDisplayName("")
      setPassword("")
      setEnabled(true)

      refetch()

    } catch (err) {
      console.error("Create user error", err)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <p>Loading...</p>

  return (
  <div className="space-y-10">

      {/* ---------------- CREATE USER ---------------- */}
      <section>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-x-14 gap-y-8 md:grid-cols-3">
            <div>
              <h2 className="font-semibold">Create user</h2>
              <p className="mt-1 text-sm text-gray-500">
                Manage user credentials and status.
              </p>
            </div>

            <div className="md:col-span-2">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-6">

                <div className="col-span-full sm:col-span-3">
                  <Label>User</Label>
                  <Input
                    className="mt-2"
                    value={user}
                    onChange={e => setUser(e.target.value)}
                    placeholder="admin"
                  />
                </div>

                <div className="col-span-full sm:col-span-3">
                  <Label>Password</Label>
                  <Input
                    type="password"
                    className="mt-2"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="******"
                  />
                </div>

                <div className="col-span-full">
                  <Label>Display name</Label>
                  <Input
                    className="mt-2"
                    value={displayName}
                    onChange={e => setDisplayName(e.target.value)}
                    placeholder="Administrator"
                  />
                </div>

                <div className="col-span-full sm:col-span-3">
                  <Label>Active</Label>
                  <div className="mt-2">
                    <Switch checked={enabled} onCheckedChange={setEnabled} />
                  </div>
                </div>

                <div className="col-span-full mt-6 flex justify-end">
                  <Button type="submit" disabled={submitting}>
                    {submitting ? "Creating..." : "Create user"}
                  </Button>
                </div>

              </div>
            </div>
          </div>
        </form>
      </section>

      <Divider />

      {/* ---------------- USER LIST ---------------- */}
      <section>
        <ul className="divide-y">
          {users.map(u => (
            <li key={u.id} className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm font-medium">{u.user}</p>
                <p className="text-xs text-gray-500">{u.display_name}</p>
                <p className="text-xs text-gray-500">{u.email}</p>
              </div>

              <div className="flex items-center gap-2">
                <Switch checked={u.is_active} disabled />
                <span className="text-sm text-gray-500">
                  {u.is_active ? "On" : "Off"}
                </span>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <Divider />

      {/* ---------------- PLACEHOLDERS ---------------- */}
      <Card className="p-4 text-sm text-gray-500">
        Roles, permissions, edit & delete actions go here next.
      </Card>

    </div>
  )

}
