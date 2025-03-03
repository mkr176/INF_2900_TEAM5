import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./LoginPage/LoginPage";
import SignUpPage from "./SignUpPage/SignUpPage";
import WelcomePage from "./WelcomePage/WelcomePage";
import PrincipalPage from "./PrincipalPage/PrincipalPage"; // Importa PrincipalPage

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/principal" element={<PrincipalPage />} /> {/* Agrega esta línea */}
      </Routes>
    </Router>
  );
};

export default App;
