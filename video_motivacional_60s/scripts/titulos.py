"""Genera los títulos como PNG transparentes 1080x1920 (capas editables en CapCut / Filmora / Premiere).
Tipografía: Cormorant Garamond (OFL, uso comercial libre). Palabras clave en dorado itálica.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(BASE, "fonts")
OUT = os.path.join(BASE, "overlays")
W, H = 1080, 1920
WHITE = (255, 255, 255, 255)
GOLD = (232, 196, 120, 255)

# (id, inicio, fin, tamaño, posición vertical (centro del bloque), líneas)
# cada línea es una lista de segmentos (texto, estilo) con estilo "n" normal / "g" dorado itálica
TITULOS = [
    ("01_cuando_el_mundo", 0.30, 4.85, 92, 0.42,
     [[("Cuando el mundo", "n")], [("se siente ", "n"), ("demasiado...", "g")]]),
    ("02_paz_interior", 5.50, 14.55, 96, 0.42,
     [[("...tu ", "n"), ("paz interior", "g")], [("te llama.", "n")]]),
    ("03a_riqueza", 15.60, 21.45, 84, 0.40,
     [[("La verdadera ", "n"), ("riqueza", "g")], [("no está en lo que posees,", "n")]]),
    ("03b_libertad", 21.80, 28.05, 88, 0.40,
     [[("sino en la ", "n"), ("libertad", "g")], [("de tu tiempo", "n")]]),
    ("03c_tranquilidad", 28.40, 34.55, 88, 0.40,
     [[("y la ", "n"), ("tranquilidad", "g")], [("de tu mente.", "n")]]),
    ("04a_calma", 35.50, 40.45, 74, 0.40,
     [[("Deja que la ", "n"), ("calma", "g")], [("de estos paisajes", "n")], [("te recuerde", "n")]]),
    ("04b_constancia", 40.80, 45.30, 86, 0.40,
     [[("que la ", "n"), ("constancia", "g")], [("vence a la prisa", "n")]]),
    ("04c_no_rendirse", 45.60, 49.60, 76, 0.40,
     [[("y que el orgullo", "n")], [("de no rendirse", "n")], [("es ", "n"), ("para siempre.", "g")]]),
    ("05a_respira", 51.00, 59.40, 120, 0.36, [[("Respira.", "n")]]),
    ("05b_confia", 52.60, 59.40, 120, 0.44, [[("Confía.", "n")]]),
    ("05c_sigue", 54.20, 59.40, 132, 0.52, [[("Sigue.", "g")]]),
]


def font(style, size):
    if style == "g":
        f = ImageFont.truetype(os.path.join(FONTS, "CormorantGaramond-Italic.ttf"), size)
        f.set_variation_by_name("SemiBold Italic")
    else:
        f = ImageFont.truetype(os.path.join(FONTS, "CormorantGaramond.ttf"), size)
        f.set_variation_by_name("Medium")
    return f


def render(lines, size, ycenter):
    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(text_layer)
    line_h = int(size * 1.18)
    total_h = line_h * len(lines)
    y = int(H * ycenter - total_h / 2)
    for line in lines:
        widths = [d.textlength(txt, font=font(st, size)) for txt, st in line]
        x = (W - sum(widths)) / 2
        for (txt, st), w in zip(line, widths):
            d.text((x, y), txt, font=font(st, size), fill=GOLD if st == "g" else WHITE)
            x += w
        y += line_h
    # sombra suave (legibilidad sobre cualquier fondo) + leve glow
    alpha = text_layer.split()[3]
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda a: int(a * 0.85)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    shadow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow2.putalpha(alpha.point(lambda a: int(a * 0.6)))
    shadow2 = shadow2.filter(ImageFilter.GaussianBlur(4))
    out = Image.alpha_composite(shadow, shadow2)
    out = Image.alpha_composite(out, text_layer)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = []
    for tid, ini, fin, size, yc, lines in TITULOS:
        path = os.path.join(OUT, f"{tid}.png")
        render(lines, size, yc).save(path)
        texto = " ".join("".join(t for t, _ in l) for l in lines)
        meta.append({"id": tid, "png": path, "inicio": ini, "fin": fin, "texto": texto})
    with open(os.path.join(OUT, "titulos.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    # subtítulos SRT (para auto-captions / accesibilidad)
    def ts(s):
        ms = int(round(s * 1000))
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"
    srt = []
    seq = [m for m in meta if not m["id"].startswith("05")]
    seq.append({"inicio": 51.0, "fin": 59.4, "texto": "Respira. Confía. Sigue."})
    for i, m in enumerate(seq, 1):
        srt.append(f"{i}\n{ts(m['inicio'])} --> {ts(m['fin'])}\n{m['texto']}\n")
    with open(os.path.join(BASE, "proyecto", "subtitulos_es.srt"), "w", encoding="utf-8") as f:
        f.write("\n".join(srt))
    print(f"{len(meta)} títulos generados")


if __name__ == "__main__":
    main()
