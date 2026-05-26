import { readdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const distAssets = resolve('dist/assets');
const dotAsset = readdirSync(distAssets).find((name) => name.startsWith('dot-') && name.endsWith('.js'));
if (!dotAsset) {
  throw new Error('Run npm run build before exporting SVG assets.');
}
const { svgSource } = await import(pathToFileURL(resolve(distAssets, dotAsset)).href);
const outputDir = resolve('../docs/assets/architecture');
writeFileSync(resolve(outputDir, 'appsec-pilot-system.svg'), svgSource('index'), 'utf8');
writeFileSync(resolve(outputDir, 'appsec-pilot-runtime.svg'), svgSource('runtime'), 'utf8');
