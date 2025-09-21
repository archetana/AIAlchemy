/**
 * Application Card Component
 * Individual card for each startup application in the pipeline
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Avatar,
  IconButton,
  LinearProgress,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
} from '@mui/material';
import {
  Business as BusinessIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  TrendingUp as TrendingUpIcon,
  MoreVert as MoreVertIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
  Assignment as AssignmentIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';

const ApplicationCard = ({ application, stageColor, onViewApplication }) => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const menuOpen = Boolean(anchorEl);

  const handleMenuClick = (event) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = (event) => {
    event?.stopPropagation();
    setAnchorEl(null);
  };

  const handleDragStart = (e) => {
    e.dataTransfer.setData('application/json', JSON.stringify({
      id: application.id,
      currentStatus: application.status
    }));
  };

  const handleCardClick = () => {
    onViewApplication(application.id);
  };

  const getInitials = (name) => {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return 'Recent';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 85) return '#059669'; // Green
    if (score >= 70) return '#f59e0b'; // Orange  
    return '#ef4444'; // Red
  };

  const getFundingStageColor = (stage) => {
    const colors = {
      'Pre-Seed': '#6b7280',
      'Seed': '#3b82f6',
      'Series A': '#8b5cf6',
      'Series B': '#10b981',
      'Series C': '#059669',
    };
    return colors[stage] || '#6b7280';
  };

  return (
    <Card
      sx={{
        cursor: 'pointer',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 3,
        },
        border: `1px solid ${stageColor}20`,
      }}
      draggable
      onDragStart={handleDragStart}
      onClick={handleCardClick}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        {/* Header with company name and menu */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box flex={1}>
            <Typography 
              variant="subtitle1" 
              fontWeight={600}
              sx={{ 
                mb: 0.5,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
              }}
            >
              {application.company_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {formatDate(application.created_at)}
            </Typography>
          </Box>
          
          <IconButton 
            size="small" 
            onClick={handleMenuClick}
            sx={{ ml: 1 }}
          >
            <MoreVertIcon fontSize="small" />
          </IconButton>
        </Box>

        {/* Contact Info */}
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Avatar 
            sx={{ 
              width: 32, 
              height: 32, 
              fontSize: '0.75rem',
              backgroundColor: stageColor,
            }}
          >
            {getInitials(application.contact_name)}
          </Avatar>
          <Box flex={1}>
            <Typography variant="caption" display="block" fontWeight={500}>
              {application.contact_name || 'No Contact'}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              {application.industry || 'Unknown Industry'}
            </Typography>
          </Box>
        </Box>

        {/* AI Score */}
        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="caption" color="text.secondary">
              AI Score
            </Typography>
            <Typography 
              variant="caption" 
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

        {/* Tags */}
        <Box display="flex" gap={0.5} flexWrap="wrap">
          {application.funding_stage && (
            <Chip
              size="small"
              label={application.funding_stage}
              sx={{
                fontSize: '0.7rem',
                height: 20,
                backgroundColor: `${getFundingStageColor(application.funding_stage)}20`,
                color: getFundingStageColor(application.funding_stage),
              }}
            />
          )}
          {application.assigned_analyst_id && (
            <Chip
              size="small"
              label={`Analyst ${application.assigned_analyst_id}`}
              variant="outlined"
              sx={{
                fontSize: '0.7rem',
                height: 20,
              }}
            />
          )}
        </Box>
      </CardContent>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={menuOpen}
        onClose={handleMenuClose}
        PaperProps={{
          elevation: 3,
          sx: {
            minWidth: 160,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={(e) => { handleMenuClose(e); onViewApplication(application.id); }}>
          <ListItemIcon>
            <VisibilityIcon fontSize="small" />
          </ListItemIcon>
          View Investment Memo
        </MenuItem>
        <MenuItem onClick={(e) => { handleMenuClose(e); console.log('Edit', application.id); }}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          Edit Application
        </MenuItem>
        <MenuItem onClick={(e) => { handleMenuClose(e); console.log('Assign', application.id); }}>
          <ListItemIcon>
            <AssignmentIcon fontSize="small" />
          </ListItemIcon>
          Assign Analyst
        </MenuItem>
        <MenuItem onClick={(e) => { handleMenuClose(e); console.log('Schedule', application.id); }}>
          <ListItemIcon>
            <ScheduleIcon fontSize="small" />
          </ListItemIcon>
          Schedule Review
        </MenuItem>
      </Menu>
    </Card>
  );
};

export default ApplicationCard;