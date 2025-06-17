import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      // Actions
      setAuth: (user, token) => {
        console.log('Setting auth:', { user, token });
        set({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        });
        
        // Set axios default authorization header safely
        if (typeof window !== 'undefined') {
          try {
            const axios = require('axios');
            if (axios && axios.defaults && axios.defaults.headers) {
              axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            }
          } catch (error) {
            console.warn('Axios not available for header setting:', error);
          }
        }
      },

      logout: () => {
        console.log('Logging out user');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
        
        // Remove axios authorization header safely
        if (typeof window !== 'undefined') {
          try {
            const axios = require('axios');
            if (axios && axios.defaults && axios.defaults.headers && axios.defaults.headers.common) {
              delete axios.defaults.headers.common['Authorization'];
            }
          } catch (error) {
            console.warn('Axios not available for header removal:', error);
          }
        }
      },

      setLoading: (loading) => {
        console.log('Setting loading:', loading);
        set({ isLoading: loading });
      },

      updateUser: (userData) => {
        set(state => ({
          user: { ...state.user, ...userData }
        }));
      },

      // Token expiration check
      isTokenExpired: () => {
        const { token } = get();
        if (!token) return true;
        
        try {
          // For fake tokens, never expire during testing
          if (token === "fake-jwt-token-for-testing") {
            return false;
          }
          
          const payload = JSON.parse(atob(token.split('.')[1]));
          const currentTime = Date.now() / 1000;
          return payload.exp < currentTime;
        } catch (error) {
          console.warn('Error checking token expiry:', error);
          return true;
        }
      },

      // Auto logout on token expiry
      checkTokenExpiry: () => {
        const { isTokenExpired, logout, token } = get();
        console.log('Checking token expiry, token exists:', !!token);
        
        if (token && isTokenExpired()) {
          console.log('Token expired, logging out');
          logout();
          return false;
        }
        return true;
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        console.log('Auth store rehydrated:', state);
        if (state) {
          // Validate token on hydration
          if (state.token && state.isAuthenticated) {
            console.log('Existing auth state found');
          }
        }
      },
    }
  )
);

export default useAuthStore; 