// Kampala_Marriott_PV_Graphic_Proposal.html -> .pdf (A4, 16 pages) + page previews for checking
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + __dirname + '/Kampala_Marriott_PV_Graphic_Proposal.html', { waitUntil: 'load' });
  await p.pdf({ path: __dirname + '/Kampala_Marriott_PV_Graphic_Proposal.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  if (process.argv[2]) {
    await p.setViewportSize({ width: 794, height: 1123 });
    const n = await p.$$eval('section.page', s => s.length);
    const els = await p.$$('section.page');
    for (let i = 0; i < n; i++) await els[i].screenshot({ path: `${process.argv[2]}/p${String(i + 1).padStart(2, '0')}.png` });
  }
  await b.close();
})();
