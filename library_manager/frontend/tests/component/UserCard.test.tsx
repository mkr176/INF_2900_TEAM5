// INF_2900_TEAM5/library_manager/frontend/tests/component/UserCard.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import UserCard from '../../src/components/UserCard/UserCard'; // Adjust path as necessary
import '@testing-library/jest-dom';

describe('UserCard Component', () => {
  const mockUser = {
    username: 'testuser',
    email: 'testuser@example.com',
    avatar: 'user-avatar.svg', // This is just the filename part
  };

  it('renders user information correctly', () => {
    render(<UserCard {...mockUser} />);

    expect(screen.getByRole('heading', { name: mockUser.username })).toBeInTheDocument();
    expect(screen.getByText(mockUser.email)).toBeInTheDocument();
  });

  it('renders the user avatar with the correct src path', () => {
    render(<UserCard {...mockUser} />);
    const avatarImage = screen.getByRole('img', { name: /User Avatar/i });
    expect(avatarImage).toBeInTheDocument();
    // The component prepends "/static/images/avatars/" to the avatar filename
    expect(avatarImage).toHaveAttribute('src', `/static/images/avatars/${mockUser.avatar}`);
  });

  it('applies correct CSS classes (basic check)', () => {
    render(<UserCard {...mockUser} />);
    // Check if the main container has the 'user-card' class (from UserCard.css)
    // Note: UserCard.css seems to be a copy of ProfilePage.css, so classes might be generic.
    // Let's assume there's a distinct 'user-card' class for the root element of UserCard.
    const userCardElement = screen.getByRole('heading', { name: mockUser.username }).closest('div');
    // This is a bit fragile, depends on UserCard.tsx root element being a div and having the class.
    // If UserCard.tsx root element does not have 'user-card', this will fail.
    // UserCard.tsx: <div className="user-card">
    expect(userCardElement).toHaveClass('user-card');
    
    const avatarImage = screen.getByRole('img', { name: /User Avatar/i });
    expect(avatarImage).toHaveClass('user-avatar'); // from UserCard.css (copied from ProfilePage.css)
  });
});