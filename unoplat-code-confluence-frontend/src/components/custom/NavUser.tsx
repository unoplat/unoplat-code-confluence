import type { FC } from "react"
import { SidebarMenuButton } from "../ui/sidebar"
import { Avatar, AvatarImage, AvatarFallback } from "../ui/avatar"
// import { ChevronsUpDown } from "lucide-react"
import { GitHubUser } from "@/lib/api"



export const NavUser: FC<{ user: GitHubUser }> = ({ user }) => {
  return (
    <SidebarMenuButton
      size="lg"
      className="w-full data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
    >
      <Avatar className="h-8 w-8 rounded-lg flex-shrink-0">
        <AvatarImage src={user.avatar_url || ""} alt={user.name || ""} />
        <AvatarFallback className="rounded-lg">
          {(user.name || user.login).slice(0, 2).toUpperCase()}
        </AvatarFallback>
      </Avatar>
      <div className="grid flex-1 text-left text-sm leading-tight">
        <span className="truncate font-semibold">{user.name}</span>
        <span className="truncate text-xs">{user.email}</span>
      </div>
      {/* <ChevronsUpDown className="ml-auto size-4" /> */}
    </SidebarMenuButton>
  )
}
