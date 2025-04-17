import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "./NavBar.css";

// <<< ADD: Define the default avatar URL (must match AuthContext) >>>
const DEFAULT_AVATAR_URL = "/static/images/avatars/default.svg";

const Navbar: React.FC = () => {
  // <<< CHANGE: Get avatarUrl from context >>>
  const { isLoggedIn, username, avatarUrl, userType, logout, fetchUser } = useAuth();
  const navigate = useNavigate();


  React.useEffect(() => {
    // Fetch user initially if not already fetched by context provider
    // This might be redundant if AuthProvider already fetches on load
    if (!isLoggedIn) {
        fetchUser();
    }
  }, [fetchUser, isLoggedIn]); // Depend on fetchUser and isLoggedIn

  React.useEffect(() => {
    const handlePopState = () => {
      if (!isLoggedIn) {
        // navigate("/"); // This might be too aggressive, consider just re-fetching user
        fetchUser();
      }
    };
    window.addEventListener("popstate", handlePopState);
    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, [isLoggedIn, navigate, fetchUser]); // Added fetchUser dependency

  const handleHomepageClick = () => {
    if (isLoggedIn) {
      navigate("/principal");
    } else {
      navigate("/");
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <nav className="navbar">
    <div className="nav-logo" onClick={handleHomepageClick} style={{ cursor: "pointer" }}>
        Homepage
      </div>
      <ul className="nav-links">
        <li><Link to="/contact">Contact</Link></li>
        <li><Link to="/about">About</Link></li>
         {isLoggedIn && (userType === "AD" || userType === "LB") && (
          <li>
            <Link to="/admin/users">Manage Users</Link>
          </li>
        )}
      </ul>

      <div className="nav-profile">
        {isLoggedIn ? (
          <>
            <img
              // <<< CHANGE: Use avatarUrl directly >>>
              src={avatarUrl}
              alt="User Avatar"
              className="nav-avatar"
              onClick={() => navigate("/profile")}
              style={{ cursor: "pointer" }}
              onError={(e) => {
                console.warn(`Failed to load avatar: ${avatarUrl}. Using default.`);
                // <<< CHANGE: Fallback to the default URL >>>
                (e.target as HTMLImageElement).src = DEFAULT_AVATAR_URL;
              }}
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
           <Link to="/login" className="nav-login">Login</Link>
        )}
      </div>
    </nav>
  );
};

export default Navbar;