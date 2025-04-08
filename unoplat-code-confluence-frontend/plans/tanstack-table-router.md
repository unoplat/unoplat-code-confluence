Implementing Server-Side Pagination and Global Search with TanStack Table v8+

Fixing the Pagination Issue (TanStack Table + TanStack Query)

Problem: Clicking the pagination controls updated the URL (via TanStack Router) but did not fetch new data or update the table. This indicates that the table/page state change wasn’t linked to the data-fetching logic. In a server-side setup, we must manually trigger data refetch when page changes, and inform the table of new data.

Solution: Use TanStack Query (React Query) to fetch data keyed by the current page and search, and configure TanStack Table for manual pagination. Key steps:
	•	Include page (and search) in the query key: This ensures React Query knows to refetch when these params change. For example, use useQuery(['repos', page, search], ...). TanStack’s docs note that paginated queries should include the page in the key ￼. When page or search changes (from URL), the query key changes and triggers a new fetch.
	•	Keep previous data during page transitions: To avoid a flash of empty data when switching pages, use the placeholderData: keepPreviousData option (or keepPreviousData: true in older versions). This way, the last page’s data remains shown until the new page’s data arrives ￼ ￼. TanStack Query’s guide explains that using keepPreviousData (now via placeholderData) lets the UI display the last data while the new page loads, then seamlessly swaps it in ￼.
	•	Configure TanStack Table for manual server-side pagination: Set manualPagination: true on the table instance. According to the docs, this tells the table not to do client-side slicing, and to assume the provided data is already paginated ￼. You should also provide the total row count or page count from your server response. For example, use rowCount (preferred in v8.13+) or pageCount. The table uses this to know how many pages exist ￼. If total count is unknown, you can pass pageCount: -1 (the table will then always allow a “next” page until your data source indicates no more results) ￼.
	•	Sync table page state with the router: Pass the current page index to the table via state: { pagination: { pageIndex, pageSize } }. Here pageIndex = currentPageNumber - 1 (TanStack Table uses 0-based page index). Implement onPaginationChange to update the router’s query param. This way, when the user clicks “Next” or a page button, TanStack Table calls our handler, and we use TanStack Router to update the URL page param. For example:

onPaginationChange: (updater) => {
  const newState = typeof updater === 'function' 
    ? updater({ pageIndex, pageSize: itemsPerPage }) 
    : updater;
  router.navigate({
    search: { ...router.state.search, page: newState.pageIndex + 1 }
  });
}

This navigates to the same route with an updated ?page= query. TanStack Router treats search params as first-class state, so storing page in the URL is recommended ￼. (In a route component, you can retrieve it with const { page } = Route.useSearch() ￼.)

	•	Fetch data using TanStack Query (React Query): In the component, call useQuery with a query function that uses the current page and search. For example:

const { page = 1, search = "" } = router.useSearch<{ page: number; search: string }>();
const pageIndex = page - 1;
const { data, isFetching, isPreviousData } = useQuery({
  queryKey: ['repos', page, search],
  queryFn: async () => {
    // Determine cursor for GraphQL if needed:
    let cursorParam: string | undefined;
    if (page > 1) {
      // get previous page’s cursor from cache
      const prevData = queryClient.getQueryData(['repos', page - 1, search]);
      cursorParam = prevData?.nextCursor;
    }
    return fetchGitHubRepositories(page, itemsPerPage, search, cursorParam);
  },
  placeholderData: keepPreviousData,  // keep last data on screen during fetch
});

In this snippet, we derive page and search from the URL (via useSearch). The query key is ['repos', page, search] – this ensures any change to page or search causes a new fetch ￼. The queryFn uses page and search (and for page > 1, attempts to use a stored nextCursor from the previous page’s data if using cursor-based pagination). The use of placeholderData: keepPreviousData tells React Query to reuse the previous page’s data while fetching the next ￼.

	•	Provide data and config to the table: Use the data from the query in the table instance. For example:

