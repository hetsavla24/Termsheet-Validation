import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Tabs,
  Tab,
  Typography,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Folder as FolderIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import FileUpload from './FileUpload';
import FileManager from './FileManager';

const FilesPage = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [refreshManager, setRefreshManager] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleUploadComplete = (uploadResponse) => {
    // Refresh the file manager when a new file is uploaded
    setRefreshManager(prev => prev + 1);
    // Switch to file manager tab to see the uploaded file
    setActiveTab(1);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 3 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link underline="hover" color="inherit" href="/dashboard" display="flex" alignItems="center">
          <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Dashboard
        </Link>
        <Typography color="text.primary" display="flex" alignItems="center">
          <FolderIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Files
        </Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          File Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload and manage your termsheet documents. Supported formats include PDF, Word documents, 
          Excel files, and images. All files are processed automatically with OCR and text extraction.
        </Typography>
      </Box>

      {/* Main Content */}
      <Paper sx={{ mt: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab 
            icon={<CloudUploadIcon />} 
            label="Upload Files" 
            iconPosition="start"
          />
          <Tab 
            icon={<FolderIcon />} 
            label="Manage Files" 
            iconPosition="start"
          />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Upload New Files
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Drag and drop files or click to browse. Files will be automatically processed to extract text content.
              </Typography>
              <FileUpload onUploadComplete={handleUploadComplete} />
            </Box>
          )}

          {activeTab === 1 && (
            <Box>
              <FileManager key={refreshManager} />
            </Box>
          )}
        </Box>
      </Paper>

      {/* Features Info */}
      <Paper sx={{ mt: 3, p: 3, backgroundColor: 'primary.50' }}>
        <Typography variant="h6" gutterBottom>
          Phase 2 Features
        </Typography>
        <Box display="grid" gridTemplateColumns={{ xs: '1fr', md: 'repeat(2, 1fr)' }} gap={2}>
          <Box>
            <Typography variant="subtitle2" color="primary.main" gutterBottom>
              ✅ Drag & Drop Upload
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Modern file upload interface with progress tracking and validation.
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" color="primary.main" gutterBottom>
              ✅ Multi-format Support
            </Typography>
            <Typography variant="body2" color="text.secondary">
              PDF, Word, Excel, and image files with automatic format detection.
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" color="primary.main" gutterBottom>
              ✅ OCR Processing
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Automatic text extraction from scanned documents and images.
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2" color="primary.main" gutterBottom>
              ✅ Real-time Feedback
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Live progress updates and processing status for all uploaded files.
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default FilesPage; 