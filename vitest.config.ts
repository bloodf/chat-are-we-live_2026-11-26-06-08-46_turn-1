import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: { include: ['tests/unit/**/*.test.ts'], environment: 'node', testTimeout: 60000, coverage: { provider: 'v8', include: ['src/core/**/*.ts', 'src/games/**/*.ts', 'src/three/nav.ts', 'src/three/lighting.ts'], reporter: ['text-summary', 'html'], reportsDirectory: 'test-results/coverage', thresholds: { lines: 88, functions: 88, statements: 86, branches: 74 } } },
});
