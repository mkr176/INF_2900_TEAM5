import React from "react";
import "./AboutPage.css";

const About: React.FC = () => {
  return (
    <div className="about-container">
      <h1 className="about-title">About Us</h1>
 

      <div className="about-content">
        <h2>Who We Are</h2>
        <p>
          Our team consists of Alvaro, Carlos, Julius & Matt, Computer Science students who is passionate about software development and teamwork.
         
        </p>

        <h2>What This Project is About</h2>
    

        <ul>
          <li>Requirement gathering and project planning</li>
          <li>Software design and implementation</li>
          <li>Testing, debugging, and maintenance</li>
          <li>Collaboration and project management</li>
          <li>Documentation and user feedback</li>
        </ul>

        <p className="about-footer">
          We are excited to build this project and improve our software engineering skills along the way!
        </p>
      </div>
    </div>
  );
};

export default About;
