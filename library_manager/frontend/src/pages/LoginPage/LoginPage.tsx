import React, { useState } from "react";
import "./LoginPage.css";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = () => {
    if (username && password) {
      alert("Logging in...");
    } else {
      alert("Both username and password are required");
    }
  };

  const redirectToSignUp = () => {
    window.location.href = "/signup";
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>Login</h1>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="input-field"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="input-field"
        />
        <button onClick={handleLogin} className="login-button">
          Login
        </button>
        <div className="signup-link">
          <p>Don't have an account?</p>
          <button onClick={redirectToSignUp} className="signup-button">
            Sign Up
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;