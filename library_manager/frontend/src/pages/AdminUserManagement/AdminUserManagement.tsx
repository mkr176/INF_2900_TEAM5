import React, { useEffect, useState, useCallback } from "react"; // Added useCallback
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext"; // Import useAuth
import "./AdminUserManagement.css";

// Define interfaces based on backend serializers
interface UserProfile {
  user_id: number;
  username: string;
  type: string; // 'AD', 'US', 'LB'
  age: number | null;
  avatar: string | null;
  get_type_display: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile: UserProfile | null; // Profile can be null
  date_joined: string;
  is_staff: boolean;
}


const AdminUserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  // Get user info and CSRF token function from AuthContext
  const { currentUser, userType, getCSRFToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check authorization on component mount and when userType changes
  useEffect(() => {
    if (!currentUser) {
      // If currentUser is null (still loading or not logged in), wait or redirect
      // Add a small delay or check loading state if needed
      const timer = setTimeout(() => {
        if (!currentUser) { // Check again
             alert("Please log in to access this page.");
             navigate("/login");
        }
      }, 500); // Adjust delay if needed
      return () => clearTimeout(timer);
    } else if (userType !== "AD" && userType !== "LB") {
      alert("Access denied: Only admins or librarians can manage users.");
      navigate("/principal"); // Redirect to a safe page
    } else {
      // User is authorized, proceed to fetch users
      fetchUsers();
    }
    // Depend on currentUser and userType
  }, [currentUser, userType, navigate]); // Removed fetchUsers from here

  // Function to fetch users (now called from useEffect after auth check)
  const fetchUsers = useCallback(async () => { // Wrap in useCallback
    setLoading(true);
    try {
      // Use the correct endpoint from urls.py
      const res = await fetch("/api/users/"); // GET request is default
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data: User[] = await res.json();

      // Filter based on current user type (Admins see all, Librarians see non-Admins)
      // Backend UserListView doesn't filter, so we do it here.
      if (userType === "LB") {
        // Librarians can only see regular users ('US') and other librarians ('LB')?
        // Or just 'US'? Let's assume they can see 'US' and 'LB' but not 'AD'.
        setUsers(data.filter((user: User) => user.profile?.type !== "AD"));
      } else {
        // Admins see all users returned by the API
        setUsers(data);
      }
    } catch (error) {
      console.error("Failed to fetch users:", error);
      alert("Failed to load users. Please try again later.");
      setUsers([]); // Clear users on error
    } finally {
      setLoading(false);
    }
    // Depend on userType for filtering logic
  }, [userType]); // Add userType dependency

  const handleDelete = async (userId: number) => {
    // Prevent users from deleting themselves (optional, but good practice)
    if (currentUser && userId === currentUser.id) {
        alert("You cannot delete your own account from this panel.");
        return;
    }

    const userToDelete = users.find(user => user.id === userId);
    if (!userToDelete) return;

    // Confirmation dialog
    const confirmDelete = window.confirm(
      `Are you sure you want to delete the user "${userToDelete.username}"? This action cannot be undone.`
    );
    if (!confirmDelete) return;

    // Get CSRF token using the context function
    const csrfToken = await getCSRFToken();
    if (!csrfToken) {
      alert("Error: Could not verify security token. Please refresh and try again.");
      return;
    }

    try {
      // Use the correct endpoint and method from urls.py
      const res = await fetch(`/api/users/${userId}/`, {
        method: "DELETE",
        headers: {
          "X-CSRFToken": csrfToken, // Use the token from context
        },
        credentials: "include", // Include cookies if needed by session auth
      });

      if (res.ok) {
        // Successfully deleted on backend, remove from frontend state
        setUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId));
        alert(`User "${userToDelete.username}" deleted successfully.`);
      } else {
        // Handle specific errors from backend if possible
        let errorMsg = `Failed to delete user "${userToDelete.username}".`;
        try {
          const err = await res.json();
          // Use DRF's 'detail' field or flatten errors
          if (err.detail) {
              errorMsg += ` Error: ${err.detail}`;
          } else if (typeof err === 'object') {
               errorMsg += ` Errors: ${JSON.stringify(err)}`;
          }
        } catch (e) {
          // Ignore if response is not JSON
          errorMsg += ` Status: ${res.status}`;
        }
        alert(errorMsg);
      }
    } catch (error) {
      console.error("Error deleting user:", error);
      alert(`An error occurred while deleting user "${userToDelete.username}".`);
    }
  };

  // Removed useEffect(() => { if (currentUser) fetchUsers(); }, [currentUser]);
  // fetchUsers is now called within the authorization useEffect

  if (loading) return <p>Loading users...</p>;

  // Ensure currentUser is available before rendering the main content
  if (!currentUser || (userType !== "AD" && userType !== "LB")) {
      // This should ideally not be reached due to the useEffect checks, but acts as a fallback
      return <p>Access Denied or User Not Loaded.</p>;
  }


  return (
    <div className="admin-user-container">
      <h1 className="admin-user-title">
        {/* Title based on the actual userType from context */}
        {userType === "AD" ? "Admin User Management" : "Librarian User Management"}
      </h1>
      {users.length === 0 ? (
        <p>No users found.</p>
      ) : (
        <div>
          {users.map((user) => (
            <div key={user.id} className="user-card">
              <div className="user-info">
              <img
                // <<< CHANGE: Remove hardcoded prefix and handle potential null >>>
                // src={`/static/images/${user.profile?.avatar || "avatars/default.svg"}`} // Old line
                src={user.profile?.avatar || '/static/images/avatars/default.svg'} // Use avatar directly, provide default if null/undefined
                alt={`${user.username}'s avatar`}
                className="user-avatar"
                // Add error handling for image loading
                onError={(e) => {
                  console.warn(`Failed to load avatar for user ${user.username}: ${user.profile?.avatar}. Using default.`);
                  // Fallback to a known static default
                  (e.target as HTMLImageElement).src = '/static/images/avatars/default.svg';
                }}
                />

                <div className="user-details">
                  {/* Display username, first/last name */}
                  <p className="name">{user.username} ({user.first_name} {user.last_name})</p>
                  <p className="email">{user.email}</p>
                  {/* Display user role from profile.get_type_display */}
                  <p className="role">Role: {user.profile?.get_type_display || 'N/A'}</p>
                </div>
              </div>
              {/* Prevent deleting own user or users with higher/equal privilege for librarians */}
              {currentUser.id !== user.id && (userType === 'AD' || (userType === 'LB' && user.profile?.type === 'US')) && (
                 <button onClick={() => handleDelete(user.id)} className="delete-btn">
                    Delete
                 </button>
              )}
              {/* Optionally show a disabled button or nothing */}
              {currentUser.id === user.id && (
                 <button className="delete-btn" disabled style={{backgroundColor: 'grey', cursor: 'not-allowed'}}>Self</button>
              )}
              {userType === 'LB' && user.profile?.type !== 'US' && currentUser.id !== user.id && (
                 <button className="delete-btn" disabled style={{backgroundColor: 'grey', cursor: 'not-allowed'}}>No Access</button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

};

export default AdminUserManagement;