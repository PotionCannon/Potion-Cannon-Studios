from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
from urllib.parse import urlsplit, quote
import html, re, shutil

r=Path(__file__).resolve().parent
out=r/'_site'
if out.exists(): shutil.rmtree(out)
out.mkdir(parents=True)
if (r/'assets').is_dir(): shutil.copytree(r/'assets',out/'assets')

def parse(path):
    s=path.read_text(encoding='utf-8')
    parts=s.split('---',2)
    if len(parts)<3:return {},s.strip()
    m={}
    for line in parts[1].strip().splitlines():
        if ':' in line:
            k,v=line.split(':',1)
            m[k.strip()]=v.strip().strip('"').strip("'")
    return m,parts[2].strip()

def page(title,body,depth=0):
    prefix='../'*depth
    nav=' '.join('<a href="'+prefix+x+'.html">'+x.title()+'</a>' for x in ['index','games','blog','about','contact'])
    return ('<!doctype html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>'+html.escape(title)+'</title>'
            '<link rel="stylesheet" href="'+prefix+'assets/style.css">'
            '<link rel="icon" href="'+prefix+'assets/icon.png">'
            '</head><body><header><nav class="wrap"><b>Potion Cannon Studios</b><div>'
            +nav+'</div></nav></header><main class="wrap">'+body+
            '</main><footer class="wrap">Potion Cannon Studios</footer></body></html>')

def save(name,title,body):
    p=out/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(page(title,body,len(Path(name).parts)-1),encoding='utf-8')

def demo_url(value):
    value=value.strip().replace('\\','/').lstrip('/')
    if value.startswith('assets/demos/'):value=value[len('assets/demos/'):]
    elif value.startswith('demos/'):value=value[len('demos/'):]
    if not value or any(x in ('','.','..') for x in value.split('/')) or not value.lower().endswith('.html') or '?' in value or '#' in value:return None
    source=(r/'assets'/'demos'/value).resolve()
    root=(r/'assets'/'demos').resolve()
    if not source.is_relative_to(root) or not source.is_file():
        print('Warning: demo file missing or invalid:',value)
        return None
    return '../assets/demos/'+'/'.join(quote(part,safe='') for part in value.split('/'))

def demo_player(url,title):
    safe_url=html.escape(url,quote=True)
    safe_title=html.escape(title,quote=True)
    return (
      '<section class="section game-demo" id="demo"><h2>Playable Demo</h2>'
      '<button type="button" class="btn demo-button" id="demo-launch">Play Demo</button>'
      '<div id="demo-shell" hidden>'
      '<iframe id="demo-frame" title="'+safe_title+' demo" data-src="'+safe_url+'" '
      'allow="fullscreen; autoplay; gamepad" allowfullscreen></iframe>'
      '</div><div class="demo-actions" id="demo-actions" hidden>'
      '<button type="button" class="btn demo-button" id="demo-fullscreen">Fullscreen</button>'
      '<button type="button" class="btn demo-button" id="demo-close">Close Demo</button></div>'
      '</section><script>(function(){'
      'const shell=document.getElementById("demo-shell");'
      'const frame=document.getElementById("demo-frame");'
      'const actions=document.getElementById("demo-actions");'
      'const launch=document.getElementById("demo-launch");'
      'launch.addEventListener("click",function(){'
      'shell.hidden=false;actions.hidden=false;launch.hidden=true;'
      'if(!frame.getAttribute("src"))frame.src=frame.dataset.src;'
      'shell.scrollIntoView({behavior:"smooth",block:"nearest"});});'
      'document.getElementById("demo-close").addEventListener("click",function(){'
      'if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});'
      'frame.removeAttribute("src");shell.hidden=true;actions.hidden=true;launch.hidden=false;});'
      'document.getElementById("demo-fullscreen").addEventListener("click",function(){'
      'if(frame.requestFullscreen)frame.requestFullscreen().catch(()=>{'
      'if(shell.requestFullscreen)shell.requestFullscreen().catch(()=>{});});'
      'else if(shell.requestFullscreen)shell.requestFullscreen().catch(()=>{});});'
      'document.addEventListener("fullscreenchange",function(){'
      'shell.classList.toggle("is-fullscreen",document.fullscreenElement===shell);});'
      '})();</script>'
    )

image_pattern=re.compile(r'!\[([^\]\n]*)\]\((https?://[^\s)]+|/[^\s)]+|(?:\.\./)*assets/[^\s)]+)\)')
link_pattern=re.compile(r'(?<!!)\[([^\]\n]+)\]\((https?://[^\s)]+)\)')
# Inline Markdown formatting. Escape source first so user-supplied HTML is not executed.
format_pattern=re.compile(r'(?<!\*)\*\*\*(?=\S)(.+?)(?<=\S)\*\*\*(?!\*)|(?<!\*)\*\*(?=\S)(.+?)(?<=\S)\*\*(?!\*)|(?<!\*)\*(?=\S)(.+?)(?<=\S)\*(?!\*)')
def inline_md(text):
    text=html.escape(text)
    def img(m):
        url=html.unescape(m.group(2))
        parsed=urlsplit(url)
        if parsed.scheme and parsed.scheme not in ('https','http'):return m.group(0)
        return '<img loading="lazy" src="'+html.escape(url,quote=True)+'" alt="'+m.group(1)+'">'
    text=image_pattern.sub(img,text)
    text=link_pattern.sub(lambda m:'<a href="'+html.escape(html.unescape(m.group(2)),quote=True)+'" rel="noopener noreferrer">'+m.group(1)+'</a>',text)
    text=format_pattern.sub(lambda m: ('<strong><em>'+m.group(1)+'</em></strong>' if m.group(1) is not None else '<strong>'+m.group(2)+'</strong>' if m.group(2) is not None else '<em>'+m.group(3)+'</em>'),text)
    return text

