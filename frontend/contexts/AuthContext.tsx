import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface User {
  id: string;
  phone: string;
  name: string;
  email: string;
  addresses: any[];
  wishlist: string[];
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (phone: string, otp: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: any) => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  const loadStoredAuth = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('token');
      const storedUser = await AsyncStorage.getItem('user');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      } else {
        // Auto-login as guest for browsing
        await autoLogin();
      }
    } catch (error) {
      console.error('Error loading auth:', error);
      await autoLogin();
    } finally {
      setLoading(false);
    }
  };

  const autoLogin = async () => {
    try {
      // Send OTP for guest user
      const otpRes = await axios.post(`${API_URL}/api/auth/send-otp`, { phone: '0000000000' });
      const otpCode = otpRes.data.otp;
      
      // Verify OTP to get token
      const verifyRes = await axios.post(`${API_URL}/api/auth/verify-otp`, {
        phone: '0000000000',
        otp: otpCode,
      });

      const { token: newToken, user: newUser } = verifyRes.data;
      
      // Update user name
      const guestUser = { ...newUser, name: 'Guest User' };
      await axios.put(`${API_URL}/api/auth/profile`, { name: 'Guest User' }, {
        headers: { Authorization: `Bearer ${newToken}` },
      });
      
      await AsyncStorage.setItem('token', newToken);
      await AsyncStorage.setItem('user', JSON.stringify(guestUser));
      
      setToken(newToken);
      setUser(guestUser);
    } catch (error) {
      console.error('Auto login failed:', error);
    }
  };

  const login = async (phone: string, otp: string) => {
    try {
      const response = await axios.post(`${API_URL}/api/auth/verify-otp`, {
        phone,
        otp,
      });

      const { token: newToken, user: newUser } = response.data;
      
      await AsyncStorage.setItem('token', newToken);
      await AsyncStorage.setItem('user', JSON.stringify(newUser));
      
      setToken(newToken);
      setUser(newUser);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const logout = async () => {
    await AsyncStorage.removeItem('token');
    await AsyncStorage.removeItem('user');
    setToken(null);
    setUser(null);
    // Re-login as guest
    await autoLogin();
  };

  const updateProfile = async (data: any) => {
    try {
      await axios.put(`${API_URL}/api/auth/profile`, data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      const updatedUser = { ...user, ...data };
      await AsyncStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser as User);
    } catch (error) {
      throw new Error('Failed to update profile');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        logout,
        updateProfile,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
