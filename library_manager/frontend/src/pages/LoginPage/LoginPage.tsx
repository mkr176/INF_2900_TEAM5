import React, { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import "./LoginPage.css";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = () => {
    if (username && password) {
      alert("Logging in...");
      navigate("/principal");
    } else {
      alert("Both username and password are required");
    }
  };

  const redirectToSignUp = () => {
    window.location.href = "/signup";
  };

  return ( 
    <div className="relative flex items-center justify-center h-screen bg-gradient-to-r from-purple-500 to-pink-500 overflow-hidden">
      <motion.div
        className="absolute inset-0 flex items-center justify-center overflow-hidden"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <motion.img
          src="/image2vector.svg" //need an image of books in the background
          alt="Floating Books"
          className="absolute w-full h-full object-cover opacity-30"
          animate={{ y: [0, -10, 0] }}
          transition={{ repeat: Infinity, duration: 5, ease: "easeInOut" }}
        />
      </motion.div>
      <motion.div
        className="bg-white p-8 rounded-2xl shadow-xl w-96 text-center relative z-10"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-indigo-900 mb-6">Library Login</h1>
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 transition-all"
        />
        <motion.input
          whileFocus={{ scale: 1.05 }}
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-3 mb-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 transition-all"
        />
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleLogin}
          className="w-full bg-indigo-700 text-white py-3 rounded-lg font-semibold hover:bg-indigo-800 transition-all"
        >
          Login
        </motion.button>
        <div className="mt-4 text-gray-600">
          <p>Don't have an account?</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={redirectToSignUp}
            className="text-indigo-700 font-semibold hover:text-indigo-900 transition-all"
          >
            Sign Up
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;