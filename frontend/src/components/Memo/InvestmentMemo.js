/**
 * Investment Memo Screen Component
 * Detailed view and memo creation/editing for startup applications
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  IconButton,
  Chip,
  Divider,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Breadcrumbs,
  Link,
  Skeleton,
  Paper,
  Tooltip,
  LinearProgress,
  Avatar,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Send as SendIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Visibility as VisibilityIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  AttachFile as AttachFileIcon,
  Home as HomeIcon,
  AccountTree as PipelineIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';

// Components
import ApplicationDetails from './ApplicationDetails';
import MemoEditor from './MemoEditor';
import MemoApproval from './MemoApproval';
import FilesList from './FilesList';

// Services
import { memosApi, startupsApi, uploadsApi, apiUtils } from '../../services/api';

const InvestmentMemo = () => {
  const { applicationId } = useParams();
  const navigate = useNavigate();
  
  // State management
  const [application, setApplication] = useState(null);
  const [memo, setMemo] = useState(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editMode, setEditMode] = useState(false);
  
  // Dialog states
  const [approvalDialogOpen, setApprovalDialogOpen] = useState(false);
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  
  // Form states
  const [memoContent, setMemoContent] = useState('');
  const [recommendation, setRecommendation] = useState('');
  const [reviewDate, setReviewDate] = useState('');

  // Fetch application and memo data
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      const [appResponse, filesResponse] = await Promise.all([
        startupsApi.getStartup(applicationId),
        uploadsApi.getStartupFiles(applicationId).catch(() => ({ data: [] }))
      ]);
      
      if (appResponse.data) {
        setApplication(appResponse.data);
      }
      
      if (filesResponse.data) {
        setFiles(Array.isArray(filesResponse.data) ? filesResponse.data : []);
      }
      
      // Try to fetch existing memo
      try {
        const memoResponse = await memosApi.getMemoByStartup(applicationId);
        if (memoResponse.data) {
          setMemo(memoResponse.data);
          setMemoContent(memoResponse.data.content || '');
          setRecommendation(memoResponse.data.recommendation || '');
        }
      } catch (memoErr) {
        // No existing memo - this is fine for new applications
        console.log('No existing memo found, will create new one');
      }
      
    } catch (err) {
      console.error('Data fetch error:', err);
      const errorInfo = apiUtils.handleError(err);
      setError(`Failed to load application: ${errorInfo.message}`);
      
      // Set fallback data for development
      const fallbackApplication = {
        id: parseInt(applicationId),
        company_name: 'TechFlow AI',
        website: 'https://techflow.ai',
        contact_name: 'Sarah Chen',
        contact_email: 'sarah@techflow.ai',
        contact_phone: '+1 (555) 123-4567',
        industry: 'AI/ML',
        funding_stage: 'Series A',
        funding_amount_requested: 5000000,
        current_arr: 1200000,
        gross_margin: 75.5,
        runway_months: 18,
        status: 'manual_review',
        ai_score: 83.08,
        manual_score: null,
        final_rating: null,
        assigned_analyst_id: 1,
        processing_notes: 'Strong technical team with proven AI expertise',
        created_at: '2025-01-20T10:30:00Z',
        updated_at: '2025-01-20T14:45:00Z'
      };
      
      setApplication(fallbackApplication);
      setFiles([
        {
          id: 1,
          filename: 'pitch_deck.pdf',
          original_filename: 'TechFlow AI - Series A Pitch Deck.pdf',
          file_type: 'pitch_deck',
          file_size: 2456789,
          mime_type: 'application/pdf',
          uploaded_at: '2025-01-20T10:35:00Z'
        },
        {
          id: 2,
          filename: 'financial_model.xlsx',
          original_filename: 'TechFlow Financial Model 2024-2026.xlsx',
          file_type: 'financial',
          file_size: 987654,
          mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          uploaded_at: '2025-01-20T11:20:00Z'
        }
      ]);
    } finally {
      setLoading(false);
    }
  }, [applicationId]);

  // Initial data load
  useEffect(() => {
    if (applicationId) {
      fetchData();
    }
  }, [applicationId, fetchData]);

  // Handle memo save
  const handleSaveMemo = async () => {
    try {
      setSaving(true);
      
      const memoData = {
        startup_application_id: parseInt(applicationId),
        content: memoContent,
        recommendation: recommendation,
        is_draft: true
      };
      
      let response;
      if (memo?.id) {
        // Update existing memo
        response = await memosApi.updateMemo(memo.id, memoData);
      } else {
        // Create new memo
        response = await memosApi.createMemo(memoData, 1); // TODO: Get actual user ID
      }
      
      if (response.data) {
        setMemo(response.data);
        setSuccess('Memo saved successfully');
        setEditMode(false);
      }
    } catch (err) {
      console.error('Save memo error:', err);
      const errorInfo = apiUtils.handleError(err);
      setError(`Failed to save memo: ${errorInfo.message}`);
    } finally {
      setSaving(false);
    }
  };

  // Handle memo approval
  const handleApproveMemo = async () => {
    try {
      if (memo?.id) {
        await memosApi.approveMemo(memo.id);
        setMemo(prev => ({ ...prev, approved: true, approved_at: new Date().toISOString() }));
        setSuccess('Memo approved successfully');
      }
    } catch (err) {
      console.error('Approve memo error:', err);
      setError('Failed to approve memo');
    }
    setApprovalDialogOpen(false);
  };

  // Handle schedule review
  const handleScheduleReview = async () => {
    try {
      if (memo?.id && reviewDate) {
        await memosApi.scheduleReview(memo.id, reviewDate);
        setMemo(prev => ({ ...prev, review_date: reviewDate }));
        setSuccess(`Review scheduled for ${new Date(reviewDate).toLocaleDateString()}`);
      }
    } catch (err) {
      console.error('Schedule review error:', err);
      setError('Failed to schedule review');
    }
    setReviewDialogOpen(false);
    setReviewDate('');
  };

  // Handle back navigation
  const handleBack = () => {
    navigate('/pipeline');
  };

  // Close notifications
  const handleCloseError = () => setError(null);
  const handleCloseSuccess = () => setSuccess(null);

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box display="flex" alignItems="center" mb={3}>
          <Skeleton variant="circular" width={40} height={40} />
          <Skeleton variant="text" width={200} height={32} sx={{ ml: 2 }} />
        </Box>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Skeleton variant="rectangular" height={600} sx={{ borderRadius: 2 }} />
          </Grid>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (!application) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error">
          Application not found. Please check the application ID and try again.
        </Alert>
      </Container>
    );
  }

  const getStatusColor = (status) => {
    const colors = {
      new: '#6b7280',
      data_processing: '#3b82f6',
      ai_analysis: '#8b5cf6',
      manual_review: '#f59e0b',
      partner_review: '#10b981',
      completed: '#059669',
      rejected: '#ef4444',
    };
    return colors[status] || '#6b7280';
  };

  const formatStatus = (status) => {
    return status?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown';
  };

  return (
    <Box sx={{ flexGrow: 1, backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
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
            <Link
              color="inherit"
              href="#"
              onClick={() => navigate('/pipeline')}
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <PipelineIcon fontSize="small" />
              Pipeline
            </Link>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.primary' }}>
              <AssignmentIcon fontSize="small" />
              Investment Memo
            </Box>
          </Breadcrumbs>
          
          {/* Title and Actions */}
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
            <Box display="flex" alignItems="center" gap={2}>
              <IconButton onClick={handleBack} sx={{ mr: 1 }}>
                <ArrowBackIcon />
              </IconButton>
              
              <Box>
                <Typography variant="h4" fontWeight={700} color="text.primary" gutterBottom>
                  {application.company_name}
                </Typography>
                <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
                  <Chip
                    label={formatStatus(application.status)}
                    sx={{
                      backgroundColor: `${getStatusColor(application.status)}20`,
                      color: getStatusColor(application.status),
                      fontWeight: 500,
                    }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {application.funding_stage} • {application.industry}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    AI Score: {application.ai_score?.toFixed(1)}%
                  </Typography>
                </Box>
              </Box>
            </Box>
            
            <Box display="flex" gap={1} alignItems="center" flexWrap="wrap">
              {!editMode && (
                <>
                  <Button
                    variant="outlined"
                    startIcon={<EditIcon />}
                    onClick={() => setEditMode(true)}
                    size="small"
                  >
                    Edit Memo
                  </Button>
                  {memo && !memo.approved && (
                    <Button
                      variant="contained"
                      startIcon={<CheckCircleIcon />}
                      onClick={() => setApprovalDialogOpen(true)}
                      color="success"
                      size="small"
                    >
                      Approve
                    </Button>
                  )}
                  <Button
                    variant="outlined"
                    startIcon={<ScheduleIcon />}
                    onClick={() => setReviewDialogOpen(true)}
                    size="small"
                  >
                    Schedule Review
                  </Button>
                </>
              )}
              
              {editMode && (
                <>
                  <Button
                    variant="outlined"
                    onClick={() => {
                      setEditMode(false);
                      setMemoContent(memo?.content || '');
                      setRecommendation(memo?.recommendation || '');
                    }}
                    size="small"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSaveMemo}
                    disabled={saving}
                    size="small"
                  >
                    {saving ? 'Saving...' : 'Save Memo'}
                  </Button>
                </>
              )}
            </Box>
          </Box>
        </Box>

        {/* Main Content */}
        <Grid container spacing={4}>
          {/* Left Column - Memo Editor */}
          <Grid item xs={12} lg={8}>
            <MemoEditor
              content={memoContent}
              recommendation={recommendation}
              editMode={editMode}
              memo={memo}
              onContentChange={setMemoContent}
              onRecommendationChange={setRecommendation}
              saving={saving}
            />
          </Grid>

          {/* Right Column - Application Details and Files */}
          <Grid item xs={12} lg={4}>
            <Box display="flex" flexDirection="column" gap={3}>
              {/* Application Details */}
              <ApplicationDetails application={application} />
              
              {/* Files List */}
              <FilesList 
                files={files}
                applicationId={applicationId}
                onFilesUpdate={setFiles}
              />
              
              {/* Memo Approval Status */}
              {memo && (
                <MemoApproval 
                  memo={memo}
                  onApprove={() => setApprovalDialogOpen(true)}
                  onScheduleReview={() => setReviewDialogOpen(true)}
                />
              )}
            </Box>
          </Grid>
        </Grid>

        {/* Approval Dialog */}
        <Dialog
          open={approvalDialogOpen}
          onClose={() => setApprovalDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Approve Investment Memo</DialogTitle>
          <DialogContent>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Are you sure you want to approve this investment memo for <strong>{application.company_name}</strong>?
            </Typography>
            <Alert severity="info">
              Once approved, this memo will be finalized and ready for partner review.
            </Alert>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setApprovalDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleApproveMemo} variant="contained" color="success">
              Approve Memo
            </Button>
          </DialogActions>
        </Dialog>

        {/* Schedule Review Dialog */}
        <Dialog
          open={reviewDialogOpen}
          onClose={() => setReviewDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Schedule Partner Review</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <TextField
              label="Review Date"
              type="date"
              value={reviewDate}
              onChange={(e) => setReviewDate(e.target.value)}
              fullWidth
              InputLabelProps={{
                shrink: true,
              }}
              inputProps={{
                min: new Date().toISOString().split('T')[0]
              }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setReviewDialogOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleScheduleReview} 
              variant="contained"
              disabled={!reviewDate}
            >
              Schedule Review
            </Button>
          </DialogActions>
        </Dialog>

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
      </Container>
    </Box>
  );
};

export default InvestmentMemo;