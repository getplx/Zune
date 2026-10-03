// Render brief.html -> PDF with Chromium (Playwright).
//  1) detail sheets (.flowcols) are split into as many continuation pages as their content needs
//  2) every page is auto-shrunk (scale 1.0 -> 0.72) until its content fits; shrink warnings are printed
//  3) page numbers are renumbered; overflow that survives is reported
// Usage: node render.js <abs/path/brief.html> <abs/path/out.pdf>
const { chromium } = require('playwright')

;(async () => {
  const [, , htmlPath, pdfPath] = process.argv
  const browser = await chromium.launch()
  const page = await browser.newPage()
  await page.goto('file://' + htmlPath)
  await page.waitForTimeout(300)
  const report = await page.evaluate(() => {
    const GAP_MM = 5
    const mm = (v) => v * 96 / 25.4
    // 1) split flow pages
    ;[...document.querySelectorAll('.page')].forEach((pg) => {
      const cols = pg.querySelector('.flowcols')
      if (!cols) return
      const gap = mm(GAP_MM)
      const k = Math.max(1, Math.ceil((cols.scrollWidth + gap - 2) / (cols.clientWidth + gap)))
      let last = pg
      for (let i = 1; i < k; i++) {
        const c = pg.cloneNode(true)
        c.querySelector('.flowcols').style.transform = `translateX(${-i * (cols.clientWidth + gap)}px)`
        const h1 = c.querySelector('h1')
        if (h1) h1.insertAdjacentHTML('beforeend', ` <span style="font-size:10pt;color:#5b6475;font-weight:400">(${i + 1}/${k})</span>`)
        last.after(c)
        last = c
      }
      if (k > 1) {
        const h1 = pg.querySelector('h1')
        if (h1) h1.insertAdjacentHTML('beforeend', ` <span style="font-size:10pt;color:#5b6475;font-weight:400">(1/${k})</span>`)
      }
    })
    // 2) auto-fit
    const pages = [...document.querySelectorAll('.page')]
    const shrunk = []
    pages.forEach((pg, idx) => {
      const fit = pg.querySelector('.fit')
      if (!fit || pg.querySelector('.flowcols') || pg.classList.contains('cover')) return
      let z = 1
      const skip = new Set(['TABLE', 'THEAD', 'TBODY', 'TR', 'TD', 'TH', 'svg', 'SVG', 'path', 'g', 'text', 'rect', 'line', 'circle', 'defs', 'marker', 'SPAN', 'B', 'I', 'S'])
      const innerOver = () => [...fit.querySelectorAll('*')].some((el) => {
        if (skip.has(el.tagName) || el.closest('svg')) return false
        const d = getComputedStyle(el).display
        if (d === 'inline' || d.startsWith('table')) return false
        return el.scrollHeight - el.clientHeight > 2
      })
      const over = () => fit.scrollHeight - fit.clientHeight > 1 || fit.scrollWidth - fit.clientWidth > 1 || innerOver()
      while (over() && z > 0.72) {
        z = Math.round((z - 0.02) * 100) / 100
        fit.style.setProperty('--z', z)
      }
      if (z < 1) shrunk.push({ page: idx + 1, z, still: over() })
    })
    // 3) renumber
    pages.forEach((pg, i) => {
      const n = pg.querySelector('.pgn'), t = pg.querySelector('.pgt')
      if (n) n.textContent = i + 1
      if (t) t.textContent = pages.length
    })
    const rows = pages.map((pg, i) => {
      const fit = pg.querySelector('.fit')
      const h = pg.querySelector('h1')
      return { page: i + 1, title: h ? h.textContent.slice(0, 50) : '', over: fit ? Math.max(fit.scrollHeight - fit.clientHeight, fit.scrollWidth - fit.clientWidth) : 0 }
    })
    return { total: pages.length, shrunk, bad: rows.filter((r) => r.over > 1) }
  })
  console.log(`pages: ${report.total}; shrunk: ${report.shrunk.length}; still overflowing: ${report.bad.length}`)
  report.shrunk.filter((r) => r.z < 0.85 || r.still).forEach((r) => console.log(`  p${r.page} scale ${r.z}${r.still ? ' STILL OVERFLOWS' : ''}`))
  report.bad.forEach((r) => console.log(`  OVERFLOW p${r.page} "${r.title}" by ${r.over}px`))
  await page.pdf({ path: pdfPath, preferCSSPageSize: true, printBackground: true })
  await browser.close()
})()
