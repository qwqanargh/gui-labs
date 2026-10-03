"""Генерация картинок для ЛР1 (запускается один раз; готовые PNG лежат в assets/)."""
from PIL import Image, ImageDraw, ImageFilter
import math

S = 4  # суперсэмплинг для сглаживания

# 1) Картинка, которая заменяет надпись: простой пейзаж с солнцем
W, H = 220, 130
img = Image.new("RGBA", (W*S, H*S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, W*S-1, H*S-1], radius=18*S, fill=(135, 196, 235, 255))
d.ellipse([150*S, 14*S, 196*S, 60*S], fill=(255, 205, 60, 255))
d.polygon([(0, 105*S), (60*S, 45*S), (115*S, 105*S)], fill=(90, 120, 150, 255))
d.polygon([(70*S, 105*S), (140*S, 35*S), (210*S, 105*S)], fill=(70, 100, 130, 255))
d.polygon([(118*S, 63*S), (140*S, 35*S), (162*S, 63*S)], fill=(245, 245, 250, 255))
d.rounded_rectangle([0, 100*S, W*S-1, H*S-1], radius=18*S, fill=(95, 170, 90, 255))
d.rectangle([0, 100*S, W*S-1, 112*S], fill=(95, 170, 90, 255))
img.resize((W, H), Image.LANCZOS).save("assets/picture.png")

# 2) Полупрозрачный PNG, задающий форму окна: «капля»-шестерёнка с мягким краем
N = 460
cx = cy = N * S / 2
mask = Image.new("L", (N*S, N*S), 0)
md = ImageDraw.Draw(mask)
pts = []
for i in range(720):
    a = 2*math.pi*i/720
    r = (N*S/2 - 14*S) * (0.93 + 0.07*math.cos(8*a))   # волнистый край
    pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
md.polygon(pts, fill=255)
mask = mask.resize((N, N), Image.LANCZOS)

# заливка: радиальный градиент, альфа 150..235 => окно полупрозрачное
fill = Image.new("RGBA", (N, N))
px = fill.load()
for y in range(N):
    for x in range(N):
        t = min(1.0, math.hypot(x - N/2, y - N/2) / (N/2))
        r = int(70 + 60*t); g = int(40 + 30*t); b = int(160 + 60*t)
        a = int(235 - 85*t)
        px[x, y] = (r, g, b, a)
alpha = Image.eval(mask, lambda v: v)
out = Image.new("RGBA", (N, N), (0, 0, 0, 0))
fill.putalpha(Image.composite(fill.getchannel("A"), Image.new("L", (N, N), 0), alpha))
out = Image.alpha_composite(out, fill)
# светлый контур
edge = mask.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.GaussianBlur(1))
rim = Image.new("RGBA", (N, N), (230, 220, 255, 0)); rim.putalpha(edge)
out = Image.alpha_composite(out, rim)
out.save("assets/shape.png")
print("ok")
