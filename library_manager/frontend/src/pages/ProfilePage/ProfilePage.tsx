import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext"; // ✅ Import AuthContext
import { useNavigate } from "react-router-dom";
import "./ProfilePage.css";

const avatars = [
  "account-avatar-profile-user-2-svgrepo-com.svg",
  "account-avatar-profile-user-3-svgrepo-com.svg",
  "account-avatar-profile-user-4-svgrepo-com.svg",
  "account-avatar-profile-user-5-svgrepo-com.svg",
  "account-avatar-profile-user-6-svgrepo-com.svg",
  "account-avatar-profile-user-7-svgrepo-com.svg",
  "account-avatar-profile-user-8-svgrepo-com.svg",
  "account-avatar-profile-user-9-svgrepo-com.svg",
  "account-avatar-profile-user-10-svgrepo-com.svg",
  "account-avatar-profile-user-11-svgrepo-com.svg",
  "account-avatar-profile-user-12-svgrepo-com.svg",
  "account-avatar-profile-user-13-svgrepo-com.svg",
  "account-avatar-profile-user-14-svgrepo-com.svg",
  "account-avatar-profile-user-15-svgrepo-com.svg",
  "account-avatar-profile-user-16-svgrepo-com.svg",
  "default.svg",
];

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { username, avatar, logout, fetchUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [newUsername, setNewUsername] = useState(username);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState(avatar || "default.svg");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch("/api/user/", { credentials: "include" });
        if (response.ok) {
          const user = await response.json();
          setNewUsername(user.username);
          setEmail(user.email);
          setSelectedAvatar(user.avatar || "default.svg");
        } else {
          navigate("/login");
        }
      } catch (error) {
        console.error("Error fetching user:", error);
        navigate("/login");
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  // ✅ Update user profile
  const saveProfile = async () => {
    try {
      const response = await fetch("/api/update-profile/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: newUsername !== username ? newUsername : undefined,
          email: email || undefined,
          password: password || undefined,
          avatar: selectedAvatar !== avatar ? selectedAvatar : undefined,
        }),
        credentials: "include",
      });

      if (response.ok) {
        alert("Profile updated successfully!");
        setIsEditing(false);
        fetchUser(); // ✅ Update global auth state
      } else {
        alert("Error updating profile.");
      }
    } catch (error) {
      console.error("Error updating profile:", error);
    }
  };

  return (
    <div className="profile-container">
      <h1 className="profile-title">User Profile</h1>

      {isLoading ? (
        <p className="loading-text">Loading...</p>
      ) : (
        <>
          <div className="profile-card">
            <img
              src={`/static/images/avatars/${selectedAvatar}`}
              alt="User Avatar"
              className="profile-avatar"
            />
            {isEditing ? (
              <>
                <input
                  type="text"
                  className="profile-input"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="Username"
                />
                <input
                  type="email"
                  className="profile-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email"
                />
                <input
                  type="password"
                  className="profile-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="New Password (optional)"
                />
              </>
            ) : (
              <>
                <h2 className="profile-username">{username}</h2>
                <p className="profile-email">{email}</p>
              </>
            )}
          </div>

          {isEditing && (
            <>
              <h3 className="avatar-selection-title">Choose Your Avatar</h3>
              <div className="avatar-grid">
                {avatars.map((avatar, index) => (
                  <img
                    key={index}
                    src={`/static/images/avatars/${avatar}`}
                    alt="Avatar Option"
                    className={`avatar-option ${
                      selectedAvatar === avatar ? "selected" : ""
                    }`}
                    onClick={() => setSelectedAvatar(avatar)}
                  />
                ))}
              </div>
            </>
          )}

          <div className="profile-actions">
            {isEditing ? (
              <>
                <button className="save-button" onClick={saveProfile}>
                  Save Changes
                </button>
                <button className="cancel-button" onClick={() => setIsEditing(false)}>
                  Cancel
                </button>
              </>
            ) : (
              <button className="edit-button" onClick={() => setIsEditing(true)}>
                Edit Profile
              </button>
            )}
            <button className="logout-button" onClick={logout}>
              Logout
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ProfilePage;
