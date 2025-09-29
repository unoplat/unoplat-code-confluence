import { createFileRoute } from '@tanstack/react-router';
import ModelProvidersPage from '../pages/ModelProvidersPage';

export const Route = createFileRoute('/settings/model-providers')({
  beforeLoad: () => ({ getTitle: () => 'Model Providers' }),
  component: ModelProvidersPage,
});
