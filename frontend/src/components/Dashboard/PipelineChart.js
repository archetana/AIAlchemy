/**
 * Pipeline Overview Chart Component
 * Shows application flow through different stages with interactive charts
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  CircularProgress,
  Chip,
  LinearProgress,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  FunnelChart,
  Funnel,
  LabelList,
} from 'recharts';
import {
  ShowChart,
  TrendingUp,
  Warning,
  CheckCircle,
} from '@mui/icons-material';

const PipelineChart = ({ pipelineData, loading }) => {
  // Color scheme for different stages
  const stageColors = {
    new: '#6b7280',
    data_processing: '#3b82f6',
    ai_analysis: '#8b5cf6',
    manual_review: '#f59e0b',
    partner_review: '#10b981',
    completed: '#059669',
    rejected: '#ef4444',
  };

  // Format stage names for display
  const formatStageName = (stage) => {
    return stage.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Prepare data for charts
  const chartData = React.useMemo(() => {
    if (!pipelineData?.stages) return [];
    
    return Object.entries(pipelineData.stages).map(([stage, count]) => ({
      stage: formatStageName(stage),
      stageKey: stage,
      count,
      color: stageColors[stage] || '#6b7280',
    }));
  }, [pipelineData]);

  // Prepare funnel data (conversion flow)
  const funnelData = React.useMemo(() => {
    if (!pipelineData?.stages) return [];
    
    const stages = ['new', 'data_processing', 'ai_analysis', 'manual_review', 'partner_review', 'completed'];
    let cumulative = 0;
    
    return stages.map(stage => {
      const count = pipelineData.stages[stage] || 0;
      cumulative += count;
      return {
        value: cumulative,
        name: formatStageName(stage),
        fill: stageColors[stage],
      };
    }).reverse(); // Reverse for funnel effect
  }, [pipelineData]);

  // Calculate conversion rates
  const conversionRates = React.useMemo(() => {
    if (!pipelineData?.conversion_rates) return {};
    return pipelineData.conversion_rates;
  }, [pipelineData]);

  // Get bottleneck information
  const bottlenecks = React.useMemo(() => {
    if (!pipelineData?.stages) return [];
    
    const sorted = Object.entries(pipelineData.stages)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3);
    
    return sorted.map(([stage, count]) => ({
      stage: formatStageName(stage),
      count,
      severity: count > 5 ? 'high' : count > 2 ? 'medium' : 'low'
    }));
  }, [pipelineData]);

  if (loading) {
    return (
      <Card elevation={2}>
        <CardContent sx={{ p: 3 }}>
          <Box display="flex" alignItems="center" justifyContent="center" height={300}>
            <CircularProgress size={50} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Grid container spacing={3}>
      {/* Main Pipeline Chart */}
      <Grid item xs={12} md={8}>
        <Card elevation={2}>
          <CardContent sx={{ p: 3 }}>
            <Box display="flex" justifyContent="between" alignItems="center" mb={3}>
              <Typography variant="h6" fontWeight={600}>
                Pipeline Flow
              </Typography>
              <Chip 
                icon={<ShowChart />}
                label={`${pipelineData?.weekly_throughput || 0} weekly throughput`}
                size="small"
                variant="outlined"
                color="primary"
              />
            </Box>
            
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="stage" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  formatter={(value, name) => [value, 'Applications']}
                  labelFormatter={(label) => `Stage: ${label}`}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Pipeline Metrics */}
      <Grid item xs={12} md={4}>
        <Grid container spacing={2}>
          {/* Conversion Rates */}
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardContent sx={{ p: 2 }}>
                <Typography variant="h6" fontWeight={600} mb={2}>
                  Conversion Rates
                </Typography>
                <Box space={1}>
                  {Object.entries(conversionRates).map(([stage, rate]) => (
                    <Box key={stage} mb={1.5}>
                      <Box display="flex" justifyContent="between" mb={0.5}>
                        <Typography variant="body2" color="text.secondary">
                          {formatStageName(stage)}
                        </Typography>
                        <Typography variant="body2" fontWeight={500}>
                          {rate?.toFixed(1) || 0}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={Math.min(rate || 0, 100)}
                        sx={{ 
                          height: 6,
                          borderRadius: 3,
                          backgroundColor: '#f0f0f0',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 3,
                            backgroundColor: rate > 80 ? '#059669' : rate > 60 ? '#f59e0b' : '#ef4444'
                          }
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Bottlenecks */}
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardContent sx={{ p: 2 }}>
                <Typography variant="h6" fontWeight={600} mb={2}>
                  Current Bottlenecks
                </Typography>
                <Box>
                  {bottlenecks.map((bottleneck, index) => (
                    <Box 
                      key={index}
                      display="flex" 
                      justifyContent="between" 
                      alignItems="center"
                      mb={1}
                    >
                      <Box display="flex" alignItems="center" gap={1}>
                        {bottleneck.severity === 'high' && <Warning color="error" fontSize="small" />}
                        {bottleneck.severity === 'medium' && <TrendingUp color="warning" fontSize="small" />}
                        {bottleneck.severity === 'low' && <CheckCircle color="success" fontSize="small" />}
                        <Typography variant="body2">
                          {bottleneck.stage}
                        </Typography>
                      </Box>
                      <Chip 
                        label={bottleneck.count}
                        size="small"
                        color={
                          bottleneck.severity === 'high' ? 'error' : 
                          bottleneck.severity === 'medium' ? 'warning' : 'success'
                        }
                        variant="outlined"
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Grid>

      {/* Stage Distribution Pie Chart */}
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Stage Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  dataKey="count"
                  nameKey="stage"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [value, 'Applications']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* Processing Time Analytics */}
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Average Processing Time
            </Typography>
            <Box>
              {pipelineData?.avg_days_per_stage && Object.entries(pipelineData.avg_days_per_stage).map(([stage, days]) => (
                <Box key={stage} mb={2}>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                    <Typography variant="body2" color="text.secondary">
                      {formatStageName(stage)}
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {days?.toFixed(1) || 0} days
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={Math.min((days / 10) * 100, 100)}
                    sx={{
                      height: 4,
                      borderRadius: 2,
                      backgroundColor: '#f0f0f0',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 2,
                        backgroundColor: days > 7 ? '#ef4444' : days > 3 ? '#f59e0b' : '#059669'
                      }
                    }}
                  />
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default PipelineChart;