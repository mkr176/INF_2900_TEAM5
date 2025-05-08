// INF_2900_TEAM5/library_manager/frontend/tests/endtoend/login.cy.ts

describe('User Authentication Flows', () => {
  beforeEach(() => {
    // Base URL is configured in cypress.config.ts or cypress.json
    // Example: "baseUrl": "http://localhost:5173" for Vite dev server
    // Or "baseUrl": "http://localhost:8000" if Django serves the frontend directly
    cy.visit('/'); // Adjust if your login page is not at the root

    // Intercept CSRF token requests to ensure it's handled if needed,
    // though Cypress often handles cookies automatically.
    // This is more for complex scenarios or debugging.
    cy.intercept('GET', '/api/csrf/').as('getCsrfToken');
  });

  it('should display the login page correctly', () => {
    cy.contains('h1', 'Library Login'); // Or whatever your login page title is
    cy.get('input[placeholder="Username"]').should('be.visible');
    cy.get('input[placeholder="Password"]').should('be.visible');
    cy.get('button').contains('Login').should('be.visible');
    cy.get('button').contains('Sign Up').should('be.visible');
  });

  it('should allow navigation to the sign-up page', () => {
    cy.get('button').contains('Sign Up').click();
    cy.url().should('include', '/signup');
    cy.contains('h1', 'Create Account'); // Or your sign-up page title
  });

  it('should show an error for empty login credentials', () => {
    cy.get('button').contains('Login').click();
    // Cypress automatically waits for alerts.
    // If you have a custom error message display (not an alert),
    // you would assert its visibility and content here.
    // For window.alert():
    cy.on('window:alert', (str) => {
      expect(str).to.contain('Invalid username or password'); // Or your specific error message
    });
  });

  it('should show an error for invalid login credentials', () => {
    cy.get('input[placeholder="Username"]').type('invaliduser');
    cy.get('input[placeholder="Password"]').type('wrongpassword');
    cy.get('button').contains('Login').click();

    cy.on('window:alert', (str) => {
      expect(str).to.contain('Invalid credentials'); // Or the specific error from backend
    });
  });

  // Test for successful login (requires a valid test user in your database)
  // IMPORTANT: Avoid hardcoding sensitive credentials. Use environment variables for Cypress.
  // Example: Cypress.env('TEST_USER_USERNAME'), Cypress.env('TEST_USER_PASSWORD')
  // These would be set in cypress.env.json or via CLI
  it('should log in a valid user and redirect to the principal page', () => {
    const username = Cypress.env('TEST_USER_USERNAME') || 'testuser'; // Fallback for local testing
    const password = Cypress.env('TEST_USER_PASSWORD') || 'password123'; // Fallback

    // Ensure your backend is running and the user exists, and DB is library_test
    // For this test to pass, 'testuser' with 'password123' must exist
    // or be created by a seeding script before tests run.

    cy.get('input[placeholder="Username"]').type(username);
    cy.get('input[placeholder="Password"]').type(password);
    cy.get('button').contains('Login').click();

    // Wait for redirection and check URL
    cy.url().should('include', '/principal', { timeout: 10000 }); // Increased timeout for async operations
    cy.contains('h1, h2, div', /Book Catalog|Welcome|Available Books/i); // Check for content on the principal page
  });

  describe('Registration', () => {
    beforeEach(() => {
      cy.visit('/signup'); // Navigate to signup page
    });

    it('should display the registration page correctly', () => {
      cy.contains('h1', 'Create Account');
      cy.get('input[placeholder="Username *"]').should('be.visible');
      cy.get('input[placeholder="Email *"]').should('be.visible');
      cy.get('input[placeholder="Password *"]').should('be.visible');
      cy.get('input[placeholder="Confirm Password *"]').should('be.visible');
      cy.get('button').contains('Sign Up').should('be.visible');
    });

    it('should show errors for incomplete registration form', () => {
      cy.get('button').contains('Sign Up').click();
      cy.on('window:alert', (str) => {
        expect(str).to.contain('Username, Email, Password, and Password Confirmation are required!');
      });
    });

    it('should show error if passwords do not match', () => {
      cy.get('input[placeholder="Username *"]').type('newuser');
      cy.get('input[placeholder="Email *"]').type('newuser@example.com');
      cy.get('input[placeholder="Password *"]').type('password123');
      cy.get('input[placeholder="Confirm Password *"]').type('password456');
      cy.get('button').contains('Sign Up').click();
      cy.on('window:alert', (str) => {
        expect(str).to.contain('Passwords do not match!');
      });
    });

    // This test will attempt to create a new user.
    // Ensure your test database can handle this (e.g., clean up after tests).
    it('should successfully register a new user and redirect to login', () => {
      // Use a unique username and email for each test run to avoid conflicts
      const uniqueId = Date.now();
      const username = `testuser${uniqueId}`;
      const email = `test${uniqueId}@example.com`;
      const password = 'StrongPassword123!';

      cy.get('input[placeholder="Username *"]').type(username);
      cy.get('input[placeholder="Email *"]').type(email);
      cy.get('input[placeholder="Password *"]').type(password);
      cy.get('input[placeholder="Confirm Password *"]').type(password);
      // Optionally fill in non-required fields
      cy.get('input[placeholder="First Name (Optional)"]').type('Test');
      cy.get('input[placeholder="Last Name (Optional)"]').type('User');
      cy.get('input[placeholder="Age (Optional)"]').type('30');

      cy.get('button').contains('Sign Up').click();

      // Check for success alert and redirection
      cy.on('window:alert', (str) => {
        expect(str).to.contain('Sign-up successful! Please log in.');
      });
      cy.url().should('include', '/login', { timeout: 10000 });
      cy.contains('h1', 'Library Login'); // Verify it's the login page
    });

     it('should show an error if username is already taken', () => {
      // First, register a user.
      const username = `existinguser${Date.now()}`;
      const email = `existing${Date.now()}@example.com`;
      const password = 'Password123!';

      cy.request({
        method: 'POST',
        url: '/api/auth/register/', // Adjust if your API prefix is different
        body: {
          username: username,
          email: email,
          password: password,
          password2: password
        },
        failOnStatusCode: false // Allow request to "fail" if user already exists for setup
      }).then((resp) => {
         // Now try to register with the same username via UI
        cy.visit('/signup');
        cy.get('input[placeholder="Username *"]').type(username); // Same username
        cy.get('input[placeholder="Email *"]').type(`another${Date.now()}@example.com`); // Different email
        cy.get('input[placeholder="Password *"]').type(password);
        cy.get('input[placeholder="Confirm Password *"]').type(password);
        cy.get('button').contains('Sign Up').click();

        cy.on('window:alert', (str) => {
            // The exact error message might come from your backend serializer
            expect(str).to.contain('username: A user with that username already exists.');
        });
      });
    });
  });
});