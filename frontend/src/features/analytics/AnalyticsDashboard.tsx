import { useEffect, useState } from "react";
import {
  Box,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ApiError, getCompensationAnalytics } from "../../api/client";
import type { AnalyticsQuery, CompensationAnalytics } from "../../api/types";
import { EmployeeFilters } from "../../components/EmployeeFilters";
import { LoadState } from "../../components/LoadState";
import type { ReactNode } from "react";

function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : "Compensation insights could not be loaded.";
}

export function AnalyticsDashboard() {
  const [filters, setFilters] = useState<AnalyticsQuery>({});
  const [data, setData] = useState<CompensationAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    getCompensationAnalytics(filters)
      .then((result) => {
        if (active) setData(result);
      })
      .catch((caughtError: unknown) => {
        if (active) setError(errorMessage(caughtError));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [filters, retryCount]);

  return (
    <Stack spacing={2.5}>
      <Stack className="section-heading" direction={{ xs: "column", md: "row" }} justifyContent="space-between" alignItems={{ md: "flex-end" }} spacing={1.5}>
        <div>
          <Typography variant="overline" color="text.secondary">COMPENSATION</Typography>
          <Typography variant="h4" className="page-title">Overview</Typography>
          <Typography color="text.secondary">A current view of employee distribution and salary ranges.</Typography>
        </div>
        <Typography className="as-of-label">Live data · filters apply to all totals</Typography>
      </Stack>

      <Paper className="filter-panel" variant="outlined">
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ md: "center" }} justifyContent="space-between">
          <div>
            <Typography fontWeight={700}>Refine this view</Typography>
            <Typography variant="body2" color="text.secondary">Salary figures always stay grouped by currency.</Typography>
          </div>
          <EmployeeFilters value={filters} onChange={setFilters} />
        </Stack>
      </Paper>

      {loading && <LoadState loading error={null} empty={false} emptyMessage="" onRetry={() => setRetryCount((count) => count + 1)} />}
      {!loading && error && <LoadState loading={false} error={error} empty={false} emptyMessage="" onRetry={() => setRetryCount((count) => count + 1)} />}
      {!loading && !error && data && (
        <>
          {data.employee_count === 0 ? (
            <LoadState loading={false} error={null} empty emptyMessage="No employees match the selected filters." onRetry={() => setRetryCount((count) => count + 1)} />
          ) : (
            <>
              <Paper className="headcount-panel" variant="outlined">
                <Typography variant="overline" color="text.secondary">EMPLOYEES IN VIEW</Typography>
                <Typography variant="h3" className="headcount-number">{data.employee_count.toLocaleString()}</Typography>
                <Typography color="text.secondary">Current employee records</Typography>
              </Paper>

              <section className="salary-section" aria-labelledby="salary-summary-heading">
                <Stack direction="row" justifyContent="space-between" alignItems="baseline" className="section-title-row">
                  <Typography id="salary-summary-heading" variant="h5" className="subsection-title">Salary metrics by currency</Typography>
                  <Typography variant="body2" color="text.secondary">No foreign-exchange conversion</Typography>
                </Stack>
                <div className="currency-grid">
                  {data.salary_by_currency.map((group) => (
                    <Paper className="currency-panel" variant="outlined" key={group.currency}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" className="currency-panel-heading">
                        <Typography variant="h6">{group.currency}</Typography>
                        <Typography variant="body2" color="text.secondary">{group.employee_count} employees</Typography>
                      </Stack>
                      <div className="metric-grid">
                        <Metric label="Average" value={group.average_salary} currency={group.currency} />
                        <Metric label="Median" value={group.median_salary} currency={group.currency} />
                        <Metric label="Minimum" value={group.minimum_salary} currency={group.currency} />
                        <Metric label="Maximum" value={group.maximum_salary} currency={group.currency} />
                      </div>
                      <DividerLabel>Salary distribution · {group.currency}</DividerLabel>
                      <Box className="chart-wrap" role="img" aria-label={`${group.currency} salary distribution`}>
                        <ResponsiveContainer width="100%" height={210}>
                          <BarChart data={group.salary_distribution.map((bucket) => ({
                            range: `${bucket.minimum_salary}–${bucket.maximum_salary}`,
                            employees: bucket.employee_count,
                          }))} margin={{ top: 8, right: 8, bottom: 42, left: -18 }}>
                            <CartesianGrid stroke="#e5e9e3" vertical={false} />
                            <XAxis dataKey="range" angle={-25} textAnchor="end" interval={0} tick={{ fontSize: 10, fill: "#65736d" }} />
                            <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#65736d" }} />
                            <Tooltip formatter={(value) => [`${value} employees`, "Employees"]} />
                            <Bar dataKey="employees" fill="#247263" radius={[3, 3, 0, 0]} maxBarSize={44} />
                          </BarChart>
                        </ResponsiveContainer>
                      </Box>
                    </Paper>
                  ))}
                </div>
              </section>

              <div className="distribution-grid">
                <CountTable
                  title="Employees by country"
                  label="Country"
                  rows={data.employees_by_country.map((row) => ({ label: row.country, count: row.employee_count }))}
                />
                <CountTable
                  title="Employees by department"
                  label="Department"
                  rows={data.employees_by_department.map((row) => ({ label: row.department, count: row.employee_count }))}
                />
              </div>
            </>
          )}
        </>
      )}
    </Stack>
  );
}

function Metric({ label, value, currency }: { label: string; value: string; currency: string }) {
  return (
    <div className="metric-cell">
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Typography className="metric-value">{value} <span>{currency}</span></Typography>
    </div>
  );
}

function DividerLabel({ children }: { children: ReactNode }) {
  return <Typography className="chart-label" variant="caption">{children}</Typography>;
}

function CountTable({ title, label, rows }: { title: string; label: string; rows: { label: string; count: number }[] }) {
  return (
    <Paper className="count-panel" variant="outlined">
      <Typography variant="h6" className="count-title">{title}</Typography>
      <Table size="small" aria-label={title}>
        <TableHead><TableRow><TableCell>{label}</TableCell><TableCell align="right">Employees</TableCell></TableRow></TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.label}><TableCell>{row.label}</TableCell><TableCell align="right">{row.count.toLocaleString()}</TableCell></TableRow>
          ))}
          {rows.length === 0 && <TableRow><TableCell colSpan={2}>No counts for this view.</TableCell></TableRow>}
        </TableBody>
      </Table>
    </Paper>
  );
}