/**
 * Settings Screen Component
 * User preferences, AI configuration, team management, and integrations
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  IconButton,
  Switch,
  FormControlLabel,
  TextField,
  MenuItem,
  Divider,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Breadcrumbs,
  Link,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondary,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tab,
  Tabs,
  Paper,
  Tooltip,
  Fab,
} from '@mui/material';
import {
  Home as HomeIcon,
  Settings as SettingsIcon,
  Save as SaveIcon,
  Person as PersonIcon,
  SmartToy as AIIcon,
  Group as TeamIcon,
  Integration as IntegrationIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Palette as ThemeIcon,
  Language as LanguageIcon,
  Storage as StorageIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

// Services
import { settingsApi, usersApi, apiUtils } from '../../services/api';

const Settings = () => {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [settings, setSettings] = useState({
    // General Settings
    language: 'en',
    timezone: 'UTC',
    theme: 'light',
    notifications: {
      email: true,
      push: true,
      newApplications: true,
      memoApprovals: true,
      systemUpdates: false,
    },
    // AI Configuration
    ai: {
      defaultModel: 'gpt-4',
      confidenceThreshold: 0.8,
      autoProcessing: true,
      humanReviewRequired: true,
      customPrompts: {
        riskAssessment: '',
        marketAnalysis: '',
        founderEvaluation: '',
      },
      scoringWeights: {
        market: 25,
        team: 30,
        product: 25,
        financials: 20,
      },
    },
    // Team Management
    team: {
      defaultAssignments: true,
      workloadBalance: true,
      collaborationMode: 'standard',
    },
    // Integration Settings
    integrations: {
      calendar: false,
      crm: false,
      slack: false,
      email: false,
    },
    // Security Settings
    security: {
      twoFactor: false,
      sessionTimeout: 8, // hours
      ipWhitelist: [],
      apiAccessEnabled: false,
    },
  });
  
  const [teamMembers, setTeamMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Dialog states
  const [addMemberOpen, setAddMemberOpen] = useState(false);
  const [newMember, setNewMember] = useState({
    name: '',
    email: '',
    role: 'analyst',
  });

  // Tab configuration
  const tabs = [
    { label: 'General', icon: <PersonIcon fontSize="small" />, value: 0 },
    { label: 'AI Configuration', icon: <AIIcon fontSize="small" />, value: 1 },
    { label: 'Team', icon: <TeamIcon fontSize="small" />, value: 2 },
    { label: 'Integrations', icon: <IntegrationIcon fontSize="small" />, value: 3 },
    { label: 'Security', icon: <SecurityIcon fontSize="small" />, value: 4 },
  ];

  // Fetch settings data
  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      
      const [preferencesResponse, investmentWeightsResponse, teamResponse] = await Promise.all([
        settingsApi.getPreferences().catch(() => ({ data: null })),
        settingsApi.getInvestmentWeights().catch(() => ({ data: null })),
        usersApi.getTeamMembers().catch(() => ({ data: [] }))
      ]);
      
      // Merge preferences into settings
      if (preferencesResponse.data) {
        setSettings(prev => ({
          ...prev,
          language: preferencesResponse.data.language || prev.language,
          timezone: preferencesResponse.data.timezone || prev.timezone,
          theme: preferencesResponse.data.display?.theme || prev.theme,
          notifications: {
            ...prev.notifications,
            ...preferencesResponse.data.notifications
          }
        }));
      }
      
      // Update AI scoring weights from backend
      if (investmentWeightsResponse.data) {
        setSettings(prev => ({
          ...prev,
          ai: {
            ...prev.ai,
            scoringWeights: {
              market: investmentWeightsResponse.data.market_size_weight || prev.ai.scoringWeights.market,
              team: investmentWeightsResponse.data.team_experience_weight || prev.ai.scoringWeights.team,
              product: investmentWeightsResponse.data.business_model_weight || prev.ai.scoringWeights.product,
              financials: investmentWeightsResponse.data.financial_health_weight || prev.ai.scoringWeights.financials,
            }
          }
        }));
      }
      
      // Load team members
      if (teamResponse.data && Array.isArray(teamResponse.data)) {
        // Map backend user data to frontend format
        const formattedTeamMembers = teamResponse.data.map(user => ({
          id: user.id,
          name: user.full_name || user.name || 'Unknown',
          email: user.email,
          role: user.role || 'viewer',
          avatar: user.avatar_url || null,
          status: user.is_active ? 'active' : 'inactive',
          lastActive: user.last_login || user.updated_at,
        }));
        setTeamMembers(formattedTeamMembers);
      } else {
        // Fallback team data for development
        setTeamMembers([
          {
            id: 1,
            name: 'John Doe',
            email: 'john.doe@aialchemy.com',
            role: 'admin',
            avatar: null,
            status: 'active',
            lastActive: '2025-01-21T10:30:00Z',
          },
          {
            id: 2,
            name: 'Jane Smith',
            email: 'jane.smith@aialchemy.com',
            role: 'senior_analyst',
            avatar: null,
            status: 'active',
            lastActive: '2025-01-21T09:45:00Z',
          },
          {
            id: 3,
            name: 'Michael Chen',
            email: 'michael.chen@aialchemy.com',
            role: 'analyst',
            avatar: null,
            status: 'away',
            lastActive: '2025-01-20T16:20:00Z',
          },
        ]);
      }
      
    } catch (err) {
      console.error('Settings fetch error:', err);
      const errorInfo = apiUtils.handleError(err);
      setError(`Failed to load settings: ${errorInfo.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data load
  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  // Handle settings save
  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      
      // Prepare preferences data for backend
      const preferencesData = {
        language: settings.language,
        timezone: settings.timezone,
        display: {
          theme: settings.theme
        },
        notifications: {
          email_notifications: settings.notifications.email,
          desktop_notifications: settings.notifications.push,
          new_applications: settings.notifications.newApplications,
          memo_approvals: settings.notifications.memoApprovals,
          system_updates: settings.notifications.systemUpdates
        }
      };
      
      // Prepare investment weights data
      const weightsData = {
        market_size_weight: settings.ai.scoringWeights.market,
        team_experience_weight: settings.ai.scoringWeights.team,
        business_model_weight: settings.ai.scoringWeights.product,
        financial_health_weight: settings.ai.scoringWeights.financials,
        traction_weight: 100 - (settings.ai.scoringWeights.market + settings.ai.scoringWeights.team + settings.ai.scoringWeights.product + settings.ai.scoringWeights.financials)
      };
      
      // Save both preferences and investment weights
      await Promise.all([
        settingsApi.updatePreferences(preferencesData),
        settingsApi.updateInvestmentWeights(weightsData)
      ]);
      
      setSuccess('Settings saved successfully');
      
    } catch (err) {
      console.error('Save settings error:', err);
      const errorInfo = apiUtils.handleError(err);
      setError(`Failed to save settings: ${errorInfo.message}`);
    } finally {
      setSaving(false);
    }
  };

  // Handle add team member
  const handleAddMember = async () => {
    try {
      if (!newMember.name || !newMember.email) {
        setError('Please fill in all required fields');
        return;
      }

      const response = await usersApi.inviteUser(newMember);
      
      if (response.data) {
        setTeamMembers(prev => [...prev, response.data]);
        setSuccess(`Invitation sent to ${newMember.email}`);
        setNewMember({ name: '', email: '', role: 'analyst' });
        setAddMemberOpen(false);
      }
    } catch (err) {
      console.error('Add member error:', err);
      const errorInfo = apiUtils.handleError(err);
      setError(`Failed to add team member: ${errorInfo.message}`);
    }
  };

  // Handle remove team member
  const handleRemoveMember = async (memberId) => {
    try {
      await usersApi.removeUser(memberId);
      setTeamMembers(prev => prev.filter(member => member.id !== memberId));
      setSuccess('Team member removed successfully');
    } catch (err) {
      console.error('Remove member error:', err);
      setError('Failed to remove team member');
    }
  };

  // Handle setting updates
  const updateSetting = (path, value) => {
    setSettings(prev => {
      const newSettings = { ...prev };
      const keys = path.split('.');
      let current = newSettings;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!(keys[i] in current)) {
          current[keys[i]] = {};
        }
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newSettings;
    });
  };

  // Close notifications
  const handleCloseError = () => setError(null);
  const handleCloseSuccess = () => setSuccess(null);

  // Get role display name
  const getRoleDisplayName = (role) => {
    const roles = {
      admin: 'Administrator',
      senior_analyst: 'Senior Analyst',
      analyst: 'Analyst',
      viewer: 'Viewer',
    };
    return roles[role] || role;
  };

  // Get role color
  const getRoleColor = (role) => {
    const colors = {
      admin: '#ef4444',
      senior_analyst: '#8b5cf6',
      analyst: '#3b82f6',
      viewer: '#6b7280',
    };
    return colors[role] || '#6b7280';
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
              sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
            >
              <HomeIcon fontSize="small" />
              Home
            </Link>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.primary' }}>
              <SettingsIcon fontSize="small" />
              Settings
            </Box>
          </Breadcrumbs>
          
          {/* Title */}
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Box>
              <Typography variant="h4" fontWeight={700} color="text.primary" gutterBottom>
                Settings & Configuration
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Customize your AIAlchemy platform experience
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Settings Content */}
        <Grid container spacing={4}>
          {/* Settings Navigation */}
          <Grid item xs={12} md={3}>
            <Paper elevation={1} sx={{ borderRadius: 2 }}>
              <Tabs
                orientation="vertical"
                value={activeTab}
                onChange={(e, newValue) => setActiveTab(newValue)}
                sx={{
                  borderRight: 1,
                  borderColor: 'divider',
                  '& .MuiTab-root': {
                    alignItems: 'flex-start',
                    textAlign: 'left',
                    minHeight: 'auto',
                    py: 2,
                    px: 3,
                  },
                }}
              >
                {tabs.map((tab) => (
                  <Tab
                    key={tab.value}
                    icon={tab.icon}
                    label={tab.label}
                    iconPosition="start"
                    sx={{
                      justifyContent: 'flex-start',
                      gap: 1.5,
                    }}
                  />
                ))}
              </Tabs>
            </Paper>
          </Grid>

          {/* Settings Panels */}
          <Grid item xs={12} md={9}>
            <Box>
              {/* General Settings */}
              {activeTab === 0 && (
                <Card elevation={1} sx={{ borderRadius: 2 }}>
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      General Preferences
                    </Typography>
                    <Divider sx={{ mb: 3 }} />
                    
                    <Grid container spacing={3}>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          select
                          label="Language"
                          value={settings.language}
                          onChange={(e) => updateSetting('language', e.target.value)}
                          fullWidth
                        >
                          <MenuItem value="en">English</MenuItem>
                          <MenuItem value="es">Spanish</MenuItem>
                          <MenuItem value="fr">French</MenuItem>
                          <MenuItem value="de">German</MenuItem>
                        </TextField>
                      </Grid>
                      
                      <Grid item xs={12} sm={6}>
                        <TextField
                          select
                          label="Timezone"
                          value={settings.timezone}
                          onChange={(e) => updateSetting('timezone', e.target.value)}
                          fullWidth
                        >
                          <MenuItem value="UTC">UTC</MenuItem>
                          <MenuItem value="America/New_York">Eastern Time</MenuItem>
                          <MenuItem value="America/Los_Angeles">Pacific Time</MenuItem>
                          <MenuItem value="Europe/London">London</MenuItem>
                        </TextField>
                      </Grid>
                      
                      <Grid item xs={12} sm={6}>
                        <TextField
                          select
                          label="Theme"
                          value={settings.theme}
                          onChange={(e) => updateSetting('theme', e.target.value)}
                          fullWidth
                        >
                          <MenuItem value="light">Light</MenuItem>
                          <MenuItem value="dark">Dark</MenuItem>
                          <MenuItem value="auto">Auto</MenuItem>
                        </TextField>
                      </Grid>
                    </Grid>
                    
                    <Typography variant="h6" fontWeight={600} sx={{ mt: 4, mb: 2 }}>
                      Notifications
                    </Typography>
                    <Divider sx={{ mb: 3 }} />
                    
                    <Box display="flex" flexDirection="column" gap={2}>
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={settings.notifications.email}
                            onChange={(e) => updateSetting('notifications.email', e.target.checked)}
                          />
                        }
                        label="Email notifications"
                      />
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={settings.notifications.push}
                            onChange={(e) => updateSetting('notifications.push', e.target.checked)}
                          />
                        }
                        label="Push notifications"
                      />
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={settings.notifications.newApplications}
                            onChange={(e) => updateSetting('notifications.newApplications', e.target.checked)}
                          />
                        }
                        label="New application alerts"
                      />
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={settings.notifications.memoApprovals}
                            onChange={(e) => updateSetting('notifications.memoApprovals', e.target.checked)}
                          />
                        }
                        label="Memo approval notifications"
                      />
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={settings.notifications.systemUpdates}
                            onChange={(e) => updateSetting('notifications.systemUpdates', e.target.checked)}
                          />
                        }
                        label="System update notifications"
                      />
                    </Box>
                  </CardContent>
                </Card>
              )}

              {/* AI Configuration */}
              {activeTab === 1 && (
                <Card elevation={1} sx={{ borderRadius: 2 }}>
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      AI Model Configuration
                    </Typography>
                    <Divider sx={{ mb: 3 }} />
                    
                    <Grid container spacing={3}>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          select
                          label="Default AI Model"
                          value={settings.ai.defaultModel}
                          onChange={(e) => updateSetting('ai.defaultModel', e.target.value)}
                          fullWidth
                        >
                          <MenuItem value="gpt-4">GPT-4</MenuItem>
                          <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                          <MenuItem value="claude">Claude</MenuItem>
                          <MenuItem value="gemini">Gemini Pro</MenuItem>
                        </TextField>
                      </Grid>
                      
                      <Grid item xs={12} sm={6}>
                        <TextField
                          label="Confidence Threshold"
                          type="number"
                          value={settings.ai.confidenceThreshold}
                          onChange={(e) => updateSetting('ai.confidenceThreshold', parseFloat(e.target.value))}
                          inputProps={{ min: 0, max: 1, step: 0.1 }}
                          fullWidth
                        />
                      </Grid>
                    </Grid>
                    
                    <Box sx={{ mt: 3 }}>
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={settings.ai.autoProcessing}
                            onChange={(e) => updateSetting('ai.autoProcessing', e.target.checked)}
                          />
                        }
                        label="Enable automatic processing"
                      />
                    </Box>
                    
                    <Box sx={{ mt: 2 }}>
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={settings.ai.humanReviewRequired}
                            onChange={(e) => updateSetting('ai.humanReviewRequired', e.target.checked)}
                          />
                        }
                        label="Require human review for all decisions"
                      />
                    </Box>
                    
                    <Typography variant="h6" fontWeight={600} sx={{ mt: 4, mb: 2 }}>
                      Scoring Weights
                    </Typography>
                    <Divider sx={{ mb: 3 }} />
                    
                    <Grid container spacing={3}>
                      {Object.entries(settings.ai.scoringWeights).map(([key, value]) => (
                        <Grid item xs={12} sm={6} key={key}>
                          <TextField
                            label={key.charAt(0).toUpperCase() + key.slice(1)}
                            type="number"
                            value={value}
                            onChange={(e) => updateSetting(`ai.scoringWeights.${key}`, parseInt(e.target.value))}
                            inputProps={{ min: 0, max: 100 }}
                            InputProps={{ endAdornment: '%' }}
                            fullWidth
                          />
                        </Grid>
                      ))}
                    </Grid>
                  </CardContent>
                </Card>
              )}

              {/* Team Management */}
              {activeTab === 2 && (
                <Card elevation={1} sx={{ borderRadius: 2 }}>
                  <CardContent sx={{ p: 4 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="h6" fontWeight={600}>
                        Team Members
                      </Typography>
                      <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={() => setAddMemberOpen(true)}
                        size="small"
                      >
                        Add Member
                      </Button>
                    </Box>
                    <Divider sx={{ mb: 3 }} />
                    
                    <List>
                      {teamMembers.map((member, index) => (
                        <ListItem key={member.id} divider={index < teamMembers.length - 1}>
                          <ListItemIcon>
                            <Avatar sx={{ bgcolor: 'primary.main' }}>
                              {member.name.charAt(0).toUpperCase()}
                            </Avatar>
                          </ListItemIcon>
                          <ListItemText
                            primary={member.name}
                            secondary={member.email}
                          />
                          <Box display="flex" alignItems="center" gap={1}>
                            <Chip
                              label={getRoleDisplayName(member.role)}
                              size="small"
                              sx={{
                                backgroundColor: `${getRoleColor(member.role)}20`,
                                color: getRoleColor(member.role),
                              }}
                            />
                            <Chip
                              label={member.status}
                              size="small"
                              color={member.status === 'active' ? 'success' : 'default'}
                            />
                            <IconButton
                              size="small"
                              onClick={() => handleRemoveMember(member.id)}
                              color="error"
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Box>
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              )}

              {/* Integrations */}
              {activeTab === 3 && (
                <Card elevation={1} sx={{ borderRadius: 2 }}>
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      External Integrations
                    </Typography>
                    <Divider sx={{ mb: 3 }} />
                    
                    <Box display="flex" flexDirection="column" gap={3}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="subtitle1" fontWeight={500}>
                            Calendar Integration
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Sync with Google Calendar for interview scheduling
                          </Typography>
                        </Box>
                        <Switch 
                          checked={settings.integrations.calendar}
                          onChange={(e) => updateSetting('integrations.calendar', e.target.checked)}
                        />
                      </Box>
                      
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="subtitle1" fontWeight={500}>
                            CRM Integration
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Connect with Salesforce or HubSpot
                          </Typography>
                        </Box>
                        <Switch 
                          checked={settings.integrations.crm}
                          onChange={(e) => updateSetting('integrations.crm', e.target.checked)}
                        />
                      </Box>
                      
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="subtitle1" fontWeight={500}>
                            Slack Integration
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Get notifications in Slack channels
                          </Typography>
                        </Box>
                        <Switch 
                          checked={settings.integrations.slack}
                          onChange={(e) => updateSetting('integrations.slack', e.target.checked)}
                        />
                      </Box>
                      
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="subtitle1" fontWeight={500}>
                            Email Integration
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Automated email workflows and notifications
                          </Typography>
                        </Box>
                        <Switch 
                          checked={settings.integrations.email}
                          onChange={(e) => updateSetting('integrations.email', e.target.checked)}
                        />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              )}

              {/* Security Settings */}
              {activeTab === 4 && (
                <Card elevation={1} sx={{ borderRadius: 2 }}>
                  <CardContent sx={{ p: 4 }}>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Security & Privacy
                    </Typography>
                    <Divider sx={{ mb: 3 }} />
                    
                    <Grid container spacing={3}>
                      <Grid item xs={12}>
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={settings.security.twoFactor}
                              onChange={(e) => updateSetting('security.twoFactor', e.target.checked)}
                            />
                          }
                          label="Enable two-factor authentication"
                        />
                      </Grid>
                      
                      <Grid item xs={12} sm={6}>
                        <TextField
                          label="Session Timeout (hours)"
                          type="number"
                          value={settings.security.sessionTimeout}
                          onChange={(e) => updateSetting('security.sessionTimeout', parseInt(e.target.value))}
                          inputProps={{ min: 1, max: 24 }}
                          fullWidth
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={settings.security.apiAccessEnabled}
                              onChange={(e) => updateSetting('security.apiAccessEnabled', e.target.checked)}
                            />
                          }
                          label="Enable API access"
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              )}
            </Box>
          </Grid>
        </Grid>

        {/* Floating Action Button for Save */}
        <Fab
          color="primary"
          aria-label="save"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1000,
          }}
          onClick={handleSaveSettings}
          disabled={saving}
        >
          <SaveIcon />
        </Fab>

        {/* Add Member Dialog */}
        <Dialog
          open={addMemberOpen}
          onClose={() => setAddMemberOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Add Team Member</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  label="Full Name"
                  value={newMember.name}
                  onChange={(e) => setNewMember(prev => ({ ...prev, name: e.target.value }))}
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Email Address"
                  type="email"
                  value={newMember.email}
                  onChange={(e) => setNewMember(prev => ({ ...prev, email: e.target.value }))}
                  fullWidth
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  select
                  label="Role"
                  value={newMember.role}
                  onChange={(e) => setNewMember(prev => ({ ...prev, role: e.target.value }))}
                  fullWidth
                >
                  <MenuItem value="analyst">Analyst</MenuItem>
                  <MenuItem value="senior_analyst">Senior Analyst</MenuItem>
                  <MenuItem value="admin">Administrator</MenuItem>
                  <MenuItem value="viewer">Viewer</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAddMemberOpen(false)}>Cancel</Button>
            <Button onClick={handleAddMember} variant="contained">
              Send Invitation
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
              <strong>Settings Development Mode</strong>
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Settings: {loading ? 'Loading...' : 'Loaded'}
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Team Members: {teamMembers.length} total
            </Typography>
            <Typography variant="caption" display="block" color="text.secondary">
              Active Tab: {tabs[activeTab]?.label}
            </Typography>
          </Paper>
        )}
      </Container>
    </Box>
  );
};

export default Settings;