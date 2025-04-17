import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "./AdminUserManagement.css";

// Define interfaces based on backend serializers
interface UserProfile {
  user_id: number;
  username: string;
  type: string;
  age: number | null;
  // avatar: string | null; // Original field
  avatar_url: string | null; // Expect URL from serializer
  get_type_display: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile: UserProfile | null;
  date_joined: string;
  is_staff: boolean;
}

// <<< ADD: Define the default avatar URL (must match AuthContext) >>>
const DEFAULT_AVATAR_URL = "/static/images/avatars/default.svg";


const AdminUserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const { currentUser, userType, getCSRFToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

   // Function to fetch users
   const fetchUsers = useCallback(async () => {
    // No need to check auth here again, outer useEffect handles it
    setLoading(true);
    try {
      const res = await fetch("/api/users/", { credentials: 'include' }); // Added credentials
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data: User[] = await res.json();

      // Filter based on current user type (Admins see all, Librarians see non-Admins)
      if (userType === "LB") {
        setUsers(data.filter((user: User) => user.profile?.type !== "AD"));
      } else {
        setUsers(data);
      }
    } catch (error) {
      console.error("Failed to fetch users:", error);
      alert("Failed to load users. Please try again later.");
      setUsers([]);
    } finally {
      setLoading(false);
    }
  }, [userType]); // Depend on userType for filtering logic


  // Check authorization on component mount and when userType changes
  useEffect(() => {
    if (!currentUser) {
      const timer = setTimeout(() => {
        if (!currentUser) {
             alert("Please log in to access this page.");
             navigate("/login");
        }
      }, 500);
      return () => clearTimeout(timer);
    } else if (userType !== "AD" && userType !== "LB") {
      alert("Access denied: Only admins or librarians can manage users.");
      navigate("/principal");
    } else {
      // User is authorized, proceed to fetch users
      fetchUsers(); // Call fetchUsers here
    }
  }, [currentUser, userType, navigate, fetchUsers]); // Added fetchUsers dependency


  const handleDelete = async (userId: number) => {
    if (currentUser && userId === currentUser.id) {
        alert("You cannot delete your own account from this panel.");
        return;
    }

    const userToDelete = users.find(user => user.id === userId);
    if (!userToDelete) return;

    const confirmDelete = window.confirm(
      `Are you sure you want to delete the user "${userToDelete.username}"? This action cannot be undone.`
    );
    if (!confirmDelete) return;

    const csrfToken = await getCSRFToken();
    if (!csrfToken) {
      alert("Error: Could not verify security token. Please refresh and try again.");
      return;
    }

    try {
      const res = await fetch(`/api/users/${userId}/`, {
        method: "DELETE",
        headers: {
          "X-CSRFToken": csrfToken,
        },
        credentials: "include",
      });

      if (res.ok || res.status === 204) { // Handle 204 No Content
        setUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId));
        alert(`User "${userToDelete.username}" deleted successfully.`);
      } else {
        let errorMsg = `Failed to delete user "${userToDelete.username}".`;
        try {
          const err = await res.json();
          if (err.detail) {
              errorMsg += ` Error: ${err.detail}`;
          } else if (typeof err === 'object') {
               errorMsg += ` Errors: ${JSON.stringify(err)}`;
          }
        } catch (e) {
          errorMsg += ` Status: ${res.status}`;
        }
        alert(errorMsg);
      }
    } catch (error) {
      console.error("Error deleting user:", error);
      alert(`An error occurred while deleting user "${userToDelete.username}".`);
    }
  };


  if (loading) return <p>Loading users...</p>;

  if (!currentUser || (userType !== "AD" && userType !== "LB")) {
      return <p>Access Denied or User Not Loaded.</p>;
  }


  return (
    <div className="admin-user-container">
      <h1 className="admin-user-title">
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
                // <<< CHANGE: Use avatar_url, fallback to default URL >>>
                src={user.profile?.avatar_url || DEFAULT_AVATAR_URL}
                alt={`${user.username}'s avatar`}
                className="user-avatar"
                onError={(e) => {
                  console.warn(`Failed to load avatar for user ${user.username}: ${user.profile?.avatar_url}. Using default.`);
                  // <<< CHANGE: Fallback to the default URL >>>
                  (e.target as HTMLImageElement).src = DEFAULT_AVATAR_URL;
                }}
                />

                <div className="user-details">
                  <p className="name">{user.username} ({user.first_name} {user.last_name})</p>
                  <p className="email">{user.email}</p>
                  <p className="role">Role: {user.profile?.get_type_display || 'N/A'}</p>
                </div>
              </div>
              {/* Prevent deleting own user or users with higher/equal privilege for librarians */}
              {currentUser.id !== user.id && (userType === 'AD' || (userType === 'LB' && user.profile?.type === 'US')) && (
                 <button onClick={() => handleDelete(user.id)} className="delete-btn">
                    Delete
                 </button>
              )}
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