const table = useReactTable({
  data: data?.items ?? [],         // current page rows
  columns,
  state: {
    pagination: { pageIndex, pageSize: itemsPerPage },
    globalFilter: searchTerm,      // handled in next section
  },
  onPaginationChange: (updater) => { ...navigate as shown above... },
  manualPagination: true,          // don't paginate client-side
  pageCount: data?.pageCount ?? -1,  // total pages if known (or -1 if unknown)
  // (or rowCount: data?.totalCount for automatic pageCount calculation [oai_citation_attribution:11‡tanstack.com](https://tanstack.com/table/v8/docs/guide/pagination#:~:text=manualPagination%3A%20true%2C%20%2F%2Fturn%20off%20client,pageCount%20instead%20of%20rowCount))
  getCoreRowModel: getCoreRowModel(),
  manualFiltering: true,          // explained below (for global filter)
  // ... any sorting config (manualSorting: true if needed)
});

Here we pass manualPagination: true and either pageCount or rowCount to align with TanStack Table’s server-side mode ￼. We also connect the current page state and update handler to the router. Now, when page changes in the URL (either via user action or programmatically), the component re-renders, the query key changes, and new data is fetched. The table then receives a new data prop and updates to show the new page.

What was broken: In the original implementation, likely the React Query queryKey did not include the page (or search) param, so changing the URL didn’t change the query key – no refetch occurred. Also, without manualPagination: true and proper pageCount/rowCount, TanStack Table might not have known it should request another page or might have been stuck on the first set of data. By applying the above changes, the table is now fully controlled by external state and React Query:
	•	The URL is the single source of truth for pagination state (page number). This is a best practice with TanStack Router ￼, allowing users to refresh or share the URL and maintain the same view.
	•	React Query sees the page param change (via the key) and refetches data for that page ￼.
	•	TanStack Table receives the new data and updates the rows, because we pass the query result into useReactTable. The table’s internal pagination.pageIndex is also updated via our state prop (since it derives from the URL’s page), so the UI highlights the correct page.

Adding a Global Search Filter (TanStack Table Global Filtering)

To implement a global search bar that filters data server-side:
	•	TanStack Table global filter state: We will use TanStack Table’s global filtering mechanism to manage the search term. The table has a globalFilter state and an setGlobalFilter API, but since our filtering is done on the server, we enable manual filtering. Set manualFiltering: true in the table options. This tells TanStack Table not to attempt any client-side filtering – it will assume the data is already filtered by the server ￼. In other words, the table won’t hide/show rows itself; we control what data it gets.
	•	Sync search term with router (URL): Just like page, we store the global search query in the URL (e.g. ?search=abc). This allows sharing/bookmarking a filtered view ￼. We can use useSearch() to read the current search param from TanStack Router ￼. For example:

const { search = "" } = router.useSearch<{ search: string }>();
const [searchTerm, setSearchTerm] = useState(search);

However, we don’t even need a separate state variable if we treat the router param as the state. We can control the table’s global filter directly via this search param.

	•	Wire up the global filter to the table: Pass the search term to the table’s state and handle changes. For instance:

const table = useReactTable({
  // ...other options as above
  state: { 
    pagination: { pageIndex, pageSize: itemsPerPage },
    globalFilter: search        // use URL search param as the global filter state
  },
  onGlobalFilterChange: (newValue) => {
    // Update URL 'search' param and reset to page 1
    router.navigate({
      search: { ...router.state.search, search: newValue, page: 1 }
    });
  },
  manualFiltering: true,
  // ... 
});

Here, by supplying state.globalFilter, we make the table’s global filter a controlled state (the source is our URL param). We also provide an onGlobalFilterChange callback. According to TanStack Table docs, onGlobalFilterChange is called whenever the global filter state changes, and is typically used to sync that state externally ￼. In our case, when the user types into the search bar (which will call table.setGlobalFilter internally), this callback will fire – we then use it to update the router’s search param. We also reset page to 1 whenever a new search is applied, to avoid querying an out-of-range page of a filtered result set. (By default, TanStack Table would auto-reset to page 0 on filter change, but with manual pagination that auto-reset is disabled ￼ ￼, so we handle it manually.)

	•	Add the search input UI: Place an input field above the table. TanStack Table doesn’t provide the input – you add it and call table.setGlobalFilter on change ￼. For example:

