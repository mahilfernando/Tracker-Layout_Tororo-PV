// Render cover (no header/footer) and body (with header/footer) separately, then merge with pdfunite.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const hdr = '<div style="font-size:7px;width:100%;padding:0 18mm;color:#5b6673;font-family:Inter,Arial;display:flex;justify-content:space-between"><span>Marriott Hotel – Rooftop Solar PV</span><span>PV-RPT-D18102-001 Rev A</span></div>';
const ftr = '<div style="font-size:7px;width:100%;padding:0 18mm;color:#5b6673;font-family:Inter,Arial;text-align:right">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>';
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const url = 'file://' + __dirname + '/Rooftop_PV_Report.html';
  await p.goto(url, { waitUntil: 'load' });
  await p.pdf({ path: '/tmp/_cover.pdf', format: 'A4', preferCSSPageSize: true, printBackground: true, pageRanges: '1' });
  await p.addStyleTag({ content: '@page :first { margin: 22mm 18mm 20mm 18mm; } .cover{display:none!important}' });
  await p.evaluate(() => { const s = document.querySelector('.section'); if (s) s.style.breakBefore = 'auto'; });
  await p.pdf({ path: '/tmp/_body.pdf', format: 'A4', preferCSSPageSize: true, printBackground: true,
    displayHeaderFooter: true, headerTemplate: hdr, footerTemplate: ftr });
  await b.close();
  execFileSync('pdfunite', ['/tmp/_cover.pdf', '/tmp/_body.pdf', __dirname + '/Rooftop_PV_Report.pdf']);
})();
