"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/Button"
import { Card } from "@/components/Card"
import { Divider } from "@/components/Divider"
import { Checkbox } from "@/components/Checkbox"
import { Label } from "@/components/Label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/Select"
import { useAppToast } from "@/components/Toast"

// -------------------- DATA HOOKS --------------------
export function useDataPermissions() {
  const [permissions, setPermissions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    const res = await fetch("https://localhost:5000/admin/permissions")
    const data = await res.json()
    setPermissions(data ?? [])
    setLoading(false)
  }

  useEffect(() => {
    fetchData()
  }, [])

  return { permissions, loading, refetch: fetchData }
}

export function useDataUsers(enabled: boolean) {
  const [users, setUsers] = useState<any[]>([])

  useEffect(() => {
    if (!enabled) return

    fetch("https://localhost:5000/admin/users")
      .then(r => r.json())
      .then(d => setUsers(d ?? []))
  }, [enabled])

  return { users }
}


export function useDataGroups(enabled: boolean) {
  const [groups, setGroups] = useState<any[]>([])

  useEffect(() => {
    if (!enabled) return

    fetch("https://localhost:5000/admin/groups")
      .then(r => r.json())
      .then(d => setGroups(d ?? []))
  }, [enabled])

  return { groups }
}


export function useDataEndpoints() {
  const [endpoints, setEndpoints] = useState<any[]>([])
  useEffect(() => {
    fetch("https://localhost:5000/admin/endpoints")
      .then(r => r.json())
      .then(d => setEndpoints(d ?? []))
  }, [])
  return { endpoints }
}

// -------------------- COMPONENT --------------------
export default function Permissions() {

  // ─────────────────────────────
  // Subjects (modelo nuevo)
  // ─────────────────────────────
  const [subjectType, setSubjectType] = useState<"user" | "group" | "">("")
  const [subjectId, setSubjectId] = useState("")

  // ─────────────────────────────
  // Data
  // ─────────────────────────────
  const { permissions, loading, refetch } = useDataPermissions()
  const { users } = useDataUsers(subjectType === "user")
  const { groups } = useDataGroups(subjectType === "group")
  const { endpoints } = useDataEndpoints()
  const { showToast } = useAppToast()

  // ─────────────────────────────
  // Form state
  // ─────────────────────────────
  const [editingId, setEditingId] = useState<string | null>(null)
  const [endpointName, setEndpointName] = useState("")
  const [actions, setActions] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)

  // ─────────────────────────────
  // Reset subjectId when type changes
  // ─────────────────────────────
  useEffect(() => {
    setSubjectId("")
  }, [subjectType])

  // ─────────────────────────────
  // Actions
  // ─────────────────────────────
  function toggleAction(action: string) {
    setActions(prev =>
      prev.includes(action)
        ? prev.filter(a => a !== action)
        : [...prev, action]
    )
  }

  // ─────────────────────────────
  // Load permission for edit
  // ─────────────────────────────
  function loadForEdit(p: any) {
    setEditingId(p.uid)

    const firstSubject = p.subjects?.[0]
    const firstEndpoint = p.endpoints?.[0]

    if (firstSubject) {
      setSubjectType(firstSubject.type)
      setSubjectId(firstSubject.id)
    }

    if (firstEndpoint) {
      setEndpointName(firstEndpoint.name)
      setActions(firstEndpoint.actions ?? [])
    }
  }

  // ─────────────────────────────
  // Submit
  // ─────────────────────────────
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!subjectType || !subjectId || !endpointName || actions.length === 0) {
      return
    }

    setSubmitting(true)

    const payload = {
      subjects: [
        {
          type: subjectType,
          id: subjectId
        }
      ],
      endpoints: [
        {
          name: endpointName,
          actions
        }
      ]
    }

    const url = editingId
      ? `https://localhost:5000/admin/permissions/${editingId}`
      : "https://localhost:5000/admin/permissions"

    const method = editingId ? "PUT" : "POST"

    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        throw new Error(await res.text())
      }

      showToast({
        title: editingId ? "Permission updated" : "Permission created",
        description: "Saved successfully"
      })

      setEditingId(null)
      setSubjectType("")
      setSubjectId("")
      setEndpointName("")
      setActions([])

      refetch()

    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <p>Loading...</p>

  return (
    <div className="space-y-10">

      {/* CREATE / EDIT */}
      <section>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-6">

            <div className="col-span-3">
              <Label>Apply permission by</Label>

              <Select value={subjectType} onValueChange={v => setSubjectType(v as any)}>
                <SelectTrigger className="mt-2"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="group">Group</SelectItem>
                </SelectContent>
              </Select>

            </div>

            <div className="col-span-3">
              <Label>Target</Label>

              <Select
                  value={subjectId}
                  onValueChange={setSubjectId}
                  disabled={!subjectType}
                >
                  <SelectTrigger className="mt-2">
                    <SelectValue placeholder="Select" />
                  </SelectTrigger>

                  <SelectContent>
                    {subjectType === "user" &&
                      users.map((u: any) => (
                        <SelectItem
                          key={u.user}
                          value={u.user}
                        >
                          {u.display_name}
                        </SelectItem>
                      ))}

                    {subjectType === "group" &&
                      groups.map((g: any) => (
                        <SelectItem
                          key={g.group_name}
                          value={g.group_name}
                        >
                          {g.display_name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>


            </div>

            <div className="col-span-3">
              <Label>Endpoint</Label>

              <Select value={endpointName} onValueChange={setEndpointName}>
                <SelectTrigger className="mt-2"><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent>
                  {endpoints.map((ep: any) => (
                    <SelectItem key={ep.id} value={ep.name}>{ep.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

            </div>

            <div className="col-span-full">
              <Label>Actions</Label>

              <div className="mt-2 flex gap-6">
                {["read", "write", "delete"].map(a => (
                  <label key={a} className="flex items-center gap-2">
                    <Checkbox
                      checked={actions.includes(a)}
                      onCheckedChange={() => toggleAction(a)}
                    />
                    <span className="text-sm">{a}</span>
                  </label>
                ))}
              </div>

            </div>

            <div className="col-span-full mt-6 flex justify-end">
              <Button type="submit" disabled={submitting}>
                {editingId ? "Update permission" : "Create permission"}
              </Button>
            </div>

          </div>
        </form>
      </section>

      <Divider />

      {/* LIST */}
      <section>
        <ul className="divide-y">
          {permissions.map(p => (
            <li
              key={p.id}
              onClick={() => loadForEdit(p)}
              className="cursor-pointer py-3 hover:bg-gray-50"
            >
              <p className="text-sm font-medium">
                {p.by}: {p.target}
              </p>
              <p className="text-xs text-gray-500">
                {p.endpoints[0]?.name} → {p.endpoints[0]?.actions.join(", ")}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <Divider />

      <Card className="p-4 text-sm text-gray-500">
        Click a permission to edit it.
      </Card>

    </div>
  )
}