<input
  type="text"
  placeholder="Search..."
  value={search} 
  onChange={(e) => table.setGlobalFilter(e.target.value)}
/>
<DataTable table={table} /* Dice UI DataTable component */ />

We use the current search param as the input value, so it reflects the URL state. On change, we call table.setGlobalFilter(...) with the new string. This updates the table’s internal state (or calls our onGlobalFilterChange). In our setup, onGlobalFilterChange will then update the URL param. The result is a one-way data flow: user types -> table’s global filter updates -> we sync to URL -> this causes React Query to refetch with the new search term.

	•	Trigger data refetch on search change: Because our React Query queryKey includes search, any change to the search param triggers a new fetch (just like page) ￼. The fetchGitHubRepositories function should use this search term to query the server for filtered results. Ensure your query function forwards the search to the API. For example, if using GitHub’s API, pass the search term as a query parameter or GraphQL filter. The table will then receive the filtered data and display only those rows.

What was broken/missing: The original code did not have a global search at all. Adding it requires introducing a controlled global filter state. We utilize TanStack Table’s global filter API so that the integration is smooth: the table instance itself calls our handler when the filter changes, and we tie that into the router. This approach is supported by TanStack Table’s design for persisting filter state externally ￼. Also, by setting manualFiltering: true, we prevent TanStack Table from doing any client filtering, which is correct since the filtering is done by the server (our fetched data is already filtered) ￼.

Finally, here’s a combined code snippet illustrating the above solutions in a React + Vite context with Dice UI’s <DataTable> (for brevity, assume imports and router setup are done):

