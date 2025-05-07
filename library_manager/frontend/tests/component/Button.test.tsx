// INF_2900_TEAM5/library_manager/frontend/tests/component/Button.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Button from '../../src/components/Button/Button'; // Adjust path as necessary
import '@testing-library/jest-dom';

describe('Button Component', () => {
  it('renders with the correct text', () => {
    render(<Button text="Click Me" onClick={() => {}} />);
    expect(screen.getByRole('button', { name: /Click Me/i })).toBeInTheDocument();
  });

  it('calls onClick handler when clicked', () => {
    const handleClick = vi.fn();
    render(<Button text="Submit" onClick={handleClick} />);
    fireEvent.click(screen.getByRole('button', { name: /Submit/i }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies the primary class by default', () => {
    render(<Button text="Default" onClick={() => {}} />);
    expect(screen.getByRole('button', { name: /Default/i })).toHaveClass('btn primary');
  });

  it('applies the primary class when variant is primary', () => {
    render(<Button text="Primary Action" onClick={() => {}} variant="primary" />);
    expect(screen.getByRole('button', { name: /Primary Action/i })).toHaveClass('btn primary');
  });

  it('applies the secondary class when variant is secondary', () => {
    render(<Button text="Secondary Action" onClick={() => {}} variant="secondary" />);
    expect(screen.getByRole('button', { name: /Secondary Action/i })).toHaveClass('btn secondary');
  });
});