# Testing Guide

Complete testing setup for backend (pytest) and frontend (Jest) with examples and best practices.

## Backend Testing (Python - pytest)

### Setup

All test dependencies are in `requirements.txt`:
```bash
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
aiosqlite==3.0.0
```

### Running Tests

```bash
# Run all backend tests
pytest

# Run tests for a specific service
pytest gateway-service/tests/ -v

# Run with coverage report
pytest --cov --cov-report=html

# Run specific test file
pytest gateway-service/tests/test_auth.py -v

# Run specific test
pytest gateway-service/tests/test_auth.py::TestAuthEndpoints::test_register_success -v

# Run tests matching a pattern
pytest -k "test_login" -v

# Run with markers
pytest -m "unit" -v  # Only unit tests
pytest -m "asyncio" -v  # Only async tests

# Run with output
pytest -s  # Show print statements
pytest -vv  # Very verbose
```

### Test Structure

Each service has:
```
{service}/tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_auth.py          # Auth endpoint tests
├── test_quotes.py        # Quote endpoint tests
└── test_services/        # Service/business logic tests
    └── test_quote_service.py
```

### Key Fixtures (conftest.py)

**Gateway Service** (`gateway-service/tests/conftest.py`):
```python
# In-memory SQLite database for testing
db_session

# Test settings with JWT configuration
test_settings

# FastAPI test client
client

# Test user with hashed password
test_user

# Authenticated client with valid JWT
authenticated_client
```

### Writing Tests

#### Unit Test Example
```python
def test_password_hashing():
    """Test password hash and verify"""
    from app.utils.security import hash_password, verify_password
    
    password = "test123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
```

#### Endpoint Test Example
```python
def test_login_success(client, test_user):
    """Test login returns token"""
    response = client.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123"
        }
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "access_token" in client.cookies
```

#### Async Test Example
```python
@pytest.mark.asyncio
async def test_database_query(db_session):
    """Test async database query"""
    from app.models import User
    from sqlalchemy.future import select
    
    # Create test user
    user = User(email="test@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()
    
    # Query
    stmt = select(User).where(User.email == "test@example.com")
    result = await db_session.execute(stmt)
    found_user = result.scalar_one_or_none()
    
    assert found_user is not None
    assert found_user.email == "test@example.com"
```

### Mocking External Services

```python
from unittest.mock import patch, AsyncMock

def test_with_mock_httpx(mocker):
    """Mock external HTTP calls"""
    mock_get = mocker.patch("httpx.AsyncClient.get")
    mock_get.return_value.json.return_value = {
        "Global Quote": {"05. price": "150.00"}
    }
    
    # Your test code here
    # The external API call will return mocked data
```

### Coverage Target

Aim for >80% coverage:

```bash
# Generate coverage report
pytest --cov --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html

# Check coverage for specific file
pytest --cov=app.utils.security --cov-report=term-missing
```

---

## Frontend Testing (React - Jest)

### Setup

Jest is built into Create React App. Test dependencies in `package.json`:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### Running Tests

```bash
cd frontend-service

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests matching a pattern
npm test Login

# Run with coverage
npm test -- --coverage

# Run tests in CI mode (no watch)
npm test -- --watchAll=false
```

### Test Structure

```
frontend-service/src/
├── setupTests.js                    # Jest setup and mocks
├── components/
│   ├── Login.js
│   ├── Login.css
│   └── __tests__/
│       ├── Login.test.js
│       ├── Dashboard.test.js
│       └── StockSearch.test.js
└── api/
    ├── client.js
    └── __tests__/
        └── client.test.js
```

### Writing Component Tests

#### Basic Component Test
```javascript
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import MyComponent from '../MyComponent';

test('renders component', () => {
  render(
    <BrowserRouter>
      <MyComponent />
    </BrowserRouter>
  );
  
  expect(screen.getByText(/expected text/i)).toBeInTheDocument();
});
```

#### Test with User Interactions
```javascript
import userEvent from '@testing-library/user-event';

test('handles form submission', async () => {
  const user = userEvent.setup();
  render(<LoginForm onSubmit={mockSubmit} />);
  
  const emailInput = screen.getByLabelText(/email/i);
  const submitButton = screen.getByText(/submit/i);
  
  await user.type(emailInput, 'test@example.com');
  await user.click(submitButton);
  
  expect(mockSubmit).toHaveBeenCalledWith('test@example.com');
});
```

