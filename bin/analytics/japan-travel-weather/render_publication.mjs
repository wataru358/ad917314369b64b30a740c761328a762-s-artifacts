// ローカルレビュー用のHTMLと配布可能なPNGを作る。サイトへの公開は行わない。
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { createMarkdownProcessor } from '@astrojs/markdown-remark';
import sharp from 'sharp';

const base = path.dirname(fileURLToPath(import.meta.url));
const output = path.join(base, 'publication');
const processor = await createMarkdownProcessor();
const style = `body{margin:0;background:#fafaf7;color:#203333;font:18px/1.7 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:48px 24px}h1{font-size:clamp(30px,5vw,48px);line-height:1.15}h2{margin-top:2.5em;line-height:1.3}p,li{max-width:78ch}a{color:#076b70}img{max-width:100%;height:auto}blockquote{margin:24px 0;padding:12px 20px;background:#edf1ed;border-left:4px solid #66847e;font-size:15px}table{border-collapse:collapse;min-width:760px;width:100%;font-size:14px;font-variant-numeric:tabular-nums}th,td{text-align:left;padding:10px 12px;border-bottom:1px solid #ced9d3}th{background:#e6eeea}tbody tr:nth-child(even){background:#f2f5f1}.table-wrap{overflow-x:auto;margin:24px 0}pre{overflow:auto;background:#eaf0eb;padding:18px;font-size:14px}code{font-size:.9em}nav{font-size:14px;margin-bottom:30px}`;
for (const name of ['travel-article.en', 'learning-article.en']) {
  const markdown = await readFile(path.join(output, `${name}.md`), 'utf8');
  const rendered = await processor.render(markdown);
  const content = rendered.code.replaceAll('<table>', '<div class="table-wrap"><table>').replaceAll('</table>', '</table></div>').replaceAll('<p><img', '<p class="chart-wrap"><img');
  const title = markdown.split('\n')[0].replace(/^# /, '');
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title><style>${style}.chart-wrap{max-width:none;overflow-x:auto}.chart-wrap img{min-width:760px;display:block}</style></head><body><main><nav>Local review draft · <a href="travel-article.en.html">Travel article</a> · <a href="learning-article.en.html">Learning article</a></nav>${content}</main></body></html>`;
  await writeFile(path.join(output, `${name}.html`), html);
}
await sharp(path.join(output, 'weather-monthly.svg'), { density: 160 }).png().toFile(path.join(output, 'weather-monthly.png'));
console.log('Rendered two local HTML drafts and weather-monthly.png');
