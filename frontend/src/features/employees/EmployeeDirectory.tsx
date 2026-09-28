import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  TextField,
  Typography,
} from "@mui/material";
import SearchRounded from "@mui/icons-material/SearchRounded";
import { ApiError, getEmployees } from "../../api/client";
import type { AnalyticsQuery, Employee, EmployeePage, EmployeeQuery, SortField } from "../../api/types";
import { EmployeeFilters } from "../../components/EmployeeFilters";
import { LoadState } from "../../components/LoadState";
import { EmployeeDetailDrawer } from "./EmployeeDetailDrawer";

const INITIAL_QUERY: EmployeeQuery = {
  page: 1,
  page_size: 25,
  sort_by: "employee_id",
  sort_order: "asc",
};

const COLUMNS: { key: SortField; label: string }[] = [
  { key: "employee_id", label: "Employee ID" },
  { key: "name", label: "Name" },
  { key: "country", label: "Country" },
  { key: "department", label: "Department" },
  { key: "salary", label: "Annual salary" },
  { key: "updated_at", label: "Last updated" },
];

function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : "Employee data could not be loaded.";
}

export function EmployeeDirectory() {
  const [query, setQuery] = useState<EmployeeQuery>(INITIAL_QUERY);
  const [searchInput, setSearchInput] = useState("");
  const [filters, setFilters] = useState<AnalyticsQuery>({ country: "", department: "", currency: "" });
  const [result, setResult] = useState<EmployeePage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [refreshVersion, setRefreshVersion] = useState(0);

  useEffect(() => {
    let active = true;
    const debounce = window.setTimeout(() => {
      const nextQuery: EmployeeQuery = {
        ...query,
        search: searchInput.trim() || undefined,
        country: filters.country?.trim() || undefined,
        department: filters.department?.trim() || undefined,
        currency: filters.currency || undefined,
      };
      setLoading(true);
      setError(null);
      getEmployees(nextQuery)
        .then((page) => {
          if (active) setResult(page);
        })
        .catch((caughtError: unknown) => {
          if (active) setError(errorMessage(caughtError));
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    }, 250);
    return () => {
      active = false;
      window.clearTimeout(debounce);
    };
  }, [query, searchInput, filters, refreshVersion]);

  const updateFilter = (next: AnalyticsQuery) => {
    setFilters(next);
    setQuery((current) => ({
      ...current,
      page: 1,
      sort_by: current.sort_by === "salary" && !next.currency ? "employee_id" : current.sort_by,
    }));
  };

  const changeSort = (field: SortField) => {
    if (field === "salary" && !filters.currency) return;
    setQuery((current) => ({
      ...current,
      page: 1,
      sort_by: field,
      sort_order:
        current.sort_by === field && current.sort_order === "asc" ? "desc" : "asc",
    }));
  };

  const employeeUpdated = (updated: Employee) => {
    setSelectedEmployee(updated);
    setRefreshVersion((version) => version + 1);
  };

  const empty = !loading && !error && Boolean(result && result.items.length === 0);

  return (
    <Stack spacing={2.5}>
      <Stack className="section-heading" direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ md: "flex-end" }} spacing={1.5}>
        <div>
          <Typography variant="overline" color="text.secondary">PEOPLE</Typography>
          <Typography variant="h4" className="page-title">Employee directory</Typography>
          <Typography color="text.secondary">Search, inspect, and update current annual salaries.</Typography>
        </div>
        <Typography className="result-count" color="text.secondary">
          {result ? `${result.total.toLocaleString()} employees` : "Directory"}
        </Typography>
      </Stack>

      <Paper className="filter-panel" variant="outlined">
        <Stack spacing={1.5}>
          <Stack direction={{ xs: "column", lg: "row" }} spacing={1.5}>
            <TextField
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              label="Search employee ID or name"
              placeholder="e.g. SYN00042 or Morgan"
              size="small"
              fullWidth
              InputProps={{
                startAdornment: <SearchRounded fontSize="small" sx={{ color: "text.secondary", mr: 1 }} />,
              }}
            />
            <EmployeeFilters value={filters} onChange={updateFilter} />
          </Stack>
          {query.sort_by === "salary" && !filters.currency && (
            <Alert severity="info">Choose a currency before sorting by salary.</Alert>
          )}
        </Stack>
      </Paper>

      {loading || empty || (Boolean(error) && !result) ? (
        <LoadState
          loading={loading}
          error={error}
          empty={empty}
          emptyMessage="Try changing the search or filters."
          onRetry={() => setRefreshVersion((version) => version + 1)}
        />
      ) : (
        <Paper className="table-panel" variant="outlined">
          <TableContainer>
            <Table aria-label="Employee directory" size="medium">
              <TableHead>
                <TableRow>
                  {COLUMNS.map((column) => (
                    <TableCell key={column.key} sortDirection={query.sort_by === column.key ? query.sort_order : false}>
                      <TableSortLabel
                        active={query.sort_by === column.key}
                        direction={query.sort_by === column.key ? query.sort_order : "asc"}
                        disabled={column.key === "salary" && !filters.currency}
                        onClick={() => changeSort(column.key)}
                      >
                        {column.label}
                      </TableSortLabel>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {result?.items.map((employee) => (
                  <TableRow key={employee.employee_id} hover>
                    <TableCell>
                      <Button
                        className="employee-link"
                        onClick={() => setSelectedEmployee(employee)}
                        aria-label={`Open employee ${employee.employee_id}`}
                      >
                        {employee.employee_id}
                      </Button>
                    </TableCell>
                    <TableCell>{employee.name}</TableCell>
                    <TableCell>{employee.country}</TableCell>
                    <TableCell>{employee.department}</TableCell>
                    <TableCell className="salary-cell">{employee.salary_amount} <span>{employee.currency}</span></TableCell>
                    <TableCell>{new Date(employee.updated_at).toLocaleDateString()}</TableCell>
                  </TableRow>
                ))}
                {result?.items.length === 0 && (
                  <TableRow><TableCell colSpan={COLUMNS.length}>No employees match these filters.</TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
          {error && <Alert severity="error" sx={{ m: 2 }}>{error}</Alert>}
          <TablePagination
            component="div"
            count={result?.total ?? 0}
            page={query.page - 1}
            rowsPerPage={query.page_size}
            rowsPerPageOptions={[25, 50, 100]}
            onPageChange={(_, page) => setQuery((current) => ({ ...current, page: page + 1 }))}
            onRowsPerPageChange={(event) => setQuery((current) => ({ ...current, page: 1, page_size: Number(event.target.value) }))}
          />
        </Paper>
      )}

      <EmployeeDetailDrawer
        employee={selectedEmployee}
        onClose={() => setSelectedEmployee(null)}
        onUpdated={employeeUpdated}
      />
      <Box className="sr-only" aria-live="polite">{loading ? "Refreshing employee directory" : ""}</Box>
    </Stack>
  );
}