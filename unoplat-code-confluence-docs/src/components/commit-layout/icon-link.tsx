import { Link } from "@tanstack/react-router";

import { cn } from "@/lib/utils";

interface IconLinkBaseProps {
  children: React.ReactNode;
  className?: string;
  compact?: boolean;
  icon?: React.ComponentType<{ className?: string }>;
}

interface IconLinkWithTo extends IconLinkBaseProps {
  to: string;
  href?: never;
}

interface IconLinkWithHref extends IconLinkBaseProps {
  href: string;
  to?: never;
  target?: string;
  rel?: string;
}

type IconLinkProps = IconLinkWithTo | IconLinkWithHref;

export function IconLink({
  children,
  className,
  compact = false,
  icon: Icon,
  ...props
}: IconLinkProps) {
  const classes = cn(
    className,
    "group relative isolate flex items-center rounded-lg px-2 py-0.5 text-[0.8125rem]/6 font-medium text-white/30 transition-colors hover:text-white/80",
    compact ? "gap-x-2" : "gap-x-3",
  );

  const content = (
    <>
      <span className="absolute inset-0 -z-10 scale-75 rounded-lg bg-white/5 opacity-0 transition group-hover:scale-100 group-hover:opacity-100" />
      {Icon && <Icon className="h-4 w-4 flex-none" />}
      <span className="self-baseline text-white">{children}</span>
    </>
  );

  if ("to" in props && props.to) {
    return (
      <Link to={props.to} className={classes}>
        {content}
      </Link>
    );
  }

  const { href, target, rel, ...rest } = props as IconLinkWithHref;
  return (
    <a href={href} target={target} rel={rel} className={classes} {...rest}>
      {content}
    </a>
  );
}
