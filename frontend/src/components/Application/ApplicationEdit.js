/**
 * Application Edit Component
 * Form for editing existing startup applications
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  Home as HomeIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';

// Import the Upload component to reuse its form
import Upload from '../Upload/Upload';

const ApplicationEdit = () => {
  const { applicationId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Simulate loading - in real implementation, fetch application data
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, [applicationId]);

  const handleCancel = () => {
    navigate(-1); // Go back to previous page
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="outlined" onClick={handleCancel}>
          Go Back
        </Button>
      </Container>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box mb={4}>
          {/* Breadcrumbs */}
          <Breadcrumbs sx={{ mb: 2 }}>
            <Link 
              color="inherit" 
              href="#" 
              onClick={() => navigate('/')}
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <HomeIcon fontSize="small" />
              Dashboard
            </Link>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.primary' }}>
              <EditIcon fontSize="small" />
              Edit Application
            </Box>
          </Breadcrumbs>
          
          {/* Title */}
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Box>
              <Typography variant="h4" fontWeight={700} color="text.primary" gutterBottom>
                Edit Application #{applicationId}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Update startup application information and documents
              </Typography>
            </Box>
            
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<CancelIcon />}
                onClick={handleCancel}
              >
                Cancel
              </Button>
            </Box>
          </Box>
        </Box>

        {/* Form Content - Reuse Upload component in edit mode */}
        <Paper elevation={1} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
            Application Information
          </Typography>
          
          {/* Note: In a real implementation, you would pass the existing application data 
              to the Upload component as props to pre-populate the form */}
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Edit Mode:</strong> This form would be pre-populated with existing application data.
              For now, it shows the new application form structure.
            </Typography>
          </Alert>
          
          <Upload editMode={true} applicationId={applicationId} />
        </Paper>
      </Container>
    </Box>
  );
};

export default ApplicationEdit;