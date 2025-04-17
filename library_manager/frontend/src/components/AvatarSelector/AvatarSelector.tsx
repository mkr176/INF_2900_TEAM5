import React from "react";
import "./AvatarSelector.css";

// <<< CHANGE: Define the BASE URL for static avatars >>>
// This should match how Django serves these files via STATIC_URL/MEDIA_URL
// Adjust if your setup is different (e.g., using MEDIA_URL)
const AVATAR_BASE_URL = "/static/images/avatars/"; // Assuming avatars are under static/images/avatars/

const DEFAULT_AVATAR_FILENAME = "default.svg";

// Array of avatar filenames (relative to AVATAR_BASE_URL)
const avatarFilenames = [
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
  DEFAULT_AVATAR_FILENAME, // Use the constant
];

interface AvatarSelectorProps {
  // selectedAvatar expects the full URL now
  selectedAvatar: string; // e.g., /static/images/avatars/default.svg or http://localhost:8000/static/...
  // onSelectAvatar expects the full URL now
  onSelectAvatar: (fullUrl: string) => void; // e.g., /static/images/avatars/user-2.svg
}

const AvatarSelector: React.FC<AvatarSelectorProps> = ({ selectedAvatar, onSelectAvatar }) => {
  return (
    // <<< CHANGE: Use avatar-grid class from the CSS provided >>>
    <div className="avatar-grid">
      {avatarFilenames.map((filename, index) => {
        // Construct the full URL for this option
        const fullUrl = AVATAR_BASE_URL + filename;
        return (
        <img
          key={index}
            // Use the constructed full URL for src
            src={fullUrl}
            alt={`Avatar Option ${index + 1}`}
            // Compare full URLs for selection state
            className={`avatar-option ${selectedAvatar === fullUrl ? "selected" : ""}`}
            // Pass the full URL to the handler
            onClick={() => onSelectAvatar(fullUrl)}
            onError={(e) => {
              console.warn(`Failed to load avatar option: ${fullUrl}. Hiding.`);
              (e.target as HTMLImageElement).style.display = 'none';
            }}
        />
        );
      })}
    </div>
  );
};

export default AvatarSelector;
