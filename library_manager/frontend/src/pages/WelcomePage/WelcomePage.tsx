import React, { useEffect } from "react"; // Import useEffect
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../../context/AuthContext"; // Import useAuth
import "./WelcomePage.css";

const WelcomePage = () => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth(); // Get login status from AuthContext

  // Add useEffect to check login status and redirect if necessary
  useEffect(() => {
    if (isLoggedIn) {
      // If the user is logged in, redirect them to the principal page
      // 'replace: true' ensures the welcome page isn't added to the history stack
      navigate("/principal", { replace: true });
    }
    // Dependency array: run this effect when isLoggedIn or navigate changes
  }, [isLoggedIn, navigate]);

  // If logged in, the component will redirect, so we can optionally return null or a loading indicator
  // to avoid rendering the welcome content briefly before redirection.
  if (isLoggedIn) {
    return null; // Or <p>Redirecting...</p>
  }

  // If not logged in, render the welcome page content
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