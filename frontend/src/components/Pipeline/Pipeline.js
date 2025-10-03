/**
 * Deal Pipeline Screen Component
 * Kanban-style view of startup applications through the evaluation pipeline
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Chip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Home as HomeIcon,
  AccountTree as PipelineIcon,
  Add as AddIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';

// Components
import KanbanBoard from './KanbanBoard';
import PipelineStats from './PipelineStats';

// Services
import { pipelineApi, startupsApi, apiUtils } from '../../services/api';

const Pipeline = () => {
  const navigate = useNavigate();
  
  // State management
  const [pipelineData, setPipelineData] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [filterOpen, setFilterOpen] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    industry: '',
    analyst: '',
    aiScoreRange: [0, 100],
  });

  // Pipeline stages configuration
  const stages = [
    { id: 'new', name: 'New Applications', color: '#6b7280', maxItems: null },
    { id: 'data_processing', name: 'Data Processing', color: '#3b82f6', maxItems: 5 },
    { id: 'ai_analysis', name: 'AI Analysis', color: '#8b5cf6', maxItems: 3 },
    { id: 'manual_review', name: 'Manual Review', color: '#f59e0b', maxItems: 4 },
    { id: 'partner_review', name: 'Partner Review', color: '#10b981', maxItems: 2 },
    { id: 'completed', name: 'Completed', color: '#059669', maxItems: null },
  ];

  // Fetch pipeline data
  const fetchPipelineData = useCallback(async () => {
    try {
      setLoading(true);
      
      const [statsResponse, applicationsResponse] = await Promise.all([
        pipelineApi.getStats(),
        startupsApi.getStartups({ page_size: 100 })
      ]);
      
      if (statsResponse.data.success) {
        setPipelineData(statsResponse.data.data);
      }
      
      if (applicationsResponse.data.success) {
        setApplications(applicationsResponse.data.data);
      } else {
        // Use applications from stats if available
        setApplications(statsResponse.data.data?.applications || []);
      }
      
      setLastUpdated(new Date());
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
        bottlenecks: {
          ai_analysis: 3,
          data_processing: 2
        }
      });
      
      // Fallback applications data
      setApplications([
        {
          id: 1,
          company_name: 'TechFlow AI',
          status: 'new',
          ai_score: 83.08,
          industry: 'AI/ML',
          contact_name: 'Sarah Chen',
          contact_email: 'sarah@techflow.ai',
          funding_stage: 'Series A',
          created_at: '2025-01-20T10:30:00Z',
          assigned_analyst_id: 1,
        },
        {
          id: 2,
          company_name: 'GreenPay',
          status: 'data_processing',
          ai_score: 77.05,
          industry: 'FinTech',
          contact_name: 'Michael Rodriguez',
          contact_email: 'mike@greenpay.com',
          funding_stage: 'Seed',
          created_at: '2025-01-19T15:45:00Z',
          assigned_analyst_id: 2,
        },
        {
          id: 3,
          company_name: 'HealthLink Pro',
          status: 'ai_analysis',
          ai_score: 89.59,
          industry: 'HealthTech',
          contact_name: 'Dr. Lisa Wang',
          contact_email: 'lisa@healthlink.pro',
          funding_stage: 'Series B',
          created_at: '2025-01-18T09:20:00Z',
          assigned_analyst_id: 1,
        },
        {
          id: 4,
          company_name: 'EduSmart Labs',
          status: 'manual_review',
          ai_score: 90.41,
          industry: 'EdTech',
          contact_name: 'James Thompson',
          contact_email: 'james@edusmartlabs.com',
          funding_stage: 'Series A',
          created_at: '2025-01-17T14:10:00Z',
          assigned_analyst_id: 3,
        },
        {
          id: 5,
          company_name: 'CloudSync Solutions',
          status: 'partner_review',
          ai_score: 82.89,
          industry: 'Enterprise SaaS',
          contact_name: 'Rachel Kim',
          contact_email: 'rachel@cloudsync.io',
          funding_stage: 'Series A',
          created_at: '2025-01-16T11:30:00Z',
          assigned_analyst_id: 2,
        },
        {
          id: 6,
          company_name: 'Quantum Commerce',
          status: 'completed',
          ai_score: 70.37,
          industry: 'E-commerce',
          contact_name: 'David Park',
          contact_email: 'david@quantumcommerce.com',
          funding_stage: 'Seed',
          created_at: '2025-01-15T16:45:00Z',
          assigned_analyst_id: 1,
        }
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data load
  useEffect(() => {
    fetchPipelineData();
  }, [fetchPipelineData]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchPipelineData();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [fetchPipelineData]);

  // Handle manual refresh
  const handleRefresh = () => {
    fetchPipelineData();
  };

  // Handle application status change (drag and drop or manual update)
  const handleStatusChange = async (applicationId, newStatus, notes = '') => {
    try {
      await pipelineApi.updateStatus(applicationId, newStatus, notes);
      
      // Update local state
      setApplications(prevApps => 
        prevApps.map(app => 
          app.id === applicationId 
            ? { ...app, status: newStatus }
            : app
        )
      );
      
      // Refresh pipeline stats
      fetchPipelineData();
      
    } catch (err) {
      console.error('Status update error:', err);
      setError('Failed to update application status');
    }
  };

  // Handle view application details
  const handleViewApplication = (applicationId) => {
    navigate(`/memo/${applicationId}`);
  };

  // Close error snackbar
  const handleCloseError = () => {
    setError(null);
  };

  // Group applications by status
  const applicationsByStatus = stages.reduce((acc, stage) => {
    acc[stage.id] = applications.filter(app => app.status === stage.id);
    return acc;
  }, {});

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
              <PipelineIcon fontSize="small" />
              Deal Pipeline
            </Box>
          </Breadcrumbs>
          
          {/* Title and Controls */}
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
            <Box>
              <Typography variant="h4" fontWeight={700} color="text.primary" gutterBottom>
                Deal Pipeline
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Manage startup applications through the evaluation process
              </Typography>
              {lastUpdated && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </Typography>
              )}
            </Box>
            
            <Box display="flex" gap={1} alignItems="center">
              <Button
                variant="outlined"
                startIcon={<FilterIcon />}
                onClick={() => setFilterOpen(true)}
                size="small"
              >
                Filter
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => console.log('Add application')}
                size="small"
              >
                Add Application
              </Button>
            </Box>
          </Box>
        </Box>

        {/* Pipeline Stats */}
        <Box mb={4}>
          <PipelineStats 
            pipelineData={pipelineData}
            loading={loading}
          />
        </Box>

        {/* Kanban Board */}
        <KanbanBoard
          stages={stages}
          applicationsByStatus={applicationsByStatus}
          loading={loading}
          onStatusChange={handleStatusChange}
          onViewApplication={handleViewApplication}
        />

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
          disabled={loading}
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

        {/* Filter Dialog */}
        <Dialog 
          open={filterOpen} 
          onClose={() => setFilterOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Filter Applications</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 3 }}>
              <TextField
                select
                label="Status"
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                fullWidth
                size="small"
              >
                <MenuItem value="">All Statuses</MenuItem>
                {stages.map(stage => (
                  <MenuItem key={stage.id} value={stage.id}>
                    {stage.name}
                  </MenuItem>
                ))}
              </TextField>
              
              <TextField
                select
                label="Industry"
                value={filters.industry}
                onChange={(e) => setFilters(prev => ({ ...prev, industry: e.target.value }))}
                fullWidth
                size="small"
              >
                <MenuItem value="">All Industries</MenuItem>
                <MenuItem value="AI/ML">AI/ML</MenuItem>
                <MenuItem value="FinTech">FinTech</MenuItem>
                <MenuItem value="HealthTech">HealthTech</MenuItem>
                <MenuItem value="EdTech">EdTech</MenuItem>
                <MenuItem value="Enterprise SaaS">Enterprise SaaS</MenuItem>
                <MenuItem value="E-commerce">E-commerce</MenuItem>
              </TextField>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFilterOpen(false)}>Cancel</Button>
            <Button onClick={() => setFilterOpen(false)} variant="contained">Apply Filters</Button>
          </DialogActions>
        </Dialog>

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
              <strong>Pipeline Development Mode</strong>
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Pipeline: {loading ? 'Loading...' : 'Loaded'}
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Applications: {applications.length} total
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Stages: {Object.keys(applicationsByStatus).length} configured
            </Typography>
          </Paper>
        )}
      </Container>
    </Box>
  );
};

export default Pipeline;