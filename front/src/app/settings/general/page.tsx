"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/Button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/Dropdown"
import { RiAddLine, RiMore2Fill } from "@remixicon/react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/Select"
import { Switch } from "@/components/Switch"

import { Tooltip } from "@/components/Tooltip"
import { ModalAddConnection } from "@/components/ui/settings/ModalAddConnection"
import { invitedUsers, roles, users } from "@/data/data"

export async function deleteDS(id: string) {
  const res = await fetch(
    `https://localhost:5000/admin/data-sources/${id}`,
    { method: "DELETE" }
  )

  if (!res.ok) {
    throw new Error("Delete failed")
  }
}

export function useDataSources() {
  const [datasource, setDataSources] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  // GET lista
  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await fetch("https://localhost:5000/admin/data-sources")
      const data = await res.json()
      setDataSources(data.items ?? [])
    } catch (err) {
      console.error("Fetch error:", err)
    } finally {
      setLoading(false)
    }
  }

  // DELETE + actualización de UI
  const deleteDataSource = async (id: string) => {
    // 1️⃣ Llamada al backend
    await deleteDS(id)

    // 2️⃣ Actualización del estado (UI)
    setDataSources(prev => prev.filter(ds => ds.id !== id))
  }

  useEffect(() => {
    fetchData()
  }, [])

  return {
    datasource,
    loading,
    refetch: fetchData,
    deleteDataSource,
  }
}

export default function Connections() {

    const { datasource, loading, deleteDataSource, refetch } = useDataSources()
    const [enabled, setEnabled] = useState(datasource.is_active)

  if (loading) return <p>Loading...</p>

    const DIALECT_ICONS: Record<string, string> = {
      postgres: "/assets/icons/postgresql-svgrepo-com.svg",
      mysql: "/assets/icons/mysql-logo-svgrepo-com.svg",
      mariadb: "/assets/icons/mariadb-svgrepo-com.svg",
      mssql: "/assets/icons/microsoft-sql-server-logo-svgrepo-com.svg",
      oracle: "/assets/icons/oracle-svgrepo-com.svg",
      sqlite: "/assets/icons/sqlite-svgrepo-com.svg",
    }

  return (
    <>
      <section aria-labelledby="existing-users">
        <div className="sm:flex sm:items-center sm:justify-between">
          <div>
            <h3
              id="existing-users"
              className="scroll-mt-10 font-semibold text-gray-900 dark:text-gray-50"
            >
              Database connections
            </h3>
            <p className="text-sm leading-6 text-gray-500">
              Add database connection
            </p>
          </div>
          <ModalAddConnection onSuccess={refetch}>
            <Button className="mt-4 w-full gap-2 sm:mt-0 sm:w-fit">
              <RiAddLine className="-ml-1 size-4 shrink-0" aria-hidden="true" />
              Add connection
            </Button>
          </ModalAddConnection>
        </div>
        <ul
          role="list"
          className="mt-6 divide-y divide-gray-200 dark:divide-gray-800"
        >

          {datasource.map((ds) => (
            <li
              key={ds.id}
              className="flex items-center justify-between gap-x-6 py-2.5"
            >
              <div className="flex items-center gap-x-4 truncate">
                <span
                  className="hidden size-16 shrink-0 items-center justify-center rounded-full border border-gray-300 bg-white text-xs text-gray-700 sm:flex dark:border-gray-800 dark:bg-gray-950 dark:text-gray-300"
                  aria-hidden="true"
                >
                  {DIALECT_ICONS[ds.dialect_key] ? (

                    <img
                      src={DIALECT_ICONS[ds.dialect_key]}
                      alt={ds.dialect_key}
                      className="size-10"
                    />
                  ) : (
                    <span className="text-xs text-gray-500">?</span>
                  )}
                </span>
                <div className="truncate">
                  <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-50">
                    {ds.name}
                  </p>
                  <p className="truncate text-xs text-gray-500">{ds.host}:{ds.port}</p>
                  <p className="truncate text-xs text-gray-500">{ds.dialect_name}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">

                <div className="flex items-center gap-2">
                  <Switch
                    checked={enabled}
                    onCheckedChange={setEnabled}
                    disabled={ds.is_active === "true"}
                  />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {enabled ? "On" : "Off"}
                  </span>
                </div>



                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      className="group size-8 hover:border hover:border-gray-300 hover:bg-gray-50 data-[state=open]:border-gray-300 data-[state=open]:bg-gray-50 hover:dark:border-gray-700 hover:dark:bg-gray-900 data-[state=open]:dark:border-gray-700 data-[state=open]:dark:bg-gray-900"
                    >
                      <RiMore2Fill
                        className="size-4 shrink-0 text-gray-500 group-hover:text-gray-700 group-hover:dark:text-gray-400"
                        aria-hidden="true"
                      />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-36">
                    <DropdownMenuItem disabled={ds.id === "admin"}>
                      View details
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="text-red-600 dark:text-red-500"
                      onClick={() => {
                          if (confirm("Are you sure you want to delete this data source?")) {
                            deleteDataSource(ds.id)
                          }
                        }}
                    >
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </li>
          ))}
        </ul>
      </section>


      <section className="mt-12" aria-labelledby="pending-invitations">
        <h2
          id="pending-invitations"
          className="scroll-mt-10 font-semibold text-gray-900 dark:text-gray-50"
        >
          Pending invitations
        </h2>
        <ul
          role="list"
          className="mt-6 divide-y divide-gray-200 dark:divide-gray-800"
        >
          {invitedUsers.map((user) => (
            <li
              key={user.initials}
              className="flex items-center justify-between gap-x-6 py-2.5"
            >
              <div className="flex items-center gap-x-4">
                <span
                  className="hidden size-9 shrink-0 items-center justify-center rounded-full border border-dashed border-gray-300 bg-white text-xs text-gray-700 sm:flex dark:border-gray-800 dark:bg-gray-950 dark:text-gray-300"
                  aria-hidden="true"
                >
                  {user.initials}
                </span>
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                    {user.email}
                  </p>
                  <p className="text-xs text-gray-500">
                    Expires in {user.expires} days
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Select defaultValue={user.role}>
                  <SelectTrigger className="h-8 w-32">
                    <SelectValue placeholder="Select" />
                  </SelectTrigger>
                  <SelectContent align="end">
                    {roles.map((role) => (
                      <SelectItem
                        key={role.value}
                        value={role.value}
                        disabled={role.value === "admin"}
                      >
                        {role.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      className="group size-8 hover:border hover:border-gray-300 hover:bg-gray-50 data-[state=open]:border-gray-300 data-[state=open]:bg-gray-50 hover:dark:border-gray-700 hover:dark:bg-gray-900 data-[state=open]:dark:border-gray-700 data-[state=open]:dark:bg-gray-900"
                    >
                      <RiMore2Fill
                        className="size-4 shrink-0 text-gray-500 group-hover:text-gray-700 group-hover:dark:text-gray-400"
                        aria-hidden="true"
                      />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-36">
                    <DropdownMenuItem
                      className="text-red-600 dark:text-red-500"
                      disabled={user.role === "admin"}
                    >
                      Revoke invitation
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </>
  )
}
