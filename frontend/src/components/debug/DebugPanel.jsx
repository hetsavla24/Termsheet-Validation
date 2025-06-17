import React from 'react';
import { Box, Typography, Paper, Button } from '@mui/material';
import useAuthStore from '../../store/authStore';

const DebugPanel = () => {
  const authState = useAuthStore();

  const clearStorage = () => {
    localStorage.clear();
    window.location.reload();
  };

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 16,
        right: 16,
        p: 2,
        minWidth: 300,
        maxWidth: 400,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        color: 'white',
        zIndex: 9999,
        fontSize: '0.75rem',
      }}
    >
      <Typography variant="h6" gutterBottom>
        Debug Panel
      </Typography>
      
      <Box mb={2}>
        <Typography variant="subtitle2">Auth State:</Typography>
        <Typography variant="body2">
          isAuthenticated: {authState.isAuthenticated ? 'true' : 'false'}
        </Typography>
        <Typography variant="body2">
          isLoading: {authState.isLoading ? 'true' : 'false'}
        </Typography>
        <Typography variant="body2">
          user: {authState.user ? JSON.stringify(authState.user, null, 2) : 'null'}
        </Typography>
        <Typography variant="body2">
          token: {authState.token ? 'exists' : 'null'}
        </Typography>
      </Box>

      <Box mb={2}>
        <Typography variant="subtitle2">Location:</Typography>
        <Typography variant="body2">
          pathname: {window.location.pathname}
        </Typography>
        <Typography variant="body2">
          hash: {window.location.hash}
        </Typography>
      </Box>

      <Button
        variant="outlined"
        size="small"
        onClick={clearStorage}
        sx={{ color: 'white', borderColor: 'white' }}
      >
        Clear Storage & Reload
      </Button>
    </Paper>
  );
};

export default DebugPanel; 