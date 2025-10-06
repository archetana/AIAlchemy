/**
 * Main Dashboard Component
 * Orchestrates all dashboard widgets and manages data fetching
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Box,
  Alert,
  Snackbar,
  Fab,
  Typography,
  Paper,
  Breadcrumbs,
  Link,
  Button,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Home as HomeIcon,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';

// Components
import MetricsCards from './MetricsCards';
import PipelineChart from './PipelineChart';
import RecentApplications from './RecentApplications';

// Services
import { dashboardApi, pipelineApi, apiUtils } from '../../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  
  // State management
  const [dashboardData, setDashboardData] = useState(null);
  const [pipelineData, setPipelineData] = useState(null);
  const [loading, setLoading] = useState({
    dashboard: true,
    pipeline: true,
  });
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch dashboard overview data
  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, dashboard: true }));
      
      const response = await dashboardApi.getStats();
      
      if (response.data.success) {
        setDashboardData(response.data.data);
        setLastUpdated(new Date());
      } else {
        throw new Error('Failed to fetch dashboard data');
      }
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      const errorInfo = apiUtils.handleError(err);
      setError(`Dashboard: ${errorInfo.message}`);
      
      // Set fallback data for development
      setDashboardData({
        total_applications: 8,
        ai_processing: 3,
        completed_analysis: 1,
        average_score: 81.8,
        recent_applications: []
      });
    } finally {
      setLoading(prev => ({ ...prev, dashboard: false }));
    }
  }, []);

  // Fetch pipeline data
  const fetchPipelineData = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, pipeline: true }));
      
      const response = await pipelineApi.getStats();
      
      if (response.data.success) {
        setPipelineData(response.data.data);
      } else {
        throw new Error('Failed to fetch pipeline data');
      }
    } catch (err) {
      console.error('Pipeline fetch error:', err);
      const errorInfo = apiUtils.handleError(err);
      setError(`Pipeline: ${errorInfo.message}`);
      
      // Set fallback data for development
      setPipelineData({
        stages: {
          new: 2,
          data_processing: 2,
          ai_analysis: 1,
          manual_review: 1,
          partner_review: 1,
          completed: 1
        },
        conversion_rates: {
          data_processing: 85.7,
          ai_analysis: 73.2,
          manual_review: 68.4,
          partner_review: 85.0
        },
        avg_days_per_stage: {
          data_processing: 0.8,
          ai_analysis: 3.2,
          manual_review: 5.1,
          partner_review: 2.3
        },
        weekly_throughput: 2
      });
    } finally {
      setLoading(prev => ({ ...prev, pipeline: false }));
    }
  }, []);

  // Fetch all dashboard data
  const fetchAllData = useCallback(async () => {
    await Promise.all([
      fetchDashboardData(),
      fetchPipelineData()
    ]);
  }, [fetchDashboardData, fetchPipelineData]);

  // Initial data load
  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchAllData();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [fetchAllData]);

  // Handle manual refresh
  const handleRefresh = () => {
    fetchAllData();
  };

  // Handle view application
  const handleViewApplication = (applicationId) => {
    navigate(`/memo/${applicationId}`);
  };

  // Handle edit application
  const handleEditApplication = (applicationId) => {
    navigate(`/applications/${applicationId}/edit`);
  };

  // Close error snackbar
  const handleCloseError = () => {
    setError(null);
  };

  // Check if any data is loading
  const isLoading = Object.values(loading).some(Boolean);

  return (
    <Box sx={{ flexGrow: 1, backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box mb={4}>
          {/* Breadcrumbs */}
          <Breadcrumbs sx={{ mb: 2 }}>
            <Link 
              color="inherit" 
              href="#" 
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <HomeIcon fontSize="small" />
              Home
            </Link>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.primary' }}>
              <DashboardIcon fontSize="small" />
              Dashboard
            </Box>
          </Breadcrumbs>
          
          {/* Title */}
          <Box display="flex" justifyContent="between" alignItems="flex-start">
            <Box>
              <Typography variant="h4" fontWeight={700} color="text.primary" gutterBottom>
                AIAlchemy Dashboard
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Real-time insights into your startup evaluation pipeline
              </Typography>
              {lastUpdated && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </Typography>
              )}
            </Box>
          </Box>
        </Box>

        {/* Dashboard Content */}
        <Grid container spacing={4}>
          {/* Key Metrics */}
          <Grid item xs={12}>
            <MetricsCards 
              metrics={dashboardData}
              loading={loading.dashboard}
              onRefresh={handleRefresh}
            />
          </Grid>

          {/* Pipeline Analytics */}
          <Grid item xs={12}>
            <PipelineChart 
              pipelineData={pipelineData}
              loading={loading.pipeline}
            />
          </Grid>

          {/* Recent Applications */}
          <Grid item xs={12}>
            <RecentApplications 
              applications={dashboardData?.recent_applications || []}
              loading={loading.dashboard}
              onViewApplication={handleViewApplication}
              onEditApplication={handleEditApplication}
            />
          </Grid>
        </Grid>

        {/* Floating Action Button for Refresh */}
        <Fab
          color="primary"
          aria-label="refresh"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1000,
          }}
          onClick={handleRefresh}
          disabled={isLoading}
        >
          <RefreshIcon />
        </Fab>

        {/* Error Snackbar */}
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={handleCloseError}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        >
          <Alert 
            onClose={handleCloseError} 
            severity="error" 
            sx={{ width: '100%' }}
          >
            {error}
          </Alert>
        </Snackbar>

        {/* Development Info */}
        {process.env.NODE_ENV === 'development' && (
          <Paper 
            elevation={1} 
            sx={{ 
              position: 'fixed', 
              top: 80, 
              right: 16, 
              p: 2, 
              backgroundColor: '#fff3cd',
              border: '1px solid #ffeaa7',
              maxWidth: 300,
              zIndex: 1100
            }}
          >
            <Typography variant="caption" display="block" gutterBottom>
              <strong>Development Mode</strong>
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Dashboard: {loading.dashboard ? 'Loading...' : 'Loaded'}
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Pipeline: {loading.pipeline ? 'Loading...' : 'Loaded'}
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              API: {process.env.REACT_APP_API_URL || '/api (via gateway)'}
            </Typography>
          </Paper>
        )}
      </Container>
    </Box>
  );
};

export default Dashboard;