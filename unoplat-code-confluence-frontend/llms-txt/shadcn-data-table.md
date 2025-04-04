[Docs](https://ui.shadcn.com/docs)

Data Table

# Data Table

Powerful table and datagrids built using TanStack Table.

[Docs](https://tanstack.com/table/v8/docs/introduction)

PreviewCode

Style: New York

Copy

Columns

|  | Status | Email | Amount |  |
| --- | --- | --- | --- | --- |
|  | success | ken99@example.com | $316.00 | Open menu |
|  | success | Abe45@example.com | $242.00 | Open menu |
|  | processing | Monserrat44@example.com | $837.00 | Open menu |
|  | success | Silas22@example.com | $874.00 | Open menu |
|  | failed | carmella@example.com | $721.00 | Open menu |

0 of 5 row(s) selected.

PreviousNext

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#introduction) Introduction

Every data table or datagrid I've created has been unique. They all behave differently, have specific sorting and filtering requirements, and work with different data sources.

It doesn't make sense to combine all of these variations into a single component. If we do that, we'll lose the flexibility that [headless UI](https://tanstack.com/table/v8/docs/introduction#what-is-headless-ui) provides.

So instead of a data-table component, I thought it would be more helpful to provide a guide on how to build your own.

We'll start with the basic `<Table />` component and build a complex data table from scratch.

**Tip:** If you find yourself using the same table in multiple places in your app, you can always extract it into a reusable component.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#table-of-contents) Table of Contents

This guide will show you how to use [TanStack Table](https://tanstack.com/table) and the `<Table />` component to build your own custom data table. We'll cover the following topics:

- [Basic Table](https://ui.shadcn.com/docs/components/data-table#basic-table)
- [Row Actions](https://ui.shadcn.com/docs/components/data-table#row-actions)
- [Pagination](https://ui.shadcn.com/docs/components/data-table#pagination)
- [Sorting](https://ui.shadcn.com/docs/components/data-table#sorting)
- [Filtering](https://ui.shadcn.com/docs/components/data-table#filtering)
- [Visibility](https://ui.shadcn.com/docs/components/data-table#visibility)
- [Row Selection](https://ui.shadcn.com/docs/components/data-table#row-selection)
- [Reusable Components](https://ui.shadcn.com/docs/components/data-table#reusable-components)

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#installation) Installation

1. Add the `<Table />` component to your project:

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm dlx shadcn@latest add table

```

Copy

2. Add `tanstack/react-table` dependency:

pnpmnpmyarnbun

```relative font-mono text-sm leading-none
pnpm add @tanstack/react-table

```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#prerequisites) Prerequisites

We are going to build a table to show recent payments. Here's what our data looks like:

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
type Payment = {
  id: string
  amount: number
  status: "pending" | "processing" | "success" | "failed"
  email: string
}

export const payments: Payment[] = [\
  {\
    id: "728ed52f",\
    amount: 100,\
    status: "pending",\
    email: "m@example.com",\
  },\
  {\
    id: "489e1d42",\
    amount: 125,\
    status: "processing",\
    email: "example@gmail.com",\
  },\
  // ...\
]
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#project-structure) Project Structure

Start by creating the following file structure:

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
app
└── payments
    ├── columns.tsx
    ├── data-table.tsx
    └── page.tsx
```

Copy

I'm using a Next.js example here but this works for any other React framework.

- `columns.tsx` (client component) will contain our column definitions.
- `data-table.tsx` (client component) will contain our `<DataTable />` component.
- `page.tsx` (server component) is where we'll fetch data and render our table.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#basic-table) Basic Table

Let's start by building a basic table.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#column-definitions) Column Definitions

First, we'll define our columns.

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { ColumnDef } from "@tanstack/react-table"

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Payment = {
  id: string
  amount: number
  status: "pending" | "processing" | "success" | "failed"
  email: string
}

export const columns: ColumnDef<Payment>[] = [\
  {\
    accessorKey: "status",\
    header: "Status",\
  },\
  {\
    accessorKey: "email",\
    header: "Email",\
  },\
  {\
    accessorKey: "amount",\
    header: "Amount",\
  },\
]
```

Copy

**Note:** Columns are where you define the core of what your table
will look like. They define the data that will be displayed, how it will be
formatted, sorted and filtered.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#datatable--component)`<DataTable />` component

Next, we'll create a `<DataTable />` component to render our table.

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
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
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}
```

Copy

**Tip**: If you find yourself using `<DataTable />` in multiple places, this is the component you could make reusable by extracting it to `components/ui/data-table.tsx`.

`<DataTable columns={columns} data={data} />`

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#render-the-table) Render the table

Finally, we'll render our table in our page component.

app/payments/page.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Payment, columns } from "./columns"
import { DataTable } from "./data-table"

async function getData(): Promise<Payment[]> {
  // Fetch data from your API here.
  return [\
    {\
      id: "728ed52f",\
      amount: 100,\
      status: "pending",\
      email: "m@example.com",\
    },\
    // ...\
  ]
}

export default async function DemoPage() {
  const data = await getData()

  return (
    <div className="container mx-auto py-10">
      <DataTable columns={columns} data={data} />
    </div>
  )
}
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#cell-formatting) Cell Formatting

Let's format the amount cell to display the dollar amount. We'll also align the cell to the right.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-columns-definition) Update columns definition

Update the `header` and `cell` definitions for amount as follows:

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export const columns: ColumnDef<Payment>[] = [\
  {\
    accessorKey: "amount",\
    header: () => <div className="text-right">Amount</div>,\
    cell: ({ row }) => {\
      const amount = parseFloat(row.getValue("amount"))\
      const formatted = new Intl.NumberFormat("en-US", {\
        style: "currency",\
        currency: "USD",\
      }).format(amount)\
\
      return <div className="text-right font-medium">{formatted}</div>\
    },\
  },\
]
```

Copy

You can use the same approach to format other cells and headers.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#row-actions) Row Actions

Let's add row actions to our table. We'll use a `<Dropdown />` component for this.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-columns-definition-1) Update columns definition

Update our columns definition to add a new `actions` column. The `actions` cell returns a `<Dropdown />` component.

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { ColumnDef } from "@tanstack/react-table"
import { MoreHorizontal } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export const columns: ColumnDef<Payment>[] = [\
  // ...\
  {\
    id: "actions",\
    cell: ({ row }) => {\
      const payment = row.original\
\
      return (\
        <DropdownMenu>\
          <DropdownMenuTrigger asChild>\
            <Button variant="ghost" className="h-8 w-8 p-0">\
              <span className="sr-only">Open menu</span>\
              <MoreHorizontal className="h-4 w-4" />\
            </Button>\
          </DropdownMenuTrigger>\
          <DropdownMenuContent align="end">\
            <DropdownMenuLabel>Actions</DropdownMenuLabel>\
            <DropdownMenuItem\
              onClick={() => navigator.clipboard.writeText(payment.id)}\
            >\
              Copy payment ID\
            </DropdownMenuItem>\
            <DropdownMenuSeparator />\
            <DropdownMenuItem>View customer</DropdownMenuItem>\
            <DropdownMenuItem>View payment details</DropdownMenuItem>\
          </DropdownMenuContent>\
        </DropdownMenu>\
      )\
    },\
  },\
  // ...\
]
```

Copy

You can access the row data using `row.original` in the `cell` function. Use this to handle actions for your row eg. use the `id` to make a DELETE call to your API.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#pagination) Pagination

Next, we'll add pagination to our table.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  // ...
}
```

Copy

This will automatically paginate your rows into pages of 10. See the [pagination docs](https://tanstack.com/table/v8/docs/api/features/pagination) for more information on customizing page size and implementing manual pagination.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#add-pagination-controls) Add pagination controls

We can add pagination controls to our table using the `<Button />` component and the `table.previousPage()`, `table.nextPage()` API methods.

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Button } from "@/components/ui/button"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  })

  return (
    <div>
      <div className="rounded-md border">
        <Table>
          { // .... }
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
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
  )
}
```

Copy

See [Reusable Components](https://ui.shadcn.com/docs/components/data-table#reusable-components) section for a more advanced pagination component.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#sorting) Sorting

Let's make the email column sortable.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable-1) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import * as React from "react"
import {
  ColumnDef,
  SortingState,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting,
    },
  })

  return (
    <div>
      <div className="rounded-md border">
        <Table>{ ... }</Table>
      </div>
    </div>
  )
}
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#make-header-cell-sortable) Make header cell sortable

We can now update the `email` header cell to add sorting controls.

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"

export const columns: ColumnDef<Payment>[] = [\
  {\
    accessorKey: "email",\
    header: ({ column }) => {\
      return (\
        <Button\
          variant="ghost"\
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}\
        >\
          Email\
          <ArrowUpDown className="ml-2 h-4 w-4" />\
        </Button>\
      )\
    },\
  },\
]
```

Copy

This will automatically sort the table (asc and desc) when the user toggles on the header cell.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#filtering) Filtering

Let's add a search input to filter emails in our table.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable-2) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import * as React from "react"
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
    },
  })

  return (
    <div>
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter emails..."
          value={(table.getColumn("email")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("email")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
      </div>
      <div className="rounded-md border">
        <Table>{ ... }</Table>
      </div>
    </div>
  )
}
```

Copy

Filtering is now enabled for the `email` column. You can add filters to other columns as well. See the [filtering docs](https://tanstack.com/table/v8/docs/guide/filters) for more information on customizing filters.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#visibility) Visibility

Adding column visibility is fairly simple using `@tanstack/react-table` visibility API.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable-3) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
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

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({})

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
    state: {
      sorting,
      columnFilters,
      columnVisibility,
    },
  })

  return (
    <div>
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter emails..."
          value={table.getColumn("email")?.getFilterValue() as string}
          onChange={(event) =>
            table.getColumn("email")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="ml-auto">
              Columns
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter(
                (column) => column.getCanHide()
              )
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
        <Table>{ ... }</Table>
      </div>
    </div>
  )
}
```

Copy

This adds a dropdown menu that you can use to toggle column visibility.

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#row-selection) Row Selection

Next, we're going to add row selection to our table.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-column-definitions) Update column definitions

app/payments/columns.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { ColumnDef } from "@tanstack/react-table"

import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"

export const columns: ColumnDef<Payment>[] = [\
  {\
    id: "select",\
    header: ({ table }) => (\
      <Checkbox\
        checked={\
          table.getIsAllPageRowsSelected() ||\
          (table.getIsSomePageRowsSelected() && "indeterminate")\
        }\
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}\
        aria-label="Select all"\
      />\
    ),\
    cell: ({ row }) => (\
      <Checkbox\
        checked={row.getIsSelected()}\
        onCheckedChange={(value) => row.toggleSelected(!!value)}\
        aria-label="Select row"\
      />\
    ),\
    enableSorting: false,\
    enableHiding: false,\
  },\
]
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#update-datatable-4) Update `<DataTable>`

app/payments/data-table.tsx

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
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
    <div>
      <div className="rounded-md border">
        <Table />
      </div>
    </div>
  )
}
```

Copy

This adds a checkbox to each row and a checkbox in the header to select all rows.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#show-selected-rows) Show selected rows

You can show the number of selected rows using the `table.getFilteredSelectedRowModel()` API.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<div className="flex-1 text-sm text-muted-foreground">
  {table.getFilteredSelectedRowModel().rows.length} of{" "}
  {table.getFilteredRowModel().rows.length} row(s) selected.
</div>
```

Copy

## [Link to section](https://ui.shadcn.com/docs/components/data-table\#reusable-components) Reusable Components

Here are some components you can use to build your data tables. This is from the [Tasks](https://ui.shadcn.com/examples/tasks) demo.

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#column-header) Column header

Make any column header sortable and hideable.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Column } from "@tanstack/react-table"
import { ArrowDown, ArrowUp, ChevronsUpDown, EyeOff } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface DataTableColumnHeaderProps<TData, TValue>
  extends React.HTMLAttributes<HTMLDivElement> {
  column: Column<TData, TValue>
  title: string
}

export function DataTableColumnHeader<TData, TValue>({
  column,
  title,
  className,
}: DataTableColumnHeaderProps<TData, TValue>) {
  if (!column.getCanSort()) {
    return <div className={cn(className)}>{title}</div>
  }

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="-ml-3 h-8 data-[state=open]:bg-accent"
          >
            <span>{title}</span>
            {column.getIsSorted() === "desc" ? (
              <ArrowDown />
            ) : column.getIsSorted() === "asc" ? (
              <ArrowUp />
            ) : (
              <ChevronsUpDown />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start">
          <DropdownMenuItem onClick={() => column.toggleSorting(false)}>
            <ArrowUp className="h-3.5 w-3.5 text-muted-foreground/70" />
            Asc
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => column.toggleSorting(true)}>
            <ArrowDown className="h-3.5 w-3.5 text-muted-foreground/70" />
            Desc
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => column.toggleVisibility(false)}>
            <EyeOff className="h-3.5 w-3.5 text-muted-foreground/70" />
            Hide
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
```

Copy

Expand

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
export const columns = [\
  {\
    accessorKey: "email",\
    header: ({ column }) => (\
      <DataTableColumnHeader column={column} title="Email" />\
    ),\
  },\
]
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#pagination-1) Pagination

Add pagination controls to your table including page size and selection count.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
import { Table } from "@tanstack/react-table"
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface DataTablePaginationProps<TData> {
  table: Table<TData>
}

export function DataTablePagination<TData>({
  table,
}: DataTablePaginationProps<TData>) {
  return (
    <div className="flex items-center justify-between px-2">
      <div className="flex-1 text-sm text-muted-foreground">
        {table.getFilteredSelectedRowModel().rows.length} of{" "}
        {table.getFilteredRowModel().rows.length} row(s) selected.
      </div>
      <div className="flex items-center space-x-6 lg:space-x-8">
        <div className="flex items-center space-x-2">
          <p className="text-sm font-medium">Rows per page</p>
          <Select
            value={`${table.getState().pagination.pageSize}`}
            onValueChange={(value) => {
              table.setPageSize(Number(value))
            }}
          >
            <SelectTrigger className="h-8 w-[70px]">
              <SelectValue placeholder={table.getState().pagination.pageSize} />
            </SelectTrigger>
            <SelectContent side="top">
              {[10, 20, 30, 40, 50].map((pageSize) => (
                <SelectItem key={pageSize} value={`${pageSize}`}>
                  {pageSize}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex w-[100px] items-center justify-center text-sm font-medium">
          Page {table.getState().pagination.pageIndex + 1} of{" "}
          {table.getPageCount()}
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            className="hidden h-8 w-8 p-0 lg:flex"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
          >
            <span className="sr-only">Go to first page</span>
            <ChevronsLeft />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 p-0"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <span className="sr-only">Go to previous page</span>
            <ChevronLeft />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 p-0"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <span className="sr-only">Go to next page</span>
            <ChevronRight />
          </Button>
          <Button
            variant="outline"
            className="hidden h-8 w-8 p-0 lg:flex"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
          >
            <span className="sr-only">Go to last page</span>
            <ChevronsRight />
          </Button>
        </div>
      </div>
    </div>
  )
}
```

Copy

Expand

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<DataTablePagination table={table} />
```

Copy

### [Link to section](https://ui.shadcn.com/docs/components/data-table\#column-toggle) Column toggle

A component to toggle column visibility.

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
"use client"

import { DropdownMenuTrigger } from "@radix-ui/react-dropdown-menu"
import { Table } from "@tanstack/react-table"
import { Settings2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu"

interface DataTableViewOptionsProps<TData> {
  table: Table<TData>
}

export function DataTableViewOptions<TData>({
  table,
}: DataTableViewOptionsProps<TData>) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="ml-auto hidden h-8 lg:flex"
        >
          <Settings2 />
          View
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[150px]">
        <DropdownMenuLabel>Toggle columns</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {table
          .getAllColumns()
          .filter(
            (column) =>
              typeof column.accessorFn !== "undefined" && column.getCanHide()
          )
          .map((column) => {
            return (
              <DropdownMenuCheckboxItem
                key={column.id}
                className="capitalize"
                checked={column.getIsVisible()}
                onCheckedChange={(value) => column.toggleVisibility(!!value)}
              >
                {column.id}
              </DropdownMenuCheckboxItem>
            )
          })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

Copy

Expand

```relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm
<DataTableViewOptions table={table} />
```

Copy

[Context Menu](https://ui.shadcn.com/docs/components/context-menu) [Date Picker](https://ui.shadcn.com/docs/components/date-picker)

On This Page

- [Introduction](https://ui.shadcn.com/docs/components/data-table#introduction)
- [Table of Contents](https://ui.shadcn.com/docs/components/data-table#table-of-contents)
- [Installation](https://ui.shadcn.com/docs/components/data-table#installation)
- [Prerequisites](https://ui.shadcn.com/docs/components/data-table#prerequisites)
- [Project Structure](https://ui.shadcn.com/docs/components/data-table#project-structure)
- [Basic Table](https://ui.shadcn.com/docs/components/data-table#basic-table)
  - [Column Definitions](https://ui.shadcn.com/docs/components/data-table#column-definitions)
  - [<DataTable /> component](https://ui.shadcn.com/docs/components/data-table#datatable--component)
  - [Render the table](https://ui.shadcn.com/docs/components/data-table#render-the-table)
- [Cell Formatting](https://ui.shadcn.com/docs/components/data-table#cell-formatting)
  - [Update columns definition](https://ui.shadcn.com/docs/components/data-table#update-columns-definition)
- [Row Actions](https://ui.shadcn.com/docs/components/data-table#row-actions)
  - [Update columns definition](https://ui.shadcn.com/docs/components/data-table#update-columns-definition-1)
- [Pagination](https://ui.shadcn.com/docs/components/data-table#pagination)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable)
  - [Add pagination controls](https://ui.shadcn.com/docs/components/data-table#add-pagination-controls)
- [Sorting](https://ui.shadcn.com/docs/components/data-table#sorting)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable-1)
  - [Make header cell sortable](https://ui.shadcn.com/docs/components/data-table#make-header-cell-sortable)
- [Filtering](https://ui.shadcn.com/docs/components/data-table#filtering)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable-2)
- [Visibility](https://ui.shadcn.com/docs/components/data-table#visibility)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable-3)
- [Row Selection](https://ui.shadcn.com/docs/components/data-table#row-selection)
  - [Update column definitions](https://ui.shadcn.com/docs/components/data-table#update-column-definitions)
  - [Update <DataTable>](https://ui.shadcn.com/docs/components/data-table#update-datatable-4)
  - [Show selected rows](https://ui.shadcn.com/docs/components/data-table#show-selected-rows)
- [Reusable Components](https://ui.shadcn.com/docs/components/data-table#reusable-components)
  - [Column header](https://ui.shadcn.com/docs/components/data-table#column-header)
  - [Pagination](https://ui.shadcn.com/docs/components/data-table#pagination-1)
  - [Column toggle](https://ui.shadcn.com/docs/components/data-table#column-toggle)

Deploy your shadcn/ui app on Vercel

Trusted by OpenAI, Sonos, Chick-fil-A, and more.

Vercel provides tools and infrastructure to deploy apps and features at scale.

Deploy Now [Deploy to Vercel](https://vercel.com/new?utm_source=shadcn_site&utm_medium=web&utm_campaign=docs_cta_deploy_now_callout)