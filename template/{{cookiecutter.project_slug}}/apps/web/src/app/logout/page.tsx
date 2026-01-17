'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Logout Page - Handles user logout and redirects to login.
 * 
 * This page is necessary because:
 * 1. Sidebar "Logout" link needs a destination
 * 2. Logout requires client-side execution (clearing tokens)
 * 3. Provides visual feedback during logout process
 */
export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    let mounted = true;

    const performLogout = async () => {
      try {
        // Clear tokens from storage
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('refresh_token');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Optional: Call backend logout endpoint
        // await fetch('/api/v1/auth/logout', { method: 'POST' });
        
        if (mounted) {
          router.push('/login');
        }
      } catch (error) {
        console.error('Logout failed', error);
        // Fallback to login even if something fails
        if (mounted) {
          router.push('/login');
        }
      }
    };

    performLogout();

    return () => {
      mounted = false;
    };
  }, [router]);

  return (
    <div style={{ 
      height: '100vh', 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center',
      flexDirection: 'column',
      gap: '1rem',
      backgroundColor: '#f9fafb'
    }}>
      <div style={{
        width: '40px',
        height: '40px',
        border: '3px solid #e5e7eb',
        borderTopColor: '#3b82f6',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
      }}></div>
      <p style={{ fontFamily: 'system-ui, sans-serif', color: '#6b7280' }}>Logging out...</p>
      <style jsx global>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
