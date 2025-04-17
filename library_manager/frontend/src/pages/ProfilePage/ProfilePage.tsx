import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import AvatarSelector from "../../components/AvatarSelector/AvatarSelector";
import { useNavigate } from "react-router-dom";
import "./ProfilePage.css";

// Constants
const MIN_PASSWORD_LENGTH = 8;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// <<< CHANGE: Use the default URL from AuthContext or define consistently >>>
const DEFAULT_AVATAR_URL = "/static/images/avatars/default.svg"; // Must match AuthContext

// <<< ADDED: Helper function to get relative path from full URL for sending to backend >>>
// This needs to know the base URL part to remove.
const getRelativeAvatarPathFromUrl = (fullUrl: string | null | undefined): string | null => {
    if (!fullUrl || typeof fullUrl !== 'string') {
        return null; // Or return default relative path 'avatars/default.svg' if needed
    }
    // Find the part of the URL that corresponds to the relative path
    // This assumes the URL structure is like '.../static/images/avatars/filename.svg'
    // or '.../media/avatars/filename.svg'
    const avatarMarker = "/avatars/";
    const markerIndex = fullUrl.lastIndexOf(avatarMarker);

    if (markerIndex !== -1) {
        // Extract the part starting from 'avatars/'
        return fullUrl.substring(markerIndex + 1); // e.g., "avatars/default.svg"
    }

    // Fallback or error handling if the structure is unexpected
    console.warn("Could not determine relative path from avatar URL:", fullUrl);
    // Return the default relative path as a safe fallback if the current URL is the default one
    if (fullUrl.endsWith(DEFAULT_AVATAR_FILENAME)) {
        return `avatars/${DEFAULT_AVATAR_FILENAME}`;
    }
    return null; // Or handle error appropriately
};


