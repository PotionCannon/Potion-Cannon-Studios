from pathlib import Path
import html
import shutil
from urllib.parse import urlsplit

r = Path(__file__).resolve().parent
out = r / '_site'
if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)
if (r / 'assets').is_dir():
    shutil.copytree(r / 'assets', out / 'assets')

def parse(path):
    s = path.read_text(encoding='utf-8')
    parts = s.split('---', 2)
    if len(parts) < 3:
        return {}, s.strip()
    m = {}
    for line in parts[1].strip().splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            m[k.strip()] = v.strip().strip('"').strip("'")
    return m, parts[2].strip()

def page(title, body, depth=0):
    prefix = '../' * depth
    nav = ' '.join(
        '<a href="' + prefix + x + '.html">' + x.title() + '</a>'
        for x in ['index', 'games', 'blog', 'about', 'contact']
    )
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>' + html.escape(title) + '</title>'
        '<link rel="stylesheet" href="' + prefix + 'assets/style.css">'
        '<link rel="icon" href="' + prefix + 'assets/icon.png">'
        '</head><body><header><nav class="wrap"><b>Potion Cannon Studios</b><div>'
        + nav + '</div></nav></header><main class="wrap">' + body
        + '</main><footer class="wrap">Potion Cannon Studios</footer></body></html>'
    )

def save(name, title, body):
    p = out / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(page(title, body, len(Path(name).parts)-1), encoding='utf-8')

def demo_url(value):
    """Only allow demo files in assets/demos, not external or traversal URLs."""
    value = value.strip().replace('\\', '/').lstrip('/')
    if not value:
        return None
    if value.startswith('assets/demos/'):
        value = value[len('assets/demos/'):]
    elif value.startswith('demos/'):
        value = value[len('demos/'):]
    if not value or any(x in ('', '.', '..') for x in value.split('/')):
        return None
    if not value.lower().endswith('.html') or '?' in value or '#' in value:
        return None
    source = (r / 'assets' / 'demos' / value).resolve()
    root = (r / 'assets' / 'demos').resolve()
    if not source.is_relative_to(root) or not source.is_file():
        print('Warning: demo file missing or invalid:', value)
        return None
    return '../assets/demos/' + '/'.join(
        __import__('urllib.parse', fromlist=['quote']).quote(part, safe='')
        for part in value.split('/')
    )

def demo_player(url, title):
    safe_url = html.escape(url, quote=True)
    safe_title = html.escape(title, quote=True)
    return (
        '<section class="section game-demo" id="demo">'
        '<h2>Playable Demo</h2>'
        '<button type="button" id="demo-launch">Play Demo</button>'
        '<div id="demo-shell" hidden style="position:relative;margin-top:1rem;'
        'background:#000;aspect-ratio:16/9;max-height:80vh">'
        '<iframe id="demo-frame" title="' + safe_title + ' demo" '
        'data-src="' + safe_url + '" allow="fullscreen; autoplay; gamepad" '
        'allowfullscreen style="width:100%;height:100%;border:0;display:block"></iframe>'
        '<div style="position:absolute;right:8px;top:8px;z-index:2;display:flex;gap:8px">'
        '<button type="button" id="demo-fullscreen">Fullscreen</button>'
        '<button type="button" id="demo-close">Close Demo</button></div></div>'
        '</section><script>(function(){'
        'const shell=document.getElementById("demo-shell");'
        'const frame=document.getElementById("demo-frame");'
        'document.getElementById("demo-launch").addEventListener("click",function(){'
        'shell.hidden=false;if(!frame.src)frame.src=frame.dataset.src;'
        'shell.scrollIntoView({behavior:"smooth",block:"nearest"});});'
        'document.getElementById("demo-close").addEventListener("click",function(){'
        'if(document.fullscreenElement)document.exitFullscreen();'
        'frame.removeAttribute("src");shell.hidden=true;});'
        'document.getElementById("demo-fullscreen").addEventListener("click",function(){'
        'if(shell.requestFullscreen) shell.requestFullscreen();});'
        'document.addEventListener("fullscreenchange",function(){'
        'const full=document.fullscreenElement===shell;'
        'shell.style.maxHeight=full?"none":"80vh";'
        'shell.style.height=full?"100vh":"";'
        'shell.style.aspectRatio=full?"auto":"16/9";'
        '});'
        '})();</script>'
    )

def listing(kind):
    cards = []
    directory = r / 'content' / kind
    for f in sorted(directory.glob('*.md'), reverse=True):
        m, b = parse(f)
        if kind == 'posts' and m.get('published') != 'true':
            continue
        title = html.escape(m.get('title', f.stem))
        summary = html.escape(m.get('summary', ''))
        cards.append(
            '<div class="card"><h3><a href="' + kind + '/' + f.stem
            + '.html">' + title + '</a></h3><p>' + summary + '</p></div>'
        )
        body = (
            '<article class="article"><h1>' + title
            + '</h1><p class="muted">'
            + html.escape(m.get('date', m.get('status', '')))
            + '</p>' + ''.join('<p>' + html.escape(x) + '</p>' for x in b.split('\n\n'))
            + '</article>'
        )
        if kind == 'games':
            requested = m.get('demo', '')
            if requested:
                url = demo_url(requested)
                if url:
                    body += demo_player(url, m.get('title', f.stem))
        save(kind + '/' + f.stem + '.html', title, body)
    return '<div class="grid">' + ''.join(cards) + '</div>'

games = listing('games')
posts = listing('posts')
save('index.html', 'Home', '<section class="hero"><img src="assets/logo.png" alt="Potion Cannon Studios"><h1>Independent games. Creative experiments.</h1><p>Explore our games and follow our development journey.</p></section><section class="section"><h2>Games</h2>' + games + '</section><section class="section"><h2>Latest development updates</h2>' + posts + '</section>')
save('games.html', 'Games', '<section class="section"><h1>Games</h1>' + games + '</section>')
save('blog.html', 'Development blog', '<section class="section"><h1>Development blog</h1>' + posts + '</section>')
save('about.html', 'About', '<article class="article"><h1>About Potion Cannon Studios</h1><p>Replace this text with your studio story.</p></article>')
save('contact.html', 'Contact', '<article class="article"><h1>Contact</h1><p>Add your public business email or social links here.</p></article>')
print('Site built')
