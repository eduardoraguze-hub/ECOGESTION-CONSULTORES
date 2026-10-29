"""Anima una foto fija con movimiento de cámara cinematográfico suave (sub-píxel, sin vibración).
Uso: kenburns.py entrada.png salida.mp4 duracion zoom_ini zoom_fin cx_ini cy_ini cx_fin cy_fin
cx/cy = centro del encuadre en fracción de la imagen (0-1).
"""
import subprocess
import sys

from PIL import Image

W, H, FPS = 1080, 1920, 24
src, dst = sys.argv[1], sys.argv[2]
dur, z0, z1, cx0, cy0, cx1, cy1 = map(float, sys.argv[3:10])
img = Image.open(src).convert("RGB")
iw, ih = img.size
n = int(round(dur * FPS))

ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
     "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
     "-pix_fmt", "yuv420p", dst],
    stdin=subprocess.PIPE,
)


def ease(x):  # ease-in-out sinusoidal: arranque y frenado suaves como un dolly real
    import math
    return 0.5 - 0.5 * math.cos(math.pi * x)


base_scale = max(W / iw, H / ih)  # escala para cubrir 1080x1920 con zoom 1.0
for i in range(n):
    p = ease(i / max(n - 1, 1))
    z = z0 + (z1 - z0) * p
    cx = cx0 + (cx1 - cx0) * p
    cy = cy0 + (cy1 - cy0) * p
    cw = W / (base_scale * z)
    ch = H / (base_scale * z)
    left = min(max(cx * iw - cw / 2, 0), iw - cw)
    top = min(max(cy * ih - ch / 2, 0), ih - ch)
    frame = img.resize((W, H), Image.BICUBIC, box=(left, top, left + cw, top + ch))
    ff.stdin.write(frame.tobytes())
ff.stdin.close()
ff.wait()
print("ok", dst, n, "frames")
