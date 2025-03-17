import React from "react";
import "./AvatarSelector.css";

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

interface AvatarSelectorProps {
  selectedAvatar: string;
  onSelectAvatar: (avatar: string) => void;
}

const AvatarSelector: React.FC<AvatarSelectorProps> = ({ selectedAvatar, onSelectAvatar }) => {
  return (
    <div className="avatar-selector">
      {avatars.map((avatar, index) => (
        <img
          key={index}
          src={`/static/images/avatars/${avatar}`}
          alt="Avatar Option"
          className={`avatar-option ${selectedAvatar === avatar ? "selected" : ""}`}
          onClick={() => onSelectAvatar(avatar)}
        />
      ))}
    </div>
  );
};

export default AvatarSelector;
