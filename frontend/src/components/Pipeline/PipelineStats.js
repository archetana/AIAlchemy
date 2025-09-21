/**
 * Pipeline Statistics Component
 * Shows key metrics and bottlenecks for the deal pipeline
 */

import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  CircularProgress,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';

const PipelineStats = ({ pipelineData, loading }) => {
  if (loading || !pipelineData) {
    return (
      <Card elevation={2}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Pipeline Analytics
          </Typography>
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  const {
    stages = {},
    conversion_rates = {},
    avg_days_per_stage = {},
    bottlenecks = [],
    weekly_throughput = 0
  } = pipelineData;

  const totalApplications = Object.values(stages).reduce((sum, count) => sum + count, 0);
  const completionRate = totalApplications > 0 ? ((stages.completed || 0) / totalApplications * 100) : 0;
  
  const conversionMetrics = [
    {
      stage: 'data_processing',
      name: 'To Data Processing',
      rate: conversion_rates.data_processing || 0,
      avgDays: avg_days_per_stage.data_processing || 0,
    },
    {
      stage: 'ai_analysis',
      name: 'To AI Analysis', 
      rate: conversion_rates.ai_analysis || 0,
      avgDays: avg_days_per_stage.ai_analysis || 0,
    },
    {
      stage: 'manual_review',
      name: 'To Manual Review',
      rate: conversion_rates.manual_review || 0,
      avgDays: avg_days_per_stage.manual_review || 0,
    },
    {
      stage: 'partner_review',
      name: 'To Partner Review',
      rate: conversion_rates.partner_review || 0,
      avgDays: avg_days_per_stage.partner_review || 0,
    },
  ];

  const getBottleneckSeverityColor = (severity) => {
    const colors = {
      low: '#10b981',
      medium: '#f59e0b', 
      high: '#ef4444',
      critical: '#dc2626',
    };
    return colors[severity] || '#6b7280';
  };

  const getConversionIcon = (rate) => {
    if (rate >= 80) return <TrendingUpIcon color="success" fontSize="small" />;
    if (rate >= 60) return <SpeedIcon color="warning" fontSize="small" />;
    return <TrendingDownIcon color="error" fontSize="small" />;
  };

  return (
    <Card elevation={2}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
          Pipeline Analytics
        </Typography>

        <Grid container spacing={3}>
          {/* Key Metrics */}
          <Grid item xs={12} md={8}>
            <Grid container spacing={2}>
              {/* Total Applications */}
              <Grid item xs={6} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: '#f8fafc', borderRadius: 2 }}>
                  <Typography variant="h4" color="primary" fontWeight={700}>
                    {totalApplications}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Total Applications
                  </Typography>
                </Box>
              </Grid>

              {/* Completion Rate */}
              <Grid item xs={6} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: '#f0fdf4', borderRadius: 2 }}>
                  <Typography variant="h4" color="success.main" fontWeight={700}>
                    {completionRate.toFixed(1)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Completion Rate
                  </Typography>
                </Box>
              </Grid>

              {/* Weekly Throughput */}
              <Grid item xs={6} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: '#fef2f2', borderRadius: 2 }}>
                  <Typography variant="h4" color="error.main" fontWeight={700}>
                    {weekly_throughput}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Weekly Throughput
                  </Typography>
                </Box>
              </Grid>

              {/* Active Pipeline */}
              <Grid item xs={6} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: '#f3e8ff', borderRadius: 2 }}>
                  <Typography variant="h4" color="secondary.main" fontWeight={700}>
                    {totalApplications - (stages.completed || 0) - (stages.rejected || 0)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Active Pipeline
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            {/* Conversion Rates */}
            <Box mt={3}>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Conversion Rates by Stage
              </Typography>
              <Grid container spacing={2}>
                {conversionMetrics.map((metric) => (
                  <Grid item xs={12} sm={6} key={metric.stage}>
                    <Box p={2} sx={{ border: '1px solid #e5e7eb', borderRadius: 2 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="body2" fontWeight={500}>
                          {metric.name}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={0.5}>
                          {getConversionIcon(metric.rate)}
                          <Typography variant="body2" fontWeight={600}>
                            {metric.rate.toFixed(1)}%
                          </Typography>
                        </Box>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={metric.rate}
                        sx={{
                          height: 4,
                          borderRadius: 2,
                          mb: 1,
                          backgroundColor: '#f3f4f6',
                        }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        Avg: {metric.avgDays.toFixed(1)} days
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </Grid>

          {/* Bottlenecks */}
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Pipeline Bottlenecks
            </Typography>
            
            {bottlenecks.length === 0 ? (
              <Alert severity="success" icon={<CheckCircleIcon />}>
                <Typography variant="body2">
                  No bottlenecks detected
                </Typography>
                <Typography variant="caption">
                  Pipeline is flowing smoothly
                </Typography>
              </Alert>
            ) : (
              <Box display="flex" flexDirection="column" gap={2}>
                {bottlenecks.map((bottleneck, index) => (
                  <Alert 
                    key={index}
                    severity={bottleneck.severity === 'high' ? 'error' : 'warning'}
                    icon={<WarningIcon />}
                    sx={{
                      '& .MuiAlert-message': {
                        width: '100%'
                      }
                    }}
                  >
                    <Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="body2" fontWeight={600}>
                          {bottleneck.stage.replace('_', ' ').toUpperCase()}
                        </Typography>
                        <Chip
                          label={bottleneck.severity}
                          size="small"
                          sx={{
                            backgroundColor: getBottleneckSeverityColor(bottleneck.severity),
                            color: 'white',
                            fontSize: '0.7rem',
                            height: 20,
                          }}
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {bottleneck.reason}
                      </Typography>
                    </Box>
                  </Alert>
                ))}
              </Box>
            )}

            {/* Quick Actions */}
            <Box mt={3}>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Chip
                  label="Auto-assign applications"
                  onClick={() => console.log('Auto-assign')}
                  variant="outlined"
                  size="small"
                  sx={{ justifyContent: 'flex-start' }}
                />
                <Chip
                  label="Schedule team review"
                  onClick={() => console.log('Schedule review')}
                  variant="outlined"
                  size="small"
                  sx={{ justifyContent: 'flex-start' }}
                />
                <Chip
                  label="Export pipeline report"
                  onClick={() => console.log('Export report')}
                  variant="outlined"
                  size="small"
                  sx={{ justifyContent: 'flex-start' }}
                />
              </Box>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default PipelineStats;