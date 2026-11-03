const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + __dirname + '/Structure_RFQ.html', { waitUntil: 'load' });
  await p.pdf({ path: __dirname + '/PV_Structure_RFQ.pdf', format: 'A4', preferCSSPageSize: true, printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<div></div>',
    footerTemplate: '<div style="font-size:7px;width:100%;padding:0 18mm;color:#5b6673;font-family:Inter,Arial;display:flex;justify-content:space-between"><span>PV Mounting Structure – RFQ · PV-RFQ-STR-001 Rev A</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>' });
  await b.close();
})();
