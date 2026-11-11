#!/usr/bin/env python3
"""
Organizador automático de evidencias de auditoría capturadas con gafas inteligentes.

Flujo:
  Gafas -> app del fabricante (auto-importación a la galería del teléfono)
        -> carga automática a la nube (OneDrive / Google Drive / iCloud)
        -> carpeta "Bandeja" sincronizada en la PC
        -> ESTE SCRIPT clasifica cada foto/video en:
           Destino/<Ingenio>/<Norma>/<Auditoría>/<Pilar o área>/<Fotos|Videos>/
           y registra la evidencia (hash SHA-256, fecha, GPS) en un CSV listo para el informe.

Clasificación (en este orden):
  1. GPS del archivo dentro de la geocerca de un ingenio  -> ese ingenio.
  2. Sesión de auditoría activa (comando `sesion`)          -> ingenio/norma/pilar de la sesión.
  3. Sin datos                                              -> _Sin_Clasificar/<fecha>/

Uso rápido:
  python organizador_evidencias.py sesion --ingenio Ingenio_01 --norma SMETA \
         --pilar 02_Salud_Seguridad --auditoria 2026-11_SMETA_Anual
  python organizador_evidencias.py vigilar          # corre en segundo plano
  python organizador_evidencias.py procesar         # una sola pasada
  python organizador_evidencias.py estado
  python organizador_evidencias.py cerrar

Requisitos: Python 3.9+, Pillow (pip install pillow). Opcionales: ffprobe (metadatos de video),
pillow-heif (fotos HEIC de iPhone).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # el script funciona sin Pillow, solo pierde EXIF de fotos
    Image = None

try:
    import pillow_heif  # type: ignore

    pillow_heif.register_heif_opener()
except Exception:
    pass

BASE = Path(__file__).resolve().parent
CONFIG_POR_DEFECTO = BASE / "config.json"
ARCHIVO_SESION = BASE / "sesion_activa.json"

TEMPORALES = (".tmp", ".partial", ".crdownload", ".part", ".download", ".icloud")
COLUMNAS_REGISTRO = [
    "id_evidencia", "fecha_captura", "tipo", "ingenio", "norma", "auditoria",
    "pilar_area", "archivo", "ruta_relativa", "sha256", "latitud", "longitud",
    "fuente_clasificacion", "alerta", "archivo_original", "procesado_en",
    "hallazgo_vinculado", "observaciones_auditor",
]


# ----------------------------------------------------------------------------- utilidades
def cargar_json(ruta: Path, defecto=None):
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return defecto
    except json.JSONDecodeError as e:
        sys.exit(f"[ERROR] {ruta} no es un JSON válido: {e}")


def guardar_json(ruta: Path, datos) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_suffix(ruta.suffix + ".tmp")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(ruta)


def limpiar(texto: str) -> str:
    texto = re.sub(r"[^\w\-]+", "_", str(texto).strip(), flags=re.UNICODE)
    return texto.strip("_") or "SinNombre"


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def distancia_m(lat1, lon1, lat2, lon2) -> float:
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def log(msg: str) -> None:
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


# ----------------------------------------------------------------------------- metadatos
def _gps_a_decimal(valor, ref) -> float | None:
    try:
        g, m, s = (float(x) for x in valor)
        dec = g + m / 60 + s / 3600
        return -dec if str(ref).upper() in ("S", "W") else dec
    except Exception:
        return None


def metadatos_foto(ruta: Path):
    if Image is None:
        return None, None, None
    try:
        with Image.open(ruta) as img:
            exif = img.getexif()
            fecha_txt = exif.get_ifd(0x8769).get(0x9003) or exif.get(0x0132)
            gps = exif.get_ifd(0x8825)
    except Exception:
        return None, None, None
    fecha = None
    if fecha_txt:
        try:
            fecha = datetime.strptime(str(fecha_txt).strip("\x00 "), "%Y:%m:%d %H:%M:%S")
        except ValueError:
            pass
    lat = lon = None
    if gps and 2 in gps and 4 in gps:
        lat = _gps_a_decimal(gps[2], gps.get(1, "N"))
        lon = _gps_a_decimal(gps[4], gps.get(3, "E"))
    return fecha, lat, lon


def metadatos_video(ruta: Path):
    if not shutil.which("ffprobe"):
        return None, None, None
    try:
        salida = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(ruta)],
            capture_output=True, text=True, timeout=30,
        ).stdout
        tags = {k.lower(): v for k, v in json.loads(salida or "{}").get("format", {}).get("tags", {}).items()}
    except Exception:
        return None, None, None
    fecha = None
    if "creation_time" in tags:
        try:
            utc = datetime.fromisoformat(tags["creation_time"].replace("Z", "+00:00"))
            fecha = utc.astimezone().replace(tzinfo=None)  # hora local de la PC
        except ValueError:
            pass
    lat = lon = None
    iso6709 = tags.get("location") or tags.get("com.apple.quicktime.location.iso6709")
    if iso6709:
        m = re.match(r"([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)", iso6709)
        if m:
            lat, lon = float(m.group(1)), float(m.group(2))
    return fecha, lat, lon


# ----------------------------------------------------------------------------- clasificación
def ingenio_por_gps(cfg, lat, lon):
    if lat is None or lon is None:
        return None
    mejor = None
    for ing in cfg.get("ingenios", []):
        if ing.get("lat") is None or ing.get("lon") is None:
            continue
        d = distancia_m(lat, lon, ing["lat"], ing["lon"])
        if d <= (ing.get("radio_m") or cfg.get("radio_geocerca_m", 3000)) and (mejor is None or d < mejor[1]):
            mejor = (ing["nombre"], d)
    return mejor[0] if mejor else None


def sesion_vigente(sesion, fecha: datetime):
    if not sesion:
        return None
    inicio = datetime.fromisoformat(sesion["inicio"]) - timedelta(minutes=sesion.get("tolerancia_min", 15))
    fin = datetime.fromisoformat(sesion["fin"]) if sesion.get("fin") else \
        datetime.fromisoformat(sesion["inicio"]) + timedelta(hours=sesion.get("vigencia_horas", 12))
    return sesion if inicio <= fecha <= fin else None


def clasificar(cfg, sesion, fecha, lat, lon):
    ing_gps = ingenio_por_gps(cfg, lat, lon)
    ses = sesion_vigente(sesion, fecha)
    alerta = ""
    if ses:
        ingenio = ing_gps or ses["ingenio"]
        if ing_gps and ing_gps != ses["ingenio"]:
            alerta = f"GPS indica {ing_gps}, la sesión indica {ses['ingenio']}"
        fuente = "GPS+sesion" if ing_gps else "sesion"
        return dict(ingenio=ingenio, norma=ses["norma"], auditoria=ses.get("auditoria") or f"{fecha:%Y-%m-%d}",
                    pilar=ses.get("pilar") or "00_General", fuente=fuente, alerta=alerta)
    if ing_gps:
        return dict(ingenio=ing_gps, norma=cfg.get("norma_por_defecto", "Inspeccion_Campo"),
                    auditoria=f"{fecha:%Y-%m-%d}", pilar="00_General", fuente="GPS", alerta="Sin sesión activa")
    return dict(ingenio="_Sin_Clasificar", norma="", auditoria=f"{fecha:%Y-%m-%d}", pilar="",
                fuente="ninguna", alerta="Sin GPS ni sesión: asignar manualmente")


# ----------------------------------------------------------------------------- procesamiento
class Organizador:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.entrada = Path(cfg["carpeta_entrada"]).expanduser()
        self.destino = Path(cfg["carpeta_destino"]).expanduser()
        self.ext_foto = {e.lower() for e in cfg.get("extensiones_foto", [".jpg", ".jpeg", ".heic", ".png", ".dng"])}
        self.ext_video = {e.lower() for e in cfg.get("extensiones_video", [".mp4", ".mov", ".m4v"])}
        self.indice_ruta = self.destino / ".indice_hashes.json"
        self.indice = cargar_json(self.indice_ruta, {})
        self.tamanos: dict[str, tuple[int, float]] = {}
        self.vistos: set[tuple[str, int, float]] = set()  # evita re-hashear y repetir avisos

    def candidatos(self):
        if not self.entrada.exists():
            log(f"[AVISO] No existe la carpeta de entrada: {self.entrada}")
            return []
        patron = "**/*" if self.cfg.get("incluir_subcarpetas", True) else "*"
        return [p for p in self.entrada.glob(patron)
                if p.is_file() and not p.name.startswith((".", "~"))
                and not p.name.lower().endswith(TEMPORALES)
                and p.suffix.lower() in self.ext_foto | self.ext_video
                and self.destino not in p.parents]

    def estable(self, ruta: Path) -> bool:
        """Evita tomar archivos que la nube aún está descargando."""
        st = ruta.stat()
        espera = self.cfg.get("segundos_estabilidad", 10)
        previo = self.tamanos.get(str(ruta))
        self.tamanos[str(ruta)] = (st.st_size, time.time())
        if time.time() - st.st_mtime >= espera and st.st_size > 0:
            return True
        return bool(previo and previo[0] == st.st_size and time.time() - previo[1] >= espera)

    def procesar_archivo(self, ruta: Path, sesion) -> bool:
        tipo = "Foto" if ruta.suffix.lower() in self.ext_foto else "Video"
        huella = sha256(ruta)
        if huella in self.indice:
            log(f"Duplicado omitido: {ruta.name} (ya está en {self.indice[huella]})")
            if self.cfg.get("accion", "copiar") == "mover":
                ruta.unlink()
            return False

        fecha, lat, lon = metadatos_foto(ruta) if tipo == "Foto" else metadatos_video(ruta)
        fecha = fecha or datetime.fromtimestamp(ruta.stat().st_mtime)
        c = clasificar(self.cfg, sesion, fecha, lat, lon)

        partes = [limpiar(c["ingenio"])]
        if c["norma"]:
            partes += [limpiar(c["norma"]), limpiar(c["auditoria"])]
            if c["pilar"]:
                partes.append(limpiar(c["pilar"]))
        else:
            partes.append(limpiar(c["auditoria"]))
        carpeta = self.destino.joinpath(*partes, "Fotos" if tipo == "Foto" else "Videos")
        carpeta.mkdir(parents=True, exist_ok=True)

        id_ev = f"{'F' if tipo == 'Foto' else 'V'}-{fecha:%Y%m%d-%H%M%S}-{huella[:6].upper()}"
        nombre = f"{fecha:%Y%m%d_%H%M%S}_{limpiar(c['ingenio'])}"
        if c["norma"]:
            nombre += f"_{limpiar(c['norma'])}"
        nombre += f"_{huella[:6]}{ruta.suffix.lower()}"
        final = carpeta / nombre

        if self.cfg.get("accion", "copiar") == "mover":
            shutil.move(str(ruta), final)
        else:
            shutil.copy2(ruta, final)

        rel = final.relative_to(self.destino).as_posix()
        fila = {
            "id_evidencia": id_ev, "fecha_captura": fecha.isoformat(sep=" ", timespec="seconds"), "tipo": tipo,
            "ingenio": c["ingenio"], "norma": c["norma"], "auditoria": c["auditoria"], "pilar_area": c["pilar"],
            "archivo": nombre, "ruta_relativa": rel, "sha256": huella,
            "latitud": "" if lat is None else f"{lat:.6f}", "longitud": "" if lon is None else f"{lon:.6f}",
            "fuente_clasificacion": c["fuente"], "alerta": c["alerta"], "archivo_original": ruta.name,
            "procesado_en": datetime.now().isoformat(sep=" ", timespec="seconds"),
            "hallazgo_vinculado": "", "observaciones_auditor": "",
        }
        raiz_auditoria = self.destino.joinpath(*partes[:3]) if c["norma"] else self.destino.joinpath(*partes)
        self._anexar_csv(raiz_auditoria / "registro_evidencias.csv", fila)
        self._anexar_csv(self.destino / "_registro_maestro.csv", fila)
        self.indice[huella] = rel
        guardar_json(self.indice_ruta, self.indice)
        log(f"{tipo} -> {rel}" + (f"  [ALERTA: {c['alerta']}]" if c["alerta"] else ""))
        return True

    @staticmethod
    def _anexar_csv(ruta: Path, fila: dict) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        nuevo = not ruta.exists()
        # utf-8-sig para que Excel abra acentos correctamente
        with ruta.open("a", newline="", encoding="utf-8-sig" if nuevo else "utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNAS_REGISTRO)
            if nuevo:
                w.writeheader()
            w.writerow(fila)

    def pasada(self, esperar_estabilidad=True) -> int:
        sesion = cargar_json(ARCHIVO_SESION)
        n = 0
        for ruta in sorted(self.candidatos()):
            try:
                st = ruta.stat()
                clave = (str(ruta), st.st_size, st.st_mtime)
                if clave in self.vistos:
                    continue
                if esperar_estabilidad and not self.estable(ruta):
                    continue
                if self.procesar_archivo(ruta, sesion):
                    n += 1
                self.vistos.add(clave)
            except Exception as e:  # un archivo dañado no detiene el servicio
                log(f"[ERROR] {ruta.name}: {e}")
        return n


# ----------------------------------------------------------------------------- comandos
def cmd_sesion(args, cfg):
    nombres = [i["nombre"] for i in cfg.get("ingenios", [])]
    if args.ingenio not in nombres:
        sys.exit(f"[ERROR] Ingenio '{args.ingenio}' no está en config.json. Opciones: {', '.join(nombres)}")
    normas = cfg.get("normas", {})
    if args.norma not in normas:
        sys.exit(f"[ERROR] Norma '{args.norma}' no está en config.json. Opciones: {', '.join(normas)}")
    if args.pilar and normas[args.norma] and args.pilar not in normas[args.norma]:
        sys.exit(f"[ERROR] Pilar/área '{args.pilar}' no válido para {args.norma}. Opciones: {', '.join(normas[args.norma])}")
    sesion = {
        "ingenio": args.ingenio, "norma": args.norma, "pilar": args.pilar or "",
        "auditoria": args.auditoria or f"{datetime.now():%Y-%m-%d}_{args.norma}",
        "inicio": datetime.now().isoformat(timespec="seconds"), "fin": None,
        "vigencia_horas": args.horas, "tolerancia_min": 15,
    }
    guardar_json(ARCHIVO_SESION, sesion)
    log(f"Sesión activa: {sesion['ingenio']} / {sesion['norma']} / {sesion['pilar'] or '00_General'} "
        f"/ {sesion['auditoria']} (vigencia {args.horas} h)")


def cmd_cerrar(args, cfg):
    sesion = cargar_json(ARCHIVO_SESION)
    if not sesion:
        log("No hay sesión activa.")
        return
    sesion["fin"] = datetime.now().isoformat(timespec="seconds")
    guardar_json(ARCHIVO_SESION, sesion)
    log(f"Sesión cerrada ({sesion['ingenio']} / {sesion['norma']}). Las fotos tomadas después irán por GPS "
        f"o a _Sin_Clasificar.")


def cmd_estado(args, cfg):
    sesion = cargar_json(ARCHIVO_SESION)
    print(json.dumps(sesion, ensure_ascii=False, indent=2) if sesion else "Sin sesión.")
    vigente = sesion_vigente(sesion, datetime.now()) if sesion else None
    print("Vigente ahora:", "SÍ" if vigente else "NO")
    print("Entrada:", cfg["carpeta_entrada"])
    print("Destino:", cfg["carpeta_destino"])


def cmd_procesar(args, cfg):
    n = Organizador(cfg).pasada(esperar_estabilidad=False)
    log(f"Pasada terminada: {n} evidencia(s) nueva(s).")


def cmd_vigilar(args, cfg):
    org = Organizador(cfg)
    log(f"Vigilando {org.entrada} cada {args.intervalo}s. Ctrl+C para detener.")
    try:
        while True:
            org.pasada()
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        log("Detenido.")


def main():
    p = argparse.ArgumentParser(description="Organizador automático de evidencias de gafas inteligentes")
    p.add_argument("--config", default=str(CONFIG_POR_DEFECTO))
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sesion", help="Inicia una sesión de auditoría/inspección")
    s.add_argument("--ingenio", required=True)
    s.add_argument("--norma", required=True)
    s.add_argument("--pilar", default="")
    s.add_argument("--auditoria", default="")
    s.add_argument("--horas", type=float, default=12)
    sub.add_parser("cerrar", help="Cierra la sesión activa")
    sub.add_parser("estado", help="Muestra la sesión y rutas")
    sub.add_parser("procesar", help="Procesa la bandeja una vez")
    v = sub.add_parser("vigilar", help="Procesa la bandeja de forma continua")
    v.add_argument("--intervalo", type=int, default=20)
    args = p.parse_args()

    ruta_cfg = Path(args.config)
    cfg = cargar_json(ruta_cfg)
    if cfg is None:
        sys.exit(f"[ERROR] No existe {ruta_cfg}. Copia config.ejemplo.json como config.json y edítalo.")
    {"sesion": cmd_sesion, "cerrar": cmd_cerrar, "estado": cmd_estado,
     "procesar": cmd_procesar, "vigilar": cmd_vigilar}[args.cmd](args, cfg)


if __name__ == "__main__":
    main()
