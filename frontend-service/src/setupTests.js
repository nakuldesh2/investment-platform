// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock axios for API calls
jest.mock('./api/client', () => ({
  authAPI: {
    register: jest.fn(),
    login: jest.fn(),
    logout: jest.fn(),
    refresh: jest.fn(),
    getCurrentUser: jest.fn(),
  },
  marketAPI: {
    getQuote: jest.fn(),
    getCachedQuote: jest.fn(),
  },
  newsAPI: {
    getSentiment: jest.fn(),
    getNews: jest.fn(),
  },
  signalAPI: {
    getTopIdeas: jest.fn(),
  },
  default: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));
