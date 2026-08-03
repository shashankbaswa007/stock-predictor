import { test, expect } from '@playwright/test';

test('homepage has correct title and layout', async ({ page }) => {
  // Go to the homepage
  await page.goto('/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Stock Predictor|AI Trading/);

  // Expect the page to have a navigation bar or header
  const header = page.locator('header');
  await expect(header).toBeVisible();
});

test('chat panel allows input', async ({ page }) => {
  await page.goto('/');
  
  // Look for the chat input box
  const chatInput = page.locator('textarea[placeholder*="Ask about"]');
  await expect(chatInput).toBeVisible();
  
  await chatInput.fill('Analyze MSFT');
  await expect(chatInput).toHaveValue('Analyze MSFT');
});
