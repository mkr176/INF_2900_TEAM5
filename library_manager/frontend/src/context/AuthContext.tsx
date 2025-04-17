import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

// Define the structure based on UserSerializer and UserProfileSerializer
interface UserProfile {
    user_id: number;
    username: string;
    type: string; // 'AD', 'US', 'LB'
    age: number | null;
    // avatar: string | null; // Keep original field if needed, but URL is primary for display
    avatar_url: string | null; // Expect the full URL from backend
    get_type_display: string;
}

interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    profile: UserProfile | null; // Profile can be null initially or if error
    date_joined: string;
    is_staff: boolean;
}

interface AuthContextType {
  isLoggedIn: boolean;
    currentUser: User | null; // Store the full user object
    username: string; // Keep for convenience? Or derive from currentUser
    avatarUrl: string; // <<< CHANGE: Store the full URL >>>
    userType: string; // Keep for convenience? Or derive from currentUser
    fetchUser: () => Promise<void>; // Make async
    logout: () => Promise<void>; // Make async
    getCSRFToken: () => Promise<string | null>; // Add CSRF utility
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper to get CSRF token from cookie
const getCSRFTokenFromCookie = (): string | null => {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : null;
};

// <<< REMOVE: Static path prefix and helper function are no longer needed >>>
// const STATIC_AVATAR_PATH_PREFIX = "/static/images/";
// const DEFAULT_AVATAR_FILENAME = "avatars/default.svg";
// const DEFAULT_AVATAR_FULL_PATH = STATIC_AVATAR_PATH_PREFIX + DEFAULT_AVATAR_FILENAME;
// const getFullAvatarPath = (...) => { ... };

// <<< ADD: Define the default avatar URL (should match the one provided by backend serializer) >>>
// This needs to be the actual URL where the default image is served.
// Adjust if your static files setup is different.
const DEFAULT_AVATAR_URL = "/static/images/avatars/default.svg";


export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
    // Derived state for convenience
  const [username, setUsername] = useState("Not logged in");
    // <<< CHANGE: Initialize avatar state with the default URL >>>
    const [avatarUrl, setAvatarUrl] = useState(DEFAULT_AVATAR_URL);
  const [userType, setUserType] = useState("");

    const getCSRFToken = async (): Promise<string | null> => {
        // 1. Try getting from cookie first (most common case after initial load)
        let token = getCSRFTokenFromCookie();
        if (token) {
            return token;
        }
        // 2. If not in cookie, fetch from the endpoint
        try {
            console.log("Fetching CSRF token from /api/csrf/");
            const response = await fetch("/api/csrf/", { credentials: "include" });
      if (response.ok) {
                const data = await response.json();
                console.log("CSRF token fetched:", data.csrfToken);
                // The act of fetching might set the cookie, try reading it again
                token = getCSRFTokenFromCookie();
                return token || data.csrfToken; // Return from cookie if set, else from response
            } else {
                console.error("Failed to fetch CSRF token, status:", response.status);
                return null;
            }
        } catch (error) {
            console.error("Error fetching CSRF token:", error);
            return null;
        }
    };


    const fetchUser = useCallback(async () => {
        console.log("AuthContext: Fetching user data...");
        try {
            // Use the endpoint GET /api/users/me/
            const response = await fetch("/api/users/me/", {
                credentials: "include", // Send cookies
                headers: {
                    'Accept': 'application/json', // Explicitly accept JSON
                }
            });

            if (response.ok) {
                const userData: User = await response.json();
                console.log("AuthContext: User data received:", userData);
                setCurrentUser(userData);
        setIsLoggedIn(true);
                // Update derived state
                setUsername(userData.username);
                // Safely access profile type, default to 'US' if profile or type is missing/null
                setUserType(userData.profile?.type ?? "US");
                // <<< CHANGE: Use avatar_url from backend, fallback to default URL >>>
                setAvatarUrl(userData.profile?.avatar_url || DEFAULT_AVATAR_URL);
      } else {
                console.log("AuthContext: No user session found or error:", response.status);
                setCurrentUser(null);
        setIsLoggedIn(false);
        setUsername("Not logged in");
                // <<< CHANGE: Reset avatar to the default URL >>>
                setAvatarUrl(DEFAULT_AVATAR_URL);
                setUserType("");
      }
    } catch (error) {
            console.error("AuthContext: Error fetching user:", error);
            setCurrentUser(null);
      setIsLoggedIn(false);
            setUsername("Not logged in");
            // <<< CHANGE: Reset avatar to the default URL >>>
            setAvatarUrl(DEFAULT_AVATAR_URL);
            setUserType("");
    }
    }, []); // No dependencies needed if it doesn't rely on component state

  // ✅ Global Logout (Ensures all components update)
  const logout = async () => {
        console.log("AuthContext: Logging out...");
        const csrfToken = await getCSRFToken(); // Fetch CSRF token first
        if (!csrfToken) {
            console.error("Logout failed: Could not get CSRF token.");
            // Optionally inform the user
            alert("Logout failed: Could not verify security token. Please refresh and try again.");
            return;
        }

        try {
            // Use the new endpoint POST /api/auth/logout/
            const response = await fetch("/api/auth/logout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken, // Include CSRF token in header
        },
                credentials: "include", // Send cookies
      });

      if (response.ok) {
                console.log("AuthContext: Logout successful.");
                // Clear state regardless of server response status for robustness
      } else {
                console.error("AuthContext: Logout failed on server:", response.status, await response.text());
                // Still clear local state as a safety measure even if server fails
      }
    } catch (error) {
            console.error("AuthContext: Error during logout:", error);
             // Still clear local state as a safety measure
        } finally {
            // <<< CHANGE: Ensure state is cleared in finally block >>>
             setCurrentUser(null);
             setIsLoggedIn(false);
             setUsername("Not logged in");
             // <<< CHANGE: Reset avatar to the default URL >>>
             setAvatarUrl(DEFAULT_AVATAR_URL);
             setUserType("");
    }
  };

    // Fetch user on initial load
  useEffect(() => {
    fetchUser();
    }, [fetchUser]); // Depend on fetchUser useCallback

  return (
        // <<< CHANGE: Provide avatarUrl instead of avatar >>>
        <AuthContext.Provider value={{ isLoggedIn, currentUser, username, avatarUrl, userType, fetchUser, logout, getCSRFToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
