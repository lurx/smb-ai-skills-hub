# -*- coding: utf-8 -*-
# Post-process an ASS from captions_hz.py: caption lines whose words are ALL Latin
# (e.g. an English outro like "Welcome to the NEXT LEVEL") are laid out RTL by the
# generator and read reversed. This recomputes their \pos values to LTR visual order.
# Mixed Hebrew+Latin lines are left alone (RLI handles single embedded Latin words).
# usage: python fix_ltr_lines.py FILE.ass FS [SPACEMULT]
import re, sys, os
from PIL import ImageFont
SK=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path=sys.argv[1]; FS=int(sys.argv[2]); SPM=float(sys.argv[3]) if len(sys.argv)>3 else 1.0
CX=540; MAXW=1000
font=ImageFont.truetype(os.path.join(SK,"fonts","Arial Bold.ttf"),FS); SP=font.getlength(" ")*SPM
RLI="⁧"; PDI="⁩"
lines=open(path,encoding="utf-8").read().splitlines()
ev=re.compile(r'^(Dialogue: ([01]),([\d:.]+),([\d:.]+),Cap,,0,0,0,,\{\\an5\\pos\()([\d.]+)(,\d+\)[^}]*\})(.*)$')
def sec(t):
    h,m,s=t.split(":"); return int(h)*3600+int(m)*60+float(s)
# collect words + line window per start-time from layer 0 (base words span the full line)
groups={}
for i,l in enumerate(lines):
    m=ev.match(l)
    if m and m.group(2)=="0":
        word=m.group(7).replace(RLI,"").replace(PDI,"")
        g=groups.setdefault(m.group(3),{"end":sec(m.group(4)),"words":[]})
        g["words"].append(word)
def latin(w): return bool(re.fullmatch(r"[A-Za-z0-9'!?.,:-]+",w))
patched=0
for st,g in groups.items():
    words=g["words"]
    if len(words)<2 or not all(latin(w) for w in words): continue
    wd=[font.getlength(w) for w in words]; total=sum(wd)+SP*(len(wd)-1)
    f=min(1.0,MAXW/total); wd=[x*f for x in wd]; sp=SP*f; total*=f
    xl=CX-total/2; run=xl; cx={}
    for w,x in zip(words,wd): cx[w]=run+x/2; run+=x+sp
    s0=sec(st)
    for i,l in enumerate(lines):
        m=ev.match(l)
        if not m: continue
        # patch BOTH layers: any event starting inside the line's window (highlight
        # events of non-first words start mid-line, not at the line start)
        if not (s0<=sec(m.group(3))<g["end"]): continue
        word=m.group(7).replace(RLI,"").replace(PDI,"")
        if word in cx:
            lines[i]=m.group(1)+f"{cx[word]:.1f}"+m.group(6)+m.group(7); patched+=1
open(path,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print(f"LTR-fixed {patched} events in {path}")
