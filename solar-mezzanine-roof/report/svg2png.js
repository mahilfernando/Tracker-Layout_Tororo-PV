// usage: node svg2png.js in.svg out.png width height
const { chromium } = require('playwright'); const fs = require('fs');
const [,, inp, out, w, h] = process.argv;
(async () => { const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 3, viewport: { width: +w + 40, height: +h + 40 } });
  const svg = fs.readFileSync(inp, 'utf8').replace('<svg ', `<svg width="${w}" height="${h}" `);
  await p.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
  await (await p.$('svg')).screenshot({ path: out }); await b.close(); })();
