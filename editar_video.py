#!/usr/bin/env python3
"""
Editor de video EcoGestión Consultores -> Reels/TikTok/Shorts 9:16 (1080x1920).

Uso:
  python3 editar_video.py VIDEO_ENTRADA [--srt subtitulos.srt] [--titulo "Texto gancho"] [--sin-cortes]

Pasos que aplica (según 2_Estilo/estilo.json y 1_Referencias/referencias.json):
  1. Ritmo/cortes: elimina silencios (jump cuts) para un ritmo ágil.
  2. Reencuadre 9:16: si el video es horizontal, centra y rellena con fondo desenfocado.
  3. Color: grading de marca (contraste, saturación, verdes).
  4. Logo: marca de agua en esquina + tarjeta de cierre con logo.
  5. Animaciones: título gancho animado (entrada), fade in/out, zoom suave.
  6. Subtítulos: estilo de marca (Inter Bold, blanco con resaltado verde) desde SRT
     o transcripción automática si faster-whisper está disponible.
  7. Audio normalizado a -14 LUFS. Exporta a 3_Entregas/.
"""
import argparse, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
STYLE = json.load(open(os.path.join(ROOT, "2_Estilo", "estilo.json"), encoding="utf-8"))
REF_PATH = os.path.join(ROOT, "1_Referencias", "referencias.json")
REF = json.load(open(REF_PATH, encoding="utf-8")) if os.path.exists(REF_PATH) else {}
W, H, FPS = 1080, 1920, STYLE["salida"]["fps"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Error ejecutando:\n{' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
               "-of", "json", path]).stdout
    d = json.loads(out)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    has_audio = any(s["codec_type"] == "audio" for s in d["streams"])
    return v["width"], v["height"], float(d["format"]["duration"]), has_audio


def ass_color(hexc, alpha="00"):
    h = hexc.lstrip("#")
    return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


