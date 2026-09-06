// dev-server.js — ShopEase Application Server
import { spawn, execSync } from 'child_process';

console.log('[ShopEase] Initializing ShopEase Backend...');

try {
  execSync('python3 manage.py migrate --noinput', { stdio: 'inherit' });
  execSync('python3 manage.py seed_data', { stdio: 'inherit' });
} catch (e) {
  console.warn('[ShopEase] DB Setup warning:', e.message);
}

console.log('[ShopEase] Starting Django server on 0.0.0.0:3000...');

const django = spawn('python3', ['manage.py', 'runserver', '0.0.0.0:3000'], {
  stdio: 'inherit',
  env: { ...process.env, PYTHONUNBUFFERED: '1' }
});

django.on('error', (err) => {
  console.error('[ShopEase] Failed to start Django server:', err);
  process.exit(1);
});

django.on('exit', (code, signal) => {
  console.log(`[ShopEase] Django server exited with code ${code} and signal ${signal}`);
  process.exit(code || 0);
});

process.on('SIGTERM', () => {
  django.kill('SIGTERM');
  process.exit(0);
});

process.on('SIGINT', () => {
  django.kill('SIGINT');
  process.exit(0);
});
