# Unoplat Code Confluence Frontend - Current Issues

## Overview
This document outlines the current issues identified in the Unoplat Code Confluence Frontend application, particularly related to the integration of TanStack Query and TanStack Router to replace Nuqs for URL state management.

## Critical Issues

### 1. JSON Parsing Errors in URL State Management
- **Error Message**: `[useDataTableWithRouter] Error parsing sorting from URL: SyntaxError: Unexpected token 'o', "[object+Object]" is not valid JSON`
- **Description**: The application is attempting to parse URL search parameters that contain object references instead of serialized JSON strings.
- **Location**: `useDataTableWithRouter` hook and `RepositoryDataTable` component
- **Probable Cause**: When serializing sorting state to URL parameters, the application is storing the object reference directly rather than stringifying it properly.
- **Impact**: Sorting functionality broken, console errors, potential performance degradation.

#### Solution
The error occurs because complex objects (like sorting state) are being directly passed to URL parameters without proper serialization. TanStack Router handles this automatically, but it requires proper implementation:

1. **Ensure proper object serialization**: When setting sort state in URL parameters, objects must be stringified first:

```typescript
// INCORRECT - Passing object reference directly
router.navigate({
  search: {
    // This causes the error - an object is being set directly
    sort: sortingState
  }
});

// CORRECT - Using TanStack Router's built-in serialization
router.navigate({
  search: {
    // This works - TanStack Router will automatically handle serialization
    sort: sortingState
  }
});
```

2. **Fix the `useDataTableWithRouter` hook**:
```typescript
// Modify the hook to handle sorting state properly
export function useDataTableWithRouter<TData>(props: DataTableRouterOptions<TData>) {
  const router = useRouter();
  const searchParams = router.state.search;
  
  // Extract and safely parse sorting from search params
  const sortingFromUrl = useMemo(() => {
    try {
      // Make sure to handle the case when the sort param might be a string or object
      const sortParam = searchParams?.sort;
      if (typeof sortParam === 'string') {
        return JSON.parse(sortParam);
      } else if (Array.isArray(sortParam)) {
        return sortParam;
      }
      return props.initialSort || [];
    } catch (err) {
      console.error('[useDataTableWithRouter] Error parsing sorting from URL:', err);
      return props.initialSort || [];
    }
  }, [searchParams?.sort, props.initialSort]);
  
  // Update URL when sorting changes
  const onSortingChange = useCallback((updatedSorting: SortingState) => {
    router.navigate({
      search: (prev) => ({
        ...prev,
        sort: updatedSorting,
      }),
      replace: true,
    });
  }, [router]);

  // Return the table configuration with safe sorting state
  return {
    sorting: sortingFromUrl,
    onSortingChange,
    // ...other properties
  };
}
```

3. **Configure custom serialization** (optional, for more complex cases):
   
   If you encounter persistent issues with the default serialization, you can customize how TanStack Router handles serialization:

```typescript
import { createRouter, parseSearchWith, stringifySearchWith } from '@tanstack/react-router';

const router = createRouter({
  routeTree,
  // Custom search param handling
  parseSearch: parseSearchWith((value) => {
    try {
      return JSON.parse(value);
    } catch (e) {
      // If it fails to parse as JSON, return the original value
      return value;
    }
  }),
  stringifySearch: stringifySearchWith((value) => {
    if (typeof value === 'object' && value !== null) {
      return JSON.stringify(value);
    }
    return String(value);
  }),
});
```

This solution ensures proper serialization of complex objects in URL parameters while providing fallbacks for error cases. TanStack Router handles JSON serialization automatically by default, but it's crucial to ensure objects are properly passed to the router's APIs.

### 2. Pagination State Synchronization
- **Symptoms**: 
  - Clicking on pagination controls updates the URL (e.g., `/onboarding?page=2`) but doesn't update the table data
  - UI still shows "Page 1 of 1" after URL has changed
- **Description**: Pagination state in the URL isn't correctly synchronized with the table component state.
- **Probable Cause**: Incomplete implementation of TanStack Router state management or incorrect data refetching trigger.
- **Impact**: Users cannot navigate through pages of repository data.

### 3. React Component Lifecycle Issues
- **Error Message**: `useImperativeHandle received a final argument during this render, but not during the previous render. Even though the final argument is optional, its type cannot change between renders.`
- **Description**: There's an inconsistency in how the `useImperativeHandle` hook is being used in component renders.
- **Location**: `RepositoryDataTable` component
- **Impact**: Potential instability in component rendering and state management.

### 4. Data Fetching and URL State Coordination
- **Description**: The URL parameters are being updated, but the application isn't using these parameters to trigger new data fetches.
- **Probable Cause**: Missing or incorrect dependencies in data fetch queries, or improper implementation of TanStack Query's integration with router state.
- **Impact**: User interactions with filters, sorting, and pagination don't reflect in the displayed data.

### 5. TanStack Router and Query Integration
- **Description**: The transition from Nuqs to TanStack Router for URL state management appears incomplete, with several disconnect points in the data flow.
- **Specific Issues**:
  - Router state extraction not properly synchronized with table state
  - Query invalidation/refetching not triggered on URL parameter changes
  - URL serialization for complex objects (especially sorting state) is failing

## Recommended Next Steps

### Short-term Fixes
1. **Fix JSON Serialization**: Properly stringify complex objects before storing in URL parameters and parse them when extracting.
2. **Update Query Dependencies**: Ensure TanStack Query dependencies include URL parameters so queries refetch when URL changes.
3. **Correct useImperativeHandle Implementation**: Review and fix the component lifecycle issue in RepositoryDataTable.

### Medium-term Improvements
1. **Complete TanStack Router Migration**: Fully migrate from Nuqs to TanStack Router for URL state management.
2. **Add Error Handling**: Implement proper error boundaries and fallback UI for data fetching failures.
3. **Improve Table-Router Integration**: Create a more robust integration between TanStack Table and Router.

### Long-term Enhancements
1. **Comprehensive Testing**: Add unit and integration tests to prevent regression of these issues.
2. **Documentation**: Document the patterns for URL state management to ensure consistent implementation.
3. **Performance Optimization**: Review and optimize data fetching patterns, potentially implementing request deduplication and caching. 