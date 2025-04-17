# Custom Row Actions & Dialogs with DiceUI DataTable

This guide shows how to implement per‑row custom dialogs (e.g. Edit, Delete, nested Labels, or any other custom action) in a Next.js App Router + Shadcn UI + DiceUI DataTable using the `rowAction` pattern.

## 1. Initialize State & Table Instance

```tsx
"use client";

import * as React from "react";
import { DataTable } from "@/components/data-table";
import { useDataTable } from "@/hooks/use-data-table";
import type { ColumnDef } from "@tanstack/react-table";
import type { DataTableRowAction } from "@/types/data-table";

interface DataRow {
  id: string;
  // ... other fields
}

export function YourTable({ data, pageCount }: { data: DataRow[]; pageCount: number }) {
  // 1️⃣ Track the current row action in state
  const [rowAction, setRowAction] = React.useState<DataTableRowAction<DataRow> | null>(null);

  // 2️⃣ Build columns with the setter
  const columns = React.useMemo<ColumnDef<DataRow>[]>(
    () => getYourColumns({ setRowAction }),
    [setRowAction],
  );

  // 3️⃣ Initialize DiceUI DataTable
  const { table } = useDataTable({
    data,
    columns,
    pageCount,
    getRowId: (row) => row.id,
    // see https://diceui.com/docs/components/data-table#useDataTable
  });

  return (
    <>
      <DataTable table={table}>
        {/* optional toolbars */}
      </DataTable>

      {/* 4️⃣ Conditionally render dialogs based on `rowAction` */}
      <YourEditDialog
        open={rowAction?.variant === "edit"}
        onOpenChange={() => setRowAction(null)}
        row={rowAction?.row}
      />
      <YourDeleteDialog
        open={rowAction?.variant === "delete"}
        onOpenChange={() => setRowAction(null)}
        row={rowAction?.row}
      />
    </>
  );
}
```

## 2. Define Columns with Actions

```tsx
// src/app/_components/your-table-columns.tsx
import type { ColumnDef } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Ellipsis } from "lucide-react";
import type { DataTableRowAction } from "@/types/data-table";

export function getYourColumns<TData>({
  setRowAction,
}: {
  setRowAction: React.Dispatch<
    React.SetStateAction<DataTableRowAction<TData> | null>
  >;
}): ColumnDef<TData>[] {
  return [
    // ... other columns
    {
      id: "actions",
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" aria-label="Open menu">
              <Ellipsis />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-40">
            <DropdownMenuItem onSelect={() => setRowAction({ row, variant: "edit" })}>
              Edit
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onSelect={() => setRowAction({ row, variant: "delete" })}>
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
      size: 40,
      // see https://diceui.com/docs/components/data-table#column-definitions
    },
  ];
}
```

## 3. Implement Custom Dialogs

Use Shadcn UI's `Dialog`, `Sheet`, or `Drawer` for your modal UIs:

```tsx
// src/app/_components/your-edit-dialog.tsx
"use client";

import * as React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import type { DataRow } from "./your-table";

interface YourEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  row?: import("@tanstack/react-table").Row<DataRow>;
}

export function YourEditDialog({ open, onOpenChange, row }: YourEditDialogProps) {
  const [formValues, setFormValues] = React.useState(/* init from row?.original */);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Row</DialogTitle>
        </DialogHeader>
        {/* your form fields here */}
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={() => {/* handle save */}}>Save</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

## 4. Summary

By passing a `setRowAction` setter into your column definitions and conditionally rendering dialogs in your parent component based on `rowAction.variant`, you can flexibly implement any per‑row workflow (modals, confirmations, submenus, etc.) with DiceUI DataTable.

---
