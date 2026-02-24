import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";
import { Globe, Linkedin } from "lucide-react";
import DiscordIcon from "@/assets/brands/discord-icon-svgrepo-com.svg?react";
import XIcon from "@/assets/brands/x-icon.svg?react";
import { BrandLogo } from "@/components/brand-logo";

export function baseOptions(): BaseLayoutProps {
  return {
    nav: {
      title: <BrandLogo className="h-6 w-auto" />,
      url: "https://www.unoplat.io",
    },
    githubUrl: "https://github.com/unoplat/unoplat-code-confluence",
    links: [
      {
        type: "main",
        text: "Changelog",
        url: "/changelog",
      },
      {
        type: "icon",
        text: "Website",
        label: "Unoplat Website",
        url: "https://www.unoplat.io",
        icon: <Globe className="size-5" />,
        external: true,
      },
      {
        type: "icon",
        text: "Discord",
        label: "Discord Community",
        url: "https://discord.gg/qe2nbQMnWB",
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
