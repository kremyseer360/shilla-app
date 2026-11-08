#!/usr/bin/env python3
"""يولّد أيقونة التطبيق (adaptive + قديمة + دائرية) وشاشة البداية بخلفية داكنة، ويكتبها داخل مشروع أندرويد.
آمن: لو شي مو موجود بالقالب بيتخطاه وما بيوقّف البناء."""
from pathlib import Path
from PIL import Image, ImageDraw
import re, sys

BG = (4, 8, 20, 255)           # #040814
BG_HEX = "#040814"
ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "android" / "app" / "src" / "main" / "res"
LOGO = Image.open(ROOT / "www" / "icons" / "icon-512.png").convert("RGBA")

def fit(img, size):
    return img.resize((size, size), Image.LANCZOS)

def on_bg(canvas, logo_ratio):
    c = Image.new("RGBA", (canvas, canvas), BG)
    s = int(canvas * logo_ratio)
    c.alpha_composite(fit(LOGO, s), ((canvas - s) // 2, (canvas - s) // 2))
    return c

def circle(img):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, img.size[0] - 1, img.size[1] - 1), fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0)); out.paste(img, (0, 0), m); return out

if not RES.exists():
    print("res غير موجود — تخطيت", RES); sys.exit(0)

legacy = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
n = 0
for d, px in legacy.items():
    folder = RES / f"mipmap-{d}"; folder.mkdir(parents=True, exist_ok=True)
    fit(LOGO, px).save(folder / "ic_launcher.png")
    circle(on_bg(px, 0.84)).save(folder / "ic_launcher_round.png")
    fg = Image.new("RGBA", (px * 9 // 4,) * 2, (0, 0, 0, 0))   # 108dp
    s = int(fg.size[0] * 0.66)
    fg.alpha_composite(fit(LOGO, s), ((fg.size[0] - s) // 2,) * 2)
    fg.save(folder / "ic_launcher_foreground.png")
    n += 3
vals = RES / "values"; vals.mkdir(parents=True, exist_ok=True)
(vals / "ic_launcher_background.xml").write_text(
    f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">{BG_HEX}</color>\n</resources>\n')
anydpi = RES / "mipmap-anydpi-v26"; anydpi.mkdir(parents=True, exist_ok=True)
for name in ("ic_launcher", "ic_launcher_round"):
    (anydpi / f"{name}.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/ic_launcher_background"/>\n'
        '    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n</adaptive-icon>\n')

splashes = 0
for f in RES.glob("drawable*/splash.png"):
    try:
        w, h = Image.open(f).size
    except Exception:
        w, h = 1080, 1920
    c = Image.new("RGBA", (w, h), BG)
    s = int(min(w, h) * 0.34)
    c.alpha_composite(fit(LOGO, s), ((w - s) // 2, (h - s) // 2))
    c.convert("RGB").save(f); splashes += 1

styles = RES / "values" / "styles.xml"
if styles.exists():
    t = styles.read_text(encoding="utf-8")
    if "Theme.SplashScreen" in t and "windowSplashScreenBackground" not in t:
        t = re.sub(r'(<style name="AppTheme\.NoActionBarLaunch"[^>]*>)', r'\1\n        <item name="windowSplashScreenBackground">' + BG_HEX + '</item>', t, count=1)
        styles.write_text(t, encoding="utf-8")
        print("حُقن لون خلفية السبلاش بالـ styles.xml")
print(f"✓ أيقونات: {n} ملف، سبلاش: {splashes} ملف، خلفية {BG_HEX}")
