// PDF (A3) + hi-res PNG of the engineering SLD
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1680, height: 1188 }, deviceScaleFactor: 3 });
  await p.goto('file://' + __dirname + '/PV_SLD_Engineering.html', { waitUntil: 'load' });
  await p.pdf({ path: __dirname + '/PV_SLD_Engineering.pdf', preferCSSPageSize: true, printBackground: true });
  await p.goto('file://' + __dirname + '/PV_SLD_Engineering.svg', { waitUntil: 'load' });
  await p.screenshot({ path: __dirname + '/PV_SLD_Engineering.png', clip: { x: 0, y: 0, width: 1680, height: 1188 } });
  await b.close();
})();
