/**
 * Kanban Board Component
 * Drag-and-drop interface for managing applications through pipeline stages
 */

import React from 'react';
import {
  Box,
  Grid,
  Typography,
  CircularProgress,
  Skeleton,
} from '@mui/material';

// Components
import StageColumn from './StageColumn';

const KanbanBoard = ({ 
  stages, 
  applicationsByStatus, 
  loading, 
  onStatusChange, 
  onViewApplication 
}) => {
  
  if (loading) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Pipeline Stages
        </Typography>
        <Grid container spacing={3}>
          {[1, 2, 3, 4, 5, 6].map((stage) => (
            <Grid item xs={12} sm={6} md={4} lg={2} key={stage}>
              <Box sx={{ p: 2, backgroundColor: 'white', borderRadius: 2, minHeight: 400 }}>
                <Skeleton variant="text" width="60%" height={32} sx={{ mb: 2 }} />
                <Skeleton variant="rectangular" height={24} sx={{ mb: 1, borderRadius: 1 }} />
                {[1, 2, 3].map((item) => (
                  <Skeleton 
                    key={item}
                    variant="rectangular" 
                    height={120} 
                    sx={{ mb: 2, borderRadius: 2 }} 
                  />
                ))}
              </Box>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
        Pipeline Stages
      </Typography>
      
      <Grid container spacing={3}>
        {stages.map((stage) => {
          const applications = applicationsByStatus[stage.id] || [];
          const isOverCapacity = stage.maxItems && applications.length > stage.maxItems;
          
          return (
            <Grid item xs={12} sm={6} md={4} lg={2} key={stage.id}>
              <StageColumn
                stage={stage}
                applications={applications}
                isOverCapacity={isOverCapacity}
                onStatusChange={onStatusChange}
                onViewApplication={onViewApplication}
              />
            </Grid>
          );
        })}
      </Grid>
      
      {/* Pipeline Summary */}
      <Box sx={{ mt: 4, p: 3, backgroundColor: 'white', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Pipeline Summary
        </Typography>
        <Grid container spacing={3}>
          {stages.map((stage) => {
            const count = applicationsByStatus[stage.id]?.length || 0;
            const capacity = stage.maxItems;
            const utilizationRate = capacity ? (count / capacity * 100).toFixed(1) : null;
            
            return (
              <Grid item xs={6} sm={4} md={2} key={stage.id}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color={stage.color} fontWeight={700}>
                    {count}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    {stage.name}
                  </Typography>
                  {capacity && (
                    <Typography variant="caption" color="text.secondary" display="block">
                      {utilizationRate}% of capacity
                    </Typography>
                  )}
                </Box>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    </Box>
  );
};

export default KanbanBoard;