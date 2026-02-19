"use client"

import { useEffect, useState, useCallback } from "react"
import { Button } from "@/components/Button"
import { Card } from "@/components/Card"
import { Divider } from "@/components/Divider"
import { Input } from "@/components/Input"
import { Label } from "@/components/Label"
import { Switch } from "@/components/Switch"
import { useAppToast } from "@/components/Toast"
import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "@/components/ui/data-table/DataTable"

type User = {
  user: string
  display_name: string
  active: number | boolean | string
}

function isUserActive(value: User["active"]) {
  return value === 1 || value === true || value === "1"
}

  export function useDataUsers() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {

    setLoading(true)

    try {

      const res = await fetch("https://localhost:5000/api/admin/users")
      const data = await res.json()

      setUsers(data.data ?? [])

    } catch (err) {
      console.error("Fetch error:", err)
      setUsers([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { users, loading, refetch: fetchData }
}

const userColumns: ColumnDef<User>[] = [
  {
    accessorKey: "user",
    header: "User",
    cell: ({ row }) => <p className="text-sm font-medium">{row.original.user}</p>,
  },
  {
    accessorKey: "display_name",
    header: "Display name",
    cell: ({ row }) => <p className="text-xs text-gray-500">{row.original.display_name}</p>,
  },
  {
    accessorKey: "active",
    header: "Active",
    cell: ({ row }) => <Switch checked={isUserActive(row.original.active)} disabled />,
  },
]

export default function Users() {
  const { users, loading, refetch } = useDataUsers()
  const { showToast } = useAppToast()

  const [editingUser, setEditingUser] = useState<string | null>(null)
  const [user, setUser] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [password, setPassword] = useState("")
  const [enabled, setEnabled] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  function loadForEdit(item: User) {
    setEditingUser(item.user)
    setUser(item.user)
    setDisplayName(item.display_name ?? "")
    setPassword("")
    setEnabled(isUserActive(item.active))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!user) return
    if (!editingUser && !password) return

    setSubmitting(true)

    try {

      if (editingUser) {
        const fields: Record<string, string> = { user: editingUser }
        if (displayName) fields.display_name = displayName
        if (password) fields.password_hash = password

        if (Object.keys(fields).length > 1) {
          const updateRes = await fetch("https://localhost:5000/api/admin/users/update", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(fields),
          })

          if (!updateRes.ok) throw new Error(await updateRes.text())
        }

        const activeRes = await fetch("https://localhost:5000/api/admin/users/disable", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user: editingUser, action: enabled ? 1 : 0 }),
        })

        if (!activeRes.ok) throw new Error(await activeRes.text())
      } else {
        const res = await fetch("https://localhost:5000/api/admin/users", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user,
            display_name: displayName,
            password_hash: password,
          }),
        })

        if (!res.ok) throw new Error(await res.text())
      }

      showToast({
        title: editingUser ? "User updated" : "User created",
        description: "Saved successfully",
      })

      setEditingUser(null)
      setUser("")
      setDisplayName("")
      setPassword("")
      setEnabled(true)

      refetch()

    } catch (err) {
      console.error("Save user error", err)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <p>Loading...</p>

  return (
      <div className="space-y-10">
      <section>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-x-14 gap-y-8 md:grid-cols-3">
            <div>
              <h2 className="font-semibold">{editingUser ? "Edit user" : "Create user"}</h2>
              <p className="mt-1 text-sm text-gray-500">Manage user credentials and status.</p>
            </div>

            <div className="md:col-span-2">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-6">

                <div className="col-span-full sm:col-span-3">
                  <Label>User</Label>
                  <Input className="mt-2" value={user} onChange={e => setUser(e.target.value)} placeholder="admin" disabled={Boolean(editingUser)} />
                </div>

                <div className="col-span-full sm:col-span-3">
                  <Label>{editingUser ? "New password (optional)" : "Password"}</Label>
                  <Input type="password" className="mt-2" value={password} onChange={e => setPassword(e.target.value)} placeholder="******" />
                </div>

                <div className="col-span-full">
                  <Label>Display name</Label>
                  <Input className="mt-2" value={displayName} onChange={e => setDisplayName(e.target.value)} placeholder="Administrator" />
                </div>

                <div className="col-span-full sm:col-span-3">
                  <Label>Active</Label>
                  <div className="mt-2">
                    <Switch checked={enabled} onCheckedChange={setEnabled} />
                  </div>
                </div>

                <div className="col-span-full mt-6 flex justify-end gap-2">
                  {editingUser && (
                    <Button type="button" variant="secondary" onClick={() => {
                      setEditingUser(null)
                      setUser("")
                      setDisplayName("")
                      setPassword("")
                      setEnabled(true)
                    }}>
                      Cancel
                    </Button>
                  )}
                  <Button type="submit" disabled={submitting}>
                    {submitting ? "Saving..." : editingUser ? "Update user" : "Create user"}
                  </Button>
                </div>

              </div>
            </div>
          </div>
        </form>
      </section>

      <Divider />

      <section>
        <h1 className="text-lg font-semibold text-gray-900 sm:text-xl dark:text-gray-50">Users available</h1>
        <div className="mt-4 sm:mt-6 lg:mt-10">
          <DataTable data={users} columns={userColumns} onRowClick={loadForEdit} />
        </div>
      </section>

      <Divider />

      <Card className="p-4 text-sm text-gray-500">Click a user to edit it.</Card>

    </div>
  )

}
