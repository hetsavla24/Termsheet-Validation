import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  Chip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Folder as FolderIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import useAuthStore from '../store/authStore';

const Navbar = () => {
  const { user, logout } = useAuthStore();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logout();
  };

  return (
    <AppBar position="static" sx={{ backgroundColor: 'white', color: 'text.primary', boxShadow: 3 }}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
            <Typography
              variant="h6"
              component={Link}
              to="/"
              sx={{
                mr: 4,
                fontWeight: 'bold',
                color: 'primary.main',
                textDecoration: 'none',
                fontSize: '1.5rem'
              }}
            >
              Termsheet Validator
            </Typography>
            
            <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 2 }}>
              <Button
                component={Link}
                to="/dashboard"
                startIcon={<DashboardIcon />}
                variant={isActive('/dashboard') ? 'contained' : 'text'}
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 'medium'
                }}
              >
                Dashboard
              </Button>
              
              <Button
                component={Link}
                to="/files"
                startIcon={<FolderIcon />}
                variant={isActive('/files') ? 'contained' : 'text'}
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 'medium'
                }}
              >
                Files
              </Button>
              
              <Button
                component={Link}
                to="/validation"
                startIcon={<SearchIcon />}
                variant={isActive('/validation') ? 'contained' : 'text'}
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 'medium',
                  position: 'relative'
                }}
              >
                Validation
                <Chip
                  label="Phase 3"
                  size="small"
                  color="secondary"
                  sx={{
                    ml: 1,
                    height: 20,
                    fontSize: '0.65rem'
                  }}
                />
              </Button>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Welcome, {user?.username || user?.full_name || 'User'}
            </Typography>
            <Button
              onClick={handleLogout}
              variant="outlined"
              color="error"
              sx={{
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 'medium'
              }}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar; 