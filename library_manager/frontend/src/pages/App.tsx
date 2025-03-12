import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./LoginPage/LoginPage";
import SignUpPage from "./SignUpPage/SignUpPage";
import WelcomePage from "./WelcomePage/WelcomePage";
import PrincipalPage from "./PrincipalPage/PrincipalPage";
import ContactPage from "./ContactPage/ContactPage";
import AboutPage from "./AboutPage/AboutPage";

import Footer from "../components/Footer/Footer"; // Import the Footer component
import NavBar from "../components/NavBar/NavBar";
import "./App.css";

const App = () => {
  return (
    <Router>
      <NavBar />
      <div className="app-container"> {/* Ensures content fills available space */}
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/principal" element={<PrincipalPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </div>
      <Footer /> {/* Footer always at bottom */}
    </Router>
  );
};

export default App;
