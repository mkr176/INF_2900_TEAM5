import React from "react";
import "./ServicePage.css";

const TermsOfService: React.FC = () => {
  return (
    <div className="terms-container">
      <h1>Terms of Service</h1>
      <p>Last updated: March 19, 2025</p>

      <section>
        <h2>1. Introduction</h2>
        <p>Welcome to LibManager. By accessing or using our services, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use our services.</p>
      </section>

      <section>
        <h2>2. User Responsibilities</h2>
        <ul>
          <li>Users must provide accurate and up-to-date registration details.</li>
          <li>Books must be returned within the specified loan period to avoid late fees.</li>
          <li>Users are responsible for any damage or loss of borrowed books and may be charged accordingly.</li>
          <li>Users must respect other library members and maintain a quiet environment.</li>
        </ul>
      </section>

      <section>
        <h2>3. Library Usage Rules</h2>
        <p>Library resources, including books, digital content, and study spaces, must be used responsibly. Misuse of library resources, including vandalism, theft, or unauthorized distribution of digital content, may result in temporary or permanent suspension of access.</p>
      </section>

      <section>
        <h2>4. Account and Membership</h2>
        <p>To access certain features, users may need to create an account. Users agree to maintain the confidentiality of their account credentials and are responsible for any activities conducted under their account.</p>
      </section>

      <section>
        <h2>5. Borrowing and Returning Books</h2>
        <ul>
          <li>Each user has a borrowing limit based on their membership type.</li>
          <li>Overdue books will incur a late fee, and users with excessive overdue books may have borrowing privileges suspended.</li>
          <li>Renewals are subject to availability and library policies.</li>
        </ul>
      </section>

      <section>
        <h2>6. Account Termination</h2>
        <p>LibManager reserves the right to terminate or suspend accounts that violate our policies. Users who repeatedly fail to comply with library rules may be permanently banned.</p>
      </section>

      <section>
        <h2>7. Privacy and Data Usage</h2>
        <p>We value your privacy. Your data is stored securely and used only for library-related services. Please refer to our <a href="/policy">Privacy Policy</a> for more details.</p>
      </section>

      <section>
        <h2>8. Changes to Terms</h2>
        <p>We may update these terms periodically. Continued use of our service implies acceptance of the new terms. Users will be notified of any significant changes.</p>
      </section>

      <section>
        <h2>9. Contact Us</h2>
        <p>If you have any questions regarding these Terms of Service, please contact us at support@libmanager.com or call +47 123 456 789.</p>
      </section>
    </div>
  );
};

export default TermsOfService;
