/**
 * Recent Applications Table Component
 * Shows the latest startup applications with quick actions
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Avatar,
  Button,
  Skeleton,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import {
  Visibility,
  Edit,
  TrendingUp,
  Business,
  Schedule,
  Launch,
} from '@mui/icons-material';

const RecentApplications = ({ applications, loading, onViewApplication, onEditApplication }) => {
  // Status color mapping
  const statusColors = {
    new: 'default',
    data_processing: 'info',
    ai_analysis: 'secondary', 
    manual_review: 'warning',
    partner_review: 'primary',
    completed: 'success',
    rejected: 'error',
  };

  // Format status for display
  const formatStatus = (status) => {
    return status?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown';
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Format AI score
  const formatScore = (score) => {
    if (!score && score !== 0) return 'N/A';
    return `${Math.round(score)}%`;
  };

  // Get company initial for avatar
  const getCompanyInitial = (companyName) => {
    return companyName?.charAt(0).toUpperCase() || '?';
  };

  // Get score color
  const getScoreColor = (score) => {
    if (!score) return '#6b7280';
    if (score >= 80) return '#059669';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  if (loading) {
    return (
      <Card elevation={2}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" fontWeight={600} mb={3}>
            Recent Applications
          </Typography>
          {[1, 2, 3, 4, 5].map((item) => (
            <Box key={item} display="flex" alignItems="center" mb={2}>
              <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
              <Box flex={1}>
                <Skeleton variant="text" width="60%" height={20} />
                <Skeleton variant="text" width="40%" height={16} />
              </Box>
              <Skeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 1, mr: 1 }} />
              <Skeleton variant="rectangular" width={60} height={24} sx={{ borderRadius: 1 }} />
            </Box>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card elevation={2}>
      <CardContent sx={{ p: 0 }}>
        {/* Header */}
        <Box p={3} pb={0}>
          <Box display="flex" justifyContent="between" alignItems="center">
            <Typography variant="h6" fontWeight={600}>
              Recent Applications
            </Typography>
            <Button
              variant="outlined"
              size="small"
              startIcon={<Launch />}
              onClick={() => console.log('Navigate to full list')}
            >
              View All
            </Button>
          </Box>
        </Box>

        {/* Applications Table */}
        {applications && applications.length > 0 ? (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Company</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>AI Score</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Submitted</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {applications.map((application) => (
                  <TableRow 
                    key={application.id}
                    sx={{ 
                      '&:hover': { backgroundColor: '#f8fafc' },
                      cursor: 'pointer'
                    }}
                    onClick={() => onViewApplication && onViewApplication(application.id)}
                  >
                    {/* Company */}
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        <Avatar 
                          sx={{ 
                            width: 40, 
                            height: 40, 
                            mr: 2,
                            backgroundColor: '#3b82f6',
                            fontSize: 14,
                            fontWeight: 600
                          }}
                        >
                          <Business />
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight={500}>
                            {application.company_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ID: {application.id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>

                    {/* Status */}
                    <TableCell>
                      <Chip 
                        label={formatStatus(application.status)}
                        color={statusColors[application.status] || 'default'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>

                    {/* AI Score */}
                    <TableCell>
                      {application.ai_score ? (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Box
                            sx={{
                              minWidth: 50,
                              height: 6,
                              backgroundColor: '#f0f0f0',
                              borderRadius: 3,
                              position: 'relative'
                            }}
                          >
                            <Box
                              sx={{
                                width: `${Math.min(application.ai_score, 100)}%`,
                                height: '100%',
                                backgroundColor: getScoreColor(application.ai_score),
                                borderRadius: 3,
                              }}
                            />
                          </Box>
                          <Typography 
                            variant="body2" 
                            fontWeight={500}
                            color={getScoreColor(application.ai_score)}
                          >
                            {formatScore(application.ai_score)}
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Pending
                        </Typography>
                      )}
                    </TableCell>

                    {/* Submitted Date */}
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Schedule fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(application.created_at)}
                        </Typography>
                      </Box>
                    </TableCell>

                    {/* Actions */}
                    <TableCell>
                      <Box display="flex" gap={0.5}>
                        <Tooltip title="View Details">
                          <IconButton 
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              onViewApplication && onViewApplication(application.id);
                            }}
                          >
                            <Visibility fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit Application">
                          <IconButton 
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              onEditApplication && onEditApplication(application.id);
                            }}
                          >
                            <Edit fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box p={3} textAlign="center">
            <Business sx={{ fontSize: 48, color: '#d1d5db', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" mb={1}>
              No Recent Applications
            </Typography>
            <Typography variant="body2" color="text.secondary">
              New startup applications will appear here when submitted
            </Typography>
          </Box>
        )}

        {/* Footer with summary */}
        {applications && applications.length > 0 && (
          <Box p={2} borderTop="1px solid #f0f0f0" backgroundColor="#f8fafc">
            <Box display="flex" justifyContent="between" alignItems="center">
              <Typography variant="body2" color="text.secondary">
                Showing {applications.length} most recent applications
              </Typography>
              <Box display="flex" gap={2}>
                <Box display="flex" alignItems="center" gap={0.5}>
                  <Box 
                    sx={{ 
                      width: 8, 
                      height: 8, 
                      borderRadius: '50%', 
                      backgroundColor: '#059669' 
                    }} 
                  />
                  <Typography variant="caption">High Score</Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={0.5}>
                  <Box 
                    sx={{ 
                      width: 8, 
                      height: 8, 
                      borderRadius: '50%', 
                      backgroundColor: '#f59e0b' 
                    }} 
                  />
                  <Typography variant="caption">Medium Score</Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={0.5}>
                  <Box 
                    sx={{ 
                      width: 8, 
                      height: 8, 
                      borderRadius: '50%', 
                      backgroundColor: '#ef4444' 
                    }} 
                  />
                  <Typography variant="caption">Low Score</Typography>
                </Box>
              </Box>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default RecentApplications;