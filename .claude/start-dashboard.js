// Helper to start vite from the dashboard directory
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
const __dirname = dirname(fileURLToPath(import.meta.url));
process.chdir(join(__dirname, '..', 'dashboard'));
await import('../dashboard/node_modules/vite/bin/vite.js');
