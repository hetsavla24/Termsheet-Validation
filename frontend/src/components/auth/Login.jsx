import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import {
  Container,
  Paper,
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Login as LoginIcon,
} from '@mui/icons-material';
import { authAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import toast from 'react-hot-toast';

// Validation schema
const validationSchema = Yup.object({
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  password: Yup.string()
    .min(6, 'Password must be at least 6 characters')
    .required('Password is required'),
});

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setAuth, setLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle messages from registration or other sources
  useEffect(() => {
    if (location.state?.message) {
      setSuccessMessage(location.state.message);
      // Clear the state to prevent showing the message on refresh
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  const getErrorMessage = (error) => {
    if (error?.response?.data?.detail) {
      const detail = error.response.data.detail;
      // Map backend error messages to user-friendly messages
      if (detail.includes('Incorrect email or password')) {
        return 'Invalid email or password. Please check your credentials.';
      } else if (detail.includes('Account is deactivated')) {
        return 'Your account has been deactivated. Please contact support.';
      } else if (detail.includes('User not found')) {
        return 'No account found with this email address.';
      } else {
        return detail;
      }
    } else if (error?.response?.status === 401) {
      return 'Invalid email or password. Please check your credentials.';
    } else if (error?.response?.status === 422) {
      return 'Please check your input and try again.';
    } else if (error?.response?.status >= 500) {
      return 'Server error. Please try again later.';
    } else if (error?.message) {
      return error.message;
    } else {
      return 'Login failed. Please try again.';
    }
  };

  const handleSubmit = async (values, { setSubmitting }) => {
    console.log('Login attempt with:', values.email);
    setError('');
    setSuccessMessage(''); // Clear success message on new login attempt
    setLoading(true);
    setIsSubmitting(true);

    try {
      const response = await authAPI.login({
        email: values.email,
        password: values.password,
      });

      console.log('Login response:', response);

      if (response.access_token && response.user) {
        setAuth(response.user, response.access_token);
        toast.success(`Welcome back, ${response.user.full_name}!`);
        console.log('Navigating to dashboard...');
        navigate('/dashboard', { replace: true });
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = getErrorMessage(error);
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
      setIsSubmitting(false);
      setSubmitting(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Container 
      component="main" 
      maxWidth="sm"
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        py: 4,
      }}
    >
      <Paper
        elevation={6}
        sx={{
          width: '100%',
          p: 4,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: 3,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <LoginIcon sx={{ fontSize: 48, mb: 2 }} />
          <Typography component="h1" variant="h4" gutterBottom>
            Welcome Back
          </Typography>
          <Typography variant="body1" sx={{ mb: 3, textAlign: 'center', opacity: 0.9 }}>
            Sign in to your Termsheet Validation account
          </Typography>

          {successMessage && (
            <Alert 
              severity="success" 
              sx={{ 
                width: '100%', 
                mb: 2,
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                color: 'white',
                '& .MuiAlert-icon': {
                  color: 'white'
                }
              }}
            >
              {successMessage}
            </Alert>
          )}

          {error && (
            <Alert 
              severity="error" 
              sx={{ 
                width: '100%', 
                mb: 2,
                backgroundColor: 'rgba(211, 47, 47, 0.1)',
                color: 'white',
                '& .MuiAlert-icon': {
                  color: 'white'
                }
              }}
            >
              {error}
            </Alert>
          )}

          <Formik
            initialValues={{
              email: location.state?.email || '',
              password: '',
            }}
            validationSchema={validationSchema}
            onSubmit={handleSubmit}
          >
            {({ errors, touched, values, handleChange, handleBlur }) => (
              <Form style={{ width: '100%' }}>
                <Field name="email">
                  {({ field, meta }) => (
                    <TextField
                      {...field}
                      fullWidth
                      type="email"
                      label="Email Address"
                      margin="normal"
                      error={meta.touched && !!meta.error}
                      helperText={meta.touched && meta.error}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Email />
                          </InputAdornment>
                        ),
                      }}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          backgroundColor: 'rgba(255, 255, 255, 0.1)',
                          '& fieldset': {
                            borderColor: 'rgba(255, 255, 255, 0.3)',
                          },
                          '&:hover fieldset': {
                            borderColor: 'rgba(255, 255, 255, 0.5)',
                          },
                          '&.Mui-focused fieldset': {
                            borderColor: 'white',
                          },
                        },
                        '& .MuiInputLabel-root': {
                          color: 'rgba(255, 255, 255, 0.7)',
                        },
                        '& .MuiInputBase-input': {
                          color: 'white',
                        },
                        '& .MuiFormHelperText-root': {
                          color: 'rgba(255, 255, 255, 0.8)',
                        },
                      }}
                    />
                  )}
                </Field>

                <Field name="password">
                  {({ field, meta }) => (
                    <TextField
                      {...field}
                      fullWidth
                      type={showPassword ? 'text' : 'password'}
                      label="Password"
                      margin="normal"
                      error={meta.touched && !!meta.error}
                      helperText={meta.touched && meta.error}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Lock />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={togglePasswordVisibility}
                              edge="end"
                              sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
                            >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          backgroundColor: 'rgba(255, 255, 255, 0.1)',
                          '& fieldset': {
                            borderColor: 'rgba(255, 255, 255, 0.3)',
                          },
                          '&:hover fieldset': {
                            borderColor: 'rgba(255, 255, 255, 0.5)',
                          },
                          '&.Mui-focused fieldset': {
                            borderColor: 'white',
                          },
                        },
                        '& .MuiInputLabel-root': {
                          color: 'rgba(255, 255, 255, 0.7)',
                        },
                        '& .MuiInputBase-input': {
                          color: 'white',
                        },
                        '& .MuiFormHelperText-root': {
                          color: 'rgba(255, 255, 255, 0.8)',
                        },
                      }}
                    />
                  )}
                </Field>

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  disabled={isSubmitting}
                  sx={{
                    mt: 3,
                    mb: 2,
                    py: 1.5,
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    color: 'white',
                    fontWeight: 'bold',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.3)',
                    },
                    '&:disabled': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'rgba(255, 255, 255, 0.5)',
                    },
                  }}
                >
                  {isSubmitting ? 'Signing In...' : 'Sign In'}
                </Button>

                <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.3)' }} />

                <Box textAlign="center">
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Don't have an account?{' '}
                    <Link
                      to="/register"
                      style={{
                        color: 'white',
                        textDecoration: 'underline',
                        fontWeight: 'bold',
                      }}
                    >
                      Sign up here
                    </Link>
                  </Typography>
                </Box>
              </Form>
            )}
          </Formik>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login; 