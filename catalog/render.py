#!/usr/bin/env python3
"""쿼카 모션랩 모션 하나를 영상 파일로 뽑는 도구 (Playwright + ffmpeg).
저장소를 받아 둔 폴더에서 실행합니다. 사이트(index.html)의 quokaLab.html()로 문구·비율·색을 넣은 장면을 만들고, 한 장씩 찍어 묶습니다.

  python3 catalog/render.py --id sf-travel-box --ratio 9:16 --secs 6 \\
      --set '{"LINES": ["선생님, 이거", "딱 *3초면 / 돼요"]}' --alpha --out scene01.webm
  python3 catalog/render.py --id kt-ladder --out title.mp4               # 비율·길이는 모션 기본값(한 바퀴)
  python3 catalog/render.py --batch plan.json                            # 여러 장면을 차례로 (아래 모양)

  plan.json = {"out_dir": "scenes", "concat": "final.mp4",
               "scenes": [{"id": "...", "secs": 4, "set": {...}, "ratio": "9:16"}, ...]}
  (concat은 투명이 아닌 장면을 같은 크기로 이어 붙임)

옵션: --font 눈누글꼴이름  --point #rrggbb(포인트 색)  --bg #rrggbb  --words a,b,c  --fps 30  --start 0(시작 초)
      --alpha  투명 배경 (.webm = VP9 알파, .mov = ProRes 4444 알파, .png 폴더)   --frames 폴더 (낱장만)
"""
import argparse, asyncio, functools, http.server, json, os, shutil, socketserver, ssl, subprocess, sys, tempfile, threading, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # 저장소 폴더 (index.html이 있는 곳)
SIZE = {'1 / 1': (1080, 1080), '16 / 9': (1920, 1080), '4 / 5': (1080, 1350), '9 / 16': (1080, 1920)}

def norm_ratio(r):
    if not r: return ''
    r = r.replace(' ', '').replace(':', '/')
    return {'9/16': '9 / 16', '16/9': '16 / 9', '1/1': '1 / 1', '4/5': '4 / 5'}.get(r, '')

