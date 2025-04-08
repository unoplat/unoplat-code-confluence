import { createFileRoute } from '@tanstack/react-router';
import OnboardingPage from '../pages/OnboardingPage';
import { Schema as S } from 'effect'

const codeConfluenceSearchSchema = S.standardSchemaV1(
  S.Struct({
    pageIndex: S.Number.pipe(
      S.optional,
      S.withDefaults({
        constructor: () => 1,
        decoding: () => 1,
      }),
    ),
    perPage: S.Number.pipe(
      S.optional,
      S.withDefaults({
        constructor: () => 10,
        decoding: () => 10,
      }),
    ),
    searchTerm: S.String.pipe(
      S.optional,
      S.withDefaults({
        constructor: () => '',
        decoding: () => '',
      }),
    ),
  }),
)

export const Route = createFileRoute('/_app/onboarding')({
  component: OnboardingPage,
  validateSearch: codeConfluenceSearchSchema,
});
