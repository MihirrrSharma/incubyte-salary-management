import { MenuItem, Stack, TextField } from "@mui/material";
import type { AnalyticsQuery } from "../api/types";

interface EmployeeFiltersProps {
  value: AnalyticsQuery;
  onChange: (next: AnalyticsQuery) => void;
}

export function EmployeeFilters({ value, onChange }: EmployeeFiltersProps) {
  const update = (key: keyof AnalyticsQuery, nextValue: string) => {
    onChange({ ...value, [key]: nextValue || undefined });
  };

  return (
    <Stack className="filter-row" direction="row" spacing={1.5} useFlexGap flexWrap="wrap">
      <TextField
        label="Country"
        value={value.country ?? ""}
        onChange={(event) => update("country", event.target.value)}
        placeholder="Any country"
        size="small"
        inputProps={{ "aria-label": "Country filter" }}
      />
      <TextField
        label="Department"
        value={value.department ?? ""}
        onChange={(event) => update("department", event.target.value)}
        placeholder="Any department"
        size="small"
        inputProps={{ "aria-label": "Department filter" }}
      />
      <TextField
        select
        label="Currency"
        value={value.currency ?? ""}
        onChange={(event) => update("currency", event.target.value)}
        size="small"
        sx={{ minWidth: 150 }}
      >
        <MenuItem value="">All currencies</MenuItem>
        <MenuItem value="CAD">CAD</MenuItem>
        <MenuItem value="JPY">JPY</MenuItem>
        <MenuItem value="USD">USD</MenuItem>
      </TextField>
    </Stack>
  );
}