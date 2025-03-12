import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./WelcomePage.css";

const WelcomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="WelcomePage-container">
      <section className="hero">
        <div className="hero-content">
          <motion.h1 className="hero-title">Welcome to LibManager!</motion.h1>
          <motion.img
            src="/static/images/library_seal.jpg"
            alt="LibManager Logo"
            className="hero-image"
          />
          <motion.p className="hero-description">
            Discover, Borrow, and Enjoy Thousands of Books!
          </motion.p>
          <div className="button-group">
            <motion.button onClick={() => navigate("/login")} className="primary-button">
              📖 Login
            </motion.button>
            <motion.button onClick={() => navigate("/signup")} className="secondary-button">
              📝 Sign Up
            </motion.button>
          </div>
        </div>
      </section>

 
    </div>
  );
};

export default WelcomePage;
