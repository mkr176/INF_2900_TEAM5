import React from "react";
import { useNavigate } from "react-router-dom";
import "./Footer.css";

const Footer = () => {
  const navigate = useNavigate();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-column">
          <h3>About LibManager</h3>
          <p>
            LibManager is designed to make library<br />
            management seamless and efficient.<br />
            It helps both users and librarians.
          </p>
        </div>
        <div className="footer-column">
          <h3>Quick Links</h3>
          <ul>
            <li onClick={() => navigate("/about")}>About Us</li>
            <li onClick={() => navigate("/contact")}>Contact</li>
            <li onClick={() => navigate("/privacy")}>Privacy Policy</li>
            <li onClick={() => navigate("/terms")}>Terms of Service</li>
          </ul>
        </div>
        <div className="footer-column">
          <h3>Contact Us</h3>
          <p>Email: support@libmanager.com</p>
          <p>Phone: +47 123 456 789</p>
        </div>
      </div>
      <div className="footer-bottom">
        &copy; 2025 LibManager. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