# 바깥 주소(글꼴·three.js)는 파이썬이 대신 받아 브라우저에 건넴 (프록시·인증서 설정을 그대로 따름)
CA = next((p for p in [os.environ.get('SSL_CERT_FILE'), os.environ.get('REQUESTS_CA_BUNDLE'), '/root/.ccr/ca-bundle.crt'] if p and os.path.exists(p)), None)
CTX = ssl.create_default_context(cafile=CA) if CA else ssl.create_default_context()
PROXY = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({'https': PROXY, 'http': PROXY} if PROXY else {}), urllib.request.HTTPSHandler(context=CTX))
CACHE = {}
def fetch(url):
    if url in CACHE: return CACHE[url]
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/126.0 Safari/537.36', 'Accept': '*/*'})
        with OPENER.open(req, timeout=40) as r:
            CACHE[url] = (r.status, r.headers.get('Content-Type', 'application/octet-stream'), r.read())
    except Exception as e:
        CACHE[url] = (599, 'text/plain', str(e).encode())
    return CACHE[url]

def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    handler = functools.partial(Quiet, directory=root)
    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]

async def render_one(ctx, port, sc, out, fps):
    from PIL import Image
    alpha = bool(sc.get('alpha'))
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.goto(f'http://127.0.0.1:{port}/index.html', wait_until='domcontentloaded', timeout=180000)
    await pg.wait_for_function('window.quokaLab', timeout=60000)
    meta = await pg.evaluate("id => quokaLab.catalog().find(m => m.id === id) || null", sc['id'])
    if not meta: raise SystemExit('없는 id: ' + sc['id'])
    ratio = norm_ratio(sc.get('ratio')) or meta['ratio']
    W, H = SIZE.get(ratio, (1080, 1080))
    secs = float(sc.get('secs') or meta['loop'] or 6)
    opts = {'set': sc.get('set') or {}, 'ratio': ratio, 'player': True, 'transparent': alpha}
    for k in ('font', 'point', 'bg'):
        if sc.get(k): opts[k] = sc[k]
    if sc.get('words'): opts['words'] = sc['words'] if isinstance(sc['words'], list) else [w.strip() for w in str(sc['words']).split(',')]
    html = await pg.evaluate('([id, o]) => quokaLab.html(id, o)', [sc['id'], opts])
    await pg.close()
    html = html.replace('const CONFIG = {', 'const CONFIG = {\n    autoplay: false,', 1)
    fit = f'<style>html,body{{margin:0!important;width:{W}px;height:{H}px;overflow:hidden;min-height:0!important;display:block!important}}' + \
          f'[id^="qm-"]{{width:{W}px!important;max-width:none!important;margin:0!important}}' + ('html,body{background:transparent!important}' if alpha else '') + '</style>'
    html = html.replace('</head>', fit + '</head>', 1)
    tmp = tempfile.mkdtemp(prefix='qm-scene-', dir=ROOT)
    try:
        open(os.path.join(tmp, 'scene.html'), 'w', encoding='utf-8').write(html)
        sp = await ctx.new_page(); sp.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await sp.set_viewport_size({'width': W, 'height': H})
        await sp.goto(f'http://127.0.0.1:{port}/{os.path.basename(tmp)}/scene.html', timeout=180000)
        await sp.wait_for_function('window.qmPlayer', timeout=60000)
        # 쓰이는 글자를 한 번 훑어 글꼴을 다 불러온 뒤에 찍음
        start = float(sc.get('start') or 0)
        for k in range(0, int(secs * 2) + 1):
            await sp.evaluate(f'qmPlayer.seek({start + k / 2})')
        await sp.evaluate('document.fonts.ready.then(() => true)'); await sp.wait_for_timeout(900)
        bad = await sp.evaluate("[...document.fonts].filter(f => f.status === 'error').map(f => f.family)")
        frames = sc.get('frames_dir') or os.path.join(tmp, 'frames')
        os.makedirs(frames, exist_ok=True)
        stage = await sp.query_selector('[id^="qm-"]')
        n = int(round(secs * fps))
        for i in range(n):
            await sp.evaluate(f'qmPlayer.seek({start + i / fps})')
            await stage.screenshot(path=os.path.join(frames, f'f{i:05d}.png'), omit_background=alpha)
        await sp.close()
        if sc.get('frames_only'):
            print(f"{sc['id']}: 낱장 {n}장 → {frames}"); return out
        ext = os.path.splitext(out)[1].lower()
        pat = os.path.join(frames, 'f%05d.png')
        if alpha and ext == '.webm': codec = ['-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', '28', '-auto-alt-ref', '0']
        elif alpha and ext == '.mov': codec = ['-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le']
        elif ext == '.webm': codec = ['-c:v', 'libvpx-vp9', '-pix_fmt', 'yuv420p', '-b:v', '0', '-crf', '30']
        else: codec = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart']
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', pat] + codec + [out], check=True)
        size = os.path.getsize(out)
        print(f"{sc['id']}: {out} · {W}×{H} · {secs:g}초 · " + (f'{size / 1048576:.1f}MB' if size > 1048576 else f'{size // 1024}KB') + (f' · 글꼴 못 불러옴: {bad}' if bad else '') + (f' · 오류: {errs[:2]}' if errs else ''))
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

async def main_async(scenes, fps, concat, out_dir):
    from playwright.async_api import async_playwright
    httpd, port = serve(ROOT)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--use-angle=swiftshader', '--proxy-server=direct://'])
        ctx = await b.new_context(device_scale_factor=1)
        async def route(r):
            url = r.request.url
            if url.startswith('http://127.0.0.1') or url.startswith('data:') or url.startswith('blob:') or url.startswith('about:'): return await r.continue_()
            st, ct, body = await asyncio.get_event_loop().run_in_executor(None, fetch, url)
            if st >= 400: return await r.abort()
            await r.fulfill(status=st, headers={'content-type': ct, 'access-control-allow-origin': '*'}, body=body)
        await ctx.route('**/*', route)
        outs = []
        for i, sc in enumerate(scenes):
            out = sc.get('out') or os.path.join(out_dir or '.', f"{i + 1:02d}_{sc['id']}" + ('.webm' if sc.get('alpha') else '.mp4'))
            if os.path.dirname(out): os.makedirs(os.path.dirname(out), exist_ok=True)
            outs.append(await render_one(ctx, port, sc, out, fps))
        await b.close()
    httpd.shutdown()
    if concat:
        lst = os.path.join(out_dir or '.', '_list.txt')
        open(lst, 'w').write(''.join(f"file '{os.path.abspath(o)}'\n" for o in outs))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', concat], check=True)
        print('이어 붙임:', concat)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--id'); ap.add_argument('--ratio'); ap.add_argument('--secs', type=float); ap.add_argument('--start', type=float)
    ap.add_argument('--set', help='JSON: {"TITLE": "…", "LINES": ["…", "…"]}'); ap.add_argument('--words')
    ap.add_argument('--font'); ap.add_argument('--point'); ap.add_argument('--bg')
    ap.add_argument('--alpha', action='store_true'); ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--out'); ap.add_argument('--frames'); ap.add_argument('--batch')
    a = ap.parse_args()
    if not os.path.exists(os.path.join(ROOT, 'index.html')): sys.exit('index.html을 못 찾았어요. 저장소를 받은 폴더 안의 catalog/render.py로 실행하세요.')
    if a.batch:
        plan = json.load(open(a.batch, encoding='utf-8'))
        asyncio.run(main_async(plan['scenes'], plan.get('fps', a.fps), plan.get('concat'), plan.get('out_dir', 'scenes')))
        return
    if not a.id: ap.print_help(); return
    sc = {'id': a.id, 'ratio': a.ratio, 'secs': a.secs, 'start': a.start, 'set': json.loads(a.set) if a.set else {}, 'words': a.words,
          'font': a.font, 'point': a.point, 'bg': a.bg, 'alpha': a.alpha, 'out': a.out or (a.id + ('.webm' if a.alpha else '.mp4'))}
    if a.frames: sc['frames_dir'] = a.frames; sc['frames_only'] = True
    asyncio.run(main_async([sc], a.fps, None, None))

if __name__ == '__main__':
    main()
