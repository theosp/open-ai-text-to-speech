// This file is run before each test file

// Add any global setup here
global.fetch = jest.fn();

// Mock DOM elements and functions that might be needed
global.document.getElementById = jest.fn(() => ({
  textContent: '',
  value: '',
  addEventListener: jest.fn(),
  style: {}
}));

global.document.querySelector = jest.fn(() => ({
  value: '',
  textContent: ''
}));

global.document.querySelectorAll = jest.fn(() => []);

// Mock alert
global.alert = jest.fn();

// Create a basic localStorage mock
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock; 