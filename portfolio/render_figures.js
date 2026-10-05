#!/usr/bin/env node
/**
 * Multi-purpose renderer for the SRG portfolio build.
 *
 * Usage:
 *   node shots.js mmd <in.mmd> <out.png> <width>       render mermaid source to PNG
 *   node shots.js svg <in.svg> <out.png> <width>        rasterize SVG to PNG
 *   node shots.js page <url> <out.png> <vw> <vh> [full] screenshot a page
 *   node shots.js pdf <url> <out.pdf> <opts.json>       print a page to PDF (Chrome headless)
 */
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function main() {
  const [mode, ...rest] = process.argv.slice(2);
  const browser = await puppeteer.launch({
    headless: 'shell',
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none'],
  });
  try {
    const page = await browser.newPage();
    if (mode === 'mmd') {
      const [inFile, outFile, width] = rest;
      const code = fs.readFileSync(inFile, 'utf8');
      await page.setViewport({ width: Number(width) || 1800, height: 1400, deviceScaleFactor: 2 });
      await page.setContent('<!doctype html><body style="margin:0;background:#fff"><div id="c"></div></body>');
      await page.addScriptTag({ path: require.resolve('mermaid/dist/mermaid.min.js') });
      const cssW = Number(width) || 1800;
      const svg = await page.evaluate(async (src, w) => {
        mermaid.initialize({ startOnLoad: false, theme: 'default', themeFontFamily: 'DejaVu Sans' });
        const { svg } = await mermaid.render('fig', src);
        const c = document.getElementById('c');
        c.style.width = w + 'px';
        c.innerHTML = svg;
        const s = c.querySelector('svg');
        if (s && !s.getAttribute('height')) { s.style.maxWidth = 'none'; s.style.width = '100%'; }
        return svg;
      }, code, cssW);
      const el = await page.$('#c');
      await el.screenshot({ path: outFile });
      console.log('mmd ok', outFile, svg.length);
    } else if (mode === 'svg') {
      const [inFile, outFile, width] = rest;
      const svg = fs.readFileSync(inFile, 'utf8');
      const m = svg.match(/width="(\d+)" height="(\d+)"/);
      const w = Number(width) || (m ? Number(m[1]) : 1600);
      const h = m ? Number(m[2]) : 900;
      await page.setViewport({ width: w, height: h, deviceScaleFactor: 2 });
      await page.setContent(
        `<!doctype html><body style="margin:0">${svg}</body>`,
        { waitUntil: 'load' }
      );
      await page.screenshot({ path: outFile, clip: { x: 0, y: 0, width: w, height: h } });
      console.log('svg ok', outFile);
    } else if (mode === 'page') {
      const [url, outFile, vw, vh, full] = rest;
      await page.setViewport({ width: Number(vw), height: Number(vh), deviceScaleFactor: 2 });
      await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });
      await new Promise((r) => setTimeout(r, 2500)); // let Chart.js draw
      await page.screenshot({ path: outFile, fullPage: full === 'full' });
      console.log('page ok', outFile);
    } else if (mode === 'pdf') {
      const [url, outFile, optsFile] = rest;
      const opts = optsFile ? JSON.parse(fs.readFileSync(optsFile, 'utf8')) : {};
      await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });
      await new Promise((r) => setTimeout(r, 2000));
      await page.pdf({
        path: outFile,
        printBackground: true,
        preferCSSPageSize: true,
        ...opts,
      });
      console.log('pdf ok', outFile);
    } else {
      console.error('unknown mode', mode);
      process.exit(2);
    }
  } finally {
    await browser.close();
  }
}
main().catch((e) => { console.error(e); process.exit(1); });
