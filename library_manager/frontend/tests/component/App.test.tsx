import { render, screen, fireEvent } from '@testing-library/react';
import App from '../../src/App';
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('App Component', () => {

    beforeEach(() => {
        render(<App />);
    });

    it('renders the heading', () => {
        const heading = screen.getByRole('heading', {
            name: /Vite \+ React \+ Django/i,
        });
        expect(heading).toBeInTheDocument();
    });

    it('increments count on button click', () => {
        const button = screen.getByRole('button', { name: /count is/i });
        expect(button.textContent).toBe('count is 0');
        fireEvent.click(button);
        expect(button.textContent).toBe('count is 1');
    });

    it('renders links to Vite and React documentation', () => {
        const viteLink = screen.getByRole('link', { name: /vite logo/i });
        expect(viteLink).toBeInTheDocument();
        expect(viteLink).toHaveAttribute('href', 'https://vitejs.dev');

        const reactLink = screen.getByRole('link', { name: /react logo/i });
        expect(reactLink).toBeInTheDocument();
        expect(reactLink).toHaveAttribute('href', 'https://react.dev');
    });
});