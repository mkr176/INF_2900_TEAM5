// INF_2900_TEAM5/library_manager/frontend/cypress/e2e/performance/principalPagePerformance.cy.ts

describe('Performance - Principal Page (Book Catalog)', () => {
    const username = Cypress.env('TEST_USER_USERNAME') || 'testuser';
    const password = Cypress.env('TEST_USER_PASSWORD') || 'password123';
    const maxPrincipalPageLoadTime = 3500; // ms, includes API calls for books
  
    beforeEach(() => {
      // Log in the user
      cy.request({
        method: 'POST',
        url: '/api/auth/login/',
        body: { username, password },
        failOnStatusCode: true, // Should succeed
      }).then(() => {
        // Set a cookie to simulate being logged in, if your app relies on it
        // This might vary based on your auth setup (e.g., sessionid)
        // For DRF, the sessionid cookie is HttpOnly, so direct setting might not be possible.
        // The login request above should establish the session.
      });
    });
  
    it('Principal page (book catalog) should load and display books within an acceptable time', () => {
      let startTime: number;
  
      // Intercept the books API call
      cy.intercept('GET', '/api/books/*').as('getBooks'); // Use wildcard for query params
  
      cy.visit('/principal', {
        onBeforeLoad: (win) => {
          startTime = win.performance.now();
          win.performance.mark('start-principal-load');
        },
      });
  
      // Wait for the books API call to complete
      cy.wait('@getBooks').its('response.statusCode').should('oneOf', [200, 304]);
  
      // Ensure some books are visible (assuming .book-card-container is used)
      cy.get('.book-card-container', { timeout: 10000 }).should('have.length.greaterThan', 0);
  
      cy.window().then((win) => {
        win.performance.mark('end-principal-load');
        win.performance.measure('principalPageRenderTime', 'start-principal-load', 'end-principal-load');
        const measure = win.performance.getEntriesByName('principalPageRenderTime')[0];
        expect(measure.duration).to.be.lessThan(maxPrincipalPageLoadTime);
        cy.log(`Principal Page (Book Catalog) Load and Render Time: ${measure.duration.toFixed(2)}ms`);
      });
    });
  
    it('Filtering books by category should be performant', () => {
      const maxFilterTime = 1500; // ms
      cy.visit('/principal');
      cy.wait('@getBooks'); // Wait for initial load
  
      cy.get('.category-select').should('be.visible');
  
      let filterStartTime: number;
      cy.intercept('GET', '/api/books/?category=SF*').as('filterScienceFiction');
  
      cy.window().then((win) => {
        filterStartTime = win.performance.now();
      });
  
      cy.get('.category-select').select('SF'); // Assuming 'SF' is a valid value for Science Fiction
  
      cy.wait('@filterScienceFiction');
      cy.get('.book-card-container').should('exist'); // Check that books are still rendered
  
      cy.window().then((win) => {
        const filterEndTime = win.performance.now();
        const duration = filterEndTime - filterStartTime;
        expect(duration).to.be.lessThan(maxFilterTime);
        cy.log(`Book Filtering Time (Science Fiction): ${duration.toFixed(2)}ms`);
      });
    });
  });
  