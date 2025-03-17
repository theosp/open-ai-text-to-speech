module.exports = {
  // The test environment that will be used for testing
  testEnvironment: 'jsdom',
  
  // The directory where Jest should output its coverage files
  coverageDirectory: 'client-tests/coverage',
  
  // Indicates whether each individual test should be reported during the run
  verbose: true,
  
  // A list of paths to directories that Jest should use to search for files in
  roots: ['client-tests'],
  
  // The glob patterns Jest uses to detect test files
  testMatch: ['**/__tests__/**/*.js?(x)', '**/?(*.)+(spec|test).js?(x)'],
  
  // An array of regexp pattern strings that are matched against all test paths
  testPathIgnorePatterns: ['/node_modules/'],
  
  // An array of regexp pattern strings that are matched against all source file paths
  moduleFileExtensions: ['js', 'json', 'jsx'],
  
  // Automatically clear mock calls, instances, contexts and results before every test
  clearMocks: true,
  
  // Collect coverage from these directories
  collectCoverageFrom: [
    'static/js/**/*.js',
    '!**/node_modules/**',
    '!**/vendor/**'
  ],
  
  // The paths to modules that run some code to configure the testing framework
  // before each test file in the suite is executed
  setupFilesAfterEnv: ['<rootDir>/client-tests/setupTests.js'],
}; 