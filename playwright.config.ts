import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: 'tests/e2e', timeout: 150_000, expect: { timeout: 25_000 }, workers: 2, fullyParallel: false, retries: 1, reporter: [['list'], ['html', { open: 'never', outputFolder: 'playwright-report' }]], outputDir: 'test-results/e2e',
  use: { baseURL: 'http://127.0.0.1:4199', viewport: { width: 1280, height: 720 }, contextOptions: { reducedMotion: 'reduce' }, actionTimeout: 25_000, screenshot: 'only-on-failure', trace: 'retain-on-failure', launchOptions: { args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'] } },
  webServer: { command: 'npx vite preview --host 127.0.0.1 --port 4199 --strictPort', url: 'http://127.0.0.1:4199', reuseExistingServer: false, timeout: 60_000 },
});
