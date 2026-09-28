import { Alert, Box, Button, CircularProgress, Stack, Typography } from "@mui/material";

interface LoadStateProps {
  loading: boolean;
  error: string | null;
  empty: boolean;
  emptyMessage: string;
  onRetry: () => void;
}

export function LoadState({ loading, error, empty, emptyMessage, onRetry }: LoadStateProps) {
  if (loading) {
    return (
      <Box className="load-state" role="status" aria-label="Loading">
        <CircularProgress size={28} />
        <Typography color="text.secondary">Loading salary data</Typography>
      </Box>
    );
  }
  if (error) {
    return (
      <Alert
        severity="error"
        action={<Button color="inherit" size="small" onClick={onRetry}>Retry</Button>}
      >
        {error}
      </Alert>
    );
  }
  if (empty) {
    return (
      <Stack className="empty-state" spacing={0.5}>
        <Typography fontWeight={700}>Nothing to show</Typography>
        <Typography color="text.secondary">{emptyMessage}</Typography>
      </Stack>
    );
  }
  return null;
}