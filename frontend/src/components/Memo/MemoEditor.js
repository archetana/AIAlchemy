/**
 * Memo Editor Component
 * Rich text editor for creating and editing investment memos
 */

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  MenuItem,
  Chip,
  Divider,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

const MemoEditor = ({ 
  content, 
  recommendation, 
  editMode, 
  memo, 
  onContentChange, 
  onRecommendationChange,
  saving 
}) => {
  
  const recommendationOptions = [
    { value: 'strongly_recommend', label: 'Strongly Recommend', color: '#059669' },
    { value: 'recommend', label: 'Recommend', color: '#10b981' },
    { value: 'neutral', label: 'Neutral', color: '#f59e0b' },
    { value: 'not_recommend', label: 'Not Recommend', color: '#ef4444' },
    { value: 'strongly_not_recommend', label: 'Strongly Not Recommend', color: '#dc2626' },
  ];

  const getRecommendationColor = (value) => {
    const option = recommendationOptions.find(opt => opt.value === value);
    return option?.color || '#6b7280';
  };

  const getRecommendationLabel = (value) => {
    const option = recommendationOptions.find(opt => opt.value === value);
    return option?.label || value;
  };

  const memoTemplate = `# Investment Analysis: [Company Name]

## Executive Summary
[Brief overview of the investment opportunity, key strengths, and recommendation]

## Company Overview
### Business Model
[Description of how the company makes money]

### Market Opportunity
[Market size, growth potential, and positioning]

### Competitive Landscape
[Key competitors and differentiation]

## Financial Analysis
### Revenue Model
[Current revenue streams and projections]

### Key Metrics
[Important KPIs and financial health indicators]

### Funding Requirements
[Use of funds and projected returns]

## Team Assessment
### Leadership Team
[Backgrounds and track records of key executives]

### Advisory Board
[Notable advisors and their contributions]

## Technology & Product
### Product Overview
[Description of core product/service]

### Technology Stack
[Technical architecture and IP considerations]

### Development Roadmap
[Future product plans and milestones]

## Market Analysis
### Target Market
[Customer segments and addressable market]

### Go-to-Market Strategy
[Sales and marketing approach]

### Traction & Validation
[Customer testimonials, partnerships, and growth metrics]

## Risk Assessment
### Market Risks
[Competition, market timing, and adoption risks]

### Execution Risks
[Team, technology, and operational challenges]

### Financial Risks
[Funding, burn rate, and profitability concerns]

## Investment Terms
### Valuation
[Pre-money and post-money valuations]

### Investment Structure
[Equity percentage, liquidation preferences, board seats]

### Exit Strategy
[Potential acquirers and timeline to exit]

## Recommendation
[Final investment recommendation with supporting rationale]

## Appendices
### Financial Projections
### Market Research
### Technical Due Diligence
### Legal Review`;

  return (
    <Card elevation={2}>
      <CardContent sx={{ p: 0 }}>
        {/* Header */}
        <Box sx={{ p: 3, borderBottom: '1px solid #e5e7eb' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" fontWeight={600}>
              Investment Memo
            </Typography>
            
            {memo && (
              <Box display="flex" alignItems="center" gap={1}>
                {memo.is_draft && (
                  <Chip 
                    size="small" 
                    label="Draft" 
                    color="warning"
                    variant="outlined"
                  />
                )}
                {memo.approved && (
                  <Chip 
                    size="small" 
                    label="Approved" 
                    color="success"
                    icon={<CheckCircleIcon />}
                  />
                )}
                {memo.review_date && (
                  <Chip 
                    size="small" 
                    label={`Review: ${new Date(memo.review_date).toLocaleDateString()}`}
                    color="primary"
                    variant="outlined"
                    icon={<ScheduleIcon />}
                  />
                )}
              </Box>
            )}
          </Box>

          {/* Memo Info */}
          {memo && (
            <Box display="flex" gap={2} flexWrap="wrap">
              <Typography variant="caption" color="text.secondary">
                Created: {new Date(memo.created_at).toLocaleDateString()}
              </Typography>
              {memo.updated_at && (
                <Typography variant="caption" color="text.secondary">
                  Updated: {new Date(memo.updated_at).toLocaleDateString()}
                </Typography>
              )}
              {memo.author_name && (
                <Typography variant="caption" color="text.secondary">
                  Author: {memo.author_name}
                </Typography>
              )}
            </Box>
          )}
        </Box>

        {/* Saving Progress */}
        {saving && <LinearProgress />}

        {/* Content Editor */}
        <Box sx={{ p: 3 }}>
          {editMode ? (
            <Box display="flex" flexDirection="column" gap={3}>
              {/* Recommendation Selector */}
              <TextField
                select
                label="Investment Recommendation"
                value={recommendation}
                onChange={(e) => onRecommendationChange(e.target.value)}
                fullWidth
                size="small"
                helperText="Your overall investment recommendation"
              >
                {recommendationOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: option.color,
                        }}
                      />
                      {option.label}
                    </Box>
                  </MenuItem>
                ))}
              </TextField>

              {/* Memo Content Editor */}
              <TextField
                label="Memo Content"
                multiline
                rows={25}
                value={content}
                onChange={(e) => onContentChange(e.target.value)}
                placeholder={content || memoTemplate}
                fullWidth
                sx={{
                  '& .MuiInputBase-root': {
                    fontFamily: 'Monaco, Consolas, "Liberation Mono", monospace',
                    fontSize: '0.875rem',
                    lineHeight: 1.6,
                  }
                }}
                helperText="Use Markdown formatting for better structure. Template provided as placeholder."
              />
            </Box>
          ) : (
            <Box>
              {/* Recommendation Display */}
              {recommendation && (
                <Box mb={3}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    Investment Recommendation
                  </Typography>
                  <Chip
                    label={getRecommendationLabel(recommendation)}
                    sx={{
                      backgroundColor: `${getRecommendationColor(recommendation)}20`,
                      color: getRecommendationColor(recommendation),
                      fontWeight: 600,
                    }}
                  />
                </Box>
              )}

              <Divider sx={{ my: 2 }} />

              {/* Memo Content Display */}
              {content ? (
                <Box sx={{ 
                  '& h1, & h2, & h3, & h4, & h5, & h6': { 
                    fontWeight: 600, 
                    mt: 3, 
                    mb: 1,
                    color: 'text.primary'
                  },
                  '& h1': { fontSize: '1.5rem' },
                  '& h2': { fontSize: '1.25rem' },
                  '& h3': { fontSize: '1.125rem' },
                  '& p': { mb: 2, lineHeight: 1.7 },
                  '& ul, & ol': { pl: 3, mb: 2 },
                  '& li': { mb: 0.5 },
                  '& blockquote': { 
                    borderLeft: '4px solid #e5e7eb', 
                    pl: 2, 
                    ml: 0, 
                    fontStyle: 'italic',
                    color: 'text.secondary'
                  },
                  '& code': {
                    backgroundColor: '#f3f4f6',
                    padding: '2px 4px',
                    borderRadius: 1,
                    fontSize: '0.875rem',
                    fontFamily: 'Monaco, Consolas, monospace'
                  },
                  '& pre': {
                    backgroundColor: '#f8fafc',
                    p: 2,
                    borderRadius: 1,
                    overflow: 'auto',
                    border: '1px solid #e5e7eb'
                  }
                }}>
                  {/* Simple Markdown Rendering */}
                  <div dangerouslySetInnerHTML={{ 
                    __html: content
                      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
                      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
                      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
                      .replace(/^#### (.*$)/gm, '<h4>$1</h4>')
                      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                      .replace(/\*(.*?)\*/g, '<em>$1</em>')
                      .replace(/`(.*?)`/g, '<code>$1</code>')
                      .replace(/\n\n/g, '</p><p>')
                      .replace(/^(.*)$/gm, '<p>$1</p>')
                      .replace(/<p><h([1-6])>(.*?)<\/h[1-6]><\/p>/g, '<h$1>$2</h$1>')
                      .replace(/<p><\/p>/g, '')
                  }} />
                </Box>
              ) : (
                <Alert severity="info" icon={<AssignmentIcon />}>
                  <Typography variant="body2">
                    No memo content yet. Click "Edit Memo" to start writing your investment analysis.
                  </Typography>
                </Alert>
              )}
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default MemoEditor;