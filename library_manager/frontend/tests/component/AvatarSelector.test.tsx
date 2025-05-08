// INF_2900_TEAM5/library_manager/frontend/tests/component/AvatarSelector.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import AvatarSelector from '../../src/components/AvatarSelector/AvatarSelector'; // Adjust path
import '@testing-library/jest-dom';

// Mock AVATAR_BASE_URL and avatarFilenames as they are module-level constants in the component
const AVATAR_BASE_URL = "/static/images/avatars/";
const MOCK_AVATAR_FILENAMES = [
  "avatar1.svg",
  "avatar2.svg",
  "default.svg",
];

// Manually mock the constants used by AvatarSelector
vi.mock('../../src/components/AvatarSelector/AvatarSelector', async (importOriginal) => {
    const originalModule = await importOriginal<typeof import('../../src/components/AvatarSelector/AvatarSelector')>();
    return {
        ...originalModule,
        // Override specific exports or behavior if needed,
        // but for constants, ensure they are defined before component usage if they were top-level in the original.
        // In this case, the component itself uses the constants internally, so direct mocking of them is hard.
        // Instead, we ensure our test props align with how the component would use its internal constants.
    };
});


describe('AvatarSelector Component', () => {
  const defaultSelectedAvatar = `${AVATAR_BASE_URL}default.svg`;

  it('renders all avatar options', () => {
    // To test rendering, we need to ensure the component uses a known set of avatar filenames.
    // Since the actual filenames are hardcoded in AvatarSelector.tsx, our test can rely on that structure.
    // If these filenames were dynamic, we'd need a different approach (e.g., mocking the source of filenames).

    render(
      <AvatarSelector
        selectedAvatar={defaultSelectedAvatar}
        onSelectAvatar={() => {}}
      />
    );

    // Check if images are rendered. The number should match avatarFilenames in the component.
    // The actual number of avatarFilenames in the component is 16.
    const avatarImages = screen.getAllByRole('img');
    expect(avatarImages.length).toBe(16); // Based on the hardcoded avatarFilenames in the component

    // Check if one of the known avatars (e.g., default) is present
    const defaultAvatarImage = screen.getByAltText('Avatar Option 16'); // Assuming default is last
    expect(defaultAvatarImage).toHaveAttribute('src', `${AVATAR_BASE_URL}default.svg`);
  });

  it('highlights the selected avatar', () => {
    const selectedFilename = "account-avatar-profile-user-2-svgrepo-com.svg";
    const selectedAvatarFullUrl = `${AVATAR_BASE_URL}${selectedFilename}`;
    render(
      <AvatarSelector
        selectedAvatar={selectedAvatarFullUrl}
        onSelectAvatar={() => {}}
      />
    );

    // Find the image corresponding to the selected avatar.
    // The alt text is "Avatar Option X", so we need to know its index.
    // "account-avatar-profile-user-2-svgrepo-com.svg" is the first in the component's list.
    const selectedImage = screen.getByAltText('Avatar Option 1');
    expect(selectedImage).toHaveClass('selected');

    // Check another avatar to ensure it's not selected
    const anotherImage = screen.getByAltText('Avatar Option 2'); // e.g., avatar2.svg
    expect(anotherImage).not.toHaveClass('selected');
  });

  it('calls onSelectAvatar with the correct URL when an avatar is clicked', () => {
    const handleSelectAvatar = vi.fn();
    const avatarToClickFilename = "account-avatar-profile-user-3-svgrepo-com.svg";
    const expectedUrl = `${AVATAR_BASE_URL}${avatarToClickFilename}`;

    render(
      <AvatarSelector
        selectedAvatar={defaultSelectedAvatar}
        onSelectAvatar={handleSelectAvatar}
      />
    );

    // "account-avatar-profile-user-3-svgrepo-com.svg" is the second in the component's list.
    const avatarToClickImage = screen.getByAltText('Avatar Option 2');
    fireEvent.click(avatarToClickImage);

    expect(handleSelectAvatar).toHaveBeenCalledTimes(1);
    expect(handleSelectAvatar).toHaveBeenCalledWith(expectedUrl);
  });

  it('handles onError for a broken image link gracefully (hides the image)', () => {
    // This test is a bit tricky as jsdom doesn't fully load images or trigger onError for network issues.
    // We can simulate the onError event more directly if needed, or trust the handler logic.
    // For this example, let's assume the onError prop in the component works.
    // We will check if the image is still in the document but potentially styled as display:none
    // which is what the component's onError does.

    render(
        <AvatarSelector
          selectedAvatar={defaultSelectedAvatar}
          onSelectAvatar={() => {}}
        />
      );
      
      // Get one image to simulate error on
      const firstAvatarImage = screen.getByAltText('Avatar Option 1') as HTMLImageElement;
      
      // Manually trigger the error event
      fireEvent.error(firstAvatarImage);
      
      // Check if the style 'display: none' was applied
      expect(firstAvatarImage).toHaveStyle('display: none');
  });
});