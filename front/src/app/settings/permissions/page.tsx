"use client"

import { useEffect, useState, useCallback } from "react"
import { Button } from "@/components/Button"
import { Card } from "@/components/Card"
import { Divider } from "@/components/Divider"
import { Checkbox } from "@/components/Checkbox"
import { Label } from "@/components/Label"
import { Switch } from "@/components/Switch"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/Select"
import { useAppToast } from "@/components/Toast"
import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "@/components/ui/data-table/DataTable"

type Permission = {
  uid: number
  active: boolean
  endpoints: {
    name: string
    actions: string[]
  }[]
  subjects: {
    id: string
    type: string
  }[]
}

// -------------------- DATA HOOKS --------------------
export function useDataPermissions() {

  const [permissions, setPermissions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {

    setLoading(true)

    try {

      const res = await fetch("https://localhost:5000/api/admin/permissions")
      const json = await res.json()

      setPermissions(json.data ?? [])

    } catch (err) {
      console.error("Error fetching permissions", err)
      setPermissions([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return {
    permissions,
    loading,
    refetch: fetchData,
  }
}

export const permissionsColumns: ColumnDef<Permission>[] = [
{
  header: "Type permission",
  cell: ({ row }) => (
    <div className="space-y-1">
      {row.original.subjects.map((ep) => (
        <div key={ep.type} className="text-sm font-medium">
          {ep.type}
        </div>
      ))}
    </div>
  ),
},
{
  header: "Name",
  cell: ({ row }) => (
    <div className="space-y-1">
      {row.original.subjects.map((ep) => (
        <div key={ep.id} className="text-sm font-medium">
          {ep.id}
        </div>
      ))}
    </div>
  ),
},
{
  header: "Endpoints",
  cell: ({ row }) => (
    <div className="space-y-1">
      {row.original.endpoints.map((ep) => (
        <div key={ep.name} className="text-sm font-medium">
          {ep.name}
        </div>
      ))}
    </div>
  ),
},
{
  header: "Actions",
  cell: ({ row }) => (
    <div className="flex gap-1 flex-wrap">
      {row.original.endpoints.flatMap(ep =>
        ep.actions.map(action => (
          <span
            key={`${ep.name}-${action}`}
            className="px-2 py-0.5 text-xs rounded bg-gray-200"
          >
            {action}
          </span>
        ))
      )}
    </div>
  ),
},
{
  header: "Active",
  cell: ({ row }) => (
    <Switch checked={row.original.active} disabled />
  ),
}
]

export function useDataUsers(enabled: boolean) {
  const [users, setUsers] = useState<any[]>([])

  useEffect(() => {
    if (!enabled) return

    fetch("https://localhost:5000/api/admin/users")
      .then(r => r.json())
      .then(d => setUsers(d.data ?? []))
  }, [enabled])

  return { users }
}


export function useDataGroups(enabled: boolean) {
  const [groups, setGroups] = useState<any[]>([])

  useEffect(() => {
    if (!enabled) return

    fetch("https://localhost:5000/api/admin/groups")
      .then(r => r.json())
      .then(d => setGroups(d.data ?? []))
  }, [enabled])

  return { groups }
}


export function useDataEndpoints() {
  const [endpoints, setEndpoints] = useState<any[]>([])
  useEffect(() => {
    fetch("https://localhost:5000/api/admin/endpoints")
      .then(r => r.json())
      .then(d => setEndpoints(d.data ?? []))
  }, [])
  return { endpoints }
}

// -------------------- COMPONENT --------------------
export default function Permissions() {

  const [subjectType, setSubjectType] = useState<"user" | "group" | "">("")
  const [subjectId, setSubjectId] = useState("")
  const { permissions, loading, refetch } = useDataPermissions()
  const { users } = useDataUsers(subjectType === "user")
  const { groups } = useDataGroups(subjectType === "group")
  const { endpoints } = useDataEndpoints()
  const { showToast } = useAppToast()
  const [editingId, setEditingId] = useState<number | null>(null)
  const [endpointName, setEndpointName] = useState("")
  const [actions, setActions] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    setSubjectId("")
  }, [subjectType])

  function toggleAction(action: string) {
    setActions(prev =>
      prev.includes(action)
        ? prev.filter(a => a !== action)
        : [...prev, action]
    )
  }

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
      ? "https://localhost:5000/api/admin/permissions/update"
      : "https://localhost:5000/api/admin/permissions"

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editingId ? { uid: editingId, ...payload } : payload)
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
          <h1 className="text-lg font-semibold text-gray-900 sm:text-xl dark:text-gray-50">
            Permissions available
          </h1>
          <div className="mt-4 sm:mt-6 lg:mt-10">
          <DataTable
              data={permissions}
              columns={permissionsColumns}
              onRowClick={loadForEdit}
            />
          </div>
      </section>

      <Divider />

      <Card className="p-4 text-sm text-gray-500">
        Click a permission to edit it.
      </Card>

    </div>
  )
}