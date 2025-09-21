/**
 * Dashboard Metrics Cards Component
 * Displays key performance indicators in an attractive card layout
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  Assessment,
  Speed,
  RefreshRounded,
} from '@mui/icons-material';

const MetricsCards = ({ metrics, loading, onRefresh }) => {
  const metricsConfig = [
    {
      id: 'total_applications',
      title: 'Total Applications',
      value: metrics?.total_applications || 0,
      icon: Assessment,
      color: '#2563eb',
      bgColor: '#eff6ff',
      description: 'All startup applications submitted',
    },
    {
      id: 'ai_processing',
      title: 'AI Processing',
      value: metrics?.ai_processing || 0,
      icon: Psychology,
      color: '#7c3aed',
      bgColor: '#f3e8ff',
      description: 'Applications currently being analyzed by AI',
    },
    {
      id: 'completed_analysis',
      title: 'Completed Analysis',
      value: metrics?.completed_analysis || 0,
      icon: TrendingUp,
      color: '#059669',
      bgColor: '#f0fdf4',
      description: 'Applications with completed evaluations',
    },
    {
      id: 'average_score',
      title: 'Average AI Score',
      value: `${metrics?.average_score || 0}%`,
      icon: Speed,
      color: '#dc2626',
      bgColor: '#fef2f2',
      description: 'Average AI evaluation score',
    },
  ];

  const formatValue = (value) => {
    if (typeof value === 'number' && value > 999) {
      return `${(value / 1000).toFixed(1)}k`;
    }
    return value;
  };

  const getCompletionRate = () => {
    if (!metrics?.total_applications || metrics.total_applications === 0) return 0;
    return Math.round((metrics.completed_analysis / metrics.total_applications) * 100);
  };

  if (loading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3, 4].map((item) => (
          <Grid item xs={12} sm={6} md={3} key={item}>
            <Card 
              elevation={2}
              sx={{ 
                height: 140,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <CircularProgress size={40} />
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Box>
      {/* Header with refresh button */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600} color="text.primary">
          Dashboard Overview
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip 
            label={`${getCompletionRate()}% Completion Rate`}
            color="success"
            size="small"
            variant="outlined"
          />
          <Tooltip title="Refresh metrics">
            <IconButton onClick={onRefresh} size="small">
              <RefreshRounded />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Metrics Cards */}
      <Grid container spacing={3}>
        {metricsConfig.map((metric) => {
          const IconComponent = metric.icon;
          return (
            <Grid item xs={12} sm={6} md={3} key={metric.id}>
              <Card 
                elevation={2}
                sx={{ 
                  height: 140,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    elevation: 4,
                    transform: 'translateY(-2px)',
                  }
                }}
              >
                <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box flex={1}>
                      <Typography 
                        variant="body2" 
                        color="text.secondary" 
                        sx={{ mb: 1, fontWeight: 500 }}
                      >
                        {metric.title}
                      </Typography>
                      <Typography 
                        variant="h3" 
                        fontWeight={700}
                        color={metric.color}
                        sx={{ mb: 1 }}
                      >
                        {formatValue(metric.value)}
                      </Typography>
                      <Typography 
                        variant="caption" 
                        color="text.secondary"
                        sx={{ opacity: 0.8 }}
                      >
                        {metric.description}
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        backgroundColor: metric.bgColor,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <IconComponent 
                        sx={{ 
                          fontSize: 28, 
                          color: metric.color 
                        }} 
                      />
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Additional insights */}
      <Box mt={2} display="flex" gap={1} flexWrap="wrap">
        <Chip 
          label={`${metrics?.ai_processing || 0} in pipeline`}
          size="small" 
          variant="outlined"
          color="primary"
        />
        <Chip 
          label={`${Math.round(((metrics?.completed_analysis || 0) / Math.max(metrics?.total_applications || 1, 1)) * 100)}% success rate`}
          size="small"
          variant="outlined" 
          color="success"
        />
        <Chip 
          label="Real-time data"
          size="small"
          variant="outlined"
        />
      </Box>
    </Box>
  );
};

export default MetricsCards;