import { useReactTable, getCoreRowModel } from '@tanstack/react-table';
import { useQuery, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import { router } from './router'; // TanStack Router instance
import { DataTable } from '@/components/data-table'; // Dice UI DataTable
import type { PaginationState } from '@tanstack/react-table';

function ReposPage({ columns }) {
  // Get page & search from URL (with defaults)
  const { page = 1, search = "" } = router.useSearch<{ page: number; search: string }>();
  const pageIndex = page - 1;
  const itemsPerPage = 10;
  const queryClient = useQueryClient();

  // Fetch data with TanStack Query, keyed by page and search
  const { data, isFetching } = useQuery({
    queryKey: ['repos', page, search],
    queryFn: async () => {
      // If using cursor-based pagination (e.g., GraphQL), get the cursor for this page
      let cursor: string | undefined;
      if (page > 1) {
        const prev = queryClient.getQueryData<{ nextCursor?: string }>(['repos', page - 1, search]);
        cursor = prev?.nextCursor;
      }
      // Fetch data from server (page, perPage, search, cursor)
      return fetchGitHubRepositories(page, itemsPerPage, search, cursor);
    },
    placeholderData: keepPreviousData,  // keep previous page data while loading new
  });

  // Total count or page count from API response (for example, GitHub search provides total count)
  const totalCount = data?.totalCount; 
  // Calculate total pages if we know totalCount
  const pageCount = totalCount ? Math.ceil(totalCount / itemsPerPage) : -1;

  // Configure TanStack Table instance
  const table = useReactTable({
    data: data?.items ?? [],
    columns,
    state: {
      pagination: { pageIndex, pageSize: itemsPerPage },
      globalFilter: search,  // use search param as global filter state
    },
    manualPagination: true,
    pageCount: pageCount,    // total pages (or use rowCount: totalCount)
    manualFiltering: true,
    onPaginationChange: (updater) => {
      const newPageState = typeof updater === 'function' 
        ? updater({ pageIndex, pageSize: itemsPerPage } as PaginationState) 
        : updater;
      // Navigate to the new page (preserve other search params, e.g. search term)
      router.navigate({ 
        search: { ...router.state.search, page: newPageState.pageIndex + 1 } 
      });
    },
    onGlobalFilterChange: (newFilter) => {
      // When search input changes, reset to page 1 and update 'search' param
      router.navigate({ 
        search: { ...router.state.search, search: newFilter, page: 1 } 
      });
    },
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div>
      {/* Global Search Input */}
      <input
        type="text"
        placeholder="Search..."
        value={search}
        onChange={(e) => table.setGlobalFilter(e.target.value)}
        style={{ marginBottom: '1em' }}
      />

      {/* Data Table */}
      <DataTable table={table} />

      {/* Loading indicator */}
      {isFetching && <p>Loading...</p>}
    </div>
  );
}

In this code:
	•	The query uses page and search from router.useSearch to fetch data, and keepPreviousData to avoid flicker ￼.
	•	We configure useReactTable with manualPagination and manualFiltering so the table delegates these duties to us (server) ￼ ￼.
	•	We pass globalFilter: search and handle onGlobalFilterChange to sync with the URL. The search input calls table.setGlobalFilter on change, as recommended by TanStack Table docs ￼, which in turn triggers our router update.
	•	The pageCount (or rowCount) is provided so the table knows when it’s on the last page ￼. If pageCount is -1 (unknown total), the Next button will always be enabled, but in a cursor-based setup you likely know when there are no more pages from the API (or you disable jumping to arbitrary pages).

How the Fix Works

After these changes, pagination and search are fully functional and in sync:
	•	Clicking a pagination button updates the URL and the table state, which invalidates the React Query key and fetches the new page. The table renders the new data once loaded. This resolves the issue of “URL changes but data doesn’t” – now the data refetch is correctly triggered by the page param change ￼.
	•	The global search bar updates a query param and triggers a refetch with the new filter. The table’s global filter state is kept in sync with this param, leveraging TanStack Table’s built-in mechanism for global filters (via setGlobalFilter and onGlobalFilterChange callbacks) ￼ ￼. Because we turned on manual filtering, the table simply displays whatever rows the server returned for that search term ￼.
	•	Both page and search being in the URL means the app uses TanStack Router’s URL-as-state benefits: users can bookmark/share a URL with ?page=2&search=react and get the same data view ￼. Also, using TanStack Router’s useSearch hook gives us a type-safe way to access these params in our component ￼.
	•	By providing rowCount/pageCount and using the TanStack Table pagination API, the UI controls (Next/Prev buttons, page numbers) correctly reflect available pages (e.g., disabling “Next” on the last page works because the table knows when pageIndex >= pageCount-1).

References:
	•	TanStack Table docs on manual server-side pagination and providing rowCount/pageCount ￼ ￼. This ensures the table knows how to handle page changes and when to allow navigation.
	•	TanStack Table docs on manual filtering (to delegate filtering to server) ￼.
	•	TanStack Table global filtering guide on external state and adding a custom global filter UI ￼ ￼.
	•	TanStack Query docs on paginated queries with keepPreviousData and including parameters in the query key ￼ ￼.
	•	TanStack Router docs on using search params for state (e.g., page number in URL) ￼ and retrieving them in components ￼.

With these fixes, the DataTable (Dice UI) wrapping TanStack Table will correctly fetch and display new pages on pagination, and filter results based on the global search term, all while keeping the URL in sync with the table’s state. This makes the data table behavior predictable, sharable, and aligned with TanStack’s best practices for tables, query, and routing.

Sources:
	1.	TanStack Table – Server-Side Pagination guide (manual pagination with rowCount/pageCount) ￼ ￼
	2.	TanStack Table – Global Filtering (controlling filter state and input UI) ￼ ￼
	3.	TanStack Table – Manual Filtering mode explained ￼
	4.	TanStack Query – Paginated Queries (including page in queryKey and using keepPreviousData) ￼ ￼
	5.	TanStack Router – Using URL search params as state (page & filter in URL) ￼ ￼