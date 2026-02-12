'use client';

import { useAuthStore } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Navbar from '@/components/Navbar'; // Assuming you will create this component

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isLoggedIn, initializeAuth } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    initializeAuth(); // Attempt to load auth state from local storage
  }, [initializeAuth]);

  useEffect(() => {
    if (!isLoggedIn) {
      router.push('/login');
    }
  }, [isLoggedIn, router]);

  if (!isLoggedIn) {
    return <div className="flex items-center justify-center min-h-screen">Loading authentication...</div>; // Or a loading spinner
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar /> {/* This component will have the logout button */}
      <main className="flex-grow container mx-auto p-4">
        {children}
      </main>
    </div>
  );
}