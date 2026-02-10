"use client"

import { useEffect, useState, useCallback } from "react"
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

import { ColumnDef } from "@tanstack/react-table"
import { DataTable } from "@/components/ui/data-table/DataTable"


// -------------------- HOOKS --------------------
export function useDataListObjects(connectionId?: string, objectType?: string) {
  const [listObjects, setListObjects] = useState<string[]>([])

  useEffect(() => {
    if (!connectionId || !objectType) return

    fetch("https://localhost:5000/api/admin/schema/objects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ connection_id: connectionId, object_type: objectType }),
    })
      .then(r => r.json())
      .then(d => setListObjects(d.data.items ?? []))
      .catch(() => setListObjects([]))
  }, [connectionId, objectType])

  return { listObjects }
}

export type Endpoint = {
  id: string
  name: string
  namespace: string
  is_active: boolean
}

export function useDataEndpoints() {

  const [endpoints, setEndpoints] = useState<Endpoint[]>([])
  const [loading, setLoading] = useState(false)

  const fetchData = useCallback(async () => {

    setLoading(true)

    try {

      const res = await fetch("https://localhost:5000/api/admin/endpoints")
      const json = await res.json()

      setEndpoints(json.data ?? [])

    } catch (err) {
      console.error("Error fetching endpoints", err)
      setEndpoints([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return {
    endpoints,
    loading,
    refetch: fetchData,
  }
}

export const endpointColumns: ColumnDef<Endpoint>[] = [
  {
    accessorKey: "name",
    header: "Endpoint",
    cell: ({ row }) => (
      <div>
        <p className="text-sm font-medium">
          {row.original.name}
        </p>
      </div>
    ),
  },
    {
    accessorKey: "namespace",
    header: "Namespace",
    cell: ({ row }) => (
      <div>
        <p className="text-xs text-gray-500">
          {row.original.namespace}
        </p>
      </div>
    ),
  },
  {
    accessorKey: "type",
    header: "Type",
    cell: ({ row }) => (
      <div>
        <p className="text-xs text-gray-500">
          {row.original.type}
        </p>
      </div>
    ),
  },
    {
    accessorKey: "source",
    header: "Source",
    cell: ({ row }) => (
      <div>
        <p className="text-xs text-gray-500">
          {row.original.source}
        </p>
      </div>
    ),
  },
  {
    accessorKey: "dialect",
    header: "Dialect",
    cell: ({ row }) => (
      <div>
        <p className="text-xs text-gray-500">
          {row.original.name_dialect}
        </p>
      </div>
    ),
  },
  {
    accessorKey: "datasource",
    header: "Datasource",
    cell: ({ row }) => (
      <div>
        <p className="text-xs text-gray-500">
          {row.original.datasource}
        </p>
      </div>
    ),
  },
  {
    accessorKey: "database_name",
    header: "Database name",
    cell: ({ row }) => (
      <div>
        <p className="text-xs text-gray-500">
          {row.original.database_name}
        </p>
      </div>
    ),
  },
  {
    accessorKey: "is_active",
    header: "Active",
    cell: ({ row }) => (
      <Switch checked={row.original.is_active} disabled />
    ),
  },
]

export function useDataSources() {
  const [datasource, setDatasource] = useState<any[]>([])

  useEffect(() => {
    fetch("https://localhost:5000/api/admin/data-sources")
      .then(r => r.json())
      .then(d => setDatasource(d.data.items ?? []))
  }, [])

  return { datasource }
}

export function useDataObjects() {
  const [objects, setObjects] = useState<any[]>([])

  useEffect(() => {
    fetch("https://localhost:5000/api/admin/objects")
      .then(r => r.json())
      .then(d => setObjects(d.data ?? []))
  }, [])

  return { objects }
}

// -------------------- COMPONENT --------------------
export default function Endpoints() {
  const { endpoints, loading, refetch } = useDataEndpoints()
  const { datasource } = useDataSources()
  const { objects } = useDataObjects()
  const { showToast } = useAppToast()

  const [editingName, setEditingName] = useState<string | null>(null)

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
    setEditingName(ep.name)
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

try {
      const payload = editingName
        ? {
            name: editingName,
            id_connection: connectionId,
            type: objectType,
            source,
            namespace,
            primary_key: primaryKey,
          }
        : {
            name,
            id_connection: connectionId,
            type: objectType,
            source,
            namespace,
            primary_key: primaryKey,
          }

      const url = editingName
        ? "https://localhost:5000/api/admin/endpoints/update"
        : "https://localhost:5000/api/admin/endpoints"

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!res.ok) throw new Error(await res.text())

      showToast({
        title: editingName ? "Endpoint updated" : "Endpoint created",
        description: "Saved successfully",
      })

      setEditingName(null)
      setName("")
      setNamespace("")
      setConnectionId(undefined)
      setObjectType(undefined)
      setSource("")
      setPrimaryKey("")
      setEnabled(true)

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
                {editingName ? "Update endpoint" : "Create endpoint"}
              </Button>
            </div>

          </div>
        </form>
      </section>

      <Divider />

      {/* LIST */}
      <section>
          <h1 className="text-lg font-semibold text-gray-900 sm:text-xl dark:text-gray-50">
            Endpoints available
          </h1>
          <div className="mt-4 sm:mt-6 lg:mt-10">
          <DataTable
              data={endpoints}
              columns={endpointColumns}
              onRowClick={loadForEdit}
            />
          </div>
      </section>

    </div>
  )
}