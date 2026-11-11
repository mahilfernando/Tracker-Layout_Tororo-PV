// String_Sizing_Justification.html -> .pdf (A4)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + __dirname + '/String_Sizing_Justification.html', { waitUntil: 'load' });
  await p.pdf({ path: __dirname + '/String_Sizing_Justification.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
