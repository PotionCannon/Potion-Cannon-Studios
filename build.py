from pathlib import Path
import html, shutil
r=Path(__file__).parent
out=r/'_site'
if out.exists(): shutil.rmtree(out)
shutil.copytree(r/'assets',out/'assets')
def parse(path):
 s=path.read_text()
 a,b=s.split('---',2)[1:]
 m={}
 for line in a.strip().splitlines():
  if ':' in line:
   k,v=line.split(':',1);m[k.strip()]=v.strip().strip('"')
 return m,b.strip()
def page(title,body):
 nav=' '.join('<a href="/'+x+'.html">'+x.title()+'</a>' for x in ['index','games','blog','about','contact'])
 return '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><link rel="stylesheet" href="/assets/style.css"><link rel="icon" href="/assets/icon.png"></head><body><header><nav class="wrap"><b>Potion Cannon Studios</b><div>'+nav+'</div></nav></header><main class="wrap">'+body+'</main><footer class="wrap">Potion Cannon Studios</footer></body></html>'
def save(name,title,body):
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(page(title,body).replace('="/', '="' + ('../' if '/' in name else '')))
def listing(kind):
 cards=[]
 for f in sorted((r/'content'/kind).glob('*.md'),reverse=True):
  m,b=parse(f)
  if kind=='posts' and m.get('published')!='true':continue
  title=html.escape(m.get('title',f.stem));summary=html.escape(m.get('summary',''))
  cards.append('<div class="card"><h3><a href="/'+kind+'/'+f.stem+'.html">'+title+'</a></h3><p>'+summary+'</p></div>')
  body='<article class="article"><h1>'+title+'</h1><p class="muted">'+html.escape(m.get('date',m.get('status','')))+'</p>'+''.join('<p>'+html.escape(x)+'</p>' for x in b.split('\n\n'))+'</article>'
  save(kind+'/'+f.stem+'.html',title,body)
 return '<div class="grid">'+''.join(cards)+'</div>'
games=listing('games');posts=listing('posts')
save('index.html','Home','<section class="hero"><img src="/assets/logo.png" alt="Potion Cannon Studios"><h1>Independent games. Creative experiments.</h1><p>Explore our games and follow our development journey.</p></section><section class="section"><h2>Games</h2>'+games+'</section><section class="section"><h2>Latest development updates</h2>'+posts+'</section>')
save('games.html','Games','<section class="section"><h1>Games</h1>'+games+'</section>')
save('blog.html','Development blog','<section class="section"><h1>Development blog</h1>'+posts+'</section>')
save('about.html','About','<article class="article"><h1>About Potion Cannon Studios</h1><p>Replace this text with your studio story.</p></article>')
save('contact.html','Contact','<article class="article"><h1>Contact</h1><p>Add your public business email or social links here.</p></article>')
print('Site built')
