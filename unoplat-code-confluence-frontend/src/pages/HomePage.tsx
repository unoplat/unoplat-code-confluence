import React, { useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";

/**
 * HomePage Component
 *
 * This component redirects to the onboarding page, since we've moved
 * the GitHub token authentication to a popup modal.
 */
export default function HomePage(): React.ReactElement {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to the onboarding page
    navigate({ to: "/onboarding" });
  }, [navigate]);

  // Return empty div while redirecting
  return <div className="bg-background min-h-screen p-8" />;
}
