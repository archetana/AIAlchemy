/**
 * Upload Screen Component
 * File upload and new startup application creation interface
 */

import React, { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  Snackbar,
  LinearProgress,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondary,
  Divider,
  Paper,
  Breadcrumbs,
  Link,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Checkbox,
  Tooltip,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
  VideoFile as VideoFileIcon,
  AttachFile as AttachFileIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Upload as UploadIcon,
  Home as HomeIcon,
  Business as BusinessIcon,
  Send as SendIcon,
  Preview as PreviewIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

// Services
import { uploadsApi, startupsApi, apiUtils } from '../../services/api';

const Upload = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  // Stepper state
  const [activeStep, setActiveStep] = useState(0);
  
  // Form data state
  const [formData, setFormData] = useState({
    // Company Information
    company_name: '',
    website: '',
    industry: '',
    funding_stage: '',
    funding_amount_requested: '',
    description: '',
    
    // Contact Information
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    contact_title: '',
    
    // Additional Information
    founded_year: new Date().getFullYear(),
    team_size: '',
    current_arr: '',
    runway_months: '',
    previous_funding: '',
    
    // Processing preferences
    auto_processing: true,
    notify_completion: true,
    priority: 'normal',
  });
  
  // File upload state
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  // Stepper configuration
  const steps = [
    {
      label: 'Company Information',
      description: 'Basic company details and contact information',
    },
    {
      label: 'Upload Documents',
      description: 'Upload pitch deck, financial models, and other materials',
    },
    {
      label: 'Additional Details',
      description: 'Funding history and key metrics',
    },
    {
      label: 'Review & Submit',
      description: 'Review information and submit for evaluation',
    },
  ];

  // Accepted file types
  const acceptedFileTypes = {
    'application/pdf': 'PDF Documents',
    'application/vnd.ms-powerpoint': 'PowerPoint Presentations',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint Presentations',
    'application/vnd.ms-excel': 'Excel Spreadsheets', 
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel Spreadsheets',
    'video/mp4': 'MP4 Videos',
    'video/mov': 'MOV Videos',
    'video/avi': 'AVI Videos',
    'audio/mp3': 'MP3 Audio',
    'audio/wav': 'WAV Audio',
  };

  // Industry options
  const industries = [
    'AI/ML', 'FinTech', 'HealthTech', 'EdTech', 'E-commerce', 'Enterprise SaaS',
    'Consumer Apps', 'IoT', 'Blockchain/Crypto', 'CleanTech', 'Biotech', 
    'Manufacturing', 'Transportation', 'Real Estate', 'Food & Beverage', 'Other'
  ];

  // Funding stage options
  const fundingStages = [
    'Pre-Seed', 'Seed', 'Series A', 'Series B', 'Series C', 'Series D+', 
    'Growth/Late Stage', 'Bridge Funding', 'Convertible Note'
  ];

  // Handle form field updates
  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Handle file selection
  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const validFiles = selectedFiles.filter(file => {
      if (!Object.keys(acceptedFileTypes).includes(file.type)) {
        setError(`File type ${file.type} is not supported`);
        return false;
      }
      if (file.size > 100 * 1024 * 1024) { // 100MB limit
        setError(`File ${file.name} is too large. Maximum size is 100MB.`);
        return false;
      }
      return true;
    });
    
    setFiles(prev => [...prev, ...validFiles.map(file => ({
      file,
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0,
      error: null,
    }))]);
    
    // Clear the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Remove file from list
  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  // Upload files
  const uploadFiles = async () => {
    if (files.length === 0) return true;
    
    setUploading(true);
    let allSuccessful = true;
    
    try {
      for (let i = 0; i < files.length; i++) {
        const fileData = files[i];
        if (fileData.status === 'uploaded') continue;
        
        try {
          const formData = new FormData();
          formData.append('file', fileData.file);
          formData.append('file_type', getFileType(fileData.type));
          
          setFiles(prev => prev.map(f => 
            f.id === fileData.id 
              ? { ...f, status: 'uploading', progress: 0 }
              : f
          ));
          
          const response = await uploadsApi.uploadFile(formData, {
            onUploadProgress: (progressEvent) => {
              const progress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setFiles(prev => prev.map(f => 
                f.id === fileData.id 
                  ? { ...f, progress }
                  : f
              ));
            },
          });
          
          if (response.data) {
            setFiles(prev => prev.map(f => 
              f.id === fileData.id 
                ? { ...f, status: 'uploaded', progress: 100, uploadData: response.data }
                : f
            ));
          }
        } catch (err) {
          console.error('File upload error:', err);
          allSuccessful = false;
          setFiles(prev => prev.map(f => 
            f.id === fileData.id 
              ? { ...f, status: 'error', error: apiUtils.handleError(err).message }
              : f
          ));
        }
      }
    } finally {
      setUploading(false);
    }
    
    return allSuccessful;
  };

  // Get file type category
  const getFileType = (mimeType) => {
    if (mimeType.includes('pdf')) return 'pitch_deck';
    if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return 'pitch_deck';
    if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return 'financial';
    if (mimeType.includes('video')) return 'video_pitch';
    if (mimeType.includes('audio')) return 'audio_pitch';
    return 'other';
  };

  // Get file icon
  const getFileIcon = (type) => {
    if (type.includes('pdf') || type.includes('presentation') || type.includes('powerpoint')) {
      return <DescriptionIcon />;
    }
    if (type.includes('video')) {
      return <VideoFileIcon />;
    }
    return <AttachFileIcon />;
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Handle step navigation
  const handleNext = async () => {
    if (activeStep === 1) {
      // Upload files when moving from step 1 to 2
      const uploadSuccess = await uploadFiles();
      if (!uploadSuccess) {
        setError('Some files failed to upload. Please try again.');
        return;
      }
    }
    
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  // Handle form submission
  const handleSubmit = async () => {
    try {
      setLoading(true);
      
      // Create startup application
      const applicationData = {
        ...formData,
        funding_amount_requested: parseFloat(formData.funding_amount_requested) || 0,
        current_arr: parseFloat(formData.current_arr) || 0,
        runway_months: parseInt(formData.runway_months) || 0,
        team_size: parseInt(formData.team_size) || 0,
        founded_year: parseInt(formData.founded_year),
        file_ids: files
          .filter(f => f.status === 'uploaded')
          .map(f => f.uploadData.id),
      };
      
      const response = await startupsApi.createStartup(applicationData);
      
      if (response.data) {
        setSuccess('Application submitted successfully! Redirecting to pipeline...');
        setTimeout(() => {
          navigate('/pipeline');
        }, 2000);
      }
    } catch (err) {
      console.error('Submit error:', err);
      const errorInfo = apiUtils.handleError(err);
      setError(`Failed to submit application: ${errorInfo.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Validate step
  const isStepValid = (step) => {
    switch (step) {
      case 0:
        return formData.company_name && formData.contact_name && formData.contact_email;
      case 1:
        return files.length > 0;
      case 2:
        return true; // Optional step
      case 3:
        return true; // Review step
      default:
        return false;
    }
  };

  // Close notifications
  const handleCloseError = () => setError(null);
  const handleCloseSuccess = () => setSuccess(null);

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
              Home
            </Link>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.primary' }}>
              <CloudUploadIcon fontSize="small" />
              New Application
            </Box>
          </Breadcrumbs>
          
          {/* Title */}
          <Box>
            <Typography variant="h4" fontWeight={700} color="text.primary" gutterBottom>
              Submit New Application
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Upload startup materials for AI-powered evaluation and analysis
            </Typography>
          </Box>
        </Box>

        {/* Stepper */}
        <Card elevation={1} sx={{ borderRadius: 2, mb: 4 }}>
          <CardContent sx={{ p: 3 }}>
            <Stepper activeStep={activeStep} orientation="horizontal">
              {steps.map((step, index) => (
                <Step key={step.label}>
                  <StepLabel>
                    <Typography variant="subtitle2" fontWeight={500}>
                      {step.label}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {step.description}
                    </Typography>
                  </StepLabel>
                </Step>
              ))}
            </Stepper>
          </CardContent>
        </Card>

        {/* Step Content */}
        <Card elevation={1} sx={{ borderRadius: 2 }}>
          <CardContent sx={{ p: 4 }}>
            {/* Step 0: Company Information */}
            {activeStep === 0 && (
              <Box>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Company Information
                </Typography>
                <Divider sx={{ mb: 3 }} />
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Company Name"
                      value={formData.company_name}
                      onChange={(e) => updateFormData('company_name', e.target.value)}
                      fullWidth
                      required
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Website"
                      value={formData.website}
                      onChange={(e) => updateFormData('website', e.target.value)}
                      placeholder="https://..."
                      fullWidth
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      select
                      label="Industry"
                      value={formData.industry}
                      onChange={(e) => updateFormData('industry', e.target.value)}
                      fullWidth
                      required
                    >
                      {industries.map(industry => (
                        <MenuItem key={industry} value={industry}>
                          {industry}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      select
                      label="Funding Stage"
                      value={formData.funding_stage}
                      onChange={(e) => updateFormData('funding_stage', e.target.value)}
                      fullWidth
                      required
                    >
                      {fundingStages.map(stage => (
                        <MenuItem key={stage} value={stage}>
                          {stage}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Funding Amount Requested"
                      type="number"
                      value={formData.funding_amount_requested}
                      onChange={(e) => updateFormData('funding_amount_requested', e.target.value)}
                      InputProps={{ startAdornment: '$' }}
                      placeholder="5000000"
                      fullWidth
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Founded Year"
                      type="number"
                      value={formData.founded_year}
                      onChange={(e) => updateFormData('founded_year', e.target.value)}
                      inputProps={{ min: 1900, max: new Date().getFullYear() }}
                      fullWidth
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      label="Company Description"
                      value={formData.description}
                      onChange={(e) => updateFormData('description', e.target.value)}
                      multiline
                      rows={3}
                      placeholder="Brief description of your company, product, and mission..."
                      fullWidth
                    />
                  </Grid>
                </Grid>
                
                <Typography variant="h6" fontWeight={600} sx={{ mt: 4, mb: 2 }}>
                  Contact Information
                </Typography>
                <Divider sx={{ mb: 3 }} />
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Contact Name"
                      value={formData.contact_name}
                      onChange={(e) => updateFormData('contact_name', e.target.value)}
                      fullWidth
                      required
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Contact Title"
                      value={formData.contact_title}
                      onChange={(e) => updateFormData('contact_title', e.target.value)}
                      placeholder="CEO, Founder, etc."
                      fullWidth
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Email Address"
                      type="email"
                      value={formData.contact_email}
                      onChange={(e) => updateFormData('contact_email', e.target.value)}
                      fullWidth
                      required
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Phone Number"
                      value={formData.contact_phone}
                      onChange={(e) => updateFormData('contact_phone', e.target.value)}
                      placeholder="+1 (555) 123-4567"
                      fullWidth
                    />
                  </Grid>
                </Grid>
              </Box>
            )}

            {/* Step 1: File Upload */}
            {activeStep === 1 && (
              <Box>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Upload Documents
                </Typography>
                <Divider sx={{ mb: 3 }} />
                
                {/* Drop Zone */}
                <Paper
                  sx={{
                    border: '2px dashed #d1d5db',
                    borderRadius: 2,
                    p: 4,
                    textAlign: 'center',
                    mb: 3,
                    backgroundColor: '#f9fafb',
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: '#f3f4f6',
                      borderColor: '#9ca3af',
                    },
                  }}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Drop files here or click to browse
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Supported formats: PDF, PPT, XLSX, MP4, MOV, MP3, WAV
                  </Typography>
                  <Button variant="contained" startIcon={<UploadIcon />}>
                    Select Files
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept={Object.keys(acceptedFileTypes).join(',')}
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                  />
                </Paper>
                
                {/* File List */}
                {files.length > 0 && (
                  <Box>
                    <Typography variant="subtitle1" fontWeight={500} gutterBottom>
                      Uploaded Files ({files.length})
                    </Typography>
                    <List>
                      {files.map((file) => (
                        <ListItem 
                          key={file.id}
                          sx={{ 
                            border: '1px solid #e5e7eb', 
                            borderRadius: 1, 
                            mb: 1,
                            backgroundColor: 'white'
                          }}
                        >
                          <ListItemIcon>
                            {getFileIcon(file.type)}
                          </ListItemIcon>
                          <ListItemText
                            primary={file.name}
                            secondary={
                              <Box>
                                <Typography variant="caption" color="text.secondary">
                                  {formatFileSize(file.size)}
                                </Typography>
                                {file.status === 'uploading' && (
                                  <LinearProgress 
                                    variant="determinate" 
                                    value={file.progress} 
                                    sx={{ mt: 1 }}
                                  />
                                )}
                                {file.error && (
                                  <Typography variant="caption" color="error">
                                    Error: {file.error}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                          <Box display="flex" alignItems="center" gap={1}>
                            {file.status === 'uploaded' && (
                              <CheckCircleIcon color="success" fontSize="small" />
                            )}
                            {file.status === 'error' && (
                              <ErrorIcon color="error" fontSize="small" />
                            )}
                            <IconButton
                              size="small"
                              onClick={() => removeFile(file.id)}
                              color="error"
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Box>
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
                
                {/* Upload Progress */}
                {uploading && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Uploading files...
                    </Typography>
                    <LinearProgress />
                  </Box>
                )}
              </Box>
            )}

            {/* Step 2: Additional Details */}
            {activeStep === 2 && (
              <Box>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Additional Information
                </Typography>
                <Divider sx={{ mb: 3 }} />
                
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Team Size"
                      type="number"
                      value={formData.team_size}
                      onChange={(e) => updateFormData('team_size', e.target.value)}
                      placeholder="15"
                      fullWidth
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Current ARR"
                      type="number"
                      value={formData.current_arr}
                      onChange={(e) => updateFormData('current_arr', e.target.value)}
                      InputProps={{ startAdornment: '$' }}
                      placeholder="1200000"
                      fullWidth
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Runway (Months)"
                      type="number"
                      value={formData.runway_months}
                      onChange={(e) => updateFormData('runway_months', e.target.value)}
                      placeholder="18"
                      fullWidth
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Previous Funding"
                      type="number"
                      value={formData.previous_funding}
                      onChange={(e) => updateFormData('previous_funding', e.target.value)}
                      InputProps={{ startAdornment: '$' }}
                      placeholder="2000000"
                      fullWidth
                    />
                  </Grid>
                </Grid>
                
                <Typography variant="h6" fontWeight={600} sx={{ mt: 4, mb: 2 }}>
                  Processing Options
                </Typography>
                <Divider sx={{ mb: 3 }} />
                
                <Box display="flex" flexDirection="column" gap={2}>
                  <FormControlLabel
                    control={
                      <Checkbox 
                        checked={formData.auto_processing}
                        onChange={(e) => updateFormData('auto_processing', e.target.checked)}
                      />
                    }
                    label="Enable automatic AI processing"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox 
                        checked={formData.notify_completion}
                        onChange={(e) => updateFormData('notify_completion', e.target.checked)}
                      />
                    }
                    label="Notify when evaluation is complete"
                  />
                </Box>
                
                <TextField
                  select
                  label="Processing Priority"
                  value={formData.priority}
                  onChange={(e) => updateFormData('priority', e.target.value)}
                  fullWidth
                  sx={{ mt: 2 }}
                >
                  <MenuItem value="low">Low Priority</MenuItem>
                  <MenuItem value="normal">Normal Priority</MenuItem>
                  <MenuItem value="high">High Priority</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </TextField>
              </Box>
            )}

            {/* Step 3: Review & Submit */}
            {activeStep === 3 && (
              <Box>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Review & Submit
                </Typography>
                <Divider sx={{ mb: 3 }} />
                
                <Alert severity="info" sx={{ mb: 3 }}>
                  Please review all information before submitting. The AI evaluation process will begin immediately after submission.
                </Alert>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Paper elevation={0} sx={{ p: 3, backgroundColor: '#f8fafc' }}>
                      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                        Company Details
                      </Typography>
                      <Typography variant="body2"><strong>Name:</strong> {formData.company_name}</Typography>
                      <Typography variant="body2"><strong>Industry:</strong> {formData.industry}</Typography>
                      <Typography variant="body2"><strong>Stage:</strong> {formData.funding_stage}</Typography>
                      <Typography variant="body2"><strong>Contact:</strong> {formData.contact_name} ({formData.contact_email})</Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Paper elevation={0} sx={{ p: 3, backgroundColor: '#f8fafc' }}>
                      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                        Files ({files.filter(f => f.status === 'uploaded').length})
                      </Typography>
                      {files.filter(f => f.status === 'uploaded').map(file => (
                        <Typography key={file.id} variant="body2">
                          • {file.name} ({formatFileSize(file.size)})
                        </Typography>
                      ))}
                    </Paper>
                  </Grid>
                </Grid>
              </Box>
            )}

            {/* Navigation Buttons */}
            <Box sx={{ display: 'flex', flexDirection: 'row', pt: 4 }}>
              <Button
                color="inherit"
                disabled={activeStep === 0}
                onClick={handleBack}
                sx={{ mr: 1 }}
              >
                Back
              </Button>
              <Box sx={{ flex: '1 1 auto' }} />
              {activeStep === steps.length - 1 ? (
                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={loading || !isStepValid(activeStep)}
                  startIcon={<SendIcon />}
                >
                  {loading ? 'Submitting...' : 'Submit Application'}
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={!isStepValid(activeStep)}
                >
                  Next
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={handleCloseError}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        >
          <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>

        <Snackbar
          open={!!success}
          autoHideDuration={4000}
          onClose={handleCloseSuccess}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert onClose={handleCloseSuccess} severity="success" sx={{ width: '100%' }}>
            {success}
          </Alert>
        </Snackbar>

        {/* Development Info */}
        {process.env.NODE_ENV === 'development' && (
          <Paper 
            elevation={1} 
            sx={{ 
              position: 'fixed', 
              top: 80, 
              right: 16, 
              p: 2, 
              backgroundColor: '#fff3cd',
              border: '1px solid #ffeaa7',
              maxWidth: 300,
              zIndex: 1100
            }}
          >
            <Typography variant="caption" display="block" gutterBottom>
              <strong>Upload Development Mode</strong>
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Step: {activeStep + 1} of {steps.length}
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Files: {files.length} selected
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Uploaded: {files.filter(f => f.status === 'uploaded').length}
            </Typography>
          </Paper>
        )}
      </Container>
    </Box>
  );
};

export default Upload;