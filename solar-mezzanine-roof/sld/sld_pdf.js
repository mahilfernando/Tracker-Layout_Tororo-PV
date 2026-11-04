const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1680, height: 1060 }, deviceScaleFactor: 2 });
  await p.goto('file://' + __dirname + '/SLD.html', { waitUntil: 'load' });
  await p.pdf({ path: __dirname + '/PV_Single_Line_Diagram.pdf', preferCSSPageSize: true, printBackground: true });
  await p.addStyleTag({ content: '.sld{width:1680px!important}' });
  await (await p.$('svg.sld')).screenshot({ path: __dirname + '/PV_Single_Line_Diagram.png' });
  await b.close();
})();
