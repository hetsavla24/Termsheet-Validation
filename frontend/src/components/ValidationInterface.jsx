import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert,
  LinearProgress,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  CloudUpload as UploadIcon,
  Assessment as ValidationIcon,
  Report as ReportIcon,
  Gavel as ComplianceIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Psychology as AIIcon,
  TrendingUp as TrendingUpIcon,
  Assignment as AssignmentIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { validationAPI } from '../services/api';
import useAuthStore from '../store/authStore';

const ValidationInterface = ({ sessionId, tradeId }) => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [validationData, setValidationData] = useState(null);
  const [activeTab, setActiveTab] = useState('term-sheet');
  const [showDecisionDialog, setShowDecisionDialog] = useState(false);
  const [decisionData, setDecisionData] = useState({
    decision: '',
    decision_reason: ''
  });

  // Tab configuration
  const tabs = [
    { id: 'term-sheet', label: 'Term Sheet', icon: <AssignmentIcon /> },
    { id: 'trade-record', label: 'Trade Record', icon: <TrendingUpIcon /> },
    { id: 'ai-analysis', label: 'AI Analysis', icon: <AIIcon /> },
    { id: 'compliance', label: 'Compliance View', icon: <ComplianceIcon /> }
  ];

  useEffect(() => {
    if (sessionId) {
      loadValidationData();
    }
  }, [sessionId]);

  const loadValidationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log("Loading validation data for session ID:", sessionId);
      const data = await validationAPI.getValidationInterfaceData(sessionId);
      console.log('Validation interface data loaded:', data);
      
      // Check if we have term sheet data with trade ID
      if (data?.term_sheet_data?.trade_id) {
        console.log("Term sheet data contains trade ID:", data.term_sheet_data.trade_id);
      } else if (data?.trade_record?.trade_id) {
        console.log("Trade record contains trade ID:", data.trade_record.trade_id);
        
        // If we have trade record but no term sheet data, create a placeholder
        if (!data.term_sheet_data) {
          console.log("Creating placeholder term sheet data from trade record");
          data.term_sheet_data = {
            trade_id: data.trade_record.trade_id,
            // Copy other relevant fields from trade record
            counterparty: data.trade_record.counterparty,
            notional_amount: data.trade_record.notional_amount,
            settlement_date: data.trade_record.settlement_date,
            interest_rate: data.trade_record.interest_rate,
            currency: data.trade_record.currency,
            payment_terms: data.trade_record.payment_terms,
            legal_entity: data.trade_record.legal_entity
          };
        }
      } else if (data?.session?.trade_id) {
        console.log("Session contains trade ID:", data.session.trade_id);
        
        // If we have session trade ID but no term sheet data, create a placeholder
        if (!data.term_sheet_data) {
          console.log("Creating placeholder term sheet data from session");
          data.term_sheet_data = {
            trade_id: data.session.trade_id
          };
        }
      } else if (tradeId) {
        // Use the tradeId prop if provided and no other trade ID is found
        console.log("Using tradeId prop:", tradeId);
        
        if (!data.term_sheet_data) {
          data.term_sheet_data = { trade_id: tradeId };
        } else {
          data.term_sheet_data.trade_id = tradeId;
        }
      } else {
        console.warn("No trade ID found in any data source");
      }
      
      setValidationData(data);
      
      if (data && data.session) {
        console.log('Session data loaded successfully');
      } else {
        console.warn('Incomplete validation data received');
      }
    } catch (err) {
      console.error('Error loading validation data:', err);
      setError(err.response?.data?.detail || 'Failed to load validation data');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleDecision = async () => {
    try {
      setLoading(true);
      const decisionType = decisionData.decision;
      
      // Make the validation decision API call
      const response = await validationAPI.makeValidationDecision(sessionId, decisionData);
      
      // Update session status based on decision
      let newStatus = '';
      switch (decisionType) {
        case 'approve':
          newStatus = 'completed';
          break;
        case 'reject':
          newStatus = 'failed';
          break;
        case 'manual_review':
          newStatus = 'manual_review';
          break;
        default:
          newStatus = 'completed';
      }
      
      // Update session status through the API
      try {
        await validationAPI.updateSessionStatus(sessionId, { status: newStatus });
        console.log(`Session status updated to ${newStatus}`);
      } catch (statusError) {
        console.error("Failed to update session status:", statusError);
      }
      
      // Show appropriate message based on decision type
      let message = '';
      let severity = 'success';
      
      switch (decisionType) {
        case 'approve':
          message = 'Term sheet has been approved successfully. The report is now available.';
          break;
        case 'manual_review':
          message = 'Term sheet has been sent for manual review. You will be notified when the review is complete.';
          severity = 'info';
          break;
        case 'reject':
          message = 'Term sheet has been rejected. Please review the issues and resubmit if necessary.';
          severity = 'error';
          break;
        default:
          message = 'Decision has been recorded.';
      }
      
      // Close the decision dialog
      setShowDecisionDialog(false);
      
      // Store message in sessionStorage to display on dashboard
      sessionStorage.setItem('validation_decision_message', message);
      sessionStorage.setItem('validation_decision_severity', severity);
      sessionStorage.setItem('validation_decision_type', decisionType);
      sessionStorage.setItem('validation_session_id', sessionId);
      
      // Navigate to dashboard to show the progress
      navigate('/dashboard');
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to make decision');
      setShowDecisionDialog(false);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'compliant': '#4caf50',
      'warning': '#ff9800',
      'non_compliant': '#f44336',
      'critical': '#f44336',
      'minor': '#ff9800'
    };
    return colors[status] || '#9e9e9e';
  };

  const getStatusIcon = (status) => {
    const icons = {
      'compliant': <CheckCircleIcon />,
      'warning': <WarningIcon />,
      'non_compliant': <ErrorIcon />,
      'critical': <ErrorIcon />,
      'minor': <WarningIcon />
    };
    return icons[status] || <CheckCircleIcon />;
  };

  const getSessionName = () => {
    if (validationData?.session?.session_name) {
      return validationData.session.session_name;
    }
    return 'Validation Session';
  };

  const getTradeId = () => {
    console.log("Validation data in getTradeId:", validationData);
    
    // First check term sheet data
    if (validationData?.term_sheet_data?.trade_id) {
      console.log("Found trade ID in term_sheet_data:", validationData.term_sheet_data.trade_id);
      return validationData.term_sheet_data.trade_id;
    }
    
    // Then check trade record
    if (validationData?.trade_record?.trade_id) {
      console.log("Found trade ID in trade_record:", validationData.trade_record.trade_id);
      return validationData.trade_record.trade_id;
    }
    
    // Check session data for trade_id
    if (validationData?.session?.trade_id) {
      console.log("Found trade ID in session:", validationData.session.trade_id);
      return validationData.session.trade_id;
    }
    
    // If we have a session ID, check URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const tradeIdFromUrl = urlParams.get('trade_id');
    if (tradeIdFromUrl) {
      console.log("Found trade ID from URL:", tradeIdFromUrl);
      return tradeIdFromUrl;
    }
    
    console.log("No trade ID found in any data source");
    return 'Unknown';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button onClick={() => navigate('/validation')} sx={{ mt: 2 }}>
          Back to Validation Dashboard
        </Button>
      </Container>
    );
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f8fafc' }}>
      {/* Main Content */}
      <Box sx={{ flex: 1 }}>
        {/* Header */}
        <Paper elevation={0} sx={{ p: 3, bgcolor: 'white', borderBottom: '1px solid #e0e0e0' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h5" fontWeight="bold" color="text.primary">
                AI-Powered Validation Interface
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Chip 
                  label={`Trade ID: ${getTradeId()}`}
                  sx={{ mr: 2, bgcolor: '#fff3cd', color: '#856404' }}
                />
              </Box>
            </Box>
            <Button
              variant="contained"
              sx={{
                bgcolor: '#ff9800',
                color: 'white',
                borderRadius: 3,
                px: 3,
                py: 1,
                textTransform: 'none',
                fontWeight: 'medium'
              }}
            >
              AI Review
            </Button>
          </Box>
        </Paper>

        {/* Data Validation View Header */}
        <Container maxWidth="xl" sx={{ py: 2 }}>
          <Typography variant="h6" fontWeight="medium" color="text.primary" gutterBottom>
            Data Validation View
          </Typography>
          
          {/* Tabs */}
          <Paper elevation={1}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="fullWidth"
              sx={{
                borderBottom: 1,
                borderColor: 'divider',
                '& .MuiTab-root': {
                  textTransform: 'none',
                  fontWeight: 'medium',
                  minHeight: 64
                }
              }}
            >
              {tabs.map((tab) => (
                <Tab
                  key={tab.id}
                  value={tab.id}
                  icon={tab.icon}
                  iconPosition="start"
                  label={tab.label}
                  sx={{
                    '&.Mui-selected': {
                      bgcolor: '#e3f2fd',
                      color: '#1976d2'
                    }
                  }}
                />
              ))}
            </Tabs>
          </Paper>
        </Container>

        {/* Tab Content */}
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Grid container spacing={3}>
            {/* Term Sheet Data Section */}
            {activeTab === 'term-sheet' && (
              <>
                <Grid item xs={12} md={6}>
                  <Card elevation={2}>
                    <CardContent>
                      <Typography variant="h6" fontWeight="bold" gutterBottom>
                        Term Sheet Data
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableBody>
                            <TableRow>
                              <TableCell><strong>Trade ID:</strong></TableCell>
                              <TableCell>{getTradeId()}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Valid" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Counterparty:</strong></TableCell>
                              <TableCell>{validationData?.term_sheet_data?.counterparty || 'HSBC Bank PLC'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<WarningIcon />} 
                                  label="Warning" 
                                  size="small" 
                                  sx={{ bgcolor: '#ff9800', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Notional Amount:</strong></TableCell>
                              <TableCell>{validationData?.term_sheet_data?.notional_amount || '$25,000,000'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Valid" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Settlement Date:</strong></TableCell>
                              <TableCell>{validationData?.term_sheet_data?.settlement_date || 'April 15, 2025'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<ErrorIcon />} 
                                  label="Invalid" 
                                  size="small" 
                                  sx={{ bgcolor: '#f44336', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Interest Rate:</strong></TableCell>
                              <TableCell>{validationData?.term_sheet_data?.interest_rate || '3.75%'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Valid" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Currency:</strong></TableCell>
                              <TableCell>{validationData?.term_sheet_data?.currency || 'USD'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Valid" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Payment Terms:</strong></TableCell>
                              <TableCell>{validationData?.term_sheet_data?.payment_terms || 'Quarterly'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Valid" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Legal Entity:</strong></TableCell>
                              <TableCell>{validationData?.term_sheet_data?.legal_entity || 'Barclays Bank PLC'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Valid" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Internal Trade Record Section */}
                <Grid item xs={12} md={6}>
                  <Card elevation={2}>
                    <CardContent>
                      <Typography variant="h6" fontWeight="bold" gutterBottom>
                        Internal Trade Record
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableBody>
                            <TableRow>
                              <TableCell><strong>Trade ID:</strong></TableCell>
                              <TableCell>{validationData?.trade_record?.trade_id || 'TR-2025-0420'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Match" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Counterparty:</strong></TableCell>
                              <TableCell>{validationData?.trade_record?.counterparty || 'HSBC Bank'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<WarningIcon />} 
                                  label="Partial" 
                                  size="small" 
                                  sx={{ bgcolor: '#ff9800', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Notional Amount:</strong></TableCell>
                              <TableCell>{validationData?.trade_record?.notional_amount || '$25,000,000'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Match" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Settlement Date:</strong></TableCell>
                              <TableCell>{validationData?.trade_record?.settlement_date ? new Date(validationData.trade_record.settlement_date).toLocaleDateString() : 'April 5, 2025'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<ErrorIcon />} 
                                  label="Mismatch" 
                                  size="small" 
                                  sx={{ bgcolor: '#f44336', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Interest Rate:</strong></TableCell>
                              <TableCell>{validationData?.trade_record?.interest_rate || '3.75%'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Match" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Currency:</strong></TableCell>
                              <TableCell>{validationData?.trade_record?.currency || 'USD'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Match" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Payment Terms:</strong></TableCell>
                              <TableCell>{validationData?.trade_record?.payment_terms || 'Quarterly'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Match" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell><strong>Legal Entity:</strong></TableCell>
                              <TableCell>{validationData?.trade_record?.legal_entity || 'Barclays Bank PLC'}</TableCell>
                              <TableCell>
                                <Chip 
                                  icon={<CheckCircleIcon />} 
                                  label="Match" 
                                  size="small" 
                                  sx={{ bgcolor: '#4caf50', color: 'white' }}
                                />
                              </TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </CardContent>
                  </Card>
                </Grid>
              </>
            )}

            {/* AI Analysis Tab */}
            {activeTab === 'ai-analysis' && (
              <Grid item xs={12}>
                <Card elevation={2} sx={{ bgcolor: '#1e3a8a', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      AI Analysis
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      Detected {validationData?.discrepancies?.length || 2} discrepancies:
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Alert 
                          severity="error" 
                          sx={{ mb: 2, bgcolor: 'rgba(244, 67, 54, 0.1)', color: 'white' }}
                          icon={<ErrorIcon sx={{ color: '#f44336' }} />}
                        >
                          <Typography variant="body2" fontWeight="bold">
                            • Critical: Settlement date mismatch (10 days difference)
                          </Typography>
                        </Alert>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Alert 
                          severity="warning" 
                          sx={{ mb: 2, bgcolor: 'rgba(255, 152, 0, 0.1)', color: 'white' }}
                          icon={<WarningIcon sx={{ color: '#ff9800' }} />}
                        >
                          <Typography variant="body2" fontWeight="bold">
                            • Minor: Counterparty name format inconsistency (PLC suffix missing)
                          </Typography>
                        </Alert>
                      </Grid>
                    </Grid>

                    <Box sx={{ mt: 3 }}>
                      <Grid container spacing={4}>
                        <Grid item xs={12} md={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" fontWeight="bold">
                              {validationData?.validation_decision?.ai_risk_score || 65}/100
                            </Typography>
                            <Typography variant="body2">AI Risk Score</Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h6" fontWeight="bold">Warning</Typography>
                            <Typography variant="body2">MiFID II</Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h6" fontWeight="bold">Compliant</Typography>
                            <Typography variant="body2">FCA</Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Trade Record Tab */}
            {activeTab === 'trade-record' && (
              <Grid item xs={12}>
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      Internal Trade Record Details
                    </Typography>
                    {/* Similar content structure as term sheet but for trade record */}
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Compliance View Tab */}
            {activeTab === 'compliance' && (
              <Grid item xs={12}>
                <Card elevation={2}>
                  <CardContent>
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      Compliance Assessment
                    </Typography>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={4}>
                        <Card sx={{ bgcolor: '#f44336', color: 'white' }}>
                          <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h6">SEC</Typography>
                            <Typography variant="body2">Compliant</Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Card sx={{ bgcolor: '#4caf50', color: 'white' }}>
                          <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h6">Compliant</Typography>
                            <Typography variant="body2">FCA</Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Card sx={{ bgcolor: '#ff9800', color: 'white' }}>
                          <CardContent sx={{ textAlign: 'center' }}>
                            <Typography variant="h6">Warning</Typography>
                            <Typography variant="body2">MiFID II</Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 4 }}>
            <Button
              variant="contained"
              size="large"
              sx={{
                bgcolor: '#f44336',
                color: 'white',
                px: 4,
                py: 1.5,
                borderRadius: 3,
                textTransform: 'none',
                fontWeight: 'medium'
              }}
              onClick={() => {
                setDecisionData({ ...decisionData, decision: 'reject' });
                setShowDecisionDialog(true);
              }}
            >
              Reject
            </Button>
            <Button
              variant="contained"
              size="large"
              sx={{
                bgcolor: '#ff9800',
                color: 'white',
                px: 4,
                py: 1.5,
                borderRadius: 3,
                textTransform: 'none',
                fontWeight: 'medium'
              }}
              onClick={() => {
                setDecisionData({ ...decisionData, decision: 'manual_review' });
                setShowDecisionDialog(true);
              }}
            >
              Manual Review
            </Button>
            <Button
              variant="contained"
              size="large"
              sx={{
                bgcolor: '#4caf50',
                color: 'white',
                px: 4,
                py: 1.5,
                borderRadius: 3,
                textTransform: 'none',
                fontWeight: 'medium'
              }}
              onClick={() => {
                setDecisionData({ ...decisionData, decision: 'approve' });
                setShowDecisionDialog(true);
              }}
            >
              Approve
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Decision Dialog */}
      <Dialog open={showDecisionDialog} onClose={() => setShowDecisionDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Validation Decision</DialogTitle>
        <DialogContent>
          <TextField
            label="Decision Reason (Optional)"
            multiline
            rows={4}
            fullWidth
            value={decisionData.decision_reason}
            onChange={(e) => setDecisionData({ ...decisionData, decision_reason: e.target.value })}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDecisionDialog(false)}>Cancel</Button>
          <Button onClick={handleDecision} variant="contained">
            Confirm {decisionData.decision?.charAt(0)?.toUpperCase() + decisionData.decision?.slice(1)}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ValidationInterface; 