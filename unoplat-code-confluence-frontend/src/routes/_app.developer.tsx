// src/routes/_app.developer.tsx
import { createFileRoute } from '@tanstack/react-router'
import DeveloperModePage from '../pages/DeveloperModePage'

export const Route = createFileRoute('/_app/developer')({
  component: DeveloperModePage,
  beforeLoad: () => ({ getTitle: () => 'Developer Mode' }),
})