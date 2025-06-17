import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
  LinearProgress,
  Pagination,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
  Description as FileIcon,
  PlayArrow as ProcessIcon,
} from '@mui/icons-material';
import { fileAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { formatDistanceToNow } from 'date-fns';

const FileManager = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedFile, setSelectedFile] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [processingFiles, setProcessingFiles] = useState(new Set());

  const pageSize = 10;

  const loadFiles = async (pageNum = 1) => {
    try {
      setLoading(true);
      const response = await fileAPI.getFiles(pageNum, pageSize);
      
      // Ensure response has the expected structure
      const files = Array.isArray(response?.files) ? response.files : [];
      const totalCount = response?.total_count || 0;
      
      // Sanitize files data to prevent undefined field errors
      const sanitizedFiles = files.map(file => ({
        ...file,
        file_type: file.file_type || file.file_extension || 'unknown',
        processing_status: file.processing_status || 'pending',
        original_filename: file.original_filename || file.filename || 'Unknown',
        file_size: file.file_size || 0,
        upload_date: file.upload_date || file.upload_timestamp || file.created_at || new Date().toISOString(),
        progress_percentage: file.progress_percentage || 0,
        id: file.id || `file-${Date.now()}-${Math.random()}`
      }));
      
      setFiles(sanitizedFiles);
      setTotalPages(Math.ceil(totalCount / pageSize));
      setPage(pageNum);
    } catch (error) {
      toast.error('Failed to load files');
      console.error('Error loading files:', error);
      // Set empty array on error to prevent undefined issues
      setFiles([]);
    } finally {
      setLoading(false);
    }
  };

  const checkProcessingStatus = async (fileId) => {
    try {
      const status = await fileAPI.getProcessingStatus(fileId);
      setFiles(prev => prev.map(file => 
        file.id === fileId 
          ? { 
              ...file, 
              processing_status: status.processing_status,
              progress_percentage: status.progress_percentage 
            }
          : file
      ));
      
      if (status.processing_status === 'processing') {
        setProcessingFiles(prev => new Set(prev.add(fileId)));
      } else {
        setProcessingFiles(prev => {
          const newSet = new Set(prev);
          newSet.delete(fileId);
          return newSet;
        });
      }
    } catch (error) {
      console.error('Error checking processing status:', error);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  // Poll processing status for files that are still processing
  useEffect(() => {
    const interval = setInterval(() => {
      files.forEach(file => {
        if (file.processing_status === 'processing' || file.processing_status === 'pending') {
          checkProcessingStatus(file.id);
        }
      });
    }, 5000); // Check every 5 seconds

    return () => clearInterval(interval);
  }, [files]);

  const handleDownload = async (file) => {
    try {
      const response = await fileAPI.downloadFile(file.id);
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.original_filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('File downloaded successfully');
    } catch (error) {
      toast.error('Download failed');
      console.error('Download error:', error);
    }
  };

  const handleDelete = async () => {
    if (!selectedFile) return;
    
    try {
      await fileAPI.deleteFile(selectedFile.id);
      setFiles(prev => prev.filter(f => f.id !== selectedFile.id));
      setDeleteDialogOpen(false);
      setSelectedFile(null);
      toast.success('File deleted successfully');
    } catch (error) {
      toast.error('Delete failed');
      console.error('Delete error:', error);
    }
  };

  const handleProcessFile = async (file) => {
    try {
      toast.loading(`Processing ${file.original_filename}...`);
      
      // Update UI immediately
      setFiles(prev => prev.map(f => 
        f.id === file.id 
          ? { ...f, processing_status: 'processing', progress_percentage: 0 }
          : f
      ));
      
      const result = await fileAPI.processFile(file.id);
      
      // Update with result
      setFiles(prev => prev.map(f => 
        f.id === file.id 
          ? { 
              ...f, 
              processing_status: result.processing_status,
              progress_percentage: result.progress_percentage || 100,
              processing_time: result.processing_time
            }
          : f
      ));
      
      toast.dismiss();
      toast.success(`File ${file.original_filename} processed successfully!`);
    } catch (error) {
      toast.dismiss();
      toast.error(`Processing failed for ${file.original_filename}`);
      console.error('Processing error:', error);
      
      // Reset status on error
      setFiles(prev => prev.map(f => 
        f.id === file.id 
          ? { ...f, processing_status: 'pending', progress_percentage: 0 }
          : f
      ));
    }
  };

  const handleViewFile = async (file) => {
    try {
      const fileInfo = await fileAPI.getFileInfo(file.id);
      
      // Sanitize the file info to prevent undefined field errors
      const sanitizedFileInfo = {
        ...fileInfo,
        file_type: fileInfo.file_type || fileInfo.file_extension || 'unknown',
        processing_status: fileInfo.processing_status || 'pending',
        original_filename: fileInfo.original_filename || fileInfo.filename || 'Unknown',
        file_size: fileInfo.file_size || 0,
        upload_date: fileInfo.upload_date || fileInfo.upload_timestamp || fileInfo.created_at || new Date().toISOString(),
        progress_percentage: fileInfo.progress_percentage || 0
      };
      
      setSelectedFile(sanitizedFileInfo);
      setViewDialogOpen(true);
    } catch (error) {
      toast.error('Failed to load file details');
      console.error('Error loading file details:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'processing':
        return 'primary';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileTypeIcon = (fileType) => {
    return <FileIcon />;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          File Manager
        </Typography>
        <Button
          startIcon={<RefreshIcon />}
          onClick={() => loadFiles(page)}
          variant="outlined"
        >
          Refresh
        </Button>
      </Box>

      {files.length === 0 ? (
        <Alert severity="info">
          No files uploaded yet. Use the upload section to add files.
        </Alert>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>File</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell>Uploaded</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Array.isArray(files) && files.length > 0 ? files.map((file) => (
                  <TableRow key={file.id || `file-${Math.random()}`}>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getFileTypeIcon(file.file_type)}
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {file.original_filename || 'Unknown'}
                          </Typography>
                          {file.processing_time && (
                            <Typography variant="caption" color="text.secondary">
                              Processed in {file.processing_time.toFixed(2)}s
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={(file.file_type || file.file_extension || 'unknown').toUpperCase()} size="small" />
                    </TableCell>
                    <TableCell>{formatFileSize(file.file_size)}</TableCell>
                    <TableCell>
                      <Chip 
                        label={(file.processing_status || 'pending').charAt(0).toUpperCase() + (file.processing_status || 'pending').slice(1)}
                        color={getStatusColor(file.processing_status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {file.processing_status === 'processing' || file.processing_status === 'pending' ? (
                        <Box display="flex" alignItems="center" gap={1}>
                          <LinearProgress 
                            variant="determinate" 
                            value={file.progress_percentage || 0} 
                            sx={{ flexGrow: 1, mr: 1 }}
                          />
                          <Typography variant="caption">
                            {file.progress_percentage || 0}%
                          </Typography>
                        </Box>
                      ) : file.processing_status === 'completed' ? (
                        <Typography variant="caption" color="success.main">
                          Complete
                        </Typography>
                      ) : file.processing_status === 'failed' ? (
                        <Typography variant="caption" color="error.main">
                          Failed
                        </Typography>
                      ) : null}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">
                        {file.upload_date ? formatDistanceToNow(new Date(file.upload_date), { addSuffix: true }) : 'Unknown'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Tooltip title="View Details">
                          <IconButton 
                            size="small" 
                            onClick={() => handleViewFile(file)}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        
                        {(file.processing_status === 'pending' || file.processing_status === 'failed') && (
                          <Tooltip title="Process File">
                            <IconButton 
                              size="small" 
                              color="primary"
                              onClick={() => handleProcessFile(file)}
                              disabled={file.processing_status === 'processing'}
                            >
                              <ProcessIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        {file.processing_status === 'completed' && (
                          <Tooltip title="Download">
                            <IconButton 
                              size="small" 
                              onClick={() => handleDownload(file)}
                            >
                              <DownloadIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        
                        <Tooltip title="Delete">
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => {
                              setSelectedFile(file);
                              setDeleteDialogOpen(true);
                            }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                        No files found
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" mt={3}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(_, newPage) => loadFiles(newPage)}
                color="primary"
              />
            </Box>
          )}
        </>
      )}

      {/* View File Dialog */}
      <Dialog 
        open={viewDialogOpen} 
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>File Details</DialogTitle>
        <DialogContent>
          {selectedFile && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {selectedFile.original_filename}
              </Typography>
              <Box display="grid" gridTemplateColumns="1fr 1fr" gap={2} mb={3}>
                <Box>
                  <Typography variant="caption" color="text.secondary">File Type</Typography>
                  <Typography variant="body2">{(selectedFile.file_type || selectedFile.file_extension || 'unknown').toUpperCase()}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">File Size</Typography>
                  <Typography variant="body2">{formatFileSize(selectedFile.file_size)}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">Status</Typography>
                  <Chip 
                    label={(selectedFile.processing_status || 'pending').charAt(0).toUpperCase() + (selectedFile.processing_status || 'pending').slice(1)}
                    color={getStatusColor(selectedFile.processing_status)}
                    size="small"
                  />
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">Uploaded</Typography>
                  <Typography variant="body2">
                    {selectedFile.upload_date ? formatDistanceToNow(new Date(selectedFile.upload_date), { addSuffix: true }) : 'Unknown'}
                  </Typography>
                </Box>
              </Box>
              
              {selectedFile.extracted_text && (
                <Box>
                  <Typography variant="h6" gutterBottom>Extracted Text</Typography>
                  <Paper 
                    sx={{ 
                      p: 2, 
                      maxHeight: 300, 
                      overflow: 'auto', 
                      backgroundColor: 'grey.50' 
                    }}
                  >
                    <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                      {selectedFile.extracted_text}
                    </Typography>
                  </Paper>
                </Box>
              )}
              
              {selectedFile.error_message && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  <Typography variant="body2">{selectedFile.error_message}</Typography>
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog 
        open={deleteDialogOpen} 
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{selectedFile?.original_filename}"? 
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error">Delete</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FileManager; 