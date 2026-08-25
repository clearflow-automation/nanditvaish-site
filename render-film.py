#!/usr/bin/env python3
"""Pull the film onto the site: the playable build, plus a strip of real scene frames.

The 80 MB master is far too heavy for Pages. The "-small" build is 4.3 MB and plays
fine in a browser, so the film can sit on the page rather than being described.

Frames are sampled across the whole three minutes so the gallery shows the actual
range of the piece — the question cards, the counters, the comparisons.
"""
import pathlib
import subprocess

SRC = pathlib.Path.home() / "Desktop/Unreal Engine/1st Video /production/out"
SITE = pathlib.Path(__file__).parent
VID = SITE / "assets/film"
FRAMES = SITE / "assets/film/frames"
VID.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

build = SRC / "humanoids-2050_NANDIT-small.mp4"
if not build.exists():
    raise SystemExit(f"missing {build}")

out = VID / "humanoids-2050.mp4"
subprocess.run(["cp", str(build), str(out)], check=True)
print(f"film      {out.stat().st_size // 1024 // 1024} MB  ->  assets/film/")

# Sample across the full runtime. Avoid the first and last second (fade in/out).
STOPS = [4, 12, 21, 30, 39, 47, 56, 65, 74, 83, 92, 101, 110, 119, 128, 137, 148, 162]
for i, t in enumerate(STOPS, 1):
    dst = FRAMES / f"f{i:02d}.jpg"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", str(build),
        "-frames:v", "1", "-vf", "scale=1000:-2", "-q:v", "5", str(dst)], check=True)
kb = sum(f.stat().st_size for f in FRAMES.glob("*.jpg")) // 1024
print(f"frames    {len(list(FRAMES.glob('*.jpg')))} stills, {kb} KB  ->  assets/film/frames/")
