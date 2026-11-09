// Renderiza index.html cuadro por cuadro a MP4 1080p (uso: node render.js)
const {chromium} = require('playwright');
const {spawn} = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const FPS = 30, out = path.join(__dirname, 'ecogestion_ruta_esg.mp4');
  const b = await chromium.launch();
  const p = await b.newPage({viewport:{width:1920, height:1080}});
  await p.goto('file://' + path.join(__dirname, 'index.html') + '?render=1');
  await p.waitForTimeout(800);
  const DUR = await p.evaluate(() => window.__DUR);
  fs.writeFileSync(path.join(__dirname, 'ecogestion_ruta_esg.srt'), await p.evaluate(() => window.__SRT()));
  const ff = spawn('ffmpeg', ['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-',
    '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-preset','medium','-movflags','+faststart', out], {stdio:['pipe','inherit','inherit']});
  const N = Math.ceil(DUR * FPS);
  for(let i = 0; i < N; i++){
    await p.evaluate(t => window.__seek(t), i / FPS);
    const buf = await p.screenshot({type:'jpeg', quality:92});
    if(!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if(i % 300 === 0) console.log(`frame ${i}/${N}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  console.log('OK', out);
})();
