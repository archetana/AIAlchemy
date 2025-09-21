/**
 * Memo Approval Component
 * Shows memo approval status and workflow actions
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
  Assignment as AssignmentIcon,
  Send as SendIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  Warning as WarningIcon,
  AccessTime as AccessTimeIcon,
} from '@mui/icons-material';

const MemoApproval = ({ memo, onApprove, onScheduleReview }) => {
  
  const getApprovalStatus = () => {
    if (!memo) return 'not_created';
    if (memo.approved) return 'approved';
    if (memo.review_date) return 'scheduled';
    if (memo.is_draft) return 'draft';
    return 'submitted';
  };

  const status = getApprovalStatus();

  const statusConfig = {
    not_created: {
      color: '#6b7280',
      label: 'Not Created',
      description: 'Investment memo has not been created yet',
      icon: <AssignmentIcon />,
    },
    draft: {
      color: '#f59e0b',
      label: 'Draft',
      description: 'Memo is being written and edited',
      icon: <EditIcon />,
    },
    submitted: {
      color: '#3b82f6',
      label: 'Submitted',
      description: 'Memo is ready for review and approval',
      icon: <SendIcon />,
    },
    scheduled: {
      color: '#8b5cf6',
      label: 'Review Scheduled',
      description: 'Partner review has been scheduled',
      icon: <ScheduleIcon />,
    },
    approved: {
      color: '#059669',
      label: 'Approved',
      description: 'Memo has been approved and finalized',
      icon: <CheckCircleIcon />,
    },
  };

  const currentStatus = statusConfig[status];

  const getProgress = () => {
    const progressMap = {
      not_created: 0,
      draft: 25,
      submitted: 50,
      scheduled: 75,
      approved: 100,
    };
    return progressMap[status] || 0;
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Memo Status
        </Typography>

        {/* Status Overview */}
        <Box mb={3}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Approval Progress
            </Typography>
            <Typography variant="body2" fontWeight={600}>
              {getProgress()}%
            </Typography>
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={getProgress()}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: '#f3f4f6',
              '& .MuiLinearProgress-bar': {
                backgroundColor: currentStatus.color,
                borderRadius: 3,
              },
            }}
          />
          
          <Box mt={2}>
            <Chip
              icon={currentStatus.icon}
              label={currentStatus.label}
              sx={{
                backgroundColor: `${currentStatus.color}20`,
                color: currentStatus.color,
                fontWeight: 600,
              }}
            />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {currentStatus.description}
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Status Details */}
        <Box mb={3}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ color: 'text.secondary' }}>
            Details
          </Typography>
          
          <List dense sx={{ py: 0 }}>
            {memo?.created_at && (
              <ListItem sx={{ px: 0, py: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  <AssignmentIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2">
                      Created: {new Date(memo.created_at).toLocaleDateString()}
                    </Typography>
                  }
                />
              </ListItem>
            )}

            {memo?.updated_at && memo.updated_at !== memo.created_at && (
              <ListItem sx={{ px: 0, py: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  <EditIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2">
                      Updated: {new Date(memo.updated_at).toLocaleDateString()}
                    </Typography>
                  }
                />
              </ListItem>
            )}

            {memo?.author_name && (
              <ListItem sx={{ px: 0, py: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  <PersonIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2">
                      Author: {memo.author_name}
                    </Typography>
                  }
                />
              </ListItem>
            )}

            {memo?.review_date && (
              <ListItem sx={{ px: 0, py: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  <ScheduleIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2">
                      Review: {new Date(memo.review_date).toLocaleDateString()}
                    </Typography>
                  }
                />
              </ListItem>
            )}

            {memo?.approved_at && (
              <ListItem sx={{ px: 0, py: 0.5 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  <CheckCircleIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2">
                      Approved: {new Date(memo.approved_at).toLocaleDateString()}
                    </Typography>
                  }
                />
              </ListItem>
            )}
          </List>
        </Box>

        {/* Actions */}
        {memo && (
          <>
            <Divider sx={{ my: 2 }} />
            <Box>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ color: 'text.secondary' }}>
                Actions
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={1}>
                {/* Approval Action */}
                {!memo.approved && status !== 'draft' && (
                  <Button
                    variant="contained"
                    startIcon={<CheckCircleIcon />}
                    onClick={onApprove}
                    color="success"
                    size="small"
                    fullWidth
                  >
                    Approve Memo
                  </Button>
                )}

                {/* Schedule Review Action */}
                {!memo.review_date && (
                  <Button
                    variant="outlined"
                    startIcon={<ScheduleIcon />}
                    onClick={onScheduleReview}
                    size="small"
                    fullWidth
                  >
                    Schedule Review
                  </Button>
                )}

                {/* View History (placeholder) */}
                <Button
                  variant="text"
                  startIcon={<VisibilityIcon />}
                  onClick={() => console.log('View memo history')}
                  size="small"
                  fullWidth
                >
                  View History
                </Button>
              </Box>
            </Box>
          </>
        )}

        {/* Warnings/Notes */}
        {status === 'draft' && (
          <Alert severity="info" sx={{ mt: 2 }} icon={<EditIcon />}>
            <Typography variant="body2">
              Save your changes and submit the memo for review when ready.
            </Typography>
          </Alert>
        )}

        {status === 'scheduled' && memo?.review_date && (
          <Alert 
            severity="warning" 
            sx={{ mt: 2 }} 
            icon={<AccessTimeIcon />}
          >
            <Typography variant="body2">
              Partner review is scheduled for {new Date(memo.review_date).toLocaleDateString()}.
            </Typography>
          </Alert>
        )}

        {status === 'approved' && (
          <Alert severity="success" sx={{ mt: 2 }} icon={<CheckCircleIcon />}>
            <Typography variant="body2">
              This memo has been approved and is ready for investment decision.
            </Typography>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default MemoApproval;