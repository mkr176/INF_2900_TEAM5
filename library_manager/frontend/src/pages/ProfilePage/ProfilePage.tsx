import React, { useState, useEffect } from "react";
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
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedAvatar, setSelectedAvatar] = useState("default.svg");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Fetch user data securely
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await fetch("/api/user/", {
          method: "GET",
          credentials: "include",
        });

        if (response.ok) {
          const user = await response.json();
          setUsername(user.username);
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

    fetchUserData();
  }, [navigate]);

  // Update user profile
  const saveProfile = async () => {
    try {
      const response = await fetch("/api/update-profile/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          email,
          password: password || undefined, // Only send password if changed
          avatar: selectedAvatar,
        }),
        credentials: "include",
      });

      if (response.ok) {
        alert("Profile updated successfully!");
        setIsEditing(false);
      } else {
        alert("Error updating profile.");
      }
    } catch (error) {
      console.error("Error updating profile:", error);
    }
  };

  // Logout function
  const logout = async () => {
    await fetch("/api/logout/", { method: "POST", credentials: "include" });
    navigate("/login");
  };

  return (
    <div className="profile-container">
      <h1 className="profile-title">User Profile</h1>

      {isLoading ? (
        <p>Loading...</p>
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
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
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
                  placeholder="New Password (leave blank to keep current)"
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
