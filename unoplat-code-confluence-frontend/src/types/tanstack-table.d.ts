import "@tanstack/react-table";
import type { Row } from "@tanstack/react-table";
import type { ParentWorkflowJobResponse } from "./index";

declare module "@tanstack/react-table" {
  interface ColumnMeta<TData, TValue> {
    handleRowAction?: (action: { row: Row<TData>; variant: string }) => void;
  }

  interface TableMeta<TData> {
    handleRowAction?: (action: { row: Row<TData>; variant: string }) => void;
  }
}
