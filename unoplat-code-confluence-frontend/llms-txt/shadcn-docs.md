# https://ui.shadcn.com/docs/components/ llms-full.txt

## Checkbox Component
[Docs](https://ui.shadcn.com/docs)

Checkbox

# Checkbox

A control that allows the user to toggle between checked and not checked.

[Docs](https://www.radix-ui.com/docs/primitives/components/checkbox) [API Reference](https://www.radix-ui.com/docs/primitives/components/checkbox#api-reference)

PreviewCode

Style: New York

Open in Copy

Accept terms and conditions

## [Link to section](https://ui.shadcn.com/docs/components/checkbox\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add checkbox

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/checkbox\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Checkbox } from "@/components/ui/checkbox"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Checkbox />
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/checkbox\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/checkbox\#with-text) With text

PreviewCode

Style: New York

Open in Copy

Accept terms and conditions

You agree to our Terms of Service and Privacy Policy.

### [Link to section](https://ui.shadcn.com/docs/components/checkbox\#disabled) Disabled

PreviewCode

Style: New York

Open in Copy

Accept terms and conditions

### [Link to section](https://ui.shadcn.com/docs/components/checkbox\#form) Form

PreviewCode

Style: New York

Copy

Use different settings for my mobile devices

You can manage your mobile notifications in the [mobile settings](https://ui.shadcn.com/examples/forms) page.

Submit

PreviewCode

Style: New York

Copy

Sidebar

Select the items you want to display in the sidebar.

Recents

Home

Applications

Desktop

Downloads

Documents

Submit

[Chart](https://ui.shadcn.com/docs/components/chart) [Collapsible](https://ui.shadcn.com/docs/components/collapsible)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/checkbox#installation)
- [Usage](https://ui.shadcn.com/docs/components/checkbox#usage)
- [Examples](https://ui.shadcn.com/docs/components/checkbox#examples)
  - [With text](https://ui.shadcn.com/docs/components/checkbox#with-text)
  - [Disabled](https://ui.shadcn.com/docs/components/checkbox#disabled)
  - [Form](https://ui.shadcn.com/docs/components/checkbox#form)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Command Menu Component
[Docs](https://ui.shadcn.com/docs)

Command

# Command

Fast, composable, unstyled command menu for React.

[Docs](https://cmdk.paco.me/)

PreviewCode

Style: New York

Open in Copy

Suggestions

Calendar

Search Emoji

Calculator

Settings

Profile⌘P

Billing⌘B

Settings⌘S

## [Link to section](https://ui.shadcn.com/docs/components/command\#about) About

The `<Command />` component uses the [`cmdk`](https://cmdk.paco.me/) component by [pacocoursey](https://twitter.com/pacocoursey).

## [Link to section](https://ui.shadcn.com/docs/components/command\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add command

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/command\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Command>
  <CommandInput placeholder="Type a command or search..." />
  <CommandList>
    <CommandEmpty>No results found.</CommandEmpty>
    <CommandGroup heading="Suggestions">
      <CommandItem>Calendar</CommandItem>
      <CommandItem>Search Emoji</CommandItem>
      <CommandItem>Calculator</CommandItem>
    </CommandGroup>
    <CommandSeparator />
    <CommandGroup heading="Settings">
      <CommandItem>Profile</CommandItem>
      <CommandItem>Billing</CommandItem>
      <CommandItem>Settings</CommandItem>
    </CommandGroup>
  </CommandList>
</Command>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/command\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/command\#dialog) Dialog

PreviewCode

Style: New York

Open in Copy

Press `⌘J`

To show the command menu in a dialog, use the `<CommandDialog />` component.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export function CommandMenu() {
  const [open, setOpen] = React.useState(false)

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Suggestions">
          <CommandItem>Calendar</CommandItem>
          <CommandItem>Search Emoji</CommandItem>
          <CommandItem>Calculator</CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/command\#combobox) Combobox

You can use the `<Command />` component as a combobox. See the [Combobox](https://ui.shadcn.com/docs/components/combobox) page for more information.

## [Link to section](https://ui.shadcn.com/docs/components/command\#changelog) Changelog

### [Link to section](https://ui.shadcn.com/docs/components/command\#2024-10-25-classes-for-icons) 2024-10-25 Classes for icons

Added `gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0` to the `<CommandItem />` to automatically style icon inside.

Add the following classes to the `cva` call in your `command.tsx` file.

command.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const CommandItem = React.forwardRef<
  React.ElementRef<typeof CommandPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof CommandPrimitive.Item>
>(({ className, ...props }, ref) => (
  <CommandPrimitive.Item
    ref={ref}
    className={cn(
      "... gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
      className
    )}
    {...props}
  />
))
```

Copy

[Combobox](https://ui.shadcn.com/docs/components/combobox) [Context Menu](https://ui.shadcn.com/docs/components/context-menu)

On This Page

- [About](https://ui.shadcn.com/docs/components/command#about)
- [Installation](https://ui.shadcn.com/docs/components/command#installation)
- [Usage](https://ui.shadcn.com/docs/components/command#usage)
- [Examples](https://ui.shadcn.com/docs/components/command#examples)
  - [Dialog](https://ui.shadcn.com/docs/components/command#dialog)
  - [Combobox](https://ui.shadcn.com/docs/components/command#combobox)
- [Changelog](https://ui.shadcn.com/docs/components/command#changelog)
  - [2024-10-25 Classes for icons](https://ui.shadcn.com/docs/components/command#2024-10-25-classes-for-icons)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Toast Notifications Guide
[Docs](https://ui.shadcn.com/docs)

Toast

# Toast

A succinct message that is displayed temporarily.

[Docs](https://www.radix-ui.com/docs/primitives/components/toast) [API Reference](https://www.radix-ui.com/docs/primitives/components/toast#api-reference)

PreviewCode

Style: New York

Copy

Add to calendar

## [Link to section](https://ui.shadcn.com/docs/components/toast\#installation) Installation

CLIManual

### Run the following command:

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add toast

```

Copy

### Add the Toaster component

app/layout.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Toaster } from "@/components/ui/toaster"

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head />
      <body>
        <main>{children}</main>
        <Toaster />
      </body>
    </html>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/toast\#usage) Usage

The `useToast` hook returns a `toast` function that you can use to display a toast.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { useToast } from "@/hooks/use-toast"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export const ToastDemo = () => {
  const { toast } = useToast()

  return (
    <Button
      onClick={() => {
        toast({
          title: "Scheduled: Catch up",
          description: "Friday, February 10, 2023 at 5:57 PM",
        })
      }}
    >
      Show Toast
    </Button>
  )
}
```

Copy

To display multiple toasts at the same time, you can update the `TOAST_LIMIT` in `use-toast.tsx`.

## [Link to section](https://ui.shadcn.com/docs/components/toast\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/toast\#simple) Simple

PreviewCode

Style: New York

Copy

Show Toast

### [Link to section](https://ui.shadcn.com/docs/components/toast\#with-title) With title

PreviewCode

Style: New York

Copy

Show Toast

### [Link to section](https://ui.shadcn.com/docs/components/toast\#with-action) With Action

PreviewCode

Style: New York

Copy

Show Toast

### [Link to section](https://ui.shadcn.com/docs/components/toast\#destructive) Destructive

Use `toast({ variant: "destructive" })` to display a destructive toast.

PreviewCode

Style: New York

Copy

Show Toast

[Textarea](https://ui.shadcn.com/docs/components/textarea) [Toggle](https://ui.shadcn.com/docs/components/toggle)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/toast#installation)
- [Usage](https://ui.shadcn.com/docs/components/toast#usage)
- [Examples](https://ui.shadcn.com/docs/components/toast#examples)
  - [Simple](https://ui.shadcn.com/docs/components/toast#simple)
  - [With title](https://ui.shadcn.com/docs/components/toast#with-title)
  - [With Action](https://ui.shadcn.com/docs/components/toast#with-action)
  - [Destructive](https://ui.shadcn.com/docs/components/toast#destructive)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Typography Styles Overview
[Docs](https://ui.shadcn.com/docs)

Typography

# Typography

Styles for headings, paragraphs, lists...etc

PreviewCode

Style: New York

Open in Copy

# The Joke Tax Chronicles

Once upon a time, in a far-off land, there was a very lazy king who spent all day lounging on his throne. One day, his advisors came to him with a problem: the kingdom was running out of money.

## The King's Plan

The king thought long and hard, and finally came up with [a brilliant plan](https://ui.shadcn.com/docs/components/typography#): he would tax the jokes in the kingdom.

> "After all," he said, "everyone enjoys a good joke, so it's only fair that they should pay for the privilege."

### The Joke Tax

The king's subjects were not amused. They grumbled and complained, but the king was firm:

- 1st level of puns: 5 gold coins
- 2nd level of jokes: 10 gold coins
- 3rd level of one-liners : 20 gold coins

As a result, people stopped telling jokes, and the kingdom fell into a gloom. But there was one person who refused to let the king's foolishness get him down: a court jester named Jokester.

### Jokester's Revolt

Jokester began sneaking into the castle in the middle of the night and leaving jokes all over the place: under the king's pillow, in his soup, even in the royal toilet. The king was furious, but he couldn't seem to stop Jokester.

And then, one day, the people of the kingdom discovered that the jokes left by Jokester were so funny that they couldn't help but laugh. And once they started laughing, they couldn't stop.

### The People's Rebellion

The people of the kingdom, feeling uplifted by the laughter, started to tell jokes and puns again, and soon the entire kingdom was in on the joke.

| King's Treasury | People's happiness |
| --- | --- |
| Empty | Overflowing |
| Modest | Satisfied |
| Full | Ecstatic |

The king, seeing how much happier his subjects were, realized the error of his ways and repealed the joke tax. Jokester was declared a hero, and the kingdom lived happily ever after.

The moral of the story is: never underestimate the power of a good laugh and always be careful of bad ideas.

## [Link to section](https://ui.shadcn.com/docs/components/typography\#h1) h1

PreviewCode

Style: New York

Copy

# Taxing Laughter: The Joke Tax Chronicles

## [Link to section](https://ui.shadcn.com/docs/components/typography\#h2) h2

PreviewCode

Style: New York

Copy

## The People of the Kingdom

## [Link to section](https://ui.shadcn.com/docs/components/typography\#h3) h3

PreviewCode

Style: New York

Copy

### The Joke Tax

## [Link to section](https://ui.shadcn.com/docs/components/typography\#h4) h4

PreviewCode

Style: New York

Copy

#### People stopped telling jokes

## [Link to section](https://ui.shadcn.com/docs/components/typography\#p) p

PreviewCode

Style: New York

Copy

The king, seeing how much happier his subjects were, realized the error of his ways and repealed the joke tax.

## [Link to section](https://ui.shadcn.com/docs/components/typography\#blockquote) blockquote

PreviewCode

Style: New York

Copy

> "After all," he said, "everyone enjoys a good joke, so it's only fair that they should pay for the privilege."

## [Link to section](https://ui.shadcn.com/docs/components/typography\#table) table

PreviewCode

Style: New York

Copy

| King's Treasury | People's happiness |
| --- | --- |
| Empty | Overflowing |
| Modest | Satisfied |
| Full | Ecstatic |

## [Link to section](https://ui.shadcn.com/docs/components/typography\#list) list

PreviewCode

Style: New York

Copy

- 1st level of puns: 5 gold coins
- 2nd level of jokes: 10 gold coins
- 3rd level of one-liners : 20 gold coins

## [Link to section](https://ui.shadcn.com/docs/components/typography\#inline-code) Inline code

PreviewCode

Style: New York

Copy

`@radix-ui/react-alert-dialog`

## [Link to section](https://ui.shadcn.com/docs/components/typography\#lead) Lead

PreviewCode

Style: New York

Copy

A modal dialog that interrupts the user with important content and expects a response.

## [Link to section](https://ui.shadcn.com/docs/components/typography\#large) Large

PreviewCode

Style: New York

Copy

Are you absolutely sure?

## [Link to section](https://ui.shadcn.com/docs/components/typography\#small) Small

PreviewCode

Style: New York

Copy

Email address

## [Link to section](https://ui.shadcn.com/docs/components/typography\#muted) Muted

PreviewCode

Style: New York

Copy

Enter your email address.

[Next.js 15 + React 19](https://ui.shadcn.com/docs/react-19) [Open in v0](https://ui.shadcn.com/docs/v0)

On This Page

- [h1](https://ui.shadcn.com/docs/components/typography#h1)
- [h2](https://ui.shadcn.com/docs/components/typography#h2)
- [h3](https://ui.shadcn.com/docs/components/typography#h3)
- [h4](https://ui.shadcn.com/docs/components/typography#h4)
- [p](https://ui.shadcn.com/docs/components/typography#p)
- [blockquote](https://ui.shadcn.com/docs/components/typography#blockquote)
- [table](https://ui.shadcn.com/docs/components/typography#table)
- [list](https://ui.shadcn.com/docs/components/typography#list)
- [Inline code](https://ui.shadcn.com/docs/components/typography#inline-code)
- [Lead](https://ui.shadcn.com/docs/components/typography#lead)
- [Large](https://ui.shadcn.com/docs/components/typography#large)
- [Small](https://ui.shadcn.com/docs/components/typography#small)
- [Muted](https://ui.shadcn.com/docs/components/typography#muted)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Customizable Sidebar
[Docs](https://ui.shadcn.com/docs)

Sidebar

# Sidebar

A composable, themeable and customizable sidebar component.

![sidebar-07](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-07-light.png&w=3840&q=75)![sidebar-07](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-07-dark.png&w=3840&q=75)

sidebar-07 - A sidebar that collapses to icons. - shadcn/ui

A sidebar that collapses to icons.

Sidebars are one of the most complex components to build. They are central
to any application and often contain a lot of moving parts.

I don't like building sidebars. So I built 30+ of them. All kinds of
configurations. Then I extracted the core components into `sidebar.tsx`.

We now have a solid foundation to build on top of. Composable. Themeable.
Customizable.

[Browse the Blocks Library](https://ui.shadcn.com/blocks).

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#installation) Installation

CLIManual

### Run the following command to install `sidebar.tsx`

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add sidebar

```

Copy

### Add the following colors to your CSS file

The command above should install the colors for you. If not, copy and paste the following in your CSS file.

We'll go over the colors later in the [theming section](https://ui.shadcn.com/docs/components/sidebar#theming).

app/globals.css

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
@layer base {
  :root {
    --sidebar-background: 0 0% 98%;
    --sidebar-foreground: 240 5.3% 26.1%;
    --sidebar-primary: 240 5.9% 10%;
    --sidebar-primary-foreground: 0 0% 98%;
    --sidebar-accent: 240 4.8% 95.9%;
    --sidebar-accent-foreground: 240 5.9% 10%;
    --sidebar-border: 220 13% 91%;
    --sidebar-ring: 217.2 91.2% 59.8%;
  }

  .dark {
    --sidebar-background: 240 5.9% 10%;
    --sidebar-foreground: 240 4.8% 95.9%;
    --sidebar-primary: 224.3 76.3% 48%;
    --sidebar-primary-foreground: 0 0% 100%;
    --sidebar-accent: 240 3.7% 15.9%;
    --sidebar-accent-foreground: 240 4.8% 95.9%;
    --sidebar-border: 240 3.7% 15.9%;
    --sidebar-ring: 217.2 91.2% 59.8%;
  }
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#structure) Structure

A `Sidebar` component is composed of the following parts:

- `SidebarProvider` \- Handles collapsible state.
- `Sidebar` \- The sidebar container.
- `SidebarHeader` and `SidebarFooter` \- Sticky at the top and bottom of the sidebar.
- `SidebarContent` \- Scrollable content.
- `SidebarGroup` \- Section within the `SidebarContent`.
- `SidebarTrigger` \- Trigger for the `Sidebar`.

![Sidebar Structure](https://ui.shadcn.com/_next/image?url=%2Fimages%2Fsidebar-structure.png&w=1920&q=75)![Sidebar Structure](https://ui.shadcn.com/_next/image?url=%2Fimages%2Fsidebar-structure-dark.png&w=1920&q=75)

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#usage) Usage

app/layout.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <main>
        <SidebarTrigger />
        {children}
      </main>
    </SidebarProvider>
  )
}
```

Copy

components/app-sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
} from "@/components/ui/sidebar"

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarHeader />
      <SidebarContent>
        <SidebarGroup />
        <SidebarGroup />
      </SidebarContent>
      <SidebarFooter />
    </Sidebar>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#your-first-sidebar) Your First Sidebar

Let's start with the most basic sidebar. A collapsible sidebar with a menu.

### Add a `SidebarProvider` and `SidebarTrigger` at the root of your application.

app/layout.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <main>
        <SidebarTrigger />
        {children}
      </main>
    </SidebarProvider>
  )
}
```

Copy

### Create a new sidebar component at `components/app-sidebar.tsx`.

components/app-sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Sidebar, SidebarContent } from "@/components/ui/sidebar"

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent />
    </Sidebar>
  )
}
```

Copy

### Now, let's add a `SidebarMenu` to the sidebar.

We'll use the `SidebarMenu` component in a `SidebarGroup`.

components/app-sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Calendar, Home, Inbox, Search, Settings } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

// Menu items.
const items = [\
  {\
    title: "Home",\
    url: "#",\
    icon: Home,\
  },\
  {\
    title: "Inbox",\
    url: "#",\
    icon: Inbox,\
  },\
  {\
    title: "Calendar",\
    url: "#",\
    icon: Calendar,\
  },\
  {\
    title: "Search",\
    url: "#",\
    icon: Search,\
  },\
  {\
    title: "Settings",\
    url: "#",\
    icon: Settings,\
  },\
]

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
```

Copy

### You've created your first sidebar.

![sidebar-demo](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-demo-light.png&w=3840&q=75)![sidebar-demo](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-demo-dark.png&w=3840&q=75)

sidebar-demo - shadcn/ui

Your first sidebar.

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#components) Components

The components in `sidebar.tsx` are built to be composable i.e you build your sidebar by putting the provided components together. They also compose well with other shadcn/ui components such as `DropdownMenu`, `Collapsible` or `Dialog` etc.

**If you need to change the code in `sidebar.tsx`, you are encouraged to do so. The code is yours. Use `sidebar.tsx` as a starting point and build your own.**

In the next sections, we'll go over each component and how to use them.

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarprovider) SidebarProvider

The `SidebarProvider` component is used to provide the sidebar context to the `Sidebar` component. You should always wrap your application in a `SidebarProvider` component.

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#props) Props

| Name | Type | Description |
| --- | --- | --- |
| `defaultOpen` | `boolean` | Default open state of the sidebar. |
| `open` | `boolean` | Open state of the sidebar (controlled). |
| `onOpenChange` | `(open: boolean) => void` | Sets open state of the sidebar (controlled). |

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#width) Width

If you have a single sidebar in your application, you can use the `SIDEBAR_WIDTH` and `SIDEBAR_WIDTH_MOBILE` variables in `sidebar.tsx` to set the width of the sidebar.

components/ui/sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const SIDEBAR_WIDTH = "16rem"
const SIDEBAR_WIDTH_MOBILE = "18rem"
```

Copy

For multiple sidebars in your application, you can use the `style` prop to set the width of the sidebar.

To set the width of the sidebar, you can use the `--sidebar-width` and `--sidebar-width-mobile` CSS variables in the `style` prop.

components/ui/sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarProvider
  style={{
    "--sidebar-width": "20rem",
    "--sidebar-width-mobile": "20rem",
  }}
>
  <Sidebar />
</SidebarProvider>
```

Copy

This will handle the width of the sidebar but also the layout spacing.

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#keyboard-shortcut) Keyboard Shortcut

The `SIDEBAR_KEYBOARD_SHORTCUT` variable is used to set the keyboard shortcut used to open and close the sidebar.

To trigger the sidebar, you use the `cmd+b` keyboard shortcut on Mac and `ctrl+b` on Windows.

You can change the keyboard shortcut by updating the `SIDEBAR_KEYBOARD_SHORTCUT` variable.

components/ui/sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const SIDEBAR_KEYBOARD_SHORTCUT = "b"
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#persisted-state) Persisted State

The `SidebarProvider` supports persisting the sidebar state across page reloads and server-side rendering. It uses cookies to store the current state of the sidebar. When the sidebar state changes, a default cookie named `sidebar_state` is set with the current open/closed state. This cookie is then read on subsequent page loads to restore the sidebar state.

To persist sidebar state in Next.js, set up your `SidebarProvider` in `app/layout.tsx` like this:

app/layout.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { cookies } from "next/headers"

import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"

export async function Layout({ children }: { children: React.ReactNode }) {
  const cookieStore = await cookies()
  const defaultOpen = cookieStore.get("sidebar_state")?.value === "true"

  return (
    <SidebarProvider defaultOpen={defaultOpen}>
      <AppSidebar />
      <main>
        <SidebarTrigger />
        {children}
      </main>
    </SidebarProvider>
  )
}
```

Copy

You can change the name of the cookie by updating the `SIDEBAR_COOKIE_NAME` variable in `sidebar.tsx`.

components/ui/sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const SIDEBAR_COOKIE_NAME = "sidebar_state"
```

Copy

The main `Sidebar` component used to render a collapsible sidebar.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Sidebar } from "@/components/ui/sidebar"

export function AppSidebar() {
  return <Sidebar />
}
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#props-1) Props

| Property | Type | Description |
| --- | --- | --- |
| `side` | `left` or `right` | The side of the sidebar. |
| `variant` | `sidebar`, `floating`, or `inset` | The variant of the sidebar. |
| `collapsible` | `offcanvas`, `icon`, or `none` | Collapsible state of the sidebar. |

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#side) side

Use the `side` prop to change the side of the sidebar.

Available options are `left` and `right`.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Sidebar } from "@/components/ui/sidebar"

export function AppSidebar() {
  return <Sidebar side="left | right" />
}
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#variant) variant

Use the `variant` prop to change the variant of the sidebar.

Available options are `sidebar`, `floating` and `inset`.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Sidebar } from "@/components/ui/sidebar"

export function AppSidebar() {
  return <Sidebar variant="sidebar | floating | inset" />
}
```

Copy

**Note:** If you use the `inset` variant, remember to wrap your main content
in a `SidebarInset` component.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarProvider>
  <Sidebar variant="inset" />
  <SidebarInset>
    <main>{children}</main>
  </SidebarInset>
</SidebarProvider>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#collapsible) collapsible

Use the `collapsible` prop to make the sidebar collapsible.

Available options are `offcanvas`, `icon` and `none`.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Sidebar } from "@/components/ui/sidebar"

export function AppSidebar() {
  return <Sidebar collapsible="offcanvas | icon | none" />
}
```

Copy

| Prop | Description |
| --- | --- |
| `offcanvas` | A collapsible sidebar that slides in from the left or right. |
| `icon` | A sidebar that collapses to icons. |
| `none` | A non-collapsible sidebar. |

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#usesidebar) useSidebar

The `useSidebar` hook is used to control the sidebar.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { useSidebar } from "@/components/ui/sidebar"

export function AppSidebar() {
  const {
    state,
    open,
    setOpen,
    openMobile,
    setOpenMobile,
    isMobile,
    toggleSidebar,
  } = useSidebar()
}
```

Copy

| Property | Type | Description |
| --- | --- | --- |
| `state` | `expanded` or `collapsed` | The current state of the sidebar. |
| `open` | `boolean` | Whether the sidebar is open. |
| `setOpen` | `(open: boolean) => void` | Sets the open state of the sidebar. |
| `openMobile` | `boolean` | Whether the sidebar is open on mobile. |
| `setOpenMobile` | `(open: boolean) => void` | Sets the open state of the sidebar on mobile. |
| `isMobile` | `boolean` | Whether the sidebar is on mobile. |
| `toggleSidebar` | `() => void` | Toggles the sidebar. Desktop and mobile. |

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarheader) SidebarHeader

Use the `SidebarHeader` component to add a sticky header to the sidebar.

The following example adds a `<DropdownMenu>` to the `SidebarHeader`.

![sidebar-header](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-header-light.png&w=3840&q=75)![sidebar-header](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-header-dark.png&w=3840&q=75)

sidebar-header - shadcn/ui

A sidebar header with a dropdown menu.

components/app-sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Sidebar>
  <SidebarHeader>
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton>
              Select Workspace
              <ChevronDown className="ml-auto" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-[--radix-popper-anchor-width]">
            <DropdownMenuItem>
              <span>Acme Inc</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <span>Acme Corp.</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  </SidebarHeader>
</Sidebar>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarfooter) SidebarFooter

Use the `SidebarFooter` component to add a sticky footer to the sidebar.

The following example adds a `<DropdownMenu>` to the `SidebarFooter`.

![sidebar-footer](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-footer-light.png&w=3840&q=75)![sidebar-footer](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-footer-dark.png&w=3840&q=75)

sidebar-footer - shadcn/ui

A sidebar footer with a dropdown menu.

components/app-sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export function AppSidebar() {
  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader />
        <SidebarContent />
        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <SidebarMenuButton>
                    <User2 /> Username
                    <ChevronUp className="ml-auto" />
                  </SidebarMenuButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  side="top"
                  className="w-[--radix-popper-anchor-width]"
                >
                  <DropdownMenuItem>
                    <span>Account</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <span>Billing</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <span>Sign out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>
    </SidebarProvider>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarcontent) SidebarContent

The `SidebarContent` component is used to wrap the content of the sidebar. This is where you add your `SidebarGroup` components. It is scrollable.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Sidebar, SidebarContent } from "@/components/ui/sidebar"

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup />
        <SidebarGroup />
      </SidebarContent>
    </Sidebar>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebargroup) SidebarGroup

Use the `SidebarGroup` component to create a section within the sidebar.

A `SidebarGroup` has a `SidebarGroupLabel`, a `SidebarGroupContent` and an optional `SidebarGroupAction`.

![sidebar-group](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-group-light.png&w=3840&q=75)![sidebar-group](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-group-dark.png&w=3840&q=75)

sidebar-group - shadcn/ui

A sidebar group.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Sidebar, SidebarContent, SidebarGroup } from "@/components/ui/sidebar"

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupAction>
            <Plus /> <span className="sr-only">Add Project</span>
          </SidebarGroupAction>
          <SidebarGroupContent></SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#collapsible-sidebargroup) Collapsible SidebarGroup

To make a `SidebarGroup` collapsible, wrap it in a `Collapsible`.

![sidebar-group-collapsible](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-group-collapsible-light.png&w=3840&q=75)![sidebar-group-collapsible](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-group-collapsible-dark.png&w=3840&q=75)

sidebar-group-collapsible - shadcn/ui

A collapsible sidebar group.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export function AppSidebar() {
  return (
    <Collapsible defaultOpen className="group/collapsible">
      <SidebarGroup>
        <SidebarGroupLabel asChild>
          <CollapsibleTrigger>
            Help
            <ChevronDown className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-180" />
          </CollapsibleTrigger>
        </SidebarGroupLabel>
        <CollapsibleContent>
          <SidebarGroupContent />
        </CollapsibleContent>
      </SidebarGroup>
    </Collapsible>
  )
}
```

Copy

**Note:** We wrap the `CollapsibleTrigger` in a `SidebarGroupLabel` to render
a button.

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebargroupaction) SidebarGroupAction

Use the `SidebarGroupAction` component to add an action button to the `SidebarGroup`.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export function AppSidebar() {
  return (
    <SidebarGroup>
      <SidebarGroupLabel asChild>Projects</SidebarGroupLabel>
      <SidebarGroupAction title="Add Project">
        <Plus /> <span className="sr-only">Add Project</span>
      </SidebarGroupAction>
      <SidebarGroupContent />
    </SidebarGroup>
  )
}
```

Copy

![sidebar-group-action](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-group-action-light.png&w=3840&q=75)![sidebar-group-action](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-group-action-dark.png&w=3840&q=75)

sidebar-group-action - shadcn/ui

A sidebar group with an action button.

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarmenu) SidebarMenu

The `SidebarMenu` component is used for building a menu within a `SidebarGroup`.

A `SidebarMenu` component is composed of `SidebarMenuItem`, `SidebarMenuButton`, `<SidebarMenuAction />` and `<SidebarMenuSub />` components.

![Sidebar Menu](https://ui.shadcn.com/_next/image?url=%2Fimages%2Fsidebar-menu.png&w=1920&q=75)![Sidebar Menu](https://ui.shadcn.com/_next/image?url=%2Fimages%2Fsidebar-menu-dark.png&w=1920&q=75)

Here's an example of a `SidebarMenu` component rendering a list of projects.

![sidebar-menu](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-light.png&w=3840&q=75)![sidebar-menu](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-dark.png&w=3840&q=75)

sidebar-menu - shadcn/ui

A sidebar menu with a list of projects.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Sidebar>
  <SidebarContent>
    <SidebarGroup>
      <SidebarGroupLabel>Projects</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          {projects.map((project) => (
            <SidebarMenuItem key={project.name}>
              <SidebarMenuButton asChild>
                <a href={project.url}>
                  <project.icon />
                  <span>{project.name}</span>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  </SidebarContent>
</Sidebar>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarmenubutton) SidebarMenuButton

The `SidebarMenuButton` component is used to render a menu button within a `SidebarMenuItem`.

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#link-or-anchor) Link or Anchor

By default, the `SidebarMenuButton` renders a button but you can use the `asChild` prop to render a different component such as a `Link` or an `a` tag.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarMenuButton asChild>
  <a href="#">Home</a>
</SidebarMenuButton>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#icon-and-label) Icon and Label

You can render an icon and a truncated label inside the button. Remember to wrap the label in a `<span>`.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarMenuButton asChild>
  <a href="#">
    <Home />
    <span>Home</span>
  </a>
</SidebarMenuButton>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#isactive) isActive

Use the `isActive` prop to mark a menu item as active.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarMenuButton asChild isActive>
  <a href="#">Home</a>
</SidebarMenuButton>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarmenuaction) SidebarMenuAction

The `SidebarMenuAction` component is used to render a menu action within a `SidebarMenuItem`.

This button works independently of the `SidebarMenuButton` i.e you can have the `<SidebarMenuButton />` as a clickable link and the `<SidebarMenuAction />` as a button.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarMenuItem>
  <SidebarMenuButton asChild>
    <a href="#">
      <Home />
      <span>Home</span>
    </a>
  </SidebarMenuButton>
  <SidebarMenuAction>
    <Plus /> <span className="sr-only">Add Project</span>
  </SidebarMenuAction>
</SidebarMenuItem>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#dropdownmenu) DropdownMenu

Here's an example of a `SidebarMenuAction` component rendering a `DropdownMenu`.

![sidebar-menu-action](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-action-light.png&w=3840&q=75)![sidebar-menu-action](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-action-dark.png&w=3840&q=75)

sidebar-menu-action - shadcn/ui

A sidebar menu action with a dropdown menu.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarMenuItem>
  <SidebarMenuButton asChild>
    <a href="#">
      <Home />
      <span>Home</span>
    </a>
  </SidebarMenuButton>
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <SidebarMenuAction>
        <MoreHorizontal />
      </SidebarMenuAction>
    </DropdownMenuTrigger>
    <DropdownMenuContent side="right" align="start">
      <DropdownMenuItem>
        <span>Edit Project</span>
      </DropdownMenuItem>
      <DropdownMenuItem>
        <span>Delete Project</span>
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</SidebarMenuItem>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarmenusub) SidebarMenuSub

The `SidebarMenuSub` component is used to render a submenu within a `SidebarMenu`.

Use `<SidebarMenuSubItem />` and `<SidebarMenuSubButton />` to render a submenu item.

![sidebar-menu-sub](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-sub-light.png&w=3840&q=75)![sidebar-menu-sub](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-sub-dark.png&w=3840&q=75)

sidebar-menu-sub - shadcn/ui

A sidebar menu with a submenu.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarMenuItem>
  <SidebarMenuButton />
  <SidebarMenuSub>
    <SidebarMenuSubItem>
      <SidebarMenuSubButton />
    </SidebarMenuSubItem>
    <SidebarMenuSubItem>
      <SidebarMenuSubButton />
    </SidebarMenuSubItem>
  </SidebarMenuSub>
</SidebarMenuItem>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#collapsible-sidebarmenu) Collapsible SidebarMenu

To make a `SidebarMenu` component collapsible, wrap it and the `SidebarMenuSub` components in a `Collapsible`.

![sidebar-menu-collapsible](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-collapsible-light.png&w=3840&q=75)![sidebar-menu-collapsible](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-collapsible-dark.png&w=3840&q=75)

sidebar-menu-collapsible - shadcn/ui

A collapsible sidebar menu.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarMenu>
  <Collapsible defaultOpen className="group/collapsible">
    <SidebarMenuItem>
      <CollapsibleTrigger asChild>
        <SidebarMenuButton />
      </CollapsibleTrigger>
      <CollapsibleContent>
        <SidebarMenuSub>
          <SidebarMenuSubItem />
        </SidebarMenuSub>
      </CollapsibleContent>
    </SidebarMenuItem>
  </Collapsible>
</SidebarMenu>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarmenubadge) SidebarMenuBadge

The `SidebarMenuBadge` component is used to render a badge within a `SidebarMenuItem`.

![sidebar-menu-badge](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-badge-light.png&w=3840&q=75)![sidebar-menu-badge](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-menu-badge-dark.png&w=3840&q=75)

sidebar-menu-badge - shadcn/ui

A sidebar menu with a badge.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarMenuItem>
  <SidebarMenuButton />
  <SidebarMenuBadge>24</SidebarMenuBadge>
</SidebarMenuItem>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarmenuskeleton) SidebarMenuSkeleton

The `SidebarMenuSkeleton` component is used to render a skeleton for a `SidebarMenu`. You can use this to show a loading state when using React Server Components, SWR or react-query.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
function NavProjectsSkeleton() {
  return (
    <SidebarMenu>
      {Array.from({ length: 5 }).map((_, index) => (
        <SidebarMenuItem key={index}>
          <SidebarMenuSkeleton />
        </SidebarMenuItem>
      ))}
    </SidebarMenu>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarseparator) SidebarSeparator

The `SidebarSeparator` component is used to render a separator within a `Sidebar`.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Sidebar>
  <SidebarHeader />
  <SidebarSeparator />
  <SidebarContent>
    <SidebarGroup />
    <SidebarSeparator />
    <SidebarGroup />
  </SidebarContent>
</Sidebar>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebartrigger) SidebarTrigger

Use the `SidebarTrigger` component to render a button that toggles the sidebar.

The `SidebarTrigger` component must be used within a `SidebarProvider`.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarProvider>
  <Sidebar />
  <main>
    <SidebarTrigger />
  </main>
</SidebarProvider>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#custom-trigger) Custom Trigger

To create a custom trigger, you can use the `useSidebar` hook.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { useSidebar } from "@/components/ui/sidebar"

export function CustomTrigger() {
  const { toggleSidebar } = useSidebar()

  return <button onClick={toggleSidebar}>Toggle Sidebar</button>
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#sidebarrail) SidebarRail

The `SidebarRail` component is used to render a rail within a `Sidebar`. This rail can be used to toggle the sidebar.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Sidebar>
  <SidebarHeader />
  <SidebarContent>
    <SidebarGroup />
  </SidebarContent>
  <SidebarFooter />
  <SidebarRail />
</Sidebar>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#data-fetching) Data Fetching

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#react-server-components) React Server Components

Here's an example of a `SidebarMenu` component rendering a list of projects using React Server Components.

![sidebar-rsc](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-rsc-light.png&w=3840&q=75)![sidebar-rsc](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-rsc-dark.png&w=3840&q=75)

sidebar-rsc - shadcn/ui

A sidebar menu using React Server Components.

Skeleton to show loading state.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
function NavProjectsSkeleton() {
  return (
    <SidebarMenu>
      {Array.from({ length: 5 }).map((_, index) => (
        <SidebarMenuItem key={index}>
          <SidebarMenuSkeleton showIcon />
        </SidebarMenuItem>
      ))}
    </SidebarMenu>
  )
}
```

Copy

Server component fetching data.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
async function NavProjects() {
  const projects = await fetchProjects()

  return (
    <SidebarMenu>
      {projects.map((project) => (
        <SidebarMenuItem key={project.name}>
          <SidebarMenuButton asChild>
            <a href={project.url}>
              <project.icon />
              <span>{project.name}</span>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      ))}
    </SidebarMenu>
  )
}
```

Copy

Usage with React Suspense.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
function AppSidebar() {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Projects</SidebarGroupLabel>
          <SidebarGroupContent>
            <React.Suspense fallback={<NavProjectsSkeleton />}>
              <NavProjects />
            </React.Suspense>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#swr-and-react-query) SWR and React Query

You can use the same approach with [SWR](https://swr.vercel.app/) or [react-query](https://tanstack.com/query/latest/docs/framework/react/overview).

SWR

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
function NavProjects() {
  const { data, isLoading } = useSWR("/api/projects", fetcher)

  if (isLoading) {
    return (
      <SidebarMenu>
        {Array.from({ length: 5 }).map((_, index) => (
          <SidebarMenuItem key={index}>
            <SidebarMenuSkeleton showIcon />
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    )
  }

  if (!data) {
    return ...
  }

  return (
    <SidebarMenu>
      {data.map((project) => (
        <SidebarMenuItem key={project.name}>
          <SidebarMenuButton asChild>
            <a href={project.url}>
              <project.icon />
              <span>{project.name}</span>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      ))}
    </SidebarMenu>
  )
}
```

Copy

React Query

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
function NavProjects() {
  const { data, isLoading } = useQuery()

  if (isLoading) {
    return (
      <SidebarMenu>
        {Array.from({ length: 5 }).map((_, index) => (
          <SidebarMenuItem key={index}>
            <SidebarMenuSkeleton showIcon />
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    )
  }

  if (!data) {
    return ...
  }

  return (
    <SidebarMenu>
      {data.map((project) => (
        <SidebarMenuItem key={project.name}>
          <SidebarMenuButton asChild>
            <a href={project.url}>
              <project.icon />
              <span>{project.name}</span>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      ))}
    </SidebarMenu>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#controlled-sidebar) Controlled Sidebar

Use the `open` and `onOpenChange` props to control the sidebar.

![sidebar-controlled](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-controlled-light.png&w=3840&q=75)![sidebar-controlled](https://ui.shadcn.com/_next/image?url=%2Fr%2Fstyles%2Fnew-york%2Fsidebar-controlled-dark.png&w=3840&q=75)

sidebar-controlled - shadcn/ui

A controlled sidebar.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export function AppSidebar() {
  const [open, setOpen] = React.useState(false)

  return (
    <SidebarProvider open={open} onOpenChange={setOpen}>
      <Sidebar />
    </SidebarProvider>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#theming) Theming

We use the following CSS variables to theme the sidebar.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
@layer base {
  :root {
    --sidebar-background: 0 0% 98%;
    --sidebar-foreground: 240 5.3% 26.1%;
    --sidebar-primary: 240 5.9% 10%;
    --sidebar-primary-foreground: 0 0% 98%;
    --sidebar-accent: 240 4.8% 95.9%;
    --sidebar-accent-foreground: 240 5.9% 10%;
    --sidebar-border: 220 13% 91%;
    --sidebar-ring: 217.2 91.2% 59.8%;
  }

  .dark {
    --sidebar-background: 240 5.9% 10%;
    --sidebar-foreground: 240 4.8% 95.9%;
    --sidebar-primary: 0 0% 98%;
    --sidebar-primary-foreground: 240 5.9% 10%;
    --sidebar-accent: 240 3.7% 15.9%;
    --sidebar-accent-foreground: 240 4.8% 95.9%;
    --sidebar-border: 240 3.7% 15.9%;
    --sidebar-ring: 217.2 91.2% 59.8%;
  }
}
```

Copy

**We intentionally use different variables for the sidebar and the rest of the application** to make it easy to have a sidebar that is styled differently from the rest of the application. Think a sidebar with a darker shade from the main application.

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#styling) Styling

Here are some tips for styling the sidebar based on different states.

- **Styling an element based on the sidebar collapsible state.** The following will hide the `SidebarGroup` when the sidebar is in `icon` mode.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Sidebar collapsible="icon">
  <SidebarContent>
    <SidebarGroup className="group-data-[collapsible=icon]:hidden" />
  </SidebarContent>
</Sidebar>
```

Copy

- **Styling a menu action based on the menu button active state.** The following will force the menu action to be visible when the menu button is active.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<SidebarMenuItem>
  <SidebarMenuButton />
  <SidebarMenuAction className="peer-data-[active=true]/menu-button:opacity-100" />
</SidebarMenuItem>
```

Copy

You can find more tips on using states for styling in this [Twitter thread](https://x.com/shadcn/status/1842329158879420864).

## [Link to section](https://ui.shadcn.com/docs/components/sidebar\#changelog) Changelog

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#2024-10-30-cookie-handling-in-setopen) 2024-10-30 Cookie handling in setOpen

- [#5593](https://github.com/shadcn-ui/ui/pull/5593) \- Improved setOpen callback logic in `<SidebarProvider>`.

Update the `setOpen` callback in `<SidebarProvider>` as follows:

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const setOpen = React.useCallback(
  (value: boolean | ((value: boolean) => boolean)) => {
    const openState = typeof value === "function" ? value(open) : value
    if (setOpenProp) {
      setOpenProp(openState)
    } else {
      _setOpen(openState)
    }

    // This sets the cookie to keep the sidebar state.
    document.cookie = `${SIDEBAR_COOKIE_NAME}=${openState}; path=/; max-age=${SIDEBAR_COOKIE_MAX_AGE}`
  },
  [setOpenProp, open]
)
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#2024-10-21-fixed-text-sidebar-foreground) 2024-10-21 Fixed `text-sidebar-foreground`

- [#5491](https://github.com/shadcn-ui/ui/pull/5491) \- Moved `text-sidebar-foreground` from `<SidebarProvider>` to `<Sidebar>` component.

### [Link to section](https://ui.shadcn.com/docs/components/sidebar\#2024-10-20-typo-in-usesidebar-hook) 2024-10-20 Typo in `useSidebar` hook.

Fixed typo in `useSidebar` hook.

sidebar.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
-  throw new Error("useSidebar must be used within a Sidebar.")
+  throw new Error("useSidebar must be used within a SidebarProvider.")
```

Copy

[Sheet](https://ui.shadcn.com/docs/components/sheet) [Skeleton](https://ui.shadcn.com/docs/components/skeleton)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/sidebar#installation)
- [Structure](https://ui.shadcn.com/docs/components/sidebar#structure)
- [Usage](https://ui.shadcn.com/docs/components/sidebar#usage)
- [Your First Sidebar](https://ui.shadcn.com/docs/components/sidebar#your-first-sidebar)
- [Components](https://ui.shadcn.com/docs/components/sidebar#components)
- [SidebarProvider](https://ui.shadcn.com/docs/components/sidebar#sidebarprovider)
  - [Props](https://ui.shadcn.com/docs/components/sidebar#props)
  - [Width](https://ui.shadcn.com/docs/components/sidebar#width)
  - [Keyboard Shortcut](https://ui.shadcn.com/docs/components/sidebar#keyboard-shortcut)
  - [Persisted State](https://ui.shadcn.com/docs/components/sidebar#persisted-state)
- [Sidebar](https://ui.shadcn.com/docs/components/sidebar#sidebar)
  - [Props](https://ui.shadcn.com/docs/components/sidebar#props-1)
  - [side](https://ui.shadcn.com/docs/components/sidebar#side)
  - [variant](https://ui.shadcn.com/docs/components/sidebar#variant)
  - [collapsible](https://ui.shadcn.com/docs/components/sidebar#collapsible)
- [useSidebar](https://ui.shadcn.com/docs/components/sidebar#usesidebar)
- [SidebarHeader](https://ui.shadcn.com/docs/components/sidebar#sidebarheader)
- [SidebarFooter](https://ui.shadcn.com/docs/components/sidebar#sidebarfooter)
- [SidebarContent](https://ui.shadcn.com/docs/components/sidebar#sidebarcontent)
- [SidebarGroup](https://ui.shadcn.com/docs/components/sidebar#sidebargroup)
- [Collapsible SidebarGroup](https://ui.shadcn.com/docs/components/sidebar#collapsible-sidebargroup)
- [SidebarGroupAction](https://ui.shadcn.com/docs/components/sidebar#sidebargroupaction)
- [SidebarMenu](https://ui.shadcn.com/docs/components/sidebar#sidebarmenu)
- [SidebarMenuButton](https://ui.shadcn.com/docs/components/sidebar#sidebarmenubutton)
  - [Link or Anchor](https://ui.shadcn.com/docs/components/sidebar#link-or-anchor)
  - [Icon and Label](https://ui.shadcn.com/docs/components/sidebar#icon-and-label)
  - [isActive](https://ui.shadcn.com/docs/components/sidebar#isactive)
- [SidebarMenuAction](https://ui.shadcn.com/docs/components/sidebar#sidebarmenuaction)
  - [DropdownMenu](https://ui.shadcn.com/docs/components/sidebar#dropdownmenu)
- [SidebarMenuSub](https://ui.shadcn.com/docs/components/sidebar#sidebarmenusub)
- [Collapsible SidebarMenu](https://ui.shadcn.com/docs/components/sidebar#collapsible-sidebarmenu)
- [SidebarMenuBadge](https://ui.shadcn.com/docs/components/sidebar#sidebarmenubadge)
- [SidebarMenuSkeleton](https://ui.shadcn.com/docs/components/sidebar#sidebarmenuskeleton)
- [SidebarSeparator](https://ui.shadcn.com/docs/components/sidebar#sidebarseparator)
- [SidebarTrigger](https://ui.shadcn.com/docs/components/sidebar#sidebartrigger)
  - [Custom Trigger](https://ui.shadcn.com/docs/components/sidebar#custom-trigger)
- [SidebarRail](https://ui.shadcn.com/docs/components/sidebar#sidebarrail)
- [Data Fetching](https://ui.shadcn.com/docs/components/sidebar#data-fetching)
  - [React Server Components](https://ui.shadcn.com/docs/components/sidebar#react-server-components)
  - [SWR and React Query](https://ui.shadcn.com/docs/components/sidebar#swr-and-react-query)
- [Controlled Sidebar](https://ui.shadcn.com/docs/components/sidebar#controlled-sidebar)
- [Theming](https://ui.shadcn.com/docs/components/sidebar#theming)
- [Styling](https://ui.shadcn.com/docs/components/sidebar#styling)
- [Changelog](https://ui.shadcn.com/docs/components/sidebar#changelog)
  - [2024-10-30 Cookie handling in setOpen](https://ui.shadcn.com/docs/components/sidebar#2024-10-30-cookie-handling-in-setopen)
  - [2024-10-21 Fixed text-sidebar-foreground](https://ui.shadcn.com/docs/components/sidebar#2024-10-21-fixed-text-sidebar-foreground)
  - [2024-10-20 Typo in useSidebar hook.](https://ui.shadcn.com/docs/components/sidebar#2024-10-20-typo-in-usesidebar-hook)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Input Field Documentation
[Docs](https://ui.shadcn.com/docs)

Input

# Input

Displays a form input field or a component that looks like an input field.

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/input\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add input

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/input\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Input } from "@/components/ui/input"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Input />
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/input\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/input\#default) Default

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/input\#file) File

PreviewCode

Style: New York

Open in Copy

Picture

### [Link to section](https://ui.shadcn.com/docs/components/input\#disabled) Disabled

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/input\#with-label) With Label

PreviewCode

Style: New York

Open in Copy

Email

### [Link to section](https://ui.shadcn.com/docs/components/input\#with-button) With Button

PreviewCode

Style: New York

Open in Copy

Subscribe

### [Link to section](https://ui.shadcn.com/docs/components/input\#form) Form

PreviewCode

Style: New York

Copy

Username

This is your public display name.

Submit

[Hover Card](https://ui.shadcn.com/docs/components/hover-card) [Input OTP](https://ui.shadcn.com/docs/components/input-otp)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/input#installation)
- [Usage](https://ui.shadcn.com/docs/components/input#usage)
- [Examples](https://ui.shadcn.com/docs/components/input#examples)
  - [Default](https://ui.shadcn.com/docs/components/input#default)
  - [File](https://ui.shadcn.com/docs/components/input#file)
  - [Disabled](https://ui.shadcn.com/docs/components/input#disabled)
  - [With Label](https://ui.shadcn.com/docs/components/input#with-label)
  - [With Button](https://ui.shadcn.com/docs/components/input#with-button)
  - [Form](https://ui.shadcn.com/docs/components/input#form)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Toggle Component
[Docs](https://ui.shadcn.com/docs)

Toggle

# Toggle

A two-state button that can be either on or off.

[Docs](https://www.radix-ui.com/docs/primitives/components/toggle) [API Reference](https://www.radix-ui.com/docs/primitives/components/toggle#api-reference)

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/toggle\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add toggle

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/toggle\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Toggle } from "@/components/ui/toggle"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Toggle>Toggle</Toggle>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/toggle\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/toggle\#default) Default

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/toggle\#outline) Outline

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/toggle\#with-text) With Text

PreviewCode

Style: New York

Open in Copy

Italic

### [Link to section](https://ui.shadcn.com/docs/components/toggle\#small) Small

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/toggle\#large) Large

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/toggle\#disabled) Disabled

PreviewCode

Style: New York

Open in Copy

[Toast](https://ui.shadcn.com/docs/components/toast) [Toggle Group](https://ui.shadcn.com/docs/components/toggle-group)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/toggle#installation)
- [Usage](https://ui.shadcn.com/docs/components/toggle#usage)
- [Examples](https://ui.shadcn.com/docs/components/toggle#examples)
  - [Default](https://ui.shadcn.com/docs/components/toggle#default)
  - [Outline](https://ui.shadcn.com/docs/components/toggle#outline)
  - [With Text](https://ui.shadcn.com/docs/components/toggle#with-text)
  - [Small](https://ui.shadcn.com/docs/components/toggle#small)
  - [Large](https://ui.shadcn.com/docs/components/toggle#large)
  - [Disabled](https://ui.shadcn.com/docs/components/toggle#disabled)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Calendar Component
[Docs](https://ui.shadcn.com/docs)

Calendar

# Calendar

A date field component that allows users to enter and edit date.

[Docs](https://react-day-picker.js.org/)

PreviewCode

Style: New York

Open in Copy

March 2025

| Su | Mo | Tu | We | Th | Fr | Sa |
| --- | --- | --- | --- | --- | --- | --- |
| 23 | 24 | 25 | 26 | 27 | 28 | 1 |
| 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| 16 | 17 | 18 | 19 | 20 | 21 | 22 |
| 23 | 24 | 25 | 26 | 27 | 28 | 29 |
| 30 | 31 | 1 | 2 | 3 | 4 | 5 |

## [Link to section](https://ui.shadcn.com/docs/components/calendar\#about) About

The `Calendar` component is built on top of [React DayPicker](https://react-day-picker.js.org/).

## [Link to section](https://ui.shadcn.com/docs/components/calendar\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add calendar

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/calendar\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Calendar } from "@/components/ui/calendar"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const [date, setDate] = React.useState<Date | undefined>(new Date())

return (
  <Calendar
    mode="single"
    selected={date}
    onSelect={setDate}
    className="rounded-md border"
  />
)
```

Copy

See the [React DayPicker](https://react-day-picker.js.org/) documentation for more information.

## [Link to section](https://ui.shadcn.com/docs/components/calendar\#date-picker) Date Picker

You can use the `<Calendar>` component to build a date picker. See the [Date Picker](https://ui.shadcn.com/docs/components/date-picker) page for more information.

## [Link to section](https://ui.shadcn.com/docs/components/calendar\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/calendar\#form) Form

PreviewCode

Style: New York

Copy

Date of birthPick a date

Your date of birth is used to calculate your age.

Submit

## [Link to section](https://ui.shadcn.com/docs/components/calendar\#changelog) Changelog

### [Link to section](https://ui.shadcn.com/docs/components/calendar\#11-03-2024-day_outside-color) 11-03-2024 day\_outside color

- Changed the color of the `day_outside` class to the following to improve contrast:



calendar.tsx



```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"day_outside:
        "day-outside text-muted-foreground aria-selected:bg-accent/50 aria-selected:text-muted-foreground",
```

Copy


[Button](https://ui.shadcn.com/docs/components/button) [Card](https://ui.shadcn.com/docs/components/card)

On This Page

- [About](https://ui.shadcn.com/docs/components/calendar#about)
- [Installation](https://ui.shadcn.com/docs/components/calendar#installation)
- [Usage](https://ui.shadcn.com/docs/components/calendar#usage)
- [Date Picker](https://ui.shadcn.com/docs/components/calendar#date-picker)
- [Examples](https://ui.shadcn.com/docs/components/calendar#examples)
  - [Form](https://ui.shadcn.com/docs/components/calendar#form)
- [Changelog](https://ui.shadcn.com/docs/components/calendar#changelog)
  - [11-03-2024 day\_outside color](https://ui.shadcn.com/docs/components/calendar#11-03-2024-day_outside-color)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Breadcrumb Component Guide
[Docs](https://ui.shadcn.com/docs)

Breadcrumb

# Breadcrumb

Displays the path to the current resource using a hierarchy of links.

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/breadcrumb\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add breadcrumb

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/breadcrumb\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbLink href="/components">Components</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbPage>Breadcrumb</BreadcrumbPage>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/breadcrumb\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/breadcrumb\#custom-separator) Custom separator

Use a custom component as `children` for `<BreadcrumbSeparator />` to create a custom separator.

PreviewCode

Style: New York

Open in Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Slash } from "lucide-react"

...

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator>
      <Slash />
    </BreadcrumbSeparator>
    <BreadcrumbItem>
      <BreadcrumbLink href="/components">Components</BreadcrumbLink>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

Copy

* * *

### [Link to section](https://ui.shadcn.com/docs/components/breadcrumb\#dropdown) Dropdown

You can compose `<BreadcrumbItem />` with a `<DropdownMenu />` to create a dropdown in the breadcrumb.

PreviewCode

Style: New York

Open in Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

...

<BreadcrumbItem>
  <DropdownMenu>
    <DropdownMenuTrigger className="flex items-center gap-1">
      Components
      <ChevronDownIcon />
    </DropdownMenuTrigger>
    <DropdownMenuContent align="start">
      <DropdownMenuItem>Documentation</DropdownMenuItem>
      <DropdownMenuItem>Themes</DropdownMenuItem>
      <DropdownMenuItem>GitHub</DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</BreadcrumbItem>
```

Copy

* * *

### [Link to section](https://ui.shadcn.com/docs/components/breadcrumb\#collapsed) Collapsed

We provide a `<BreadcrumbEllipsis />` component to show a collapsed state when the breadcrumb is too long.

PreviewCode

Style: New York

Open in Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { BreadcrumbEllipsis } from "@/components/ui/breadcrumb"

...

<Breadcrumb>
  <BreadcrumbList>
    {/* ... */}
    <BreadcrumbItem>
      <BreadcrumbEllipsis />
    </BreadcrumbItem>
    {/* ... */}
  </BreadcrumbList>
</Breadcrumb>
```

Copy

* * *

### [Link to section](https://ui.shadcn.com/docs/components/breadcrumb\#link-component) Link component

To use a custom link component from your routing library, you can use the `asChild` prop on `<BreadcrumbLink />`.

PreviewCode

Style: New York

Open in Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Link } from "next/link"

...

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink asChild>
        <Link href="/">Home</Link>
      </BreadcrumbLink>
    </BreadcrumbItem>
    {/* ... */}
  </BreadcrumbList>
</Breadcrumb>
```

Copy

* * *

### [Link to section](https://ui.shadcn.com/docs/components/breadcrumb\#responsive) Responsive

Here's an example of a responsive breadcrumb that composes `<BreadcrumbItem />` with `<BreadcrumbEllipsis />`, `<DropdownMenu />`, and `<Drawer />`.

It displays a dropdown on desktop and a drawer on mobile.

PreviewCode

Style: New York

Open in Copy

[Badge](https://ui.shadcn.com/docs/components/badge) [Button](https://ui.shadcn.com/docs/components/button)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/breadcrumb#installation)
- [Usage](https://ui.shadcn.com/docs/components/breadcrumb#usage)
- [Examples](https://ui.shadcn.com/docs/components/breadcrumb#examples)
  - [Custom separator](https://ui.shadcn.com/docs/components/breadcrumb#custom-separator)
  - [Dropdown](https://ui.shadcn.com/docs/components/breadcrumb#dropdown)
  - [Collapsed](https://ui.shadcn.com/docs/components/breadcrumb#collapsed)
  - [Link component](https://ui.shadcn.com/docs/components/breadcrumb#link-component)
  - [Responsive](https://ui.shadcn.com/docs/components/breadcrumb#responsive)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Sheet Component Overview
[Docs](https://ui.shadcn.com/docs)

Sheet

# Sheet

Extends the Dialog component to display content that complements the main content of the screen.

[Docs](https://www.radix-ui.com/docs/primitives/components/dialog) [API Reference](https://www.radix-ui.com/docs/primitives/components/dialog#api-reference)

PreviewCode

Style: New York

Open in Copy

Open

## [Link to section](https://ui.shadcn.com/docs/components/sheet\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add sheet

```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/sheet\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Sheet>
  <SheetTrigger>Open</SheetTrigger>
  <SheetContent>
    <SheetHeader>
      <SheetTitle>Are you absolutely sure?</SheetTitle>
      <SheetDescription>
        This action cannot be undone. This will permanently delete your account
        and remove your data from our servers.
      </SheetDescription>
    </SheetHeader>
  </SheetContent>
</Sheet>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sheet\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/sheet\#side) Side

Use the `side` property to `<SheetContent />` to indicate the edge of the screen where the component will appear. The values can be `top`, `right`, `bottom` or `left`.

PreviewCode

Style: New York

Copy

toprightbottomleft

### [Link to section](https://ui.shadcn.com/docs/components/sheet\#size) Size

You can adjust the size of the sheet using CSS classes:

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Sheet>
  <SheetTrigger>Open</SheetTrigger>
  <SheetContent className="w-[400px] sm:w-[540px]">
    <SheetHeader>
      <SheetTitle>Are you absolutely sure?</SheetTitle>
      <SheetDescription>
        This action cannot be undone. This will permanently delete your account
        and remove your data from our servers.
      </SheetDescription>
    </SheetHeader>
  </SheetContent>
</Sheet>
```

Copy

[Separator](https://ui.shadcn.com/docs/components/separator) [Sidebar](https://ui.shadcn.com/docs/components/sidebar)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/sheet#installation)
  - [Usage](https://ui.shadcn.com/docs/components/sheet#usage)
- [Examples](https://ui.shadcn.com/docs/components/sheet#examples)
  - [Side](https://ui.shadcn.com/docs/components/sheet#side)
  - [Size](https://ui.shadcn.com/docs/components/sheet#size)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Combobox Component
[Docs](https://ui.shadcn.com/docs)

Combobox

# Combobox

Autocomplete input and command palette with a list of suggestions.

PreviewCode

Style: New York

Open in Copy

Select framework...

## [Link to section](https://ui.shadcn.com/docs/components/combobox\#installation) Installation

The Combobox is built using a composition of the `<Popover />` and the `<Command />` components.

See installation instructions for the [Popover](https://ui.shadcn.com/docs/components/popover#installation) and the [Command](https://ui.shadcn.com/docs/components/command#installation) components.

## [Link to section](https://ui.shadcn.com/docs/components/combobox\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

const frameworks = [\
  {\
    value: "next.js",\
    label: "Next.js",\
  },\
  {\
    value: "sveltekit",\
    label: "SvelteKit",\
  },\
  {\
    value: "nuxt.js",\
    label: "Nuxt.js",\
  },\
  {\
    value: "remix",\
    label: "Remix",\
  },\
  {\
    value: "astro",\
    label: "Astro",\
  },\
]

export function ComboboxDemo() {
  const [open, setOpen] = React.useState(false)
  const [value, setValue] = React.useState("")

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[200px] justify-between"
        >
          {value
            ? frameworks.find((framework) => framework.value === value)?.label
            : "Select framework..."}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder="Search framework..." />
          <CommandList>
            <CommandEmpty>No framework found.</CommandEmpty>
            <CommandGroup>
              {frameworks.map((framework) => (
                <CommandItem
                  key={framework.value}
                  value={framework.value}
                  onSelect={(currentValue) => {
                    setValue(currentValue === value ? "" : currentValue)
                    setOpen(false)
                  }}
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      value === framework.value ? "opacity-100" : "opacity-0"
                    )}
                  />
                  {framework.label}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/combobox\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/combobox\#combobox) Combobox

PreviewCode

Style: New York

Open in Copy

Select framework...

### [Link to section](https://ui.shadcn.com/docs/components/combobox\#popover) Popover

PreviewCode

Style: New York

Copy

Status

\+ Set status

### [Link to section](https://ui.shadcn.com/docs/components/combobox\#dropdown-menu) Dropdown menu

PreviewCode

Style: New York

Open in Copy

featureCreate a new project

### [Link to section](https://ui.shadcn.com/docs/components/combobox\#responsive) Responsive

You can create a responsive combobox by using the `<Popover />` on desktop and the `<Drawer />` components on mobile.

PreviewCode

Style: New York

Copy

\+ Set status

### [Link to section](https://ui.shadcn.com/docs/components/combobox\#form) Form

PreviewCode

Style: New York

Copy

LanguageSelect language

This is the language that will be used in the dashboard.

Submit

[Collapsible](https://ui.shadcn.com/docs/components/collapsible) [Command](https://ui.shadcn.com/docs/components/command)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/combobox#installation)
- [Usage](https://ui.shadcn.com/docs/components/combobox#usage)
- [Examples](https://ui.shadcn.com/docs/components/combobox#examples)
  - [Combobox](https://ui.shadcn.com/docs/components/combobox#combobox)
  - [Popover](https://ui.shadcn.com/docs/components/combobox#popover)
  - [Dropdown menu](https://ui.shadcn.com/docs/components/combobox#dropdown-menu)
  - [Responsive](https://ui.shadcn.com/docs/components/combobox#responsive)
  - [Form](https://ui.shadcn.com/docs/components/combobox#form)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Textarea Component Guide
[Docs](https://ui.shadcn.com/docs)

Textarea

# Textarea

Displays a form textarea or a component that looks like a textarea.

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/textarea\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add textarea

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/textarea\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Textarea } from "@/components/ui/textarea"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Textarea />
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/textarea\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/textarea\#default) Default

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/textarea\#disabled) Disabled

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/textarea\#with-label) With Label

PreviewCode

Style: New York

Open in Copy

Your message

### [Link to section](https://ui.shadcn.com/docs/components/textarea\#with-text) With Text

PreviewCode

Style: New York

Open in Copy

Your Message

Your message will be copied to the support team.

### [Link to section](https://ui.shadcn.com/docs/components/textarea\#with-button) With Button

PreviewCode

Style: New York

Open in Copy

Send message

### [Link to section](https://ui.shadcn.com/docs/components/textarea\#form) Form

PreviewCode

Style: New York

Copy

Bio

You can @mention other users and organizations.

Submit

[Tabs](https://ui.shadcn.com/docs/components/tabs) [Toast](https://ui.shadcn.com/docs/components/toast)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/textarea#installation)
- [Usage](https://ui.shadcn.com/docs/components/textarea#usage)
- [Examples](https://ui.shadcn.com/docs/components/textarea#examples)
  - [Default](https://ui.shadcn.com/docs/components/textarea#default)
  - [Disabled](https://ui.shadcn.com/docs/components/textarea#disabled)
  - [With Label](https://ui.shadcn.com/docs/components/textarea#with-label)
  - [With Text](https://ui.shadcn.com/docs/components/textarea#with-text)
  - [With Button](https://ui.shadcn.com/docs/components/textarea#with-button)
  - [Form](https://ui.shadcn.com/docs/components/textarea#form)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Interactive Chart Components
[Docs](https://ui.shadcn.com/docs)

Chart

# Chart

Beautiful charts. Built using Recharts. Copy and paste into your apps.

**Note:** If you are using charts with **React 19** or the **Next.js 15**, see the note [here](https://ui.shadcn.com/docs/react-19#recharts).

Style: New York

Copy

Bar Chart - Interactive

Showing total visitors for the last 3 months

Desktop24,828Mobile25,010

Introducing **Charts**. A collection of chart components that you can copy and paste into your apps.

Charts are designed to look great out of the box. They work well with the other components and are fully customizable to fit your project.

[Browse the Charts Library](https://ui.shadcn.com/charts).

## [Link to section](https://ui.shadcn.com/docs/components/chart\#component) Component

We use [Recharts](https://recharts.org/) under the hood.

We designed the `chart` component with composition in mind. **You build your charts using Recharts components and only bring in custom components, such as `ChartTooltip`, when and where you need it**.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Bar, BarChart } from "recharts"

import { ChartContainer, ChartTooltipContent } from "@/components/ui/charts"

export function MyChart() {
  return (
    <ChartContainer>
      <BarChart data={data}>
        <Bar dataKey="value" />
        <ChartTooltip content={<ChartTooltipContent />} />
      </BarChart>
    </ChartContainer>
  )
}
```

Copy

We do not wrap Recharts. This means you're not locked into an abstraction. When a new Recharts version is released, you can follow the official upgrade path to upgrade your charts.

**The components are yours**.

## [Link to section](https://ui.shadcn.com/docs/components/chart\#installation) Installation

**Note:** If you are using charts with **React 19** or the **Next.js 15**, see the note [here](https://ui.shadcn.com/docs/react-19#recharts).

CLIManual

### Run the following command to install `chart.tsx`

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add chart

```

Copy

### Add the following colors to your CSS file

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
@layer base {
  :root {
    --chart-1: 12 76% 61%;
    --chart-2: 173 58% 39%;
    --chart-3: 197 37% 24%;
    --chart-4: 43 74% 66%;
    --chart-5: 27 87% 67%;
  }

  .dark {
    --chart-1: 220 70% 50%;
    --chart-2: 160 60% 45%;
    --chart-3: 30 80% 55%;
    --chart-4: 280 65% 60%;
    --chart-5: 340 75% 55%;
  }
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/chart\#your-first-chart) Your First Chart

Let's build your first chart. We'll build a bar chart, add a grid, axis, tooltip and legend.

### Start by defining your data

The following data represents the number of desktop and mobile users for each month.

**Note:** Your data can be in any shape. You are not limited to the shape of the data below. Use the `dataKey` prop to map your data to the chart.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const chartData = [\
  { month: "January", desktop: 186, mobile: 80 },\
  { month: "February", desktop: 305, mobile: 200 },\
  { month: "March", desktop: 237, mobile: 120 },\
  { month: "April", desktop: 73, mobile: 190 },\
  { month: "May", desktop: 209, mobile: 130 },\
  { month: "June", desktop: 214, mobile: 140 },\
]
```

Copy

### Define your chart config

The chart config holds configuration for the chart. This is where you place human-readable strings, such as labels, icons and color tokens for theming.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { type ChartConfig } from "@/components/ui/chart"

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#2563eb",
  },
  mobile: {
    label: "Mobile",
    color: "#60a5fa",
  },
} satisfies ChartConfig
```

Copy

### Build your chart

You can now build your chart using Recharts components.

**Important:** Remember to set a `min-h-[VALUE]` on the `ChartContainer` component. This is required for the chart be responsive.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { Bar, BarChart } from "recharts"

import { ChartConfig, ChartContainer } from "@/components/ui/chart"

const chartData = [\
  { month: "January", desktop: 186, mobile: 80 },\
  { month: "February", desktop: 305, mobile: 200 },\
  { month: "March", desktop: 237, mobile: 120 },\
  { month: "April", desktop: 73, mobile: 190 },\
  { month: "May", desktop: 209, mobile: 130 },\
  { month: "June", desktop: 214, mobile: 140 },\
]

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#2563eb",
  },
  mobile: {
    label: "Mobile",
    color: "#60a5fa",
  },
} satisfies ChartConfig

export function Component() {
  return (
    <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
      <BarChart accessibilityLayer data={chartData}>
        <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
        <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
      </BarChart>
    </ChartContainer>
  )
}
```

Copy

Expand

PreviewCode

Style: New York

Copy

### [Link to section](https://ui.shadcn.com/docs/components/chart\#add-a-grid) Add a Grid

Let's add a grid to the chart.

### Import the `CartesianGrid` component.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Bar, BarChart, CartesianGrid } from "recharts"
```

Copy

### Add the `CartesianGrid` component to your chart.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ChartContainer config={chartConfig} className="min-h-[200px] w-full">
  <BarChart accessibilityLayer data={chartData}>
    <CartesianGrid vertical={false} />
    <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
    <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
  </BarChart>
</ChartContainer>
```

Copy

PreviewCode

Style: New York

Copy

### [Link to section](https://ui.shadcn.com/docs/components/chart\#add-an-axis) Add an Axis

To add an x-axis to the chart, we'll use the `XAxis` component.

### Import the `XAxis` component.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"
```

Copy

### Add the `XAxis` component to your chart.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ChartContainer config={chartConfig} className="h-[200px] w-full">
  <BarChart accessibilityLayer data={chartData}>
    <CartesianGrid vertical={false} />
    <XAxis
      dataKey="month"
      tickLine={false}
      tickMargin={10}
      axisLine={false}
      tickFormatter={(value) => value.slice(0, 3)}
    />
    <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
    <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
  </BarChart>
</ChartContainer>
```

Copy

PreviewCode

Style: New York

Copy

### [Link to section](https://ui.shadcn.com/docs/components/chart\#add-tooltip) Add Tooltip

So far we've only used components from Recharts. They look great out of the box thanks to some customization in the `chart` component.

To add a tooltip, we'll use the custom `ChartTooltip` and `ChartTooltipContent` components from `chart`.

### Import the `ChartTooltip` and `ChartTooltipContent` components.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
```

Copy

### Add the components to your chart.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ChartContainer config={chartConfig} className="h-[200px] w-full">
  <BarChart accessibilityLayer data={chartData}>
    <CartesianGrid vertical={false} />
    <XAxis
      dataKey="month"
      tickLine={false}
      tickMargin={10}
      axisLine={false}
      tickFormatter={(value) => value.slice(0, 3)}
    />
    <ChartTooltip content={<ChartTooltipContent />} />
    <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
    <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
  </BarChart>
</ChartContainer>
```

Copy

PreviewCode

Style: New York

Copy

Hover to see the tooltips. Easy, right? Two components, and we've got a beautiful tooltip.

### [Link to section](https://ui.shadcn.com/docs/components/chart\#add-legend) Add Legend

We'll do the same for the legend. We'll use the `ChartLegend` and `ChartLegendContent` components from `chart`.

### Import the `ChartLegend` and `ChartLegendContent` components.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { ChartLegend, ChartLegendContent } from "@/components/ui/chart"
```

Copy

### Add the components to your chart.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ChartContainer config={chartConfig} className="h-[200px] w-full">
  <BarChart accessibilityLayer data={chartData}>
    <CartesianGrid vertical={false} />
    <XAxis
      dataKey="month"
      tickLine={false}
      tickMargin={10}
      axisLine={false}
      tickFormatter={(value) => value.slice(0, 3)}
    />
    <ChartTooltip content={<ChartTooltipContent />} />
    <ChartLegend content={<ChartLegendContent />} />
    <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
    <Bar dataKey="mobile" fill="var(--color-mobile)" radius={4} />
  </BarChart>
</ChartContainer>
```

Copy

PreviewCode

Style: New York

Copy

Done. You've built your first chart! What's next?

- [Themes and Colors](https://ui.shadcn.com/docs/components/chart#theming)
- [Tooltip](https://ui.shadcn.com/docs/components/chart#tooltip)
- [Legend](https://ui.shadcn.com/docs/components/chart#legend)

## [Link to section](https://ui.shadcn.com/docs/components/chart\#chart-config) Chart Config

The chart config is where you define the labels, icons and colors for a chart.

It is intentionally decoupled from chart data.

This allows you to share config and color tokens between charts. It can also works independently for cases where your data or color tokens live remotely or in a different format.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Monitor } from "lucide-react"

import { type ChartConfig } from "@/components/ui/chart"

const chartConfig = {
  desktop: {
    label: "Desktop",
    icon: Monitor,
    // A color like 'hsl(220, 98%, 61%)' or 'var(--color-name)'
    color: "#2563eb",
    // OR a theme object with 'light' and 'dark' keys
    theme: {
      light: "#2563eb",
      dark: "#dc2626",
    },
  },
} satisfies ChartConfig
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/chart\#theming) Theming

Charts has built-in support for theming. You can use css variables (recommended) or color values in any color format, such as hex, hsl or oklch.

### [Link to section](https://ui.shadcn.com/docs/components/chart\#css-variables) CSS Variables

### Define your colors in your css file

globals.css

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    // ...
    --chart-1: 12 76% 61%;
    --chart-2: 173 58% 39%;
  }

  .dark: {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 100%;
    // ...
    --chart-1: 220 70% 50%;
    --chart-2: 160 60% 45%;
  }
}
```

Copy

### Add the color to your `chartConfig`

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "hsl(var(--chart-1))",
  },
  mobile: {
    label: "Mobile",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig
```

Copy

We're wrapping the value in `hsl()` here because we define the colors without color space function.

This is not required. You can use full color values, such as hex, hsl or oklch.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
--chart-1: oklch(70% 0.227 154.59);
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
color: "var(--chart-1)",
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/chart\#hex-hsl-or-oklch) hex, hsl or oklch

You can also define your colors directly in the chart config. Use the color format you prefer.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#2563eb",
  },
} satisfies ChartConfig
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/chart\#using-colors) Using Colors

To use the theme colors in your chart, reference the colors using the format `var(--color-KEY)`.

#### [Link to section](https://ui.shadcn.com/docs/components/chart\#components) Components

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Bar dataKey="desktop" fill="var(--color-desktop)" />
```

Copy

#### [Link to section](https://ui.shadcn.com/docs/components/chart\#chart-data) Chart Data

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const chartData = [\
  { browser: "chrome", visitors: 275, fill: "var(--color-chrome)" },\
  { browser: "safari", visitors: 200, fill: "var(--color-safari)" },\
]
```

Copy

#### [Link to section](https://ui.shadcn.com/docs/components/chart\#tailwind) Tailwind

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<LabelList className="fill-[--color-desktop]" />
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/chart\#tooltip) Tooltip

A chart tooltip contains a label, name, indicator and value. You can use a combination of these to customize your tooltip.

Style: New York

Copy

Label

Page Views

Desktop

186

Mobile

80

Name

Chrome

1,286

Firefox

1,000

Page Views

Desktop

12,486

Indicator

Chrome

1,286

You can turn on/off any of these using the `hideLabel`, `hideIndicator` props and customize the indicator style using the `indicator` prop.

Use `labelKey` and `nameKey` to use a custom key for the tooltip label and name.

Chart comes with the `<ChartTooltip>` and `<ChartTooltipContent>` components. You can use these two components to add custom tooltips to your chart.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ChartTooltip content={<ChartTooltipContent />} />
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/chart\#props) Props

Use the following props to customize the tooltip.

| Prop | Type | Description |
| --- | --- | --- |
| `labelKey` | string | The config or data key to use for the label. |
| `nameKey` | string | The config or data key to use for the name. |
| `indicator` | `dot` `line` or `dashed` | The indicator style for the tooltip. |
| `hideLabel` | boolean | Whether to hide the label. |
| `hideIndicator` | boolean | Whether to hide the indicator. |

### [Link to section](https://ui.shadcn.com/docs/components/chart\#colors) Colors

Colors are automatically referenced from the chart config.

### [Link to section](https://ui.shadcn.com/docs/components/chart\#custom) Custom

To use a custom key for tooltip label and names, use the `labelKey` and `nameKey` props.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const chartData = [\
  { browser: "chrome", visitors: 187, fill: "var(--color-chrome)" },\
  { browser: "safari", visitors: 200, fill: "var(--color-safari)" },\
]

const chartConfig = {
  visitors: {
    label: "Total Visitors",
  },
  chrome: {
    label: "Chrome",
    color: "hsl(var(--chart-1))",
  },
  safari: {
    label: "Safari",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ChartTooltip
  content={<ChartTooltipContent labelKey="visitors" nameKey="browser" />}
/>
```

Copy

This will use `Total Visitors` for label and `Chrome` and `Safari` for the tooltip names.

## [Link to section](https://ui.shadcn.com/docs/components/chart\#legend) Legend

You can use the custom `<ChartLegend>` and `<ChartLegendContent>` components to add a legend to your chart.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { ChartLegend, ChartLegendContent } from "@/components/ui/chart"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ChartLegend content={<ChartLegendContent />} />
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/chart\#colors-1) Colors

Colors are automatically referenced from the chart config.

### [Link to section](https://ui.shadcn.com/docs/components/chart\#custom-1) Custom

To use a custom key for legend names, use the `nameKey` prop.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const chartData = [\
  { browser: "chrome", visitors: 187, fill: "var(--color-chrome)" },\
  { browser: "safari", visitors: 200, fill: "var(--color-safari)" },\
]

const chartConfig = {
  chrome: {
    label: "Chrome",
    color: "hsl(var(--chart-1))",
  },
  safari: {
    label: "Safari",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ChartLegend content={<ChartLegendContent nameKey="browser" />} />
```

Copy

This will use `Chrome` and `Safari` for the legend names.

## [Link to section](https://ui.shadcn.com/docs/components/chart\#accessibility) Accessibility

You can turn on the `accessibilityLayer` prop to add an accessible layer to your chart.

This prop adds keyboard access and screen reader support to your charts.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<LineChart accessibilityLayer />
```

Copy

[Carousel](https://ui.shadcn.com/docs/components/carousel) [Checkbox](https://ui.shadcn.com/docs/components/checkbox)

On This Page

- [Component](https://ui.shadcn.com/docs/components/chart#component)
- [Installation](https://ui.shadcn.com/docs/components/chart#installation)
- [Your First Chart](https://ui.shadcn.com/docs/components/chart#your-first-chart)
  - [Add a Grid](https://ui.shadcn.com/docs/components/chart#add-a-grid)
  - [Add an Axis](https://ui.shadcn.com/docs/components/chart#add-an-axis)
  - [Add Tooltip](https://ui.shadcn.com/docs/components/chart#add-tooltip)
  - [Add Legend](https://ui.shadcn.com/docs/components/chart#add-legend)
- [Chart Config](https://ui.shadcn.com/docs/components/chart#chart-config)
- [Theming](https://ui.shadcn.com/docs/components/chart#theming)
  - [CSS Variables](https://ui.shadcn.com/docs/components/chart#css-variables)
  - [hex, hsl or oklch](https://ui.shadcn.com/docs/components/chart#hex-hsl-or-oklch)
  - [Using Colors](https://ui.shadcn.com/docs/components/chart#using-colors)
- [Tooltip](https://ui.shadcn.com/docs/components/chart#tooltip)
  - [Props](https://ui.shadcn.com/docs/components/chart#props)
  - [Colors](https://ui.shadcn.com/docs/components/chart#colors)
  - [Custom](https://ui.shadcn.com/docs/components/chart#custom)
- [Legend](https://ui.shadcn.com/docs/components/chart#legend)
  - [Colors](https://ui.shadcn.com/docs/components/chart#colors-1)
  - [Custom](https://ui.shadcn.com/docs/components/chart#custom-1)
- [Accessibility](https://ui.shadcn.com/docs/components/chart#accessibility)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Card Component Documentation
[Docs](https://ui.shadcn.com/docs)

Card

# Card

Displays a card with header, content, and footer.

PreviewCode

Style: New York

Open in Copy

Create project

Deploy your new project in one-click.

Name

FrameworkSelectNext.jsSvelteKitAstroNuxt.js

CancelDeploy

## [Link to section](https://ui.shadcn.com/docs/components/card\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add card

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/card\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card Description</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card Content</p>
  </CardContent>
  <CardFooter>
    <p>Card Footer</p>
  </CardFooter>
</Card>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/card\#examples) Examples

PreviewCode

Style: New York

Open in Copy

Notifications

You have 3 unread messages.

Push Notifications

Send notifications to device.

Your call has been confirmed.

1 hour ago

You have a new message!

1 hour ago

Your subscription is expiring soon!

2 hours ago

Mark all as read

## [Link to section](https://ui.shadcn.com/docs/components/card\#changelog) Changelog

### [Link to section](https://ui.shadcn.com/docs/components/card\#11-03-2024-a11y-for-title-and-description) 11-03-2024 a11y for title and description

- Changed the `CardTitle` and `CardDescription` components to use `div` instead of `h3` and `p` to improve accessibility.

card.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const CardTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("font-semibold leading-none tracking-tight", className)}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"
```

Copy

[Calendar](https://ui.shadcn.com/docs/components/calendar) [Carousel](https://ui.shadcn.com/docs/components/carousel)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/card#installation)
- [Usage](https://ui.shadcn.com/docs/components/card#usage)
- [Examples](https://ui.shadcn.com/docs/components/card#examples)
- [Changelog](https://ui.shadcn.com/docs/components/card#changelog)
  - [11-03-2024 a11y for title and description](https://ui.shadcn.com/docs/components/card#11-03-2024-a11y-for-title-and-description)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Select Component
[Docs](https://ui.shadcn.com/docs)

Select

# Select

Displays a list of options for the user to pick from—triggered by a button.

[Docs](https://www.radix-ui.com/docs/primitives/components/select) [API Reference](https://www.radix-ui.com/docs/primitives/components/select#api-reference)

PreviewCode

Style: New York

Open in Copy

Select a fruit

## [Link to section](https://ui.shadcn.com/docs/components/select\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add select

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/select\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Select>
  <SelectTrigger className="w-[180px]">
    <SelectValue placeholder="Theme" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="light">Light</SelectItem>
    <SelectItem value="dark">Dark</SelectItem>
    <SelectItem value="system">System</SelectItem>
  </SelectContent>
</Select>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/select\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/select\#scrollable) Scrollable

PreviewCode

Style: New York

Open in Copy

Select a timezone

### [Link to section](https://ui.shadcn.com/docs/components/select\#form) Form

PreviewCode

Style: New York

Copy

EmailSelect a verified email to displaym@example.comm@google.comm@support.com

You can manage email addresses in your [email settings](https://ui.shadcn.com/examples/forms).

Submit

[Scroll Area](https://ui.shadcn.com/docs/components/scroll-area) [Separator](https://ui.shadcn.com/docs/components/separator)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/select#installation)
- [Usage](https://ui.shadcn.com/docs/components/select#usage)
- [Examples](https://ui.shadcn.com/docs/components/select#examples)
  - [Scrollable](https://ui.shadcn.com/docs/components/select#scrollable)
  - [Form](https://ui.shadcn.com/docs/components/select#form)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## React Hook Form Guide
[Docs](https://ui.shadcn.com/docs)

React Hook Form

# React Hook Form

Building forms with React Hook Form and Zod.

[Docs](https://react-hook-form.com/)

Forms are tricky. They are one of the most common things you'll build in a web application, but also one of the most complex.

Well-designed HTML forms are:

- Well-structured and semantically correct.
- Easy to use and navigate (keyboard).
- Accessible with ARIA attributes and proper labels.
- Has support for client and server side validation.
- Well-styled and consistent with the rest of the application.

In this guide, we will take a look at building forms with [`react-hook-form`](https://react-hook-form.com/) and [`zod`](https://zod.dev/). We're going to use a `<FormField>` component to compose accessible forms using Radix UI components.

## [Link to section](https://ui.shadcn.com/docs/components/form\#features) Features

The `<Form />` component is a wrapper around the `react-hook-form` library. It provides a few things:

- Composable components for building forms.
- A `<FormField />` component for building controlled form fields.
- Form validation using `zod`.
- Handles accessibility and error messages.
- Uses `React.useId()` for generating unique IDs.
- Applies the correct `aria` attributes to form fields based on states.
- Built to work with all Radix UI components.
- Bring your own schema library. We use `zod` but you can use anything you want.
- **You have full control over the markup and styling.**

## [Link to section](https://ui.shadcn.com/docs/components/form\#anatomy) Anatomy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Form>
  <FormField
    control={...}
    name="..."
    render={() => (
      <FormItem>
        <FormLabel />
        <FormControl>
          { /* Your form field */}
        </FormControl>
        <FormDescription />
        <FormMessage />
      </FormItem>
    )}
  />
</Form>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/form\#example) Example

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const form = useForm()

<FormField
  control={form.control}
  name="username"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Username</FormLabel>
      <FormControl>
        <Input placeholder="shadcn" {...field} />
      </FormControl>
      <FormDescription>This is your public display name.</FormDescription>
      <FormMessage />
    </FormItem>
  )}
/>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/form\#installation) Installation

CLIManual

### [Link to section](https://ui.shadcn.com/docs/components/form\#command) Command

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add form

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/form\#usage) Usage

### [Link to section](https://ui.shadcn.com/docs/components/form\#create-a-form-schema) Create a form schema

Define the shape of your form using a Zod schema. You can read more about using Zod in the [Zod documentation](https://zod.dev/).

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { z } from "zod"

const formSchema = z.object({
  username: z.string().min(2).max(50),
})
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/form\#define-a-form) Define a form

Use the `useForm` hook from `react-hook-form` to create a form.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

const formSchema = z.object({
  username: z.string().min(2, {
    message: "Username must be at least 2 characters.",
  }),
})

export function ProfileForm() {
  // 1. Define your form.
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
    },
  })

  // 2. Define a submit handler.
  function onSubmit(values: z.infer<typeof formSchema>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.
    console.log(values)
  }
}
```

Copy

Since `FormField` is using a controlled component, you need to provide a default value for the field. See the [React Hook Form docs](https://react-hook-form.com/docs/usecontroller) to learn more about controlled components.

### [Link to section](https://ui.shadcn.com/docs/components/form\#build-your-form) Build your form

We can now use the `<Form />` components to build our form.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  username: z.string().min(2, {
    message: "Username must be at least 2 characters.",
  }),
})

export function ProfileForm() {
  // ...

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="shadcn" {...field} />
              </FormControl>
              <FormDescription>
                This is your public display name.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/form\#done) Done

That's it. You now have a fully accessible form that is type-safe with client-side validation.

PreviewCode

Style: New York

Copy

Username

This is your public display name.

Submit

## [Link to section](https://ui.shadcn.com/docs/components/form\#examples) Examples

See the following links for more examples on how to use the `<Form />` component with other components:

- [Checkbox](https://ui.shadcn.com/docs/components/checkbox#form)
- [Date Picker](https://ui.shadcn.com/docs/components/date-picker#form)
- [Input](https://ui.shadcn.com/docs/components/input#form)
- [Radio Group](https://ui.shadcn.com/docs/components/radio-group#form)
- [Select](https://ui.shadcn.com/docs/components/select#form)
- [Switch](https://ui.shadcn.com/docs/components/switch#form)
- [Textarea](https://ui.shadcn.com/docs/components/textarea#form)
- [Combobox](https://ui.shadcn.com/docs/components/combobox#form)

[Dropdown Menu](https://ui.shadcn.com/docs/components/dropdown-menu) [Hover Card](https://ui.shadcn.com/docs/components/hover-card)

On This Page

- [Features](https://ui.shadcn.com/docs/components/form#features)
- [Anatomy](https://ui.shadcn.com/docs/components/form#anatomy)
- [Example](https://ui.shadcn.com/docs/components/form#example)
- [Installation](https://ui.shadcn.com/docs/components/form#installation)
  - [Command](https://ui.shadcn.com/docs/components/form#command)
- [Usage](https://ui.shadcn.com/docs/components/form#usage)
  - [Create a form schema](https://ui.shadcn.com/docs/components/form#create-a-form-schema)
  - [Define a form](https://ui.shadcn.com/docs/components/form#define-a-form)
  - [Build your form](https://ui.shadcn.com/docs/components/form#build-your-form)
  - [Done](https://ui.shadcn.com/docs/components/form#done)
- [Examples](https://ui.shadcn.com/docs/components/form#examples)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## React Drawer Component
[Docs](https://ui.shadcn.com/docs)

Drawer

# Drawer

A drawer component for React.

[Docs](https://vaul.emilkowal.ski/getting-started)

PreviewCode

Style: New York

Open in Copy

Open Drawer

## [Link to section](https://ui.shadcn.com/docs/components/drawer\#about) About

Drawer is built on top of [Vaul](https://github.com/emilkowalski/vaul) by [emilkowalski\_](https://twitter.com/emilkowalski_).

## [Link to section](https://ui.shadcn.com/docs/components/drawer\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add drawer

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/drawer\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Drawer>
  <DrawerTrigger>Open</DrawerTrigger>
  <DrawerContent>
    <DrawerHeader>
      <DrawerTitle>Are you absolutely sure?</DrawerTitle>
      <DrawerDescription>This action cannot be undone.</DrawerDescription>
    </DrawerHeader>
    <DrawerFooter>
      <Button>Submit</Button>
      <DrawerClose>
        <Button variant="outline">Cancel</Button>
      </DrawerClose>
    </DrawerFooter>
  </DrawerContent>
</Drawer>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/drawer\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/drawer\#responsive-dialog) Responsive Dialog

You can combine the `Dialog` and `Drawer` components to create a responsive dialog. This renders a `Dialog` component on desktop and a `Drawer` on mobile.

PreviewCode

Style: New York

Copy

Edit Profile

[Dialog](https://ui.shadcn.com/docs/components/dialog) [Dropdown Menu](https://ui.shadcn.com/docs/components/dropdown-menu)

On This Page

- [About](https://ui.shadcn.com/docs/components/drawer#about)
- [Installation](https://ui.shadcn.com/docs/components/drawer#installation)
- [Usage](https://ui.shadcn.com/docs/components/drawer#usage)
- [Examples](https://ui.shadcn.com/docs/components/drawer#examples)
  - [Responsive Dialog](https://ui.shadcn.com/docs/components/drawer#responsive-dialog)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Button Component Guide
[Docs](https://ui.shadcn.com/docs)

Button

# Button

Displays a button or a component that looks like a button.

PreviewCode

Style: New York

Open in Copy

Button

## [Link to section](https://ui.shadcn.com/docs/components/button\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add button

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/button\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Button } from "@/components/ui/button"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Button variant="outline">Button</Button>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/button\#link) Link

You can use the `buttonVariants` helper to create a link that looks like a button.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { buttonVariants } from "@/components/ui/button"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Link className={buttonVariants({ variant: "outline" })}>Click here</Link>
```

Copy

Alternatively, you can set the `asChild` parameter and nest the link component.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Button asChild>
  <Link href="/login">Login</Link>
</Button>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/button\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/button\#primary) Primary

PreviewCode

Style: New York

Open in Copy

Button

### [Link to section](https://ui.shadcn.com/docs/components/button\#secondary) Secondary

PreviewCode

Style: New York

Open in Copy

Secondary

### [Link to section](https://ui.shadcn.com/docs/components/button\#destructive) Destructive

PreviewCode

Style: New York

Open in Copy

Destructive

### [Link to section](https://ui.shadcn.com/docs/components/button\#outline) Outline

PreviewCode

Style: New York

Open in Copy

Outline

### [Link to section](https://ui.shadcn.com/docs/components/button\#ghost) Ghost

PreviewCode

Style: New York

Open in Copy

Ghost

### [Link to section](https://ui.shadcn.com/docs/components/button\#link-1) Link

PreviewCode

Style: New York

Open in Copy

Link

### [Link to section](https://ui.shadcn.com/docs/components/button\#icon) Icon

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/button\#with-icon) With Icon

PreviewCode

Style: New York

Open in Copy

Login with Email

### [Link to section](https://ui.shadcn.com/docs/components/button\#loading) Loading

PreviewCode

Style: New York

Open in Copy

Please wait

### [Link to section](https://ui.shadcn.com/docs/components/button\#as-child) As Child

PreviewCode

Style: New York

Open in Copy

[Login](https://ui.shadcn.com/login)

## [Link to section](https://ui.shadcn.com/docs/components/button\#changelog) Changelog

### [Link to section](https://ui.shadcn.com/docs/components/button\#2024-10-16-classes-for-icons) 2024-10-16 Classes for icons

Added `gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0` to the button to automatically style icon inside the button.

Add the following classes to the `cva` call in your `button.tsx` file.

button.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const buttonVariants = cva(
  "inline-flex ... gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0"
)
```

Copy

[Breadcrumb](https://ui.shadcn.com/docs/components/breadcrumb) [Calendar](https://ui.shadcn.com/docs/components/calendar)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/button#installation)
- [Usage](https://ui.shadcn.com/docs/components/button#usage)
- [Link](https://ui.shadcn.com/docs/components/button#link)
- [Examples](https://ui.shadcn.com/docs/components/button#examples)
  - [Primary](https://ui.shadcn.com/docs/components/button#primary)
  - [Secondary](https://ui.shadcn.com/docs/components/button#secondary)
  - [Destructive](https://ui.shadcn.com/docs/components/button#destructive)
  - [Outline](https://ui.shadcn.com/docs/components/button#outline)
  - [Ghost](https://ui.shadcn.com/docs/components/button#ghost)
  - [Link](https://ui.shadcn.com/docs/components/button#link-1)
  - [Icon](https://ui.shadcn.com/docs/components/button#icon)
  - [With Icon](https://ui.shadcn.com/docs/components/button#with-icon)
  - [Loading](https://ui.shadcn.com/docs/components/button#loading)
  - [As Child](https://ui.shadcn.com/docs/components/button#as-child)
- [Changelog](https://ui.shadcn.com/docs/components/button#changelog)
  - [2024-10-16 Classes for icons](https://ui.shadcn.com/docs/components/button#2024-10-16-classes-for-icons)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Pagination Components Guide
[Docs](https://ui.shadcn.com/docs)

Pagination

# Pagination

Pagination with page navigation, next and previous links.

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/pagination\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add pagination

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/pagination\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Pagination>
  <PaginationContent>
    <PaginationItem>
      <PaginationPrevious href="#" />
    </PaginationItem>
    <PaginationItem>
      <PaginationLink href="#">1</PaginationLink>
    </PaginationItem>
    <PaginationItem>
      <PaginationEllipsis />
    </PaginationItem>
    <PaginationItem>
      <PaginationNext href="#" />
    </PaginationItem>
  </PaginationContent>
</Pagination>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/pagination\#nextjs) Next.js

By default the `<PaginationLink />` component will render an `<a />` tag.

To use the Next.js `<Link />` component, make the following updates to `pagination.tsx`.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
+ import Link from "next/link"

- type PaginationLinkProps = ... & React.ComponentProps<"a">
+ type PaginationLinkProps = ... & React.ComponentProps<typeof Link>

const PaginationLink = ({...props }: ) => (
  <PaginationItem>
-   <a>
+   <Link>
      // ...
-   </a>
+   </Link>
  </PaginationItem>
)

```

Copy

**Note:** We are making updates to the cli to automatically do this for you.

[Navigation Menu](https://ui.shadcn.com/docs/components/navigation-menu) [Popover](https://ui.shadcn.com/docs/components/popover)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/pagination#installation)
- [Usage](https://ui.shadcn.com/docs/components/pagination#usage)
  - [Next.js](https://ui.shadcn.com/docs/components/pagination#nextjs)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Badge Component Guide
[Docs](https://ui.shadcn.com/docs)

Badge

# Badge

Displays a badge or a component that looks like a badge.

PreviewCode

Style: New York

Open in Copy

Badge

## [Link to section](https://ui.shadcn.com/docs/components/badge\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add badge

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/badge\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Badge } from "@/components/ui/badge"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Badge variant="outline">Badge</Badge>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/badge\#link) Link

You can use the `badgeVariants` helper to create a link that looks like a badge.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { badgeVariants } from "@/components/ui/badge"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Link className={badgeVariants({ variant: "outline" })}>Badge</Link>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/badge\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/badge\#default) Default

PreviewCode

Style: New York

Open in Copy

Badge

* * *

### [Link to section](https://ui.shadcn.com/docs/components/badge\#secondary) Secondary

PreviewCode

Style: New York

Open in Copy

Secondary

* * *

### [Link to section](https://ui.shadcn.com/docs/components/badge\#outline) Outline

PreviewCode

Style: New York

Open in Copy

Outline

* * *

### [Link to section](https://ui.shadcn.com/docs/components/badge\#destructive) Destructive

PreviewCode

Style: New York

Open in Copy

Destructive

[Avatar](https://ui.shadcn.com/docs/components/avatar) [Breadcrumb](https://ui.shadcn.com/docs/components/breadcrumb)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/badge#installation)
- [Usage](https://ui.shadcn.com/docs/components/badge#usage)
  - [Link](https://ui.shadcn.com/docs/components/badge#link)
- [Examples](https://ui.shadcn.com/docs/components/badge#examples)
  - [Default](https://ui.shadcn.com/docs/components/badge#default)
  - [Secondary](https://ui.shadcn.com/docs/components/badge#secondary)
  - [Outline](https://ui.shadcn.com/docs/components/badge#outline)
  - [Destructive](https://ui.shadcn.com/docs/components/badge#destructive)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Switch Component
[Docs](https://ui.shadcn.com/docs)

Switch

# Switch

A control that allows the user to toggle between checked and not checked.

[Docs](https://www.radix-ui.com/docs/primitives/components/switch) [API Reference](https://www.radix-ui.com/docs/primitives/components/switch#api-reference)

PreviewCode

Style: New York

Open in Copy

Airplane Mode

## [Link to section](https://ui.shadcn.com/docs/components/switch\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add switch

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/switch\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Switch } from "@/components/ui/switch"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Switch />
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/switch\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/switch\#form) Form

PreviewCode

Style: New York

Copy

### Email Notifications

Marketing emails

Receive emails about new products, features, and more.

Security emails

Receive emails about your account security.

Submit

[Sonner](https://ui.shadcn.com/docs/components/sonner) [Table](https://ui.shadcn.com/docs/components/table)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/switch#installation)
- [Usage](https://ui.shadcn.com/docs/components/switch#usage)
- [Examples](https://ui.shadcn.com/docs/components/switch#examples)
  - [Form](https://ui.shadcn.com/docs/components/switch#form)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Carousel Component Guide
[Docs](https://ui.shadcn.com/docs)

Carousel

# Carousel

A carousel with motion and swipe built using Embla.

[Docs](https://www.embla-carousel.com/get-started/react) [API Reference](https://www.embla-carousel.com/api)

PreviewCode

Style: New York

Open in Copy

1

2

3

4

5

Previous slideNext slide

## [Link to section](https://ui.shadcn.com/docs/components/carousel\#about) About

The carousel component is built using the [Embla Carousel](https://www.embla-carousel.com/) library.

## [Link to section](https://ui.shadcn.com/docs/components/carousel\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add carousel

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/carousel\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Carousel>
  <CarouselContent>
    <CarouselItem>...</CarouselItem>
    <CarouselItem>...</CarouselItem>
    <CarouselItem>...</CarouselItem>
  </CarouselContent>
  <CarouselPrevious />
  <CarouselNext />
</Carousel>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/carousel\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/carousel\#sizes) Sizes

To set the size of the items, you can use the `basis` utility class on the `<CarouselItem />`.

PreviewCode

Style: New York

Open in Copy

1

2

3

4

5

Previous slideNext slide

Example

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
// 33% of the carousel width.
<Carousel>
  <CarouselContent>
    <CarouselItem className="basis-1/3">...</CarouselItem>
    <CarouselItem className="basis-1/3">...</CarouselItem>
    <CarouselItem className="basis-1/3">...</CarouselItem>
  </CarouselContent>
</Carousel>
```

Copy

Responsive

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
// 50% on small screens and 33% on larger screens.
<Carousel>
  <CarouselContent>
    <CarouselItem className="md:basis-1/2 lg:basis-1/3">...</CarouselItem>
    <CarouselItem className="md:basis-1/2 lg:basis-1/3">...</CarouselItem>
    <CarouselItem className="md:basis-1/2 lg:basis-1/3">...</CarouselItem>
  </CarouselContent>
</Carousel>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/carousel\#spacing) Spacing

To set the spacing between the items, we use a `pl-[VALUE]` utility on the `<CarouselItem />` and a negative `-ml-[VALUE]` on the `<CarouselContent />`.

**Why:** I tried to use the `gap` property or a `grid` layout on the `   <CarouselContent />` but it required a lot of math and mental effort to get the
spacing right. I found `pl-[VALUE]` and `-ml-[VALUE]` utilities much easier to
use.

You can always adjust this in your own project if you need to.

PreviewCode

Style: New York

Open in Copy

1

2

3

4

5

Previous slideNext slide

Example

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Carousel>
  <CarouselContent className="-ml-4">
    <CarouselItem className="pl-4">...</CarouselItem>
    <CarouselItem className="pl-4">...</CarouselItem>
    <CarouselItem className="pl-4">...</CarouselItem>
  </CarouselContent>
</Carousel>
```

Copy

Responsive

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Carousel>
  <CarouselContent className="-ml-2 md:-ml-4">
    <CarouselItem className="pl-2 md:pl-4">...</CarouselItem>
    <CarouselItem className="pl-2 md:pl-4">...</CarouselItem>
    <CarouselItem className="pl-2 md:pl-4">...</CarouselItem>
  </CarouselContent>
</Carousel>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/carousel\#orientation) Orientation

Use the `orientation` prop to set the orientation of the carousel.

PreviewCode

Style: New York

Open in Copy

1

2

3

4

5

Previous slideNext slide

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Carousel orientation="vertical | horizontal">
  <CarouselContent>
    <CarouselItem>...</CarouselItem>
    <CarouselItem>...</CarouselItem>
    <CarouselItem>...</CarouselItem>
  </CarouselContent>
</Carousel>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/carousel\#options) Options

You can pass options to the carousel using the `opts` prop. See the [Embla Carousel docs](https://www.embla-carousel.com/api/options/) for more information.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Carousel
  opts={{
    align: "start",
    loop: true,
  }}
>
  <CarouselContent>
    <CarouselItem>...</CarouselItem>
    <CarouselItem>...</CarouselItem>
    <CarouselItem>...</CarouselItem>
  </CarouselContent>
</Carousel>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/carousel\#api) API

Use a state and the `setApi` props to get an instance of the carousel API.

PreviewCode

Style: New York

Open in Copy

1

2

3

4

5

Previous slideNext slide

Slide 1 of 1

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { type CarouselApi } from "@/components/ui/carousel"

export function Example() {
  const [api, setApi] = React.useState<CarouselApi>()
  const [current, setCurrent] = React.useState(0)
  const [count, setCount] = React.useState(0)

  React.useEffect(() => {
    if (!api) {
      return
    }

    setCount(api.scrollSnapList().length)
    setCurrent(api.selectedScrollSnap() + 1)

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap() + 1)
    })
  }, [api])

  return (
    <Carousel setApi={setApi}>
      <CarouselContent>
        <CarouselItem>...</CarouselItem>
        <CarouselItem>...</CarouselItem>
        <CarouselItem>...</CarouselItem>
      </CarouselContent>
    </Carousel>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/carousel\#events) Events

You can listen to events using the api instance from `setApi`.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { type CarouselApi } from "@/components/ui/carousel"

export function Example() {
  const [api, setApi] = React.useState<CarouselApi>()

  React.useEffect(() => {
    if (!api) {
      return
    }

    api.on("select", () => {
      // Do something on select.
    })
  }, [api])

  return (
    <Carousel setApi={setApi}>
      <CarouselContent>
        <CarouselItem>...</CarouselItem>
        <CarouselItem>...</CarouselItem>
        <CarouselItem>...</CarouselItem>
      </CarouselContent>
    </Carousel>
  )
}
```

Copy

See the [Embla Carousel docs](https://www.embla-carousel.com/api/events/) for more information on using events.

## [Link to section](https://ui.shadcn.com/docs/components/carousel\#plugins) Plugins

You can use the `plugins` prop to add plugins to the carousel.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import Autoplay from "embla-carousel-autoplay"

export function Example() {
  return (
    <Carousel
      plugins={[\
        Autoplay({\
          delay: 2000,\
        }),\
      ]}
    >
      // ...
    </Carousel>
  )
}
```

Copy

PreviewCode

Style: New York

Open in Copy

1

2

3

4

5

Previous slideNext slide

See the [Embla Carousel docs](https://www.embla-carousel.com/api/plugins/) for more information on using plugins.

[Card](https://ui.shadcn.com/docs/components/card) [Chart](https://ui.shadcn.com/docs/components/chart)

On This Page

- [About](https://ui.shadcn.com/docs/components/carousel#about)
- [Installation](https://ui.shadcn.com/docs/components/carousel#installation)
- [Usage](https://ui.shadcn.com/docs/components/carousel#usage)
- [Examples](https://ui.shadcn.com/docs/components/carousel#examples)
  - [Sizes](https://ui.shadcn.com/docs/components/carousel#sizes)
  - [Spacing](https://ui.shadcn.com/docs/components/carousel#spacing)
  - [Orientation](https://ui.shadcn.com/docs/components/carousel#orientation)
- [Options](https://ui.shadcn.com/docs/components/carousel#options)
- [API](https://ui.shadcn.com/docs/components/carousel#api)
- [Events](https://ui.shadcn.com/docs/components/carousel#events)
- [Plugins](https://ui.shadcn.com/docs/components/carousel#plugins)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Dialog Component Guide
[Docs](https://ui.shadcn.com/docs)

Dialog

# Dialog

A window overlaid on either the primary window or another dialog window, rendering the content underneath inert.

[Docs](https://www.radix-ui.com/docs/primitives/components/dialog) [API Reference](https://www.radix-ui.com/docs/primitives/components/dialog#api-reference)

PreviewCode

Style: New York

Open in Copy

Edit Profile

## [Link to section](https://ui.shadcn.com/docs/components/dialog\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add dialog

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/dialog\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you absolutely sure?</DialogTitle>
      <DialogDescription>
        This action cannot be undone. This will permanently delete your account
        and remove your data from our servers.
      </DialogDescription>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/dialog\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/dialog\#custom-close-button) Custom close button

PreviewCode

Style: New York

Copy

Share

## [Link to section](https://ui.shadcn.com/docs/components/dialog\#notes) Notes

To activate the `Dialog` component from within a `Context Menu` or `Dropdown Menu`, you must encase the `Context Menu` or
`Dropdown Menu` component in the `Dialog` component. For more information, refer to the linked issue [here](https://github.com/radix-ui/primitives/issues/1836).

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Dialog>
  <ContextMenu>
    <ContextMenuTrigger>Right click</ContextMenuTrigger>
    <ContextMenuContent>
      <ContextMenuItem>Open</ContextMenuItem>
      <ContextMenuItem>Download</ContextMenuItem>
      <DialogTrigger asChild>
        <ContextMenuItem>
          <span>Delete</span>
        </ContextMenuItem>
      </DialogTrigger>
    </ContextMenuContent>
  </ContextMenu>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you absolutely sure?</DialogTitle>
      <DialogDescription>
        This action cannot be undone. Are you sure you want to permanently
        delete this file from our servers?
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button type="submit">Confirm</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

Copy

[Date Picker](https://ui.shadcn.com/docs/components/date-picker) [Drawer](https://ui.shadcn.com/docs/components/drawer)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/dialog#installation)
- [Usage](https://ui.shadcn.com/docs/components/dialog#usage)
- [Examples](https://ui.shadcn.com/docs/components/dialog#examples)
  - [Custom close button](https://ui.shadcn.com/docs/components/dialog#custom-close-button)
- [Notes](https://ui.shadcn.com/docs/components/dialog#notes)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Skeleton Component
[Docs](https://ui.shadcn.com/docs)

Skeleton

# Skeleton

Use to show a placeholder while content is loading.

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/skeleton\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add skeleton

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/skeleton\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Skeleton } from "@/components/ui/skeleton"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Skeleton className="w-[100px] h-[20px] rounded-full" />
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/skeleton\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/skeleton\#card) Card

PreviewCode

Style: New York

Open in Copy

[Sidebar](https://ui.shadcn.com/docs/components/sidebar) [Slider](https://ui.shadcn.com/docs/components/slider)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/skeleton#installation)
- [Usage](https://ui.shadcn.com/docs/components/skeleton#usage)
- [Examples](https://ui.shadcn.com/docs/components/skeleton#examples)
  - [Card](https://ui.shadcn.com/docs/components/skeleton#card)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Resizable Panels
[Docs](https://ui.shadcn.com/docs)

Resizable

# Resizable

Accessible resizable panel groups and layouts with keyboard support.

[Docs](https://github.com/bvaughn/react-resizable-panels) [API Reference](https://github.com/bvaughn/react-resizable-panels/tree/main/packages/react-resizable-panels)

PreviewCode

Style: New York

Open in Copy

One

Two

Three

## [Link to section](https://ui.shadcn.com/docs/components/resizable\#about) About

The `Resizable` component is built on top of [react-resizable-panels](https://github.com/bvaughn/react-resizable-panels) by [bvaughn](https://github.com/bvaughn).

## [Link to section](https://ui.shadcn.com/docs/components/resizable\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add resizable

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/resizable\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ResizablePanelGroup direction="horizontal">
  <ResizablePanel>One</ResizablePanel>
  <ResizableHandle />
  <ResizablePanel>Two</ResizablePanel>
</ResizablePanelGroup>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/resizable\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/resizable\#vertical) Vertical

Use the `direction` prop to set the direction of the resizable panels.

PreviewCode

Style: New York

Open in Copy

Header

Content

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

export default function Example() {
  return (
    <ResizablePanelGroup direction="vertical">
      <ResizablePanel>One</ResizablePanel>
      <ResizableHandle />
      <ResizablePanel>Two</ResizablePanel>
    </ResizablePanelGroup>
  )
}
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/resizable\#handle) Handle

You can set or hide the handle by using the `withHandle` prop on the `ResizableHandle` component.

PreviewCode

Style: New York

Open in Copy

Sidebar

Content

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"

export default function Example() {
  return (
    <ResizablePanelGroup direction="horizontal">
      <ResizablePanel>One</ResizablePanel>
      <ResizableHandle withHandle />
      <ResizablePanel>Two</ResizablePanel>
    </ResizablePanelGroup>
  )
}
```

Copy

[Radio Group](https://ui.shadcn.com/docs/components/radio-group) [Scroll Area](https://ui.shadcn.com/docs/components/scroll-area)

On This Page

- [About](https://ui.shadcn.com/docs/components/resizable#about)
- [Installation](https://ui.shadcn.com/docs/components/resizable#installation)
- [Usage](https://ui.shadcn.com/docs/components/resizable#usage)
- [Examples](https://ui.shadcn.com/docs/components/resizable#examples)
  - [Vertical](https://ui.shadcn.com/docs/components/resizable#vertical)
  - [Handle](https://ui.shadcn.com/docs/components/resizable#handle)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Alert Component Guide
[Docs](https://ui.shadcn.com/docs)

Alert

# Alert

Displays a callout for user attention.

PreviewCode

Style: New York

Open in Copy

##### Heads up!

You can add components to your app using the cli.

## [Link to section](https://ui.shadcn.com/docs/components/alert\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add alert

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/alert\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Alert>
  <Terminal className="h-4 w-4" />
  <AlertTitle>Heads up!</AlertTitle>
  <AlertDescription>
    You can add components and dependencies to your app using the cli.
  </AlertDescription>
</Alert>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/alert\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/alert\#default) Default

PreviewCode

Style: New York

Open in Copy

##### Heads up!

You can add components to your app using the cli.

### [Link to section](https://ui.shadcn.com/docs/components/alert\#destructive) Destructive

PreviewCode

Style: New York

Open in Copy

##### Error

Your session has expired. Please log in again.

[Accordion](https://ui.shadcn.com/docs/components/accordion) [Alert Dialog](https://ui.shadcn.com/docs/components/alert-dialog)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/alert#installation)
- [Usage](https://ui.shadcn.com/docs/components/alert#usage)
- [Examples](https://ui.shadcn.com/docs/components/alert#examples)
  - [Default](https://ui.shadcn.com/docs/components/alert#default)
  - [Destructive](https://ui.shadcn.com/docs/components/alert#destructive)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Menubar Component
[Docs](https://ui.shadcn.com/docs)

Menubar

# Menubar

A visually persistent menu common in desktop applications that provides quick access to a consistent set of commands.

[Docs](https://www.radix-ui.com/docs/primitives/components/menubar) [API Reference](https://www.radix-ui.com/docs/primitives/components/menubar#api-reference)

PreviewCode

Style: New York

Open in Copy

FileEditViewProfiles

## [Link to section](https://ui.shadcn.com/docs/components/menubar\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add menubar

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/menubar\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Menubar,
  MenubarContent,
  MenubarItem,
  MenubarMenu,
  MenubarSeparator,
  MenubarShortcut,
  MenubarTrigger,
} from "@/components/ui/menubar"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Menubar>
  <MenubarMenu>
    <MenubarTrigger>File</MenubarTrigger>
    <MenubarContent>
      <MenubarItem>
        New Tab <MenubarShortcut>⌘T</MenubarShortcut>
      </MenubarItem>
      <MenubarItem>New Window</MenubarItem>
      <MenubarSeparator />
      <MenubarItem>Share</MenubarItem>
      <MenubarSeparator />
      <MenubarItem>Print</MenubarItem>
    </MenubarContent>
  </MenubarMenu>
</Menubar>
```

Copy

[Label](https://ui.shadcn.com/docs/components/label) [Navigation Menu](https://ui.shadcn.com/docs/components/navigation-menu)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/menubar#installation)
- [Usage](https://ui.shadcn.com/docs/components/menubar#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Sonner Toast Component
[Docs](https://ui.shadcn.com/docs)

Sonner

# Sonner

An opinionated toast component for React.

[Docs](https://sonner.emilkowal.ski/)

PreviewCode

Style: New York

Copy

Show Toast

## [Link to section](https://ui.shadcn.com/docs/components/sonner\#about) About

Sonner is built and maintained by [emilkowalski\_](https://twitter.com/emilkowalski_).

## [Link to section](https://ui.shadcn.com/docs/components/sonner\#installation) Installation

CLIManual

### Run the following command:

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add sonner

```

Copy

### Add the Toaster component

app/layout.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Toaster } from "@/components/ui/sonner"

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head />
      <body>
        <main>{children}</main>
        <Toaster />
      </body>
    </html>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/sonner\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { toast } from "sonner"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
toast("Event has been created.")
```

Copy

[Slider](https://ui.shadcn.com/docs/components/slider) [Switch](https://ui.shadcn.com/docs/components/switch)

On This Page

- [About](https://ui.shadcn.com/docs/components/sonner#about)
- [Installation](https://ui.shadcn.com/docs/components/sonner#installation)
- [Usage](https://ui.shadcn.com/docs/components/sonner#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Label Component
[Docs](https://ui.shadcn.com/docs)

Label

# Label

Renders an accessible label associated with controls.

[Docs](https://www.radix-ui.com/docs/primitives/components/label) [API Reference](https://www.radix-ui.com/docs/primitives/components/label#api-reference)

PreviewCode

Style: New York

Open in Copy

Accept terms and conditions

## [Link to section](https://ui.shadcn.com/docs/components/label\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add label

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/label\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Label } from "@/components/ui/label"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Label htmlFor="email">Your email address</Label>
```

Copy

[Input OTP](https://ui.shadcn.com/docs/components/input-otp) [Menubar](https://ui.shadcn.com/docs/components/menubar)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/label#installation)
- [Usage](https://ui.shadcn.com/docs/components/label#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## User Avatar Component
[Docs](https://ui.shadcn.com/docs)

Avatar

# Avatar

An image element with a fallback for representing the user.

[Docs](https://www.radix-ui.com/docs/primitives/components/avatar) [API Reference](https://www.radix-ui.com/docs/primitives/components/avatar#api-reference)

PreviewCode

Style: New York

Open in Copy

![@shadcn](https://github.com/shadcn.png)

## [Link to section](https://ui.shadcn.com/docs/components/avatar\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add avatar

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/avatar\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Avatar>
  <AvatarImage src="https://github.com/shadcn.png" />
  <AvatarFallback>CN</AvatarFallback>
</Avatar>
```

Copy

[Aspect Ratio](https://ui.shadcn.com/docs/components/aspect-ratio) [Badge](https://ui.shadcn.com/docs/components/badge)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/avatar#installation)
- [Usage](https://ui.shadcn.com/docs/components/avatar#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Tabs Component Guide
[Docs](https://ui.shadcn.com/docs)

Tabs

# Tabs

A set of layered sections of content—known as tab panels—that are displayed one at a time.

[Docs](https://www.radix-ui.com/docs/primitives/components/tabs) [API Reference](https://www.radix-ui.com/docs/primitives/components/tabs#api-reference)

PreviewCode

Style: New York

Open in Copy

AccountPassword

Account

Make changes to your account here. Click save when you're done.

Name

Username

Save changes

## [Link to section](https://ui.shadcn.com/docs/components/tabs\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add tabs

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/tabs\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Tabs defaultValue="account" className="w-[400px]">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
  </TabsList>
  <TabsContent value="account">Make changes to your account here.</TabsContent>
  <TabsContent value="password">Change your password here.</TabsContent>
</Tabs>
```

Copy

[Table](https://ui.shadcn.com/docs/components/table) [Textarea](https://ui.shadcn.com/docs/components/textarea)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/tabs#installation)
- [Usage](https://ui.shadcn.com/docs/components/tabs#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Content Separator Component
[Docs](https://ui.shadcn.com/docs)

Separator

# Separator

Visually or semantically separates content.

[Docs](https://www.radix-ui.com/docs/primitives/components/separator) [API Reference](https://www.radix-ui.com/docs/primitives/components/separator#api-reference)

PreviewCode

Style: New York

Open in Copy

#### Radix Primitives

An open-source UI component library.

Blog

Docs

Source

## [Link to section](https://ui.shadcn.com/docs/components/separator\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add separator

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/separator\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Separator } from "@/components/ui/separator"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Separator />
```

Copy

[Select](https://ui.shadcn.com/docs/components/select) [Sheet](https://ui.shadcn.com/docs/components/sheet)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/separator#installation)
- [Usage](https://ui.shadcn.com/docs/components/separator#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Progress Indicator
[Docs](https://ui.shadcn.com/docs)

Progress

# Progress

Displays an indicator showing the completion progress of a task, typically displayed as a progress bar.

[Docs](https://www.radix-ui.com/docs/primitives/components/progress) [API Reference](https://www.radix-ui.com/docs/primitives/components/progress#api-reference)

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/progress\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add progress

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/progress\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Progress } from "@/components/ui/progress"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Progress value={33} />
```

Copy

[Popover](https://ui.shadcn.com/docs/components/popover) [Radio Group](https://ui.shadcn.com/docs/components/radio-group)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/progress#installation)
- [Usage](https://ui.shadcn.com/docs/components/progress#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Slider Component
[Docs](https://ui.shadcn.com/docs)

Slider

# Slider

An input where the user selects a value from within a given range.

[Docs](https://www.radix-ui.com/docs/primitives/components/slider) [API Reference](https://www.radix-ui.com/docs/primitives/components/slider#api-reference)

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/slider\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add slider

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/slider\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Slider } from "@/components/ui/slider"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Slider defaultValue={[33]} max={100} step={1} />
```

Copy

[Skeleton](https://ui.shadcn.com/docs/components/skeleton) [Sonner](https://ui.shadcn.com/docs/components/sonner)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/slider#installation)
- [Usage](https://ui.shadcn.com/docs/components/slider#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Popover Component Guide
[Docs](https://ui.shadcn.com/docs)

Popover

# Popover

Displays rich content in a portal, triggered by a button.

[Docs](https://www.radix-ui.com/docs/primitives/components/popover) [API Reference](https://www.radix-ui.com/docs/primitives/components/popover#api-reference)

PreviewCode

Style: New York

Open in Copy

Open popover

## [Link to section](https://ui.shadcn.com/docs/components/popover\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add popover

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/popover\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Popover>
  <PopoverTrigger>Open</PopoverTrigger>
  <PopoverContent>Place content for the popover here.</PopoverContent>
</Popover>
```

Copy

[Pagination](https://ui.shadcn.com/docs/components/pagination) [Progress](https://ui.shadcn.com/docs/components/progress)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/popover#installation)
- [Usage](https://ui.shadcn.com/docs/components/popover#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Accordion Component
[Docs](https://ui.shadcn.com/docs)

Accordion

# Accordion

A vertically stacked set of interactive headings that each reveal a section of content.

[Docs](https://www.radix-ui.com/docs/primitives/components/accordion) [API Reference](https://www.radix-ui.com/docs/primitives/components/accordion#api-reference)

PreviewCode

Style: New York

Open in Copy

### Is it accessible?

### Is it styled?

### Is it animated?

## [Link to section](https://ui.shadcn.com/docs/components/accordion\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add accordion

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/accordion\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>
      Yes. It adheres to the WAI-ARIA design pattern.
    </AccordionContent>
  </AccordionItem>
</Accordion>
```

Copy

[Manual](https://ui.shadcn.com/docs/installation/manual) [Alert](https://ui.shadcn.com/docs/components/alert)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/accordion#installation)
- [Usage](https://ui.shadcn.com/docs/components/accordion#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Collapsible Component
[Docs](https://ui.shadcn.com/docs)

Collapsible

# Collapsible

An interactive component which expands/collapses a panel.

[Docs](https://www.radix-ui.com/docs/primitives/components/collapsible) [API Reference](https://www.radix-ui.com/docs/primitives/components/collapsible#api-reference)

PreviewCode

Style: New York

Open in Copy

#### @peduarte starred 3 repositories

Toggle

@radix-ui/primitives

## [Link to section](https://ui.shadcn.com/docs/components/collapsible\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add collapsible

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/collapsible\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Collapsible>
  <CollapsibleTrigger>Can I use this in my project?</CollapsibleTrigger>
  <CollapsibleContent>
    Yes. Free to use for personal and commercial projects. No attribution
    required.
  </CollapsibleContent>
</Collapsible>
```

Copy

[Checkbox](https://ui.shadcn.com/docs/components/checkbox) [Combobox](https://ui.shadcn.com/docs/components/combobox)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/collapsible#installation)
- [Usage](https://ui.shadcn.com/docs/components/collapsible#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Tooltip Component
[Docs](https://ui.shadcn.com/docs)

Tooltip

# Tooltip

A popup that displays information related to an element when the element receives keyboard focus or the mouse hovers over it.

[Docs](https://www.radix-ui.com/docs/primitives/components/tooltip) [API Reference](https://www.radix-ui.com/docs/primitives/components/tooltip#api-reference)

PreviewCode

Style: New York

Open in Copy

Hover

## [Link to section](https://ui.shadcn.com/docs/components/tooltip\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add tooltip

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/tooltip\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<TooltipProvider>
  <Tooltip>
    <TooltipTrigger>Hover</TooltipTrigger>
    <TooltipContent>
      <p>Add to library</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

Copy

[Toggle Group](https://ui.shadcn.com/docs/components/toggle-group) [Introduction](https://ui.shadcn.com/docs/registry)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/tooltip#installation)
- [Usage](https://ui.shadcn.com/docs/components/tooltip#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Custom Data Tables Guide
[Docs](https://ui.shadcn.com/docs)

Data Table

# Data Table

Powerful table and datagrids built using TanStack Table.

[Docs](https://tanstack.com/table/v8/docs/introduction)

PreviewCode

Style: New York

Copy

Loading...

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#introduction) Introduction

Every data table or datagrid I've created has been unique. They all behave differently, have specific sorting and filtering requirements, and work with different data sources.

It doesn't make sense to combine all of these variations into a single component. If we do that, we'll lose the flexibility that [headless UI](https://tanstack.com/table/v8/docs/introduction#what-is-headless-ui) provides.

So instead of a data-table component, I thought it would be more helpful to provide a guide on how to build your own.

We'll start with the basic `<Table />` component and build a complex data table from scratch.

**Tip:** If you find yourself using the same table in multiple places in your app, you can always extract it into a reusable component.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#table-of-contents) Table of Contents

This guide will show you how to use [TanStack Table](https://tanstack.com/table) and the `<Table />` component to build your own custom data table. We'll cover the following topics:

- [Basic Table](https://ui.shadcn.com/docs/components/data-table#basic-table)
- [Row Actions](https://ui.shadcn.com/docs/components/data-table#row-actions)
- [Pagination](https://ui.shadcn.com/docs/components/data-table#pagination)
- [Sorting](https://ui.shadcn.com/docs/components/data-table#sorting)
- [Filtering](https://ui.shadcn.com/docs/components/data-table#filtering)
- [Visibility](https://ui.shadcn.com/docs/components/data-table#visibility)
- [Row Selection](https://ui.shadcn.com/docs/components/data-table#row-selection)
- [Reusable Components](https://ui.shadcn.com/docs/components/data-table#reusable-components)

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#installation) Installation

1. Add the `<Table />` component to your project:

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add table

```

Copy

2. Add `tanstack/react-table` dependency:

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm add @tanstack/react-table

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#prerequisites) Prerequisites

We are going to build a table to show recent payments. Here's what our data looks like:

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
type Payment = {
  id: string
  amount: number
  status: "pending" | "processing" | "success" | "failed"
  email: string
}

export const payments: Payment[] = [\
  {\
    id: "728ed52f",\
    amount: 100,\
    status: "pending",\
    email: "m@example.com",\
  },\
  {\
    id: "489e1d42",\
    amount: 125,\
    status: "processing",\
    email: "example@gmail.com",\
  },\
  // ...\
]
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#project-structure) Project Structure

Start by creating the following file structure:

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
app
└── payments
    ├── columns.tsx
    ├── data-table.tsx
    └── page.tsx
```

Copy

I'm using a Next.js example here but this works for any other React framework.

- `columns.tsx` (client component) will contain our column definitions.
- `data-table.tsx` (client component) will contain our `<DataTable />` component.
- `page.tsx` (server component) is where we'll fetch data and render our table.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#basic-table) Basic Table

Let's start by building a basic table.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#column-definitions) Column Definitions

First, we'll define our columns.

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { ColumnDef } from "@tanstack/react-table"

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Payment = {
  id: string
  amount: number
  status: "pending" | "processing" | "success" | "failed"
  email: string
}

export const columns: ColumnDef<Payment>[] = [\
  {\
    accessorKey: "status",\
    header: "Status",\
  },\
  {\
    accessorKey: "email",\
    header: "Email",\
  },\
  {\
    accessorKey: "amount",\
    header: "Amount",\
  },\
]
```

Copy

**Note:** Columns are where you define the core of what your table
will look like. They define the data that will be displayed, how it will be
formatted, sorted and filtered.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#datatable--component)`<DataTable />` component

Next, we'll create a `<DataTable />` component to render our table.

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                )
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && "selected"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}
```

Copy

**Tip**: If you find yourself using `<DataTable />` in multiple places, this is the component you could make reusable by extracting it to `components/ui/data-table.tsx`.

`<DataTable columns={columns} data={data} />`

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#render-the-table) Render the table

Finally, we'll render our table in our page component.

app/payments/page.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Payment, columns } from "./columns"
import { DataTable } from "./data-table"

async function getData(): Promise<Payment[]> {
  // Fetch data from your API here.
  return [\
    {\
      id: "728ed52f",\
      amount: 100,\
      status: "pending",\
      email: "m@example.com",\
    },\
    // ...\
  ]
}

export default async function DemoPage() {
  const data = await getData()

  return (
    <div className="container mx-auto py-10">
      <DataTable columns={columns} data={data} />
    </div>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#cell-formatting) Cell Formatting

Let's format the amount cell to display the dollar amount. We'll also align the cell to the right.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-columns-definition) Update columns definition

Update the `header` and `cell` definitions for amount as follows:

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export const columns: ColumnDef<Payment>[] = [\
  {\
    accessorKey: "amount",\
    header: () => <div className="text-right">Amount</div>,\
    cell: ({ row }) => {\
      const amount = parseFloat(row.getValue("amount"))\
      const formatted = new Intl.NumberFormat("en-US", {\
        style: "currency",\
        currency: "USD",\
      }).format(amount)\
\
      return <div className="text-right font-medium">{formatted}</div>\
    },\
  },\
]
```

Copy

You can use the same approach to format other cells and headers.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#row-actions) Row Actions

Let's add row actions to our table. We'll use a `<Dropdown />` component for this.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-columns-definition-1) Update columns definition

Update our columns definition to add a new `actions` column. The `actions` cell returns a `<Dropdown />` component.

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { ColumnDef } from "@tanstack/react-table"
import { MoreHorizontal } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export const columns: ColumnDef<Payment>[] = [\
  // ...\
  {\
    id: "actions",\
    cell: ({ row }) => {\
      const payment = row.original\
\
      return (\
        <DropdownMenu>\
          <DropdownMenuTrigger asChild>\
            <Button variant="ghost" className="h-8 w-8 p-0">\
              <span className="sr-only">Open menu</span>\
              <MoreHorizontal className="h-4 w-4" />\
            </Button>\
          </DropdownMenuTrigger>\
          <DropdownMenuContent align="end">\
            <DropdownMenuLabel>Actions</DropdownMenuLabel>\
            <DropdownMenuItem\
              onClick={() => navigator.clipboard.writeText(payment.id)}\
            >\
              Copy payment ID\
            </DropdownMenuItem>\
            <DropdownMenuSeparator />\
            <DropdownMenuItem>View customer</DropdownMenuItem>\
            <DropdownMenuItem>View payment details</DropdownMenuItem>\
          </DropdownMenuContent>\
        </DropdownMenu>\
      )\
    },\
  },\
  // ...\
]
```

Copy

You can access the row data using `row.original` in the `cell` function. Use this to handle actions for your row eg. use the `id` to make a DELETE call to your API.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#pagination) Pagination

Next, we'll add pagination to our table.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  // ...
}
```

Copy

This will automatically paginate your rows into pages of 10. See the [pagination docs](https://tanstack.com/table/v8/docs/api/features/pagination) for more information on customizing page size and implementing manual pagination.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#add-pagination-controls) Add pagination controls

We can add pagination controls to our table using the `<Button />` component and the `table.previousPage()`, `table.nextPage()` API methods.

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Button } from "@/components/ui/button"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  return (
    <div>
      <div className="rounded-md border">
        <Table>
          { // .... }
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
        >
          Next
        </Button>
      </div>
    </div>
  )
}
```

Copy

See [Reusable Components](https://ui.shadcn.com/docs/components/data-table#reusable-components) section for a more advanced pagination component.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#sorting) Sorting

Let's make the email column sortable.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable-1) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import * as React from "react"
import {
  ColumnDef,
  SortingState,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting,
    },
  })

  return (
    <div>
      <div className="rounded-md border">
        <Table>{ ... }</Table>
      </div>
    </div>
  )
}
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#make-header-cell-sortable) Make header cell sortable

We can now update the `email` header cell to add sorting controls.

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"

export const columns: ColumnDef<Payment>[] = [\
  {\
    accessorKey: "email",\
    header: ({ column }) => {\
      return (\
        <Button\
          variant="ghost"\
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}\
        >\
          Email\
          <ArrowUpDown className="ml-2 h-4 w-4" />\
        </Button>\
      )\
    },\
  },\
]
```

Copy

This will automatically sort the table (asc and desc) when the user toggles on the header cell.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#filtering) Filtering

Let's add a search input to filter emails in our table.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable-2) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import * as React from "react"
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
    },
  })

  return (
    <div>
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter emails..."
          value={(table.getColumn("email")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("email")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
      </div>
      <div className="rounded-md border">
        <Table>{ ... }</Table>
      </div>
    </div>
  )
}
```

Copy

Filtering is now enabled for the `email` column. You can add filters to other columns as well. See the [filtering docs](https://tanstack.com/table/v8/docs/guide/filters) for more information on customizing filters.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#visibility) Visibility

Adding column visibility is fairly simple using `@tanstack/react-table` visibility API.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable-3) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import * as React from "react"
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({})

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
    },
  })

  return (
    <div>
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter emails..."
          value={table.getColumn("email")?.getFilterValue() as string}
          onChange={(event) =>
            table.getColumn("email")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="ml-auto">
              Columns
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter(
                (column) => column.getCanHide()
              )
              .map((column) => {
                return (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize"
                    checked={column.getIsVisible()}
                    onCheckedChange={(value) =>
                      column.toggleVisibility(!!value)
                    }
                  >
                    {column.id}
                  </DropdownMenuCheckboxItem>
                )
              })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <div className="rounded-md border">
        <Table>{ ... }</Table>
      </div>
    </div>
  )
}
```

Copy

This adds a dropdown menu that you can use to toggle column visibility.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#row-selection) Row Selection

Next, we're going to add row selection to our table.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-column-definitions) Update column definitions

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { ColumnDef } from "@tanstack/react-table"

import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"

export const columns: ColumnDef<Payment>[] = [\
  {\
    id: "select",\
    header: ({ table }) => (\
      <Checkbox\
        checked={\
          table.getIsAllPageRowsSelected() ||\
          (table.getIsSomePageRowsSelected() && "indeterminate")\
        }\
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}\
        aria-label="Select all"\
      />\
    ),\
    cell: ({ row }) => (\
      <Checkbox\
        checked={row.getIsSelected()}\
        onCheckedChange={(value) => row.toggleSelected(!!value)}\
        aria-label="Select row"\
      />\
    ),\
    enableSorting: false,\
    enableHiding: false,\
  },\
]
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable-4) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  })

  return (
    <div>
      <div className="rounded-md border">
        <Table />
      </div>
    </div>
  )
}
```

Copy

This adds a checkbox to each row and a checkbox in the header to select all rows.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#show-selected-rows) Show selected rows

You can show the number of selected rows using the `table.getFilteredSelectedRowModel()` API.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<div className="flex-1 text-sm text-muted-foreground">
  {table.getFilteredSelectedRowModel().rows.length} of{" "}
  {table.getFilteredRowModel().rows.length} row(s) selected.
</div>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#reusable-components) Reusable Components

Here are some components you can use to build your data tables. This is from the [Tasks](https://ui.shadcn.com/examples/tasks) demo.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#column-header) Column header

Make any column header sortable and hideable.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Column } from "@tanstack/react-table"
import { ArrowDown, ArrowUp, ChevronsUpDown, EyeOff } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface DataTableColumnHeaderProps<TData, TValue>
  extends React.HTMLAttributes<HTMLDivElement> {
  column: Column<TData, TValue>
  title: string
}

export function DataTableColumnHeader<TData, TValue>({
  column,
  title,
  className,
}: DataTableColumnHeaderProps<TData, TValue>) {
  if (!column.getCanSort()) {
    return <div className={cn(className)}>{title}</div>
  }

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="-ml-3 h-8 data-[state=open]:bg-accent"
          >
            <span>{title}</span>
            {column.getIsSorted() === "desc" ? (
              <ArrowDown />
            ) : column.getIsSorted() === "asc" ? (
              <ArrowUp />
            ) : (
              <ChevronsUpDown />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem onClick={() => column.toggleSorting(false)}>
            <ArrowUp className="h-3.5 w-3.5 text-muted-foreground/70" />
            Asc
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => column.toggleSorting(true)}>
            <ArrowDown className="h-3.5 w-3.5 text-muted-foreground/70" />
            Desc
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => column.toggleVisibility(false)}>
            <EyeOff className="h-3.5 w-3.5 text-muted-foreground/70" />
            Hide
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
```

Copy

Expand

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export const columns = [\
  {\
    accessorKey: "email",\
    header: ({ column }) => (\
      <DataTableColumnHeader column={column} title="Email" />\
    ),\
  },\
]
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#pagination-1) Pagination

Add pagination controls to your table including page size and selection count.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Table } from "@tanstack/react-table"
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface DataTablePaginationProps<TData> {
  table: Table<TData>
}

export function DataTablePagination<TData>({
  table,
}: DataTablePaginationProps<TData>) {
  return (
    <div className="flex items-center justify-between px-2">
      <div className="flex-1 text-sm text-muted-foreground">
        {table.getFilteredSelectedRowModel().rows.length} of{" "}
        {table.getFilteredRowModel().rows.length} row(s) selected.
      </div>
      <div className="flex items-center space-x-6 lg:space-x-8">
        <div className="flex items-center space-x-2">
          <p className="text-sm font-medium">Rows per page</p>
          <Select
            value={`${table.getState().pagination.pageSize}`}
            onValueChange={(value) => {
              table.setPageSize(Number(value))
            }}
          >
            <SelectTrigger className="h-8 w-[70px]">
              <SelectValue placeholder={table.getState().pagination.pageSize} />
            </SelectTrigger>
            <SelectContent side="top">
              {[10, 20, 30, 40, 50].map((pageSize) => (
                <SelectItem key={pageSize} value={`${pageSize}`}>
                  {pageSize}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex w-[100px] items-center justify-center text-sm font-medium">
          Page {table.getState().pagination.pageIndex + 1} of{" "}
          {table.getPageCount()}
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            className="hidden h-8 w-8 p-0 lg:flex"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
          >
            <span className="sr-only">Go to first page</span>
            <ChevronsLeft />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 p-0"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <span className="sr-only">Go to previous page</span>
            <ChevronLeft />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 p-0"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <span className="sr-only">Go to next page</span>
            <ChevronRight />
          </Button>
          <Button
            variant="outline"
            className="hidden h-8 w-8 p-0 lg:flex"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
          >
            <span className="sr-only">Go to last page</span>
            <ChevronsRight />
          </Button>
        </div>
      </div>
    </div>
  )
}
```

Copy

Expand

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<DataTablePagination table={table} />
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#column-toggle) Column toggle

A component to toggle column visibility.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { DropdownMenuTrigger } from "@radix-ui/react-dropdown-menu"
import { Table } from "@tanstack/react-table"
import { Settings2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu"

interface DataTableViewOptionsProps<TData> {
  table: Table<TData>
}

export function DataTableViewOptions<TData>({
  table,
}: DataTableViewOptionsProps<TData>) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="ml-auto hidden h-8 lg:flex"
        >
          <Settings2 />
          View
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[150px]">
        <DropdownMenuLabel>Toggle columns</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {table
          .getAllColumns()
          .filter(
            (column) =>
              typeof column.accessorFn !== "undefined" && column.getCanHide()
          )
          .map((column) => {
            return (
              <DropdownMenuCheckboxItem
                key={column.id}
                className="capitalize"
                checked={column.getIsVisible()}
                onCheckedChange={(value) => column.toggleVisibility(!!value)}
              >
                {column.id}
              </DropdownMenuCheckboxItem>
            )
          })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

Copy

Expand

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<DataTableViewOptions table={table} />
```

Copy

[Context Menu](https://ui.shadcn.com/docs/components/context-menu) [Date Picker](https://ui.shadcn.com/docs/components/date-picker)

On This Page

- [Introduction](https://ui.shadcn.com/docs/components/data-table#introduction)
- [Table of Contents](https://ui.shadcn.com/docs/components/data-table#table-of-contents)
- [Installation](https://ui.shadcn.com/docs/components/data-table#installation)
- [Prerequisites](https://ui.shadcn.com/docs/components/data-table#prerequisites)
- [Project Structure](https://ui.shadcn.com/docs/components/data-table#project-structure)
- [Basic Table](https://ui.shadcn.com/docs/components/data-table#basic-table)
  - [Column Definitions](https://ui.shadcn.com/docs/components/data-table#column-definitions)
  - [<DataTable /> component](https://ui.shadcn.com/docs/components/data-table#datatable--component)
  - [Render the table](https://ui.shadcn.com/docs/components/data-table#render-the-table)
- [Cell Formatting](https://ui.shadcn.com/docs/components/data-table#cell-formatting)
  - [Update columns definition](https://ui.shadcn.com/docs/components/data-table#update-columns-definition)
- [Row Actions](https://ui.shadcn.com/docs/components/data-table#row-actions)
  - [Update columns definition](https://ui.shadcn.com/docs/components/data-table#update-columns-definition-1)
- [Pagination](https://ui.shadcn.com/docs/components/data-table#pagination)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable)
  - [Add pagination controls](https://ui.shadcn.com/docs/components/data-table#add-pagination-controls)
- [Sorting](https://ui.shadcn.com/docs/components/data-table#sorting)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable-1)
  - [Make header cell sortable](https://ui.shadcn.com/docs/components/data-table#make-header-cell-sortable)
- [Filtering](https://ui.shadcn.com/docs/components/data-table#filtering)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable-2)
- [Visibility](https://ui.shadcn.com/docs/components/data-table#visibility)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable-3)
- [Row Selection](https://ui.shadcn.com/docs/components/data-table#row-selection)
  - [Update column definitions](https://ui.shadcn.com/docs/components/data-table#update-column-definitions)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable-4)
  - [Show selected rows](https://ui.shadcn.com/docs/components/data-table#show-selected-rows)
- [Reusable Components](https://ui.shadcn.com/docs/components/data-table#reusable-components)
  - [Column header](https://ui.shadcn.com/docs/components/data-table#column-header)
  - [Pagination](https://ui.shadcn.com/docs/components/data-table#pagination-1)
  - [Column toggle](https://ui.shadcn.com/docs/components/data-table#column-toggle)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Input OTP Component
[Docs](https://ui.shadcn.com/docs)

Input OTP

# Input OTP

Accessible one-time password component with copy paste functionality.

[Docs](https://input-otp.rodz.dev/)

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/input-otp\#about) About

Input OTP is built on top of [input-otp](https://github.com/guilhermerodz/input-otp) by [@guilherme\_rodz](https://twitter.com/guilherme_rodz).

## [Link to section](https://ui.shadcn.com/docs/components/input-otp\#installation) Installation

CLIManual

### Run the following command:

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add input-otp

```

Copy

### Update `tailwind.config.js`

Add the following animations to your `tailwind.config.js` file:

tailwind.config.js

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      keyframes: {
        "caret-blink": {
          "0%,70%,100%": { opacity: "1" },
          "20%,50%": { opacity: "0" },
        },
      },
      animation: {
        "caret-blink": "caret-blink 1.25s ease-out infinite",
      },
    },
  },
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/input-otp\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<InputOTP maxLength={6}>
  <InputOTPGroup>
    <InputOTPSlot index={0} />
    <InputOTPSlot index={1} />
    <InputOTPSlot index={2} />
  </InputOTPGroup>
  <InputOTPSeparator />
  <InputOTPGroup>
    <InputOTPSlot index={3} />
    <InputOTPSlot index={4} />
    <InputOTPSlot index={5} />
  </InputOTPGroup>
</InputOTP>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/input-otp\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/input-otp\#pattern) Pattern

Use the `pattern` prop to define a custom pattern for the OTP input.

PreviewCode

Style: New York

Open in Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { REGEXP_ONLY_DIGITS_AND_CHARS } from "input-otp"

...

<InputOTP
  maxLength={6}
  pattern={REGEXP_ONLY_DIGITS_AND_CHARS}
>
  <InputOTPGroup>
    <InputOTPSlot index={0} />
    {/* ... */}
  </InputOTPGroup>
</InputOTP>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/input-otp\#separator) Separator

You can use the `<InputOTPSeparator />` component to add a separator between the input groups.

PreviewCode

Style: New York

Open in Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from "@/components/ui/input-otp"

...

<InputOTP maxLength={4}>
  <InputOTPGroup>
    <InputOTPSlot index={0} />
    <InputOTPSlot index={1} />
  </InputOTPGroup>
  <InputOTPSeparator />
  <InputOTPGroup>
    <InputOTPSlot index={2} />
    <InputOTPSlot index={3} />
  </InputOTPGroup>
</InputOTP>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/input-otp\#controlled) Controlled

You can use the `value` and `onChange` props to control the input value.

PreviewCode

Style: New York

Copy

Enter your one-time password.

### [Link to section](https://ui.shadcn.com/docs/components/input-otp\#form) Form

PreviewCode

Style: New York

Copy

One-Time Password

Please enter the one-time password sent to your phone.

Submit

## [Link to section](https://ui.shadcn.com/docs/components/input-otp\#changelog) Changelog

### [Link to section](https://ui.shadcn.com/docs/components/input-otp\#2024-03-19-composition) 2024-03-19 Composition

We've made some updates and replaced the render props pattern with composition. Here's how to update your code if you prefer the composition pattern.

**Note:** You are not required to update your code if you are using the
`render` prop. It is still supported.

### Update to the latest version of `input-otp`.

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm add input-otp@latest

```

Copy

### Update `input-otp.tsx`

input-otp.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
- import { OTPInput, SlotProps } from "input-otp"
+ import { OTPInput, OTPInputContext } from "input-otp"

 const InputOTPSlot = React.forwardRef<
   React.ElementRef<"div">,
-   SlotProps & React.ComponentPropsWithoutRef<"div">
-  >(({ char, hasFakeCaret, isActive, className, ...props }, ref) => {
+   React.ComponentPropsWithoutRef<"div"> & { index: number }
+  >(({ index, className, ...props }, ref) => {
+   const inputOTPContext = React.useContext(OTPInputContext)
+   const { char, hasFakeCaret, isActive } = inputOTPContext.slots[index]
```

Copy

### Then replace the `render` prop in your code.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<InputOTP maxLength={6}>
  <InputOTPGroup>
    <InputOTPSlot index={0} />
    <InputOTPSlot index={1} />
    <InputOTPSlot index={2} />
  </InputOTPGroup>
  <InputOTPSeparator />
  <InputOTPGroup>
    <InputOTPSlot index={3} />
    <InputOTPSlot index={4} />
    <InputOTPSlot index={5} />
  </InputOTPGroup>
</InputOTP>
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/input-otp\#2024-03-19-disabled) 2024-03-19 Disabled

To add a disabled state to the input, update `<InputOTP />` as follows:

input-otp.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const InputOTP = React.forwardRef<
  React.ElementRef<typeof OTPInput>,
  React.ComponentPropsWithoutRef<typeof OTPInput>
>(({ className, containerClassName, ...props }, ref) => (
  <OTPInput
    ref={ref}
    containerClassName={cn(
      "flex items-center gap-2 has-[:disabled]:opacity-50",
      containerClassName
    )}
    className={cn("disabled:cursor-not-allowed", className)}
    {...props}
  />
))
InputOTP.displayName = "InputOTP"
```

Copy

[Input](https://ui.shadcn.com/docs/components/input) [Label](https://ui.shadcn.com/docs/components/label)

On This Page

- [About](https://ui.shadcn.com/docs/components/input-otp#about)
- [Installation](https://ui.shadcn.com/docs/components/input-otp#installation)
- [Usage](https://ui.shadcn.com/docs/components/input-otp#usage)
- [Examples](https://ui.shadcn.com/docs/components/input-otp#examples)
  - [Pattern](https://ui.shadcn.com/docs/components/input-otp#pattern)
  - [Separator](https://ui.shadcn.com/docs/components/input-otp#separator)
  - [Controlled](https://ui.shadcn.com/docs/components/input-otp#controlled)
  - [Form](https://ui.shadcn.com/docs/components/input-otp#form)
- [Changelog](https://ui.shadcn.com/docs/components/input-otp#changelog)
  - [2024-03-19 Composition](https://ui.shadcn.com/docs/components/input-otp#2024-03-19-composition)
  - [2024-03-19 Disabled](https://ui.shadcn.com/docs/components/input-otp#2024-03-19-disabled)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Custom Scroll Area
[Docs](https://ui.shadcn.com/docs)

Scroll-area

# Scroll-area

Augments native scroll functionality for custom, cross-browser styling.

[Docs](https://www.radix-ui.com/docs/primitives/components/scroll-area) [API Reference](https://www.radix-ui.com/docs/primitives/components/scroll-area#api-reference)

PreviewCode

Style: New York

Open in Copy

#### Tags

v1.2.0-beta.50

v1.2.0-beta.49

v1.2.0-beta.48

v1.2.0-beta.47

v1.2.0-beta.46

v1.2.0-beta.45

v1.2.0-beta.44

v1.2.0-beta.43

v1.2.0-beta.42

v1.2.0-beta.41

v1.2.0-beta.40

v1.2.0-beta.39

v1.2.0-beta.38

v1.2.0-beta.37

v1.2.0-beta.36

v1.2.0-beta.35

v1.2.0-beta.34

v1.2.0-beta.33

v1.2.0-beta.32

v1.2.0-beta.31

v1.2.0-beta.30

v1.2.0-beta.29

v1.2.0-beta.28

v1.2.0-beta.27

v1.2.0-beta.26

v1.2.0-beta.25

v1.2.0-beta.24

v1.2.0-beta.23

v1.2.0-beta.22

v1.2.0-beta.21

v1.2.0-beta.20

v1.2.0-beta.19

v1.2.0-beta.18

v1.2.0-beta.17

v1.2.0-beta.16

v1.2.0-beta.15

v1.2.0-beta.14

v1.2.0-beta.13

v1.2.0-beta.12

v1.2.0-beta.11

v1.2.0-beta.10

v1.2.0-beta.9

v1.2.0-beta.8

v1.2.0-beta.7

v1.2.0-beta.6

v1.2.0-beta.5

v1.2.0-beta.4

v1.2.0-beta.3

v1.2.0-beta.2

v1.2.0-beta.1

## [Link to section](https://ui.shadcn.com/docs/components/scroll-area\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add scroll-area

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/scroll-area\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { ScrollArea } from "@/components/ui/scroll-area"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ScrollArea className="h-[200px] w-[350px] rounded-md border p-4">
  Jokester began sneaking into the castle in the middle of the night and leaving
  jokes all over the place: under the king's pillow, in his soup, even in the
  royal toilet. The king was furious, but he couldn't seem to stop Jokester. And
  then, one day, the people of the kingdom discovered that the jokes left by
  Jokester were so funny that they couldn't help but laugh. And once they
  started laughing, they couldn't stop.
</ScrollArea>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/scroll-area\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/scroll-area\#horizontal-scrolling) Horizontal Scrolling

PreviewCode

Style: New York

Copy

![Photo by Ornella Binni](https://ui.shadcn.com/_next/image?url=https%3A%2F%2Fimages.unsplash.com%2Fphoto-1465869185982-5a1a7522cbcb%3Fauto%3Dformat%26fit%3Dcrop%26w%3D300%26q%3D80&w=640&q=75)

Photo by Ornella Binni

![Photo by Tom Byrom](https://ui.shadcn.com/_next/image?url=https%3A%2F%2Fimages.unsplash.com%2Fphoto-1548516173-3cabfa4607e9%3Fauto%3Dformat%26fit%3Dcrop%26w%3D300%26q%3D80&w=640&q=75)

Photo by Tom Byrom

![Photo by Vladimir Malyavko](https://ui.shadcn.com/_next/image?url=https%3A%2F%2Fimages.unsplash.com%2Fphoto-1494337480532-3725c85fd2ab%3Fauto%3Dformat%26fit%3Dcrop%26w%3D300%26q%3D80&w=640&q=75)

Photo by Vladimir Malyavko

[Resizable](https://ui.shadcn.com/docs/components/resizable) [Select](https://ui.shadcn.com/docs/components/select)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/scroll-area#installation)
- [Usage](https://ui.shadcn.com/docs/components/scroll-area#usage)
- [Examples](https://ui.shadcn.com/docs/components/scroll-area#examples)
  - [Horizontal Scrolling](https://ui.shadcn.com/docs/components/scroll-area#horizontal-scrolling)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Toggle Group Buttons
[Docs](https://ui.shadcn.com/docs)

Toggle Group

# Toggle Group

A set of two-state buttons that can be toggled on or off.

[Docs](https://www.radix-ui.com/docs/primitives/components/toggle-group) [API Reference](https://www.radix-ui.com/docs/primitives/components/toggle-group#api-reference)

PreviewCode

Style: New York

Open in Copy

## [Link to section](https://ui.shadcn.com/docs/components/toggle-group\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add toggle-group

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/toggle-group\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ToggleGroup type="single">
  <ToggleGroupItem value="a">A</ToggleGroupItem>
  <ToggleGroupItem value="b">B</ToggleGroupItem>
  <ToggleGroupItem value="c">C</ToggleGroupItem>
</ToggleGroup>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/toggle-group\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/toggle-group\#default) Default

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/toggle-group\#outline) Outline

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/toggle-group\#single) Single

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/toggle-group\#small) Small

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/toggle-group\#large) Large

PreviewCode

Style: New York

Open in Copy

### [Link to section](https://ui.shadcn.com/docs/components/toggle-group\#disabled) Disabled

PreviewCode

Style: New York

Open in Copy

[Toggle](https://ui.shadcn.com/docs/components/toggle) [Tooltip](https://ui.shadcn.com/docs/components/tooltip)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/toggle-group#installation)
- [Usage](https://ui.shadcn.com/docs/components/toggle-group#usage)
- [Examples](https://ui.shadcn.com/docs/components/toggle-group#examples)
  - [Default](https://ui.shadcn.com/docs/components/toggle-group#default)
  - [Outline](https://ui.shadcn.com/docs/components/toggle-group#outline)
  - [Single](https://ui.shadcn.com/docs/components/toggle-group#single)
  - [Small](https://ui.shadcn.com/docs/components/toggle-group#small)
  - [Large](https://ui.shadcn.com/docs/components/toggle-group#large)
  - [Disabled](https://ui.shadcn.com/docs/components/toggle-group#disabled)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Date Picker Component
[Docs](https://ui.shadcn.com/docs)

Date Picker

# Date Picker

A date picker component with range and presets.

PreviewCode

Style: New York

Open in Copy

Loading...

## [Link to section](https://ui.shadcn.com/docs/components/date-picker\#installation) Installation

The Date Picker is built using a composition of the `<Popover />` and the `<Calendar />` components.

See installation instructions for the [Popover](https://ui.shadcn.com/docs/components/popover#installation) and the [Calendar](https://ui.shadcn.com/docs/components/calendar#installation) components.

## [Link to section](https://ui.shadcn.com/docs/components/date-picker\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import * as React from "react"
import { format } from "date-fns"
import { Calendar as CalendarIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

export function DatePickerDemo() {
  const [date, setDate] = React.useState<Date>()

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={"outline"}
          className={cn(
            "w-[280px] justify-start text-left font-normal",
            !date && "text-muted-foreground"
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, "PPP") : <span>Pick a date</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <Calendar
          mode="single"
          selected={date}
          onSelect={setDate}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  )
}
```

Copy

See the [React DayPicker](https://react-day-picker.js.org/) documentation for more information.

## [Link to section](https://ui.shadcn.com/docs/components/date-picker\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/date-picker\#date-picker) Date Picker

PreviewCode

Style: New York

Open in Copy

Loading...

### [Link to section](https://ui.shadcn.com/docs/components/date-picker\#date-range-picker) Date Range Picker

PreviewCode

Style: New York

Open in Copy

Loading...

### [Link to section](https://ui.shadcn.com/docs/components/date-picker\#with-presets) With Presets

PreviewCode

Style: New York

Open in Copy

Loading...

### [Link to section](https://ui.shadcn.com/docs/components/date-picker\#form) Form

PreviewCode

Style: New York

Copy

Loading...

[Data Table](https://ui.shadcn.com/docs/components/data-table) [Dialog](https://ui.shadcn.com/docs/components/dialog)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/date-picker#installation)
- [Usage](https://ui.shadcn.com/docs/components/date-picker#usage)
- [Examples](https://ui.shadcn.com/docs/components/date-picker#examples)
  - [Date Picker](https://ui.shadcn.com/docs/components/date-picker#date-picker)
  - [Date Range Picker](https://ui.shadcn.com/docs/components/date-picker#date-range-picker)
  - [With Presets](https://ui.shadcn.com/docs/components/date-picker#with-presets)
  - [Form](https://ui.shadcn.com/docs/components/date-picker#form)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Dropdown Menu Guide
[Docs](https://ui.shadcn.com/docs)

Dropdown Menu

# Dropdown Menu

Displays a menu to the user — such as a set of actions or functions — triggered by a button.

[Docs](https://www.radix-ui.com/docs/primitives/components/dropdown-menu) [API Reference](https://www.radix-ui.com/docs/primitives/components/dropdown-menu#api-reference)

PreviewCode

Style: New York

Open in Copy

Open

## [Link to section](https://ui.shadcn.com/docs/components/dropdown-menu\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add dropdown-menu

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/dropdown-menu\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<DropdownMenu>
  <DropdownMenuTrigger>Open</DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Billing</DropdownMenuItem>
    <DropdownMenuItem>Team</DropdownMenuItem>
    <DropdownMenuItem>Subscription</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/dropdown-menu\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/dropdown-menu\#checkboxes) Checkboxes

PreviewCode

Style: New York

Open in Copy

Open

### [Link to section](https://ui.shadcn.com/docs/components/dropdown-menu\#radio-group) Radio Group

PreviewCode

Style: New York

Open in Copy

Open

## [Link to section](https://ui.shadcn.com/docs/components/dropdown-menu\#changelog) Changelog

### [Link to section](https://ui.shadcn.com/docs/components/dropdown-menu\#2024-10-16-classes-for-icons) 2024-10-16 Classes for icons

Added `gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0` to the `DropdownMenuItem` to automatically style icon inside the dropdown menu item.

Add the following classes to the `DropdownMenuItem` in your `dropdown-menu.tsx` file.

dropdown-menu.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const DropdownMenuItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item> & {
    inset?: boolean
  }
>(({ className, inset, ...props }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={cn(
      "relative ... gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
      inset && "pl-8",
      className
    )}
    {...props}
  />
))
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/dropdown-menu\#2024-10-25-classes-for-dropdownmenusubtrigger-) 2024-10-25 Classes for `<DropdownMenuSubTrigger />`

Added `gap-2 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0` to the `<DropdownMenuSubTrigger />` to automatically style icon inside.

Add the following classes to the `cva` call in your `dropdown-menu.tsx` file.

dropdown-menu.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<DropdownMenuPrimitive.SubTrigger
  ref={ref}
  className={cn(
    "flex cursor-default gap-2 select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none focus:bg-accent data-[state=open]:bg-accent [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
    inset && "pl-8",
    className
  )}
  {...props}
>
  {/* ... */}
</DropdownMenuPrimitive.SubTrigger>
```

Copy

[Drawer](https://ui.shadcn.com/docs/components/drawer) [Form](https://ui.shadcn.com/docs/components/form)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/dropdown-menu#installation)
- [Usage](https://ui.shadcn.com/docs/components/dropdown-menu#usage)
- [Examples](https://ui.shadcn.com/docs/components/dropdown-menu#examples)
  - [Checkboxes](https://ui.shadcn.com/docs/components/dropdown-menu#checkboxes)
  - [Radio Group](https://ui.shadcn.com/docs/components/dropdown-menu#radio-group)
- [Changelog](https://ui.shadcn.com/docs/components/dropdown-menu#changelog)
  - [2024-10-16 Classes for icons](https://ui.shadcn.com/docs/components/dropdown-menu#2024-10-16-classes-for-icons)
  - [2024-10-25 Classes for <DropdownMenuSubTrigger />](https://ui.shadcn.com/docs/components/dropdown-menu#2024-10-25-classes-for-dropdownmenusubtrigger-)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Alert Dialog
[Docs](https://ui.shadcn.com/docs)

Alert Dialog

# Alert Dialog

A modal dialog that interrupts the user with important content and expects a response.

[Docs](https://www.radix-ui.com/docs/primitives/components/alert-dialog) [API Reference](https://www.radix-ui.com/docs/primitives/components/alert-dialog#api-reference)

PreviewCode

Style: New York

Open in Copy

Show Dialog

## [Link to section](https://ui.shadcn.com/docs/components/alert-dialog\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add alert-dialog

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/alert-dialog\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<AlertDialog>
  <AlertDialogTrigger>Open</AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
      <AlertDialogDescription>
        This action cannot be undone. This will permanently delete your account
        and remove your data from our servers.
      </AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel>Cancel</AlertDialogCancel>
      <AlertDialogAction>Continue</AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```

Copy

[Alert](https://ui.shadcn.com/docs/components/alert) [Aspect Ratio](https://ui.shadcn.com/docs/components/aspect-ratio)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/alert-dialog#installation)
- [Usage](https://ui.shadcn.com/docs/components/alert-dialog#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Hover Card Component
[Docs](https://ui.shadcn.com/docs)

Hover Card

# Hover Card

For sighted users to preview content available behind a link.

[Docs](https://www.radix-ui.com/docs/primitives/components/hover-card) [API Reference](https://www.radix-ui.com/docs/primitives/components/hover-card#api-reference)

PreviewCode

Style: New York

Open in Copy

@nextjs

## [Link to section](https://ui.shadcn.com/docs/components/hover-card\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add hover-card

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/hover-card\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<HoverCard>
  <HoverCardTrigger>Hover</HoverCardTrigger>
  <HoverCardContent>
    The React Framework – created and maintained by @vercel.
  </HoverCardContent>
</HoverCard>
```

Copy

[Form](https://ui.shadcn.com/docs/components/form) [Input](https://ui.shadcn.com/docs/components/input)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/hover-card#installation)
- [Usage](https://ui.shadcn.com/docs/components/hover-card#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Radio Group
[Docs](https://ui.shadcn.com/docs)

Radio Group

# Radio Group

A set of checkable buttons—known as radio buttons—where no more than one of the buttons can be checked at a time.

[Docs](https://www.radix-ui.com/docs/primitives/components/radio-group) [API Reference](https://www.radix-ui.com/docs/primitives/components/radio-group#api-reference)

PreviewCode

Style: New York

Open in Copy

Default

Comfortable

Compact

## [Link to section](https://ui.shadcn.com/docs/components/radio-group\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add radio-group

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/radio-group\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<RadioGroup defaultValue="option-one">
  <div className="flex items-center space-x-2">
    <RadioGroupItem value="option-one" id="option-one" />
    <Label htmlFor="option-one">Option One</Label>
  </div>
  <div className="flex items-center space-x-2">
    <RadioGroupItem value="option-two" id="option-two" />
    <Label htmlFor="option-two">Option Two</Label>
  </div>
</RadioGroup>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/radio-group\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/radio-group\#form) Form

PreviewCode

Style: New York

Copy

Notify me about...

All new messages

Direct messages and mentions

Nothing

Submit

[Progress](https://ui.shadcn.com/docs/components/progress) [Resizable](https://ui.shadcn.com/docs/components/resizable)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/radio-group#installation)
- [Usage](https://ui.shadcn.com/docs/components/radio-group#usage)
- [Examples](https://ui.shadcn.com/docs/components/radio-group#examples)
  - [Form](https://ui.shadcn.com/docs/components/radio-group#form)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Context Menu Guide
[Docs](https://ui.shadcn.com/docs)

Context Menu

# Context Menu

Displays a menu to the user — such as a set of actions or functions — triggered by a button.

[Docs](https://www.radix-ui.com/docs/primitives/components/context-menu) [API Reference](https://www.radix-ui.com/docs/primitives/components/context-menu#api-reference)

PreviewCode

Style: New York

Open in Copy

Right click here

## [Link to section](https://ui.shadcn.com/docs/components/context-menu\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add context-menu

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/context-menu\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<ContextMenu>
  <ContextMenuTrigger>Right click</ContextMenuTrigger>
  <ContextMenuContent>
    <ContextMenuItem>Profile</ContextMenuItem>
    <ContextMenuItem>Billing</ContextMenuItem>
    <ContextMenuItem>Team</ContextMenuItem>
    <ContextMenuItem>Subscription</ContextMenuItem>
  </ContextMenuContent>
</ContextMenu>
```

Copy

[Command](https://ui.shadcn.com/docs/components/command) [Data Table](https://ui.shadcn.com/docs/components/data-table)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/context-menu#installation)
- [Usage](https://ui.shadcn.com/docs/components/context-menu#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Aspect Ratio Component
[Docs](https://ui.shadcn.com/docs)

Aspect Ratio

# Aspect Ratio

Displays content within a desired ratio.

[Docs](https://www.radix-ui.com/docs/primitives/components/aspect-ratio) [API Reference](https://www.radix-ui.com/docs/primitives/components/aspect-ratio#api-reference)

PreviewCode

Style: New York

Open in Copy

![Photo by Drew Beamer](https://ui.shadcn.com/_next/image?url=https%3A%2F%2Fimages.unsplash.com%2Fphoto-1588345921523-c2dcdb7f1dcd%3Fw%3D800%26dpr%3D2%26q%3D80&w=3840&q=75)

## [Link to section](https://ui.shadcn.com/docs/components/aspect-ratio\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add aspect-ratio

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/aspect-ratio\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import Image from "next/image"

import { AspectRatio } from "@/components/ui/aspect-ratio"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<div className="w-[450px]">
  <AspectRatio ratio={16 / 9}>
    <Image src="..." alt="Image" className="rounded-md object-cover" />
  </AspectRatio>
</div>
```

Copy

[Alert Dialog](https://ui.shadcn.com/docs/components/alert-dialog) [Avatar](https://ui.shadcn.com/docs/components/avatar)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/aspect-ratio#installation)
- [Usage](https://ui.shadcn.com/docs/components/aspect-ratio#usage)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Navigation Menu Guide
[Docs](https://ui.shadcn.com/docs)

Navigation Menu

# Navigation Menu

A collection of links for navigating websites.

[Docs](https://www.radix-ui.com/docs/primitives/components/navigation-menu) [API Reference](https://www.radix-ui.com/docs/primitives/components/navigation-menu#api-reference)

PreviewCode

Style: New York

Copy

## [Link to section](https://ui.shadcn.com/docs/components/navigation-menu\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add navigation-menu

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/navigation-menu\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuIndicator,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  NavigationMenuViewport,
} from "@/components/ui/navigation-menu"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<NavigationMenu>
  <NavigationMenuList>
    <NavigationMenuItem>
      <NavigationMenuTrigger>Item One</NavigationMenuTrigger>
      <NavigationMenuContent>
        <NavigationMenuLink>Link</NavigationMenuLink>
      </NavigationMenuContent>
    </NavigationMenuItem>
  </NavigationMenuList>
</NavigationMenu>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/navigation-menu\#examples) Examples

### [Link to section](https://ui.shadcn.com/docs/components/navigation-menu\#link-component) Link Component

When using the Next.js `<Link />` component, you can use `navigationMenuTriggerStyle()` to apply the correct styles to the trigger.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { navigationMenuTriggerStyle } from "@/components/ui/navigation-menu"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<NavigationMenuItem>
  <Link href="/docs" legacyBehavior passHref>
    <NavigationMenuLink className={navigationMenuTriggerStyle()}>
      Documentation
    </NavigationMenuLink>
  </Link>
</NavigationMenuItem>
```

Copy

See also the [Radix UI documentation](https://www.radix-ui.com/docs/primitives/components/navigation-menu#with-client-side-routing) for handling client side routing.

[Menubar](https://ui.shadcn.com/docs/components/menubar) [Pagination](https://ui.shadcn.com/docs/components/pagination)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/navigation-menu#installation)
- [Usage](https://ui.shadcn.com/docs/components/navigation-menu#usage)
- [Examples](https://ui.shadcn.com/docs/components/navigation-menu#examples)
  - [Link Component](https://ui.shadcn.com/docs/components/navigation-menu#link-component)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## Responsive Invoice Table
[Docs](https://ui.shadcn.com/docs)

Table

# Table

A responsive table component.

PreviewCode

Style: New York

Open in Copy

| Invoice | Status | Method | Amount |
| --- | --- | --- | --- |
| INV001 | Paid | Credit Card | $250.00 |
| INV002 | Pending | PayPal | $150.00 |
| INV003 | Unpaid | Bank Transfer | $350.00 |
| INV004 | Paid | Credit Card | $450.00 |
| INV005 | Paid | PayPal | $550.00 |
| INV006 | Pending | Bank Transfer | $200.00 |
| INV007 | Unpaid | Credit Card | $300.00 |
| Total | $2,500.00 |

A list of your recent invoices.

## [Link to section](https://ui.shadcn.com/docs/components/table\#installation) Installation

CLIManual

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add table

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/table\#usage) Usage

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
```

Copy

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<Table>
  <TableCaption>A list of your recent invoices.</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead className="w-[100px]">Invoice</TableHead>
      <TableHead>Status</TableHead>
      <TableHead>Method</TableHead>
      <TableHead className="text-right">Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell className="font-medium">INV001</TableCell>
      <TableCell>Paid</TableCell>
      <TableCell>Credit Card</TableCell>
      <TableCell className="text-right">$250.00</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/table\#data-table) Data Table

You can use the `<Table />` component to build more complex data tables. Combine it with [@tanstack/react-table](https://tanstack.com/table/v8) to create tables with sorting, filtering and pagination.

See the [Data Table](https://ui.shadcn.com/docs/components/data-table) documentation for more information.

You can also see an example of a data table in the [Tasks](https://ui.shadcn.com/examples/tasks) demo.

[Switch](https://ui.shadcn.com/docs/components/switch) [Tabs](https://ui.shadcn.com/docs/components/tabs)

On This Page

- [Installation](https://ui.shadcn.com/docs/components/table#installation)
- [Usage](https://ui.shadcn.com/docs/components/table#usage)
- [Data Table](https://ui.shadcn.com/docs/components/table#data-table)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)

## 404 Error Page
# 404

## This page could not be found.
