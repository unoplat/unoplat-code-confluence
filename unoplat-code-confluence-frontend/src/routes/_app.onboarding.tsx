import { createFileRoute } from '@tanstack/react-router';
import OnboardingPage from '../pages/OnboardingPage';
import { zodValidator, fallback } from '@tanstack/zod-adapter'
import { z } from 'zod'

const codeConfluenceSearchSchema = z.object({
  pageIndex: fallback(z.number(), 1).default(1),
  perPage: fallback(z.number(), 10).default(10),
  filterValues: fallback(
    z.record(z.union([z.string(), z.array(z.string()), z.null()]))
  , {}).default({}),
});


export const Route = createFileRoute('/_app/onboarding')({
  component: OnboardingPage,
  validateSearch: zodValidator(codeConfluenceSearchSchema),
  beforeLoad: () => ({ getTitle: () => 'Github Onboarding' }),
});
