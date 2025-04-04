Below is a sample plan outlining the changes required per file. The goal is to “lift” your table state into the URL using TanStack Router’s search params so that pagination, sorting, filtering, and even row selection become shareable and bookmarkable. You’ll update your state initialization and change callbacks to read from and write to the router’s search parameters.

⸻

Plan to Integrate TanStack Router Search Params

1. File: src/hooks/use-data-table.ts

Changes Required:
	•	Import and Use Router:
Import useRouter from TanStack Router. Instead of only using local state with useState, initialize each state property (pagination, sorting, column filters, column visibility, row selection) from the router’s search parameters.
Example:

import { useRouter } from '@tanstack/router';


	•	State Initialization:
Change the initial state so that if the URL contains search parameters (e.g. ?pagination=...&sorting=...), they are used to initialize the table state. For example, replace:

const [sorting, setSorting] = useState<SortingState>(initialState?.sorting || []);

with something like:

const router = useRouter();
const urlSorting = router.state.search.sorting as SortingState | undefined;
const [sorting, setSorting] = useState<SortingState>(urlSorting || initialState?.sorting || []);


	•	Callback Updates:
In each state change handler (for pagination, sorting, filters, and row selection), update both the local state and use router.navigate to update the URL search parameters. For example:

const handlePaginationChange: OnChangeFn<PaginationState> = (updaterOrValue) => {
  setPagination((prev) => {
    const newValue = typeof updaterOrValue === 'function'
      ? updaterOrValue(prev)
      : updaterOrValue;
    if (onPaginationChange) onPaginationChange(newValue);
    // Update URL search params
    router.navigate({
      search: {
        ...router.state.search,
        pagination: newValue,
      },
    });
    return newValue;
  });
};

Apply similar changes for sorting, column filters, etc.

	•	Pass Through Table Instance:
Continue returning the table instance, which now uses state that is synchronized with the URL.

⸻

2. File: src/components/RepositoryTable.tsx

Changes Required:
	•	Prop-Driven State vs. URL State:
This component receives its table state (pagination, sorting, row selection) as props. If you choose to integrate URL state here as well, you have two options:
	•	Option A: Move the integration logic to the parent (see OnboardingPage) and keep RepositoryTable as a pure, prop-driven component.
	•	Option B: If you want RepositoryTable to manage its own state from the URL, import useRouter and initialize local state using search params similar to the hook.
	•	If Option A is chosen:
No changes may be necessary here—the parent should pass in state and change callbacks that already update the URL.
Ensure that any callbacks like onPaginationChange or onSortingChange passed into RepositoryTable are updated to call router.navigate so that changes are reflected in the URL.

⸻

3. File: src/pages/OnboardingPage.tsx

Changes Required:
	•	Import and Use Router:
Import useRouter from TanStack Router.
Example:

import { useRouter } from '@tanstack/router';


	•	Initialize Table State from URL:
When setting initial states for sorting, pagination, and row selection, read these values from router.state.search. For example, update:

const [pagination, setPagination] = useState<PaginationState>({
  pageIndex: 0,
  pageSize: 10,
});

to:

const router = useRouter();
const urlPagination = router.state.search.pagination as PaginationState | undefined;
const [pagination, setPagination] = useState<PaginationState>(urlPagination || { pageIndex: 0, pageSize: 10 });


	•	Update Change Callbacks:
Replace direct state setters with functions that update both local state and the URL. For instance, instead of simply calling setPagination(newValue), create a callback that does:

const handlePaginationChange: OnChangeFn<PaginationState> = (updaterOrValue) => {
  setPagination((prev) => {
    const newValue = typeof updaterOrValue === 'function'
      ? updaterOrValue(prev)
      : updaterOrValue;
    router.navigate({
      search: {
        ...router.state.search,
        pagination: newValue,
      },
    });
    return newValue;
  });
};

Do this similarly for setSorting and any other state changes.

	•	Update Query Keys:
When calling your repository fetching query (via React Query), include the table state from the URL (i.e. the search params) in your query key so that any URL change triggers a refetch. For example:

queryKey: ['repositories', pagination.pageIndex, pagination.pageSize, router.state.search.sorting]


	•	Listening for URL Changes:
Optionally, if the user navigates back or forward in the browser, listen to changes in router.state.search and update the local state accordingly. This ensures that the table state stays in sync with the URL.
	•	Pass Callbacks to Child Components:
When rendering <RepositoryDataTable> (or <RepositoryTable>), pass the updated callbacks (e.g. handlePaginationChange, handleSortingChange, etc.) so that user interactions update both the state and the URL.

⸻

Summary
	1.	In use-data-table.ts:
	•	Import and use useRouter to read and write search params.
	•	Initialize state using URL parameters.
	•	Update all state change handlers to call router.navigate with the new state.
	2.	In RepositoryTable.tsx:
	•	Ensure that state change callbacks (if provided by parent) are updated to use URL integration.
	•	Optionally, if managing local state here, integrate useRouter similarly.
	3.	In OnboardingPage.tsx:
	•	Import useRouter and initialize the table’s state from URL search params.
	•	Update change handlers to update the URL (using router.navigate).
	•	Update query keys for fetching repositories to include URL state.
	•	Pass these updated states and callbacks down to the table component.

This plan should serve as a guide to modify your files to leverage TanStack Router’s excellent search param integration for deep linking and state persistence in your table components.

Feel free to ask if you need further details or specific code examples for any part of the plan!