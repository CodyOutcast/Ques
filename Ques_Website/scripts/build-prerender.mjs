import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const projectDir = process.cwd();
const clientOutDir = process.env.BUILD_DIR_OVERRIDE || 'dist';
const ssrOutDir = `${clientOutDir}-ssr`;
const npxCommand = process.platform === 'win32' ? 'npx.cmd' : 'npx';

function run(command, args) {
  execFileSync(command, args, {
    cwd: projectDir,
    env: process.env,
    stdio: 'inherit',
  });
}

function findServerEntry(outDir) {
  const candidates = [outDir];

  while (candidates.length > 0) {
    const dir = candidates.pop();
    const entries = readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = resolve(dir, entry.name);

      if (entry.isDirectory()) {
        candidates.push(fullPath);
        continue;
      }

      if (/^entry-server\.(m?js|cjs)$/.test(entry.name)) {
        return fullPath;
      }
    }
  }

  if (!existsSync(outDir)) {
    throw new Error(`SSR output directory not found: ${outDir}`);
  }

  {
    throw new Error(`Could not find SSR entry output in ${outDir}`);
  }
}

async function prerenderHomePage() {
  const rootPlaceholderPattern = /<div id="root">\s*<\/div>/;
  const builtIndexPath = resolve(projectDir, clientOutDir, 'index.html');
  if (!existsSync(builtIndexPath)) {
    throw new Error(`Expected build output at ${builtIndexPath}`);
  }

  const serverEntryPath = findServerEntry(resolve(projectDir, ssrOutDir));
  const serverModule = await import(pathToFileURL(serverEntryPath).href);
  const appHtml = await serverModule.render();
  const builtHtml = readFileSync(builtIndexPath, 'utf8');
  const prerenderedHtml = builtHtml.replace(rootPlaceholderPattern, `<div id="root">${appHtml}</div>`);

  if (prerenderedHtml === builtHtml) {
    throw new Error('Failed to inject prerendered app HTML into index.html');
  }

  writeFileSync(builtIndexPath, prerenderedHtml);
}

async function main() {
  rmSync(resolve(projectDir, clientOutDir), { force: true, recursive: true });
  rmSync(resolve(projectDir, ssrOutDir), { force: true, recursive: true });

  run(npxCommand, ['vite', 'build', '--outDir', clientOutDir]);
  run(npxCommand, ['vite', 'build', '--ssr', 'src/entry-server.jsx', '--outDir', ssrOutDir]);
  await prerenderHomePage();
  rmSync(resolve(projectDir, ssrOutDir), { force: true, recursive: true });
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});