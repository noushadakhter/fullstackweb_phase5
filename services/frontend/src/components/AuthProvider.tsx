"use client";

import { useAuthStore } from "@/lib/auth";
import { useEffect } from "react";

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    useAuthStore.getState().initializeAuth();
  }, []);

  return <>{children}</>;
}
