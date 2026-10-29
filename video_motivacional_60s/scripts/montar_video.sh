#!/usr/bin/env bash
# Montaje final del video motivacional 60 s (1080x1920, 24 fps).
# Línea de tiempo (segundos):  S1 0-5 | S2 5-15 | S3a 15-25 | S3b 25-35 | S4a 35-43 | S4b 43-50 | S5 50-60
set -euo pipefail
cd "$(dirname "$0")/.."
FX="fps=24,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p"
T=0.5   # duración de cada transición (disolvencia cinematográfica)

# 1) Tomas de video Kling: normalizar y alargar 0.5 s (congelado) para cubrir la disolvencia
[ -f escenas/S1_montanas_amanecer.mp4 ] || ffmpeg -v error -y -i clips/S1_montanas_amanecer.mp4 -vf "$FX,tpad=stop_mode=clone:stop_duration=0.5" -t 5.5  -an -c:v libx264 -crf 14 -preset slow escenas/S1_montanas_amanecer.mp4
[ -f escenas/S3a_bosque_rayos_sol.mp4 ] || ffmpeg -v error -y -i clips/S3a_bosque_rayos_sol.mp4 -vf "$FX,tpad=stop_mode=clone:stop_duration=0.5" -t 10.5 -an -c:v libx264 -crf 14 -preset slow escenas/S3a_bosque_rayos_sol.mp4
[ -f escenas/S4a_lago_atardecer.mp4 ] || ffmpeg -v error -y -i clips/S4a_lago_atardecer.mp4  -vf "$FX,tpad=stop_mode=clone:stop_duration=0.5" -t 8.5  -an -c:v libx264 -crf 14 -preset slow escenas/S4a_lago_atardecer.mp4

# 2) Ensamble con disolvencias + etalonaje cinematográfico (contraste suave, viñeta, grano)
#    (borra escenas/BASE_sin_texto.mp4 para forzar un nuevo ensamble)
[ -f escenas/BASE_sin_texto.mp4 ] || ffmpeg -v error -y \
  -i escenas/S1_montanas_amanecer.mp4 -i escenas/S2_playa.mp4 -i escenas/S3a_bosque_rayos_sol.mp4 \
  -i escenas/S3b_sendero_bosque.mp4 -i escenas/S4a_lago_atardecer.mp4 -i escenas/S4b_camino_rural.mp4 \
  -i escenas/S5_cielo_estrellado.mp4 \
  -filter_complex "
    [0:v]fade=in:st=0:d=0.6[v0];
    [v0][1:v]xfade=transition=fade:duration=$T:offset=5[x1];
    [x1][2:v]xfade=transition=fade:duration=$T:offset=15[x2];
    [x2][3:v]xfade=transition=fadeblack:duration=$T:offset=25[x3];
    [x3][4:v]xfade=transition=fade:duration=$T:offset=35[x4];
    [x4][5:v]xfade=transition=fade:duration=$T:offset=43[x5];
    [x5][6:v]xfade=transition=fadeblack:duration=0.8:offset=50[x6];
    [x6]eq=contrast=1.06:saturation=1.08:gamma=0.98,
        colorbalance=rs=0.02:bs=-0.02:rh=0.03:bh=-0.03,
        vignette=angle=PI/5,
        noise=alls=3:allf=t,
        fade=out:st=59.0:d=1.0,format=yuv420p[v]" \
  -map "[v]" -t 60 -c:v libx264 -crf 19 -maxrate 24M -bufsize 48M -preset slow escenas/BASE_sin_texto.mp4

# 3) Títulos animados (fade + leve ascenso) sobre la base
python3 - <<'PY'
import json, subprocess
meta = json.load(open("overlays/titulos.json", encoding="utf-8"))
inputs, chains = ["-i", "escenas/BASE_sin_texto.mp4"], []
prev = "0:v"
for k, m in enumerate(meta, 1):
    ini, fin = m["inicio"], m["fin"]
    d = fin - ini
    inputs += ["-loop", "1", "-t", f"{d:.3f}", "-i", m["png"]]
    fo = 0.7 if not m["id"].startswith("05") else 0.6
    chains.append(
        f"[{k}:v]format=rgba,fade=in:st=0:d=0.9:alpha=1,fade=out:st={d-fo:.3f}:d={fo}:alpha=1,"
        f"setpts=PTS+{ini}/TB[t{k}]")
    # ascenso de 28 px con desaceleración durante 1.4 s
    y = f"28*pow(max(0\\,1-(t-{ini})/1.4)\\,2)"
    chains.append(f"[{prev}][t{k}]overlay=x=0:y='{y}':eof_action=pass:enable='between(t,{ini},{fin})'[o{k}]")
    prev = f"o{k}"
fc = ";".join(chains)
cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", f"[{prev}]",
       "-t", "60", "-c:v", "libx264", "-crf", "19", "-maxrate", "22M", "-bufsize", "44M", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
       "escenas/VIDEO_con_texto_sin_audio.mp4"]
subprocess.run(cmd, check=True)
print("titulos ok")
PY

# 4) Audio: música original, fade-in, desvanecimiento lento final, normalizada a -14 LUFS (redes sociales)
ffmpeg -v error -y -i audio/musica_original_62s.wav \
  -af "atrim=0:60,afade=t=in:st=0:d=1.5,afade=t=out:st=52:d=8,loudnorm=I=-14:TP=-1.5:LRA=11" \
  -ar 48000 audio/musica_final_60s.wav

mkdir -p FINAL
ffmpeg -v error -y -i escenas/VIDEO_con_texto_sin_audio.mp4 -i audio/musica_final_60s.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart \
  "FINAL/Respira_Confia_Sigue_60s_9x16_FINAL.mp4"
ffmpeg -v error -y -i escenas/BASE_sin_texto.mp4 -i audio/musica_final_60s.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart \
  "FINAL/Respira_Confia_Sigue_60s_9x16_SIN_TEXTO_editable.mp4"
echo "MONTAJE COMPLETO"
