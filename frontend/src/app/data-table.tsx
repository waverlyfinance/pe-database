"use client"

import React, { useEffect, useState } from 'react';
import { z } from 'zod';

import { MoreHorizontal } from "lucide-react"
import { Checkbox } from "@/components/ui/checkbox"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

import {
    ColumnDef,
    flexRender,
    getCoreRowModel,
    getPaginationRowModel,
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

import { Button } from "@/components/ui/button"

import {
    ChevronLeftIcon,
    ChevronRightIcon,
    DoubleArrowLeftIcon,
    DoubleArrowRightIcon,
  } from "@radix-ui/react-icons"

  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from "@/components/ui/select"

// Zod schema
const PortcoSchema = z.object({
  firm: z.string(),
  company_name: z.string(),
  industry_stan: z.string().nullable(),
  region_stan: z.string().nullable(),
  fund: z.string().nullable(),
  date_of_investment_stan: z.number().nullable(),
  company_description: z.string().nullable(),
  status_current_stan: z.string().nullable(),
  website: z.string().nullable(),
});
 
export type Portco = z.infer<typeof PortcoSchema>;

// define table columns
export const columns: ColumnDef<Portco>[] = [
  
  // First column is Row Selection. Checkboxes to be clicked
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

  // Other columns for the table
  {
    accessorKey: "firm",
    header: "Firm",
  },
  {
    accessorKey: "company_name",
    header: "Company",
  },
  {
    accessorKey: "industry_stan",
    header: "Industry",
  },
  {
    accessorKey: "fund",
    header: "Fund",
  },
  {
    accessorKey: "date_of_investment_stan",
    header: "Date of Investment",
  },
  {
    accessorKey: "company_description",
    header: "Description",
  },
  {
    accessorKey: "status_current_stan",
    header: "Status",
  },
  {
    accessorKey: "website",
    header: "Website",
    cell: info => {
        const url = info.getValue();
        return url ? <a href={String(url)} target="_blank" rel="noopener noreferrer">link</a> : null; // if there is a valid URL, return a link. Otherwise, null 
    },
  },
]


// 
interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[]
    data: TData[]
  }

export function DataTable<TData, TValue>({ columns, data, }: DataTableProps<TData, TValue>) {
  const [selectedRows, setSelectedRows] = useState<any>([]); // State declaration. Used for selecting rows

  const table = useReactTable({
    data: data || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
          pageSize: 50, // sets page size to 50
      },
    },
  })

  if (!data) {
      return <div>Loading...</div>;
  }

  // React hook to monitor changes in row selection
  useEffect(() => {
    const updateSelectedRows = table.getSelectedRowModel().rows.map(row => row.original); // table.getSelectedRowModel() is a React Table function
    setSelectedRows(updateSelectedRows);
  }, [table.getSelectedRowModel().rows]); 

  // Function to perform actions with selected rows
  const getSelectedRows = () => { 
    const selectedData = selectedRows.map(row => ({
      company_name: row.company_name, 
      firm: row.firm
    }));
    console.log(selectedData); // To update in the future with additional actions
  };

  // JSX section
  return (
  <>
  {/* Button to trigger actions using selected rows  */}
  <div className="flex items-center justify-between">
    {/* useState hook to only make this clickable if rows are selected */}
      <Button 
        onClick={getSelectedRows} 
        disabled={selectedRows.length === 0}
        title={selectedRows.length === 0 ? "Must select rows first": ""}
      >
          Perform custom Google search</Button>
    </div>

  {/* Pagination control. Page size of 50 */}
  <div className="flex items-center justify-between px-2">
      <div className="flex-1 text-sm text-muted-foreground">
          {/* {table.getState().pagination.pageSize * table} {" "} */}
          {table.getFilteredRowModel().rows.length} total results
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
              {[25, 50, 100].map((pageSize) => (
                  <SelectItem key={pageSize} value={`${pageSize}`}>
                  {pageSize}
                  </SelectItem>
              ))}
              </SelectContent>
          </Select>
          </div>
      </div>
  </div>
  
  <div>
    {/* Table content */}
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
  </div>
    
  {/* Buttons for pagination */}
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
      <DoubleArrowLeftIcon className="h-4 w-4" />
      </Button>
      <Button
      variant="outline"
      className="h-8 w-8 p-0"
      onClick={() => table.previousPage()}
      disabled={!table.getCanPreviousPage()}
      >
      <span className="sr-only">Go to previous page</span>
      <ChevronLeftIcon className="h-4 w-4" />
      </Button>
      <Button
      variant="outline"
      className="h-8 w-8 p-0"
      onClick={() => table.nextPage()}
      disabled={!table.getCanNextPage()}
      >
      <span className="sr-only">Go to next page</span>
      <ChevronRightIcon className="h-4 w-4" />
      </Button>
      <Button
      variant="outline"
      className="hidden h-8 w-8 p-0 lg:flex"
      onClick={() => table.setPageIndex(table.getPageCount() - 1)}
      disabled={!table.getCanNextPage()}
      >
      <span className="sr-only">Go to last page</span>
      <DoubleArrowRightIcon className="h-4 w-4" />
      </Button>
  </div>

  </>
  )
}  