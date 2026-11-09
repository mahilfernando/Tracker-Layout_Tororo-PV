// PV_SLD_Detailed.html -> PV_SLD_Detailed.pdf (A3 landscape) + PV_SLD_Detailed.png
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1680, height: 1188 }, deviceScaleFactor: 2 });
  await p.goto('file://' + __dirname + '/PV_SLD_Detailed.html', { waitUntil: 'load' });
  await p.pdf({ path: __dirname + '/PV_SLD_Detailed.pdf', width: '420mm', height: '297mm', printBackground: true, pageRanges: '1' });
  await p.setContent(require('fs').readFileSync(__dirname + '/PV_SLD_Detailed.svg', 'utf8').replace(/^<\?xml[^>]*>/, ''));
  await (await p.$('svg')).screenshot({ path: __dirname + '/PV_SLD_Detailed.png' });
  await b.close();
})();
