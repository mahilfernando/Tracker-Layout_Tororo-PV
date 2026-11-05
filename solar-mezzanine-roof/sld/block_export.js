const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1600, height: 640 }, deviceScaleFactor: 3 });
  await p.goto('file://' + __dirname + '/PV_Block_Diagram.svg');
  await p.screenshot({ path: __dirname + '/PV_Block_Diagram.png', clip: { x: 0, y: 0, width: 1600, height: 640 } });
  await p.goto('file://' + __dirname + '/PV_Block_Diagram.html');
  await p.pdf({ path: __dirname + '/PV_Block_Diagram.pdf', preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
