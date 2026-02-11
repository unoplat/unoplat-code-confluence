import logoLight from "@/assets/code-confluence-logo-light.svg";
import logoDark from "@/assets/code-confluence-logo-dark.svg";

interface BrandLogoProps {
  className?: string;
}

export function BrandLogo({ className = "h-8 w-auto" }: BrandLogoProps) {
  return (
    <>
      <img
        src={logoLight}
        alt="Unoplat Code Confluence"
        className={`block dark:hidden ${className}`}
      />
      <img
        src={logoDark}
        alt="Unoplat Code Confluence"
        className={`hidden dark:block ${className}`}
      />
    </>
  );
}
