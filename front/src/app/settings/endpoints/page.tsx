"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/Button"
import { Card } from "@/components/Card"
import { Divider } from "@/components/Divider"
import { Input } from "@/components/Input"
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

// -------------------- HOOKS --------------------
export function useDataListObjects(connectionId?: string, objectType?: string) {
  const [listObjects, setListObjects] = useState<string[]>([])

  useEffect(() => {
    if (!connectionId || !objectType) return

    fetch("https://localhost:5000/admin/schema/objects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ connection_id: connectionId, object_type: objectType }),
    })
      .then(r => r.json())
      .then(d => setListObjects(d.items ?? []))
      .catch(() => setListObjects([]))
  }, [connectionId, objectType])

  return { listObjects }
}

export function useDataEndpoints() {
  const [endpoints, setEndpoints] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    const res = await fetch("https://localhost:5000/admin/endpoints")
    const data = await res.json()
    setEndpoints(data ?? [])
    setLoading(false)
  }

  useEffect(() => {
    fetchData()
  }, [])

  return { endpoints, loading, refetch: fetchData }
}

export function useDataSources() {
  const [datasource, setDatasource] = useState<any[]>([])

  useEffect(() => {
    fetch("https://localhost:5000/admin/data-sources")
      .then(r => r.json())
      .then(d => setDatasource(d.items ?? []))
  }, [])

  return { datasource }
}

export function useDataObjects() {
  const [objects, setObjects] = useState<any[]>([])

  useEffect(() => {
    fetch("https://localhost:5000/admin/objects")
      .then(r => r.json())
      .then(d => setObjects(d ?? []))
  }, [])

  return { objects }
}

// -------------------- COMPONENT --------------------
export default function Endpoints() {
  const { endpoints, loading, refetch } = useDataEndpoints()
  const { datasource } = useDataSources()
  const { objects } = useDataObjects()
  const { showToast } = useAppToast()

  const [editingId, setEditingId] = useState<string | null>(null)

  const [name, setName] = useState("")
  const [namespace, setNamespace] = useState("")
  const [connectionId, setConnectionId] = useState<string>()
  const [objectType, setObjectType] = useState<string>()
  const [source, setSource] = useState("")
  const [primaryKey, setPrimaryKey] = useState("")
  const [enabled, setEnabled] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  const { listObjects } = useDataListObjects(connectionId, objectType)

  function loadForEdit(ep: any) {
    setEditingId(ep.id)
    setName(ep.name)
    setNamespace(ep.namespace)
    setConnectionId(ep.id_connection)
    setObjectType(ep.type)
    setSource(ep.source)
    setPrimaryKey(ep.primary_key)
    setEnabled(ep.is_active)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name || !connectionId || !objectType || !source) return

    setSubmitting(true)

    const payload = {
      name,
      id_connection: connectionId,
      type: objectType,
      source,
      namespace,
      primary_key: primaryKey,
      is_active: enabled,
    }

    const url = editingId
      ? `https://localhost:5000/admin/endpoints/${editingId}`
      : "https://localhost:5000/admin/endpoints"

    const method = editingId ? "PUT" : "POST"

    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })

    if (!res.ok) throw new Error(await res.text())

    showToast({
      title: editingId ? "Endpoint updated" : "Endpoint created",
      description: "Saved successfully",
    })

    setEditingId(null)
    setName("")
    setNamespace("")
    setSource("")
    setPrimaryKey("")
    setEnabled(true)

    refetch()
    setSubmitting(false)
  }

  if (loading) return <p>Loading...</p>

  return (
    <div className="space-y-10">

      {/* CREATE / EDIT */}
      <section>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-6">

            <div className="col-span-3">
              <Label>Name</Label>
              <Input value={name} onChange={e => setName(e.target.value)} className="mt-2" />
            </div>

            <div className="col-span-3">
              <Label>Namespace</Label>
              <Input value={namespace} onChange={e => setNamespace(e.target.value)} className="mt-2" />
            </div>

            <div className="col-span-3">
              <Label>Connection</Label>
              <Select value={connectionId} onValueChange={setConnectionId}>
                <SelectTrigger className="mt-2"><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent>
                  {datasource.map(ds => (
                    <SelectItem key={ds.id} value={ds.id}>{ds.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="col-span-3">
              <Label>Object type</Label>
              <Select value={objectType} onValueChange={setObjectType}>
                <SelectTrigger className="mt-2"><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent>
                  {objects.map(o => (
                    <SelectItem key={o.object} value={o.object}>{o.display_name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="col-span-3">
              <Label>Object name</Label>
              <Select value={source} onValueChange={setSource}>
                <SelectTrigger className="mt-2"><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent>
                  {listObjects.map(item => (
                    <SelectItem key={item} value={item}>{item}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="col-span-3">
              <Label>Primary key</Label>
              <Input value={primaryKey} onChange={e => setPrimaryKey(e.target.value)} className="mt-2" />
            </div>

            <div className="col-span-3">
              <Label>Active</Label>
              <Switch checked={enabled} onCheckedChange={setEnabled} />
            </div>

            <div className="col-span-full mt-6 flex justify-end">
              <Button type="submit" disabled={submitting}>
                {editingId ? "Update endpoint" : "Create endpoint"}
              </Button>
            </div>

          </div>
        </form>
      </section>

      <Divider />

      {/* LIST */}
      <section>
        <ul className="divide-y">
          {endpoints.map(ep => (
            <li
              key={ep.id}
              onClick={() => loadForEdit(ep)}
              className="flex cursor-pointer items-center justify-between py-3 hover:bg-gray-50"
            >
              <div>
                <p className="text-sm font-medium">{ep.name}</p>
                <p className="text-xs text-gray-500">{ep.namespace}</p>
              </div>
              <Switch checked={ep.is_active} disabled />
            </li>
          ))}
        </ul>
      </section>

      <Divider />

      <Card className="p-4 text-sm text-gray-500">
        Click an endpoint to edit it.
      </Card>

    </div>
  )
}