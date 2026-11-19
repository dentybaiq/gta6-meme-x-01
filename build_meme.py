#!/usr/bin/env python3
"""Build the GTA 6 meme: Vice City sunset + make.fun ghost + bold captions."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ENTRY = "/home/hatch/workspace/makefun/entries/gta6-meme-x-01"
SCENE = f"{ENTRY}/assets/media-generation-vice-city-sunset-scene-0-8e359f2b-1d3c-4dd7-bce5-9e406fcd33f1.png"
GHOST = f"{ENTRY}/assets/mark-1024.png"
OUT = f"{ENTRY}/meme.png"

S = 1080  # square output
BLACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"

def font(sz):
    return ImageFont.truetype(BLACK, sz)

def draw_centered_text(draw, cx, y, lines, fnt, fill, stroke_w, stroke_fill):
    """Draw lines centered at cx, starting at y; returns bottom y."""
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt, stroke_width=stroke_w)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text((cx - w / 2, y), line, font=fnt, fill=fill,
                  stroke_width=stroke_w, stroke_fill=stroke_fill)
        y += h + 6
    return y

# --- background: center-crop scene to square, resize to 1080 ---
scene = Image.open(SCENE).convert("RGB")
w, h = scene.size
side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
bg = scene.crop((left, top, left + side, top + side)).resize((S, S), Image.LANCZOS)

# slight darken for text contrast
from PIL import ImageEnhance
bg = ImageEnhance.Brightness(bg).enhance(0.94)

# subtle top and bottom dark gradients for caption legibility
overlay = Image.new("L", (S, S), 0)
od = ImageDraw.Draw(overlay)
for y in range(0, 260):
    a = int(110 * (1 - y / 260))
    od.line([(0, y), (S, y)], fill=a)
for y in range(S - 300, S):
    a = int(120 * ((y - (S - 300)) / 300))
    od.line([(0, y), (S, y)], fill=a)
black = Image.new("RGB", (S, S), (10, 5, 20))
bg = Image.composite(black, bg, overlay)

# --- ghost: drop shadow + paste, centered, standing on the road ---
ghost = Image.open(GHOST).convert("RGBA")
GH = 430
gw = int(ghost.width * GH / ghost.height)
ghost = ghost.resize((gw, GH), Image.LANCZOS)
gx = (S - gw) // 2
gy = 300  # top of ghost
# shadow: black silhouette, blurred, offset down
alpha = ghost.split()[3]
shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sh = Image.new("RGBA", (gw, GH), (0, 0, 0, 0))
sh.putalpha(alpha.point(lambda p: int(p * 0.55)))
shadow.paste(sh, (gx + 10, gy + 16), sh)
shadow = shadow.filter(ImageFilter.GaussianBlur(10))
bg = Image.alpha_composite(bg.convert("RGBA"), shadow)
bg.paste(ghost, (gx, gy), ghost)

# --- captions ---
draw = ImageDraw.Draw(bg)
# top caption
top_font = font(104)
draw_centered_text(draw, S // 2, 34, ["WAITED 13 YEARS", "FOR GTA 6"],
                   top_font, (255, 255, 255), 8, (0, 0, 0))
# bottom caption
bot_font = font(76)
draw_centered_text(draw, S // 2, 812, ["MY AI AGENT GOT PAID", "THE WHOLE TIME"],
                   bot_font, (255, 255, 255), 7, (0, 0, 0))

# make.fun pill badge at very bottom (text centered with anchor="mm")
pill_font = font(44)
label = "make.fun"
bbox = draw.textbbox((0, 0), label, font=pill_font)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
pad_x, pad_y = 34, 20
pill_w, pill_h = tw + pad_x * 2, th + pad_y * 2
pill = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
pd = ImageDraw.Draw(pill)
pd.rounded_rectangle([0, 0, pill_w - 1, pill_h - 1], radius=pill_h // 2,
                     fill=(214, 38, 140, 255))  # magenta
pd.text((pill_w // 2, pill_h // 2), label, font=pill_font,
        fill=(255, 255, 255), anchor="mm")
px = (S - pill_w) // 2
py = S - pill_h - 18
bg.paste(pill, (px, py), pill)

bg.convert("RGB").save(OUT, "PNG")
print("saved", OUT)
im = Image.open(OUT)
print("size:", im.size)
