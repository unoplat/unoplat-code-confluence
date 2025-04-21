import React from 'react'
import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarRail,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent
} from '../ui/sidebar'
import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent
} from '../ui/collapsible'
import { Link } from '@tanstack/react-router'
import { FileCheck, Settings, ChevronRight, LifeBuoy, Handshake } from 'lucide-react'
import { useAuthStore } from '@/stores/useAuthStore'
import { NavUser } from './NavUser'


export function AppSidebar(): React.ReactElement {
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
          {/* Workspace Setup Group */}
          <Collapsible className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="text-sm text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground cursor-pointer group-data-[collapsible=icon]:!opacity-100 group-data-[collapsible=icon]:!mt-0"
              >
                <CollapsibleTrigger className="flex w-full items-center font-semibold group-data-[collapsible=icon]:justify-center">
                  <FileCheck className="h-4 w-4" aria-hidden />
                  <span className="ml-2 group-data-[collapsible=icon]:hidden">Workspace Setup</span>
                  <ChevronRight className="ml-auto h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-90 group-data-[collapsible=icon]:hidden" aria-hidden />
                </CollapsibleTrigger>
              </SidebarGroupLabel>
              <CollapsibleContent className="group-data-[collapsible=icon]:hidden">
                <SidebarGroupContent>
                  <SidebarMenu>
                    <SidebarMenuItem>
                      <SidebarMenuButton asChild tooltip="GitHub Onboarding">
                        <Link to="/onboarding" className="flex w-full items-center rounded-md px-4 py-2 group-data-[collapsible=icon]:justify-center">
                          <span className="text-sm font-medium">GitHub Onboarding</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  </SidebarMenu>
                </SidebarGroupContent>
              </CollapsibleContent>
            </SidebarGroup>
          </Collapsible>
          {/* Settings Group */}
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="text-sm text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground cursor-pointer group-data-[collapsible=icon]:!opacity-100 group-data-[collapsible=icon]:!mt-0"
              >
                <CollapsibleTrigger className="flex w-full items-center font-semibold group-data-[collapsible=icon]:justify-center">
                  <Settings className="h-4 w-4" aria-hidden />
                  <span className="ml-2 group-data-[collapsible=icon]:hidden">Settings</span>
                  <ChevronRight className="ml-auto h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-90 group-data-[collapsible=icon]:hidden" aria-hidden />
                </CollapsibleTrigger>
              </SidebarGroupLabel>
              <CollapsibleContent className="group-data-[collapsible=icon]:hidden">
                <SidebarGroupContent>
                  <SidebarMenu>
                    <SidebarMenuItem>
                      <SidebarMenuButton asChild tooltip="Settings">
                        <Link to="/settings" className="flex w-full items-center rounded-md px-4 py-2 group-data-[collapsible=icon]:justify-center">
                          <span className="text-sm font-medium">GitHub Configuration</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                    <SidebarMenuItem>
                      <SidebarMenuButton asChild tooltip="Developer Mode">
                        <Link to="/settings/developer" className="flex w-full items-center rounded-md px-4 py-2 group-data-[collapsible=icon]:justify-center">
                          <span className="text-sm font-medium">Developer Mode</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  </SidebarMenu>
                </SidebarGroupContent>
              </CollapsibleContent>
            </SidebarGroup>
          </Collapsible>
          {/* Help and Support Group */}
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="text-sm text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground cursor-pointer group-data-[collapsible=icon]:!opacity-100 group-data-[collapsible=icon]:!mt-0"
              >
                <CollapsibleTrigger className="flex w-full items-center font-semibold group-data-[collapsible=icon]:justify-center">
                  <LifeBuoy className="h-4 w-4" aria-hidden />
                  <span className="ml-2 group-data-[collapsible=icon]:hidden">Help & Support</span>
                  <ChevronRight className="ml-auto h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-90 group-data-[collapsible=icon]:hidden" aria-hidden />
                </CollapsibleTrigger>
              </SidebarGroupLabel>
              <CollapsibleContent className="group-data-[collapsible=icon]:hidden">
                <SidebarGroupContent>
                  <SidebarMenu>
                    <SidebarMenuItem>
                      <SidebarMenuButton asChild tooltip="Discord Community">
                        <a 
                          href="https://discord.com/channels/1131597983058755675/1169968780953260106" 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="flex w-full items-center rounded-md px-4 py-2 group-data-[collapsible=icon]:justify-center"
                        >
                          <span className="text-sm font-medium">Discord Community</span>
                        </a>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                    <SidebarMenuItem>
                      <SidebarMenuButton asChild tooltip="Report an Issue">
                         <a 
                          href="https://github.com/unoplat/unoplat-code-confluence/issues" 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="flex w-full items-center rounded-md px-4 py-2 group-data-[collapsible=icon]:justify-center"
                        >
                          <span className="text-sm font-medium">Report an Issue</span>
                        </a>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  </SidebarMenu>
                </SidebarGroupContent>
              </CollapsibleContent>
            </SidebarGroup>
          </Collapsible>
          {/* Unoplat Connect Group */}
          <Collapsible defaultOpen className="group/collapsible">
            <SidebarGroup>
              <SidebarGroupLabel
                asChild
                className="text-sm text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground cursor-pointer group-data-[collapsible=icon]:!opacity-100 group-data-[collapsible=icon]:!mt-0"
              >
                <CollapsibleTrigger className="flex w-full items-center font-semibold group-data-[collapsible=icon]:justify-center">
                  <Handshake className="h-4 w-4" aria-hidden />
                  <span className="ml-2 group-data-[collapsible=icon]:hidden">Unoplat Connect</span>
                  <ChevronRight className="ml-auto h-4 w-4 transition-transform group-data-[state=open]/collapsible:rotate-90 group-data-[collapsible=icon]:hidden" aria-hidden />
                </CollapsibleTrigger>
              </SidebarGroupLabel>
              <CollapsibleContent className="group-data-[collapsible=icon]:hidden">
                <SidebarGroupContent>
                  <SidebarMenu>
                    <SidebarMenuItem>
                      <SidebarMenuButton asChild tooltip="LinkedIn: Dive into our latest updates">
                        <a
                          href="https://www.linkedin.com/company/unoplat"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex w-full items-center rounded-md px-4 py-2 group-data-[collapsible=icon]:justify-center"
                        >
                          <span className="text-sm font-medium">LinkedIn</span>
                        </a>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                    <SidebarMenuItem>
                      <SidebarMenuButton asChild tooltip="X/Twitter: Follow us for real-time insights">
                        <a
                          href="https://x.com/unoplatio"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex w-full items-center rounded-md px-4 py-2 group-data-[collapsible=icon]:justify-center"
                        >
                          <span className="text-sm font-medium">X / Twitter</span>
                        </a>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  </SidebarMenu>
                </SidebarGroupContent>
              </CollapsibleContent>
            </SidebarGroup>
          </Collapsible>
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