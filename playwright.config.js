// @ts-check
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests', // Directory where tests are located
  timeout: 60 * 1000, // Increased timeout to 60 seconds
  fullyParallel: true, // Run tests in parallel
  forbidOnly: !!process.env.CI, // Disallow .only on CI
  retries: process.env.CI ? 2 : 0, // Retries on CI
  workers: process.env.CI ? 1 : undefined, // Workers on CI
  reporter: 'html', // Reporter to use. See https://playwright.dev/docs/test-reporters
  use: {
    trace: 'on-first-retry', // Collect trace when retrying a test for the first time.
    navigationTimeout: 30 * 1000, // Increased navigation timeout
    permissions: ['geolocation'], // Grant location permission
    geolocation: { latitude: 28.7041, longitude: 77.1025 }, // Delhi coordinates
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});