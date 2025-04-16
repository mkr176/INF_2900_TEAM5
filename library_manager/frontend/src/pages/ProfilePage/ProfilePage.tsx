import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext"; // ✅ Use AuthContext
import AvatarSelector from "../../components/AvatarSelector/AvatarSelector";
import { useNavigate } from "react-router-dom";
import "./ProfilePage.css";

// Constants (can be moved to a config file)
const MIN_PASSWORD_LENGTH = 8; // Match backend validator if possible
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  // Get user data, logout, fetchUser, and CSRF token function from context
  const { currentUser, logout, fetchUser, getCSRFToken } = useAuth();

  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(!currentUser); // Start loading if currentUser isn't available yet

  // State for editable fields, initialized from context
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [newPassword, setNewPassword] = useState(""); // For entering a new password
  // Removed currentPassword state - not sending it based on backend view logic
  const [selectedAvatar, setSelectedAvatar] = useState("avatars/default.svg"); // Default

  // Store original values to compare for changes
  const [originalEmail, setOriginalEmail] = useState("");
  const [originalFirstName, setOriginalFirstName] = useState("");
  const [originalLastName, setOriginalLastName] = useState("");
  const [originalAvatar, setOriginalAvatar] = useState("avatars/default.svg");

  useEffect(() => {
    setIsLoading(!currentUser); // Update loading state based on currentUser availability
    if (currentUser) {
      // Initialize state from currentUser when it becomes available or changes
      const userEmail = currentUser.email || "";
      const userFirstName = currentUser.first_name || "";
      const userLastName = currentUser.last_name || "";
      // Ensure avatar path is relative to the expected static/media root
      const userAvatar = currentUser.profile?.avatar || "avatars/default.svg";

      setEmail(userEmail);
      setOriginalEmail(userEmail);
      setFirstName(userFirstName);
      setOriginalFirstName(userFirstName);
      setLastName(userLastName);
      setOriginalLastName(userLastName);
      setSelectedAvatar(userAvatar);
      setOriginalAvatar(userAvatar);
      setIsLoading(false); // Stop loading once data is set
    } else {
      // If no currentUser after initial load, maybe redirect
      // Add a small delay or check loading state to prevent premature redirect
      const timer = setTimeout(() => {
        if (!currentUser && !isLoading) { // Check again after a brief moment
             console.log("No current user found, redirecting to login.");
             // navigate("/login"); // Consider redirecting if user data isn't loaded
        }
      }, 500); // Adjust delay as needed
      return () => clearTimeout(timer);
    }
    // Depend on currentUser object changes
  }, [currentUser, isLoading, navigate]); // Added isLoading and navigate

  const handleCancel = () => {
    setIsEditing(false);
    // Reset fields to their original values from context/state
    setEmail(originalEmail);
    setFirstName(originalFirstName);
    setLastName(originalLastName);
    setSelectedAvatar(originalAvatar);
    setNewPassword(""); // Clear password field
  };

  const saveProfile = async () => {
    const isEmailChanged = email !== originalEmail;
    const isFirstNameChanged = firstName !== originalFirstName;
    const isLastNameChanged = lastName !== originalLastName;
    const isPasswordChanged = newPassword !== "";
    const isAvatarChanged = selectedAvatar !== originalAvatar;

    // --- Validation ---
    if (isEmailChanged && !EMAIL_REGEX.test(email)) {
      alert("Please enter a valid email address.");
      return;
    }

    if (isPasswordChanged && newPassword.length < MIN_PASSWORD_LENGTH) {
      alert(`New password must be at least ${MIN_PASSWORD_LENGTH} characters long.`);
      return;
    }

    // Check if any actual changes were made
    if (!isEmailChanged && !isFirstNameChanged && !isLastNameChanged && !isPasswordChanged && !isAvatarChanged) {
      alert("No changes detected.");
      setIsEditing(false); // Exit edit mode
      return;
    }

    // --- Get CSRF Token ---
    const csrfToken = await getCSRFToken();
    if (!csrfToken) {
      alert("Error: Could not verify security token. Please refresh and try again.");
      return;
    }

    // --- Payload Construction ---
    const payload: { [key: string]: any } = {}; // Use 'any' or a specific interface
    const profilePayload: { [key: string]: any } = {};

    if (isEmailChanged) payload.email = email;
    if (isFirstNameChanged) payload.first_name = firstName;
    if (isLastNameChanged) payload.last_name = lastName;
    if (isPasswordChanged) payload.password = newPassword; // Send new password as 'password'

    // Avatar is part of the profile
    if (isAvatarChanged) profilePayload.avatar = selectedAvatar;
    // Add other profile fields here if they become editable (e.g., age)
    // if (isAgeChanged) profilePayload.age = age;

    // Only include the 'profile' key if there are profile changes
    if (Object.keys(profilePayload).length > 0) {
      payload.profile = profilePayload;
    }

    // --- API Call ---
    setIsLoading(true); // Indicate loading state
    try {
      // <<< CHANGE: Use PATCH and the correct endpoint >>>
      const response = await fetch("/api/users/me/update/", {
        method: "PATCH", // Use PATCH for partial updates
        headers: {
          "Content-Type": "application/json",
          // <<< CHANGE: Include CSRF token >>>
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
        credentials: "include", // Send cookies
      });

      // Try to parse JSON regardless of status code for error details
      let responseData;
      try {
          responseData = await response.json();
      } catch (e) {
          responseData = { detail: `Update failed with status: ${response.status}` }; // Default error if JSON parsing fails
      }


      if (response.ok) {
        alert("Profile updated successfully!");
        // Update original values *after* successful save
        if (isEmailChanged) setOriginalEmail(email);
        if (isFirstNameChanged) setOriginalFirstName(firstName);
        if (isLastNameChanged) setOriginalLastName(lastName);
        if (isAvatarChanged) setOriginalAvatar(selectedAvatar);

        setNewPassword(""); // Clear password field on success
        setIsEditing(false);
        await fetchUser(); // Refresh auth context to get the very latest data
      } else {
        // Display specific error from backend if available
        let errorMsg = "Error updating profile.";
        if (responseData && typeof responseData === 'object') {
             errorMsg = Object.entries(responseData)
               .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
               .join('\n');
        }
        alert(errorMsg);
      }
    } catch (error) {
      console.error("Error updating profile:", error);
      alert("An network error occurred while updating the profile.");
    } finally {
      setIsLoading(false); // Stop loading indicator
    }
  };

  // Render loading state
  if (isLoading && !currentUser) { // Show loading only if currentUser isn't available yet
     return <div className="profile-container"><p className="loading-text">Loading Profile...</p></div>;
  }

  // Handle case where user data couldn't be loaded (e.g., not logged in)
  if (!currentUser) {
     // This part might be reached briefly before redirect or if context fails
     return <div className="profile-container"><p>Could not load user profile. Please <button onClick={() => navigate('/login')}>log in</button>.</p></div>;
  }


  return (
    <div className="profile-container">
      {/* Use username from context */}
      <h1 className="profile-title">{currentUser.username}'s Profile</h1>

      <div className="profile-card">
        <img
          // Construct full URL if needed, otherwise relative path
          src={`/static/images/${selectedAvatar}`} // Use state variable for avatar
          alt="User Avatar"
          className="profile-avatar"
        />
        {/* Display username from context */}
        <h2 className="profile-username">{currentUser.username}</h2>

        {isEditing ? (
          <>
            {/* First Name Input */}
            <input
              type="text"
              className="profile-input"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="First Name"
            />
            {/* Last Name Input */}
            <input
              type="text"
              className="profile-input"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Last Name"
            />
            {/* Email Input */}
            <input
              type="email"
              className="profile-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
            />
            {/* New Password Input */}
            <input
              type="password"
              className="profile-input"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="New Password (leave blank to keep)"
            />
            {/* Removed Current Password input */}
          </>
        ) : (
          <>
            {/* Display current info when not editing */}
            <p className="profile-info">{originalFirstName} {originalLastName}</p>
            <p className="profile-info">{originalEmail}</p>
            {/* Display user type */}
            <p className="profile-info">Role: {currentUser.profile?.get_type_display || 'User'}</p>
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
            <button className="save-button" onClick={saveProfile} disabled={isLoading}>
              {isLoading ? "Saving..." : "Save Changes"}
            </button>
            <button className="cancel-button" onClick={handleCancel} disabled={isLoading}>
              Cancel
            </button>
          </>
        ) : (
          <button className="edit-button" onClick={() => setIsEditing(true)}>
            Edit Profile
          </button>
        )}
        {/* Logout button uses logout from AuthContext */}
        <button className="logout-button" onClick={() => { logout(); navigate('/'); }} disabled={isLoading}>
          Logout
        </button>
      </div>
    </div>
  );
};

export default ProfilePage;