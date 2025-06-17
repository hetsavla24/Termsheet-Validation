import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  CloudUpload,
  Assessment,
  History,
  Folder,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const Dashboard = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome back, {user?.full_name}!
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Termsheet Validation Dashboard
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <CloudUpload sx={{ mr: 2, color: 'primary.main' }} />
                      <Typography variant="h6">Upload Files</Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      Upload termsheets, documents, and images for processing
                    </Typography>
                    <Button 
                      variant="contained" 
                      fullWidth
                      sx={{ textTransform: 'none' }}
                      onClick={() => navigate('/files')}
                    >
                      Go to File Upload
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Folder sx={{ mr: 2, color: 'success.main' }} />
                      <Typography variant="h6">Manage Files</Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      View uploaded files, processing status, and download results
                    </Typography>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      sx={{ textTransform: 'none' }}
                      onClick={() => navigate('/files')}
                    >
                      View File Manager
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Assessment sx={{ mr: 2, color: 'warning.main' }} />
                      <Typography variant="h6">Document Analysis</Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      Advanced termsheet validation with NLP processing
                    </Typography>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      disabled
                      sx={{ textTransform: 'none' }}
                    >
                      Coming in Phase 3
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Assessment sx={{ mr: 2, color: 'secondary.main' }} />
                      <Typography variant="h6">Reports & Analytics</Typography>
                    </Box>
                    <Typography variant="body2" color="textSecondary" mb={2}>
                      Access validation reports and analytics dashboards
                    </Typography>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      disabled
                      sx={{ textTransform: 'none' }}
                    >
                      Coming in Phase 4
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" mb={2}>
              <History sx={{ mr: 2 }} />
              <Typography variant="h6">Recent Activity</Typography>
            </Box>
            <Typography variant="body2" color="textSecondary">
              No recent activities yet. Start by uploading your first document!
            </Typography>
          </Paper>
        </Grid>

        {/* System Status */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <Box display="flex" alignItems="center" gap={2}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: 'success.main',
                  mr: 2,
                }}
              />
              <Typography variant="body2">
                ✅ Phase 1: Authentication Complete
              </Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={2} mt={1}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: 'success.main',
                  mr: 2,
                }}
              />
              <Typography variant="body2">
                ✅ Phase 2: File Upload & Processing Complete
              </Typography>
            </Box>
            <Box display="flex" alignItems="center" gap={2} mt={1}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: 'warning.main',
                  mr: 2,
                }}
              />
              <Typography variant="body2">
                🔄 Phase 3: Document Validation (Coming Soon)
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 