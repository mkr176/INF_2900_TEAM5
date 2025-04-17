import React from "react";
import "./AvatarSelector.css";

// <<< CHANGE: Define the static prefix and default filename here too, or import from a shared config/context >>>
const STATIC_AVATAR_PATH_PREFIX = "/static/images/avatars/";
const DEFAULT_AVATAR_FILENAME = "default.svg";

// Array of avatar filenames
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
  // <<< CHANGE: selectedAvatar expects the full path now >>>
  selectedAvatar: string; // e.g., /static/images/avatars/default.svg
  // <<< CHANGE: onSelectAvatar expects the full path now >>>
  onSelectAvatar: (fullPath: string) => void; // e.g., /static/images/avatars/default.svg
}

const AvatarSelector: React.FC<AvatarSelectorProps> = ({ selectedAvatar, onSelectAvatar }) => {
  return (
    // <<< CHANGE: Use avatar-grid class from the CSS provided >>>
    <div className="avatar-grid">
      {avatarFilenames.map((filename, index) => {
        // <<< CHANGE: Construct the full path for comparison and selection >>>
        const fullPath = STATIC_AVATAR_PATH_PREFIX + filename;
        return (
        <img
          key={index}
            // <<< CHANGE: Use the constructed full path for src >>>
            src={fullPath}
            alt={`Avatar Option ${index + 1}`}
            // <<< CHANGE: Compare full paths for selection state >>>
            // <<< CHANGE: Use avatar-option and selected classes from CSS >>>
            className={`avatar-option ${selectedAvatar === fullPath ? "selected" : ""}`}
            // <<< CHANGE: Pass the full path to the handler >>>
            onClick={() => onSelectAvatar(fullPath)}
            // Add error handling for individual avatar options if needed
            onError={(e) => {
              console.warn(`Failed to load avatar option: ${fullPath}. Hiding.`);
              (e.target as HTMLImageElement).style.display = 'none'; // Hide broken image
            }}
        />
        );
      })}
    </div>
  );
};

export default AvatarSelector;
