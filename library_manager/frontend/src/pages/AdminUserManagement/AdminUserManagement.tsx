import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminUserManagement.css";

interface User {
  id: number;
  name: string;
  email: string;
  avatar: string;
  type: string; // AD, LB, US
}

const AdminUserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [currentUser, setCurrentUser] = useState<{ username: string; type: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const getCookie = (name: string) => {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? match[2] : null;
  };

  const fetchCurrentUser = async () => {
    const res = await fetch("/api/current_user/");
    if (res.ok) {
      const data = await res.json();
      setCurrentUser(data);
      if (data.type !== "AD" && data.type !== "LB") {
        alert("Access denied: Only admins or librarians can manage users.");
        navigate("/");
      }
    } else {
      alert("You are not logged in.");
      navigate("/login");
    }
  };

  const fetchUsers = async () => {
    const res = await fetch("/api/users/");
    const data = await res.json();

    // Filter based on current user type
    if (currentUser?.type === "LB") {
      // Librarians can only see regular users
      setUsers(data.filter((user: User) => user.type === "US"));
    } else {
      // Admins can see all users
      setUsers(data);
    }

    setLoading(false);
  };

  const handleDelete = async (userId: number) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this user?");
    if (!confirmDelete) return;

    const res = await fetch(`/api/user/${userId}/delete/`, {

      method: "DELETE",
      headers: {
        "X-CSRFToken": getCookie("csrftoken") || "",
      },
    });

    if (res.ok) {
      setUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId));
    } else {
      const err = await res.json();
      alert("Failed to delete user: " + err.error);
    }
  };

  useEffect(() => {
    const init = async () => {
      await fetchCurrentUser();  // Wait to know user type
    };
    init();
  }, []);

  useEffect(() => {
    if (currentUser) fetchUsers();
  }, [currentUser]);

  if (loading) return <p>Loading users...</p>;

  return (
    <div className="admin-user-container">
      <h1 className="admin-user-title">
        {currentUser?.type === "AD" ? "Admin User Management" : "Librarian User Management"}
      </h1>
      {users.length === 0 ? (
        <p>No users found.</p>
      ) : (
        <div>
          {users.map((user) => (
            <div key={user.id} className="user-card">
              <div className="user-info">
              <img
                src={`/static/images/avatars/${user.avatar?.trim() ? user.avatar : "default.svg"}`}
                alt="avatar"
                className="user-avatar"
                />

                <div className="user-details">
                  <p className="name">{user.name}</p>
                  <p className="email">{user.email}</p>
                  <p className="role">Role: {user.type}</p>
                </div>
              </div>
              <button onClick={() => handleDelete(user.id)} className="delete-btn">
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
  
};

export default AdminUserManagement;
