import { expect, test, type Page } from "@playwright/test";

const login = async (page: Page) => {
  await page.goto("/");
  // If login form is shown, fill credentials
  const usernameInput = page.getByLabel(/username/i);
  if (await usernameInput.isVisible()) {
    await usernameInput.fill("user");
    await page.getByLabel(/password/i).fill("password");
    await page.getByRole("button", { name: /sign in/i }).click();
  }
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
};

test("prompts for login when unauthenticated and displays error on invalid credentials", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Sign In" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).not.toBeVisible();

  await page.getByLabel(/username/i).fill("wrong");
  await page.getByLabel(/password/i).fill("wrongpass");
  await page.getByRole("button", { name: /sign in/i }).click();

  await expect(page.getByRole("alert")).toHaveText("Invalid username or password");
});

test("logs in with valid credentials and logs out successfully", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel(/username/i).fill("user");
  await page.getByLabel(/password/i).fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();

  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.getByText(/Demo User/i)).toBeVisible();

  // Click Sign Out
  await page.getByRole("button", { name: /sign out/i }).click();
  await expect(page.getByRole("heading", { name: "Sign In" })).toBeVisible();
});

test("loads the kanban board after login", async ({ page }) => {
  await login(page);
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  await login(page);
  const card = page.getByTestId("card-card-1");
  const targetColumn = page.getByTestId("column-col-review");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
});

test("persists added card across page reload", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Persistent Card");
  await firstColumn.getByPlaceholder("Details").fill("Should survive reload.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Persistent Card")).toBeVisible();

  // Reload page
  await page.reload();
  await expect(page.getByText("Persistent Card")).toBeVisible();
});

