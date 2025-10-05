/**
 * Simple About Dialog Component
 * Shows app information without complex version dependencies
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
} from '@mui/material';
import {
  Close as CloseIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

const SimpleAboutDialog = ({ open, onClose }) => {
  const appInfo = {
    name: 'AIAlchemy',
    version: '1.0.3',
    description: 'AI-powered startup evaluation platform with automated due diligence, AI interviews, and investment memo generation',
    credits: [
      'Built with ❤️ by the AIAlchemy Team',
      'Powered by Google Cloud AI Services',
      'Document processing by Google Document AI',
      'Investment analysis by Google Gemini Pro'
    ]
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
        }
      }}
    >
      {/* Header */}
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #2563eb 0%, #8b5cf6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography 
                variant="h5" 
                sx={{ 
                  color: 'white',
                  fontWeight: 700,
                }}
              >
                AI
              </Typography>
            </Box>
            <Box>
              <Typography variant="h5" fontWeight={700}>
                About {appInfo.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Version {appInfo.version}
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {/* App Description */}
        <Box mb={3}>
          <Typography variant="body1" paragraph>
            {appInfo.description}
          </Typography>
        </Box>

        {/* Credits */}
        <Box mb={3}>
          <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
            <InfoIcon color="primary" />
            Credits & Acknowledgments
          </Typography>
          
          {appInfo.credits.map((credit, index) => (
            <Typography key={index} variant="body2" paragraph>
              • {credit}
            </Typography>
          ))}
        </Box>

        {/* Additional Info */}
        <Box>
          <Typography variant="body2" color="text.secondary">
            Repository: https://github.com/archetana/AIAlchemy
          </Typography>
          <Typography variant="body2" color="text.secondary">
            License: MIT License
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary" sx={{ flex: 1 }}>
          © 2025 AIAlchemy Team. All rights reserved.
        </Typography>
        <Button onClick={onClose} variant="contained">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SimpleAboutDialog;