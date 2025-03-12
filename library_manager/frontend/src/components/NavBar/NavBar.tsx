import React from "react";
import { Link } from "react-router-dom";
import "./NavBar.css";

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <Link to="/" className="nav-logo">Homepage</Link>
      <ul className="nav-links">
        <li><Link to="/contact">Contact</Link></li>
        <li><Link to="/about">About</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar;
