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

export function useDataGroups() {

  const [groups, setDataGroups] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  // GET lista
  const fetchData = async () => {

    setLoading(true)

    try {
      const res = await fetch("https://localhost:5000/admin/groups")
      const data = await res.json()
      setDataGroups(data ?? [])
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
    groups,
    loading,
    refetch: fetchData
  }
}

export default function Users() {

    const { groups, loading, refetch } = useDataGroups()
    const [enabled, setEnabled] = useState(groups.is_active)

    if (loading) return <p>Loading...</p>

  return (
    <>
      <div className="space-y-10">
        <section aria-labelledby="personal-information">
          <form>
            <div className="grid grid-cols-1 gap-x-14 gap-y-8 md:grid-cols-3">
              <div>
                <h2
                  id="personal-information"
                  className="scroll-mt-10 font-semibold text-gray-900 dark:text-gray-50"
                >
                  Create group
                </h2>
                <p className="mt-1 text-sm leading-6 text-gray-500">
                  Manage and create groups.
                </p>
              </div>
              <div className="md:col-span-2">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-6">
                  <div className="col-span-full sm:col-span-3">
                    <Label htmlFor="group_name" className="font-medium">
                      Group name
                    </Label>
                    <Input
                      type="text"
                      id="group_name"
                      name="group_name"
                      autoComplete="given-name"
                      placeholder="admin"
                      className="mt-2"
                    />
                  </div>
                  <div className="col-span-full sm:col-span-3">
                    <Label htmlFor="display_name" className="font-medium">
                      Description
                    </Label>
                    <Input
                      type="text"
                      id="display_name"
                      name="display_name"
                      autoComplete="family-name"
                      placeholder="Public"
                      className="mt-2"
                    />
                  </div>
                  <div className="col-span-full sm:col-span-3">
                    <Label htmlFor="email" className="font-medium">
                      Email
                    </Label>
                    <Input
                      type="email"
                      id="email"
                      name="email"
                      autoComplete="family-name"
                      placeholder="admin@mail.com"
                      className="mt-2"
                    />
                  </div>
                  <div className="col-span-full sm:col-span-3">
                    <Label htmlFor="email" className="font-medium">
                      Role
                    </Label>
                    <Switch
                    checked={enabled}
                    onCheckedChange={setEnabled}
                    />
                  </div>
                  <div className="col-span-full mt-6 flex justify-end">
                    <Button type="submit">Save settings</Button>
                  </div>
                </div>
              </div>
            </div>
          </form>
        </section>

        <Divider />

        <section aria-labelledby="existing-users">
        <ul
          role="list"
          className="mt-6 divide-y divide-gray-200 dark:divide-gray-800"
        >

          {groups.map((group) => (
            <li
              key={group.id}
              className="flex items-center justify-between gap-x-6 py-2.5"
            >
              <div className="flex items-center gap-x-4 truncate">
                <span
                  className="hidden size-16 shrink-0 items-center justify-center rounded-full border border-gray-300 bg-white text-xs text-gray-700 sm:flex dark:border-gray-800 dark:bg-gray-950 dark:text-gray-300"
                  aria-hidden="true"
                >
                    <span className="text-xs text-gray-500">?</span>

                </span>
                <div className="truncate">
                  <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-50">
                    {group.name}
                  </p>
                  <p className="truncate text-xs text-gray-500">{group.group_name}</p>
                  <p className="truncate text-xs text-gray-500">{group.display_name}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">

                <div className="flex items-center gap-2">
                  <Switch
                    checked={enabled}
                    onCheckedChange={setEnabled}
                    disabled={group.is_active === "true"}
                  />
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {enabled ? "On" : "Off"}
                  </span>
                </div>

                {/*<DropdownMenu>
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
                          if (confirm("Are you sure you want to delete this user?")) {
                            deleteDataSource(group.id)
                          }
                        }}
                    >
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>*/}
              </div>
            </li>
          ))}
        </ul>
      </section>

        <Divider />

        <section aria-labelledby="notification-settings">
          <form>
            <div className="grid grid-cols-1 gap-x-14 gap-y-8 md:grid-cols-3">
              <div>
                <h2
                  id="notification-settings"
                  className="scroll-mt-10 font-semibold text-gray-900 dark:text-gray-50"
                >
                  Database connections
                </h2>
                <p className="mt-1 text-sm leading-6 text-gray-500">
                  Configure the types of notifications you want to receive.
                </p>
              </div>
              <div className="md:col-span-2">
                <fieldset>
                  <legend className="text-sm font-medium text-gray-900 dark:text-gray-50">
                    Team
                  </legend>
                  <p className="mt-1 text-sm leading-6 text-gray-500">
                    Configure the types of team alerts you want to receive.
                  </p>
                  <ul
                    role="list"
                    className="mt-4 divide-y divide-gray-200 dark:divide-gray-800"
                  >
                    <li className="flex items-center gap-x-3 py-3">
                      <Checkbox
                        id="team-requests"
                        name="team-requests"
                        defaultChecked
                      />
                      <Label htmlFor="team-requests">Team join requests</Label>
                    </li>
                    <li className="flex items-center gap-x-3 py-3">
                      <Checkbox id="team-activity-digest" />
                      <Label htmlFor="team-activity-digest">
                        Weekly team activity digest
                      </Label>
                    </li>
                  </ul>
                </fieldset>
                <fieldset className="mt-6">
                  <legend className="text-sm font-medium text-gray-900 dark:text-gray-50">
                    Usage
                  </legend>
                  <p className="mt-1 text-sm leading-6 text-gray-500">
                    Configure the types of usage alerts you want to receive.
                  </p>
                  <ul
                    role="list"
                    className="mt-4 divide-y divide-gray-200 dark:divide-gray-800"
                  >
                    <li className="flex items-center gap-x-3 py-3">
                      <Checkbox id="api-requests" name="api-requests" />
                      <Label htmlFor="api-requests">API incidents</Label>
                    </li>
                    <li className="flex items-center gap-x-3 py-3">
                      <Checkbox
                        id="workspace-execution"
                        name="workspace-execution"
                      />
                      <Label htmlFor="workspace-execution">
                        Platform incidents
                      </Label>
                    </li>
                    <li className="flex items-center gap-x-3 py-3">
                      <Checkbox
                        id="query-caching"
                        name="query-caching"
                        defaultChecked
                      />
                      <Label htmlFor="query-caching">
                        Payment transactions
                      </Label>
                    </li>
                    <li className="flex items-center gap-x-3 py-3">
                      <Checkbox id="storage" name="storage" defaultChecked />
                      <Label htmlFor="storage">User behavior</Label>
                    </li>
                  </ul>
                </fieldset>
                <div className="col-span-full mt-6 flex justify-end">
                  <Button type="submit">Save settings</Button>
                </div>
              </div>
            </div>
          </form>
        </section>
        <Divider />
        <section aria-labelledby="danger-zone">
          <form>
            <div className="grid grid-cols-1 gap-x-14 gap-y-8 md:grid-cols-3">
              <div>
                <h2
                  id="danger-zone"
                  className="scroll-mt-10 font-semibold text-gray-900 dark:text-gray-50"
                >
                  Danger zone
                </h2>
                <p className="mt-1 text-sm leading-6 text-gray-500">
                  Manage general workspace. Contact system admin for more
                  information.{" "}
                  <a
                    href="#"
                    className="inline-flex items-center gap-1 text-indigo-600 hover:underline hover:underline-offset-4 dark:text-indigo-400"
                  >
                    Learn more
                    <RiExternalLinkLine
                      className="size-4 shrink-0"
                      aria-hidden="true"
                    />
                  </a>
                </p>
              </div>
              <div className="space-y-6 md:col-span-2">
                <Card className="p-4">
                  <div className="flex items-start justify-between gap-10">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-gray-50">
                        Leave workspace
                      </h4>
                      <p className="mt-2 text-sm leading-6 text-gray-500">
                        Revoke your access to this team. Other people you have
                        added to the workspace will remain.
                      </p>
                    </div>
                    <Button
                      variant="secondary"
                      className="text-red-600 dark:text-red-500"
                    >
                      Leave
                    </Button>
                  </div>
                </Card>
                <Card className="overflow-hidden p-0">
                  <div className="flex items-start justify-between gap-10 p-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-400 dark:text-gray-600">
                        Delete workspace
                      </h4>
                      <p className="mt-2 text-sm leading-6 text-gray-400 dark:text-gray-600">
                        Revoke your access to this team. Other people you have
                        added to the workspace will remain.
                      </p>
                    </div>
                    <Button
                      variant="secondary"
                      disabled
                      className="whitespace-nowrap text-red-600 disabled:text-red-300 disabled:opacity-50 dark:text-red-500 disabled:dark:text-red-700"
                    >
                      Delete workspace
                    </Button>
                  </div>
                  <div className="border-t border-gray-200 bg-gray-50 p-4 dark:border-gray-900 dark:bg-gray-900">
                    <p className="text-sm text-gray-500">
                      You cannot delete the workspace because you are not the
                      system admin.
                    </p>
                  </div>
                </Card>
              </div>
            </div>
          </form>
        </section>
      </div>
    </>
  )
}
