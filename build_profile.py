#!/usr/bin/env python3
"""Regenerate the self-contained, animated SVG profile cards.

Requires Pillow, fontTools and locally installed Inter, Go Mono, Simple Icons fonts.
No font files are packaged: text and brand marks are converted to vector outlines.
Edit profile_config.json, then run: python build_profile.py
"""
from __future__ import annotations
import base64, io, json, math, random, html, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parent
CFG=json.loads((ROOT/'profile_config.json').read_text('utf-8'))

FONT_CANDIDATES={
 'display':['/usr/share/fonts/opentype/inter/Inter-Bold.otf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'],
 'body':['/usr/share/fonts/opentype/inter/Inter-Regular.otf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'],
 'mono':['/usr/share/fonts/fonts-go/Go-Mono.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'],
 'si':['/usr/share/texlive/texmf-dist/fonts/opentype/public/simpleicons/SimpleIcons.otf'],
}
class Outliner:
 def __init__(self):
  self.fonts={}
  for family, candidates in FONT_CANDIDATES.items():
   item=next((x for x in candidates if Path(x).exists()),None)
   if not item: raise RuntimeError(f'{family} font is missing. Set FONT_CANDIDATES in build_profile.py to your local font path.')
   f=TTFont(item)
   self.fonts[family]=(f,f.getBestCmap(),f.getGlyphSet(),f['head'].unitsPerEm)
  self.si_names={n.replace('icon',''):cp for cp,n in self.fonts['si'][1].items()}
  self.used={}
  self.prefix='x'
 def start(self,prefix):
  self.prefix=prefix; self.used={}
 def path_id(self,family,cp): return f'{self.prefix}-g-{family}-{cp:x}'
 def draw(self,s,x,y,size=16,font='body',fill='#fff',spacing=0,anchor='start',opacity=None,klass=None,rotate=None):
  s=str(s)
  f,cmap,glyphset,upm=self.fonts[font]
  adv=[]; units=0
  for c in s:
   cp=ord(c)
   nm=cmap.get(cp,cmap.get(ord('?')))
   if not nm: continue
   w=f['hmtx'][nm][0]
   adv.append((cp,nm,units))
   units+=w+spacing*upm/size
  units-=spacing*upm/size if adv else 0
  factor=size/upm
  if anchor=='middle': x-=units*factor/2
  if anchor=='end': x-=units*factor
  props=''
  if opacity is not None: props+=f' opacity="{opacity}"'
  if klass: props+=f' class="{klass}"'
  if rotate is not None: props+=f' transform="rotate({rotate} {x:.2f} {y:.2f})"'
  contents=[]
  for cp,nm,pos in adv:
   self.used[(font,cp)]=nm
   contents.append(f'<use href="#{self.path_id(font,cp)}" x="{pos:.2f}"/>')
  return f'<g{props} fill="{fill}" aria-label="{html.escape(s,quote=True)}"><g transform="translate({x:.2f} {y:.2f}) scale({factor:.6f} {-factor:.6f})">'+''.join(contents)+'</g></g>'
 def icon(self,name,x,y,size=21,color='#fff'):
  cp=self.si_names.get(name)
  if cp is None: return self.draw('✦',x,y,size,font='body',fill=color,anchor='middle')
  return self.draw(chr(cp),x,y,size,font='si',fill=color,anchor='middle')
 def definitions(self):
  out=[]
  for (family,cp),nm in sorted(self.used.items()):
   f,cmap,glyphset,upm=self.fonts[family]
   pen=SVGPathPen(glyphset)
   glyphset[nm].draw(pen)
   d=pen.getCommands()
   if not d: continue
   out.append(f'<path id="{self.path_id(family,cp)}" d="{d}"/>')
  return '\n'.join(out)
R=Outliner()

def img64(path):
 p=Path(path)
 return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()

def jpg64(im,q=75):
 b=io.BytesIO(); im.convert('RGB').save(b,format='JPEG',quality=q,optimize=True)
 return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()

def box(x,y,w,h,fill='#171927',stroke='#303146',r=20,sw=1,other=''):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {other}/>'
def ln(x1,y1,x2,y2,color='#474a63',width=1,other=''):
 return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {other}/>'
def circle(x,y,r,fill,other=''):
 return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" {other}/>'
def gradient_title(s,x,y,size=58,anchor='start'):
 return R.draw(s,x,y,size,font='display',fill=f'url(#{R.prefix}-aurora)',anchor=anchor)
def eyebrow(s,x,y,color='#8c91ae'):
 return R.draw(s,x,y,12,font='mono',fill=color,spacing=.6)
def bodytext(s,x,y,size=16,fill='#c5c7db',font='body'):
 return R.draw(s,x,y,size,font=font,fill=fill)
