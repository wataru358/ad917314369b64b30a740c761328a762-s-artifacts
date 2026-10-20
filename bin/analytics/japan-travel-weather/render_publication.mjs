// 公開用のSVG図をPNGに変換する。
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import sharp from 'sharp';

const base = path.dirname(fileURLToPath(import.meta.url));
const output = path.join(base, 'publication');
await sharp(path.join(output, 'weather-monthly.svg'), { density: 160 }).png().toFile(path.join(output, 'weather-monthly.png'));
console.log('Rendered weather-monthly.png');
