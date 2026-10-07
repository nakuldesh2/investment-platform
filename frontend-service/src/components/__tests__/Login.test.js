import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Login from '../Login';
import * as apiClient from '../../api/client';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('Login Component', () => {
  const mockOnLoginSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  const renderLogin = () => {
    return render(
      <BrowserRouter>
        <Login onLoginSuccess={mockOnLoginSuccess} />
      </BrowserRouter>
    );
  };

  test('renders login form by default', () => {
    renderLogin();
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  test('toggles between login and signup', async () => {
    const user = userEvent.setup();
    renderLogin();

    const toggleButton = screen.getByText(/sign up/i);
    await user.click(toggleButton);

    expect(screen.getByText(/create account/i)).toBeInTheDocument();
  });

  test('successfully logs in user', async () => {
    const user = userEvent.setup();
    apiClient.authAPI.login.mockResolvedValue({ access_token: 'test_token' });

    renderLogin();

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByText(/sign in/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    await waitFor(() => {
      expect(apiClient.authAPI.login).toHaveBeenCalledWith(
        'test@example.com',
        'password123'
      );
      expect(mockOnLoginSuccess).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('displays error on login failure', async () => {
    const user = userEvent.setup();
    const errorMessage = 'Invalid email or password';
    apiClient.authAPI.login.mockRejectedValue({
      response: { data: { error: errorMessage } },
    });

    renderLogin();

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByText(/sign in/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'wrongpassword');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  test('successfully registers new user', async () => {
    const user = userEvent.setup();
    apiClient.authAPI.register.mockResolvedValue({ id: 1, email: 'newuser@example.com' });
    apiClient.authAPI.login.mockResolvedValue({ access_token: 'test_token' });

    renderLogin();

    // Switch to signup
    const toggleButton = screen.getByText(/sign up/i);
    await user.click(toggleButton);

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByText(/create account/i);

    await user.type(emailInput, 'newuser@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    await waitFor(() => {
      expect(apiClient.authAPI.register).toHaveBeenCalledWith(
        'newuser@example.com',
        'password123'
      );
      expect(apiClient.authAPI.login).toHaveBeenCalled();
      expect(mockOnLoginSuccess).toHaveBeenCalled();
    });
  });

  test('disables submit button while loading', async () => {
    const user = userEvent.setup();
    apiClient.authAPI.login.mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderLogin();

    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByText(/sign in/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);

    expect(submitButton).toBeDisabled();
    expect(submitButton).toHaveTextContent('Processing...');
  });

  test('validates password length', async () => {
    const user = userEvent.setup();
    renderLogin();

    const passwordInput = screen.getByLabelText(/password/i);
    await user.type(passwordInput, 'short');

    // HTML5 validation should prevent short passwords
    expect(passwordInput.validity.valid).toBe(false);
  });
});