# ---------- 1. Ritmo: detección de silencios ----------
def keep_segments(path, dur):
    r = STYLE["ritmo"]
    out = subprocess.run(["ffmpeg", "-i", path, "-af",
                          f"silencedetect=noise={r['umbral_silencio_db']}dB:d={r['silencio_minimo_s']}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    pad = 0.12
    segs, t = [], 0.0
    for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
        if s - t > 0.2:
            segs.append((max(0, t - pad if t else 0), min(dur, s + pad)))
        t = e
    if dur - t > 0.2:
        segs.append((max(0, t - pad), dur))
    return segs or [(0, dur)]


# ---------- 6. Subtítulos ----------
def parse_srt(path):
    txt = open(path, encoding="utf-8-sig").read()
    items = []
    for b in re.split(r"\n\s*\n", txt.strip()):
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)\s*\n(.+)", b, re.S)
        if m:
            g = list(map(int, m.groups()[:8]))
            a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
            z = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
            items.append((a, z, " ".join(m.group(9).split())))
    return items


def transcribe(path):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("· faster-whisper no instalado: se omite transcripción automática (usa --srt).")
        return []
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = model.transcribe(path, language="es", word_timestamps=True, vad_filter=True)
    words = [(w.start, w.end, w.word.strip()) for s in segs for w in (s.words or [])]
    return words  # nivel palabra


def remap(t, segs):
    """Convierte tiempo original -> tiempo tras cortes."""
    acc = 0.0
    for a, b in segs:
        if a <= t <= b:
            return acc + (t - a)
        if t < a:
            return acc
        acc += b - a
    return acc


def build_chunks(items, word_level):
    """Agrupa en bloques cortos de N palabras (estilo reels)."""
    n = STYLE["subtitulos"]["max_palabras_por_linea"]
    chunks = []
    if word_level:
        for i in range(0, len(items), n):
            grp = items[i:i + n]
            chunks.append((grp[0][0], grp[-1][1], [g[2] for g in grp], [(g[0], g[1]) for g in grp]))
    else:
        for a, z, text in items:
            ws = text.split()
            per = (z - a) / max(1, len(ws))
            for i in range(0, len(ws), n):
                grp = ws[i:i + n]
                s = a + i * per
                chunks.append((s, s + per * len(grp), grp, [(s + k * per, s + (k + 1) * per) for k in range(len(grp))]))
    return chunks


def ts(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def write_ass(chunks, segs, offset, title, total, out):
    st = STYLE["subtitulos"]; c = STYLE["colores"]
    font = "Inter"
    hi = ass_color(st["color_resaltado"]); wh = ass_color(st["color_texto"])
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Sub,{font},{st['tamano']},{wh},{hi},{ass_color(st['contorno'])},&H80000000,-1,0,0,0,100,100,1,0,1,"
        f"{st['grosor_contorno']},2,2,80,80,{st['posicion_y_desde_abajo']},1",
        f"Style: Titulo,{font},86,{wh},{wh},{ass_color(c['fondo_oscuro'])},&H00000000,-1,0,0,0,100,100,0,0,3,"
        f"22,0,8,90,90,330,1",
        f"Style: Tag,{font},40,{ass_color(c['fondo_oscuro'])},{wh},{ass_color(c['verde_acento'])},&H00000000,-1,0,0,0,100,100,2,0,3,"
        f"14,0,8,90,90,270,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    # Gancho animado (entra con escala + fade) los primeros segundos
    if title:
        tag = REF.get("etiqueta_gancho", "ECOGESTIÓN CONSULTORES")
        lines.append(f"Dialogue: 1,{ts(0.15)},{ts(offset + 3.2)},Tag,,0,0,0,,"
                     r"{\fad(200,250)\move(540,250,540,270,0,300)}" + tag)
        lines.append(f"Dialogue: 1,{ts(0.25)},{ts(offset + 3.2)},Titulo,,0,0,0,,"
                     r"{\fad(250,300)\fscx70\fscy70\t(0,280,\fscx104\fscy104)\t(280,420,\fscx100\fscy100)}"
                     + title.upper())
    up = st.get("mayusculas", True)
    for a, z, words, wt in chunks:
        A, Z = remap(a, segs) + offset, remap(z, segs) + offset
        if Z - A < 0.05:
            continue
        # karaoke: la palabra activa se resalta en verde de marca (pop)
        for k, (wa, wz) in enumerate(wt):
            s = remap(wa, segs) + offset
            e = remap(wt[k + 1][0], segs) + offset if k + 1 < len(wt) else Z
            if e - s < 0.03:
                continue
            txt = " ".join(
                (r"{\c" + hi + r"\fscx112\fscy112}" + (w.upper() if up else w) + r"{\c" + wh + r"\fscx100\fscy100}")
                if j == k else (w.upper() if up else w) for j, w in enumerate(words))
            pop = r"{\fad(60,0)}" if k == 0 else ""
            lines.append(f"Dialogue: 0,{ts(s)},{ts(e)},Sub,,0,0,0,,{pop}{txt}")
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")


# ---------- Tarjeta de cierre (outro) con logo animado ----------
def make_outro(tmp, dur):
    c = STYLE["colores"]; logo = os.path.join(ROOT, STYLE["logo"]["archivo"])
    cta = REF.get("cta_cierre", "Sostenibilidad que genera valor")
    web = REF.get("cta_web", "ecogestionconsultores.com")
    font = os.path.join(ROOT, STYLE["tipografia"]["titulos"])
    out = os.path.join(tmp, "outro.mp4")
    fil = (f"color=c={c['blanco']}:s={W}x{H}:r={FPS}:d={dur}[bg];"
           f"[1:v]scale=640:-1,format=rgba,fade=in:st=0:d=0.4:alpha=1[lg];"
           f"[bg][lg]overlay=(W-w)/2:'560-40*min(1,t/0.5)'[a];"
           f"[a]drawtext=fontfile='{font}':text='{cta}':fontsize=58:fontcolor={c['verde_oscuro']}:"
           f"x=(w-tw)/2:y=1320:alpha='min(1,max(0,(t-0.4)/0.4))',"
           f"drawbox=x=340:y=1430:w=400:h=8:color={c['verde_acento']}:t=fill:enable='gte(t,0.6)',"
           f"drawtext=fontfile='{font}':text='{web}':fontsize=44:fontcolor={c['azul']}:"
           f"x=(w-tw)/2:y=1480:alpha='min(1,max(0,(t-0.7)/0.4))',fade=out:st={dur-0.3}:d=0.3,format=yuv420p[v]")
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=white:s=16x16:d={dur}", "-loop", "1", "-t", str(dur), "-i", logo,
         "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo",
         "-filter_complex", fil.replace("color=c=", "color=c=").replace("[bg];", "[bg];", 1),
         "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-ar", "48000", "-shortest", out])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("--srt")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--sin-cortes", action="store_true")
    ap.add_argument("--salida")
    a = ap.parse_args()

    src = os.path.abspath(a.entrada)
    w, h, dur, has_audio = probe(src)
    base = os.path.splitext(os.path.basename(src))[0]
    out = a.salida or os.path.join(ROOT, STYLE["salida"]["carpeta"], f"{base}_9x16_1080x1920.mp4")
    tmp = tempfile.mkdtemp(prefix="eco_")
    print(f"▶ {base}: {w}x{h}, {dur:.1f}s")

    # 1. Ritmo/cortes
    segs = [(0, dur)] if (a.sin_cortes or not has_audio or not STYLE["ritmo"]["corte_silencios"]) else keep_segments(src, dur)
    print(f"· Cortes: {len(segs)} segmentos, {sum(b - a_ for a_, b in segs):.1f}s de {dur:.1f}s")

    # 6. Subtítulos (sobre tiempos originales)
    if a.srt:
        chunks = build_chunks(parse_srt(a.srt), word_level=False)
    else:
        words = transcribe(src)
        chunks = build_chunks(words, word_level=True) if words else []

    # 2-5. Construcción del filtro principal
    g = STYLE["color_grading"]; lg = STYLE["logo"]
    logo = os.path.join(ROOT, lg["archivo"])
    parts, concat_in = [], ""
    for i, (s, e) in enumerate(segs):
        parts.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}]")
        if has_audio:
            parts.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=in:d=0.02,afade=out:st={max(0, e - s - 0.03)}:d=0.03[a{i}]")
        concat_in += f"[v{i}]" + (f"[a{i}]" if has_audio else "")
    parts.append(f"{concat_in}concat=n={len(segs)}:v=1:a={1 if has_audio else 0}[vc]" + ("[ac]" if has_audio else ""))
    total = sum(e - s for s, e in segs)
    # reencuadre 9:16 con fondo desenfocado si es horizontal
    if w / h > 0.6:
        parts.append(f"[vc]split[bga][fga];"
                     f"[bga]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.08[bgb];"
                     f"[fga]scale={W}:-2[fgb];[bgb][fgb]overlay=(W-w)/2:(H-h)/2[vr]")
    else:
        parts.append(f"[vc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}[vr]")
    # zoom suave (push-in 4%) + color de marca
    parts.append(f"[vr]scale=w='{W}*(1+0.04*t/{max(total,1):.2f})':h=-2:eval=frame,crop={W}:{H},setsar=1,fps={FPS},"
                 f"eq=contrast={g['contraste']}:saturation={g['saturacion']}:brightness={g['brillo']}:gamma_g={g['gamma_verde']},"
                 f"fade=in:st=0:d=0.3[vg]")
    parts.append(f"[1:v]scale={lg['ancho_px']}:-1,format=rgba,colorchannelmixer=aa={lg['opacidad']}[lgo]")
    parts.append("[vg][lgo]overlay=W-w-50:70[vl]")
    ass = os.path.join(tmp, "subs.ass")
    write_ass(chunks, segs, 0.0, a.titulo, total, ass)
    fontsdir = os.path.join(ROOT, "2_Estilo", "fuentes")
    parts.append(f"[vl]ass='{ass}':fontsdir='{fontsdir}',format=yuv420p[vout]")
    if has_audio:
        parts.append("[ac]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")

    main_mp4 = os.path.join(tmp, "main.mp4")
    cmd = ["ffmpeg", "-y", "-i", src, "-loop", "1", "-i", logo]
    if not has_audio:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]" if has_audio else "2:a",
            "-t", f"{total:.3f}", "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", main_mp4]
    run(cmd)

    # Cierre con logo + concatenación final
    outro = make_outro(tmp, STYLE["ritmo"]["outro_s"])
    run(["ffmpeg", "-y", "-i", main_mp4, "-i", outro, "-filter_complex",
         "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print(f"✔ Entrega: {out}")


if __name__ == "__main__":
    main()
