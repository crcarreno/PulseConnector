
"use client"

import { CategoryBarCard } from "@/components/ui/overview/DashboardCategoryBarCard"
import { ChartCard } from "@/components/ui/overview/DashboardChartCard"
import { Filterbar } from "@/components/ui/overview/DashboardFilterbar"
import { ProgressBarCard } from "@/components/ui/overview/DashboardProgressBarCard"
import { overviews } from "@/data/overview-data"
import { OverviewData } from "@/data/schema"
import { cx } from "@/lib/utils"
import { subDays, toDate } from "date-fns"
import { DateRange } from "react-day-picker"

import React, { useEffect, useState } from "react"
import { Button } from "@/components/Button"
import { useAppToast } from "@/components/Toast"


export type PeriodValue = "previous-period" | "last-year" | "no-comparison"

const categories: {
  title: keyof OverviewData
  type: "currency" | "unit"
}[] = [
  {
    title: "Rows read",
    type: "unit",
  },
  {
    title: "Rows written",
    type: "unit",
  },
  {
    title: "Queries",
    type: "unit",
  },
  {
    title: "Payments completed",
    type: "currency",
  },
  {
    title: "Sign ups",
    type: "unit",
  },
  {
    title: "Logins",
    type: "unit",
  },
  {
    title: "Sign outs",
    type: "unit",
  },
  {
    title: "Support calls",
    type: "unit",
  },
]

export type KpiEntry = {
  title: string
  percentage: number
  current: number
  allowed: number
  unit?: string
}

const data: KpiEntry[] = [
  {
    title: "Rows read",
    percentage: 48.1,
    current: 48.1,
    allowed: 100,
    unit: "M",
  },
  {
    title: "Rows written",
    percentage: 78.3,
    current: 78.3,
    allowed: 100,
    unit: "M",
  },
  {
    title: "Storage",
    percentage: 26,
    current: 5.2,
    allowed: 20,
    unit: "GB",
  },
]

const data2: KpiEntry[] = [
  {
    title: "Weekly active users",
    percentage: 21.7,
    current: 21.7,
    allowed: 100,
    unit: "%",
  },
  {
    title: "Total users",
    percentage: 70,
    current: 28,
    allowed: 40,
  },
  {
    title: "Uptime",
    percentage: 98.3,
    current: 98.3,
    allowed: 100,
    unit: "%",
  },
]

export type KpiEntryExtended = Omit<
  KpiEntry,
  "current" | "allowed" | "unit"
> & {
  value: string
  color: string
}

const data3: KpiEntryExtended[] = [
  {
    title: "Base tier",
    percentage: 68.1,
    value: "$200",
    color: "bg-indigo-600 dark:bg-indigo-500",
  },
  {
    title: "On-demand charges",
    percentage: 20.8,
    value: "$61.1",
    color: "bg-purple-600 dark:bg-purple-500",
  },
  {
    title: "Caching",
    percentage: 11.1,
    value: "$31.9",
    color: "bg-gray-400 dark:bg-gray-600",
  },
]

const overviewsDates = overviews.map((item) => toDate(item.date).getTime())
const maxDate = toDate(Math.max(...overviewsDates))

