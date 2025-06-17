import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Assessment as ValidationIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  FilePresent as FilePresentIcon,
  PlayArrow as PlayArrowIcon
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { validationAPI, fileAPI } from '../services/api';
import ValidationInterface from '../components/ValidationInterface';
import useAuthStore from '../store/authStore';

const ValidationPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = useAuthStore();
  
  // State management
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [validationSession, setValidationSession] = useState(null);
  const [showCreateSession, setShowCreateSession] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [tradeRecords, setTradeRecords] = useState([]);
  const [loadingTradeRecords, setLoadingTradeRecords] = useState(false);
  
  // Session creation form data
  const [sessionData, setSessionData] = useState({
    session_name: '',
    file_id: '',
    trade_id: ''
  });

  // Check for existing session from URL params
  const sessionIdFromUrl = searchParams.get('session');
  const fileIdFromUrl = searchParams.get('file');

  const steps = [
    'File Upload',
    'Session Setup',
    'Validation Interface'
  ];

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    // Handle URL parameters for direct session access
    if (sessionIdFromUrl) {
      loadExistingSession(sessionIdFromUrl);
    } else if (fileIdFromUrl) {
      // Set file from URL and move to session setup
      setSelectedFile({ id: fileIdFromUrl });
      setCurrentStep(1);
    }
  }, [sessionIdFromUrl, fileIdFromUrl]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load uploaded files and trade records in parallel
      const [filesResponse] = await Promise.all([
        fileAPI.getFiles(1, 50),
        loadTradeRecords()
      ]);
      
      const processedFiles = filesResponse.files?.filter(
        file => file.processing_status === 'completed'
      ) || [];
      setUploadedFiles(processedFiles);
      
      // If no processed files, show upload step
      if (processedFiles.length === 0) {
        setCurrentStep(0);
        setShowFileUpload(true);
      } else {
        // If files exist, move to file selection
        setCurrentStep(1);
      }
      
    } catch (err) {
      setError('Failed to load initial data: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const loadTradeRecords = async () => {
    try {
      setLoadingTradeRecords(true);
      
      // Fetch trade records from the backend API
      const tradeRecords = await validationAPI.listTradeRecords(0, 50, 'active');
      setTradeRecords(tradeRecords);
      
    } catch (err) {
      console.warn('Failed to load trade records from API:', err);
      // Fall back to mock data if API fails
      const mockTradeRecords = [
        { trade_id: 'TR-2025-0420', counterparty: 'HSBC Bank', status: 'active' },
        { trade_id: 'TR-2025-0421', counterparty: 'Goldman Sachs', status: 'active' },
        { trade_id: 'TR-2025-0422', counterparty: 'JP Morgan', status: 'active' },
        { trade_id: 'TR-2025-0423', counterparty: 'Deutsche Bank', status: 'active' }
      ];
      setTradeRecords(mockTradeRecords);
    } finally {
      setLoadingTradeRecords(false);
    }
  };

  const loadExistingSession = async (sessionId) => {
    try {
      setLoading(true);
      const sessionResponse = await validationAPI.getValidationSession(sessionId);
      setValidationSession(sessionResponse);
      setCurrentStep(2); // Go directly to validation interface
    } catch (err) {
      setError('Failed to load validation session: ' + (err.response?.data?.detail || err.message));
      // Fall back to normal flow
      setCurrentStep(0);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setSessionData({ ...sessionData, file_id: file.id });
    setCurrentStep(1);
  };

  const validateTradeId = async (tradeId) => {
    try {
      // Validate trade ID exists in the system
      const tradeRecord = await validationAPI.getTradeRecord(tradeId);
      return tradeRecord;
    } catch (err) {
      if (err.response?.status === 404) {
        throw new Error(`Trade ID "${tradeId}" not found in the system`);
      }
      throw new Error('Failed to validate Trade ID: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleCreateSession = async () => {
    try {
      // Validate required fields
      if (!sessionData.session_name) {
        setError('Please enter a session name');
        return;
      }
      if (!sessionData.file_id) {
        setError('Please select a file');
        return;
      }
      if (!sessionData.trade_id) {
        setError('Trade ID is required for validation');
        return;
      }

      setLoading(true);
      setError(null);
      
      // First validate that the trade ID exists
      let tradeRecord;
      try {
        tradeRecord = await validateTradeId(sessionData.trade_id);
      } catch (validationError) {
        setError(validationError.message);
        return;
      }
      
      // Create validation session
      const sessionResponse = await validationAPI.createValidationSession({
        session_name: sessionData.session_name,
        file_id: sessionData.file_id,
        validation_type: 'enhanced_interface'
      });
      
      if (!sessionResponse || !sessionResponse.id) {
        throw new Error('Failed to create validation session - invalid response');
      }
      
      setValidationSession(sessionResponse);
      
      // Start the validation interface process with the trade ID
      try {
        await validationAPI.startValidationInterface(sessionResponse.id, {
          file_id: sessionData.file_id,
          trade_id: sessionData.trade_id
        });
      } catch (startError) {
        console.warn('Failed to start validation interface automatically:', startError);
        // Continue to interface anyway - user can start it manually
      }
      
      setShowCreateSession(false);
      setCurrentStep(2);
      
    } catch (err) {
      setError('Failed to create validation session: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = () => {
    navigate('/files?upload=true');
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <Container maxWidth="md" sx={{ py: 4 }}>
            <Card elevation={3}>
              <CardContent sx={{ textAlign: 'center', py: 6 }}>
                <UploadIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
                <Typography variant="h4" fontWeight="bold" gutterBottom>
                  Upload a Term Sheet
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
                  To access the validation interface, you need to upload and process a term sheet document first. 
                  The system will extract key information and prepare it for validation.
                </Typography>
                
                {uploadedFiles.length > 0 && (
                  <Alert severity="info" sx={{ mb: 3, textAlign: 'left' }}>
                    You have {uploadedFiles.length} processed file(s) available. 
                    You can select from existing files or upload a new one.
                  </Alert>
                )}

                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<UploadIcon />}
                    onClick={handleFileUpload}
                    sx={{
                      px: 4,
                      py: 1.5,
                      borderRadius: 3,
                      textTransform: 'none',
                      fontWeight: 'medium'
                    }}
                  >
                    Upload New File
                  </Button>
                  
                  {uploadedFiles.length > 0 && (
                    <Button
                      variant="outlined"
                      size="large"
                      startIcon={<FilePresentIcon />}
                      onClick={() => setCurrentStep(1)}
                      sx={{
                        px: 4,
                        py: 1.5,
                        borderRadius: 3,
                        textTransform: 'none',
                        fontWeight: 'medium'
                      }}
                    >
                      Select Existing File
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Container>
        );

      case 1:
        return (
          <Container maxWidth="lg" sx={{ py: 4 }}>
            <Grid container spacing={4}>
              {/* File Selection */}
              <Grid item xs={12} md={6}>
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      Select Term Sheet File
                    </Typography>
                    
                    {uploadedFiles.length === 0 ? (
                      <Alert severity="warning">
                        No processed files available. Please upload a file first.
                        <Button onClick={handleFileUpload} sx={{ ml: 2 }}>
                          Upload File
                        </Button>
                      </Alert>
                    ) : (
                      <List>
                        {uploadedFiles.map((file) => (
                          <ListItem
                            key={file.id}
                            button
                            selected={selectedFile?.id === file.id}
                            onClick={() => handleFileSelect(file)}
                            sx={{
                              borderRadius: 2,
                              mb: 1,
                              border: selectedFile?.id === file.id ? '2px solid #1976d2' : '1px solid #e0e0e0'
                            }}
                          >
                            <Box sx={{ flex: 1 }}>
                              <ListItemText
                                primary={file.filename}
                                secondary={`Uploaded: ${new Date(file.upload_date).toLocaleDateString()} | Size: ${(file.file_size / 1024 / 1024).toFixed(2)} MB`}
                              />
                              <Chip
                                icon={<CheckCircleIcon />}
                                label="Processed"
                                size="small"
                                sx={{ bgcolor: '#4caf50', color: 'white' }}
                              />
                            </Box>
                          </ListItem>
                        ))}
                      </List>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Session Setup */}
              <Grid item xs={12} md={6}>
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      Session Configuration
                    </Typography>
                    
                    <TextField
                      label="Session Name"
                      fullWidth
                      required
                      value={sessionData.session_name}
                      onChange={(e) => setSessionData({ ...sessionData, session_name: e.target.value })}
                      sx={{ mb: 3 }}
                      placeholder="e.g., HSBC Trade Validation - Jan 2025"
                      error={!sessionData.session_name}
                      helperText={!sessionData.session_name ? "Session name is required" : ""}
                    />

                    <FormControl fullWidth sx={{ mb: 3 }} required error={!sessionData.trade_id}>
                      <InputLabel>Trade ID *</InputLabel>
                      <Select
                        value={sessionData.trade_id}
                        onChange={(e) => setSessionData({ ...sessionData, trade_id: e.target.value })}
                        label="Trade ID *"
                      >
                        <MenuItem value="">
                          <em>Select a Trade ID</em>
                        </MenuItem>
                        {loadingTradeRecords ? (
                          <MenuItem disabled>
                            <CircularProgress size={20} sx={{ mr: 1 }} />
                            Loading trade records...
                          </MenuItem>
                        ) : (
                          tradeRecords.map((trade) => (
                            <MenuItem key={trade.trade_id} value={trade.trade_id}>
                              {trade.trade_id} - {trade.counterparty}
                            </MenuItem>
                          ))
                        )}
                      </Select>
                      {!sessionData.trade_id && (
                        <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                          Trade ID is required as it serves as the primary key for validation
                        </Typography>
                      )}
                    </FormControl>

                    {sessionData.trade_id && (
                      <Alert severity="info" sx={{ mb: 3 }}>
                        <Typography variant="body2">
                          <strong>Selected Trade ID:</strong> {sessionData.trade_id}
                          <br />
                          This will be used as the primary key for validation against the term sheet data.
                        </Typography>
                      </Alert>
                    )}

                    <Button
                      variant="contained"
                      fullWidth
                      size="large"
                      startIcon={<PlayArrowIcon />}
                      onClick={handleCreateSession}
                      disabled={!selectedFile || !sessionData.session_name || !sessionData.trade_id || loading}
                      sx={{
                        py: 1.5,
                        borderRadius: 3,
                        textTransform: 'none',
                        fontWeight: 'medium'
                      }}
                    >
                      {loading ? (
                        <>
                          <CircularProgress size={20} sx={{ mr: 1 }} />
                          Creating Session...
                        </>
                      ) : (
                        'Start Validation'
                      )}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Container>
        );

      case 2:
        return validationSession ? (
          <ValidationInterface 
            sessionId={validationSession.id} 
            tradeId={sessionData.trade_id}
          />
        ) : (
          <Container maxWidth="md" sx={{ py: 4 }}>
            <Alert severity="error">
              Validation session not found. Please start a new session.
              <Button onClick={() => setCurrentStep(0)} sx={{ ml: 2 }}>
                Start Over
              </Button>
            </Alert>
          </Container>
        );

      default:
        return null;
    }
  };

  if (loading && currentStep !== 2) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} sx={{ mb: 2 }} />
        <Typography variant="h6">Loading validation system...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      {/* Header - only show for steps 0 and 1 */}
      {currentStep < 2 && (
        <Paper elevation={2} sx={{ bgcolor: 'white' }}>
          <Container maxWidth="xl">
            <Box sx={{ py: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 4 }}>
                <Box>
                  <Typography variant="h3" fontWeight="bold" color="text.primary" gutterBottom>
                    Enhanced Validation Interface
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    AI-powered term sheet validation with comprehensive analysis
                  </Typography>
                </Box>
                <Chip
                  label="Phase 3"
                  sx={{
                    bgcolor: '#e1bee7',
                    color: '#6a1b9a',
                    fontWeight: 'medium',
                    fontSize: '1rem',
                    px: 2,
                    py: 1
                  }}
                />
              </Box>

              {/* Stepper */}
              <Stepper activeStep={currentStep} alternativeLabel>
                {steps.map((label, index) => (
                  <Step key={label}>
                    <StepLabel
                      StepIconProps={{
                        sx: {
                          color: index <= currentStep ? '#1976d2' : '#9e9e9e',
                          '&.Mui-active': { color: '#1976d2' },
                          '&.Mui-completed': { color: '#4caf50' }
                        }
                      }}
                    >
                      {label}
                    </StepLabel>
                  </Step>
                ))}
              </Stepper>
            </Box>
          </Container>
        </Paper>
      )}

      {/* Error Display */}
      {error && currentStep < 2 && (
        <Container maxWidth="xl" sx={{ pt: 2 }}>
          <Alert 
            severity="error" 
            onClose={() => setError(null)}
            sx={{ mb: 2 }}
          >
            {error}
          </Alert>
        </Container>
      )}

      {/* Step Content */}
      {renderStepContent()}
    </Box>
  );
};

export default ValidationPage; 