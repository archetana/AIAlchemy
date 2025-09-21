/**
 * Files List Component
 * Display and manage uploaded files for the application
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Tooltip,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from '@mui/material';
import {
  InsertDriveFile as FileIcon,
  PictureAsPdf as PdfIcon,
  TableChart as ExcelIcon,
  Description as WordIcon,
  Image as ImageIcon,
  VideoFile as VideoIcon,
  AudioFile as AudioIcon,
  Archive as ArchiveIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  CloudUpload as UploadIcon,
} from '@mui/icons-material';

const FilesList = ({ files, applicationId, onFilesUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState(null);

  const getFileIcon = (mimeType) => {
    if (!mimeType) return <FileIcon />;
    
    if (mimeType.includes('pdf')) return <PdfIcon sx={{ color: '#ef4444' }} />;
    if (mimeType.includes('sheet') || mimeType.includes('excel')) return <ExcelIcon sx={{ color: '#10b981' }} />;
    if (mimeType.includes('document') || mimeType.includes('word')) return <WordIcon sx={{ color: '#3b82f6' }} />;
    if (mimeType.includes('image')) return <ImageIcon sx={{ color: '#8b5cf6' }} />;
    if (mimeType.includes('video')) return <VideoIcon sx={{ color: '#f59e0b' }} />;
    if (mimeType.includes('audio')) return <AudioIcon sx={{ color: '#06b6d4' }} />;
    if (mimeType.includes('zip') || mimeType.includes('archive')) return <ArchiveIcon sx={{ color: '#6b7280' }} />;
    
    return <FileIcon />;
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown size';
    
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getFileTypeChip = (fileType) => {
    const typeColors = {
      pitch_deck: { color: '#8b5cf6', label: 'Pitch Deck' },
      financial: { color: '#10b981', label: 'Financial' },
      legal: { color: '#ef4444', label: 'Legal' },
      technical: { color: '#3b82f6', label: 'Technical' },
      market_research: { color: '#f59e0b', label: 'Market Research' },
      team: { color: '#06b6d4', label: 'Team' },
      other: { color: '#6b7280', label: 'Other' },
    };

    const type = typeColors[fileType] || typeColors.other;
    
    return (
      <Chip
        size="small"
        label={type.label}
        sx={{
          backgroundColor: `${type.color}20`,
          color: type.color,
          fontSize: '0.7rem',
          height: 20,
        }}
      />
    );
  };

  const handleDownload = async (fileId) => {
    try {
      setLoading(true);
      // Simulate download - in real app would call API
      console.log('Downloading file:', fileId);
      // const response = await uploadsApi.downloadFile(fileId);
      // Handle download...
    } catch (error) {
      console.error('Download error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleView = (fileId) => {
    // Open file in new tab for viewing
    window.open(`/api/uploads/files/${fileId}`, '_blank');
  };

  const handleDeleteClick = (file) => {
    setFileToDelete(file);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      setLoading(true);
      // In real app would call API to delete
      console.log('Deleting file:', fileToDelete.id);
      // await uploadsApi.deleteFile(fileToDelete.id);
      
      // Update local state
      const updatedFiles = files.filter(f => f.id !== fileToDelete.id);
      onFilesUpdate(updatedFiles);
      
    } catch (error) {
      console.error('Delete error:', error);
    } finally {
      setLoading(false);
      setDeleteDialogOpen(false);
      setFileToDelete(null);
    }
  };

  const handleUpload = () => {
    // TODO: Implement file upload functionality
    console.log('Upload new files for application:', applicationId);
  };

  return (
    <>
      <Card elevation={2}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" fontWeight={600}>
              Uploaded Files
            </Typography>
            <Button
              size="small"
              startIcon={<UploadIcon />}
              onClick={handleUpload}
              variant="outlined"
            >
              Upload
            </Button>
          </Box>

          {files.length === 0 ? (
            <Alert severity="info" icon={<FileIcon />}>
              <Typography variant="body2">
                No files uploaded yet. Click "Upload" to add documents.
              </Typography>
            </Alert>
          ) : (
            <List dense sx={{ py: 0 }}>
              {files.map((file, index) => (
                <ListItem
                  key={file.id}
                  sx={{
                    px: 0,
                    py: 1,
                    borderBottom: index < files.length - 1 ? '1px solid #f3f4f6' : 'none',
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    {getFileIcon(file.mime_type)}
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={
                      <Box>
                        <Typography variant="body2" fontWeight={500} noWrap>
                          {file.original_filename || file.filename}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                          {file.file_type && getFileTypeChip(file.file_type)}
                          <Typography variant="caption" color="text.secondary">
                            {formatFileSize(file.file_size)}
                          </Typography>
                        </Box>
                      </Box>
                    }
                    secondary={
                      file.uploaded_at && (
                        <Typography variant="caption" color="text.secondary">
                          Uploaded {new Date(file.uploaded_at).toLocaleDateString()}
                        </Typography>
                      )
                    }
                  />
                  
                  <ListItemSecondaryAction>
                    <Box display="flex" gap={0.5}>
                      <Tooltip title="View File">
                        <IconButton 
                          size="small" 
                          onClick={() => handleView(file.id)}
                        >
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Download">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDownload(file.id)}
                          disabled={loading}
                        >
                          {loading ? (
                            <CircularProgress size={16} />
                          ) : (
                            <DownloadIcon fontSize="small" />
                          )}
                        </IconButton>
                      </Tooltip>
                      
                      <Tooltip title="Delete">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteClick(file)}
                          sx={{ color: 'error.main' }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}

          {/* File Statistics */}
          {files.length > 0 && (
            <Box mt={2} pt={2} sx={{ borderTop: '1px solid #f3f4f6' }}>
              <Typography variant="caption" color="text.secondary">
                {files.length} file{files.length !== 1 ? 's' : ''} • Total size: {
                  formatFileSize(files.reduce((sum, file) => sum + (file.file_size || 0), 0))
                }
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Delete File</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Are you sure you want to delete this file?
          </Typography>
          {fileToDelete && (
            <Box sx={{ 
              p: 2, 
              backgroundColor: '#f8fafc', 
              borderRadius: 1,
              border: '1px solid #e5e7eb'
            }}>
              <Typography variant="body2" fontWeight={500}>
                {fileToDelete.original_filename || fileToDelete.filename}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatFileSize(fileToDelete.file_size)} • {
                  fileToDelete.uploaded_at ? 
                    new Date(fileToDelete.uploaded_at).toLocaleDateString() : 
                    'Unknown date'
                }
              </Typography>
            </Box>
          )}
          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="body2">
              This action cannot be undone. The file will be permanently deleted.
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleDeleteConfirm} 
            color="error" 
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Deleting...' : 'Delete File'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default FilesList;