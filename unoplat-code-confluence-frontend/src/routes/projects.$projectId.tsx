import { createFileRoute, useParams } from '@tanstack/react-router'
import { ProjectDetails } from '../features/projects/project-details'

export const Route = createFileRoute('/projects/$projectId')({
  component: ProjectRoute,
})

function ProjectRoute(): JSX.Element {
  const { projectId } = useParams({ from: '/projects/$projectId' })
  
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Project Details</h2>
      <ProjectDetails projectId={projectId} />
    </div>
  )
} 