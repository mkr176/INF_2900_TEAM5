import React, { createContext, useContext, useState, useEffect } from "react";

interface AuthContextType {
  isLoggedIn: boolean;
  username: string;
  avatar: string;
  userType: string; 
  fetchUser: () => void;
  logout: () => void;
  
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("Not logged in");
  const [avatar, setAvatar] = useState("default.svg");
  const [userType, setUserType] = useState<string>("");

  // ✅ Fetch user details when app starts
  const fetchUser = async () => {
    try {
      const response = await fetch("/api/user/", { credentials: "include" });
      if (response.ok) {
        const user = await response.json();
        setUsername(user.username);
        setUserType(user.type || "");
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

  // ✅ Global Logout (Ensures all components update)
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
        setIsLoggedIn(false);
        setUsername("Not logged in");
        setAvatar("default.svg");
        fetchUser(); // 🔄 Ensures all components update!
      } else {
        console.error("Logout failed.");
      }
    } catch (error) {
      console.error("Error during logout:", error);
    }
  };

  // ✅ Run on app start
  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn, username, avatar, userType, fetchUser, logout }}>
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
