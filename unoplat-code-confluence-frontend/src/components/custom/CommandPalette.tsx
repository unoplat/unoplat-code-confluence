import { useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";
import {
  BookOpen,
  Code2,
  Cpu,
  Home,
  Monitor,
  Moon,
  Settings,
  Sun,
  Wrench,
} from "lucide-react";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";
import { useCommandPaletteStore } from "@/stores/useCommandPaletteStore";
import { useThemeStore } from "@/stores/useThemeStore";

export function CommandPalette() {
  const { isOpen, close, toggle } = useCommandPaletteStore();
  const { setTheme } = useThemeStore();
  const navigate = useNavigate();

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        toggle();
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [toggle]);

  return (
    <CommandDialog open={isOpen} onOpenChange={(v) => !v && close()}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Navigation">
          <CommandItem
            value="Go to Onboarding"
            keywords={["home", "start", "setup"]}
            onSelect={() => {
              void navigate({ to: "/onboarding" });
              close();
            }}
          >
            <Home />
            Go to Onboarding
          </CommandItem>
          <CommandItem
            value="Go to Operations Management"
            keywords={["operations", "manage", "dashboard"]}
            onSelect={() => {
              void navigate({ to: "/operationsManagement" });
              close();
            }}
          >
            <Cpu />
            Go to Operations Management
          </CommandItem>
          <CommandItem
            value="Go to Repository Operations"
            keywords={["repo", "repository", "git"]}
            onSelect={() => {
              void navigate({ to: "/repositoryOperations" });
              close();
            }}
          >
            <Code2 />
            Go to Repository Operations
          </CommandItem>
          <CommandItem
            value="Go to Settings"
            keywords={["preferences", "config", "options"]}
            onSelect={() => {
              void navigate({ to: "/settings" });
              close();
            }}
          >
            <Settings />
            Go to Settings
            <CommandShortcut>⌘,</CommandShortcut>
          </CommandItem>
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Settings">
          <CommandItem
            value="Tool Configuration"
            keywords={["tools", "configure", "setup"]}
            onSelect={() => {
              void navigate({ to: "/settings/tool-config" });
              close();
            }}
          >
            <Wrench />
            Tool Configuration
          </CommandItem>
          <CommandItem
            value="Model Providers"
            keywords={["ai", "llm", "models", "provider"]}
            onSelect={() => {
              void navigate({ to: "/settings/model-providers" });
              close();
            }}
          >
            <BookOpen />
            Model Providers
          </CommandItem>
          <CommandItem
            value="Developer Settings"
            keywords={["dev", "debug", "developer"]}
            onSelect={() => {
              void navigate({ to: "/settings/developer" });
              close();
            }}
          >
            <Code2 />
            Developer Settings
          </CommandItem>
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Theme">
          <CommandItem
            value="Light Mode"
            keywords={["light", "theme", "bright"]}
            onSelect={() => {
              setTheme("light");
              close();
            }}
          >
            <Sun />
            Light Mode
          </CommandItem>
          <CommandItem
            value="Dark Mode"
            keywords={["dark", "theme", "night"]}
            onSelect={() => {
              setTheme("dark");
              close();
            }}
          >
            <Moon />
            Dark Mode
          </CommandItem>
          <CommandItem
            value="System Theme"
            keywords={["system", "auto", "theme", "default"]}
            onSelect={() => {
              setTheme("system");
              close();
            }}
          >
            <Monitor />
            System Theme
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
