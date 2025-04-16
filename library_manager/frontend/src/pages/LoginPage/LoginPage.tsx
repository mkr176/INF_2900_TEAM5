import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext"; // ✅ Import AuthContext
import "./LoginPage.css";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
    // <<< CHANGE: Use getCSRFToken from context >>>
    const { isLoggedIn, fetchUser, getCSRFToken } = useAuth(); // ✅ Use AuthContext
  const navigate = useNavigate();

    // <<< REMOVED: CSRF token fetching logic here, use context's getCSRFToken >>>
    // useEffect(() => { ... }, []);

  const handleLogin = async () => {
        // <<< CHANGE: Use getCSRFToken from context >>>
        const csrfToken = await getCSRFToken();
    if (!csrfToken) {
            alert("Login failed: Could not verify security token. Please refresh and try again.");
      return;
    }

    try {
            // <<< CHANGE: Update API endpoint >>>
            const response = await fetch("/api/auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ username, password }),
        credentials: "include",
      });

      if (response.ok) {
                // <<< CHANGE: Rely on fetchUser to update state >>>
                // const userData = await response.json(); // No need to parse user data here
        alert("Logging in...");
                await fetchUser(); // ✅ Update authentication state via context
                navigate("/principal"); // Redirect after successful login and state update
      } else {
                // <<< CHANGE: Handle potential JSON error response >>>
                let errorMsg = "Invalid username or password";
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg; // Use backend error if available
                } catch (e) {
                    // Ignore if response is not JSON
                }
                alert(errorMsg);
      }
    } catch (error) {
      console.error("Error during login:", error);
            alert("An error occurred during login. Please try again."); // Generic error for network issues etc.
    }
  };

    // Redirect if already logged in
    useEffect(() => {
        if (isLoggedIn) {
            navigate("/principal", { replace: true });
        }
    }, [isLoggedIn, navigate]);


    // Render login form only if not logged in
    if (isLoggedIn) {
        return <p>Redirecting...</p>; // Or null
    }

  return (
    <div className="login-container">
      <motion.div
                className="login-card" // Assuming login-card is defined in LoginPage.css
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
                <h1 className="login-title">Library Login</h1> {/* Assuming login-title is defined */}
                {/* Removed isLoggedIn check here as it's handled by the redirect effect */}
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
                    {/* Link to Sign Up Page */}
                    <div className="signup-link"> {/* Assuming signup-link is defined */}
                        <p>Don't have an account?</p>
                        <button onClick={() => navigate("/signup")} className="signup-button"> {/* Assuming signup-button is defined */}
                            Sign Up
                        </button>
                    </div>
                </>
      </motion.div>
    </div>
  );
};

export default LoginPage;
