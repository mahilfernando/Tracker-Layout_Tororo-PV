const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + __dirname + '/PV_Layout_Enerack_10deg.html', { waitUntil: 'load' });
  await p.pdf({ path: __dirname + '/PV_Layout_Enerack_10deg.pdf', preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