export default function Overview() {

    const [serverRunning, setServerRunning] = useState<boolean | null>(null)
    const [serverLoading, setServerLoading] = useState(false)

    const { showToast } = useAppToast()

    const StopSvg = (
          <svg viewBox="0 0 24 24" fill="currentColor" className="size-4">
            <path d="M6 6H18V18H6V6Z" />
          </svg>
        )

    const PlaySvg = (
          <svg viewBox="0 0 24 24" fill="currentColor" className="size-4">
            <path d="M7 4V20L20 12L7 4Z" />
          </svg>
        )

  const [selectedDates, setSelectedDates] = React.useState<DateRange | undefined>({
    from: subDays(maxDate, 30),
    to: maxDate,
  })
  const [selectedPeriod, setSelectedPeriod] =
    React.useState<PeriodValue>("last-year")

  const [selectedCategories, setSelectedCategories] = React.useState<string[]>(
    categories.map((category) => category.title),
  )

useEffect(() => {
  fetchServerStatus()
}, [])

async function fetchServerStatus() {
  try {
    const res = await fetch("https://localhost:5000/api/status")
    const json = await res.json()

    setServerRunning(json.data.running)
  } catch (err) {
    console.error("Error fetching server status", err)
  }
}


async function startServer() {
  setServerLoading(true)
  try {
    await fetch("https://localhost:5000/api/server/start", { method: "POST" })
    setServerRunning(true)
    showToast({ title: "Server started" })
  } finally {
    setServerLoading(false)
  }
}

async function stopServer() {
  setServerLoading(true)
  try {
    await fetch("https://localhost:5000/api/server/stop", { method: "POST" })
    setServerRunning(false)
    showToast({ title: "Server stopped" })
  } finally {
    setServerLoading(false)
  }
}



function Spinner() {
  return (
    <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-transparent" />
  )
}

  return (

    <>
      <section aria-labelledby="current-billing-cycle">
        <h1
          id="current-billing-cycle"
          className="scroll-mt-10 text-lg font-semibold text-gray-900 sm:text-xl dark:text-gray-50"
        >
          Main
        </h1>
        <div className="mt-4 grid grid-cols-1 gap-14 sm:mt-8 sm:grid-cols-2 lg:mt-10 xl:grid-cols-3">
          <div className="flex items-center gap-3">

            <Button
              disabled={serverLoading}
              onClick={serverRunning ? stopServer : startServer}
              className={cx(
                "flex items-center gap-2 transition-colors",
                serverRunning
                  ? "!bg-red-600 hover:!bg-red-700 text-white"
                  : "!bg-green-500 hover:!bg-green-600 text-white"
              )}
            >
              {serverLoading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/60 border-t-transparent" />
              ) : serverRunning ? (
                StopSvg
              ) : (
                PlaySvg
              )}

              {serverLoading
                ? serverRunning
                  ? "Stopping..."
                  : "Starting..."
                : serverRunning
                ? "Stop server"
                : "Start server"}
            </Button>



            <span className="text-xs text-gray-500">
              {serverRunning ? "Active" : "Inactive"}
            </span>

        </div>

          <ProgressBarCard
            title="Workspace"
            change="+2.9%"
            value="21.7%"
            valueDescription="weekly active users"
            ctaDescription="Add up to 20 members in free plan."
            ctaText="Invite users."
            ctaLink="#"
            data={data2}
          />
          <CategoryBarCard
            title="Costs"
            change="-1.4%"
            value="$293.5"
            valueDescription="current billing cycle"
            subtitle="Current costs"
            ctaDescription="Set hard caps in"
            ctaText="cost spend management."
            ctaLink="#"
            data={data3}
          />
        </div>
      </section>
      <section aria-labelledby="usage-overview">
        <h1
          id="usage-overview"
          className="mt-16 scroll-mt-8 text-lg font-semibold text-gray-900 sm:text-xl dark:text-gray-50"
        >
          Overview
        </h1>
        <div className="sticky top-16 z-20 flex items-center justify-between border-b border-gray-200 bg-white pb-4 pt-4 sm:pt-6 lg:top-0 lg:mx-0 lg:px-0 lg:pt-8 dark:border-gray-800 dark:bg-gray-950">
          <Filterbar
            maxDate={maxDate}
            minDate={new Date(2024, 0, 1)}
            selectedDates={selectedDates}
            onDatesChange={(dates) => setSelectedDates(dates)}
            selectedPeriod={selectedPeriod}
            onPeriodChange={(period) => setSelectedPeriod(period)}
            categories={categories}
            setSelectedCategories={setSelectedCategories}
            selectedCategories={selectedCategories}
          />
        </div>
        <dl
          className={cx(
            "mt-10 grid grid-cols-1 gap-14 sm:grid-cols-1 md:grid-cols-2 xl:grid-cols-3",
          )}
        >
          {categories
            .filter((category) => selectedCategories.includes(category.title))
            .map((category) => {
              return (
                <ChartCard
                  key={category.title}
                  title={category.title}
                  type={category.type}
                  selectedDates={selectedDates}
                  selectedPeriod={selectedPeriod}
                />
              )
            })}
        </dl>
      </section>
    </>
  )
}
