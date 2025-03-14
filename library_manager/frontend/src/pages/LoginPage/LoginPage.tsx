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
  const { fetchUser } = useAuth(); // ✅ Use AuthContext

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
        await fetchUser();  // ✅ Update authentication state
        navigate("/principal");
      } else {
        alert("Invalid username or password");
      }
    } catch (error) {
      console.error("Error during login:", error);
    }
  };

  return (
    <div className="relative flex items-center justify-center h-screen bg-gradient-to-r from-purple-500 to-pink-500">
      <motion.div className="bg-white p-8 rounded-2xl shadow-xl w-96 text-center">
        <h1 className="text-3xl font-bold text-indigo-900 mb-6">Library Login</h1>
        <motion.input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg"
        />
        <motion.input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg"
        />
        <motion.button
          onClick={handleLogin}
          className="w-full bg-indigo-700 text-white py-3 rounded-lg"
        >
          Login
        </motion.button>
      </motion.div>
    </div>
  );
};

export default LoginPage;
