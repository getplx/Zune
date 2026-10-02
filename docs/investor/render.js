// Render brief.html -> PDF with Chromium (Playwright) and report any page whose content overflows.
// Usage: node render.js <abs/path/brief.html> <abs/path/out.pdf>
const { chromium } = require('playwright')

;(async () => {
  const [, , htmlPath, pdfPath] = process.argv
  const browser = await chromium.launch()
  const page = await browser.newPage()
  await page.goto('file://' + htmlPath)
  await page.waitForTimeout(300)
  const rows = await page.evaluate(() =>
    [...document.querySelectorAll('.page')].map((pg, i) => {
      const bd = pg.querySelector('.body')
      const h = pg.querySelector('h1')
      return {
        page: i + 1,
        title: h ? h.textContent.slice(0, 60) : '(no h1)',
        overflowY: bd ? bd.scrollHeight - bd.clientHeight : 0,
        overflowX: bd ? bd.scrollWidth - bd.clientWidth : 0,
      }
    }),
  )
  const bad = rows.filter((r) => r.overflowY > 1 || r.overflowX > 1)
  console.log(`pages: ${rows.length}; overflowing: ${bad.length}`)
  bad.forEach((r) => console.log(`  p${r.page} "${r.title}" overflowY=${r.overflowY}px overflowX=${r.overflowX}px`))
  await page.pdf({ path: pdfPath, preferCSSPageSize: true, printBackground: true })
  await browser.close()
})()
