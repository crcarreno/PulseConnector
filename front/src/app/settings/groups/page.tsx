"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/Button"
import { Card } from "@/components/Card"
import { Divider } from "@/components/Divider"
import { Input } from "@/components/Input"
import { Label } from "@/components/Label"
import { Switch } from "@/components/Switch"
import { useAppToast } from "@/components/Toast"

// -------------------- HOOK --------------------
export function useDataGroups() {
  const [groups, setGroups] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await fetch("https://localhost:5000/api/admin/groups")
      const d = await res.json()
      setGroups(d.data ?? [])
    } catch (err) {
      console.error("Fetch error:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return { groups, loading, refetch: fetchData }
}

// -------------------- COMPONENT --------------------
export default function Groups() {
  const { groups, loading, refetch } = useDataGroups()
  const { showToast } = useAppToast()

  // form state (same lifecycle pattern)
  const [group, setGroup] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [enabled, setEnabled] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!group) return

    setSubmitting(true)

    const payload = {
      group,
      display_name: displayName,
      is_active: enabled,
    }

    try {
      const res = await fetch("https://localhost:5000/api/admin/groups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!res.ok) throw new Error(await res.text())

      showToast({
        title: "Group created",
        description: "Saved successfully",
      })

      // reset form
      setGroup("")
      setDisplayName("")
      setEnabled(true)

      refetch()

    } catch (err) {
      console.error("Create group error", err)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <p>Loading...</p>

  return (
    <div className="space-y-10">

      {/* ---------------- CREATE GROUP ---------------- */}
      <section>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-x-14 gap-y-8 md:grid-cols-3">
            <div>
              <h2 className="font-semibold">Create group</h2>
              <p className="mt-1 text-sm text-gray-500">
                Manage and organize user groups.
              </p>
            </div>

            <div className="md:col-span-2">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-6">

                <div className="col-span-full sm:col-span-3">
                  <Label>Group</Label>
                  <Input
                    className="mt-2"
                    value={group}
                    onChange={e => setGroup(e.target.value)}
                    placeholder="public"
                  />
                </div>

                <div className="col-span-full sm:col-span-3">
                  <Label>Display name</Label>
                  <Input
                    className="mt-2"
                    value={displayName}
                    onChange={e => setDisplayName(e.target.value)}
                    placeholder="Public Group"
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
                    {submitting ? "Creating..." : "Create group"}
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
        <ul className="divide-y">
          {groups.map(g => (
            <li key={g.id} className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm font-medium">{g.group}</p>
                <p className="text-xs text-gray-500">{g.display_name}</p>
              </div>

              <div className="flex items-center gap-2">
                <Switch checked={g.is_active} disabled />
                <span className="text-sm text-gray-500">
                  {g.is_active ? "On" : "Off"}
                </span>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <Divider />

      {/* ---------------- PLACEHOLDERS ---------------- */}
      <Card className="p-4 text-sm text-gray-500">
        Group members, permissions & delete actions go here next.
      </Card>

    </div>
  )
}