#### Test with API Mocking
```javascript
import * as apiClient from '../../api/client';

jest.mock('../../api/client');

test('fetches and displays data', async () => {
  apiClient.getQuote.mockResolvedValue({
    symbol: 'AAPL',
    price: 150.00
  });
  
  render(<QuoteComponent />);
  
  const priceText = await screen.findByText(/150.00/i);
  expect(priceText).toBeInTheDocument();
});
```

#### Test Async Operations
```javascript
import { waitFor } from '@testing-library/react';

test('handles async operations', async () => {
  render(<AsyncComponent />);
  
  await waitFor(() => {
    expect(screen.getByText(/loaded/i)).toBeInTheDocument();
  });
});
```

### Mocking Modules

In `setupTests.js`:
```javascript
// Mock axios
jest.mock('./api/client', () => ({
  authAPI: {
    login: jest.fn(),
    logout: jest.fn(),
  },
  // ...
}));

// Mock React Router
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));
```

### Common Test Patterns

#### Testing Error States
```javascript
test('displays error message', async () => {
  apiClient.getQuote.mockRejectedValue({
    response: { data: { error: 'API Error' } }
  });
  
  render(<QuoteComponent symbol="AAPL" />);
  
  const errorMsg = await screen.findByText(/API Error/i);
  expect(errorMsg).toBeInTheDocument();
});
```

#### Testing Loading States
```javascript
test('shows loading indicator', async () => {
  const user = userEvent.setup();
  apiClient.getQuote.mockImplementation(
    () => new Promise(resolve => setTimeout(resolve, 100))
  );
  
  render(<QuoteComponent />);
  const button = screen.getByText(/search/i);
  
  await user.click(button);
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
});
```

#### Testing Form Validation
```javascript
test('validates form input', async () => {
  const user = userEvent.setup();
  render(<LoginForm />);
  
  const emailInput = screen.getByLabelText(/email/i);
  
  // Test required field
  expect(emailInput.required).toBe(true);
  
  // Test email format
  await user.type(emailInput, 'invalid-email');
  expect(emailInput.validity.valid).toBe(false);
});
```

---

## Continuous Integration

### Pre-commit Checks

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run tests before commit

# Backend
pytest --co -q > /dev/null 2>&1 && pytest -q || exit 1

# Frontend
cd frontend-service
npm test -- --watchAll=false --passWithNoTests || exit 1
```

### GitHub Actions Workflow

Create `.github/workflows/tests.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r gateway-service/requirements.txt
      - run: pytest --cov

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: cd frontend-service && npm install
      - run: npm test -- --coverage --watchAll=false
```

---

## Best Practices

### ✅ DO

- Test behavior, not implementation
- Use descriptive test names
- Keep tests focused and small
- Mock external dependencies
- Test error conditions
- Use fixtures for setup
- Test async operations properly

### ❌ DON'T

- Test implementation details
- Write brittle tests that break easily
- Skip negative test cases
- Mock everything
- Test third-party libraries
- Leave console.error in logs
- Ignore test failures

---

## Debugging Tests

```bash
# Run with verbose output
pytest -vv -s

# Run single test with output
pytest gateway-service/tests/test_auth.py::TestAuthEndpoints::test_login_success -vv -s

# Use pdb for debugging
pytest --pdb  # Drop into debugger on failure

# Keep test database for inspection
pytest --keep-db
```

For JavaScript:
```bash
# Debug in Chrome
npm test -- --inspect

# Watch mode for debugging
npm test -- --watch

# Run specific test file
npm test Login.test.js
```

---

## Coverage Goals

| Category | Target |
|----------|--------|
| Overall | >80% |
| Functions | >85% |
| Branches | >75% |
| Lines | >80% |
| Statements | >80% |

Focus first on:
1. Auth endpoints (security critical)
2. API error handling
3. Data validation
4. Business logic

---

## Adding New Tests

When adding new features:

1. **Write tests first** (TDD approach) or immediately after
2. **Test the happy path** - basic functionality
3. **Test error cases** - what could go wrong
4. **Test edge cases** - boundary conditions
5. **Run with coverage** - aim for >80%
6. **Mock external services** - don't hit real APIs

Example checklist for new endpoint:
- ✅ Test successful request
- ✅ Test missing required fields
- ✅ Test invalid input
- ✅ Test unauthorized access
- ✅ Test upstream service error
- ✅ Test response schema

---

## Resources

- [pytest docs](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Jest docs](https://jestjs.io/)
- [Testing Best Practices](https://testingjavascript.com/)
