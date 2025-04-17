import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";  // ✅ Import AuthContext
import "./NavBar.css";

const Navbar: React.FC = () => {
  const { isLoggedIn, username, avatar, userType, logout, fetchUser } = useAuth(); // Correctly using context
  const navigate = useNavigate();

  
  React.useEffect(() => {
    fetchUser();
  }, [fetchUser]);
 
  React.useEffect(() => {
    const handlePopState = () => {
      // Re-check login status on popstate, as context might have updated
      if (!isLoggedIn) {
        navigate("/");
      }
    };

    window.addEventListener("popstate", handlePopState);

    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
    // Re-run if isLoggedIn changes
  }, [isLoggedIn, navigate]);
  const handleHomepageClick = () => {
    if (isLoggedIn) {
      navigate("/principal");
    } else {
      navigate("/");
    }
  };

  // Updated logout handler
  const handleLogout = async () => { // Make async to await logout if needed
    await logout(); // Call context logout function
    navigate("/"); // Navigate to home page after logout completes
    // Removed window.history.pushState - let context and navigation handle state
  };

  return (
    <nav className="navbar">
    <div className="nav-logo" onClick={handleHomepageClick} style={{ cursor: "pointer" }}>
        Homepage
      </div>
      <ul className="nav-links">
        <li><Link to="/contact">Contact</Link></li>
        <li><Link to="/about">About</Link></li>
        

         {/* ✅ Add User Management button for Admins and Librarians */}
         {isLoggedIn && (userType === "AD" || userType === "LB") && (
          <li>
            <Link to="/admin/users">Manage Users</Link>
          </li>
        )}
      
      </ul>

      {/* Right-aligned profile info */}
      <div className="nav-profile">
        {isLoggedIn ? (
          <>
            <img
              // <<< CHANGE: Remove hardcoded prefix >>>
              // src={`/static/images/${avatar}`} // Old line
              src={avatar} // Use avatar path from context directly
              alt="User Avatar"
              className="nav-avatar"
              onClick={() => navigate("/profile")}  
              style={{ cursor: "pointer" }}  
              // Add error handling for image loading
              onError={(e) => {
                console.warn(`Failed to load avatar: ${avatar}. Using default.`);
                // Optionally set to a known default static image path if needed
                (e.target as HTMLImageElement).src = '/static/images/avatars/default.svg'; // Fallback to a known static default
              }}
            />
            <span
              className="nav-username"
              onClick={() => navigate("/profile")} 
              style={{ cursor: "pointer" }} 
            >
              {username} {/* Use username from context */}
            </span>
            {/* Use updated handleLogout */}
            <button onClick={handleLogout} className="nav-logout">Logout</button>
          </>
        ) : (
          // <<< SUGGESTION: Add a Login link/button here for better UX >>>
          // Example: <Link to="/login" className="nav-login">Login</Link>
          <span className="nav-username">Not logged in</span>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
