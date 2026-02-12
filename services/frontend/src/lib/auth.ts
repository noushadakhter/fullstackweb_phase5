import { create } from 'zustand';
import { api } from './api'; // Assuming api.ts exports the axios instance

interface User {
  id: string;
  email: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isLoggedIn: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  initializeAuth: () => void; // To check local storage on app load
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: null,
  user: null,
  isLoggedIn: false,

  login: (token: string, user: User) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ token, user, isLoggedIn: true });
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ token: null, user: null, isLoggedIn: false });
  },

  initializeAuth: () => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    if (token && user) {
      try {
        const parsedUser: User = JSON.parse(user);
        set({ token, user: parsedUser, isLoggedIn: true });
      } catch (e) {
        console.error("Failed to parse user from localStorage", e);
        get().logout(); // Clear invalid data
      }
    }
  },
}));

export function isAuthenticated() {
  return !!localStorage.getItem("token"); // Assuming you store your login token here
}


// Automatically initialize auth state on app load
// This might need to be called explicitly in _app.tsx or a root layout component
// useAuthStore.getState().initializeAuth();