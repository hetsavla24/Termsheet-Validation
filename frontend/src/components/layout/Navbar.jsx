import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  AccountCircle,
  Logout,
  Settings,
  Dashboard as DashboardIcon,
  Folder as FolderIcon,
  Assessment as ValidationIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import useAuthStore from '../../store/authStore';
import { authAPI } from '../../services/api';

const Navbar = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      logout();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      // Even if API call fails, logout locally
      logout();
      navigate('/login');
    }
    handleMenuClose();
  };

  const handleProfile = () => {
    // Will be implemented in later phases
    handleMenuClose();
    toast.info('Profile settings coming soon!');
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <AppBar 
      position="sticky" 
      sx={{ 
        backgroundColor: 'primary.main',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <Toolbar>
        <Box display="flex" alignItems="center" sx={{ flexGrow: 1 }}>
          <DashboardIcon sx={{ mr: 2 }} />
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              fontWeight: 600,
              cursor: 'pointer'
            }}
            onClick={() => navigate('/dashboard')}
          >
            Termsheet Validator
          </Typography>
          <Chip 
            label="v2.0" 
            size="small" 
            sx={{ 
              ml: 2, 
              backgroundColor: 'rgba(255,255,255,0.2)',
              color: 'white',
              fontSize: '0.75rem'
            }} 
          />
          
          {/* Navigation Links */}
          <Box sx={{ ml: 4, display: 'flex', gap: 2 }}>
            <Typography 
              variant="body1" 
              sx={{ 
                cursor: 'pointer',
                padding: '8px 16px',
                borderRadius: '20px',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)'
                },
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}
              onClick={() => navigate('/dashboard')}
            >
              <DashboardIcon fontSize="small" />
              Dashboard
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                cursor: 'pointer',
                padding: '8px 16px',
                borderRadius: '20px',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)'
                },
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}
              onClick={() => navigate('/files')}
            >
              <FolderIcon fontSize="small" />
              Files
            </Typography>
            <Typography 
              variant="body1" 
              sx={{ 
                cursor: 'pointer',
                padding: '8px 16px',
                borderRadius: '20px',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.1)'
                },
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}
              onClick={() => navigate('/validation')}
            >
              <ValidationIcon fontSize="small" />
              Validation
            </Typography>
          </Box>
        </Box>

        <Box display="flex" alignItems="center">
          <Box mr={2} textAlign="right">
            <Typography variant="body2" sx={{ lineHeight: 1.2 }}>
              {user?.full_name}
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.8 }}>
              @{user?.username}
            </Typography>
          </Box>
          
          <IconButton
            size="large"
            edge="end"
            onClick={handleMenuOpen}
            color="inherit"
          >
            <Avatar 
              sx={{ 
                width: 40, 
                height: 40,
                backgroundColor: 'secondary.main',
                fontSize: '1rem',
                fontWeight: 600
              }}
            >
              {user?.full_name ? getInitials(user.full_name) : 'U'}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            onClick={handleMenuClose}
            PaperProps={{
              elevation: 4,
              sx: {
                overflow: 'visible',
                filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                mt: 1.5,
                minWidth: 200,
                '& .MuiAvatar-root': {
                  width: 32,
                  height: 32,
                  ml: -0.5,
                  mr: 1,
                },
                '&:before': {
                  content: '""',
                  display: 'block',
                  position: 'absolute',
                  top: 0,
                  right: 14,
                  width: 10,
                  height: 10,
                  bgcolor: 'background.paper',
                  transform: 'translateY(-50%) rotate(45deg)',
                  zIndex: 0,
                },
              },
            }}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={handleProfile}>
              <ListItemIcon>
                <AccountCircle fontSize="small" />
              </ListItemIcon>
              Profile Settings
            </MenuItem>
            <MenuItem onClick={() => toast.info('Settings coming soon!')}>
              <ListItemIcon>
                <Settings fontSize="small" />
              </ListItemIcon>
              Preferences
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 