def base(title,height=500):
 p=R.prefix; W=1240
 defs=f'''<linearGradient id="{p}-hairline" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#22d3ee" stop-opacity=".50"/><stop offset=".42" stop-color="#a78bfa" stop-opacity=".20"/><stop offset=".78" stop-color="#f472b6" stop-opacity=".44"/><stop offset="1" stop-color="#22d3ee" stop-opacity=".22"/></linearGradient>
 <linearGradient id="{p}-aurora" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#22d3ee"/><stop offset=".45" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/></linearGradient>
 <linearGradient id="{p}-violet" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#22d3ee" stop-opacity=".17"/><stop offset="1" stop-color="#a78bfa" stop-opacity=".04"/></linearGradient>
 <radialGradient id="{p}-glow"><stop stop-color="#a78bfa" stop-opacity=".15"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>
 <radialGradient id="{p}-cyan-glow"><stop stop-color="#22d3ee" stop-opacity=".19"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></radialGradient>
 <pattern id="{p}-dots" width="23" height="23" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".85" fill="#c5d1f1" fill-opacity=".14"/></pattern>
 <clipPath id="{p}-rounded"><rect x="13" y="13" width="1214" height="{height-26}" rx="30"/></clipPath>
 <filter id="{p}-soft"><feGaussianBlur stdDeviation="12"/></filter>
 '''
 background=f'''<rect width="1240" height="{height}" fill="#0d0e16"/><rect x="13" y="13" width="1214" height="{height-26}" rx="30" fill="#131521" stroke="url(#{p}-hairline)" stroke-width="1.5"/>
 <g clip-path="url(#{p}-rounded)"><ellipse cx="1160" cy="42" rx="340" ry="220" fill="url(#{p}-glow)"/><ellipse cx="70" cy="{height+32}" rx="370" ry="190" fill="url(#{p}-cyan-glow)"/><rect x="13" y="13" width="1214" height="{height-26}" fill="url(#{p}-dots)"/></g>
 '''
 css=f'''<style><![CDATA[
@keyframes {p}-breath{{0%,100%{{opacity:.34}}50%{{opacity:.88}}}}
@keyframes {p}-slidein{{from{{transform:translateY(14px);opacity:0}}to{{transform:translateY(0);opacity:1}}}}
@keyframes {p}-draw{{from{{stroke-dashoffset:90}}to{{stroke-dashoffset:0}}}}
@keyframes {p}-float{{0%,100%{{transform:translateY(0px)}}50%{{transform:translateY(-6px)}}}}
@keyframes {p}-blink{{0%,49%{{opacity:1}}50%,100%{{opacity:.12}}}}
@keyframes {p}-flash{{0%,100%{{opacity:.08}}50%{{opacity:.55}}}}
.{p}-enter{{animation:{p}-slidein 1s ease-out both}}
.{p}-pulse{{animation:{p}-breath 2.1s ease-in-out infinite}}
.{p}-blink{{animation:{p}-blink 1.3s step-end infinite}}
.{p}-float{{animation:{p}-float 5s ease-in-out infinite}}
.{p}-dash{{stroke-dasharray:90;stroke-dashoffset:0;animation:{p}-draw 1.2s ease-out both}}
]]></style>'''
 return defs,background,css

def write_svg(name,height,content,extra_defs='',description='Animated developer profile graphic'):
 p=R.prefix
 common,bg,css=base(name,height)
 glyphs=R.definitions()
 out=f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1240" height="{height}" viewBox="0 0 1240 {height}" role="img" aria-labelledby="{p}-title {p}-desc">
