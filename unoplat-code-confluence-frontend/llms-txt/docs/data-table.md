Components

# Data Table

A powerful and flexible data table component for displaying, filtering, sorting, and paginating tabular data. We will be using this 
in combination with tanstack router and query. we will not be using nuqs.

[Docs](https://tanstack.com/table/latest/docs/introduction) [API](https://www.diceui.com/docs/components/data-table#api-reference)

PreviewCode

Status

View

|  | Title | Status | Budget |  |
| --- | --- | --- | --- | --- |
|  | Project Alpha | active | 50,000 | Open menu |
|  | Project Beta | inactive | 75,000 | Open menu |
|  | Project Gamma | active | 25,000 | Open menu |
|  | Project Delta | active | 100,000 | Open menu |

0 of 4 row(s) selected.

Rows per page

10

Page 1 of 1

## [Installation](https://www.diceui.com/docs/components/data-table\#installation)

Install the components and dependencies:

npmpnpmyarnbun

```
npx shadcn@latest add "https://diceui.com/r/data-table"
```

Wrap your application with the [`NuqsAdapter`](https://nuqs.47ng.com/docs/adapters) for query state management:

```
import { NuqsAdapter } from "nuqs/adapters/next/app";

<NuqsAdapter>
  <App />
</NuqsAdapter>
```

## [Layout](https://www.diceui.com/docs/components/data-table\#layout)

Import the components and compose them together:

```
import { DataTable } from "@/components/data-table";
import { DataTableToolbar } from "@/components/data-table-toolbar";
import { DataTableAdvancedToolbar } from "@/components/data-table-advanced-toolbar";
import { DataTableFilterList } from "@/components/data-table-filter-list";
import { DataTableSortList } from "@/components/data-table-sort-list";
import { useDataTable } from "@/hooks/use-data-table";

const { table } = useDataTable({
  data,
  columns,
  pageCount,
});

// With standard toolbar
<DataTable table={table}>
  <DataTableToolbar table={table}>
    <DataTableSortList table={table} />
  </DataTableToolbar>
</DataTable>

// With advanced toolbar
<DataTable table={table}>
  <DataTableAdvancedToolbar table={table}>
    <DataTableFilterList table={table} />
    <DataTableSortList table={table} />
  </DataTableAdvancedToolbar>
</DataTable>
```

## [Sort List](https://www.diceui.com/docs/components/data-table\#sort-list)

The [`DataTableSortList`](https://www.diceui.com/docs/components/data-table#datatablesortlist) provides a comprehensive way to sort data by multiple columns simultaneously.

### [Features](https://www.diceui.com/docs/components/data-table\#features)

- Supports multiple column sorting
- Drag and drop reordering
- Ascending and descending directions

### [Installation](https://www.diceui.com/docs/components/data-table\#installation-1)

npmpnpmyarnbun

```
npx shadcn@latest add "https://diceui.com/r/data-table-sort-list"
```

## [Filter List](https://www.diceui.com/docs/components/data-table\#filter-list)

The [`DataTableFilterList`](https://www.diceui.com/docs/components/data-table#datatablefilterlist) provides a comprehensive way to filter data with multiple conditions.

### [Features](https://www.diceui.com/docs/components/data-table\#features-1)

- Multiple filter conditions with AND/OR logic
- Drag and drop reordering
- Dynamic operators per field type

### [Installation](https://www.diceui.com/docs/components/data-table\#installation-2)

npmpnpmyarnbun

```
npx shadcn@latest add "https://diceui.com/r/data-table-filter-list"
```

## [Filter Menu](https://www.diceui.com/docs/components/data-table\#filter-menu)

The [`DataTableFilterMenu`](https://www.diceui.com/docs/components/data-table#datatablefiltermenu) provides a command palette-style interface for quickly adding and managing filters.

### [Features](https://www.diceui.com/docs/components/data-table\#features-2)

- Command palette-style interface
- Context-aware input fields
- Compact token display

### [Installation](https://www.diceui.com/docs/components/data-table\#installation-3)

npmpnpmyarnbun

```
npx shadcn@latest add "https://diceui.com/r/data-table-filter-menu"
```

## [Action Bar](https://www.diceui.com/docs/components/data-table\#action-bar)

The [`DataTableActionBar`](https://www.diceui.com/docs/components/data-table#datatableactionbar) provides a toolbar for the data table when rows are selected.

### [Features](https://www.diceui.com/docs/components/data-table\#features-3)

- Floating action bar
- Customizable actions
- Row selection tracking

### [Installation](https://www.diceui.com/docs/components/data-table\#installation-4)

npmpnpmyarnbun

```
npx shadcn@latest add "https://diceui.com/r/data-table-action-bar"
```

## [Walkthrough](https://www.diceui.com/docs/components/data-table\#walkthrough)

Define columns with appropriate metadata:

```
import { Text, CalendarIcon, DollarSign } from "lucide-react";
import { DataTableColumnHeader } from "@/components/data-table-column-header";

const columns = React.useMemo(() => [\
  {\
    // Provide an unique id for the column\
    // This id will be used as query key for the column filter\
    id: "title",\
    accessorKey: "title",\
    header: ({ column }) => (\
      <DataTableColumnHeader column={column} title="Title" />\
    ),\
    cell: ({ row }) => <div>{row.getValue("title")}</div>,\
    // Define the column meta options for sorting, filtering, and view options\
    meta: {\
      label: "Title",\
      placeholder: "Search titles...",\
      variant: "text",\
      icon: Text,\
    },\
    // By default, the column will not be filtered. Set to `true` to enable filtering.\
    enableColumnFilter: true,\
  },\
], []);
```

Initialize the table state using the `useDataTable` hook:

```
import { useDataTable } from "@/hooks/use-data-table";

function DataTableDemo() {
  const { table } = useDataTable({
    data,
    columns,
    // Pass the total number of pages for the table
    pageCount,
    initialState: {
      sorting: [{ id: "createdAt", desc: true }],
      pagination: { pageSize: 10 },
    },
    // Unique identifier for rows, can be used for unique row selection
    getRowId: (row) => row.id,
  });

  return (
    // ... render table
  );
}
```

Pass the table instance to the `DataTable`, and `DataTableToolbar` components:

```
import { DataTable } from "@/components/data-table";
import { DataTableToolbar } from "@/components/data-table-toolbar";
import { DataTableSortList } from "@/components/data-table-sort-list";

function DataTableDemo() {
  return (
    <DataTable table={table}>
      <DataTableToolbar table={table}>
        <DataTableSortList table={table} />
      </DataTableToolbar>
    </DataTable>
  );
}
```

For advanced filtering, use the `DataTableAdvancedToolbar` component:

```
import { DataTableAdvancedToolbar } from "@/components/data-table-advanced-toolbar";
import { DataTableFilterList } from "@/components/data-table-filter-list";
import { DataTableFilterMenu } from "@/components/data-table-filter-menu";

function DataTableDemo() {
  return (
    <DataTable table={table}>
      <DataTableAdvancedToolbar table={table}>
        <DataTableFilterList table={table} />
        <DataTableSortList table={table} />
      </DataTableAdvancedToolbar>
    </DataTable>
  );
}
```

Alternatively, swap out `DataTableFilterList` with `DataTableFilterMenu` for a command palette-style interface:

```
import { DataTableAdvancedToolbar } from "@/components/data-table-advanced-toolbar";
import { DataTableFilterList } from "@/components/data-table-filter-list";
import { DataTableFilterMenu } from "@/components/data-table-filter-menu";
import { DataTableSortList } from "@/components/data-table-sort-list";

function DataTableDemo() {
  return (
    <DataTable table={table}>
      <DataTableAdvancedToolbar table={table}>
        <DataTableFilterList table={table} />
        <DataTableFilterMenu table={table} />
        <DataTableSortList table={table} />
      </DataTableAdvancedToolbar>
    </DataTable>
  );
}
```

Render an action bar on row selection:

```
import { DataTableActionBar } from "@/components/data-table-action-bar";
import { CustomTableActions } from "@/components/custom-table-actions";

function DataTableDemo() {
  return (
    <DataTable
      table={table}
      actionBar={
        <DataTableActionBar table={table}>
          {/* Add your custom actions here */}
          <CustomTableActions />
        </DataTableActionBar>
      }
    >
      <DataTableToolbar table={table} />
    </DataTable>
  );
}
```

## [API Reference](https://www.diceui.com/docs/components/data-table\#api-reference)

### [Column Definitions](https://www.diceui.com/docs/components/data-table\#column-definitions)

The column definitions are used to define the columns of the data table.

```
const columns = React.useMemo<ColumnDef<Project>[]>(() => [\
  {\
    // Required: Unique identifier for the column\
    id: "title",\
    // Required: Key to access the data, `accessorFn` can also be used\
    accessorKey: "title",\
    // Optional: Custom header component\
    header: ({ column }) => (\
      <DataTableColumnHeader column={column} title="Title" />\
    ),\
    // Optional: Custom cell component\
    cell: ({ row }) => <div>{row.getValue("title")}</div>,\
    // Optional: Meta options for filtering, sorting, and view options\
    meta: {\
      label: "Title",\
      placeholder: "Search titles...",\
      variant: "text",\
      icon: Text,\
    },\
    // By default, the column will not be filtered. Set to `true` to enable filtering.\
    enableColumnFilter: true,\
  },\
  {\
    id: "status",\
    // Access nested data using `accessorFn`\
    accessorFn: (row) => row.lineItem.status,\
    header: "Status",\
    meta: {\
      label: "Status",\
      variant: "select",\
      options: [\
        { label: "Active", value: "active" },\
        { label: "Inactive", value: "inactive" },\
      ],\
    },\
    enableColumnFilter: true,\
  },\
], []);
```

#### [Properties](https://www.diceui.com/docs/components/data-table\#properties)

Core configuration options for defining columns.

| Prop | Description |
| --- | --- |
| `id` | Required: Unique identifier for the column |
| `accessorKey` | Required: Key to access the data from the row |
| `accessorFn` | Optional: Custom accessor function to access data |
| `header` | Optional: Custom header component with column props |
| `cell` | Optional: Custom cell component with row props |
| `meta` | Optional: Meta options for accessing column metadata |
| `enableColumnFilter` | By default, the column will not be filtered. Set to \`true\` to enable filtering |
| `enableSorting` | Enable sorting for this column |
| `enableHiding` | Enable column visibility toggle |

#### [Column Meta](https://www.diceui.com/docs/components/data-table\#column-meta)

Column meta options for filtering, sorting, and view options.

| Prop | Description |
| --- | --- |
| `label` | The display name for the column |
| `placeholder` | The placeholder text for filter inputs |
| `variant` | The type of filter to use (\`text\`, \`number\`, \`select\`, etc.) |
| `options` | For select/multi-select filters, an array of options with \`label\`, \`value\`, and optional \`count\` and \`icon\` |
| `range` | For range filters, a tuple of \`\[min, max\]\` values |
| `unit` | For numeric filters, the unit to display (e.g., 'hr', '$') |
| `icon` | The react component to use as an icon for the column |

#### [Filter Variants](https://www.diceui.com/docs/components/data-table\#filter-variants)

Available filter variants for [column meta](https://www.diceui.com/docs/components/data-table#column-meta).

| Title | Description |
| --- | --- |
| `text` | Text search with contains, equals, etc. |
| `number` | Numeric filters with equals, greater than, less than, etc. |
| `range` | Range filters with minimum and maximum values |
| `date` | Date filters with equals, before, after, etc. |
| `dateRange` | Date range filters with start and end dates |
| `boolean` | Boolean filters with true/false values |
| `select` | Single-select filters with predefined options |
| `multiSelect` | Multi-select filters with predefined options |

Reference the [TanStack Table Column Definitions Guide](https://tanstack.com/table/latest/docs/guide/column-defs#column-definitions-guide) for detailed column definition guide.

### [useDataTable](https://www.diceui.com/docs/components/data-table\#usedatatable)

A hook for initializing the data table with state management.

| Prop | Type | Default |
| --- | --- | --- |
| `history?` | `"push" | "replace"` | `"replace"` |
| `debounceMs?` | `number` | `300` |
| `throttleMs?` | `number` | `50` |
| `clearOnDefault?` | `boolean` | `false` |
| `enableAdvancedFilter?` | `boolean` | `false` |
| `scroll?` | `boolean` | `false` |
| `shallow?` | `boolean` | `true` |
| `startTransition?` | `TransitionStartFunction` | - |
| `pageCount` | `number` | - |
| `data` | `TData[]` | - |
| `columns` | `ColumnDef<TData, any>[]` | - |
| `getRowId?` | `(originalRow: TData, index: number, parent?: Row<TData> | undefined) => string` | - |
| `defaultColumn?` | `Partial<ColumnDef<TData, unknown>>` | - |
| `initialState?` | `InitialTableState` | - |

### [DataTable](https://www.diceui.com/docs/components/data-table\#datatable)

The main data table component.

| Prop | Type | Default |
| --- | --- | --- |
| `table` | `Table<TData>` | - |
| `actionBar?` | `ReactNode` | - |

### [DataTableColumnHeader](https://www.diceui.com/docs/components/data-table\#datatablecolumnheader)

Custom header component for columns with sorting.

| Prop | Type | Default |
| --- | --- | --- |
| `column` | `Column<TData, TValue>` | - |
| `title` | `string` | - |

### [DataTableToolbar](https://www.diceui.com/docs/components/data-table\#datatabletoolbar)

Standard toolbar with filtering and view options.

| Prop | Type | Default |
| --- | --- | --- |
| `table` | `Table<TData>` | - |

### [DataTableAdvancedToolbar](https://www.diceui.com/docs/components/data-table\#datatableadvancedtoolbar)

Advanced toolbar with more comprehensive filtering capabilities.

| Prop | Type | Default |
| --- | --- | --- |
| `table` | `Table<TData>` | - |

### [DataTableViewOptions](https://www.diceui.com/docs/components/data-table\#datatableviewoptions)

Controls column visibility and display preferences in the data table.

| Prop | Type | Default |
| --- | --- | --- |
| `table` | `Table<TData>` | - |

### [DataTableSortList](https://www.diceui.com/docs/components/data-table\#datatablesortlist)

List of applied sorting with ability to add, remove, and modify sorting.

| Prop | Type | Default |
| --- | --- | --- |
| `table` | `Table<TData>` | - |
| `debounceMs?` | `number` | `300` |
| `throttleMs?` | `number` | `50` |
| `shallow?` | `boolean` | `true` |

### [DataTableFilterList](https://www.diceui.com/docs/components/data-table\#datatablefilterlist)

List of applied filters with ability to add, remove, and modify filters.

| Prop | Type | Default |
| --- | --- | --- |
| `table` | `Table<TData>` | - |
| `debounceMs?` | `number` | `300` |
| `throttleMs?` | `number` | `50` |
| `shallow?` | `boolean` | `true` |

### [DataTableFilterMenu](https://www.diceui.com/docs/components/data-table\#datatablefiltermenu)

Filter menu with ability to add, remove, and modify filters.

| Prop | Type | Default |
| --- | --- | --- |
| `table` | `Table<TData>` | - |
| `debounceMs?` | `number` | `300` |
| `throttleMs?` | `number` | `50` |
| `shallow?` | `boolean` | `true` |

### [DataTableActionBar](https://www.diceui.com/docs/components/data-table\#datatableactionbar)

Floating action bar component for actions for selected rows.

| Prop | Type | Default |
| --- | --- | --- |
| `table` | `Table<TData>` | - |
| `visible?` | `boolean` | - |
| `container?` | `Element | DocumentFragment` | `document.body` |

### [DataTablePagination](https://www.diceui.com/docs/components/data-table\#datatablepagination)

Pagination controls for the data table.

| Prop | Type | Default |
| --- | --- | --- |
| `table` | `Table<TData>` | - |
| `pageSizeOptions?` | `number[]` | `[10, 20, 30, 40, 50]` |

## [Accessibility](https://www.diceui.com/docs/components/data-table\#accessibility)

### [Keyboard Interactions](https://www.diceui.com/docs/components/data-table\#keyboard-interactions)

| Key | Description |
| --- | --- |
| `F` | Opens the filter menu. |
| `Shift + F` | Removes the last applied filter. |
| `S` | Opens the sort menu. |
| `Shift + S` | Removes the last applied sort. |
| `Backspace`  `Delete` | Removes the focused filter/sort item. Removes the last applied filter/sort when menu trigger is focused. |

## [Credits](https://www.diceui.com/docs/components/data-table\#credits)

- [shadcn/ui](https://github.com/shadcn-ui/ui/tree/main/apps/www/app/(app)/examples/tasks) \- For the initial implementation of the data table.

[Combobox\\
\\
An input with a popover that helps users filter through a list of options.](https://www.diceui.com/docs/components/combobox) [Editable\\
\\
An accessible inline editable component for editing text content in place.](https://www.diceui.com/docs/components/editable)

### On this page

[Installation](https://www.diceui.com/docs/components/data-table#installation) [Layout](https://www.diceui.com/docs/components/data-table#layout) [Sort List](https://www.diceui.com/docs/components/data-table#sort-list) [Features](https://www.diceui.com/docs/components/data-table#features) [Installation](https://www.diceui.com/docs/components/data-table#installation-1) [Filter List](https://www.diceui.com/docs/components/data-table#filter-list) [Features](https://www.diceui.com/docs/components/data-table#features-1) [Installation](https://www.diceui.com/docs/components/data-table#installation-2) [Filter Menu](https://www.diceui.com/docs/components/data-table#filter-menu) [Features](https://www.diceui.com/docs/components/data-table#features-2) [Installation](https://www.diceui.com/docs/components/data-table#installation-3) [Action Bar](https://www.diceui.com/docs/components/data-table#action-bar) [Features](https://www.diceui.com/docs/components/data-table#features-3) [Installation](https://www.diceui.com/docs/components/data-table#installation-4) [Walkthrough](https://www.diceui.com/docs/components/data-table#walkthrough) [API Reference](https://www.diceui.com/docs/components/data-table#api-reference) [Column Definitions](https://www.diceui.com/docs/components/data-table#column-definitions) [Properties](https://www.diceui.com/docs/components/data-table#properties) [Column Meta](https://www.diceui.com/docs/components/data-table#column-meta) [Filter Variants](https://www.diceui.com/docs/components/data-table#filter-variants) [useDataTable](https://www.diceui.com/docs/components/data-table#usedatatable) [DataTable](https://www.diceui.com/docs/components/data-table#datatable) [DataTableColumnHeader](https://www.diceui.com/docs/components/data-table#datatablecolumnheader) [DataTableToolbar](https://www.diceui.com/docs/components/data-table#datatabletoolbar) [DataTableAdvancedToolbar](https://www.diceui.com/docs/components/data-table#datatableadvancedtoolbar) [DataTableViewOptions](https://www.diceui.com/docs/components/data-table#datatableviewoptions) [DataTableSortList](https://www.diceui.com/docs/components/data-table#datatablesortlist) [DataTableFilterList](https://www.diceui.com/docs/components/data-table#datatablefilterlist) [DataTableFilterMenu](https://www.diceui.com/docs/components/data-table#datatablefiltermenu) [DataTableActionBar](https://www.diceui.com/docs/components/data-table#datatableactionbar) [DataTablePagination](https://www.diceui.com/docs/components/data-table#datatablepagination) [Accessibility](https://www.diceui.com/docs/components/data-table#accessibility) [Keyboard Interactions](https://www.diceui.com/docs/components/data-table#keyboard-interactions) [Credits](https://www.diceui.com/docs/components/data-table#credits)