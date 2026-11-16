"""Draw deterministic, original monochrome storyboard art for daily panels.
No letters are baked into these images: Chinese dialogue remains readable HTML.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import random, math

W,H=1200,620

def draw_panel(output:Path, chapter:int, panel:int, dialogue:str, title:str):
    rng=random.Random(chapter*104729+panel*769)
    is_rain=(chapter%5 in (1,2))
    canvas=Image.new("RGB",(W,H),(215,217,215))
    d=ImageDraw.Draw(canvas)
    # Mountains, ridgelines, and mist.
    for layer in range(4):
        base=95+layer*95
        ridge=[(-10,H)]
        for x in range(-30,W+70,65):
            y=int(base+rng.randint(-55,60)+(x/W)*20)
            ridge.append((x,y))
        ridge.append((W+10,H))
        g=(162-layer*24,)*3
        d.polygon(ridge,fill=g)
        d.line(ridge[1:-1],fill=(50+layer*10,)*3,width=4)
    # Side frame of traditional inn, tiled roof and doors.
    loc=(chapter+panel)%5
    if loc in (0,1,4):
        d.rectangle((735,95,1195,595),fill=(78,80,83),outline=(10,11,12),width=12)
        for x in range(785,1200,90):
            d.line((x,150,x,590),fill=(15,16,18),width=14)
        for y in range(170,600,95):
            d.line((740,y,1190,y),fill=(25,26,27),width=10)
        d.polygon([(675,170),(1015,25),(1255,140),(1255,176),(675,205)],fill=(34,35,38),outline=(6,7,8))
        for x in range(705,1210,27):
            d.line((x,179,x+30,160),fill=(118,119,119),width=2)
        d.ellipse((980,180,1035,260),fill=(245,244,221),outline=(25,25,26),width=7)
        d.line((1007,159,1007,184),fill=(12,12,12),width=3)
    elif loc==2:
        for x in range(80,W,120):
            d.line((x,0,x-20,620),fill=(34,37,39),width=rng.randint(9,18))
            for k in range(6):
                y=rng.randint(40,550)
                d.line((x,y,x-45,y-60),fill=(29,34,36),width=3)
                d.line((x,y,x+45,y-55),fill=(29,34,36),width=3)
    else:
        d.polygon([(600,520),(720,355),(880,300),(1100,475),(1250,620)],fill=(72,75,77),outline=(25,29,30))
        d.line((0,470,1200,540),fill=(245,247,246),width=19)
        for i in range(20):
            x=rng.randrange(W);y=rng.randrange(450,620)
            d.arc((x-80,y-25,x+90,y+40),0,180,fill=(208,212,211),width=2)
    # Ink hatching (subtle, deliberately not text).
    for i in range(450):
        x=rng.randrange(W);y=rng.randrange(H); length=rng.randrange(4,30)
        ink=rng.choice([(32,34,37),(71,75,78),(112,117,118)])
        d.line((x,y,x-length,y+length),fill=ink,width=1)
    # Foreground main swordsman with inked robe and ponytail.
    left=210+rng.randint(-45,45)
    head_y=220+rng.randint(-25,25)
    # Cloak outline / cape
    d.polygon([(left-185,620),(left-112,355),(left-85,275),(left+58,330),
               (left+165,620)],fill=(48,51,56),outline=(7,8,10),width=10)
    # Robe folds
    for q in range(15):
        xa=left-130+rng.randint(0,260)
        d.line((xa,385,xa+rng.randint(-40,80),630),fill=(129,135,137),width=rng.randint(1,5))
    # Neck and face
    d.ellipse((left-66,head_y-113,left+68,head_y+60),fill=(196,198,195),outline=(10,12,13),width=9)
    d.polygon([(left-75,head_y-60),(left-52,head_y-155),(left+34,head_y-159),
               (left+79,head_y-68),(left+51,head_y-95),(left-20,head_y-83)],
              fill=(18,21,22),outline=(10,11,12),width=5)
    # ponytail
    d.line((left+30,head_y-127,left+135,head_y-168,left+186,head_y-112),
           fill=(19,21,24),width=23,joint="curve")
    d.arc((left-56,head_y-37,left-7,head_y-20),184,352,fill=(9,10,11),width=6)
    d.arc((left+11,head_y-35,left+50,head_y-25),185,345,fill=(9,10,11),width=6)
    d.line((left-2,head_y+20,left+17,head_y+26),fill=(36,36,36),width=3)
    # Sword scabbard and hilt, changing angle with pose.
    d.line((left-167,563,left+155,155),fill=(9,11,12),width=28)
    d.line((left-170,559,left+155,155),fill=(180,180,176),width=10)
    d.line((left+105,226,left+197,302),fill=(25,28,31),width=14)
    d.ellipse((left+132,123,left+170,160),fill=(222,222,214),outline=(12,13,13),width=8)
    # Secondary figure (the innkeeper or the watcher).
    if panel%3!=1:
        x=790+rng.randint(-60,55); hy=235+rng.randint(-20,20)
        d.polygon([(x-125,620),(x-68,hy+80),(x+90,hy+75),(x+158,620)],
                  fill=(73,76,77),outline=(9,10,11),width=9)
        d.ellipse((x-62,hy-70,x+76,hy+85),fill=(190,194,190),outline=(15,16,17),width=7)
        d.arc((x-68,hy-85,x+82,hy-6),175,360,fill=(17,17,17),width=20)
        d.line((x-38,hy-2,x-6,hy-7),fill=(17,18,18),width=5)
        d.line((x+19,hy-8,x+52,hy-5),fill=(17,18,18),width=5)
        d.arc((x-30,hy+32,x+49,hy+102),0,160,fill=(56,55,55),width=6)
        d.line((x-22,hy+75,x+10,hy+121),fill=(64,64,64),width=5)
    # Distinct plot prop close-ups in alternating frames.
    if panel%3==2:
        px=565;py=385
        d.ellipse((px-66,py-73,px+69,py+76),fill=(233,236,232),outline=(20,21,22),width=13)
        d.arc((px-35,py-43,px+36,py+46),0,220,fill=(105,110,109),width=8)
        d.line((px,py-68,px+7,py-104),fill=(22,24,25),width=12)
    # Falling rain/storm or drifting snow/light.
    if is_rain:
        for _ in range(115):
            x=rng.randrange(W);y=rng.randrange(H);ll=rng.randrange(13,50)
            d.line((x,y,x-ll//3,y+ll),fill=(220,222,219),width=rng.choice((1,1,2)))
    # Strong manga panel border
    d.rectangle((3,3,W-4,H-4),outline=(8,9,11),width=8)
    output.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(output,"JPEG",quality=87,optimize=True)
