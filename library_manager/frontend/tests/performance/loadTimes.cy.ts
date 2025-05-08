// INF_2900_TEAM5/library_manager/frontend/cypress/e2e/performance/loadTimes.cy.ts

describe('Performance - Page Load Times', () => {
    it('Welcome page should load within an acceptable time', () => {
      const maxLoadTime = 2000; // milliseconds
      cy.visit('/', {
        onBeforeLoad: (win) => {
          win.performance.mark('start-loading');
        },
        onLoad: (win) => {
          win.performance.mark('end-loading');
          win.performance.measure('pageLoad', 'start-loading', 'end-loading');
          const measure = win.performance.getEntriesByName('pageLoad')[0];
          expect(measure.duration).to.be.lessThan(maxLoadTime);
          cy.log(`Welcome Page Load Time: ${measure.duration.toFixed(2)}ms`);
        },
      });
      cy.contains('Welcome to LibManager!').should('be.visible');
    });
  
    it('Login page should load within an acceptable time', () => {
      const maxLoadTime = 1500; // milliseconds
      cy.visit('/login', {
        onBeforeLoad: (win) => {
          win.performance.mark('start-loading-login');
        },
        onLoad: (win) => {
          win.performance.mark('end-loading-login');
          win.performance.measure('loginPageLoad', 'start-loading-login', 'end-loading-login');
          const measure = win.performance.getEntriesByName('loginPageLoad')[0];
          expect(measure.duration).to.be.lessThan(maxLoadTime);
          cy.log(`Login Page Load Time: ${measure.duration.toFixed(2)}ms`);
        },
      });
      cy.contains('Library Login').should('be.visible');
    });
  
    it('Sign Up page should load within an acceptable time', () => {
        const maxLoadTime = 1500; // milliseconds
        cy.visit('/signup', {
          onBeforeLoad: (win) => {
            win.performance.mark('start-loading-signup');
          },
          onLoad: (win) => {
            win.performance.mark('end-loading-signup');
            win.performance.measure('signupPageLoad', 'start-loading-signup', 'end-loading-signup');
            const measure = win.performance.getEntriesByName('signupPageLoad')[0];
            expect(measure.duration).to.be.lessThan(maxLoadTime);
            cy.log(`Sign Up Page Load Time: ${measure.duration.toFixed(2)}ms`);
          },
        });
        cy.contains('Create Account').should('be.visible');
      });
  });
  