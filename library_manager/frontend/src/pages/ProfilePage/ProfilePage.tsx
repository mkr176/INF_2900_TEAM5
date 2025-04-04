import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext"; // ✅ Import AuthContext
import AvatarSelector from "../../components/AvatarSelector/AvatarSelector";
// Removed UserCard import as it wasn't used
import { useNavigate } from "react-router-dom";
import "./ProfilePage.css";

// Removed avatars array as it's handled within AvatarSelector

const MIN_PASSWORD_LENGTH = 6; // Define minimum password length
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Basic email format regex

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  // Get username directly from context, it won't be editable locally
  const { username, avatar, logout, fetchUser } = useAuth();

  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // State for editable fields (excluding username)
  const [email, setEmail] = useState("");
  const [originalEmail, setOriginalEmail] = useState(""); // Store the initial email
  const [newPassword, setNewPassword] = useState(""); // For entering a new password
  const [currentPassword, setCurrentPassword] = useState(""); // Required for email/password changes
  const [selectedAvatar, setSelectedAvatar] = useState("default.svg"); // Use context avatar initially

  useEffect(() => {
    // Initialize avatar from context
    setSelectedAvatar(avatar || "default.svg");

    // Then fetch detailed profile data
    const fetchProfile = async () => {
      setIsLoading(true); // Start loading
      try {
        const response = await fetch("/api/user/", { credentials: "include" });
        if (response.ok) {
          const user = await response.json();
          // Set email and avatar from fetched data
          setEmail(user.email || "");
          setOriginalEmail(user.email || "");
          setSelectedAvatar(user.avatar || avatar || "default.svg");
          // Username comes from context, no need to set it here
        } else {
          // If fetching fails (e.g., not logged in), rely on context or redirect
          if (!username) { // Check if context also lacks username
          navigate("/login");
          }
        }
      } catch (error) {
        console.error("Error fetching user:", error);
        if (!username) { // Check if context also lacks username
        navigate("/login");
        }
      } finally {
        setIsLoading(false); // Stop loading
      }
    };

    fetchProfile();
    // Depend on context values changing as well
  }, [navigate, username, avatar]); // Rerun if context changes or navigate function changes

  const handleCancel = () => {
    setIsEditing(false);
    // Reset fields to their original values
    setEmail(originalEmail);
    setSelectedAvatar(avatar || "default.svg");
    setNewPassword(""); // Clear password fields
    setCurrentPassword(""); // Clear password fields
  };

  const saveProfile = async () => {
    const isEmailChanged = email !== originalEmail;
    const isPasswordChanged = newPassword !== "";
    // Username change is no longer tracked
    const isAvatarChanged = selectedAvatar !== avatar;

    // --- Validation ---
    if (isEmailChanged || isPasswordChanged) {
      if (!currentPassword) {
        alert("Please enter your current password to change email or password.");
        return;
      }
    }

    if (isEmailChanged) {
      if (!EMAIL_REGEX.test(email)) {
        alert("Please enter a valid email address.");
        return;
      }
    }

    if (isPasswordChanged) {
      if (newPassword.length < MIN_PASSWORD_LENGTH) {
        alert(`New password must be at least ${MIN_PASSWORD_LENGTH} characters long.`);
        return;
      }
    }

    // --- Payload Construction ---
    const payload: { [key: string]: string } = {};
    // Do not include username in payload
    if (isEmailChanged) payload.email = email;
    if (isPasswordChanged) payload.new_password = newPassword;
    if (isAvatarChanged) payload.avatar = selectedAvatar;
    if (isEmailChanged || isPasswordChanged) payload.current_password = currentPassword;

    // Check if there's anything to update
    if (Object.keys(payload).length === 0 || (Object.keys(payload).length === 1 && payload.current_password)) {
        // Adjust check: only check if email, password, or avatar changed
        if (!isEmailChanged && !isPasswordChanged && !isAvatarChanged) {
            alert("No changes detected.");
            setIsEditing(false); // Exit edit mode if no changes
            return;
        }
    }


    // --- API Call ---
    try {
      const response = await fetch("/api/update-profile/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        credentials: "include",
      });

      const responseData = await response.json(); // Try to get response data regardless of status
  
      if (response.ok) {
        alert("Profile updated successfully!");
        if (isEmailChanged) {
          setOriginalEmail(email); // Update original email state if change was successful
        }
        setNewPassword(""); // Clear password fields on success
        setCurrentPassword("");
        setIsEditing(false);
        fetchUser(); // Refresh auth context (updates navbar etc.)
      } else {
        // Display specific error from backend if available
        alert(`Error updating profile: ${responseData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Error updating profile:", error);
      alert("An error occurred while updating the profile.");
    }
  };
  
  // Determine if current password input should be shown
  const showCurrentPasswordInput = isEditing && (email !== originalEmail || newPassword !== "");

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
            {/* Display username from context always */}
            <h2 className="profile-username">{username}</h2>

            {isEditing ? (
              <>
                {/* Removed username input */}
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
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="New Password (leave blank to keep current)"
                />
                {/* Conditionally render Current Password input */}
                {showCurrentPasswordInput && (
                   <input
                     type="password"
                     className="profile-input"
                     value={currentPassword}
                     onChange={(e) => setCurrentPassword(e.target.value)}
                     placeholder="Current Password (required)"
                />
                )}
              </>
            ) : (
              <>
                {/* Display current email when not editing */}
                <p className="profile-email">{originalEmail}</p>
              </>
            )}
          </div>

            {isEditing && (
              <>
                <h3 className="avatar-selection-title">Choose Your Avatar</h3>
                <AvatarSelector selectedAvatar={selectedAvatar} onSelectAvatar={setSelectedAvatar} />
              </>
            )}

          <div className="profile-actions">
            {isEditing ? (
              <>
                <button className="save-button" onClick={saveProfile}>
                  Save Changes
                </button>
                {/* Use handleCancel for the Cancel button */}
                <button className="cancel-button" onClick={handleCancel}>
                  Cancel
                </button>
              </>
            ) : (
              <button className="edit-button" onClick={() => setIsEditing(true)}>
                Edit Profile
              </button>
            )}
            {/* Logout button now uses logout from AuthContext */}
            <button className="logout-button" onClick={() => { logout(); navigate('/'); }}>
              Logout
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ProfilePage;
