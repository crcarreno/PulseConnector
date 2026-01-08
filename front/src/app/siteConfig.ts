export const siteConfig = {
  name: "Dashboard",
  url: "https://dashboard.tremor.so",
  description: "The only dashboard you will ever need.",
  baseLinks: {
    home: "/",
    overview: "/overview",
    details: "/details",
    settings: {
      general: "/settings/general",
      connections: "/settings/connections",
      users: "/settings/users",
      groups: "/settings/groups",
      endpoints: "/settings/endpoints",
      permissions: "/settings/permissions",
      billing: "/settings/billing"
    },
  },
}

export type siteConfig = typeof siteConfig