const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  // <<< CHANGE: Get avatarUrl from context >>>
  const { currentUser, logout, fetchUser, getCSRFToken, avatarUrl: contextAvatarUrl } = useAuth();

  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(!currentUser);

  // State for editable fields
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [newPassword, setNewPassword] = useState("");
  // <<< CHANGE: Store the full avatar URL in state >>>
  const [selectedAvatarUrl, setSelectedAvatarUrl] = useState(contextAvatarUrl || DEFAULT_AVATAR_URL);

  // Store original values
  const [originalEmail, setOriginalEmail] = useState("");
  const [originalFirstName, setOriginalFirstName] = useState("");
  const [originalLastName, setOriginalLastName] = useState("");
  // <<< CHANGE: Store the original full avatar URL >>>
  const [originalAvatarUrl, setOriginalAvatarUrl] = useState(contextAvatarUrl || DEFAULT_AVATAR_URL);

  useEffect(() => {
    setIsLoading(!currentUser);
    if (currentUser) {
      const userEmail = currentUser.email || "";
      const userFirstName = currentUser.first_name || "";
      const userLastName = currentUser.last_name || "";
      // <<< CHANGE: Use avatar_url from context >>>
      const userAvatarUrl = contextAvatarUrl || DEFAULT_AVATAR_URL;

      setEmail(userEmail);
      setOriginalEmail(userEmail);
      setFirstName(userFirstName);
      setOriginalFirstName(userFirstName);
      setLastName(userLastName);
      setOriginalLastName(userLastName);
      // <<< CHANGE: Set state with the full URL >>>
      setSelectedAvatarUrl(userAvatarUrl);
      setOriginalAvatarUrl(userAvatarUrl);
      setIsLoading(false);
    } else {
      const timer = setTimeout(() => {
        if (!currentUser && !isLoading) {
             console.log("No current user found, redirecting to login.");
             // navigate("/login");
        }
      }, 500);
      return () => clearTimeout(timer);
    }
    // <<< CHANGE: Depend on contextAvatarUrl >>>
  }, [currentUser, isLoading, navigate, contextAvatarUrl]);

  const handleCancel = () => {
    setIsEditing(false);
    setEmail(originalEmail);
    setFirstName(originalFirstName);
    setLastName(originalLastName);
    // <<< CHANGE: Reset selected URL to original URL >>>
    setSelectedAvatarUrl(originalAvatarUrl);
    setNewPassword("");
  };

  const saveProfile = async () => {
    // <<< CHANGE: Compare full avatar URLs >>>
    const isAvatarChanged = selectedAvatarUrl !== originalAvatarUrl;
    const isEmailChanged = email !== originalEmail;
    const isFirstNameChanged = firstName !== originalFirstName;
    const isLastNameChanged = lastName !== originalLastName;
    const isPasswordChanged = newPassword !== "";

    // --- Validation ---
    if (isEmailChanged && !EMAIL_REGEX.test(email)) {
      alert("Please enter a valid email address.");
      return;
    }
    if (isPasswordChanged && newPassword.length < MIN_PASSWORD_LENGTH) {
      alert(`New password must be at least ${MIN_PASSWORD_LENGTH} characters long.`);
      return;
    }
    if (!isEmailChanged && !isFirstNameChanged && !isLastNameChanged && !isPasswordChanged && !isAvatarChanged) {
      alert("No changes detected.");
      setIsEditing(false);
      return;
    }

    const csrfToken = await getCSRFToken();
    if (!csrfToken) {
      alert("Error: Could not verify security token. Please refresh and try again.");
      return;
    }

    // --- Payload Construction ---
    const payload: { [key: string]: any } = {};
    const profilePayload: { [key: string]: any } = {};

    if (isEmailChanged) payload.email = email;
    if (isFirstNameChanged) payload.first_name = firstName;
    if (isLastNameChanged) payload.last_name = lastName;
    if (isPasswordChanged) payload.password = newPassword;

    // <<< CHANGE: Convert selected full URL back to relative path for backend >>>
    if (isAvatarChanged) {
        const relativePath = getRelativeAvatarPathFromUrl(selectedAvatarUrl);
        if (relativePath !== null) {
            profilePayload.avatar = relativePath; // Send relative path string
        } else {
            // Handle error: couldn't extract relative path. Maybe skip avatar update?
            console.error("Could not determine relative path for avatar update. Skipping avatar change.");
            // Optionally alert the user
            // alert("There was an issue selecting the avatar. Please try again.");
            // return; // Or just skip sending the avatar field
        }
    }

    if (Object.keys(profilePayload).length > 0) {
      payload.profile = profilePayload;
    }

    // --- API Call ---
    setIsLoading(true);
    try {
      const response = await fetch("/api/users/me/update/", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
        credentials: "include",
      });

      let responseData;
      try {
          responseData = await response.json();
      } catch (e) {
          responseData = { detail: `Update failed with status: ${response.status}` };
      }

      if (response.ok) {
        alert("Profile updated successfully!");
        if (isEmailChanged) setOriginalEmail(email);
        if (isFirstNameChanged) setOriginalFirstName(firstName);
        if (isLastNameChanged) setOriginalLastName(lastName);
        // <<< CHANGE: Update original URL >>>
        if (isAvatarChanged) setOriginalAvatarUrl(selectedAvatarUrl);

        setNewPassword("");
        setIsEditing(false);
        await fetchUser(); // Refresh auth context
      } else {
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
      setIsLoading(false);
    }
  };

  if (isLoading && !currentUser) {
     return <div className="profile-container"><p className="loading-text">Loading Profile...</p></div>;
  }
  if (!currentUser) {
     return <div className="profile-container"><p>Could not load user profile. Please <button onClick={() => navigate('/login')}>log in</button>.</p></div>;
  }

  return (
    <div className="profile-container">
      <h1 className="profile-title">{currentUser.username}'s Profile</h1>

      <div className="profile-card">
        <img
          // <<< CHANGE: Use selectedAvatarUrl directly >>>
          src={selectedAvatarUrl}
          alt="User Avatar"
          className="profile-avatar"
          onError={(e) => {
            console.warn(`Failed to load avatar: ${selectedAvatarUrl}. Using default.`);
            // <<< CHANGE: Fallback to the default URL >>>
            (e.target as HTMLImageElement).src = DEFAULT_AVATAR_URL;
            // Update state if the current selection failed
            setSelectedAvatarUrl(DEFAULT_AVATAR_URL);
          }}
        />
        <h2 className="profile-username">{currentUser.username}</h2>

        {isEditing ? (
          <>
            <input type="text" className="profile-input" value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="First Name" />
            <input type="text" className="profile-input" value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder="Last Name" />
            <input type="email" className="profile-input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
            <input type="password" className="profile-input" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="New Password (leave blank to keep)" />
          </>
        ) : (
          <>
            {/* <<< CHANGE: Display original values >>> */}
            <p className="profile-info">{originalFirstName} {originalLastName}</p>
            <p className="profile-info">{originalEmail}</p>
            <p className="profile-info">Role: {currentUser.profile?.get_type_display || 'User'}</p>
          </>
        )}
      </div>

      {isEditing && (
        <>
          <h3 className="avatar-selection-title">Choose Your Avatar</h3>
          {/* <<< CHANGE: Pass selectedAvatarUrl and expect full URL back >>> */}
          <AvatarSelector selectedAvatar={selectedAvatarUrl} onSelectAvatar={setSelectedAvatarUrl} />
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
        <button className="logout-button" onClick={() => { logout(); navigate('/'); }} disabled={isLoading}>
          Logout
        </button>
      </div>
    </div>
  );
};

export default ProfilePage;