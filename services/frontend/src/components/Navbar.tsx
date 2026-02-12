// frontend/src/components/Navbar.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "../lib/auth";

const Navbar = () => {
  const router = useRouter();
  const { isLoggedIn, logout } = useAuthStore();
  const [isAuth, setIsAuth] = useState(false);

  useEffect(() => {
    setIsAuth(isLoggedIn);
  }, [isLoggedIn]);
  
  // A simple way to re-check auth state on navigation changes.
  useEffect(() => {
    const handleRouteChange = () => {
      setIsAuth(isLoggedIn);
    };
    // Next.js router doesn't have a native event system like this,
    // so we listen to popstate and pushstate.
    window.addEventListener('popstate', handleRouteChange);
    // You might need a more robust way to listen to router changes if this fails.
    
    return () => {
      window.removeEventListener('popstate', handleRouteChange);
    };
  }, [isLoggedIn]);


  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <nav className="bg-white shadow-md dark:bg-gray-800">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link href="/" className="text-xl font-bold text-gray-900 dark:text-white">
            TodoApp
          </Link>
          <div className="flex items-center space-x-4">
            {isAuth ? (
              <>
                <Link href="/tasks" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
                  Tasks
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
                  Login
                </Link>
                <Link href="/signup" className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
