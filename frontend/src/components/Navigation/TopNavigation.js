/**
 * Top Navigation Component
 * Main navigation bar with tabs for different screens
 */

import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Tabs,
  Tab,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountTree as PipelineIcon,
  CloudUpload as UploadIcon,
  Assignment as MemoIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountCircleIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

const TopNavigation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const menuOpen = Boolean(anchorEl);

  // Navigation tabs configuration
  const navigationTabs = [
    {
      label: 'Dashboard',
      value: '/',
      icon: <DashboardIcon fontSize="small" />,
      path: '/'
    },
    {
      label: 'Pipeline',
      value: '/pipeline',
      icon: <PipelineIcon fontSize="small" />,
      path: '/pipeline'
    },
    {
      label: 'Upload',
      value: '/upload', 
      icon: <UploadIcon fontSize="small" />,
      path: '/upload',
      disabled: false // Now implemented
    },
    {
      label: 'Memos',
      value: '/memos',
      icon: <MemoIcon fontSize="small" />,
      path: '/memos',
      disabled: true // Will enable when implemented
    },
    {
      label: 'Settings',
      value: '/settings',
      icon: <SettingsIcon fontSize="small" />,
      path: '/settings',
      disabled: false // Now implemented
    },
  ];

  // Get current tab value based on pathname
  const getCurrentTab = () => {
    const currentPath = location.pathname;
    const matchingTab = navigationTabs.find(tab => tab.path === currentPath);
    return matchingTab ? matchingTab.value : '/';
  };

  const handleTabChange = (event, newValue) => {
    const tab = navigationTabs.find(t => t.value === newValue);
    if (tab && !tab.disabled) {
      navigate(newValue);
    }
  };

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <AppBar 
      position="sticky" 
      elevation={1}
      sx={{ 
        backgroundColor: 'white',
        color: 'text.primary',
        borderBottom: '1px solid #e5e7eb'
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', minHeight: '64px !important' }}>
        {/* Left Side - Logo and Navigation */}
        <Box display="flex" alignItems="center" flex={1}>
          {/* Logo */}
          <Box display="flex" alignItems="center" mr={4}>
            <Box
              sx={{
                width: 32,
                height: 32,
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mr: 2,
              }}
            >
              <Typography 
                variant="h6" 
                sx={{ 
                  color: 'white',
                  fontWeight: 700,
                  fontSize: '1rem'
                }}
              >
                AI
              </Typography>
            </Box>
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 700,
                background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              AIAlchemy
            </Typography>
          </Box>

          {/* Navigation Tabs */}
          <Tabs
            value={getCurrentTab()}
            onChange={handleTabChange}
            sx={{
              minHeight: 'auto',
              '& .MuiTab-root': {
                minHeight: 'auto',
                py: 1,
                px: 2,
                textTransform: 'none',
                fontWeight: 500,
                fontSize: '0.875rem',
                color: 'text.secondary',
                '&.Mui-selected': {
                  color: 'primary.main',
                  fontWeight: 600,
                },
                '&.Mui-disabled': {
                  color: 'text.disabled',
                },
              },
              '& .MuiTabs-indicator': {
                backgroundColor: 'primary.main',
                height: 2,
              },
            }}
          >
            {navigationTabs.map((tab) => (
              <Tab
                key={tab.value}
                label={
                  <Box display="flex" alignItems="center" gap={0.5}>
                    {tab.icon}
                    {tab.label}
                    {tab.disabled && (
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          ml: 0.5, 
                          color: 'text.disabled',
                          fontSize: '0.7rem'
                        }}
                      >
                        (Soon)
                      </Typography>
                    )}
                  </Box>
                }
                value={tab.value}
                disabled={tab.disabled}
              />
            ))}
          </Tabs>
        </Box>

        {/* Right Side - Actions and User Menu */}
        <Box display="flex" alignItems="center" gap={1}>
          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton size="small" sx={{ color: 'text.secondary' }}>
              <Badge badgeContent={3} color="error" variant="dot">
                <NotificationsIcon fontSize="small" />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User Menu */}
          <Tooltip title="Account">
            <IconButton 
              onClick={handleMenuClick}
              size="small"
              sx={{ ml: 1 }}
            >
              <Avatar 
                sx={{ 
                  width: 32, 
                  height: 32,
                  backgroundColor: 'primary.main',
                  fontSize: '0.875rem'
                }}
              >
                JD
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>

        {/* User Account Menu */}
        <Menu
          anchorEl={anchorEl}
          open={menuOpen}
          onClose={handleMenuClose}
          PaperProps={{
            elevation: 3,
            sx: {
              minWidth: 200,
              mt: 1,
            },
          }}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
          {/* User Info */}
          <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid #e5e7eb' }}>
            <Typography variant="body2" fontWeight={600}>
              John Doe
            </Typography>
            <Typography variant="caption" color="text.secondary">
              john.doe@aialchemy.com
            </Typography>
          </Box>

          <MenuItem onClick={handleMenuClose}>
            <ListItemIcon>
              <PersonIcon fontSize="small" />
            </ListItemIcon>
            Profile Settings
          </MenuItem>
          
          <MenuItem 
            onClick={() => {
              handleMenuClose();
              navigate('/settings');
            }}
          >
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            Account Settings
          </MenuItem>
          
          <MenuItem onClick={handleMenuClose}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            Sign Out
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default TopNavigation;