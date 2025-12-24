import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";
import { Linkedin } from "lucide-react";
import DiscordIcon from "@/assets/brands/discord-icon-svgrepo-com.svg?react";
import XIcon from "@/assets/brands/x-icon.svg?react";

export function baseOptions(): BaseLayoutProps {
  return {
    nav: {
      title: "Unoplat Code Confluence",
    },
    githubUrl: "https://github.com/unoplat/unoplat-code-confluence",
    links: [
      {
        type: "icon",
        text: "Discord",
        label: "Discord Community",
        url: "https://discord.com/channels/1131597983058755675/1169968780953260106",
        icon: <DiscordIcon className="size-5" />,
        external: true,
      },
      {
        type: "icon",
        text: "LinkedIn",
        label: "LinkedIn Page",
        url: "https://www.linkedin.com/company/unoplat/",
        icon: <Linkedin />,
        external: true,
      },
      {
        type: "icon",
        text: "X",
        label: "X (Twitter)",
        url: "https://x.com/unoplatio",
        icon: <XIcon className="size-5" />,
        external: true,
      },
    ],
  };
}
