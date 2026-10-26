#!/usr/bin/env python3
"""Arma el reel 'El Plan Divino' (60 s, 9:16) a partir de imágenes, voz y música.

Salidas en video-plan-divino/:
  final/PlanDivino_60s_subtitulado.mp4   -> listo para publicar
  final/PlanDivino_60s_limpio.mp4        -> sin texto, para editar en CapCut/Filmora
  clips/E*.mp4                           -> cada escena por separado (sin audio)
  subtitulos/PlanDivino_ES.srt           -> importable en CapCut / Filmora / YouTube
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMG, CLIPS, SUBS, FINAL, TMP = (ROOT / d for d in ("imagenes", "clips", "subtitulos", "final", "tmp"))
for d in (CLIPS, SUBS, FINAL, TMP):
    d.mkdir(exist_ok=True)

W, H, FPS, TOTAL, XF = 1080, 1920, 30, 60.0, 0.6  # XF = duración del crossfade
# 6 Mbps: calidad alta para Reels/TikTok y archivos < 50 MB (el grano fílmico infla el CRF)
VENC = ["-c:v", "libx264", "-preset", "slow", "-b:v", "6M", "-maxrate", "8M", "-bufsize", "12M", "-pix_fmt", "yuv420p"]

# (imagen, inicio, fin, movimiento) — cortes alineados a las frases de la voz
SCENES = [
    ("E1_oracion_cielo.png",     0.0,  5.7, "push_face"),   # gancho
    ("E1_oracion_cielo.png",     5.7, 15.5, "pull_out"),    # preguntas
    ("E2_rompecabezas_mapa.png", 15.5, 27.0, "rotate_in"),  # plan divino
    ("E3_atleta.png",            27.0, 33.5, "push_in"),    # preparación
    ("E4_violinista.png",        33.5, 37.8, "pan_right"),  # puliendo
    ("E5_brote_mar.png",         37.8, 46.0, "rise"),       # confianza y paciencia
    ("E6_amanecer_sonrisa.png",  46.0, 60.0, "pull_out_slow"),  # cierre
]


def run(cmd):
    subprocess.run(cmd, check=True)


def zoompan(motion, frames):
    n = frames
    # z: zoom; x/y: esquina superior izquierda del recorte sobre la imagen escalada
    expr = {
        "push_face":     (f"1.35+0.20*on/{n}", "iw*0.18", "ih*0.22"),
        "pull_out":      (f"1.45-0.40*on/{n}", "(iw-iw/zoom)/2", "(ih-ih/zoom)*0.35"),
        "rotate_in":     (f"1.05+0.30*on/{n}", "(iw-iw/zoom)/2", "(ih-ih/zoom)*0.45"),
        "push_in":       (f"1.10+0.25*on/{n}", "(iw-iw/zoom)/2", "(ih-ih/zoom)*0.55"),
        "pan_right":     ("1.25", f"(iw-iw/zoom)*(0.15+0.6*on/{n})", "(ih-ih/zoom)*0.45"),
        "rise":          ("1.20", "(iw-iw/zoom)/2", f"(ih-ih/zoom)*(0.95-0.9*on/{n})"),
        "pull_out_slow": (f"1.30-0.30*on/{n}", "(iw-iw/zoom)/2", "(ih-ih/zoom)*0.4"),
    }[motion]
    z, x, y = expr
    return (f"scale={W*2}:{H*2}:flags=lanczos,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS},"
            # look cinematográfico: leve contraste, viñeta y grano
            "eq=contrast=1.06:saturation=1.08,vignette=PI/5,noise=alls=6:allf=t,format=yuv420p")


def render_clips():
    paths = []
    for i, (img, start, end, motion) in enumerate(SCENES):
        # cada clip se alarga XF para cubrir el solapamiento del crossfade
        dur = end - start + (XF if i < len(SCENES) - 1 else 0)
        frames = round(dur * FPS)
        out = CLIPS / f"E{i+1:02d}_{Path(img).stem}_{motion}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", str(IMG / img),
             "-vf", zoompan(motion, frames), "-frames:v", str(frames),
             *VENC, str(out)])
        paths.append((out, dur))
    return paths


def join_clips(paths):
    inputs, chain, offset, last = [], [], 0.0, "0:v"
    for p, _ in paths:
        inputs += ["-i", str(p)]
    for i in range(1, len(paths)):
        offset += paths[i - 1][1] - XF
        lbl = f"v{i}"
        chain.append(f"[{last}][{i}:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[{lbl}]")
        last = lbl
    chain.append(f"[{last}]fade=t=in:st=0:d=0.4,fade=t=out:st={TOTAL-1.2}:d=1.2[vout]")
    out = TMP / "video_mudo.mp4"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(chain),
         "-map", "[vout]", "-t", str(TOTAL), *VENC, str(out)])
    return out


def mix_audio():
    voz, musica = ROOT / "audio/voz_toma1.mp3", ROOT / "audio/musica_toma1.mp3"
    out = FINAL / "PlanDivino_mezcla_audio.m4a"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(voz), "-i", str(musica), "-filter_complex",
         "[0:a]aresample=48000,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,"
         "volume=1.6,apad,asplit=2[v][vsc];"
         "[1:a]aresample=48000,volume=0.55[m];"
         # la música baja automáticamente cuando habla la voz (ducking)
         "[m][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=600[mduck];"
         f"[v][mduck]amix=inputs=2:duration=longest:normalize=0,atrim=0:{TOTAL},"
         f"afade=t=in:d=0.5,afade=t=out:st={TOTAL-2.5}:d=2.5,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
         "-map", "[a]", "-c:a", "aac", "-b:a", "256k", str(out)])
    return out


def build_subs():
    words = [w for w in json.loads((SUBS / "words.json").read_text())["words"]
             if w["type"] == "word" and not w["text"].startswith("[") and not w["text"].endswith("]")]
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        t = w["text"]
        if t[-1] in ".?…," or len(cur) >= 5:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)

    def ts(s, sep=","):
        h, m = int(s // 3600), int(s % 3600 // 60)
        return f"{h:02d}:{m:02d}:{s % 60:06.3f}".replace(".", sep)

    srt, ass_events = [], []
    for i, c in enumerate(chunks):
        start = c[0]["start"]
        end = chunks[i + 1][0]["start"] - 0.02 if i + 1 < len(chunks) else c[-1]["end"] + 0.6
        end = min(end, c[-1]["end"] + 0.8)
        text = " ".join(w["text"] for w in c).rstrip(",")
        srt.append(f"{i+1}\n{ts(start)} --> {ts(end)}\n{text}\n")
        ass_events.append((start, end, text))
    (SUBS / "PlanDivino_ES.srt").write_text("\n".join(srt), encoding="utf-8")

    def at(s):
        return f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"

    keywords = {"Dios", "plan", "perfecto", "preparando", "confiar,", "paciente", "Su", "tiempo…", "plan.",
                "grande.", "fortaleciendo,", "puliendo.", "infinitamente"}
    lines = []
    for s, e, t in ass_events:
        styled = " ".join(r"{\c&H4FC8FF&}" + w + r"{\c&HFFFFFF&}" if w in keywords else w for w in t.split())
        lines.append(f"Dialogue: 0,{at(s)},{at(e)},Sub,,0,0,0,,{{\\fad(120,80)}}{styled.upper()}")
    # gancho visual (primeros 3.5 s) y cierre con CTA
    lines.append(r"Dialogue: 1,0:00:00.00,0:00:03.60,Hook,,0,0,0,,{\fad(200,300)}¿Y SI TU FRACASO" r"\N" r"{\c&H4FC8FF&}FUERA PARTE DEL PLAN?")
    lines.append(r"Dialogue: 1,0:00:55.80,0:01:00.00,Title,,0,0,0,,{\fad(500,0)}Cree en Su tiempo" r"\N" r"y en Su plan")
    lines.append(r"Dialogue: 1,0:00:56.60,0:01:00.00,CTA,,0,0,0,,{\fad(400,0)}Comenta «CONFÍO» si lo necesitabas hoy" r"\N" r"Síguenos para más")
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,DejaVu Sans,62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,1,0,1,5,2,2,90,90,560,1
Style: Hook,DejaVu Sans,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,1,0,1,6,3,8,70,70,300,1
Style: Title,DejaVu Serif,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,1,0,0,100,100,1,0,1,4,3,5,80,80,0,1
Style: CTA,DejaVu Sans,46,&H004FC8FF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,1,0,1,4,2,2,80,80,330,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lines) + "\n"
    path = SUBS / "PlanDivino_ES_estilizado.ass"
    path.write_text(ass, encoding="utf-8")
    return path


def mux(video, audio, ass):
    clean = FINAL / "PlanDivino_60s_limpio.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(audio), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(clean)])
    final = FINAL / "PlanDivino_60s_subtitulado.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(audio), "-vf", f"ass={ass}",
         "-map", "0:v", "-map", "1:a", *VENC, "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(final)])
    return clean, final


if __name__ == "__main__":
    ass = build_subs()
    audio = mix_audio()
    video = join_clips(render_clips())
    for f in mux(video, audio, ass):
        print(f)
