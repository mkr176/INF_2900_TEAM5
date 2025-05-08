// INF_2900_TEAM5/library_manager/frontend/cypress/e2e/performance/authPerformance.cy.ts

describe('Performance - Authentication', () => {
    const username = Cypress.env('TEST_USER_USERNAME') || 'testuser';
    const password = Cypress.env('TEST_USER_PASSWORD') || 'password123';
    const maxLoginTime = 3000; // ms for the entire login process (API call + redirect)
  
    beforeEach(() => {
      // Ensure we are logged out before each test in this suite
      cy.request({
        method: 'POST',
        url: '/api/auth/logout/',
        failOnStatusCode: false, // Don't fail if already logged out
        headers: {
          'X-CSRFToken': '', // May not be needed for logout if session-based
        },
      });
      cy.clearCookies(); // Clear any session cookies
      cy.visit('/login');
    });
  
    it('Login process should complete within an acceptable time', () => {
      cy.get('input[placeholder="Username"]').type(username);
      cy.get('input[placeholder="Password"]').type(password);
  
      let startTime: number;
      cy.intercept('POST', '/api/auth/login/').as('loginRequest');
      cy.intercept('GET', '/api/users/me/').as('fetchUserRequest'); // AuthContext fetches user
  
      cy.window().then((win) => {
        startTime = win.performance.now();
      });
  
      cy.get('button').contains('Login').click();
  
      cy.wait('@loginRequest').its('response.statusCode').should('eq', 200);
      cy.wait('@fetchUserRequest').its('response.statusCode').should('oneOf', [200, 304]); // 304 if cached
  
      cy.url().should('include', '/principal'); // Verify redirection
  
      cy.window().then((win) => {
        const endTime = win.performance.now();
        const duration = endTime - startTime;
        expect(duration).to.be.lessThan(maxLoginTime);
        cy.log(`Login Process Time: ${duration.toFixed(2)}ms`);
      });
    });
  
    // Placeholder for a sign-up performance test if needed
    // it('Sign-up process should complete within an acceptable time', () => {
    //   // Similar structure to the login test, but for the /api/auth/register/ endpoint
    //   // Remember to use unique credentials for each run or clean up
    // });
  });
  