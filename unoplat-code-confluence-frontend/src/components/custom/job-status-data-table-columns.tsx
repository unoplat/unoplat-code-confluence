import React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import type { FlattenedCodebaseRun, JobStatus } from '../../types';
import { DataTableColumnHeader } from '../data-table-column-header';
import { Button } from '../ui/button';
import { AlertCircle, CheckCircle, Clock, PauseCircle, RefreshCw } from 'lucide-react';

// Reusing the status icon and styles functions from the parent component
export const getStatusIcon = (status: JobStatus): React.ReactNode => {
  switch (status) {
    case 'COMPLETED':
      return <CheckCircle className="h-4 w-4 text-emerald-500" />;
    case 'FAILED':
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    case 'TIMED_OUT':
      return <Clock className="h-4 w-4 text-red-500" />;
    case 'SUBMITTED':
      return <Clock className="h-4 w-4 text-amber-500" />;
    case 'RUNNING':
      return <PauseCircle className="h-4 w-4 text-blue-500" />;
    case 'RETRYING':
      return <RefreshCw className="h-4 w-4 text-blue-500" />;
    default:
      return <Clock className="h-4 w-4 text-gray-500" />;
  }
};

export const getStatusStyles = (status: JobStatus): string => {
  switch (status) {
    case 'COMPLETED':
      return 'bg-emerald-100 text-emerald-800';
    case 'FAILED':
    case 'TIMED_OUT':
      return 'bg-red-100 text-red-800';
    case 'SUBMITTED':
      return 'bg-amber-100 text-amber-800';
    case 'RUNNING':
    case 'RETRYING':
      return 'bg-blue-100 text-blue-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

interface JobStatusDataTableColumnsProps {
  showFeedbackColumn: boolean;
  onSubmitFeedback: (run: FlattenedCodebaseRun) => void;
}

export function getJobStatusDataTableColumns({ 
  showFeedbackColumn, 
  onSubmitFeedback 
}: JobStatusDataTableColumnsProps): ColumnDef<FlattenedCodebaseRun>[] {
  const columns: ColumnDef<FlattenedCodebaseRun>[] = [
    {
      accessorKey: 'root_package',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Root Package" />
      ),
      cell: ({ row }): React.ReactNode => (
        <div className="flex items-center">
          <span className="text-sm font-normal text-primary">
            {row.original.root_package}
          </span>
        </div>
      ),
      meta: {
        label: 'Root Package',
        placeholder: 'Search package...',
        variant: 'text',
      },
      enableSorting: false,
    },
    {
      accessorKey: 'codebase_workflow_run_id',
      id: 'codebase_workflow_run_id',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Run ID" />
      ),
      cell: ({ row }): React.ReactNode => (
        <div className="flex items-center">
          <span className="text-sm font-normal">
            {row.original.codebase_workflow_run_id}
          </span>
        </div>
      ),
      enableSorting: false,
    },
    {
      accessorKey: 'codebase_status',
      id: 'codebase_status',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Status" />
      ),
      cell: ({ row }): React.ReactNode => (
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusStyles(
              row.original.codebase_status
            )}`}
          >
            {getStatusIcon(row.original.codebase_status)}
            {row.original.codebase_status}
          </span>
        </div>
      ),
      meta: {
        label: 'Status',
        variant: 'select',
        options: [
          { label: 'Submitted', value: 'SUBMITTED' },
          { label: 'Running', value: 'RUNNING' },
          { label: 'Completed', value: 'COMPLETED' },
          { label: 'Failed', value: 'FAILED' },
          { label: 'Timed Out', value: 'TIMED_OUT' },
          { label: 'Retrying', value: 'RETRYING' },
        ],
      },
      enableColumnFilter: true,
    },
    {
      accessorKey: 'codebase_started_at',
      id: 'codebase_started_at',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Started" />
      ),
      cell: ({ row }): React.ReactNode => {
        const date = new Date(row.original.codebase_started_at);
        return (
          <div className="flex flex-col">
            <span className="text-sm font-normal">
              {date.toLocaleString(undefined, {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
              })}
            </span>
          </div>
        );
      },
      enableSorting: false,
    },
    {
      accessorKey: 'codebase_completed_at',
      id: 'codebase_completed_at',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Completed" />
      ),
      cell: ({ row }): React.ReactNode => {
        if (!row.original.codebase_completed_at) {
          return <span className="text-sm text-muted-foreground">-</span>;
        }
        const date = new Date(row.original.codebase_completed_at);
        return (
          <div className="flex flex-col">
            <span className="text-sm font-normal">
              {date.toLocaleString(undefined, {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false
              })}
            </span>
          </div>
        );
      },
      enableSorting: false,
    },
  ];

  // Conditionally add the feedback column if needed
  if (showFeedbackColumn) {
    columns.push({
      id: 'codebase_feedback',
      header: ({ column }): React.ReactNode => (
        <DataTableColumnHeader column={column} title="Action" />
      ),
      cell: ({ row }): React.ReactNode => {
        // Extract potential issue tracking info
        const issueTracking = row.original.codebase_issue_tracking;
        const issueUrl = issueTracking?.issue_url;
        const issueNumber = issueTracking?.issue_number;
        
        console.log('issueUrl', issueUrl);
        console.log('issueNumber', issueNumber);
        // If feedback has been submitted, show issue number as a link
        if (issueUrl && issueNumber != null) {
          return (
            <a
              href={issueUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline flex items-center gap-1"
            >
              #{issueNumber}
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
            </a>
          );
        }
        
        // If feedback hasn't been submitted and status is FAILED, show submit button
        return row.original.codebase_status === 'FAILED' ? (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onSubmitFeedback(row.original)}
            className="text-xs"
          >
            Submit Feedback
          </Button>
        ) : null;
      },
      enableSorting: false,
      enableHiding: false,
    });
  }

  return columns;
}
