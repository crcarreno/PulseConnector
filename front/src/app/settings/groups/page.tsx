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

type Group = {
  group_name: string
  display_name: string
  active: number
}

export function useDataGroups() {
  const [groups, setGroups] = useState<Group[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch("https://localhost:5000/api/admin/groups")
      const d = await res.json()
      setGroups(d.data ?? [])
    } catch (err) {
      console.error("Fetch error:", err)
      setGroups([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { groups, loading, refetch: fetchData }
}

const groupColumns: ColumnDef<Group>[] = [
  {
    accessorKey: "group_name",
    header: "Group",
    cell: ({ row }) => <p className="text-sm font-medium">{row.original.group_name}</p>,
  },
  {
    accessorKey: "display_name",
    header: "Display name",
    cell: ({ row }) => <p className="text-xs text-gray-500">{row.original.display_name}</p>,
  },
  {
    accessorKey: "active",
    header: "Active",
    cell: ({ row }) => <Switch checked={row.original.active === 1} disabled />,
  },
]

export default function Groups() {
  const { groups, loading, refetch } = useDataGroups()
  const { showToast } = useAppToast()
  const [editingGroup, setEditingGroup] = useState<string | null>(null)
  const [group, setGroup] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [enabled, setEnabled] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  function loadForEdit(item: Group) {
    setEditingGroup(item.group_name)
    setGroup(item.group_name)
    setDisplayName(item.display_name ?? "")
    setEnabled(item.active === 1)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!group) return

    setSubmitting(true)

    try {
      if (editingGroup) {
        const updateRes = await fetch("https://localhost:5000/api/admin/groups/update", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            group: editingGroup,
            display_name: displayName,
          }),
        })

        if (!updateRes.ok) throw new Error(await updateRes.text())

        const activeRes = await fetch("https://localhost:5000/api/admin/groups/disable", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ group: editingGroup, action: enabled ? 1 : 0 }),
        })

        if (!activeRes.ok) throw new Error(await activeRes.text())
      } else {
        const res = await fetch("https://localhost:5000/api/admin/groups", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            group,
            display_name: displayName,
          }),
        })

        if (!res.ok) throw new Error(await res.text())
      }

      showToast({
        title: editingGroup ? "Group updated" : "Group created",
        description: "Saved successfully",
      })

      setEditingGroup(null)
      setGroup("")
      setDisplayName("")
      setEnabled(true)

      refetch()

    } catch (err) {
        console.error("Save group error", err)
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
              <h2 className="font-semibold">{editingGroup ? "Edit group" : "Create group"}</h2>
              <p className="mt-1 text-sm text-gray-500">Manage and organize user groups.</p>
            </div>

            <div className="md:col-span-2">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-6">

                <div className="col-span-full sm:col-span-3">
                  <Label>Group</Label>
                  <Input className="mt-2" value={group} onChange={e => setGroup(e.target.value)} placeholder="public" disabled={Boolean(editingGroup)} />
                </div>

                <div className="col-span-full sm:col-span-3">
                  <Label>Display name</Label>
                  <Input className="mt-2" value={displayName} onChange={e => setDisplayName(e.target.value)} placeholder="Public Group" />
                </div>

                <div className="col-span-full sm:col-span-3">
                  <Label>Active</Label>
                  <div className="mt-2">
                    <Switch checked={enabled} onCheckedChange={setEnabled} />
                  </div>
                </div>

                <div className="col-span-full mt-6 flex justify-end gap-2">
                  {editingGroup && (
                    <Button type="button" variant="secondary" onClick={() => {
                      setEditingGroup(null)
                      setGroup("")
                      setDisplayName("")
                      setEnabled(true)
                    }}>
                      Cancel
                    </Button>
                  )}
                  <Button type="submit" disabled={submitting}>
                    {submitting ? "Saving..." : editingGroup ? "Update group" : "Create group"}
                  </Button>
                </div>

              </div>
            </div>
          </div>
        </form>
      </section>

      <Divider />

      {/* ---------------- GROUP LIST ---------------- */}
      <section>
        <h1 className="text-lg font-semibold text-gray-900 sm:text-xl dark:text-gray-50">Groups available</h1>
        <div className="mt-4 sm:mt-6 lg:mt-10">
          <DataTable data={groups} columns={groupColumns} onRowClick={loadForEdit} />
        </div>
      </section>

      <Divider />

      <Card className="p-4 text-sm text-gray-500">Click a group to edit it.</Card>

    </div>
  )
}