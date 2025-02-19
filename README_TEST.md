# Running Tests

This project includes multiple test suites organized in separate directories for backend and frontend components:

```
library_manager/
├── backend/
│   └── tests/
│       ├── functional/
│       │   └── test_views.py
│       ├── security/
│       │   └── test_security.py
│       └── unit/
│           └── test_models.py
└── frontend/
    └── tests/
        ├── component/
        │   └── App.test.tsx
        ├── endtoend/
        │   └── login.cy.ts
        └── performance/
            └── performance.test.js
```

## Automatic Test Runner

To run all tests automatically:

1. Save the test runner script as `run_tests.py` in your project root (same level as `library_manager` directory)
2. Make sure you have all dependencies installed:
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd library_manager/frontend
   npm install
   ```
3. Run the test script:
   ```bash
   python run_tests.py
   ```

The script will automatically run all test categories in both backend and frontend.

## Manual Testing

### Backend (Django) Tests

Run specific test categories from the `library_manager` directory:
```bash
# All backend tests
python manage.py test backend.tests

# Functional tests
python manage.py test backend.tests.functional

# Security tests
python manage.py test backend.tests.security

# Unit tests
python manage.py test backend.tests.unit
```

Run a specific test file:
```bash
python manage.py test backend.tests.functional.test_views
```

### Frontend (React) Tests

From the `library_manager/frontend` directory:

Run component tests:
```bash
npm test -- tests/component/App.test.tsx
```

Run performance tests:
```bash
npm test -- tests/performance/performance.test.js
```

### End-to-End Tests (Cypress)

From the `library_manager/frontend` directory:

```bash
# Run specific E2E test
npm run cypress:run -- --spec "tests/endtoend/login.cy.ts"

# Open Cypress Test Runner (interactive mode)
npm run cypress:open
```

## Test Coverage

Generate coverage reports from the appropriate directories:

### Backend Coverage
From `library_manager`:
```bash
coverage run manage.py test backend.tests
coverage report
coverage html  # Generates HTML report
```

### Frontend Coverage
From `library_manager/frontend`:
```bash
npm test -- --coverage
```

Coverage reports will be generated in the respective `coverage` directories.
