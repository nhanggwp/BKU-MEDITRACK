import apiService from './api';

class AuthService {
  // Sign up new user
  async signUp(userData) {
    try {
      const response = await apiService.post('/api/auth/signup', userData, false);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Sign up failed');
    }
  }

  // Sign in user
  async signIn(email, password) {
    try {
      const response = await apiService.post('/api/auth/signin', {
        email,
        password
      }, false);

      if (response.session?.access_token) {
        apiService.setToken(response.session.access_token);
        // Store user data
        localStorage.setItem('user_data', JSON.stringify({
          user: response.user,
          profile: response.profile
        }));
      }

      return response;
    } catch (error) {
      throw new Error(error.message || 'Sign in failed');
    }
  }

  // Sign out user
  async signOut() {
    try {
      await apiService.post('/api/auth/signout', {});
      this.clearUserData();
      return { success: true };
    } catch (error) {
      // Even if API call fails, clear local data
      this.clearUserData();
      throw new Error(error.message || 'Sign out failed');
    }
  }

  // Verify token
  async verifyToken() {
    try {
      const response = await apiService.get('/api/auth/verify');
      return response;
    } catch (error) {
      this.clearUserData();
      throw new Error('Token verification failed');
    }
  }

  // Reset password
  async resetPassword(email) {
    try {
      const response = await apiService.post('/api/auth/reset-password', { email }, false);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Password reset failed');
    }
  }

  // Update password
  async updatePassword(newPassword, refreshToken) {
    try {
      const response = await apiService.post('/api/auth/update-password', {
        new_password: newPassword,
        refresh_token: refreshToken
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Password update failed');
    }
  }

  // Get current user data from localStorage
  getCurrentUser() {
    try {
      const userData = localStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    const token = localStorage.getItem('auth_token');
    const userData = this.getCurrentUser();
    return !!(token && userData);
  }

  // Clear user data from localStorage
  clearUserData() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    apiService.setToken(null);
  }

  // Get user role
  getUserRole() {
    const userData = this.getCurrentUser();
    return userData?.profile?.role || 'patient';
  }

  // Auto-login check (verify token on app load)
  async autoLogin() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return false;
    }

    try {
      await this.verifyToken();
      return true;
    } catch (error) {
      this.clearUserData();
      return false;
    }
  }
}

export default new AuthService();
