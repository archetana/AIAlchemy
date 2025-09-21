/**
 * Application Details Component
 * Detailed information panel for the startup application
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Avatar,
  Divider,
  LinearProgress,
  Link,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Business as BusinessIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Language as LanguageIcon,
  AttachMoney as AttachMoneyIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  Assessment as AssessmentIcon,
  Launch as LaunchIcon,
} from '@mui/icons-material';

const ApplicationDetails = ({ application }) => {
  const formatCurrency = (amount) => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value) => {
    if (!value && value !== 0) return 'N/A';
    return `${value.toFixed(1)}%`;
  };

  const getScoreColor = (score) => {
    if (!score) return '#6b7280';
    if (score >= 85) return '#059669';
    if (score >= 70) return '#f59e0b';
    return '#ef4444';
  };

  const getFundingStageColor = (stage) => {
    const colors = {
      'Pre-Seed': '#6b7280',
      'Seed': '#3b82f6',
      'Series A': '#8b5cf6',
      'Series B': '#10b981',
      'Series C+': '#059669',
    };
    return colors[stage] || '#6b7280';
  };

  const getInitials = (name) => {
    if (!name) return 'N/A';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Application Details
        </Typography>

        {/* Company Information */}
        <Box mb={3}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ color: 'text.secondary' }}>
            Company Information
          </Typography>
          
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <BusinessIcon fontSize="small" color="action" />
            <Typography variant="body2" fontWeight={500}>
              {application.company_name}
            </Typography>
          </Box>

          {application.website && (
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <LanguageIcon fontSize="small" color="action" />
              <Link 
                href={application.website} 
                target="_blank" 
                rel="noopener noreferrer"
                variant="body2"
                sx={{ textDecoration: 'none' }}
              >
                {application.website}
                <IconButton size="small" sx={{ ml: 0.5, p: 0 }}>
                  <LaunchIcon fontSize="small" />
                </IconButton>
              </Link>
            </Box>
          )}

          <Box display="flex" gap={1} mt={1} flexWrap="wrap">
            <Chip
              size="small"
              label={application.industry}
              sx={{
                backgroundColor: '#f0f9ff',
                color: '#0369a1',
              }}
            />
            {application.funding_stage && (
              <Chip
                size="small"
                label={application.funding_stage}
                sx={{
                  backgroundColor: `${getFundingStageColor(application.funding_stage)}20`,
                  color: getFundingStageColor(application.funding_stage),
                }}
              />
            )}
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Contact Information */}
        <Box mb={3}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ color: 'text.secondary' }}>
            Contact Information
          </Typography>
          
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Avatar 
              sx={{ 
                width: 32, 
                height: 32, 
                fontSize: '0.875rem',
                backgroundColor: 'primary.main'
              }}
            >
              {getInitials(application.contact_name)}
            </Avatar>
            <Box>
              <Typography variant="body2" fontWeight={500}>
                {application.contact_name || 'No contact provided'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Primary Contact
              </Typography>
            </Box>
          </Box>

          {application.contact_email && (
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <EmailIcon fontSize="small" color="action" />
              <Link href={`mailto:${application.contact_email}`} variant="body2">
                {application.contact_email}
              </Link>
            </Box>
          )}

          {application.contact_phone && (
            <Box display="flex" alignItems="center" gap={1}>
              <PhoneIcon fontSize="small" color="action" />
              <Link href={`tel:${application.contact_phone}`} variant="body2">
                {application.contact_phone}
              </Link>
            </Box>
          )}
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Financial Metrics */}
        <Box mb={3}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ color: 'text.secondary' }}>
            Financial Information
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="caption" color="text.secondary">
                  Funding Requested
                </Typography>
                <Typography variant="body2" fontWeight={600}>
                  {formatCurrency(application.funding_amount_requested)}
                </Typography>
              </Box>
            </Grid>

            {application.current_arr && (
              <Grid item xs={12}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption" color="text.secondary">
                    Current ARR
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {formatCurrency(application.current_arr)}
                  </Typography>
                </Box>
              </Grid>
            )}

            {application.gross_margin && (
              <Grid item xs={12}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption" color="text.secondary">
                    Gross Margin
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {formatPercentage(application.gross_margin)}
                  </Typography>
                </Box>
              </Grid>
            )}

            {application.runway_months && (
              <Grid item xs={12}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption" color="text.secondary">
                    Runway
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {application.runway_months} months
                  </Typography>
                </Box>
              </Grid>
            )}
          </Grid>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* AI Analysis */}
        <Box mb={3}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ color: 'text.secondary' }}>
            AI Analysis
          </Typography>

          <Box mb={2}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="caption" color="text.secondary">
                AI Score
              </Typography>
              <Typography 
                variant="body2" 
                fontWeight={600}
                sx={{ color: getScoreColor(application.ai_score) }}
              >
                {application.ai_score ? `${application.ai_score.toFixed(1)}%` : 'N/A'}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={application.ai_score || 0}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: '#f3f4f6',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: getScoreColor(application.ai_score),
                  borderRadius: 3,
                },
              }}
            />
          </Box>

          {application.manual_score && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="caption" color="text.secondary">
                  Manual Score
                </Typography>
                <Typography 
                  variant="body2" 
                  fontWeight={600}
                  sx={{ color: getScoreColor(application.manual_score) }}
                >
                  {application.manual_score.toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={application.manual_score}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: '#f3f4f6',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getScoreColor(application.manual_score),
                    borderRadius: 3,
                  },
                }}
              />
            </Box>
          )}

          {application.processing_notes && (
            <Box mt={2}>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                Analysis Notes
              </Typography>
              <Typography variant="body2" sx={{ 
                fontStyle: 'italic',
                backgroundColor: '#f8fafc',
                p: 1.5,
                borderRadius: 1,
                border: '1px solid #e5e7eb'
              }}>
                {application.processing_notes}
              </Typography>
            </Box>
          )}
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Timeline */}
        <Box>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ color: 'text.secondary' }}>
            Timeline
          </Typography>

          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="caption" color="text.secondary">
              Submitted
            </Typography>
            <Typography variant="body2">
              {new Date(application.created_at).toLocaleDateString()}
            </Typography>
          </Box>

          {application.updated_at && application.updated_at !== application.created_at && (
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="caption" color="text.secondary">
                Last Updated
              </Typography>
              <Typography variant="body2">
                {new Date(application.updated_at).toLocaleDateString()}
              </Typography>
            </Box>
          )}

          {application.assigned_analyst_id && (
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="caption" color="text.secondary">
                Assigned Analyst
              </Typography>
              <Chip
                size="small"
                label={`Analyst ${application.assigned_analyst_id}`}
                variant="outlined"
                sx={{ fontSize: '0.75rem' }}
              />
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ApplicationDetails;