import React from "react";
import "./PolicyPage.css";

const PrivacyPolicy: React.FC = () => {
  return (
    <div className="privacy-container">
      <h1>Privacy Policy</h1>
      <p>Last updated: March 19, 2025</p>
      
      <section>
        <h2>1. Introduction</h2>
        <p>Welcome to our website. Your privacy is important to us, and this Privacy Policy explains how we collect, use, and safeguard your information.</p>
      </section>
      
      <section>
        <h2>2. Information We Collect</h2>
        <ul>
          <li>Personal Information: emails, name</li>
          <li>Usage Data: books borrowed, books you search, time spent on website</li>
          <li>Cookies and Tracking Technologies</li>
        </ul>
      </section>
      
      <section>
        <h2>3. How We Use Your Information</h2>
        <p>We use collected data to enhance your experience, provide support, improve our services, and comply with legal obligations.</p>
      </section>
      
      <section>
        <h2>4. Your Rights</h2>
        <p>You have the right to access, modify, or delete your data. Contact us for any requests regarding your personal information.</p>
      </section>
      
      <section>
        <h2>5. Security</h2>
        <p>We implement security measures to protect your data. However, no method of transmission over the Internet is 100% secure.</p>
      </section>
      
      <section>
        <h2>6. Contact Us</h2>
        <p>If you have any questions about this Privacy Policy, please contact us at support@libmanager.com or call us +47 123 456 789</p>
      </section>
    </div>
  );
};

export default PrivacyPolicy;
