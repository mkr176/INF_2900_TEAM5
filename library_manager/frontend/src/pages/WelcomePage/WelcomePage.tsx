import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./WelcomePage.css";

const WelcomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="WelcomePage-container">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <motion.h1
            className="hero-title"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 3 }}
          >
            Welcome to LibManager!
          </motion.h1>
          <motion.img
            src="/static/images/library_seal.jpg"
            alt="LibManager Logo"
            className="hero-image"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1.2 }}
            transition={{ duration: 3 }}
          />
          <motion.p
            className="hero-description"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 3, delay: 0.3 }}
          >
            Discover, Borrow, and Enjoy Thousands of Books!
          </motion.p>
          <div className="button-group">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/login")}
              className="primary-button"
            >
              📖 Login
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate("/signup")}
              className="secondary-button"
            >
              📝 Sign Up
            </motion.button>
          </div>
        </div>
      </section>

      


      
    </div>
  );
};

export default WelcomePage;