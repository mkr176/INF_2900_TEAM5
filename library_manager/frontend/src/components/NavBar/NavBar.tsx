import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";  // ✅ Import AuthContext
import "./NavBar.css";

const Navbar: React.FC = () => {
  const { isLoggedIn, username, avatar, userType, logout,fetchUser } = useAuth();
  const navigate = useNavigate();

  
  React.useEffect(() => {
    fetchUser();
  }, [fetchUser]);
 
  React.useEffect(() => {
    const handlePopState = () => {
      if (!isLoggedIn) {
        navigate("/");
      }
    };

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, [isLoggedIn, navigate]);
  const handleHomepageClick = () => {
    if (isLoggedIn) {
      navigate("/principal");
    } else {
      navigate("/");
    }
  };
  const handleLogout = () => {
    logout();
    navigate("/");
    window.history.pushState(null, "", "/");
  };

  return (
    <nav className="navbar">
    <div className="nav-logo" onClick={handleHomepageClick} style={{ cursor: "pointer" }}>
        Homepage
      </div>      <ul className="nav-links">
        <li><Link to="/contact">Contact</Link></li>
        <li><Link to="/about">About</Link></li>
        <li><Link to="/admin/users">Manage Users</Link></li>

         {/* ✅ Add User Management button for Admins and Librarians */}
         {isLoggedIn && (userType === "AD" || userType === "LB") && (
          <li>
            <button
              onClick={() => navigate("/admin/users")}
              className="nav-button"
            >
              Manage Users
            </button>
          </li>
        )}
      
      </ul>

      {/* Right-aligned profile info */}
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
            <button onClick={handleLogout} className="nav-logout">Logout</button>
          </>
        ) : (
          <span className="nav-username">Not logged in</span>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
