import React from "react";

import "./ContactPage.css";

const ContactPage = () => {
  const teamMembers = [
    {
      name: "Alvario",
      role: "Software Engineer",
      email: "alvario@uit.no",
      phone: "+47 123 45 671",
    },
    
    {
        name: "Carlos",
        role: "Software Engineer",
        email: "carlos@uit.no",
        phone: "+47 123 45 672",
    },

    {
      name: "Julius",
      role: "Software Engineer",
      email: "julius@uit.no",
      phone: "+47 123 45 672",
    },
    {
      name: "Matt Ricote Kristiansen",
      role: "Software Engineer",
      email: "matt@uit.no",
      phone: "+47 123 45 673",
    },
  ];

  return (
    <div className="contact-container">
      <h1 className="contact-title">Meet the Team</h1>
      <p className="contact-subtitle">
        Get to know the developers behind LibManager.
      </p>

      <div className="contact-grid">
        {teamMembers.map((member, index) => (
          <div key={index} className="contact-card">
            <h2>{member.name}</h2>
            <p>{member.role}</p>
            <p>
              <strong>Email:</strong> <a href={`mailto:${member.email}`}>{member.email}</a>
            </p>
            <p>
              <strong>Phone:</strong> {member.phone}
            </p>
          </div>
        ))}
      </div>

    </div>
  );
};

export default ContactPage;