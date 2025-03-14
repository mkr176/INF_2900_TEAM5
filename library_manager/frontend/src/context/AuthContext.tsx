import React, { createContext, useContext, useState, useEffect } from "react";

interface AuthContextType {
  isLoggedIn: boolean;
  username: string;
  avatar: string;
  fetchUser: () => void;  // Function to refresh user data
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("Not logged in");
  const [avatar, setAvatar] = useState("default.svg");

  // ✅ Fetch user details when the app starts or after login/logout
  const fetchUser = async () => {
    try {
      const response = await fetch("/api/user/", { credentials: "include" });
      if (response.ok) {
        const user = await response.json();
        setUsername(user.username);
        setAvatar(user.avatar || "default.svg");
        setIsLoggedIn(true);
      } else {
        setIsLoggedIn(false);
        setUsername("Not logged in");
        setAvatar("default.svg");
      }
    } catch (error) {
      console.error("Error fetching user:", error);
      setIsLoggedIn(false);
    }
  };

  // ✅ Logout function
  const logout = async () => {
    try {
      const csrfResponse = await fetch("/api/csrf/", { credentials: "include" });
      const csrfData = await csrfResponse.json();
      const csrfToken = csrfData.csrfToken;

      const response = await fetch("/api/logout/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        credentials: "include",
      });

      if (response.ok) {
        alert("Logged out successfully!");
        setIsLoggedIn(false);
        setUsername("Not logged in");
        setAvatar("default.svg");
      } else {
        alert("Logout failed.");
      }
    } catch (error) {
      console.error("Error during logout:", error);
    }
  };

  // Fetch user on app start
  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn, username, avatar, fetchUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// ✅ Hook to use authentication state in components
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
