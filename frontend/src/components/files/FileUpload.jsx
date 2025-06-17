import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  IconButton,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Button,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  InsertDriveFile as FileIcon,
} from '@mui/icons-material';
import { fileAPI } from '../../services/api';
import toast from 'react-hot-toast';

const SUPPORTED_FILE_TYPES = [
  '.pdf', '.docx', '.doc', '.xlsx', '.xls', 
  '.jpg', '.jpeg', '.png', '.tiff', '.tif'
];

const MAX_FILE_SIZE = 16 * 1024 * 1024; // 16MB

const FileUpload = ({ onUploadComplete }) => {
  const [uploadingFiles, setUploadingFiles] = useState([]);
  const [completedFiles, setCompletedFiles] = useState([]);

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    rejectedFiles.forEach((rejection) => {
      const { file, errors } = rejection;
      errors.forEach((error) => {
        if (error.code === 'file-too-large') {
          toast.error(`File ${file.name} is too large. Maximum size is 16MB.`);
        } else if (error.code === 'file-invalid-type') {
          toast.error(`File ${file.name} has unsupported format.`);
        } else {
          toast.error(`Error with file ${file.name}: ${error.message}`);
        }
      });
    });

    // Process accepted files
    for (const file of acceptedFiles) {
      const fileUpload = {
        id: Date.now() + Math.random(),
        file,
        progress: 0,
        status: 'uploading',
        error: null,
      };

      setUploadingFiles(prev => [...prev, fileUpload]);

      try {
        const uploadResponse = await fileAPI.uploadFile(file, (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadingFiles(prev => 
            prev.map(f => 
              f.id === fileUpload.id 
                ? { ...f, progress } 
                : f
            )
          );
        });

        // Move to completed files
        setUploadingFiles(prev => prev.filter(f => f.id !== fileUpload.id));
        setCompletedFiles(prev => [...prev, {
          ...fileUpload,
          status: 'completed',
          uploadId: uploadResponse.id,
          uploadResponse,
        }]);

        toast.success(`File ${file.name} uploaded successfully!`);
        
        if (onUploadComplete) {
          onUploadComplete(uploadResponse);
        }

      } catch (error) {
        setUploadingFiles(prev => 
          prev.map(f => 
            f.id === fileUpload.id 
              ? { ...f, status: 'error', error: error.message } 
              : f
          )
        );
        toast.error(`Upload failed for ${file.name}`);
      }
    }
  }, [onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif'],
    },
    maxSize: MAX_FILE_SIZE,
    multiple: true,
  });

  const removeUploadingFile = (fileId) => {
    setUploadingFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const removeCompletedFile = (fileId) => {
    setCompletedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const getFileIcon = () => <FileIcon sx={{ fontSize: 48, color: 'text.secondary' }} />;

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon sx={{ color: 'success.main' }} />;
      case 'error':
        return <ErrorIcon sx={{ color: 'error.main' }} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'error':
        return 'error';
      case 'uploading':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Dropzone */}
      <Paper
        {...getRootProps()}
        sx={{
          border: 2,
          borderStyle: 'dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          p: 4,
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon 
          sx={{ 
            fontSize: 64, 
            color: isDragActive ? 'primary.main' : 'text.secondary',
            mb: 2 
          }} 
        />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop files here...' : 'Drag & drop files here'}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          or click to select files
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Supported formats: {SUPPORTED_FILE_TYPES.join(', ')}
        </Typography>
        <br />
        <Typography variant="caption" color="text.secondary">
          Maximum file size: 16MB
        </Typography>
      </Paper>

      {/* Uploading Files */}
      {uploadingFiles.length > 0 && (
        <Paper sx={{ mt: 2, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Uploading Files
          </Typography>
          <List>
            {uploadingFiles.map((fileUpload) => (
              <ListItem key={fileUpload.id}>
                {getFileIcon()}
                <ListItemText
                  primary={fileUpload.file.name}
                  secondary={
                    <Box>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Chip 
                          label={fileUpload.status} 
                          size="small" 
                          color={getStatusColor(fileUpload.status)}
                        />
                        {fileUpload.status === 'uploading' && (
                          <Typography variant="caption">
                            {fileUpload.progress}%
                          </Typography>
                        )}
                      </Box>
                      {fileUpload.status === 'uploading' && (
                        <LinearProgress 
                          variant="determinate" 
                          value={fileUpload.progress} 
                          sx={{ width: '100%' }}
                        />
                      )}
                      {fileUpload.error && (
                        <Alert severity="error" sx={{ mt: 1 }}>
                          {fileUpload.error}
                        </Alert>
                      )}
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  {getStatusIcon(fileUpload.status)}
                  <IconButton 
                    edge="end" 
                    onClick={() => removeUploadingFile(fileUpload.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Completed Files */}
      {completedFiles.length > 0 && (
        <Paper sx={{ mt: 2, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Upload Complete
          </Typography>
          <List>
            {completedFiles.map((fileUpload) => (
              <ListItem key={fileUpload.id}>
                {getFileIcon()}
                <ListItemText
                  primary={fileUpload.file.name}
                  secondary={
                    <Box>
                      <Chip 
                        label="Uploaded Successfully" 
                        size="small" 
                        color="success"
                      />
                      <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                        Processing started. You can view progress in the Files section.
                      </Typography>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                  <IconButton 
                    edge="end" 
                    onClick={() => removeCompletedFile(fileUpload.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Button 
              variant="outlined" 
              onClick={() => setCompletedFiles([])}
              size="small"
            >
              Clear All
            </Button>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default FileUpload; 