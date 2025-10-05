/**
 * Robust About Dialog Component
 * Handles version dependencies gracefully with fallbacks
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
  Chip,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Grid,
  Card,
  CardContent,
  IconButton,
  Link,
} from '@mui/material';
import {
  Close as CloseIcon,
  Code as CodeIcon,
  Cloud as CloudIcon,
  Psychology as PsychologyIcon,
  GitHub as GitHubIcon,
  Info as InfoIcon,
  Schedule as ScheduleIcon,
  Build as BuildIcon,
  People as PeopleIcon,
  Copyright as CopyrightIcon,
} from '@mui/icons-material';

// Safe version import with fallbacks
const getVersionInfo = () => {
  try {
    // Try to import version config
    const { APP_INFO, DEPLOYMENT_INFO } = require('../../config/version');
    return { APP_INFO, DEPLOYMENT_INFO };
  } catch (error) {
    console.warn('Version config not available, using fallback:', error);
    // Fallback version info
    return {
      APP_INFO: {
        name: 'AIAlchemy',
        fullName: 'AIAlchemy - AI Analyst for Startup Evaluation',
        version: '1.0.3',
        description: 'AI-powered startup evaluation platform with automated due diligence, AI interviews, and investment memo generation',
        team: 'AIAlchemy Team',
        credits: [
          'Built with ❤️ by the AIAlchemy Team',
          'Powered by Google Cloud AI Services',
          'Document processing by Google Document AI',
          'Investment analysis by Google Gemini Pro'
        ],
        buildDate: new Date().toISOString(),
        repository: 'https://github.com/archetana/AIAlchemy',
        license: 'MIT License',
        technologies: [
          'React 18+ with Material-UI',
          'FastAPI with Python 3.11+',
          'Google Cloud Vertex AI',
          'Document AI & Gemini Pro',
          'SQLite with SQLAlchemy',
          'Real-time processing pipeline'
        ]
      },
      DEPLOYMENT_INFO: {
        environment: 'development',
        buildNumber: 'local',
        commitHash: 'local-dev',
        buildDate: new Date().toISOString(),
        deploymentDate: new Date().toISOString()
      }
    };
  }
};

const RobustAboutDialog = ({ open, onClose }) => {
  const { APP_INFO, DEPLOYMENT_INFO } = getVersionInfo();

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch (error) {
      return dateString || 'N/A';
    }
  };

  const copyVersionInfo = () => {
    const versionInfo = `
AIAlchemy Version: ${APP_INFO.version}
Build: ${DEPLOYMENT_INFO.buildNumber || 'N/A'}
Environment: ${DEPLOYMENT_INFO.environment}
Build Date: ${formatDate(DEPLOYMENT_INFO.buildDate)}
Commit: ${DEPLOYMENT_INFO.commitHash || 'N/A'}
    `.trim();
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(versionInfo).then(() => {
        console.log('Version info copied to clipboard');
      }).catch((error) => {
        console.warn('Failed to copy to clipboard:', error);
      });
    } else {
      console.warn('Clipboard API not available');
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          maxHeight: '90vh'
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
                About AIAlchemy
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI-powered startup evaluation platform
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {/* Version Information */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="h6" display="flex" alignItems="center" gap={1}>
                <InfoIcon color="primary" />
                Version Information
              </Typography>
              <Button 
                size="small" 
                variant="outlined" 
                onClick={copyVersionInfo}
                startIcon={<CodeIcon />}
              >
                Copy Info
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Version</Typography>
                <Typography variant="h6" fontWeight={600}>
                  {APP_INFO.version}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Environment</Typography>
                <Chip 
                  label={DEPLOYMENT_INFO.environment.toUpperCase()} 
                  size="small" 
                  color={DEPLOYMENT_INFO.environment === 'production' ? 'success' : 'warning'}
                  sx={{ mt: 0.5 }}
                />
              </Grid>
              {DEPLOYMENT_INFO.buildNumber && DEPLOYMENT_INFO.buildNumber !== 'local' && (
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Build Number</Typography>
                  <Typography variant="body1" fontFamily="monospace">
                    #{DEPLOYMENT_INFO.buildNumber}
                  </Typography>
                </Grid>
              )}
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">Build Date</Typography>
                <Typography variant="body2">
                  {formatDate(DEPLOYMENT_INFO.buildDate)}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* App Description */}
        <Box mb={3}>
          <Typography variant="body1" paragraph>
            {APP_INFO.description}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" paragraph>
            AIAlchemy transforms startup evaluation with advanced AI agents that process pitch decks, 
            conduct due diligence, and generate comprehensive investment memos in minutes, not hours.
          </Typography>
        </Box>

        {/* Credits */}
        <Box mb={3}>
          <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
            <PeopleIcon color="primary" />
            Credits & Acknowledgments
          </Typography>
          
          <List dense>
            {APP_INFO.credits.map((credit, index) => (
              <ListItem key={index} sx={{ py: 0.5 }}>
                <ListItemIcon>
                  <Box 
                    sx={{ 
                      width: 6, 
                      height: 6, 
                      borderRadius: '50%', 
                      backgroundColor: 'primary.main' 
                    }} 
                  />
                </ListItemIcon>
                <ListItemText primary={credit} />
              </ListItem>
            ))}
          </List>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Technologies */}
        <Box mb={3}>
          <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
            <BuildIcon color="primary" />
            Built With
          </Typography>
          
          <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
            {APP_INFO.technologies.map((tech, index) => (
              <Chip 
                key={index}
                label={tech}
                size="small"
                variant="outlined"
                sx={{ mb: 1 }}
              />
            ))}
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Additional Information */}
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Repository
            </Typography>
            <Link 
              href={APP_INFO.repository} 
              target="_blank" 
              rel="noopener noreferrer"
              display="flex"
              alignItems="center"
              gap={0.5}
              sx={{ textDecoration: 'none' }}
            >
              <GitHubIcon fontSize="small" />
              View on GitHub
            </Link>
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              License
            </Typography>
            <Typography variant="body2" display="flex" alignItems="center" gap={0.5}>
              <CopyrightIcon fontSize="small" />
              {APP_INFO.license}
            </Typography>
          </Grid>
        </Grid>
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

export default RobustAboutDialog;