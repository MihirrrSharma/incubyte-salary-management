import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Divider,
  Drawer,
  IconButton,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import CloseRounded from "@mui/icons-material/CloseRounded";
import { ApiError, updateEmployeeSalary } from "../../api/client";
import type { Employee } from "../../api/types";

interface EmployeeDetailDrawerProps {
  employee: Employee | null;
  onClose: () => void;
  onUpdated: (employee: Employee) => void;
}

function userMessage(error: unknown): string {
  return error instanceof ApiError
    ? error.message
    : "Salary could not be updated. Please try again.";
}

export function EmployeeDetailDrawer({ employee, onClose, onUpdated }: EmployeeDetailDrawerProps) {
  const [salaryAmount, setSalaryAmount] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    setSalaryAmount(employee?.salary_amount ?? "");
    setError(null);
    setSuccess(false);
  }, [employee?.employee_id]);

  const saveSalary = async () => {
    if (!employee) return;
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const updatedEmployee = await updateEmployeeSalary(employee.employee_id, salaryAmount);
      setSalaryAmount(updatedEmployee.salary_amount);
      setSuccess(true);
      onUpdated(updatedEmployee);
    } catch (caughtError) {
      setError(userMessage(caughtError));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Drawer anchor="right" open={Boolean(employee)} onClose={onClose}>
      {employee && (
        <Stack className="employee-drawer" spacing={2.5}>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
            <div>
              <Typography variant="overline" color="text.secondary">EMPLOYEE RECORD</Typography>
              <Typography variant="h5" className="drawer-title">{employee.name}</Typography>
              <Typography color="text.secondary">{employee.employee_id}</Typography>
            </div>
            <IconButton aria-label="Close employee details" onClick={onClose}>
              <CloseRounded />
            </IconButton>
          </Stack>

          <Divider />
          <div className="detail-grid">
            <div><span>Country</span><strong>{employee.country}</strong></div>
            <div><span>Department</span><strong>{employee.department}</strong></div>
            <div><span>Last updated</span><strong>{new Date(employee.updated_at).toLocaleString()}</strong></div>
          </div>
          <Divider />

          <div>
            <Typography variant="overline" color="text.secondary">CURRENT COMPENSATION</Typography>
            <Typography variant="h4" className="salary-display">
              {employee.salary_amount} <small>{employee.currency}</small>
            </Typography>
          </div>

          <TextField
            label="Annual salary"
            value={salaryAmount}
            onChange={(event) => setSalaryAmount(event.target.value)}
            type="text"
            inputProps={{ inputMode: employee.currency === "JPY" ? "numeric" : "decimal" }}
            helperText={`Amount in ${employee.currency}; currency cannot be changed.`}
            fullWidth
          />
          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">Salary updated successfully.</Alert>}
          <Button variant="contained" onClick={saveSalary} disabled={saving || !salaryAmount.trim()}>
            {saving ? "Saving…" : "Save salary"}
          </Button>
        </Stack>
      )}
    </Drawer>
  );
}