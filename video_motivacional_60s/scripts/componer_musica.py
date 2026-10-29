"""Composición original 'Respira. Confía. Sigue.' — ambient cinematográfico, 70 BPM, 62 s.
Generada 100% por síntesis (sin samples de terceros) => libre de derechos de autor.
Estructura: piano + pads (0-15s) -> entran cuerdas (15-30s) -> cello y crescendo (30-46s)
-> clímax suave (~45s) -> se disuelve a piano y pads con fade-out (50-62s).
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 62.0
BPM = 70
BEAT = 60 / BPM
N = int(SR * DUR)
t_all = np.arange(N) / SR
rng = np.random.default_rng(7)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def env_adsr(n, a, d, s, r):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n); e[:na] = np.linspace(0, 1, na)
    nd = min(nd, max(n - na, 0)); e[na:na + nd] = np.linspace(1, s, nd)
    if nr > 0 and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(buf, sig, start):
    i = int(start * SR)
    j = min(i + len(sig), len(buf))
    if i < len(buf):
        buf[i:j] += sig[: j - i]


def piano(f, dur, vel=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k, amp in enumerate([1, 0.45, 0.22, 0.12, 0.06, 0.03], start=1):
        inh = 1 + 0.0004 * k * k
        s += amp * np.sin(2 * np.pi * f * k * inh * t) * np.exp(-t * (1.6 + 0.9 * k))
    hammer = np.exp(-t * 60) * rng.normal(0, 0.02, n)
    att = np.minimum(1, t / 0.004)
    return vel * (s + hammer) * att


def pad(freqs, dur, amp=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 2 * np.pi)
            s += np.sin(2 * np.pi * ff * t + ph) + 0.3 * np.sin(2 * np.pi * 2 * ff * t + ph)
    s *= amp / (len(freqs) * 3)
    return s * env_adsr(n, 2.5, 1.0, 0.85, 2.5)


def strings(freqs, dur, amp=0.1):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.07, 0.05, 0.0):
            ff = f * 2 ** (det / 12)
            vib = 0.004 * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6))
            phase = 2 * np.pi * np.cumsum(ff * (1 + vib)) / SR
            # sierra suavizada (8 armónicos)
            saw = sum(np.sin(k * phase) / k for k in range(1, 9))
            s += saw
    s *= amp / (len(freqs) * 3)
    sos = butter(2, 2600, "low", fs=SR, output="sos")
    return sosfilt(sos, s) * env_adsr(n, 1.8, 0.5, 0.9, 1.8)


# Progresión en Re mayor: D - A - Bm - G (I-V-vi-IV), 2 compases por acorde
prog = [
    (50, [62, 66, 69]),  # D
    (45, [61, 64, 69]),  # A
    (47, [62, 66, 71]),  # Bm
    (43, [62, 67, 71]),  # G
]
chord_len = 8 * BEAT  # 6.857 s
n_chords = int(np.ceil(DUR / chord_len))

piano_b = np.zeros(N); pad_b = np.zeros(N); str_b = np.zeros(N); cello_b = np.zeros(N)

for c in range(n_chords):
    root, tri = prog[c % 4]
    t0 = c * chord_len
    # pads a lo largo de todo el tema
    add(pad_b, pad([hz(m) for m in tri] + [hz(root + 12)], chord_len + 2.5), t0)
    # piano: arpegio ascendente/descendente en corcheas suaves
    arp = [root + 12, tri[0], tri[1], tri[2], tri[1] + 12, tri[2], tri[1], tri[0]]
    density = 1 if t0 < 15 or t0 > 48 else 2
    for b in range(8 * density):
        if density == 1 and b % 2:
            continue
        note = arp[(b // (1 if density == 2 else 1)) % len(arp)]
        when = t0 + b * BEAT / density
        if when > DUR - 3:
            break
        vel = 0.32 + 0.06 * np.sin(b) + rng.uniform(-0.03, 0.03)
        add(piano_b, piano(hz(note), 3.5, vel), when)
    # melodía de piano (nota alta por acorde) para dar el "hook"
    add(piano_b, piano(hz(tri[2] + 12), 4.5, 0.38), t0 + 0.02)
    # cuerdas desde 15 s
    if 13 <= t0 <= 52:
        add(str_b, strings([hz(m) for m in tri] + [hz(tri[0] + 12)], chord_len + 1.8), t0)
    # cello (fundamental grave) desde 27 s
    if 26 <= t0 <= 52:
        add(cello_b, strings([hz(root - 12), hz(root)], chord_len + 1.8, 0.16), t0)

# automatización dinámica
def curve(points):
    xs, ys = zip(*points)
    return np.interp(t_all, xs, ys)

str_b *= curve([(0, 0), (14, 0), (20, 0.6), (32, 0.8), (45, 1.15), (50, 0.7), (55, 0.0), (62, 0)])
cello_b *= curve([(0, 0), (26, 0), (33, 0.7), (45, 1.2), (50, 0.6), (54, 0.0), (62, 0)])
pad_b *= curve([(0, 0.0), (2.5, 0.8), (30, 1.0), (45, 1.2), (55, 0.9), (62, 0.6)])
piano_b *= curve([(0, 1.0), (40, 1.0), (45, 1.15), (55, 0.9), (62, 0.8)])

dry = 0.9 * piano_b + 1.0 * pad_b + 0.9 * str_b + 0.8 * cello_b

# reverb de sala grande (IR sintética estéreo, cola ~4.5 s)
def ir(seed):
    r = np.random.default_rng(seed)
    n = int(4.5 * SR)
    tt = np.arange(n) / SR
    noise = r.normal(0, 1, n) * np.exp(-tt * 1.4)
    sos = butter(1, 5500, "low", fs=SR, output="sos")
    return sosfilt(sos, noise) / np.sqrt(n)

wetL = fftconvolve(dry, ir(1))[:N]
wetR = fftconvolve(dry, ir(2))[:N]
L = 0.62 * dry + 2.2 * wetL
R = 0.62 * dry + 2.2 * wetR
# ligero ensanchado estéreo del pad
L += 0.15 * np.roll(pad_b, 480); R += 0.15 * np.roll(pad_b, -480)

st = np.stack([L, R], axis=1)
# fade in/out global (la música se desvanece lentamente al final)
fade = curve([(0, 0), (1.2, 1), (50, 1), (62, 0)]) ** 1.3
st *= fade[:, None]
# highpass para limpiar subgraves
st = sosfilt(butter(2, 35, "high", fs=SR, output="sos"), st, axis=0)
st /= np.max(np.abs(st)) + 1e-9
st *= 0.89  # ~ -1 dBFS pico
out = sys.argv[1] if len(sys.argv) > 1 else "musica.wav"
wavfile.write(out, SR, (st * 32767).astype(np.int16))
print("ok", out)
