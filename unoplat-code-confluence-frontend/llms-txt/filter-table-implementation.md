- [![bazza/ui](https://ui.bazza.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fbazzaui-v3-color.75a4cf6a.png&w=1080&q=75)bazza/ui](https://ui.bazza.dev/) Toggle Sidebar

Basics

- [Introduction](https://ui.bazza.dev/docs/intro)
- [Getting Started](https://ui.bazza.dev/docs/getting-started)
- [Feedback](https://ui.bazza.dev/docs/feedback)

Components

- [Data Table Filter](https://ui.bazza.dev/docs/data-table-filter)

- Toggle theme

Toggle Sidebar

Data table filterbeta

A powerful data table filter for client-side filtering with TanStack Table.

Title

contains

fix pay

Clear

|  | Status | Title | Assignee | Assignee (Name) | Labels | Estimated Hours | Start Date | End Date |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Todo | Fix payment processing | ![](https://ui.bazza.dev/avatars/rose-eve.png) | Rose Eve | Bug | 6h |  |  |

0 of 1 row(s) selected.

PreviousNext

## Introduction

This is an add-on to your existing shadcn/ui data table component. It adds client-side filtering with a clean, modern UI inspired by [Linear](https://linear.app/homepage).

This component relies on [TanStack Table](https://tanstack.com/table), a headless UI for building powerful tables & datagrids.

## Prerequisites

Before you begin:

- Create your `<DataTable />` component. You can follow the [shadcn/ui docs](https://ui.shadcn.com/docs/components/data-table) for guidance.
- Ensure you're using client-side filtering.

## Installation

From the command line, install the component into your project:

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add https://ui.bazza.dev/r/data-table-filter.json

```

Copy

## Concepts

Let's take a look at the most important concepts for using this component.

### Column data types

Whenever you want to filter a column, you need to define what type of data it contains. `ColumnDataType` identifies the types of data we currently support filtering for.

Set the `type` property of the column meta (explained below) to one of the following values:

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export type ColumnDataType =
  | 'text'         /* Text data */
  | 'number'       /* Numerical data */
  | 'date'         /* Dates */
  | 'option'       /* Single-valued option (e.g. status) */
  | 'multiOption'  /* Multi-valued option (e.g. labels) */
```

### Column options

For `option` and `multiOption` columns, we represent each possible option as a `ColumnOption`:

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export interface ColumnOption {
  /* The label to display for the option. */
  label: string
  /* The internal value of the option. */
  value: string
  /* An optional icon to display next to the label. */
  icon?: React.ReactElement | React.ElementType
}
```

#### `label`

This is the label or display name for the option.

#### `value`

This is the interval value for the option and must be unique across all options for a given column.

For an `option` column, the filter value is a `string` which matches the `value` property of chosen column option.

For a `multiOption` column, the filter value is a `string[]` where each array member is the `value` property of the chosen column option.

#### `icon`

Optionally, you can provide an icon to represent the column option.

An icon must be provided for every column option. Otherwise, icons will not be displayed for the column's options.

### Column meta

The star of the show is the `ColumnMeta` interface, which defines the metadata shape for a column.

The metadata for each column is configured using the column's `meta` property, which accepts an object of type `ColumnMeta`.

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export type ElementType<T> = T extends (infer U)[] ? U : T

interface ColumnMeta<TData extends RowData, TValue> {
  /* The display name of the column. */
  displayName: string
  /* The column icon. */
  icon: LucideIcon
  /* The data type of the column. */
  type: ColumnDataType
  /* An optional list of options for the column. */
  /* This is used for columns with type 'option' or 'multiOption'. */
  /* If the options are known ahead of time, they can be defined here. */
  /* Otherwise, they will be dynamically generated based on the data. */
  options?: ColumnOption[]
  /* An optional function to transform columns with type 'option' or 'multiOption'. */
  /* This is used to convert each raw option into a ColumnOption. */
  transformOptionFn?: (
    value: ElementType<NonNullable<TValue>>,
  ) => ColumnOption
  /* An optional "soft" max for the range slider. */
  /* This is used for columns with type 'number'. */
  max?: number
}
```

Let's go through each property in detail:

#### `displayName`

This is the display name for the column. It is used when showing the property in various filter-related interfaces, such as the filter menu.

#### `icon`

This is the icon for the column. It is displayed alongside the `displayName`.

#### `type`

This is the data type of the column. It is used to determine many core functionalities of the data table filter component, such as:

- Rendering the correct user interfaces for modifying the filter values.
- Determining the correct filter operators for the property.

#### `options`

Only for `option` and `multiOption` columns.

If you have a static list of options for the column, you can pass them as an `ColumnOption[]` object.

#### `transformOptionFn`

Only for `option` and `multiOption` columns.

This is used when you're inferring the available options for a column using the column data itself.

The `transformOptionFn` will be used to transform each unique column value into a `ColumnOption` object.

Internally, this is used when determining the available options for a column when the `options` property is not defined.

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
/* Get all non-null column values */
const columnVals = table
  .getCoreRowModel()
  .rows.flatMap((r) => r.getValue<TValue>(id))
  .filter((v): v is NonNullable<TValue> => v !== undefined && v !== null)

/* Keep unique values */
/* Transform column values into `ColumnOption` objects */
const options = uniq(columnVals).map(meta.transformOptionFn)
```

#### `max`

Only for `number` columns.

Sets a "soft" maximum value for the range slider when filtering on a `number` column.

If omitted, the range slider will compute the maximum value based on the available column data.

## Usage

### Add component

Import the `<DataTableFilter />` component and pass it your `table` instance:

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { DataTableFilter } from '@/components/data-table-filter'

export default function DataTable() {
  return (
    <div>
      <DataTableFilter table={table} />
      <div className="rounded-md border">
        <Table>
          {/* ... */}
        </Table>
      </div>
    </div>
  )
}
```

### Update columns

#### Updating your columns

For each column that you want to be filterable, you need to do two things:

- Use our provided `filterFn()` for filtering the column data.
- Add the `meta` property using the `defineMeta()` helper function.

For the filter function, we provide one for you - it is conveniently called `filterFn()` and takes a single argument `type` which is the column data type (i.e. `ColumnDataType`).

For the column meta, we provide a helper function called `defineMeta()` which takes two arguments: **(1)** the property name from your data object, and **(2)** an object containing the column meta.

When specifying the property name, you must use an accessor function, as demonstrated below.

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export const columns = [\
  columnHelper.accessor('status', {\
    filterFn: filterFn('option'),\
    meta: defineMeta(row => row.status, {\
      displayName: 'Status',\
      type: 'option',\
      icon: CircleDotDashedIcon,\
      options: ISSUE_STATUSES,\
    }),\
  }),\
]
```

## Integrations

### `nuqs`

This integration is in alpha.

We are working on making this easier to use.

You can use [`nuqs`](https://nuqs.47ng.com/) to persist the filter state in the URL.

1. Install the `nuqs` and `zod` packages:

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm add nuqs zod

```

Copy

2. Use the appropriate `nuqs` adapter for your framework from the [nuqs docs](https://nuqs.47ng.com/docs/adapters).

3. Create your Zod schema for the query filter state:


```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { z } from 'zod'

const dataTableFilterQuerySchema = z
  .object({
    id: z.string(),
    value: z.object({
      operator: z.string(),
      values: z.any(),
    }),
  })
  .array()
  .min(0)

type DataTableFilterQuerySchema = z.infer<typeof dataTableFilterQuerySchema>
```

4. Create the following helper function:

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
function initializeFiltersFromQuery<TData, TValue>(
  filters: DataTableFilterQuerySchema,
  columns: ColumnDef<TData, TValue>[],
) {
  return filters && filters.length > 0
    ? filters.map((f) => {
        const columnMeta = columns.find((c) => c.id === f.id)!.meta!

        const values =
          columnMeta.type === 'date'
            ? f.value.values.map((v: string) => new Date(v))
            : f.value.values

        return {
          ...f,
          value: {
            operator: f.value.operator,
            values,
            columnMeta,
          },
        }
      })
    : []
}
```

5. Update your date table component file:

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { parseAsJson, useQueryState } from 'nuqs'
import { type ColumnDef } from '@tanstack/react-table'

export default function YourDataTableComponent() {
  const [queryFilters, setQueryFilters] = useQueryState(
    'filter',
    parseAsJson(dataTableFilterQuerySchema.parse).withDefault([]),
  )
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    // Replace `Issue` with your data type
    () => initializeFiltersFromQuery(queryFilters, columns as ColumnDef<Issue>[]),
  )

  const table = useReactTable({
    /* ... */
  })

  React.useEffect(() => {
    setQueryFilters(
      columnFilters.map((f) => ({
        id: f.id,
        value: { ...(f.value as any), columnMeta: undefined },
      })),
    )
  }, [columnFilters, setQueryFilters])

  /* ... */
}
```

## Overview

Let's take a high-level look at how we've created the data table filter component.

This will help you understand what each file contains and the general component composition.

### File structure

The data table filter component is composed of several files.

Components are placed in the `@/components` directory - all components are placed in a single file for ease of distribution:

- `data-table-filter.tsx`: The main component file.

Types, interfaces, and utilities are placed in the `@/lib` directory:

- `array.ts`: Utility functions for working with arrays.
- `filters.ts`: All TypeScript types, interfaces, and constants related to the data table filter component. Also includes the filter functions `filterFn()` for each column type.
- `table.ts`: Utility functions for working with the TanStack Table library.

### Component structure

A `PropertyFilterItem` component is composed of the following parts:

- `PropertyFilterSubject` shows the name and _(optionally)_ icon of the property being filtered on.
- `PropertyFilterOperator` shows the operator used to filter on the property.
- `PropertyFilterValue` shows the actual filter value.

![](https://ui.bazza.dev/_next/image?url=%2Fdocs%2Fdata-table-filter%2Fproperty-filter-item-composition-light.png&w=3840&q=75)![](https://ui.bazza.dev/_next/image?url=%2Fdocs%2Fdata-table-filter%2Fproperty-filter-item-composition-dark.png&w=3840&q=75)

The composition of a property filter item.

The `PropertyFilterOperator` and `PropertyFilterValue` components are represented by a `Controller` which is essentially a `Popover` with an associated trigger and content.

We can break down the `PropertyFilterValueController` as an example:

- `PropertyFilterValueDisplay` is the popover **trigger**. This displays the filter value for the associated property.
- `PropertyFilterValueMenu` is the popover **content**. This renders the menu for modifying the filter value.

![](https://ui.bazza.dev/_next/image?url=%2Fdocs%2Fdata-table-filter%2Fproperty-filter-value-composition-light.png&w=3840&q=75)![](https://ui.bazza.dev/_next/image?url=%2Fdocs%2Fdata-table-filter%2Fproperty-filter-value-composition-dark.png&w=3840&q=75)

The composition of a property filter value controller.

The `PropertyFilterOperatorController` has a similar composition and can be inferred from the above description and image.

## Changelog

### 2025.04.01

This is a breaking change.

This adds support for filtering columns where the column value is not strictly a property of the original data. This was not possible before, due to the limitation of `defineMeta`'s first argument, which only accepted a direct property on the initial data type.

You can now filter columns where the value is:

- a deeply nested property (i.e. `user.name`)
- accessed using a function (i.e. `row => row.user.name.split(' ')[0]`)

To accomplish this, we've decided to change the interface for the `defineMeta` helper function. The first property is now an **accessor function**, instead of an accessor key.

See the example below for how to migrate:

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
type Issue = {
  status: string
  user: {
    name: string
  }
}
```

```relative rounded-sm bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
const columns = [\
  /* ... */\
  columnHelper.accessor('status', {\
    meta: defineMeta(\
      'status',\
      row => row.status,\
      {\
        type: 'option',\
        icon: CircleDotDashedIcon,\
        options: ISSUE_STATUSES,\
      }\
    ),\
  }),\
  columnHelper.accessor(row => row.user.name, {\
    meta: defineMeta(\
      row => row.user.name,\
      {\
        type: 'option',\
        icon: AvatarIcon,\
        /* ... */\
      }\
    ),\
  }),\
]
```

On This Page

- [Introduction](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#introduction)
- [Prerequisites](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#prerequisites)
- [Installation](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#installation)
- [Concepts](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#concepts)
  - [Column data types](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#column-data-types)
  - [Column options](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#column-options)
  - [Column meta](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#column-meta)
- [Usage](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#usage)
  - [Add component](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#add-component)
  - [Update columns](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#update-columns)
- [Integrations](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#integrations)
  - [nuqs](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#nuqs)
- [Overview](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#overview)
  - [File structure](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#file-structure)
  - [Component structure](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#component-structure)
- [Changelog](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#changelog)
  - [2025.04.01](https://ui.bazza.dev/docs/data-table-filter?filter=[{%22id%22:%22title%22,%22value%22:{%22operator%22:%22contains%22,%22values%22:[%22fix+pay%22]}}]#20250401)


Example Code:

python```
"use client"

import * as React from "react"
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { ArrowUpDown, ChevronDown, MoreHorizontal } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const data: Payment[] = [
  {
    id: "m5gr84i9",
    amount: 316,
    status: "success",
    email: "ken99@example.com",
  },
  {
    id: "3u1reuv4",
    amount: 242,
    status: "success",
    email: "Abe45@example.com",
  },
  {
    id: "derv1ws0",
    amount: 837,
    status: "processing",
    email: "Monserrat44@example.com",
  },
  {
    id: "5kma53ae",
    amount: 874,
    status: "success",
    email: "Silas22@example.com",
  },
  {
    id: "bhqecj4p",
    amount: 721,
    status: "failed",
    email: "carmella@example.com",
  },
]

export type Payment = {
  id: string
  amount: number
  status: "pending" | "processing" | "success" | "failed"
  email: string
}

export const columns: ColumnDef<Payment>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => (
      <div className="capitalize">{row.getValue("status")}</div>
    ),
  },
  {
    accessorKey: "email",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Email
          <ArrowUpDown />
        </Button>
      )
    },
    cell: ({ row }) => <div className="lowercase">{row.getValue("email")}</div>,
  },
  {
    accessorKey: "amount",
    header: () => <div className="text-right">Amount</div>,
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue("amount"))

      // Format the amount as a dollar amount
      const formatted = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount)

      return <div className="text-right font-medium">{formatted}</div>
    },
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const payment = row.original

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem
              onClick={() => navigator.clipboard.writeText(payment.id)}
            >
              Copy payment ID
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>View customer</DropdownMenuItem>
            <DropdownMenuItem>View payment details</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]

export function DataTableDemo() {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  })

  return (
    <div className="w-full">
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter emails..."
          value={(table.getColumn("email")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("email")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="ml-auto">
              Columns <ChevronDown />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter((column) => column.getCanHide())
              .map((column) => {
                return (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize"
                    checked={column.getIsVisible()}
                    onCheckedChange={(value) =>
                      column.toggleVisibility(!!value)
                    }
                  >
                    {column.id}
                  </DropdownMenuCheckboxItem>
                )
              })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
```