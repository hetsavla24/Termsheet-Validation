import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  LinearProgress,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  PlayArrow as PlayArrowIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { validationAPI, fileAPI } from '../api';

const ValidationDashboard = () => {
  const [sessions, setSessions] = useState([]);
  const [files, setFiles] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateSession, setShowCreateSession] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  
  const [sessionData, setSessionData] = useState({
    session_name: '',
    file_id: '',
    template_id: '',
    validation_type: 'standard'
  });

  const [sessionDetails, setSessionDetails] = useState({
    session: null,
    terms: [],
    results: [],
    summary: null
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sessionsRes, filesRes, templatesRes] = await Promise.all([
        validationAPI.getValidationSessions(),
        fileAPI.listFiles(),
        validationAPI.getTemplates()
      ]);
      
      setSessions(sessionsRes.data);
      setFiles(filesRes.data.files);
      setTemplates(templatesRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const createValidationSession = async (e) => {
    e.preventDefault();
    try {
      await validationAPI.createValidationSession(sessionData);
      setShowCreateSession(false);
      setSessionData({
        session_name: '',
        file_id: '',
        template_id: '',
        validation_type: 'standard'
      });
      loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create validation session');
    }
  };

  const loadSessionDetails = async (sessionId) => {
    try {
      const [sessionRes, termsRes, resultsRes, summaryRes] = await Promise.all([
        validationAPI.getValidationSession(sessionId),
        validationAPI.getSessionTerms(sessionId),
        validationAPI.getSessionResults(sessionId),
        validationAPI.getSessionSummary(sessionId)
      ]);

      setSessionDetails({
        session: sessionRes.data,
        terms: termsRes.data,
        results: resultsRes.data,
        summary: summaryRes.data
      });
      setSelectedSession(sessionId);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load session details');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'pending': 'warning',
      'processing': 'info',
      'completed': 'success',
      'failed': 'error'
    };
    return colors[status] || 'default';
  };

  const getValidationStatusColor = (status) => {
    const colors = {
      'valid': 'success',
      'invalid': 'error',
      'missing': 'warning',
      'warning': 'warning'
    };
    return colors[status] || 'default';
  };

  const getComplianceColor = (status) => {
    const colors = {
      'compliant': 'success',
      'partial_compliant': 'warning',
      'non_compliant': 'error'
    };
    return colors[status] || 'default';
  };

  const getComplianceIcon = (status) => {
    const icons = {
      'compliant': <CheckCircleIcon />,
      'partial_compliant': <WarningIcon />,
      'non_compliant': <ErrorIcon />
    };
    return icons[status] || <ScheduleIcon />;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" color="text.primary">
          Validation Dashboard
        </Typography>
        <Button
          variant="contained"
          startIcon={<PlayArrowIcon />}
          onClick={() => setShowCreateSession(true)}
          sx={{
            borderRadius: 2,
            textTransform: 'none',
            px: 3,
            py: 1.5,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)'
            }
          }}
        >
          Start Validation
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {/* Sessions Grid */}
      {!selectedSession ? (
        <Box>
          <Typography variant="h5" fontWeight="semibold" sx={{ mb: 3 }}>
            Recent Validation Sessions
          </Typography>
          <Grid container spacing={3}>
            {sessions.map((session) => (
              <Grid item xs={12} md={6} lg={4} key={session.id}>
                <Card
                  elevation={4}
                  sx={{
                    borderRadius: 3,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: 8
                    }
                  }}
                  onClick={() => loadSessionDetails(session.id)}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Typography variant="h6" fontWeight="bold" color="text.primary">
                        {session.session_name}
                      </Typography>
                      <Chip
                        label={session.status}
                        color={getStatusColor(session.status)}
                        size="small"
                        sx={{ fontWeight: 'medium' }}
                      />
                    </Box>

                    <Box sx={{ space: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          File:
                        </Typography>
                        <Typography 
                          variant="body2" 
                          color="text.primary"
                          sx={{ 
                            maxWidth: 150,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                          title={session.file_id}
                        >
                          {session.file_id.slice(0, 20)}...
                        </Typography>
                      </Box>
                      
                      {session.status === 'processing' && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                            Progress: {session.progress_percentage || 0}%
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={session.progress_percentage || 0}
                            sx={{
                              height: 8,
                              borderRadius: 4,
                              bgcolor: 'rgba(0,0,0,0.1)',
                              '& .MuiLinearProgress-bar': {
                                borderRadius: 4,
                                background: 'linear-gradient(135deg, #667eea, #764ba2)'
                              }
                            }}
                          />
                        </Box>
                      )}

                      {session.status === 'completed' && (
                        <>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2" color="text.secondary">
                              Terms:
                            </Typography>
                            <Typography variant="body2" color="text.primary">
                              {session.total_terms || 0}
                            </Typography>
                          </Box>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2" color="text.secondary">
                              Accuracy:
                            </Typography>
                            <Typography variant="body2" color="text.primary">
                              {session.accuracy_score ? `${(session.accuracy_score * 100).toFixed(1)}%` : 'N/A'}
                            </Typography>
                          </Box>
                        </>
                      )}

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Created:
                        </Typography>
                        <Typography variant="body2" color="text.primary">
                          {new Date(session.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {sessions.length === 0 && (
            <Paper elevation={2} sx={{ p: 8, textAlign: 'center', borderRadius: 3 }}>
              <AssessmentIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No validation sessions found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Start your first validation session to get started
              </Typography>
            </Paper>
          )}
        </Box>
      ) : (
        /* Session Details View */
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
            <IconButton
              onClick={() => setSelectedSession(null)}
              sx={{ mr: 2, color: 'primary.main' }}
            >
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h5" fontWeight="bold" sx={{ mr: 2 }}>
              {sessionDetails.session?.session_name}
            </Typography>
            <Chip
              label={sessionDetails.session?.status}
              color={getStatusColor(sessionDetails.session?.status)}
              icon={getComplianceIcon(sessionDetails.session?.status)}
              sx={{ fontWeight: 'medium' }}
            />
          </Box>

          {/* Summary Cards */}
          {sessionDetails.summary && (
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={4} sx={{ borderRadius: 3, textAlign: 'center' }}>
                  <CardContent>
                    <Typography variant="h3" fontWeight="bold" color="text.primary">
                      {sessionDetails.summary.total_terms}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Terms
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={4} sx={{ borderRadius: 3, textAlign: 'center' }}>
                  <CardContent>
                    <Typography variant="h3" fontWeight="bold" color="success.main">
                      {sessionDetails.summary.valid_terms}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Valid
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={4} sx={{ borderRadius: 3, textAlign: 'center' }}>
                  <CardContent>
                    <Typography variant="h3" fontWeight="bold" color="error.main">
                      {sessionDetails.summary.invalid_terms}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Invalid
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card elevation={4} sx={{ borderRadius: 3, textAlign: 'center' }}>
                  <CardContent>
                    <Typography variant="h3" fontWeight="bold" color="warning.main">
                      {sessionDetails.summary.missing_terms}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Missing
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Compliance Status */}
          {sessionDetails.summary && (
            <Paper elevation={4} sx={{ p: 4, borderRadius: 3, mb: 4 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h6" fontWeight="bold">
                  Compliance Status
                </Typography>
                <Chip
                  label={sessionDetails.summary.compliance_status.replace('_', ' ').toUpperCase()}
                  color={getComplianceColor(sessionDetails.summary.compliance_status)}
                  icon={getComplianceIcon(sessionDetails.summary.compliance_status)}
                  sx={{ fontWeight: 'medium' }}
                />
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Overall Accuracy</Typography>
                  <Typography variant="body2" fontWeight="medium">
                    {(sessionDetails.summary.overall_accuracy * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={sessionDetails.summary.overall_accuracy * 100}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    bgcolor: 'rgba(0,0,0,0.1)',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 4,
                      background: 'linear-gradient(135deg, #667eea, #764ba2)'
                    }
                  }}
                />
              </Box>
              
              {sessionDetails.summary.recommendations.length > 0 && (
                <Box>
                  <Typography variant="subtitle1" fontWeight="medium" sx={{ mb: 2 }}>
                    Recommendations:
                  </Typography>
                  <List dense>
                    {sessionDetails.summary.recommendations.map((rec, index) => (
                      <ListItem key={index} sx={{ py: 0.5 }}>
                        <ListItemText
                          primary={rec}
                          primaryTypographyProps={{
                            variant: 'body2',
                            color: 'text.secondary'
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Paper>
          )}

          {/* Validation Results */}
          <Paper elevation={4} sx={{ borderRadius: 3 }}>
            <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6" fontWeight="bold">
                Validation Results
              </Typography>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.50' }}>
                    <TableCell sx={{ fontWeight: 'bold', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                      Term
                    </TableCell>
                    <TableCell sx={{ fontWeight: 'bold', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                      Expected
                    </TableCell>
                    <TableCell sx={{ fontWeight: 'bold', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                      Extracted
                    </TableCell>
                    <TableCell sx={{ fontWeight: 'bold', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                      Status
                    </TableCell>
                    <TableCell sx={{ fontWeight: 'bold', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                      Score
                    </TableCell>
                    <TableCell sx={{ fontWeight: 'bold', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                      Method
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sessionDetails.results.map((result, index) => (
                    <TableRow 
                      key={index} 
                      sx={{ 
                        '&:hover': { bgcolor: 'grey.50' },
                        '&:nth-of-type(even)': { bgcolor: 'grey.25' }
                      }}
                    >
                      <TableCell sx={{ fontWeight: 'medium' }}>
                        {result.term_name}
                      </TableCell>
                      <TableCell sx={{ color: 'text.secondary' }}>
                        {result.expected_value || 'N/A'}
                      </TableCell>
                      <TableCell sx={{ color: 'text.secondary' }}>
                        {result.extracted_value || 'N/A'}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={result.validation_status}
                          color={getValidationStatusColor(result.validation_status)}
                          size="small"
                          sx={{ fontWeight: 'medium' }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: 'text.secondary' }}>
                        {result.match_score ? (result.match_score * 100).toFixed(1) + '%' : 'N/A'}
                      </TableCell>
                      <TableCell sx={{ color: 'text.secondary' }}>
                        {result.validation_method}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            {sessionDetails.results.length === 0 && (
              <Box sx={{ p: 6, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                  No validation results available
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>
      )}

      {/* Create Session Modal */}
      <Dialog
        open={showCreateSession}
        onClose={() => setShowCreateSession(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3 }
        }}
      >
        <DialogTitle>
          <Typography variant="h5" fontWeight="bold">
            Start New Validation
          </Typography>
        </DialogTitle>
        
        <form onSubmit={createValidationSession}>
          <DialogContent sx={{ pb: 2 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
              <TextField
                label="Session Name"
                variant="outlined"
                fullWidth
                required
                value={sessionData.session_name}
                onChange={(e) => setSessionData(prev => ({...prev, session_name: e.target.value}))}
                sx={{ borderRadius: 2 }}
              />

              <FormControl fullWidth required>
                <InputLabel>Select File</InputLabel>
                <Select
                  value={sessionData.file_id}
                  onChange={(e) => setSessionData(prev => ({...prev, file_id: e.target.value}))}
                  label="Select File"
                >
                  <MenuItem value="">
                    <em>Choose a file</em>
                  </MenuItem>
                  {files.filter(f => f.status === 'completed').map((file) => (
                    <MenuItem key={file.id} value={file.id}>
                      {file.filename}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Validation Template (Optional)</InputLabel>
                <Select
                  value={sessionData.template_id}
                  onChange={(e) => setSessionData(prev => ({...prev, template_id: e.target.value}))}
                  label="Validation Template (Optional)"
                >
                  <MenuItem value="">
                    <em>No template (analyze only)</em>
                  </MenuItem>
                  {templates.map((template) => (
                    <MenuItem key={template.id} value={template.id}>
                      {template.template_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Validation Type</InputLabel>
                <Select
                  value={sessionData.validation_type}
                  onChange={(e) => setSessionData(prev => ({...prev, validation_type: e.target.value}))}
                  label="Validation Type"
                >
                  <MenuItem value="standard">Standard Validation</MenuItem>
                  <MenuItem value="custom">Custom Rules</MenuItem>
                  <MenuItem value="comparison">Template Comparison</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </DialogContent>

          <DialogActions sx={{ p: 3, pt: 1 }}>
            <Button
              onClick={() => setShowCreateSession(false)}
              variant="outlined"
              sx={{ borderRadius: 2, textTransform: 'none' }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              sx={{
                borderRadius: 2,
                textTransform: 'none',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)'
                }
              }}
            >
              Start Validation
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
};

export default ValidationDashboard; 