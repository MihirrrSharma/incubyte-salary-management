import React from "react";
import ReactDOM from "react-dom/client";
import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import { App } from "./app/App";
import "./styles.css";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#176b5b", dark: "#104b40" },
    secondary: { main: "#cb684e" },
    background: { default: "#f3f5f1", paper: "#ffffff" },
    text: { primary: "#172522", secondary: "#64736d" },
    divider: "#e3e8e2",
  },
  shape: { borderRadius: 8 },
  typography: {
    fontFamily: '"Aptos", "Segoe UI", "Helvetica Neue", sans-serif',
    h4: { fontSize: "1.8rem", fontWeight: 700 },
    h5: { fontSize: "1.22rem", fontWeight: 700 },
    h6: { fontSize: "1rem", fontWeight: 700 },
    button: { textTransform: "none", fontWeight: 650 },
  },
  components: {
    MuiPaper: { styleOverrides: { root: { borderRadius: 8 } } },
    MuiButton: { defaultProps: { disableElevation: true } },
    MuiTableCell: { styleOverrides: { head: { color: "#64736d", fontWeight: 700, whiteSpace: "nowrap" } } },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>,
);