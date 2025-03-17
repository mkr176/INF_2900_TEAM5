import React from "react";
import "./UserCard.css";

interface UserCardProps {
  username: string;
  email: string;
  avatar: string;
}

const UserCard: React.FC<UserCardProps> = ({ username, email, avatar }) => {
  return (
    <div className="user-card">
      <img src={`/static/images/avatars/${avatar}`} alt="User Avatar" className="user-avatar" />
      <h2 className="user-name">{username}</h2>
      <p className="user-email">{email}</p>
    </div>
  );
};

export default UserCard;
