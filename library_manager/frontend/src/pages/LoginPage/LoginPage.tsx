import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext"; // ✅ Import AuthContext
import "./LoginPage.css";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const navigate = useNavigate();
  const { isLoggedIn, fetchUser } = useAuth(); // ✅ Use AuthContext

 

  // ✅ Fetch CSRF token
  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        const response = await fetch("/api/csrf/", {
          method: "GET",
          credentials: "include",
        });

        if (response.ok) {
          const data = await response.json();
          setCsrfToken(data.csrfToken);
        }
      } catch (error) {
        console.error("Error fetching CSRF token:", error);
      }
    };

    fetchCsrfToken();
  }, []);

  const handleLogin = async () => {
    if (!csrfToken) {
      alert("CSRF token is missing. Please refresh the page.");
      return;
    }

    try {
      const response = await fetch("/api/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ username, password }),
        credentials: "include",
      });

      if (response.ok) {
        alert("Logging in...");
        await fetchUser(); // ✅ Update authentication state
        navigate("/principal");
      } else {
        alert("Invalid username or password");
      }
    } catch (error) {
      console.error("Error during login:", error);
    }
  };

  return (
    <div className="login-container">
      <motion.div
        className="login-card"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="login-title">Library Login</h1>
        {isLoggedIn ? (
          <p className="login-message">You're already logged in.</p>
        ) : (
          <>
            <motion.input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="login-input"
              whileFocus={{ scale: 1.05 }}
            />
            <motion.input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="login-input"
              whileFocus={{ scale: 1.05 }}
            />
            <motion.button
              onClick={handleLogin}
              className="login-button"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Login
            </motion.button>
          </>
        )}
      </motion.div>
    </div>
  );
};

export default LoginPage;
