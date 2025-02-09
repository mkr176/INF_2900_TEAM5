import React from "react";
import { useNavigate } from "react-router-dom";
import "./WelcomePage.css";

const WelcomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="welcome-container">
      <h1>Welcome to LibManager!</h1>
      <img src="/static/images/library_seal.jpg" alt="LibManager Logo" width="200" />
      <p>Your Library Management System</p>
      <button onClick={() => navigate("/login")}>Go to Login</button>
      <button onClick={() => navigate("/signup")}>Sign Up</button>
    </div>
  );
};

export default WelcomePage;
