import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./WelcomePage.css";

const WelcomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-r from-brown-700 to-yellow-500 text-white text-center p-6">
      <motion.div
        className="bg-white p-10 rounded-3xl shadow-2xl text-brown-900 w-full max-w-lg"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.h1
          className="text-4xl font-extrabold mb-6 text-yellow-700"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          Welcome to LibManager!
        </motion.h1>
        <motion.img
          src="/static/images/library_seal.jpg"
          alt="LibManager Logo"
          width="150"
          className="mb-6 rounded-full shadow-lg border-4 border-yellow-700"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        />
        <motion.p
          className="text-lg mb-6 font-medium"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          Discover, Borrow, and Enjoy Thousands of Books!
        </motion.p>
        <div className="space-y-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate("/login")}
            className="w-full bg-yellow-600 text-white px-6 py-3 rounded-lg font-bold shadow-md hover:bg-yellow-700 transition-all"
          >
            📖 Go to Login
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate("/signup")}
            className="w-full bg-brown-800 text-white px-6 py-3 rounded-lg font-bold shadow-md hover:bg-brown-900 transition-all"
          >
            📝 Sign Up
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
};

export default WelcomePage;
