import React from 'react'
import { 
  Sidebar, 
  SidebarHeader, 
  SidebarContent, 
  SidebarFooter, 
  SidebarMenu, 
  SidebarMenuItem, 
  SidebarMenuButton,
  SidebarRail
} from '../ui/sidebar'
import { Link } from '@tanstack/react-router'
import { FileCheck, Settings } from 'lucide-react'
import { useAuthStore } from '@/stores/useAuthStore'
import { NavUser } from './NavUser'





export function AppSidebar(): React.ReactElement {
  // Use Zustand store for auth state
  const { user, tokenStatus } = useAuthStore()

  // Only show user info in footer when token is valid and user data exists
  const showUserInfo = tokenStatus?.status && user

  return (
    <Sidebar 
      side="left" 
      collapsible="icon" 
      variant="sidebar"
      className="group max-w-[14rem] w-full"

    >
      <SidebarHeader>
        <div className="flex items-center gap-2 px-4 py-2">
          {/* <img src={logoUnoplat} alt="Unoplat Code Confluence" className="h-8 w-8 object-contain" /> */}
          <h1 className="font-semibold text-lg truncate bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">Code Confluence</h1>
        </div>
      </SidebarHeader>

      <SidebarContent>
      <div className="px-2 space-y-1">

        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild tooltip="GitHub Onboarding">
              <Link to="/onboarding" className="flex w-full items-center gap-3 rounded-md px-4 py-2">
                <FileCheck />
                <span className="text-sm font-medium">Onboarding</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>

          <SidebarMenuItem>
            <SidebarMenuButton asChild tooltip="Settings">
              <Link to="/settings" className="flex w-full items-center gap-3 rounded-md px-4 py-2">
                <Settings />
                <span className="text-sm font-medium">Settings</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
        </div>
      </SidebarContent>

      {showUserInfo && (
        <SidebarFooter className="px-2 py-3">
          <NavUser user={user} />
        </SidebarFooter>
      )}
      
      {/* Add the sidebar rail for dragging/resizing */}
      <SidebarRail />
    </Sidebar>
  )
} 