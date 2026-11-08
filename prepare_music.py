#!/usr/bin/env python3
"""يجهّز الأغاني الثابتة: بيلاقيها بـ www/assets/music (وبمجلداتها الفرعية) وكمان بالأماكن البديلة
(assets/music أو music أو www/music بجذر المشروع) وبينسخها لمكانها الصح، ثم بيكتب manifest.json."""
from pathlib import Path
import json, shutil

ROOT = Path(__file__).resolve().parent
MUSIC = ROOT / "www" / "assets" / "music"
MUSIC.mkdir(parents=True, exist_ok=True)
EXTS = {".mp3", ".m4a", ".aac", ".wav", ".ogg", ".opus", ".flac", ".mp4", ".webm", ".weba", ".oga"}

for alt in (ROOT / "assets" / "music", ROOT / "music", ROOT / "www" / "music", ROOT / "Music"):
    if alt.is_dir():
        for f in alt.rglob("*"):
            if f.is_file() and f.suffix.lower() in EXTS and not (MUSIC / f.name).exists():
                shutil.copy2(f, MUSIC / f.name)
                print(f"نسخت {f.relative_to(ROOT)} -> www/assets/music/")

files = sorted((f for f in MUSIC.rglob("*") if f.is_file() and f.suffix.lower() in EXTS),
               key=lambda x: str(x.relative_to(MUSIC)).casefold())
tracks = [{"id": f"static-{i+1}", "file": f.relative_to(MUSIC).as_posix(), "title": f.stem.replace("_", " ")}
          for i, f in enumerate(files)]
(MUSIC / "manifest.json").write_text(json.dumps({"tracks": tracks}, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"Prepared {len(tracks)} bundled tracks in {MUSIC}")
for t in tracks: print(" -", t["file"])
if not tracks:
    print("WARNING: no tracks found! Current folder content:")
    for f in sorted(MUSIC.rglob("*")): print("   ", f.relative_to(ROOT))
    print("Supported extensions:", ", ".join(sorted(EXTS)))
