import { createFileRoute } from '@tanstack/react-router';
import SettingsPage from '../pages/SettingsPage';

export const Route = createFileRoute('/_app/settings')({
  component: SettingsPage,
}); 