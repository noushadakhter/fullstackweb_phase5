// frontend/src/components/ProtectedRoute.tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "../lib/auth";

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  // Render children only if authenticated, otherwise render null or a loading spinner
  // while the redirect is in progress.
  if (!isAuthenticated()) {
    return (
        <div className="flex justify-center items-center h-screen">
            <div className="text-lg">Redirecting to login...</div>
        </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
