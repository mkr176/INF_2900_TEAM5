import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";  // ✅ Import AuthContext
import "./NavBar.css";

const Navbar: React.FC = () => {
  const { isLoggedIn, username, avatar, logout, fetchUser } = useAuth();
  const navigate = useNavigate();

  
  React.useEffect(() => {
    fetchUser();
  }, []);

  return (
    <nav className="navbar">
      <Link to="/" className="nav-logo">Homepage</Link>
      <ul className="nav-links">
        <li><Link to="/contact">Contact</Link></li>
        <li><Link to="/about">About</Link></li>
      </ul>

      {/* ✅ Right-aligned profile info */}
      <div className="nav-profile">
        {isLoggedIn ? (
          <>
            <img
              src={`/static/images/avatars/${avatar}`}
              alt="User Avatar"
              className="nav-avatar"
              onClick={() => navigate("/profile")}  
              style={{ cursor: "pointer" }}  
            />
            <span
              className="nav-username"
              onClick={() => navigate("/profile")} 
              style={{ cursor: "pointer" }} 
            >
              {username}
            </span>
            <button onClick={logout} className="nav-logout">Logout</button>
          </>
        ) : (
          <span className="nav-username">Not logged in</span>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
