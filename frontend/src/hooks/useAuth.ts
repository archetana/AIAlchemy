import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '../store';
import { authService } from '../services/authService';
import { setUser, clearUser, setLoading } from '../store/authSlice';

interface LoginCredentials {
  email: string;
  password: string;
}

export const useAuth = () => {
  const dispatch = useDispatch();
  const { user, isAuthenticated, isLoading } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    // Check for existing token on app start
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('aialchemy_token');
      if (token) {
        try {
          const userData = await authService.getCurrentUser();
          dispatch(setUser(userData));
        } catch (error) {
          localStorage.removeItem('aialchemy_token');
          dispatch(clearUser());
        }
      }
      dispatch(setLoading(false));
    };

    checkAuthStatus();
  }, [dispatch]);

  const login = async (credentials: LoginCredentials) => {
    try {
      dispatch(setLoading(true));
      const response = await authService.login(credentials);
      localStorage.setItem('aialchemy_token', response.access_token);
      
      const userData = await authService.getCurrentUser();
      dispatch(setUser(userData));
      
      return { success: true };
    } catch (error: any) {
      dispatch(setLoading(false));
      return { 
        success: false, 
        error: error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      // Continue with logout even if API call fails
    } finally {
      localStorage.removeItem('aialchemy_token');
      dispatch(clearUser());
    }
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
  };
};