import { createFileRoute } from "@tanstack/react-router";
import OnboardingPage from "../pages/OnboardingPage";

export const Route = createFileRoute("/_app/onboarding")({
  component: OnboardingPage,
  beforeLoad: () => ({ getTitle: () => "Onboarding" }),
});
