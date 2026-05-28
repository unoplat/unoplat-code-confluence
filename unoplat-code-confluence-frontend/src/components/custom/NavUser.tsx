import type { FC } from "react";
import { SidebarMenuButton } from "../ui/sidebar";
import { Avatar, AvatarImage, AvatarFallback } from "../ui/avatar";
// import { ChevronsUpDown } from "lucide-react"
import { GitHubUser } from "@/lib/api";

export const NavUser: FC<{ user: GitHubUser }> = ({ user }) => {
  const name = user.name?.trim();
  const login = user.login?.trim();
  const email = user.email?.trim();
  const displayLabel = name || login || "User";
  const secondaryLabel = email || (name ? login : null);
  const initials = displayLabel.slice(0, 2).toUpperCase();

  return (
    <SidebarMenuButton
      size="lg"
      className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground w-full"
    >
      <Avatar className="h-8 w-8 flex-shrink-0 rounded-lg">
        <AvatarImage src={user.avatar_url || ""} alt={displayLabel} />
        <AvatarFallback className="rounded-lg">{initials}</AvatarFallback>
      </Avatar>
      <div className="grid flex-1 text-left text-sm leading-tight">
        <span className="truncate font-semibold">{displayLabel}</span>
        {secondaryLabel ? (
          <span className="truncate text-xs">{secondaryLabel}</span>
        ) : null}
      </div>
      {/* <ChevronsUpDown className="ml-auto size-4" /> */}
    </SidebarMenuButton>
  );
};
