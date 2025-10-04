/**
 * Protected Route Component for AIAlchemy
 * Handles authentication guards and role-based access control
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';

// Loading spinner component
const LoadingScreen = () => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      gap: 2,
    }}
  >
    <CircularProgress size={40} />
    <Typography variant="body1" color="textSecondary">
      Loading...
    </Typography>
  </Box>
);

/**
 * ProtectedRoute Component
 * @param {Object} props - Component props
 * @param {React.Component} props.children - Child components to render
 * @param {Array<string>} props.requiredRoles - Array of roles that can access this route
 * @param {boolean} props.requireAuth - Whether authentication is required (default: true)
 */
const ProtectedRoute = ({ 
  children, 
  requiredRoles = [], 
  requireAuth = true 
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Show loading screen while authentication state is being determined
  if (isLoading) {
    return <LoadingScreen />;
  }

  // If authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    // Redirect to login with the current location as state
    return (
      <Navigate 
        to="/login" 
        state={{ from: location }} 
        replace 
      />
    );
  }

  // If specific roles are required, check user role
  if (requiredRoles.length > 0 && user) {
    const userRole = user.role?.toLowerCase();
    const hasRequiredRole = requiredRoles.some(role => 
      role.toLowerCase() === userRole
    );

    if (!hasRequiredRole) {
      // User doesn't have required role, show unauthorized page or redirect
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            gap: 2,
            p: 3,
            textAlign: 'center',
          }}
        >
          <Typography variant="h4" color="error" gutterBottom>
            Access Denied
          </Typography>
          <Typography variant="body1" color="textSecondary" sx={{ maxWidth: 400 }}>
            You don't have the required permissions to access this page. 
            Please contact your administrator if you believe this is an error.
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Required roles: {requiredRoles.join(', ')}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Your role: {userRole || 'Unknown'}
          </Typography>
        </Box>
      );
    }
  }

  // User is authenticated and has required permissions
  return children;
};

/**
 * Higher-order component for protecting routes
 * @param {React.Component} Component - Component to protect
 * @param {Object} options - Protection options
 * @param {Array<string>} options.requiredRoles - Required roles
 * @param {boolean} options.requireAuth - Whether auth is required
 */
export const withAuth = (Component, options = {}) => {
  return function AuthenticatedComponent(props) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
};

/**
 * Role-based route protection hooks
 */
export const useRequireAuth = () => {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return { 
      isAuthorized: false, 
      redirectTo: '/login',
      state: { from: location } 
    };
  }

  return { isAuthorized: true };
};

export const useRequireRole = (requiredRoles = []) => {
  const { isAuthenticated, user } = useAuth();
  
  if (!isAuthenticated) {
    return { 
      isAuthorized: false, 
      reason: 'not_authenticated',
      redirectTo: '/login' 
    };
  }

  const userRole = user?.role?.toLowerCase();
  const hasRequiredRole = requiredRoles.some(role => 
    role.toLowerCase() === userRole
  );

  if (!hasRequiredRole) {
    return { 
      isAuthorized: false, 
      reason: 'insufficient_permissions',
      userRole,
      requiredRoles 
    };
  }

  return { isAuthorized: true, userRole };
};

export default ProtectedRoute;