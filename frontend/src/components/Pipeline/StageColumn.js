/**
 * Pipeline Stage Column Component
 * Individual column in the Kanban board representing one pipeline stage
 */

import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Badge,
  Alert,
} from '@mui/material';
import {
  Warning as WarningIcon,
} from '@mui/icons-material';

// Components
import ApplicationCard from './ApplicationCard';

const StageColumn = ({ 
  stage, 
  applications, 
  isOverCapacity, 
  onStatusChange, 
  onViewApplication 
}) => {
  
  const handleDrop = (e) => {
    e.preventDefault();
    const applicationId = e.dataTransfer.getData('application/json');
    if (applicationId) {
      const parsedData = JSON.parse(applicationId);
      if (parsedData.id && parsedData.currentStatus !== stage.id) {
        onStatusChange(parsedData.id, stage.id);
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <Box
      sx={{
        backgroundColor: 'white',
        borderRadius: 2,
        p: 2,
        minHeight: 500,
        border: isOverCapacity ? '2px solid #f59e0b' : '1px solid #e5e7eb',
        position: 'relative',
      }}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      {/* Stage Header */}
      <Box sx={{ mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography 
            variant="h6" 
            fontWeight={600}
            sx={{ color: stage.color }}
          >
            {stage.name}
          </Typography>
          <Badge
            badgeContent={applications.length}
            color={isOverCapacity ? 'error' : 'primary'}
            sx={{
              '& .MuiBadge-badge': {
                backgroundColor: stage.color,
                color: 'white',
              }
            }}
          />
        </Box>
        
        {/* Stage Info */}
        <Box display="flex" gap={1} flexWrap="wrap">
          <Chip
            size="small"
            label={`${applications.length} apps`}
            sx={{ 
              backgroundColor: `${stage.color}20`,
              color: stage.color,
              fontSize: '0.75rem'
            }}
          />
          {stage.maxItems && (
            <Chip
              size="small"
              label={`Max: ${stage.maxItems}`}
              variant="outlined"
              sx={{ fontSize: '0.75rem' }}
            />
          )}
        </Box>
        
        {/* Capacity Warning */}
        {isOverCapacity && (
          <Alert 
            severity="warning" 
            size="small" 
            sx={{ mt: 1, '& .MuiAlert-message': { fontSize: '0.75rem' } }}
            icon={<WarningIcon fontSize="small" />}
          >
            Over capacity ({applications.length}/{stage.maxItems})
          </Alert>
        )}
      </Box>

      {/* Applications */}
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 2,
        maxHeight: 400,
        overflowY: 'auto',
        '&::-webkit-scrollbar': {
          width: 4,
        },
        '&::-webkit-scrollbar-track': {
          background: '#f1f1f1',
          borderRadius: 2,
        },
        '&::-webkit-scrollbar-thumb': {
          background: '#c1c1c1',
          borderRadius: 2,
        },
      }}>
        {applications.length === 0 ? (
          <Box 
            sx={{ 
              textAlign: 'center', 
              py: 4, 
              color: 'text.secondary',
              border: '2px dashed #e5e7eb',
              borderRadius: 2,
              backgroundColor: '#fafafa'
            }}
          >
            <Typography variant="body2">
              No applications in this stage
            </Typography>
            <Typography variant="caption">
              Drop applications here
            </Typography>
          </Box>
        ) : (
          applications.map((application) => (
            <ApplicationCard
              key={application.id}
              application={application}
              stageColor={stage.color}
              onViewApplication={onViewApplication}
            />
          ))
        )}
      </Box>
      
      {/* Stage Indicator Bar */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          backgroundColor: stage.color,
          borderRadius: '8px 8px 0 0',
        }}
      />
    </Box>
  );
};

export default StageColumn;