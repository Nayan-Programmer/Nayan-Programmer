#!/usr/bin/env python3
"""Create a clearly labeled first-run placeholder for the 3D contribution workflow."""
from pathlib import Path
import random
from build_profile import R,box,circle,eyebrow,ln
ROOT=Path(__file__).resolve().parent
R.start('night');random.seed(13)
W,H=1240,310
p=[]
p.append('<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="310" viewBox="0 0 1240 310" role="img" aria-label="Placeholder skyline until the real GitHub contribution city is generated">')
p.append('<defs><linearGradient id="night-sky" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#0d0e16"/><stop offset=".6" stop-color="#1a1930"/><stop offset="1" stop-color="#1b3444"/></linearGradient><linearGradient id="night-outline" x1="0" x2="1"><stop stop-color="#22d3ee"/><stop offset=".5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6"/></linearGradient></defs>')
p.append('<rect x="0" y="0" width="1240" height="310" rx="28" fill="url(#night-sky)"/><rect x="8" y="8" width="1224" height="294" rx="25" fill="none" stroke="url(#night-outline)" stroke-opacity=".6"/>')
for i in range(110):
 x=random.randrange(18,1220);y=random.randrange(20,220)
 p.append(f'<circle cx="{x}" cy="{y}" r="{random.choice([.65,.8,1.15])}" fill="{random.choice(["#a78bfa","#22d3ee","#e6e5ff"])}" fill-opacity=".45"/>')
for i in range(37):
 x=14+i*33; h=random.randint(20,90);w=26
 p.append(f'<rect x="{x}" y="{306-h}" width="{w}" height="{h}" fill="{random.choice(["#18283c","#182236","#20243e","#202944"])}" opacity=".86"/>')
 for j in range(2):
  for k in range(2,h//12):
   p.append(f'<rect x="{x+5+j*11}" y="{308-h+k*10}" width="3.5" height="3.5" fill="{random.choice(["#22d3ee","#a78bfa","#f472b6"])}" opacity=".43"/>')
p.append('<rect x="85" y="80" width="1070" height="126" rx="22" fill="#14182a" fill-opacity=".88" stroke="#55516d" stroke-opacity=".5"/>')
p.append(R.draw('THE CONTRIBUTION VILLAGE',620,130,29,'display','#ebe9ff',anchor='middle'))
p.append(R.draw('NIGHT CITY / FIRST AUTOMATED BUILD PENDING',620,165,15,'mono','#80e5ef',anchor='middle'))
p.append(R.draw('Run the Profile 3D workflow once to replace this preview.',620,190,13,'body','#b2b4d5',anchor='middle'))
p.append('<defs>'+R.definitions()+'</defs></svg>')
(ROOT/'profile-3d-contrib/profile-night-view.svg').write_text(''.join(p),'utf8')
print('Created city placeholder')