def formatted_text(source):
    # Admin textareas may save literal backslash-n instead of a newline.
    # Support both while leaving ordinary backslashes alone.
    source=source.replace('\\r\\n','\n').replace('\\n','\n').replace('\r\n','\n').replace('\r','\n')
    return '<br>'.join(inline_md(part) for part in source.split('\n'))

def markdown_body(source):
    source=source.replace('\\r\\n','\n').replace('\\n','\n')
    blocks=[]
    for para in re.split(r'\n\s*\n',source.strip()):
        if not para.strip():continue
        lines=para.splitlines()
        if len(lines)==1 and re.match(r'^#{1,3} ',lines[0]):
            match=re.match(r'^(#{1,3}) (.*)',lines[0])
            level=len(match.group(1))
            blocks.append(f'<h{level}>'+inline_md(match.group(2))+f'</h{level}>')
        else:
            blocks.append('<p>'+ '<br>'.join(inline_md(x) for x in lines)+'</p>')
    return ''.join(blocks)

def get_date(meta,path):
    for key in ('date','created','created_at'):
        value=meta.get(key,'')
        if value:
            try:return datetime.fromisoformat(value.replace('Z','+00:00')).date()
            except ValueError:pass
    st=path.stat()
    timestamp=getattr(st,'st_birthtime',None) or st.st_mtime
    return datetime.fromtimestamp(timestamp,timezone.utc).date()

def listing(kind):
    entries=[]
    directory=r/'content'/kind
    if not directory.is_dir():return '<p class="muted">Nothing published yet.</p>'
    for f in directory.glob('*.md'):
        m,b=parse(f)
        if kind=='posts' and m.get('published')!='true':continue
        date=get_date(m,f)
        title=html.escape(m.get('title',f.stem))
        summary=formatted_text(m.get('summary',''))
        href=kind+'/'+quote(f.stem,safe='')+'.html'
        entries.append((date,f.stem,title,summary,href))
        article=('<article class="article"><h1>'+title+'</h1>'
                 '<p class="muted">'+html.escape(date.strftime('%B %d, %Y'))+'</p>'
                 +markdown_body(b)+'</article>')
        if kind=='games' and m.get('demo'):
            url=demo_url(m['demo'])
            if url:article+=demo_player(url,m.get('title',f.stem))
        save(kind+'/'+f.stem+'.html',m.get('title',f.stem),article)
    entries.sort(key=lambda x:(x[0],x[1]),reverse=True)
    if not entries:return '<p class="muted">Nothing published yet.</p>'
    groups=defaultdict(list)
    for entry in entries:groups[entry[0].strftime('%B %Y')].append(entry)
    sections=[]
    for month,items in groups.items():
        cards=[]
        for date,stem,title,summary,href in items:
            cards.append('<article class="card timeline-card"><time datetime="'+date.isoformat()+'">'+
                         html.escape(date.strftime('%b %d, %Y'))+'</time><h3><a href="'+
                         html.escape(href,quote=True)+'">'+title+'</a></h3><p>'+summary+'</p></article>')
        sections.append('<section class="timeline-month"><h2 class="month-divider"><span>'+
                        html.escape(month)+'</span></h2><div class="timeline-cards">'+''.join(cards)+'</div></section>')
    return '<div class="timeline-scroll" tabindex="0" aria-label="'+('Game posts' if kind=='games' else 'Development posts')+'">'+''.join(sections)+'</div>'

games=listing('games')
posts=listing('posts')
save('index.html','Home','<section class="hero"><img src="assets/logo.png" alt="Potion Cannon Studios"><h1>Independent games. Creative experiments.</h1><p>Explore our games and follow our development journey.</p></section><section class="section"><h2>Games</h2>'+games+'</section><section class="section"><h2>Latest development updates</h2>'+posts+'</section>')
home = out / 'index.html'
home.write_text(home.read_text(encoding='utf-8').replace('</body>', '<script src="assets/hidden/winter-launcher.js" defer></script></body>'), encoding='utf-8')
save('games.html','Games','<section class="section"><h1>Games</h1>'+games+'</section>')
save('blog.html','Development blog','<section class="section"><h1>Development blog</h1>'+posts+'</section>')
save('about.html','About','<article class="article"><h1>About Potion Cannon Studios</h1><p>Replace this text with your studio story.</p></article>')
save('contact.html','Contact','<article class="article"><h1>Contact</h1><p>Add your public business email or social links here.</p></article>')
print('Site built')
