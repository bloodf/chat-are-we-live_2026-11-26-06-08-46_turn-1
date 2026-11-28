import { boot, expect, live, start, test } from './util';

test.use({ viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true });

test('phone users can read the title and create a streamer with taps', async ({ page }) => {
  await boot(page);
  const heading = await page.getByRole('heading', { level: 1 }).boundingBox();
  expect(heading).not.toBeNull();
  expect(heading!.x + heading!.width).toBeLessThanOrEqual(375);
  await page.getByRole('button', { name: 'Go live', exact: true }).tap();
  await page.getByTestId('name').fill('Pocket Player');
  await page.getByTestId('channel').fill('PocketChannel');
  await page.getByTestId('create').tap();
  await expect(page.getByTestId('hud')).toBeVisible();
});

test('phone live view keeps the game, chat and stream actions reachable', async ({ page }) => {
  await start(page);
  await live(page);
  const game = page.getByTestId('game-canvas');
  await game.scrollIntoViewIfNeeded();
  await game.tap();
  const box = await game.boundingBox();
  expect(box!.width).toBeGreaterThan(100);
  expect(box!.height).toBeGreaterThan(100);
  await page.getByTestId('react-laugh').tap();
  await page.getByTestId('end-stream').tap();
  await expect(page.getByTestId('end-stream')).toContainText('Sure');
  await page.getByTestId('end-stream').tap();
  await expect(page.getByTestId('recap')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(375);
});
