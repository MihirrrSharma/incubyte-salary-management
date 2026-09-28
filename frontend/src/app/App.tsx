import { useState } from "react";
import {
  AppBar,
  Box,
  Container,
  Tab,
  Tabs,
  Toolbar,
  Typography,
} from "@mui/material";
import DashboardOutlined from "@mui/icons-material/DashboardOutlined";
import Groups2Outlined from "@mui/icons-material/Groups2Outlined";
import { AnalyticsDashboard } from "../features/analytics/AnalyticsDashboard";
import { EmployeeDirectory } from "../features/employees/EmployeeDirectory";

export function App() {
  const [view, setView] = useState<"overview" | "employees">("overview");

  return (
    <Box className="app-shell">
      <AppBar position="static" color="inherit" elevation={0} className="topbar">
        <Toolbar className="topbar-inner">
          <div className="brand-lockup" aria-label="ACME people operations">
            <div className="brand-mark">A</div>
            <div>
              <Typography className="brand-name">ACME</Typography>
              <Typography className="brand-caption">PEOPLE OPERATIONS</Typography>
            </div>
          </div>
          <div className="topbar-context">
            <span className="status-dot" />
            <Typography variant="body2">HR workspace</Typography>
          </div>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" className="page-container">
        <Box className="navigation-wrap">
          <Tabs
            value={view}
            onChange={(_, value: "overview" | "employees") => setView(value)}
            aria-label="Salary management views"
          >
            <Tab value="overview" label="Overview" icon={<DashboardOutlined fontSize="small" />} iconPosition="start" />
            <Tab value="employees" label="People" icon={<Groups2Outlined fontSize="small" />} iconPosition="start" />
          </Tabs>
        </Box>

        <main className="main-content">
          {view === "overview" ? <AnalyticsDashboard /> : <EmployeeDirectory />}
        </main>
        <footer className="page-footer">
          <Typography variant="caption">ACME · Compensation data is shown in each employee’s local currency.</Typography>
        </footer>
      </Container>
    </Box>
  );
}