<title id="{p}-title">{html.escape(name)}</title><desc id="{p}-desc">{html.escape(description)}</desc>
<defs>{common}{extra_defs}{glyphs}</defs>{css}{bg}{content}</svg>'''
 from lxml import etree
 etree.fromstring(out.encode('utf-8'))
 target=ROOT/name
 target.write_text(out,'utf-8')
 print(name,round(target.stat().st_size/1024), 'KiB')

def camera_frames():
 """Placeholder animation from the uploaded still (NOT an extracted video)."""
 src=Image.open(ROOT/'source/hacker_character.png').convert('RGBA')
 src=src.crop((250,0,1115,990))
 frames=[]
 for i in range(12):
  W,H=440,355
  canvas=Image.new('RGB',(W,H),(12,17,32))
  back=Image.new('RGBA',(W,H))
  d=ImageDraw.Draw(back)
  for yy in range(H):
   t=yy/H
   d.line((0,yy,W,yy),fill=(int(17+13*t),int(20+5*t),int(44+14*t),255))
  d.ellipse((150,-150,480,200),fill=(47,61,113,50))
  back=back.filter(ImageFilter.GaussianBlur(20))
  orig=src.copy(); scale=.67
  orig=orig.resize((int(src.width*scale),int(src.height*scale)),Image.Resampling.LANCZOS)
  a=i*math.pi/6
  orig=orig.rotate(1.4*math.sin(a),resample=Image.Resampling.BICUBIC,expand=False)
  x=int(-95+5*math.sin(a)); y=int(-6-4*math.cos(a))
  back.alpha_composite(orig,(x,y))
  canvas=Image.alpha_composite(canvas.convert('RGBA'),back).convert('RGB')
  frames.append(jpg64(canvas,q=73))
 return frames

def frame_markup(frames,x=792,y=111,w=397,h=323):
 n=len(frames); seq=[]
 for i,frame in enumerate(frames):
  start=i*2.0/n/4
  end=(i+1)*2.0/n/4 if i<n-1 else 1
  if i==0: keytimes=f'0;{end:.6f};1'; values='1;0;0'
  elif i==n-1: keytimes=f'0;{start:.6f};1'; values='0;1;1'
  else: keytimes=f'0;{start:.6f};{end:.6f};1';values='0;1;0;0'
  seq.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" href="{frame}" opacity="{1 if i==n-1 else 0}"><animate attributeName="opacity" begin="0s" dur="4s" repeatCount="indefinite" calcMode="discrete" keyTimes="{keytimes}" values="{values}"/></image>')
 return '\n'.join(seq)

def hero():
 R.start('hero'); p=R.prefix
 frames=camera_frames()
 extra=f'''<clipPath id="hero-camera-clip"><rect x="790" y="111" width="398" height="323" rx="17"/></clipPath>
 <radialGradient id="hero-feather"><stop offset=".57" stop-color="white"/><stop offset=".84" stop-color="white" stop-opacity=".89"/><stop offset="1" stop-color="white" stop-opacity="0"/></radialGradient>
 <mask id="hero-video-feather" maskUnits="userSpaceOnUse" x="790" y="111" width="398" height="323"><rect x="790" y="111" width="398" height="323" fill="url(#hero-feather)"/></mask>
 <linearGradient id="hero-scrub" x1="0" x2="1"><stop stop-color="#22d3ee"/><stop offset=".55" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/></linearGradient>
 <clipPath id="hero-name-clip"><rect x="67" y="221" width="690" height="83"><animate attributeName="y" values="305;221;221" keyTimes="0;.40;1" begin="0s" dur="3s" fill="freeze"/></rect></clipPath>
 <clipPath id="hero-type-clip"><rect x="66" y="142" width="258" height="43"><animate attributeName="width" values="0;0;258;258" keyTimes="0;.13;.50;1" begin="0s" dur="2s" fill="freeze"/></rect></clipPath>
 '''
 a=[]
 a+=[eyebrow('DEVELOPER / CREATOR / HUMAN',68,77),R.draw('EST. 20XX',690,76,11,'mono','#8b91ae',anchor='end')]
 a += [box(69,99,177,34,'#12312f','#2b787d',17),circle(88,116,5,'#37e0b8',f'class="{p}-pulse"'),R.draw('OPEN TO COLLABS',104,120,12,'mono','#a7fce6')]
 a += [f'<g clip-path="url(#hero-type-clip)">{R.draw("HI THERE, I'M",69,177,26,"mono","#d3d4e9")}</g>']
 a += [f'<g clip-path="url(#hero-name-clip)">{gradient_title(CFG["name"].upper(),67,291,66)}</g>']
 roles=[CFG.get('role','CREATIVE DEVELOPER').upper(),'CODE + DESIGN ENTHUSIAST','OPEN-SOURCE EXPLORER']
 for i,role in enumerate(roles):
  vals=['1','0','0','0'] if i==0 else ['0','0','0','0']
  times='0;.333;.666;1'
  if i==0: vals='1;0;0;1'
  if i==1: vals='0;1;0;0'
  if i==2: vals='0;0;1;0'
  # static first line visible if animation is disabled
  a.append(f'<g opacity="{1 if i==0 else 0}">{R.draw(role,70,335,19,"display","#e6e4ff")}<animate attributeName="opacity" values="{vals}" keyTimes="{times}" dur="12s" repeatCount="indefinite" begin="0s" calcMode="discrete"/></g>')
 a += [bodytext(CFG.get('pitch','I make useful things with code and curiosity.'),69,377,16,'#b9bdd5'),ln(69,399,709,399,'#373c54')]
 # custom tiny icons
 a += [f'<g transform="translate(75 433)" stroke="#22d3ee" fill="none" stroke-width="1.5"><path d="M0 -9C-9 -9 -9 2 0 11C9 2 9 -9 0 -9Z"/><circle r="3"/></g>',R.draw(CFG['location'].upper(),95,437,12,'mono','#ccd1e8'),
       f'<g transform="translate(303 432)" stroke="#a78bfa" fill="none" stroke-width="1.5"><rect x="-9" y="-9" width="18" height="17" rx="2"/><path d="M-5 7V-4H4M-5 0H4"/></g>',R.draw(CFG['company'].upper(),324,437,12,'mono','#ccd1e8'),
       R.icon('github',563,438,20,'#f472b6'),R.draw(f'@{CFG["github"]}',580,438,12,'mono','#ccd1e8')]
 # camera viewfinder
 a += [box(777,96,425,354,'#101521','#46516c',21),box(789,108,401,326,'#111723','#2e4466',16)]
 a += [f'<g id="hero-video-sequence" clip-path="url(#hero-camera-clip)" mask="url(#hero-video-feather)"><g><animate attributeName="opacity" values="1;1;0" keyTimes="0;.85;1" begin="0s" dur="4s" repeatCount="indefinite"/><!-- VIDEO_FRAMES_START -->{frame_markup(frames)}<!-- VIDEO_FRAMES_END --></g></g>']
 a += [f'<rect x="798" y="116" width="383" height="312" rx="12" fill="none" stroke="#a5c5e0" opacity=".24"/>']
 # viewfinder corners draw
 for sx,sy,xx,yy in [(808,131,1,1),(1173,131,-1,1),(808,410,1,-1),(1173,410,-1,-1)]:
  d=f'M{sx+xx*24} {sy}H{sx}V{sy+yy*24}'
  a.append(f'<path d="{d}" stroke="#ccedff" stroke-width="2.8" fill="none" stroke-linecap="round" class="hero-dash"/>')
 a += [circle(829,139,5,'#f472b6','class="hero-blink"'),R.draw('REC',842,143,12,'mono','#fff'),R.draw('CAM_01 / STILL PREVIEW',803,112,10,'mono','#d9e6ff')]
 a += [R.draw('00:00',807,422,12,'mono','#d8dfef'),R.draw('00:04',1149,422,12,'mono','#d8dfef',anchor='end'),box(860,414,226,7,'#344057','none',4),
       '<rect x="860" y="414" width="0" height="7" rx="3.5" fill="url(#hero-scrub)"><animate attributeName="width" values="0;226;226;0" keyTimes="0;.50;.85;1" dur="4s" repeatCount="indefinite" begin="0s"/></rect>']
 a += [eyebrow('SELF-CONTAINED MOTION STUDY',981,473,'#83899f')]
 write_svg('hero.svg',500,''.join(a),extra,'Animated intro with a simulated still-image loop. Replace with provided footage via tools/embed_video.py.')

def about():
 R.start('about');p=R.prefix
 a=[]
 a += [box(33,32,566,454,'#151725','#33334e',25),box(616,32,591,454,'#151725','#33334e',25)]
 a += [eyebrow('01 / MORE THAN CODE',63,76,'#22d3ee'),R.draw('Curiosity is my engine.',62,114,28,'display','#f2efff')]
 a += [box(61,140,506,200,'#0b111e','#424a69',17),box(61,140,506,31,'#22263a','#454b68',15)]
 for i,c in enumerate(['#f472b6','#fbbf24','#22d3ee']): a += [circle(83+i*19,156,5,c)]
 a += [box(147,146,349,20,'#111627','#2d3550',10),R.draw('https://localhost/this-is-me',163,160,10,'mono','#8edff0')]
 a += [R.draw('const developer = {',89,206,17,'mono','#a78bfa'),R.draw('  mindset: "keep learning",',89,233,15,'mono','#c8c6ec'),R.draw('  superpower: "build & iterate",',89,261,15,'mono','#22d3ee'),R.draw('  status: "creating..."',89,289,15,'mono','#f9a8d4'),R.draw('}',89,314,17,'mono','#a78bfa')]
 a += [box(91,349,456,37,'#1b2032','#2a324c',11),box(91,395,456,37,'#1b2032','#2a324c',11),box(91,441,456,28,'#1b2032','#2a324c',11)]
 rows=[('BRUSH','Building clean experiences','#22d3ee'),('SPARK','Turning ideas into prototypes','#a78bfa'),('LOOP','Learning something every day','#f472b6')]
 for idx,(sym,t,c) in enumerate(rows):
  y=[368,413,458][idx]
  a += [box(101,y-14,28,26,'#202d41','#354663',6),R.draw(['01','02','03'][idx],115,y+5,12,'mono',c,anchor='middle'),R.draw(t,142,y+5,15,'body','#e7e8f6')]
 a += [eyebrow('02 / AWAY FROM THE SCREEN',647,76,'#f472b6'),R.draw('Life, on repeat.',646,114,29,'display','#f1edff')]
 a += [box(640,133,544,271,'#101625','#35415b',18)]
 # carousel segment bars
 for i in range(3):
  x=664+i*165
  a += [box(x,150,150,4,'#3b3c56','none',2)]
  # 12-sec timeline, one 4s bar filling at a time
  start=i/3; end=(i+1)/3
  keytimes=f'0;{start:.5f};{end:.5f};1'
  vals='0;0;150;150'
  a += [f'<rect x="{x}" y="150" width="150" height="4" rx="2" fill="{["#22d3ee","#a78bfa","#f472b6"][i]}" opacity=".96"><animate attributeName="width" values="{vals}" keyTimes="{keytimes}" begin="0s" dur="12s" repeatCount="indefinite"/></rect>']
 # slides with sliding motion and crossfade
 hobbies=CFG.get('hobbies',[])
 defaults=[('PHOTO MODE','Collecting light, colour and moments.'),('GAME NIGHT','Trying every challenge, one level at a time.'),('OFFLINE TIME','Finding space for new ideas to grow.')]
 icons=['camera','game','sun']
 for i in range(3):
  ttl=(str(hobbies[i]).upper() if i<len(hobbies) else defaults[i][0])
  cap=defaults[i][1]
  t0=i/3; t1=(i+1)/3
  # one visible at a time, immediate first-frame fallback
  opacity='1' if i==0 else '0'
  vals=['1;1;0;0;1','0;0;1;1;0;0','0;0;1;1;0'][i]
  slide_times=['0;.30;.36;.94;1','0;.30;.36;.63;.69;1','0;.63;.69;.94;1'][i]
  slide=f'<g opacity="{opacity}"><animate attributeName="opacity" values="{vals}" keyTimes="{slide_times}" dur="12s" repeatCount="indefinite" begin="0s" calcMode="linear"/>'
  slide+=f'<g><animateTransform attributeName="transform" type="translate" values="26 0;0 0;0 0" keyTimes="0;.08;1" dur="4s" begin="{i*4}s;{i*4+12}s" fill="freeze"/>'
  slide+=circle(913,240,73,'#1c2341',f'stroke="{["#22d3ee","#a78bfa","#f472b6"][i]}" stroke-opacity=".65" stroke-width="1.4"')
  if i==0:
   slide += '<rect x="873" y="212" width="80" height="55" rx="10" fill="none" stroke="#9be9f1" stroke-width="5"/><circle cx="913" cy="239" r="16" fill="none" stroke="#9be9f1" stroke-width="5"/><path d="M891 211l9 -12h28l9 12" stroke="#9be9f1" stroke-width="5" fill="none"/>'
  elif i==1:
   slide += '<path d="M865 252q-5 -46 30 -46h36q35 0 30 46l-15 17 -22 -20h-22l-22 20Z" fill="none" stroke="#bba5fc" stroke-width="5"/><path d="M886 226v23m-12 -12h24" stroke="#bba5fc" stroke-width="5"/><circle cx="936" cy="228" r="5" fill="#f472b6"/><circle cx="947" cy="241" r="5" fill="#22d3ee"/>'
  else:
   slide += '<circle cx="913" cy="236" r="28" fill="none" stroke="#f472b6" stroke-width="5"/>'+''.join(f'<path d="M{913+38*math.cos(j*math.pi/4):.1f} {236+38*math.sin(j*math.pi/4):.1f}L{913+51*math.cos(j*math.pi/4):.1f} {236+51*math.sin(j*math.pi/4):.1f}" stroke="#f9a8d4" stroke-width="4"/>' for j in range(8))
  slide+=R.draw(ttl,912,340,22,'display','#eae8ff',anchor='middle')
  slide+=R.draw(cap,911,368,12,'body','#b1b6d1',anchor='middle')+'</g></g>'
  a += [slide]
 a += [R.draw('DAILY RINGS',653,434,11,'mono','#9da3bd')]
 for j,(lab,val,col) in enumerate([('CREATE',.84,'#22d3ee'),('LEARN',.68,'#a78bfa'),('MOVE',.91,'#f472b6')]):
  xx=858+110*j; yy=438;circ=2*math.pi*22
  a += [circle(xx,yy,22,'none','stroke="#353950" stroke-width="6"'),f'<circle cx="{xx}" cy="{yy}" r="22" fill="none" stroke="{col}" stroke-width="6" stroke-linecap="round" stroke-dasharray="{circ:.2f}" stroke-dashoffset="{circ*(1-val):.2f}" transform="rotate(-90 {xx} {yy})"><animate attributeName="stroke-dashoffset" values="{circ:.2f};{circ*(1-val):.2f};{circ*(1-val):.2f}" keyTimes="0;.22;1" dur="12s" repeatCount="indefinite" begin="0s"/></circle>',R.draw(lab,xx,473,9,'mono','#abb1c9',anchor='middle')]
 write_svg('about-life.svg',500,''.join(a),description='Side-by-side about and lifestyle cards, with animated stories and activity rings.')

def ellipse_path(cx,cy,rx,ry,angle=-18,points=96):
 out=[];an=math.radians(angle)
 for i in range(points+1):
  th=2*math.pi*i/points
  X=rx*math.cos(th);Y=ry*math.sin(th)
  x=cx+X*math.cos(an)-Y*math.sin(an); y=cy+X*math.sin(an)+Y*math.cos(an)
  out.append(f'{"M" if i==0 else "L"}{x:.2f},{y:.2f}')
 return ''.join(out)+'Z'

def orbit_item(name, path, dur, color, size=26, begin='0s', orbitmoons=False):
 el=f'<g><circle r="29" fill="#171e34" stroke="{color}" stroke-opacity=".65" stroke-width="1.3"/>'+R.icon(name,0,9,size,color)
 if orbitmoons:
  for ii,(nm,cl) in enumerate([('typescript','#65bcff'),('figma','#fc8eb3')]):
   moonpath=ellipse_path(0,0,43,43,0,40)
   el+=f'<g><circle r="13" fill="#101627" stroke="{cl}" stroke-width="1"/>'+R.icon(nm,0,5,12,cl)+f'<animateMotion path="{moonpath}" dur="{3+ii}s" begin="0s" repeatCount="indefinite" rotate="0" keyPoints="0;1" keyTimes="0;1"/></g>'
 el+=f'<animateMotion path="{path}" dur="{dur}s" begin="{begin}" repeatCount="indefinite" rotate="0"/></g>'
 return el

def stack():
 R.start('stack'); p=R.prefix; a=[]
 a += [eyebrow('03 / THE TOOLBOX',65,77,'#22d3ee'),R.draw('Made of many disciplines.',64,119,31,'display','#f4f2ff')]
 # orbit left under stylized wire frames
 cx,cy=332,328
 paths=[ellipse_path(cx,cy,206,145,-12),ellipse_path(cx,cy,254,145,17),ellipse_path(cx,cy,292,138,-17)]
 colors=['#22d3ee','#a78bfa','#f472b6']
 for j,path in enumerate(paths):
  a += [f'<path d="{path}" stroke="{colors[j]}" stroke-width="1.5" stroke-opacity=".34" stroke-dasharray="6 8" fill="none"/>']
 a += [circle(cx,cy,105,f'url(#{p}-cyan-glow)'),circle(cx,cy,74,'#1c2040','stroke="#7080b8" stroke-opacity=".46" stroke-width="1.5"'),circle(cx,cy,56,'#12182b','stroke="#a78bfa" stroke-opacity=".55"'),R.draw('BUILD',cx,cy-3,19,'mono','#d7d4ff',anchor='middle'),R.draw('CREATE',cx,cy+23,12,'mono','#24dbf5',anchor='middle')]
 a += [f'<circle cx="{cx}" cy="{cy}" r="88" fill="none" stroke="#22d3ee" stroke-opacity=".16" stroke-dasharray="10 14"><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="19s" repeatCount="indefinite"/></circle>']
 a += [orbit_item('react',paths[0],'17',colors[0],27,orbitmoons=True),orbit_item('python',paths[1],'22',colors[1]),orbit_item('figma',paths[2],'27',colors[2]),orbit_item('javascript',paths[0],'17',colors[0],23,'-9s'),orbit_item('docker',paths[1],'22',colors[1],26,'-11s'),orbit_item('blender',paths[2],'27',colors[2],26,'-16s')]
 a += [eyebrow('TECH STACK / SAMPLE - EDIT CONFIG',722,76,'#f472b6'),R.draw('The bits I build with.',721,119,28,'display','#f1edff')]
 groups=[('FRONTEND',['React','TypeScript','JavaScript','CSS']),('MOTION + 3D',['Blender','Figma','Animation']),('DATA',['Python','Data Tools','Automation']),('AI',['OpenAI','TensorFlow','ML Experiments'])]
 icon_names={'React':'react','TypeScript':'typescript','JavaScript':'javascript','CSS':'css3','Blender':'blender','Figma':'figma','Python':'python','OpenAI':'openai','TensorFlow':'tensorflow'}
 cols=['#22d3ee','#a78bfa','#f472b6','#22d3ee']
 for gi,(name,items) in enumerate(groups):
  y=157+gi*91
  a += [eyebrow(name,725,y,cols[gi]),ln(728,y+11,1180,y+11,'#363950')]
  x=726
  for ii,item in enumerate(items):
   w=max(92,min(155,52+len(item)*7.4))
   c=cols[gi]
   delay=(gi*4+ii)*.55
   a += [f'<g><rect x="{x}" y="{y+22}" width="{w:.1f}" height="42" rx="13" fill="#1b2134" stroke="{c}" stroke-opacity=".38"><animate attributeName="stroke-opacity" values=".38;.95;.38" keyTimes="0;.5;1" dur="2.1s" repeatCount="indefinite" begin="{delay}s"/></rect>']
   if item in icon_names:
    a += [R.icon(icon_names[item],x+20,y+49,17,c),R.draw(item,x+36,y+51,12,'body','#e4e8f8')]
   else:a += [R.draw(item,x+13,y+51,12,'body','#e4e8f8')]
   a += ['</g>'];x+=w+9
 a += [eyebrow('TINY MOONS: TS + FIGMA',69,148,'#929bb7'),eyebrow('ORBIT SYSTEM : CSS + SMIL',1000,511,'#929bb7')]
 write_svg('stack.svg',540,''.join(a),description='Technology marks from Simple Icons vector outlines move on three elliptical orbits, with two orbiting moons.')

def odometer(value,x,y,size=27,color='#fff'):
 numbers=[round(value*i/8) for i in range(9)]
 result=''
 for i,n in enumerate(numbers):
  st=i/9; en=(i+1)/9 if i<8 else 1.0
  start=f'{st:.4f}';end=f'{en:.4f}'
  vals='1;0;0' if i==0 else ('0;1;1' if i==8 else '0;1;0;0')
  times=f'0;{end};1' if i==0 else (f'0;{start};1' if i==8 else f'0;{start};{end};1')
  result+=f'<g opacity="{1 if i==8 else 0}">'+R.draw(str(n),x,y,size,'display',color)+f'<animate attributeName="opacity" values="{vals}" keyTimes="{times}" dur="1.8s" begin="0s" fill="freeze" calcMode="discrete"/></g>'
 return result

def id_dashboard():
 R.start('id');p=R.prefix;a=[]
 a += [eyebrow('04 / CREATOR IDENTITY',65,67,'#22d3ee'),R.draw('ACCESS GRANTED',750,72,12,'mono','#80f5dc')]
 # badge anchor and lanyard strap
 badge=[]
 badge += [f'<path d="M205 -38L261 107L317 -38" stroke="#c0a3ff" stroke-width="15" fill="none" opacity=".57"/>',f'<path d="M215 -38L261 99L307 -38" stroke="#e7b9ff" stroke-width="5" fill="none" opacity=".75"/>']
 badge += [R.draw('CREATE',222,44,10,'mono','#fce7ff',rotate=-68),R.draw('BUILD',300,43,10,'mono','#fce7ff',rotate=68)]
 badge += [box(241,96,40,22,'#d7e0ed','#b7c1d9',6),circle(261,107,7,'#68738e'),box(250,119,22,19,'#9faabd','#d6dbe9',4)]
 badge += [box(103,133,315,343,'#141b2f','#5d6792',21,1.8),box(111,141,299,327,'#1a2033','#354563',16)]
 badge += [box(124,153,272,42,'#222941','#293c63',12),R.draw('CREATOR / ACCESS PASS',138,181,15,'mono','#d4eafa')]
 badge += [box(124,207,144,139,'#0f1328','#586b9c',12)]
 image=img64(ROOT/'source/badge_portrait.png')
 badge += [f'<defs><clipPath id="id-photo-clip"><rect x="129" y="212" width="134" height="130" rx="8"/></clipPath></defs><g clip-path="url(#id-photo-clip)"><rect x="129" y="212" width="134" height="130" fill="#242744"/><image href="{image}" x="106" y="182" width="185" height="210" preserveAspectRatio="xMidYMid meet"/></g>']
 badge += [f'<rect x="129" y="212" width="134" height="130" rx="8" stroke="#22d3ee" stroke-width="2" stroke-dasharray="34 470" fill="none"><animate attributeName="stroke-dashoffset" from="0" to="-505" dur="4s" repeatCount="indefinite"/></rect>']
 badge += [R.draw('NAME',281,231,10,'mono','#a5aac7'),R.draw(CFG['name'].upper(),281,256,16,'display','#f2efff'),R.draw('ROLE',281,280,10,'mono','#a5aac7'),R.draw(CFG['role'].upper()[:16],281,302,11,'mono','#74ddf0')]
 badge += [box(278,313,110,24,'#1d2b3a','#6d708b',5),R.draw('@'+CFG['github'][:13],287,329,9,'mono','#c5b7ff')]
 badge += [box(124,363,66,46,'#d9ae5a','#fce7aa',6),'<path d="M149 363v46m18 -46v46m-43 -29h66m-66 18h66" stroke="#aa8449" stroke-width="2" fill="none"/>',R.draw('ID. 0001 / BUILD',209,380,12,'mono','#dbe2fa')]
 badge += [R.draw('VERIFIED CREATOR',209,402,11,'mono','#69eec9')]
 random.seed(4);xx=129
 for j in range(41):
  bw=random.choice([1.3,2.1,3.3])
  badge += [f'<rect x="{xx:.2f}" y="424" width="{bw}" height="{random.choice([18,21,23,26])}" fill="#ced9ec"/>'];xx+=bw+random.choice([1.5,2.0,3.2])
 badge += [R.draw('NO. 0420-2026',271,458,8,'mono','#cbd1e5')]
 badge += [f'<rect x="111" y="141" width="90" height="325" fill="url(#id-foil)" opacity=".25" transform="skewX(-25)"><animate attributeName="x" values="-150;480" dur="4.4s" repeatCount="indefinite" begin="0s"/></rect>']
 a += [f'<g><g>'+''.join(badge)+f'<animateTransform attributeName="transform" type="translate" values="0 -510;0 12;0 -6;0 0" keyTimes="0;.42;.68;1" dur="1.4s" fill="freeze" begin="0s"/></g><animateTransform attributeName="transform" type="rotate" values="12 261 100;-8 261 100;5 261 100;-2 261 100;0 261 100" keyTimes="0;.20;.46;.71;1" dur="3.2s" fill="freeze" begin="0s"/></g>']
 # dashboard right side
 a += [R.draw('YOUR SIGNAL',518,113,26,'display','#f1eaff'),eyebrow('LIVE STATS / DEMO UNTIL CONFIGURED',519,136,'#969db6')]
 stats=[('REPOSITORIES','repos','#22d3ee'),('STARS EARNED','stars','#a78bfa'),('DAY STREAK','streak','#f472b6')]
 for j,(lab,key,col) in enumerate(stats):
  x=516+j*226;val=int(CFG['stats'][key]);a += [box(x,156,210,108,'#1a1f34','#384264',16),R.draw(lab,x+16,181,10,'mono','#a3aac8'),odometer(val,x+16,228,30,col),R.draw('↗',x+170,235,25,'body',col)]
 a += [box(515,284,482,198,'#141a2c','#343c56',18),R.draw('MOST-STARRED REPOS',535,315,13,'mono','#d8ddf5'),R.draw('ILLUSTRATIVE',940,313,9,'mono','#7b86a5',anchor='end')]
 repos=CFG['repos'][:4];mx=max([int(x['stars']) for x in repos]+[1])
 for i,item in enumerate(repos):
  y=344+i*34;name=item['name'][:20];v=int(item['stars']); wid=int(v/mx*230)
  a += [R.draw(name,535,y+5,12,'mono','#c8cede'),box(687,y-7,230,15,'#26304a','none',6)]
  a += [f'<rect x="687" y="{y-7}" width="{wid}" height="15" rx="6" fill="#22d3ee" opacity=".86"><animate attributeName="width" values="0;0;{wid}" keyTimes="0;.25;1" dur="1.9s" fill="freeze" begin="0s"/></rect>',R.draw(str(v),935,y+5,12,'mono','#7fe4f3')]
 a += [box(1010,284,179,198,'#171f32','#364361',18),eyebrow('NOW //',1026,314,'#f472b6')]
 for yy,lab,desc in [(345,'WORKING ON','MY NEXT BIG IDEA'),(401,'LISTENING TO','FOCUS PLAYLIST'),(457,'STATUS','OPEN TO IDEAS')]:
  a += [R.draw(lab,1027,yy,9,'mono','#8e9aba'),R.draw(desc,1027,yy+18,10,'display','#ecedfd')]
 a += [circle(1158,457,4,'#44dfb6','class="id-pulse"')]
 extra='<linearGradient id="id-foil"><stop stop-color="#ffffff" stop-opacity="0"/><stop offset=".5" stop-color="#f7a8fd" stop-opacity=".75"/><stop offset="1" stop-color="#22d3ee" stop-opacity="0"/></linearGradient>'
 write_svg('id-dashboard.svg',520,''.join(a),extra,'Swinging creator lanyard and ID card with placeholder demo repository statistics.')

def connect():
 R.start('connect');p=R.prefix;a=[]
 a += [eyebrow('05 / SEND A SIGNAL',65,69,'#22d3ee'),R.draw('Let us build something.',64,111,32,'display','#f4f0ff')]
 # pointing character cropped from artwork, portrait fully embedded PNG
 pointing=img64(ROOT/'source/pointing_small.png')
 a += [f'<ellipse cx="275" cy="409" rx="195" ry="55" fill="url(#{p}-cyan-glow)"/>',f'<image class="{p}-float" href="{pointing}" x="113" y="123" width="300" height="352" preserveAspectRatio="xMidYMid meet"/>']
 a += [R.draw('THE INTERNET IS BETTER',430,187,14,'mono','#bdc4e0'),R.draw('WHEN WE TALK.',430,212,14,'mono','#22d3ee')]
 cards=[('github','GITHUB','Browse projects',f'https://github.com/{CFG["github"]}','#e7e9fb'),('linkedin','LINKEDIN','Connect professionally',CFG['links'].get('linkedin','https://www.linkedin.com/'), '#a78bfa'),('gmail','EMAIL','Start a conversation',f'mailto:{CFG["email"]}','#22d3ee')]
 for i,(ic,ttl,sub,url,c) in enumerate(cards):
  x=668;y=146+i*104
  a += [f'<a href="{html.escape(url,quote=True)}" target="_blank">',box(x,y,504,88,'#1a2034','#343e5a',17),box(x+16,y+15,58,58,'#262943','#495477',14),R.icon(ic,x+45,y+55,30,c),R.draw(ttl,x+92,y+37,17,'display','#f1f2ff'),R.draw(sub,x+92,y+62,13,'body','#aaaecd')]
  a += [f'<g class="{p}-float">'+R.draw('>',x+463,y+55,26,'mono',c)+'</g></a>']
 a += [eyebrow('CLICK THE CARDS OR SCAN THE README LINKS',690,484,'#7f86a2')]
 write_svg('connect.svg',515,''.join(a),description='Pointing illustrated character and three linked contact cards.')

if __name__=='__main__':
 hero();about();stack();id_dashboard();connect()
 from generate_readme import main as generate_readme
 generate_readme()
 print('Done. Edit profile_config.json and run again to personalize.')
